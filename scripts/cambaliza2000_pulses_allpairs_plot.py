r"""Figures of the all-pairs pulsed 2CE (cambaliza2000_pulses_allpairs.py): 350-nm pairs (750 + 656 nm) alone against all pairs.

    python scripts/cambaliza2000_pulses_allpairs_plot.py -> output/08_two_color/cambaliza2000/pulses/allpairs/*.png
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
from mcdo.twobeam import beam_field

_apply_style()
matplotlib.rcParams.update({'font.size': 28, 'axes.titlesize': 30, 'axes.labelsize': 30, 'xtick.labelsize': 26,
                            'ytick.labelsize': 26, 'legend.fontsize': 26})
D = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'cambaliza2000', 'pulses', 'allpairs')
R = np.load(os.path.join(D, 'allpairs.npz'))
zs, xs = R['zs'], R['xs']
for tk, th, cut, lab in (('pi', np.pi, 'z', 'facing lenses (θ = π), along the axis'),
                         ('pi2', np.pi / 2, 'x', 'crossed lenses (θ = π/2), across the axis'),
                         ('0', 0.0, 'z', 'collinear lenses (θ = 0), along the axis')):
    s = zs if cut == 'z' else xs
    fig, axes = plt.subplots(1, 2, figsize=(18.5, 7.0), sharey=True)
    for ax, tau in zip(axes, (10, 20)):
        k = f'{tk}_{tau}_{cut}'
        one, allp, single = R[k + '_one'], R[k + '_all'], R[k + '_single']
        pts = (0 * s, s) if cut == 'z' else (s, 0 * s)
        cw = np.abs(beam_field(*pts, 0.750, 0.5)) ** 2 * np.abs(beam_field(*pts, 0.656, 0.5, theta=th)) ** 2
        ax.plot(s, cw / cw.max(), '--', color='k', lw=2.5, label='continuous beams')
        ax.plot(s, one / one.max(), color='#1f77b4', lw=3, label='350-nm pairs (750 + 656 nm) only')
        ax.plot(s, allp / one.max(), color='#d62728', lw=2, label='2CE, all pairs (phase-locked beams)')
        ax.plot(s, single / one.max(), color='#ff7f0e', lw=2.5, label='375- and 328-nm pairs (750 + 750, 656 + 656 nm)')
        ax.set_title(f'τ = {tau} fs'); ax.set_xlabel(f'{cut} (µm), at {"x" if cut == "z" else "z"} = 0')
        ax.set_xlim(s[0], s[-1])
    axes[0].set_ylabel('2CE (one-pair peak = 1)')
    h, l = axes[0].get_legend_handles_labels()
    fig_legend(fig, h, l)
    fig.savefig(os.path.join(D, f'allpairs_{tk}.png'), dpi=300, bbox_inches='tight'); plt.close(fig)
    print('Saved ->', f'allpairs_{tk}.png')
