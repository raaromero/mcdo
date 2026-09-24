r"""How much of the pupil an obstruction ratio actually blocks.

The obstruction ratio is a ratio of radii, so the blocked area is its square:
eps = 0.5 blocks a quarter of the pupil, not half.

    python scripts/fig_occluded_area.py
    -> output/03_annular/occluded_area.png
"""

import os
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo.style import apply as _apply_style
_apply_style()
matplotlib.rcParams.update({
    'font.size': 17, 'axes.titlesize': 19, 'axes.labelsize': 18,
    'xtick.labelsize': 16, 'ytick.labelsize': 16, 'legend.fontsize': 16,
})

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '03_annular')
EPS_PTS = [round(0.1 * i, 1) for i in range(11)]

e = np.linspace(0.0, 1.0, 400)
fig, ax = plt.subplots(figsize=(9.5, 9.0))
ax.plot(e, e ** 2, '-', color='#1f77b4', lw=3.0)
ax.plot(EPS_PTS, [x ** 2 for x in EPS_PTS], 'o', color='#1f77b4',
        ms=11, mec='white', mew=1.5)
ax.set_xlim(0.0, 1.0)
ax.set_ylim(0.0, 1.0)
ax.set_xlabel('Obstruction ratio ε')
ax.set_ylabel('Fraction of pupil area occluded, ε²')
ax.set_title('Fraction of pupil area occluded against obstruction ratio',
             fontsize=19)
ax.grid(alpha=0.25)

ax.set_aspect('equal', adjustable='box')

plt.tight_layout()
out = os.path.join(OUT, 'occluded_area.png')
fig.savefig(out, dpi=200, bbox_inches='tight')
plt.close(fig)
print(f'Saved -> {out}')
shutil.copy(out, os.path.expanduser('~/Downloads/occluded_area.png'))


print(f"\n{'ε':>6} {'ε²':>8}")
for x in EPS_PTS:
    print(f'{x:>6.2f} {x ** 2:>8.4f}')
