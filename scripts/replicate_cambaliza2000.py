r"""Replication of Cambaliza & Saloma, Opt. Commun. 184 (2000) 25–35, Figs. 2–7 and the values quoted in the text.

Model (paper Eqs. 1–6): paraxial scalar focal field of each lens (Lommel form, NA 0.5), beam 2 rotated by θ about the
common focus; 2CE F2c = I1 I2 (750 + 656 nm), 2PE F2p = |U1 + U2|^4 (700 nm); annular pupil U_a = U_R − U_εR, ε = 0.99.
Profiles: transverse F(x, 0, 0; θ), axial F(0, 0, z; θ), each normalized to its own maximum.

    python scripts/replicate_cambaliza2000.py
    -> output/08_two_color/cambaliza2000/fig{2..7}.png, numbers.txt
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
import matplotlib.ticker
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo.style import apply as _apply_style
_apply_style()
matplotlib.rcParams.update({'font.size': 24, 'axes.titlesize': 28, 'axes.labelsize': 28, 'xtick.labelsize': 24,
                            'ytick.labelsize': 24, 'legend.fontsize': 24})

from mcdo.twobeam import beam_field

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'cambaliza2000')
os.makedirs(OUT, exist_ok=True)
NA, L1, L2, L2P, LE = 0.5, 0.750, 0.656, 0.700, 0.350
THETAS = ((0.0, 'θ = 0'), (np.pi / 2, 'θ = π/2'), (np.pi, 'θ = π'))
STYLE = {0.0: ('k', '-', 3), np.pi / 2: ('#d62728', '-', 3), np.pi: ('#1f77b4', '--', 3)}
xs = np.linspace(-1.0, 1.0, 2001)
zs = np.linspace(-5.0, 5.0, 8001)
LINES = []


def F2c(x, z, th, eps=0.0, l1=L1, l2=L2):
    return np.abs(beam_field(x, z, l1, NA, eps=eps)) ** 2 * np.abs(beam_field(x, z, l2, NA, theta=th, eps=eps)) ** 2


def F2p(x, z, th, eps=0.0):
    return np.abs(beam_field(x, z, L2P, NA, eps=eps) + beam_field(x, z, L2P, NA, theta=th, eps=eps)) ** 4


def norm(v):
    return v / v.max()


def fwhm(s, y):
    """Full width at half maximum of the central peak (the one at s = 0)."""
    y = y / y[np.argmin(np.abs(s))]
    i0 = int(np.argmin(np.abs(s)))
    r = i0
    while r < len(y) - 1 and y[r] >= 0.5:
        r += 1
    l = i0
    while l > 0 and y[l] >= 0.5:
        l -= 1
    if y[r] >= 0.5 or y[l] >= 0.5:
        return np.nan                                        # never falls to half within the window
    xr = np.interp(0.5, [y[r], y[r - 1]], [s[r], s[r - 1]])
    xl = np.interp(0.5, [y[l], y[l + 1]], [s[l], s[l + 1]])
    return xr - xl


def profiles(fig_no, eps, axis):
    """Figs. 2/3 (circular) and 6/7 (annular): (a) 2PE, (b) 2CE, three angles."""
    s = xs if axis == 'x' else zs
    fig, axes = plt.subplots(2, 1, figsize=(11, 13), sharex=True)
    out = {}
    for ax, (name, f) in zip(axes, (('2PE', F2p), ('2CE', F2c))):
        for th, lab in THETAS:
            v = norm(f(s, 0 * s, th, eps) if axis == 'x' else f(0 * s, s, th, eps))
            c, ls, lw = STYLE[th]
            ax.plot(s, v, ls, color=c, lw=lw, label=lab)
            out[(name, th)] = (s, v)
        ax.set_ylim(0, 1.05); ax.set_ylabel('Intensity'); ax.set_title(f'({"ab"[name == "2CE"]}) {name}', loc='left')
    axes[1].set_xlabel('x (µm)' if axis == 'x' else 'z (µm)')
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc='lower center', ncol=3, bbox_to_anchor=(0.5, -0.04), frameon=False)
    plt.tight_layout()
    fig.savefig(os.path.join(OUT, f'fig{fig_no}.png'), dpi=300, bbox_inches='tight'); plt.close(fig)
    print('Saved -> fig%d.png' % fig_no, flush=True)
    return out


def pair(dl):
    """λ1 − λ2 = dl with 1/λ1 + 1/λ2 = 1/λe (µm)."""
    # λ1 λ2 = λe (λ1 + λ2), λ1 = λ2 + dl  →  λ2² + (dl − 2λe) λ2 − λe dl = 0
    b, c = dl - 2 * LE, -LE * dl
    l2 = (-b + np.sqrt(b * b - 4 * c)) / 2
    return l2 + dl, l2


# ── Figs. 2–3: circular pupils; Figs. 6–7: annular pupils (ε = 0.99) ──
T = profiles(2, 0.0, 'x')
A = profiles(3, 0.0, 'z')
TA = profiles(6, 0.99, 'x')
AA = profiles(7, 0.99, 'z')
W = lambda d, k: fwhm(*d[k])
LINES += ['Quoted value (page) | paper | current work',
          f'Fig. 2a: F2p(x;π/2) central spot / F2p(x;0) (p. 28) | 0.67 | {W(T, ("2PE", np.pi / 2)) / W(T, ("2PE", 0.0)):.3f}',
          f'Fig. 2b: F2c(x;0) / F2c(x;π/2) central spot (p. 28, "0.75 times narrower") | 0.75 | '
          f'{W(T, ("2CE", 0.0)) / W(T, ("2CE", np.pi / 2)):.3f}',
          f'Fig. 2: F2c(x;π/2) / F2p(x;π/2) central spot (p. 29, "1.58 times wider") | 1.58 | '
          f'{W(T, ("2CE", np.pi / 2)) / W(T, ("2PE", np.pi / 2)):.3f}',
          f'Fig. 3: DOF F2c(z;π/2) / F2p(z;π/2) (p. 29, "approximately twice") | 2 | '
          f'{W(A, ("2CE", np.pi / 2)) / W(A, ("2PE", np.pi / 2)):.3f}',
          f'Fig. 6b: F2c/a(x;0) / F2c/a(x;π/2) central spot (p. 31, "0.82 times") | 0.82 | '
          f'{W(TA, ("2CE", 0.0)) / W(TA, ("2CE", np.pi / 2)):.3f}',
          f'Fig. 6a: min of F2p/a(x;π/2) (p. 31, "not lower than 0.08") | 0.08 | {TA[("2PE", np.pi / 2)][1].min():.3f}',
          f'p. 31 (1): F2c/a(x;0) narrower than F2p(x;0) by ("almost 30%") | 0.30 | '
          f'{1 - W(TA, ("2CE", 0.0)) / W(T, ("2PE", 0.0)):.3f}',
          f'p. 31 (2): F2p/a(x;π/2) narrower than F2c/a(x;π/2) by ("approximately 35%") | 0.35 | '
          f'{1 - W(TA, ("2PE", np.pi / 2)) / W(TA, ("2CE", np.pi / 2)):.3f}',
          f'p. 31 (3): F2c/a(x;π/2) narrower than F2c(x;π/2) by ("approximately 32%") | 0.32 | '
          f'{1 - W(TA, ("2CE", np.pi / 2)) / W(T, ("2CE", np.pi / 2)):.3f}',
          f'Fig. 7b: F2c/a(z;π/2) central spot (p. 32, "about 1 µm, 1.43 λ2p") | 1.0 µm | {W(AA, ("2CE", np.pi / 2)):.3f} µm',
          f'p. 32: DOF F2c/a(z;π/2) narrower than F2c(z;π/2) by ("about 40%") | 0.40 | '
          f'{1 - W(AA, ("2CE", np.pi / 2)) / W(A, ("2CE", np.pi / 2)):.3f}',
          f'p. 32: DOF F2c/a(z;π/2) longer than F2p(z;π/2) by ("20%") | 0.20 | '
          f'{W(AA, ("2CE", np.pi / 2)) / W(A, ("2PE", np.pi / 2)) - 1:.3f}']

# ── Fig. 4: F2c(x, 0, 0; π/2) and F2c(0, 0, z; π/2) for Δλ = 10, 39, 94 nm (shorter λ2 on lens L2) ──
xh, zh = np.linspace(0, 1.0, 1001), np.linspace(0, 1.0, 1001)
fig, axes = plt.subplots(2, 1, figsize=(11, 13))
for dl, ls in ((0.010, '-'), (0.094, ':'), (0.039, '-.')):
    l1, l2 = pair(dl)
    axes[0].plot(xh, norm(F2c(xh, 0 * xh, np.pi / 2, l1=l1, l2=l2)), ls, color='k', lw=3, label=f'{dl * 1000:.0f} nm')
    axes[1].plot(zh, norm(F2c(0 * zh, zh, np.pi / 2, l1=l1, l2=l2)), ls, color='k', lw=3)
axes[0].set_xlabel('x (µm)'); axes[1].set_xlabel('z (µm)')
for ax, t in zip(axes, 'ab'):
    ax.set_ylabel('Intensity'); ax.set_xlim(0, 1); ax.set_ylim(0, 1.05); ax.set_title(f'({t})', loc='left')
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, loc='lower center', ncol=3, bbox_to_anchor=(0.5, -0.04), frameon=False)
plt.tight_layout(); fig.savefig(os.path.join(OUT, 'fig4.png'), dpi=300, bbox_inches='tight'); plt.close(fig)
print('Saved -> fig4.png', flush=True)

# ── Fig. 5: FWHM of F2c(x, 0, 0; π/2) and DOF of F2c(0, 0, z; π/2) against Δλ, with linear fits ──
dls = np.arange(0.010, 0.0941, 0.0105)
fw, dof = [], []
for dl in dls:
    l1, l2 = pair(dl)
    fw.append(fwhm(xs, F2c(xs, 0 * xs, np.pi / 2, l1=l1, l2=l2)))
    dof.append(fwhm(zs, F2c(0 * zs, zs, np.pi / 2, l1=l1, l2=l2)))
fw, dof, d_nm = np.array(fw), np.array(dof), dls * 1000
pf, pd = np.polyfit(d_nm, fw, 1), np.polyfit(d_nm, dof, 1)
fig, ax = plt.subplots(figsize=(12, 9))
ax.plot(d_nm, fw, 'o', color='k', ms=11, label='FWHM')
ax.plot(d_nm, dof, 'o', color='k', mfc='white', ms=11, mew=2, label='DOF')
for p in (pf, pd):
    ax.plot([0, 100], np.polyval(p, [0, 100]), '-', color='k', lw=2)
ax.set_xlabel('Δλ (nm)'); ax.set_ylabel('Magnitude (µm)'); ax.set_xlim(0, 100)
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.14), ncol=2, frameon=False)
fig.savefig(os.path.join(OUT, 'fig5.png'), dpi=300, bbox_inches='tight'); plt.close(fig)
print('Saved -> fig5.png', flush=True)
LINES += [f'Fig. 5: FWHM fit (p. 30: (2.4e-4) Δλ + 0.356e-1, plotted line ≈ 0.711 at 0) | slope 2.4e-4 µm/nm | '
          f'slope {pf[0]:.2e} µm/nm, intercept {pf[1]:.4f} µm',
          f'Fig. 5: DOF fit (p. 30: (4.81e-4) Δλ + 0.7112, plotted line decreasing) | slope 4.81e-4, intercept 0.7112 | '
          f'slope {pd[0]:.2e} µm/nm, intercept {pd[1]:.4f} µm',
          f'p. 30: FWHM increase over 10–94 nm ("less than 6%") | < 0.06 | {fw[-1] / fw[0] - 1:.3f}']
open(os.path.join(OUT, 'numbers.txt'), 'w').write('\n'.join(LINES) + '\n')
print('\n'.join(LINES))


# ── one panel per image, on the axes of the paper, for the side-by-side slides ──
PAN = os.path.join(OUT, 'panels')
os.makedirs(PAN, exist_ok=True)


# width/height of the plot box of each original panel, measured from its axis lines (pixels)
BOX = {'fig2a': 478 / 245, 'fig2b': 478 / 243, 'fig3a': 486 / 270, 'fig3b': 486 / 294, 'fig4a': 490 / 305,
       'fig4b': 493 / 309, 'fig5': 450 / 367, 'fig6a': 490 / 256, 'fig6b': 492 / 283, 'fig7a': 488 / 281,
       'fig7b': 491 / 288}


def one(name, curves, xlabel, xlim, ylim=(0, 1), legend=True):
    fig, ax = plt.subplots(figsize=(12, 12 / BOX[name[:5]] + 2.5))
    ax.set_box_aspect(1 / BOX[name[:5]])                     # same plot-box shape as the paper's panel
    for x, y, lab, c, ls, lw in curves:
        ax.plot(x, y, ls, color=c, lw=lw, label=lab)
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_xlabel(xlabel); ax.set_ylabel('Intensity')
    ax.set_xticks(np.arange(xlim[0], xlim[1] + 1e-9, 0.2 if xlim == (0, 1) else 0.5 if xlim[1] == 1 else 1))
    ax.xaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%g'))
    ax.set_yticks(np.arange(0, 1.01, 0.2)); ax.tick_params(axis='x', pad=12)
    if legend:
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.125 * BOX[name[:5]]), ncol=3, frameon=False)
    fig.savefig(os.path.join(PAN, name), dpi=300, bbox_inches='tight'); plt.close(fig)


for fig_no, data, axis in ((2, T, 'x'), (3, A, 'z'), (6, TA, 'x'), (7, AA, 'z')):
    for t, kind in (('a', '2PE'), ('b', '2CE')):
        cs = [(*data[(kind, th)], lab, *STYLE[th]) for th, lab in THETAS]
        one(f'fig{fig_no}{t}.png', cs, 'x (µm)' if axis == 'x' else 'z (µm)', (-1, 1) if axis == 'x' else (-5, 5))
for fig_no, eps, axis, s in ((6, 0.99, 'x', xs), (7, 0.99, 'z', zs)):     # 2PE as the excitation |U1 + U2|^2
    cs = []
    for th, lab in THETAS:
        U = (lambda a, b: beam_field(a, b, L2P, NA, eps=eps) + beam_field(a, b, L2P, NA, theta=th, eps=eps))
        v = np.abs(U(s, 0 * s) if axis == 'x' else U(0 * s, s)) ** 2
        cs.append((s, norm(v), lab, *STYLE[th]))
    one(f'fig{fig_no}a_excitation.png', cs, 'x (µm)' if axis == 'x' else 'z (µm)', (-1, 1) if axis == 'x' else (-5, 5))
for t, axis in (('a', 'x'), ('b', 'z')):
    cs = []
    for dl, ls in ((0.010, '-'), (0.094, ':'), (0.039, '-.')):
        l1, l2 = pair(dl)
        s = xh
        v = F2c(s, 0 * s, np.pi / 2, l1=l1, l2=l2) if axis == 'x' else F2c(0 * s, s, np.pi / 2, l1=l1, l2=l2)
        cs.append((s, norm(v), f'{dl * 1000:.0f} nm', 'k', ls, 3))
    one(f'fig4{t}.png', cs, 'x (µm)' if axis == 'x' else 'z (µm)', (0, 1))
fig, ax = plt.subplots(figsize=(12, 12 / BOX['fig5'] + 2.5))
ax.set_box_aspect(1 / BOX['fig5'])
ax.plot(d_nm, fw, 'o', color='k', ms=11, label='FWHM')
ax.plot(d_nm, dof, 'o', color='k', mfc='white', ms=11, mew=2, label='DOF')
for p in (pf, pd):
    ax.plot([0, 100], np.polyval(p, [0, 100]), '-', color='k', lw=2)
ax.set_xlim(0, 100); ax.set_ylim(0.65, 0.775); ax.set_xlabel('Δλ (nm)'); ax.set_ylabel('Magnitude (µm)')
ax.set_yticks(np.arange(0.65, 0.7751, 0.025)); ax.tick_params(axis='x', pad=12)
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.125 * BOX['fig5']), ncol=2, frameon=False)
fig.savefig(os.path.join(PAN, 'fig5.png'), dpi=300, bbox_inches='tight'); plt.close(fig)
print('Saved panels ->', PAN)
