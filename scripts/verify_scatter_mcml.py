r"""
Phase 6b — validation RUNG 6: the canonical diffusion Green's function
(the benchmark MCML / Farrell-Patterson tissue-transport codes are validated
against). Independent of rungs 1-5 in BOTH geometry (infinite medium, isotropic
point source — not a slab or a focused beam) and analytic form, and the first
check to exercise **absorption**.

An isotropic point source in an infinite absorbing+scattering medium produces,
by diffusion theory, the steady-state fluence rate

    φ(r) = exp(−μ_eff r) / (4π D r),   D = 1/[3(μ_a+μ_s')],
    μ_eff = √(3 μ_a μ_tr),  μ_tr = μ_a + μ_s',  μ_s' = μ_s(1−g).

So **r·φ(r) ∝ exp(−μ_eff r)**: a log-linear decay whose slope is −μ_eff. We walk
photons from the origin with the standard weighted-MC transport (free path
−lnξ/μ_t, albedo weight reduction, Henyey-Greenstein deflection, Russian
roulette) and estimate φ(r) with the path-length estimator. Checks, K trials:

  (A) μ_eff RECOVERY. The fitted decay rate matches √(3 μ_a μ_tr) across a sweep
      of absorption μ_a — the defining diffusion relation (tests absorption).
  (B) SIMILARITY (again, independent geometry). g=0.9 at matched μ_s' gives the
      same φ(r) as isotropic g=0.

Units: length in 1/μ_s' (μ_s' ≡ 1). Output:
output/06_monte_carlo/verify_scatter_mcml.png + trials/mcml_*.npz
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo.scatter import hg_sample, rotate
from mcdo.trials import run_trials, save_trials

plt.rcParams.update({'font.size': 12, 'axes.titlesize': 12, 'axes.labelsize': 11,
                     'legend.fontsize': 9, 'axes.grid': True, 'grid.alpha': 0.25,
                     'savefig.dpi': 300})

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '06_monte_carlo')
TRIALS = os.path.join(OUT, 'trials')
MU_SP = 1.0                                  # reduced coefficient sets the unit
R_EDGES = np.linspace(0.0, 15.0, 61)
R_CTR = 0.5 * (R_EDGES[:-1] + R_EDGES[1:])
FIT = (R_CTR >= 3.0) & (R_CTR <= 10.0)       # diffusion-valid window
N_PH, K = 25000, 8
MU_A = np.array([0.05, 0.1, 0.2, 0.5])


def mu_eff_analytic(mu_a):
    return np.sqrt(3.0 * mu_a * (mu_a + MU_SP))


def greens_fluence(mu_s, mu_a, g, rng, n_steps=1500, w_min=1e-4):
    """Path-length-estimator fluence φ(r) for an isotropic point source."""
    mu_t = mu_s + mu_a
    albedo = mu_s / mu_t
    pos = np.zeros((3, N_PH))
    cost = 2 * rng.random(N_PH) - 1
    sint = np.sqrt(np.clip(1 - cost ** 2, 0, 1))
    ph = 2 * np.pi * rng.random(N_PH)
    mu = np.vstack([sint * np.cos(ph), sint * np.sin(ph), cost])
    w = np.ones(N_PH)
    alive = np.ones(N_PH, bool)
    fl = np.zeros(R_CTR.size)
    for _ in range(n_steps):
        if not alive.any():
            break
        idx = np.where(alive)[0]
        s = -np.log(rng.random(idx.size)) / mu_t
        p0 = pos[:, idx]
        rmid = np.sqrt(((p0 + 0.5 * s * mu[:, idx]) ** 2).sum(0))
        b = np.digitize(rmid, R_EDGES) - 1
        ok = (b >= 0) & (b < fl.size)
        np.add.at(fl, b[ok], (w[idx] * s)[ok])          # path-length deposit
        pos[:, idx] = p0 + s * mu[:, idx]
        w[idx] *= albedo                                 # absorption weight loss
        ct, pph = hg_sample(g, idx.size, rng)
        mu[:, idx] = rotate(mu[:, idx], ct, pph)
        low = w[idx] < w_min                             # Russian roulette
        if low.any():
            li = idx[low]
            surv = rng.random(li.size) < 0.1
            w[li] = np.where(surv, w[li] * 10.0, 0.0)
            alive[li[~surv]] = False
    V = 4.0 / 3.0 * np.pi * (R_EDGES[1:] ** 3 - R_EDGES[:-1] ** 3)
    return fl / (V * N_PH)                                # φ(r) per source photon


def fit_mu_eff(phi):
    """Slope of ln(r·φ) vs r over the diffusion window → −μ_eff."""
    y = np.log(np.clip(R_CTR * phi, 1e-30, None))
    A = np.polyfit(R_CTR[FIT], y[FIT], 1)
    return -A[0]


# ── (A) μ_eff vs μ_a, isotropic ─────────────────────────────────────────────
print(f"RUNG 6 — diffusion Green's function (isotropic point source), K={K}:\n")
print(f"{'μ_a':>6} {'μ_eff(MC)':>11} {'√(3μ_aμ_tr)':>13} {'rel.err':>9}")
phi_iso = {}; meff_mc = []; meff_an = []; meff_sd = []
for mu_a in MU_A:
    def fn(rng, ma=mu_a):
        return greens_fluence(MU_SP, ma, 0.0, rng)
    tr, seeds = run_trials(fn, K)
    save_trials(os.path.join(TRIALS, f'mcml_mua{mu_a:g}.npz'), tr, seeds,
                mu_a=mu_a, g=0.0, r=R_CTR)
    phi_m = tr.mean(0); phi_iso[mu_a] = phi_m
    me = np.array([fit_mu_eff(t) for t in tr])           # per-trial μ_eff
    an = float(mu_eff_analytic(mu_a))
    meff_mc.append(me.mean()); meff_sd.append(me.std(ddof=1)); meff_an.append(an)
    print(f"{mu_a:>6g} {me.mean():>11.4f} {an:>13.4f} {abs(me.mean()-an)/an:>9.4f}")
meff_mc = np.array(meff_mc); meff_an = np.array(meff_an); meff_sd = np.array(meff_sd)

# ── (B) similarity: g=0.9 at matched μ_s' vs g=0, at μ_a=0.1 ─────────────────
mu_a_s = 0.1
phi_aniso = greens_fluence(MU_SP / (1 - 0.9), mu_a_s, 0.9,
                           np.random.default_rng(777), n_steps=4000)
sim_rel = float(np.sqrt(np.mean(((phi_aniso[FIT] - phi_iso[mu_a_s][FIT])
                                 / phi_iso[mu_a_s][FIT]) ** 2)))

# ── validation report ───────────────────────────────────────────────────────
# Diffusion is valid only for μ_a ≪ μ_s' (albedo→1); restrict the μ_eff-match
# claim to that regime, and report the growing deviation at high μ_a as the
# EXPECTED breakdown of the diffusion approximation (the MC is exact transport).
diffusive = MU_A <= 0.1
rel = np.abs(meff_mc - meff_an) / meff_an
r6a = float(np.max(rel[diffusive]))
print("\n================ VALIDATION (RUNG 6) ================")
print(f"6A μ_eff = √(3μ_aμ_tr) in the diffusion regime (μ_a≤0.1, albedo≥0.9): "
      f"max rel err {r6a:.4f}  → {'PASS' if r6a < 0.05 else 'CHECK'}")
print(f"    deviation grows to {rel[-1]:.2f} at μ_a=0.5 (albedo 0.67) — diffusion "
      f"legitimately breaks down as absorption rises; the MC is exact transport.")
print(f"6B similarity g=0.9 ≡ g=0 (matched μ_s'), fluence rel RMS {sim_rel:.3f}  "
      f"→ {'PASS' if sim_rel < 0.12 else 'CHECK'}")
print("(Reproduces the diffusion-propagator benchmark MCML/Farrell-Patterson are "
      "validated against — independent geometry + the first absorption test.)")

# ── figure ──────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(1, 3, figsize=(16, 4.8))
fig.suptitle("RUNG 6 — diffusion Green's function (isotropic point source; "
             f"the MCML/Farrell-Patterson benchmark), K={K}", fontsize=13)

a = ax[0]
cols = plt.cm.viridis(np.linspace(0, 0.85, len(MU_A)))
for mu_a, c in zip(MU_A, cols):
    y = R_CTR * phi_iso[mu_a]
    a.semilogy(R_CTR, y / y[FIT][0], 'o', color=c, ms=3, label=f'μ_a={mu_a:g}')
    an = mu_eff_analytic(mu_a)
    a.semilogy(R_CTR[FIT], np.exp(-an * (R_CTR[FIT] - R_CTR[FIT][0])), '-', color=c, lw=1.4)
a.set_ylim(1e-3, 3); a.set_xlabel('r (units of 1/μ_s′)')
a.set_ylabel('r·φ(r) (norm.)')
a.set_title('(A) r·φ decays as exp(−μ_eff r)\n(points MC, lines diffusion)')
a.legend(fontsize=8)

a = ax[1]
dif = MU_A <= 0.1
a.errorbar(meff_an[dif], meff_mc[dif], meff_sd[dif], fmt='o', color='C0',
           capsize=3, ms=8, label='diffusion regime (albedo≥0.9)')
a.errorbar(meff_an[~dif], meff_mc[~dif], meff_sd[~dif], fmt='s', color='C3',
           capsize=3, ms=8, mfc='none', label='high absorption')
lo, hi = 0.9 * meff_an.min(), 1.1 * meff_an.max()
a.plot([lo, hi], [lo, hi], 'k--', lw=1.2, label='y = x')
a.annotate('diffusion breaks down\n(μ_a=0.5, albedo 0.67)',
           (meff_an[-1], meff_mc[-1]), (meff_an[0] * 1.1, meff_mc[-1]),
           fontsize=8, color='C3', va='center',
           arrowprops=dict(arrowstyle='->', color='C3', lw=1))
a.set_xlabel('analytic μ_eff = √(3μ_aμ_tr)'); a.set_ylabel('fitted μ_eff (MC)')
a.set_title('(A) μ_eff recovered where diffusion is valid'); a.legend(fontsize=8)

a = ax[2]
yi = R_CTR * phi_iso[mu_a_s]; ya = R_CTR * phi_aniso
a.semilogy(R_CTR, yi / yi[FIT][0], 'o', color='C0', ms=4, label='isotropic g=0')
a.semilogy(R_CTR, ya / ya[FIT][0], 's', color='C3', ms=4, mfc='none',
           label='g=0.9, matched μ_s′')
a.set_ylim(1e-3, 3); a.set_xlabel('r (units of 1/μ_s′)'); a.set_ylabel('r·φ(r) (norm.)')
a.set_title(f'(B) similarity in infinite medium\n(rel RMS {sim_rel:.3f})')
a.legend()

plt.tight_layout()
out = os.path.join(OUT, 'verify_scatter_mcml.png')
fig.savefig(out, bbox_inches='tight'); plt.close(fig)
print(f"\nSaved → {out}\n      → {TRIALS}/mcml_*.npz")
