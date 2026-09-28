r"""Lim & Saloma (2002) Fig. 4 at three NAs: the peak signal surviving as a
function of where O′ sits, (x_c, z_c), vector (Richards–Wolf) focus in air.

    θ = π:    NA 0.5, 0.7, 0.9
    θ = π/2:  NA 0.5, 0.7, 0.9 (above NA 0.71 two lenses cannot cross in air;
              computed, not buildable)

Offsets on the paper's axes, x_c ±1 µm and z_c ±5 µm, at every NA, so the
shrinking tolerance reads directly; contours at 10–80% of the aligned peak.
2CE beams unpolarized; 2PE beams both polarized along y (full interference).

    python scripts/fig_lim2002_na_peakmaps.py
    -> output/08_two_color/lim2002/na_peakmaps_fig4{a,b,c,d}.png
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

from mcdo.twobeam import beam_field, intensity

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002')
L1, L2, L2P = 0.750, 0.656, 0.700
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


def peak_map(pair, na, theta):
    s0, s1 = XW.shape
    if pair == '2ce':
        I = lambda X, Z, lam, th: chunked(lambda x, z: 0.5 * sum(
            intensity(beam_field(x, z, lam, na, 1.0, theta=th, model='rw', psi=p)) for p in (0.0, np.pi / 2)), X, Z)
        I1, I2 = I(XW, ZW, L1, 0.0), I(XE, ZE, L2, theta)
        sig = lambda ix, iz: I1 * I2[MZ - iz:MZ - iz + s0, MX - ix:MX - ix + s1]
    else:
        E = lambda X, Z, th, k: np.stack([chunked(lambda x, z: beam_field(x, z, L2P, na, 1.0, theta=th, model='rw',
                                                                          psi=np.pi / 2)[c], X, Z) for c in range(3)])
        E1, E2 = E(XW, ZW, 0.0, 0), E(XE, ZE, theta, 0)
        sig = lambda ix, iz: np.sum(np.abs(E1 + E2[:, MZ - iz:MZ - iz + s0, MX - ix:MX - ix + s1]) ** 2, axis=0) ** 2
    ixs, izs = np.arange(-MX, MX + 1, SX), np.arange(-MZ, MZ + 1, SZ)
    p0 = sig(0, 0).max()
    P = np.array([[sig(ix, iz).max() / p0 for ix in ixs] for iz in izs])
    return ixs * DX, izs * DZ, P


for tag, pair, th, lab in PANELS:
    fig, axes = plt.subplots(1, 3, figsize=(21.0, 8.2))
    for ax, na in zip(axes, (0.5, 0.7, 0.9)):
        xc, zc, P = peak_map(pair, na, th)
        cs = ax.contour(xc, zc, 100 * P, levels=[10, 20, 40, 60, 80], colors='k', linewidths=2.0)
        ax.clabel(cs, fmt='%d', fontsize=20)
        ax.set_xlabel('x$_c$ (µm)'); ax.set_ylabel('z$_c$ (µm)')
        ax.set_box_aspect(1.0)
        ax.set_xticks([-1.0, 0.0, 1.0]); ax.set_yticks([-4, -2, 0, 2, 4])
        ax.set_title(f'NA {na}' + (' *' if th == np.pi / 2 and na > 0.71 else ''))
        i0, j0 = np.argmin(np.abs(zc)), np.argmin(np.abs(xc))
        print(f'Fig. 4({tag}) {lab}, NA {na}: peak at x_c = 0.5 µm {100 * np.interp(0.5, xc, P[i0]):.0f}%, '
              f'at z_c = 1 µm {100 * np.interp(1.0, zc, P[:, j0]):.0f}%', flush=True)
    note = '   * not buildable in air (NA > 0.71)' if th == np.pi / 2 else ''
    fig.suptitle(f'Fig. 4({tag}): peak surviving, % of aligned, {lab}, vector{note}', fontsize=30, y=1.03)
    plt.tight_layout()
    fig.savefig(os.path.join(OUT, f'na_peakmaps_fig4{tag}.png'), dpi=600, bbox_inches='tight')
    plt.close(fig)
print('Saved -> na_peakmaps_fig4a..d.png')
