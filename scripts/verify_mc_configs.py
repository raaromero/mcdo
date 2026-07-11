"""
Phase 6a proof — the coherent MC photon launcher reproduces the deterministic
(scalar Debye) field for EACH pupil configuration, not just uniform.

For uniform, Gaussian (α_t=2), annular (ε=0.5 top-hat ring) and axicon (β=20
conical phase), the SAME scalar Debye integral is evaluated two ways:
  • deterministically (mcdo.debye.scalar_debye with that apodization)
  • by Monte-Carlo photon launching (mcdo.montecarlo, same apodization)
They must agree as N→∞ — the per-configuration validation gate. The launcher
samples θ ∝ |A(θ)|√cosθ sinθ and carries the pupil phase on each photon's
weight, so annular (A=0 outside the ring) and axicon (A=phase) are handled by
the same sampler.

x–z slice, X_NA=0.8, N=10⁵. Output: output/06_monte_carlo/verify_mc_configs.png
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

from mcdo import SimConfig
from mcdo.debye import scalar_debye
from mcdo.montecarlo import sample_photons, coherent_intensity
from mcdo.apodization import gaussian, axicon

LAM, N_MED = 0.750, 1.3
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '06_monte_carlo')
rng = np.random.default_rng(1)
N = 100_000

cfg = SimConfig(lam_c=LAM, X_NA=0.8, n=N_MED, tau=np.inf, N_freq=3, N_theta=1201)
dx = LAM / (8 * cfg.X_NA)
dz = LAM / (8 * cfg.n * (1 - np.cos(cfg.alpha)))
x = np.arange(-1.2, 1.2 + dx, dx)
z = np.arange(-4.0, 4.0 + dz, dz)
Z, X = np.meshgrid(z, x, indexing='ij')
Y = np.zeros_like(X)

theta_in = np.arcsin(0.5 * cfg.sin_alpha)            # ε=0.5 ring inner angle
CONFIGS = [
    ('uniform', None),
    ('Gaussian α_t=2', gaussian(2.0, cfg.sin2_alpha)),
    ('annular ε=0.5', (lambda th: (np.asarray(th) >= theta_in).astype(float))),
    ('axicon β=20', axicon(20.0, cfg.sin_alpha)),
]

fig, axes = plt.subplots(len(CONFIGS), 4, figsize=(15, 3.3 * len(CONFIGS)))
fig.suptitle('Phase 6a proof — MC photon launcher = deterministic scalar field, '
             'per configuration (X_NA=0.8, N=10⁵)', fontsize=12)
ext = [x[0], x[-1], z[0], z[-1]]

print("config              RMS(MC−det)   peak-rel")
for row, (label, apod) in enumerate(CONFIGS):
    det = scalar_debye(np.abs(x), z, cfg.k_c, cfg.alpha, cfg.N_theta, apodization=apod)
    det = det / det.max()
    kx, ky, kz, w = sample_photons(cfg, N, apod=apod, rng=rng)
    mc = coherent_intensity(kx, ky, kz, w, X, Y, Z)
    mc = mc / mc.max()
    rms = np.sqrt(np.mean((mc - det) ** 2))
    print(f"{label:<18} {rms:>10.4f}    {rms:>8.2%}")

    izpk = np.argmax(det[:, np.argmin(np.abs(x))])
    ix0 = np.argmin(np.abs(x))
    a = axes[row]
    a[0].imshow(det, extent=ext, origin='lower', aspect='auto', cmap='inferno',
                norm=LogNorm(1e-3, 1)); a[0].set_ylabel(f'{label}\nz (μm)', fontsize=9)
    a[1].imshow(mc, extent=ext, origin='lower', aspect='auto', cmap='inferno',
                norm=LogNorm(1e-3, 1))
    a[2].plot(x, det[izpk], 'k-', lw=1.4, label='deterministic')
    a[2].plot(x, mc[izpk], 'C3--', lw=1.0, label='MC 10⁵')
    a[2].set_yscale('log'); a[2].set_ylim(1e-4, 1.5); a[2].legend(fontsize=7)
    a[3].plot(z, det[:, ix0], 'k-', lw=1.4); a[3].plot(z, mc[:, ix0], 'C3--', lw=1.0)
    a[3].set_ylim(0, 1.05)
    a[2].text(0.5, 0.04, f'RMS={rms:.4f}', transform=a[2].transAxes, ha='center',
              fontsize=8, color='C3')
    if row == 0:
        a[0].set_title('deterministic', fontsize=10)
        a[1].set_title('Monte Carlo', fontsize=10)
        a[2].set_title('transverse (log)', fontsize=10)
        a[3].set_title('axial', fontsize=10)
    if row == len(CONFIGS) - 1:
        for k_ in range(2):
            a[k_].set_xlabel('x (μm)')
        a[2].set_xlabel('x (μm)'); a[3].set_xlabel('z (μm)')

plt.tight_layout()
out = os.path.join(OUT, 'verify_mc_configs.png')
fig.savefig(out, dpi=140, bbox_inches='tight')
plt.close(fig)
print(f"Saved → {out}")
