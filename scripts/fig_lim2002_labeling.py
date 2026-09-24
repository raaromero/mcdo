r"""Lim & Saloma (2002) Figs. 5-6: the second column is labeled C but shows Q.

Linfoot's criteria as the paper defines them (p. 126), aligned PSF t and
misaligned PSF a, each normalized to its peak, averaged over the x–z window:

    F = 1 − <(t − a)²>/<t²>,   C = <a²>/<t²>,   Q = <|a||t|>/<t²>,
    so  F = 2Q − C  identically, and  F ≥ −C  since Q ≥ 0.

This plots F, C and Q against zc (xc = 0) for 2CE at θ = π/2 — the cut the paper
quotes on p. 128 ("F and C ... decrease to about −0.8 and zero at |zc| = 1.33 λ1")
— and checks the identity numerically.

    python scripts/fig_lim2002_labeling.py
    -> output/08_two_color/lim2002/labeling_FCQ.png
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
matplotlib.rcParams.update({'font.size': 24, 'axes.titlesize': 30,
                            'axes.labelsize': 28, 'xtick.labelsize': 24,
                            'ytick.labelsize': 24, 'legend.fontsize': 24})

from mcdo.twobeam import beam_field

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002')
NA, N, L1, L2 = 0.5, 1.0, 0.750, 0.656
dz = 0.02 * L1
x = np.arange(-50, 50) * 0.02
z = np.arange(-250, 250) * dz
IZ = np.arange(-300, 301, 3)
ze = np.arange(-250 - 300, 250 + 300) * dz
X, Z = np.meshgrid(x, z)
XE, ZE = np.meshgrid(x, ze)
I1 = np.abs(beam_field(X, Z, L1, NA, N)) ** 2
I2e = np.abs(beam_field(XE, ZE, L2, NA, N, theta=np.pi / 2)) ** 2
nz = X.shape[0]
t = I1 * I2e[300:300 + nz]
t = t / t.max(); t2 = np.mean(t ** 2)
F, C, Q = [], [], []
for iz in IZ:
    a = I1 * I2e[300 - iz:300 - iz + nz]; a = a / a.max()
    F.append(1 - np.mean((t - a) ** 2) / t2)
    C.append(np.mean(a ** 2) / t2)
    Q.append(np.mean(a * t) / t2)
F, C, Q = map(np.array, (F, C, Q))
zc = IZ * dz / L1
print(f"max |F − (2Q − C)| = {np.max(np.abs(F - (2 * Q - C))):.1e}")
for v in (1.33,):
    print(f"zc = {v} λ1: F = {np.interp(v, zc, F):+.2f}, C = {np.interp(v, zc, C):+.2f}, "
          f"Q = {np.interp(v, zc, Q):+.2f}")

fig, ax = plt.subplots(figsize=(16.0, 9.0))
ax.plot(zc, F, '-', color='#d62728', lw=3.4, label='F (fidelity)')
ax.plot(zc, C, '-', color='#1f77b4', lw=3.4, label='C (structural content)')
ax.plot(zc, Q, '-', color='#2ca02c', lw=3.4, label='Q (correlation quality)')
ax.plot([1.33, -1.33], [-0.8, -0.8], 'o', ms=16, mfc='none', mec='#d62728', mew=3,
        label='Paper: F ≈ −0.8 at |z$_c$| = 1.33 λ$_1$')
ax.plot([1.33, -1.33], [0.0, 0.0], 's', ms=16, mfc='none', mec='k', mew=3,
        label='Paper: "C" ≈ 0 at |z$_c$| = 1.33 λ$_1$')
ax.axhline(0, color='#999999', lw=1.2)
ax.set_xlabel('Focus offset along z, z$_c$ (λ$_1$)')
ax.set_ylabel('Linfoot criterion')
ax.set_xlim(-4, 4); ax.set_ylim(-1.1, 1.2)
ax.set_title('2CE, θ = π/2, x$_c$ = 0, NA 0.5')
fig.legend(loc='upper center', bbox_to_anchor=(0.5, 0.02), ncol=2)
plt.tight_layout()
fig.savefig(os.path.join(OUT, 'labeling_FCQ.png'), dpi=300, bbox_inches='tight')
print('Saved -> labeling_FCQ.png')
