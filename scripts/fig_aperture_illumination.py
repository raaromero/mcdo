"""When does Gaussian illumination behave like uniform?

The pupil face for a range of truncation coefficients, with the amplitude that
survives at the aperture edge:

    A(rho) = exp(-alpha rho^2),      edge amplitude = exp(-alpha)

    alpha -> 0   beam much wider than the aperture, so illumination is uniform
    alpha = 1    beam waist equals the aperture radius, 37 per cent at the edge
    alpha >= 4   beam narrower than the aperture, effectively untruncated,
                 about 2 per cent at the edge

The last panel is the useful one for the model: below alpha of about 0.01 the
edge amplitude is within one per cent of uniform, so the apodized calculation
and the uniform one are interchangeable [HB03].

Output: output/02_na_apodization/fig_aperture_illumination.png (+ panels/)
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo.style import apply as _apply_style
_apply_style()

from mcdo.figio import save_panels

ALPHAS = [0.0, 0.1, 1.0, 4.0]
OUTDIR = os.path.join(os.path.dirname(__file__), '..', 'output', '02_na_apodization')

n = 401
x = np.linspace(-1.3, 1.3, n)
X, Y = np.meshgrid(x, x)
R = np.hypot(X, Y)
inside = R <= 1.0

fig = plt.figure(figsize=(20.5, 13.0))
gs = fig.add_gridspec(2, len(ALPHAS), height_ratios=[1.0, 0.95], hspace=0.38)
axes = [fig.add_subplot(gs[0, i]) for i in range(len(ALPHAS))]
ax_edge = fig.add_subplot(gs[1, :])
for ax, a in zip(axes, ALPHAS):
    A = np.exp(-a * R ** 2)
    A = np.where(inside, A, np.nan)                 # outside the stop: no light
    im = ax.imshow(A, extent=[x[0], x[-1], x[0], x[-1]], origin='lower',
                   cmap='inferno', vmin=0.0, vmax=1.0)
    circle = plt.Circle((0, 0), 1.0, fill=False, color='w', ls='--', lw=1.4)
    ax.add_patch(circle)
    edge = np.exp(-a)
    label = 'Uniform' if a == 0 else f'Truncation coefficient {a:g}'
    ax.set_title(f'{label}, edge amplitude {edge:.2f}', fontsize=11)
    ax.set_xlabel('Normalized pupil coordinate')
    ax.set_facecolor('black')
    if ax is axes[0]:
        ax.set_ylabel('Normalized pupil coordinate')
    else:
        ax.set_yticklabels([])
cb = fig.colorbar(im, ax=axes, fraction=0.020, pad=0.02)
cb.set_label('Input amplitude A(ρ)', fontsize=10)

# ── edge amplitude against the truncation coefficient ─────────────────────
a_fine = np.linspace(0, 8.5, 600)
ax_edge.plot(a_fine, np.exp(-a_fine), color='#1f4e79', lw=2.0,
             label='edge amplitude, exp(−α)')
ax_edge.axhline(1.0, color='#2e7d32', ls='--', lw=1.2, label='uniform, edge amplitude 1')
ax_edge.axhline(np.exp(-4), color='#c0504d', ls='--', lw=1.2,
                label='untruncated threshold, about 2 per cent')
ax_edge.axvspan(0, 0.25, color='#2e7d32', alpha=0.14,
                label='effectively uniform, α below 0.25')
ax_edge.axvspan(4, 8.5, color='#c0504d', alpha=0.14,
                label='effectively untruncated, α above 4')
for a in [0.01, 0.1, 0.25, 1.0, 2.0, 4.0]:
    e = np.exp(-a)
    ax_edge.plot(a, e, 'ko', ms=6)
    ax_edge.annotate(f'α={a:g}\n({e:.3f})', xy=(a, e), xytext=(a + 0.35, e + 0.07),
                     fontsize=9, arrowprops=dict(arrowstyle='-', lw=0.8, color='#777'))
ax_edge.set_xlim(0, 8.5); ax_edge.set_ylim(0, 1.12)
ax_edge.set_xlabel('Truncation coefficient α')
ax_edge.set_ylabel('Edge amplitude')
ax_edge.set_title('Edge amplitude against truncation coefficient', fontsize=12)
ax_edge.grid(alpha=0.25)
ax_edge.legend(fontsize=9, loc='upper right')

print('Edge amplitude against truncation coefficient:')
for a in [0.0, 0.001, 0.01, 0.1, 0.5, 1.0, 2.0, 4.0, 8.0]:
    edge = np.exp(-a)
    note = '   within 1 % of uniform' if abs(1 - edge) < 0.01 else ''
    print(f'  alpha={a:>6g}:  edge amplitude {edge:6.3f}{note}')

save_panels(fig, list(axes) + [ax_edge], os.path.join(OUTDIR, 'panels'), 'fig_aperture_illumination')
# the four faces also belong together as one progression
fig.canvas.draw()
bb = axes[0].get_tightbbox(fig.canvas.get_renderer())
for a in axes[1:]:
    bb = bb.union([bb, a.get_tightbbox(fig.canvas.get_renderer())])
bb = bb.transformed(fig.dpi_scale_trans.inverted()).padded(0.15)
os.makedirs(os.path.join(OUTDIR, 'panels'), exist_ok=True)
fig.savefig(os.path.join(OUTDIR, 'panels', 'fig_aperture_illumination_row.png'),
            dpi=300, bbox_inches=bb)
out = os.path.join(OUTDIR, 'fig_aperture_illumination.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f'Saved → {out}')
