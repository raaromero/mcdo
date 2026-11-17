r"""Why pulses shorten the 2CE focus with facing lenses, and the check that 100-fs pulses give the continuous-beam 2CE.

Facing lenses (θ = π): pulse 1 passes z at t = z/c and pulse 2 at t = −z/c, so their intensities overlap in time only
near the focus. For Gaussian pulses the overlap at each z is

    G(z) = ∫ I₁(t − z/c) I₂(t + z/c) dt ∝ exp(−8 ln 2 z² / (cτ)²),   FWHM cτ/√2 (4.2 µm at 20 fs),

and the pulsed 2CE along the axis is the continuous-beam profile times G (the 350-nm pairs alone, τ ≥ 20 fs). Crossed
lenses: the overlap along z is √2 cτ wide (8.5 µm at 20 fs), far longer than the focus; collinear lenses: G = 1.
Profiles from the sweep (cambaliza2000_pulses_sweep.py, NA 0.5, air): the total accumulated as the pulses pass the focus.

    python scripts/cambaliza2000_pulses_gate_plot.py
    -> output/08_two_color/cambaliza2000/pulses/sweep/{gate_pi.png, profiles_100fs_2ce.png}
    PANELS=1 python scripts/cambaliza2000_pulses_gate_plot.py
    -> …/sweep/{profiles_100fs_2ce_0_pi.png (θ = 0 and π), profiles_100fs_2ce_pi2.png (θ = π/2)}
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
from cambaliza2000_pulses_profile_10fs import diagram
from mcdo.style import apply as _apply_style

_apply_style()
matplotlib.rcParams.update({'font.size': 26, 'axes.titlesize': 26, 'axes.labelsize': 26, 'xtick.labelsize': 22,
                            'ytick.labelsize': 22, 'legend.fontsize': 22})
D = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'cambaliza2000', 'pulses', 'sweep')
R = np.load(os.path.join(D, 'sweep.npz'))
C = 0.299792458                                                     # µm/fs
TAU_COL = {10: '#e15759', 20: '#f28e2b', 100: '#4e79a7'}
gate = lambda z, tau: np.exp(-8 * np.log(2) * z ** 2 / (C * tau) ** 2)
norm = lambda y: y / y.max()
PANELS = os.environ.get('PANELS')                                   # PANELS=1: the 100-fs profiles, two panels and one

# 1. The overlap in time along the axis, and the product check at 20 fs (skipped with PANELS=1)
if not PANELS:
    z = R['zs']
    cw = norm(R['pi_z_cw'])
    fig = plt.figure(figsize=(24, 8.4))
    g = fig.add_gridspec(1, 3, width_ratios=[0.42, 1, 1], wspace=0.3)
    diagram(fig.add_subplot(g[0]), '2ce', False)
    a, b = fig.add_subplot(g[1]), fig.add_subplot(g[2])
    a.plot(z, cw, '--', color='k', lw=2.4, label='2CE, continuous beams')
    for tau, col in TAU_COL.items():
        a.plot(z, gate(z, tau), color=col, lw=2.8, label=f'{tau} fs')
    a.set_xlim(-5, 5); a.set_ylim(0, 1.05); a.set_xlabel('z (µm), at x = 0'); a.set_ylabel('Normalized to its peak (a.u.)')
    a.set_title('(a) Overlap of the facing pulses in time')
    a.legend(loc='upper center', bbox_to_anchor=(0.5, -0.17), ncol=2, frameon=False, fontsize=18)
    p20 = norm(R['pi_z_20_fin_all'])
    b.plot(z, cw, '--', color='k', lw=2.4, label=f'continuous beams, {fwhm(z, cw):.2f} µm')
    b.plot(z, gate(z, 20), ':', color='#f28e2b', lw=2.8, label=f'overlap, {fwhm(z, gate(z, 20)):.2f} µm')
    b.plot(z, norm(cw * gate(z, 20)), color='0.35', lw=5, alpha=0.45, label=f'product, {fwhm(z, cw * gate(z, 20)):.2f} µm')
    b.plot(z, p20, color='#d62728', lw=2.2, label=f'computed, {fwhm(z, p20):.2f} µm')
    b.set_xlim(-5, 5); b.set_ylim(0, 1.05); b.set_xlabel('z (µm), at x = 0')
    b.set_title('(b) 2CE along the axis, 20 fs')
    b.legend(loc='upper center', bbox_to_anchor=(0.5, -0.17), ncol=2, frameon=False, fontsize=18)
    fig.savefig(os.path.join(D, 'gate_pi.png'), dpi=250, bbox_inches='tight'); plt.close(fig)


# 2. 100-fs pulses against continuous beams, 2CE, the three lens angles
def lenses(ax, th):
    """L1 focusing along +z (z down) and L2 rotated by θ about the focus, L2 on +x at θ = π/2 as in setup_cambaliza.png."""
    for t, col, off in ((0.0, '#d62728', 0.0), (th, '#1f77b4', 0.35 if th == 0 else 0.0)):
        u = np.array([-np.sin(t), np.cos(t)]); n = np.array([u[1], -u[0]]); L = -3 * u
        ax.add_patch(Ellipse(L, 2.6, 0.42, angle=-np.degrees(t), fc='none', ec='k', lw=2))
        for s in (-1, 1):
            ax.plot([L[0] + s * (1.15 - off) * n[0], 0], [L[1] + s * (1.15 - off) * n[1], 0], color=col, lw=2.2)
    ax.plot(0, 0, 'k+', ms=12, mew=2.5)
    ax.set_xlim(-4.5, 4.5); ax.set_ylim(3.5, -3.6); ax.set_aspect('equal'); ax.axis('off')


PANELS_ = (('0', 0.0, 'z', 'θ = 0, along the axis'), ('pi2', np.pi / 2, 'x', 'θ = π/2, across the axis'),
           ('pi', np.pi, 'z', 'θ = π, along the axis'))


def profile(ax, tk, th, cut, ttl, fs=19, ttl_fs=24):
    s = R['zs'] if cut == 'z' else R['xs']
    c, p = norm(R[f'{tk}_{cut}_cw']), norm(R[f'{tk}_{cut}_100_fin_all'])
    ax.plot(s, c, '--', color='k', lw=2.6, label=f'continuous beams, {fwhm(s, c):.2f} µm')
    ax.plot(s, p, color='#4e79a7', lw=2.2, label=f'100-fs pulses, {fwhm(s, p):.2f} µm')
    ax.set_xlim(s[0], s[-1]) if cut == 'z' else ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(0, 1.4); ax.set_xlabel(f'{cut} (µm), at {"x" if cut == "z" else "z"} = 0'); ax.set_title(ttl, fontsize=ttl_fs)
    ax.legend(loc='upper center', frameon=False, fontsize=fs)
    lenses(ax.inset_axes([0.0, 0.42, 0.26, 0.36]), th)


if PANELS:
    # The same profiles at most two panels across, for slides (fonts 32, 28, 24; about 11 × 10 in per panel; 600 DPI).
    # Writes new files and leaves gate_pi.png and profiles_100fs_2ce.png as they are.
    matplotlib.rcParams.update({'font.size': 28, 'axes.titlesize': 32, 'axes.labelsize': 28, 'xtick.labelsize': 24,
                                'ytick.labelsize': 24, 'legend.fontsize': 24, 'figure.dpi': 100})
    for name, keep in (('0_pi', ('0', 'pi')), ('pi2', ('pi2',))):
        sel = [q for q in PANELS_ if q[0] in keep]
        fig, axes = plt.subplots(1, len(sel), figsize=(11 * len(sel), 10), squeeze=False)
        fig.subplots_adjust(wspace=0.15)
        for ax, (tk, th, cut, ttl) in zip(axes[0], sel):
            profile(ax, tk, th, cut, ttl, 24, 32)
        axes[0, 0].set_ylabel('2CE, normalized to its peak (a.u.)')
        fig.savefig(os.path.join(D, f'profiles_100fs_2ce_{name}.png'), dpi=600, bbox_inches='tight'); plt.close(fig)
    print('Saved -> profiles_100fs_2ce_0_pi.png, profiles_100fs_2ce_pi2.png')
    sys.exit()
fig, axes = plt.subplots(1, 3, figsize=(26, 8.0))
fig.subplots_adjust(wspace=0.22)
for ax, (tk, th, cut, ttl) in zip(axes, PANELS_):
    profile(ax, tk, th, cut, ttl)
axes[0].set_ylabel('2CE, normalized to its peak (a.u.)')
fig.savefig(os.path.join(D, 'profiles_100fs_2ce.png'), dpi=250, bbox_inches='tight'); plt.close(fig)
print('Saved -> gate_pi.png, profiles_100fs_2ce.png')
