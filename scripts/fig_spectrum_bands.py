r"""Spectral power of a 1 fs pulse at 750 nm, an 18 as Gaussian model at
7.2 nm, and a 1 fs pulse at the same 7.2 nm center, with Gao et al.'s measured
band (Fig. 2d, 50–284 eV) and the infrared, visible and ultraviolet bands.

The 18 as carrier sits at 4 sigma of its own spectrum (172 eV), the lowest
carrier that keeps the Gaussian off negative frequencies. Every spectrum is
Gaussian in photon energy (equivalently frequency), |E|^2 ∝ exp[-(E-Ec)^2/2σ^2].

Three x variables (wavelength, frequency, photon energy); for each a single
log-axis figure with every curve, and linear- and log-axis pairs.

    python scripts/fig_spectrum_bands.py
    -> output/05_pulsed_pupils/spectrum_bands_1fs_18as*.png
"""

import os
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from mcdo.style import apply as _apply_style
_apply_style()
matplotlib.rcParams.update({'font.size': 24, 'axes.titlesize': 32,
                            'axes.labelsize': 28, 'xtick.labelsize': 24,
                            'ytick.labelsize': 24, 'legend.fontsize': 24})

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '05_pulsed_pupils')
HC = 1239.84198          # eV nm
HBAR = 0.658211957       # eV fs
C_NM_THZ = 299792.458    # f[THz] = C_NM_THZ / λ[nm]
SQ = np.sqrt(2 * np.log(2))
E_750 = HC / 750.0
E_18AS = 4.0 * SQ * HBAR / 0.018                     # 172 eV
BAND_LO, BAND_HI = 50.0, 284.0                       # Gao Fig. 2d, eV

CURVES = {
    'ir':   (1.0, E_750, '1 fs, 750 nm carrier', '#d62728', 4.0),
    'as':   (0.018, E_18AS, '18 as Gaussian model, 7.2 nm carrier', '#1f77b4', 4.0),
    'fsx':  (1.0, E_18AS, '1 fs, 7.2 nm carrier (same center as 18 as)', '#9467bd', 3.0),
}
BANDS_NM = ((10.0, 380.0, '#b39ddb', 'Ultraviolet'), (380.0, 750.0, '#fff59d', 'Visible'),
            (750.0, 20000.0, '#ffab91', 'Infrared'))
AXES = {  # to_x(E), label, single-figure log range (in x), unit text for band
    'wavelength': (lambda e: HC / e, 'Wavelength (nm)', (1.0, 20000.0)),
    'freq':       (lambda e: e * C_NM_THZ / HC, 'Frequency (THz)', (C_NM_THZ / 20000, C_NM_THZ)),
    'energy':     (lambda e: e, 'Photon energy (eV)', (HC / 20000, HC)),
}
PAIR_RANGES = {   # (left, right) x ranges; linear then log
    'wavelength': (((0.0, 3000.0), (0.0, 30.0)), ((200.0, 20000.0), (2.0, 40.0))),
    'freq':       (((0.0, 1000.0), (0.0, 90000.0)), ((15.0, 1500.0), (7500.0, 150000.0))),
    'energy':     (((0.0, 5.0), (0.0, 350.0)), ((0.06, 6.0), (30.0, 620.0))),
}
MEASURED = Patch(fc='none', ec='#2ca02c', hatch='//', lw=2.5,
                 label='Gao et al. measured band, Fig. 2d: 4.4–24.8 nm (50–284 eV)')


def spectrum(E, key):
    tau, Ec, *_ = CURVES[key]
    sig = SQ * HBAR / tau
    return np.exp(-(E - Ec) ** 2 / (2 * sig ** 2))


def x_to_E(x, kind):
    if kind == 'wavelength':
        return HC / x
    if kind == 'freq':
        return x * HC / C_NM_THZ
    return x


