r"""Facing lenses (θ = π): 10-fs pulses against continuous beams. Left half: the total accumulated as the pulses pass the
focus. Right half: the instant the pulse centres meet at the focus (t = 0; I₁·I₂ for 2CE, |E₁ + E₂|⁴ for 2PE). Each half has a
diagram of the lenses with the pulses, the x–z map as contour lines (10-fs pulses in red, 50% thick; continuous beams 50% in
black dashed), the profile along the axis (x = 0) and across it (z = 0). Each curve and map of its own peak.
Fields and excitation from compute() of cambaliza2000_pulse_video.py (all photon pairs, narrow 350-nm level, phase-locked);
the runs are kept in pulses/sweep/profile_10fs_<sig>.npz.

    python scripts/cambaliza2000_pulses_profile_10fs.py [--rerun] -> output/08_two_color/cambaliza2000/pulses/sweep/profiles_pi_10_{2ce,2pe}.png
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Ellipse, FancyArrowPatch

from cambaliza2000_pulse_video import compute, LAMS, NA
from mcdo.twobeam import beam_field
from mcdo.style import apply as _apply_style
from mcdo.cutinset import fig_legend

_apply_style()
matplotlib.rcParams.update({'font.size': 26, 'axes.titlesize': 26, 'axes.labelsize': 26, 'xtick.labelsize': 22,
                            'ytick.labelsize': 22, 'legend.fontsize': 24})
D = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'cambaliza2000', 'pulses', 'sweep')
PULSE, CW, C1, C2 = '#d62728', 'k', '#d62728', '#1f77b4'
LINES = [0.1, 0.2, 0.4, 0.6, 0.8]


def run(sig):
    """Accumulated total and t = 0 maps and axis lines of a 10-fs run, and the continuous beams on the same grids."""
    path = os.path.join(D, f'profile_10fs_{sig}.npz')
    if os.path.exists(path) and '--rerun' not in sys.argv:
        return dict(np.load(path))
    R = compute(10.0, 'pi', sig)
    k0 = int(np.argmin(np.abs(R['tf'])))
    xs, zs, zf = R['xs'], R['zs'], R['zf']
    X, Z = np.meshgrid(xs, zs)
    l1, l2 = LAMS[sig]
    sig_cw = lambda u1, u2: np.abs(u1) ** 2 * np.abs(u2) ** 2 if sig == '2ce' else np.abs(u1 + u2) ** 4
    cw_map = sig_cw(beam_field(X, Z, l1, NA), beam_field(X, Z, l2, NA, theta=np.pi))
    out = dict(xs=xs, zs=zs, zf=zf, t0=R['tf'][k0], tot_map=R['maps']['all'][-1], now_map=R['maps']['P'][k0],
               tot_z=R['line']['all'][-1], now_z=R['line']['P'][k0], cw_map=cw_map, cw_z=R['cw'])
    np.savez(path, **out)
    return out


def diagram(ax, sig, instant):
    """Lenses L1 (top) and L2 (bottom) facing each other, θ = π, z downwards; the two pulses as wave packets on the axis."""
    l1, l2 = (int(round(1000 * v)) for v in LAMS[sig])
    for zl, c, lab in ((-3.0, C1, f'L1, {l1} nm'), (3.0, C2, f'L2, {l2} nm')):
        ax.add_patch(Ellipse((0, zl), 2.6, 0.45, fc='none', ec='k', lw=2))
        for s in (-1, 1):
            ax.plot([s * 1.2, 0], [zl, 0], color=c, lw=1.6, alpha=0.7)
        ax.text(1.55, zl, lab, ha='left', va='center', fontsize=20, color=c)
    s = np.linspace(-0.7, 0.7, 300)
    packet = lambda c0, col, ph: ax.plot(0.45 * np.exp(-(s / 0.28) ** 2) * np.cos(2 * np.pi * s / 0.16 + ph), c0 + s, color=col, lw=2)
    if instant:
        packet(0.0, C1, 0); packet(0.0, C2, np.pi)
    else:
        packet(-1.7, C1, 0); packet(1.7, C2, 0)
        for z0, dz, c in ((-1.7, 1.0, C1), (1.7, -1.0, C2)):
            ax.add_patch(FancyArrowPatch((0.75, z0), (0.75, z0 + dz), arrowstyle='-|>', mutation_scale=22, color=c, lw=2))
    ax.plot(0, 0, 'k+', ms=12, mew=2)
    ax.set_xlim(-2.2, 4.6); ax.set_ylim(3.6, -3.6); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title('Pulse centres at the focus, t = 0' if instant else 'Pulses passing\nthrough the focus', fontsize=22)


def figure(sig):
    R = run(sig)
    xs, zs, zf = R['xs'], R['zs'], R['zf']
    iz = int(np.argmin(np.abs(zs)))
    SIG = sig.upper()
    now = 'I₁·I₂' if sig == '2ce' else '|E₁ + E₂|⁴'
    fig = plt.figure(figsize=(30, 15))
    outer = fig.add_gridspec(1, 2, wspace=0.16)
    for c, (key, head, instant) in enumerate((('tot', f'Total {SIG} accumulated as the pulses pass the focus', False),
                                              ('now', f'{now} at the instant the pulse centres meet at the focus', True))):
        g = outer[c].subgridspec(2, 2, width_ratios=[1, 1.7], height_ratios=[1, 2.4], wspace=0.32, hspace=0.3)
        dg, mp = fig.add_subplot(g[0, 0]), fig.add_subplot(g[1, 0])
        gz = g[:, 1].subgridspec(2, 1, hspace=0.4)
        az, ax = fig.add_subplot(gz[0]), fig.add_subplot(gz[1])
        diagram(dg, sig, instant)
        m, cwm = R[f'{key}_map'], R['cw_map']
        mp.contour(xs, zs, m / m.max(), levels=LINES, colors=PULSE, linewidths=1.0)
        mp.contour(xs, zs, m / m.max(), levels=[0.5], colors=PULSE, linewidths=3.0)
        mp.contour(xs, zs, cwm / cwm.max(), levels=[0.5], colors=CW, linewidths=2.2, linestyles='--')
        mp.set_ylim(3, -3); mp.set_xlabel('x (µm)'); mp.set_ylabel('z (µm)'); mp.set_title('x–z map')
        y = R[f'{key}_z']
        az.plot(zf, R['cw_z'], '--', color=CW, lw=2.4); az.plot(zf, y / y.max(), color=PULSE, lw=2)
        az.set_xlim(zf[0], zf[-1]); az.set_xlabel('z (µm), at x = 0'); az.set_title('Along the axis')
        az.set_ylim(0, 1.08); az.set_ylabel('Normalized to its peak (a.u.)')
        yx, cx = m[iz], cwm[iz]
        ax.plot(xs, cx / cx.max(), '--', color=CW, lw=2.4); ax.plot(xs, yx / yx.max(), color=PULSE, lw=2)
        ax.set_xlim(xs[0], xs[-1]); ax.set_xlabel('x (µm), at z = 0'); ax.set_title('Across the axis')
        ax.set_ylim(0, 1.08); ax.set_ylabel('Normalized to its peak (a.u.)')
        fig.text(0.29 + 0.43 * c, 0.97, head, ha='center', va='bottom', fontsize=28, weight='bold')
    h = [Line2D([], [], color=CW, ls='--', lw=2.4), Line2D([], [], color=PULSE, lw=2),
         Line2D([], [], color=PULSE, lw=1.0), Line2D([], [], color=PULSE, lw=3.0)]
    fig.legend(h, ['continuous beams (50% contour on the map)', '10-fs pulses', '10, 20, 40, 60 and 80% of the peak on the map', '50% of the peak on the map'],
               loc='lower center', bbox_to_anchor=(0.5, -0.04), ncol=4, frameon=False)
    fig.savefig(os.path.join(D, f'profiles_pi_10_{sig}.png'), dpi=200, bbox_inches='tight'); plt.close(fig)
    print(sig, 't of the instant:', float(R['t0']), 'fs')


if __name__ == '__main__':
    for sig in ('2ce', '2pe'):
        figure(sig)
    print('Saved ->', D)
