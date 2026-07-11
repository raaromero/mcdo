"""
Check 7 — axial counterpart of the NA-convergence study.

The radial (focal-plane) study is checks 1–3; this adds the axial direction:
  (a) axial profiles RW vs scalar (same A(θ)) for an NA family
  (b) axial FWHM (u units) vs NA against the paraxial sinc² value 11.13
  (c) axial RW-vs-scalar FWHM deviation vs NA, uniform and Gaussian α_t=4

On axis (v=0) only I₀ survives, so the axial RW−scalar difference isolates
the (1+cosθ) vector kernel; there is no x/y anisotropy on the axis.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo import SimConfig
from mcdo.rw_integrals import compute_integrals
from mcdo.debye import scalar_debye, axial_sinc2
from mcdo.apodization import gaussian as gaussian_apod

LAM, N_MED, NT = 0.750, 1.3, 1001
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '02_na_apodization')

u_arr = np.linspace(0.0, 25.0, 1001)
SINC2_FWHM_U = 2 * 4 * 1.39156   # paraxial axial FWHM in u: 11.132


def cfg_at(xna):
    return SimConfig(lam_c=LAM, X_NA=xna, n=N_MED, tau=np.inf, N_freq=3, N_theta=NT)


def rw_axial(cfg, apod=None):
    z = u_arr / (cfg.k_c * cfg.sin2_alpha)
    I0, _, I2 = compute_integrals(np.array([0.0]), z, cfg.k_c, cfg.alpha,
                                  NT, apodization=apod)
    I = np.abs(I0[:, 0] - I2[:, 0]) ** 2     # on axis I2=0; |I0|²
    return I / I.max()


def scalar_axial(cfg, apod=None):
    z = u_arr / (cfg.k_c * cfg.sin2_alpha)
    I = scalar_debye(np.array([0.0]), z, cfg.k_c, cfg.alpha, NT,
                     apodization=apod)[:, 0]
    return I / I.max()


def fwhm_u(I):
    half = I.max() / 2.0
    i = np.where(np.diff((I >= half).astype(int)))[0][0]
    return 2.0 * np.interp(half, [I[i + 1], I[i]], [u_arr[i + 1], u_arr[i]])


NA_FAMILY = [0.3, 0.6, 0.9, 1.2]
NA_COLORS = plt.cm.viridis(np.linspace(0.0, 0.85, len(NA_FAMILY)))
XNA_vals = np.arange(0.05, 1.26, 0.05)

# sweep: axial FWHM for RW & scalar, uniform & Gaussian α_t=4
fw = {('uniform', 'rw'): [], ('uniform', 'sc'): [],
      ('gauss4', 'rw'): [], ('gauss4', 'sc'): []}
for xna in XNA_vals:
    cfg = cfg_at(xna)
    A4 = gaussian_apod(4.0, cfg.sin2_alpha)
    fw[('uniform', 'rw')].append(fwhm_u(rw_axial(cfg)))
    fw[('uniform', 'sc')].append(fwhm_u(scalar_axial(cfg)))
    fw[('gauss4', 'rw')].append(fwhm_u(rw_axial(cfg, A4)))
    fw[('gauss4', 'sc')].append(fwhm_u(scalar_axial(cfg, A4)))
fw = {k: np.array(v) for k, v in fw.items()}

dev_uni = 100 * np.abs(fw[('uniform', 'rw')] / fw[('uniform', 'sc')] - 1)
dev_g4 = 100 * np.abs(fw[('gauss4', 'rw')] / fw[('gauss4', 'sc')] - 1)

print("Axial RW-vs-scalar FWHM deviation thresholds:")
for name, dev in [('uniform', dev_uni), ('Gaussian α_t=4', dev_g4)]:
    t1 = XNA_vals[np.argmax(dev > 1.0)] if (dev > 1.0).any() else np.nan
    t5 = XNA_vals[np.argmax(dev > 5.0)] if (dev > 5.0).any() else np.nan
    print(f"  {name:<16} >1% at X_NA={t1:.2f}   >5% at X_NA={t5}")
print("  (radial x-cut for comparison: 1% @ 0.30, 5% @ 0.60)")

# ── Figure ─────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(14, 4.4))
fig.suptitle('Check 7 — axial direction: RW vs scalar Debye vs NA '
             '(on-axis the vector effect is the (1+cosθ) kernel; no x/y anisotropy)',
             fontsize=11)

ax = axes[0]
ax.plot(u_arr, axial_sinc2(u_arr), '-', color='0.7', lw=4,
        label='paraxial sinc²(u/4)')
for xna, col in zip(NA_FAMILY, NA_COLORS):
    cfg = cfg_at(xna)
    ax.plot(u_arr, rw_axial(cfg), color=col, lw=1.3, label=f'RW  X_NA={xna}')
    ax.plot(u_arr, scalar_axial(cfg), color=col, lw=1.1, ls='--',
            label=f'scalar  X_NA={xna}')
ax.set_yscale('log'); ax.set_ylim(1e-7, 1.5)
ax.set_xlabel('u (optical units)'); ax.set_ylabel('normalized intensity')
ax.set_title('(a) axial profiles: RW (solid) vs scalar (dashed)', fontsize=10)
ax.legend(fontsize=6.5, ncol=2)

ax = axes[1]
ax.axhline(SINC2_FWHM_U, color='0.7', lw=3, label='paraxial 11.13')
ax.plot(XNA_vals, fw[('uniform', 'rw')], 'C0o-', ms=3.5, lw=1.1,
        label='RW uniform')
ax.plot(XNA_vals, fw[('uniform', 'sc')], 'C0^:', ms=3.5, lw=1.1,
        label='scalar uniform')
ax.plot(XNA_vals, fw[('gauss4', 'rw')], 'C3s-', ms=3.5, lw=1.1,
        label='RW Gaussian α_t=4')
ax.plot(XNA_vals, fw[('gauss4', 'sc')], 'C3v:', ms=3.5, lw=1.1,
        label='scalar Gaussian α_t=4')
ax.set_xlabel('X_NA'); ax.set_ylabel('axial FWHM (u units)')
ax.set_title('(b) axial FWHM vs NA', fontsize=10)
ax.legend(fontsize=8)

ax = axes[2]
ax.plot(XNA_vals, dev_uni, 'C0o-', ms=3.5, lw=1.1, label='uniform')
ax.plot(XNA_vals, dev_g4, 'C3s--', ms=3.5, lw=1.1, label='Gaussian α_t=4')
ax.axhline(1, color='gray', lw=0.6, ls=':')
ax.axhline(5, color='gray', lw=0.6, ls='--')
ax.set_yscale('log'); ax.set_ylim(1e-3, 30)
ax.set_xlabel('X_NA'); ax.set_ylabel('|axial FWHM deviation| RW vs scalar (%)')
ax.set_title('(c) axial vector-effect magnitude', fontsize=10)
ax.legend(fontsize=8)

plt.tight_layout()
out = os.path.join(OUT, 'check7_axial_vs_na.png')
fig.savefig(out, dpi=150, bbox_inches='tight')
plt.close(fig)
print(f"Saved → {out}")
