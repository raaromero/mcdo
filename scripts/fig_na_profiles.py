"""Focal profiles as the numerical aperture is raised, for each illumination,
and the field components that cause the departure.

Panels (also saved individually to output/02_na_apodization/panels/):
  p1 — uniform illumination: vector against scalar at four numerical apertures
  p2 — truncated Gaussian: the same comparison
  p3 — the three field components at high numerical aperture

The first two show where the curves come apart. The third shows why: the
longitudinal component, absent at low numerical aperture, grows until it fills
the region where the scalar profile has its zero.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo.style import apply as _apply_style
_apply_style()

from mcdo import SimConfig
from mcdo.rw_integrals import compute_integrals
from mcdo.apodization import gaussian
from mcdo.debye import scalar_debye
from mcdo.components import full as vec_intensity
from mcdo.figio import save_panels

LAM, N_MED, NT = 0.750, 1.3, 801
NA_SHOW = [0.1, 0.3, 0.7, 0.9]
ALPHA_T = 4.0
V_MAX = 8.0
OUTDIR = os.path.join(os.path.dirname(__file__), '..', 'output', '02_na_apodization')
Z0 = np.array([0.0])
COLORS = plt.cm.viridis(np.linspace(0.0, 0.85, len(NA_SHOW)))


def fwhm_v(v, I):
    I = I / I.max()
    b = np.where(I < 0.5)[0]
    if len(b) == 0:
        return np.nan
    i = b[0]
    return 2 * (v[i - 1] + (v[i] - v[i - 1]) * (I[i - 1] - 0.5) / (I[i - 1] - I[i]))


def panel(ax, alpha_t, title):
    print(f'{title}:')
    for xna, c in zip(NA_SHOW, COLORS):
        cfg = SimConfig(lam_c=LAM, X_NA=xna, n=N_MED, tau=np.inf, N_freq=3, N_theta=NT)
        v = np.linspace(0.0, V_MAX, 401)
        r = v / (cfg.k_c * cfg.sin_alpha)
        apod = gaussian(alpha_t, cfg.sin2_alpha) if alpha_t > 0 else None
        I0, I1, I2 = compute_integrals(r, Z0, cfg.k_c, cfg.alpha, NT, apodization=apod)
        vec = vec_intensity(I0[0], I1[0], I2[0])
        sca = scalar_debye(r, Z0, cfg.k_c, cfg.alpha, NT, apodization=apod)[0]
        vec, sca = vec / vec.max(), sca / sca.max()
        ax.semilogy(v, vec, '-', color=c, lw=2.0, label=f'NA {xna:g}, vector')
        ax.semilogy(v, sca, ':', color=c, lw=2.0)
        d = 100 * abs(fwhm_v(v, vec) / fwhm_v(v, sca) - 1)
        print(f'  NA {xna:g}:  focal width differs from scalar by {d:5.2f} per cent')
    ax.set_ylim(1e-5, 2.0); ax.set_xlim(0, V_MAX)
    ax.set_xlabel('Optical radial coordinate')
    ax.set_ylabel('Normalized intensity')
    ax.set_title(title, fontsize=11)
    ax.grid(alpha=0.25, which='both')
    ax.legend(fontsize=8, loc='upper right', title='Solid: Vector, Dotted: Scalar')


fig, axes = plt.subplots(1, 3, figsize=(30.8, 6.5))
panel(axes[0], 0.0, '(a) Uniform illumination, 750 nm')
panel(axes[1], ALPHA_T, f'(b) Gaussian, truncation coefficient {ALPHA_T:g}, 750 nm')

# ── p3: the components that cause it ──────────────────────────────────────
ax = axes[2]
cfg = SimConfig(lam_c=LAM, X_NA=1.2, n=N_MED, tau=np.inf, N_freq=3, N_theta=NT)
v = np.linspace(0.0, V_MAX, 401)
r = v / (cfg.k_c * cfg.sin_alpha)
I0, I1, I2 = compute_integrals(r, Z0, cfg.k_c, cfg.alpha, NT)
I0, I1, I2 = I0[0], I1[0], I2[0]
ex = np.abs(I0) ** 2 + 0.5 * np.abs(I2) ** 2
ey = 0.5 * np.abs(I2) ** 2
ez = 2 * np.abs(I1) ** 2
tot = ex + ey + ez
n = tot.max()
ax.semilogy(v, tot / n, 'k-', lw=2.0, label='total intensity')
ax.semilogy(v, ex / n, '-', color='#1f77b4', lw=2.0, label='transverse, along the polarization')
ax.semilogy(v, ey / n, '--', color='#2ca02c', lw=2.0, label='transverse, orthogonal')
ax.semilogy(v, ez / n, '-.', color='#c0504d', lw=2.0, label='longitudinal')
ax.set_ylim(1e-5, 2.0); ax.set_xlim(0, V_MAX)
ax.set_xlabel('Optical radial coordinate')
ax.set_ylabel('Normalized intensity')
ax.set_title('(c) Field components, numerical aperture 1.2, 750 nm', fontsize=11)
ax.grid(alpha=0.25, which='both')
ax.legend(fontsize=8, loc='upper right')
print(f'\nAt numerical aperture 1.2 the longitudinal component carries '
      f'{100 * np.trapezoid(ez * v, v) / np.trapezoid(tot * v, v):.1f} per cent of the focal energy')

plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUTDIR, 'panels'), 'fig_na_profiles')
out = os.path.join(OUTDIR, 'fig_na_profiles.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f'Saved → {out}')
