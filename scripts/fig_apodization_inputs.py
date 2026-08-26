"""Gaussian illumination — how the pupil INPUT changes with the truncation
coefficient α, and the focal profile that results.

    A(ρ) = exp(-α ρ²),      ρ = r_aperture-normalized radius
    α    = (r_aperture / w_beam)²

Panels (also saved individually to output/02_na_apodization/panels/):
  p1 — input amplitude A(ρ) across the pupil for a range of α
  p2 — resulting focal-plane intensity (Richards-Wolf, y-cut) for the same α

α → 0 is uniform illumination; α = 1 gives 37% amplitude at the aperture edge;
α ≥ 4 is effectively untruncated (2% at the edge)  [Horvath & Bor 2003].
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
from mcdo.components import full as vec_intensity
from mcdo.figio import save_panels, mark_focus

LAM_C, N_MED, X_NA = 0.750, 1.3, 0.8
ALPHAS = [0.0, 0.5, 1.0, 2.0, 4.0, 8.0]
OUTDIR = os.path.join(os.path.dirname(__file__), '..', 'output', '02_na_apodization')

cfg = SimConfig(lam_c=LAM_C, X_NA=X_NA, n=N_MED, tau=np.inf, N_freq=1, N_theta=1201)
colors = plt.cm.viridis(np.linspace(0.0, 0.85, len(ALPHAS)))

fig, axes = plt.subplots(1, 3, figsize=(30.8, 6.5))

# ── p1: the input across the pupil ────────────────────────────────────────
rho = np.linspace(-1.0, 1.0, 400)
ax = axes[0]
for a, c in zip(ALPHAS, colors):
    lab = 'uniform ($\\alpha$=0)' if a == 0 else f'$\\alpha$={a:g}'
    ax.plot(rho, np.exp(-a * rho ** 2), color=c, lw=2, label=lab)
ax.set_xlabel('Normalized pupil radius  $\\rho$')
ax.set_ylabel('Input amplitude  $A(\\rho)$')
ax.set_title('(a) Pupil illumination', fontsize=10)
ax.set_xlim(-1, 1); ax.set_ylim(0, 1.05); ax.grid(alpha=0.25)
ax.legend(fontsize=8, loc='upper left', bbox_to_anchor=(1.02, 1.0), frameon=False)

# ── p2: the focal profile that results ────────────────────────────────────
ks = cfg.k_c * np.sin(cfg.alpha)
r = np.linspace(0, 6.5 / ks, 400)      # physical radius (μm) out to v = 6.5
z0 = np.array([0.0])
ax = axes[1]
print('Focal FWHM (v units) vs truncation coefficient:')
for a, c in zip(ALPHAS, colors):
    apod = gaussian(a, cfg.sin2_alpha) if a > 0 else None
    I0, I1, I2 = compute_integrals(r, z0, cfg.k_c, cfg.alpha, cfg.N_theta, apodization=apod)
    I = vec_intensity(I0[0], I1[0], I2[0])
    I = I / I.max()
    lab = 'uniform ($\\alpha$=0)' if a == 0 else f'$\\alpha$={a:g}'
    ax.plot(r, I, color=c, lw=2, label=lab)
    below = np.where(I < 0.5)[0]
    if len(below):
        i = below[0]
        fw = 2 * (r[i - 1] + (r[i] - r[i - 1]) * (I[i - 1] - 0.5) / (I[i - 1] - I[i]))
        print(f'  alpha={a:>4g}:  FWHM = {fw * 1000:.1f} nm')
ax.set_xlabel('Radial position r (μm)')
ax.set_ylabel('Normalized intensity')
ax.set_title('(b) Focal profile, numerical aperture 0.8, 750 nm', fontsize=10)
ax.set_xlim(0, r[-1]); ax.grid(alpha=0.25)
ax.legend(fontsize=8, loc='upper left', bbox_to_anchor=(1.02, 1.0), frameon=False)

# ── p3: focal width against the truncation coefficient ────────────────────
alpha_fine = [0.0, 0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0]
widths_nm = []
for a in alpha_fine:
    apod = gaussian(a, cfg.sin2_alpha) if a > 0 else None
    I0, I1, I2 = compute_integrals(r, z0, cfg.k_c, cfg.alpha, cfg.N_theta, apodization=apod)
    I = vec_intensity(I0[0], I1[0], I2[0]); I = I / I.max()
    below = np.where(I < 0.5)[0]
    i = below[0]
    widths_nm.append(2000 * (r[i - 1] + (r[i] - r[i - 1]) * (I[i - 1] - 0.5) / (I[i - 1] - I[i])))
ax = axes[2]
ax.plot(alpha_fine, widths_nm, 'o-', color='#1f77b4', lw=2.0, ms=6)
ax.set_xlabel('Truncation coefficient')
ax.set_ylabel('Focal-spot FWHM (nm)')
ax.set_title('(c) Focal width against truncation coefficient, numerical aperture 0.8, 750 nm', fontsize=11)
ax.grid(alpha=0.25)
print('FWHM vs truncation coefficient:', dict(zip(alpha_fine, [round(w) for w in widths_nm])))

plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUTDIR, 'panels'), 'fig_apodization_inputs')
out = os.path.join(OUTDIR, 'fig_apodization_inputs.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f'Saved → {out}')

# ── paired field maps: uniform against Gaussian, same scale ────────────────
fig2, axes2 = plt.subplots(1, 2, figsize=(20.5, 8.2), sharey=True)
z_arr = np.linspace(-4.0, 4.0, 220)
r_map = np.linspace(0.0, 1.5, 140)
LEVELS = [0.01, 0.05, 0.10, 0.20, 0.30, 0.50, 0.70, 0.90]
for ax2, a, title in [(axes2[0], 0.0, '(a) Uniform input'),
                      (axes2[1], 4.0, '(b) Gaussian input, truncation coefficient 4')]:
    apod = gaussian(a, cfg.sin2_alpha) if a > 0 else None
    M0, M1, M2 = compute_integrals(r_map, z_arr, cfg.k_c, cfg.alpha, 401, apodization=apod)
    I = vec_intensity(M0, M1, M2); I = I / I.max()
    r_full = np.concatenate([-r_map[::-1], r_map[1:]])
    I_full = np.concatenate([I[:, ::-1], I[:, 1:]], axis=1)
    cs = ax2.contour(r_full, z_arr, I_full, levels=LEVELS, colors='k', linewidths=1.0)
    ax2.clabel(cs, inline=True, fontsize=9, fmt='%.2f')
    mark_focus(ax2, r_full, z_arr, I_full, airy_um=0.61 * LAM_C / X_NA)
    ax2.set_xlabel('Radial position r (μm)')
    ax2.set_title(title + ', NA 0.8, 750 nm', fontsize=12)
    ax2.grid(alpha=0.2)
axes2[0].set_ylabel('Axial position z (μm)')
out2 = os.path.join(OUTDIR, 'fig_apodization_maps.png')
fig2.savefig(out2, dpi=300, bbox_inches='tight')
plt.close(fig2)
print(f'Saved → {out2}')
