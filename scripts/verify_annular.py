"""
Phase 3 verification — annular apertures via field-level Babinet.

Checks (output/03_annular/):
  A. ε→0 regression: annular(ε=1e-9) ≡ full disk (machine precision).
  B. Transverse profiles vs ε: central lobe narrows, sidelobes grow;
     thin-annulus limit (ε=0.99) → Durnin J₀²(v) (FWHM_v 2.252 vs Airy 3.233).
  C. Axial profiles vs ε and DOF extension: paraxial theory
     DOF(ε)/DOF(0) = 1/(1−ε²); quantify the high-NA shortfall.
  D. Uniform vs Gaussian (α_t=2, outer-referenced) across ε.

All for linear-x input, y-cut |I₀−I₂|² unless noted; u,v referenced to the
full (outer) aperture.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo.style import apply as _apply_style
_apply_style()
from scipy.special import j0

from mcdo import SimConfig
from mcdo.rw_integrals import compute_integrals
from mcdo.annular import compute_integrals_annular
from mcdo.apodization import gaussian as gaussian_apod

LAM, N_MED, NT = 0.750, 1.3, 1001
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '03_annular')
os.makedirs(OUT, exist_ok=True)

v_arr = np.linspace(0.0, 12.0, 481)
u_arr = np.linspace(0.0, 1200.0, 6001)   # long: DOF(ε=0.99) ~ 50–90× DOF₀

ydir = lambda I0, I1, I2: np.abs(I0 - I2) ** 2


def cfg_at(xna):
    return SimConfig(lam_c=LAM, X_NA=xna, n=N_MED, tau=np.inf, N_freq=3, N_theta=NT)


def transverse(cfg, eps, apod=None):
    r = v_arr / (cfg.k_c * cfg.sin_alpha)
    I = ydir(*[a[0] for a in compute_integrals_annular(
        r, np.array([0.0]), cfg.k_c, cfg.alpha, eps, NT, apodization=apod)])
    return I / I.max()


def axial(cfg, eps, apod=None):
    z = u_arr / (cfg.k_c * cfg.sin2_alpha)
    I = ydir(*[a[:, 0] for a in compute_integrals_annular(
        np.array([0.0]), z, cfg.k_c, cfg.alpha, eps, NT, apodization=apod)])
    return I / I.max()


def fwhm(x, y):
    half = y.max() / 2.0
    i = np.where(np.diff((y >= half).astype(int)))[0][0]
    return 2.0 * np.interp(half, [y[i + 1], y[i]], [x[i + 1], x[i]])


# ── A. regression ──────────────────────────────────────────────────────────
cfg = cfg_at(0.8)
r = v_arr / (cfg.k_c * cfg.sin_alpha)
I_full = ydir(*[a[0] for a in compute_integrals(
    r, np.array([0.0]), cfg.k_c, cfg.alpha, NT)])
I_ann0 = ydir(*[a[0] for a in compute_integrals_annular(
    r, np.array([0.0]), cfg.k_c, cfg.alpha, 0.0, NT)])
print(f"A. ε=0 regression: max diff = {np.max(np.abs(I_full - I_ann0)):.2e}")

# ── B/C/D. sweeps ──────────────────────────────────────────────────────────
EPS = [0.0, 0.3, 0.5, 0.7, 0.9, 0.99]
EPS_SHOW = [0.0, 0.5, 0.99]        # profile panels: three curves stay legible
COLS = plt.cm.plasma(np.linspace(0, 0.85, len(EPS)))
XNA_LO, XNA_HI = 0.13, 1.17        # sinα = 0.1 and 0.9

print("\nB. transverse FWHM_v vs ε (X_NA=1.17, y-cut; Airy 3.233, J₀² 2.252):")
tr_hi = {}
for e in EPS:
    tr_hi[e] = transverse(cfg_at(XNA_HI), e)
    print(f"   ε={e:4.2f}  FWHM_v = {fwhm(v_arr, tr_hi[e]):.3f}")
J0sq = j0(v_arr) ** 2
print(f"   thin-annulus check: max|I(ε=0.99) − J₀²| = "
      f"{np.max(np.abs(tr_hi[0.99] - J0sq)):.3f}")

print("\nC. DOF ratio vs ε (axial FWHM_u / FWHM_u(ε=0); theory 1/(1−ε²)):")
print(f"{'ε':>5} {'theory':>8} {'lowNA(0.13)':>12} {'highNA(1.17)':>13}")
dof = {XNA_LO: [], XNA_HI: []}
for e in EPS:
    row = []
    for xna in [XNA_LO, XNA_HI]:
        dof[xna].append(fwhm(u_arr, axial(cfg_at(xna), e)))
    r0_lo, r0_hi = dof[XNA_LO][0], dof[XNA_HI][0]
    print(f"{e:>5.2f} {1/(1-e**2+1e-30):>8.2f} "
          f"{dof[XNA_LO][-1]/r0_lo:>12.2f} {dof[XNA_HI][-1]/r0_hi:>13.2f}")

print("\nD. uniform vs Gaussian α_t=2 (X_NA=1.17, ε=0.7): transverse FWHM_v")
cfg_hi = cfg_at(XNA_HI)
A2 = gaussian_apod(2.0, cfg_hi.sin2_alpha)
I_g = transverse(cfg_hi, 0.7, apod=A2)
print(f"   uniform {fwhm(v_arr, tr_hi[0.7]):.3f}   Gaussian {fwhm(v_arr, I_g):.3f}"
      f"   (annulus passes only the Gaussian tail → nearly uniform ring)")

# ── Figure ─────────────────────────────────────────────────────────────────
_chi = cfg_at(XNA_HI)
r_um = v_arr / (_chi.k_c * _chi.sin_alpha)     # physical radius (μm) at the high-NA config
z_um = u_arr / (_chi.k_c * _chi.sin2_alpha)    # physical defocus (μm)

fig, axes = plt.subplots(2, 2, figsize=(16.9, 12.2))
fig.suptitle('Annular apertures, 750 nm',
             fontsize=12)

ax = axes[0, 0]
for e in EPS_SHOW:
    ax.plot(r_um, tr_hi[e], color=COLS[EPS.index(e)], lw=2.0, label=f'ε={e:g}')
ax.plot(r_um, J0sq, 'k--', lw=2.0, label='ideal thin ring (non-diffracting limit)')
ax.set_yscale('log'); ax.set_ylim(1e-5, 1.5)
ax.set_xlabel('Radial position r (μm)'); ax.set_ylabel('Normalized intensity')
ax.set_title('(a) Transverse profile versus obstruction ratio', fontsize=11)
ax.legend(fontsize=7.5, ncol=2)

ax = axes[0, 1]
for e in EPS_SHOW:
    ax.plot(z_um, axial(cfg_at(XNA_HI), e), color=COLS[EPS.index(e)], lw=2.0, label=f'ε={e:g}')
ax.set_xlim(0, 40); ax.set_yscale('log'); ax.set_ylim(1e-4, 1.5)
ax.set_xlabel('Axial position z (μm)'); ax.set_ylabel('Normalized intensity')
ax.set_title('(b) Axial profile versus obstruction ratio', fontsize=11)
ax.legend(fontsize=7.5, ncol=2)

ax = axes[1, 0]
e_th = np.linspace(0, 0.992, 200)
ax.plot(e_th, 1 / (1 - e_th ** 2), 'k--', lw=2.0, label='theory 1/(1−ε²)')
for xna, st, lab in [(XNA_LO, 'C0o-', f'X_NA={XNA_LO} (sinα=0.1)'),
                     (XNA_HI, 'C3s-', f'X_NA={XNA_HI} (sinα=0.9)')]:
    ratios = np.array(dof[xna]) / dof[xna][0]
    ax.plot(EPS, ratios, st, ms=5, lw=2.0, label=lab)
ax.set_yscale('log')
ax.set_xlabel('Obstruction ratio'); ax.set_ylabel('Depth of focus, relative')
ax.set_title('(c) Depth-of-focus extension against obstruction ratio', fontsize=11)
ax.legend(fontsize=8)

ax = axes[1, 1]
ax.plot(r_um, tr_hi[0.7], 'C0-', lw=2.0, label='uniform, ε=0.7')
ax.plot(r_um, I_g, 'C3--', lw=2.0, label='Gaussian $\\alpha_t$=2, ε=0.7')
ax.plot(r_um, tr_hi[0.0], 'k:', lw=2.0, label='uniform, full disk')
ax.set_yscale('log'); ax.set_ylim(1e-5, 1.5)
ax.set_xlabel('Radial position r (μm)'); ax.set_ylabel('Normalized intensity')
ax.set_title('(d) Uniform and Gaussian illumination compared', fontsize=11)
ax.legend(fontsize=8)

plt.tight_layout()
out = os.path.join(OUT, 'verify_annular.png')
from mcdo.figio import save_panels
save_panels(fig, fig.axes, os.path.join(os.path.dirname(__file__), '..', 'output', '03_annular', 'panels'), 'verify_annular')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f"\nSaved → {out}")
