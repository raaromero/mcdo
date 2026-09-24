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
OUT = os.path.join(ROOT, 'output', '03_annular', 'axes_fit')
DEST = os.path.expanduser('~/Downloads/mcdo_fits')
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


FITS = []

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
            if kind == 'loglog_open':
                m = [i for i, e in enumerate(eps) if e >= 0.9]
                X = np.log(np.asarray(xs, float)[m])
                Y = np.log(np.asarray(cw, float)[m])
                b, a = np.polyfit(X, Y, 1)
                res = Y - (b * X + a)
                r2 = 1.0 - np.sum(res ** 2) / np.sum((Y - Y.mean()) ** 2)
                se = np.sqrt(np.sum(res ** 2) / (len(X) - 2)
                             / np.sum((X - X.mean()) ** 2))
                xf = np.linspace(X.min(), X.max(), 100)
                ax.plot(np.exp(xf), np.exp(b * xf + a), ':',
                        color=COLOR[at], lw=2.0, alpha=0.9)
            else:
                b = r2 = se = np.nan
            FITS.append((quant, kind, at, b, se, r2))
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
        ttl = f'Numerical aperture {NA:g}, 750 nm'
        if kind == 'loglog_open':
            bb = [f[3] for f in FITS if f[1] == kind and f[0] == quant]
            ee = [f[4] for f in FITS if f[1] == kind and f[0] == quant]
            rr = [f[5] for f in FITS if f[1] == kind and f[0] == quant]
            unit = 'µm' if quant == 'depth' else ''
            ttl += (f'\nPower-law fit over ε ≥ 0.9:   '
                    f'y = A (1 − ε)$^{{b}}$'
                    f'    R² ≥ {min(rr):.4f}')
        ax.set_title(ttl, fontsize=13)
        ax.grid(alpha=0.25, which='both')

        pf = {f[2]: f for f in FITS if f[1] == kind and f[0] == quant}
        keys = [Line2D([], [], color=COLOR[a], lw=3.0,
                       label=(f'{alpha_label(a)}:  b = {pf[a][3]:.3f} '
                              f'± {pf[a][4]:.3f}'
                              if kind == 'loglog_open' and a in pf
                              else alpha_label(a)))
                for a in ALPHAS]
        keys += ([Line2D([], [], color='#555555', lw=2.0, ls=':',
                         label='Power-law fit, ε ≥ 0.9')]
                 if kind == 'loglog_open' else [])
        keys += [
                 Line2D([], [], color='#555555', lw=2.8, ls='-', marker='o',
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

print(f"\n{'quantity':<11}{'α':>4}{'exponent':>10}{'±':>8}{'R²':>10}")
for q, k, at, b, se, r2 in FITS:
    if k == 'loglog_open':
        print(f'{q:<11}{at:>4g}{b:>10.3f}{se:>8.3f}{r2:>10.5f}')
