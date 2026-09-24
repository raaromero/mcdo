r"""Where the scalar approximation fails, and how truncation delays it.

The scalar Debye integral is the cheap model; the vector Richards-Wolf
calculation is the expensive one. Knowing the aperture at which they part
company sets the boundary of where a scalar Monte Carlo would be adequate.

Three criteria are drawn because they disagree by a factor of two, and the
disagreement is systematic rather than arbitrary: a width criterion reacts to a
change in the profile's scale, a root-mean-square criterion to a change in its
shape, and the shape survives longer than the scale does.

The second panel is the reason truncation matters here. An apodized pupil
concentrates the light near the axis, so the rays carrying energy converge at
shallower angles than the rim allows, and the scalar description survives to a
higher stated aperture: 0.75 at truncation 8 against 0.45 uniform.

    python scripts/fig_scalar_breakdown.py
    -> output/02_na_apodization/scalar_breakdown.png
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

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '02_na_apodization')
DATA = os.path.join(OUT, 'scalar_breakdown.npz')
if not os.path.exists(DATA):
    raise SystemExit('run scripts/verify_scalar_breakdown.py first')

d = np.load(DATA)
ALPHAS = sorted({float(v) for v in d['alpha_t']})
COLOR = dict(zip(ALPHAS, plt.cm.viridis(np.linspace(0.0, 0.85, len(ALPHAS)))))


def label(at):
    return 'α = 0 (Uniform)' if at == 0.0 else f'α = {at:g}'


def series(at, field):
    m = d['alpha_t'] == at
    order = np.argsort(d['na'][m])
    return d['na'][m][order], d[field][m][order]


def crossing(at, field, threshold):
    x, y = series(at, field)
    hit = np.where(y >= threshold)[0]
    return x[hit[0]] if len(hit) else np.nan


fig, axes = plt.subplots(1, 2, figsize=(17.0, 7.0))

# ── the deviation itself ──────────────────────────────────────────────────
ax = axes[0]
for at in ALPHAS:
    x, y = series(at, 'fwhm_dev')
    ax.plot(x, y, '-', color=COLOR[at], lw=2.6, label=label(at))
for thr, name in ((1.0, '1%'), (5.0, '5%')):
    ax.axhline(thr, color='#bbbbbb', lw=1.6)
    ax.text(1.26, thr, name, fontsize=10, color='#666666', va='center')
ax.set_yscale('log')
ax.set_xlabel('Numerical aperture')
ax.set_ylabel('Focal width, vector against scalar (%)')
ax.set_title('Focal width, vector against scalar, by truncation — 750 nm, continuous wave', fontsize=12)
ax.legend(fontsize=10)
ax.grid(alpha=0.25, which='both')

# ── where each criterion first fires ──────────────────────────────────────
ax = axes[1]
CRIT = [('fwhm_dev', 1.0, 'Focal width, 1%', '#1f77b4', 'o-'),
        ('fwhm_dev', 5.0, 'Focal width, 5%', '#2ca02c', 'v-'),
        ('rmse_peak', 0.01, 'Root-mean-square, peak matched', '#d62728', 's--'),
        ('rmse_energy', 0.01, 'Root-mean-square, energy matched', '#9467bd',
         '^:')]
for field, thr, lab, color, style in CRIT:
    y = [crossing(at, field, thr) for at in ALPHAS]
    ax.plot(ALPHAS, y, style, color=color, lw=2.4, ms=9, label=lab)
ax.set_xlabel('Truncation parameter α  (0 is uniform, larger is more truncated)')
ax.set_ylabel('Numerical aperture at which the criterion is first met')
ax.set_title('Aperture at which each criterion is first met — 750 nm, continuous wave', fontsize=12)
ax.legend(fontsize=10)
ax.grid(alpha=0.25)

plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUT, 'panels'), 'scalar_breakdown')
out = os.path.join(OUT, 'scalar_breakdown.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f'Saved -> {out}')

print(f"\n{'α':>6} " + '  '.join(f'{c[2]:>32}' for c in CRIT))
for at in ALPHAS:
    print(f'{at:>6.1f} ' + '  '.join(
        f'{crossing(at, c[0], c[1]):>32.2f}' for c in CRIT))
