r"""Photon pairs in frequency: which (ω_1, ω_2) pairs reach ω_e = ω_1 + ω_2, and how many land at each ω_e.

Left: pair density S_1(ω_1) S_2(ω_2) of two transform-limited Gaussian pulses (750 and 656 nm, τ = 20 fs), with straight
lines of constant ω_e (labelled by λ_e). Right: P(ω_e) = ∫ S_1(ω) S_2(ω_e − ω) dω, the integral along each line,
for τ = 100, 20 and 10 fs, against λ_e.

    python scripts/fig_pulse_pairs_omega.py  -> output/08_two_color/lim2002/slides/pulse_pairs_omega.png
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
                            'ytick.labelsize': 24, 'legend.fontsize': 24})
C, LN2 = 299.792458, np.log(2)                     # nm/fs
w1, w2 = 2 * np.pi * C / 750, 2 * np.pi * C / 656  # rad/fs
spec = lambda w, w0, tau: np.exp(-(w - w0) ** 2 * tau ** 2 / (4 * LN2))     # intensity spectrum of a τ-fs pulse

fig, axes = plt.subplots(1, 2, figsize=(22.0, 10.0))
ax = axes[0]                                       # one frequency axis: the two pulses, and their pairs at ω_1 + ω_2
tau = 20.0
nu = np.linspace(330, 920, 4001)                   # THz
n1, n2 = C * 1e3 / 750, C * 1e3 / 656              # 400 and 457 THz
dnu = 0.441 / (tau * 1e-3)                          # FWHM of each pulse's intensity spectrum (THz)
g = lambda x, x0, fw: np.exp(-4 * LN2 * (x - x0) ** 2 / fw ** 2)
ax.fill_between(nu, g(nu, n1, dnu), color='#d62728', alpha=0.35, lw=0)
ax.plot(nu, g(nu, n1, dnu), color='#d62728', lw=4, label='750 nm pulse')
ax.fill_between(nu, g(nu, n2, dnu), color='#1f77b4', alpha=0.35, lw=0)
ax.plot(nu, g(nu, n2, dnu), color='#1f77b4', lw=4, label='656 nm pulse')
ax.fill_between(nu, g(nu, n1 + n2, np.sqrt(2) * dnu), color='k', alpha=0.2, lw=0)
ax.plot(nu, g(nu, n1 + n2, np.sqrt(2) * dnu), color='k', lw=4, label='pairs, ν$_1$ + ν$_2$ (350 nm)')
ax.set_xlabel('frequency (THz)'); ax.set_ylabel('spectrum'); ax.set_ylim(0, 1.05); ax.set_xlim(330, 920)
ax.set_title('Spectra, τ = 20 fs')
ax.legend(loc='upper center', frameon=False)

ax = axes[1]
le = np.linspace(330, 370, 801); we = 2 * np.pi * C / le
for tau, col in ((100, '#1f77b4'), (20, '#d62728'), (10, '#2ca02c')):
    w = np.linspace(w1 - 6, w1 + 6, 6001); dw = w[1] - w[0]
    Pe = np.array([np.sum(spec(w, w1, tau) * spec(x - w, w2, tau)) * dw for x in we])
    ax.plot(le, Pe / Pe.max(), color=col, lw=4, label=f'τ = {tau} fs')
ax.axvline(350, color='k', lw=2, ls='--')
ax.set_xlabel('λ$_e$ (nm)'); ax.set_ylabel('pairs'); ax.set_ylim(0, 1.05); ax.set_xlim(330, 370)
ax.set_title('Pairs against λ$_e$')
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.13), ncol=3, frameon=False)
plt.tight_layout()
fig.savefig(os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002', 'slides',
                         'pulse_pairs_omega.png'), dpi=600, bbox_inches='tight')