def draw(ax, kind, keys, xr, logx, bands=True, measured=True):
    to_x, xlabel, _ = AXES[kind]
    lo, hi = xr
    x = (np.logspace(np.log10(lo), np.log10(hi), 8000) if logx
         else np.linspace(max(lo, hi / 8000), hi, 8000))
    E = x_to_E(x, kind)
    if bands:
        for b_lo, b_hi, col, name in BANDS_NM:
            a, b = sorted((to_x(HC / b_lo), to_x(HC / b_hi)))
            a, b = max(a, lo if logx else 0.0), min(b, hi)
            if a >= b:
                continue
            ax.axvspan(a, b, color=col, alpha=0.35, lw=0)
            frac = (np.log(b / a) / np.log(hi / lo)) if logx else (b - a) / (hi - lo)
            xm = np.sqrt(a * b) if logx else 0.5 * (a + b)
            if frac > 0.22:
                ax.text(xm, 1.09, name, ha='center', va='bottom', fontsize=24, zorder=6,
                        bbox=dict(fc='white', ec='none', alpha=0.9, pad=1.5))
            elif frac > 0.08:
                ax.text(xm, 1.13, name, ha='center', va='top', fontsize=22, rotation=90,
                        zorder=6, bbox=dict(fc='white', ec='none', alpha=0.9, pad=1.5))
    for k in keys:
        _, _, lab, col, lw = CURVES[k]
        ax.plot(x, spectrum(E, k), '-', color=col, lw=lw, label=lab)
    if measured:
        a, b = sorted((to_x(BAND_LO), to_x(BAND_HI)))
        if b > lo and a < hi:
            ax.axvspan(a, b, fc='none', ec='#2ca02c', hatch='//', lw=2.5, zorder=3)
    if logx:
        ax.set_xscale('log')
    ax.set_xlim(lo, hi)
    ax.set_ylim(0, 1.2)
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_xlabel(xlabel)
    ax.set_ylabel('Spectral power, normalized to the peak')
    ax.grid(alpha=0.25, which='both' if logx else 'major')


def save(fig, name):
    out = os.path.join(OUT, name)
    fig.savefig(out, dpi=200, bbox_inches='tight')
    plt.close(fig)
    shutil.copy(out, os.path.expanduser(f'~/Downloads/{name}'))
    print('Saved ->', out)


SINGLE_NAME = {'wavelength': 'spectrum_bands_1fs_18as.png',
               'freq': 'spectrum_bands_1fs_18as_logfreq.png',
               'energy': 'spectrum_bands_1fs_18as_logenergy.png'}
PAIR_NAME = {('wavelength', False): 'spectrum_bands_1fs_18as_linear_wavelength.png',
             ('freq', False): 'spectrum_bands_1fs_18as_freq.png',
             ('energy', False): 'spectrum_bands_1fs_18as_linear_energy.png',
             ('wavelength', True): 'spectrum_bands_1fs_18as_pair_log_wavelength.png',
             ('freq', True): 'spectrum_bands_1fs_18as_pair_log_freq.png',
             ('energy', True): 'spectrum_bands_1fs_18as_pair_log_energy.png'}

keys_all = ['ir', 'as', 'fsx']
legend_all = [Line2D([], [], color=CURVES[k][3], lw=CURVES[k][4], label=CURVES[k][2])
              for k in keys_all] + [MEASURED]

for kind in AXES:
    fig, ax = plt.subplots(figsize=(22.0, 11.5))
    draw(ax, kind, keys_all, AXES[kind][2], True)
    fig.legend(handles=legend_all, loc='upper center', bbox_to_anchor=(0.5, 0.02), ncol=2)
    plt.tight_layout()
    save(fig, SINGLE_NAME[kind])

    for logx in (False, True):
        left, right = PAIR_RANGES[kind][1 if logx else 0]
        fig, axes = plt.subplots(1, 2, figsize=(30.0, 12.0))
        draw(axes[0], kind, ['ir'], left, logx, measured=False)
        axes[0].set_title('1 fs, 750 nm carrier')
        draw(axes[1], kind, ['as', 'fsx'], right, logx)
        axes[1].set_title('7.2 nm carrier: 18 as and 1 fs')
        fig.legend(handles=legend_all, loc='upper center', bbox_to_anchor=(0.5, 0.02), ncol=2)
        plt.tight_layout()
        save(fig, PAIR_NAME[(kind, logx)])

# ── Gaussian pulse equations, rendered ──────────────────────────────────
EQ = [r'$E(t) = \left(\frac{2a}{\pi}\right)^{1/4}\,\exp(-\Gamma t^{2})\,\exp(-j\omega_c t),\qquad \Gamma = a - jb$',
      r'$|E(t)|^{2} = \left(\frac{2a}{\pi}\right)^{1/2}\exp\left[-4\ln 2\left(\frac{t}{\tau}\right)^{2}\right],\qquad \tau = \left(\frac{2\ln 2}{a}\right)^{1/2}$',
      r'$|E(\omega)|^{2} \propto \exp\left[-\frac{(\omega-\omega_c)^{2}}{2a}\right]$']
fig = plt.figure(figsize=(14.0, 5.0))
for i, e in enumerate(EQ):
    fig.text(0.02, 0.83 - 0.33 * i, e, fontsize=26, va='center')
out = os.path.join(OUT, 'gaussian_pulse_equations.png')
fig.savefig(out, dpi=200, bbox_inches='tight')
print('Saved ->', out)
