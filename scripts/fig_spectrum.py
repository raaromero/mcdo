r"""How the spectrum spreads as the pulse gets shorter.

The whole pulsed question starts here: a short pulse is not one wavelength. At
1 fs the spectral power spans 483 to 1674 nm between its half-maximum points,
so the focus is a superposition of colors that each focus to a different scale.

Left panel is the spectral power against wavelength for each duration, with the
half-maximum span of the 1 fs case marked. Right panel is the same against
frequency, where the Gaussian is symmetric and the width is 441 THz against a
400 THz carrier.

    python scripts/fig_spectrum.py
    -> output/05_pulsed_pupils/spectrum.png
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo.style import apply as _apply_style
_apply_style()

from mcdo import SimConfig
from mcdo.figio import save_panels

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '05_pulsed_pupils')
os.makedirs(OUT, exist_ok=True)

LAM_C, N_MED = 0.750, 1.3
C = 2.99792458e14                        # um/s
TAUS = [(1e-15, '1 fs', '#d62728', '-'),
        (2e-15, '2 fs', '#ff7f0e', '-'),
        (3e-15, '3 fs', '#8c9e2f', '-'),
        (5e-15, '5 fs', '#2ca02c', '-'),
        (10e-15, '10 fs', '#17a2b8', '-'),
        (20e-15, '20 fs', '#1f77b4', '-')]

fig, axes = plt.subplots(1, 2, figsize=(17.0, 6.8))
cfg_c = SimConfig(lam_c=LAM_C, X_NA=0.8, n=N_MED, tau=np.inf,
                  N_freq=3, N_theta=101)
om_c = cfg_c.omega_c

# ── against wavelength, which is what the focus responds to ───────────────
ax = axes[0]
lam = np.linspace(0.25, 3.0, 6000)
om = 2.0 * np.pi * C / lam
for tau, lab, color, style in TAUS:
    cfg = SimConfig(lam_c=LAM_C, X_NA=0.8, n=N_MED, tau=tau,
                    N_freq=3, N_theta=101)
    sp = cfg.spectral_power(om)
    half = cfg.spectral_bandwidth / 2.0
    lo = 2.0 * np.pi * C / (om_c + half) * 1000
    hi = 2.0 * np.pi * C / (om_c - half) * 1000
    ax.plot(lam * 1000, sp / sp.max(), style, color=color, lw=2.6,
            label=f'{lab}, {lo:.0f} to {hi:.0f} nm')
ax.axvline(LAM_C * 1000, color='#555555', lw=1.6)
ax.text(LAM_C * 1000 + 25, 1.02, 'Carrier 750 nm', fontsize=10, color='#555555')

ax.set_xlim(300, 2600)
ax.set_ylim(0, 1.12)
ax.set_xlabel('Wavelength (nm)')
ax.set_ylabel('Spectral power, normalized to the peak')
ax.set_title('Spectral power against wavelength, by pulse duration — center 750 nm',
             fontsize=12)
ax.legend(fontsize=10)
ax.grid(alpha=0.25)

# ── at what duration the pulse is effectively one wavelength ────────────
ax = axes[1]
tau_fs = np.linspace(1.0, 20.0, 400)
lo, hi = [], []
for t in tau_fs:
    cfg = SimConfig(lam_c=LAM_C, X_NA=0.8, n=N_MED, tau=t * 1e-15,
                    N_freq=3, N_theta=101)
    half = cfg.spectral_bandwidth / 2.0
    lo.append(2.0 * np.pi * C / (om_c + half) * 1000)
    hi.append(2.0 * np.pi * C / (om_c - half) * 1000 if om_c - half > 0
              else np.nan)
ax.fill_between(tau_fs, lo, hi, color='#d62728', alpha=0.16)
ax.plot(tau_fs, lo, '-', color='#d62728', lw=2.4)
ax.plot(tau_fs, hi, '-', color='#d62728', lw=2.4)
ax.axhline(LAM_C * 1000, color='#1d1d1f', lw=2.0)
ax.set_xlim(1.0, 20.0)
ax.set_xticks(np.arange(1, 21, 2))
ax.set_ylim(300, 1800)
ax.set_yticks(np.arange(400, 1801, 200))
ax.set_xlabel('Pulse duration (fs)')
ax.set_ylabel('Half-maximum span (nm)')
ax.set_title('Half-maximum wavelength span against pulse duration — center 750 nm',
             fontsize=12)
ax.grid(alpha=0.25, which='both')

plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUT, 'panels'), 'spectrum')
out = os.path.join(OUT, 'spectrum.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f'Saved -> {out}')

print(f"\n{'duration':>10} {'width THz':>11} {'width/carrier':>15} "
      f"{'half-maximum span':>26}")
for tau, lab, _c, _s in TAUS:
    cfg = SimConfig(lam_c=LAM_C, X_NA=0.8, n=N_MED, tau=tau,
                    N_freq=3, N_theta=101)
    bw = cfg.spectral_bandwidth
    lo = 2.0 * np.pi * C / (om_c + bw / 2) * 1000
    hi = 2.0 * np.pi * C / (om_c - bw / 2) * 1000
    hi_txt = f'{hi:.0f}' if om_c - bw / 2 > 0 else 'unbounded'
    print(f'{lab:>10} {bw / (2 * np.pi) / 1e12:>11.0f} '
          f'{bw / om_c:>15.2f} {lo:>14.0f} to {hi_txt:>8} nm')
