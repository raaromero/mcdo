r"""Optical setup of two-beam excitation, after Cambaliza & Saloma (2000) Fig. 1
and Lim & Saloma (2002) Fig. 1.

Beam 1 (λ1) is focused by lens L1 along the z axis to the origin O. Beam 2
(λ2) is focused by an identical lens L2 whose axis makes an angle θ with the
z axis, toward O' = (xc, zc). One panel per geometry: θ = 0, π/2, π, and a
fourth showing a focus offset (xc, zc).

    python scripts/fig_2ce_setup.py
    -> output/08_two_color/setup.png
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Ellipse, FancyArrowPatch, Polygon

from mcdo.style import apply as _apply_style
_apply_style()
matplotlib.rcParams.update({'font.size': 24, 'axes.titlesize': 32,
                            'axes.labelsize': 28, 'legend.fontsize': 24})

from mcdo.figio import save_panels

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color')
os.makedirs(OUT, exist_ok=True)
C1, C2 = '#d62728', '#1f77b4'
HALF = np.arcsin(0.5)          # cone half-angle at NA 0.5, n = 1
F, A = 3.0, 1.0                # lens distance and half-aperture, drawing units


def beam(ax, theta, focus, color, lens_label, beam_label, draw_lens=True):
    """A converging beam arriving along direction (sinθ, cosθ) toward `focus`.

    Drawing coordinates: horizontal = x, vertical = z pointing down, as in the
    papers' figures.
    """
    d = np.array([np.sin(theta), np.cos(theta)])        # propagation (x, z)
    p = np.array([d[1], -d[0]])                          # transverse to it
    fx, fz = focus
    lens_c = np.array([fx, fz]) - F * d
    e1, e2 = lens_c + A * p, lens_c - A * p
    cone = Polygon([e1, (fx, fz), e2], closed=True, fc=color, alpha=0.18, lw=0)
    ax.add_patch(cone)
    for e in (e1, e2):
        ax.plot([e[0], fx], [e[1], fz], color=color, lw=2.4)
    # collimated input beam above the lens
    for s in (1, -1):
        a = lens_c + s * 0.8 * A * p
        ax.plot([a[0] - 1.3 * d[0], a[0]], [a[1] - 1.3 * d[1], a[1]], color=color, lw=2.4)
    ax.add_patch(FancyArrowPatch(lens_c - 1.3 * d, lens_c - 0.5 * d, arrowstyle='-|>',
                                 mutation_scale=28, color=color, lw=2.4))
    if draw_lens:
        ang = np.degrees(np.arctan2(p[1], p[0]))
        ax.add_patch(Ellipse(lens_c, 2.3 * A, 0.32, angle=ang, fc='white', ec='k', lw=2.2,
                             zorder=4))
        lab = lens_c - 1.55 * A * p
        ax.text(lab[0], lab[1], lens_label, ha='center', va='center', fontsize=28, zorder=5)
    if beam_label:
        tip = lens_c - 0.95 * d + 1.2 * A * p
        ax.text(tip[0], tip[1], beam_label, ha='left' if p[0] >= 0 else 'right',
                va='center', fontsize=26, color=color, zorder=5,
                bbox=dict(fc='white', ec='none', pad=1.0))


def frame(ax, title):
    ax.set_aspect('equal')
    ax.set_xlim(-6.6, 6.6)
    ax.set_ylim(6.0, -6.0)                 # z downward
    ax.axis('off')
    ax.set_title(title)
    ax.annotate('', xy=(5.6, 0), xytext=(-5.6, 0),
                arrowprops=dict(arrowstyle='->', color='#555555', lw=1.6))
    ax.annotate('', xy=(0, 5.6), xytext=(0, -5.6),
                arrowprops=dict(arrowstyle='->', color='#555555', lw=1.6))
    ax.text(5.75, 0.0, 'x', fontsize=28, va='center')
    ax.text(0.2, 5.75, 'z', fontsize=28, va='center')


fig, axes = plt.subplots(2, 2, figsize=(12.0, 11.0))
axes = axes.ravel()
L1TXT, L2TXT = 'λ$_1$ = 750 nm', 'λ$_2$ = 656 nm'

ax = axes[0]; frame(ax, 'θ = 0')
beam(ax, 0.0, (0, 0), C1, 'L1', L1TXT)
beam(ax, 0.0, (0, 0), C2, '', '', draw_lens=False)
ax.text(-1.3, -4.3, L2TXT, fontsize=26, color=C2, ha='right',
        bbox=dict(fc='white', ec='none'))

ax = axes[1]; frame(ax, 'θ = π/2')
beam(ax, 0.0, (0, 0), C1, 'L1', L1TXT)
beam(ax, -np.pi / 2, (0, 0), C2, 'L2', L2TXT)

ax = axes[2]; frame(ax, 'θ = π')
beam(ax, 0.0, (0, 0), C1, 'L1', L1TXT)
beam(ax, np.pi, (0, 0), C2, 'L2', L2TXT)

ax = axes[3]; frame(ax, 'Focus offset, θ = π/2')
beam(ax, 0.0, (0, 0), C1, 'L1', L1TXT)
off = (1.2, 1.0)
beam(ax, -np.pi / 2, off, C2, 'L2', L2TXT)
ax.plot(*off, 'o', color='k', ms=10, zorder=6)
ax.text(off[0] - 0.15, off[1] + 0.55, 'O′', fontsize=28, ha='right')
ax.plot([off[0], off[0]], [0, off[1]], '--', color='k', lw=1.4)
ax.plot([0, off[0]], [off[1], off[1]], '--', color='k', lw=1.4)
ax.text(off[0] / 2, -0.25, 'x$_c$', fontsize=26, ha='center')
ax.text(-0.2, off[1], 'z$_c$', fontsize=26, ha='right', va='center')

for a in axes:
    a.plot(0, 0, 'o', color='k', ms=10, zorder=6)
    a.text(-0.3, -0.35, 'O', fontsize=28, ha='right')

plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUT, 'panels'), 'setup')
out = os.path.join(OUT, 'setup.png')
fig.savefig(out, dpi=600, bbox_inches='tight')
print('Saved ->', out)
