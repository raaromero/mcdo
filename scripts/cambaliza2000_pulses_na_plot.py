r"""Depth of focus against pulse width at NA 0.3, 0.4 and 0.5, for collinear, crossed and facing lenses, 2CE and 2PE
(paraxial scalar, air, zero delay; sweeps of cambaliza2000_pulses_sweep.py with --na). Depth of focus = FWHM along the
axis (x = 0) of the total accumulated as the pulses pass the focus, through the fringe crests. Continuous beams as
dashed lines of the same colour: I₁I₂ for 2CE and, for 2PE, its envelope through the fringe crests, (|U₁| + |U₂|)⁴
(the 2PE fringes along z are 350 nm apart at θ = π and 700 nm at θ = π/2). Top row: the lens arrangement of each column.

    python scripts/cambaliza2000_pulses_na_plot.py -> output/08_two_color/cambaliza2000/pulses/sweep/{dof_na, dof_na_pi, dof_na_0_pi2}.png
    (all angles; facing lenses for a slide; collinear and crossed lenses, pulses over continuous beams, for a slide)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

from cambaliza2000_pulses_sweep import fwhm
from mcdo.twobeam import beam_field
from mcdo.style import apply as _apply_style

_apply_style()
matplotlib.rcParams.update({'font.size': 28, 'axes.titlesize': 28, 'axes.labelsize': 28, 'xtick.labelsize': 26,
                            'ytick.labelsize': 26, 'legend.fontsize': 26})
D = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'cambaliza2000', 'pulses', 'sweep')
NAS = {0.3: '#e15759', 0.4: '#f28e2b', 0.5: '#4e79a7'}
ANG = (('0', 0.0, 'Collinear lenses, θ = 0'), ('pi2', np.pi / 2, 'Crossed lenses, θ = π/2'), ('pi', np.pi, 'Facing lenses, θ = π'))
R = {na: np.load(os.path.join(D, 'sweep.npz' if na == 0.5 else f'sweep_na{na:g}.npz')) for na in NAS}
C1, C2 = '#d62728', '#1f77b4'


def lenses(ax, th, ttl):
    """L1 focusing along +z (z down) and L2 rotated by θ about the focus."""
    for t, c, off in ((0.0, C1, 0.0), (th, C2, 0.35 if th == 0 else 0.0)):
        a = np.array([-np.sin(t), np.cos(t)]); n = np.array([a[1], -a[0]]); L = -3 * a      # L2 on +x at θ = π/2, as in setup_cambaliza.png
        ax.add_patch(Ellipse(L, 2.6, 0.42, angle=-np.degrees(t), fc='none', ec='k', lw=2))
        for s in (-1, 1):
            ax.plot([L[0] + s * (1.15 - off) * n[0], 0], [L[1] + s * (1.15 - off) * n[1], 0], color=c, lw=2.2)
    ax.plot(0, 0, 'k+', ms=14, mew=2.5)
    ax.set_xlim(-4.5, 4.5); ax.set_ylim(3.5, -3.6); ax.set_aspect('equal'); ax.axis('off'); ax.set_title(ttl)


def cw_dof(r, tk, th, sig, na):
    if sig == '2CE':
        return fwhm(r['zs'], r[f'{tk}_z_cw'])
    z = r['zs']
    u1, u2 = beam_field(0 * z, z, 0.700, na), beam_field(0 * z, z, 0.700, na, theta=th)
    return fwhm(z, (np.abs(u1) + np.abs(u2)) ** 4)


fig = plt.figure(figsize=(30, 22))
g = fig.add_gridspec(3, 3, height_ratios=[0.55, 1, 1], hspace=0.38, wspace=0.24)
out = []
for c, (tk, th, ttl) in enumerate(ANG):
    lenses(fig.add_subplot(g[0, c]), th, ttl)
    for rw, (pre, sig) in enumerate((('', '2CE'), ('pe_', '2PE')), start=1):
        ax = fig.add_subplot(g[rw, c])
        top = 0
        for na, col in NAS.items():
            r = R[na]
            taus = r['taus']
            cw = cw_dof(r, tk, th, sig, na)
            w = [fwhm(r['zs'], r[f'{pre}{tk}_z_{t:g}_fin_crest']) for t in taus]
            ax.axhline(cw, color=col, ls='--', lw=2.2)
            ax.plot(taus, w, 'o-', color=col, lw=3, ms=9)
            top = max(top, cw, *w)
            out.append(f'{sig} {tk:3s} NA {na}: continuous {cw:.2f} µm; ' + ', '.join(f'{t:g} fs {v / cw:.2f}' for t, v in zip(taus, w)))
        ax.set_xscale('log'); ax.set_xticks([5, 10, 20, 50, 100]); ax.set_xticklabels(['5', '10', '20', '50', '100'])
        ax.set_xlabel('Pulse width τ (fs)'); ax.set_ylim(0, 1.12 * top); ax.set_title(sig)
        if c == 0:
            ax.set_ylabel('Depth of focus (µm)')
h = [plt.Line2D([], [], color=c, lw=6) for c in NAS.values()] + [plt.Line2D([], [], color='k', marker='o', ms=9, lw=3),
                                                                plt.Line2D([], [], color='k', ls='--', lw=2.2)]
l = [f'NA {na:g}' for na in NAS] + ['pulses', 'continuous beams']
fig.legend(h, l, loc='lower center', bbox_to_anchor=(0.5, 0.0), ncol=5, frameon=False)
fig.savefig(os.path.join(D, 'dof_na.png'), dpi=200, bbox_inches='tight'); plt.close(fig)
print('\n'.join(out))

# For the slides, one figure per message (panels large enough to read on a slide).
# (1) Facing lenses: depth of focus in µm, 2CE and 2PE, with the pulses on their way to the focus.
from cambaliza2000_pulses_profile_10fs import diagram                # noqa: E402
fig = plt.figure(figsize=(22, 8.2))
g = fig.add_gridspec(1, 2, width_ratios=[0.42, 2], wspace=0.34)
diagram(fig.add_subplot(g[0]), '2ce', False)
gp = g[1].subgridspec(1, 2, wspace=0.18)
axes = [fig.add_subplot(gp[0]), fig.add_subplot(gp[1])]
for ax, (pre, sig) in zip(axes, (('', '2CE'), ('pe_', '2PE'))):
    for na, col in NAS.items():
        r = R[na]
        ax.axhline(cw_dof(r, 'pi', np.pi, sig, na), color=col, ls='--', lw=2.2)
        ax.plot(r['taus'], [fwhm(r['zs'], r[f'{pre}pi_z_{t:g}_fin_crest']) for t in r['taus']], 'o-', color=col, lw=3, ms=9)
    ax.set_xscale('log'); ax.set_xticks([5, 10, 20, 50, 100]); ax.set_xticklabels(['5', '10', '20', '50', '100'])
    ax.set_xlabel('Pulse width τ (fs)'); ax.set_title(f'{sig}, facing lenses (θ = π)'); ax.set_ylim(0, 11)
axes[0].set_ylabel('Depth of focus (µm)')
fig.legend(h, l, loc='lower center', bbox_to_anchor=(0.6, 0.95), ncol=5, frameon=False)
fig.savefig(os.path.join(D, 'dof_na_pi.png'), dpi=250, bbox_inches='tight'); plt.close(fig)

# (2) Collinear and crossed lenses: depth of focus of the pulses over that of continuous beams, 2CE and 2PE.
fig, axes = plt.subplots(1, 2, figsize=(20, 8.2))
fig.subplots_adjust(wspace=0.2)
for ax, (tk, th, ttl) in zip(axes, ANG[:2]):
    for na, col in NAS.items():
        r = R[na]
        for pre, sig, ls, mk in (('', '2CE', '-', 'o'), ('pe_', '2PE', '--', 's')):
            cw = cw_dof(r, tk, th, sig, na)
            ax.plot(r['taus'], [fwhm(r['zs'], r[f'{pre}{tk}_z_{t:g}_fin_crest']) / cw for t in r['taus']], ls, marker=mk,
                    color=col, lw=3, ms=9)
    ax.axhline(1, color='k', lw=1.2, ls=':')
    ax.set_xscale('log'); ax.set_xticks([5, 10, 20, 50, 100]); ax.set_xticklabels(['5', '10', '20', '50', '100'])
    ax.set_xlabel('Pulse width τ (fs)'); ax.set_title(ttl); ax.set_ylim(0.85, 1.15)
    ins = ax.inset_axes([0.62, 0.03, 0.36, 0.36])
    lenses(ins, th, ''); ins.set_title('')
axes[0].set_ylabel('DOF pulsed / DOF continuous (ratio)')
h2 = [plt.Line2D([], [], color=c, lw=6) for c in NAS.values()] + [plt.Line2D([], [], color='k', marker='o', ms=9, lw=3),
                                                                 plt.Line2D([], [], color='k', marker='s', ms=9, lw=3, ls='--')]
fig.legend(h2, [f'NA {na:g}' for na in NAS] + ['2CE', '2PE'], loc='lower center', bbox_to_anchor=(0.5, 0.93), ncol=5, frameon=False)
fig.savefig(os.path.join(D, 'dof_na_0_pi2.png'), dpi=250, bbox_inches='tight'); plt.close(fig)
print('Saved -> dof_na.png, dof_na_pi.png, dof_na_0_pi2.png')
