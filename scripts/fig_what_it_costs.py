r"""Everything the annulus changes, on one set of axes.

The depth of focus is the quantity this work reports, but it is not the only
one measured, and quoting it alone makes the ring look free. Six quantities are
recorded in the baseline sweep and they move by wildly different amounts across
the same obstruction range: the peak intensity falls by a factor of 2500 while
the transverse width changes by 1.4.

That contrast is the result rather than a limitation of the metric. A ring that
extended the focus by widening it would be no use; this one gives 44 times the
depth for a 27% change in spot size, and pays in brightness, transmitted power
and side-lobe energy.

The second panel is a robustness check. Full width at half maximum is the
measure that failed when a window was too narrow, so the axial extent holding
80% of the on-axis energy - which has no such failure mode - is plotted against
it. They track, so the extension is not an artifact of choosing one definition.

    python scripts/fig_what_it_costs.py
    -> output/03_annular/what_it_costs.png
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

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '03_annular')
BASE = os.path.join(OUT, 'annular_baseline.npz')
GRID = os.path.join(os.path.dirname(__file__), '..', 'output', '05_pulsed_pupils',
                    'pulsed_annular_grid.npz')
if not os.path.exists(BASE):
    raise SystemExit('run scripts/verify_annular_baseline.py first')

b = np.load(BASE, allow_pickle=True)
names = [str(v) for v in b['input']]
g = np.load(GRID, allow_pickle=True) if os.path.exists(GRID) else None
g_names = [str(v) for v in g['input']] if g is not None else []
g_taus = [str(v) for v in g['tau']] if g is not None else []


def pulsed(inp, eps, field, tau='1 fs'):
    """Same quantity at numerical aperture 0.8 with a 1 fs pulse."""
    if g is None:
        return np.nan
    for i in range(len(g['eps'])):
        if (g_names[i].startswith(inp) and float(g['eps'][i]) == eps
                and g_taus[i] == tau):
            return float(g[field][i])
    return np.nan
EPS = [0.0, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99]
NAS = [0.1, 0.8, 1.2]
NCOLOR = {0.1: '#1f77b4', 0.8: '#d62728', 1.2: '#2ca02c'}


def val(na, inp, eps, field):
    for i in range(len(b['eps'])):
        if (float(b['na'][i]) == na and names[i].startswith(inp)
                and float(b['eps'][i]) == eps):
            return float(b[field][i])
    return np.nan


fig, axes = plt.subplots(2, 2, figsize=(19.0, 13.0))

# ── the whole cost and benefit picture, one aperture ──────────────────────
ax = axes[0, 0]
SERIES = [('depth_um', 'Depth of focus', '#d62728', 'o-'),
          ('extent_um', 'Axial extent holding 80% of the energy', '#ff7f0e', 'v-'),
          ('width_nm', 'Transverse width', '#1f77b4', 's-'),
          ('transmission', 'Fraction of the beam past the stop', '#2ca02c', '^-'),
          ('peak', 'On-axis peak intensity', '#9467bd', 'd-')]
for f, lab, color, style in SERIES:
    y = np.array([val(0.8, 'uniform', e, f) for e in EPS])
    ax.plot(EPS, y / y[0], style, color=color, lw=2.2, ms=8,
            label=lab + ', continuous wave')
    if f in ('depth_um', 'width_nm'):
        yp = np.array([pulsed('uniform', e, f) for e in EPS])
        if np.isfinite(yp).all():
            ax.plot(EPS, yp / yp[0], ':', color=color, lw=2.4,
                    label=lab + ', 1 fs')
ax.axhline(1.0, color='#999999', lw=1.2)
ax.set_yscale('log')
ax.set_xlabel('Obstruction ratio')
ax.set_ylabel('Relative to the unobstructed pupil')
ax.set_title('Depth of focus, transmitted power and peak intensity against obstruction ratio — uniform, numerical aperture 0.8, continuous wave, 750 nm',
             fontsize=12)
ax.legend(fontsize=9, loc='lower left')
ax.grid(alpha=0.25, which='both')

# ── the extension does not depend on which axial measure is used ──────────
ax = axes[0, 1]
for na in NAS:
    for inp, mark in (('uniform', 'o'), ('Gaussian', 's')):
        x = [val(na, inp, e, 'depth_um') for e in EPS]
        y = [val(na, inp, e, 'extent_um') for e in EPS]
        ax.plot(x, y, mark + '-', color=NCOLOR[na], lw=1.8, ms=8,
                alpha=1.0 if inp == 'uniform' else 0.7,
                label=f'{"Uniform" if inp == "uniform" else "Gaussian, alpha = 4"}'
                      f', numerical aperture {na:g}')
lim = [0.4, 2e4]
ax.plot(lim, lim, 'k--', lw=2.0, label='Equal')
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlim(lim)
ax.set_ylim(lim)
ax.set_xlabel('Depth of focus, full width at half maximum (um)')
ax.set_ylabel('Axial extent holding 80% of the energy (um)')
ax.set_title('Axial extent holding 80% of the energy against the half-maximum depth of focus', fontsize=12)
ax.legend(fontsize=8)
ax.grid(alpha=0.25, which='both')

# ── the transverse width barely moves, which is the point ─────────────────
ax = axes[1, 0]
for na in NAS:
    for inp, style in (('uniform', 'o-'), ('Gaussian', 's--')):
        y = np.array([val(na, inp, e, 'width_nm') for e in EPS])
        ax.plot(EPS, y / y[0], style, color=NCOLOR[na], lw=2.0, ms=8,
                alpha=1.0 if inp == 'uniform' else 0.7,
                label=f'{"Uniform" if inp == "uniform" else "Gaussian, alpha = 4"}'
                      f', numerical aperture {na:g}')
ax.axhline(1.0, color='#999999', lw=1.2)
for inp, style in (('uniform', 'o:'), ('Gaussian', 's:')):
    yp = np.array([pulsed(inp, e, 'width_nm') for e in EPS])
    if np.isfinite(yp).all():
        ax.plot(EPS, yp / yp[0], style, color='#1d1d1f', lw=1.6, ms=6,
                alpha=0.65,
                label=f'{"Uniform" if inp == "uniform" else "Gaussian"}, '
                      f'1 fs, numerical aperture 0.8')
ax.set_ylim(0.4, 1.15)
ax.set_xlabel('Obstruction ratio')
ax.set_ylabel('Transverse width, relative to the unobstructed pupil')
ax.set_title('Transverse width against obstruction ratio, continuous wave and 1 fs',
             fontsize=12)
ax.legend(fontsize=8)
ax.grid(alpha=0.25)

# ── where the energy the ring displaces ends up ───────────────────────────
ax = axes[1, 1]
for na in NAS:
    y = [val(na, 'uniform', e, 'sidelobe') for e in EPS]
    ax.plot(EPS, y, 'o-', color=NCOLOR[na], lw=2.2, ms=8,
            label=f'Numerical aperture {na:g}')
ax.set_xlabel('Obstruction ratio')
ax.set_ylabel('First side lobe, as a fraction of the peak')
ax.set_title('First side lobe against obstruction ratio — uniform, continuous wave', fontsize=12)
ax.legend(fontsize=10)
ax.grid(alpha=0.25)

plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUT, 'panels'), 'what_it_costs')
out = os.path.join(OUT, 'what_it_costs.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f'Saved -> {out}')

print('\nRange across the obstruction sweep, uniform, numerical aperture 0.8')
for f, lab, _c, _s in SERIES:
    y = np.array([val(0.8, 'uniform', e, f) for e in EPS])
    print(f'  {lab:<40} {max(y) / min(y):9.1f}x')
