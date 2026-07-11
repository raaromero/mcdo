"""
Fig. 2 — Transverse and axial intensity profiles, CW vs 1-fs pulsed.
(X_NA=0.8, λ_c=750 nm, n=1.3)

Intensity = |I₀ − I₂|² (x-polarized beam, scan along y, φ=π/2): the only cut
with true zeros, matching the paper's "cw contains zero points" statement.

Pulsed: Eq. 10 spectral sum, 201 frequencies over the FULL positive spectrum
ω ∈ (0, 2ω_c) — validated against the paper's Linfoot values (S≈1.06, F≈0.96)
and the Fig. 2 pedestal (≈0.05 at r=1 μm).

NOTE on the published figure: the paper's panel labels are swapped. Its
panel (a) "r (μm)" on ±6 μm shows half-max at ±1.2 μm and zeros at ±3 μm —
that is the AXIAL profile (FWHM 2.42 μm, first zero 3.05 μm). Its panel (b)
"z (μm)" on ±1 μm shows zeros at ±0.555 μm with sidelobes at ±0.7 μm — that
is the TRANSVERSE profile. We plot each profile on the paper's window for
direct comparison, with correct labels.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo import SimConfig, transverse_profile, axial_profile

cfg = SimConfig(lam_c=0.750, X_NA=0.8, n=1.3, tau=1e-15, N_freq=201, N_theta=501)

r_arr = np.linspace(0.0, 1.0, 201)     # transverse: ±1 μm window (paper Fig 2b)
z_arr = np.linspace(-6.0, 6.0, 401)    # axial: ±6 μm window (paper Fig 2a)

print("Fig 2: CW transverse + axial …")
I_cw_r = transverse_profile(r_arr, cfg, pulsed=False)
I_cw_z = axial_profile(z_arr, cfg, pulsed=False)

print("Fig 2: pulsed transverse …")
I_pls_r = transverse_profile(r_arr, cfg, pulsed=True, verbose=True)
print("Fig 2: pulsed axial …")
I_pls_z = axial_profile(z_arr, cfg, pulsed=True, verbose=True)

# Mirror transverse for display
r_full = np.concatenate([-r_arr[::-1][:-1], r_arr])
I_cw_r_full  = np.concatenate([I_cw_r[::-1][:-1],  I_cw_r])
I_pls_r_full = np.concatenate([I_pls_r[::-1][:-1], I_pls_r])

def fwhm(x, y):
    half = y.max() / 2.0
    above = y >= half
    idx = np.where(np.diff(above.astype(int)))[0]
    def interp(i):
        x0, x1, y0, y1 = x[i], x[i+1], y[i], y[i+1]
        return x0 + (half - y0) / (y1 - y0) * (x1 - x0) if abs(y1-y0) > 1e-30 else x0
    if len(idx) < 2:
        return np.nan
    return interp(idx[-1]) - interp(idx[0])

print(f"  Transverse FWHM — CW: {fwhm(r_full, I_cw_r_full)*1e3:.1f} nm   "
      f"pulsed: {fwhm(r_full, I_pls_r_full)*1e3:.1f} nm")
print(f"  Axial FWHM      — CW: {fwhm(z_arr, I_cw_z)*1e3:.1f} nm   "
      f"pulsed: {fwhm(z_arr, I_pls_z)*1e3:.1f} nm")
# pedestal diagnostics vs paper scan
i555 = np.argmin(np.abs(r_arr - 0.555))
print(f"  Pulsed pedestal at zero ring (0.555 μm): {I_pls_r[i555]:.4f}  [paper ≈0.09-0.10]")
print(f"  Pulsed pedestal at r=1 μm: {I_pls_r[-1]:.4f}  [paper ≈0.05]")

# ── Plot ───────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
fig.suptitle(r'Fig. 2 — Intensity profiles ($X_{NA}=0.8$, $\lambda_c=750$ nm)'
             '\n(paper shows these panels with swapped axis labels)',
             fontsize=10)

ax = axes[0]
ax.plot(r_full, I_cw_r_full,  'k-', lw=1.5, label='cw')
ax.plot(r_full, I_pls_r_full, 'k:', lw=1.8, label='pulsed (1 fs)')
ax.set_xlabel('r (μm)')
ax.set_ylabel('Normalized Intensity')
ax.set_title('Transverse  (z = 0)   [paper panel b]', fontsize=10)
ax.set_xlim(-1.0, 1.0)
ax.set_ylim(0, 1.0)
ax.set_yticks(np.arange(0, 1.05, 0.1))
ax.legend(fontsize=9)

ax = axes[1]
ax.plot(z_arr, I_cw_z,  'k-', lw=1.5, label='cw')
ax.plot(z_arr, I_pls_z, 'k:', lw=1.8, label='pulsed (1 fs)')
ax.set_xlabel('z (μm)')
ax.set_ylabel('Normalized Intensity')
ax.set_title('Axial  (r = 0)   [paper panel a]', fontsize=10)
ax.set_xlim(-6.0, 6.0)
ax.set_ylim(0, 1.0)
ax.set_yticks(np.arange(0, 1.05, 0.1))
ax.legend(fontsize=9)

plt.tight_layout()
out = os.path.join(os.path.dirname(__file__), '..', 'output', '01_romallosa', 'fig2_profiles.png')
fig.savefig(out, dpi=150, bbox_inches='tight')
plt.close(fig)
print(f"Saved → {out}")
