r"""Where the scalar approximation stops describing the focus, against truncation.

The scalar Debye integral and the full vector calculation agree at low
numerical aperture and diverge as the cone opens. Where that divergence becomes
important depends on what is measured, and the earlier comparison ran uniform
illumination only. This adds the truncation parameter as a second axis.

The physical expectation: a truncated pupil concentrates the light near the
axis, so the rays that actually carry energy converge at shallower angles than
the rim allows. The scalar description should then survive to a higher stated
aperture.

Three criteria are reported at each aperture and truncation, because they do
not agree with one another:

    the change in full width at half maximum
    root-mean-square error with the profiles matched at their peaks
    root-mean-square error with the profiles matched on transmitted energy

Both root-mean-square figures are area weighted, since the difference at radius
r occupies an annulus of area proportional to r.

    python scripts/verify_scalar_breakdown.py
    -> output/02_na_apodization/scalar_breakdown.npz
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np

from mcdo import SimConfig
from mcdo.apodization import gaussian
from mcdo.components import full as vec_intensity
from mcdo.debye import scalar_debye
from mcdo.rw_integrals import compute_integrals

LAM, N_MED, NT = 0.750, 1.3, 801
ALPHAS = [0.0, 1.0, 2.0, 4.0, 8.0]
XNA = np.round(np.arange(0.10, 1.26, 0.05), 3)

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '02_na_apodization')
os.makedirs(OUT, exist_ok=True)

v = np.linspace(0.0, 12.0, 3000)          # optical radial coordinate


def pair(xna, at):
    """Vector and scalar transverse profiles on a common optical grid."""
    cfg = SimConfig(lam_c=LAM, X_NA=xna, n=N_MED, tau=np.inf,
                    N_freq=3, N_theta=NT)
    apod = None if at == 0.0 else gaussian(at, cfg.sin2_alpha)
    r = v / (cfg.k_c * cfg.sin_alpha)
    z0 = np.array([0.0])
    I0, I1, I2 = compute_integrals(r, z0, cfg.k_c, cfg.alpha, NT,
                                   apodization=apod)
    vec = vec_intensity(I0[0], I1[0], I2[0])
    # scalar_debye returns an intensity, not a field; squaring it here was a
    # bug that put the deviation at 39% before the comparison even began
    sca = scalar_debye(r, z0, cfg.k_c, cfg.alpha, NT, apodization=apod)[0]
    return vec, sca


def fwhm(y):
    y = y / y.max()
    below = np.where(y < 0.5)[0]
    if not len(below):
        return np.nan
    i = below[0]
    return 2.0 * np.interp(0.5, [y[i], y[i - 1]], [v[i], v[i - 1]])


def rmse(a, b):
    """Area-weighted root-mean-square difference of two normalized profiles."""
    return float(np.sqrt(np.trapezoid((a - b) ** 2 * v, v)
                         / np.trapezoid(v, v)))


rows = []
print(f"{'alpha':>6} {'NA':>6} {'FWHM dev':>10} {'RMSE peak':>11} "
      f"{'RMSE energy':>13}", flush=True)
for at in ALPHAS:
    for xna in XNA:
        vec, sca = pair(xna, at)
        dev = 100.0 * abs(fwhm(vec) / fwhm(sca) - 1.0)
        pv, ps = vec / vec.max(), sca / sca.max()
        ev = vec / np.trapezoid(vec * v, v)
        es = sca / np.trapezoid(sca * v, v)
        scale = max(ev.max(), es.max())
        rows.append(dict(alpha_t=at, na=float(xna), fwhm_dev=dev,
                         rmse_peak=rmse(pv, ps),
                         rmse_energy=rmse(ev / scale, es / scale)))
        print(f'{at:>6.1f} {xna:>6.2f} {dev:>9.3f}% {rmse(pv, ps):>11.5f} '
              f'{rmse(ev / scale, es / scale):>13.5f}', flush=True)

np.savez_compressed(os.path.join(OUT, 'scalar_breakdown.npz'),
                    **{k: np.array([r[k] for r in rows]) for k in rows[0]})


def crossing(at, field, threshold):
    xs = [r['na'] for r in rows if r['alpha_t'] == at]
    ys = [r[field] for r in rows if r['alpha_t'] == at]
    for x, y in zip(xs, ys):
        if y >= threshold:
            return x
    return np.nan


print('\nNumerical aperture at which each criterion is first exceeded')
print(f"{'alpha':>6} {'FWHM 1%':>10} {'FWHM 5%':>10} "
      f"{'RMSE peak 0.01':>16} {'RMSE energy 0.01':>18}")
for at in ALPHAS:
    print(f'{at:>6.1f} {crossing(at, "fwhm_dev", 1.0):>10.2f} '
          f'{crossing(at, "fwhm_dev", 5.0):>10.2f} '
          f'{crossing(at, "rmse_peak", 0.01):>16.2f} '
          f'{crossing(at, "rmse_energy", 0.01):>18.2f}')
