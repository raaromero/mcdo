r"""Wavelength matters for a pulse, and only for a pulse.

The continuous-wave annular result is exactly scale invariant: the
Richards-Wolf integral sees z only through k z and r only through k r, so
changing color rescales every length and leaves every ratio alone. The
companion sweep verifies that to four decimal places.

A pulse breaks the argument. Its bandwidth is set by the duration, not the
color: at 1 fs the full width is 441 THz whatever the carrier. So the
fractional bandwidth is 0.74 at 500 nm and 1.47 at 1000 nm, and a pulse of the
same duration is relatively twice as broadband in the infrared. The prediction
is that both the bandwidth broadening and the Gaussian erosion grow with center
wavelength at fixed duration.

    python scripts/verify_wavelength_pulsed.py
    -> output/05_pulsed_pupils/wavelength_pulsed.npz
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

N_MED, NT, NFREQ = 1.3, 801, 101
NA_CASES = [0.1, 0.8, 1.2]
LAMS = [0.400, 0.500, 0.633, 0.750, 0.850, 1.000, 1.300]
EPS = [0.0, 0.5, 0.9, 0.99]
TAUS = [(np.inf, 'continuous wave'), (1e-15, '1 fs')]
INPUTS = [('uniform', None), ('Gaussian, alpha = 4', 4.0)]

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '05_pulsed_pupils')
os.makedirs(OUT, exist_ok=True)


def _fwhm(x, y):
    y = y / y.max()
    below = np.where(y < 0.5)[0]
    if not len(below):
        return np.nan
    i = below[0]
    return 2.0 * np.interp(0.5, [y[i], y[i - 1]], [x[i], x[i - 1]])


rows = []
print(f"{'lambda':>8} {'NA':>5} {'input':<22} {'eps':>6} {'pulse':<17} "
      f"{'depth um':>10} {'extension':>10}", flush=True)
for lam in LAMS:
  for X_NA in NA_CASES:
    z = np.linspace(0.0, 40.0 * 2.0 * lam / X_NA ** 2, 4000)
    r0 = np.array([0.0])
    for label, at in INPUTS:
        for tau, tlab in TAUS:
            cfg = SimConfig(lam_c=lam, X_NA=X_NA, n=N_MED, tau=tau,
                            N_freq=NFREQ if np.isfinite(tau) else 3,
                            N_theta=NT)
            apod = None if at is None else gaussian(at, cfg.sin2_alpha)
            base = None
            for eps in EPS:
                def _axial(k):
                    if eps == 0.0:
                        A0, A1, A2 = compute_integrals(r0, z, k, cfg.alpha,
                                                       NT, apodization=apod)
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
                rows.append(dict(lam=lam, na=X_NA, input=label, eps=eps,
                                 tau=tlab, depth_um=d, gain=d / base))
                print(f"{lam:>8.3f} {X_NA:>5.1f} {label:<22} {eps:>6.2f} {tlab:<17} "
                      f"{d:>10.3f} {d / base:>10.4f}", flush=True)

np.savez_compressed(
    os.path.join(OUT, 'wavelength_pulsed.npz'),
    **{k: np.array([r[k] for r in rows]) for k in rows[0]})


def get(lam, na, inp, eps, tau, field):
    for r in rows:
        if (r['lam'] == lam and r['na'] == na and r['input'].startswith(inp)
                and r['eps'] == eps and r['tau'] == tau):
            return r[field]
    return np.nan


print("\nBandwidth broadening of the unobstructed focus at 1 fs")
print(f"{'lambda':>8} {'bandwidth/carrier':>18} {'NA':>5} {'uniform':>10} {'Gaussian':>10}")
for lam in LAMS:
    frac = (4 * np.log(2) / 1e-15) / (2 * np.pi * 2.99792458e14 / lam)
    for na in NA_CASES:
        u = get(lam, na, 'uniform', 0.0, '1 fs', 'depth_um') / get(
            lam, na, 'uniform', 0.0, 'continuous wave', 'depth_um')
        g = get(lam, na, 'Gaussian', 0.0, '1 fs', 'depth_um') / get(
            lam, na, 'Gaussian', 0.0, 'continuous wave', 'depth_um')
        print(f"{lam:>8.3f} {frac:>18.2f} {na:>5.1f} {u:>10.4f} {g:>10.4f}")

print("\nExtension lost at 1 fs (%), by center wavelength and aperture")
print(f"{'lambda':>8} {'NA':>5} {'input':<22} " +
      "  ".join(f"eps {e:<5}" for e in EPS[1:]))
for lam in LAMS:
    for na in NA_CASES:
        for inp in ('uniform', 'Gaussian'):
            cells = []
            for e in EPS[1:]:
                cw = get(lam, na, inp, e, 'continuous wave', 'gain')
                p = get(lam, na, inp, e, '1 fs', 'gain')
                cells.append(f"{100 * (1 - p / cw):+8.2f}")
            print(f"{lam:>8.3f} {na:>5.1f} {inp:<22} " + "  ".join(cells))
