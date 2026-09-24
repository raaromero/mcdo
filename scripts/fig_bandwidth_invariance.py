r"""What bandwidth invariance looks like, as profiles rather than as a ratio.

The extension curves elsewhere say that a uniform annulus gives a 1 fs pulse the
same depth of focus it gives continuous light, and that a truncated Gaussian
does not. Both are ratios, and a ratio hides what the focus is doing. This draws
the axial profiles themselves.

Left column is uniform illumination: the three pulse durations lie on one curve
at every obstruction ratio, so the ring's extension is a geometric effect that
does not care about bandwidth. Right column is a Gaussian with alpha = 4, where
the curves separate and the pulsed focus is visibly shorter, because the
apodization weights the pupil and the weighting is wavelength dependent.

Profiles come from the saved sweep. Nothing is recomputed.

    python scripts/fig_bandwidth_invariance.py
    -> output/05_pulsed_pupils/bandwidth_invariance.png
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
INPUTS = [('uniform', 'Uniform'), ('Gaussian, alpha = 4', 'Gaussian, alpha = 4')]
TAUS = [('continuous wave', 'Continuous wave', '#1d1d1f', '-'),
        ('2 fs', '2 fs pulse', '#1f77b4', '--'),
        ('1 fs', '1 fs pulse', '#d62728', ':')]
SHOW_EPS = [0.5, 0.9, 0.99]


def axial(inp, eps, tau):
    k = f'0.8|{inp}|{eps}|{tau}|z'
    return d[k] if k in d.files else None


def _depth(z, y):
    """Full width at half maximum of a profile sampled from the focus outward."""
    y = y / y.max()
    below = np.where(y < 0.5)[0]
    if not len(below):
        return np.nan
    i = below[0]
    return 2.0 * np.interp(0.5, [y[i], y[i - 1]], [z[i], z[i - 1]])


fig, axes = plt.subplots(2, 2, figsize=(19.0, 13.0))

# ── one ratio, all three durations, both illuminations ────────────────────
for col, (inp, lab) in enumerate(INPUTS):
    ax = axes[0, col]
    for tau, tlab, color, style in TAUS:
        p = axial(inp, 0.9, tau)
        if p is None:
            continue
        z, y = p[0], p[1] / p[1].max()
        ax.plot(z, y, style, color=color, lw=2.2, label=tlab)
    ax.axhline(0.5, color='#999999', lw=1.2)
    ax.set_xlim(0, 12)
    ax.set_xlabel('Axial position (um)')
    ax.set_ylabel('On-axis intensity, normalized to the peak')
    ax.set_title(f'{lab}, obstruction ratio 0.9, numerical aperture 0.8, 750 nm',
                 fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(alpha=0.25)

# ── several ratios, continuous wave against the shortest pulse ────────────
COLOR = dict(zip(SHOW_EPS, ['#1f77b4', '#d62728', '#2ca02c']))
for col, (inp, lab) in enumerate(INPUTS):
    ax = axes[1, col]
    for eps in SHOW_EPS:
        for tau, style, alpha in (('continuous wave', '-', 1.0),
                                  ('1 fs', ':', 0.9)):
            p = axial(inp, eps, tau)
            if p is None:
                continue
            z, y = p[0], p[1] / p[1].max()
            dof = _depth(z, y)
            ax.plot(z / dof, y, style, color=COLOR[eps], lw=2.2, alpha=alpha,
                    label=f'Ratio {eps:g}, '
                          f'{"continuous wave" if tau == "continuous wave" else "1 fs"}')
    ax.axhline(0.5, color='#999999', lw=1.2)
    ax.set_xlim(0, 1.6)
    ax.set_xlabel('Axial position, divided by that profile\'s depth of focus')
    ax.set_ylabel('On-axis intensity, normalized to the peak')
    ax.set_title(f'{lab}, three ratios, numerical aperture 0.8, 750 nm',
                 fontsize=12)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.25)

plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUT, 'panels'), 'bandwidth_invariance')
out = os.path.join(OUT, 'bandwidth_invariance.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f'Saved -> {out}')

print('\nDepth of focus read off these profiles (um):')
print(f"{'input':<22} {'ratio':>6} {'continuous':>11} {'2 fs':>8} {'1 fs':>8} "
      f"{'change':>8}")
for inp, lab in INPUTS:
    for eps in [0.0, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99]:
        vals = []
        for tau, _l, _c, _s in TAUS:
            p = axial(inp, eps, tau)
            vals.append(np.nan if p is None else _depth(p[0], p[1]))
        chg = 100 * (vals[2] / vals[0] - 1) if vals[0] else np.nan
        print(f'{lab:<22} {eps:>6.2f} {vals[0]:>11.3f} {vals[1]:>8.3f} '
              f'{vals[2]:>8.3f} {chg:>+7.2f}%')
