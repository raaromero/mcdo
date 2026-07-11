"""
Phase 3 literature anchor — Sheppard & Wilson (1978), "Gaussian-beam theory
of lenses with annular aperture", Microwaves Opt. Acoust. 2, 105.

Independent method (Laguerre-Gaussian mode sum) → closed forms for a Gaussian
annulus parametrised by a:
    focal plane (Eq. 27):  I(v) = J₀²(v) · exp(−v² a²)
    on axis    (Eq. 33):  I(u) = exp(−u²a²/(1+u²a⁴)) / (1 + u²a⁴)
with optical coordinates v = k r sinθ₀, u = k z sin²θ₀ about the ring angle θ₀.

Test (rigorous, one free parameter): build a Gaussian-ring pupil at low NA
(scalar/paraxial regime where Sheppard holds), FIT a from the focal-plane
envelope I(v)/J₀²(v), then PREDICT the axial profile from Eq. 33 with that
same a and compare to the independently computed RW axial profile.

Output: output/03_annular/verify_sheppard.png + printed fit/match.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.special import j0
from scipy.optimize import curve_fit

from mcdo import SimConfig
from mcdo.rw_integrals import compute_integrals
from mcdo.apodization import gaussian_ring

LAM, N_MED, NT = 0.750, 1.3, 4001
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '03_annular')
os.makedirs(OUT, exist_ok=True)

# Low NA so RW → scalar → paraxial (Sheppard's regime). Ring at sinθ₀=0.06,
# aperture edge at sinθ=0.10; narrow ring → small a → long DOF.
SIN_TH0 = 0.06
SIGMA_S = 0.012
XNA_AP = 0.10 * N_MED          # aperture so the ring fits inside
cfg = SimConfig(lam_c=LAM, X_NA=XNA_AP, n=N_MED, tau=np.inf, N_freq=3, N_theta=NT)
A = gaussian_ring(SIN_TH0, SIGMA_S)
k = cfg.k_c

v_arr = np.linspace(0.0, 16.0, 801)
u_arr = np.linspace(0.0, 400.0, 4001)
r_arr = v_arr / (k * SIN_TH0)          # v referenced to the RING angle θ₀
z_arr = u_arr / (k * SIN_TH0 ** 2)

# scalar focal/axial via I₀ only (low NA: I₁,I₂ negligible; use |I₀|²)
I0f, _, _ = compute_integrals(r_arr, np.array([0.0]), k, cfg.alpha, NT, apodization=A)
If = np.abs(I0f[0]) ** 2; If /= If.max()
I0a, _, _ = compute_integrals(np.array([0.0]), z_arr, k, cfg.alpha, NT, apodization=A)
Ia = np.abs(I0a[:, 0]) ** 2; Ia /= Ia.max()

# ── fit a from the focal envelope I/J₀² (use points away from J₀ zeros) ────
J0sq = j0(v_arr) ** 2
mask = J0sq > 0.02
ratio = If[mask] / J0sq[mask]
popt, _ = curve_fit(lambda v, a2: np.exp(-a2 * v ** 2), v_arr[mask], ratio,
                    p0=[0.01])
a_fit = np.sqrt(popt[0])
print(f"Sheppard checkpoint (low NA, ring sinθ₀={SIN_TH0}, σ_s={SIGMA_S}):")
print(f"  fitted a (from focal envelope I/J₀²) = {a_fit:.4f}")
focal_pred = J0sq * np.exp(-a_fit ** 2 * v_arr ** 2)
print(f"  focal:  max|I − J₀²·exp(−a²v²)| = {np.max(np.abs(If - focal_pred)):.4f}")

# ── predict axial from Eq. 33 with the SAME a, compare ─────────────────────
axial_pred = np.exp(-u_arr ** 2 * a_fit ** 2 / (1 + u_arr ** 2 * a_fit ** 4)) \
    / (1 + u_arr ** 2 * a_fit ** 4)
print(f"  axial:  max|I − Sheppard Eq.33(a)| = {np.max(np.abs(Ia - axial_pred)):.4f}")
# axial FWHM check
def fwhm_u(I):
    h = I.max() / 2; i = np.where(np.diff((I >= h).astype(int)))[0][0]
    return 2 * np.interp(h, [I[i+1], I[i]], [u_arr[i+1], u_arr[i]])
print(f"  axial FWHM_u: ours {fwhm_u(Ia):.1f}, Sheppard {fwhm_u(axial_pred):.1f}")

# ── Figure ─────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
fig.suptitle('Phase 3 anchor — Gaussian-ring pupil vs Sheppard & Wilson 1978 '
             '(low NA; a fitted from focal, predicts axial)', fontsize=11)

ax = axes[0]
ax.plot(v_arr, If, 'C0-', lw=1.3, label='RW Gaussian ring (low NA)')
ax.plot(v_arr, focal_pred, 'k--', lw=1.3,
        label=f'Sheppard Eq.27: J₀²(v)exp(−a²v²), a={a_fit:.3f}')
ax.plot(v_arr, J0sq, '0.7', lw=1.0, ls=':', label='J₀²(v) (a→0 δ-ring)')
ax.set_yscale('log'); ax.set_ylim(1e-4, 1.5)
ax.set_xlabel('v = k r sinθ₀'); ax.set_ylabel('normalized intensity')
ax.set_title('(a) focal plane', fontsize=10); ax.legend(fontsize=8)

ax = axes[1]
ax.plot(u_arr, Ia, 'C3-', lw=1.3, label='RW Gaussian ring (low NA)')
ax.plot(u_arr, axial_pred, 'k--', lw=1.3,
        label=f'Sheppard Eq.33 (same a={a_fit:.3f})')
ax.set_xlabel('u = k z sin²θ₀'); ax.set_ylabel('normalized on-axis intensity')
ax.set_title('(b) axial — predicted, not fitted', fontsize=10); ax.legend(fontsize=8)

plt.tight_layout()
out = os.path.join(OUT, 'verify_sheppard.png')
fig.savefig(out, dpi=150, bbox_inches='tight')
plt.close(fig)
print(f"Saved → {out}")
