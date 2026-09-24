r"""Does the deck's bandwidth result hold away from numerical aperture 0.8?

The working deck fixes the aperture at 0.8 and reports two things: a uniform
annulus gives a 1 fs pulse the same depth-of-focus extension it gives
continuous light, and a truncated Gaussian loses some of it. Neither statement
is worth much if it belongs to that one aperture.

This draws both against obstruction ratio at 0.1, 0.8 and 1.2. Uniform stays
flat everywhere, so the invariance is a property of the ring rather than of a
setting. The Gaussian erosion grows with aperture at every ratio, so the deck's
number is the middle of a trend and can be quoted with a direction.

Sweeps: pulsed_annular_grid.npz at aperture 0.8, pulsed_annular_apertures.npz
at 0.1 and 1.2. Nothing is recomputed.

    python scripts/fig_erosion_vs_aperture.py
    -> output/05_pulsed_pupils/erosion_vs_aperture.png
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

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '05_pulsed_pupils')
GRID = os.path.join(OUT, 'pulsed_annular_grid.npz')
APS = os.path.join(OUT, 'pulsed_annular_apertures.npz')
for p in (GRID, APS):
    if not os.path.exists(p):
        raise SystemExit(f'missing {p}')

g = np.load(GRID, allow_pickle=True)
a = np.load(APS, allow_pickle=True)
EPS = [0.0, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99]
NAS = [0.1, 0.8, 1.2]
COLOR = {0.1: '#1f77b4', 0.8: '#d62728', 1.2: '#2ca02c'}
MARK = {0.1: 'o-', 0.8: 's--', 1.2: '^:'}


def gain(na, inp, eps, tau):
    src, has_na = (g, False) if na == 0.8 else (a, True)
    names = [str(v) for v in src['input']]
    taus = [str(v) for v in src['tau']]
    for i in range(len(src['eps'])):
        if (names[i].startswith(inp) and float(src['eps'][i]) == eps
                and taus[i] == tau
                and (not has_na or float(src['na'][i]) == na)):
            return float(src['gain'][i])
    return np.nan


def erosion(na, inp, eps, tau='1 fs'):
    cw = gain(na, inp, eps, 'continuous wave')
    p = gain(na, inp, eps, tau)
    return np.nan if not np.isfinite(cw) or cw == 0 else 100.0 * (1.0 - p / cw)


fig, axes = plt.subplots(2, 2, figsize=(19.0, 13.0))

for col, (inp, lab) in enumerate((('uniform', 'Uniform'),
                                  ('Gaussian', 'Gaussian, alpha = 4'))):
    ax = axes[0, col]
    for na in NAS:
        y = [erosion(na, inp, e) for e in EPS]
        ax.plot(EPS, y, MARK[na], color=COLOR[na], lw=2.0, ms=8,
                label=f'Numerical aperture {na:g}')
    ax.axhline(0.0, color='#999999', lw=1.2)
    ax.set_xlabel('Obstruction ratio')
    ax.set_ylabel('Extension lost at 1 fs (%)')
    ax.set_title(f'{lab}, 1 fs against continuous wave, 750 nm', fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(alpha=0.25)

# the two illuminations on one axis at the deck's aperture, for reference
ax = axes[1, 0]
for inp, lab, color, style in (('uniform', 'Uniform', '#1f77b4', 'o-'),
                               ('Gaussian', 'Gaussian, alpha = 4',
                                '#d62728', 's--')):
    for tau, alpha_v, suffix in (('2 fs', 0.55, ', 2 fs'), ('1 fs', 1.0, ', 1 fs')):
        y = [erosion(0.8, inp, e, tau) for e in EPS]
        ax.plot(EPS, y, style, color=color, lw=2.0, ms=7, alpha=alpha_v,
                label=lab + suffix)
ax.axhline(0.0, color='#999999', lw=1.2)
ax.set_xlabel('Obstruction ratio')
ax.set_ylabel('Extension lost (%)')
ax.set_title('Numerical aperture 0.8, both durations, 750 nm', fontsize=12)
ax.legend(fontsize=9)
ax.grid(alpha=0.25)

# how the loss at the thinnest ring scales with aperture
ax = axes[1, 1]
for inp, lab, color, style in (('uniform', 'Uniform', '#1f77b4', 'o-'),
                               ('Gaussian', 'Gaussian, alpha = 4',
                                '#d62728', 's--')):
    y = [erosion(na, inp, 0.99) for na in NAS]
    ax.plot(NAS, y, style, color=color, lw=2.2, ms=9, label=lab)
ax.axhline(0.0, color='#999999', lw=1.2)
ax.set_xlabel('Numerical aperture')
ax.set_ylabel('Extension lost at 1 fs, obstruction ratio 0.99 (%)')
ax.set_title('Extension lost at 1 fs against numerical aperture — obstruction ratio 0.99, 750 nm', fontsize=12)
ax.legend(fontsize=10)
ax.grid(alpha=0.25)

plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUT, 'panels'), 'erosion_vs_aperture')
out = os.path.join(OUT, 'erosion_vs_aperture.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f'Saved -> {out}')

print(f"\nExtension lost at 1 fs (%), against continuous wave")
print(f"{'input':<22} {'NA':>5} " + ' '.join(f'{e:>7}' for e in EPS))
for inp, lab in (('uniform', 'Uniform'), ('Gaussian', 'Gaussian, alpha = 4')):
    for na in NAS:
        row = ' '.join(f'{erosion(na, inp, e):>7.2f}' for e in EPS)
        print(f'{lab:<22} {na:>5} {row}')
