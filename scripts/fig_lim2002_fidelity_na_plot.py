r"""Figures from the fidelity-against-NA study (fig_lim2002_fidelity_na.py).

For each case (2CE/2PE, θ = π/π2, uniform/α_t = 4) and each criterion (F, C, Q),
one figure in three rows:

  (a) the 0.8 contour of the vector map at every NA, coloured by NA, over the
      paraxial scalar contour (red dotted), offsets in the units of the run
      (spot units for 2CE; λ/n along 2PE fringe directions);
  (b) Δ = vector − paraxial scalar at the same NA, at six NAs (colour scale set
      where the scalar value is ≥ 0, saturating outside);
  (c) shape numbers against NA, vector / paraxial scalar: half-width along x̃,
      half-width along z̃, and area above 0.8 (the region around the aligned
      point only). Water points (n = 1.33) are open
      markers; for θ = π/2 the band above NA 0.71 (lenses overlap in air) is hatched.

    python scripts/fig_lim2002_fidelity_na_plot.py
    -> output/08_two_color/lim2002/fidelity/fidelity_na_{pair}_{theta}[_at4]_{F,C,Q}.png
       and fidelity_shape_{pair}_{theta}[_at4]_{F,C,Q}.csv (the numbers in (c))
"""

import glob
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from scipy.interpolate import RectBivariateSpline
from scipy.ndimage import label

from mcdo.style import apply as _apply_style
_apply_style()
matplotlib.rcParams.update({'font.size': 24, 'axes.titlesize': 28,
                            'axes.labelsize': 28, 'xtick.labelsize': 22,
                            'ytick.labelsize': 22, 'legend.fontsize': 22})

DIR = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002', 'fidelity')
LEVEL = 0.8
NAMES = {'F': 'Fidelity F', 'C': 'Structural content C', 'Q': 'Correlation quality Q'}
PAIRS = {'2ce': '2CE', '2pe': '2PE'}
THETAS = {'pi': 'θ = π', 'pi2': 'θ = π/2'}


def load(pair, th, suf):
    runs = []
    for p in glob.glob(os.path.join(DIR, f'{pair}_{th}{suf}_na*_n*.npz')):
        m = re.search(rf'{pair}_{th}{suf}_na([\d.]+)_n([\d.]+)\.npz$', p)
        if m:
            runs.append((float(m.group(1)), float(m.group(2)), dict(np.load(p))))
    return sorted(runs, key=lambda r: (r[0], r[1]))


def half_width(t, v):
    """Distance from the centre to where v first drops below LEVEL, averaged over both sides."""
    c = len(t) // 2
    out = []
    for s in (1, -1):
        idx = np.arange(c, len(t)) if s == 1 else np.arange(c, -1, -1)
        below = np.nonzero(v[idx] < LEVEL)[0]
        if not below.size:
            return np.nan
        k = below[0]
        a, b = v[idx[k - 1]], v[idx[k]]
        out.append(abs(t[idx[k - 1]] + (t[idx[k]] - t[idx[k - 1]]) * (a - LEVEL) / (a - b)))
    return np.mean(out)


