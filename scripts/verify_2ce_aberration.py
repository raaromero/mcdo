r"""Lim & Saloma (2003): primary spherical aberration in 2CE and 2PE.

Each beam carries its own aberration φ1, φ2, with Φ = (φ/100) λ ρ⁴. Reproduced:
Fig. 3 (PSFs at φ1 = φ2 = 16), Fig. 4 (peak fluorescence), Fig. 5 (fidelity F)
and Fig. 6 (correlation quality Q) over φ1, φ2 ∈ [−60, 60], for θ = 0, π/2, π.
PSFs on a 101 × 101 x–z field centered at O [LS03 p. 3401].

    python scripts/verify_2ce_aberration.py
    -> output/08_two_color/aberration_*.png, aberration_numbers.txt
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
x = np.linspace(-1.0, 1.0, 101)
z = np.linspace(-5.0, 5.0, 101)
X, Z = np.meshgrid(x, z)
PHI = np.arange(-60, 61, 5)
THETAS = [(0.0, 'θ = 0'), (np.pi / 2, 'θ = π/2'), (np.pi, 'θ = π')]
LINES = []


def sig(U1, U2, pair):
    return np.abs(U1) ** 2 * np.abs(U2) ** 2 if pair == '2ce' else np.abs(U1 + U2) ** 4


def lin(t, a):
    t = t / t.max(); a = a / a.max(); t2 = np.mean(t ** 2)
    return 1 - np.mean((t - a) ** 2) / t2, np.mean(np.abs(a) * np.abs(t)) / t2


res = {}
for pair in ('2pe', '2ce'):
    la, lb = (0.750, 0.656) if pair == '2ce' else (0.700, 0.700)
    U1 = {p: beam_field(X, Z, la, NA, N, sa=p) for p in PHI}
    for th, tlab in THETAS:
        U2 = {p: beam_field(X, Z, lb, NA, N, theta=th, sa=p) for p in PHI}
        ref = sig(U1[0], U2[0], pair)
        P = np.zeros((PHI.size, PHI.size)); Fm = np.zeros_like(P); Qm = np.zeros_like(P)
        for i, p2 in enumerate(PHI):
            for j, p1 in enumerate(PHI):
                a = sig(U1[p1], U2[p2], pair)
                P[i, j] = a.max() / ref.max()
                Fm[i, j], Qm[i, j] = lin(ref, a)
        res[(pair, th)] = (P, Fm, Qm)

for k, (name, lv) in enumerate((('peak', [10, 30, 50, 70, 90]),
                                ('fidelity', [0.5, 0.7, 0.8, 0.9, 1.0]),
                                ('correlation', [0.5, 0.7, 0.9, 1.0, 1.05, 1.1, 1.15]))):
    fig, axes = plt.subplots(3, 2, figsize=(22.0, 32.0))
    for r, (th, tlab) in enumerate(THETAS):
        for c, pair in enumerate(('2pe', '2ce')):
            M = res[(pair, th)][k] * (100 if k == 0 else 1)
            ax = axes[r, c]
            cs = ax.contour(PHI, PHI, M, levels=lv, colors='k', linewidths=1.4)
            ax.clabel(cs, fmt='%g', fontsize=14)
            ax.set_aspect('equal')
            ax.set_xlabel('φ$_1$'); ax.set_ylabel('φ$_2$')
            ax.set_title(f"{'2PE' if pair == '2pe' else '2CE'}, {tlab}")
    plt.tight_layout()
    save_panels(fig, fig.axes, os.path.join(OUT, 'panels'), f'aberration_{name}')
    fig.savefig(os.path.join(OUT, f'aberration_{name}.png'), dpi=300, bbox_inches='tight')
    plt.close(fig)

# Fig. 3: PSFs at φ1 = φ2 = 16
fig, axes = plt.subplots(3, 2, figsize=(20.0, 30.0))
for r, (th, tlab) in enumerate(THETAS):
    for c, pair in enumerate(('2pe', '2ce')):
        la, lb = (0.750, 0.656) if pair == '2ce' else (0.700, 0.700)
        F = sig(beam_field(X, Z, la, NA, N, sa=16), beam_field(X, Z, lb, NA, N, theta=th, sa=16), pair)
        cs = axes[r, c].contour(x, z, 100 * F / F.max(), levels=[1, 10, 20, 40, 60, 80],
                                colors='k', linewidths=1.4)
        axes[r, c].clabel(cs, fmt='%d', fontsize=14)
        axes[r, c].set_xlabel('x (µm)'); axes[r, c].set_ylabel('z (µm)')
        axes[r, c].set_title(f"{'2PE' if pair == '2pe' else '2CE'}, {tlab}")
        iz, ix = np.unravel_index(np.argmax(F), F.shape)
        LINES.append(f"φ1=φ2=16 {pair} {tlab}: peak at x = {x[ix]:+.2f}, z = {z[iz]:+.2f} µm")
plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUT, 'panels'), 'aberration_psf16')
fig.savefig(os.path.join(OUT, 'aberration_psf16.png'), dpi=300, bbox_inches='tight')

c0 = PHI.size // 2
def box(M, lo, hi):
    s = (PHI >= lo) & (PHI <= hi)
    return M[np.ix_(s, s)].min()
for pair in ('2ce', '2pe'):
    for th, tlab in THETAS:
        P, Fm, Qm = res[(pair, th)]
        d = np.array([P[i, i] for i in range(PHI.size)])
        ad = np.array([P[i, PHI.size - 1 - i] for i in range(PHI.size)])
        LINES.append(f"{pair} {tlab}: peak on φ1=φ2 at ±60: {d[0]:.2f}/{d[-1]:.2f};"
                     f" on φ1=−φ2 at ±60: {ad[0]:.2f}/{ad[-1]:.2f};"
                     f" min F in |φ|≤40: {box(Fm, -40, 40):.3f};"
                     f" Q range {Qm.min():.2f}–{Qm.max():.2f}")
LINES.append("paper (LS03 p. 3401, 3403): peak compensated along φ1=φ2 at θ=0 and φ1=−φ2 at "
             "θ=π; 2CE θ=π/2 keeps F>0.9 within |φ1|,|φ2|≤40; 2CE Q varies <10% over a wider "
             "range than 2PE")
with open(os.path.join(OUT, 'aberration_numbers.txt'), 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(LINES) + '\n')
print('\n'.join(LINES))
