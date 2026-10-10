r"""Photon pairs of the two pulses on (λ_a, λ_b) axes, with lines of constant pair wavelength λ_e.

Grey: pair density |a(ω_a)|² |a(ω_b)|² of two transform-limited Gaussian pulses (750 and 656 nm). Red: lines
1/λ_a + 1/λ_b = 1/λ_e. Integrating the grey along each red line gives the pair-wavelength distribution.

    python scripts/fig_pulse_pairs_2d.py  -> output/08_two_color/lim2002/slides/pulse_pairs_2d.png
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mcdo.style import apply
apply()
matplotlib.rcParams.update({'font.size': 24, 'axes.titlesize': 28, 'axes.labelsize': 28, 'xtick.labelsize': 22,
                            'ytick.labelsize': 22})
C, LN2 = 299.792458, np.log(2)
fig, axes = plt.subplots(1, 2, figsize=(15.5, 7.6))
for ax, tau, lev in zip(axes, (20, 10), ((344, 347, 350, 353, 356), (338, 344, 350, 356, 362))):
    w1, w2 = 2 * np.pi * C / 750, 2 * np.pi * C / 656
    s = 2 * np.sqrt(LN2) / tau                                   # field-spectrum standard deviation (rad/fs)
    wa, wb = np.linspace(w1 - 3 * s, w1 + 3 * s, 400), np.linspace(w2 - 3 * s, w2 + 3 * s, 400)
    WA, WB = np.meshgrid(wa, wb)
    P = np.exp(-(WA - w1) ** 2 / s ** 2) * np.exp(-(WB - w2) ** 2 / s ** 2)
    LA, LB = 2 * np.pi * C / WA, 2 * np.pi * C / WB
    ax.pcolormesh(LA, LB, P, cmap='Greys', shading='auto', rasterized=True)
    cs = ax.contour(LA, LB, 1 / (1 / LA + 1 / LB), levels=lev, colors='#d62728', linewidths=2.5)
    ax.clabel(cs, fmt='%d', fontsize=20, inline_spacing=8)
    ax.set_xlabel('λ$_a$ (nm), 750 nm pulse'); ax.set_title(f'τ = {tau} fs')
axes[0].set_ylabel('λ$_b$ (nm), 656 nm pulse')
plt.tight_layout()
fig.savefig(os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002', 'slides', 'pulse_pairs_2d.png'),
            dpi=600, bbox_inches='tight')
