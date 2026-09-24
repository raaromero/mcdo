r"""Where the depth-of-focus extension of an annulus comes from.

The paraxial law 1/(1-eps^2) is quoted everywhere and fails badly at the
apertures this work uses: at numerical aperture 1.2 it overstates the measured
extension by 80%. Saying so is not a result. The result is that the extension
follows an exact expression at every aperture, and that the paraxial law is its
small-angle limit.

An annulus transmits the angular band from theta_in to alpha, where

    theta_in = arcsin(eps * sin alpha).

On axis the Richards-Wolf phase is exp(i k z cos theta), so the phase the
transmitted band spans is k z (cos theta_in - cos alpha). The focus stays
bright while that spread stays below about a radian, so the depth of focus goes
as its reciprocal, and relative to the unobstructed disk

    extension(eps) = (1 - cos alpha) / (cos theta_in - cos alpha).

For small alpha, cos alpha -> 1 - alpha^2/2 and cos theta_in -> 1 - eps^2
alpha^2/2, and the expression collapses to 1/(1 - eps^2). The textbook law is
the paraxial limit of this one, not a separate result.

    python scripts/fig_exact_extension_law.py
    -> output/03_annular/exact_extension_law.png
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

from mcdo.extension import exact, paraxial
from mcdo.figio import save_panels

LAM, N_MED = 0.750, 1.3
NA_CASES = [0.1, 0.8, 1.2]
COLOR = {0.1: '#1f77b4', 0.8: '#d62728', 1.2: '#2ca02c'}

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '03_annular')
BASE = os.path.join(OUT, 'annular_baseline.npz')
os.makedirs(OUT, exist_ok=True)




if not os.path.exists(BASE):
    raise SystemExit('run scripts/verify_annular_baseline.py first')

d = np.load(BASE, allow_pickle=True)
names = [str(v) for v in d['input']]

# the same measurement with a 1 fs pulse, so the law's independence of
# wavelength and bandwidth is visible rather than asserted
APS = os.path.join(OUT, '..', '05_pulsed_pupils', 'pulsed_annular_apertures.npz')
GRID = os.path.join(OUT, '..', '05_pulsed_pupils', 'pulsed_annular_grid.npz')
_a = np.load(APS, allow_pickle=True) if os.path.exists(APS) else None
_g = np.load(GRID, allow_pickle=True) if os.path.exists(GRID) else None


def measured_pulsed(xna, eps):
    src = _g if xna == 0.8 else _a
    if src is None:
        return np.nan
    nm = [str(v) for v in src['input']]
    tt = [str(v) for v in src['tau']]
    has_na = 'na' in src.files
    for i in range(len(src['eps'])):
        if (nm[i] == 'uniform' and float(src['eps'][i]) == eps
                and tt[i] == '1 fs'
                and (not has_na or float(src['na'][i]) == xna)):
            return float(src['gain'][i])
    return np.nan


def measured(xna, eps):
    for i in range(len(d['eps'])):
        if (float(d['na'][i]) == xna and names[i] == 'uniform'
                and float(d['eps'][i]) == eps):
            return float(d['gain'][i])
    return np.nan


EPS_PTS = [0.0, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99]
e_fine = np.linspace(0.0, 0.995, 400)

fig, axes = plt.subplots(2, 2, figsize=(19.0, 13.0))

# ── the two laws against the computed extension ───────────────────────────
ax = axes[0, 0]
for xna in NA_CASES:
    y = [measured(xna, e) for e in EPS_PTS]
    ax.plot(EPS_PTS, y, 'o', color=COLOR[xna], ms=9,
            label=f'Continuous wave, numerical aperture {xna:g}')
    yp = [measured_pulsed(xna, e) for e in EPS_PTS]
    if np.isfinite(yp).any():
        ax.plot(EPS_PTS, yp, 'x', color=COLOR[xna], ms=11, mew=2.0,
                label=f'1 fs pulse, numerical aperture {xna:g}')
    ax.plot(e_fine, exact(e_fine, xna), '-', color=COLOR[xna], lw=2.0,
            label=f'Exact law, numerical aperture {xna:g}')
ax.plot(e_fine, paraxial(e_fine), 'k:', lw=2.4, label='Paraxial law')
ax.set_yscale('log')
ax.set_xlabel('Obstruction ratio')
ax.set_ylabel('Depth-of-focus extension')
ax.set_title('Depth-of-focus extension against obstruction ratio — circles continuous wave, crosses 1 fs, lines the exact law, 750 nm',
             fontsize=12)
ax.legend(fontsize=9)
ax.grid(alpha=0.25, which='both')

# ── how far each law is from the computation ──────────────────────────────
ax = axes[0, 1]
for xna in NA_CASES:
    m = np.array([measured(xna, e) for e in EPS_PTS[1:]])
    ex = np.array([exact(e, xna) for e in EPS_PTS[1:]])
    pa = np.array([paraxial(e) for e in EPS_PTS[1:]])
    ax.plot(EPS_PTS[1:], 100 * np.abs(ex / m - 1), 'o-', color=COLOR[xna],
            lw=2.0, ms=8, label=f'Exact law, numerical aperture {xna:g}')
    ax.plot(EPS_PTS[1:], 100 * np.abs(pa / m - 1), 's--', color=COLOR[xna],
            lw=1.8, ms=7, alpha=0.65,
            label=f'Paraxial law, numerical aperture {xna:g}')
ax.set_yscale('log')
ax.set_xlabel('Obstruction ratio')
ax.set_ylabel('Departure from the computed extension (%)')
ax.set_title('Departure of each law from the computed extension',
             fontsize=12)
ax.legend(fontsize=9)
ax.grid(alpha=0.25, which='both')

# ── what the annulus actually changes ─────────────────────────────────────
ax = axes[1, 0]
for xna in NA_CASES:
    alpha = np.arcsin(xna / N_MED)
    th_in = np.arcsin(np.clip(e_fine * np.sin(alpha), -1.0, 1.0))
    span = np.cos(th_in) - np.cos(alpha)
    ax.plot(e_fine, span / (1.0 - np.cos(alpha)), '-', color=COLOR[xna],
            lw=2.2, label=f'Numerical aperture {xna:g}')
ax.set_xlabel('Obstruction ratio')
ax.set_ylabel('Transmitted axial phase span, relative to the full disk')
ax.set_title('Transmitted axial phase span against obstruction ratio',
             fontsize=12)
ax.legend(fontsize=10)
ax.grid(alpha=0.25)

# ── the paraxial law as a limit ───────────────────────────────────────────
ax = axes[1, 1]
na_fine = np.linspace(0.02, 1.29, 300)
for eps_show, style in [(0.5, '-'), (0.9, '--'), (0.99, ':')]:
    ratio = [exact(eps_show, x) / paraxial(eps_show) for x in na_fine]
    ax.plot(na_fine, ratio, style, color='#1d1d1f', lw=2.2,
            label=f'Obstruction ratio {eps_show:g}')
for xna in NA_CASES:
    ax.axvline(xna, color=COLOR[xna], lw=1.4, alpha=0.5)
ax.axhline(1.0, color='#888888', lw=1.2)
ax.set_xlabel('Numerical aperture')
ax.set_ylabel('Exact law divided by the paraxial law')
ax.set_title('Exact law divided by the paraxial law, against numerical aperture',
             fontsize=12)
ax.legend(fontsize=10)
ax.grid(alpha=0.25)

plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUT, 'panels'), 'exact_extension_law')
out = os.path.join(OUT, 'exact_extension_law.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f'Saved -> {out}')

print(f"\n{'NA':>5} {'ratio':>6} {'computed':>9} {'exact':>8} {'paraxial':>9} "
      f"{'exact err':>10} {'paraxial err':>13}")
for xna in NA_CASES:
    for e in EPS_PTS[1:]:
        m = measured(xna, e)
        ex, pa = exact(e, xna), paraxial(e)
        print(f'{xna:>5.1f} {e:>6.2f} {m:>9.3f} {ex:>8.3f} {pa:>9.3f} '
              f'{100 * abs(ex / m - 1):>9.2f}% {100 * abs(pa / m - 1):>12.2f}%')
