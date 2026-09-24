r"""At what pulse duration does a pulse stop differing from continuous wave?

The duration axis has been sampled at three points: continuous wave, 2 fs and
1 fs. That is enough to show a trend and not enough to say where it ends. This
sweeps seven durations and reports, for each, how far the depth of focus and
the extension sit from their continuous-wave values, so the crossover can be
read rather than guessed.

Bandwidth is inversely proportional to duration, so the natural expectation is
that everything scales with 1/tau and the difference falls off smoothly. What
counts as equivalent is a choice; 1% and 0.1% of the continuous-wave depth are
both reported.

    python scripts/verify_duration.py
    -> output/05_pulsed_pupils/duration_sweep.npz
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np

from mcdo import SimConfig
from mcdo.annular import compute_integrals_annular
from mcdo.apodization import gaussian
from mcdo.components import full as vec_intensity
from mcdo.rw_integrals import compute_integrals

LAM, N_MED, X_NA, NT = 0.750, 1.3, 0.8, 801
TAUS = [(1e-15, '1 fs'), (2e-15, '2 fs'), (3e-15, '3 fs'), (5e-15, '5 fs'),
        (10e-15, '10 fs'), (20e-15, '20 fs'), (np.inf, 'continuous wave')]
EPS = [0.0, 0.5, 0.9, 0.99]
INPUTS = [('uniform', None), ('Gaussian, alpha = 4', 4.0)]

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '05_pulsed_pupils')
os.makedirs(OUT, exist_ok=True)

z = np.linspace(0.0, 40.0 * 2.0 * LAM / X_NA ** 2, 4000)
r0 = np.array([0.0])


def _fwhm(x, y):
    y = y / y.max()
    below = np.where(y < 0.5)[0]
    if not len(below):
        return np.nan
    i = below[0]
    return 2.0 * np.interp(0.5, [y[i], y[i - 1]], [x[i], x[i - 1]])


rows = []
print(f"{'input':<22} {'tau':<17} {'bandwidth/carrier':>18} {'eps':>6} "
      f"{'depth um':>10} {'extension':>10}", flush=True)
for label, at in INPUTS:
    for tau, tlab in TAUS:
        cfg = SimConfig(lam_c=LAM, X_NA=X_NA, n=N_MED, tau=tau,
                        N_freq=201 if np.isfinite(tau) else 3, N_theta=NT)
        apod = None if at is None else gaussian(at, cfg.sin2_alpha)
        frac = (0.0 if not np.isfinite(tau)
                else cfg.spectral_bandwidth / cfg.omega_c)
        base = None
        for eps in EPS:
            def _axial(k):
                if eps == 0.0:
                    A = compute_integrals(r0, z, k, cfg.alpha, NT,
                                          apodization=apod)
                else:
                    A = compute_integrals_annular(r0, z, k, cfg.alpha, eps, NT,
                                                  apodization=apod)
                return vec_intensity(A[0][:, 0], A[1][:, 0], A[2][:, 0])

            if not np.isfinite(tau):
                I_z = _axial(cfg.k_c)
            else:
                om = cfg.omega_grid()
                wt = cfg.spectral_power(om)
                I_z = np.zeros(len(z))
                for o, w in zip(om, wt):
                    if o <= 0:
                        continue
                    I_z += w * _axial(cfg.k_for_omega(o))
            d = _fwhm(z, I_z)
            if eps == 0.0:
                base = d
            rows.append(dict(input=label, tau=tlab,
                             tau_fs=(np.inf if not np.isfinite(tau)
                                     else tau * 1e15),
                             frac=frac, eps=eps, depth_um=d, gain=d / base))
            print(f'{label:<22} {tlab:<17} {frac:>18.3f} {eps:>6.2f} '
                  f'{d:>10.3f} {d / base:>10.4f}', flush=True)

np.savez_compressed(os.path.join(OUT, 'duration_sweep.npz'),
                    **{k: np.array([r[k] for r in rows]) for k in rows[0]})


def get(inp, tlab, eps, field):
    for r in rows:
        if (r['input'].startswith(inp) and r['tau'] == tlab
                and r['eps'] == eps):
            return r[field]
    return np.nan


print('\nDeparture from continuous wave, as a percentage')
print(f"{'input':<12} {'tau':<17} {'depth at eps 0':>15} "
      f"{'extension at eps 0.9':>21}")
for inp in ('uniform', 'Gaussian'):
    for tau, tlab in TAUS[:-1]:
        d0 = get(inp, tlab, 0.0, 'depth_um')
        dc = get(inp, 'continuous wave', 0.0, 'depth_um')
        g9 = get(inp, tlab, 0.9, 'gain')
        gc = get(inp, 'continuous wave', 0.9, 'gain')
        print(f'{inp:<12} {tlab:<17} {100 * (d0 / dc - 1):>14.3f}% '
              f'{100 * (g9 / gc - 1):>20.3f}%')

print('\nShortest duration still within a threshold of continuous wave')
for inp in ('uniform', 'Gaussian'):
    for thr in (1.0, 0.1):
        best = None
        for tau, tlab in TAUS[:-1]:
            d0 = get(inp, tlab, 0.0, 'depth_um')
            dc = get(inp, 'continuous wave', 0.0, 'depth_um')
            if abs(100 * (d0 / dc - 1)) <= thr:
                best = tlab
                break
        print(f'  {inp:<12} depth within {thr:>4.1f}% : '
              f'{best if best else "none of those run"}')
