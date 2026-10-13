r"""Lim & Saloma (2002) Fig. 4 at three NAs: the peak signal surviving as a
function of where O′ sits, (x_c, z_c), vector (Richards–Wolf) focus in air.

    θ = π:    NA 0.5, 0.7, 0.9
    θ = π/2:  NA 0.5, 0.7, 0.9 (above NA 0.71 two lenses cannot cross in air;
              computed, not buildable)

Offsets on the paper's axes, x_c ±1 µm and z_c ±5 µm, at every NA, so the
shrinking tolerance reads directly; contours at 10–80% of the aligned peak.
2CE beams unpolarized; 2PE beams both polarized along y (full interference).

    python scripts/fig_lim2002_na_peakmaps.py
    ALPHA_T=4 python scripts/fig_lim2002_na_peakmaps.py   # Gaussian input, suffix _at4
    WATER=1 python scripts/fig_lim2002_na_peakmaps.py     # adds θ = π/2 at NA 0.9 in water (P_na0.9_n1.33)
    -> output/08_two_color/lim2002/na_peakmaps_fig4{a,b,c,d}.png, and the maps themselves in
       na_peakmaps_fig4{a,b,c,d}.npz (x_c_um, z_c_um, P_na0.5, P_na0.7, P_na0.9; saved after each NA)
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo.style import apply as _apply_style
_apply_style()
matplotlib.rcParams.update({'font.size': 24, 'axes.titlesize': 32,
                            'axes.labelsize': 28, 'xtick.labelsize': 24,
                            'ytick.labelsize': 24, 'legend.fontsize': 24})

from mcdo.apodization import gaussian
from mcdo.twobeam import beam_field, intensity

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002')
L1, L2, L2P = 0.750, 0.656, 0.700
AT = float(os.environ.get('ALPHA_T', '0'))       # input truncation; 0 = uniform, Lim & Saloma's case
SUF = '' if AT == 0 else f'_at{AT:g}'
APOD = lambda na, n=1.0: gaussian(AT, (na / n) ** 2) if AT else None
DX, DZ = 0.02, 0.05                     # µm, PSF grid
NX, NZ = 60, 110                        # window ±1.2 × ±5.5 µm
SX, SZ = 2, 4                           # offset steps: 0.04 µm across, 0.2 µm along
MX, MZ = 50, 100                        # offsets to ±1.0 × ±5.0 µm
PANELS = [('a', '2ce', np.pi, '2CE, θ = π'), ('b', '2pe', np.pi, '2PE, θ = π'),
          ('c', '2ce', np.pi / 2, '2CE, θ = π/2'), ('d', '2pe', np.pi / 2, '2PE, θ = π/2')]

XW, ZW = np.meshgrid(np.arange(-NX, NX + 1) * DX, np.arange(-NZ, NZ + 1) * DZ)
XE, ZE = np.meshgrid(np.arange(-NX - MX, NX + MX + 1) * DX, np.arange(-NZ - MZ, NZ + MZ + 1) * DZ)


def chunked(f, X, Z, chunk=15000):
    fx, fz = X.ravel(), Z.ravel()
    return np.concatenate([f(fx[i:i + chunk], fz[i:i + chunk]) for i in range(0, fx.size, chunk)]).reshape(X.shape)


def peak_map(pair, na, theta, n=1.0):
    s0, s1 = XW.shape
    if pair == '2ce':
        I = lambda X, Z, lam, th: chunked(lambda x, z: 0.5 * sum(
            intensity(beam_field(x, z, lam, na, n, theta=th, apodization=APOD(na, n), model='rw', psi=p)) for p in (0.0, np.pi / 2)), X, Z)
        I1, I2 = I(XW, ZW, L1, 0.0), I(XE, ZE, L2, theta)
        sig = lambda ix, iz: I1 * I2[MZ - iz:MZ - iz + s0, MX - ix:MX - ix + s1]
    else:
        E = lambda X, Z, th, k: np.stack([chunked(lambda x, z: beam_field(x, z, L2P, na, n, theta=th, apodization=APOD(na, n), model='rw',
                                                                          psi=np.pi / 2)[c], X, Z) for c in range(3)])
        E1, E2 = E(XW, ZW, 0.0, 0), E(XE, ZE, theta, 0)
        sig = lambda ix, iz: np.sum(np.abs(E1 + E2[:, MZ - iz:MZ - iz + s0, MX - ix:MX - ix + s1]) ** 2, axis=0) ** 2
    ixs, izs = np.arange(-MX, MX + 1, SX), np.arange(-MZ, MZ + 1, SZ)
    p0 = sig(0, 0).max()
    P = np.array([[sig(ix, iz).max() / p0 for ix in ixs] for iz in izs])
    return ixs * DX, izs * DZ, P


if os.environ.get('WATER') == '1':                  # crossed lenses at NA 0.9 do not fit in air: water, n = 1.33
    for tag, pair, th, lab in PANELS[2:]:
        path = os.path.join(OUT, f'na_peakmaps_fig4{tag}{SUF}.npz')
        data = dict(np.load(path))
        data['P_na0.9_n1.33'] = peak_map(pair, 0.9, th, 1.33)[2]
        np.savez_compressed(path, **data)
        print(f'Fig. 4({tag}) {lab}, NA 0.9 in water: saved', flush=True)
    sys.exit(0)
REPLOT = os.environ.get('REPLOT') == '1'             # redraw from the saved maps
for tag, pair, th, lab in PANELS:
    fig, axes = plt.subplots(1, 3, figsize=(18.2, 7.0))  # twice its width on the slide: 24-pt text shows at 12 pt
    maps = {}
    saved = np.load(os.path.join(OUT, f'na_peakmaps_fig4{tag}{SUF}.npz')) if REPLOT else None
    for ax, na in zip(axes, (0.5, 0.7, 0.9)):
        if REPLOT:
            xc, zc, P = saved['x_c_um'], saved['z_c_um'], saved[f'P_na{na:g}']
        else:
            xc, zc, P = peak_map(pair, na, th)
            maps[f'P_na{na:g}'] = P
            np.savez_compressed(os.path.join(OUT, f'na_peakmaps_fig4{tag}{SUF}.npz'), x_c_um=xc, z_c_um=zc, **maps)
        cs = ax.contour(xc, zc, 100 * P, levels=[10, 20, 40, 60, 80], cmap='viridis', linewidths=3.0)   # levels: shared colorbar
        ax.set_xlabel('x$_c$ (µm)'); ax.set_ylabel('z$_c$ (µm)')
        ax.set_box_aspect(1.0)
        ax.set_xticks([-1.0, 0.0, 1.0]); ax.set_yticks([-4, -2, 0, 2, 4])
        ax.set_title(f'NA {na}' + (' *' if th == np.pi / 2 and na > 0.71 else ''))
        i0, j0 = np.argmin(np.abs(zc)), np.argmin(np.abs(xc))
        print(f'Fig. 4({tag}) {lab}, NA {na}: peak at x_c = 0.5 µm {100 * np.interp(0.5, xc, P[i0]):.0f}%, '
              f'at z_c = 1 µm {100 * np.interp(1.0, zc, P[:, j0]):.0f}%', flush=True)
    note = ';  * lenses cannot cross' if th == np.pi / 2 else ''
    plt.tight_layout()
    fig.colorbar(cs, ax=list(axes), fraction=0.02, pad=0.02, ticks=cs.levels).set_label('Peak surviving (%)')
    fig.suptitle(f'Peak surviving (% of aligned), {lab}' + (f', α$_t$ = {AT:g}' if AT else '') + note, fontsize=32, y=1.03)
    fig.savefig(os.path.join(OUT, f'na_peakmaps_fig4{tag}{SUF}.png'), dpi=600, bbox_inches='tight')
    plt.close(fig)
print('Saved -> na_peakmaps_fig4a..d.png')
