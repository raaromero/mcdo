r"""Spectral power of a 1 fs and an 18 as Gaussian pulse at a 750 nm carrier.

    python scripts/fig_spectrum_attosecond.py
    -> output/05_pulsed_pupils/spectrum_1fs_vs_18as.png
"""

import os
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo.style import apply as _apply_style
_apply_style()
matplotlib.rcParams.update({'font.size': 16, 'axes.labelsize': 17,
                            'xtick.labelsize': 15, 'ytick.labelsize': 15,
                            'legend.fontsize': 15, 'axes.titlesize': 17})

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '05_pulsed_pupils')
C = 299792458.0
f_c = C / 750e-9                                   # carrier, Hz
f = np.linspace(-50000e12, 50000e12, 20001)       # Hz

fig, ax = plt.subplots(figsize=(13.0, 7.5))
for tau, lab, col in ((1e-15, '1 fs', '#d62728'), (18e-18, '18 as', '#1f77b4')):
    a = 2.0 * np.log(2.0) / tau ** 2               # |E(ω)|² ∝ exp[-(ω-ω_c)²/2a]
    w = 2 * np.pi * f
    wc = 2 * np.pi * f_c
    ax.plot(f / 1e12, np.exp(-(w - wc) ** 2 / (2 * a)), '-', color=col,
            lw=2.8, label=lab)
ax.set_xlabel('Frequency (THz)')
ax.set_ylabel('Spectral power, normalized to the peak')
ax.set_title('Spectral power, 750 nm carrier (400 THz)')
ax.set_ylim(0, 1.05)
ax.grid(alpha=0.25)
fig.legend(loc='center left', bbox_to_anchor=(0.86, 0.5))
plt.tight_layout(rect=[0, 0, 0.85, 1])
out = os.path.join(OUT, 'spectrum_1fs_vs_18as.png')
fig.savefig(out, dpi=200, bbox_inches='tight')
shutil.copy(out, os.path.expanduser('~/Downloads/spectrum_1fs_vs_18as.png'))
print('Saved ->', out)

for tau, lab in ((1e-15, '1 fs'), (18e-18, '18 as')):
    sig = np.sqrt(2 * np.log(2)) / tau             # std of |E(ω)|², rad/s
    wc = 2 * np.pi * f_c
    from scipy.stats import norm
    frac = norm.cdf(2 * wc, wc, sig) - norm.cdf(0, wc, sig)
    print(f'{lab}: FWHM {4*np.log(2)/tau/(2*np.pi)/1e12:9.0f} THz, '
          f'cycles {tau*f_c:.4f}, weight in (0, 2ω_c) {100*frac:.2f}%')
