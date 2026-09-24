r"""Replication of the two-color (2CE) and two-photon (2PE) excitation results
of Cambaliza & Saloma (2000) and Lim & Saloma (2002), with the paraxial scalar
field they used, before any extension to Richards-Wolf or pulses.

Parameters from the papers: NA 0.5, n = 1, λ1 = 750 nm, λ2 = 656 nm for 2CE
(λe = 350 nm), λ = 700 nm for both 2PE beams [CS00 p. 28; LS02 p. 123].

Beam 2 is rotated in real space. The optical-coordinate rotation as written in
[LS02 p. 122] was tested and does not reproduce their peak-fluorescence numbers
(in-plane θ = π/2: −0.21 xc² against their −0.06 xc²); the real-space rotation
does.

    python scripts/verify_2ce_replication.py
    -> output/08_two_color/*.png, replication_numbers.txt
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
from mcdo.twobeam import beam_field, intensity

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color')
os.makedirs(OUT, exist_ok=True)

NA, N = 0.5, 1.0
L1, L2, L2P = 0.750, 0.656, 0.700
THETAS = [(0.0, 'θ = 0'), (np.pi / 2, 'θ = π/2'), (np.pi, 'θ = π')]
LEVELS = [1, 10, 20, 40, 60, 80]
LINES = []


def note(s):
    print(s)
    LINES.append(s)


def fields(x, z, theta, rot, pair='2ce', xc=0.0, zc=0.0):
    la, lb = (L1, L2) if pair == '2ce' else (L2P, L2P)
    U1 = beam_field(x, z, la, NA, N)
    U2 = beam_field(x, z, lb, NA, N, theta=theta, xc=xc, zc=zc, rotation=rot)
    return U1, U2


def signal(U1, U2, pair):
    F = intensity(U1) * intensity(U2) if pair == '2ce' else np.abs(U1 + U2) ** 4
    return F / F.max()


def fwhm(s, y):
    y = y / y.max()
    i0 = int(np.argmax(y))
    lo = np.where(y[:i0] < 0.5)[0]
    hi = np.where(y[i0:] < 0.5)[0]
    if not len(lo) or not len(hi):
        return np.nan
    a, b = lo[-1], i0 + hi[0]
    xa = np.interp(0.5, [y[a], y[a + 1]], [s[a], s[a + 1]])
    xb = np.interp(0.5, [y[b], y[b - 1]], [s[b], s[b - 1]])
    return xb - xa


# ── aligned point spread functions, x–z plane ─────────────────────────────
x = np.linspace(-1.0, 1.0, 201)
z = np.linspace(-5.0, 5.0, 401)
X, Z = np.meshgrid(x, z)

for rot in ('geometric',):
    fig, axes = plt.subplots(3, 2, figsize=(20.0, 30.0))
    for row, (th, tlab) in enumerate(THETAS):
        for col, pair in enumerate(('2pe', '2ce')):
            F = signal(*fields(X, Z, th, rot, pair), pair)
            ax = axes[row, col]
            cs = ax.contour(x, z, 100 * F, levels=LEVELS, colors='k', linewidths=1.4)
            ax.clabel(cs, fmt='%d', fontsize=14)
            ax.set_xlabel('x (µm)'); ax.set_ylabel('z (µm)')
            ax.set_title(f"{'2PE' if pair == '2pe' else '2CE'}, {tlab}")
            ax.set_xlim(-1, 1); ax.set_ylim(-5, 5)
    plt.tight_layout()
    name = f'psf_aligned_{rot}'
    save_panels(fig, fig.axes, os.path.join(OUT, 'panels'), name)
    fig.savefig(os.path.join(OUT, f'{name}.png'), dpi=300, bbox_inches='tight')
    plt.close(fig)

# ── transverse and axial profiles, with the papers' stated ratios ─────────
xs = np.linspace(-1.0, 1.0, 801)
zs = np.linspace(-5.0, 5.0, 2001)
note('Aligned profiles, NA 0.5, n = 1')
note(f"{'rotation':<10}{'pair':<5}{'θ':<8}{'transverse FWHM (µm)':>22}{'axial FWHM (µm)':>18}")
W = {}
for rot in ('geometric',):
    for pair in ('2pe', '2ce'):
        for th, tlab in THETAS:
            Ft = signal(*fields(xs, 0 * xs, th, rot, pair), pair)
            Fa = signal(*fields(0 * zs, zs, th, rot, pair), pair)
            W[(rot, pair, th)] = (fwhm(xs, Ft), fwhm(zs, Fa), Ft, Fa)
            note(f"{rot:<10}{pair:<5}{tlab:<8}{W[(rot, pair, th)][0]:>22.3f}"
                 f"{W[(rot, pair, th)][1]:>18.3f}")

note('\nRatios stated in Cambaliza & Saloma (2000), against ours:')
for rot in ('geometric',):
    t = lambda p, th: W[(rot, p, th)][0]
    a = lambda p, th: W[(rot, p, th)][1]
    note(f"  [{rot}] 2PE transverse π/2 / 0  = {t('2pe', np.pi/2)/t('2pe', 0):.2f}   (paper 0.67, p. 28)")
    note(f"  [{rot}] 2CE transverse 0 / π/2  = {t('2ce', 0)/t('2ce', np.pi/2):.2f}   (paper 0.75, p. 28)")
    note(f"  [{rot}] 2CE / 2PE transverse π/2 = {t('2ce', np.pi/2)/t('2pe', np.pi/2):.2f}   (paper 1.58, p. 29)")
    note(f"  [{rot}] 2CE / 2PE axial π/2      = {a('2ce', np.pi/2)/a('2pe', np.pi/2):.2f}   (paper ~2, p. 29)")

for rot in ('geometric',):
    fig, axes = plt.subplots(2, 2, figsize=(26.0, 18.0))
    for col, pair in enumerate(('2pe', '2ce')):
        for th, tlab in THETAS:
            _, _, Ft, Fa = W[(rot, pair, th)]
            ls = {0.0: '-', np.pi / 2: '--', np.pi: ':'}[th]
            axes[0, col].plot(xs, Ft, ls, lw=3.0, label=tlab)
            axes[1, col].plot(zs, Fa, ls, lw=3.0, label=tlab)
        tag = '2PE' if pair == '2pe' else '2CE'
        axes[0, col].set_title(f'{tag}, transverse'); axes[0, col].set_xlabel('x (µm)')
        axes[1, col].set_title(f'{tag}, axial'); axes[1, col].set_xlabel('z (µm)')
    for ax in axes.ravel():
        ax.set_ylabel('Normalized fluorescence'); ax.set_ylim(0, 1.05)
    h, l = axes[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc='upper center', bbox_to_anchor=(0.5, 0.02), ncol=3)
    plt.tight_layout()
    name = f'profiles_{rot}'
    save_panels(fig, fig.axes, os.path.join(OUT, 'panels'), name)
    fig.savefig(os.path.join(OUT, f'{name}.png'), dpi=300, bbox_inches='tight')
    plt.close(fig)

# ── peak fluorescence against focus offset (Lim & Saloma 2002, Fig. 4) ────
H = 0.0375                              # grid step (µm) = 0.05 λ1
xl = np.arange(-1.5, 1.5 + H / 2, H)
zl = np.arange(-6.0, 6.0 + H / 2, H)
XC = np.arange(-36, 37)                 # offsets in steps of H: ±1.35 µm = ±1.8 λ1
ZC = np.arange(-120, 121, 5)            # ±4.5 µm = ±6 λ1
pad_x, pad_z = XC.max(), ZC.max()
xe = np.arange(xl[0] - pad_x * H, xl[-1] + pad_x * H + H / 2, H)
ze = np.arange(zl[0] - pad_z * H, zl[-1] + pad_z * H + H / 2, H)
XL, ZL = np.meshgrid(xl, zl)
XE, ZE = np.meshgrid(xe, ze)


def peak_map(theta, rot, pair):
    la, lb = (L1, L2) if pair == '2ce' else (L2P, L2P)
    U1 = beam_field(XL, ZL, la, NA, N)
    U2e = beam_field(XE, ZE, lb, NA, N, theta=theta, rotation=rot)
    nz, nx = XL.shape
    out = np.zeros((ZC.size, XC.size))
    for i, dz in enumerate(ZC):
        for j, dx in enumerate(XC):
            # focus moved by (+dx, +dz): U2(P) = U2e(P - O')
            U2 = U2e[pad_z - dz: pad_z - dz + nz, pad_x - dx: pad_x - dx + nx]
            F = (np.abs(U1) ** 2 * np.abs(U2) ** 2 if pair == '2ce'
                 else np.abs(U1 + U2) ** 4)
            out[i, j] = F.max()
    return out / out[ZC.size // 2, XC.size // 2]


note('\nPeak 2CE fluorescence against focus offset (units of λ1 = 750 nm)')
lam_units = H / L1
fig, axes = plt.subplots(2, 2, figsize=(22.0, 22.0))
for row, (th, tlab) in enumerate([(np.pi, 'θ = π'), (np.pi / 2, 'θ = π/2')]):
    for col, pair in enumerate(('2ce', '2pe')):
        rot = 'geometric'
        P = peak_map(th, rot, pair)
        unit = H / (L1 if pair == '2ce' else L2P)
        ax = axes[row, col]
        cs = ax.contour(XC * unit, ZC * unit, 100 * P, levels=[10, 20, 40, 60, 80],
                        colors='k', linewidths=1.4)
        ax.clabel(cs, fmt='%d', fontsize=14)
        ax.set_xlabel('x$_c$ (λ$_1$)'); ax.set_ylabel('z$_c$ (λ$_1$)')
        ax.set_title(f"{'2CE' if pair == '2ce' else '2PE'}, {tlab}")
        if pair == '2ce':
            j0, i0 = XC.size // 2, ZC.size // 2
            xcu, zcu = XC * unit, ZC * unit
            sx, sz = np.abs(xcu) <= 1.33, np.abs(zcu) <= 2.7   # papers' ranges
            px = np.polyfit(xcu[sx], P[i0, sx], 2)
            pz = np.polyfit(zcu[sz], P[sz, j0], 2)
            note(f"  {tlab}: in-plane  F ≈ {px[0]:+.3f} xc² {px[2]:+.3f};"
                 f"  F(0.37 λ1) = {np.interp(0.37, xcu, P[i0, :]):.3f},"
                 f"  F(1.33 λ1) = {np.interp(1.33, xcu, P[i0, :]):.3f}")
            note(f"  {tlab}: axial     F ≈ {pz[0]:+.3f} zc² {pz[2]:+.3f};"
                 f"  F(1.8 λ1) = {np.interp(1.8, zcu, P[:, j0]):.3f},"
                 f"  F(2.7 λ1) = {np.interp(2.7, zcu, P[:, j0]):.3f}")
note("  paper (LS02 p. 126, 129): π/2 in-plane −0.06 xc² + 1, 11% drop at 1.33 λ1;"
     " θ = 0/π 20% drop at 0.37 λ1; π/2 axial −0.045 zc² + 0.986, 30% drop at 2.7 λ1;"
     " θ = 0/π axial −0.027 zc² + 0.996, 20% drop at 2.7 λ1")
plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUT, 'panels'), 'peak_vs_offset')
fig.savefig(os.path.join(OUT, 'peak_vs_offset.png'), dpi=300, bbox_inches='tight')
plt.close(fig)

with open(os.path.join(OUT, 'replication_numbers.txt'), 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(LINES) + '\n')
print('Saved ->', OUT)
