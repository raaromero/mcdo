r"""Lim & Saloma's quoted peak losses (Section 3.2), recomputed against NA: the
vector (Richards–Wolf) focus as the line, the paper's paraxial scalar model as a
dashed line, the paper's quoted value marked at NA 0.5, and NA ≤ 0.5 (the
scalar model's stated range) shaded.

Each metric keeps the paper's offset in wavelength units, so it reads "how
much of the peak does the same misalignment cost at this NA":

    1. 2CE, θ = π/2, x_c = 1.33 λ1    paper: 11%
    2. 2CE, θ = π,   x_c = 0.37 λ1    paper: 20%
    3. 2PE, θ = π/2, x_c = 0.5 λ2p    paper: 30%
    4. 2CE, θ = π,   z_c = 2.7 λ1     paper: 20%
    5. 2CE, θ = π/2, z_c = 2.7 λ1     paper: 30%

Air throughout, NA 0.1–0.95 at both angles. Above NA 0.71 two lenses cannot
cross at θ = π/2 in air; that range is computed (the field overlap is well
defined) and hatched as not realizable. 2CE beams are unpolarized (mean of two orthogonal input
polarizations; the colors do not interfere). 2PE beams are both polarized
along y, perpendicular to both optical axes, so they interfere fully, the case
the scalar model describes. Peak = maximum of the signal over a window around
the foci, divided by the aligned maximum.

Figures are one metric each at 10 × 7.5 in, fonts 32/28/24 pt, 600 dpi.

    python scripts/fig_lim2002_quoted_vs_na.py
    ALPHA_T=4 python scripts/fig_lim2002_quoted_vs_na.py   # the same with input truncation α_t = 4
    -> output/08_two_color/lim2002/quoted_vs_na_{1..5}[_at4].png, quoted_vs_na[_at4].csv
"""

import glob
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
                            'ytick.labelsize': 24, 'legend.fontsize': 24})

from mcdo.apodization import gaussian
from mcdo.twobeam import beam_field, intensity

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002')
L1, L2, L2P = 0.750, 0.656, 0.700
AT = float(os.environ.get('ALPHA_T', '0'))       # input truncation; 0 = uniform, Lim & Saloma's case
SUF = '' if AT == 0 else f'_at{AT:g}'
APOD = lambda na: gaussian(AT, na ** 2) if AT else None
NA_LIST = (np.array([float(v) for v in os.environ['NA_LIST'].split(',')])   # a coarser NA grid, e.g. 0.3,0.5,0.7,0.9
           if os.environ.get('NA_LIST') else None)
METRICS = [  # (pair, θ, offset along, offset in λ, λ unit, paper %, title)
    ('2ce', np.pi / 2, 'x', 1.33, L1, 11, '2CE, θ = π/2, x$_c$ = 1.33 λ$_1$'),
    ('2ce', np.pi, 'x', 0.37, L1, 20, '2CE, θ = π, x$_c$ = 0.37 λ$_1$'),
    ('2pe', np.pi / 2, 'x', 0.5, L2P, 30, '2PE, θ = π/2, x$_c$ = 0.5 λ$_{2p}$'),
    ('2ce', np.pi, 'z', 2.7, L1, 20, '2CE, θ = π, z$_c$ = 2.7 λ$_1$'),
    ('2ce', np.pi / 2, 'z', 2.7, L1, 30, '2CE, θ = π/2, z$_c$ = 2.7 λ$_1$'),
]


def chunked(f, x, z, chunk=15000):
    x, z = np.broadcast_arrays(np.asarray(x, float), np.asarray(z, float))
    fx, fz = x.ravel(), z.ravel()
    out = np.concatenate([f(fx[i:i + chunk], fz[i:i + chunk]) for i in range(0, fx.size, chunk)], axis=-1)
    return out.reshape(out.shape[:-1] + x.shape)     # keeps a leading field-component axis


def intens(lam, na, model, X, Z, **geo):
    """2CE: one beam's intensity on the grid, unpolarized for the vector model."""
    if model == 'scalar':
        return chunked(lambda x, z: intensity(beam_field(x, z, lam, na, 1.0, apodization=APOD(na), **geo)), X, Z)
    return chunked(lambda x, z: 0.5 * sum(intensity(beam_field(x, z, lam, na, 1.0, model='rw', psi=p,
                                                                apodization=APOD(na), **geo))
                                          for p in (0.0, np.pi / 2)), X, Z)


def field(lam, na, model, X, Z, **geo):
    """2PE: one beam's field on the grid, polarized along y for the vector model."""
    kw = {} if model == 'scalar' else dict(model='rw', psi=np.pi / 2)
    return chunked(lambda x, z: beam_field(x, z, lam, na, 1.0, apodization=APOD(na), **kw, **geo), X, Z)


_BEAM1 = {}


