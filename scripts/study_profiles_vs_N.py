r"""
Profile mean ± SD vs photon count N — how the Monte-Carlo error band on the
focal cross-sections tightens as N grows. For each N we run K=10 independent
trials (the project standard), keep the per-trial profiles, and plot the
per-point mean ± 1σ against the deterministic expected curve.

Transverse (z=0) and axial (x=0) cuts; uniform pupil, NA=0.8, scalar. The band
shrinks ∝ 1/√N and is widest in the dark side-lobes/zeros (where the relative MC
noise lives). Per-trial data saved to output/06_monte_carlo/trials/profiles_vs_N.npz.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo import SimConfig
from mcdo.debye import scalar_debye
from mcdo.montecarlo import sample_photons, coherent_intensity
from mcdo.trials import run_trials, save_trials, summarize

plt.rcParams.update({'font.size': 12, 'axes.titlesize': 12, 'axes.labelsize': 11,
                     'legend.fontsize': 9, 'axes.grid': True, 'grid.alpha': 0.25,
                     'savefig.dpi': 300})

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '06_monte_carlo')
cfg = SimConfig(lam_c=0.750, X_NA=0.8, n=1.3, N_theta=801)
K = 10
NS = [1000, 10000, 100000]

x = np.linspace(-1.2, 1.2, 121)
z = np.linspace(-4.0, 4.0, 161)
nt = x.size
det_t = scalar_debye(np.abs(x), np.array([0.0]), cfg.k_c, cfg.alpha, cfg.N_theta)[0]
det_t /= det_t.max()
det_z = scalar_debye(np.array([0.0]), z, cfg.k_c, cfg.alpha, cfg.N_theta)[:, 0]
det_z /= det_z.max()


def trial_profiles(N):
    """fn(rng) → concatenated [transverse(121), axial(161)], each peak-normalised."""
    def fn(rng):
        kx, ky, kz, w = sample_photons(cfg, N, rng=rng)
        It = coherent_intensity(kx, ky, kz, w, x, np.zeros_like(x), np.zeros_like(x))
        Iz = coherent_intensity(kx, ky, kz, w, np.zeros_like(z), np.zeros_like(z), z)
        return np.concatenate([It / It.max(), Iz / Iz.max()])
    return fn


data = {}
for N in NS:
    trials, seeds = run_trials(trial_profiles(N), K)
    data[N] = trials
    save_trials(os.path.join(OUT, 'trials', f'profiles_N{N}.npz'), trials, seeds,
                x=x, z=z, det_t=det_t, det_z=det_z, nt=nt, N=N)

# combined archive too
save_trials(os.path.join(OUT, 'trials', 'profiles_vs_N.npz'),
            np.stack([data[N] for N in NS], 0), np.array(NS),
            x=x, z=z, det_t=det_t, det_z=det_z, nt=nt, NS=np.array(NS),
            note='axis0 = N ladder, axis1 = trials')

# ── figure: 2 rows (transverse, axial) × len(NS) columns ────────────────────
fig, axes = plt.subplots(2, len(NS), figsize=(5 * len(NS), 8.4), squeeze=False)
fig.suptitle('Profile mean ± 1σ vs photon count N  (K=10 trials, uniform, NA=0.8)',
             fontsize=14)

print(f"profile MC band (uniform, NA=0.8), K={K} trials:")
print(f"{'N':>8} {'transverse mean σ':>20} {'axial mean σ':>16}")
for col, N in enumerate(NS):
    tr_t = data[N][:, :nt]; tr_z = data[N][:, nt:]
    for row, (coord, tr, det, xlab, ttl) in enumerate([
            (x * 1e3, tr_t, det_t, 'x (nm)', 'transverse (z=0)'),
            (z, tr_z, det_z, 'z (µm)', 'axial (x=0)')]):
        ax = axes[row][col]
        m, sd, _ = summarize(tr)
        for r in tr:
            ax.semilogy(coord, np.clip(r, 1e-6, None), color='C0', lw=0.4, alpha=0.12)
        ax.fill_between(coord, np.clip(m - sd, 1e-6, None), m + sd, color='C0',
                        alpha=0.30, label='mean ± 1σ')
        ax.semilogy(coord, m, color='C0', lw=2.0, label='MC mean')
        ax.semilogy(coord, np.clip(det, 1e-6, None), 'k--', lw=1.5, label='expected')
        ax.set_ylim(1e-4 if row == 0 else 1e-3, 2)
        ax.set_xlabel(xlab); ax.set_ylabel('intensity (norm.)')
        ax.set_title(f'{ttl} — N = {N:,}')
        if row == 0 and col == 0:
            ax.legend(loc='lower center', ncol=3, fontsize=8)
    print(f"{N:>8} {summarize(tr_t)[1].mean():>20.5f} {summarize(tr_z)[1].mean():>16.5f}")

plt.tight_layout()
out = os.path.join(OUT, 'profiles_vs_N.png')
fig.savefig(out, bbox_inches='tight'); plt.close(fig)
print("\nThe ±1σ band tightens ∝ 1/√N (mean σ over the profile drops as N grows).")
print(f"Saved → {out}\n      → {OUT}/trials/profiles_vs_N.npz (+ per-N)")
