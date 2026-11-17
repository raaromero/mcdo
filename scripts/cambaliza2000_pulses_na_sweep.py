r"""Pulsed 2CE and 2PE against NA, pulse width τ, focus model, medium and pupil: the total profiles, and how far they
are from the continuous-beam profiles.

Same physics as cambaliza2000_pulses_sweep.py (zero delay, transform-limited Gaussian pulses, narrow 350-nm transition,
phase-locked beams, all photon pairs), keeping only the total accumulated as the pulses pass the focus:

    A_ij(P) = A¹¹_ij + X_ij + A²²_ij,   A^{ab}_ij = ∫ E_{a,i}(P, t) E_{b,j}(P, t) e^{iω_e t} dt,   F(P) = Σ_ij |A_ij(P)|²,

with i, j the field components (one component for the scalar model) and X the cross term of the two beams: 2A¹²
for 2CE, so that long pulses give |E₁|²|E₂|² (the convention of mcdo.pulsed2ce.pair_signal), and A¹² + A²¹ for 2PE,
so that long pulses give |E₁ + E₂|⁴. Both beams are polarized along y (psi = π/2) in the vector model. The crest
envelope Σ_ij (|A¹¹_ij| + |X_ij| + |A²²_ij|)² runs through the fringe maxima; its FWHM is the width through the fringe
crests, as in cambaliza2000_pulses_sweep.py (continuous beams: (|E₁| + |E₂|)⁴ for 2PE in the scalar model).

Settings come from the environment, so the worker processes see them:
    MODEL = paraxial | rw,   MEDIUM = air | water,   EPS = obstruction ratio (0: circular pupil),   NAS = "0.1,0.2,…"

    MODEL=rw MEDIUM=air NAS=0.5 python scripts/cambaliza2000_pulses_na_sweep.py
    -> output/08_two_color/cambaliza2000/pulses/na_sweep/<model>_<medium>[_eps<ε>]/na<NA>.npz  (one file per NA)
    MEDIUM also takes oil (n = 1.515); APOD = truncation parameter α of a Gaussian input, A(ϑ) = exp(−α sin²ϑ/sin²α_max)
    (0: uniform, as in Cambaliza & Saloma; 4: Lim & Saloma); TAUS = pulse widths in fs; DELAYS = delays of pulse 2 in
    units of τ (0: none). A delay line delays the whole field of beam 2, carrier included. Runs add to an existing file
    of the same NA, so extra pulse widths or delays can be computed later; the keys are <sig>_<θ>_<cut>_<τ> and
    <sig>_<θ>_<cut>_<τ>_d<delay/τ>.
Crossed lenses (θ = π/2) only where the two cones fit, NA ≤ n sin 45°.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np
from multiprocessing import Pool

from mcdo.pulsed2ce import spectrum, C_UM_FS
from mcdo.twobeam import beam_field
from cambaliza2000_pulses_sweep import fwhm

MODEL, MEDIUM = os.environ.get('MODEL', 'paraxial'), os.environ.get('MEDIUM', 'air')
EPS = float(os.environ.get('EPS', 0.0))
APOD = float(os.environ.get('APOD', 0.0))
POL = os.environ.get('POL', 's')         # vector model: s, both beams polarized along y (perpendicular to the plane of the
PSI = {'s': np.pi / 2, 'p': 0.0}[POL]    # lens axes); p, each beam polarized in that plane, across its own axis
N = {'air': 1.0, 'water': 1.33, 'oil': 1.515}[MEDIUM]
NAS = [float(a) for a in os.environ.get('NAS', '0.5').split(',')]
TAUS = tuple(float(a) for a in os.environ.get('TAUS', '4,5,7,10,15,20,30,50,70,100,150,200,300,500,1000').split(','))
DELAYS = tuple(float(a) for a in os.environ.get('DELAYS', '0').split(','))      # in units of τ
THETAS = (('0', 0.0), ('pi2', np.pi / 2), ('pi', np.pi))
LAMS = {'2ce': (0.750, 0.656), '2pe': (0.700, 0.700)}
WE = 2 * np.pi * C_UM_FS / 0.350
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'cambaliza2000', 'pulses', 'na_sweep',
                   f'{MODEL}_{MEDIUM}' + (f'_eps{EPS:g}' if EPS else '') + (f'_gauss{APOD:g}' if APOD else '') + ('_polp' if POL == 'p' else ''))
BLOCK = 300                                                         # points per block of the time integral


def grid(na, cut):
    """Lab points along z (x = 0) or across x (z = 0), scaled with the focus, 50 samples per µm along z."""
    zspan = 5 * N * (0.5 / na) ** 2 / max(1 - EPS ** 2, 1e-3) ** (1 if EPS else 0)
    if cut == 'z':
        return np.linspace(-zspan, zspan, 2 * int(50 * zspan) + 1)
    return np.linspace(-1.5 * 0.5 / na, 1.5 * 0.5 / na, 301)


def field(lam_or_w, na, theta, x, z, w=False):
    lam = 2 * np.pi * C_UM_FS / lam_or_w if w else lam_or_w
    kw = dict(model='rw', psi=PSI) if MODEL == 'rw' else {}
    if APOD:
        kw['apodization'] = lambda th: np.exp(-APOD * np.sin(th) ** 2 / (na / N) ** 2)
    E = beam_field(x, z, lam, na, N, theta=theta, eps=EPS, **kw)
    return E if MODEL == 'rw' else E[None]                       # (components, points)


def tensor(a, b):
    return a[:, None] * b[None, :]                                  # (comp, comp, pts)


def signal(E1, E2, sig):
    """The continuous-beam profile and its crest envelope, the long-pulse limit of F with the same cross term X."""
    X = 2 * tensor(E1, E2) if sig == '2ce' else tensor(E1, E2) + tensor(E2, E1)
    if sig == '2ce':                                                # no 350-nm pairs within one beam
        return (np.abs(X) ** 2).sum((0, 1)), (np.abs(X) ** 2).sum((0, 1))
    A11, A22 = tensor(E1, E1), tensor(E2, E2)
    return (np.abs(A11 + X + A22) ** 2).sum((0, 1)), ((np.abs(A11) + np.abs(X) + np.abs(A22)) ** 2).sum((0, 1))


def pulsed(na, tau, theta, s, cut, sig, delay=0.0):
    """Total F(P) = Σ_ij |A_ij|² along the cut, accumulated as the pulses pass the focus, and its crest envelope;
    pulse 2 arrives `delay` fs after pulse 1."""
    l1, l2 = LAMS[sig]
    w1, w2 = 2 * np.pi * C_UM_FS / l1, 2 * np.pi * C_UM_FS / l2
    reach = N * np.max(np.abs(s)) / C_UM_FS + abs(delay)
    dt = min(tau / 20, 0.4)
    t = np.arange(-(3 * tau + reach), 3 * tau + reach + dt / 2, dt)
    window = 2 * (4 * tau + reach)
    out, crest = np.empty(len(s)), np.empty(len(s))
    specs = [spectrum(l, tau, t_window=window) for l in (l1, l2)]
    for b0 in range(0, len(s), BLOCK):
        sb = s[b0:b0 + BLOCK]
        x, z = (0 * sb, sb) if cut == 'z' else (sb, 0 * sb)
        env = []
        for (w, a, d), th, dl in zip(specs, (0.0, theta), (0.0, delay)):
            E = np.stack([field(wm, na, th, x, z, w=True) for wm in w])            # (n_ω, comp, pts)
            # envelope about the mean frequency; a delay dl multiplies each component by e^{iω dl}
            c = a * d * np.exp(-1j * np.outer(t - dl, w - w.mean())) * np.exp(1j * w.mean() * dl)
            env.append(np.tensordot(c, E, axes=(1, 0)))                               # (n_t, comp, pts)
        e1, e2 = env
        ph = lambda dw: np.exp(1j * dw * t) * dt
        A12 = np.einsum('t,tip,tjp->ijp', ph(WE - w1 - w2), e1, e2)
        X = 2 * A12 if sig == '2ce' else A12 + A12.transpose(1, 0, 2)
        A11 = np.einsum('t,tip,tjp->ijp', ph(WE - 2 * w1), e1, e1)
        A22 = np.einsum('t,tip,tjp->ijp', ph(WE - 2 * w2), e2, e2)
        out[b0:b0 + BLOCK] = (np.abs(A11 + X + A22) ** 2).sum(axis=(0, 1))
        crest[b0:b0 + BLOCK] = ((np.abs(A11) + np.abs(X) + np.abs(A22)) ** 2).sum(axis=(0, 1))
    return out, crest


def one_case(args):
    na, sig, tk, th, cut = args
    t0 = time.time()
    s = grid(na, cut)
    x, z = (0 * s, s) if cut == 'z' else (s, 0 * s)
    l1, l2 = LAMS[sig]
    res = {f'{sig}_{tk}_{cut}_s': s}
    cw, cwc = signal(field(l1, na, 0.0, x, z), field(l2, na, th, x, z), sig)
    res[f'{sig}_{tk}_{cut}_cw'], res[f'{sig}_{tk}_{cut}_cw_crest'] = cw / cw.max(), cwc / cwc.max()
    for tau in TAUS:
        peak = {}
        for dl in DELAYS:
            p, pc = pulsed(na, tau, th, s, cut, sig, dl * tau)
            key = f'{sig}_{tk}_{cut}_{tau:g}' + (f'_d{dl:g}' if dl else '')
            peak[dl] = p.max()
            res[key], res[key + '_crest'] = p / p.max(), pc / pc.max()
        if any(DELAYS):                                                 # peak at each delay over the peak at none
            p0 = peak[0.0] if 0.0 in peak else pulsed(na, tau, th, s, cut, sig)[0].max()
            for dl in DELAYS:
                if dl:
                    res[f'{sig}_{tk}_{cut}_{tau:g}_d{dl:g}_rel'] = np.array(peak[dl] / p0)
    print(f'{MODEL} {MEDIUM} eps {EPS:g} apod {APOD:g} NA {na:g} {sig} {tk} {cut}: {time.time() - t0:.0f} s', flush=True)
    return na, res


def main():
    os.makedirs(OUT, exist_ok=True)
    cases = [(na, sig, tk, th, cut) for na in NAS for sig in ('2ce', '2pe') for tk, th in THETAS for cut in ('z', 'x')
             if not (tk == 'pi2' and na > N * np.sin(np.pi / 4) + 1e-9)]
    cases.sort(key=lambda c: -len(grid(c[0], c[4])))                    # longest first
    res = {na: {} for na in NAS}
    with Pool(int(os.environ.get('WORKERS', 7))) as pool:
        for na, r in pool.imap_unordered(one_case, cases):
            res[na].update(r)
            done = sum(1 for c in cases if c[0] == na)
            if len([k for k in res[na] if k.endswith('_s')]) == done:          # all cases of this NA are in
                f = os.path.join(OUT, f'na{na:g}.npz')
                old = dict(np.load(f)) if os.path.exists(f) else {}                 # add to an earlier run of this NA
                for k in ('taus', 'na', 'n', 'eps', 'model', 'apod'):
                    old.pop(k, None)
                old.update(res[na])
                taus = sorted({float(k.split('_')[3]) for k in old if k.count('_') == 3 and k.split('_')[3] not in ('s', 'cw')})
                np.savez_compressed(f, taus=np.array(taus), na=na, n=N, eps=EPS, apod=APOD, model=MODEL, **old)
                print(f'saved NA {na:g}', flush=True)


if __name__ == '__main__':
    main()
