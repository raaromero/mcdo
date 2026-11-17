r"""Figures of the pulse-length sweep (cambaliza2000_pulses_sweep.py): widths and strengths against τ, and how the
2CE builds up in time for each τ.

    python scripts/cambaliza2000_pulses_sweep_plot.py
    -> output/08_two_color/cambaliza2000/pulses/sweep/{widths_vs_tau, strength_vs_tau, timeseries_<θ>}.png
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo.style import apply as _apply_style
from mcdo.cutinset import fig_legend, place_legend

_apply_style()
matplotlib.rcParams.update({'font.size': 28, 'axes.titlesize': 30, 'axes.labelsize': 30, 'xtick.labelsize': 26,
                            'ytick.labelsize': 26, 'legend.fontsize': 24})
D = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'cambaliza2000', 'pulses', 'sweep')
R = np.load(os.path.join(D, 'sweep.npz'))
TAUS = R['taus']
PANELS = (('0', 'z', 'collinear lenses (θ = 0), along the axis'),
          ('pi2', 'x', 'crossed lenses (θ = π/2), across the axis'),
          ('pi', 'z', 'facing lenses (θ = π), along the axis'))
COL = plt.cm.viridis(np.linspace(0, 0.9, len(TAUS)))


def fwhm(s, y):
    y = y / y.max()
    i0 = int(np.argmax(y))
    r, l = i0, i0
    while r < len(y) - 1 and y[r] >= 0.5:
        r += 1
    while l > 0 and y[l] >= 0.5:
        l -= 1
    return np.interp(0.5, [y[r], y[r - 1]], [s[r], s[r - 1]]) - np.interp(0.5, [y[l], y[l + 1]], [s[l], s[l + 1]])


def fin(tk, cut, tau, q):
    return R[f'{tk}_{cut}_{tau:g}_fin_{q}']


# 1. Widths against τ
fig, axes = plt.subplots(1, 3, figsize=(24, 8.0))
for ax, (tk, cut, ttl) in zip(axes, PANELS):
    s = R['zs'] if cut == 'z' else R['xs']
    w = {q: np.array([fwhm(s, fin(tk, cut, t, q)) for t in TAUS]) for q in ('all', 'crest', 'mean')}
    ax.axhline(fwhm(s, R[f'{tk}_{cut}_cw']), color='k', ls='--', lw=2.5, label='continuous beams')
    ax.plot(TAUS, w['crest'], 's-', color='#ff7f0e', lw=3, ms=8, label='through the fringe crests')
    ax.plot(TAUS, w['mean'], '^:', color='#6a3d9a', lw=3, ms=8, label='fringes averaged')
    ax.plot(TAUS, w['all'], 'D-', color='#d62728', lw=2, ms=7, label='central fringe')
    ax.set_xscale('log'); ax.set_xticks([5, 10, 20, 50, 100]); ax.set_xticklabels(['5', '10', '20', '50', '100'])
    ax.set_xlabel('Pulse width τ (fs)'); ax.set_title(ttl, fontsize=26)
    ax.set_ylim(0, None)
axes[0].set_ylabel('2CE FWHM (µm)')
h, l = axes[0].get_legend_handles_labels()
fig_legend(fig, h, l)
fig.savefig(os.path.join(D, 'widths_vs_tau.png'), dpi=300, bbox_inches='tight'); plt.close(fig)

# 2. Strength and fringe depth against τ (at the focus they do not depend on θ)
fig, axes = plt.subplots(1, 2, figsize=(18.5, 6.6))
one = np.array([fin('pi', 'z', t, 'one').max() for t in TAUS])
ratio = np.array([fin('pi', 'z', t, 'all').max() for t in TAUS]) / one
same = np.array([fin('pi', 'z', t, 'single').max() for t in TAUS]) / one
crest = np.array([fin('pi', 'z', t, 'crest').max() for t in TAUS])
a, b = np.sqrt(one), np.sqrt(crest) - np.sqrt(one)
dep = 2 * a * b / (a ** 2 + b ** 2)
pos = lambda v: np.where(v > 1e-7, v, np.nan)                   # zero on a log axis: leave out
axes[0].plot(TAUS, pos(ratio - 1), 'o-', color='#d62728', lw=3, ms=9, label='total / 350-nm pairs alone − 1')
axes[0].plot(TAUS, pos(same), 's-', color='#ff7f0e', lw=3, ms=8, label='375- and 328-nm pairs / 350-nm pairs')
axes[0].set_yscale('log'); axes[0].set_ylim(1e-6, 1e3); axes[0].set_ylabel('Ratio of peaks')
axes[0].set_title('Signal added by the 375- and 328-nm pairs', fontsize=26)
axes[1].plot(TAUS, dep, 'o-', color='#6a3d9a', lw=3, ms=9, label='fringe depth')
axes[1].set_ylim(0, 1.05); axes[1].set_ylabel('Fringe depth (0 to 1)')
axes[1].set_title('Depth of the fringes (θ ≠ 0)', fontsize=26)
for ax in axes:
    ax.set_xscale('log'); ax.set_xticks([5, 10, 20, 50, 100]); ax.set_xticklabels(['5', '10', '20', '50', '100'])
    ax.set_xlabel('Pulse width τ (fs)')
h, l = axes[0].get_legend_handles_labels()
fig_legend(fig, h, l)
fig.savefig(os.path.join(D, 'strength_vs_tau.png'), dpi=300, bbox_inches='tight'); plt.close(fig)

# 3. Time series, one figure per θ
for tk, cut, ttl in PANELS:
    ax_lab = f'{cut} (µm)'
    fig, axes = plt.subplots(2, 2, figsize=(18.5, 14.5), sharex=True)
    for c, tau in zip(COL, TAUS):
        g = lambda q: R[f'{tk}_{cut}_{tau:g}_ts_{q}']
        u = g('t') / tau
        on = g('P_peak') > 1e-3 * g('P_peak').max()                  # the pulses overlap somewhere on the cut
        built = g('all_peak') > 0.05 * g('all_peak')[-1]              # once 5% of the final 2CE is reached
        axes[0, 0].plot(u[on], g('P_centre')[on], color=c, lw=2.5, label=f'{tau:g} fs')
        axes[0, 1].plot(u[on], g('P_fwhm')[on], color=c, lw=2.5)
        axes[1, 0].plot(u[built], g('crest_fwhm')[built], color=c, lw=2.5)
        axes[1, 1].plot(u, g('all_peak') / g('all_peak')[-1], color=c, lw=2.5)
    axes[0, 0].set_ylabel(f'Centre of I₁·I₂, {ax_lab}'); axes[0, 0].set_title('Where the pulses overlap now (I₁·I₂)', fontsize=26)
    axes[0, 1].set_ylabel(f'FWHM of I₁·I₂, {ax_lab}'); axes[0, 1].set_title('Width of the overlap now', fontsize=26)
    axes[1, 0].set_ylabel(f'FWHM of |A(t)|², {ax_lab}'); axes[1, 0].set_title('Width of the cumulative 2CE (fringe crests)', fontsize=26)
    axes[1, 1].set_ylabel('Peak |A(t)|² / total (ratio)'); axes[1, 1].set_title('Cumulative 2CE at its peak', fontsize=26)
    for ax in axes[1]:
        ax.set_xlabel('Time t / τ')
    for ax in axes.ravel():
        ax.set_xlim(-1.6, 1.6)
    half = 5.0 if cut == 'z' else 1.5
    axes[0, 0].set_ylim(-half, half); axes[0, 1].set_ylim(0, None); axes[1, 0].set_ylim(0, None)
    h, l = axes[0, 0].get_legend_handles_labels()
    leg = fig_legend(fig, h, l, title='τ', title_fontsize=24)
    fig.canvas.draw()
    top = max(leg.get_window_extent().transformed(fig.transFigure.inverted()).y1,
              max(a.get_tightbbox().transformed(fig.transFigure.inverted()).y1 for a in axes[0]))
    fig.suptitle(ttl, fontsize=30, y=top + 0.005, va='bottom')        # above the legend, never on it
    fig.savefig(os.path.join(D, f'timeseries_{tk}.png'), dpi=200, bbox_inches='tight'); plt.close(fig)
print('Saved ->', D)

# 4. Facing lenses: 2CE and 2PE depth of focus against τ (fringe crests: the envelope through the fringe maxima)
fig, ax = plt.subplots(figsize=(18.5, 6.8))
for pre, col, lab in (('', '#f28e2b', '2CE'), ('pe_', '#4e79a7', '2PE')):
    w = [fwhm(R['zs'], R[f'{pre}pi_z_{t:g}_fin_crest']) for t in TAUS]
    ax.plot(TAUS, w, 'o-', color=col, lw=3.5, ms=10, label=lab)
ax.axhline(fwhm(R['zs'], R['pi_z_cw']), color='k', ls='--', lw=2.5, label='continuous beams (2CE and 2PE)')   # equal within 0.3%
ax.set_xscale('log'); ax.set_xticks([5, 10, 20, 50, 100]); ax.set_xticklabels(['5', '10', '20', '50', '100'])
ax.set_xlabel('Pulse width τ (fs)'); ax.set_ylabel('Depth of focus (µm)'); ax.set_ylim(0, 4.2)
ax.legend(loc='lower right', frameon=False)
fig.savefig(os.path.join(D, 'dof_2ce_2pe_pi.png'), dpi=300, bbox_inches='tight'); plt.close(fig)

# 5. Collinear and crossed lenses: 2CE widths against τ (along the axis at θ = 0, across at θ = π/2)
fig, axes = plt.subplots(1, 2, figsize=(18.5, 6.6))
for ax, (tk, cut, ttl) in zip(axes, PANELS[:2]):
    s = R['zs'] if cut == 'z' else R['xs']
    ax.axhline(fwhm(s, R[f'{tk}_{cut}_cw']), color='k', ls='--', lw=2.5, label='continuous beams')
    ax.plot(TAUS, [fwhm(s, fin(tk, cut, t, 'crest')) for t in TAUS], 'o-', color='#d62728', lw=3, ms=9, label='pulses, through the fringe crests')
    ax.set_xscale('log'); ax.set_xticks([5, 10, 20, 50, 100]); ax.set_xticklabels(['5', '10', '20', '50', '100'])
    ax.set_xlabel('Pulse width τ (fs)'); ax.set_title(ttl, fontsize=26); ax.set_ylim(0, 1.12 * fwhm(s, R[f'{tk}_{cut}_cw']))
axes[0].set_ylabel('2CE FWHM (µm)')
h, l = axes[1].get_legend_handles_labels()
fig_legend(fig, h, l)
fig.savefig(os.path.join(D, 'widths_0_pi2.png'), dpi=300, bbox_inches='tight'); plt.close(fig)
print('Saved -> dof_2ce_2pe_pi.png, widths_0_pi2.png')
