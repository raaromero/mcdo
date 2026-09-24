r"""Cambaliza & Saloma (2000): wavelength-gap dependence (Figs. 4-5) and annular
pupils (Figs. 6-7). The Monte Carlo scattering result (Fig. 8) is not
reproduced here.

Wavelength gap: 1/λ1 + 1/λ2 = 1/λe fixed at λe = 350 nm, Δλ = λ1 − λ2, the
shorter λ2 on lens L2, θ = π/2. The paper fits the transverse FWHM of
F2c(x, 0, 0; π/2) and the DOF (axial FWHM of F2c(0, 0, z; π/2)) linearly in Δλ
(Fig. 5, p. 30).

Annular: obstruction ratio ε = 0.99, both lenses, θ = 0, π/2, π [CS00 Eq. 4].

    python scripts/verify_2ce_cambaliza.py
    -> output/08_two_color/cambaliza_*.png, cambaliza_numbers.txt
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
matplotlib.rcParams.update({'font.size': 24, 'axes.titlesize': 32,
                            'axes.labelsize': 28, 'xtick.labelsize': 24,
                            'ytick.labelsize': 24, 'legend.fontsize': 24})

from mcdo.figio import save_panels
from mcdo.twobeam import beam_field

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color')
NA, N, LE = 0.5, 1.0, 0.350
xs = np.linspace(-1.0, 1.0, 1601)
zs = np.linspace(-5.0, 5.0, 4001)
LINES = []


def fwhm(s, y):
    y = y / y.max(); i0 = int(np.argmax(y))
    a = np.where(y[:i0] < 0.5)[0][-1]; b = i0 + np.where(y[i0:] < 0.5)[0][0]
    return (np.interp(0.5, [y[b], y[b - 1]], [s[b], s[b - 1]])
            - np.interp(0.5, [y[a], y[a + 1]], [s[a], s[a + 1]]))


def pair_lams(dl):
    """λ1, λ2 with λ1 − λ2 = dl and 1/λ1 + 1/λ2 = 1/λe."""
    # λ2 solves 1/(λ2 + dl) + 1/λ2 = 1/λe
    b = dl - 2 * LE
    l2 = (-b + np.sqrt(b ** 2 + 4 * LE * dl)) / 2
    return l2 + dl, l2


def F2c(xa, za, l1, l2, th, eps=0.0):
    I1 = np.abs(beam_field(xa, za, l1, NA, N, eps=eps)) ** 2
    I2 = np.abs(beam_field(xa, za, l2, NA, N, theta=th, eps=eps)) ** 2
    return I1 * I2


def F2p(xa, za, th, eps=0.0):
    U1 = beam_field(xa, za, 0.7, NA, N, eps=eps)
    U2 = beam_field(xa, za, 0.7, NA, N, theta=th, eps=eps)
    return np.abs(U1 + U2) ** 4


# ── wavelength gap ─────────────────────────────────────────────────────────
DL = np.array([0.010, 0.020, 0.030, 0.039, 0.050, 0.060, 0.070, 0.080, 0.094, 0.100])
W, D = [], []
fig, axes = plt.subplots(1, 3, figsize=(36.0, 10.0))
for dl in DL:
    l1, l2 = pair_lams(dl)
    t = F2c(xs, 0 * xs, l1, l2, np.pi / 2); a = F2c(0 * zs, zs, l1, l2, np.pi / 2)
    W.append(fwhm(xs, t)); D.append(fwhm(zs, a))
    if round(dl * 1000) in (10, 39, 94):
        lab = f'{dl*1000:.0f} nm ({l1*1000:.0f}, {l2*1000:.0f})'
        m = xs >= 0; mz = zs >= 0
        axes[0].plot(xs[m], (t / t.max())[m], lw=3.0, label=lab)
        axes[1].plot(zs[mz], (a / a.max())[mz], lw=3.0, label=lab)
W, D = np.array(W), np.array(D)
pw, pd = np.polyfit(DL * 1000, W, 1), np.polyfit(DL * 1000, D, 1)
axes[0].set_xlim(0, 1); axes[0].set_xlabel('x (µm)'); axes[0].set_title('Transverse, θ = π/2')
axes[1].set_xlim(0, 1); axes[1].set_xlabel('z (µm)'); axes[1].set_title('Axial, θ = π/2')
for a in axes[:2]:
    a.set_ylabel('Normalized 2CE fluorescence'); a.set_ylim(0, 1.05)
axes[2].plot(DL * 1000, W, 'o', ms=12, color='#1f77b4', label='FWHM')
axes[2].plot(DL * 1000, D, 's', ms=12, color='#d62728', label='DOF')
for p, c in ((pw, '#1f77b4'), (pd, '#d62728')):
    axes[2].plot(DL * 1000, np.polyval(p, DL * 1000), '-', color=c, lw=2.2)
axes[2].set_xlabel('Δλ (nm)'); axes[2].set_ylabel('Magnitude (µm)')
axes[2].set_title('FWHM and DOF against Δλ')
h0, l0 = axes[0].get_legend_handles_labels(); h2, l2_ = axes[2].get_legend_handles_labels()
fig.legend(h0 + h2, l0 + l2_, loc='upper center', bbox_to_anchor=(0.5, 0.02), ncol=5)
plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUT, 'panels'), 'cambaliza_wavelength_gap')
fig.savefig(os.path.join(OUT, 'cambaliza_wavelength_gap.png'), dpi=300, bbox_inches='tight')
plt.close(fig)
LINES.append(f"FWHM = {pw[0]:.2e} Δλ + {pw[1]:.4f}   (paper 2.4e-4 Δλ + ~0.712, Fig. 5)")
LINES.append(f"DOF  = {pd[0]:.2e} Δλ + {pd[1]:.4f}   (paper −4.81e-4 Δλ + 0.7112, Fig. 5)")
LINES.append(f"FWHM change 10→94 nm: {100*(W[DL==0.094][0]/W[0]-1):+.1f}%   (paper < 6%, p. 30)")

# ── annular ε = 0.99 ───────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(26.0, 18.0))
TH = [(0.0, 'θ = 0', '-'), (np.pi / 2, 'θ = π/2', '--'), (np.pi, 'θ = π', ':')]
AW = {}
for col, kind in enumerate(('2pe', '2ce')):
    for th, tlab, ls in TH:
        if kind == '2ce':
            t = F2c(xs, 0 * xs, 0.750, 0.656, th, 0.99); a = F2c(0 * zs, zs, 0.750, 0.656, th, 0.99)
        else:
            t = F2p(xs, 0 * xs, th, 0.99); a = F2p(0 * zs, zs, th, 0.99)
        t, a = t / t.max(), a / a.max()
        axes[0, col].plot(xs, t, ls, lw=3.0, label=tlab)
        axes[1, col].plot(zs, a, ls, lw=3.0, label=tlab)
        AW[(kind, th)] = (fwhm(xs, t), fwhm(zs, a) if a.min() < 0.5 else np.nan)
    tag = kind.upper()
    axes[0, col].set_title(f'{tag}, transverse, ε = 0.99'); axes[0, col].set_xlabel('x (µm)')
    axes[1, col].set_title(f'{tag}, axial, ε = 0.99'); axes[1, col].set_xlabel('z (µm)')
for a in axes.ravel():
    a.set_ylabel('Normalized fluorescence'); a.set_ylim(0, 1.05)
h, l = axes[0, 0].get_legend_handles_labels()
fig.legend(h, l, loc='upper center', bbox_to_anchor=(0.5, 0.02), ncol=3)
plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUT, 'panels'), 'cambaliza_annular')
fig.savefig(os.path.join(OUT, 'cambaliza_annular.png'), dpi=300, bbox_inches='tight')
plt.close(fig)

cw = lambda kind, th: fwhm(xs, F2c(xs, 0 * xs, 0.75, 0.656, th) if kind == '2ce'
                           else F2p(xs, 0 * xs, th))
ca = lambda kind, th: fwhm(zs, F2c(0 * zs, zs, 0.75, 0.656, th) if kind == '2ce'
                           else F2p(0 * zs, zs, th))
LINES.append("\nAnnular ε = 0.99, FWHM (µm): " + ", ".join(
    f"{k} {t:.2f}: {AW[(k, th)][0]:.3f} / axial {AW[(k, th)][1]:.3f}"
    for k in ('2pe', '2ce') for th, t in ((0.0, 0), (np.pi / 2, 1.57), (np.pi, 3.14))))
LINES.append(f"2CE annular transverse 0 / π/2 = {AW[('2ce', 0.0)][0]/AW[('2ce', np.pi/2)][0]:.2f}   (paper 0.82, p. 31)")
LINES.append(f"2CE annular 0 vs 2PE circular 0, transverse = {AW[('2ce', 0.0)][0]/cw('2pe', 0.0):.2f}   (paper ~0.70, p. 31)")
LINES.append(f"2PE annular π/2 vs 2CE annular π/2, transverse = {AW[('2pe', np.pi/2)][0]/AW[('2ce', np.pi/2)][0]:.2f}   (paper ~0.65, p. 31)")
LINES.append(f"2CE annular π/2 vs 2CE circular π/2, transverse = {AW[('2ce', np.pi/2)][0]/cw('2ce', np.pi/2):.2f}   (paper ~0.68, p. 31)")
LINES.append(f"2CE annular π/2 axial central spot = {AW[('2ce', np.pi/2)][1]:.2f} µm   (paper ~1 µm, p. 32)")
LINES.append(f"2CE annular π/2 vs 2CE circular π/2, axial = {AW[('2ce', np.pi/2)][1]/ca('2ce', np.pi/2):.2f}   (paper: 'about 40% narrower', p. 32)")
LINES.append(f"2CE annular π/2 vs 2PE circular π/2, axial = {AW[('2ce', np.pi/2)][1]/ca('2pe', np.pi/2):.2f}   (paper: '20% longer', p. 32)")
with open(os.path.join(OUT, 'cambaliza_numbers.txt'), 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(LINES) + '\n')
print('\n'.join(LINES))
