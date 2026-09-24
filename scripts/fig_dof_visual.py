r"""What the depth of focus is, shown on the focal field itself.

An axial profile makes the reader infer the elongation from a curve. The
two-dimensional field shows it directly: the same pupil with and without a
central obstruction, drawn on one axial scale, with the half-maximum contour
closed around each focus and the depth marked between its crossings.

    python scripts/fig_dof_visual.py
    -> output/03_annular/dof_visual.png
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

from mcdo.style import apply as _apply_style
_apply_style()

from mcdo import SimConfig
from mcdo.annular import compute_integrals_annular
from mcdo.components import full as vec_intensity
from mcdo.rw_integrals import compute_integrals

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '03_annular')
os.makedirs(OUT, exist_ok=True)

LAM, N_MED, X_NA, NT = 0.750, 1.3, 0.8, 801
cfg = SimConfig(lam_c=LAM, X_NA=X_NA, n=N_MED, tau=np.inf, N_freq=3, N_theta=NT)
CASES = [(0.0, 'No obstruction'), (0.9, 'Obstruction ratio 0.9')]

r_half = np.linspace(0.0, 2.2, 301)
r_full = np.concatenate([-r_half[::-1][:-1], r_half])
# far enough that the obstructed focus visibly decays: at +-9 um its
# on-axis intensity is still 0.14, so the focus appears to fill the frame
z = np.linspace(-16.0, 16.0, 901)


def field(eps):
    if eps == 0.0:
        A = compute_integrals(r_half, z, cfg.k_c, cfg.alpha, NT)
    else:
        A = compute_integrals_annular(r_half, z, cfg.k_c, cfg.alpha, eps, NT)
    I = vec_intensity(A[0], A[1], A[2])
    I = np.concatenate([I[:, ::-1][:, :-1], I], axis=1)
    return I / I.max()


def depth(I):
    ax = I[:, int(np.argmin(np.abs(r_full)))]
    peak = int(np.argmax(ax))
    left = np.where(ax[:peak] < 0.5)[0][-1]
    right = peak + np.where(ax[peak:] < 0.5)[0][0]
    a = np.interp(0.5, [ax[left], ax[left + 1]], [z[left], z[left + 1]])
    b = np.interp(0.5, [ax[right], ax[right - 1]], [z[right], z[right - 1]])
    return a, b


fig, axes = plt.subplots(1, 2, figsize=(15.0, 7.4), sharey=True)
for ax, (eps, name) in zip(axes, CASES):
    I = field(eps)
    a, b = depth(I)
    m = ax.pcolormesh(r_full, z, np.maximum(I, 1e-4), cmap='inferno',
                      norm=LogNorm(vmin=1e-4, vmax=1.0), shading='auto')
    ax.contour(r_full, z, I, levels=[0.5], colors=['#ff7f0e'], linewidths=2.6)
    # the depth of focus, marked between the half-maximum crossings on axis
    ax.annotate('', xy=(0.0, a), xytext=(0.0, b),
                arrowprops=dict(arrowstyle='<->', color='white', lw=2.4))
    ax.text(0.12, (a + b) / 2, f'{b - a:.2f} µm', color='white', fontsize=13,
            va='center', fontweight='semibold')
    for y in (a, b):
        ax.plot([-2.2, 2.2], [y, y], '--', color='white', lw=1.8, alpha=0.75)
    ax.set_yticks(np.arange(-16, 17, 4))
    ax.set_xlabel('Radial position r (µm)')
    ax.set_title(f'{name} — depth of focus {b - a:.2f} µm', fontsize=13)
    ax.set_xlim(-2.2, 2.2)
axes[0].set_ylabel('Axial position z (µm)')
fig.colorbar(m, ax=axes, label='Intensity, normalized to the peak',
             fraction=0.035, pad=0.02)
fig.suptitle('Depth of focus read from the half-maximum contour — uniform, '
             'numerical aperture 0.8, 750 nm, continuous wave', fontsize=12, y=0.99)

out = os.path.join(OUT, 'dof_visual.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f'Saved -> {out}')

for eps, name in CASES:
    a, b = depth(field(eps))
    print(f'  {name:<24} {b - a:7.3f} µm')
