"""
Phase 2 closer — truncated-Gaussian paraxial checkpoint (Tanaka 1985 /
Horváth & Bor 2003 regime).

Independent reference: the paraxial focal-plane field of a truncated
Gaussian through a circular pupil,
    U(v) ∝ ∫₀¹ exp(−α_t ρ²) J₀(vρ) ρ dρ        [B&W §8.8 form; Tanaka 1985]
evaluated by direct quadrature (no shared code with the angular Debye
module). Our scalar_debye with the aplanatic Gaussian A(θ) must converge to
this at low NA for every α_t; the RW y-cut must match both.

Output: output/02_na_apodization/verify_tanaka_paraxial.png + table.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.special import j0
from scipy.integrate import trapezoid

from mcdo import SimConfig
from mcdo.rw_integrals import compute_integrals
from mcdo.debye import scalar_debye
from mcdo.apodization import gaussian as gaussian_apod

LAM, N_MED, NT = 0.750, 1.3, 1001
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '02_na_apodization')

v_arr = np.linspace(0.0, 10.0, 401)
rho = np.linspace(0.0, 1.0, 2001)


def paraxial_truncated_gaussian(v, alpha_t):
    """|∫₀¹ e^{−α_t ρ²} J₀(vρ) ρ dρ|², normalized to peak."""
    W = np.exp(-alpha_t * rho ** 2) * rho
    U = np.array([trapezoid(W * j0(vi * rho), rho) for vi in v])
    I = U ** 2
    return I / I.max()


cfg = SimConfig(lam_c=LAM, X_NA=0.1, n=N_MED, tau=np.inf, N_freq=3, N_theta=NT)
r = v_arr / (cfg.k_c * cfg.sin_alpha)

print("Low-NA (X_NA=0.1) truncated-Gaussian checkpoint vs paraxial integral:")
fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
fig.suptitle('Phase 2 closer — truncated-Gaussian focal profiles vs the '
             'paraxial reference (Tanaka/H&B regime, X_NA=0.1)', fontsize=11)
styles = ['C0', 'C1', 'C2', 'C3']
for at, c in zip([0.5, 1.0, 2.0, 4.0], styles):
    A = gaussian_apod(at, cfg.sin2_alpha)
    I_par = paraxial_truncated_gaussian(v_arr, at)
    I_sc = scalar_debye(r, np.array([0.0]), cfg.k_c, cfg.alpha, NT,
                        apodization=A)[0]
    I_sc /= I_sc.max()
    I0, I1, I2 = compute_integrals(r, np.array([0.0]), cfg.k_c, cfg.alpha,
                                   NT, apodization=A)
    I_rw = np.abs(I0[0] - I2[0]) ** 2
    I_rw /= I_rw.max()
    d_sc = np.max(np.abs(I_sc - I_par))
    d_rw = np.max(np.abs(I_rw - I_par))
    print(f"  α_t={at:3.1f}:  max|scalar−paraxial|={d_sc:.2e}   "
          f"max|RW y-cut−paraxial|={d_rw:.2e}")
    axes[0].plot(v_arr, I_par, color=c, lw=3.0, alpha=0.3)
    axes[0].plot(v_arr, I_sc, color=c, lw=1.0, label=f'α_t={at:g}')
    axes[1].semilogy(v_arr, np.abs(I_sc - I_par) + 1e-12, color=c, lw=1.0,
                     label=f'scalar, α_t={at:g}')
    axes[1].semilogy(v_arr, np.abs(I_rw - I_par) + 1e-12, color=c, lw=1.0,
                     ls='--', label=f'RW y-cut, α_t={at:g}')

axes[0].set_xlabel('v'); axes[0].set_ylabel('normalized intensity')
axes[0].set_title('(a) profiles: thick faint = paraxial reference;\n'
                  'thin = our scalar Debye (overlapping)', fontsize=10)
axes[0].legend(fontsize=8)
axes[1].set_xlabel('v'); axes[1].set_ylabel('|deviation| from paraxial')
axes[1].set_ylim(1e-12, 1e-1)
axes[1].set_title('(b) deviations (log)', fontsize=10)
axes[1].legend(fontsize=7, ncol=2)

plt.tight_layout()
out = os.path.join(OUT, 'verify_tanaka_paraxial.png')
fig.savefig(out, dpi=150, bbox_inches='tight')
plt.close(fig)
print(f"Saved → {out}")
