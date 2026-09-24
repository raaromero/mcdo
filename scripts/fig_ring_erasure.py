r"""Where the transverse rings survive a pulse, and where they do not.

The axial extension an annulus gives is independent of bandwidth. The
transverse structure is not, and the two effects run opposite ways: a thin ring
spaces its zeros more widely, so they survive spectral averaging that has
already smoothed the full disk at the same pulse duration.

Top row is the unobstructed disk, bottom row the ring at obstruction ratio 0.9,
each with continuous wave, 2 fs and 1 fs overlaid. At 2 fs the disk is smooth
while the ring still shows its first minimum; by 1 fs neither does, and the
profile is monotonic everywhere out to the edge of the window.

Profiles come from the saved sweep. Nothing is recomputed.

    python scripts/fig_ring_erasure.py
    -> output/05_pulsed_pupils/ring_erasure.png
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
if not os.path.exists(GRID):
    raise SystemExit('run scripts/verify_pulsed_annular_grid.py first')

d = np.load(GRID, allow_pickle=True)
TAUS = [('continuous wave', 'Continuous wave', '#1d1d1f', '-'),
        ('2 fs', '2 fs pulse', '#1f77b4', '--'),
        ('1 fs', '1 fs pulse', '#d62728', ':')]
INPUTS = [('uniform', 'Uniform'), ('Gaussian, alpha = 4', 'Gaussian, alpha = 4')]
ROWS = [0.0, 0.9]
AIRY = 0.61 * 0.750 / 0.8


def first_minimum(r, y):
    rising = np.where(np.diff(y) > 0)[0]
    return (r[rising[0]], y[rising[0]]) if len(rising) else (None, None)


fig, axes = plt.subplots(2, 2, figsize=(19.0, 13.0))
for row, eps in enumerate(ROWS):
    for col, (inp, lab) in enumerate(INPUTS):
        ax = axes[row, col]
        for tau, tlab, color, style in TAUS:
            k = f'0.8|{inp}|{eps}|{tau}|r'
            if k not in d.files:
                continue
            p = d[k]
            r, y = p[0], p[1] / p[1].max()
            rm, ym = first_minimum(r, y)
            mark = '' if rm is None else f', first minimum at {ym:.3f}'
            ax.semilogy(r, np.maximum(y, 1e-4), style, color=color, lw=2.2,
                        label=f'{tlab}{mark}' if rm else f'{tlab}, no minimum')
            if rm is not None:
                ax.plot([rm], [ym], 'o', color=color, ms=8)
        ax.axvline(AIRY, color='#cc4400', ls='--', lw=1.4, alpha=0.7)
        ax.set_ylim(1e-4, 1.6)
        ax.set_xlim(0, 2.8)
        ax.set_xlabel('Radial position (um)')
        ax.set_ylabel('Transverse intensity, normalized to the peak')
        ax.set_title(f'{lab}, obstruction ratio {eps:g}, '
                     f'numerical aperture 0.8, 750 nm', fontsize=12)
        ax.legend(fontsize=9, loc='upper right')
        ax.grid(alpha=0.25, which='both')

plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUT, 'panels'), 'ring_erasure')
out = os.path.join(OUT, 'ring_erasure.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f'Saved -> {out}')

print('\nDoes a first minimum survive?')
print(f"{'input':<22} {'ratio':>6} {'continuous':>12} {'2 fs':>10} {'1 fs':>10}")
for inp, lab in INPUTS:
    for eps in [0.0, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99]:
        cells = []
        for tau, _l, _c, _s in TAUS:
            p = d[f'0.8|{inp}|{eps}|{tau}|r']
            _rm, ym = first_minimum(p[0], p[1] / p[1].max())
            cells.append('none' if ym is None else f'{ym:.4f}')
        print(f'{lab:<22} {eps:>6.2f} {cells[0]:>12} {cells[1]:>10} '
              f'{cells[2]:>10}')
