r"""Lim & Saloma (2002) Figs. 5-6: Linfoot fidelity F, structural content C and
correlation quality Q of the 2CE and 2PE point spread functions against the
focus offset O' = (xc, zc), for θ = π and π/2.

Definitions as in [LS02 p. 126]: over a 100 × 100 x–z field centered at O,
F = 1 − <(t − a)²>/<t²>, C = <a²>/<t²>, Q = <|a||t|>/<t²>, with t the aligned
PSF and a the misaligned PSF, each normalized to its own peak.

    python scripts/verify_2ce_linfoot.py
    -> output/08_two_color/linfoot_vs_offset.png, linfoot_numbers.txt
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
                            'axes.labelsize': 28, 'xtick.labelsize': 22,
                            'ytick.labelsize': 22})

from mcdo.figio import save_panels
from mcdo.twobeam import beam_field

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color')
NA, N = 0.5, 1.0
DX, DZ = 0.02, 0.1
x = np.arange(-50, 50) * DX            # 100 points, ±1 µm
z = np.arange(-50, 50) * DZ            # 100 points, ±5 µm
IX = np.arange(-38, 39, 2)             # offsets: ±0.76 µm ≈ ±1 λ1
IZ = np.arange(-45, 46, 3)             # ±4.5 µm = ±6 λ1
PX, PZ = 38, 45
xe = np.arange(-50 - PX, 50 + PX) * DX
ze = np.arange(-50 - PZ, 50 + PZ) * DZ
X, Z = np.meshgrid(x, z)
XE, ZE = np.meshgrid(xe, ze)
LINES = []


def criteria(t, a):
    t = t / t.max(); a = a / a.max()
    t2 = np.mean(t ** 2)
    return (1 - np.mean((t - a) ** 2) / t2, np.mean(a ** 2) / t2,
            np.mean(np.abs(a) * np.abs(t)) / t2)


def maps(theta, pair):
    la, lb = (0.750, 0.656) if pair == '2ce' else (0.700, 0.700)
    U1 = beam_field(X, Z, la, NA, N)
    U2e = beam_field(XE, ZE, lb, NA, N, theta=theta)
    nz, nx = X.shape
    sig = (lambda u2: np.abs(U1) ** 2 * np.abs(u2) ** 2) if pair == '2ce' \
        else (lambda u2: np.abs(U1 + u2) ** 4)
    t = sig(U2e[PZ:PZ + nz, PX:PX + nx])
    out = np.zeros((3, IZ.size, IX.size))
    for i, dz in enumerate(IZ):
        for j, dx in enumerate(IX):
            a = sig(U2e[PZ - dz:PZ - dz + nz, PX - dx:PX - dx + nx])
            out[:, i, j] = criteria(t, a)
    return out, la


fig, axes = plt.subplots(4, 3, figsize=(30.0, 36.0))
row = 0
for pair in ('2ce', '2pe'):
    for theta, tlab in ((np.pi, 'θ = π'), (np.pi / 2, 'θ = π/2')):
        M, la = maps(theta, pair)
        xc, zc = IX * DX / la, IZ * DZ / la
        tag = '2CE' if pair == '2ce' else '2PE'
        for col, (name, lv) in enumerate((('F', [-2, -1, -0.5, 0, 0.5, 0.8, 0.9, 0.95]),
                                          ('C', [0.2, 0.4, 0.6, 0.8, 0.9, 0.95]),
                                          ('Q', [0.6, 0.8, 0.9, 0.95, 1.05, 1.1, 1.2]))):
            ax = axes[row, col]
            pm = ax.pcolormesh(xc, zc, M[col], cmap='viridis', shading='auto')
            cs = ax.contour(xc, zc, M[col], levels=lv, colors='w', linewidths=1.4)
            ax.clabel(cs, fmt='%g', fontsize=14)
            fig.colorbar(pm, ax=ax, fraction=0.046, pad=0.04)
            ax.set_xlabel('x$_c$ (λ$_1$)'); ax.set_ylabel('z$_c$ (λ$_1$)')
            ax.set_title(f'{tag}, {tlab}: {name}')
        j0, i0 = IX.size // 2, IZ.size // 2
        for name, k in (('F', 0), ('C', 1), ('Q', 2)):
            LINES.append(f"{tag} {tlab} {name}: xc=1 λ1 {np.interp(1.0, xc, M[k, i0]):+.3f}"
                         f"  zc=1.33 λ1 {np.interp(1.33, zc, M[k][:, j0]):+.3f}"
                         f"  zc=2.7 λ1 {np.interp(2.7, zc, M[k][:, j0]):+.3f}"
                         f"  range [{M[k].min():+.2f}, {M[k].max():+.2f}]")
        row += 1
plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUT, 'panels'), 'linfoot_vs_offset')
fig.savefig(os.path.join(OUT, 'linfoot_vs_offset.png'), dpi=300, bbox_inches='tight')
LINES.append("paper (LS02 p. 127-128): π/2 F and C stable in-plane; along z they fall to "
             "about −0.8 and 0 at |zc| = 1.33 λ1; π: C dips then returns toward 1, Q rises "
             "above 1; 2PE maps fluctuate strongly")
with open(os.path.join(OUT, 'linfoot_numbers.txt'), 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(LINES) + '\n')
print('\n'.join(LINES))
