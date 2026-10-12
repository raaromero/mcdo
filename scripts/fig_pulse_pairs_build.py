r"""Which photons of the two pulses pair up to reach the 350 nm transition, for each pulse duration.

Red and blue: spectra of the 750 nm and 656 nm pulses (transform-limited Gaussians of duration τ). Shaded parts: photons
whose partner (λ_a on the red spectrum, λ_b on the blue) with 1/λ_a + 1/λ_b = 1/350 nm; each colour is one pair. Shorter
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
cmap = plt.get_cmap('viridis')
TH = 0.05                                            # a photon has a partner if the partner's spectrum is above 5% of peak
fig, axes = plt.subplots(1, 3, figsize=(30.0, 9.0), sharey=True)
for ax, tau in zip(axes, (100, 20, 10)):
    ax.plot(lam, spec(lam, 750, tau), color='#d62728', lw=3)
    ax.plot(lam, spec(lam, 656, tau), color='#1f77b4', lw=3)
    la = lam[(lam > 600) & (lam < 830)]
    lb = partner(la)
    ok = (spec(la, 750, tau) > TH) & (spec(lb, 656, tau) > TH)
    la, lb = la[ok], lb[ok]
    if la.size:
        cv = (la - la.min()) / max(np.ptp(la), 1e-9)
        for i in range(la.size - 1):                 # same colour on both spectra = partners
            c = cmap(0.1 + 0.8 * cv[i])
            ax.fill_between(la[i:i + 2], spec(la[i:i + 2], 750, tau), color=c, lw=0.6, ec=c)
            ax.fill_between(lb[i:i + 2], spec(lb[i:i + 2], 656, tau), color=c, lw=0.6, ec=c)
    ax.set_title(f'τ = {tau} fs'); ax.set_xlabel('wavelength (nm)'); ax.set_xlim(590, 830); ax.set_ylim(0, 1.08)
axes[0].set_ylabel('spectrum')
plt.tight_layout()
fig.savefig(os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002', 'slides',
                         'pulse_pairs_build.png'), dpi=600, bbox_inches='tight')
