"""Depth-of-focus extension against obstruction ratio: continuous wave and
pulsed, side by side.

The extension is the quantity the annulus is used for, and the question here is
whether it survives a pulsed source. Two panels, one per illumination, each
carrying the continuous-wave and 1 fs curves so the comparison is on the same
axes rather than across slides.

Reads the pulsed sweep. Recomputes nothing.
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
SRC = os.path.join(ROOT, 'output', '05_pulsed_pupils', 'pulsed_annular_grid.npz')
OUT = os.path.join(ROOT, 'output', '05_pulsed_pupils')
XNA = 0.8
STYLE = {'continuous wave': ('#1f77b4', 'o-'), '2 fs': ('#e8820c', 's--'),
         '1 fs': ('#d62728', '^:')}

if not os.path.exists(SRC):
    raise SystemExit(f'{SRC} not found - run verify_pulsed_annular_grid.py first')

d = np.load(SRC, allow_pickle=True)
na = d['na']
inputs = np.array([str(v) for v in d['input']])
taus = np.array([str(v) for v in d['tau']])
eps, gain, width = d['eps'], d['gain'], d['width_nm']

fig, axes = plt.subplots(1, 4, figsize=(41.0, 7.0))
GAUSS = next((v for v in set(inputs.tolist()) if v.startswith('Gaussian')), 'Gaussian')
LABELS = [('uniform', 'Uniform'), (GAUSS, 'Gaussian, alpha = 4')]

print(f"{'input':<22} {'source':<17} {'eps':>5} {'extension':>10}")
for ax, (key, title) in zip(axes, LABELS):
    for tau in ('continuous wave', '2 fs', '1 fs'):
        m = (na == XNA) & (inputs == key) & (taus == tau)
        if not m.any():
            continue
        order = np.argsort(eps[m])
        x, y = eps[m][order], gain[m][order]
        color, style = STYLE[tau]
        ax.plot(x, y, style, color=color, lw=2.2, ms=8, label=tau.capitalize())
        for xi, yi in zip(x, y):
            print(f'{title:<22} {tau:<17} {xi:>5.2f} {yi:>10.2f}')
    e = np.array(sorted(set(eps[(na == XNA) & (inputs == key)].tolist())))
    ax.plot(e, 1.0 / (1.0 - e ** 2), 'k:', lw=2.0, label='Paraxial expression')
    ax.set_yscale('log')
    ax.set_xlabel('Obstruction ratio')
    ax.set_ylabel('Depth-of-focus extension')
    ax.set_title(f'{title}, numerical aperture {XNA:g}, 750 nm', fontsize=13)
    ax.grid(alpha=0.25, which='both')
    ax.legend(fontsize=11)

# the other cut through the same grid: illumination compared at fixed source
IN_STYLE = {'uniform': ('#1f77b4', 'o-'), GAUSS: ('#d62728', 's--')}
for ax, tau, title in ((axes[2], 'continuous wave', 'Continuous wave'),
                       (axes[3], '1 fs', '1 fs pulse')):
    for key, lab in LABELS:
        m = (na == XNA) & (inputs == key) & (taus == tau)
        if not m.any():
            continue
        order = np.argsort(eps[m])
        color, style = IN_STYLE[key]
        ax.plot(eps[m][order], gain[m][order], style, color=color, lw=2.2,
                ms=8, label=lab)
    e = np.array(sorted(set(eps[(na == XNA) & (inputs == 'uniform')].tolist())))
    ax.plot(e, 1.0 / (1.0 - e ** 2), 'k:', lw=2.0, label='Paraxial expression')
    ax.set_yscale('log')
    ax.set_xlabel('Obstruction ratio')
    ax.set_ylabel('Depth-of-focus extension')
    ax.set_title(f'{title}, numerical aperture {XNA:g}, 750 nm', fontsize=13)
    ax.grid(alpha=0.25, which='both')
    ax.legend(fontsize=11)

print("\nInteraction: change from continuous wave to 1 fs")
for key, lab in LABELS:
    for e in sorted(set(eps[(na == XNA) & (inputs == key)].tolist())):
        def _g(t):
            m = (na == XNA) & (inputs == key) & (taus == t) & (eps == e)
            return float(gain[m][0]) if m.any() else float('nan')
        cw, fs = _g('continuous wave'), _g('1 fs')
        if np.isfinite(cw) and np.isfinite(fs):
            print(f'  {lab:<22} eps {e:<5} {cw:>7.2f} -> {fs:>7.2f}  '
                  f'({100 * (fs / cw - 1):+5.1f}%)')

plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUT, 'panels'), 'fig_extension_cw_pulsed')
out = os.path.join(OUT, 'fig_extension_cw_pulsed.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f'\nSaved -> {out}')
