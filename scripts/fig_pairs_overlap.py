r"""Which photon pairs reach the 350 nm transition.

(a) Probability density p(λ) of a photon's wavelength in each pulse (Gaussian spectra, τ = 20 fs), normalized.
(b) Joint probability p_1(λ_a) p_2(λ_b) of the pairs that add up to 350 nm, 1/λ_a + 1/λ_b = 1/350 nm, normalized;
    two bottom axes: λ_a from the 750 nm laser (red) and, under each tick, its partner λ_b from the 656 nm laser (blue).
    Line style by pulse duration: dotted 10 fs, dash-dot 20 fs, dashed 50 fs, solid 100 fs.

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
matplotlib.rcParams.update({'font.size': 28, 'axes.titlesize': 30, 'axes.labelsize': 30, 'xtick.labelsize': 28,
                            'ytick.labelsize': 28, 'legend.fontsize': 28})      # 22 × 9 in saved: 28 pt reads at 11 pt in the 9.0 × 3.6 in slide box
np.seterr(divide='ignore')
C, LN2, LE = 299792.458, np.log(2), 350.0
RED, BLUE = '#d62728', '#1f77b4'
partner = lambda a: 1 / (1 / LE - 1 / a)
spec = lambda lam, lam0, tau: np.exp(-4 * LN2 * (C / lam - C / lam0) ** 2 / (441.0 / tau) ** 2)

fig, axes = plt.subplots(1, 2, figsize=(22.0, 9.4))
fig.subplots_adjust(left=0.07, right=0.88, bottom=0.27, top=0.92, wspace=0.40)

ax = axes[0]                                                     # (a) probability of each wavelength
x = np.linspace(600, 820, 3001)
for l0, col, name in ((656, BLUE, '656 nm laser'), (750, RED, '750 nm laser')):
    ax.fill_between(x, spec(x, l0, 20), color=col, alpha=0.25, lw=0)
    ax.plot(x, spec(x, l0, 20), color=col, lw=4)
    ax.text(l0, 1.03, name, color=col, ha='center', fontsize=28)
ax.set_xlim(600, 820); ax.set_ylim(0, 1.15)
ax.set_xlabel('wavelength λ (nm)'); ax.set_ylabel('probability density, normalized')
ax.set_title('(a) Spectral probability density\nτ = 20 fs')

ax = axes[1]                                                     # (b) joint probability of the 350 nm pairs
la = np.linspace(680, 830, 3001)
for tau, ls in ((10, ':'), (20, '-.'), (50, '--'), (100, '-')):
    ax.plot(la, spec(la, 750, tau) * spec(partner(la), 656, tau), ls, color='k', lw=4, label=f'{tau} fs')
ax.set_xlim(680, 830); ax.set_ylim(0, 1.05)
ax.set_ylabel('joint probability, normalized')
ax.set_xlabel('λ$_a$, 750 nm laser (nm)', color=RED)
ax.tick_params(axis='x', colors=RED); ax.spines['bottom'].set_color(RED)
TA = [700, 725, 750, 775, 800, 825]
ax.set_xticks(TA)
sec = ax.secondary_xaxis(-0.16)                                  # each partner sits under its own λ_a tick
sec.set_xticks(TA, labels=[f'{partner(a):.0f}' for a in TA])
sec.set_xlabel('λ$_b$, 656 nm laser (nm)', color=BLUE)
sec.tick_params(axis='x', colors=BLUE); sec.spines['bottom'].set_color(BLUE)
ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1.0), frameon=False, handlelength=2.4, title='τ',
          title_fontsize=28)                                   # outside the axes, clear of the curves
ax.set_title('(b) Two-photon resonance\nν$_a$ + ν$_b$ = ν$_e$, λ$_e$ = 350 nm')

p0, p1 = axes[0].get_position(), axes[1].get_position()
fig.add_artist(FancyArrowPatch((p0.x1 + 0.01, 0.6), (p1.x0 - 0.065, 0.6), transform=fig.transFigure,
                               arrowstyle='-|>', mutation_scale=45, lw=5, color='k'))
out = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002', 'slides', 'pairs_overlap.png')
fig.savefig(out, dpi=600, bbox_inches='tight')
