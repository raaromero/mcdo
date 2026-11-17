r"""Pulsed 2CE over pulse width τ, counting all photon pairs from both beams, and how the excitation builds up in time.

Same model as cambaliza2000_pulses_allpairs.py (paraxial scalar, NA 0.5, air, zero delay, transform-limited Gaussian
pulses, narrow 350-nm transition, phase-locked beams). For each τ and each rotation θ (0, π/2, π), along the axis
(x = 0) and across it (z = 0):

* the running two-photon amplitude A(P, t) = ∫₋∞ᵗ E(P, t′)² e^{iω_e t′} dt′ = A₁₁(t) + 2A₁₂(t) + A₂₂(t), whose square
  |A(P, t)|² is the excited-state probability reached by time t (second-order perturbation theory); at t → ∞ it is
  the pulsed 2CE profile. 'one pair' = |2A₁₂|², 'all pairs' = |A|²;
* the crest envelope (|A₁₁| + |2A₁₂| + |A₂₂|)², the line through the fringe maxima, and the fringe average
  |A₁₁|² + |2A₁₂|² + |A₂₂|², the profile with the fringes washed out (both equal |2A₁₂|² when the spectra are apart);
* the instantaneous product I₁(P, t)·I₂(P, t): where the two pulses overlap at time t.

Widths are FWHM. 'central' is the FWHM of the fringe that holds the maximum; it drops to one fringe once the fringe
minima fall below half the maximum. With a = |2A₁₂|, b = |A₁₁| + |A₂₂|, |A|² = a²(1 + (b/a) cos q·r)², q = (ω_e/2c)(k̂₁ − k̂₂):
fringes of period λ₂ₚ/|k̂₁ − k̂₂| (λ₂ₚ = 700 nm; 350 nm at θ = π, none at θ = 0) and depth 2ab/(a² + b²).

    python scripts/cambaliza2000_pulses_sweep.py [--na 0.3]
    -> output/08_two_color/cambaliza2000/pulses/sweep/{sweep.npz, sweep.txt}     (NA 0.5; other NA: sweep_na<NA>.npz/.txt)
The grids scale with the focus: across as 0.5/NA, along as (0.5/NA)², with the same samples per µm as at NA 0.5.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np
from multiprocessing import Pool

from mcdo.pulsed2ce import _fields, C_UM_FS
from mcdo.twobeam import beam_field

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'cambaliza2000', 'pulses', 'sweep')
os.makedirs(OUT, exist_ok=True)
if '--na' in sys.argv:                                              # through the environment, so the worker processes see it
    os.environ['SWEEP_NA'] = sys.argv[sys.argv.index('--na') + 1]
NA, N, L1, L2, LE = float(os.environ.get('SWEEP_NA', 0.5)), 1.0, 0.750, 0.656, 0.350
W1, W2, WE = (2 * np.pi * C_UM_FS / l for l in (L1, L2, LE))       # rad/fs
TAUS = (5.0, 7.0, 10.0, 12.0, 15.0, 20.0, 30.0, 50.0, 100.0)       # fs
THETAS = (('0', 0.0), ('pi2', np.pi / 2), ('pi', np.pi))
SC = 0.5 / NA
ZS, XS = np.linspace(-5 * SC ** 2, 5 * SC ** 2, 2 * int(250 * SC ** 2) + 1), np.linspace(-1.5 * SC, 1.5 * SC, 2 * int(150 * SC) + 1)
TAG = '' if NA == 0.5 else f'_na{NA:g}'
LAMS = {'2ce': (0.750, 0.656), '2pe': (0.700, 0.700)}                    # 2PE: both beams at 700 nm (Eq. 6)
NT = 300                                                            # stored time samples per run


def env_t(x, z, lam, tau, theta, t, window):
    """Field envelope (n_t, points) about the centre frequency of its pulse."""
    dw, c, E = _fields(x, z, lam, tau, window, NA, N, theta, 0.0, 0.0, 'paraxial', None, None)
    return np.tensordot(c[None, :] * np.exp(-1j * np.outer(t, dw)), E, axes=(1, 0))


def fwhm(s, y):
    """FWHM of the lobe that holds the maximum of y (nan if y is ~0 or the lobe reaches the edge)."""
    if not np.isfinite(y).all() or y.max() <= 0:
        return np.nan
    y = y / y.max()
    i0 = int(np.argmax(y))
    r, l = i0, i0
    while r < len(y) - 1 and y[r] >= 0.5:
        r += 1
    while l > 0 and y[l] >= 0.5:
        l -= 1
    if y[r] >= 0.5 or y[l] >= 0.5:
        return np.nan
    return np.interp(0.5, [y[r], y[r - 1]], [s[r], s[r - 1]]) - np.interp(0.5, [y[l], y[l + 1]], [s[l], s[l + 1]])


def depth(one, crest):
    """Fringe depth 2ab/(a² + b²) at the peak, a = |2A₁₂|, b = |A₁₁| + |A₂₂|: the contrast of the fringes
    |A|² = |2A₁₂|² (1 + (b/a) cos q·r)² wherever the beams are not collinear (0: same-beam pairs absent)."""
    i = int(np.argmax(one))
    a, b = np.sqrt(one[i]), np.sqrt(crest[i]) - np.sqrt(one[i])
    return 2 * a * b / (a ** 2 + b ** 2) if a > 0 else np.nan


def centre(s, y):
    return np.sum(s * y) / np.sum(y) if y.sum() > 0 else np.nan


def run(tau, theta, cut, sig='2ce', delay=0.0):
    """One run; beam 2's pulse reaches the focus `delay` fs after beam 1's."""
    L1, L2 = LAMS[sig]
    W1, W2 = 2 * np.pi * C_UM_FS / L1, 2 * np.pi * C_UM_FS / L2
    s = ZS if cut == 'z' else XS
    x, z = (0 * s, s) if cut == 'z' else (s, 0 * s)
    reach = N * np.max(np.abs(s)) / C_UM_FS + abs(delay)
    dt = min(tau / 20, 0.4)                                     # resolves ω₂ − ω₁ = 0.36 rad/fs
    t = np.arange(-(3 * tau + reach), 3 * tau + reach + dt / 2, dt)
    window = 2 * (4 * tau + reach)
    e1 = env_t(x, z, L1, tau, 0.0, t, window)
    e2 = env_t(x, z, L2, tau, theta, t - delay, window)
    ph = lambda d: np.exp(1j * d * t)[:, None]
    A11 = np.cumsum(e1 * e1 * ph(WE - 2 * W1), axis=0) * dt
    A12 = np.cumsum(e1 * e2 * ph(WE - W1 - W2), axis=0) * dt
    A22 = np.cumsum(e2 * e2 * ph(WE - 2 * W2), axis=0) * dt
    P = np.abs(e1) ** 2 * np.abs(e2) ** 2
    one = np.abs(2 * A12) ** 2
    allp = np.abs(A11 + 2 * A12 + A22) ** 2
    crest = (np.abs(A11) + np.abs(2 * A12) + np.abs(A22)) ** 2
    mean = np.abs(A11) ** 2 + one + np.abs(A22) ** 2
    single = np.abs(A11) ** 2 + np.abs(A22) ** 2
    k = np.unique(np.linspace(0, len(t) - 1, NT).round().astype(int))
    ts = {'t': t[k], 'P_peak': P[k].max(1), 'P_fwhm': np.array([fwhm(s, P[i]) for i in k]),
          'P_centre': np.array([centre(s, P[i]) for i in k])}
    for name, F in (('one', one), ('all', allp), ('crest', crest), ('mean', mean)):
        ts[name + '_peak'] = F[k].max(1)
        ts[name + '_fwhm'] = np.array([fwhm(s, F[i]) for i in k])
    ts['depth'] = np.array([depth(one[i], crest[i]) for i in k])
    fin = {'s': s, 'one': one[-1], 'all': allp[-1], 'crest': crest[-1], 'mean': mean[-1], 'single': single[-1],
           'I12': np.sum(P, axis=0) * dt, 'P_focus': P[:, np.argmin(np.abs(s))],
           'rate': np.sum(P if sig == '2ce' else np.abs(e1 + e2) ** 4, axis=0) * dt}   # the 'now' rate added up: a dye that loses phase fast
    return ts, fin, t


def one_case(args):
    """All τ of one signal, angle and cut: the continuous-beam profile, then each run."""
    sig, pre, tk, th, cut = args
    res, lines = {}, []
    s = ZS if cut == 'z' else XS
    pts = (0 * s, s) if cut == 'z' else (s, 0 * s)
    u1, u2 = beam_field(*pts, LAMS[sig][0], NA), beam_field(*pts, LAMS[sig][1], NA, theta=th)
    cw = np.abs(u1) ** 2 * np.abs(u2) ** 2 if sig == '2ce' else np.abs(u1 + u2) ** 4
    res[f'{pre}{tk}_{cut}_cw'] = cw / cw.max()
    for tau in TAUS:
        ts, fin, t = run(tau, th, cut, sig)
        key = f'{pre}{tk}_{cut}_{tau:g}'
        res.update({f'{key}_ts_{a}': b for a, b in ts.items()})
        res.update({f'{key}_fin_{a}': b for a, b in fin.items()})
        pk = fin['one'].max()
        lines.append(
            f'{sig} theta {tk}, {cut}, tau {tau:g} fs: FWHM continuous {fwhm(s, cw):.3f}, one pair {fwhm(s, fin["one"]):.3f}, '
            f'all pairs central {fwhm(s, fin["all"]):.3f}, crest {fwhm(s, fin["crest"]):.3f}, '
            f'fringe-averaged {fwhm(s, fin["mean"]):.3f} um; fringe depth {depth(fin["one"], fin["crest"]):.3f}; '
            f'all/one peak {fin["all"].max() / pk:.3f}; same-beam/one peak {fin["single"].max() / pk:.4f}; '
            f'one pair vs ∫I1I2 rms {np.sqrt(np.mean((fin["one"] / pk - fin["I12"] / fin["I12"].max()) ** 2)):.4f}; '
            f'{len(t)} steps')
    print(f'NA {NA:g}: {sig} {tk} {cut} done', flush=True)
    return res, lines


def main():
    cases = [(sig, pre, tk, th, cut) for sig, pre in (('2ce', ''), ('2pe', 'pe_'))   # 2CE keys as before; 2PE keys start with pe_
             for tk, th in THETAS for cut in ('z', 'x')]
    res, lines = {}, []
    with Pool(6) as pool:
        for r, ls in pool.map(one_case, cases):
            res.update(r); lines += ls
    np.savez_compressed(os.path.join(OUT, f'sweep{TAG}.npz'), taus=np.array(TAUS), zs=ZS, xs=XS, na=NA, **res)
    open(os.path.join(OUT, f'sweep{TAG}.txt'), 'w').write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
