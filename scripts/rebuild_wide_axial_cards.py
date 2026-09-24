r"""Recompute the atlas cards whose axial window is too narrow for their focus.

Every atlas family sizes its axial window from the unobstructed depth of focus,
which is right for most cells and wrong for the thin rings. At obstruction
ratio 0.99 the focus is roughly 44 times longer, so the profile never falls to
half maximum inside the frame: the card shows about 47 um of a 108 um focus and
reads as a flat-topped bar. The measured numbers quoted anywhere come from the
sweeps, not from these cards, so nothing published is wrong - but the picture of
the most extended configuration is the one cut off.

This finds every card whose on-axis profile stays above half maximum at the
window edge and recomputes it on a window scaled by the extension the ring
actually produces, taken from the closed form in mcdo.extension.

    python scripts/rebuild_wide_axial_cards.py [--dry-run]
"""

import glob
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np

from mcdo import SimConfig
from mcdo.annular import compute_integrals_annular
from mcdo.apodization import gaussian
from mcdo.atlascard import render_card
from mcdo.components import full as ydir
from mcdo.extension import exact
from mcdo.rw_integrals import compute_integrals

LAM, N_MED, NT, NFREQ = 0.750, 1.3, 801, 201
ATLAS = os.path.join(os.path.dirname(__file__), '..', 'output', 'atlas')
DRY = '--dry-run' in sys.argv
# --family lets the cheap continuous-wave rebuilds run while a pulsed sweep is
# still occupying the machine; the pulsed cards cost minutes each
ONLY = None
if '--family' in sys.argv:
    ONLY = sys.argv[sys.argv.index('--family') + 1]
PAD = 1.5      # half-window in units of the depth of focus it must show


def mirror(Ih):
    return np.concatenate([Ih[:, ::-1][:, :-1], Ih], axis=1)


def window_limited(path):
    """True when the on-axis profile is still above half maximum at the edge."""
    d = np.load(path)
    I = d['intensity'].astype(float)
    ax = I[:, int(np.argmin(np.abs(d['h'])))]
    ax = ax / ax.max()
    return bool(ax[0] >= 0.5 or ax[-1] >= 0.5)


def parse(fam, stem):
    """Aperture, illumination, ratio and pulse duration encoded in a file name."""
    def num(tok):
        return float(tok.replace('p', '.'))
    if fam in ('annular_grid', 'pulsed_grid'):
        parts = stem.split('_')
        xna = num(parts[0][2:])
        inp = parts[1]
        eps = num(parts[2][3:])
        tau = parts[3] if len(parts) > 3 else 'cw'
        at = None if inp == 'uniform' else 4.0
    elif fam == 'truncation_grid':
        parts = stem.split('_')
        xna, at = 0.8, num(parts[0][2:])
        inp = 'uniform' if at == 0 else 'gaussian'
        eps, tau = num(parts[1][3:]), 'cw'
        at = None if at == 0 else at
    else:                                   # pulsed_illumination
        parts = stem.split('_')
        xna, inp = 0.8, parts[0]
        eps, tau = num(parts[1][3:]), parts[2]
        at = None if inp == 'uniform' else 4.0
    return xna, inp, at, eps, tau


def field(r, z, k, alpha, eps, apod):
    if eps == 0.0:
        return ydir(*compute_integrals(r, z, k, alpha, NT, apodization=apod))
    return ydir(*compute_integrals_annular(r, z, k, alpha, eps, NT,
                                           apodization=apod))


TAU_S = {'cw': np.inf, '1fs': 1e-15, '2fs': 2e-15}
FAMS = ('annular_grid', 'truncation_grid', 'pulsed_grid', 'pulsed_illumination')

targets = []
for fam in FAMS:
    if ONLY and fam != ONLY:
        continue
    for f in sorted(glob.glob(os.path.join(ATLAS, fam, 'field_*.npz'))):
        if window_limited(f):
            targets.append((fam, f))

print(f'{len(targets)} cards are window limited')
if DRY:
    for fam, f in targets:
        print(f'  {fam}/{os.path.basename(f)}')
    raise SystemExit

