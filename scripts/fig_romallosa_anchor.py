r"""The annular results, anchored to the replication.

Two things need to be true before an annular depth of focus can be quoted next
to Romallosa's numbers. The unobstructed case has to be the same computation
the replication ran, and the depth has to be independent of which intensity
convention is used - because the annular sweeps report the azimuthal average
while the paper reports the y-cut of a linearly polarized input.

Both hold, and the second holds exactly rather than approximately. On axis the
Bessel arguments vanish, so I1 and I2 are identically zero and every convention
collapses to |I0| squared. The axial profile cannot depend on polarization.

The conventions do differ transversely, which is why the published focal width
is 472.8 nm while the azimuthal average gives 497.5 nm. That difference is
real, and it is confined to a quantity this work does not report.

    python scripts/fig_romallosa_anchor.py
    -> output/01_romallosa/romallosa_anchor.png
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
from mcdo.annular import compute_integrals_annular
from mcdo.figio import save_panels
from mcdo.rw_integrals import compute_integrals

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '01_romallosa')
os.makedirs(OUT, exist_ok=True)

LAM, N_MED, X_NA, NT = 0.750, 1.3, 0.8, 801
cfg = SimConfig(lam_c=LAM, X_NA=X_NA, n=N_MED, tau=np.inf, N_freq=3, N_theta=NT)

CONV = [
    ('Azimuthal average', lambda a, b, d: np.abs(a) ** 2 + np.abs(d) ** 2
     + 2 * np.abs(b) ** 2, '#d62728', '-'),
    ('Romallosa y-cut', lambda a, b, d: np.abs(a - d) ** 2, '#1f77b4', '--'),
    ('x-cut', lambda a, b, d: np.abs(a + d) ** 2 + 4 * np.abs(b) ** 2,
     '#2ca02c', ':'),
    ('Scalar', lambda a, b, d: np.abs(a) ** 2, '#9467bd', '-.'),
]
EPS = [0.0, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99]


def integrals(r, z, eps):
    if eps == 0.0:
        return compute_integrals(r, z, cfg.k_c, cfg.alpha, NT)
    return compute_integrals_annular(r, z, cfg.k_c, cfg.alpha, eps, NT)


def fwhm(x, y):
    y = y / y.max()
    below = np.where(y < 0.5)[0]
    if not len(below):
        return np.nan
    i = below[0]
    return 2.0 * np.interp(0.5, [y[i], y[i - 1]], [x[i], x[i - 1]])


fig, axes = plt.subplots(2, 2, figsize=(19.0, 13.0))

# ── the transverse profile, where the conventions genuinely differ ────────
r = np.linspace(0.0, 1.6, 4000)
A = integrals(r, np.array([0.0]), 0.0)
I0, I1, I2 = A[0][0], A[1][0], A[2][0]
ax = axes[0, 0]
for name, f, color, style in CONV:
    y = f(I0, I1, I2)
    y = y / y.max()
    ax.plot(r * 1000, y, style, color=color, lw=2.2,
            label=f'{name}, {fwhm(r, f(I0, I1, I2)) * 1000:.1f} nm')
ax.axhline(0.5, color='#999999', lw=1.2)
ax.set_xlim(0, 900)
ax.set_xlabel('Radial position (nm)')
ax.set_ylabel('Transverse intensity, normalized to the peak')
ax.set_title('Transverse profile by intensity convention — obstruction ratio 0, '
             'numerical aperture 0.8, 750 nm', fontsize=11)
ax.legend(fontsize=10)
ax.grid(alpha=0.25)

# ── the axial profile, where they do not ──────────────────────────────────
z = np.linspace(0.0, 20.0, 8000)
ax = axes[0, 1]
for eps, width in ((0.0, 2.6), (0.5, 2.2), (0.9, 1.8)):
    B = integrals(np.array([0.0]), z, eps)
    J0, J1, J2 = B[0][:, 0], B[1][:, 0], B[2][:, 0]
    for name, f, color, style in CONV:
        y = f(J0, J1, J2)
        ax.plot(z, y / y.max(), style, color=color, lw=width,
                label=f'{name}, ratio {eps:g}' if eps == 0.0 else None)
ax.axhline(0.5, color='#999999', lw=1.2)
ax.set_xlim(0, 16)
ax.set_xlabel('Axial position (um)')
ax.set_ylabel('On-axis intensity, normalized to the peak')
ax.set_title('On-axis profile by intensity convention, three obstruction ratios\n'
             'Three ratios drawn, four conventions each — twelve curves, '
             'three visible', fontsize=11)
ax.legend(fontsize=9)
ax.grid(alpha=0.25)

# ── so the extension is the same number whichever is used ─────────────────
ax = axes[1, 0]
for name, f, color, style in CONV:
    depths = []
    for eps in EPS:
        zz = np.linspace(0.0, 400.0, 40001)
        B = integrals(np.array([0.0]), zz, eps)
        depths.append(fwhm(zz, f(B[0][:, 0], B[1][:, 0], B[2][:, 0])))
    depths = np.array(depths)
    ax.plot(EPS, depths / depths[0], style, color=color, lw=2.4, marker='o',
            ms=8, label=name)
ax.set_yscale('log')
ax.set_xlabel('Obstruction ratio')
ax.set_ylabel('Depth-of-focus extension')
ax.set_title('Depth-of-focus extension by intensity convention\n'
             'Numerical aperture 0.8, 750 nm, continuous wave', fontsize=11)
ax.legend(fontsize=10)
ax.grid(alpha=0.25, which='both')

# ── why: the two integrals that carry polarization vanish on axis ─────────
ax = axes[1, 1]
rr = np.linspace(0.0, 1.2, 2000)
C = integrals(rr, np.array([0.0]), 0.0)
for lab, arr, color in (('|I0|, the scalar term', np.abs(C[0][0]), '#9467bd'),
                        ('|I1|, longitudinal', np.abs(C[1][0]), '#ff7f0e'),
                        ('|I2|, cross term', np.abs(C[2][0]), '#1f77b4')):
    ax.plot(rr * 1000, arr / np.abs(C[0][0]).max(), '-', color=color, lw=2.4,
            label=lab)
ax.axvline(0.0, color='#999999', lw=1.2)
ax.set_xlim(0, 700)
ax.set_xlabel('Radial position (nm)')
ax.set_ylabel('Magnitude, relative to the peak of |I0|')
ax.set_title('Magnitude of I0, I1 and I2 against radial position\n'
             'J1(0) and J2(0) are zero, so only |I0| survives on axis',
             fontsize=11)
ax.legend(fontsize=10)
ax.grid(alpha=0.25)

plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUT, 'panels'), 'romallosa_anchor')
out = os.path.join(OUT, 'romallosa_anchor.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f'Saved -> {out}')

print('\nOn axis, the two polarization-carrying integrals:')
B = integrals(np.array([0.0]), np.linspace(0.0, 20.0, 2000), 0.0)
print(f'  max |I1| = {np.abs(B[1]).max():.3e}')
print(f'  max |I2| = {np.abs(B[2]).max():.3e}')
