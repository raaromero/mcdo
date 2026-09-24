r"""The two master-grid results, each on three pairs of axes.

Same data, same five truncations, same styling as the originals. The only
difference between the three versions of each is the axis scaling. The
logarithmic-x versions cannot carry the obstruction ratio 0 point.

    python scripts/fig_axes_variants.py
    -> output/03_annular/axes/{depth,extension}_{orig,linlin,loglog}_na0p8.png
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
OUT = os.path.join(ROOT, 'output', '03_annular', 'axes')
DEST = os.path.expanduser('~/Downloads/mcdo_plots')
os.makedirs(OUT, exist_ok=True)
os.makedirs(DEST, exist_ok=True)
DATA = os.path.join(ROOT, 'output/02_na_apodization/truncation_pulsed.npz')

d = np.load(DATA, allow_pickle=True)
taus = [str(v) for v in d['tau']]
ALPHAS = sorted({float(v) for v in d['alpha_t']})
EPS_ALL = sorted({float(v) for v in d['eps']})
COLOR = dict(zip(ALPHAS, plt.cm.viridis(np.linspace(0.0, 0.85, len(ALPHAS)))))
NA = 0.8


def alpha_label(at):
    return 'α = 0 (Uniform)' if at == 0.0 else f'α = {at:g}'


def val(at, eps, tau):
    for i in range(len(d['eps'])):
        if (float(d['na'][i]) == NA and float(d['alpha_t'][i]) == at
                and float(d['eps'][i]) == eps and taus[i] == tau):
            return float(d['depth_um'][i])
    return np.nan


for quant, ylabel in (('depth', 'Depth of focus (µm)'),
                      ('extension', 'Depth of focus, relative to no obstruction')):
    for kind, logx, logy in (('orig', False, True), ('linlin', False, False),
                             ('loglog', True, True),
                             ('loglog_open', True, True),
                             ('semilog_open', False, True)):
        eps = [e for e in EPS_ALL if e > 0.0] if logx else EPS_ALL
        xs = ([1.0 - e for e in eps]
              if kind in ('loglog_open', 'semilog_open') else eps)
        fig, ax = plt.subplots(figsize=(11.0, 8.0))
        for at in ALPHAS:
            ref_c = val(at, 0.0, 'continuous wave') if quant == 'extension' else 1.0
            ref_p = val(at, 0.0, '1 fs') if quant == 'extension' else 1.0
            cw = [val(at, e, 'continuous wave') / ref_c for e in eps]
            pu = [val(at, e, '1 fs') / ref_p for e in eps]
            if not np.isfinite(cw).any():
                continue
            ax.plot(xs, cw, '-', color=COLOR[at], lw=2.8, marker='o', ms=7)
            ax.plot(xs, pu, '--', color=COLOR[at], lw=2.4, marker='s', ms=6,
                    alpha=0.9)
        if logx:
            ax.set_xscale('log')
        if logy:
            ax.set_yscale('log')
        ax.set_xlabel('1 − obstruction ratio'
                      if kind in ('loglog_open', 'semilog_open')
                      else 'Obstruction ratio')
        ax.set_ylabel(ylabel)
        ax.set_title(f'Numerical aperture {NA:g}, 750 nm', fontsize=13)
        ax.grid(alpha=0.25, which='both')

        keys = [Line2D([], [], color=COLOR[a], lw=3.0, label=alpha_label(a))
                for a in ALPHAS]
        keys += [Line2D([], [], color='#555555', lw=2.8, ls='-', marker='o',
                        label='Continuous wave'),
                 Line2D([], [], color='#555555', lw=2.4, ls='--', marker='s',
                        label='1 fs pulse')]
        fig.legend(handles=keys, fontsize=10, loc='center left',
                   bbox_to_anchor=(0.80, 0.5), title='Truncation')
        plt.tight_layout(rect=[0.0, 0.0, 0.79, 1.0])

        name = f'{quant}_{kind}_na0p8.png'
        out = os.path.join(OUT, name)
        fig.savefig(out, dpi=200, bbox_inches='tight')
        plt.close(fig)
        shutil.copy(out, os.path.join(DEST, name))
        print(f'Saved -> {out}')
