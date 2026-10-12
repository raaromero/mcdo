r"""Spread of pair wavelengths against pulse duration, closed form Δλ_e = √2 (λ_e²/c) 0.441/τ ≈ 255 nm·fs / τ at 350 nm.

Shaded: typical Ti:sapphire pulses (50–150 fs). Hatched: τ < 8 fs, where the 750 and 656 nm spectra overlap and the
2CE-only model no longer holds.

    python scripts/fig_pair_spread.py  -> output/08_two_color/lim2002/slides/pair_spread.png
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
C, LE = 299792.458, 350.0
tau = np.logspace(np.log10(3), np.log10(300), 400)
dl = np.sqrt(2) * LE ** 2 / C * 441 / tau
fig, ax = plt.subplots(figsize=(14.0, 10.0))
ax.axvspan(50, 150, color='#1f77b4', alpha=0.12, lw=0)
ax.axvspan(3, 8, color='none', hatch='//', ec='#999999', lw=0)
ax.plot(tau, dl, color='k', lw=4)
for t in (10, 20, 50, 100):
    d = np.sqrt(2) * LE ** 2 / C * 441 / t
    ax.plot(t, d, 'o', color='k', ms=12)
    ax.text(t * 1.08, d * 1.08, f'{d:.1f} nm', fontsize=24)
ax.text(np.sqrt(50 * 150), 0.6, 'typical lasers', ha='center', fontsize=24, color='#1f77b4')
ax.text(np.sqrt(3 * 8), 0.6, 'spectra\noverlap', ha='center', fontsize=22, color='#666666')
ax.set_xscale('log'); ax.set_yscale('log')
ax.set_xticks([3, 10, 30, 100, 300]); ax.set_xticklabels(['3', '10', '30', '100', '300'])
ax.set_yticks([1, 3, 10, 30, 100]); ax.set_yticklabels(['1', '3', '10', '30', '100'])
ax.set_xlim(3, 300); ax.set_ylim(0.5, 120)
ax.set_xlabel('pulse duration τ (fs)'); ax.set_ylabel('spread of pair wavelengths Δλ$_e$ (nm)')
plt.tight_layout()
out = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002', 'slides', 'pair_spread.png')
fig.savefig(out, dpi=600, bbox_inches='tight')
