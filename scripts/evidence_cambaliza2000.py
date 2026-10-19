r"""Current-work figures for the statements of Cambaliza & Saloma (2000) that the replication does not reproduce.

Nothing is drawn on the published panels: each figure is current work on its own axes, with the curves that a
statement compares on one plot, so the widths can be read off directly.
  ratio_fig2a.png    p. 28: F2p(x;π/2) central spot "approximately 0.67 times" that of F2p(x;0)
  ratio_158.png      p. 29: F2c(x;π/2) central spot "1.58 times wider" than F2p(x;π/2)
  ratio_20pct.png    p. 32: DOF of F2c/a(z;π/2) "20% longer" than that of F2p(z;π/2)
  fig5_caption.png   Fig. 5: current-work widths with the two fit lines of the caption
  rotation.png       2CE at θ = π/2 along the axis: beam 2 rotated in (x, z) and in (u, v) as written in Eq. 1
  eq6_excitation.png θ = π/2, annular 2PE: Eq. 6 |U1 + U2|^4 against the excitation |U1 + U2|^2 (Figs. 6a, 7a)

    python scripts/evidence_cambaliza2000.py -> output/08_two_color/cambaliza2000/evidence/
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker
from mcdo.twobeam import beam_field

D = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'cambaliza2000')
OUT = os.path.join(D, 'evidence'); os.makedirs(OUT, exist_ok=True)
NA, L1, L2, LP, LE = 0.5, 0.750, 0.656, 0.700, 0.350
P2 = np.pi / 2
plt.rcParams.update({'font.size': 26, 'axes.titlesize': 28, 'axes.labelsize': 28, 'legend.fontsize': 24,
                     'lines.linewidth': 3.5, 'axes.grid': True, 'grid.alpha': 0.35})


def U(x, z, lam, th, eps=0.0, rotation='geometric'):
    return beam_field(x, z, lam, NA, theta=th, eps=eps, rotation=rotation)


def f2pe(X, Z, th, eps=0.0, power=4):
    v = np.abs(U(X, Z, LP, 0, eps) + U(X, Z, LP, th, eps)) ** power
    return v / v.max()


def f2ce(X, Z, th, eps=0.0, rotation='geometric', l1=L1, l2=L2):
    v = np.abs(U(X, Z, l1, 0, eps)) ** 2 * np.abs(U(X, Z, l2, th, eps, rotation)) ** 2
    return v / v.max()


def fwhm(s, y):
    i0 = int(np.argmin(np.abs(s)))
    r = i0
    while y[r] >= 0.5:
        r += 1
    l = i0
    while y[l] >= 0.5:
        l -= 1
    return np.interp(0.5, [y[r], y[r - 1]], [s[r], s[r - 1]]) - np.interp(0.5, [y[l], y[l + 1]], [s[l], s[l + 1]])


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=300, bbox_inches='tight'); plt.close(fig)
    print('Saved ->', name)


def one(name, s, curves, xlabel, title, xlim, panel=False):
    """Curves on one axes, legend outside; returns the FWHM of each. Full slide width (legend at the right), or
    panel=True for the slot beside a published panel (no title, legend beneath, larger text)."""
    with plt.rc_context({'font.size': 30, 'axes.labelsize': 30, 'legend.fontsize': 27} if panel else {}):
        fig, ax = plt.subplots(figsize=(10.5, 5.6) if panel else (18.5, 6.6))
        out = []
        for y, col, ls, lab in curves:
            w = fwhm(s, y)
            out.append(w)
            ax.plot(s, y, ls, color=col, label=f'{lab}: {w:.3f} µm' if panel else f'{lab}: FWHM {w:.3f} µm')
        ax.set_xlim(*xlim); ax.set_ylim(0, 1.02); ax.set_yticks(np.arange(0, 1.01, 0.2 if panel else 0.1))
        ax.set_xlabel(xlabel); ax.set_ylabel('Intensity')
        if panel:
            ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=1, frameon=False)
        else:
            ax.set_title(title)
            ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.17), ncol=2, frameon=False)
        save(fig, name)
    return out


LINES = []
x = np.linspace(-1, 1, 8001); z = np.linspace(-5, 5, 20001)
X0, Z0 = x, 0 * x
w0, w2 = one('ratio_fig2a.png', x, [(f2pe(X0, Z0, 0.0), 'k', '-', '2PE, θ = 0'), (f2pe(X0, Z0, P2), '#d62728', '-', '2PE, θ = π/2')],
             'x (µm)', '2PE across the axis, circular pupils (Fig. 2a)', (-1, 1))
LINES.append(f'p. 28, 0.67: {w2:.3f} / {w0:.3f} = {w2 / w0:.3f}')
wp, wc = one('ratio_158.png', x, [(f2pe(X0, Z0, P2), '#d62728', '-', '2PE, θ = π/2 (Fig. 2a)'),
                                  (f2ce(X0, Z0, P2), '#1f77b4', '-', '2CE, θ = π/2 (Fig. 2b)')],
             'x (µm)', 'Across the axis, θ = π/2, circular pupils', (-1, 1))
LINES.append(f'p. 29, 1.58: {wc:.3f} / {wp:.3f} = {wc / wp:.3f}')
wp, wa = one('ratio_20pct.png', z, [(f2pe(0 * z, z, P2), '#d62728', '-', '2PE, circular (Fig. 3a)'),
                                    (f2ce(0 * z, z, P2, eps=0.99), '#1f77b4', '-', '2CE, annular (Fig. 7b)')],
             'z (µm)', 'Along the axis, θ = π/2', (-2, 2))
LINES.append(f'p. 32, 20% longer: {wa:.3f} / {wp:.3f} = {wa / wp:.3f}')


def pair(dl):
    b, c = dl - 2 * LE, -LE * dl
    l2 = (-b + np.sqrt(b * b - 4 * c)) / 2
    return l2 + dl, l2


# Fig. 5: current-work widths, with the two fit lines of the caption
dls = np.arange(0.010, 0.0941, 0.0105)
fw = np.array([fwhm(x, f2ce(X0, Z0, P2, l1=pair(d)[0], l2=pair(d)[1])) for d in dls])
dof = np.array([fwhm(z, f2ce(0 * z, z, P2, l1=pair(d)[0], l2=pair(d)[1])) for d in dls])
dn = dls * 1000
with plt.rc_context({'font.size': 32, 'axes.labelsize': 32, 'legend.fontsize': 31}):
    fig, ax = plt.subplots(figsize=(10.5, 5.6))
    L = np.array([0, 100])
    ax.plot(dn, fw, 'o', color='k', ms=14, label='FWHM')
    ax.plot(dn, dof, 'o', color='k', mfc='white', mew=2.5, ms=14, label='DOF')
    ax.plot(L, 4.81e-4 * L + 0.7112, '--', color='#ff7f0e', label='Caption fit')
    ax.set_xlim(0, 100); ax.set_ylim(0.65, 0.775)
    ax.set_xlabel('Δλ (nm)'); ax.set_ylabel('Width (µm)')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=3, frameon=False, columnspacing=1.0, handletextpad=0.4)
    save(fig, 'fig5_caption.png')
pf, pd = np.polyfit(dn, fw, 1), np.polyfit(dn, dof, 1)
LINES.append(f'Fig. 5 current work: FWHM {pf[0]:.3e} dl + {pf[1]:.4f}; DOF {pd[0]:.3e} dl + {pd[1]:.4f}')

# rotation of beam 2: (x, z) against (u, v), 2CE at θ = π/2 along the axis; drawn like the panel of Fig. 3b
# (same x range and plot-box shape, as in replicate_cambaliza2000.py) to sit beside it
BOX3B = 486 / 294
yg, yo = f2ce(0 * z, z, P2), f2ce(0 * z, z, P2, rotation='optical')
wg, wo = fwhm(z, yg), fwhm(z, yo)
with plt.rc_context({'font.size': 30, 'axes.labelsize': 30, 'legend.fontsize': 28, 'axes.grid': False}):
    fig, ax = plt.subplots(figsize=(9, 9 / BOX3B + 2.5))
    ax.set_box_aspect(1 / BOX3B)
    y0 = f2ce(0 * z, z, 0.0)                                  # θ = 0 and π: both rotations give this curve
    ax.plot(z, y0, '-', color='k', label='θ = 0, π')
    ax.plot(z, yg, '-', color='#1f77b4', label='θ = π/2, rotated in (x, z)')
    ax.plot(z, yo, '--', color='#d62728', label='θ = π/2, rotated in (u, v)')
    ax.set_xlim(-5, 5); ax.set_ylim(0, 1); ax.set_xticks(np.arange(-5, 5.1, 1)); ax.set_yticks(np.arange(0, 1.01, 0.2))
    ax.xaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%g'))
    ax.set_xlabel('z (µm)'); ax.set_ylabel('Intensity'); ax.tick_params(axis='x', pad=12)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=1, frameon=False)
    save(fig, 'rotation.png')
LINES.append(f'rotation, 2CE z pi/2: (x, z) {wg:.3f}, (u, v) {wo:.3f}')

# annular 2PE at θ = π/2: Eq. 6 against the excitation
fig, axes = plt.subplots(1, 2, figsize=(18.5, 6.0))
for ax, (s, X, Z, lab, xl) in zip(axes, ((x, X0, Z0, 'across (Fig. 6a)', 'x (µm)'),
                                         (z, 0 * z, z, 'along (Fig. 7a)', 'z (µm)'))):
    ax.plot(s, f2pe(X, Z, P2, eps=0.99, power=4), '-', color='#d62728', label='Eq. 6, |U₁ + U₂|⁴')
    ax.plot(s, f2pe(X, Z, P2, eps=0.99, power=2), '--', color='#ff7f0e', label='Excitation, |U₁ + U₂|²')
    ax.set_xlim(s[0], s[-1]); ax.set_ylim(0, 1.02); ax.set_xlabel(xl); ax.set_title(f'2PE, annular, θ = π/2, {lab}')
axes[0].set_ylabel('Intensity')
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=2, frameon=False)
plt.tight_layout()
save(fig, 'eq6_excitation.png')
open(os.path.join(OUT, 'numbers.txt'), 'w').write('\n'.join(LINES) + '\n')
print('\n'.join(LINES))

# Fig. 5 (asked for as an overlay): current-work lines and the caption fits drawn on the published plot, axes
# calibrated from its tick marks (x: 0 at column 143.5, 100 at 594.5; y: 0.65 at row 380.5, 0.775 at row 13.5)
from PIL import Image
im = np.array(Image.open(os.path.join(D, 'original', 'fig5.png')).convert('L'))
H, W = im.shape
cx0, cx1, ry0, ry1 = 143.5, 594.5, 380.5, 13.5
sx, sy = 100 / (cx1 - cx0), 0.125 / (ry1 - ry0)
ext = (-cx0 * sx, (W - cx0) * sx, 0.65 + (H - ry0) * sy, 0.65 - ry0 * sy)
with plt.rc_context({'axes.grid': False, 'legend.fontsize': 24}):
    fig, ax = plt.subplots(figsize=(14, 14 * H / W * 0.95))
    ax.imshow(im, cmap='gray', extent=ext, aspect='auto', alpha=0.65)
    L = np.array([0, 100])
    ax.plot(L, np.polyval(pf, L), '-', color='#1f77b4', lw=3.5, label=f'Current work, FWHM: {pf[0] * 1e4:+.2f}×10⁻⁴ Δλ + {pf[1]:.4f}')
    ax.plot(L, np.polyval(pd, L), '-', color='#2ca02c', lw=3.5, label=f'Current work, DOF: {pd[0] * 1e4:+.2f}×10⁻⁴ Δλ + {pd[1]:.4f}')
    ax.plot(L, 4.81e-4 * L + 0.7112, '--', color='#ff7f0e', lw=3.5, label='Caption, DOF: +4.81×10⁻⁴ Δλ + 0.7112')
    ax.plot([], [], '--', color='#d62728', lw=3.5, label='Caption, FWHM: 2.4×10⁻⁴ Δλ + 0.0356 (off the plot)')
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.axis('off')
    save(fig, 'fig5_overlay.png')                         # colours explained on the slide
