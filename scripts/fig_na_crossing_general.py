r"""How high the NA can go when two lenses cross: NA ≤ n sin(θ/2).

Two cones of half-angle α whose axes meet at θ do not overlap only while
2α ≤ θ; with NA = n sin α that is NA ≤ n sin(θ/2). At θ = π (facing lenses)
this is just NA ≤ n, the physical ceiling in any medium. Curves for air
(n = 1), water (1.33) and immersion oil (1.515), with θ = π/2 marked and NA
1.2 drawn for reference.

    python scripts/fig_na_crossing_general.py
    -> output/08_two_color/na_crossing_general.png
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
                            'ytick.labelsize': 24, 'legend.fontsize': 22})

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color')
MEDIA = [(1.0, 'Air, n = 1', '#1f77b4'), (1.33, 'Water, n = 1.33', '#2ca02c'), (1.515, 'Oil, n = 1.515', '#d62728')]

theta = np.linspace(0, 180, 361)
fig, ax = plt.subplots(figsize=(9.0, 6.4))              # twice its width on the slide: 24-pt text shows at 12 pt
for n, lab, col in MEDIA:
    ax.plot(theta, n * np.sin(np.radians(theta / 2)), '-', color=col, lw=4, label=lab)
    v = n * np.sin(np.radians(45))
    ax.plot(90, v, 'o', color=col, ms=14)
    ax.annotate(f'{v:.2f}', (90, v), xytext=(-18, 8), textcoords='offset points', ha='right', fontsize=24, color=col)
ax.axhline(1.2, color='k', lw=2.5, ls='--', label='NA 1.2')
ax.axvline(90, color='#999999', lw=2, ls=':')
ax.text(92, 0.1, 'θ = π/2', fontsize=24, color='#555555')
ax.set_xlim(0, 180); ax.set_ylim(0, 1.6)
ax.set_xticks([0, 45, 90, 135, 180])
ax.set_xlabel('θ (degrees)')
ax.set_ylabel('Largest NA with no overlap')
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.17), ncol=2, frameon=False)
path = os.path.join(OUT, 'na_crossing_general.png')
fig.savefig(path, dpi=600, bbox_inches='tight')
print('Saved ->', path)
