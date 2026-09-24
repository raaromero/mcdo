r"""One figure per numerical aperture: the whole annular result.

Four variables on one set of axes. Obstruction ratio across, depth of focus up
in micrometres, truncation as color, and continuous wave against a 1 fs pulse
as solid against dashed. Absolute depth, not a ratio.

The left panel shows what is being measured, so the right panel can be read
without taking the definition on trust: two axial profiles with their half
maximum crossings marked, and the depth of focus is the distance between them.

    python scripts/fig_master_grid.py
    -> output/03_annular/master_grid_na0p1.png
       output/03_annular/master_grid_na0p8.png
       output/03_annular/master_grid_na1p2.png
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from mcdo.style import apply as _apply_style
_apply_style()

from mcdo import SimConfig
from mcdo.annular import compute_integrals_annular
from mcdo.apodization import gaussian
from mcdo.components import full as vec_intensity
from mcdo.figio import save_panels
from mcdo.rw_integrals import compute_integrals

ROOT = os.path.join(os.path.dirname(__file__), '..')
OUT = os.path.join(ROOT, 'output', '03_annular')
DATA = os.path.join(ROOT, 'output/02_na_apodization/truncation_pulsed.npz')
if not os.path.exists(DATA):
    raise SystemExit('run scripts/verify_truncation_pulsed.py first')

d = np.load(DATA, allow_pickle=True)
taus = [str(v) for v in d['tau']]
HAS_NA = 'na' in d.files
NAS = sorted({float(v) for v in d['na']}) if HAS_NA else [0.8]
# alpha 8 sits in a different regime and is not presented
ALPHAS = [a for a in sorted({float(v) for v in d['alpha_t']}) if a <= 4.0]
EPS = sorted({float(v) for v in d['eps']})
COLOR = dict(zip(ALPHAS, plt.cm.viridis(np.linspace(0.0, 0.85, len(ALPHAS)))))
LAM, N_MED, NT = 0.750, 1.3, 801


def alpha_label(at):
    return 'α = 0 (Uniform)' if at == 0.0 else f'α = {at:g}'


def val(na, at, eps, tau, field='depth_um'):
    for i in range(len(d['eps'])):
        if ((not HAS_NA or float(d['na'][i]) == na)
                and float(d['alpha_t'][i]) == at
                and float(d['eps'][i]) == eps and taus[i] == tau):
            return float(d[field][i])
    return np.nan


def axial(na, eps, at):
    """On-axis profile, for showing where the depth of focus is read."""
    cfg = SimConfig(lam_c=LAM, X_NA=na, n=N_MED, tau=np.inf,
                    N_freq=3, N_theta=NT)
    z = np.linspace(-30.0 * LAM / na ** 2, 30.0 * LAM / na ** 2, 3000)
    apod = None if at == 0.0 else gaussian(at, cfg.sin2_alpha)
    r0 = np.array([0.0])
    if eps == 0.0:
        A = compute_integrals(r0, z, cfg.k_c, cfg.alpha, NT, apodization=apod)
    else:
        A = compute_integrals_annular(r0, z, cfg.k_c, cfg.alpha, eps, NT,
                                      apodization=apod)
    I = vec_intensity(A[0][:, 0], A[1][:, 0], A[2][:, 0])
    return z, I / I.max()


def crossings(z, y):
    """The two half-maximum points either side of the peak."""
    peak = int(np.argmax(y))
    left = np.where(y[:peak] < 0.5)[0]
    right = np.where(y[peak:] < 0.5)[0]
    a = np.interp(0.5, [y[left[-1]], y[left[-1] + 1]],
                  [z[left[-1]], z[left[-1] + 1]]) if len(left) else z[0]
    j = peak + right[0]
    b = np.interp(0.5, [y[j], y[j - 1]], [z[j], z[j - 1]]) if len(right) else z[-1]
    return a, b


for na in NAS:
    fig, axes = plt.subplots(1, 2, figsize=(17.5, 7.2),
                             gridspec_kw={'width_ratios': [1.0, 1.25]})

    # ── what is being measured ────────────────────────────────────────────
    ax = axes[0]
    for eps, color, name in ((0.0, '#1d1d1f', 'No obstruction'),
                             (0.9, '#d62728', 'Obstruction ratio 0.9')):
        z, y = axial(na, eps, 0.0)
        a, b = crossings(z, y)
        ax.plot(z, y, '-', color=color, lw=2.6,
                label=f'{name} — depth {b - a:.2f} µm')
        ax.plot([a, b], [0.5, 0.5], '-', color=color, lw=2.0, alpha=0.5)
        for x in (a, b):
            ax.plot([x, x], [0.0, 0.5], ':', color=color, lw=1.8)
    ax.axhline(0.5, color='#999999', lw=1.4)
    ax.text(0.02, 0.53, 'Half maximum', transform=ax.get_yaxis_transform(),
            fontsize=10, color='#666666')
    ax.set_xlim(-18.0 * LAM / na ** 2, 18.0 * LAM / na ** 2)
    ax.set_ylim(0, 1.06)
    ax.set_xlabel('Axial position (µm)')
    ax.set_ylabel('On-axis intensity, normalized to the peak')
    ax.set_title('On-axis intensity against axial position, by obstruction ratio', fontsize=13)
    ax.legend(fontsize=10, loc='upper right')
    ax.grid(alpha=0.25)

    # ── the result ────────────────────────────────────────────────────────
    ax = axes[1]
    for at in ALPHAS:
        cw = [val(na, at, e, 'continuous wave') for e in EPS]
        pu = [val(na, at, e, '1 fs') for e in EPS]
        if not np.isfinite(cw).any():
            continue
        ax.plot(EPS, cw, '-', color=COLOR[at], lw=2.8, marker='o', ms=7)
        ax.plot(EPS, pu, '--', color=COLOR[at], lw=2.4, marker='s', ms=6,
                alpha=0.9)
    ax.set_yscale('log')
    ax.set_xlabel('Obstruction ratio')
    ax.set_ylabel('Depth of focus (µm)')
    ax.set_title(f'Numerical aperture {na:g}, 750 nm', fontsize=13)
    ax.grid(alpha=0.25, which='both')

    colour_keys = [Line2D([], [], color=COLOR[a], lw=3.0,
                          label=alpha_label(a)) for a in ALPHAS]
    style_keys = [Line2D([], [], color='#555555', lw=2.8, ls='-',
                         marker='o', label='Continuous wave'),
                  Line2D([], [], color='#555555', lw=2.4, ls='--',
                         marker='s', label='1 fs pulse')]
    first = ax.legend(handles=colour_keys, fontsize=10, loc='upper left',
                      title='Truncation')
    ax.add_artist(first)
    ax.legend(handles=style_keys, fontsize=10, loc='lower right')

    plt.tight_layout()
    tag = f"na{str(na).replace('.', 'p')}"
    save_panels(fig, fig.axes, os.path.join(OUT, 'panels'),
                f'master_grid_{tag}')
    out = os.path.join(OUT, f'master_grid_{tag}.png')
    fig.savefig(out, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f'Saved -> {out}')

print('\nDepth of focus (µm), continuous wave')
print(f"{'NA':>5} {'truncation':>16} " + '  '.join(f'{e:>8}' for e in EPS))
for na in NAS:
    for at in ALPHAS:
        row = [val(na, at, e, 'continuous wave') for e in EPS]
        if not np.isfinite(row).any():
            continue
        print(f'{na:>5.1f} {alpha_label(at):>16} ' +
              '  '.join(f'{x:8.2f}' for x in row))
