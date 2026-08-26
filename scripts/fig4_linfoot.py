"""
Fig. 4 — Single-photon microscope: Fidelity F and Structural Content S.

(a) F, S vs NA  for τ = 1 fs,  λ_c = 750 nm
(b) F, S vs τ   for X_NA = 0.8, λ_c = 750 nm  (log scale)

Linfoot arrays: 201 points (m = −100 … 100), sampled in OPTICAL coordinates
so the window scales with NA — this reproduces the paper's NA-insensitivity:
  transverse: v ∈ ±40.2   (= ±6 μm at X_NA=0.8, the paper's Fig-2a window)
  axial:      u ∈ ±24.74  (= ±6 μm at X_NA=0.8)

Validation at X_NA=0.8, τ=1 fs (full-spectrum ω-grid, ±6 μm transverse window):
  ours: S_tr=1.060  S_ax=1.058  F_tr=0.957  F_ax=0.961
  paper: S_tr=1.062  S_ax=1.057  F≈0.955–0.96
  (S_tr=⟨a²⟩/⟨r²⟩ weights the slow pulsed pedestal; ±1 μm truncates it → 1.053.)

Paper reference curves (Fig. 4b caption — local fits near τ≈1 fs):
  Curve 1  F = 0.96·τ^{0.1}
  Curve 2  S = 1.06·τ^{−0.1}
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo.style import apply as _apply_style
_apply_style()

from mcdo import SimConfig, transverse_profile, axial_profile, linfoot_profile

LAM_C = 0.750
N_MED = 1.3
V_MAX = 40.21    # = k_c·sinα·(6 μm) at X_NA=0.8 — must capture the slow pulsed
#                  transverse pedestal (paper Fig 2a spans ±6 μm). At ±1 μm the
#                  pedestal is truncated and S_tr is undercounted (1.053 vs 1.060).
U_MAX = 24.744   # = k_c·sin²α·(6 μm) at X_NA=0.8
N_PTS = 201


def _windows(cfg):
    """Per-NA physical windows equal to fixed optical-coordinate windows."""
    r_max = V_MAX / (cfg.k_c * cfg.sin_alpha)
    z_max = U_MAX / (cfg.k_c * cfg.sin2_alpha)
    return r_max, z_max


def _profiles(cfg):
    """201-pt transverse and axial profiles (CW + pulsed), normalized."""
    r_max, z_max = _windows(cfg)
    r_half = np.linspace(0.0, r_max, (N_PTS + 1) // 2)   # 101 pts → mirror to 201
    z_arr = np.linspace(-z_max, z_max, N_PTS)

    def mirror(I_half):
        return np.concatenate([I_half[::-1][:-1], I_half])

    cw_tr = mirror(transverse_profile(r_half, cfg, pulsed=False))
    pls_tr = mirror(transverse_profile(r_half, cfg, pulsed=True))
    cw_ax = axial_profile(z_arr, cfg, pulsed=False)
    pls_ax = axial_profile(z_arr, cfg, pulsed=True)
    return cw_tr, pls_tr, cw_ax, pls_ax


# ── Panel (a): F, S vs NA   (τ = 1 fs) ─────────────────────────────────────
print("Fig 4(a): sweep NA, τ=1 fs …")
XNA_vals = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2])

F_tr_a, S_tr_a, F_ax_a, S_ax_a = [], [], [], []
for xna in XNA_vals:
    cfg = SimConfig(lam_c=LAM_C, X_NA=xna, n=N_MED, tau=1e-15, N_freq=201, N_theta=501)
    cw_tr, pls_tr, cw_ax, pls_ax = _profiles(cfg)
    lf_tr = linfoot_profile(cw_tr, pls_tr)
    lf_ax = linfoot_profile(cw_ax, pls_ax)
    F_tr_a.append(lf_tr['F']); S_tr_a.append(lf_tr['S'])
    F_ax_a.append(lf_ax['F']); S_ax_a.append(lf_ax['S'])
    print(f"  NA={xna:.1f}:  transv F={lf_tr['F']:.4f} S={lf_tr['S']:.4f}   "
          f"axial F={lf_ax['F']:.4f} S={lf_ax['S']:.4f}")

# ── Panel (b): F, S vs τ   (X_NA = 0.8) ────────────────────────────────────
print("Fig 4(b): sweep τ, X_NA=0.8 …")
tau_vals_fs = [1, 1.2, 1.5, 2, 3, 5, 7, 10, 20, 50, 100]

F_tr_b, S_tr_b, F_ax_b, S_ax_b = [], [], [], []
for tau_fs in tau_vals_fs:
    cfg = SimConfig(lam_c=LAM_C, X_NA=0.8, n=N_MED, tau=tau_fs * 1e-15,
                    N_freq=201, N_theta=501)
    cw_tr, pls_tr, cw_ax, pls_ax = _profiles(cfg)
    lf_tr = linfoot_profile(cw_tr, pls_tr)
    lf_ax = linfoot_profile(cw_ax, pls_ax)
    F_tr_b.append(lf_tr['F']); S_tr_b.append(lf_tr['S'])
    F_ax_b.append(lf_ax['F']); S_ax_b.append(lf_ax['S'])
    print(f"  τ={tau_fs} fs:  transv F={lf_tr['F']:.4f} S={lf_tr['S']:.4f}   "
          f"axial F={lf_ax['F']:.4f} S={lf_ax['S']:.4f}")

# ── Plot ───────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(16.2, 6.8))
fig.suptitle('Single-photon excitation microscope, centre wavelength 750 nm')

ax = axes[0]
ax.plot(XNA_vals, F_ax_a, 's', ms=7, mfc='white', mec='k', label='F (axial)')
ax.plot(XNA_vals, S_ax_a, 's', ms=7, mfc='k',     mec='k', label='S (axial)')
ax.plot(XNA_vals, F_tr_a, 'o', ms=7, mfc='white', mec='k', label='F (transverse)')
ax.plot(XNA_vals, S_tr_a, 'o', ms=7, mfc='k',     mec='k', label='S (transverse)')
ax.axhline(1.0, color='gray', lw=1.2, ls=':')
ax.set_xlabel('Numerical aperture')
ax.set_ylabel('Criterion value')
ax.set_title('(a) Pulse width 1 fs')
ax.set_xlim(0.05, 1.25)
ax.set_ylim(0.95, 1.075)
ax.set_xticks(XNA_vals)
ax.set_xticklabels([f'{v:g}' for v in XNA_vals], rotation=90)
ax.set_yticks([0.95, 0.975, 1.0, 1.025, 1.05, 1.075])
ax.legend(fontsize=9, loc='center right', ncol=2)

ax = axes[1]
tau_arr = np.array(tau_vals_fs, dtype=float)
ax.plot(tau_arr, F_ax_b, 's', ms=7, mfc='white', mec='k', label='F (axial)')
ax.plot(tau_arr, S_ax_b, 's', ms=7, mfc='k',     mec='k', label='S (axial)')
ax.plot(tau_arr, F_tr_b, 'o', ms=7, mfc='white', mec='k', label='F (transverse)')
ax.plot(tau_arr, S_tr_b, 'o', ms=7, mfc='k',     mec='k', label='S (transverse)')
ax.axhline(1.0, color='gray', lw=1.2, ls=':')

# Reference curves from the paper's caption (local fits near τ≈1 fs)
tau_ref = np.logspace(0, 2, 100)
ax.plot(tau_ref, 0.96 * tau_ref ** 0.1,  'k-',  lw=1.6, label='1: F=0.96τ⁰·¹')
ax.plot(tau_ref, 1.06 * tau_ref ** -0.1, 'k--', lw=1.6, label='2: S=1.06τ⁻⁰·¹')

ax.set_xscale('log')
ax.set_xlabel('Pulse width (fs)')
ax.set_ylabel('Criterion value')
ax.set_title('(b) Numerical aperture 0.8')
ax.set_xlim(1, 100)
ax.set_ylim(0.95, 1.075)
ax.set_yticks([0.95, 0.975, 1.0, 1.025, 1.05, 1.075])
ax.legend(fontsize=9, loc='center right')

plt.tight_layout()
out = os.path.join(os.path.dirname(__file__), '..', 'output', '01_romallosa', 'fig4_linfoot.png')
from mcdo.figio import save_panels
save_panels(fig, fig.axes, os.path.join(os.path.dirname(__file__), '..', 'output', '01_romallosa', 'panels'), 'fig4_linfoot')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f"Saved → {out}")
