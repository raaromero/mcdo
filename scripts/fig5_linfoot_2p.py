"""
Fig. 5 — Two-photon excitation microscope: Fidelity F and Structural Content S
vs pulse width τ  (X_NA = 0.8, λ_c = 750 nm).

Two-photon PSF = normalized |E(P)|⁴ = (normalized |E(P)|²)²  [Rom03 §III].

Linfoot arrays: 201 points on the paper's Fig-2 windows at X_NA=0.8:
  transverse ±1 μm, axial ±6 μm (same windows as fig4_linfoot.py).

Paper reference curves (caption — local fits):
  Curve 1  F = τ^{0.01}
  Curve 2  S = 0.97·τ^{0.04}
Paper values at τ=1 fs (read from figure): S ≈ 0.985, F ≈ 0.999.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo import SimConfig, transverse_profile, axial_profile, linfoot_profile

LAM_C = 0.750
N_MED = 1.3
N_PTS = 201

r_half = np.linspace(0.0, 1.0, (N_PTS + 1) // 2)    # ±1 μm transverse
z_arr = np.linspace(-6.0, 6.0, N_PTS)               # ±6 μm axial


def _mirror(I_half):
    return np.concatenate([I_half[::-1][:-1], I_half])


def _2p(I):
    """Two-photon PSF: square the peak-normalized single-photon PSF."""
    I = np.asarray(I, dtype=float)
    if I.max() > 0:
        I = I / I.max()
    return I ** 2


tau_vals_fs = [1, 1.2, 1.5, 2, 3, 5, 7, 10, 20, 50, 100]
F_tr, S_tr, F_ax, S_ax = [], [], [], []

for tau_fs in tau_vals_fs:
    cfg = SimConfig(lam_c=LAM_C, X_NA=0.8, n=N_MED, tau=tau_fs * 1e-15,
                    N_freq=201, N_theta=501)
    print(f"  τ={tau_fs} fs …")

    cw_tr = _2p(_mirror(transverse_profile(r_half, cfg, pulsed=False)))
    pls_tr = _2p(_mirror(transverse_profile(r_half, cfg, pulsed=True)))
    cw_ax = _2p(axial_profile(z_arr, cfg, pulsed=False))
    pls_ax = _2p(axial_profile(z_arr, cfg, pulsed=True))

    lf_tr = linfoot_profile(cw_tr, pls_tr)
    lf_ax = linfoot_profile(cw_ax, pls_ax)
    F_tr.append(lf_tr['F']); S_tr.append(lf_tr['S'])
    F_ax.append(lf_ax['F']); S_ax.append(lf_ax['S'])
    print(f"    transv  F={lf_tr['F']:.4f}  S={lf_tr['S']:.4f}")
    print(f"    axial   F={lf_ax['F']:.4f}  S={lf_ax['S']:.4f}")

# ── Plot ───────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 5))
fig.suptitle('Fig. 5 — Two-photon microscope: F and S vs pulse width  (X_NA=0.8)',
             fontsize=11)

tau_arr = np.array(tau_vals_fs, dtype=float)
ax.plot(tau_arr, F_ax, 's', ms=7, mfc='white', mec='k', label='F (axial)')
ax.plot(tau_arr, S_ax, 's', ms=7, mfc='k',     mec='k', label='S (axial)')
ax.plot(tau_arr, F_tr, 'o', ms=7, mfc='white', mec='k', label='F (transv)')
ax.plot(tau_arr, S_tr, 'o', ms=7, mfc='k',     mec='k', label='S (transv)')
ax.axhline(1.0, color='gray', lw=0.8, ls=':')

tau_ref = np.logspace(0, 2, 100)
ax.plot(tau_ref, tau_ref ** 0.01,        'k-',  lw=1, label='1: F=τ⁰·⁰¹')
ax.plot(tau_ref, 0.97 * tau_ref ** 0.04, 'k--', lw=1, label='2: S=0.97τ⁰·⁰⁴')

ax.set_xscale('log')
ax.set_xlabel('Pulse width (fsec)', fontsize=10)
ax.set_ylabel('Criterion value', fontsize=10)
ax.set_xlim(1, 100)
ax.set_ylim(0.965, 1.005)
ax.legend(fontsize=8, loc='lower right')
plt.tight_layout()

out = os.path.join(os.path.dirname(__file__), '..', 'output', '01_romallosa', 'fig5_linfoot_2p.png')
fig.savefig(out, dpi=150, bbox_inches='tight')
plt.close(fig)
print(f"Saved → {out}")