t0 = time.time()
for fam, f in targets:
    stem = os.path.basename(f)[len('field_'):-len('.npz')]
    xna, inp, at, eps, tau = parse(fam, stem)
    tau_s = TAU_S[tau]

    # The transverse window is kept; only the axial one changes. It is sized
    # from the depth this cell actually has, not by scaling the old window:
    # the old window is already many depths wide (12 of them at aperture 1.2),
    # so multiplying it by the extension again overshoots by more than tenfold
    # and leaves the focus filling a few percent of the frame.
    d_old = np.load(f)
    h_old = d_old['h']
    r_half = h_old[h_old >= 0]
    old_span = float(np.abs(d_old['v']).max())

    cfg = SimConfig(lam_c=LAM, X_NA=xna, n=N_MED, tau=tau_s,
                    N_freq=NFREQ if np.isfinite(tau_s) else 3, N_theta=NT)
    A = None if at is None else gaussian(at, cfg.sin2_alpha)

    # unobstructed depth for this aperture, measured on the existing window
    z_probe = np.linspace(-old_span, old_span, 481)
    ref0 = field(np.array([0.0]), z_probe, cfg.k_c, cfg.alpha, 0.0, None)[:, 0]
    ref0 = ref0 / ref0.max()
    over = np.where(ref0 >= 0.5)[0]
    dof0 = float(z_probe[over[-1]] - z_probe[over[0]])
    span = max(PAD * exact(eps, xna, N_MED) * dof0, old_span)
    z_new = np.linspace(-span, span, 481)

    if np.isfinite(tau_s):
        acc = np.zeros((len(z_new), len(r_half)))
        om = cfg.omega_grid()
        for o, w in zip(om, cfg.spectral_power(om)):
            if o <= 0:
                continue
            acc += w * field(r_half, z_new, cfg.k_for_omega(o), cfg.alpha, eps, A)
        I_half = acc
    else:
        I_half = field(r_half, z_new, cfg.k_c, cfg.alpha, eps, A)

    I = mirror(I_half)
    I /= I.max()
    r_full = np.concatenate([-r_half[::-1][:-1], r_half])

    # the reference curves are the unobstructed pupil on the same window
    R = mirror(field(r_half, z_new, cfg.k_c, cfg.alpha, 0.0, None))
    R /= R.max()
    ref_tr = R[int(np.argmin(np.abs(z_new)))]
    ref_ax = R[:, int(np.argmin(np.abs(r_full)))]

    np.savez_compressed(f, intensity=I.astype(np.float32), h=r_full, v=z_new)
    # each family titles its cards its own way; a rebuilt card has to keep the
    # convention of the family it sits in, or it reads as a different figure
    lab = 'uniform' if at is None else f'Gaussian, alpha = {at:g}'
    pulse = {'cw': 'continuous wave', '1fs': '1 fs', '2fs': '2 fs'}[tau]
    if fam == 'truncation_grid':
        title = (f'alpha {0.0 if at is None else at:g}, '
                 f'obstruction ratio {eps:g}, numerical aperture 0.8')
        curve = f'Alpha {0.0 if at is None else at:g}, ratio {eps:g}'
    elif fam == 'pulsed_illumination':
        title = f'{lab}, obstruction ratio {eps:g}, {pulse}'
        curve = f'Ratio {eps:g}, {pulse}'
    elif fam == 'pulsed_grid':
        title = (f'{lab}, obstruction ratio {eps:g}, {pulse}, '
                 f'numerical aperture {xna:g}')
        curve = f'Ratio {eps:g}, {pulse}'
    else:                                   # annular_grid
        title = (f'Obstruction ratio {eps:g}, {lab} input, '
                 f'numerical aperture {xna:g}')
        curve = f'Obstruction ratio {eps:g}'
    render_card(r_full, z_new, I, title,
                os.path.join(ATLAS, fam, f'{stem}.png'), ref_tr, ref_ax,
                airy_um=0.61 * LAM / xna, curve_label=curve)
    ok = 'ok' if not window_limited(f) else 'STILL LIMITED'
    print(f'  {fam}/{stem}: axial window {2 * span:.1f} um  [{ok}]', flush=True)

print(f'\n{len(targets)} cards rebuilt in {(time.time() - t0) / 60:.1f} min')
