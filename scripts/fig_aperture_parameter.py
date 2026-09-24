"""What numerical aperture does, drawn as the focusing geometry.

Illumination and obstruction change the pupil pattern. Numerical aperture does
not: in normalized pupil coordinates the pupil looks identical. What it changes
is the cone half-angle the rays converge at,

    alpha = arcsin(NA / n),

which is 4.4 degrees at NA 0.1 and 67 degrees at NA 1.2 in a medium of index
1.3. The paraxial depth-of-focus law assumes small angles, so this is the
parameter that decides whether it applies.

An annulus passes only the angular band between arcsin(eps sin alpha) and
alpha. Drawing that band makes both results visible at once: why a ring
lengthens the focus at all, and why the paraxial prediction degrades as the
aperture grows.
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

LAM, N_MED = 0.750, 1.3
NA_CASES = [0.1, 0.8, 1.2]
EPS = 0.9
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '03_annular')

fig, axes = plt.subplots(1, 4, figsize=(34.0, 8.0))

print(f"{'X_NA':>5} {'alpha (deg)':>12} {'inner (deg)':>12} {'band (deg)':>11}")
for ax, xna in zip(axes, NA_CASES):
    cfg = SimConfig(lam_c=LAM, X_NA=xna, n=N_MED, tau=np.inf, N_freq=3, N_theta=101)
    alpha = cfg.alpha
    th_in = np.arcsin(EPS * np.sin(alpha))
    print(f"{xna:>5.1f} {np.degrees(alpha):>12.1f} {np.degrees(th_in):>12.1f} "
          f"{np.degrees(alpha - th_in):>11.1f}")

    L = 1.0
    for th in np.linspace(0.0, alpha, 25):
        blocked = th < th_in
        for sgn in (-1, 1):
            ax.plot([-L * np.cos(th), 0.0], [sgn * L * np.sin(th), 0.0],
                    color='#cccccc' if blocked else '#1f77b4',
                    lw=1.0 if blocked else 1.8,
                    ls=':' if blocked else '-',
                    alpha=0.5 if blocked else 0.9, zorder=1)

    wedge = np.linspace(th_in, alpha, 40)
    ax.fill_between(-0.55 * np.cos(wedge), -0.55 * np.sin(wedge),
                    0.55 * np.sin(wedge), color='#1f77b4', alpha=0.10, zorder=0)
    ax.plot(0, 0, 'o', color='#d62728', ms=9, zorder=3)
    ax.annotate(f'{np.degrees(alpha):.0f} degrees', xy=(-0.62, 0.0),
                fontsize=13, ha='center', va='center', color='#1f77b4')
    ax.set_xlim(-1.05, 0.35)
    ax.set_ylim(-1.05, 1.05)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(f'Numerical aperture {xna:g}, obstruction ratio {EPS:g}, '
                 f'rays span {np.degrees(alpha - th_in):.0f} degrees', fontsize=13)

# the three cones on one axes, so the angles can be compared rather than recalled
ax = axes[3]
COL = {0.1: '#2ca02c', 0.8: '#1f77b4', 1.2: '#d62728'}
for xna in NA_CASES:
    cfg = SimConfig(lam_c=LAM, X_NA=xna, n=N_MED, tau=np.inf, N_freq=3, N_theta=101)
    a = cfg.alpha
    for sgn in (-1, 1):
        ax.plot([-np.cos(a), 0.0], [sgn * np.sin(a), 0.0],
                color=COL[xna], lw=2.6,
                label=f'Numerical aperture {xna:g}, {np.degrees(a):.0f} degrees'
                if sgn == 1 else None)
    arc = np.linspace(0.0, a, 60)
    ax.plot(-0.34 * np.cos(arc), 0.34 * np.sin(arc), color=COL[xna], lw=1.6, ls='--')
ax.plot(0, 0, 'o', color='#333333', ms=9)
ax.set_xlim(-1.05, 0.35)
ax.set_ylim(-1.05, 1.05)
ax.set_aspect('equal')
ax.axis('off')
ax.set_title('Cone half-angle compared across numerical aperture', fontsize=13)
ax.legend(fontsize=11, loc='lower right')

fig.suptitle('Focusing geometry against numerical aperture, refractive index 1.3',
             fontsize=15)
plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUT, 'panels'), 'fig_aperture_parameter')
out = os.path.join(OUT, 'fig_aperture_parameter.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f'\nSaved → {out}')
