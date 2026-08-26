"""
Profile the optional MC parallelism and verify it gives identical results.

The coherent field is an additive photon sum, so parallel = serial up to FP
round-off. We confirm max|I_parallel − I_serial| ≈ 0 and report the wall-clock
speedup vs n_jobs. Output: output/06_monte_carlo/profile_parallel.png + table.
"""

import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo import SimConfig
from mcdo.montecarlo import sample_photons, coherent_intensity_parallel

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '06_monte_carlo')


def main():
    cfg = SimConfig(lam_c=0.750, X_NA=0.8, n=1.3, tau=np.inf, N_freq=3, N_theta=801)
    N = 200_000  # fixed photon set → identical result regardless of n_jobs
    kx, ky, kz, w = sample_photons(cfg, N, rng=np.random.default_rng(0))

    dx = 0.75 / (8 * cfg.X_NA)
    x = np.arange(-1.2, 1.2 + dx, dx)
    z = np.arange(-4.0, 4.0 + dx, dx)
    Z, X = np.meshgrid(z, x, indexing='ij')
    Y = np.zeros_like(X)

    njobs = [1, 2, 4, 8]
    times, maxdiff = [], []
    I_ref = None
    print(f"N={N} photons, grid {X.shape} = {X.size} points")
    print(f"{'n_jobs':>7} {'time (s)':>9} {'speedup':>8} {'max|Δ| vs serial':>17}")
    for nj in njobs:
        t0 = time.perf_counter()
        I = coherent_intensity_parallel(kx, ky, kz, w, X, Y, Z, n_jobs=nj)
        dt = time.perf_counter() - t0
        times.append(dt)
        # relative difference (intensities are un-normalized, magnitude ~1e10)
        md = 0.0 if I_ref is None else np.max(np.abs(I - I_ref)) / I_ref.max()
        if I_ref is None:
            I_ref = I
        maxdiff.append(md)
        print(f"{nj:>7} {dt:>9.2f} {times[0]/dt:>8.2f} {md:>17.2e}")

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    fig.suptitle('MC parallelism — speedup and result identity (N=2×10⁵)',
                 fontsize=11)
    ax = axes[0]
    ax.plot(njobs, [times[0] / t for t in times], 'o-', label='measured')
    ax.plot(njobs, njobs, 'k:', label='ideal (linear)')
    ax.set_xlabel('n_jobs'); ax.set_ylabel('speedup'); ax.legend(fontsize=8)
    ax.set_title('(a) Wall-clock speedup', fontsize=10)
    ax = axes[1]
    ax.semilogy(njobs, np.maximum(maxdiff, 1e-18), 's-')
    ax.axhline(1e-12, color='r', lw=0.7, ls=':')
    ax.set_xlabel('n_jobs'); ax.set_ylabel('relative max|I_par − I_ser|')
    ax.set_title('(b) Results identical (≈ FP round-off, ~1e-15)', fontsize=10)
    plt.tight_layout()
    out = os.path.join(OUT, 'profile_parallel.png')
    fig.savefig(out, dpi=300, bbox_inches='tight'); plt.close(fig)
    print(f"Saved → {out}")


if __name__ == "__main__":
    main()
