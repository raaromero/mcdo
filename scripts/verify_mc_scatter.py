r"""
Phase 6b — focused beam through a scattering slab: validation harness + headline.

Slab z∈[−d, 0] (focus at the back face), d=20 µm, anisotropy g=0.9, μ_a=0,
NA=0.8, uniform, scalar. We sweep the optical depth τ = μ_s·d and, at each τ,
run K=10 independent trials (project standard; per-trial data saved). For every
trial we record the ballistic core peak attenuation, the energy partition
(ballistic / forward-scattered / back-scattered / absorbed), and the diffuse
halo (forward-scattered exit positions on the focal plane).

Validation ladder (the answer to "is it good enough" with no closed form):
  RUNG 1  continuity   — at μ_s=0 the core = the clear focus and the halo = 0.
  RUNG 2  Beer-Lambert — the MC ballistic fraction = ⟨exp(−μ_s d/cosθ)⟩ (analytic
          angular average over the launcher density).
  RUNG 3  energy       — ballistic + forward + back + absorbed = 1 (to ~1/√N).

Output: output/06_monte_carlo/verify_mc_scatter.png + trials/scatter_*.npz.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo import SimConfig
from mcdo.focus_scatter import (focal_scatter_trial, split_trial,
                                ballistic_fraction_analytic)
from mcdo.trials import run_trials, save_trials, summarize

plt.rcParams.update({'font.size': 12, 'axes.titlesize': 12, 'axes.labelsize': 11,
                     'legend.fontsize': 9, 'axes.grid': True, 'grid.alpha': 0.25,
                     'savefig.dpi': 300})

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '06_monte_carlo')
TRIALS = os.path.join(OUT, 'trials')
cfg = SimConfig(lam_c=0.750, X_NA=0.8, n=1.3, N_theta=801)
D, G, MU_A, N_PH, K = 20.0, 0.9, 0.0, 50000, 10
TAUS = np.array([0.0, 0.1, 0.2, 0.5, 1.0, 2.0, 4.0])     # optical depth μ_s·d
MUS = TAUS / D
x_line = np.linspace(-1.5, 1.5, 121)
halo_edges = np.linspace(0.0, 25.0, 51)
halo_ctr = 0.5 * (halo_edges[:-1] + halo_edges[1:])
NX, NH = x_line.size, halo_ctr.size


def fwhm(prof, coord):
    """FWHM (nm) of a centred profile peaked near coord=0."""
    p = prof / prof.max(); c = int(np.argmax(p))
    right = p[c:]; j = int(np.argmax(right < 0.5))
    if j == 0:
        return np.nan
    half = np.interp(0.5, [right[j], right[j - 1]], [coord[c + j], coord[c + j - 1]])
    return 2.0 * (half - coord[c]) * 1e3


peak, part_m, part_s, hrms_m, hrms_s = [], [], [], [], []
core_m, halo_m, halo_s, cfwhm = [], [], [], []
ball_analytic = []
print(f"Phase 6b — focused beam through slab (d={D} µm, g={G}, NA=0.8), K={K}:\n")
print(f"{'τ=μ_s·d':>8} {'E_ball(MC)':>11} {'⟨e^-μsL⟩':>10} {'E_fwd':>8} {'E_back':>8}"
      f" {'Σparts':>8} {'peak_att':>9} {'halo_rms':>9}")
for tau, mu_s in zip(TAUS, MUS):
    fn = lambda rng, mu_s=mu_s: focal_scatter_trial(cfg, N_PH, mu_s, G, D, x_line,
                                                    halo_edges, rng=rng, mu_a=MU_A)
    vec, seeds = run_trials(fn, K)
    save_trials(os.path.join(TRIALS, f'scatter_tau{tau:g}.npz'), vec, seeds,
                tau=tau, mu_s=mu_s, d=D, g=G, x_line=x_line, halo_ctr=halo_ctr,
                nx=NX, nhalo=NH, layout='peak,part(4),hrms,core(nx),halo(nhalo)')
    d_ = split_trial(vec, NX, NH)
    pm, ps, _ = summarize(d_['partition'])
    peak.append(summarize(d_['peak_atten'])[:2])
    part_m.append(pm); part_s.append(ps)
    hm, hs, _ = summarize(d_['halo_rms']); hrms_m.append(hm); hrms_s.append(hs)
    cm = d_['core'].mean(0); core_m.append(cm); cfwhm.append(fwhm(cm, x_line))
    hm2, hs2, _ = summarize(d_['halo']); halo_m.append(hm2); halo_s.append(hs2)
    ba = ballistic_fraction_analytic(cfg, mu_s, D); ball_analytic.append(ba)
    print(f"{tau:>8.2f} {pm[0]:>11.4f} {ba:>10.4f} {pm[1]:>8.4f} {pm[2]:>8.4f}"
          f" {pm.sum():>8.4f} {peak[-1][0]:>9.4f} {hm:>9.3f}")

peak = np.array(peak); part_m = np.array(part_m); part_s = np.array(part_s)
hrms_m = np.array(hrms_m); hrms_s = np.array(hrms_s); ball_analytic = np.array(ball_analytic)
core_m = np.array(core_m); halo_m = np.array(halo_m); halo_s = np.array(halo_s)
save_trials(os.path.join(TRIALS, 'scatter_summary.npz'),
            np.stack([part_m]), np.array([0]), taus=TAUS, peak=peak,
            part_mean=part_m, part_std=part_s, hrms_mean=hrms_m, hrms_std=hrms_s,
            ball_analytic=ball_analytic, core_fwhm=np.array(cfwhm), d=D, g=G)

# ── validation report ───────────────────────────────────────────────────────
i0 = 0  # τ=0 row
r1 = (abs(peak[i0, 0] - 1) < 0.02 and part_m[i0, 1] < 1e-9 and part_m[i0, 2] < 1e-9)
r2 = float(np.max(np.abs(part_m[:, 0] - ball_analytic)))
r3 = float(np.max(np.abs(part_m.sum(1) - 1.0)))
print("\n================ VALIDATION ================")
print(f"RUNG 1 continuity (μ_s=0): core peak ratio {peak[i0,0]:.4f}=1, "
      f"E_fwd={part_m[i0,1]:.1e}, E_back={part_m[i0,2]:.1e}  → {'PASS' if r1 else 'CHECK'}")
print(f"RUNG 2 Beer-Lambert: max|E_ball(MC) − ⟨e^-μsL⟩| = {r2:.4f}  "
      f"→ {'PASS' if r2 < 0.01 else 'CHECK'}")
print(f"RUNG 3 energy conservation: max|Σparts − 1| = {r3:.2e}  "
      f"→ {'PASS' if r3 < 1e-9 else 'CHECK'}")
print(f"core FWHM vs τ (nm): {np.array(cfwhm).round(1)}  (ballistic core broadens "
      f"slightly as steep rays are preferentially scattered)")

# ── figure ──────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(2, 2, figsize=(14, 9.5))
fig.suptitle('Focused beam through a scattering slab '
             f'(d={D:.0f} µm, g={G}, NA=0.8, K={K} trials)', fontsize=14)

a = ax[0, 0]
a.errorbar(TAUS, part_m[:, 0], part_s[:, 0], fmt='o-', color='C0', capsize=3, label='ballistic (MC)')
a.plot(TAUS, ball_analytic, 'C0--', lw=1.4, label=r'$\langle e^{-\mu_s d/\cos\theta}\rangle$ (analytic)')
a.plot(TAUS, np.exp(-TAUS), 'k:', lw=1.2, label=r'$e^{-\tau}$ (normal incidence)')
a.errorbar(TAUS, part_m[:, 1], part_s[:, 1], fmt='s-', color='C1', capsize=3, label='forward-scattered')
a.errorbar(TAUS, part_m[:, 2], part_s[:, 2], fmt='^-', color='C3', capsize=3, label='back-scattered')
a.set_xlabel('optical depth  τ = μ_s·d'); a.set_ylabel('energy fraction')
a.set_title('(A) energy partition vs τ  (RUNG 2 + 3)'); a.legend(fontsize=8)

a = ax[0, 1]
a.errorbar(TAUS, peak[:, 0], peak[:, 1], fmt='o-', color='C0', capsize=3, label='ballistic core peak (MC)')
a.plot(TAUS, ball_analytic, 'C0:', lw=1.2, label=r'ballistic energy $\langle e^{-\mu_s L}\rangle$')
a.plot(TAUS, np.exp(-TAUS), 'k:', lw=1.2, label=r'$e^{-\tau}$')
a.set_yscale('log'); a.set_xlabel('optical depth τ'); a.set_ylabel('I_core(0)/I_clear(0)')
a.set_title('(B) ballistic core peak attenuation (Strehl-like)'); a.legend(fontsize=8)

a = ax[1, 0]
a.errorbar(TAUS, hrms_m, hrms_s, fmt='o-', color='C2', capsize=3)
a.set_xlabel('optical depth τ'); a.set_ylabel('halo RMS radius (µm)')
a.set_title('(C) diffuse halo widens with τ'); a.grid(True, alpha=0.3)

a = ax[1, 1]
for j, tau in enumerate(TAUS):
    if tau in (0.5, 1.0, 2.0):
        m, s = halo_m[j], halo_s[j]
        a.fill_between(halo_ctr, np.clip(m - s, 0, None), m + s, alpha=0.25)
        a.plot(halo_ctr, m, 'o-', ms=3, lw=1.4, label=f'τ={tau:g}')
a.set_xlabel('focal-plane radius r (µm)'); a.set_ylabel('halo energy / bin')
a.set_title('(D) diffuse halo radial profile (mean ± SD)'); a.legend(fontsize=9)

plt.tight_layout()
out = os.path.join(OUT, 'verify_mc_scatter.png')
fig.savefig(out, bbox_inches='tight'); plt.close(fig)
print(f"\nSaved → {out}\n      → {TRIALS}/scatter_*.npz")
