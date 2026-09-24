"""Continuous-wave baseline for the annular work.

Every pulsed result is quoted as a change against an unpulsed reference, so the
reference itself has to be measured on the same grid, with the same code, at the
same operating points. This does that and nothing else: no pulse, one wavelength.

    numerical aperture   0.1 (low), 0.8 (the deck standard), 1.2 (high)
    input                uniform, Gaussian with alpha = 4
    obstruction ratio    0, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99

For each of the 42 cells: transverse focal width, depth of focus, the
depth-of-focus gain over that cell's own unobstructed disk, and the on-axis peak
relative to the same reference (what the ring costs in brightness).

The paraxial law 1/(1-eps^2) is plotted as the low-aperture limit it is, not as
a universal prediction: it is exact at numerical aperture 0.1 and overestimates
the gain by more as the aperture grows.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo.style import apply as _apply_style
_apply_style()

from mcdo import SimConfig
from mcdo.annular import compute_integrals_annular
from mcdo.apodization import gaussian
from mcdo.components import full as vec_intensity
from mcdo.figio import save_panels
from mcdo.rw_integrals import compute_integrals

LAM, N_MED, NT = 0.750, 1.3, 801
ALPHA_T = 4.0
NA_CASES = [0.1, 0.8, 1.2]
EPS = [0.0, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99]
INPUTS = [('uniform', None), ('Gaussian, alpha = 4', ALPHA_T)]

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '03_annular')
os.makedirs(OUT, exist_ok=True)


def _fwhm(x, y):
    y = y / y.max()
    below = np.where(y < 0.5)[0]
    if not len(below):
        return np.nan
    i = below[0]
    return 2.0 * np.interp(0.5, [y[i], y[i - 1]], [x[i], x[i - 1]])


def _axial_extent(z, I, frac=0.8):
    """Axial half-extent holding `frac` of the on-axis energy.

    Full width at half maximum stops describing anything as the ring thins: at
    obstruction 0.99 the profile sits above half across most of any window, so
    the width reported is set by where the window ends. An energy fraction has
    no such failure mode.
    """
    c = np.cumsum(I)
    c = c / c[-1]
    return 2.0 * np.interp(frac, c, z)


def _sidelobe(r, I):
    """Highest secondary maximum, relative to the peak.

    Reported only where the central lobe has a well-defined first minimum. At
    high numerical aperture and high obstruction ratio the longitudinal field
    fills the first null of the transverse pattern, so no first minimum exists
    and the quantity this returns would be the second side lobe instead. Those
    cases return not-a-number rather than a number that invites comparison
    with the others.
    """
    I = I / I.max()
    falling = np.where(np.diff(I) > 0)[0]
    if not len(falling):
        return float("nan")
    first_min = r[falling[0]]
    # the transverse pattern places its first minimum near 0.6 lambda / NA;
    # a minimum far outside that means the first null has been filled in
    if first_min > 1.5 * 0.61 * LAM / cfg_xna[0]:
        return float("nan")
    return float(I[falling[0]:].max())


def _transmission(cfg, eps, apod):
    """Fraction of the incident beam's power that reaches the focus.

    Peak intensity and transmitted power are different losses and they
    compound: the ring first blocks light, then spreads what is left over a
    longer focus. Quoting only the peak hides which of the two is happening.
    """
    th = np.linspace(0.0, cfg.alpha, 4001)
    A = np.ones_like(th) if apod is None else np.abs(np.asarray(apod(th)))
    w = A ** 2 * np.sin(th) * np.cos(th)          # aplanatic area element
    th_in = np.arcsin(eps * np.sin(cfg.alpha))
    return float(np.trapezoid(w[th >= th_in], th[th >= th_in]) /
                 np.trapezoid(w, th))


def _profiles(cfg, eps, apod):
    """Transverse and axial intensity, and the on-axis peak, for one cell."""
    dof0 = 2.0 * LAM / cfg.X_NA ** 2
    r = np.linspace(0.0, 4.0 * LAM / cfg.X_NA, 900)
    z = np.linspace(0.0, 40.0 * dof0, 4000)     # one window for every ratio
    z0, r0 = np.array([0.0]), np.array([0.0])

    def _int(rr, zz):
        if eps == 0.0:
            return compute_integrals(rr, zz, cfg.k_c, cfg.alpha, NT, apodization=apod)
        return compute_integrals_annular(rr, zz, cfg.k_c, cfg.alpha, eps, NT,
                                         apodization=apod)

    A0, A1, A2 = _int(r, z0)
    I_r = vec_intensity(A0[0], A1[0], A2[0])
    B0, B1, B2 = _int(r0, z)
    I_z = vec_intensity(B0[:, 0], B1[:, 0], B2[:, 0])
    return r, I_r, z, I_z, float(I_r[0])


res = {}
profiles = {}
cfg_xna = [NA_CASES[0]]
print(f"{'NA':>5} {'input':<38} {'eps':>5} {'width nm':>9} "
      f"{'depth um':>10} {'gain':>7} {'peak':>7} {'transmit':>9}")
for xna in NA_CASES:
    cfg = SimConfig(lam_c=LAM, X_NA=xna, n=N_MED, tau=np.inf, N_freq=3, N_theta=NT)
    cfg_xna[0] = xna
    # absolute reference for this aperture: uniform illumination, no obstruction.
    # Referencing each illumination to its own unobstructed case is right for
    # isolating what the obstruction did, but it hides what the illumination
    # itself costs, since both then read 1.000 at eps = 0.
    _, _, _, I_z_u, peak_uni = _profiles(cfg, 0.0, None)
    depth_uni = _fwhm(np.linspace(0.0, 40.0 * 2.0 * LAM / xna ** 2, 4000), I_z_u)
    for label, at in INPUTS:
        apod = None if at is None else gaussian(at, cfg.sin2_alpha)
        base_d = base_p = None
        for eps in EPS:
            r, I_r, z, I_z, peak = _profiles(cfg, eps, apod)
            w = _fwhm(r, I_r) * 1000.0
            d = _fwhm(z, I_z)
            if eps == 0.0:
                base_d, base_p = d, peak
            key = f"{xna}|{label}|{eps}"
            profiles[key + '|r'] = np.vstack([r, I_r / I_r.max()])
            profiles[key + '|z'] = np.vstack([z, I_z / I_z.max()])
            ext = _axial_extent(z, I_z)
            if eps == 0.0:
                base_e = ext
            res[(xna, label, eps)] = dict(
                width_nm=w, depth_um=d, gain=d / base_d, peak=peak / base_p,
                transmission=_transmission(cfg, eps, apod),
                peak_vs_uniform=peak / peak_uni,
                depth_vs_uniform=d / depth_uni,
                extent_um=ext, extent_gain=ext / base_e,
                sidelobe=_sidelobe(r, I_r))
            print(f"{xna:>5.1f} {label:<38} {eps:>5.2f} {w:>9.1f} "
                  f"{d:>10.3f} {d / base_d:>7.2f} {peak / base_p:>7.3f} "
                  f"{res[(xna, label, eps)]['transmission']:>9.4f}")

np.savez_compressed(
    os.path.join(OUT, 'annular_baseline.npz'),
    na=np.array([k[0] for k in res]), input=np.array([k[1] for k in res]),
    eps=np.array([k[2] for k in res]),
    **{q: np.array([v[q] for v in res.values()])
       for q in ('width_nm', 'depth_um', 'gain', 'peak',
                 'extent_um', 'extent_gain', 'sidelobe', 'transmission',
                 'peak_vs_uniform', 'depth_vs_uniform')},
    **profiles)

# ── figure: one column per quantity, one row per aperture ──────────────────
fig, axes = plt.subplots(3, 3, figsize=(27.0, 19.5))
STYLE = {'uniform': ('#1f77b4', 'o-'),
         'Gaussian, alpha = 4': ('#d62728', 's--')}
eps_arr = np.array(EPS)

for row, xna in enumerate(NA_CASES):
    for col, (q, ylab) in enumerate([
            ('width_nm', 'Focal width (nm)'),
            ('gain', 'Depth-of-focus gain'),
            ('peak', 'Peak intensity, relative to the full disk')]):
        ax = axes[row, col]
        for label, _ in INPUTS:
            color, style = STYLE[label]
            y = [res[(xna, label, e)][q] for e in EPS]
            short = 'uniform' if label == 'uniform' else 'Gaussian, alpha = 4'
            ax.plot(eps_arr, y, style, color=color, lw=2.0, ms=7, label=short)
        if q == 'gain':
            ax.plot(eps_arr, 1.0 / (1.0 - eps_arr ** 2), 'k:', lw=2.0,
                    label='Paraxial law')
            ax.set_yscale('log')
        ax.set_xlabel('Obstruction ratio')
        ax.set_ylabel(ylab)
        ax.set_title(f'Numerical aperture {xna:g}, continuous wave, 750 nm',
                     fontsize=12)
        ax.grid(alpha=0.25, which='both')
        ax.legend(fontsize=10)

plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUT, 'panels'), 'annular_baseline')
out = os.path.join(OUT, 'annular_baseline.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f"\nSaved → {out}")

print("\nReferenced to uniform illumination with no obstruction, same aperture:")
print(f"{'NA':>5} {'input':<38} {'eps':>5} {'peak':>8} {'depth':>8}")
for (xna, label, eps), v in res.items():
    if eps in (0.0, 0.5, 0.9):
        print(f"{xna:>5.1f} {label:<38} {eps:>5.2f} "
              f"{v['peak_vs_uniform']:>8.4f} {v['depth_vs_uniform']:>8.3f}")

print("\nDepth-of-focus gain against the paraxial law:")
for eps in [0.5, 0.9, 0.99]:
    law = 1.0 / (1.0 - eps ** 2)
    row = "  ".join(f"NA {x:g}: {res[(x, 'uniform', eps)]['gain']:6.2f}"
                    for x in NA_CASES)
    print(f"  eps {eps:<5} law {law:7.2f}   {row}")
