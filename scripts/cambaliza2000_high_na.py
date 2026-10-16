r"""Cambaliza & Saloma (2000) extended to high NA: widths of the 2PE and 2CE responses of Figs. 2-3 against NA,
paraxial scalar (the paper's Eq. 1) against vector (Richards-Wolf), in air and in water.

Same wavelengths as the paper: 2PE λ_2p = 0.700 µm; 2CE λ₁ = 0.750 µm (L1), λ₂ = 0.656 µm (L2). Circular pupils,
θ = 0, π/2, π; beam 2 rotated in real space; both beams polarized along y (perpendicular to both axes).
Width: FWHM of the central peak, transverse F(x, 0, 0; θ) and axial F(0, 0, z; θ) (DOF).
θ = π/2 needs both lenses to fit at 90°: NA ≤ n sin 45° (air 0.71, water 0.94).

    python scripts/cambaliza2000_high_na.py [--rerun] -> output/08_two_color/cambaliza2000/high_na/{widths.csv, widths_*.png, ratios.png}
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
from mcdo.twobeam import beam_field, two_color, two_photon

_apply_style()
matplotlib.rcParams.update({'font.size': 24, 'axes.titlesize': 28, 'axes.labelsize': 28, 'xtick.labelsize': 24,
                            'ytick.labelsize': 24, 'legend.fontsize': 24})

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'cambaliza2000', 'high_na')
os.makedirs(OUT, exist_ok=True)
L1, L2, LP = 0.750, 0.656, 0.700
THETAS = (0.0, np.pi / 2, np.pi)
TLAB = {0.0: 'θ = 0', np.pi / 2: 'θ = π/2', np.pi: 'θ = π'}
TCOL = {0.0: 'k', np.pi / 2: '#d62728', np.pi: '#1f77b4'}
MEDIA = ((1.0, np.round(np.arange(0.2, 0.951, 0.05), 3)), (1.33, np.round(np.arange(0.2, 1.251, 0.05), 3)))


def fwhm(s, y):
    """FWHM of the central peak (at s = 0), normalized to its value at s = 0."""
    i0 = int(np.argmin(np.abs(s)))
    y = y / y[i0]
    r = i0
    while r < len(y) - 1 and y[r] >= 0.5:
        r += 1
    l = i0
    while l > 0 and y[l] >= 0.5:
        l -= 1
    if y[r] >= 0.5 or y[l] >= 0.5:
        return np.nan
    return np.interp(0.5, [y[r], y[r - 1]], [s[r], s[r - 1]]) - np.interp(0.5, [y[l], y[l + 1]], [s[l], s[l + 1]])


def widths(na, n, model):
    """{(signal, axis, θ): FWHM in µm} at one NA."""
    xs = np.linspace(-2.5 * LP / na, 2.5 * LP / na, 4001)
    zs = np.linspace(-6 * LP * n / na ** 2, 6 * LP * n / na ** 2, 8001)
    out = {}
    for axis, s in (('x', xs), ('z', zs)):
        X, Z = (s, 0 * s) if axis == 'x' else (0 * s, s)
        f = lambda lam, th: beam_field(X, Z, lam, na, n=n, theta=th, model=model)
        p1, c1 = f(LP, 0.0), f(L1, 0.0)
        for th in THETAS:
            out[('2PE', axis, th)] = fwhm(s, two_photon(p1, f(LP, th)))
            out[('2CE', axis, th)] = fwhm(s, two_color(c1, f(L2, th)))
    return out


def fits(na, n, th):
    return th != np.pi / 2 or na <= n * np.sin(np.pi / 4) + 1e-9


CSV = os.path.join(OUT, 'widths.csv')
rows = []
for n, nas in (MEDIA if '--rerun' in sys.argv or not os.path.exists(CSV) else ()):
    for na in nas:
        W = {m: widths(na, n, m) for m in ('paraxial', 'rw')}
        for (sig, axis, th) in W['rw']:
            if fits(na, n, th):
                rows.append((n, na, sig, axis, th, W['paraxial'][(sig, axis, th)], W['rw'][(sig, axis, th)]))
        print(f'n = {n} NA {na:.2f} done', flush=True)
if rows:
    A = np.array([(r[0], r[1], r[2] == '2CE', r[3] == 'z', r[4], r[5], r[6]) for r in rows], float)
    np.savetxt(CSV, A, delimiter=',', fmt='%.6g', header='n,NA,is_2CE,is_axial,theta,fwhm_scalar_um,fwhm_vector_um')
A = np.loadtxt(CSV, delimiter=',', ndmin=2)


def sel(n, sig, axis, th):
    m = (A[:, 0] == n) & (A[:, 2] == (sig == '2CE')) & (A[:, 3] == (axis == 'z')) & np.isclose(A[:, 4], th)
    return A[m][:, [1, 5, 6]]


# ── widths against NA: rows transverse / axial, columns 2PE / 2CE; solid vector, dashed scalar ──
for n, tag in ((1.0, 'air'), (1.33, 'water')):
    fig, axes = plt.subplots(2, 2, figsize=(28, 14), sharex=True)
    for c, sig in enumerate(('2PE', '2CE')):
        for r, axis in enumerate(('x', 'z')):
            ax = axes[r, c]
            for th in THETAS:
                d = sel(n, sig, axis, th)
                ax.plot(d[:, 0], d[:, 2], '-o', color=TCOL[th], lw=3, ms=8, label=f'{TLAB[th]}, vector')
                ax.plot(d[:, 0], d[:, 1], '--', color=TCOL[th], lw=2.5, label=f'{TLAB[th]}, scalar')
            ax.set_xscale('log'); ax.set_yscale('log')
            ax.set_xticks([0.2, 0.3, 0.5, 0.7, 1.0]); ax.set_xticklabels(['0.2', '0.3', '0.5', '0.7', '1'])
            ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
            ax.yaxis.set_major_locator(matplotlib.ticker.LogLocator(subs=(1, 2, 5)))
            ax.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%g'))
            ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
            ax.set_title(f'{sig}, {"transverse FWHM" if axis == "x" else "DOF (axial FWHM)"}')
            ax.set_ylabel('Width (µm)')
            if r == 1:
                ax.set_xlabel('NA')
    h, l = axes[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc='center left', ncol=1, bbox_to_anchor=(1.0, 0.5), frameon=False)
    plt.tight_layout()
    fig.savefig(os.path.join(OUT, f'widths_{tag}.png'), dpi=300, bbox_inches='tight'); plt.close(fig)
    print('Saved -> widths_%s.png' % tag)

# ── the paper's comparisons at θ = π/2 against NA (air and water), vector solid, scalar dashed ──
P = np.pi / 2
RAT = (('F2p(x;π/2) / F2p(x;0)', ('2PE', 'x', P), ('2PE', 'x', 0.0)),
       ('F2c(x;π/2) / F2p(x;π/2)', ('2CE', 'x', P), ('2PE', 'x', P)),
       ('DOF F2c(z;π/2) / F2p(z;π/2)', ('2CE', 'z', P), ('2PE', 'z', P)))
fig, axes = plt.subplots(1, 3, figsize=(30, 9))
for ax, (lab, a, b) in zip(axes, RAT):
    for n, mk, tag in ((1.0, 'o', 'air'), (1.33, 's', 'water')):
        da, db = sel(n, *a), sel(n, *b)
        nas = np.intersect1d(da[:, 0], db[:, 0])
        ia = np.isin(da[:, 0], nas); ib = np.isin(db[:, 0], nas)
        ax.plot(nas, da[ia, 2] / db[ib, 2], '-' + mk, color='#1f77b4', mfc='white' if n > 1 else '#1f77b4', lw=3, ms=10,
                label=f'Vector, {tag}')
        ax.plot(nas, da[ia, 1] / db[ib, 1], '--' + mk, color='#d62728', mfc='white' if n > 1 else '#d62728', lw=2.5,
                ms=8, label=f'Scalar, {tag}')
    ax.axvline(0.5, color='#999999', lw=2, ls=':')
    ax.set_title(lab); ax.set_xlabel('NA'); ax.set_ylabel('Ratio')
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, loc='lower center', ncol=4, bbox_to_anchor=(0.5, -0.1), frameon=False)
plt.tight_layout()
fig.savefig(os.path.join(OUT, 'ratios.png'), dpi=300, bbox_inches='tight'); plt.close(fig)
print('Saved -> ratios.png')

for n in (1.0, 1.33):
    for lab, a, b in RAT:
        da, db = sel(n, *a), sel(n, *b)
        for na in (0.5, 0.7, 0.9):
            ia, ib = np.isclose(da[:, 0], na), np.isclose(db[:, 0], na)
            if ia.any() and ib.any():
                print(f'n {n} NA {na}: {lab}: scalar {da[ia, 1][0] / db[ib, 1][0]:.3f}, vector {da[ia, 2][0] / db[ib, 2][0]:.3f}')
