r"""The truncation sweep, paired with a pulse.

The alpha sweep exists only at continuous wave: five truncation parameters
crossed with seven obstruction ratios, and nothing to compare them against.
Every other parameter in this work has its pulsed counterpart, so this closes
the last unpaired axis.

The expectation from the rest of the study is that the extension a ring gives
is bandwidth invariant when the pupil is uniform and erodes once the pupil is
apodized, by an amount that should grow with the truncation parameter. That
is the prediction this tests across the whole alpha range rather than at the
single value alpha = 4.

    python scripts/verify_truncation_pulsed.py
    -> output/02_na_apodization/truncation_pulsed_dense.npz
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

LAM, N_MED, NT, NFREQ = 0.750, 1.3, 801, 101
NA_CASES = [0.8]
ALPHAS = [0.0, 1.0, 2.0, 4.0, 8.0]
EPS = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.93, 0.95, 0.96,
       0.97, 0.98, 0.985, 0.99]
TAUS = [(np.inf, 'continuous wave'), (1e-15, '1 fs')]

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '02_na_apodization')
os.makedirs(OUT, exist_ok=True)


def _fwhm(x, y):
    y = y / y.max()
    below = np.where(y < 0.5)[0]
    if not len(below):
        return np.nan
    i = below[0]
    return 2.0 * np.interp(0.5, [y[i], y[i - 1]], [x[i], x[i - 1]])


r0 = np.array([0.0])

rows = []
print(f"{'NA':>5} {'alpha':>6} {'eps':>6} {'pulse':<17} {'depth um':>10} "
      f"{'extension':>10}", flush=True)
for X_NA in NA_CASES:
  z = np.linspace(0.0, 40.0 * 2.0 * LAM / X_NA ** 2, 4000)
  for at in ALPHAS:
    for tau, tlab in TAUS:
        cfg = SimConfig(lam_c=LAM, X_NA=X_NA, n=N_MED, tau=tau,
                        N_freq=NFREQ if np.isfinite(tau) else 3, N_theta=NT)
        apod = None if at == 0.0 else gaussian(at, cfg.sin2_alpha)
        base = None
        for eps in EPS:
            def _axial(k):
                if eps == 0.0:
                    A0, A1, A2 = compute_integrals(r0, z, k, cfg.alpha, NT,
                                                   apodization=apod)
                else:
                    A0, A1, A2 = compute_integrals_annular(
                        r0, z, k, cfg.alpha, eps, NT, apodization=apod)
                return vec_intensity(A0[:, 0], A1[:, 0], A2[:, 0])

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
            rows.append(dict(na=X_NA, alpha_t=at, eps=eps, tau=tlab,
                             depth_um=d, gain=d / base))
            print(f"{X_NA:>5.1f} {at:>6.1f} {eps:>6.2f} {tlab:<17} "
                  f"{d:>10.3f} {d / base:>10.4f}", flush=True)

np.savez_compressed(
    os.path.join(OUT, 'truncation_pulsed_dense.npz'),
    **{k: np.array([r[k] for r in rows]) for k in rows[0]})


def get(at, eps, tau, field, na=0.8):
    for r in rows:
        if (r['na'] == na and r['alpha_t'] == at and r['eps'] == eps
                and r['tau'] == tau):
            return r[field]
    return np.nan


print("\nExtension lost at 1 fs (%), against the truncation parameter")
print(f"{'alpha':>6} " + "  ".join(f"eps {e:<5}" for e in EPS[1:]))
for at in ALPHAS:
    cells = []
    for e in EPS[1:]:
        cw = get(at, e, 'continuous wave', 'gain')
        p = get(at, e, '1 fs', 'gain')
        cells.append(f"{100 * (1 - p / cw):+8.2f}")
    print(f"{at:>6.1f} " + "  ".join(cells))

print("\nBandwidth lengthening of the unobstructed focus")
print(f"{'alpha':>6} {'depth CW':>10} {'depth 1 fs':>12} {'ratio':>8}")
for at in ALPHAS:
    a = get(at, 0.0, 'continuous wave', 'depth_um')
    b = get(at, 0.0, '1 fs', 'depth_um')
    print(f"{at:>6.1f} {a:>10.3f} {b:>12.3f} {b / a:>8.4f}")
