r"""How the pair-wavelength distribution is built, for each pulse duration.

Each photon of the 750 nm pulse at wavelength λ_a pairs with the whole 656 nm pulse, giving a Gaussian in λ_e
(thin curves, coloured by λ_a and weighted by how many λ_a photons there are). Their sum (black) is the distribution
of λ_e the two pulses deliver. Shorter pulses: more λ_a photons, each spread wider, so the sum is wider.

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
C, LN2 = 299792.458, np.log(2)                     # nm·THz
n1, n2 = C / 750, C / 656
le = np.linspace(330, 370, 2001); ne = C / le      # pair frequency ν_e = ν_a + ν_b
g = lambda x, x0, fw: np.exp(-4 * LN2 * (x - x0) ** 2 / fw ** 2)
fig, axes = plt.subplots(1, 3, figsize=(30.0, 9.0), sharey=True)
cmap = plt.get_cmap('coolwarm')
for ax, tau in zip(axes, (100, 20, 10)):
    dnu = 0.441 / (tau * 1e-3)                      # FWHM of each pulse's spectrum (THz)
    na = n1 + np.linspace(-1.2, 1.2, 13) * dnu       # photons of the 750 nm pulse
    total = np.zeros_like(le)
    parts = [(x, g(x, n1, dnu) * g(ne - x, n2, dnu)) for x in na]   # partner from the 656 nm pulse
    peak = max(p.max() for _, p in parts)
    nb = n1 + np.linspace(-3, 3, 601) * dnu
    tot = sum(g(x, n1, dnu) * g(ne - x, n2, dnu) for x in nb) * (nb[1] - nb[0])
    for x, p in parts:
        ax.plot(le, p / peak, color=cmap((x - na[0]) / np.ptp(na)), lw=2.5)
    ax.plot(le, tot / tot.max(), color='k', lw=5)
    ax.axvline(350, color='k', lw=1.5, ls='--')
    ax.set_title(f'τ = {tau} fs'); ax.set_xlabel('λ$_e$ (nm)'); ax.set_xlim(330, 370); ax.set_ylim(0, 1.05)
axes[0].set_ylabel('pairs')
sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(C / (n1 + 1.2 * 0.441 / 0.01), C / (n1 - 1.2 * 0.441 / 0.01)))
plt.tight_layout()
fig.savefig(os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002', 'slides',
                         'pulse_pairs_build.png'), dpi=600, bbox_inches='tight')
