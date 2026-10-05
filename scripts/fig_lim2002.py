r"""Lim & Saloma (2002), Opt. Commun. 207, 121: every figure, in the paper's layout.

Paraxial scalar field at NA 0.5, n = 1 [LS02 p. 122-123]. 2CE: λ1 = 750 nm on L1,
λ2 = 656 nm on L2. 2PE: 700 nm on both. Beam 2 rotated by θ in real space, focus
moved to O' = (xc, zc). PSFs normalized to 100 at their peak; contours 1, 10, 20,
40, 60, 80 (Figs. 2-3). Offsets in units of λ1 (750 nm for 2CE, 700 nm for 2PE),
xc ∈ [−1, 1], zc ∈ [−6, 6] (Figs. 4-6).

    python scripts/fig_lim2002.py
    -> output/08_two_color/lim2002/fig1..fig6.png, lim2002_numbers.txt
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Ellipse, FancyArrowPatch, Polygon

from mcdo.style import apply as _apply_style
_apply_style()
matplotlib.rcParams.update({'font.size': 24, 'axes.titlesize': 32,
                            'axes.labelsize': 28, 'xtick.labelsize': 24,
                            'ytick.labelsize': 24, 'legend.fontsize': 24})

from mcdo.figio import save_panels
from mcdo.twobeam import beam_field

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002')
os.makedirs(OUT, exist_ok=True)
NA, N = 0.5, 1.0
LAMS = {'2ce': (0.750, 0.656), '2pe': (0.700, 0.700)}
LEVELS = [1, 10, 20, 40, 60, 80]
LINES = []


def note(s):
    print(s); LINES.append(s)


def save(fig, name):
    save_panels(fig, fig.axes, os.path.join(OUT, 'panels'), name[:-4], dpi=600)
    fig.savefig(os.path.join(OUT, name), dpi=600, bbox_inches='tight')
    plt.close(fig); print('Saved ->', name)


def signal(U1, U2, pair):
    return np.abs(U1) ** 2 * np.abs(U2) ** 2 if pair == '2ce' else np.abs(U1 + U2) ** 4


def psf(X, Z, pair, theta, xc=0.0, zc=0.0):
    la, lb = LAMS[pair]
    U1 = beam_field(X, Z, la, NA, N)
    U2 = beam_field(X, Z, lb, NA, N, theta=theta, xc=xc, zc=zc)
    return signal(U1, U2, pair)


# ── Fig. 1: geometry ──────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9.5, 9.5))
ax.set_aspect('equal'); ax.axis('off')
ax.set_xlim(-4.2, 6.6); ax.set_ylim(5.4, -5.4)
ax.annotate('', xy=(6.2, 0), xytext=(-3.6, 0), arrowprops=dict(arrowstyle='->', lw=2.0))
ax.annotate('', xy=(0, 5.0), xytext=(0, -5.0), arrowprops=dict(arrowstyle='->', lw=2.0))
ax.text(6.3, 0, 'x', fontsize=30, va='center'); ax.text(0.15, 5.2, 'z', fontsize=30)
# beam 1 along z to O
ax.add_patch(Polygon([(-1.1, -3.4), (0, 0), (1.1, -3.4)], fc='#d62728', alpha=0.15, lw=0))
for s in (-1, 1):
    ax.plot([s * 1.1, 0], [-3.4, 0], color='#d62728', lw=2.6)
    ax.plot([s * 0.9, s * 0.9], [-4.9, -3.4], color='#d62728', lw=2.6)
ax.add_patch(Ellipse((0, -3.4), 2.6, 0.45, fc='white', ec='k', lw=2.4, zorder=4))
ax.text(1.5, -3.4, 'L1', fontsize=30, va='center')
ax.text(-1.2, -4.6, 'Beam 1, λ$_1$', fontsize=26, color='#d62728', ha='right')
# beam 2 at θ to O'
th = np.deg2rad(70)
Op = np.array([1.2, 1.4])
d = np.array([-np.sin(th), np.cos(th)])          # arrives from the right, tilted
d = -np.array([np.cos(np.deg2rad(20)), -np.sin(np.deg2rad(20))])
p = np.array([-d[1], d[0]])
Lc = Op - 3.6 * d
ax.add_patch(Polygon([Lc + 1.1 * p, Op, Lc - 1.1 * p], fc='#1f77b4', alpha=0.15, lw=0))
for s in (1, -1):
    ax.plot([Lc[0] + s * 1.1 * p[0], Op[0]], [Lc[1] + s * 1.1 * p[1], Op[1]], color='#1f77b4', lw=2.6)
    a = Lc + s * 0.9 * p
    ax.plot([a[0], a[0] - 1.5 * d[0]], [a[1], a[1] - 1.5 * d[1]], color='#1f77b4', lw=2.6)
ang = np.degrees(np.arctan2(p[1], p[0]))
ax.add_patch(Ellipse(Lc, 2.6, 0.45, angle=ang, fc='white', ec='k', lw=2.4, zorder=4))
ax.text(Lc[0] + 0.2, Lc[1] - 1.5, 'L2', fontsize=30)
ax.text(Lc[0] - 1.5 * d[0] + 0.3, Lc[1] - 1.5 * d[1] + 1.3, 'Beam 2, λ$_2$', fontsize=26,
        color='#1f77b4')
# axis of L2 and angle θ
ax.plot([Op[0] - 5.0 * d[0], Op[0] + 0.8 * d[0]], [Op[1] - 5.0 * d[1], Op[1] + 0.8 * d[1]],
        ':', color='#1f77b4', lw=2.0)
ax.add_patch(Arc(Op, 2.2, 2.2, theta1=-20, theta2=90, color='k', lw=2))
ax.plot([Op[0], Op[0]], [Op[1], Op[1] + 1.4], ':', color='k', lw=2.0)
ax.text(Op[0] + 0.95, Op[1] + 0.95, 'θ', fontsize=30)
for pt, lab, off in (((0, 0), 'O', (-0.45, -0.3)), (tuple(Op), 'O′', (-0.6, 0.55))):
    ax.plot(*pt, 'o', color='k', ms=11, zorder=6)
    ax.text(pt[0] + off[0], pt[1] + off[1], lab, fontsize=30)
ax.plot([Op[0], Op[0]], [0, Op[1]], '--', color='#555555', lw=2.0)
ax.plot([0, Op[0]], [Op[1], Op[1]], '--', color='#555555', lw=2.0)
ax.text(Op[0] / 2, -0.25, 'x$_c$', fontsize=26, ha='center')
ax.text(-0.2, Op[1], 'z$_c$', fontsize=26, ha='right', va='center')
ax.text(-3.5, -1.2, 'U$_1$(P; λ$_1$)', fontsize=26, color='#d62728')
ax.text(-3.5, 3.4, 'U$_2$(P; λ$_2$, θ)', fontsize=26, color='#1f77b4')
save(fig, 'fig1_geometry.png')

# ── Figs. 2 and 3: contour plots ──────────────────────────────────────────
x = np.linspace(-1.0, 1.0, 201)
z = np.linspace(-5.0, 5.0, 201)
X, Z = np.meshgrid(x, z)
PANELS = [('2ce', np.pi, 'a', '2CE, θ = π'), ('2pe', np.pi, 'b', '2PE, θ = π'),
          ('2ce', np.pi / 2, 'c', '2CE, θ = π/2'), ('2pe', np.pi / 2, 'd', '2PE, θ = π/2')]
for fig_no, (xc, zc) in ((2, (0.0, 0.0)), (3, (0.4, 1.0))):
    fig, axes = plt.subplots(2, 2, figsize=(15.0, 15.0))
    for ax, (pair, th, tag, lab) in zip(axes.ravel(), PANELS):
        F = psf(X, Z, pair, th, xc, zc)
        F = 100 * F / F.max()
        cs = ax.contour(x, z, F, levels=LEVELS, colors='k', linewidths=2.0)
        ax.clabel(cs, fmt='%d', fontsize=24)
        ax.set_xlabel('x (µm)'); ax.set_ylabel('z (µm)')
        ax.set_box_aspect(1.0)                  # the paper's frames are square
        ax.set_xticks([-1.0, -0.5, 0.0, 0.5, 1.0]); ax.set_yticks(np.arange(-5, 6, 1))
        ax.tick_params(axis='x', pad=14)             # keeps −1.0 clear of the −5 on the z axis
        ax.set_title(f'({tag}) {lab}')
        iz, ix = np.unravel_index(np.argmax(F), F.shape)
        note(f"Fig. {fig_no} ({tag}) {lab}: peak at x = {x[ix]:+.3f}, z = {z[iz]:+.3f} µm")
    plt.tight_layout()
    save(fig, f'fig{fig_no}_contours.png')
note("paper Fig. 3 text (p. 126): 2CE π peak at the midpoint of O and O′ (0.2, 0.5); "
     "2CE π/2 peak shifted only along z")

# ── offset grids for Figs. 4-6 (window 100 × 100-like, ±1 × ±5 µm) ────────
def offset_maps(pair, theta, want_linfoot):
    la, lb = LAMS[pair]
    unit = la                                   # axes in units of λ1 (λ2p for 2PE)
    # the paper's offsets span the same physical range for 2CE and 2PE,
    # ±1 µm across and ±5 µm along, read off its Fig. 4 frames
    dx, dz = 0.02, 0.1                          # µm
    nx, nz = 50, 50                             # window ±1 × ±5 µm (100 × 100 points)
    xw = np.arange(-nx, nx) * dx; zw = np.arange(-nz, nz) * dz
    IX = np.arange(-50, 51, 2); IZ = np.arange(-50, 51, 2)
    px, pz = IX.max(), IZ.max()
    xe = np.arange(-nx - px, nx + px) * dx; ze = np.arange(-nz - pz, nz + pz) * dz
    XW, ZW = np.meshgrid(xw, zw); XE, ZE = np.meshgrid(xe, ze)
    U1 = beam_field(XW, ZW, la, NA, N)
    U2e = beam_field(XE, ZE, lb, NA, N, theta=theta)
    sz, sx = XW.shape
    t = signal(U1, U2e[pz:pz + sz, px:px + sx], pair)
    tn = t / t.max(); t2 = np.mean(tn ** 2)
    P = np.zeros((IZ.size, IX.size)); Fm = np.zeros_like(P); Cm = np.zeros_like(P); Qm = np.zeros_like(P)
    for i, iz in enumerate(IZ):
        for j, ix in enumerate(IX):
            a = signal(U1, U2e[pz - iz:pz - iz + sz, px - ix:px - ix + sx], pair)
            P[i, j] = a.max() / t.max()
            if want_linfoot:
                an = a / a.max()
                Fm[i, j] = 1 - np.mean((tn - an) ** 2) / t2
                Cm[i, j] = np.mean(an ** 2) / t2
                Qm[i, j] = np.mean(np.abs(an) * np.abs(tn)) / t2
    return IX * dx / unit, IZ * dz / unit, P, Fm, Cm, Qm


MAPS = {}
for pair in ('2ce', '2pe'):
    for th in (np.pi, np.pi / 2):
        MAPS[(pair, th)] = offset_maps(pair, th, True)
# 2PE at θ = 0 (co-propagating): the paper's Fig. 6(c)–(d), captioned θ = π/2, resemble this case
MAPS[('2pe', 0.0)] = offset_maps('2pe', 0.0, True)

# ── Fig. 4: peak fluorescence ─────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(15.0, 15.7))
for ax, (pair, th, tag, lab) in zip(axes.ravel(), PANELS):
    xc, zc, P, *_ = MAPS[(pair, th)]
    cs = ax.contour(xc, zc, 100 * P, levels=[10, 20, 40, 60, 80], colors='k', linewidths=2.0)
    ax.clabel(cs, fmt='%d', fontsize=24)
    u = 'λ$_1$' if pair == '2ce' else 'λ$_{2p}$'   # 2PE offsets are in units of its 700 nm wavelength
    ax.set_xlabel(f'x$_c$ ({u})'); ax.set_ylabel(f'z$_c$ ({u})')
    ax.set_box_aspect(1.0)                      # the paper's Fig. 4 frames are square
    ax.set_xticks([-1.0, -0.5, 0.0, 0.5, 1.0]); ax.set_yticks(np.arange(-6, 7, 2))
    ax.set_title(f'({tag}) {lab}')
plt.tight_layout()
save(fig, 'fig4_peak.png')

for th, lab in ((np.pi / 2, 'π/2'), (np.pi, 'π')):
    xc, zc, P, *_ = MAPS[('2ce', th)]
    i0, j0 = zc.size // 2, xc.size // 2
    sx, sz = np.abs(xc) <= 1.33, np.abs(zc) <= 2.7
    cx = np.polyfit(xc[sx], P[i0, sx], 2); cz = np.polyfit(zc[sz], P[sz, j0], 2)
    note(f"2CE θ = {lab}: in-plane fit {cx[0]:+.3f} xc² {cx[2]:+.3f}; axial fit "
         f"{cz[0]:+.3f} zc² {cz[2]:+.3f}; F(xc=0.37) {np.interp(0.37, xc, P[i0]):.3f}; "
         f"F(zc=1.8) {np.interp(1.8, zc, P[:, j0]):.3f}; F(zc=2.7) {np.interp(2.7, zc, P[:, j0]):.3f}")
xc, zc, P, *_ = MAPS[('2pe', np.pi / 2)]
row = P[zc.size // 2]
note(f"2PE θ = π/2 in plane: range {row.min():.2f}–{row.max():.2f} over |xc| ≤ 1; "
     f"F(xc=0.5) {np.interp(0.5, xc, row):.3f}   (paper: fluctuates 1–0.7, period ≈ λ1; 30% drop at 0.5 λ1)")

# ── Figs. 5 and 6: Linfoot F and, in the second column, Q ─────────────────
# The paper labels its second column C, but its values cannot be C: its own
# identity 2Q − C = F (p. 126) gives F ≥ −C, so F ≈ −0.8 at θ = π/2,
# |zc| = 1.33 λ1 (p. 128) requires C ≥ 0.8, while the panel shows ≈ 0. Q
# reproduces that panel; C stays near 1 for a translated spot.
def surfaces(pair, which, name, thetas=((np.pi, 'θ = π'), (np.pi / 2, 'θ = π/2'))):
    fig = plt.figure(figsize=(17.0, 8.0 * len(thetas)))
    k = 1
    for th, lab in thetas:
        xc, zc, P, Fm, Cm, Qm = MAPS[(pair, th)]
        XC, ZC = np.meshgrid(xc, zc)
        for sym in which:
            M, lim = {'F': (Fm, (-3, 1)), 'C': (Cm, (0, 1)), 'Q': (Qm, (0, 1))}[sym]
            ax = fig.add_subplot(len(thetas), len(which), k, projection='3d'); k += 1
            ax.plot_surface(XC, ZC, np.clip(M, *lim), cmap='viridis', edgecolor='k',
                            linewidth=0.2, rstride=1, cstride=1)
            ax.set_zlim(*lim)
            ax.set_ylim(zc.max(), zc.min())          # z_c from −6 in front to +6 behind
            ax.set_xticks([-1.0, -0.5, 0.0, 0.5, 1.0]); ax.set_yticks(np.arange(-6, 7, 2))
            ax.set_zticks(np.arange(-3, 1.01, 0.5) if sym == 'F' else
                          (np.arange(0, 1.01, 0.2) if pair == '2ce' else np.arange(0, 1.01, 0.25)))
            ax.set_box_aspect((1.0, 1.0, 0.9), zoom=1.25)   # fill the frame as the paper does
            ax.zaxis.set_ticks_position('lower'); ax.zaxis.set_label_position('lower')  # z axis on the left
            ax.set_xlabel('x$_c$', labelpad=18); ax.set_ylabel('z$_c$', labelpad=18)
            ax.set_zlabel(sym, labelpad=14)
            ax.set_title(f"{'2CE' if pair == '2ce' else '2PE'}, {lab}: {sym}")
            ax.view_init(elev=22, azim=120)          # x_c decreasing left to right
    save(fig, name)


for fig_no, pair in ((5, '2ce'), (6, '2pe')):
    surfaces(pair, 'FQ', f'fig{fig_no}_linfoot.png')     # the paper's layout (second column = Q)
    surfaces(pair, 'C', f'fig{fig_no}_C.png')            # C itself, for comparison
surfaces('2pe', 'FQ', 'fig6_theta0.png', thetas=((0.0, 'θ = 0'),))
_, _, _, Fm, Cm, Qm = MAPS[('2pe', 0.0)]
note(f"2PE θ = 0: F {Fm.min():+.2f} to {Fm.max():+.2f}; Q {Qm.min():.2f} to {Qm.max():.2f}; "
     f"C {Cm.min():.2f} to {Cm.max():.2f}")

# diagnostic: F, C and Q as maps, to settle which quantity the paper's C panels show
fig, axes = plt.subplots(4, 3, figsize=(30.0, 44.0))
r = 0
for pair in ('2ce', '2pe'):
    for th, lab in ((np.pi, 'θ = π'), (np.pi / 2, 'θ = π/2')):
        xc, zc, P, Fm, Cm, Qm = MAPS[(pair, th)]
        for c, (M, name) in enumerate(((Fm, 'F'), (Cm, 'C'), (Qm, 'Q'))):
            ax = axes[r, c]
            pm = ax.pcolormesh(xc, zc, M, cmap='viridis', shading='auto')
            fig.colorbar(pm, ax=ax, fraction=0.05, pad=0.03)
            ax.set_xlabel('x$_c$ (λ$_1$)'); ax.set_ylabel('z$_c$ (λ$_1$)')
            ax.set_title(f"{'2CE' if pair == '2ce' else '2PE'}, {lab}: {name}")
        i0, j0 = zc.size // 2, xc.size // 2
        note(f"{pair} {lab}: F,C,Q at zc=1.33 → {np.interp(1.33, zc, Fm[:, j0]):+.2f}, "
             f"{np.interp(1.33, zc, Cm[:, j0]):+.2f}, {np.interp(1.33, zc, Qm[:, j0]):+.2f}; "
             f"at xc=1 → {np.interp(1.0, xc, Fm[i0]):+.2f}, {np.interp(1.0, xc, Cm[i0]):+.2f}, "
             f"{np.interp(1.0, xc, Qm[i0]):+.2f}")
        r += 1
plt.tight_layout()
save(fig, 'diagnostic_FCQ_maps.png')

with open(os.path.join(OUT, 'lim2002_numbers.txt'), 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(LINES) + '\n')
