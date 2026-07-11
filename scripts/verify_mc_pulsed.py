r"""
Validate the per-photon WAVELENGTH-sampling Monte Carlo
(`montecarlo.mc_pulsed_intensity`) against the deterministic spectral sum
(Eq. 10) in the clear limit, and show it fills the focal zeros the way a real
pulse does.

Each MC photon draws its wavelength from |E(ω)|² (multinomial over the spectral
nodes), interferes coherently within its wavelength, and adds incoherently
across wavelengths. The reference is the deterministic scalar spectral sum
I_det(P) = Σ_m |E(ω_m)|² |U(P,ω_m)|² over the SAME nodes (scalar_debye per node).
Agreement (RMS) → the wavelength sampling is unbiased; both fill the CW zeros.

NA=0.8, λ_c=750 nm, n=1.3, uniform pupil, scalar.
Output: output/06_monte_carlo/verify_mc_pulsed.png
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo import SimConfig
from mcdo.debye import scalar_debye
from mcdo.montecarlo import mc_pulsed_intensity

plt.rcParams.update({'font.size': 12, 'axes.titlesize': 12, 'axes.labelsize': 11,
                     'legend.fontsize': 9, 'axes.grid': True, 'grid.alpha': 0.25,
                     'savefig.dpi': 200})

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '06_monte_carlo')
N_PH = 250_000
x = np.linspace(-1.5, 1.5, 161)
z = np.linspace(-4.0, 4.0, 161)


def det_pulsed(cfg, r, zc, axis):
    """Deterministic scalar Eq.10 sum over the same spectral nodes."""
    omes = cfg.omega_grid(); W = np.where(omes > 0, cfg.spectral_power(omes), 0.0)
    tot = None
    for om, w in zip(omes, W):
        if w == 0:
            continue
        k = cfg.k_for_omega(om)
        I = scalar_debye(r, zc, k, cfg.alpha, cfg.N_theta)
        I = I[0] if axis == 'x' else I[:, 0]
        tot = w * I if tot is None else tot + w * I
    return tot / tot.max()


fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle('Per-photon wavelength-sampling MC vs deterministic Eq. 10 '
             '(clear limit, uniform, NA=0.8, τ=2 fs)', fontsize=13)

cfg = SimConfig(lam_c=0.750, X_NA=0.8, n=1.3, tau=2e-15, N_freq=41, N_theta=801)
rms_txt = {}

# transverse
det_x = det_pulsed(cfg, np.abs(x), np.array([0.0]), 'x')
cw_x = scalar_debye(np.abs(x), np.array([0.0]), cfg.k_c, cfg.alpha, cfg.N_theta)[0]
cw_x /= cw_x.max()
mc_x = mc_pulsed_intensity(cfg, x, np.zeros_like(x), np.zeros_like(x), N_PH,
                           rng=np.random.default_rng(0))
rms_txt['transverse'] = np.sqrt(np.mean((mc_x - det_x) ** 2))
ax = axes[0]
ax.semilogy(x * 1e3, np.clip(cw_x, 1e-5, None), color='0.6', lw=1.6, ls=':',
            label='CW (monochromatic) — zeros deep')
ax.semilogy(x * 1e3, np.clip(det_x, 1e-5, None), 'k-', lw=2,
            label='pulsed — deterministic Eq.10')
ax.semilogy(x * 1e3, np.clip(mc_x, 1e-5, None), 'o', color='C3', ms=3.4,
            mfc='none', mew=0.9, label='pulsed — wavelength-sampling MC')
ax.set_ylim(1e-4, 2); ax.set_xlabel('x (nm)'); ax.set_ylabel('intensity (norm.)')
ax.set_title(f'transverse (z=0)  ·  RMS(MC,det)={rms_txt["transverse"]:.4f}')
ax.legend()

# axial
det_z = det_pulsed(cfg, np.array([0.0]), z, 'z')
cw_z = scalar_debye(np.array([0.0]), z, cfg.k_c, cfg.alpha, cfg.N_theta)[:, 0]
cw_z /= cw_z.max()
mc_z = mc_pulsed_intensity(cfg, np.zeros_like(z), np.zeros_like(z), z, N_PH,
                           rng=np.random.default_rng(1))
rms_txt['axial'] = np.sqrt(np.mean((mc_z - det_z) ** 2))
ax = axes[1]
ax.semilogy(z, np.clip(cw_z, 1e-4, None), color='0.6', lw=1.6, ls=':',
            label='CW (monochromatic)')
ax.semilogy(z, np.clip(det_z, 1e-4, None), 'k-', lw=2, label='pulsed — Eq.10')
ax.semilogy(z, np.clip(mc_z, 1e-4, None), 'o', color='C3', ms=3.4, mfc='none',
            mew=0.9, label='pulsed — wavelength MC')
ax.set_ylim(1e-3, 2); ax.set_xlabel('z (µm)'); ax.set_ylabel('intensity (norm.)')
ax.set_title(f'axial (x=0)  ·  RMS(MC,det)={rms_txt["axial"]:.4f}')
ax.legend()

plt.tight_layout()
out = os.path.join(OUT, 'verify_mc_pulsed.png')
fig.savefig(out, bbox_inches='tight'); plt.close(fig)

print("Per-photon wavelength-sampling MC vs deterministic Eq.10 (τ=2 fs):")
for k, v in rms_txt.items():
    print(f"  {k:<11} RMS = {v:.4f}")
print(f"Saved → {out}")
