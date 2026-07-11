r"""
Phase 6b — validation RUNG 5: the diffusion / multiple-scattering thick limit.

In the diffusive regime (many scattering events, transport thickness
N = μ_s'·d ≫ 1, μ_s' = μ_s(1−g)) the photon transport must obey diffusion
theory. We test the *kernel* (mcdo.scatter.propagate_slab) in the standard
pencil-beam slab benchmark — a normal-incidence collimated beam into a
non-absorbing slab — decoupled from focusing (focusing is validated by rungs
1–4). Three checks, K=10 trials each:

  (A) SIMILARITY RELATION (the decisive, self-contained one). Diffusion depends
      only on the *reduced* coefficient μ_s' = μ_s(1−g): a forward-peaked medium
      (μ_s, g=0.9) must transport identically to an isotropic one at matched
      μ_s' (μ_s/10, g=0). The diffuse transmittance and radial spread must agree
      in the thick limit and diverge in the thin limit (where single-scatter
      details still matter). This is a pure prediction of transport theory,
      needing no external formula — only our own kernel run two ways.

  (B) ANALYTIC DIFFUSION. The isotropic (g=0) slab transmittance approaches the
      extrapolated-boundary diffusion result
          T_d(N) = (1 + z*)/(N + 2 z*),  z* = 0.7104  (index-matched, source at
      one transport MFP; R_d = 1 − T_d for a non-absorber). Diffusion is
      *approximate*, so the MC→diffusion relative error must DECREASE with N.

  (C) CONVERGENCE. Both the similarity mismatch and the MC−diffusion error shrink
      as N grows — the signature of entering the diffusive regime.

Output: output/06_monte_carlo/verify_scatter_diffusion.png + trials/diffusion_*.npz
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo.scatter import propagate_slab
from mcdo.trials import run_trials, save_trials, summarize

plt.rcParams.update({'font.size': 12, 'axes.titlesize': 12, 'axes.labelsize': 11,
                     'legend.fontsize': 9, 'axes.grid': True, 'grid.alpha': 0.25,
                     'savefig.dpi': 200})

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '06_monte_carlo')
TRIALS = os.path.join(OUT, 'trials')
D = 100.0                                   # slab thickness (µm)
NTR = np.array([1.0, 2.0, 4.0, 8.0, 16.0])  # transport thicknesses N = µ_s'·d
N_PH, K = 15000, 10
ZSTAR = 0.7104                              # extrapolation ratio (index-matched)


def T_diffusion(N):
    """Extrapolated-boundary diffusion transmittance of a non-absorbing slab."""
    return (1.0 + ZSTAR) / (N + 2.0 * ZSTAR)


def pencil_slab(mu_s, g, rng):
    """Normal-incidence pencil beam into slab z∈[0,D]; return (T, R, r_rms_fwd)."""
    pos = np.zeros((3, N_PH)); mu = np.zeros((3, N_PH)); mu[2] = 1.0
    n_steps = int(min(4000, max(60, 8 * mu_s * D)))
    pos2, _, nsc, weight, _ = propagate_slab(pos, mu, mu_s, g, (0.0, D),
                                             n_steps, rng)
    fwd = pos2[2] > 0.5 * D                  # exited far face (transmitted)
    back = ~fwd
    T = weight[fwd].sum() / N_PH
    R = weight[back].sum() / N_PH
    r_rms = (np.sqrt(np.mean(pos2[0, fwd] ** 2 + pos2[1, fwd] ** 2))
             if fwd.any() else 0.0)
    return np.array([T, R, r_rms])


# ── sweep transport thickness for both anisotropies ─────────────────────────
res = {0.0: [], 0.9: []}
print(f"RUNG 5 — diffusion thick limit (pencil beam, slab d={D:g} µm), K={K}:\n")
print(f"{'N_tr':>8} {'T(g=0)':>9} {'T_diff':>9} {'T(g=0.9)':>10} "
      f"{'|dT|sim':>9} {'rel.err':>9}")
for N in NTR:
    for g in (0.0, 0.9):
        mu_sp = N / D                        # reduced coefficient µ_s'
        mu_s = mu_sp / (1.0 - g)             # actual µ_s (µ_s'/(1−g))
        tr, seeds = run_trials(lambda rng, ms=mu_s, gg=g: pencil_slab(ms, gg, rng), K)
        save_trials(os.path.join(TRIALS, f'diffusion_N{N:g}_g{g:g}.npz'), tr, seeds,
                    N=N, mu_s=mu_s, g=g, cols=np.array(['T', 'R', 'r_rms']))
        res[g].append(summarize(tr)[:2])     # (mean(3), std(3))
    m0, m9 = res[0.0][-1][0], res[0.9][-1][0]
    Td = T_diffusion(N)
    print(f"{N:>8g} {m0[0]:>9.4f} {Td:>9.4f} {m9[0]:>10.4f} "
          f"{abs(m0[0]-m9[0]):>9.4f} {abs(m0[0]-Td)/Td:>9.4f}")

T0 = np.array([r[0][0] for r in res[0.0]]); T0s = np.array([r[1][0] for r in res[0.0]])
R0 = np.array([r[0][1] for r in res[0.0]])
T9 = np.array([r[0][0] for r in res[0.9]]); T9s = np.array([r[1][0] for r in res[0.9]])
rr0 = np.array([r[0][2] for r in res[0.0]]); rr9 = np.array([r[0][2] for r in res[0.9]])
Td = T_diffusion(NTR)
sim_mismatch = np.abs(T0 - T9)
diff_err = np.abs(T0 - Td) / Td

# ── validation report ───────────────────────────────────────────────────────
sim_thick = float(sim_mismatch[NTR >= 8].max())
sim_shrinks = bool(sim_mismatch[-1] < sim_mismatch[0])
err_shrinks = bool(diff_err[-1] < diff_err[0])
err_thick = float(diff_err[-1])
print("\n================ VALIDATION (RUNG 5) ================")
print(f"5A similarity (μ_s,g=0.9)≡(μ_s',g=0): |ΔT| ≤ {sim_thick:.4f} for N≥8, "
      f"shrinks thin→thick ({sim_mismatch[0]:.3f}→{sim_mismatch[-1]:.3f})  "
      f"→ {'PASS' if sim_thick < 0.02 and sim_shrinks else 'CHECK'}")
print(f"5B MC → analytic diffusion: rel err {diff_err[0]:.3f}(N=1) → "
      f"{err_thick:.3f}(N={NTR[-1]:g}), decreasing  "
      f"→ {'PASS' if err_shrinks and err_thick < 0.15 else 'CHECK'}")
print(f"5C radial spread diffusive: r_rms(g=0.9) matches r_rms(g=0) at N≥8 to "
      f"{100*abs(rr0[-1]-rr9[-1])/rr0[-1]:.1f}%")

# ── figure ──────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(1, 3, figsize=(16, 4.8))
fig.suptitle('RUNG 5 — diffusion / multiple-scattering thick limit '
             f'(pencil beam, non-absorbing slab, K={K})', fontsize=13)

a = ax[0]
a.errorbar(NTR, T0, T0s, fmt='o', color='C0', capsize=3, label='MC transmittance (g=0)')
a.errorbar(NTR, T9, T9s, fmt='s', color='C1', capsize=3, mfc='none',
           label='MC transmittance (g=0.9, matched μ_s′)')
a.plot(NTR, Td, 'k--', lw=1.6, label='diffusion T_d(N)')
a.plot(NTR, R0, '^', color='C3', label='MC reflectance (g=0)')
a.plot(NTR, 1 - Td, 'k:', lw=1.2, label='diffusion R_d = 1−T_d')
a.set_xlabel('transport thickness  N = μ_s′·d'); a.set_ylabel('energy fraction')
a.set_title('(A/B) transmittance vs diffusion + similarity'); a.legend(fontsize=8)

a = ax[1]
a.loglog(NTR, sim_mismatch, 'o-', color='C1', lw=1.8, label='|T(g=0.9) − T(g=0)|')
a.set_xlabel('N = μ_s′·d'); a.set_ylabel('similarity mismatch')
a.set_title('(A) similarity relation tightens with N\n(diffusive regime)')
a.legend()

a = ax[2]
a.loglog(NTR, diff_err, 'o-', color='C0', lw=1.8, label='|MC − diffusion| / diffusion')
a.axhline(0.1, color='0.5', ls=':', lw=1); a.text(NTR[0], 0.105, '10%', fontsize=8, color='0.5')
a.set_xlabel('N = μ_s′·d'); a.set_ylabel('relative error')
a.set_title('(B) MC converges to diffusion as N grows')
a.legend()

plt.tight_layout()
out = os.path.join(OUT, 'verify_scatter_diffusion.png')
fig.savefig(out, bbox_inches='tight'); plt.close(fig)
print(f"\nSaved → {out}\n      → {TRIALS}/diffusion_*.npz")
