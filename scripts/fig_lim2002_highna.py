r"""Lim & Saloma (2002) at high NA: the 2CE peak-signal cuts of their Fig. 4,
recomputed with the vector Richards–Wolf focus.

Three models, all 2CE (λ1 = 750 nm, λ2 = 656 nm) in air:
    paraxial scalar, NA 0.5   the paper's model
    Richards–Wolf,   NA 0.5   same NA, exact vector focus: checks the paper's model
    Richards–Wolf,   NA 0.7   near the largest NA at which two cones can cross
                              at θ = π/2 in air, n/√2 = 0.71

Both beams are unpolarized, as the scalar model implicitly assumes: each
beam's intensity is the average over two orthogonal input polarizations,
I = (I_x + I_y)/2, and the two colors do not interfere, so F_2c = I_1 I_2. The
peak is taken over the paper's ±1 × ±5 µm window and divided by the aligned
peak; cuts run along x_c (z_c = 0) and along z_c (x_c = 0), for θ = π/2 and π.

    python scripts/fig_lim2002_highna.py
    -> output/08_two_color/lim2002/highna_tolerance.png
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

from mcdo.twobeam import beam_field, intensity

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002')
L1, L2 = 0.750, 0.656
DX, DZ = 0.02, 0.1                               # µm, the paper's grid
NX, NZ = 50, 50                                  # window ±1 × ±5 µm
MX, MZ = 50, 30                                  # offsets up to 1.0 µm across, 3.0 µm along
MODELS = [('paraxial', 0.5, 'Paraxial scalar, NA 0.5 (paper)', '#555555', '-'),
          ('rw', 0.5, 'Richards–Wolf, NA 0.5, unpolarized', '#1f77b4', '--'),
          ('rw', 0.7, 'Richards–Wolf, NA 0.7, unpolarized', '#d62728', '-')]

XW, ZW = np.meshgrid(np.arange(-NX, NX) * DX, np.arange(-NZ, NZ) * DZ)
XE, ZE = np.meshgrid(np.arange(-NX - MX, NX + MX) * DX, np.arange(-NZ - MZ, NZ + MZ) * DZ)


def unpolarized(x, z, lam, na, theta, model):
    """Intensity of an unpolarized beam: the mean over two orthogonal input polarizations."""
    if model != 'rw':
        return intensity(beam_field(x, z, lam, na, theta=theta, model=model))
    return 0.5 * sum(intensity(beam_field(x, z, lam, na, theta=theta, model=model, psi=psi))
                     for psi in (0.0, np.pi / 2))


def cuts(model, na, theta):
    """Peak 2CE signal, relative to aligned, along x_c (z_c = 0) and along z_c (x_c = 0)."""
    I1 = unpolarized(XW, ZW, L1, na, 0.0, model)
    I2 = unpolarized(XE, ZE, L2, na, theta, model)
    sz, sx = XW.shape

    def peak(ix, iz):
        return (I1 * I2[MZ - iz:MZ - iz + sz, MX - ix:MX - ix + sx]).max()

    p0 = peak(0, 0)
    px = np.array([peak(i, 0) for i in range(MX + 1)]) / p0
    pz = np.array([peak(0, i) for i in range(MZ + 1)]) / p0
    return np.arange(MX + 1) * DX, px, np.arange(MZ + 1) * DZ, pz


def at_20(d, p):
    """Offset at which 20% of the peak is lost, or None inside the range."""
    below = np.nonzero(p < 0.8)[0]
    if not below.size:
        return None
    i = below[0]
    return float(np.interp(0.8, [p[i], p[i - 1]], [d[i], d[i - 1]]))


fig, axes = plt.subplots(2, 2, figsize=(22.0, 18.0))
lines = []
for r, (theta, tl) in enumerate(((np.pi / 2, 'θ = π/2'), (np.pi, 'θ = π'))):
    for model, na, lab, col, ls in MODELS:
        xc, px, zc, pz = cuts(model, na, theta)
        ax, az = axes[r]
        l, = ax.plot(xc, px, ls, color=col, lw=4, label=lab)
        az.plot(zc, pz, ls, color=col, lw=4)
        if r == 0:
            lines.append(l)
        tx, tz = at_20(xc, px), at_20(zc, pz)
        fmt = lambda v, lim: f'{v:.2f} µm' if v is not None else f'> {lim:.1f} µm'
        print(f'2CE {tl}, {lab}: 20% lost at x_c = {fmt(tx, xc[-1])}, at z_c = {fmt(tz, zc[-1])}; '
              f'peak at x_c = 1.0 µm: {px[-1]:.2f}, at z_c = 1.0 µm: {pz[10]:.2f}')
    for a, xl in ((axes[r, 0], 'In-plane offset x$_c$ (µm)'), (axes[r, 1], 'Axial offset z$_c$ (µm)')):
        a.axhline(0.8, color='#999999', lw=2, ls=':')
        a.set_xlabel(xl); a.set_ylabel('Peak, relative to aligned')
        a.set_ylim(0, 1.05); a.set_title(f'2CE, {tl}')
    axes[r, 0].set_xlim(0, 1.0); axes[r, 1].set_xlim(0, 3.0)
fig.legend(handles=lines, loc='lower center', ncol=3, bbox_to_anchor=(0.5, -0.02))
plt.tight_layout(rect=(0, 0.05, 1, 1))
fig.savefig(os.path.join(OUT, 'highna_tolerance.png'), dpi=600, bbox_inches='tight')
print('Saved -> highna_tolerance.png')
