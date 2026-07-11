r"""
Phase 6b — validation RUNG 4: the single-scatter (Born) thin-limit.

In a thin slab (τ = μ_s·d ≪ 1) at most one scattering event occurs, so the
diffuse halo is dominated by *single* scattering — which has an analytic
signature. Three checks, K=10 trials each:

  (A) POISSON statistics. The scatter count per photon must follow the free-path
      Poisson law: the ballistic fraction P(0)=⟨e^{-μ_s L}⟩ and the single-scatter
      fraction P(1)=⟨μ_s L e^{-μ_s L}⟩ match the analytic angular averages
      (L=d/cosθ), and the double-scatter fraction P(≥2) ∝ τ² is negligible.

  (B) BORN linear scaling. The scattered energy E_scat = 1−⟨e^{-μ_s L}⟩ → μ_s⟨L⟩
      as τ→0, i.e. E_scat/τ → ⟨1/cosθ⟩ (the Born = linear-in-μ_s response), and
      single scattering dominates: P(≥2)/P(1) → 0 ∝ τ.

  (C) HALO SHAPE. The thin-limit halo from the full `propagate_slab` walk matches
      an INDEPENDENT single-scatter computation (first-scatter depth sampled
      analytically + one HG deflection + straight propagation) — a cross-check of
      the multi-step loop against a one-step prediction.

NA=0.8, uniform, d=20 µm, g=0.9. Output: output/06_monte_carlo/verify_scatter_born.png
+ trials/born_*.npz.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo import SimConfig
from mcdo.montecarlo import sample_photons
from mcdo.scatter import propagate_slab, hg_sample, rotate
from mcdo.trials import run_trials, save_trials, summarize

plt.rcParams.update({'font.size': 12, 'axes.titlesize': 12, 'axes.labelsize': 11,
                     'legend.fontsize': 9, 'axes.grid': True, 'grid.alpha': 0.25,
                     'savefig.dpi': 200})

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '06_monte_carlo')
TRIALS = os.path.join(OUT, 'trials')
cfg = SimConfig(lam_c=0.750, X_NA=0.8, n=1.3, N_theta=801)
D, G, N_PH, K = 20.0, 0.9, 50000, 10
TAUS = np.array([0.02, 0.05, 0.1, 0.2, 0.4])
_TRAPZ = np.trapezoid if hasattr(np, 'trapezoid') else np.trapz


def ang_avg(f, ngrid=6001):
    """⟨f(θ)⟩ over the uniform-pupil launcher density √cosθ sinθ."""
    th = np.linspace(0.0, cfg.alpha, ngrid)
    p = np.sqrt(np.cos(th)) * np.sin(th)
    return float(_TRAPZ(f(th) * p, th) / _TRAPZ(p, th))


def _launch(N, rng):
    """Converging photons + slab-entry positions (z=−d face)."""
    kx, ky, kz, w = sample_photons(cfg, N, rng=rng)
    mu = np.vstack([kx, ky, kz]) / cfg.k_c
    L = D / mu[2]
    pos = (-D / mu[2])[None, :] * mu
    return mu, L, pos


def stats_trial(mu_s):
    """fn(rng) → [P0, P1, P2plus, E_scat] for one trial."""
    def fn(rng):
        mu, L, pos = _launch(N_PH, rng)
        _, _, nsc, weight, _ = propagate_slab(pos, mu, mu_s, G, (-D, 0.0), 400, rng)
        P0 = np.mean(nsc == 0); P1 = np.mean(nsc == 1); P2 = np.mean(nsc >= 2)
        E_scat = weight[nsc >= 1].sum() / N_PH
        return np.array([P0, P1, P2, E_scat])
    return fn


def single_scatter_halo(N, mu_s, edges, rng):
    """Independent thin-limit halo: first-scatter depth (analytic) + one HG kick."""
    mu, L, pos = _launch(N, rng)
    p1 = 1.0 - np.exp(-mu_s * L)                       # scatter probability
    u = rng.random(N)
    xi = -np.log(1.0 - u * (1.0 - np.exp(-mu_s * L))) / mu_s   # truncated free path
    pos_s = pos + xi[None, :] * mu                    # scatter point
    cos_t, phi = hg_sample(G, N, rng)
    mu_out = rotate(mu, cos_t, phi)
    fwd = mu_out[2] > 0
    t2 = np.where(fwd, -pos_s[2] / np.where(fwd, mu_out[2], 1.0), np.inf)
    ex = pos_s + t2[None, :] * mu_out
    r = np.hypot(ex[0], ex[1])
    h, _ = np.histogram(r[fwd], bins=edges, weights=p1[fwd])
    return h / N


def slab_halo(N, mu_s, edges, rng):
    """Thin-limit halo from the full propagate_slab walk (forward-scattered)."""
    mu, L, pos = _launch(N, rng)
    pos2, _, nsc, weight, _ = propagate_slab(pos, mu, mu_s, G, (-D, 0.0), 400, rng)
    fwd = (nsc >= 1) & (pos2[2] > -0.5 * D)
    r = np.hypot(pos2[0, fwd], pos2[1, fwd])
    h, _ = np.histogram(r, bins=edges, weights=weight[fwd])
    return h / N


# ── A+B: Poisson statistics and Born scaling vs τ ───────────────────────────
P0m, P1m, P2m, Em = [], [], [], []
P0s, P1s, P2s, Es = [], [], [], []
ana_P0, ana_P1 = [], []
print(f"RUNG 4 — single-scatter Born (d={D} µm, g={G}, NA=0.8), K={K}:\n")
print(f"{'τ':>6} {'P0(MC)':>9} {'P0(an)':>9} {'P1(MC)':>9} {'P1(an)':>9} "
      f"{'P≥2':>9} {'E_scat/τ':>9}")
for tau in TAUS:
    mu_s = tau / D
    tr, seeds = run_trials(stats_trial(mu_s), K)
    save_trials(os.path.join(TRIALS, f'born_tau{tau:g}.npz'), tr, seeds,
                tau=tau, mu_s=mu_s, cols=np.array(['P0', 'P1', 'P2+', 'E_scat']))
    m, s, _ = summarize(tr)
    P0m.append(m[0]); P1m.append(m[1]); P2m.append(m[2]); Em.append(m[3])
    P0s.append(s[0]); P1s.append(s[1]); P2s.append(s[2]); Es.append(s[3])
    aP0 = ang_avg(lambda th: np.exp(-mu_s * D / np.cos(th)))
    aP1 = ang_avg(lambda th: mu_s * (D / np.cos(th)) * np.exp(-mu_s * D / np.cos(th)))
    ana_P0.append(aP0); ana_P1.append(aP1)
    print(f"{tau:>6.2f} {m[0]:>9.4f} {aP0:>9.4f} {m[1]:>9.4f} {aP1:>9.4f} "
          f"{m[2]:>9.5f} {m[3]/tau:>9.4f}")
P0m, P1m, P2m, Em = map(np.array, (P0m, P1m, P2m, Em))
P2s = np.array(P2s); ana_P0 = np.array(ana_P0); ana_P1 = np.array(ana_P1)
inv_cos = ang_avg(lambda th: 1.0 / np.cos(th))

# ── C: halo shape vs independent single-scatter at τ=0.1 ────────────────────
edges = np.linspace(0.0, 25.0, 26); ctr = 0.5 * (edges[:-1] + edges[1:])
mu_s_thin = 0.1 / D
hmc, _ = run_trials(lambda rng: slab_halo(N_PH, mu_s_thin, edges, rng), K)
hss, _ = run_trials(lambda rng: single_scatter_halo(N_PH, mu_s_thin, edges, rng), K)
save_trials(os.path.join(TRIALS, 'born_halo_tau0.1.npz'),
            np.concatenate([hmc, hss], axis=1), np.arange(K),
            ctr=ctr, nbin=ctr.size, note='cols: slab_halo | single_scatter_halo')
hmc_m, hmc_s, _ = summarize(hmc); hss_m, hss_s, _ = summarize(hss)
halo_rel = float(np.sqrt(np.mean((hmc_m - hss_m) ** 2)) / hmc_m.max())

# ── validation report ───────────────────────────────────────────────────────
thin = TAUS <= 0.1
r4a_P0 = float(np.max(np.abs(P0m - ana_P0)))               # exact at every τ
r4a_P1 = float(np.max(np.abs(P1m[thin] - ana_P1[thin])))   # thin-limit prediction
r4b = float(P2m[0] / P1m[0])                 # P(≥2)/P(1) at smallest τ
slope0 = Em[0] / TAUS[0]                      # E_scat/τ at smallest τ → ⟨1/cosθ⟩
print("\n================ VALIDATION (RUNG 4) ================")
print(f"4A Poisson: P0 vs ⟨e^-μsL⟩ max dev {r4a_P0:.4f} (all τ); P1 vs single-scatter "
      f"max dev {r4a_P1:.4f} (τ≤0.1)  → {'PASS' if r4a_P0 < 0.003 and r4a_P1 < 0.004 else 'CHECK'}")
print("    (P1 deviates at τ≥0.2 by design — onset of multiple scattering, P(≥2)↑)")
print(f"4B Born:    E_scat/τ→⟨1/cosθ⟩: {slope0:.4f} vs {inv_cos:.4f}; "
      f"single-scatter dominance P(≥2)/P(1)|τ=0.02 = {r4b:.4f}  "
      f"→ {'PASS' if abs(slope0-inv_cos)<0.03 and r4b<0.05 else 'CHECK'}")
print(f"4C halo:    indep. single-scatter vs slab walk, rel RMS = {halo_rel:.3f}  "
      f"→ {'PASS' if halo_rel < 0.12 else 'CHECK'}")

# ── figure ──────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(1, 3, figsize=(16, 4.8))
fig.suptitle('RUNG 4 — single-scatter (Born) thin-limit '
             f'(d={D:.0f} µm, g={G}, NA=0.8, K={K})', fontsize=13)

a = ax[0]
a.errorbar(TAUS, P0m, P0s, fmt='o', color='C0', capsize=3, label='P(0) ballistic (MC)')
a.plot(TAUS, ana_P0, 'C0--', lw=1.3, label='analytic ⟨e^{-μ_sL}⟩')
a.errorbar(TAUS, P1m, P1s, fmt='s', color='C1', capsize=3, label='P(1) single (MC)')
a.plot(TAUS, ana_P1, 'C1--', lw=1.3, label='analytic ⟨μ_sL e^{-μ_sL}⟩')
a.errorbar(TAUS, P2m, P2s, fmt='^', color='C3', capsize=3, label='P(≥2) double')
a.plot(TAUS, P2m[0] * (TAUS / TAUS[0]) ** 2, 'k:', lw=1, label='∝ τ²')
a.set_yscale('log'); a.set_ylim(1e-4, 1.5)
a.set_xlabel('τ = μ_s·d'); a.set_ylabel('photon fraction')
a.set_title('(A) Poisson scatter statistics'); a.legend(fontsize=7.5)

a = ax[1]
a.plot(TAUS, Em / TAUS, 'o-', color='C2', label='E_scat / τ (MC)')
a.axhline(inv_cos, color='C2', ls='--', lw=1.3, label=f'⟨1/cosθ⟩ = {inv_cos:.3f} (Born)')
a.set_xlabel('τ'); a.set_ylabel('E_scat / τ')
a.set_title('(B) Born linear scaling: E_scat → μ_s⟨L⟩'); a.legend()

a = ax[2]
a.fill_between(ctr, np.clip(hmc_m - hmc_s, 0, None), hmc_m + hmc_s, color='C0', alpha=0.25)
a.plot(ctr, hmc_m, 'o-', color='C0', ms=3, label='slab walk (MC halo)')
a.fill_between(ctr, np.clip(hss_m - hss_s, 0, None), hss_m + hss_s, color='C3', alpha=0.25)
a.plot(ctr, hss_m, 's--', color='C3', ms=3, label='independent single-scatter')
a.set_xlabel('focal-plane radius r (µm)'); a.set_ylabel('halo energy / bin')
a.set_title(f'(C) halo shape at τ=0.1 (rel RMS {halo_rel:.3f})'); a.legend()

plt.tight_layout()
out = os.path.join(OUT, 'verify_scatter_born.png')
fig.savefig(out, bbox_inches='tight'); plt.close(fig)
print(f"\nSaved → {out}\n      → {TRIALS}/born_*.npz")
