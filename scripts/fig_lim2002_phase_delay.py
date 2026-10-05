r"""Lim & Saloma (2002) with a time delay between continuous beams.

Delaying a continuous beam by Δt multiplies its field by exp(iωΔt): a phase
φ = ωΔt between the two beams. One optical period (2.33 fs at 700 nm) covers
φ = 0 to 2π.

  2PE: |U_1 + U_2 e^{iφ}|^4, both beams at 700 nm: the fringes move with φ.
  2CE: I_1 |U_2 e^{iφ}|^2 = I_1 I_2: unchanged by φ (computed to show it).

Paraxial scalar focus, NA 0.5, air, aligned foci, on the window of the paper
(x within ±1 µm, z within ±5 µm). For each φ: the peak lost (max over the window
against φ = 0) and Linfoot's fidelity F against the φ = 0 PSF, each scaled to
its own peak, as in Figs. 5–6.

    python scripts/fig_lim2002_phase_delay.py
    -> output/08_two_color/lim2002/phase_delay/phase_delay.{csv,png}
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
matplotlib.rcParams.update({'font.size': 24, 'axes.titlesize': 32, 'axes.labelsize': 28,
                            'xtick.labelsize': 24, 'ytick.labelsize': 24, 'legend.fontsize': 24})

from mcdo.linfoot import fidelity
from mcdo.twobeam import beam_field

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002', 'phase_delay')
os.makedirs(OUT, exist_ok=True)
NA, L1, L2, L2P = 0.5, 0.750, 0.656, 0.700
X, Z = np.meshgrid(np.linspace(-1, 1, 201), np.linspace(-5, 5, 501))     # window of the paper, for F
XP, ZP = np.meshgrid(np.linspace(-0.4, 0.4, 161), np.linspace(-1.0, 1.0, 1001))  # fine grid near the focus, for the peak:
PHI = np.linspace(0, 2 * np.pi, 73)                         # the fringes (0.35 µm) must be sampled finely or the peak jitters

PART = os.environ.get('PART', 'all')                       # 'phase', 'space' or 'all'
if PART in ('all', 'phase'):
    rows = []
    for th, lab in ((np.pi, 'pi'), (np.pi / 2, 'pi2')):
        def sigs(XX, ZZ):
            U1, U2 = beam_field(XX, ZZ, L2P, NA, theta=0.0), beam_field(XX, ZZ, L2P, NA, theta=th)
            V1, V2 = beam_field(XX, ZZ, L1, NA, theta=0.0), beam_field(XX, ZZ, L2, NA, theta=th)
            return (('2pe', lambda f: np.abs(U1 + U2 * np.exp(1j * f)) ** 4),
                    ('2ce', lambda f: np.abs(V1) ** 2 * np.abs(V2 * np.exp(1j * f)) ** 2))
        for (name, sig), (_, sigp) in zip(sigs(X, Z), sigs(XP, ZP)):
            ref, refp = sig(0.0), sigp(0.0)
            for f in PHI:
                s, sp = sig(f), sigp(f)
                rows.append((name, lab, f, 100 * (1 - sp.max() / refp.max()), fidelity(ref / ref.max(), s / s.max())))

    with open(os.path.join(OUT, 'phase_delay.csv'), 'w') as fh:
        fh.write('# signal,theta,phi_rad,peak_lost_pct,F\n')
        for r in rows:
            fh.write(f'{r[0]},{r[1]},{r[2]:.6f},{r[3]:.6f},{r[4]:.6f}\n')

    fig, axes = plt.subplots(1, 2, figsize=(16.4, 6.8))
    STY = {('2pe', 'pi'): ('2PE, θ = π', '#1f77b4', '-'), ('2pe', 'pi2'): ('2PE, θ = π/2', '#d62728', '-'),
           ('2ce', 'pi'): ('2CE, θ = π and π/2', 'k', '--')}
    for (name, lab), (txt, c, ls) in STY.items():
        r = np.array([(f, pl, F) for n_, l_, f, pl, F in rows if n_ == name and l_ == lab])
        axes[0].plot(r[:, 0] / np.pi, r[:, 1], ls, color=c, lw=4, label=txt)
        axes[1].plot(r[:, 0] / np.pi, r[:, 2], ls, color=c, lw=4)
    axes[0].set_ylabel('Peak lost (%)'); axes[1].set_ylabel('Fidelity F')
    for ax in axes:
        ax.set_xlabel('Phase φ = ωΔt (π)'); ax.set_xlim(0, 2); ax.set_xticks([0, 0.5, 1, 1.5, 2])
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc='lower center', ncol=3, bbox_to_anchor=(0.5, -0.12), frameon=False)
    plt.tight_layout()
    fig.savefig(os.path.join(OUT, 'phase_delay.png'), dpi=600, bbox_inches='tight')

    for name, lab in (('2pe', 'pi'), ('2pe', 'pi2'), ('2ce', 'pi'), ('2ce', 'pi2')):
        for f in (np.pi / 2, np.pi):
            r = next(x for x in rows if x[0] == name and x[1] == lab and np.isclose(x[2], f))
            print(f'{name} θ={lab:3s} φ={f / np.pi:.1f}π: peak lost {r[3]:6.2f}%  F {r[4]:+.3f}')
    print('Saved ->', OUT)


# ── delay in time against misalignment in space, 2PE, θ = π/2 ──
# A delay Δt is a phase ωΔt; it shifts the fringes by cΔt / (2n sin(θ/2)) along K. At θ = π/2 that is
# the same fringe phase as moving O′ by x_c = cΔt/n along beam 2, or by z_c = cΔt/n along beam 1.
if PART in ('all', 'space'):
    C = 0.299792458                                            # µm/fs
    T = L2P / C                                                 # one optical period at 700 nm (fs)
    Xs, Zs = np.meshgrid(np.linspace(-1, 1, 101), np.linspace(-5, 5, 251))   # coarser: one beam 2 per misalignment
    U1, U0 = beam_field(Xs, Zs, L2P, NA, theta=0.0), beam_field(Xs, Zs, L2P, NA, theta=np.pi / 2)
    ref = (np.abs(U1 + U0) ** 4).max()
    PHS = np.linspace(0, 2 * np.pi, 41)
    dts = PHS / (2 * np.pi) * T
    ds = C * dts                                                # equivalent misalignment cΔt/n, n = 1 (µm)
    if os.environ.get('REPLOT') == '1':                          # redraw from the saved losses
        _, _, lost_t, lost_x, lost_z = np.loadtxt(os.path.join(OUT, 'time_vs_space.csv'), delimiter=',').T
    else:
        lost_t = [100 * (1 - (np.abs(U1 + U0 * np.exp(1j * f)) ** 4).max() / ref) for f in PHS]
        lost_x = [100 * (1 - (np.abs(U1 + beam_field(Xs, Zs, L2P, NA, theta=np.pi / 2, xc=d)) ** 4).max() / ref) for d in ds]
        lost_z = [100 * (1 - (np.abs(U1 + beam_field(Xs, Zs, L2P, NA, theta=np.pi / 2, zc=d)) ** 4).max() / ref) for d in ds]
    with open(os.path.join(OUT, 'time_vs_space.csv'), 'w') as fh:
        fh.write('# dt_fs,equivalent_offset_um,lost_delay_pct,lost_xc_pct,lost_zc_pct\n')
        for r in zip(dts, ds, lost_t, lost_x, lost_z):
            fh.write(','.join(f'{v:.6f}' for v in r) + '\n')

    s_ = PHS / (2 * np.pi)                                      # Δt/T = misalignment/λ_2p: one shared axis
    fig, ax = plt.subplots(figsize=(16.0, 7.6))
    ax.plot(s_, lost_t, '-', color='#1f77b4', lw=4, label='Delay Δt, foci aligned')
    ax.plot(s_, lost_x, '--', color='#d62728', lw=4, label='Misalignment x$_c$, no delay')
    ax.plot(s_, lost_z, ':', color='#2ca02c', lw=4, label='Misalignment z$_c$, no delay')
    for f in (0.25, 0.5, 0.75):
        ax.axvline(f, color='#999999', lw=1.5)
    ax.set_xlim(0, 1); ax.set_ylim(0, 35)
    ax.set_xlabel('Δt / T  =  x$_c$ / λ$_{2p}$  =  z$_c$ / λ$_{2p}$        (T = 2.33 fs, λ$_{2p}$ = 0.70 µm)')
    ax.set_ylabel('2PE peak lost (%)')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=3, frameon=False)
    plt.tight_layout()
    fig.savefig(os.path.join(OUT, 'time_vs_space.png'), dpi=600, bbox_inches='tight')
    i = np.argmin(np.abs(PHS - np.pi))
    print(f'φ = π (Δt = {dts[i]:.3f} fs, cΔt/n = {ds[i]:.3f} µm): delay {lost_t[i]:.1f}%, x_c {lost_x[i]:.1f}%, z_c {lost_z[i]:.1f}%')
