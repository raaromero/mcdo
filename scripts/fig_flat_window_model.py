r"""The model the closed-form extension law comes from, and where it breaks.

On axis the Richards-Wolf integral is a Fourier transform over cos theta: the
pupil contributes a window of width

    Delta = cos theta_in - cos alpha,

so the axial intensity is sinc squared in k z Delta / 2 and its width goes as
1 / (k Delta). The ratio of that width to the unobstructed one is

    (1 - cos alpha) / (cos theta_in - cos alpha),

which is the extension law, derived rather than fitted. Nothing in it depends on
wavelength, which is why a uniform annulus gives a pulse the same extension it
gives continuous light.

The model treats the window as flat. The real pupil carries the aplanatic
weighting sqrt(cos theta) sin theta (1 + cos theta), which varies across the
window, so the model errs where that variation is large: at a wide cone with no
obstruction. A ring narrows the window and the weighting flattens over it, so
the model becomes exact at high obstruction whatever the aperture. That is the
whole error pattern, drawn in the lower row.

Sweeps and an analytic model only. No focal fields are recomputed.

    python scripts/fig_flat_window_model.py
    -> output/03_annular/flat_window_model.png
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

from mcdo import SimConfig
from mcdo.figio import save_panels

ROOT = os.path.join(os.path.dirname(__file__), '..')
OUT = os.path.join(ROOT, 'output', '03_annular')
GRID = os.path.join(ROOT, 'output', '05_pulsed_pupils', 'pulsed_annular_grid.npz')
APS = os.path.join(ROOT, 'output', '05_pulsed_pupils',
                   'pulsed_annular_apertures.npz')
for p in (GRID, APS):
    if not os.path.exists(p):
        raise SystemExit(f'missing {p}')

g = np.load(GRID, allow_pickle=True)
a = np.load(APS, allow_pickle=True)
NAS = [0.1, 0.8, 1.2]
EPS = [0.0, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99]
COLOR = {0.1: '#1f77b4', 0.8: '#d62728', 1.2: '#2ca02c'}
ZMAX = {0.1: 20000.0, 0.8: 400.0, 1.2: 200.0}


def cfg_for(na):
    return SimConfig(lam_c=0.750, X_NA=na, n=1.3, tau=np.inf,
                     N_freq=3, N_theta=801)


def model_profile(na, eps, z):
    c = cfg_for(na)
    delta = np.cos(np.arcsin(eps * np.sin(c.alpha))) - np.cos(c.alpha)
    x = c.k_c * z * delta / 2.0
    return np.where(np.abs(x) < 1e-12, 1.0,
                    (np.sin(x) / np.maximum(np.abs(x), 1e-300)) ** 2)


def _fwhm(z, y):
    y = y / y.max()
    below = np.where(y < 0.5)[0]
    if not len(below):
        return np.nan
    i = below[0]
    return 2.0 * np.interp(0.5, [y[i], y[i - 1]], [z[i], z[i - 1]])


def model_depth(na, eps):
    z = np.linspace(0.0, ZMAX[na], 200001)
    return _fwhm(z, model_profile(na, eps, z))


def swept_depth(na, eps):
    src, has_na = (g, False) if na == 0.8 else (a, True)
    names = [str(v) for v in src['input']]
    taus = [str(v) for v in src['tau']]
    for i in range(len(src['eps'])):
        if (names[i].startswith('uniform') and float(src['eps'][i]) == eps
                and taus[i] == 'continuous wave'
                and (not has_na or float(src['na'][i]) == na)):
            return float(src['depth_um'][i])
    return np.nan


fig, axes = plt.subplots(2, 2, figsize=(19.0, 13.0))

# ── the profiles the model claims to reproduce ────────────────────────────
for col, eps in enumerate((0.0, 0.99)):
    ax = axes[0, col]
    key = f'0.8|uniform|{eps}|continuous wave|z'
    if key in g.files:
        p = g[key]
        ax.plot(p[0], p[1] / p[1].max(), '-', color='#1d1d1f', lw=2.4,
                label='Richards-Wolf, all three components')
    zz = np.linspace(0.0, 400.0, 200001)
    ax.plot(zz, model_profile(0.8, eps, zz), '--', color='#d62728', lw=2.0,
            label='Flat window in cos theta')
    ax.axhline(0.5, color='#999999', lw=1.2)
    span = 6.0 if eps == 0.0 else 180.0
    ax.set_xlim(0, span)
    ax.set_xlabel('Axial position (um)')
    ax.set_ylabel('On-axis intensity, normalized to the peak')
    ax.set_title(f'Obstruction ratio {eps:g}, numerical aperture 0.8, 750 nm',
                 fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(alpha=0.25)

# ── the error pattern ─────────────────────────────────────────────────────
ax = axes[1, 0]
for na in NAS:
    eps_here = EPS if na == 0.8 else [0.0, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99]
    y = []
    for e in eps_here:
        s = swept_depth(na, e)
        y.append(np.nan if not np.isfinite(s) else 100.0 * abs(model_depth(na, e) / s - 1.0))
    ax.plot(eps_here, y, 'o-', color=COLOR[na], lw=2.0, ms=8,
            label=f'Numerical aperture {na:g}')
ax.set_yscale('log')
ax.set_xlabel('Obstruction ratio')
ax.set_ylabel('Model departure from the full calculation (%)')
ax.set_title('Departure of the flat-window model from the full calculation',
             fontsize=12)
ax.legend(fontsize=10)
ax.grid(alpha=0.25, which='both')

# ── why: the weighting varies across the window ───────────────────────────
ax = axes[1, 1]
for na in NAS:
    c = cfg_for(na)
    y = []
    for e in EPS:
        th_in = np.arcsin(e * np.sin(c.alpha))
        th = np.linspace(th_in, c.alpha, 2001)
        w = np.sqrt(np.cos(th)) * np.sin(th) * (1.0 + np.cos(th))
        y.append(100.0 * (w.max() - w.min()) / w.max())
    ax.plot(EPS, y, 'o-', color=COLOR[na], lw=2.0, ms=8,
            label=f'Numerical aperture {na:g}')
ax.set_xlabel('Obstruction ratio')
ax.set_ylabel('Variation of the aplanatic weight across the window (%)')
ax.set_title('Variation of the aplanatic weight across the transmitted window',
             fontsize=12)
ax.legend(fontsize=10)
ax.grid(alpha=0.25)

plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUT, 'panels'), 'flat_window_model')
out = os.path.join(OUT, 'flat_window_model.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f'Saved -> {out}')

print(f"\n{'NA':>5} {'eps':>6} {'model um':>11} {'swept um':>11} {'err':>8} "
      f"{'weight spread':>14}")
for na in NAS:
    c = cfg_for(na)
    for e in EPS:
        s = swept_depth(na, e)
        if not np.isfinite(s):
            continue
        th_in = np.arcsin(e * np.sin(c.alpha))
        th = np.linspace(th_in, c.alpha, 2001)
        w = np.sqrt(np.cos(th)) * np.sin(th) * (1.0 + np.cos(th))
        spread = 100.0 * (w.max() - w.min()) / w.max()
        m = model_depth(na, e)
        print(f'{na:>5} {e:>6.2f} {m:>11.3f} {s:>11.3f} '
              f'{100 * (m / s - 1):>+7.2f}% {spread:>13.1f}%')