def shape(xt, zt, M):
    fine = RectBivariateSpline(zt, xt, M, kx=3, ky=3)
    xf, zf = np.linspace(xt[0], xt[-1], 20 * len(xt)), np.linspace(zt[0], zt[-1], 20 * len(zt))
    lab, _ = label(fine(zf, xf) >= LEVEL)         # only the region around the aligned point, not
    centre = lab[len(zf) // 2, len(xf) // 2]      # periodic repeats (2PE fringes) at the frame edge
    area = (np.count_nonzero(lab == centre) if centre else 0) * (xf[1] - xf[0]) * (zf[1] - zf[0])
    c = len(xt) // 2
    return half_width(xt, M[c, :]), half_width(zt, M[:, c]), area


UNITS = {('2ce', 'pi'): ('x$_c$ NA/λ', 'z$_c$ NA²/nλ'), ('2ce', 'pi2'): ('x$_c$ NA²/nλ', 'z$_c$ NA/λ'),
         ('2pe', 'pi'): ('x$_c$ NA/λ', 'z$_c$ n/λ'), ('2pe', 'pi2'): ('x$_c$ n/λ', 'z$_c$ n/λ')}


def figure(pair, th, suf, key, runs):
    xt, zt = runs[0][2]['xt'], runs[0][2]['zt']
    ulx, ulz = UNITS[(pair, th)]
    cmap = plt.get_cmap('viridis')
    nas = np.array([r[0] for r in runs]); lo, hi = nas.min(), nas.max()
    col = lambda na: cmap((na - lo) / max(hi - lo, 1e-9))
    fig = plt.figure(figsize=(30.0, 26.0))
    gs = GridSpec(3, 6, figure=fig, height_ratios=(1.25, 0.8, 0.9), hspace=0.5, wspace=0.5)

    ax = fig.add_subplot(gs[0, 1:4])
    for na, n, d in runs:
        ax.contour(xt, zt, d[f'{key}_vec'], levels=[LEVEL], colors=[col(na)], linewidths=2.5,
                   linestyles='-' if n == 1 else '--')
    ref = min(runs, key=lambda r: abs(r[0] - 0.5))
    ax.contour(xt, zt, ref[2][f'{key}_sca'], levels=[LEVEL], colors='#d62728', linewidths=4, linestyles=':')
    ax.set_xlabel(ulx); ax.set_ylabel(ulz)
    ax.set_title(f'(a) {key} = {LEVEL} contour, vector at every NA; red dotted: paraxial scalar, NA {ref[0]:g}', pad=24)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(lo, hi))
    fig.colorbar(sm, ax=ax, fraction=0.04, pad=0.03).set_label('NA (dashed: water)')

    idx = np.unique(np.round(np.linspace(0, len(runs) - 1, min(6, len(runs)))).astype(int))
    pick = [runs[i] for i in idx]
    # colour scale from where the aligned-ness is meaningful (scalar value ≥ 0); saturates outside
    vmax = max(np.abs(d[f'{key}_vec'] - d[f'{key}_sca'])[d[f'{key}_sca'] >= 0].max() for _, _, d in pick) or 1e-3
    for i, (na, n, d) in enumerate(pick):
        ax = fig.add_subplot(gs[1, i])
        pm = ax.pcolormesh(xt, zt, d[f'{key}_vec'] - d[f'{key}_sca'], cmap='RdBu_r', vmin=-vmax, vmax=vmax,
                           shading='nearest')
        ax.set_title(f'NA {na:g}' + ('' if n == 1 else ', water'))
        ax.set_xlabel(ulx)
        if i == 0:
            ax.set_ylabel(ulz)
    fig.colorbar(pm, ax=[fig.axes[-len(pick) + j] for j in range(len(pick))], fraction=0.012, pad=0.01).set_label(f'Δ{key}')
    fig.text(0.1, 0.585, f'(b) Δ{key} = {key} vector − {key} paraxial scalar, same NA', fontsize=28)

    S = np.array([[*shape(xt, zt, d[f'{key}_vec']), *shape(xt, zt, d[f'{key}_sca'])] for _, _, d in runs])
    water = np.array([n != 1 for _, n, _ in runs])
    np.savetxt(os.path.join(DIR, f'fidelity_shape_{pair}_{th}{suf}_{key}.csv'),
               np.column_stack([nas, [n for _, n, _ in runs], S]), delimiter=',', fmt='%.6g',
               header='NA,n,hx_vec,hz_vec,area_vec,hx_sca,hz_sca,area_sca')
    for j, lab in enumerate(('Half-width along x$_c$', 'Half-width along z$_c$', f'Area with {key} ≥ {LEVEL}')):
        ax = fig.add_subplot(gs[2, 2 * j:2 * j + 2])
        r = S[:, j] / S[:, j + 3]
        ax.plot(nas[~water], r[~water], 'o-', color='#1f77b4', lw=4, ms=11)
        if water.any():
            ax.plot(nas[water], r[water], 'o--', color='#1f77b4', lw=3, ms=11, mfc='none', mew=2.5)
        ax.axhline(1.0, color='#d62728', lw=2.5, ls=':')
        if th == 'pi2':
            ax.axvspan(1 / np.sqrt(2), 1.0, facecolor='none', edgecolor='#999999', hatch='//', lw=0)
        ax.set_xlabel('NA'); ax.set_ylabel(f'{lab}\nvector / scalar')
        ax.set_xlim(0, max(1.0, hi) + 0.03)
        ax.ticklabel_format(axis='y', useOffset=False)
    fig.text(0.1, 0.30, '(c) shape against NA; open markers: water, n = 1.33', fontsize=28)
    fig.suptitle(f'{NAMES[key]} over the offset of O′ against NA: {PAIRS[pair]}, {THETAS[th]}'
                 + (', α$_t$ = 4' if suf else ', uniform input'), fontsize=34, y=0.95)
    path = os.path.join(DIR, f'fidelity_na_{pair}_{th}{suf}_{key}.png')
    fig.savefig(path, dpi=600, bbox_inches='tight')
    plt.close(fig)
    print('Saved ->', os.path.basename(path), f'({len(runs)} NAs)')


for pair in PAIRS:
    for th in THETAS:
        for suf in ('', '_at4'):
            runs = load(pair, th, suf)
            if len(runs) < 2:
                continue
            for key in 'FCQ':
                figure(pair, th, suf, key, runs)
