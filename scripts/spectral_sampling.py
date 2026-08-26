r"""
Spectral (wavelength) sampling for pulsed sources, and how the focal pattern
scales with wavelength — the answer to "is wavelength factored in, and does the
focus move?".

In the monochromatic (CW) launcher every photon has |k| = 2πn/λ_c (the centre
wavelength). For a PULSED source the wavelength is drawn from the power spectrum
|E(ω)|² ∝ exp[-(ω-ω_c)²/2a], a = 2ln2/τ²  (FWHM = 4ln2/τ) — panel (A). Converting
to the λ-domain needs the Jacobian |dω/dλ| = 2πc/λ² (∝ ω²), which shifts and
skews the peak — panel (B): the λ-probability is NOT the ω-Gaussian re-labelled.

The geometric focus stays at (r=0, z=0) for EVERY wavelength (fixed NA cone, no
lens dispersion in this ideal model); what changes is the pattern SCALE,
v = k sinα r ∝ r/λ, so the zeros/rings sit at different radii for different λ
(panels C, D). Summing intensities over the spectrum therefore washes out the
zeros — the Romallosa pulsed effect.

Output: output/05_pulsed_pupils/spectral_sampling.png
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo import SimConfig
from mcdo.annular import compute_integrals_annular

plt.rcParams.update({'font.size': 12, 'axes.titlesize': 12, 'axes.labelsize': 11,
                     'legend.fontsize': 9, 'axes.grid': True, 'grid.alpha': 0.25,
                     'savefig.dpi': 300})

LAM, N_MED, NT = 0.750, 1.3, 501
C_UM = 2.99792458e14
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '05_pulsed_pupils')
os.makedirs(OUT, exist_ok=True)

base = SimConfig(lam_c=LAM, X_NA=N_MED * 0.0 + 0.8, n=N_MED, tau=np.inf)
wc = base.omega_c
ydir = lambda I0, I1, I2: np.abs(I0 - I2) ** 2

fig, axes = plt.subplots(2, 2, figsize=(13.5, 9.5))
fig.suptitle('Pulsed wavelength sampling and the focal pattern vs λ '
             '(NA=0.8, λ_c=750 nm, n=1.3)', fontsize=14)

# (A) frequency probability |E(ω)|²
ax = axes[0, 0]
om = np.linspace(1e-3 * wc, 2 * wc, 2000)
for fs in (10, 5, 2, 1):
    cfg = SimConfig(lam_c=LAM, X_NA=0.8, n=N_MED, tau=fs * 1e-15)
    P = cfg.spectral_power(om); P = P / P.max()
    ax.plot(om / wc, P, lw=2, label=f'τ = {fs} fs')
ax.axvline(1.0, color='k', ls='--', lw=1, label='ω_c (centre)')
ax.set_xlabel('ω / ω_c'); ax.set_ylabel('P(ω) = |E(ω)|² (norm.)')
ax.set_title('(A) frequency probability — what we sample λ from')
ax.legend()

# (B) wavelength probability P(λ) ∝ P(ω)·ω²  (Jacobian) vs without
ax = axes[0, 1]
lam_nm = 2 * np.pi * C_UM / om * 1e3
for fs in (10, 5, 2, 1):
    cfg = SimConfig(lam_c=LAM, X_NA=0.8, n=N_MED, tau=fs * 1e-15)
    Pl = cfg.spectral_power(om) * om ** 2
    m = lam_nm < 2000
    ax.plot(lam_nm[m], (Pl / Pl[m].max())[m], lw=2, label=f'τ = {fs} fs')
cfg1 = SimConfig(lam_c=LAM, X_NA=0.8, n=N_MED, tau=1e-15)
Pno = cfg1.spectral_power(om); m = lam_nm < 2000
ax.plot(lam_nm[m], (Pno / Pno[m].max())[m], 'k:', lw=1.8,
        label='τ=1 fs, NO Jacobian (wrong)')
ax.axvline(750, color='k', ls='--', lw=1, label='λ_c = 750 nm')
ax.set_xlabel('λ (nm)'); ax.set_ylabel('P(λ) (norm.)')
ax.set_title('(B) wavelength probability — needs |dω/dλ|∝ω² Jacobian')
ax.legend(fontsize=8)

# (C) transverse y-cut |I0-I2|² at z=0 for 3 λ + the pulsed sum (zeros scale)
ax = axes[1, 0]
r_um = np.linspace(0, 1.6, 320)
for lam, col in [(0.55, 'C0'), (0.75, 'C1'), (1.10, 'C3')]:
    k = 2 * np.pi * N_MED / lam
    I0, I1, I2 = compute_integrals_annular(r_um, np.array([0.0]), k, base.alpha, 0.0, NT)
    I = ydir(I0[0], I1[0], I2[0]); I = I / I.max()
    ax.semilogy(r_um * 1e3, I, lw=1.8, color=col, label=f'λ = {lam*1e3:.0f} nm')
# pulsed sum over the 1 fs spectrum
cfg = SimConfig(lam_c=LAM, X_NA=0.8, n=N_MED, tau=1e-15)
oms = cfg.omega_grid(); Sw = cfg.spectral_power(oms)
Ip = np.zeros_like(r_um)
for o, s in zip(oms, Sw):
    if o <= 0:
        continue
    I0, I1, I2 = compute_integrals_annular(r_um, np.array([0.0]),
                                           cfg.n * o / C_UM, base.alpha, 0.0, NT)
    Ip += s * ydir(I0[0], I1[0], I2[0])
Ip = Ip / Ip.max()
ax.semilogy(r_um * 1e3, Ip, 'k-', lw=2.4, label='pulsed sum (1 fs)')
ax.set_ylim(1e-4, 2); ax.set_xlabel('r (nm)'); ax.set_ylabel('|I₀−I₂|² (norm.)')
ax.set_title('(C) transverse: zeros sit at different r per λ → pulsing fills them')
ax.legend(fontsize=8)

# (D) axial y-cut at r=0 for 3 λ + pulsed sum (peak fixed at z=0, scale ∝ λ)
ax = axes[1, 1]
z_um = np.linspace(-4, 4, 320)
for lam, col in [(0.55, 'C0'), (0.75, 'C1'), (1.10, 'C3')]:
    k = 2 * np.pi * N_MED / lam
    I0, I1, I2 = compute_integrals_annular(np.array([0.0]), z_um, k, base.alpha, 0.0, NT)
    I = ydir(I0[:, 0], I1[:, 0], I2[:, 0]); I = I / I.max()
    ax.plot(z_um, I, lw=1.8, color=col, label=f'λ = {lam*1e3:.0f} nm')
Ip = np.zeros_like(z_um)
for o, s in zip(oms, Sw):
    if o <= 0:
        continue
    I0, I1, I2 = compute_integrals_annular(np.array([0.0]), z_um,
                                           cfg.n * o / C_UM, base.alpha, 0.0, NT)
    Ip += s * ydir(I0[:, 0], I1[:, 0], I2[:, 0])
Ip = Ip / Ip.max()
ax.plot(z_um, Ip, 'k-', lw=2.4, label='pulsed sum (1 fs)')
ax.axvline(0, color='0.5', lw=0.8)
ax.set_xlabel('z (µm)'); ax.set_ylabel('|I₀−I₂|² (norm.)')
ax.set_title('(D) axial: peak stays at z=0 for all λ; lobe scales ∝ λ')
ax.legend(fontsize=8)

plt.tight_layout()
out = os.path.join(OUT, 'spectral_sampling.png')
fig.savefig(out, bbox_inches='tight'); plt.close(fig)
print(f"Saved → {out}")
