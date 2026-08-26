"""
Phase 6b foundation — validate the scattering kernel (the correct version of
the operation gbp-mc got wrong). Three checks:

  A. Anisotropy: the mean cosine of the deflection ⟨cosθ⟩ must equal g.
  B. Isotropy/rotation correctness: scatter a +z beam ONCE with g=0 → the exit
     directions must be uniform on the sphere (⟨μz⟩≈0, ⟨μz²⟩≈1/3). The gbp-mc
     scalar-angle-addition gives a biased result — shown for contrast.
  C. Beer-Lambert: the unscattered (ballistic) fraction through a slab of
     thickness L equals exp(−μ_s·L).

Output: output/06_monte_carlo/verify_scatter_kernel.png + printed table.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo.scatter import hg_sample, rotate, propagate_slab

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '06_monte_carlo')
rng = np.random.default_rng(0)
N = 200_000

# ── A. ⟨cosθ⟩ = g ──────────────────────────────────────────────────────────
print("A. HG anisotropy ⟨cosθ⟩ vs g:")
for g in [0.0, 0.3, 0.55, 0.9]:
    cos_t, _ = hg_sample(g, N, rng)
    print(f"   g={g:.2f}: ⟨cosθ⟩ = {cos_t.mean():+.4f}")

# ── B. isotropy after one scatter (correct rotate vs gbp-mc scalar-add) ────
mu0 = np.tile(np.array([[0.0], [0.0], [1.0]]), (1, N))   # +z beam
cos_t, phi = hg_sample(0.0, N, rng)                       # isotropic
mu_correct = rotate(mu0, cos_t, phi)

# gbp-mc style: theta0 = arctan2(z, sqrt(x^2+y^2)) (elevation!), add deflection
theta0 = np.arctan2(mu0[2], np.sqrt(mu0[0]**2 + mu0[1]**2))
defl = np.arccos(cos_t)                  # deflection magnitude
theta1 = theta0 + defl
phi1 = phi
mu_bug = np.vstack([np.sin(theta1)*np.cos(phi1),
                    np.sin(theta1)*np.sin(phi1),
                    np.cos(theta1)])
print("\nB. exit ⟨μz⟩, ⟨μz²⟩ after one isotropic (g=0) scatter of a +z beam:")
print(f"   correct rotate : ⟨μz⟩={mu_correct[2].mean():+.4f}  ⟨μz²⟩={ (mu_correct[2]**2).mean():.4f}  (want 0, 0.333)")
print(f"   gbp-mc scalar  : ⟨μz⟩={mu_bug[2].mean():+.4f}  ⟨μz²⟩={ (mu_bug[2]**2).mean():.4f}  (biased)")

# ── C. Beer-Lambert ballistic fraction ─────────────────────────────────────
print("\nC. ballistic (unscattered) fraction vs exp(−μ_s L), slab L=1 μm:")
L = 1.0
pos0 = np.vstack([np.zeros(N), np.zeros(N), np.zeros(N)])  # start at slab entrance z0=0
mu_in = np.tile(np.array([[0.0], [0.0], [1.0]]), (1, N))
mus_vals = [0.5, 1.0, 2.0, 4.0]
ball_meas, ball_theory = [], []
for mu_s in mus_vals:
    _, _, nsc, _, _ = propagate_slab(pos0, mu_in, mu_s, 0.5, (0.0, L),
                                     n_steps=200, rng=rng)
    frac = np.mean(nsc == 0)
    ball_meas.append(frac); ball_theory.append(np.exp(-mu_s * L))
    print(f"   μ_s={mu_s:.1f} (μm⁻¹): measured {frac:.4f},  exp(−μ_sL)={np.exp(-mu_s*L):.4f}")

# ── Figure ─────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(14, 4.2))
fig.suptitle('Scattering kernel validation (correct local-frame rotation)',
             fontsize=12)
ax = axes[0]
gg = np.linspace(0, 0.95, 20)
meas = [hg_sample(g, 50000, rng)[0].mean() for g in gg]
ax.plot(gg, gg, 'k:', label='⟨cosθ⟩ = g')
ax.plot(gg, meas, 'C0o', ms=3, label='sampled')
ax.set_xlabel('g'); ax.set_ylabel('⟨cosθ⟩'); ax.legend(fontsize=8)
ax.set_title('(A) HG anisotropy', fontsize=10)

ax = axes[1]
ax.hist(mu_correct[2], bins=40, density=True, alpha=0.7, label='correct rotate')
ax.hist(mu_bug[2], bins=40, density=True, alpha=0.5, label='gbp-mc scalar-add')
ax.axhline(0.5, color='k', lw=0.8, ls=':', label='uniform (correct)')
ax.set_xlabel('μz after one g=0 scatter'); ax.set_ylabel('pdf')
ax.set_title('(B) isotropy: correct = uniform', fontsize=10); ax.legend(fontsize=7)

ax = axes[2]
ax.plot(mus_vals, ball_theory, 'k:', label='exp(−μ_s L)')
ax.plot(mus_vals, ball_meas, 'C3o', ms=5, label='measured')
ax.set_xlabel('μ_s (μm⁻¹), L=1 μm'); ax.set_ylabel('ballistic fraction')
ax.set_title('(C) Beer-Lambert', fontsize=10); ax.legend(fontsize=8)

plt.tight_layout()
out = os.path.join(OUT, 'verify_scatter_kernel.png')
fig.savefig(out, dpi=300, bbox_inches='tight'); plt.close(fig)
print(f"\nSaved → {out}")
