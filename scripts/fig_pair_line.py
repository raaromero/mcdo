r"""Photon pairs on (λ_a, λ_b): joint probability of the two 20 fs pulses (shading) and the line of pairs whose
photons add up to the 350 nm transition, 1/λ_a + 1/λ_b = 1/350 nm (black); dashed: 345 and 355 nm.

    python scripts/fig_pair_line.py  -> output/08_two_color/lim2002/slides/pair_line.png
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mcdo.style import apply
apply()
matplotlib.rcParams.update({'font.size': 26, 'axes.labelsize': 28, 'xtick.labelsize': 24, 'ytick.labelsize': 24,
                            'legend.fontsize': 24})
C, LN2 = 299792.458, np.log(2)
spec = lambda lam, lam0, tau: np.exp(-4 * LN2 * (C / lam - C / lam0) ** 2 / (441.0 / tau) ** 2)
la, lb = np.linspace(690, 815, 600), np.linspace(605, 715, 600)
A, B = np.meshgrid(la, lb)
P = spec(A, 750, 20) * spec(B, 656, 20)
fig, ax = plt.subplots(figsize=(11.5, 10))
im = ax.pcolormesh(A, B, P, cmap='Greys', shading='auto', vmin=0, vmax=1.15)
for le, ls in ((345, ':'), (350, '-'), (355, '--')):
    a = la[la > le * 1.05]
    ax.plot(a, 1 / (1 / le - 1 / a), ls, color='k' if le == 350 else '#555555', lw=4 if le == 350 else 2.5,
            label=f'λ$_e$ = {le} nm')
ax.set_xlim(la[0], la[-1]); ax.set_ylim(lb[0], lb[-1])
ax.set_xlabel('λ$_a$, photon from the 750 nm pulse (nm)', color='#d62728')
ax.set_ylabel('λ$_b$, photon from the 656 nm pulse (nm)', color='#1f77b4')
cb = fig.colorbar(im, ax=ax, fraction=0.045, pad=0.03); cb.set_label('joint probability p$_1$(λ$_a$) p$_2$(λ$_b$), 20 fs')
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=3, frameon=False)
fig.savefig(os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002', 'slides', 'pair_line.png'),
            dpi=600, bbox_inches='tight')
