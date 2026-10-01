r"""Why NA 0.9 needs immersion to cross two beams at θ = π/2.

Each lens focuses a cone of half-angle α, with NA = n sin α. At θ = π/2 the two
cones' axes are perpendicular, so they fit side by side only if α ≤ 45°, that
is NA ≤ n/√2: 0.71 in air, 0.94 in water (n = 1.33).

    python scripts/fig_na_crossing_limit.py
    -> output/08_two_color/na_crossing_limit.png and ~/Downloads/Research/two_color/
"""

import os
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Ellipse, Wedge

from mcdo.style import apply as _apply_style
_apply_style()
matplotlib.rcParams.update({'font.size': 24, 'axes.titlesize': 32,
                            'axes.labelsize': 28, 'xtick.labelsize': 24,
                            'ytick.labelsize': 24, 'legend.fontsize': 24})

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color')
COPY = os.path.expanduser('~/Downloads/Research/two_color')
R = 1.0
CASES = [(1.0, 0.7, 'Air, n = 1, NA 0.7'), (1.0, 0.9, 'Air, n = 1, NA 0.9'),
         (1.33, 0.9, 'Water, n = 1.33, NA 0.9')]
if os.environ.get('AIR_ONLY') == '1':            # the air cases alone
    CASES = CASES[:2]

fig, axes = plt.subplots(1, len(CASES), figsize=(5.4 * len(CASES), 6.6))   # twice its width on the slide
for ax, (n, na, title) in zip(axes, CASES):
    a = np.degrees(np.arcsin(na / n))
    fits = a <= 45.0
    ax.add_patch(Wedge((0, 0), R, 90 - a, 90 + a, fc='#d62728', alpha=0.25, ec='#d62728', lw=3))
    ax.add_patch(Wedge((0, 0), R, -a, a, fc='#1f77b4', alpha=0.25, ec='#1f77b4', lw=3))
    if not fits:
        ax.add_patch(Wedge((0, 0), R, 90 - a, a, fc='none', ec='k', lw=3, hatch='xx'))
        ax.annotate('cones overlap', xy=(0.22, 0.22), xytext=(-0.5, -0.55), fontsize=24, ha='center',
                    arrowprops=dict(arrowstyle='->', lw=2.5, color='k'))
    h = R * np.sin(np.radians(a))
    ax.add_patch(Ellipse((0, R * np.cos(np.radians(a))), 2 * h, 0.12, fc='white', ec='k', lw=3, zorder=4))
    ax.add_patch(Ellipse((R * np.cos(np.radians(a)), 0), 0.12, 2 * h, fc='white', ec='k', lw=3, zorder=4))
    ax.text(-h - 0.05, R * np.cos(np.radians(a)), 'L1', fontsize=24, ha='right', va='center')
    ax.text(R * np.cos(np.radians(a)), -h - 0.07, 'L2', fontsize=24, ha='center', va='top')
    ax.add_patch(Arc((0, 0), 0.5, 0.5, theta1=90, theta2=90 + a, lw=3, color='k'))
    ax.text(-0.3 * np.sin(np.radians(a / 2)), 0.3 * np.cos(np.radians(a / 2)) + 0.03, 'α',
            fontsize=24, ha='center')
    ax.plot([0, 0], [0, R * 1.05], ':', color='#555555', lw=2)
    ax.plot([0, R * 1.05], [0, 0], ':', color='#555555', lw=2)
    ax.plot(0, 0, 'ko', ms=10)
    ax.text(0.03, -0.06, 'O', fontsize=24, ha='left', va='top')
    ax.text(0.5, -0.06, f'α = {a:.0f}°: ' + ('the cones fit' if fits else 'they overlap'),
            transform=ax.transAxes, ha='center', va='top', fontsize=24,
            color='#1B7F3A' if fits else '#B01E1E')
    ax.set_title(title)
    ax.set_xlim(-1.05, 1.15); ax.set_ylim(-1.05, 1.15)
    ax.set_aspect('equal'); ax.axis('off')
fig.suptitle('At θ = π/2 the cones fit only for α ≤ 45°,\nNA ≤ n/√2 ' + ('(0.71 in air)' if len(CASES) == 2 else
             '(0.71 in air, 0.94 in water)'), fontsize=28, y=1.08)
plt.tight_layout()
path = os.path.join(OUT, 'na_crossing_limit_air.png' if len(CASES) == 2 else 'na_crossing_limit.png')
fig.savefig(path, dpi=600, bbox_inches='tight')
os.makedirs(COPY, exist_ok=True)
shutil.copy(path, COPY)
print('Saved ->', path, 'and', COPY)
