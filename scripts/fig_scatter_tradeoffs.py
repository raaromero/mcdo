r"""What a depth-of-focus extension costs, as scatter plots.

The line plots elsewhere each vary one parameter. These put every configuration
that has been run on the same axes, so the trade-offs are visible as a cloud
rather than as a sequence of curves.

    Extension against transmitted power   - what the ring costs in light
    Extension against peak intensity      - what it costs in brightness
    Depth of focus against obstruction    - the raw quantity, all apertures
    Pulsed against continuous wave        - bandwidth as a departure from parity

Every point is one computed configuration. Color is numerical aperture, shape
is illumination, size grows with obstruction ratio.

    python scripts/fig_scatter_tradeoffs.py
    -> output/03_annular/scatter_tradeoffs.png
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

from mcdo.figio import save_panels

ROOT = os.path.join(os.path.dirname(__file__), '..')
OUT = os.path.join(ROOT, '03_annular')
OUT = os.path.join(ROOT, 'output', '03_annular')
BASE = os.path.join(ROOT, 'output', '03_annular', 'annular_baseline.npz')
GRID = os.path.join(ROOT, 'output', '05_pulsed_pupils', 'pulsed_annular_grid.npz')
APS = os.path.join(ROOT, 'output', '05_pulsed_pupils',
                   'pulsed_annular_apertures.npz')
for p in (BASE, GRID, APS):
    if not os.path.exists(p):
        raise SystemExit(f'missing {p}')

b = np.load(BASE, allow_pickle=True)
g = np.load(GRID, allow_pickle=True)
a = np.load(APS, allow_pickle=True)

COLOR = {0.1: '#1f77b4', 0.8: '#d62728', 1.2: '#2ca02c'}
MARK = {'uniform': 'o', 'Gaussian': 's'}


def size(eps):
    """Marker area grows with the obstruction, so thin rings stand out."""
    return 40.0 + 260.0 * float(eps) ** 2


b_names = [str(v) for v in b['input']]

fig, axes = plt.subplots(2, 2, figsize=(19.0, 13.0))

# ── what the extension costs in transmitted light ─────────────────────────
ax = axes[0, 0]
for i in range(len(b['eps'])):
    inp = 'uniform' if b_names[i] == 'uniform' else 'Gaussian'
    na = float(b['na'][i])
    ax.scatter(float(b['transmission'][i]), float(b['gain'][i]),
               s=size(b['eps'][i]), c=COLOR[na], marker=MARK[inp],
               alpha=0.8, edgecolors='white', linewidths=0.8)
for na in COLOR:
    ax.scatter([], [], c=COLOR[na], s=90, label=f'Numerical aperture {na:g}')
for inp in MARK:
    ax.scatter([], [], c='#888888', marker=MARK[inp], s=90,
               label='Uniform' if inp == 'uniform' else 'Gaussian, alpha = 4')
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Fraction of the incident beam past the stop')
ax.set_ylabel('Depth-of-focus extension')
ax.set_title('Extension against transmitted fraction of the incident beam — continuous wave, 750 nm',
             fontsize=12)
ax.legend(fontsize=9, loc='upper right')
ax.grid(alpha=0.25, which='both')

# ── and in peak intensity ─────────────────────────────────────────────────
ax = axes[0, 1]
for i in range(len(b['eps'])):
    inp = 'uniform' if b_names[i] == 'uniform' else 'Gaussian'
    na = float(b['na'][i])
    ax.scatter(float(b['peak'][i]), float(b['gain'][i]),
               s=size(b['eps'][i]), c=COLOR[na], marker=MARK[inp],
               alpha=0.8, edgecolors='white', linewidths=0.8)
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('On-axis peak intensity, relative to no obstruction')
ax.set_ylabel('Depth-of-focus extension')
ax.set_title('Extension against on-axis peak intensity — continuous wave, 750 nm',
             fontsize=12)
ax.grid(alpha=0.25, which='both')

# ── the raw depth, every aperture ─────────────────────────────────────────
ax = axes[1, 0]
for i in range(len(b['eps'])):
    inp = 'uniform' if b_names[i] == 'uniform' else 'Gaussian'
    na = float(b['na'][i])
    ax.scatter(float(b['eps'][i]), float(b['depth_um'][i]),
               s=size(b['eps'][i]), c=COLOR[na], marker=MARK[inp],
               alpha=0.8, edgecolors='white', linewidths=0.8)
ax.set_yscale('log')
ax.set_xlabel('Obstruction ratio')
ax.set_ylabel('Depth of focus (um)')
ax.set_title('Depth of focus against obstruction ratio, by numerical aperture — 750 nm',
             fontsize=12)
ax.grid(alpha=0.25, which='both')

# ── pulsed against continuous wave, as a departure from parity ────────────
ax = axes[1, 1]
for src, has_na in ((g, False), (a, True)):
    names = [str(v) for v in src['input']]
    taus = [str(v) for v in src['tau']]
    seen = {}
    for i in range(len(src['eps'])):
        key = (float(src['na'][i]) if has_na else 0.8,
               names[i], float(src['eps'][i]))
        seen.setdefault(key, {})[taus[i]] = float(src['depth_um'][i])
    for (na, nm, eps), v in seen.items():
        if 'continuous wave' not in v or '1 fs' not in v:
            continue
        inp = 'uniform' if nm == 'uniform' else 'Gaussian'
        ax.scatter(v['continuous wave'], v['1 fs'], s=size(eps),
                   c=COLOR[na], marker=MARK[inp], alpha=0.8,
                   edgecolors='white', linewidths=0.8)
lim = [0.5, 2e4]
ax.plot(lim, lim, 'k--', lw=1.6, label='Equal depth')
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlim(lim)
ax.set_ylim(lim)
ax.set_xlabel('Depth of focus at continuous wave (um)')
ax.set_ylabel('Depth of focus at 1 fs (um)')
ax.set_title('Depth of focus at 1 fs against depth of focus at continuous wave', fontsize=12)
ax.legend(fontsize=10)
ax.grid(alpha=0.25, which='both')

plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUT, 'panels'), 'scatter_tradeoffs')
out = os.path.join(OUT, 'scatter_tradeoffs.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f'Saved -> {out}')

print('\nWhat the thinnest ring costs, continuous wave')
print(f"{'NA':>5} {'input':<22} {'extension':>10} {'transmitted':>12} {'peak':>10}")
for i in range(len(b['eps'])):
    if float(b['eps'][i]) != 0.99:
        continue
    print(f"{float(b['na'][i]):>5.1f} {b_names[i]:<22} "
          f"{float(b['gain'][i]):>9.1f}x {float(b['transmission'][i]):>12.5f} "
          f"{float(b['peak'][i]):>10.5f}")
