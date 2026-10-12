r"""Which photon pairs reach the 350 nm transition.

(a) The two pulses, τ = 20 fs: Gaussian spectra at 656 nm and 750 nm.
(b) Same wavelength axis: the part of each spectrum whose photons form a pair that adds up to 350 nm
    (1/λ_a + 1/λ_b = 1/350 nm), weighted by how often the pair occurs, S_750(λ_a) S_656(λ_b).
(c) How often each pair occurs against the 750 nm photon λ_a (partner λ_b on the top axis), for τ = 100, 50, 20, 10 fs.

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
C, LN2, LE = 299792.458, np.log(2), 350.0
RED, BLUE, GREY = '#d62728', '#1f77b4', '#444444'
partner = lambda a: 1 / (1 / LE - 1 / a)
spec = lambda lam, lam0, tau: np.exp(-4 * LN2 * (C / lam - C / lam0) ** 2 / (441.0 / tau) ** 2)

fig, axes = plt.subplots(1, 3, figsize=(34.0, 10.5))
fig.subplots_adjust(left=0.05, right=0.99, bottom=0.2, top=0.78, wspace=0.28)
x = np.linspace(600, 820, 3001)

ax = axes[0]                                                     # (a) the two pulses
for l0, col, name in ((656, BLUE, '656 nm pulse'), (750, RED, '750 nm pulse')):
    ax.fill_between(x, spec(x, l0, 20), color=col, alpha=0.25, lw=0)
    ax.plot(x, spec(x, l0, 20), color=col, lw=4)
    ax.text(l0, 1.03, name, color=col, ha='center', fontsize=26)
ax.set_ylabel('relative intensity')
ax.set_title('(a) The two pulses, τ = 20 fs', y=1.2)

ax = axes[1]                                                     # (b) photons that form 350 nm pairs
for l0, col in ((656, BLUE), (750, RED)):
    ax.plot(x, spec(x, l0, 20), color=col, lw=2.5, alpha=0.6)
a = np.linspace(690, 815, 3001)
w = spec(a, 750, 20) * spec(partner(a), 656, 20)
for xs in (a, partner(a)):
    ax.fill_between(xs, w, color=GREY, alpha=0.55, lw=0)
    ax.plot(xs, w, color='k', lw=4)
ax.text(703, 0.88, '350 nm pairs', ha='center', fontsize=26)
for tip in ((662, 0.55), (742, 0.55)):
    ax.annotate('', xy=tip, xytext=(703, 0.82), arrowprops=dict(arrowstyle='-|>', lw=3, mutation_scale=30))
ax.set_title('(b) Pairs that reach 350 nm', y=1.2)
ax.tick_params(labelleft=False)          # same intensity scale as (a)

for ax in axes[:2]:
    ax.set_xlim(600, 820); ax.set_ylim(0, 1.15); ax.set_xlabel('wavelength (nm)')

ax = axes[2]                                                     # (c) against pulse duration
la = np.linspace(680, 830, 3001)
for tau, col in ((100, '#1f77b4'), (50, '#ff7f0e'), (20, '#d62728'), (10, '#2ca02c')):
    ax.plot(la, spec(la, 750, tau) * spec(partner(la), 656, tau), color=col, lw=4, label=f'{tau} fs')
ax.set_xlim(680, 830); ax.set_ylim(0, 1.05)
ax.set_xlabel('λ$_a$, 750 nm photon (nm)'); ax.set_ylabel('how often the pair occurs')
top = ax.secondary_xaxis('top', functions=(partner, partner))
top.set_xlabel('λ$_b$, 656 nm partner (nm)')
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.14), ncol=4, frameon=False, columnspacing=1.2)
ax.set_title('(c) Pairs against pulse duration', y=1.2)

p0, p1 = axes[0].get_position(), axes[1].get_position()
fig.add_artist(FancyArrowPatch((p0.x1 + 0.008, 0.5), (p1.x0 - 0.008, 0.5), transform=fig.transFigure,
                               arrowstyle='-|>', mutation_scale=45, lw=5, color='k'))
out = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002', 'slides', 'pairs_overlap.png')
fig.savefig(out, dpi=600, bbox_inches='tight')
