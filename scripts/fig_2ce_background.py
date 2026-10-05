r"""Background figures for the two-color excitation notes, from first principles.

    python scripts/fig_2ce_background.py
    -> output/08_two_color/bg_*.png

bg_focusing_geometry   aplanatic focusing: sine condition, reference sphere,
                       and the tilt of the polarization that creates E_z
bg_low_high_na         Richards-Wolf against the paraxial scalar field, NA 0.5
                       and 1.2: transverse cuts, components, axial profile
bg_nonlinear           per-plane signal ∫ I^m dA against z for 1PE and 2PE
bg_energy_levels       1PE, 2PE and 2CE transitions
bg_beating             |E1 + E2|² in time: same color against two colors
bg_pulse_overlap       spectra of 750 nm and 656 nm pulses at 1, 5 and 20 fs
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, FancyArrowPatch

from mcdo.style import apply as _apply_style
_apply_style()
matplotlib.rcParams.update({'font.size': 24, 'axes.titlesize': 32,
                            'axes.labelsize': 28, 'xtick.labelsize': 24,
                            'ytick.labelsize': 24, 'legend.fontsize': 24})

from mcdo.twobeam import beam_field, intensity

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color')
os.makedirs(OUT, exist_ok=True)
C1, C2, C3 = '#d62728', '#1f77b4', '#2ca02c'


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=600, bbox_inches='tight')
    plt.close(fig)
    print('Saved ->', name)


# ── focusing geometry ─────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(11.0, 6.8))
f = 6.0
alpha = np.deg2rad(50)
ax.plot([0, 0], [-f * np.sin(alpha) - 0.6, f * np.sin(alpha) + 0.6], color='k', lw=3)
ax.text(-0.3, f * np.sin(alpha) + 0.9, 'Aplanatic lens', ha='right', fontsize=26)
th = np.linspace(-alpha, alpha, 200)
ax.plot(f - f * np.cos(th), f * np.sin(th), '--', color='#555555', lw=2)
ax.text(f - f * np.cos(alpha) + 0.3, f * np.sin(alpha) + 0.1, 'Reference sphere, radius f',
        fontsize=24, ha='left')
F = np.array([f, 0.0])
ax.plot(*F, 'o', color='k', ms=12)
ax.text(f + 0.1, -1.0, 'Focus', fontsize=26, va='top')
ax.plot([-3.5, f + 2.5], [0, 0], color='#999999', lw=1.4)
ax.text(f + 2.7, 0, 'z', fontsize=28, va='center')
for t, col in ((np.deg2rad(40), C1), (np.deg2rad(-20), C2)):
    h = f * np.sin(t)
    S = np.array([f - f * np.cos(t), h])
    ax.plot([-3.5, 0], [h, h], color=col, lw=2.6)
    ax.plot([0, S[0]], [h, h], color=col, lw=2.6, ls=':')
    ax.annotate('', xy=F, xytext=S, arrowprops=dict(arrowstyle='-|>', color=col, lw=2.6,
                                                    mutation_scale=26))
    # polarization in the meridional plane: before (vertical) and after (⊥ to ray)
    ax.annotate('', xy=(-2.2, h + 0.9), xytext=(-2.2, h - 0.9),
                arrowprops=dict(arrowstyle='<->', color=col, lw=2.4))
    d = (F - S) / np.linalg.norm(F - S)
    p = np.array([-d[1], d[0]])
    m = S + 0.45 * (F - S)
    ax.annotate('', xy=m + 0.9 * p, xytext=m - 0.9 * p,
                arrowprops=dict(arrowstyle='<->', color=col, lw=2.4))
ax.annotate('', xy=(-0.25, f * np.sin(np.deg2rad(40))), xytext=(-0.25, 0),
            arrowprops=dict(arrowstyle='<->', color='k', lw=1.6))
ax.text(-0.75, 1.9, 'h = f sin β', fontsize=24, ha='right', rotation=90, va='center')
ax.add_patch(Arc(F, 3.0, 3.0, theta1=180 - 40, theta2=180, color='k', lw=2))
ax.text(f - 1.95, 0.45, 'β', fontsize=28)
ax.text(-0.4, -4.4, 'Incident polarization:\ntransverse to z', fontsize=22, va='top', ha='right')
ax.text(3.0, -3.6, 'After the lens: transverse to each ray,\nso a component along z appears',
        fontsize=22, va='top')
ax.set_aspect('equal'); ax.axis('off')
ax.set_xlim(-5.5, f + 5.0); ax.set_ylim(-6.2, 5.8)
save(fig, 'bg_focusing_geometry.png')

# ── low against high NA ───────────────────────────────────────────────────
lam, n = 0.75, 1.3
xs = np.linspace(-1.6, 1.6, 641)          # in units of λ
zz = np.linspace(-6.0, 6.0, 1201)
fig, axes = plt.subplots(2, 3, figsize=(36.0, 20.0))
for r, na in enumerate((0.5, 1.2)):
    x = xs * lam
    Ex = beam_field(x, 0 * x, lam, na, n, model='rw', psi=0.0)          # along polarization
    Ey = beam_field(x, 0 * x, lam, na, n, model='rw', psi=np.pi / 2)    # across it
    Ip = intensity(beam_field(x, 0 * x, lam, na, n, model='paraxial'))
    Ia, Ib = intensity(Ex), intensity(Ey)
    ax = axes[r, 0]
    ax.plot(xs, Ia / Ia.max(), '-', color=C1, lw=3.2, label='Richards–Wolf, along polarization')
    ax.plot(xs, Ib / Ib.max(), '-', color=C2, lw=3.2, label='Richards–Wolf, across polarization')
    ax.plot(xs, Ip / Ip.max(), '--', color='k', lw=2.4, label='Paraxial scalar')
    ax.set_title(f'Transverse, NA {na:g}'); ax.set_xlabel('x / λ')
    ax.set_ylabel('Normalized intensity'); ax.set_ylim(0, 1.05)
    ax = axes[r, 1]
    tot = Ia.max()
    for k, (lab, col) in ((0, ('|E$_x$|²', '#9467bd')), (2, ('|E$_z$|², longitudinal', '#ff7f0e'))):
        ax.plot(xs, np.abs(Ex[k]) ** 2 / tot, '-', color=col, lw=3.2, label=lab)
    ax.set_yscale('log'); ax.set_ylim(1e-4, 1.2)
    ax.set_title(f'Components along the polarization axis, NA {na:g}\n(|E$_y$|² = 0 on this axis)'); ax.set_xlabel('x / λ')
    ax.set_ylabel('Relative to peak |E|²')
    ax = axes[r, 2]
    z = zz * lam
    Iz = intensity(beam_field(0 * z, z, lam, na, n, model='rw', psi=0.0))
    Izp = intensity(beam_field(0 * z, z, lam, na, n, model='paraxial'))
    ax.plot(zz, Iz / Iz.max(), '-', color=C1, lw=3.2, label='Richards–Wolf')
    ax.plot(zz, Izp / Izp.max(), '--', color='k', lw=2.4)
    ax.set_title(f'Axial, NA {na:g}'); ax.set_xlabel('z / λ')
    ax.set_ylabel('Normalized intensity'); ax.set_ylim(0, 1.05)
h, l = axes[0, 0].get_legend_handles_labels(); h2, l2 = axes[0, 1].get_legend_handles_labels()
fig.legend(h + h2, l + l2, loc='upper center', bbox_to_anchor=(0.5, 0.02), ncol=3)
plt.tight_layout()
save(fig, 'bg_low_high_na.png')

# ── nonlinear confinement ─────────────────────────────────────────────────
r = np.linspace(0, 25.0, 2501)
zp = np.linspace(-12, 12, 121)
S1, S2 = [], []
for zi in zp:
    I = intensity(beam_field(r, np.full_like(r, zi), 0.7, 0.5, 1.0, model='paraxial'))
    S1.append(np.trapezoid(I * r, r)); S2.append(np.trapezoid(I ** 2 * r, r))
S1, S2 = np.array(S1), np.array(S2)
fig, ax = plt.subplots(figsize=(10.0, 6.2))
ax.plot(zp, S1 / S1[60], '-', color=C2, lw=3.4, label='One-photon, ∫ I dA')
ax.plot(zp, S2 / S2[60], '-', color=C1, lw=3.4, label='Two-photon, ∫ I² dA')
ax.set_xlabel('Axial position z (µm)'); ax.set_ylabel('Signal per plane')
ax.set_ylim(0, 1.1)
fig.legend(loc='upper center', bbox_to_anchor=(0.5, 0.02), ncol=2)
plt.tight_layout()
save(fig, 'bg_nonlinear.png')

# ── energy levels ─────────────────────────────────────────────────────────
HC = 1239.84
fig, ax = plt.subplots(figsize=(13.0, 7.0))
E_e = HC / 350
for x0, title, steps in ((0.0, 'One-photon\n350 nm', [(350, C3)]),
                         (4.0, 'Two-photon\n700 + 700 nm', [(700, C1), (700, C1)]),
                         (8.0, 'Two-color\n750 + 656 nm', [(750, C1), (656, C2)])):
    ax.plot([x0 - 1.2, x0 + 1.2], [0, 0], color='k', lw=3)
    ax.plot([x0 - 1.2, x0 + 1.2], [E_e, E_e], color='k', lw=3)
    e = 0.0
    for i, (lam_nm, col) in enumerate(steps):
        de = HC / lam_nm
        ax.annotate('', xy=(x0, e + de), xytext=(x0, e),
                    arrowprops=dict(arrowstyle='-|>', color=col, lw=4, mutation_scale=30))
        ax.text(x0 + 0.15, e + de / 2, f'{lam_nm} nm\n{de:.2f} eV', fontsize=22, va='center',
                color=col)
        e += de
        if i == 0 and len(steps) > 1:
            ax.plot([x0 - 1.0, x0 + 1.0], [e, e], '--', color='#777777', lw=2)
    ax.text(x0, -0.9, title, ha='center', va='top', fontsize=26)
ax.text(9.3, HC / 750, 'Virtual state', fontsize=22, color='#555555', va='center')
ax.text(-1.3, E_e + 0.15, f'Excited state, {E_e:.2f} eV', fontsize=22)
ax.text(-1.3, -0.3, 'Ground state', fontsize=22, va='top')
ax.set_xlim(-1.6, 11.2); ax.set_ylim(-2.3, E_e + 0.7); ax.axis('off')
save(fig, 'bg_energy_levels.png')

# ── beating ───────────────────────────────────────────────────────────────
c = 299.792458          # nm/fs
t = np.linspace(0, 60, 6001)
w1, w2 = 2 * np.pi * c / 750, 2 * np.pi * c / 656
fig, axes = plt.subplots(1, 2, figsize=(13.0, 5.6))
for ph, ls, lab in ((0.0, '-', 'relative phase 0'), (np.pi, '--', 'relative phase π')):
    E = np.exp(-1j * w1 * t) + np.exp(-1j * (w1 * t + ph))
    axes[0].plot(t, np.abs(E) ** 2, ls, color=C1, lw=3.2, label=lab)
E = np.exp(-1j * w1 * t) + np.exp(-1j * w2 * t)
axes[1].plot(t, np.abs(E) ** 2, '-', color=C2, lw=3.2, label='750 + 656 nm')
axes[1].axhline(2.0, color='k', ls=':', lw=2.4, label='Time average = I$_1$ + I$_2$')
axes[0].set_title('Same color')
axes[1].set_title('Two colors, 750 + 656 nm')
for a in axes:
    a.set_xlabel('Time (fs)'); a.set_ylabel('|E$_1$ + E$_2$|²'); a.set_ylim(-0.1, 4.3)
h, l = axes[0].get_legend_handles_labels(); h2, l2 = axes[1].get_legend_handles_labels()
fig.legend(h + h2, l + l2, loc='upper center', bbox_to_anchor=(0.5, 0.02), ncol=4)
plt.tight_layout()
save(fig, 'bg_beating.png')

# ── pulse spectra overlap ─────────────────────────────────────────────────
fnu = np.linspace(0, 900, 4000)            # THz
fig, axes = plt.subplots(1, 3, figsize=(36.0, 9.5), sharey=True)
for ax, tau in zip(axes, (1.0, 5.0, 20.0)):
    fwhm = 0.441 / tau * 1000              # THz
    sig = fwhm / (2 * np.sqrt(2 * np.log(2)))
    S1 = np.exp(-(fnu - c * 1000 / 750) ** 2 / (2 * sig ** 2))
    S2 = np.exp(-(fnu - c * 1000 / 656) ** 2 / (2 * sig ** 2))
    ov = np.trapezoid(np.minimum(S1, S2), fnu) / np.trapezoid(S1, fnu)
    ax.fill_between(fnu, S1, color=C1, alpha=0.35, lw=0)
    ax.fill_between(fnu, S2, color=C2, alpha=0.35, lw=0)
    ax.plot(fnu, S1, color=C1, lw=3.0, label='750 nm pulse')
    ax.plot(fnu, S2, color=C2, lw=3.0, label='656 nm pulse')
    ax.set_title(f'{tau:g} fs: shared area ' + ('<1%' if ov < 0.01 else f'{100*ov:.0f}%'))
    ax.set_xlabel('Frequency (THz)')
axes[0].set_ylabel('Spectral power, normalized')
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, loc='upper center', bbox_to_anchor=(0.5, 0.02), ncol=2)
plt.tight_layout()
save(fig, 'bg_pulse_overlap.png')
