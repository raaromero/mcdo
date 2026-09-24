r"""Does anything in the annular result depend on wavelength?

Every sweep in this work runs at 750 nm. That is a gap in coverage, and it is
also a testable prediction rather than a blank: the closed-form extension

    (1 - cos alpha) / (cos theta_in - cos alpha)

contains no wavelength at all. The extension an annulus gives should therefore
be identical at every color, while the absolute depth of focus scales as 1/k,
that is linearly with wavelength.

This runs the continuous-wave grid at three wavelengths spanning the visible
and near infrared and checks both halves: extension invariant, absolute depth
proportional to wavelength.

    python scripts/verify_wavelength.py
    -> output/03_annular/wavelength_sweep.npz
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

N_MED, NT = 1.3, 801
LAMS = [0.400, 0.500, 0.633, 0.750, 0.850, 1.000, 1.300]
NA_CASES = [0.1, 0.8, 1.2]
EPS = [0.0, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99]
INPUTS = [('uniform', None), ('Gaussian, alpha = 4', 4.0)]

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '03_annular')
os.makedirs(OUT, exist_ok=True)


def _fwhm(x, y):
    y = y / y.max()
    below = np.where(y < 0.5)[0]
    if not len(below):
        return np.nan
    i = below[0]
    return 2.0 * np.interp(0.5, [y[i], y[i - 1]], [x[i], x[i - 1]])


rows = []
print(f"{'lambda':>8} {'NA':>5} {'input':<22} {'eps':>6} "
      f"{'depth um':>10} {'width nm':>10} {'extension':>10}", flush=True)
for lam in LAMS:
    for xna in NA_CASES:
        cfg = SimConfig(lam_c=lam, X_NA=xna, n=N_MED, tau=np.inf,
                        N_freq=3, N_theta=NT)
        # windows scale with wavelength and aperture, so every color is
        # sampled on the same grid in optical units
        r = np.linspace(0.0, 4.0 * lam / xna, 900)
        z = np.linspace(0.0, 40.0 * 2.0 * lam / xna ** 2, 4000)
        r0, z0 = np.array([0.0]), np.array([0.0])
        for label, at in INPUTS:
            apod = None if at is None else gaussian(at, cfg.sin2_alpha)
            base = None
            for eps in EPS:
                def _int(rr, zz):
                    if eps == 0.0:
                        return compute_integrals(rr, zz, cfg.k_c, cfg.alpha,
                                                 NT, apodization=apod)
                    return compute_integrals_annular(rr, zz, cfg.k_c, cfg.alpha,
                                                     eps, NT, apodization=apod)
                A0, A1, A2 = _int(r, z0)
                B0, B1, B2 = _int(r0, z)
                w = _fwhm(r, vec_intensity(A0[0], A1[0], A2[0])) * 1000.0
                d = _fwhm(z, vec_intensity(B0[:, 0], B1[:, 0], B2[:, 0]))
                if eps == 0.0:
                    base = d
                rows.append(dict(lam=lam, na=xna, input=label, eps=eps,
                                 depth_um=d, width_nm=w, gain=d / base))
                print(f"{lam:>8.3f} {xna:>5.1f} {label:<22} {eps:>6.2f} "
                      f"{d:>10.3f} {w:>10.1f} {d / base:>10.4f}", flush=True)

np.savez_compressed(
    os.path.join(OUT, 'wavelength_sweep.npz'),
    **{k: np.array([r[k] for r in rows]) for k in rows[0]})

print("\nIs the extension the same at every wavelength?  (uniform)")
for xna in NA_CASES:
    for eps in EPS[1:]:
        g = [next(r['gain'] for r in rows if r['lam'] == L and r['na'] == xna
                  and r['input'] == 'uniform' and r['eps'] == eps)
             for L in LAMS]
        print(f"  NA {xna:<4} eps {eps:<5} " +
              "  ".join(f"{x:7.4f}" for x in g) +
              f"   spread {100 * (max(g) / min(g) - 1):+.3f}%")

print("\nDoes the absolute depth scale with wavelength?  (uniform, eps 0)")
for xna in NA_CASES:
    d = [next(r['depth_um'] for r in rows if r['lam'] == L and r['na'] == xna
              and r['input'] == 'uniform' and r['eps'] == 0.0) for L in LAMS]
    ref = LAMS.index(0.750)
    ratio = [d[i] / (LAMS[i] / LAMS[ref]) / d[ref] for i in range(len(LAMS))]
    print(f"  NA {xna:<4} depths " + "  ".join(f"{x:9.3f}" for x in d))
    print(f"  {'':<8} scaled  " + "  ".join(f"{x:9.4f}" for x in ratio))
