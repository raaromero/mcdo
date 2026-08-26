"""
Vector-component atlas — the same configurations rendered two ways:
  Ex_only/   azimuthally-averaged |Ex|²  = |I₀|² + ½|I₂|²    (scalar-like)
  full/      azimuthally-averaged |E|²   = |I₀|² + |I₂|² + 2|I₁|²  (Ex+Ey+Ez)

separated into folders so the vector (Ey,Ez) contribution is explicit. Both
are rotationally symmetric (proper azimuthal averages), so a single r–z card
is well defined. On the axis (r=0) I₁=I₂=0 ⇒ the two are identical — the axial
profiles coincide (a consistency check); the difference is purely off-axis and
grows with NA (the longitudinal/cross-pol vector effect of Phase 2).

Component reference (x-polarized input, [Rom03 Eqs. 2–4]):
  <|Ex|²> = |I₀|² + ½|I₂|²,  <|Ey|²> = ½|I₂|²,  <|Ez|²> = 2|I₁|².

Output: output/atlas_components/{Ex_only,full}/{family}/<config>.png
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo.style import apply as _apply_style
_apply_style()
from matplotlib.colors import LogNorm

from mcdo import SimConfig
from mcdo.rw_integrals import compute_integrals
from mcdo.annular import compute_integrals_annular
from mcdo.apodization import gaussian, axicon

LAM, N_MED = 0.750, 1.3
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', 'atlas_components')
LEVELS = [0.5, 1, 2, 4, 6, 10, 20, 40, 60, 80, 100]


import argparse

MODES = {'full': ('full', 'all three components'),
         'ex':   ('Ex_only', 'transverse component only')}
_ap = argparse.ArgumentParser(description='Component comparison cards.')
_ap.add_argument('--component', choices=sorted(MODES), nargs='+', default=['full'],
                 help='which focal intensities to render (default: full)')
_args, _ = _ap.parse_known_args()


def mirror(Ih):
    return np.concatenate([Ih[:, ::-1][:, :-1], Ih], axis=1)


def Ex_only(I0, I1, I2):
    return np.abs(I0) ** 2 + 0.5 * np.abs(I2) ** 2


def full_vec(I0, I1, I2):
    return np.abs(I0) ** 2 + np.abs(I2) ** 2 + 2 * np.abs(I1) ** 2


def card(h, v, I, title, outpath, base_tr=None, base_ax=None, airy_um=None,
         hlabel='Radial position r (μm)', vlabel='Axial position z (μm)',
         curve_label='this configuration', base_label='uniform disk, all components'):
    ih0 = np.argmin(np.abs(h)); izpk = np.argmax(I[:, ih0])
    fig = plt.figure(figsize=(11.3, 6.8))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.15, 1], hspace=0.55, wspace=0.75)
    axm = fig.add_subplot(gs[:, 0]); axt = fig.add_subplot(gs[0, 1])
    axa = fig.add_subplot(gs[1, 1]); fig.suptitle(title, fontsize=11)
    HH, VV = np.meshgrid(h, v); ext = [h[0], h[-1], v[0], v[-1]]
    im = axm.imshow(I, extent=ext, origin='lower', aspect='auto', cmap='inferno',
                    norm=LogNorm(1e-3, 1))
    cb = fig.colorbar(im, ax=axm, fraction=0.040, pad=0.02, shrink=0.85)
    cb.set_label('Normalized intensity', fontsize=8); cb.ax.tick_params(labelsize=7)
    from mcdo.figio import mark_focus
    mark_focus(axm, HH, VV, I / I.max(), airy_um=airy_um)
    axm.contour(HH, VV, 100 * I / I.max(), levels=LEVELS, colors='w',
                linewidths=0.4, alpha=0.45)
    axm.set_xlabel(hlabel); axm.set_ylabel(vlabel)
    axm.set_title('(a) Two-dimensional map with contours', fontsize=9)
    axt.plot(h, I[izpk], 'k-', lw=2.0, label=curve_label)
    if base_tr is not None:
        axt.plot(h, base_tr, 'k:', lw=2.0, label=base_label)
    axt.set_ylim(0, 1.05); axt.set_xlim(h[0], h[-1]); axt.legend(loc='upper left', bbox_to_anchor=(1.02, 1.0), frameon=False, borderaxespad=0.0)
    axt.set_xlabel(hlabel); axt.set_ylabel('Normalized intensity')
    axt.set_title('(b) Transverse profile', fontsize=9)
    axa.plot(v, I[:, ih0], 'k-', lw=2.0)
    if base_ax is not None:
        axa.plot(v, base_ax, 'k:', lw=2.0)
    axa.set_ylim(0, 1.05); axa.set_xlim(v[0], v[-1])
    axa.set_xlabel(vlabel); axa.set_ylabel('Normalized intensity')
    axa.set_title('(c) Axial profile (r = 0)', fontsize=9)
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    fig.savefig(outpath, dpi=300, bbox_inches='tight'); plt.close(fig)


r_half = np.linspace(0.0, 2.0, 161)
z_arr = np.linspace(-6.0, 6.0, 261)
r_full = np.concatenate([-r_half[::-1][:-1], r_half])
c8 = SimConfig(lam_c=LAM, X_NA=0.8, n=N_MED, tau=np.inf, N_freq=3, N_theta=801)


def integ(kind, val):
    if kind == 'NA':
        c = SimConfig(lam_c=LAM, X_NA=val, n=N_MED, tau=np.inf, N_freq=3, N_theta=901)
        return compute_integrals(r_half, z_arr, c.k_c, c.alpha, c.N_theta)
    if kind == 'gaussian':
        A = None if val == 0 else gaussian(val, c8.sin2_alpha)
        return compute_integrals(r_half, z_arr, c8.k_c, c8.alpha, c8.N_theta, apodization=A)
    if kind == 'annular':
        return compute_integrals_annular(r_half, z_arr, c8.k_c, c8.alpha, val, c8.N_theta)
    if kind == 'axicon':
        A = None if val == 0 else axicon(val, c8.sin_alpha)
        return compute_integrals(r_half, z_arr, c8.k_c, c8.alpha, 2001, apodization=A)


# uniform full-vector baseline for the cross-section dotted reference
I0, I1, I2 = integ('gaussian', 0)
UNI = mirror(full_vec(I0, I1, I2)); UNI /= UNI.max()
uni_tr = UNI[np.argmax(UNI[:, np.argmin(np.abs(r_full))])]
uni_ax = UNI[:, np.argmin(np.abs(r_full))]

FAMILIES = [
    ('NA', [0.1, 0.5, 0.8, 1.2], lambda v: f'{v}'),
    ('gaussian', [0.0, 2.0, 4.0], lambda v: f'truncation coefficient {v:g}'),
    ('annular', [0.0, 0.5, 0.9, 0.99], lambda v: f'obstruction ratio {v}'),
    ('axicon', [0, 20, 40], lambda v: f'conical phase depth {v}'),
]

for fam, vals, lab in FAMILIES:
    print(f"{fam} …")
    for val in vals:
        I0, I1, I2 = integ(fam, val)
        for mode, fn in [(MODES[c][0], {'full': full_vec, 'ex': Ex_only}[c])
                         for c in _args.component]:
            I = mirror(fn(I0, I1, I2)); I /= I.max()
            name = str(val).replace('.', 'p')
            extra = '' if fam == 'NA' else ', NA = 0.8'
            famname = {'NA': 'Numerical aperture', 'gaussian': 'Gaussian input',
                       'annular': 'Annular aperture', 'axicon': 'Axicon'}[fam]
            modename = ('transverse component only' if mode == 'Ex_only'
                        else 'all three components')
            airy_um = 0.61 * LAM / (val if fam == 'NA' else 0.8)
            title = f'{famname}, {lab(val)} — {modename}{extra}'
            card(r_full, z_arr, I, title,
                 os.path.join(OUT, mode, fam, f'{name}.png'), uni_tr, uni_ax,
                 airy_um=airy_um, curve_label=f'{lab(val)}, {modename}')
    print(f"  {fam}: {len(vals)} configs × {len(_args.component)} mode(s)")

print("vector atlas done →", OUT)
