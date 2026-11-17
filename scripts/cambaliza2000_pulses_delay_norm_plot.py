r"""Figures of the normalized-delay sweep (cambaliza2000_pulses_delay_norm.py), facing lenses (θ = π) and all angles.

delay_pi.png: peak of the total 2CE and 2PE against N (path difference in wavelengths of 700 nm), and where the
2CE sits along the axis (centroid) against N, with the meeting point of the pulses z = Nλ₀/2n.
delay_angles.png: 2CE peak against N at θ = 0, π/2, π (20 fs).
delay_profiles_pi.png: total 2CE along the axis at N = 0, 4, 8, 12 (20 fs).

    python scripts/cambaliza2000_pulses_delay_norm_plot.py -> output/08_two_color/cambaliza2000/pulses/delay_norm/*.png
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo.style import apply as _apply_style
from mcdo.cutinset import fig_legend

_apply_style()
matplotlib.rcParams.update({'font.size': 28, 'axes.titlesize': 28, 'axes.labelsize': 28, 'xtick.labelsize': 26,
                            'ytick.labelsize': 26, 'legend.fontsize': 24})
D = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'cambaliza2000', 'pulses', 'delay_norm')
R = np.load(os.path.join(D, 'delay_norm.npz'))
NS, Z = R['ns'], R['zs']
COL = {10: '#e15759', 20: '#f28e2b', 100: '#4e79a7'}

fig, axes = plt.subplots(1, 2, figsize=(18.5, 6.8))
for tau in (10, 20, 100):
    for sig, ls, mk in (('2ce', '-', 'o'), ('2pe', '--', 's')):
        pk = R[f'{sig}_pi_{tau}_all'].max(1)
        axes[0].plot(NS, pk / pk.max(), ls, marker=mk, ms=6, color=COL[tau], lw=2.5, label=f'{sig.upper()}, {tau} fs')
    A = R[f'2ce_pi_{tau}_all']
    axes[1].plot(NS, (A * Z).sum(1) / A.sum(1), '-o', ms=6, color=COL[tau], lw=2.5)
axes[1].plot(NS, NS * 0.700 / 2, 'k:', lw=2.5, label='meeting point Nλ₀/2')
axes[0].set_ylabel('Peak, N / N = 0 (ratio)'); axes[0].set_ylim(0, 1.08)
axes[1].set_ylabel('2CE centre along z (µm)')
for ax in axes:
    ax.set_xlabel('Path difference N (λ₀ = 700 nm)')
h0, l0 = axes[0].get_legend_handles_labels(); h1, l1 = axes[1].get_legend_handles_labels()
fig_legend(fig, h0 + h1, l0 + l1)
fig.savefig(os.path.join(D, 'delay_pi.png'), dpi=300, bbox_inches='tight'); plt.close(fig)

fig, ax = plt.subplots(figsize=(18.5, 6.8))
for tk, lab, c in (('0', 'θ = 0', '#59a14f'), ('pi2', 'θ = π/2', '#b07aa1'), ('pi', 'θ = π', '#4e79a7')):
    pk = R[f'2ce_{tk}_20_all'].max(1)
    ax.plot(NS, pk / pk.max(), '-o', ms=7 if tk != 'pi2' else 4, lw=3 if tk != 'pi2' else 1.6, color=c, label=lab)
ax.set_xlabel('Path difference N (λ₀ = 700 nm)'); ax.set_ylabel('2CE peak at 20 fs, N / N = 0 (ratio)'); ax.set_ylim(0, 1.08)
ax.legend(loc='upper left', frameon=False)   # θ = 0 and π/2 coincide
fig.savefig(os.path.join(D, 'delay_angles.png'), dpi=300, bbox_inches='tight'); plt.close(fig)

fig, ax = plt.subplots(figsize=(18.5, 6.8))
A = R['2ce_pi_20_all']
for n, c in zip((0, 4, 8, 12), ('#1f1f1f', '#4e79a7', '#f28e2b', '#e15759')):
    i = int(np.argmin(np.abs(NS - n)))
    ax.plot(Z, A[i] / A[NS == 0].max(), color=c, lw=3, label=f'N = {n}')
ax.set_xlabel('z (µm), at x = 0'); ax.set_ylabel('2CE at 20 fs, normalized to the N = 0 peak (a.u.)'); ax.set_xlim(-5, 5); ax.set_ylim(0, 1.1)
ax.legend(loc='upper left', frameon=False)
fig.savefig(os.path.join(D, 'delay_profiles_pi.png'), dpi=300, bbox_inches='tight'); plt.close(fig)
print('Saved ->', D)
