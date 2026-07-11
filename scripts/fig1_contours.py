"""
Fig. 1 — Contour plots of time-integrated focused intensity near the geometric
focus (X_NA=0.8, λ_c=750 nm, n=1.3).

(a) CW beam
(b) 1-fs pulsed beam (τ=1 fs)

Paper: peak value = 100, minimum = 0.
Contour labels at 0.5, 1, 1.8, 4, 6, 10, 20, 40, 60, 80, 100.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from mcdo import SimConfig
from mcdo.rw_integrals import compute_integrals

# ── Parameters (Rom03 Fig. 1) ──────────────────────────────────────────────
cfg = SimConfig(lam_c=0.750, X_NA=0.8, n=1.3, tau=1e-15, N_freq=201, N_theta=501)

# Grid: r ∈ [-2, 2] μm,  z ∈ [-6, 6] μm  (matches paper axis labels)
r_arr = np.linspace(-2.0, 2.0, 201)    # Δr = 0.02 μm
z_arr = np.linspace(-6.0, 6.0, 241)    # Δz = 0.05 μm

def _intensity(I0, I1, I2):
    """|I₀ − I₂|² — x-polarized beam, (y,z) plane (φ=π/2); same cut as Fig 2.

    This cut has true zeros (transverse zero ring, axial zeros), giving the
    island-contour topology of the paper's cw panel; the azimuthal average
    is smooth and cannot reproduce it.
    """
    return np.abs(I0 - I2) ** 2

print("Fig 1: computing CW 2-D intensity grid …")
I0_cw, I1_cw, I2_cw = compute_integrals(r_arr, z_arr, cfg.k_c, cfg.alpha, cfg.N_theta)
I_cw = _intensity(I0_cw, I1_cw, I2_cw)
I_cw_norm = 100.0 * I_cw / I_cw.max()   # peak = 100

print("Fig 1: computing 1-fs pulsed 2-D intensity grid …")
print("  (201 frequencies × 241 z × 201 r — may take 2–5 min)")
omegas = cfg.omega_grid()
S = cfg.spectral_power(omegas)
d_omega = omegas[1] - omegas[0]
I_pulsed = np.zeros_like(I_cw)
for j, (omega, s_j) in enumerate(zip(omegas, S)):
    if j % 50 == 0:
        lam_nm = 2*np.pi*2.998e14/omega*1e3 if omega > 0 else np.inf
        print(f"  freq {j+1}/{len(omegas)}  λ={lam_nm:.1f} nm")
    k_j = cfg.k_for_omega(omega)
    I0j, I1j, I2j = compute_integrals(r_arr, z_arr, k_j, cfg.alpha, cfg.N_theta)
    I_pulsed += s_j * _intensity(I0j, I1j, I2j) * d_omega
I_pulsed_norm = 100.0 * I_pulsed / I_pulsed.max()

# ── Plot ───────────────────────────────────────────────────────────────────
levels = [0.5, 1, 2, 4, 6, 10, 20, 30, 40, 60, 80, 100]

fig, axes = plt.subplots(2, 1, figsize=(4, 13))
fig.subplots_adjust(hspace=0.25)

RR, ZZ = np.meshgrid(r_arr, z_arr)

for ax, data, label in zip(axes, [I_cw_norm, I_pulsed_norm], ['(a) cw', '(b) 1-fs pulsed']):
    cs = ax.contour(RR, ZZ, data, levels=levels, colors='k', linewidths=0.7)
    ax.clabel(cs, fmt='%.4g', fontsize=6, inline=True)
    ax.set_xlabel('r (μm)', fontsize=10)
    ax.set_ylabel('z (μm)', fontsize=10)
    ax.set_title(label, fontsize=10)
    ax.set_xlim(-2, 2)
    ax.set_ylim(-6, 6)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(2))
    ax.tick_params(labelsize=8)
    ax.set_aspect(0.5)  # equal tick spacing: 1 μm in r = 2 μm in z visually

out = os.path.join(os.path.dirname(__file__), '..', 'output', '01_romallosa', 'fig1_contours.png')
fig.savefig(out, dpi=150, bbox_inches='tight')
plt.close(fig)
print(f"Saved → {out}")
