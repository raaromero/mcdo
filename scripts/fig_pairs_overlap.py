r"""From the two pulse spectra to the pairs that reach 350 nm, for a 20 fs pulse.

(a) The two pulses: Gaussian spectra at 656 nm and 750 nm.
(b) Each 750 nm photon λ_a has one partner λ_b = 1/(1/350 nm − 1/λ_a). Red: the 750 nm spectrum at λ_a; blue dashed:
the 656 nm spectrum at the partner λ_b. Their product (black, shaded) is how often each pair occurs: the overlap, a
Gaussian √2 narrower than either pulse.

    python scripts/fig_pairs_overlap.py  -> output/08_two_color/lim2002/slides/pairs_overlap.png
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from mcdo.style import apply
apply()
matplotlib.rcParams.update({'font.size': 24, 'axes.titlesize': 28, 'axes.labelsize': 28, 'xtick.labelsize': 24,
                            'ytick.labelsize': 24, 'legend.fontsize': 24})
np.seterr(divide='ignore')
C, LN2, LE, TAU = 299792.458, np.log(2), 350.0, 20.0
RED, BLUE = '#d62728', '#1f77b4'
partner = lambda a: 1 / (1 / LE - 1 / a)
spec = lambda lam, lam0: np.exp(-4 * LN2 * (C / lam - C / lam0) ** 2 / (441.0 / TAU) ** 2)

fig, axes = plt.subplots(1, 2, figsize=(26.0, 10.0), sharey=True)
fig.subplots_adjust(left=0.07, right=0.98, bottom=0.22, top=0.76, wspace=0.32)

ax = axes[0]
x = np.linspace(600, 820, 3001)
ax.fill_between(x, spec(x, 656), color=BLUE, alpha=0.25, lw=0); ax.plot(x, spec(x, 656), color=BLUE, lw=4)
ax.fill_between(x, spec(x, 750), color=RED, alpha=0.25, lw=0); ax.plot(x, spec(x, 750), color=RED, lw=4)
ax.text(656, 1.03, '656 nm pulse', color=BLUE, ha='center', fontsize=26)
ax.text(750, 1.03, '750 nm pulse', color=RED, ha='center', fontsize=26)
ax.set_xlim(600, 820); ax.set_ylim(0, 1.15)
ax.set_xlabel('wavelength (nm)'); ax.set_ylabel('relative intensity')
ax.set_title(f'(a) The two pulses, τ = {TAU:g} fs', y=1.22)

ax = axes[1]
a = np.linspace(700, 805, 3001)
s1, s2 = spec(a, 750), spec(partner(a), 656)
ax.plot(a, s1, color=RED, lw=4, label='750 nm pulse at λ$_a$')
ax.plot(a, s2, '--', color=BLUE, lw=4, label='656 nm pulse at its partner λ$_b$')
ax.fill_between(a, s1 * s2, color='k', alpha=0.25, lw=0)
ax.plot(a, s1 * s2, color='k', lw=5, label='product: how often the pair occurs')
ax.annotate('overlap: the pairs\nthat reach 350 nm', xy=(757, 0.55), xytext=(784, 0.86), fontsize=26, ha='center',
            arrowprops=dict(arrowstyle='-|>', lw=3, mutation_scale=30, color='k'))
ax.set_xlim(700, 805)
ax.set_xlabel('λ$_a$, photon from the 750 nm pulse (nm)')
top = ax.secondary_xaxis('top', functions=(partner, partner))
top.set_xlabel('λ$_b$, its partner (nm)')
ax.set_title('(b) Pair each photon with its 350 nm partner', y=1.22)
h, l = ax.get_legend_handles_labels()
fig.legend(h, l, loc='lower center', ncol=3, bbox_to_anchor=(0.6, 0.0), frameon=False)

p0, p1 = axes[0].get_position(), axes[1].get_position()
fig.add_artist(FancyArrowPatch((p0.x1 + 0.012, 0.5), (p1.x0 - 0.012, 0.5), transform=fig.transFigure,
                               arrowstyle='-|>', mutation_scale=45, lw=5, color='k'))
out = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002', 'slides', 'pairs_overlap.png')
fig.savefig(out, dpi=600, bbox_inches='tight')
