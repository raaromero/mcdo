r"""The existing master-grid result panel, with a logarithmic x axis.

Identical to the right-hand panel of fig_master_grid: same data, same
truncations, same styling. The only change is that the x axis is logarithmic,
which means the obstruction ratio 0 point cannot be drawn.

    python scripts/fig_master_grid_loglog.py
    -> output/03_annular/master_grid_loglog_na0p8.png
"""

import os
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from mcdo.style import apply as _apply_style
_apply_style()

ROOT = os.path.join(os.path.dirname(__file__), '..')
OUT = os.path.join(ROOT, 'output', '03_annular')
DEST = os.path.expanduser('~/Downloads/mcdo_loglog')
DATA = os.path.join(ROOT, 'output/02_na_apodization/truncation_pulsed.npz')

d = np.load(DATA, allow_pickle=True)
taus = [str(v) for v in d['tau']]
ALPHAS = sorted({float(v) for v in d['alpha_t']})
EPS = [e for e in sorted({float(v) for v in d['eps']}) if e > 0.0]
COLOR = dict(zip(ALPHAS, plt.cm.viridis(np.linspace(0.0, 0.85, len(ALPHAS)))))
LAM, NA = 0.750, 0.8


def alpha_label(at):
    return 'α = 0 (Uniform)' if at == 0.0 else f'α = {at:g}'


def val(na, at, eps, tau, field='depth_um'):
    for i in range(len(d['eps'])):
        if (float(d['na'][i]) == na and float(d['alpha_t'][i]) == at
                and float(d['eps'][i]) == eps and taus[i] == tau):
            return float(d[field][i])
    return np.nan


fig, ax = plt.subplots(figsize=(11.0, 8.5))
for at in ALPHAS:
    cw = [val(NA, at, e, 'continuous wave') for e in EPS]
    pu = [val(NA, at, e, '1 fs') for e in EPS]
    if not np.isfinite(cw).any():
        continue
    ax.plot(EPS, cw, '-', color=COLOR[at], lw=2.8, marker='o', ms=7)
    ax.plot(EPS, pu, '--', color=COLOR[at], lw=2.4, marker='s', ms=6,
            alpha=0.9)
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Obstruction ratio')
ax.set_ylabel('Depth of focus (µm)')
ax.set_title(f'Numerical aperture {NA:g}, 750 nm', fontsize=13)
ax.grid(alpha=0.25, which='both')

colour_keys = [Line2D([], [], color=COLOR[a], lw=3.0, label=alpha_label(a))
               for a in ALPHAS]
style_keys = [Line2D([], [], color='#555555', lw=2.8, ls='-', marker='o',
                     label='Continuous wave'),
              Line2D([], [], color='#555555', lw=2.4, ls='--', marker='s',
                     label='1 fs pulse')]
fig.legend(handles=colour_keys + style_keys, fontsize=10,
           loc='center left', bbox_to_anchor=(0.80, 0.5), title='Truncation')
plt.tight_layout(rect=[0.0, 0.0, 0.79, 1.0])

out = os.path.join(OUT, 'master_grid_loglog_na0p8.png')
fig.savefig(out, dpi=200, bbox_inches='tight')
plt.close(fig)
os.makedirs(DEST, exist_ok=True)
shutil.copy(out, os.path.join(DEST, os.path.basename(out)))
print(f'Saved -> {out}')
