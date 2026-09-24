r"""When a thin annulus becomes a Bessel beam, and when it does not.

An infinitely thin ring transmits a single cone angle, so its focal field is the
J0 squared pattern of a nondiffracting beam [Dur87]. mcdo/annular.py names that
limit as a checkpoint on the Babinet subtraction. It holds only where the field
is effectively scalar.

Top row is the approach at each aperture: the measured transverse profile
against J0 squared drawn on the same axes. At aperture 0.1 the ring converges
onto it. At 1.2 it does not, and the gap sits in the nulls, which the
longitudinal field fills once the cone is wide.

Bottom row makes that quantitative: the root-mean-square gap against
obstruction ratio, and the depth of the first minimum, which is where the
filling shows up. The two say the same thing from different directions - the
ring's shape becomes Bessel-like while its zeros stop being zeros.

Profiles come from the saved sweeps. Nothing is recomputed.

    python scripts/fig_bessel_limit.py
    -> output/03_annular/bessel_limit.png
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.special import j0

from mcdo.style import apply as _apply_style
_apply_style()

from mcdo.figio import save_panels
from mcdo.profiles import first_minimum as _first_minimum

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
LAM, N_MED = 0.750, 1.3
K = 2.0 * np.pi * N_MED / LAM
COLOR = {0.0: '#1d1d1f', 0.5: '#1f77b4', 0.9: '#2ca02c', 0.99: '#d62728'}


def profile(na, eps):
    src = g if na == 0.8 else a
    key = f'{na}|uniform|{eps}|continuous wave|r'
    if key not in src.files:
        return None
    p = src[key]
    return p[0], p[1] / p[1].max()


def bessel(r, na):
    return j0(K * np.sin(np.arcsin(na / N_MED)) * r) ** 2


def deviation(na, eps, span):
    p = profile(na, eps)
    if p is None:
        return np.nan
    r, y = p
    m = r <= span
    return float(np.sqrt(np.mean((y[m] - bessel(r[m], na)) ** 2)))


def first_minimum(r, y, na):
    """Depth of the first transverse minimum, guarded (see mcdo.profiles)."""
    return _first_minimum(r, y)[1]


SPAN = {0.1: 12.0, 0.8: 1.5, 1.2: 1.0}
fig, axes = plt.subplots(2, 2, figsize=(19.0, 13.0))

# ── the approach itself, at the two apertures that differ most ────────────
for col, na in enumerate((0.1, 1.2)):
    ax = axes[0, col]
    span = SPAN[na]
    for eps in (0.0, 0.9, 0.99):
        p = profile(na, eps)
        if p is None:
            continue
        r, y = p
        m = r <= span
        ax.semilogy(r[m], np.maximum(y[m], 1e-5), '-', color=COLOR[eps],
                    lw=2.2, label=f'Obstruction ratio {eps:g}')
    rr = np.linspace(0, span, 800)
    ax.semilogy(rr, np.maximum(bessel(rr, na), 1e-5), 'k--', lw=2.0,
                label='J0 squared, the nondiffracting limit')
    ax.set_ylim(1e-5, 1.8)
    ax.set_xlabel('Radial position (um)')
    ax.set_ylabel('Transverse intensity, normalized to the peak')
    ax.set_title(f'Numerical aperture {na:g}, continuous wave, 750 nm',
                 fontsize=12)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.25, which='both')

# ── how far from the limit, against obstruction ratio ─────────────────────
ax = axes[1, 0]
for na, marker in ((0.1, 'o-'), (0.8, 's--'), (1.2, '^:')):
    eps_list = [0.0, 0.5, 0.9, 0.99] if na != 0.8 else [0.0, 0.3, 0.5, 0.7,
                                                        0.9, 0.95, 0.99]
    y = [deviation(na, e, SPAN[na]) for e in eps_list]
    ax.plot(eps_list, y, marker, lw=2.0, ms=8,
            label=f'Numerical aperture {na:g}')
ax.set_yscale('log')
ax.set_xlabel('Obstruction ratio')
ax.set_ylabel('Root-mean-square gap from J0 squared')
ax.set_title('Departure from the Bessel limit against obstruction ratio',
             fontsize=12)
ax.legend(fontsize=10)
ax.grid(alpha=0.25, which='both')

# ── where the gap sits: the nulls ─────────────────────────────────────────
ax = axes[1, 1]
for na, marker in ((0.1, 'o-'), (0.8, 's--'), (1.2, '^:')):
    eps_list = [0.0, 0.5, 0.9, 0.99] if na != 0.8 else [0.0, 0.3, 0.5, 0.7,
                                                        0.9, 0.95, 0.99]
    y = []
    for e in eps_list:
        p = profile(na, e)
        y.append(np.nan if p is None else first_minimum(p[0], p[1], na))
    ax.plot(eps_list, y, marker, lw=2.0, ms=8,
            label=f'Numerical aperture {na:g}')
ax.set_xlabel('Obstruction ratio')
ax.set_ylabel('First minimum, as a fraction of the peak')
ax.set_title('First transverse minimum against obstruction ratio'
             '\nGaps: no transverse minimum remains to measure',
             fontsize=12)
ax.legend(fontsize=10)
ax.grid(alpha=0.25)

plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUT, 'panels'), 'bessel_limit')
out = os.path.join(OUT, 'bessel_limit.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f'Saved -> {out}')

print(f"\n{'NA':>5} {'ratio':>6} {'gap from J0^2':>15} {'first minimum':>15}")
for na in (0.1, 0.8, 1.2):
    for e in ([0.0, 0.5, 0.9, 0.99] if na != 0.8
              else [0.0, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99]):
        p = profile(na, e)
        fm = np.nan if p is None else first_minimum(p[0], p[1], na)
        print(f'{na:>5} {e:>6.2f} {deviation(na, e, SPAN[na]):>15.4f} '
              f'{fm:>15.4f}')
