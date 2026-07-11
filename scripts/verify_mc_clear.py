"""
Phase 6a — Monte-Carlo focal field in the CLEAR limit must reproduce the
deterministic (scalar Debye) field. This is the validation gate before
scattering.

Checks (output/06_monte_carlo/):
  A. Convergence: MC vs scalar_debye on an x–z slice, RMS and null-floor vs N
     (the null floor ∝ 1/N — the photon-count requirement for clean zeros).
  B. Resolution: the field's Nyquist limits set dx,dy,dz —
        dx,dy ≤ λ/(2·NA)            (transverse, marginal ray k·sinα)
        dz   ≤ λ/(2·n·(1−cosα))     (axial,      k·(1−cosα))
     intensity needs ~½ of that; we use ~¼ (comfortable oversampling).
  C. 3-D save: write a clear-medium volume + metadata to .npz (the scattering
     stage will populate the same grid).

Scalar field (validates against mcdo.debye.scalar_debye exactly as N→∞).
X_NA=0.8 and a low-NA case where everything also equals the analytic Airy.
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

LAM, N_MED = 0.750, 1.3
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '06_monte_carlo')
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(0)


def nyquist(cfg):
    """Comfortable (¼-Nyquist) voxel sizes for the field at this NA."""
    dx = LAM / (8.0 * cfg.X_NA)                       # transverse
    dz = LAM / (8.0 * cfg.n * (1 - np.cos(cfg.alpha)))  # axial
    return dx, dz


# ── A. convergence on an x–z slice (X_NA=0.8) ──────────────────────────────
cfg = SimConfig(lam_c=LAM, X_NA=0.8, n=N_MED, tau=np.inf, N_freq=3, N_theta=1001)
dx, dz = nyquist(cfg)
print(f"X_NA=0.8: comfortable voxels dx=dy={dx*1e3:.0f} nm, dz={dz*1e3:.0f} nm")
x_arr = np.arange(-1.2, 1.2 + dx, dx)
z_arr = np.arange(-4.0, 4.0 + dz, dz)
Zg, Xg = np.meshgrid(z_arr, x_arr, indexing='ij')
Yg = np.zeros_like(Xg)

ref = scalar_debye(np.abs(x_arr), z_arr, cfg.k_c, cfg.alpha, 1001)  # (Nz,Nx)
ref = ref / ref.max()

print("\nA. MC → scalar Debye convergence (x–z slice):")
print(f"{'N':>8} {'RMS':>9} {'null floor':>11}")
mc_by_N = {}
for N in [1_000, 10_000, 100_000]:
    kx, ky, kz, w = sample_photons(cfg, N, rng=rng)
    I = coherent_intensity(kx, ky, kz, w, Xg, Yg, Zg)
    I = I / I.max()
    mc_by_N[N] = I
    rms = np.sqrt(np.mean((I - ref) ** 2))
    # null floor: MC intensity where the true field has a deep zero ring
    nullmask = ref < 1e-3
    floor = I[nullmask].mean() if nullmask.any() else np.nan
    print(f"{N:>8d} {rms:>9.4f} {floor:>11.2e}")

# ── B. low-NA cross-check vs Airy ──────────────────────────────────────────
from mcdo.debye import airy_intensity
cfg_lo = SimConfig(lam_c=LAM, X_NA=0.3, n=N_MED, tau=np.inf, N_freq=3, N_theta=1001)
v = np.linspace(0, 10, 200)
r_lo = v / (cfg_lo.k_c * cfg_lo.sin_alpha)
kx, ky, kz, w = sample_photons(cfg_lo, 100_000, rng=rng)
I_lo = coherent_intensity(kx, ky, kz, w, r_lo, 0.0 * r_lo, 0.0 * r_lo)
I_lo /= I_lo.max()
print(f"\nB. low-NA (X_NA=0.3): max|MC − Airy| = {np.max(np.abs(I_lo - airy_intensity(v))):.4f}")

# ── C. save a clear-medium 3-D volume ──────────────────────────────────────
xs = np.arange(-1.0, 1.0 + 0.1, 0.1)
zs = np.arange(-3.0, 3.0 + 0.15, 0.15)
Zv, Yv, Xv = np.meshgrid(zs, xs, xs, indexing='ij')
kx, ky, kz, w = sample_photons(cfg, 30_000, rng=rng)
I_vol = coherent_intensity(kx, ky, kz, w, Xv, Yv, Zv)
I_vol /= I_vol.max()
npz = os.path.join(OUT, 'mc_clear_volume.npz')
np.savez_compressed(npz, intensity=I_vol.astype(np.float32), x=xs, y=xs, z=zs,
                    lam=LAM, NA=0.8, n=N_MED, n_photons=30000, scattering=0.0,
                    note='clear-medium scalar coherent MC; I normalized to peak')
print(f"\nC. saved 3-D volume {I_vol.shape} → {npz}")

# ── Figure ─────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(14, 8))
fig.suptitle('Phase 6a — coherent MC in the clear limit reproduces the '
             'deterministic field (X_NA=0.8, scalar)', fontsize=12)

ext = [x_arr[0], x_arr[-1], z_arr[0], z_arr[-1]]
for ax, (data, ttl) in zip(axes[0], [
        (ref, 'scalar Debye (deterministic)'),
        (mc_by_N[10_000], 'MC, N=10⁴'),
        (mc_by_N[100_000], 'MC, N=10⁵')]):
    im = ax.imshow(data, extent=ext, origin='lower', aspect='auto',
                   cmap='inferno', vmin=0, vmax=1)
    ax.set_xlabel('x (μm)'); ax.set_ylabel('z (μm)'); ax.set_title(ttl, fontsize=10)

ax = axes[1, 0]
iz0 = np.argmin(np.abs(z_arr))
ax.plot(x_arr, ref[iz0], 'k-', lw=1.5, label='Debye')
ax.plot(x_arr, mc_by_N[1_000][iz0], 'C0:', lw=1, label='MC 10³')
ax.plot(x_arr, mc_by_N[100_000][iz0], 'C3--', lw=1, label='MC 10⁵')
ax.set_yscale('log'); ax.set_ylim(1e-4, 1.5)
ax.set_xlabel('x (μm)  (z=0)'); ax.set_ylabel('I'); ax.legend(fontsize=8)
ax.set_title('transverse cut: null floor ∝ 1/N', fontsize=10)

ax = axes[1, 1]
ix0 = np.argmin(np.abs(x_arr))
ax.plot(z_arr, ref[:, ix0], 'k-', lw=1.5, label='Debye')
ax.plot(z_arr, mc_by_N[100_000][:, ix0], 'C3--', lw=1, label='MC 10⁵')
ax.set_xlabel('z (μm)  (x=0)'); ax.set_ylabel('I'); ax.legend(fontsize=8)
ax.set_title('axial cut', fontsize=10)

ax = axes[1, 2]
ax.plot(v, airy_intensity(v), 'k-', lw=1.5, label='Airy')
ax.plot(v, I_lo, 'C3--', lw=1, label='MC 10⁵')
ax.set_yscale('log'); ax.set_ylim(1e-4, 1.5)
ax.set_xlabel('v'); ax.set_ylabel('I'); ax.legend(fontsize=8)
ax.set_title('low-NA (X_NA=0.3): MC = Airy', fontsize=10)

plt.tight_layout()
out = os.path.join(OUT, 'verify_mc_clear.png')
fig.savefig(out, dpi=150, bbox_inches='tight')
plt.close(fig)
print(f"Saved → {out}")
