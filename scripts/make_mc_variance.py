r"""
Monte-Carlo statistical spread: the focal intensity at each point is a random
variable over the photon sampling, so across K independent runs (different
seeds) every point has a mean and a standard deviation. This is the natural way
to *see* MC convergence — faint line per run, bold mean, ±1σ shaded band (the
seaborn-style envelope), with the deterministic field overlaid as the target.

Two photon counts (N = 2×10³ and 2×10⁴) show the band shrink ∝ 1/√N; both the
transverse (z=0) and axial (x=0) cuts are shown. Each run is normalised to its
own peak (the convention used throughout), so the spread appears in the
side-lobes and zeros — where the MC noise actually lives.

NA=0.8, λ_c=750 nm, n=1.3, uniform pupil, scalar. K=40 runs.
Output: output/06_monte_carlo/mc_variance.png
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

plt.rcParams.update({'font.size': 12, 'axes.titlesize': 12, 'axes.labelsize': 11,
                     'legend.fontsize': 9, 'axes.grid': True, 'grid.alpha': 0.25,
                     'savefig.dpi': 200})

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '06_monte_carlo')
cfg = SimConfig(lam_c=0.750, X_NA=0.8, n=1.3, N_theta=801)
K = 40
NS = [2000, 20000]

x = np.linspace(-1.5, 1.5, 161)
z = np.linspace(-4.0, 4.0, 161)
det_x = scalar_debye(np.abs(x), np.array([0.0]), cfg.k_c, cfg.alpha, cfg.N_theta)[0]
det_x /= det_x.max()
det_z = scalar_debye(np.array([0.0]), z, cfg.k_c, cfg.alpha, cfg.N_theta)[:, 0]
det_z /= det_z.max()


def runs(N, pts_x, pts_y, pts_z):
    """K normalised MC cross-sections (each row = one run)."""
    out = np.empty((K, len(pts_x)))
    for s in range(K):
        rng = np.random.default_rng(1000 + s)
        kx, ky, kz, w = sample_photons(cfg, N, rng=rng)
        I = coherent_intensity(kx, ky, kz, w, pts_x, pts_y, pts_z)
        out[s] = I / I.max()
    return out


fig, axes = plt.subplots(2, 2, figsize=(14, 9))
fig.suptitle('Monte-Carlo statistical spread — per-point mean ± 1σ over '
             f'K={K} runs (clear limit, uniform, NA=0.8)', fontsize=14)

for row, N in enumerate(NS):
    tr = runs(N, x, np.zeros_like(x), np.zeros_like(x))
    ax_ = runs(N, np.zeros_like(z), np.zeros_like(z), z)
    for col, (cut, coord, data, det, xlabel) in enumerate([
            ('transverse (z=0)', x * 1e3, tr, det_x, 'x (nm)'),
            ('axial (x=0)', z, ax_, det_z, 'z (µm)')]):
        ax = axes[row, col]
        m, sd = data.mean(0), data.std(0)
        for r in data:                              # faint per-run lines
            ax.semilogy(coord, np.clip(r, 1e-6, None), color='C0', lw=0.5, alpha=0.13)
        ax.fill_between(coord, np.clip(m - sd, 1e-6, None), m + sd, color='C0',
                        alpha=0.30, label='mean ± 1σ')
        ax.semilogy(coord, m, color='C0', lw=2.0, label='MC mean')
        ax.semilogy(coord, np.clip(det, 1e-6, None), 'k--', lw=1.6, label='expected')
        ax.set_ylim(1e-4 if col == 0 else 1e-3, 2)
        ax.set_xlabel(xlabel); ax.set_ylabel('intensity (norm.)')
        ax.set_title(f'{cut} — N = {N:,} photons')
        if row == 0 and col == 0:
            ax.legend(loc='lower center', ncol=3, fontsize=8)

out = os.path.join(OUT, 'mc_variance.png')
plt.tight_layout()
fig.savefig(out, bbox_inches='tight'); plt.close(fig)
print(f"Saved → {out}")
print(f"K={K} runs at N={NS}; band is per-point ±1σ across runs (∝1/√N).")
