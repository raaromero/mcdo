r"""The truncation sweep paired with a pulse.

Every other parameter in this study has its continuous-wave and pulsed halves.
The truncation parameter did not, so the claim that bandwidth costs extension
"for a truncated Gaussian" rested on a single value, alpha = 4. This runs the
pairing across the whole sweep, alpha = 0 to 4.

A uniform pupil keeps its extension at 1 fs; the loss grows steadily with
truncation, reaching 7.48% at alpha = 4. The depth of focus itself is longer at
1 fs at every obstruction ratio - what falls is the ratio to the unobstructed
case, because the pulse lengthens the unobstructed focus by more.

    python scripts/fig_truncation_pulsed.py
    -> output/02_na_apodization/truncation_pulsed.png
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
DATA = os.path.join(OUT, 'truncation_pulsed.npz')
if not os.path.exists(DATA):
    raise SystemExit('run scripts/verify_truncation_pulsed.py first')

d = np.load(DATA, allow_pickle=True)
taus = [str(v) for v in d['tau']]
# alpha 8 sits in a different regime and is not presented
ALPHAS = [0.0, 1.0, 2.0, 4.0]
CLEAN = [0.0, 1.0, 2.0, 4.0]
EPS = [0.0, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99]
COLOR = dict(zip(ALPHAS, plt.cm.viridis(np.linspace(0.0, 0.85, len(ALPHAS)))))


def label(at):
    """alpha = 0 is an untruncated pupil, so name it rather than number it."""
    return 'α = 0 (Uniform)' if at == 0.0 else f'α = {at:g}'


HAS_NA = 'na' in d.files
X_NA = 0.8          # the sweep now spans three apertures; this figure is 0.8


def val(at, eps, tau, field):
    for i in range(len(d['eps'])):
        if ((not HAS_NA or float(d['na'][i]) == X_NA)
                and float(d['alpha_t'][i]) == at
                and float(d['eps'][i]) == eps and taus[i] == tau):
            return float(d[field][i])
    return np.nan


def erosion(at, eps):
    cw = val(at, eps, 'continuous wave', 'gain')
    p = val(at, eps, '1 fs', 'gain')
    return 100.0 * (1.0 - p / cw)


fig, axes = plt.subplots(2, 2, figsize=(19.0, 13.0))

# ── the pairing itself ────────────────────────────────────────────────────
ax = axes[0, 0]
for at in ALPHAS:
    ax.plot(EPS, [val(at, e, 'continuous wave', 'gain') for e in EPS], 'o-',
            color=COLOR[at], lw=2.2, ms=8,
            label=f'{label(at)}, continuous wave')
    ax.plot(EPS, [val(at, e, '1 fs', 'gain') for e in EPS], 's:',
            color=COLOR[at], lw=1.8, ms=7, alpha=0.75,
            label=f'{label(at)}, 1 fs')
ax.set_yscale('log')
ax.set_xlabel('Obstruction ratio')
ax.set_ylabel('Depth-of-focus extension')
ax.set_title('Depth-of-focus extension against obstruction ratio, continuous wave and 1 fs — numerical aperture 0.8, 750 nm', fontsize=12)
ax.legend(fontsize=7, ncol=2)
ax.grid(alpha=0.25, which='both')

# ── erosion against obstruction, one curve per alpha ──────────────────────
ax = axes[0, 1]
for at in ALPHAS:
    style = 'o-' if at in CLEAN else '^--'
    ax.plot(EPS[1:], [erosion(at, e) for e in EPS[1:]], style,
            color=COLOR[at], lw=2.2, ms=8,
            label=label(at))
ax.axhline(0.0, color='#999999', lw=1.2)
ax.set_xlabel('Obstruction ratio')
ax.set_ylabel('Extension lost at 1 fs (%)')
ax.set_title('Extension lost at 1 fs against obstruction ratio — numerical aperture 0.8, 750 nm', fontsize=12)
ax.legend(fontsize=9)
ax.grid(alpha=0.25)

# ── erosion against alpha, one curve per ratio ────────────────────────────
ax = axes[1, 0]
ECOL = dict(zip([0.3, 0.5, 0.9, 0.99],
                ['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728']))
for e in (0.3, 0.5, 0.9, 0.99):
    ax.plot(ALPHAS, [erosion(at, e) for at in ALPHAS], 'o-', color=ECOL[e],
            lw=2.2, ms=9, label=f'Obstruction ratio {e:g}')
ax.axhline(0.0, color='#999999', lw=1.2)
ax.set_xlabel('Truncation parameter α  (0 is uniform, larger is more truncated)')
ax.set_ylabel('Extension lost at 1 fs (%)')
ax.set_title('Extension lost at 1 fs against truncation parameter — numerical aperture 0.8, 750 nm',
             fontsize=12)
ax.legend(fontsize=9)
ax.grid(alpha=0.25)

# ── the pulse's lengthening of the depth of focus, against obstruction ────
ax = axes[1, 1]
for at in ALPHAS:
    y = [val(at, e, '1 fs', 'depth_um') / val(at, e, 'continuous wave',
                                              'depth_um') for e in EPS]
    ax.plot(EPS, y, 'o-', color=COLOR[at], lw=2.2, ms=8, label=label(at))
ax.axhline(1.0, color='#999999', lw=1.2)
ax.set_xlabel('Obstruction ratio')
ax.set_ylabel('Depth of focus, 1 fs ÷ continuous wave')
ax.set_title('Depth of focus at 1 fs divided by depth of focus at continuous '
             'wave — numerical aperture 0.8, 750 nm', fontsize=12)
ax.legend(fontsize=9)
ax.grid(alpha=0.25)

plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUT, 'panels'), 'truncation_pulsed')
out = os.path.join(OUT, 'truncation_pulsed.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f'Saved -> {out}')

print(f"\n{'alpha':>6} " + "  ".join(f"eps {e:<5}" for e in EPS[1:]))
for at in ALPHAS:
    print(f"{at:>6.1f} " + "  ".join(f"{erosion(at, e):+8.2f}"
                                     for e in EPS[1:]))
