r"""Figures of the delay sweep (cambaliza2000_pulses_delay.py): how the 2CE peak falls as pulse 2 is delayed.

* delay_facing_vs_na.png   facing lenses (θ = π), along z, τ = 100 fs, Richards–Wolf in air: the peak over the peak at
  no delay against Δt/τ for several NA, with the temporal overlap of the two pulses exp(−2 ln2 Δt²/τ²); and the
  position of the peak against Δt, with the overlap point cΔt/2n of two counter-propagating pulses.
* delay_retained_vs_na.png the peak at Δt = τ against NA, facing lenses along z, for τ = 30, 50, 100 fs (Richards–Wolf,
  air) and for the pupils and inputs at τ = 100 fs.
* delay_fringes_<τ>fs.png  fine grid (0.1 fs), NA 0.5, Richards–Wolf in air, θ = 0 and π/2: the total
  of phase-locked pulses with all photon pairs, and the 350-nm pairs alone (the 2CE signal of Lim & Saloma (2003)).
* delay_fringe_depth_vs_na.png  largest gap between those two curves against NA, τ = 5, 10, 20 fs, θ = π/2 and π.
* delay_polarization_pi2.png  crossed lenses (θ = π/2), cut x, NA 0.5, τ = 5 fs, fine grid: the total 2CE and the
  350-nm pairs against the delay, each panel over its total at Δt = 0, for the polarization perpendicular to the
  plane of the lens axes (rw_air) and in that plane (rw_air_polp).

The 2CE signal is the 350-nm pairs alone (cross) unless the panel says otherwise; for τ ≥ 30 fs it equals the total.
Scalar (paraxial) results are drawn for NA ≤ 0.5.

    python scripts/cambaliza2000_pulses_delay_plot.py  ->  output/08_two_color/cambaliza2000/pulses/delay_sweep/*.png
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo.style import apply as _apply_style
from mcdo.cutinset import place_legend
import cambaliza2000_pulses_delay as P

_apply_style()
matplotlib.rcParams.update({'font.size': 28, 'axes.titlesize': 32, 'axes.labelsize': 28, 'xtick.labelsize': 24,
                            'ytick.labelsize': 24, 'legend.fontsize': 24, 'lines.linewidth': 4})
D = P.ROOT
C = 0.299792458                                                     # µm/fs
DPI = 600
PUPILS = (('rw_air', 'circular pupil, uniform input'), ('rw_air_gauss4', 'Gaussian input, α$_t$ = 4'),
          ('rw_air_eps0.5', 'annular pupil, ε = 0.5'), ('rw_air_eps0.9', 'annular pupil, ε = 0.9'),
          ('rw_air_eps0.99', 'annular pupil, ε = 0.99'))
THETAS = (('0', 'θ = 0, collinear lenses'), ('pi2', 'θ = π/2, crossed lenses'), ('pi', 'θ = π, facing lenses'))


def table(name, grid):
    try:
        return P.load(name, grid)
    except ValueError:                                              # no files yet
        return None


def envelope(x):
    return np.exp(-2 * np.log(2) * x ** 2)


def facing_vs_na(t):
    q = t.query("sig == '2ce' and theta == 'pi' and cut == 'z' and tau == 100")
    nas = [na for na in (0.1, 0.15, 0.2, 0.3, 0.5, 0.9) if na in set(q.na)]
    cols = plt.cm.viridis(np.linspace(0, 0.9, len(nas)))
    fig, (a, b) = plt.subplots(1, 2, figsize=(22, 10))
    x = np.linspace(0, 2, 201)
    a.plot(x, envelope(x), 'k:', lw=4)
    for na, c in zip(nas, cols):
        r = q[q.na == na].sort_values('delay_tau')
        a.plot(r.delay_tau, r.rel_cross, color=c, label=f'NA {na:g}')
        b.plot(r.delay_fs, r.pos_cross, color=c, label=f'NA {na:g}')
    dt = np.linspace(0, 200, 201)
    b.plot(dt, C * dt / 2, 'k--', lw=3, label='cΔt/2')
    b.plot([], [], 'k:', lw=4, label='temporal overlap (left)')
    a.set(xlabel='Delay Δt/τ', ylabel='Peak over the peak at Δt = 0', xlim=(0, 2), ylim=(0, 1.02),
          title='Peak, facing lenses, τ = 100 fs')
    b.set(xlabel='Delay Δt (fs)', ylabel='Position of the peak, z (µm)', xlim=(0, 200), ylim=(0, 30),
          title='Position of the peak along z')
    place_legend(b)                                                 # one legend: the colours are the same in both
    fig.tight_layout()
    fig.savefig(os.path.join(D, 'delay_facing_vs_na.png'), dpi=DPI)
    plt.close(fig)


def retained_vs_na(tabs):
    fig, (a, b) = plt.subplots(1, 2, figsize=(22, 10))
    t = tabs['rw_air']
    for tau, c in zip((30, 50, 100), ('#4e79a7', '#f28e2b', '#e15759')):
        r = t.query("sig == '2ce' and theta == 'pi' and cut == 'z' and tau == @tau and delay_tau == 1").sort_values('na')
        a.plot(r.na, r.rel_cross, 'o-', color=c, ms=10, label=f'τ = {tau} fs')
    a.axhline(envelope(1.0), color='k', ls='--', lw=3, label='temporal overlap')
    a.set(xlabel='NA', ylabel='Peak at Δt = τ over the peak at Δt = 0', ylim=(0, 1.02), title='Facing lenses, along z')
    place_legend(a)
    for (name, lab), c in zip(PUPILS, ('#4e79a7', '#59a14f', '#f28e2b', '#e15759', '#b07aa1')):
        if tabs.get(name) is None:
            continue
        r = tabs[name].query("sig == '2ce' and theta == 'pi' and cut == 'z' and tau == 100 and delay_tau == 1")
        r = r.sort_values('na')
        b.plot(r.na, r.rel_cross, 'o-', color=c, ms=10, label=lab)
    b.axhline(envelope(1.0), color='k', ls='--', lw=3, label='temporal overlap')
    b.set(xlabel='NA', ylabel='Peak at Δt = τ over the peak at Δt = 0', ylim=(0, 1.02),
          title='Pupils and inputs, τ = 100 fs')
    place_legend(b)
    fig.tight_layout()
    fig.savefig(os.path.join(D, 'delay_retained_vs_na.png'), dpi=DPI)
    plt.close(fig)


def fringes(tf, na=0.5):
    for tau in (5, 10, 20):
        fig, axes = plt.subplots(1, 2, figsize=(22, 10), sharey=True)
        for ax, (tk, lab) in zip(axes, THETAS[:2]):                 # facing lenses: the two curves nearly coincide
            cut = 'x' if tk == 'pi2' else 'z'  # noqa: F841 (read by the query string as @cut)
            r = tf.query("sig == '2ce' and theta == @tk and cut == @cut and tau == @tau and na == @na")
            r = r.sort_values('delay_fs')
            ax.plot(r.delay_fs, r.rel_total, color='#4e79a7', lw=2, label='all pairs, phase-locked')
            ax.plot(r.delay_fs, r.rel_cross, color='#e15759', label='350-nm pairs')
            ax.set(xlabel='Delay Δt (fs)', xlim=(0, 2 * tau), title=lab)
            place_legend(ax)
        axes[0].set(ylabel='Peak over the peak at Δt = 0', ylim=(0, None))
        fig.tight_layout()
        fig.savefig(os.path.join(D, f'delay_fringes_{tau}fs.png'), dpi=DPI)
        plt.close(fig)


def fringe_depth(tf):
    fig, axes = plt.subplots(1, 2, figsize=(22, 10), sharey=True)
    for ax, (tk, lab) in zip(axes, THETAS[1:]):                     # collinear lenses: the same depth at all NAs
        cut = 'x' if tk == 'pi2' else 'z'  # noqa: F841 (read by the query string as @cut)
        for tau, c in zip((5, 10, 20), ('#4e79a7', '#f28e2b', '#e15759')):
            g = tf.query("sig == '2ce' and theta == @tk and cut == @cut and tau == @tau")
            dep = g.assign(gap=(g.rel_total - g.rel_cross).abs()).groupby('na').gap.max()
            ax.plot(dep.index, dep.values, 'o-', color=c, ms=10, label=f'τ = {tau} fs')
        ax.set(xlabel='NA', title=lab)
        place_legend(ax)
    axes[0].set(ylabel='Largest gap, all pairs minus 350-nm pairs', ylim=(0, 1))
    fig.tight_layout()
    fig.savefig(os.path.join(D, 'delay_fringe_depth_vs_na.png'), dpi=DPI)
    plt.close(fig)


def polarization(tabs, na=0.5, tau=5):
    """Crossed lenses: total 2CE and 350-nm pairs against the delay for the two polarizations, same y axis."""
    fig, axes = plt.subplots(1, 2, figsize=(22, 10), sharey=True)
    for ax, (name, lab) in zip(axes, (('rw_air', 'Polarization perpendicular\nto the plane of the lens axes'),
                                      ('rw_air_polp', 'Polarization in the plane\nof the lens axes'))):
        r = tabs[name].query("sig == '2ce' and theta == 'pi2' and cut == 'x' and tau == @tau and na == @na")
        r = r.sort_values('delay_fs')
        p0 = float(r.peak_total.iloc[0])                            # total at no delay, this panel
        ax.plot(r.delay_fs, r.peak_total / p0, color='#4e79a7', lw=4, label='total 2CE, phase-locked pulses')
        ax.plot(r.delay_fs, r.peak_cross / p0, color='#e15759', lw=4, label='350-nm pairs')
        ax.set(xlabel='Delay Δt (fs)', xlim=(0, 2 * tau), title=lab)
    axes[0].set(ylabel='Peak over the total at Δt = 0', ylim=(0, 1.25))
    for ax in axes:
        place_legend(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(D, 'delay_polarization_pi2.png'), dpi=DPI)
    plt.close(fig)


def main():
    tabs = {name: table(name, 'coarse') for name, _ in PUPILS}
    if tabs['rw_air'] is not None:
        facing_vs_na(tabs['rw_air'])
        retained_vs_na(tabs)
    tf = table('rw_air', 'fine')
    if tf is not None:
        fringes(tf)
        fringe_depth(tf)
    tp = table('rw_air_polp', 'fine')
    if tf is not None and tp is not None:
        polarization({'rw_air': tf, 'rw_air_polp': tp})


if __name__ == '__main__':
    main()
