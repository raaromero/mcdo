r"""Gaussian input against uniform input, vector focus: single-beam axial
profiles at NA 0.5, 0.7 and 0.9 in air.

λ = 750 nm, on the optical axis. Uniform input (α_t = 0, Lim & Saloma's case)
against a Gaussian input with truncation α_t = 4, pupil amplitude
exp(−α_t sin²ϑ / sin²α), both with the Richards–Wolf focus.

    python scripts/fig_lim2002_axial_gaussian.py
    -> output/08_two_color/lim2002/axial_gaussian_vs_uniform.png
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
matplotlib.rcParams.update({'font.size': 24, 'axes.titlesize': 32,
                            'axes.labelsize': 28, 'xtick.labelsize': 24,
                            'ytick.labelsize': 24, 'legend.fontsize': 24})

from mcdo.apodization import gaussian
from mcdo.twobeam import beam_field, intensity

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002')
LAM = 0.750

fig, axes = plt.subplots(1, 3, figsize=(21.0, 7.5))
for a, na in zip(axes, (0.5, 0.7, 0.9)):
    z = np.linspace(-3.0 * 2 * LAM / na ** 2, 3.0 * 2 * LAM / na ** 2, 1201)
    for at, lab, col, ls in ((0, 'uniform input (α$_t$ = 0)', 'k', '-'), (4, 'Gaussian input, α$_t$ = 4', '#d62728', '--')):
        ap = gaussian(at, na ** 2) if at else None
        I = intensity(beam_field(0 * z, z, LAM, na, model='rw', psi=0.0, apodization=ap))
        a.plot(z, I / I.max(), ls, color=col, lw=4, label=lab)
    a.set_title(f'NA {na}')
    a.set_xlabel('z (µm)')
    a.set_ylim(0, 1.05)
axes[0].set_ylabel('On-axis intensity, normalized')
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, loc='lower center', ncol=2, bbox_to_anchor=(0.5, -0.1))
plt.tight_layout(rect=(0, 0.06, 1, 1))
fig.savefig(os.path.join(OUT, 'axial_gaussian_vs_uniform.png'), dpi=600, bbox_inches='tight')
print('Saved -> axial_gaussian_vs_uniform.png')
