r"""Which photon pairs show up at the target transition (350 nm), for each pulse duration.

Every point on the x axis is one pair: a photon λ_a from the 750 nm pulse (bottom axis) and its partner
λ_b = 1/(1/350 nm − 1/λ_a) from the 656 nm pulse (top axis), the only partner that adds up to 350 nm. The height is how
often that pair occurs: the product of the two pulse spectra at λ_a and λ_b (transform-limited Gaussians, duration τ).

    python scripts/fig_pairs_show_up.py  -> output/08_two_color/lim2002/slides/pairs_show_up.png
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mcdo.style import apply
apply()
matplotlib.rcParams.update({'font.size': 24, 'axes.labelsize': 28, 'xtick.labelsize': 24, 'ytick.labelsize': 24,
                            'legend.fontsize': 24})
C, LN2, LE = 299792.458, np.log(2), 350.0          # nm·THz
np.seterr(divide='ignore')                          # the top-axis transform is probed at 350 nm itself
partner = lambda a: 1 / (1 / LE - 1 / a)


def spec(lam, lam0, tau):
    """Intensity spectrum of a τ-fs transform-limited Gaussian pulse centred on lam0, peak 1."""
    return np.exp(-4 * LN2 * (C / lam - C / lam0) ** 2 / (441.0 / tau) ** 2)


la = np.linspace(680, 830, 3001)
fig, ax = plt.subplots(figsize=(15.0, 9.5))
for tau, col in ((100, '#1f77b4'), (50, '#ff7f0e'), (20, '#d62728'), (10, '#2ca02c')):
    w = spec(la, 750, tau) * spec(partner(la), 656, tau)
    ax.plot(la, w, color=col, lw=4, label=f'τ = {tau} fs')
    a = la[w >= 0.5]
    print(f'τ = {tau:>3} fs: half of the peak from {a[0]:.0f} + {partner(a[0]):.0f} to {a[-1]:.0f} + {partner(a[-1]):.0f} nm')
ax.set_xlim(680, 830); ax.set_ylim(0, 1.05)
ax.set_xlabel('λ$_a$, photon from the 750 nm pulse (nm)')
ax.set_ylabel('how often the pair occurs')
top = ax.secondary_xaxis('top', functions=(partner, partner))
top.set_xlabel('λ$_b$, its partner from the 656 nm pulse (nm)')
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.14), ncol=4, frameon=False)
plt.tight_layout()
out = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002', 'slides', 'pairs_show_up.png')
fig.savefig(out, dpi=600, bbox_inches='tight')
