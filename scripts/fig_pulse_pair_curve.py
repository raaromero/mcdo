r"""Which photon pairs add up to the 350 nm transition, for three pulse durations.

Black curve: 1/λ_a + 1/λ_b = 1/350 nm. Coloured segments: the part of the curve where both photons lie within the
spectral FWHM of their pulse (750 nm and 656 nm, transform-limited Gaussians, Δν = 0.441/τ); dots mark the first and
last such pairs. Shorter pulses cover a longer stretch of the curve.

    python scripts/fig_pulse_pair_curve.py  -> output/08_two_color/lim2002/slides/pulse_pair_curve.png
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
C, LE = 299792.458, 350.0                                      # nm·THz
pair = lambda a: 1 / (1 / LE - 1 / a)


def band(lam0, tau):                                           # spectral FWHM of a τ-fs pulse, in wavelength
    nu0, dnu = C / lam0, 0.441 / (tau * 1e-3)
    return C / (nu0 + dnu / 2), C / (nu0 - dnu / 2)


la = np.linspace(690, 820, 2601); lb = pair(la)
fig, ax = plt.subplots(figsize=(13.0, 10.0))
ax.plot(la, lb, color='#bbbbbb', lw=3)
rows = []
for tau, col, lw in ((10, '#2ca02c', 16), (20, '#d62728', 10), (100, '#1f77b4', 5)):
    A, B = band(750, tau), band(656, tau)
    ok = (la >= A[0]) & (la <= A[1]) & (lb >= B[0]) & (lb <= B[1])
    ax.plot(la[ok], lb[ok], color=col, lw=lw, solid_capstyle='butt', label=f'τ = {tau} fs')
    for i in (0, -1):
        ax.plot(la[ok][i], lb[ok][i], 'o', color=col, ms=14, mec='k', mew=1.5)
    rows.append((tau, la[ok][0], lb[ok][0], la[ok][-1], lb[ok][-1]))
ax.set_xlabel('λ$_a$, 750 nm pulse (nm)'); ax.set_ylabel('λ$_b$, 656 nm pulse (nm)')
ax.set_xlim(690, 820); ax.set_ylim(615, 700)
ax.legend(loc='upper right', frameon=False)
plt.tight_layout()
out = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002', 'slides', 'pulse_pair_curve.png')
fig.savefig(out, dpi=600, bbox_inches='tight')
for r in rows:
    print(f'τ = {r[0]:>3} fs: valid pairs from {r[1]:.0f} + {r[2]:.0f} to {r[3]:.0f} + {r[4]:.0f} nm')
