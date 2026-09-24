r"""The annular result on logarithmic axes, obstruction ratio 0 dropped.

The obstruction ratio runs from 0, which a logarithmic axis cannot carry. The
variable the result is actually a power law in is the remaining pupil fraction
1 - eps: the closed form

    extension = (1 - cos alpha) / (cos theta_in - cos alpha)

has cos theta_in -> cos alpha as eps -> 1, and expanding there gives

    extension -> (1 - cos alpha) cos alpha / sin^2 alpha * 1 / (1 - eps),

a straight line of slope -1 on logarithmic axes. Both panels are drawn that
way, with the asymptote overlaid.

    python scripts/fig_master_grid_loglog.py
    -> output/03_annular/master_grid_logeps_na0p8.png
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
matplotlib.rcParams.update({
    'font.size': 17, 'axes.titlesize': 19, 'axes.labelsize': 18,
    'xtick.labelsize': 16, 'ytick.labelsize': 16,
    'legend.fontsize': 16, 'legend.title_fontsize': 17,
})

from mcdo.figio import save_panels

ROOT = os.path.join(os.path.dirname(__file__), '..')
OUT = os.path.join(ROOT, 'output', '03_annular')
DOWNLOADS = os.path.expanduser('~/Downloads')
DATA = os.path.join(ROOT, 'output/02_na_apodization/truncation_pulsed.npz')

d = np.load(DATA, allow_pickle=True)
taus = [str(v) for v in d['tau']]
ALPHAS = [a for a in sorted({float(v) for v in d['alpha_t']}) if a <= 4.0]
EPS = [e for e in sorted({float(v) for v in d['eps']}) if e > 0.0]
COLOR = dict(zip(ALPHAS, plt.cm.viridis(np.linspace(0.0, 0.85, len(ALPHAS)))))
APERTURE, LAM, N_MED = 0.8, 0.750, 1.3


def alpha_label(at):
    return 'α = 0 (Uniform)' if at == 0.0 else f'α = {at:g}'


def val(at, eps, tau, field='depth_um'):
    for i in range(len(d['eps'])):
        if (float(d['na'][i]) == APERTURE and float(d['alpha_t'][i]) == at
                and float(d['eps'][i]) == eps and taus[i] == tau):
            return float(d[field][i])


u = np.array(EPS)
alpha = np.arcsin(APERTURE / N_MED)
C = (1.0 - np.cos(alpha)) * np.cos(alpha) / np.sin(alpha) ** 2

fig, axes = plt.subplots(1, 2, figsize=(24.0, 8.0))

# ── absolute depth of focus ───────────────────────────────────────────────
ax = axes[0]
for at in ALPHAS:
    ax.plot(u, [val(at, e, 'continuous wave') for e in EPS], 'o-',
            color=COLOR[at], lw=2.4, ms=8, label=alpha_label(at))
    ax.plot(u, [val(at, e, '1 fs') for e in EPS], 's--',
            color=COLOR[at], lw=2.0, ms=7)
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Obstruction ratio')
ax.set_ylabel('Depth of focus (µm)')
ax.set_title('(a) Depth of focus', fontsize=13)
ax.grid(alpha=0.25, which='both')

# ── extension, with the asymptote ─────────────────────────────────────────
ax = axes[1]
for at in ALPHAS:
    ref = val(at, 0.0, 'continuous wave')
    ax.plot(u, [val(at, e, 'continuous wave') / ref for e in EPS], 'o-',
            color=COLOR[at], lw=2.4, ms=8, label=alpha_label(at))
    refp = val(at, 0.0, '1 fs')
    ax.plot(u, [val(at, e, '1 fs') / refp for e in EPS], 's--',
            color=COLOR[at], lw=2.0, ms=7)
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Obstruction ratio')
ax.set_ylabel('Depth-of-focus extension')
ax.set_title('(b) Depth-of-focus extension', fontsize=13)
ax.grid(alpha=0.25, which='both')

handles = [Line2D([], [], color='#666666', marker='o', lw=2.4,
                  label='Continuous wave'),
           Line2D([], [], color='#666666', marker='s', lw=2.0, ls='--',
                  label='1 fs pulse')]

fig.suptitle(f'Numerical aperture {APERTURE:g}, {LAM * 1000:.0f} nm', fontsize=20)
h0, l0 = axes[1].get_legend_handles_labels()
fig.legend(handles=h0 + handles, labels=l0 + [h.get_label() for h in handles],
           loc='center left', bbox_to_anchor=(0.845, 0.5), frameon=True,
           title='Truncation')
plt.tight_layout(rect=[0.0, 0.0, 0.835, 0.96])
save_panels(fig, fig.axes, os.path.join(OUT, 'panels'),
            'master_grid_logeps_na0p8')
out = os.path.join(OUT, 'master_grid_logeps_na0p8.png')
fig.savefig(out, dpi=200, bbox_inches='tight')
plt.close(fig)
print(f'Saved -> {out}')

for src in [out,
            os.path.join(OUT, 'panels', 'master_grid_logeps_na0p8_p1.png'),
            os.path.join(OUT, 'panels', 'master_grid_logeps_na0p8_p2.png')]:
    shutil.copy(src, os.path.join(DOWNLOADS, os.path.basename(src)))
    print(f'Copied  -> {os.path.join(DOWNLOADS, os.path.basename(src))}')

print(f"\nslope of log(extension) against log(ε), continuous wave")
for at in ALPHAS:
    ref = val(at, 0.0, 'continuous wave')
    y = np.log([val(at, e, 'continuous wave') / ref for e in EPS])
    s_all = np.polyfit(np.log(u), y, 1)[0]
    print(f'  α = {at:<4g} slope {s_all:+.3f}')
