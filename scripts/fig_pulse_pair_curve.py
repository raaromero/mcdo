r"""Which photon pairs add up to the 350 nm transition: the curve 1/λ_a + 1/λ_b = 1/350 nm inside the wavelength ranges
of 20 fs pulses at 750 nm (shaded red, vertical band) and 656 nm (shaded blue, horizontal band). The curve is solid
where both photons lie in their pulse's range; the two dots are the first and last such pairs.

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
matplotlib.rcParams.update({'font.size': 24, 'axes.labelsize': 28, 'xtick.labelsize': 24, 'ytick.labelsize': 24})
LE, A, B = 350.0, (730, 770), (640, 672)
pair = lambda a: 1 / (1 / LE - 1 / a)
la = np.linspace(710, 790, 801); lb = pair(la)
ok = (la >= A[0]) & (la <= A[1]) & (lb >= B[0]) & (lb <= B[1])
fig, ax = plt.subplots(figsize=(8.0, 7.0))
ax.axvspan(*A, color='#d62728', alpha=0.15, lw=0)
ax.axhspan(*B, color='#1f77b4', alpha=0.15, lw=0)
ax.plot(la, lb, color='#999999', lw=2.5)
ax.plot(la[ok], lb[ok], color='k', lw=5)
for a, b in ((la[ok][0], lb[ok][0]), (la[ok][-1], lb[ok][-1])):
    ax.plot(a, b, 'o', color='k', ms=13)
    ax.annotate(f'{a:.0f} + {b:.0f}', (a, b), xytext=(10, 10) if a < 750 else (-150, -40), textcoords='offset points', fontsize=24)
ax.set_xlabel('λ$_a$ (nm)'); ax.set_ylabel('λ$_b$ (nm)')
ax.set_xlim(710, 790); ax.set_ylim(625, 690)
plt.tight_layout()
out = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002', 'slides', 'pulse_pair_curve.png')
fig.savefig(out, dpi=600, bbox_inches='tight')
print(f'valid pairs from {la[ok][0]:.1f} + {lb[ok][0]:.1f} to {la[ok][-1]:.1f} + {lb[ok][-1]:.1f} nm')
