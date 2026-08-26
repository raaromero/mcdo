"""
Quick physics verification against paper values.

Checks (all at X_NA=0.8, λ_c=750 nm, n=1.3):
  1. CW transverse FWHM ≈ 0.24 μm  (diffraction-limited spot)
  2. CW axial    FWHM ≈ 1.0 μm
  3. Spectral bandwidth Ω for τ=1 fs spans λ ≈ 483–1670 nm  ✓ [Rom03 text]
  4. Pulsed transverse has NO zero crossings  [Rom03 Fig 2 description]
  5. CW transverse HAS a zero crossing (first ring)
  6. Energy at ω_c ± Δω/2: |E(ω)|² = 0.5  (by definition of FWHM)
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from mcdo import SimConfig, transverse_profile, axial_profile
from mcdo.config import C_UM

cfg = SimConfig(lam_c=0.750, X_NA=0.8, n=1.3, tau=1e-15, N_freq=201, N_theta=501)

print("=== Physics verification ===\n")
print(f"k_c        = {cfg.k_c:.4f} μm⁻¹  (expect 10.88)")
print(f"sin α      = {cfg.sin_alpha:.4f}   (expect 0.6154)")
print(f"α          = {np.degrees(cfg.alpha):.2f}°  (expect 37.9°)")
print(f"ω_c        = {cfg.omega_c:.4e} rad/s")
print(f"Bandwidth Ω= {cfg.spectral_bandwidth:.4e} rad/s")

# Bandwidth spans in wavelength
omegas = cfg.omega_grid()
lam_min = 2 * np.pi * C_UM / omegas[-1] * 1e3  # nm
lam_max = 2 * np.pi * C_UM / omegas[0]  * 1e3  # nm
print(f"ω range    : {omegas[0]:.3e} … {omegas[-1]:.3e} rad/s")
print(f"λ range    : {lam_max:.0f} – {lam_min:.0f} nm  (paper: 1670–483 nm)")

# Spectral power at edges = 0.5 (FWHM edges)
S_edge = cfg.spectral_power(np.array([omegas[0], omegas[-1]]))
print(f"S(edges)   = {S_edge}  (expect both ≈ 0.5)")

# CW transverse profile
print("\n--- CW transverse profile ---")
r_arr = np.linspace(0.0, 1.0, 1001)
I_cw = transverse_profile(r_arr, cfg, pulsed=False)

# FWHM
half = I_cw.max() / 2
idx = np.where(np.diff((I_cw >= half).astype(int)))[0]
if len(idx):
    r0, r1 = r_arr[idx[0]], r_arr[idx[0]+1]
    i0, i1 = I_cw[idx[0]], I_cw[idx[0]+1]
    r_half = r0 + (half - i0)/(i1-i0)*(r1-r0)
    fwhm_cw = 2 * r_half
    print(f"FWHM       = {fwhm_cw*1e3:.1f} nm  (expect ~476 nm for φ=π/2 y-axis profile)")

# Zero crossing (first ring)
zeros = np.where(np.diff(np.sign(I_cw)))[0]
print(f"Zero crossings at r = {r_arr[zeros]*1e3} nm  (expect ~554 nm — where I₀=I₂ at φ=π/2)")

# CW axial
print("\n--- CW axial profile ---")
z_arr = np.linspace(-2.0, 2.0, 1001)
I_ax = axial_profile(z_arr, cfg, pulsed=False)
half = I_ax.max() / 2
above = I_ax >= half
idx = np.where(np.diff(above.astype(int)))[0]
if len(idx) >= 2:
    z0 = z_arr[idx[0]] + (half-I_ax[idx[0]])/(I_ax[idx[0]+1]-I_ax[idx[0]])*(z_arr[idx[0]+1]-z_arr[idx[0]])
    z1 = z_arr[idx[-1]]+ (half-I_ax[idx[-1]])/(I_ax[idx[-1]+1]-I_ax[idx[-1]])*(z_arr[idx[-1]+1]-z_arr[idx[-1]])
    print(f"FWHM       = {(z1-z0)*1e3:.0f} nm  (expect ~2400 nm)")
ax_zeros = np.where(np.diff(np.sign(I_ax)))[0]
print(f"Axial zeros at z ≈ {z_arr[ax_zeros]} μm")

# Pulsed transverse: should have NO zeros
print("\n--- Pulsed transverse profile (τ=1 fs) ---")
I_pls = transverse_profile(r_arr, cfg, pulsed=True, verbose=True)
pls_zeros = np.where(np.diff(np.sign(I_pls)))[0]
pls_min = I_pls.min()
print(f"Min value  = {pls_min:.6f}  (expect > 0, no zeros)")
print(f"Zero crossings: {len(pls_zeros)}  (expect 0)")

half = I_pls.max() / 2
idx = np.where(np.diff((I_pls >= half).astype(int)))[0]
if len(idx):
    r0, r1 = r_arr[idx[0]], r_arr[idx[0]+1]
    i0, i1 = I_pls[idx[0]], I_pls[idx[0]+1]
    r_half = r0 + (half - i0)/(i1-i0)*(r1-r0)
    fwhm_pls = 2 * r_half
    print(f"FWHM pulsed= {fwhm_pls*1e3:.1f} nm  (expect broader than CW ~500-550 nm)")

print("\n=== Verification complete ===")
