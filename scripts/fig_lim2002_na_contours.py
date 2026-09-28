r"""Lim & Saloma (2002) Figs. 2–3, every panel, at three NAs side by side, with
the vector (Richards–Wolf) focus in air.

    θ = π:    NA 0.5, 0.7, 0.9
    θ = π/2:  NA 0.5, 0.6, 0.7   (two cones cannot cross in air above 0.71)

Paper's axes (x ±1 µm, z ±5 µm, square frames) and contour levels (1–80% of
peak) at every NA, so the change of size and shape reads directly. 2CE beams
are unpolarized; 2PE beams are both polarized along y, perpendicular to both
optical axes (full interference, the case the scalar model describes).
Fig. 3 panels have O′ = (0.4, 1.0) µm.

    python scripts/fig_lim2002_na_contours.py
    -> output/08_two_color/lim2002/na_contours_fig2a.png ... na_contours_fig3d.png
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
LEVELS = [1, 10, 20, 40, 60, 80]
x = np.linspace(-1.0, 1.0, 201)
z = np.linspace(-5.0, 5.0, 401)
X, Z = np.meshgrid(x, z)
NAS = {np.pi: (0.5, 0.7, 0.9), np.pi / 2: (0.5, 0.6, 0.7)}
PANELS = [('a', '2ce', np.pi, '2CE, θ = π'), ('b', '2pe', np.pi, '2PE, θ = π'),
          ('c', '2ce', np.pi / 2, '2CE, θ = π/2'), ('d', '2pe', np.pi / 2, '2PE, θ = π/2')]


def chunked(f, chunk=15000):
    fx, fz = X.ravel(), Z.ravel()
    return np.concatenate([f(fx[i:i + chunk], fz[i:i + chunk]) for i in range(0, fx.size, chunk)]).reshape(X.shape)


def psf(pair, na, theta, xc, zc):
    if pair == '2ce':
        I = lambda lam, th, a, b: chunked(lambda px, pz: 0.5 * sum(
            intensity(beam_field(px, pz, lam, na, 1.0, theta=th, xc=a, zc=b, model='rw', psi=p))
            for p in (0.0, np.pi / 2)))
        return I(L1, 0.0, 0.0, 0.0) * I(L2, theta, xc, zc)
    return chunked(lambda px, pz: intensity(
        beam_field(px, pz, L2P, na, 1.0, model='rw', psi=np.pi / 2)
        + beam_field(px, pz, L2P, na, 1.0, theta=theta, xc=xc, zc=zc, model='rw', psi=np.pi / 2)) ** 2)


for fig_no, (xc, zc), where in ((2, (0.0, 0.0), 'aligned'), (3, (0.4, 1.0), 'O′ = (0.4, 1.0) µm')):
    for tag, pair, th, lab in PANELS:
        fig, axes = plt.subplots(1, 3, figsize=(21.0, 8.2))
        for ax, na in zip(axes, NAS[th]):
            F = psf(pair, na, th, xc, zc)
            F = 100 * F / F.max()
            cs = ax.contour(x, z, F, levels=LEVELS, colors='k', linewidths=2.0)
            ax.clabel(cs, fmt='%d', fontsize=20)
            ax.set_xlabel('x (µm)'); ax.set_ylabel('z (µm)')
            ax.set_box_aspect(1.0)
            ax.set_xticks([-1.0, 0.0, 1.0]); ax.set_yticks([-4, -2, 0, 2, 4])
            ax.set_title(f'NA {na}')
            iz, ix = np.unravel_index(np.argmax(F), F.shape)
            print(f'Fig. {fig_no}({tag}) {lab}, {where}, NA {na}: peak at ({x[ix]:+.2f}, {z[iz]:+.2f}) µm', flush=True)
        fig.suptitle(f'Fig. {fig_no}({tag}): {lab}, {where}, vector', fontsize=32, y=1.03)
        plt.tight_layout()
        fig.savefig(os.path.join(OUT, f'na_contours_fig{fig_no}{tag}.png'), dpi=600, bbox_inches='tight')
        plt.close(fig)
print('Saved -> na_contours_fig2a..3d.png')
