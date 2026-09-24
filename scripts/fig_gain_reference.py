"""What the depth-of-focus gain is measured against.

The gain plotted elsewhere is a ratio, and a ratio is meaningless without its
denominator. This shows the denominator: the axial profile of the same pupil
with no central stop, beside the obstructed profile, both in micrometres, with
the two depths of focus marked at half maximum.

Left panel is the pair in absolute units, so the extension can be read as a
length. Right panel is the same pair with the axis divided by the unobstructed
depth of focus, which is the normalization used in the rest of this section.
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
from mcdo.components import full as vec_intensity
from mcdo.figio import save_panels
from mcdo.rw_integrals import compute_integrals

LAM, XNA, NT = 0.750, 0.8, 801
EPS = 0.9
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '03_annular')

cfg = SimConfig(lam_c=LAM, X_NA=XNA, n=1.3, tau=np.inf, N_freq=3, N_theta=NT)
z = np.linspace(0.0, 40.0 * 2.0 * LAM / XNA ** 2, 4000)
r0 = np.array([0.0])


def _axial(eps):
    if eps == 0.0:
        A0, A1, A2 = compute_integrals(r0, z, cfg.k_c, cfg.alpha, NT)
    else:
        A0, A1, A2 = compute_integrals_annular(r0, z, cfg.k_c, cfg.alpha, eps, NT)
    I = vec_intensity(A0[:, 0], A1[:, 0], A2[:, 0])
    return I / I.max()


def _dof(zz, I):
    below = np.where(I < 0.5)[0]
    i = below[0]
    return 2.0 * np.interp(0.5, [I[i], I[i - 1]], [zz[i], zz[i - 1]])


I_ref, I_obs = _axial(0.0), _axial(EPS)
d_ref, d_obs = _dof(z, I_ref), _dof(z, I_obs)
print(f'unobstructed depth of focus {d_ref:.3f} um')
print(f'obstruction ratio {EPS:g} depth of focus {d_obs:.3f} um')
print(f'ratio {d_obs / d_ref:.2f}')

zz = np.concatenate([-z[::-1], z[1:]])
ref = np.concatenate([I_ref[::-1], I_ref[1:]])
obs = np.concatenate([I_obs[::-1], I_obs[1:]])

fig, axes = plt.subplots(1, 2, figsize=(20.5, 7.0))

ax = axes[0]
ax.plot(zz, ref, '-', color='#999999', lw=2.6,
        label=f'No obstruction, depth of focus {d_ref:.2f} um')
ax.plot(zz, obs, '-', color='#d62728', lw=2.4,
        label=f'Obstruction ratio {EPS:g}, depth of focus {d_obs:.2f} um')
ax.axhline(0.5, color='#555', ls='--', lw=1.4)
for d, c in ((d_ref, '#999999'), (d_obs, '#d62728')):
    ax.annotate('', xy=(-d / 2, 0.5), xytext=(d / 2, 0.5),
                arrowprops=dict(arrowstyle='<->', color=c, lw=2.2))
ax.set_xlim(-1.6 * d_obs, 1.6 * d_obs)
ax.set_ylim(0, 1.05)
ax.set_xlabel('Axial position z (um)')
ax.set_ylabel('Normalized intensity')
ax.set_title(f'(a) Both profiles in absolute units, ratio {d_obs / d_ref:.2f}',
             fontsize=13)
ax.legend(fontsize=11, loc='upper right')
ax.grid(alpha=0.25)

ax = axes[1]
ax.plot(zz / d_ref, ref, '-', color='#999999', lw=2.6, label='No obstruction')
ax.plot(zz / d_ref, obs, '-', color='#d62728', lw=2.4,
        label=f'Obstruction ratio {EPS:g}')
ax.axhline(0.5, color='#555', ls='--', lw=1.4)
ax.set_xlim(-1.6 * d_obs / d_ref, 1.6 * d_obs / d_ref)
ax.set_ylim(0, 1.05)
ax.set_xlabel('Axial position, in unobstructed depths of focus')
ax.set_ylabel('Normalized intensity')
ax.set_title('(b) The same pair on the normalized axial scale',
             fontsize=13)
ax.legend(fontsize=11, loc='upper right')
ax.grid(alpha=0.25)

plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUT, 'panels'), 'fig_gain_reference')
out = os.path.join(OUT, 'fig_gain_reference.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f'Saved → {out}')
