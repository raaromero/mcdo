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

Air; NA from 0.1; θ = π runs to NA 0.95, θ = π/2 to 0.70 (two cones cannot cross in air
above 0.71). 2CE beams are unpolarized (mean of two orthogonal input
polarizations; the colors do not interfere). 2PE beams are both polarized
along y, perpendicular to both optical axes, so they interfere fully, the case
the scalar model describes. Peak = maximum of the signal over a window around
the foci, divided by the aligned maximum.

Figures are one metric each at 10 × 7.5 in, fonts 32/28/24 pt, 600 dpi.

    python scripts/fig_lim2002_quoted_vs_na.py
    ALPHA_T=4 python scripts/fig_lim2002_quoted_vs_na.py   # the same with input truncation α_t = 4
    -> output/08_two_color/lim2002/quoted_vs_na_{1..5}[_at4].png, quoted_vs_na[_at4].csv
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
                            'ytick.labelsize': 24, 'legend.fontsize': 24})

from mcdo.apodization import gaussian
from mcdo.twobeam import beam_field, intensity

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002')
L1, L2, L2P = 0.750, 0.656, 0.700
AT = float(os.environ.get('ALPHA_T', '0'))       # input truncation; 0 = uniform, Lim & Saloma's case
SUF = '' if AT == 0 else f'_at{AT:g}'
APOD = lambda na: gaussian(AT, na ** 2) if AT else None
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
    return np.concatenate([f(fx[i:i + chunk], fz[i:i + chunk]) for i in range(0, fx.size, chunk)],
                          axis=-1).reshape(x.shape)


def signal(pair, na, theta, xc, zc, X, Z, model):
    if pair == '2ce':
        def I(lam, th, a, b):
            if model == 'scalar':
                return chunked(lambda x, z: intensity(beam_field(x, z, lam, na, 1.0, theta=th, xc=a, zc=b,
                                                                 apodization=APOD(na))), X, Z)
            return chunked(lambda x, z: 0.5 * sum(intensity(beam_field(x, z, lam, na, 1.0, theta=th, xc=a, zc=b,
                                                                        apodization=APOD(na),
                                                                        model='rw', psi=p))
                                                  for p in (0.0, np.pi / 2)), X, Z)
        return I(L1, 0.0, 0.0, 0.0) * I(L2, theta, xc, zc)

    kw = dict(apodization=APOD(na)) if model == 'scalar' else dict(model='rw', psi=np.pi / 2, apodization=APOD(na))

    def s(x, z):
        E = (beam_field(x, z, L2P, na, 1.0, **kw)
             + beam_field(x, z, L2P, na, 1.0, theta=theta, xc=xc, zc=zc, **kw))
        return intensity(E) ** 2
    return chunked(s, X, Z)


def loss(pair, na, theta, along, off_um, model):
    xc, zc = (off_um, 0.0) if along == 'x' else (0.0, off_um)
    hx = max(1.0 * 0.5 / na, abs(xc) + 0.5)
    hz = max(5.0 * (0.5 / na) ** 2, abs(zc) + 1.0)
    X, Z = np.meshgrid(np.linspace(-hx, hx, 201), np.linspace(-hz, hz, 401))
    return 100 * (1 - signal(pair, na, theta, xc, zc, X, Z, model).max()
                  / signal(pair, na, theta, 0, 0, X, Z, model).max())


rows = []
for k, (pair, th, along, off, lam, paper, title) in enumerate(METRICS, 1):
    nas = np.round(np.arange(0.10, (0.951 if th == np.pi else 0.701), 0.05), 2)
    L = np.array([loss(pair, na, th, along, off * lam, 'vector') for na in nas])
    S = np.array([loss(pair, na, th, along, off * lam, 'scalar') for na in nas])
    for na, v, sc in zip(nas, L, S):
        rows.append((k, na, v, sc))
    print(f'{k}. {title.replace("$", "")}: paper {paper}% at NA 0.5; vector/scalar '
          + ', '.join(f'{na:.2f}: {v:.1f}/{sc:.1f}%' for na, v, sc in zip(nas, L, S)), flush=True)

    fig, ax = plt.subplots(figsize=(10.0, 7.5))
    ax.axvspan(0, 0.5, color='#dddddd', zorder=0, label='NA ≤ 0.5, scalar model\'s stated range')
    ax.plot(nas, L, '-o', color='#1f77b4', lw=4, ms=8, label='vector (Richards–Wolf)')
    ax.plot(nas, S, '--', color='#d62728', lw=4, label='paraxial scalar (Lim & Saloma\'s model)')
    ax.plot([0.5], [paper], 'k*', ms=28,
            label='Lim & Saloma, quoted at NA 0.5' + (' (uniform input)' if AT else ''))
    ax.set_xlim(0.1, nas[-1] + 0.02)
    ax.set_xlabel('NA')
    ax.set_ylabel('Peak lost (%)')
    ax.set_title(title + (f', α$_t$ = {AT:g}' if AT else ''))
    ax.set_ylim(0, 100)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=1, frameon=False)
    fig.savefig(os.path.join(OUT, f'quoted_vs_na_{k}{SUF}.png'), dpi=600, bbox_inches='tight')
    plt.close(fig)

np.savetxt(os.path.join(OUT, f'quoted_vs_na{SUF}.csv'), np.array(rows), delimiter=',', fmt='%.4f',
           header='metric,NA,peak_lost_percent_vector,peak_lost_percent_scalar')
print(f'Saved -> quoted_vs_na_1..5{SUF}.png, quoted_vs_na{SUF}.csv')
