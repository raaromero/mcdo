r"""At what pulse duration does a pulse behave as continuous wave?

The rest of this work compares continuous wave against 1 fs, which shows that
a difference exists but not how quickly it disappears. This sweeps seven
durations and reads the crossover off directly.

Both quantities fall roughly as the inverse square of the duration, so the
departure is quadratic in bandwidth. A uniform pupil is within 1% of continuous
wave by 2 fs; a truncated one takes 5 fs, and 20 fs to reach 0.1%. Anything at
or beyond 5 fs behaves as continuous light for depth of focus, which bounds the
result to the few-cycle regime rather than to pulsed illumination generally.

    python scripts/fig_duration_crossover.py
    -> output/05_pulsed_pupils/duration_crossover.png
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
DATA = os.path.join(OUT, 'duration_sweep.npz')
if not os.path.exists(DATA):
    raise SystemExit('run scripts/verify_duration.py first')

d = np.load(DATA, allow_pickle=True)
names = [str(v) for v in d['input']]
TAUS = [1.0, 2.0, 3.0, 5.0, 10.0, 20.0]
EPS = sorted({float(v) for v in d['eps']})
STYLE = {'uniform': ('#1f77b4', 'o-', 'Uniform'),
         'Gaussian': ('#d62728', 's--', 'Gaussian, α = 4')}


def val(inp, tau_fs, eps, field):
    for i in range(len(d['eps'])):
        if (names[i].startswith(inp) and float(d['tau_fs'][i]) == tau_fs
                and float(d['eps'][i]) == eps):
            return float(d[field][i])
    return np.nan


def cw(inp, eps, field):
    for i in range(len(d['eps'])):
        if (names[i].startswith(inp) and not np.isfinite(d['tau_fs'][i])
                and float(d['eps'][i]) == eps):
            return float(d[field][i])
    return np.nan


fig, axes = plt.subplots(1, 2, figsize=(17.0, 7.0))

# ── how far the depth sits from continuous wave ───────────────────────────
ax = axes[0]
for inp, (color, style, lab) in STYLE.items():
    y = [100.0 * abs(val(inp, t, 0.0, 'depth_um') / cw(inp, 0.0, 'depth_um') - 1.0)
         for t in TAUS]
    ax.plot(TAUS, y, style, color=color, lw=2.4, ms=9, label=lab)
ref = np.array(TAUS, dtype=float)
ax.plot(ref, 1.0 * (ref / 2.0) ** -2, ':', color='#888888', lw=2.0,
        label='Inverse square of the duration')
for thr, name in ((1.0, '1%'), (0.1, '0.1%')):
    ax.axhline(thr, color='#bbbbbb', lw=1.6)
    ax.text(21.0, thr, name, fontsize=10, color='#666666', va='center')
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Pulse duration (fs)')
ax.set_ylabel('Departure of the depth from continuous wave (%)')
ax.set_title('Depth of focus against pulse duration, relative to continuous wave\n'
             'No obstruction, numerical aperture 0.8, 750 nm', fontsize=12)
ax.legend(fontsize=10)
ax.grid(alpha=0.25, which='both')

# ── and the extension, which is what the result rests on ──────────────────
ax = axes[1]
for inp, (color, style, lab) in STYLE.items():
    for eps, alpha_v in ((0.5, 0.45), (0.9, 1.0)):
        y = [100.0 * abs(val(inp, t, eps, 'gain') / cw(inp, eps, 'gain') - 1.0)
             for t in TAUS]
        ax.plot(TAUS, y, style, color=color, lw=2.4, ms=8, alpha=alpha_v,
                label=f'{lab}, obstruction ratio {eps:g}')
for thr, name in ((1.0, '1%'), (0.1, '0.1%')):
    ax.axhline(thr, color='#bbbbbb', lw=1.6)
    ax.text(21.0, thr, name, fontsize=10, color='#666666', va='center')
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Pulse duration (fs)')
ax.set_ylabel('Departure of the extension from continuous wave (%)')
ax.set_title('Extension against pulse duration, relative to continuous wave\n'
             'Numerical aperture 0.8, 750 nm', fontsize=12)
ax.legend(fontsize=9)
ax.grid(alpha=0.25, which='both')

plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUT, 'panels'), 'duration_crossover')
out = os.path.join(OUT, 'duration_crossover.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f'Saved -> {out}')

print('\nShortest duration within a threshold of continuous wave')
for inp in ('uniform', 'Gaussian'):
    for thr in (1.0, 0.1):
        hit = next((t for t in TAUS
                    if abs(val(inp, t, 0.0, 'depth_um')
                           / cw(inp, 0.0, 'depth_um') - 1.0) * 100 <= thr),
                   None)
        print(f'  {inp:<10} depth within {thr:>4.1f}%: '
              f'{str(int(hit)) + " fs" if hit else "beyond 20 fs"}')
