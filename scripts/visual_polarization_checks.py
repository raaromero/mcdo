"""
Check 8 — input-polarization variants (linear-x remains the headline).

Circular input: |E|² = |I₀|²+|I₂|²+2|I₁|² (φ-independent, no zeros) — old
mcdo's convention. This check quantifies the circular-pol NA thresholds and
shows why the old progress report's numbers looked lenient.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo import SimConfig
from mcdo.rw_integrals import compute_integrals
from mcdo.debye import scalar_debye, airy_intensity
from mcdo.polarization import linear_x_xcut, linear_x_ycut, circular

LAM, N_MED, NT = 0.750, 1.3, 1001
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '02_na_apodization')

v_arr = np.linspace(0.0, 10.0, 401)


def cfg_at(xna):
    return SimConfig(lam_c=LAM, X_NA=xna, n=N_MED, tau=np.inf, N_freq=3, N_theta=NT)


def all_profiles(cfg):
    r = v_arr / (cfg.k_c * cfg.sin_alpha)
    I0, I1, I2 = compute_integrals(r, np.array([0.0]), cfg.k_c, cfg.alpha, NT)
    I0, I1, I2 = I0[0], I1[0], I2[0]
    norm = lambda I: I / I.max()
    I_s = scalar_debye(r, np.array([0.0]), cfg.k_c, cfg.alpha, NT)[0]
    return (norm(linear_x_xcut(I0, I1, I2)), norm(linear_x_ycut(I0, I1, I2)),
            norm(circular(I0, I1, I2)), norm(I_s))


def fwhm_x(x, y):
    half = y.max() / 2.0
    i = np.where(np.diff((y >= half).astype(int)))[0][0]
    return 2.0 * np.interp(half, [y[i + 1], y[i]], [x[i + 1], x[i]])


XNA_vals = np.arange(0.05, 1.26, 0.05)
dev = {'linear x-cut': [], 'linear y-cut': [], 'circular': []}
for xna in XNA_vals:
    I_x, I_y, I_c, I_s = all_profiles(cfg_at(xna))
    f_s = fwhm_x(v_arr, I_s)
    dev['linear x-cut'].append(100 * abs(fwhm_x(v_arr, I_x) / f_s - 1))
    dev['linear y-cut'].append(100 * abs(fwhm_x(v_arr, I_y) / f_s - 1))
    dev['circular'].append(100 * abs(fwhm_x(v_arr, I_c) / f_s - 1))

print("FWHM deviation vs scalar — thresholds by input polarization (uniform):")
for name, d in dev.items():
    d = np.array(d)
    t1 = XNA_vals[np.argmax(d > 1.0)] if (d > 1.0).any() else np.nan
    t5 = XNA_vals[np.argmax(d > 5.0)] if (d > 5.0).any() else np.nan
    print(f"  {name:<14} >1% at X_NA={t1}   >5% at X_NA={t5}")

# ── Figure ─────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(14, 4.4))
fig.suptitle('Check 8 — input polarization: linear-x cuts vs circular '
             '(circular = azimuthal combination; no zeros)', fontsize=11)

airy = airy_intensity(v_arr)
for ax, xna in zip(axes[:2], [0.8, 1.2]):
    I_x, I_y, I_c, I_s = all_profiles(cfg_at(xna))
    ax.plot(v_arr, airy, '-', color='0.7', lw=4, label='Airy (NA→0)')
    ax.plot(v_arr, I_x, 'C1--', lw=1.2, label='linear x, x-cut')
    ax.plot(v_arr, I_y, 'C0-', lw=1.2, label='linear x, y-cut')
    ax.plot(v_arr, I_c, 'C3-.', lw=1.4, label='circular')
    ax.plot(v_arr, I_s, 'C2:', lw=1.6, label='scalar')
    ax.set_yscale('log'); ax.set_ylim(1e-6, 1.5)
    ax.set_xlabel('Optical radial coordinate v'); ax.set_ylabel('Normalized intensity')
    ax.set_title(f'NA = {xna}', fontsize=10)
    ax.legend(fontsize=7.5)

ax = axes[2]
for (name, d), st in zip(dev.items(), ['C1s--', 'C0o-', 'C3^-.']):
    ax.plot(XNA_vals, d, st, ms=3.5, lw=1.1, label=name)
ax.axhline(1, color='gray', lw=0.6, ls=':')
ax.axhline(5, color='gray', lw=0.6, ls='--')
ax.set_yscale('log'); ax.set_ylim(1e-3, 60)
ax.set_xlabel('NA (n=1.3)'); ax.set_ylabel('FWHM deviation from scalar (%)')
ax.set_title('Threshold depends on input polarization', fontsize=10)
ax.legend(fontsize=8)

plt.tight_layout()
out = os.path.join(OUT, 'check8_polarization.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f"Saved → {out}")
