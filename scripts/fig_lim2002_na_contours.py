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
    ALPHA_T=4 python scripts/fig_lim2002_na_contours.py   # Gaussian input, suffix _at4; PSFs saved as .npz
    WATER=1 python scripts/fig_lim2002_na_contours.py     # adds θ = π/2 at NA 0.9 in water (F_na0.9_n1.33)
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

from mcdo.apodization import gaussian
from mcdo.twobeam import beam_field, intensity

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002')
L1, L2, L2P = 0.750, 0.656, 0.700
AT = float(os.environ.get('ALPHA_T', '0'))       # input truncation; 0 = uniform, Lim & Saloma's case
SUF = '' if AT == 0 else f'_at{AT:g}'
APOD = lambda na, n=1.0: gaussian(AT, (na / n) ** 2) if AT else None
LEVELS = [1, 10, 20, 40, 60, 80]
REPLOT = os.environ.get('REPLOT') == '1'             # redraw from the saved PSFs
x = np.linspace(-1.0, 1.0, 201)
z = np.linspace(-5.0, 5.0, 401)
X, Z = np.meshgrid(x, z)
NAS = {np.pi: (0.5, 0.7, 0.9), np.pi / 2: (0.5, 0.6, 0.7)}
PANELS = [('a', '2ce', np.pi, '2CE, θ = π'), ('b', '2pe', np.pi, '2PE, θ = π'),
          ('c', '2ce', np.pi / 2, '2CE, θ = π/2'), ('d', '2pe', np.pi / 2, '2PE, θ = π/2')]


def chunked(f, chunk=15000):
    fx, fz = X.ravel(), Z.ravel()
    return np.concatenate([f(fx[i:i + chunk], fz[i:i + chunk]) for i in range(0, fx.size, chunk)]).reshape(X.shape)


def psf(pair, na, theta, xc, zc, n=1.0):
    if pair == '2ce':
        I = lambda lam, th, a, b: chunked(lambda px, pz: 0.5 * sum(
            intensity(beam_field(px, pz, lam, na, n, theta=th, xc=a, zc=b, apodization=APOD(na, n), model='rw', psi=p))
            for p in (0.0, np.pi / 2)))
        return I(L1, 0.0, 0.0, 0.0) * I(L2, theta, xc, zc)
    return chunked(lambda px, pz: intensity(
        beam_field(px, pz, L2P, na, n, apodization=APOD(na, n), model='rw', psi=np.pi / 2)
        + beam_field(px, pz, L2P, na, n, theta=theta, xc=xc, zc=zc, apodization=APOD(na, n), model='rw', psi=np.pi / 2)) ** 2)


if os.environ.get('WATER') == '1':                  # crossed lenses at NA 0.9 do not fit in air: water, n = 1.33
    for fig_no, (xc, zc) in ((2, (0.0, 0.0)), (3, (0.4, 1.0))):
        for tag, pair, th, lab in PANELS[2:]:
            path = os.path.join(OUT, f'na_contours_fig{fig_no}{tag}{SUF}.npz')
            data = dict(np.load(path))
            data['F_na0.9_n1.33'] = psf(pair, 0.9, th, xc, zc, 1.33)
            np.savez_compressed(path, **data)
            print(f'Fig. {fig_no}({tag}) {lab}, NA 0.9 in water: saved', flush=True)
    sys.exit(0)

for fig_no, (xc, zc), where in ((2, (0.0, 0.0), 'aligned'), (3, (0.4, 1.0), 'O′ = (0.4, 1.0) µm')):
    for tag, pair, th, lab in PANELS:
        fig, axes = plt.subplots(1, 3, figsize=(18.2, 7.0))  # twice its width on the slide: 24-pt text shows at 12 pt
        data = {}
        saved = np.load(os.path.join(OUT, f'na_contours_fig{fig_no}{tag}{SUF}.npz')) if REPLOT else None
        for ax, na in zip(axes, NAS[th]):
            if REPLOT:
                F = saved[f'F_na{na:g}']
            else:
                F = psf(pair, na, th, xc, zc)
                data[f'F_na{na:g}'] = F
                np.savez_compressed(os.path.join(OUT, f'na_contours_fig{fig_no}{tag}{SUF}.npz'),
                                    x_um=x, z_um=z, **data)
            F = 100 * F / F.max()
            cs = ax.contour(x, z, F, levels=LEVELS, cmap='viridis', linewidths=3.0)   # levels: shared colorbar
            ax.set_xlabel('x (µm)'); ax.set_ylabel('z (µm)')
            ax.set_box_aspect(1.0)
            ax.set_xticks([-1.0, 0.0, 1.0]); ax.set_yticks([-4, -2, 0, 2, 4])
            ax.set_title(f'NA {na}')
            iz, ix = np.unravel_index(np.argmax(F), F.shape)
            print(f'Fig. {fig_no}({tag}) {lab}, {where}, NA {na}: peak at ({x[ix]:+.2f}, {z[iz]:+.2f}) µm', flush=True)
        plt.tight_layout()
        fig.colorbar(cs, ax=list(axes), fraction=0.02, pad=0.02, ticks=LEVELS).set_label('% of peak')
        fig.suptitle(f'{lab}, {where}' + (f', α$_t$ = {AT:g}' if AT else ''), fontsize=32, y=1.03)
        fig.savefig(os.path.join(OUT, f'na_contours_fig{fig_no}{tag}{SUF}.png'), dpi=600, bbox_inches='tight')
        plt.close(fig)
print('Saved -> na_contours_fig2a..3d.png')
