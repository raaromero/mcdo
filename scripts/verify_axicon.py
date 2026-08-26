"""
Phase 4 — axicon / Bessel beams via a conical pupil phase.

A true axicon is a cone: phase ∝ pupil radius ρ; with the sine condition
ρ ∝ sinθ this is A(θ) = exp(+jβ sinθ/sinα) behind the aplanatic lens. It
turns the focal point into a focal SEGMENT. Stationary phase on the on-axis
integral (phase Ψ = u cosθ/sin²α + β sinθ/sinα):

    dΨ/dθ = 0  ⇒  u(θ*) = β sinα cosθ*/sinθ* = β sinα / tanθ*  (> 0)

so axial position u maps to a contributing cone angle θ*(u), and the LOCAL
transverse profile there is the Bessel beam J₀²(v·sinθ*/sinα) [Dur87; Her91].
The scale varies along the segment (steep rays θ→α feed small u, paraxial
rays feed large u).

Checks (output/04_axicon/):
  A. β=0 regression ≡ plain disk (machine precision).
  B. Axial profiles vs β: focal segment forms; segment length vs β.
  C. Durnin checkpoint — at several θ* the transverse profile at the
     predicted u must equal J₀²(v·sinθ*/sinα). Done at low NA (scalar Bessel
     limit) and X_NA=0.8 (vector deformation).
  D. Axicon local profile vs the matched thin annulus at the same θ*.
Linear-x y-cut.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.special import j0

from mcdo import SimConfig
from mcdo.rw_integrals import compute_integrals
from mcdo.annular import compute_integrals_annular
from mcdo.apodization import axicon

LAM, N_MED, NT = 0.750, 1.3, 3001     # fine θ grid: axicon phase oscillates
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '04_axicon')
os.makedirs(OUT, exist_ok=True)

v_arr = np.linspace(0.0, 12.0, 481)
u_arr = np.linspace(0.0, 260.0, 5201)
BETA = 20
ydir = lambda I0, I1, I2: np.abs(I0 - I2) ** 2


def cfg_at(xna):
    return SimConfig(lam_c=LAM, X_NA=xna, n=N_MED, tau=np.inf, N_freq=3, N_theta=NT)


def axial(cfg, beta):
    z = u_arr / (cfg.k_c * cfg.sin2_alpha)
    A = axicon(beta, cfg.sin_alpha) if beta else None
    I = ydir(*[a[:, 0] for a in compute_integrals(
        np.array([0.0]), z, cfg.k_c, cfg.alpha, NT, apodization=A)])
    return I / I.max()


def transverse_at(cfg, beta, u0):
    z = np.array([u0 / (cfg.k_c * cfg.sin2_alpha)])
    r = v_arr / (cfg.k_c * cfg.sin_alpha)
    A = axicon(beta, cfg.sin_alpha) if beta else None
    I = ydir(*[a[0] for a in compute_integrals(
        r, z, cfg.k_c, cfg.alpha, NT, apodization=A)])
    return I / I.max()


def u_of_thetastar(cfg, beta, frac):
    """u at which θ* = frac·α is the stationary-phase angle."""
    th = frac * cfg.alpha
    return beta * cfg.sin_alpha / np.tan(th), np.sin(th) / cfg.sin_alpha


def seg_length(I):
    """Bright-segment full length (where I > 0.5·max)."""
    i = np.where(I >= 0.5 * I.max())[0]
    return u_arr[i[-1]] - u_arr[i[0]] if len(i) else np.nan


# ── A. regression ──────────────────────────────────────────────────────────
cfg = cfg_at(0.8)
I_plain = axial(cfg, 0.0)
I_b0 = axial(cfg, 0.0)  # axicon(0) path is None → same call; check explicit β=0
z = u_arr / (cfg.k_c * cfg.sin2_alpha)
A0 = axicon(0.0, cfg.sin_alpha)
I_expl = ydir(*[a[:, 0] for a in compute_integrals(
    np.array([0.0]), z, cfg.k_c, cfg.alpha, NT, apodization=A0)])
I_expl /= I_expl.max()
print(f"A. β=0 regression (explicit axicon(0) vs plain): "
      f"max diff = {np.max(np.abs(I_plain - I_expl)):.2e}")

# ── B. axial segments ──────────────────────────────────────────────────────
BETAS = [0, 10, 20, 40]
COLS = plt.cm.plasma(np.linspace(0, 0.8, len(BETAS)))
ax_prof = {b: axial(cfg, b) for b in BETAS}
print("\nB. axial bright-segment length (X_NA=0.8; plain-focus FWHM≈9.9):")
for b in BETAS:
    print(f"   β={b:3d}:  segment length = {seg_length(ax_prof[b]):7.2f} u"
          f"   (peaks within window: {ax_prof[b][1:-1].max() >= ax_prof[b].max()})")

# ── C. Durnin checkpoint at several θ* ─────────────────────────────────────
FRACS = [0.55, 0.7, 0.85]
print(f"\nC. Durnin check, β={BETA}: transverse @ predicted u vs J₀²(v·sinθ*/sinα)")
durnin = {}
for tag, cfg_d in [('lowNA X_NA=0.13', cfg_at(0.13)), ('X_NA=0.8', cfg)]:
    print(f"  {tag}:")
    durnin[tag] = []
    for fr in FRACS:
        u0, scale = u_of_thetastar(cfg_d, BETA, fr)
        I_tr = transverse_at(cfg_d, BETA, u0)
        I_bes = j0(v_arr * scale) ** 2
        dev = np.max(np.abs(I_tr - I_bes))
        durnin[tag].append((fr, u0, scale, I_tr, I_bes, dev))
        print(f"     θ*={fr:.2f}α  u={u0:6.2f}  scale={scale:.3f}  "
              f"max|I−J₀²|={dev:.3f}")

# ── D. axicon local vs matched thin annulus (low NA, mid θ*) ───────────────
cfg_lo = cfg_at(0.13)
fr = 0.7
u0, scale = u_of_thetastar(cfg_lo, BETA, fr)
I_ax_lo = transverse_at(cfg_lo, BETA, u0)
# annulus centered on θ* = 0.7α, thin
th_star = fr * cfg_lo.alpha
a_out = np.arcsin(min(np.sin(th_star) / 0.98, 0.999))
I_ann = ydir(*[a[0] for a in compute_integrals_annular(
    v_arr / (cfg_lo.k_c * cfg_lo.sin_alpha), np.array([0.0]),
    cfg_lo.k_c, a_out, 0.96, NT)])
I_ann /= I_ann.max()

# ── Figure ─────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(14, 4.4))
fig.suptitle('Axicon conical pupil phase: focal segment with '
             'position-dependent Bessel scale (linear-x y-cut)', fontsize=11)

ax = axes[0]
for b, c in zip(BETAS, COLS):
    ax.plot(u_arr, ax_prof[b], color=c, lw=1.2, label=f'β={b}')
for fr in FRACS:
    u0, _ = u_of_thetastar(cfg, BETA, fr)
    ax.axvline(u0, color='0.6', lw=0.6, ls=':')
ax.set_xlim(0, 120)
ax.set_xlabel('Optical axial coordinate u'); ax.set_ylabel('Normalized on-axis intensity')
ax.set_title('(a) NA=0.8: axial segment vs β\n',
             fontsize=10)
ax.legend(fontsize=8)

ax = axes[1]
for (fr, u0, scale, I_tr, I_bes, dev), c in zip(durnin['lowNA X_NA=0.13'],
                                                ['C0', 'C1', 'C2']):
    ax.plot(v_arr, I_tr, color=c, lw=1.2,
            label=f'θ*={fr:.2f}α (scale {scale:.2f})')
    ax.plot(v_arr, I_bes, color=c, lw=2.6, alpha=0.3)
ax.set_yscale('log'); ax.set_ylim(1e-4, 1.5)
ax.set_xlabel('Optical radial coordinate v'); ax.set_ylabel('Normalized intensity')
ax.set_title('(b) Durnin check, low NA: thin = axicon,\nfaint = J₀² prediction '
             '(overlapping)', fontsize=10)
ax.legend(fontsize=7.5)

ax = axes[2]
u0_m, scale_m = u_of_thetastar(cfg_lo, BETA, 0.7)
ax.plot(v_arr, I_ax_lo, 'C0-', lw=1.3, label='axicon @ θ*=0.70α')
ax.plot(v_arr, I_ann, 'C3--', lw=1.3, label='thin annulus @ same θ')
ax.plot(v_arr, j0(v_arr * scale_m) ** 2, 'k:', lw=1.6,
        label=f'J₀²(v·{scale_m:.2f})')
ax.set_yscale('log'); ax.set_ylim(1e-4, 1.5)
ax.set_xlabel('Optical radial coordinate v'); ax.set_ylabel('Normalized intensity')
ax.set_title('(c) Two roads to one Bessel core\n(axicon segment ≡ annulus, low NA)',
             fontsize=10)
ax.legend(fontsize=7.5)

plt.tight_layout()
out = os.path.join(OUT, 'verify_axicon.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f"\nSaved → {out}")
