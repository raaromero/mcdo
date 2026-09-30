r"""Preview: keeping the 2-D shape of Lim & Saloma's fidelity maps when comparing NAs.

From the maps saved by fig_lim2002_fidelity_preview.py (2CE, θ = π, uniform
input, vector focus, NA 0.3, 0.5, 0.7, 0.9), in spot units x̃ = x_c NA/λ1,
z̃ = z_c NA²/λ1:

  (a) contour overlay: F = 0.8 (solid) and F = 0 (dashed) for every NA on one
      set of axes, so size, aspect and tilt compare directly;
  (b) difference maps: F_vector(NA) − F_scalar, one per NA; in spot units the
      scalar map is the same at every NA, so it is a single reference;
  (c) shape numbers: half-widths of the F = 0.8 region along x̃ and z̃ (cubic
      interpolation along the axes) and their ratio, against NA.

    python scripts/fig_lim2002_fidelity_shape_preview.py
    -> output/08_two_color/lim2002/fidelity_shape_preview.png
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.interpolate import RectBivariateSpline

from mcdo.style import apply as _apply_style
_apply_style()
matplotlib.rcParams.update({'font.size': 24, 'axes.titlesize': 28,
                            'axes.labelsize': 26, 'xtick.labelsize': 22,
                            'ytick.labelsize': 22, 'legend.fontsize': 20})

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002')
d = np.load(os.path.join(OUT, 'fidelity_vs_na_preview.npz'))
xt, zt = d['xt'], d['zt']
NAS = (0.3, 0.5, 0.7, 0.9)
COL = dict(zip(NAS, ('#9ecae1', '#4292c6', '#08519c', '#08306b')))
F = {na: d[f'F_na{na:g}'] for na in NAS}


def halfwidths(Fm):
    """Half-widths of F ≥ 0.8 along x̃ (z̃ = 0) and along z̃ (x̃ = 0), from a cubic interpolation."""
    s = RectBivariateSpline(zt, xt, Fm, kx=3, ky=3)
    xf, zf = np.linspace(0, xt[-1], 2001), np.linspace(0, zt[-1], 2001)
    fx, fz = s(0.0, xf)[0], s(zf, 0.0)[:, 0]
    return xf[np.argmax(fx < 0.8)], zf[np.argmax(fz < 0.8)]


FS = d['F_scalar']
fig = plt.figure(figsize=(28.0, 16.0))
gs = fig.add_gridspec(2, 4, height_ratios=(1.0, 0.85), hspace=0.5, wspace=0.45)

ax = fig.add_subplot(gs[0, 0:2])
ax.contour(xt, zt, FS, levels=[0.8], colors='#d62728', linewidths=4, linestyles=':')
ax.contour(xt, zt, FS, levels=[0.0], colors='#d62728', linewidths=3, linestyles=':')
ax.plot([], [], ':', color='#d62728', lw=4, label='Lim & Saloma scalar (any NA)')
for na in NAS:
    ax.contour(xt, zt, F[na], levels=[0.8], colors=[COL[na]], linewidths=3.5)
    ax.contour(xt, zt, F[na], levels=[0.0], colors=[COL[na]], linewidths=2.5, linestyles='--')
    ax.plot([], [], '-', color=COL[na], lw=3.5, label=f'vector, NA {na}')
ax.set_xlabel('x̃ = x$_c$ NA/λ$_1$'); ax.set_ylabel('z̃ = z$_c$ NA²/λ$_1$')
ax.set_title('(a) F = 0.8 (inner) and F = 0 (outer) contours'); ax.set_box_aspect(0.8)
ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), frameon=False)

ax = fig.add_subplot(gs[0, 3])
hw = np.array([halfwidths(F[na]) for na in NAS])
hs = np.array(halfwidths(FS))
ax.plot(NAS, hw[:, 0] / hs[0], 'o-', color='#1f77b4', lw=4, ms=12, label='half-width along x̃')
ax.plot(NAS, hw[:, 1] / hs[1], 's-', color='#9467bd', lw=4, ms=12, label='half-width along z̃')
ax.plot(NAS, (hw[:, 1] / hw[:, 0]) / (hs[1] / hs[0]), '^--', color='#555555', lw=3, ms=12, label='aspect z̃/x̃')
ax.axhline(1, color='#d62728', lw=3, ls=':')
ax.set_xlabel('NA'); ax.set_ylabel('vector / scalar')
ax.set_title('(c) shape numbers')
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), frameon=False)

lim = max(np.abs(F[na] - FS).max() for na in NAS)
for i, na in enumerate(NAS):
    ax = fig.add_subplot(gs[1, i])
    pm = ax.pcolormesh(xt, zt, F[na] - FS, cmap='RdBu_r', vmin=-lim, vmax=lim, shading='nearest')
    ax.contour(xt, zt, FS, levels=[0.8], colors='k', linewidths=2)
    ax.set_title(f'NA {na}'); ax.set_box_aspect(1.0)
    ax.set_xlabel('x̃')
    if i == 0:
        ax.set_ylabel('z̃')
cb = fig.colorbar(pm, ax=fig.axes[-4:], fraction=0.015, pad=0.02)
cb.set_label('ΔF = F$_{vector}$ − F$_{scalar}$')
fig.text(0.07, 0.43, '(b) difference from Lim & Saloma’s scalar map; black: scalar F = 0.8', fontsize=28)
fig.suptitle('Preview: 2-D fidelity shape against NA, 2CE, θ = π, uniform input, vector (coarse grid)', fontsize=30, y=1.02)
fig.savefig(os.path.join(OUT, 'fidelity_shape_preview.png'), dpi=300, bbox_inches='tight')
print('half-widths (x̃, z̃):', {na: tuple(np.round(h, 3)) for na, h in zip(NAS, hw)})
