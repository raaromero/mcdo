r"""Which photons of the two pulses pair up to reach the 350 nm transition, for each pulse duration.

Red and blue: spectra of the 750 nm and 656 nm pulses (transform-limited Gaussians of duration τ). Matching markers:
pairs (λ_a on the red spectrum, λ_b on the blue) with 1/λ_a + 1/λ_b = 1/350 nm; each colour is one pair. Shorter
pulses have wider spectra, so pairs farther from 750 + 656 nm still have photons on both sides.

    python scripts/fig_pulse_pairs_build.py  -> output/08_two_color/lim2002/slides/pulse_pairs_build.png
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mcdo.style import apply
apply()
matplotlib.rcParams.update({'font.size': 24, 'axes.titlesize': 28, 'axes.labelsize': 28, 'xtick.labelsize': 24,
                            'ytick.labelsize': 24})
C, LN2, LE = 299792.458, np.log(2), 350.0          # nm·THz
lam = np.linspace(590, 830, 4001)
spec = lambda l, l0, tau: np.exp(-4 * LN2 * (C / l - C / l0) ** 2 / (0.441 / (tau * 1e-3)) ** 2)
partner = lambda a: 1 / (1 / LE - 1 / a)
PAIRS = (720, 735, 750, 765, 780)                    # λ_a of the marked pairs (nm)
cols = plt.get_cmap('viridis')(np.linspace(0, 0.9, len(PAIRS)))
fig, axes = plt.subplots(1, 3, figsize=(30.0, 9.0), sharey=True)
for ax, tau in zip(axes, (100, 20, 10)):
    ax.plot(lam, spec(lam, 750, tau), color='#d62728', lw=3.5)
    ax.plot(lam, spec(lam, 656, tau), color='#1f77b4', lw=3.5)
    for a, c in zip(PAIRS, cols):
        b = partner(a)
        ya, yb = spec(a, 750, tau), spec(b, 656, tau)
        if ya > 0.02 and yb > 0.02:                  # both photons present in their pulse
            ax.plot([a, b], [ya, yb], 'o', color=c, ms=18, mec='k', mew=1.5, zorder=5)
    ax.set_title(f'τ = {tau} fs'); ax.set_xlabel('wavelength (nm)'); ax.set_xlim(590, 830); ax.set_ylim(0, 1.08)
axes[0].set_ylabel('spectrum')
plt.tight_layout()
fig.savefig(os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002', 'slides',
                         'pulse_pairs_build.png'), dpi=600, bbox_inches='tight')
for a in PAIRS:
    print(f'{a} + {partner(a):.0f} nm')
