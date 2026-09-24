r"""The 2CE panels of Lim & Saloma (2002) Figs. 2–3 at high NA, with the vector
Richards–Wolf focus: aligned, and with O′ = (0.4, 1.0) µm, at θ = π and π/2.

    NA 0.7 in air           near the θ = π/2 limit in air, n/√2 = 0.71
    NA 0.9 in water, n = 1.33   the limit there is 0.94

Both beams are unpolarized: each intensity is the mean over two orthogonal
input polarizations. λ1 = 750 nm, λ2 = 656 nm in vacuum; same axes (±1 µm ×
±5 µm, square frames) and contour levels (1–80%) as the paper, so the panels
compare directly with its NA 0.5 figures.

    python scripts/fig_lim2002_highna_psf.py
    -> output/08_two_color/lim2002/highna_psf_na0p7.png, highna_psf_na0p9_water.png
       and one figure per paper panel, NA 0.5 (air) | 0.75 | 0.9 (water) side by side,
       for α_t = 0 and 4: highna_fig2a_at0.png, ..., highna_fig3c_at4.png
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

from mcdo.figio import save_panels
from mcdo.twobeam import beam_field, intensity

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002')
L1, L2 = 0.750, 0.656
LEVELS = [1, 10, 20, 40, 60, 80]
x = np.linspace(-1.0, 1.0, 201)
z = np.linspace(-5.0, 5.0, 401)
X, Z = np.meshgrid(x, z)


def unpolarized(lam, na, n, theta=0.0, xc=0.0, zc=0.0):
    return 0.5 * sum(intensity(beam_field(X, Z, lam, na, n, theta=theta, xc=xc, zc=zc,
                                          model='rw', psi=psi)) for psi in (0.0, np.pi / 2))


for na, n, tag, medium in ((0.7, 1.0, 'na0p7', 'air'), (0.9, 1.33, 'na0p9_water', 'water')):
    I1 = unpolarized(L1, na, n)
    fig, axes = plt.subplots(2, 2, figsize=(22.0, 22.0))
    for ax, (th, tl, (xc, zc), lab) in zip(axes.ravel(), (
            (np.pi, 'θ = π', (0.0, 0.0), '(a)'), (np.pi, 'θ = π', (0.4, 1.0), '(b)'),
            (np.pi / 2, 'θ = π/2', (0.0, 0.0), '(c)'), (np.pi / 2, 'θ = π/2', (0.4, 1.0), '(d)'))):
        F = I1 * unpolarized(L2, na, n, th, xc, zc)
        F = 100 * F / F.max()
        cs = ax.contour(x, z, F, levels=LEVELS, colors='k', linewidths=2.0)
        ax.clabel(cs, fmt='%d', fontsize=24)
        ax.set_xlabel('x (µm)'); ax.set_ylabel('z (µm)')
        ax.set_box_aspect(1.0)
        ax.set_xticks([-1.0, -0.5, 0.0, 0.5, 1.0]); ax.set_yticks(np.arange(-5, 6, 1))
        ax.tick_params(axis='x', pad=14)
        where = 'aligned' if xc == 0 and zc == 0 else 'O′ = (0.4, 1.0) µm'
        ax.set_title(f'{lab} 2CE, {tl}, {where}')
        iz, ix = np.unravel_index(np.argmax(F), F.shape)
        one = F >= 1
        print(f'NA {na} {medium}, {tl}, {where}: peak at ({x[ix]:+.2f}, {z[iz]:+.2f}) µm; '
              f'1% contour spans x {x[one.any(0)].min():+.2f} to {x[one.any(0)].max():+.2f}, '
              f'z {z[one.any(1)].min():+.2f} to {z[one.any(1)].max():+.2f} µm')
    plt.tight_layout()
    name = f'highna_psf_{tag}'
    save_panels(fig, fig.axes, os.path.join(OUT, 'panels'), name, dpi=600)
    fig.savefig(os.path.join(OUT, name + '.png'), dpi=600, bbox_inches='tight')
    plt.close(fig)
    print('Saved ->', name + '.png')


# ── one figure per paper panel: NA 0.5 (air), 0.75 and 0.9 (water) side by side,
#    for uniform input (α_t = 0) and a truncated Gaussian (α_t = 4) ──
from mcdo.apodization import gaussian

NAS = ((0.5, 1.0, 'NA 0.5, air'), (0.75, 1.33, 'NA 0.75, water'), (0.9, 1.33, 'NA 0.9, water'))


def unpolarized_apod(lam, na, n, alpha_t, theta=0.0, xc=0.0, zc=0.0):
    apod = gaussian(alpha_t, (na / n) ** 2) if alpha_t else None
    return 0.5 * sum(intensity(beam_field(X, Z, lam, na, n, theta=theta, xc=xc, zc=zc, model='rw',
                                          psi=psi, apodization=apod)) for psi in (0.0, np.pi / 2))


for alpha_t in (0, 4):
    I1s = {na: unpolarized_apod(L1, na, n, alpha_t) for na, n, _ in NAS}
    for tag, th, tl, (xc, zc) in (('fig2a', np.pi, 'θ = π', (0.0, 0.0)), ('fig2c', np.pi / 2, 'θ = π/2', (0.0, 0.0)),
                                  ('fig3a', np.pi, 'θ = π', (0.4, 1.0)), ('fig3c', np.pi / 2, 'θ = π/2', (0.4, 1.0))):
        fig, axes = plt.subplots(1, 3, figsize=(33.0, 12.0))
        for ax, (na, n, lab) in zip(axes, NAS):
            F = I1s[na] * unpolarized_apod(L2, na, n, alpha_t, th, xc, zc)
            F = 100 * F / F.max()
            cs = ax.contour(x, z, F, levels=LEVELS, colors='k', linewidths=2.0)
            ax.clabel(cs, fmt='%d', fontsize=24)
            ax.set_xlabel('x (µm)'); ax.set_ylabel('z (µm)')
            ax.set_box_aspect(1.0)
            ax.set_xticks([-1.0, -0.5, 0.0, 0.5, 1.0]); ax.set_yticks(np.arange(-5, 6, 1))
            ax.tick_params(axis='x', pad=14)
            ax.set_title(lab)
        where = 'aligned' if xc == 0 and zc == 0 else 'O′ = (0.4, 1.0) µm'
        inp = 'uniform input' if alpha_t == 0 else f'Gaussian input, α$_t$ = {alpha_t}'
        fig.suptitle(f'2CE, {tl}, {where}: Fig. {tag[3]}({tag[4]}), Richards–Wolf, unpolarized, {inp}',
                     fontsize=32, y=1.01)
        plt.tight_layout()
        fig.savefig(os.path.join(OUT, f'highna_{tag}_at{alpha_t}.png'), dpi=600, bbox_inches='tight')
        plt.close(fig)
        print('Saved ->', f'highna_{tag}_at{alpha_t}.png')
