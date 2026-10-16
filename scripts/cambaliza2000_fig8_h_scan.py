r"""Cambaliza & Saloma (2000) Fig. 8 against the slab half-thickness h (not stated in the paper).

Reads fig8_mc_h<h>.npz from replicate_cambaliza2000_fig8.py (h/d_s = 8 at 700 nm for every h, so h sets the scale of the
scattering against the focal region). Axial 2PE (I₁ + I₂)² and 2CE I₁ I₂ at θ = π, each normalized to its peak.

    python scripts/cambaliza2000_fig8_h_scan.py -> output/08_two_color/cambaliza2000/panels/fig8_h_scan.png
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
matplotlib.rcParams.update({'font.size': 24, 'axes.titlesize': 28, 'axes.labelsize': 28, 'xtick.labelsize': 24,
                            'ytick.labelsize': 24, 'legend.fontsize': 24})

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'cambaliza2000')
HS = (20, 50, 100, 300, 1000)
COL = dict(zip(HS, ('#9467bd', '#ff7f0e', 'k', '#1f77b4', '#2ca02c')))

fig, axes = plt.subplots(1, 2, figsize=(18.5, 6.2), sharey=True)
for h in HS:
    R = np.load(os.path.join(OUT, f'fig8_mc_h{h}.npz'))
    z = R['z']
    m = {k: R[k].mean(0) for k in ('2p_a', '2p_b', 'l1', 'l2')}
    F2p = (m['2p_a'] + m['2p_b'][::-1]) ** 2                   # beam from L2 (θ = π) enters at z = +h
    F2c = m['l1'] * m['l2'][::-1]
    far = np.abs(z) > 10
    for ax, F in zip(axes, (F2p, F2c)):
        F = F / F.max()
        ax.plot(z, F, '-', color=COL[h], lw=4 if h == 100 else 2.5, label=f'h = {h} µm')
        print(f'h = {h}: background (mean for |z| > 10 µm) {F[far].mean():.3f}')
for ax, sig in zip(axes, ('2PE', '2CE')):
    ax.set_xlim(-20, 20); ax.set_ylim(0, 1); ax.set_xticks(np.arange(-20, 21, 5))
    ax.set_xlabel('z (µm)'); ax.set_title(f'{sig}, θ = π')
axes[0].set_ylabel('Fluorescence')
hd, lb = axes[0].get_legend_handles_labels()
fig.legend(hd, lb, loc='lower center', ncol=5, bbox_to_anchor=(0.5, -0.1), frameon=False)
plt.tight_layout()
fig.savefig(os.path.join(OUT, 'panels', 'fig8_h_scan.png'), dpi=300, bbox_inches='tight'); plt.close(fig)
print('Saved -> panels/fig8_h_scan.png')
