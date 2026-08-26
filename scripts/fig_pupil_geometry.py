"""Annular pupil geometry — what the obstruction ratio means, and how much of
the input each ring actually transmits.

    ε = r_inner / r_outer            (0 = full disk, →1 = thin ring)

Panels (also saved individually to output/03_annular/panels/):
  p1 — pupil face for ε = 0, 0.3, 0.5, 0.7, 0.9
  p2 — uniform input across the pupil, blocked against transmitted
  p3 — Gaussian input, moderate obstruction
  p4 — Gaussian input, thin ring

The Gaussian panels are the point: the obstruction removes the centre of the
pupil, which is exactly where a Gaussian keeps its light, so the same ε costs a
Gaussian far more power than it costs a uniform pupil.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo.style import apply as _apply_style
_apply_style()
from matplotlib.patches import Circle

from mcdo.figio import save_panels

EPS = [0.0, 0.3, 0.5, 0.7, 0.9]
ALPHA_T = 4.0
OUTDIR = os.path.join(os.path.dirname(__file__), '..', 'output', '03_annular')
RING = '#2E9BE0'
BLOCKED = '#E8736A'
PASSED = '#57B87A'
TZ = np.trapezoid if hasattr(np, 'trapezoid') else np.trapz

fig = plt.figure(figsize=(20.5, 13.0))
gs = fig.add_gridspec(2, 2, hspace=0.42, wspace=0.26)
ax_ring = fig.add_subplot(gs[0, :])
ax_uni = fig.add_subplot(gs[1, 0])
ax_gau = fig.add_subplot(gs[1, 1])


def transmitted(rho, amp, eps):
    """Power fraction passing a ring of obstruction ratio eps (pupil area weight)."""
    keep = rho >= eps
    return TZ(amp[keep] ** 2 * rho[keep], rho[keep]) / TZ(amp ** 2 * rho, rho)


# ── p1: the pupil face ────────────────────────────────────────────────────
ax_ring.set_aspect('equal')
step = 2.6
for i, e in enumerate(EPS):
    cx = i * step
    ax_ring.add_patch(Circle((cx, 0), 1.0, facecolor=RING, edgecolor='k', lw=1.2, zorder=1))
    if e > 0:
        ax_ring.add_patch(Circle((cx, 0), e, facecolor='white', edgecolor='k', lw=1.2, zorder=2))
        # inner-radius arrow, drawn below the centre so it never crosses a label
        ax_ring.annotate('', xy=(cx - e, 0.0), xytext=(cx, 0.0),
                         arrowprops=dict(arrowstyle='<->', lw=1.1, color='k'), zorder=3)
        ax_ring.text(cx - e / 2, 0.10, r'$r_{\mathrm{in}}$', ha='center', va='bottom',
                     fontsize=11, zorder=3)
    ax_ring.text(cx, -1.55, f'ε = {e:g}', ha='center', fontsize=13)
# outer radius marked once, on the first pupil
ax_ring.annotate('', xy=(0, 1.0), xytext=(0, 0),
                 arrowprops=dict(arrowstyle='<->', lw=1.1, color='k'), zorder=3)
ax_ring.text(0.10, 0.52, r'$r_{\mathrm{out}}$', fontsize=11, zorder=3)
ax_ring.set_xlim(-1.5, (len(EPS) - 1) * step + 1.5)
ax_ring.set_ylim(-2.0, 1.4)
ax_ring.axis('off')
ax_ring.set_title('(a) Annular pupil geometry', fontsize=12)

# ── p2 / p3 / p4: what the ring transmits ─────────────────────────────────
rho = np.linspace(-1.35, 1.35, 900)
a_rho = np.abs(rho)
rho_pos = np.linspace(0, 1, 600)


def truncation_panel(ax, amp, amp_pos, eps, title):
    inside = a_rho <= 1.0
    blocked = inside & (a_rho < eps)
    passed = inside & (a_rho >= eps)
    ax.plot(rho, amp, color='#1f4e79', lw=2.0, zorder=3)
    ax.fill_between(rho, 0, amp, where=blocked, color=BLOCKED, alpha=0.75,
                    label='blocked by the central stop', zorder=2)
    ax.fill_between(rho, 0, amp, where=passed, color=PASSED, alpha=0.75,
                    label='transmitted by the ring', zorder=2)
    for x in (-1.0, 1.0):
        ax.axvline(x, color='k', ls='--', lw=1.2, zorder=4)
    if eps > 0:
        for x in (-eps, eps):
            ax.axvline(x, color=BLOCKED, ls='--', lw=1.2, zorder=4)
    frac = transmitted(rho_pos, amp_pos, eps)
    ax.text(0.5, 0.06, f'{frac * 100:.0f} % of the power transmitted',
            transform=ax.transAxes, ha='center', fontsize=11, color='#1f4e79',
            bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='#ccc', alpha=0.9))
    ax.set_xlim(-1.35, 1.35); ax.set_ylim(0, 1.15)
    ax.set_xlabel('Normalized pupil radius ρ')
    ax.set_ylabel('Input amplitude A(ρ)')
    ax.set_title(title, fontsize=12)
    ax.grid(alpha=0.22)
    ax.legend(fontsize=9, loc='upper left', frameon=True)


truncation_panel(ax_uni, np.ones_like(rho), np.ones_like(rho_pos), 0.5,
                 '(b) Uniform input, obstruction ratio 0.5')
truncation_panel(ax_gau, np.exp(-ALPHA_T * rho ** 2), np.exp(-ALPHA_T * rho_pos ** 2), 0.5,
                 f'(c) Gaussian input, truncation coefficient {ALPHA_T:g}, obstruction ratio 0.5')

print('Power transmitted by the ring:')
for e in EPS:
    p_u = transmitted(rho_pos, np.ones_like(rho_pos), e)
    p_g = transmitted(rho_pos, np.exp(-ALPHA_T * rho_pos ** 2), e)
    print(f'  eps={e:4g}:  uniform {p_u * 100:5.1f} %   '
          f'Gaussian (coefficient {ALPHA_T:g}) {p_g * 100:5.1f} %')

plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUTDIR, 'panels'), 'fig_pupil_geometry')
out = os.path.join(OUTDIR, 'fig_pupil_geometry.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f'Saved → {out}')
