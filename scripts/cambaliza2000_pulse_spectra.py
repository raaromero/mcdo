r"""Spectra of the transform-limited pulses used in the pulse extension of Cambaliza & Saloma (2000).

Gaussian pulses, intensity FWHM τ, spectral FWHM Δν = 0.441/τ, centred at the 2CE wavelengths 750 and 656 nm and the
2PE wavelength 700 nm; one panel per τ (100, 20, 10 fs), plotted against wavelength. The dotted line at 700 nm marks
where two photons of one beam add up to the 350-nm transition (1/λ + 1/λ = 1/350 nm).

    python scripts/cambaliza2000_pulse_spectra.py
    -> output/08_two_color/cambaliza2000/pulses/spectra_{frequency,wavelength}.png, spectra.txt
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo.style import apply as _apply_style
from mcdo.cutinset import fig_legend
_apply_style()
matplotlib.rcParams.update({'font.size': 28, 'axes.titlesize': 30, 'axes.labelsize': 30, 'xtick.labelsize': 26,
                            'ytick.labelsize': 26, 'legend.fontsize': 26})

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'cambaliza2000', 'pulses')
os.makedirs(OUT, exist_ok=True)
C = 299792458.0
BEAMS = ((750, '#d62728', '-', '2CE, λ₁ = 750 nm (L1)'), (656, '#1f77b4', '-', '2CE, λ₂ = 656 nm (L2)'),
         (700, '#555555', '--', '2PE, λ₂ₚ = 700 nm'))
lam = np.linspace(500, 1000, 5001)                       # nm
nu = C / (lam * 1e-9)
lines = []

nuax = np.linspace(300, 560, 5001)                          # THz
for kind in ('frequency', 'wavelength'):                    # one figure per x axis, one row of three pulse widths
    fig, axes = plt.subplots(1, 3, figsize=(18.5, 6.4), sharey=True)
    for ax, tau in zip(axes, (100, 20, 10)):
        dnu = 0.441 / (tau * 1e-15)
        for l0, col, ls, lab in BEAMS:
            nu0 = C / (l0 * 1e-9)
            if kind == 'frequency':
                ax.plot(nuax, np.exp(-4 * np.log(2) * (nuax * 1e12 - nu0) ** 2 / dnu ** 2), ls, color=col, lw=3, label=lab)
            else:
                ax.plot(lam, np.exp(-4 * np.log(2) * (nu - nu0) ** 2 / dnu ** 2), ls, color=col, lw=3, label=lab)
            if kind == 'frequency':
                lo, hi = C / (nu0 + dnu / 2) * 1e9, C / (nu0 - dnu / 2) * 1e9
                at700 = np.exp(-4 * np.log(2) * (C / 700e-9 - nu0) ** 2 / dnu ** 2)
                lines.append(f'tau {tau} fs, {l0} nm ({nu0 / 1e12:.1f} THz): FWHM {dnu / 1e12:.1f} THz = {hi - lo:.1f} nm '
                             f'({lo:.0f}-{hi:.0f} nm), spectrum at 700 nm {at700:.3f}')
        if kind == 'frequency':
            ax.axvline(C / 700e-9 / 1e12, color='k', ls=':', lw=2); ax.set_xlim(300, 560); ax.set_xlabel('Frequency (THz)')
            ax.set_title(f'τ = {tau} fs: Δν = {dnu / 1e12:.0f} THz')
        else:
            ax.axvline(700, color='k', ls=':', lw=2); ax.set_xlim(580, 860); ax.set_xlabel('Wavelength (nm)')
            ax.set_title(f'τ = {tau} fs')
        ax.set_ylim(0, 1.05)
    axes[0].set_ylabel('Spectral intensity')
    axes[0].plot([], [], ':', color='k', lw=2, label='700 nm (428 THz): two equal photons reach 350 nm')
    h, l = axes[0].get_legend_handles_labels()
    fig_legend(fig, h, l)
    fig.savefig(os.path.join(OUT, f'spectra_{kind}.png'), dpi=300, bbox_inches='tight')
    plt.close(fig)
open(os.path.join(OUT, 'spectra.txt'), 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
print('Saved -> spectra_frequency.png, spectra_wavelength.png')
