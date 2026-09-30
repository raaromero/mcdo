r"""Preview: how to present Linfoot fidelity maps as a function of NA.

One case (2CE, θ = π, uniform input) on a coarse grid, laid out the way the
full study would be:

  (a) F over the offset of O′ at NA 0.3, 0.5, 0.7, 0.9, with the offsets in
      units of the spot, x̃ = x_c NA/λ1 across and z̃ = z_c NA²/λ1 along. If
      NA only rescaled the focus, the four maps would be identical; what
      changes between them is the effect of NA itself.
  (b) one number per map, the area where F ≥ 0.8: in µm² (it shrinks as NA
      grows) and in spot units (flat for the paraxial scalar model by
      construction, so any drift in the vector curve is the vector effect).

Linfoot F = 1 − ⟨(t − a)²⟩/⟨t²⟩ as Lim & Saloma define it (p. 126): t the
aligned PSF, a the misaligned one, each scaled to its own peak, averaged over
the window. Vector (Richards–Wolf) beams unpolarized; paraxial scalar for
comparison in (b). Air, λ1 = 750 nm, λ2 = 656 nm.

    python scripts/fig_lim2002_fidelity_preview.py
    -> output/08_two_color/lim2002/fidelity_vs_na_preview.png, fidelity_vs_na_preview.npz
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from scipy.interpolate import RectBivariateSpline

from mcdo.style import apply as _apply_style
_apply_style()
matplotlib.rcParams.update({'font.size': 24, 'axes.titlesize': 30,
                            'axes.labelsize': 28, 'xtick.labelsize': 22,
                            'ytick.labelsize': 22, 'legend.fontsize': 22})

from mcdo import linfoot
from mcdo.twobeam import beam_field, intensity

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002')
L1, L2 = 0.750, 0.656
# grids in spot units: window 100 × 100, offsets every 4 window steps
DXS, DZS, NW = 0.02, 0.05, 50                  # window x̃ ±1, z̃ ±2.5
STEP, NOFF = 4, 10                             # offsets x̃ ±0.8, z̃ ±2.0 (21 × 21)
M = STEP * NOFF


def intens(x, z, lam, na, theta, model):
    if model == 'scalar':
        return intensity(beam_field(x, z, lam, na, theta=theta))
    return 0.5 * sum(intensity(beam_field(x, z, lam, na, theta=theta, model='rw', psi=p)) for p in (0.0, np.pi / 2))


def fidelity_map(na, model):
    sx, sz = L1 / na, L1 / na ** 2             # µm per spot unit, across and along
    xs, zs = np.arange(-NW, NW) * DXS, np.arange(-NW, NW) * DZS
    xe, ze = np.arange(-NW - M, NW + M) * DXS, np.arange(-NW - M, NW + M) * DZS
    XW, ZW = np.meshgrid(xs * sx, zs * sz)
    XE, ZE = np.meshgrid(xe * sx, ze * sz)
    I1 = intens(XW, ZW, L1, na, 0.0, model)
    I2 = intens(XE, ZE, L2, na, np.pi, model)
    n0, n1 = XW.shape
    psf = lambda ix, iz: I1 * I2[M - iz:M - iz + n0, M - ix:M - ix + n1]
    t = psf(0, 0); t = t / t.max()
    offs = np.arange(-NOFF, NOFF + 1) * STEP
    Fm = np.array([[linfoot.fidelity(t, (a := psf(ix, iz)) / a.max()) for ix in offs] for iz in offs])
    return offs * DXS, offs * DZS, Fm


def area(xt, zt, Fm, na):
    """Area where F ≥ 0.8, in spot units² and in µm², from a cubic interpolation of the map (20× finer)."""
    fine = RectBivariateSpline(zt, xt, Fm, kx=3, ky=3)
    xf, zf = np.linspace(xt[0], xt[-1], 20 * len(xt)), np.linspace(zt[0], zt[-1], 20 * len(zt))
    a = np.count_nonzero(fine(zf, xf) >= 0.8) * (xf[1] - xf[0]) * (zf[1] - zf[0])
    return a, a * (L1 / na) * (L1 / na ** 2)


maps = {na: fidelity_map(na, 'rw') for na in (0.3, 0.5, 0.7, 0.9)}
curve_na = np.array([0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
curves = {m: np.array([area(*fidelity_map(na, m), na) for na in curve_na]) for m in ('rw', 'scalar')}
np.savez_compressed(os.path.join(OUT, 'fidelity_vs_na_preview.npz'), curve_na=curve_na,
                    area_vector=curves['rw'], area_scalar=curves['scalar'],
                    **{f'F_na{na:g}': m[2] for na, m in maps.items()}, xt=maps[0.5][0], zt=maps[0.5][1],
                    F_scalar=fidelity_map(0.5, 'scalar')[2])   # the scalar map is the same at every NA in spot units

fig = plt.figure(figsize=(24.0, 15.0))
gs = GridSpec(2, 4, figure=fig, height_ratios=(1.0, 0.9), hspace=0.45, wspace=0.55)
for i, (na, (xt, zt, Fm)) in enumerate(maps.items()):
    ax = fig.add_subplot(gs[0, i])
    pm = ax.pcolormesh(xt, zt, Fm, cmap='viridis', vmin=-1, vmax=1, shading='nearest')
    cs = ax.contour(xt, zt, Fm, levels=[0.8], colors='w', linewidths=3)
    ax.set_title(f'NA {na}')
    ax.set_xlabel('x̃ = x$_c$ NA/λ$_1$')
    if i == 0:
        ax.set_ylabel('z̃ = z$_c$ NA²/λ$_1$')
    ax.set_box_aspect(1.0)
cb = fig.colorbar(pm, ax=[fig.axes[i] for i in range(4)], fraction=0.015, pad=0.02)
cb.set_label('Fidelity F')
fig.text(0.07, 0.93, '(a) F over the offset of O′, offsets in spot units; white: F = 0.8', fontsize=28)

ax = fig.add_subplot(gs[1, 0:2])
ax.loglog(curve_na, curves['rw'][:, 1], 'o-', color='#1f77b4', lw=4, ms=10, label='Vector (Richards–Wolf)')
ax.loglog(curve_na, curves['scalar'][:, 1], 's:', color='#d62728', lw=3, ms=10, mfc='none', mew=2.5, label='Paraxial scalar')
ax.set_xlabel('NA'); ax.set_ylabel('Area with F ≥ 0.8 (µm²)')
ax.set_title('(b) in µm²: shrinks as NA grows')
ax.set_xticks([0.2, 0.3, 0.5, 0.7, 0.9]); ax.xaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%g'))
ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.22), ncol=2, frameon=False)
ax = fig.add_subplot(gs[1, 2:4])
ax.plot(curve_na, curves['rw'][:, 0], 'o-', color='#1f77b4', lw=4, ms=10)
ax.plot(curve_na, curves['scalar'][:, 0], 's:', color='#d62728', lw=3, ms=10, mfc='none', mew=2.5)
ax.set_xlabel('NA'); ax.set_ylabel('Area with F ≥ 0.8 (spot units²)')
ax.set_title('(b) in spot units: drift = the NA effect')
ax.set_ylim(0, None)
fig.suptitle('Preview: fidelity against NA, 2CE, θ = π, uniform input (coarse grid)', fontsize=32, y=0.99)
fig.savefig(os.path.join(OUT, 'fidelity_vs_na_preview.png'), dpi=300, bbox_inches='tight')
print('Saved -> fidelity_vs_na_preview.png')
for m in ('rw', 'scalar'):
    print(m, 'area (spot²):', np.round(curves[m][:, 0], 3), ' µm²:', np.round(curves[m][:, 1], 3))