def signal(pair, na, theta, xc, zc, X, Z, model, key):
    k = (pair, na, model, key)                        # beam 1 never moves: compute it once per grid
    if k not in _BEAM1:
        _BEAM1[k] = intens(L1, na, model, X, Z) if pair == '2ce' else field(L2P, na, model, X, Z)
    if pair == '2ce':
        return _BEAM1[k] * intens(L2, na, model, X, Z, theta=theta, xc=xc, zc=zc)
    E = _BEAM1[k] + field(L2P, na, model, X, Z, theta=theta, xc=xc, zc=zc)
    return (np.sum(np.abs(E) ** 2, axis=0) if E.ndim == 3 else np.abs(E) ** 2) ** 2


def loss(pair, na, theta, along, off_um, model):
    xc, zc = (off_um, 0.0) if along == 'x' else (0.0, off_um)
    hx = max(1.0 * 0.5 / na, abs(xc) + 0.5)
    hz = max(5.0 * (0.5 / na) ** 2, abs(zc) + 1.0)
    X, Z = np.meshgrid(np.linspace(-hx, hx, 121), np.linspace(-hz, hz, 241))
    key = (round(hx, 6), round(hz, 6))
    return 100 * (1 - signal(pair, na, theta, xc, zc, X, Z, model, key).max()
                  / signal(pair, na, theta, 0, 0, X, Z, model, key).max())


SEL = os.environ.get('METRIC_SEL')                    # compute one metric only, e.g. '3'
REPLOT = os.environ.get('REPLOT') == '1'              # redraw from the saved files
TAG = os.environ.get('RUN_TAG', '')                  # extra NA points go to their own file, e.g. '_lo'
csv_of = lambda k: os.path.join(OUT, f'quoted_vs_na{SUF}_m{k}{TAG}.csv')   # one file per metric (and tag)
all_csv = lambda k: sorted(glob.glob(os.path.join(OUT, f'quoted_vs_na{SUF}_m{k}.csv'))
                           + glob.glob(os.path.join(OUT, f'quoted_vs_na{SUF}_m{k}_*.csv')))
for k, (pair, th, along, off, lam, paper, title) in enumerate(METRICS, 1):
    if SEL and str(k) != SEL:
        continue
    if not REPLOT:
        nas = NA_LIST if NA_LIST is not None else np.round(np.arange(0.10, 0.9501, 0.025), 3)   # 35 NAs
        with open(csv_of(k), 'w') as fh:
            fh.write('# NA,peak_lost_percent_vector,peak_lost_percent_scalar\n')
        for na in nas:
            v, sc = loss(pair, na, th, along, off * lam, 'vector'), loss(pair, na, th, along, off * lam, 'scalar')
            with open(csv_of(k), 'a') as fh:         # saved at once, so a stopped run keeps its points
                fh.write(f'{na:.4g},{v:.6g},{sc:.6g}\n')
            print(f'{k}. NA {na:.3f}: vector {v:.2f}%, scalar {sc:.2f}% (Lim & Saloma {paper}% at NA 0.5)', flush=True)
    if TAG or not all_csv(k):
        continue                                      # tagged runs only save; the plot merges all files
    nas, L, S = np.concatenate([np.atleast_2d(np.loadtxt(f, delimiter=',')) for f in all_csv(k)]).T
    order = np.argsort(nas); nas, L, S = nas[order], L[order], S[order]

    fig, ax = plt.subplots(figsize=(10.0, 7.5))
    ax.axvspan(0, 0.5, color='#dddddd', zorder=0, label='NA ≤ 0.5, scalar model\'s stated range')
    if th == np.pi / 2:
        ax.axvspan(1 / np.sqrt(2), 1.0, color='none', hatch='//', ec='#999999', lw=0, zorder=0,
                   label='NA > 0.71: two lenses cannot cross in air')
    ax.plot(nas, L, '-o', color='#1f77b4', lw=4, ms=8, label='Vector (Richards–Wolf)')
    ax.plot(nas, S, ':s', color='#d62728', lw=3, ms=8, mfc='none', mew=2, label='Paraxial scalar')
    ax.hlines(paper, nas[0], 0.5, colors='k', linestyles='--', lw=3,
              label='Lim & Saloma (2002), NA 0.5' + (' (uniform input)' if AT else ''))
    ax.set_xlim(0.0, 1.0)
    ax.set_xlabel('NA')
    ax.set_ylabel('Peak lost (%)')
    ax.set_title(title + (f', α$_t$ = {AT:g}' if AT else ''))
    ax.set_ylim(0, 100)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=1, frameon=False)
    fig.savefig(os.path.join(OUT, f'quoted_vs_na_{k}{SUF}.png'), dpi=600, bbox_inches='tight')
    plt.close(fig)

print(f'Saved -> quoted_vs_na_k{SUF}.png and quoted_vs_na{SUF}_mk.csv')
