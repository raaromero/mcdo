"""Few-cycle pulse characteristics — what a short pulse does to the spectrum.

Panels (also saved individually to output/05_pulsed_pupils/panels/):
  p1 — power spectrum against wavelength, for a range of pulse durations
  p2 — the same spectra against frequency, where the Gaussian is symmetric
  p3 — spectral bandwidth against pulse duration, showing the 1/tau scaling
  p4 — coherence length against pulse duration, against the Nyquist interval

The asymmetry in p1 is a change of variable, not physics: the spectrum is a
symmetric Gaussian in frequency (p2) and acquires its long-wavelength tail only
when mapped through lambda = 2 pi c / omega.

The critical duration is where the coherence length falls below the Nyquist
sampling interval lambda_c / 2, beyond which the carrier can no longer be
represented without aliasing [Rom03].
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo.style import apply as _apply_style
_apply_style()

from mcdo import SimConfig
from mcdo.figio import save_panels

LAM_C, N_MED = 0.750, 1.3
C_UM = 2.99792458e14                      # micrometres per second
TAUS_FS = [1.0, 1.5, 2.0, 3.0, 5.0]
OUTDIR = os.path.join(os.path.dirname(__file__), '..', 'output', '05_pulsed_pupils')
COLORS = plt.cm.viridis(np.linspace(0.0, 0.85, len(TAUS_FS)))

fig, axes = plt.subplots(2, 2, figsize=(20.5, 13.0))
omega_c = 2 * np.pi * C_UM / LAM_C

# ── p1 / p2: the spectrum on both axes ────────────────────────────────────
for tau_fs, c in zip(TAUS_FS, COLORS):
    cfg = SimConfig(lam_c=LAM_C, X_NA=0.8, n=N_MED, tau=tau_fs * 1e-15,
                    N_freq=801, N_theta=101)
    w = cfg.omega_grid()
    S = cfg.spectral_power(w)
    good = w > 0
    w, S = w[good], S[good] / S[good].max()
    lam_nm = 2 * np.pi * C_UM / w * 1e3
    order = np.argsort(lam_nm)
    axes[0, 0].plot(lam_nm[order], S[order], color=c, lw=2, label=f'{tau_fs:g} fs')
    axes[0, 1].plot(w / omega_c, S, color=c, lw=2, label=f'{tau_fs:g} fs')

ax = axes[0, 0]
ax.axvline(LAM_C * 1e3, color='#c0504d', ls='--', lw=1.2,
           label=f'Centre wavelength {LAM_C * 1e3:.0f} nm')
ax.set_xlim(300, 1800); ax.set_ylim(0, 1.05)
ax.set_xlabel('Wavelength (nm)'); ax.set_ylabel('Normalized spectral power')
ax.set_title('(a) Spectrum against wavelength, centre 750 nm', fontsize=11)
ax.grid(alpha=0.25); ax.legend(fontsize=9, title='Pulse Duration')

ax = axes[0, 1]
ax.axvline(1.0, color='#c0504d', ls='--', lw=1.2,
           label=f'Carrier frequency, {LAM_C * 1e3:.0f} nm')
ax.set_xlim(0, 2); ax.set_ylim(0, 1.05)
ax.set_xlabel('Frequency, in units of the carrier'); ax.set_ylabel('Normalized spectral power')
ax.set_title('(b) Spectrum against frequency, centre 750 nm', fontsize=11)
ax.grid(alpha=0.25); ax.legend(fontsize=9, title='Pulse Duration')

# ── p3: bandwidth against duration ────────────────────────────────────────
tau_fine = np.linspace(0.8, 10.0, 120)
bandwidth_hz = 4 * np.log(2) / (2 * np.pi * tau_fine * 1e-15)      # FWHM of |E(w)|^2, in Hz
ax = axes[1, 0]
ax.loglog(tau_fine, bandwidth_hz * 1e-12, color='#1f77b4', lw=2,
          label='spectral width, full width at half maximum')
for tau_fs, c in zip(TAUS_FS, COLORS):
    bw = 4 * np.log(2) / (2 * np.pi * tau_fs * 1e-15)
    ax.plot(tau_fs, bw * 1e-12, 'o', color=c, ms=7)
ax.set_xlabel('Pulse duration (fs)'); ax.set_ylabel('Spectral width (THz)')
ax.set_title('(c) Bandwidth against pulse duration', fontsize=11)
ax.grid(alpha=0.25, which='both'); ax.legend(fontsize=9)

# ── p4: coherence length against the sampling limit ───────────────────────
coh_nm = C_UM * tau_fine * 1e-15 * 1e3
nyquist_nm = LAM_C * 1e3 / 2
tau_crit = nyquist_nm / (C_UM * 1e-15 * 1e3)
ax = axes[1, 1]
ax.plot(tau_fine, coh_nm, color='#1f77b4', lw=2, label='coherence length')
ax.axhline(nyquist_nm, color='#c0504d', ls='--', lw=1.2,
           label=f'Nyquist interval, {nyquist_nm:.0f} nm')
ax.axvline(tau_crit, color='#888', ls=':', lw=1.2)
ax.fill_between(tau_fine, 0, coh_nm, where=(coh_nm < nyquist_nm),
                color='#c0504d', alpha=0.18, label='below the sampling limit')
ax.text(tau_crit, coh_nm.max() * 0.92, f'  critical duration {tau_crit:.2f} fs',
        fontsize=9, color='#444')
ax.set_xlim(tau_fine[0], tau_fine[-1]); ax.set_ylim(0, coh_nm.max())
ax.set_xlabel('Pulse duration (fs)'); ax.set_ylabel('Length (nm)')
ax.set_title('(d) Coherence length against pulse duration', fontsize=11)
ax.grid(alpha=0.25); ax.legend(fontsize=9, loc='lower right')

print(f'Carrier wavelength {LAM_C * 1e3:.0f} nm, Nyquist interval {nyquist_nm:.0f} nm')
print(f'Critical pulse duration = lambda_c / (2c) = {tau_crit:.2f} fs')
for tau_fs in TAUS_FS:
    coh = C_UM * tau_fs * 1e-15 * 1e3
    bw = 4 * np.log(2) / (2 * np.pi * tau_fs * 1e-15)
    flag = '  below Nyquist' if coh < nyquist_nm else ''
    print(f'  tau={tau_fs:>4g} fs:  coherence {coh:6.1f} nm   bandwidth {bw * 1e-12:6.1f} THz{flag}')

plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUTDIR, 'panels'), 'fig_pulse_characteristics')
out = os.path.join(OUTDIR, 'fig_pulse_characteristics.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f'Saved → {out}')
