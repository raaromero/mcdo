r"""The same axis variants, with the occluded area fraction in place of the
obstruction ratio.

eps is a ratio of radii; eps^2 is the fraction of pupil area blocked. This is
the identical data and styling of fig_axes_variants_fit, with eps -> eps^2 and
1 - eps -> 1 - eps^2 on the x axis.

    python scripts/fig_axes_variants_sq.py
    -> output/03_annular/axes_sq/*.png
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
OUT = os.path.join(ROOT, 'output', '03_annular', 'axes_sq')
DEST = os.path.expanduser('~/Downloads/mcdo_sq')
os.makedirs(OUT, exist_ok=True)
os.makedirs(DEST, exist_ok=True)
DATA = os.path.join(ROOT, 'output/02_na_apodization/truncation_pulsed.npz')

d = np.load(DATA, allow_pickle=True)
taus = [str(v) for v in d['tau']]
ALPHAS = sorted({float(v) for v in d['alpha_t']})
EPS_ALL = sorted({float(v) for v in d['eps']})
COLOR = dict(zip(ALPHAS, plt.cm.viridis(np.linspace(0.0, 0.85, len(ALPHAS)))))
NA = 0.8

KINDS = [('orig', False, True, 'sq'), ('linlin', False, False, 'sq'),
         ('loglog', True, True, 'sq'), ('loglog_open', True, True, 'open'),
         ('semilog_open', False, True, 'open')]
XLAB = {'sq': 'Occluded area fraction, ε²',
        'open': 'Open area fraction, 1 − ε²'}


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
                      ('extension',
                       'Depth of focus, relative to no obstruction')):
    for kind, logx, logy, xv in KINDS:
        eps = [e for e in EPS_ALL if e > 0.0] if logx else EPS_ALL
        xs = np.array([e ** 2 if xv == 'sq' else 1.0 - e ** 2 for e in eps])
        fitted = (kind == 'loglog_open')
        fig, ax = plt.subplots(figsize=(11.0, 8.0))
        for at in ALPHAS:
            rc = val(at, 0.0, 'continuous wave') if quant == 'extension' else 1.0
            rp = val(at, 0.0, '1 fs') if quant == 'extension' else 1.0
            cw = [val(at, e, 'continuous wave') / rc for e in eps]
            pu = [val(at, e, '1 fs') / rp for e in eps]
            if not np.isfinite(cw).any():
                continue
            ax.plot(xs, cw, '-', color=COLOR[at], lw=2.8, marker='o', ms=7)
            ax.plot(xs, pu, '--', color=COLOR[at], lw=2.4, marker='s', ms=6,
                    alpha=0.9)
            if fitted:
                m = [i for i, e in enumerate(eps) if e >= 0.9]
                X, Y = np.log(xs[m]), np.log(np.asarray(cw, float)[m])
                b, a = np.polyfit(X, Y, 1)
                res = Y - (b * X + a)
                r2 = 1.0 - np.sum(res ** 2) / np.sum((Y - Y.mean()) ** 2)
                se = np.sqrt(np.sum(res ** 2) / (len(X) - 2)
                             / np.sum((X - X.mean()) ** 2))
                xf = np.linspace(X.min(), X.max(), 100)
                ax.plot(np.exp(xf), np.exp(b * xf + a), ':',
                        color=COLOR[at], lw=2.0, alpha=0.9)
                FITS.append((quant, at, b, se, r2))
        if logx:
            ax.set_xscale('log')
        if logy:
            ax.set_yscale('log')
        ax.set_xlabel(XLAB[xv])
        ax.set_ylabel(ylabel)
        ttl = f'Numerical aperture {NA:g}, 750 nm'
        if fitted:
            rr = [f[4] for f in FITS if f[0] == quant]
            ttl += ('\nPower-law fit over ε ≥ 0.9:   y = A (1 − ε²)$^{b}$'
                    f'    R² ≥ {min(rr):.4f}')
        ax.set_title(ttl, fontsize=13)
        ax.grid(alpha=0.25, which='both')

        pf = {f[1]: f for f in FITS if f[0] == quant} if fitted else {}
        keys = [Line2D([], [], color=COLOR[a], lw=3.0,
                       label=(f'{alpha_label(a)}:  b = {pf[a][2]:.3f} '
                              f'± {pf[a][3]:.3f}' if a in pf
                              else alpha_label(a))) for a in ALPHAS]
        if fitted:
            keys += [Line2D([], [], color='#555555', lw=2.0, ls=':',
                            label='Power-law fit, ε ≥ 0.9')]
        keys += [Line2D([], [], color='#555555', lw=2.8, ls='-', marker='o',
                        label='Continuous wave'),
                 Line2D([], [], color='#555555', lw=2.4, ls='--', marker='s',
                        label='1 fs pulse')]
        fig.legend(handles=keys, fontsize=10, loc='center left',
                   bbox_to_anchor=(0.80, 0.5), title='Truncation')
        plt.tight_layout(rect=[0.0, 0.0, 0.79, 1.0])

        name = f'{quant}_{kind}_na0p8.png'
        fig.savefig(os.path.join(OUT, name), dpi=200, bbox_inches='tight')
        plt.close(fig)
        shutil.copy(os.path.join(OUT, name), os.path.join(DEST, name))

print(f"\ny = A (1 − ε²)^b, fitted over ε ≥ 0.9")
print(f"{'quantity':<11}{'α':>4}{'b':>10}{'±':>8}{'R²':>10}")
for q, at, b, se, r2 in FITS:
    print(f'{q:<11}{at:>4g}{b:>10.3f}{se:>8.3f}{r2:>10.5f}')
