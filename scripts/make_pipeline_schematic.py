r"""
A one-page visual schematic of every model built since Romallosa 2003 — the
optical configuration (pupil → aplanatic focusing cone → focal signature) for
each phase, plus the common data pipeline they all share.

Top band: the pipeline every phase runs through —
    INPUT (pupil A(θ), polarization, spectrum) → FOCUSING (Debye–Wolf integral,
    or the equivalent Monte-Carlo plane-wave sum) → FOCAL FIELD I(r,z,t) →
    METRICS (FWHM, zeros, Linfoot F/S/Q, DOF, Strehl).
The Monte-Carlo clear limit ≡ the Debye–Wolf integral (the validation gate).

Below: one card per phase — a schematic pupil (left), the focusing cone, and the
characteristic focal signature (right), with the headline result.

Output: output/00_overview/models_schematic.png
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
from scipy.special import j0, j1

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '00_overview')
os.makedirs(OUT, exist_ok=True)

BLUE, RED, GREEN, PURPLE, ORANGE, TEAL = ('#1f77b4', '#d62728', '#2ca02c',
                                          '#9467bd', '#ff7f0e', '#17becf')


# ── pupil icons ─────────────────────────────────────────────────────────────
def draw_pupil(ax, kind):
    ax.set_xlim(-1.15, 1.15); ax.set_ylim(-1.15, 1.15)
    ax.set_aspect('equal'); ax.axis('off')
    g = np.linspace(-1, 1, 160)
    Xp, Yp = np.meshgrid(g, g); R = np.hypot(Xp, Yp); disk = R <= 1.0
    img = np.full_like(R, np.nan)
    if kind == 'uniform':
        img[disk] = 1.0
        ax.imshow(img, extent=[-1, 1, -1, 1], cmap='Blues', vmin=0, vmax=1.4)
    elif kind == 'gaussian':
        img[disk] = np.exp(-2.2 * R[disk] ** 2)
        ax.imshow(img, extent=[-1, 1, -1, 1], cmap='Blues', vmin=0, vmax=1.1)
    elif kind == 'annular':
        ring = disk & (R >= 0.62)
        img[ring] = 1.0
        ax.imshow(img, extent=[-1, 1, -1, 1], cmap='Greens', vmin=0, vmax=1.4)
    elif kind == 'axicon':
        img[disk] = np.cos(9.0 * R[disk]) ** 2           # conical phase rings
        ax.imshow(img, extent=[-1, 1, -1, 1], cmap='twilight', vmin=0, vmax=1)
    elif kind == 'pulsed':                                # annulus + pulse mark
        ring = disk & (R >= 0.62); img[ring] = 1.0
        ax.imshow(img, extent=[-1, 1, -1, 1], cmap='Oranges', vmin=0, vmax=1.4)
        t = np.linspace(-1, 1, 80)
        ax.plot(t, 0.0 + 0.42 * np.cos(11 * t) * np.exp(-(t * 2.3) ** 2),
                color='k', lw=1.2)
    elif kind == 'photons':                              # MC: sampled points
        rng = np.random.default_rng(3)
        n = 240; th = np.arccos(1 - rng.random(n) * (1 - np.cos(0.66)))
        rr = np.sin(th) / np.sin(0.66); ph = rng.uniform(0, 2 * np.pi, n)
        ax.scatter(rr * np.cos(ph), rr * np.sin(ph), s=6, c=BLUE, alpha=0.7)
    ax.add_patch(Circle((0, 0), 1.0, fill=False, ec='0.3', lw=1.2))


# ── focal-signature icons ───────────────────────────────────────────────────
def draw_focus(ax, kind):
    ax.set_aspect('equal'); ax.axis('off')
    n = 160
    if kind in ('spot', 'narrow'):
        s = 9.0 if kind == 'spot' else 13.0
        g = np.linspace(-1, 1, n); X, Y = np.meshgrid(g, g)
        v = s * np.hypot(X, Y) + 1e-9
        I = (2 * j1(v) / v) ** 2
        ax.imshow(I ** 0.5, extent=[-1, 1, -1, 1], cmap='inferno')
    elif kind == 'bessel':
        g = np.linspace(-1, 1, n); X, Y = np.meshgrid(g, g)
        I = j0(11 * np.hypot(X, Y)) ** 2
        ax.imshow(I ** 0.5, extent=[-1, 1, -1, 1], cmap='inferno')
    elif kind in ('segment', 'segment_faint'):
        gz = np.linspace(-1, 1, n); gx = np.linspace(-1, 1, n)
        Xx, Zz = np.meshgrid(gx, gz)
        I = np.exp(-(Xx / 0.16) ** 2) * np.exp(-(Zz / 0.9) ** 2)
        if kind == 'segment_faint':
            I = I + 0.18 * np.exp(-(Xx / 0.5) ** 2) * np.exp(-(Zz / 0.9) ** 2)
        ax.imshow(I ** 0.5, extent=[-1, 1, -1, 1], cmap='inferno')
    elif kind == 'halo':
        g = np.linspace(-1, 1, n); X, Y = np.meshgrid(g, g)
        v = 11 * np.hypot(X, Y) + 1e-9
        I = 0.75 * (2 * j1(v) / v) ** 2 + 0.28 * np.exp(-(np.hypot(X, Y) / 0.7) ** 2)
        ax.imshow(I ** 0.5, extent=[-1, 1, -1, 1], cmap='inferno')
    ax.add_patch(Circle((0, 0), 0.985, fill=False, ec='0.3', lw=1.0,
                        transform=ax.transData))


# ── figure ──────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(15, 11.5))
bg = fig.add_axes([0, 0, 1, 1]); bg.axis('off')
bg.set_xlim(0, 1); bg.set_ylim(0, 1)
fig.suptitle('mcdo_dev — models since Romallosa 2003 (optical schematic + pipeline)',
             fontsize=17, y=0.985, weight='bold')


def box(x, y, w, h, text, fc, fs=10.5, tc='k'):
    bg.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.006',
                                fc=fc, ec='0.35', lw=1.2, alpha=0.95))
    bg.text(x + w / 2, y + h / 2, text, ha='center', va='center', fontsize=fs,
            color=tc, wrap=True)


def arrow(x0, y0, x1, y1, lw=2.0, color='0.3'):
    bg.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle='-|>',
                 mutation_scale=18, lw=lw, color=color, shrinkA=2, shrinkB=2))


# top pipeline band
yb, hb = 0.875, 0.075
box(0.030, yb, 0.150, hb, 'INPUT\npupil A(θ)\n+ polarization\n+ spectrum |E(ω)|²',
    '#eef3fb', 9.5)
box(0.235, yb, 0.205, hb, 'FOCUSING  (aplanatic, sinα=NA/n)\n———————\n'
    'Debye–Wolf integral\n≡ Monte-Carlo plane-wave sum', '#fdeeee', 9.5)
box(0.495, yb, 0.150, hb, 'FOCAL FIELD\nI(r, z, t)\n= |Σ wⱼ e^{ik·P}|²', '#eef7ee', 9.5)
box(0.700, yb, 0.150, hb, 'METRICS\nFWHM, zeros,\nLinfoot F/S/Q,\nDOF, Strehl', '#f6eefb', 9.5)
for x0, x1 in [(0.180, 0.235), (0.440, 0.495), (0.645, 0.700)]:
    arrow(x0, yb + hb / 2, x1, yb + hb / 2)
bg.text(0.865, yb + hb / 2,
        'clear-limit MC\n≡ Debye–Wolf\n(validation gate)', ha='left',
        va='center', fontsize=9, style='italic', color='0.25')

# phase cards
phases = [
    ('Phase 1 — Romallosa 2003 (baseline)', 'uniform', 'spot', BLUE,
     'High-NA Richards–Wolf field; pulsing fills the |I₀−I₂|² zeros; Linfoot S↑. '
     'All 5 paper figures reproduced.'),
    ('Phase 2 — NA + apodization', 'gaussian', 'narrow', PURPLE,
     'Spot vs NA; Gaussian apodization EXTENDS scalar validity; E_z fills the '
     'x-cut zeros → anisotropic vector thresholds.'),
    ('Phase 3 — Annular aperture', 'annular', 'bessel', GREEN,
     'Babinet at field level: DOF × 1/(1−ε²), narrower lobe, Strehl (1−ε²)²; '
     'thin ring → vector-deformed J₀² at high NA.'),
    ('Phase 4 — Axicon / Bessel', 'axicon', 'segment', TEAL,
     'Conical pupil phase → focal SEGMENT with position-dependent J₀² scale '
     '(Durnin). Axicon ≡ thin annulus at matched θ.'),
    ('Phase 5 — Pulsed × pupils  (new science)', 'pulsed', 'segment_faint', ORANGE,
     'Annular DOF extension is bandwidth-invariant (cw→1 fs); transverse ring '
     'contrast erodes — the Romallosa trade, for structured pupils.'),
    ('Phase 6 — Monte Carlo', 'photons', 'halo', RED,
     'Photons = plane-wave components over the cone; clear limit ≡ Debye–Wolf '
     '(RMS<0.1%). + scattering → ballistic RW core + diffuse halo (next).'),
]

row_y = np.linspace(0.74, 0.045, len(phases))
ph_w, ph_h = 0.085, 0.085
fo_w, fo_h = 0.105, 0.085
for (title, pk, fk, col, result), yc in zip(phases, row_y):
    # title bar + result text
    bg.add_patch(FancyBboxPatch((0.025, yc - 0.052), 0.95, 0.104,
                 boxstyle='round,pad=0.004', fc='white', ec=col, lw=1.8))
    bg.text(0.455, yc + 0.030, title, ha='left', va='center', fontsize=12.5,
            weight='bold', color=col)
    bg.text(0.455, yc - 0.018, result, ha='left', va='center', fontsize=9.7,
            color='0.15', wrap=True)
    # pupil mini-axis
    axp = fig.add_axes([0.045, yc - ph_h / 2, ph_w, ph_h]); draw_pupil(axp, pk)
    axp.set_title('pupil', fontsize=8, pad=1.5)
    # focusing cone (drawn on bg, figure coords approximate)
    cx0 = 0.045 + ph_w + 0.004
    arrow(cx0, yc + 0.028, cx0 + 0.075, yc, color=col, lw=1.6)
    arrow(cx0, yc - 0.028, cx0 + 0.075, yc, color=col, lw=1.6)
    bg.text(cx0 + 0.034, yc + 0.046, 'focus', ha='center', fontsize=7.5,
            color='0.4')
    # focal-signature mini-axis
    axf = fig.add_axes([cx0 + 0.080, yc - fo_h / 2, fo_w, fo_h]); draw_focus(axf, fk)
    axf.set_title('focal signature', fontsize=8, pad=1.5)

out = os.path.join(OUT, 'models_schematic.png')
fig.savefig(out, dpi=170, bbox_inches='tight'); plt.close(fig)
print(f"Saved → {out}")
