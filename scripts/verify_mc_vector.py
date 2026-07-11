"""
Phase 6a (vector) — the vector MC reproduces the full Richards-Wolf focal
field, closing the scalar→vector consistency gap. Each photon carries the
refracted x-polarization vector; Ex,Ey,Ez are accumulated separately.

Proof (one photon set, two independent cuts):
  • y–z plane (x=0): MC |E|² must equal the deterministic |I₀−I₂|² (Ez=0 here).
  • x–z plane (y=0): MC |E|² must equal |I₀+I₂|² + 4|I₁|² (Ez longitudinal lobe).

If both match, the vector launcher is correct. X_NA=0.8, N=2×10⁵.
Output: output/06_monte_carlo/verify_mc_vector.png
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

from mcdo import SimConfig
from mcdo.rw_integrals import compute_integrals
from mcdo.montecarlo import sample_photons_vector, coherent_intensity_vector

LAM, N_MED = 0.750, 1.3
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '06_monte_carlo')


def main():
    cfg = SimConfig(lam_c=LAM, X_NA=0.8, n=N_MED, tau=np.inf, N_freq=3, N_theta=1201)
    N = 200_000
    kx, ky, kz, wvec = sample_photons_vector(cfg, N, rng=np.random.default_rng(0))

    dx = LAM / (8 * cfg.X_NA)
    dz = LAM / (8 * cfg.n * (1 - np.cos(cfg.alpha)))
    s = np.arange(-1.2, 1.2 + dx, dx)        # transverse axis (y or x)
    z = np.arange(-4.0, 4.0 + dz, dz)
    Z, S = np.meshgrid(z, s, indexing='ij')
    O = np.zeros_like(S)

    # deterministic references
    I0, I1, I2 = compute_integrals(np.abs(s), z, cfg.k_c, cfg.alpha, cfg.N_theta)
    det_y = np.abs(I0 - I2) ** 2                       # φ=π/2 (y-axis)
    det_x = np.abs(I0 + I2) ** 2 + 4 * np.abs(I1) ** 2  # φ=0   (x-axis)
    det_y /= det_y.max(); det_x /= det_x.max()

    # MC on the two planes (same photon set)
    mc_y = coherent_intensity_vector(kx, ky, kz, wvec, O, S, Z)   # x=0 → y-z plane
    mc_x = coherent_intensity_vector(kx, ky, kz, wvec, S, O, Z)   # y=0 → x-z plane
    mc_y /= mc_y.max(); mc_x /= mc_x.max()

    rms_y = np.sqrt(np.mean((mc_y - det_y) ** 2))
    rms_x = np.sqrt(np.mean((mc_x - det_x) ** 2))
    print(f"vector MC vs deterministic RW (N={N}):")
    print(f"  y-cut |I₀−I₂|²        RMS = {rms_y:.4f}")
    print(f"  x-cut |I₀+I₂|²+4|I₁|²  RMS = {rms_x:.4f}")

    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    fig.suptitle('Vector MC reproduces the full RW field — two cuts, one photon '
                 'set (X_NA=0.8, N=2×10⁵)', fontsize=12)
    ext = [s[0], s[-1], z[0], z[-1]]
    iz0 = np.argmin(np.abs(z))
    for row, (det, mc, lab, cutlab) in enumerate([
            (det_y, mc_y, 'y-cut (⊥ pol): |I₀−I₂|²', 'y'),
            (det_x, mc_x, 'x-cut (∥ pol): |I₀+I₂|²+4|I₁|²', 'x')]):
        a = axes[row]
        a[0].imshow(det, extent=ext, origin='lower', aspect='auto', cmap='inferno',
                    norm=LogNorm(1e-3, 1)); a[0].set_ylabel(f'{lab}\nz (μm)', fontsize=9)
        a[1].imshow(mc, extent=ext, origin='lower', aspect='auto', cmap='inferno',
                    norm=LogNorm(1e-3, 1))
        a[2].plot(s, det[iz0], 'k-', lw=1.4, label='deterministic')
        a[2].plot(s, mc[iz0], 'C3--', lw=1.0, label='vector MC')
        a[2].set_yscale('log'); a[2].set_ylim(1e-4, 1.5); a[2].legend(fontsize=8)
        a[2].text(0.5, 0.04, f'RMS={rms_y if row==0 else rms_x:.4f}',
                  transform=a[2].transAxes, ha='center', color='C3', fontsize=9)
        if row == 0:
            a[0].set_title('deterministic', fontsize=10)
            a[1].set_title('vector MC', fontsize=10)
            a[2].set_title(f'transverse cut ({cutlab})', fontsize=10)
        a[2].set_xlabel(f'{cutlab} (μm)')
    plt.tight_layout()
    out = os.path.join(OUT, 'verify_mc_vector.png')
    fig.savefig(out, dpi=140, bbox_inches='tight'); plt.close(fig)
    print(f"Saved → {out}")


if __name__ == "__main__":
    main()
