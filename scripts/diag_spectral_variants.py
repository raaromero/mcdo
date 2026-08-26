"""
Diagnostic: which spectral-integration variant reproduces the paper's numbers?

Paper targets (Rom03, X_NA=0.8, τ=1 fs):
  Fig 4a: S_transv = 1.062 ± 0.002,  S_axial = 1.057 ± 0.002  (NA-flat)
  Fig 4b: F ≈ 0.955–0.96 at τ=1 fs  (ref curve F=0.96τ^0.1)
  Fig 2(b): pulsed pedestal ≈ 0.09–0.10 at the cw zero ring (r=0.555 μm),
            ≈ 0.05 at r = 1 μm
Our paper-spec implementation gives S_tr=1.020, pedestal 0.067 — too thin.

Variants tested (weight × measure × window):
  omega_S_1.0    : ω-uniform, weight |E(ω)|²=exp(-Δ²/2a), ±FWHM/2  [stated spec]
  omega_amp_1.0  : ω-uniform, weight |E(ω)| =exp(-Δ²/4a), ±FWHM/2  [amplitude err]
  omega_S_1.5    : ω-uniform, weight |E(ω)|², ±0.75·FWHM           [wider window]
  lambda_S_noJac : λ-uniform 483nm–1674nm, weight |E(ω(λ))|², summed dλ
                   WITHOUT the |dω/dλ| Jacobian  [plausible 2003 implementation]
  lambda_amp_noJac: λ-uniform, weight |E(ω)|, no Jacobian
  omega_mcdo     : ω-uniform, weight exp(-Δ²/a)  [mcdo's too-narrow weight]

Each variant × intensity cut {ydir |I0-I2|², azim, xcut} → Linfoot S, F + pedestal.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from mcdo import SimConfig
from mcdo.rw_integrals import compute_integrals
from mcdo.linfoot import structural_content, fidelity

C_UM = 2.99792458e14

cfg = SimConfig(lam_c=0.750, X_NA=0.8, n=1.3, tau=1e-15, N_freq=201, N_theta=301)
a = 2 * np.log(2) / cfg.tau ** 2
wc = cfg.omega_c
Om = 4 * np.log(2) / cfg.tau          # FWHM of |E(ω)|²

# Linfoot grids = the paper's Fig-2 windows (201 pts, NA=0.8)
r_arr = np.linspace(-1.0, 1.0, 201)   # transverse ±1 μm
z_arr = np.linspace(-6.0, 6.0, 201)   # axial ±6 μm
z0 = np.array([0.0]); r0 = np.array([0.0])

cuts = {
    'ydir': lambda I0, I1, I2: np.abs(I0 - I2) ** 2,
    'azim': lambda I0, I1, I2: np.abs(I0)**2 + np.abs(I2)**2 + 2*np.abs(I1)**2,
    'xcut': lambda I0, I1, I2: np.abs(I0 + I2) ** 2 + 4 * np.abs(I1) ** 2,
}

# ── build variant grids ─────────────────────────────────────────────────────
def om_grid(x, N=201):
    hw = x * Om / 2.0
    return np.linspace(wc - hw, wc + hw, N)

om10 = om_grid(1.0)
om15 = om_grid(1.5)
lam  = np.linspace(2*np.pi*C_UM/om10[-1], 2*np.pi*C_UM/om10[0], 201)  # 483nm→1674nm
omL  = 2 * np.pi * C_UM / lam

S_w   = lambda om: np.exp(-(om - wc)**2 / (2*a))
amp_w = lambda om: np.exp(-(om - wc)**2 / (4*a))
narrow_w = lambda om: np.exp(-(om - wc)**2 / a)

variants = {
    # name: (omegas, weights, measure per sample)
    'omega_S_1.0 (paper spec)': (om10, S_w(om10),   np.full(201, om10[1]-om10[0])),
    'omega_amp_1.0'           : (om10, amp_w(om10), np.full(201, om10[1]-om10[0])),
    'omega_S_1.5'             : (om15, S_w(om15),   np.full(201, om15[1]-om15[0])),
    'lambda_S_noJac'          : (omL,  S_w(omL),    np.full(201, lam[1]-lam[0])),
    'lambda_amp_noJac'        : (omL,  amp_w(omL),  np.full(201, lam[1]-lam[0])),
    'omega_mcdo (narrow)'     : (om10, narrow_w(om10), np.full(201, om10[1]-om10[0])),
}

# ── cache RW integrals for every unique ω ──────────────────────────────────
unique_oms = np.unique(np.concatenate([v[0] for v in variants.values()]))
print(f"computing RW integrals at {len(unique_oms)} unique frequencies …")
cache = {}
for i, om in enumerate(unique_oms):
    if i % 100 == 0:
        print(f"  {i}/{len(unique_oms)}")
    k = cfg.n * om / C_UM
    I0, I1, I2 = compute_integrals(np.abs(r_arr), z0, k, cfg.alpha, cfg.N_theta)
    tr = (I0[0], I1[0], I2[0])
    I0, I1, I2 = compute_integrals(r0, z_arr, k, cfg.alpha, cfg.N_theta)
    ax = (I0[:, 0], I1[:, 0], I2[:, 0])
    cache[om] = (tr, ax)

# cw reference at ω_c
k_c = cfg.k_c
I0, I1, I2 = compute_integrals(np.abs(r_arr), z0, k_c, cfg.alpha, cfg.N_theta)
cw_tr_int = (I0[0], I1[0], I2[0])
I0, I1, I2 = compute_integrals(r0, z_arr, k_c, cfg.alpha, cfg.N_theta)
cw_ax_int = (I0[:, 0], I1[:, 0], I2[:, 0])

# ── evaluate matrix ─────────────────────────────────────────────────────────
print()
print("Paper targets:  S_tr=1.062  S_ax=1.057  F_tr~0.955-0.96  "
      "ped(0.555)~0.09-0.10  ped(1.0)~0.05")
print()
hdr = (f"{'variant':<26} {'cut':<5} {'S_tr':>7} {'S_ax':>7} "
       f"{'F_tr':>7} {'F_ax':>7} {'ped.555':>8} {'ped1.0':>7}")
print(hdr); print('-' * len(hdr))

r_pos = r_arr[r_arr >= 0]
for vname, (oms, ws, dms) in variants.items():
    for cname, f in cuts.items():
        cw_tr = f(*cw_tr_int); cw_tr = cw_tr / cw_tr.max()
        cw_ax = f(*cw_ax_int); cw_ax = cw_ax / cw_ax.max()
        pls_tr = np.zeros(201); pls_ax = np.zeros(201)
        for om, w, dm in zip(oms, ws, dms):
            tr, ax = cache[om]
            pls_tr += w * dm * f(*tr)
            pls_ax += w * dm * f(*ax)
        pls_tr /= pls_tr.max(); pls_ax /= pls_ax.max()
        S_tr = structural_content(cw_tr, pls_tr)
        S_ax = structural_content(cw_ax, pls_ax)
        F_tr = fidelity(cw_tr, pls_tr)
        F_ax = fidelity(cw_ax, pls_ax)
        I_pos = pls_tr[r_arr >= 0]
        ped555 = np.interp(0.555, r_pos, I_pos)
        ped10  = I_pos[-1]
        print(f"{vname:<26} {cname:<5} {S_tr:>7.4f} {S_ax:>7.4f} "
              f"{F_tr:>7.4f} {F_ax:>7.4f} {ped555:>8.4f} {ped10:>7.4f}")
    print()
