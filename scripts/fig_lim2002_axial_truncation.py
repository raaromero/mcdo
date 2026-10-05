r"""Axial profiles only: Lim & Saloma's paraxial scalar focus against Gaussian
truncation, and scalar against vector at the same truncation.

Single beam, λ = 750 nm, air, on the optical axis (x = 0), where every
polarization convention gives the same intensity. Truncation
A(ϑ) = exp(−α_t sin²ϑ / sin²α), identical in all models (exactly exp(−α_t ρ²)
on the scalar pupil).

  Set 1  Lim & Saloma's paraxial scalar focus (uniform) against the paraxial
         scalar focus with α_t = 0.5, 1, 2, 4, at NA 0.3 and 0.5. As α_t → 0
         the truncated curves must fall on Lim & Saloma's.
  Set 2  scalar (paraxial) against vector (Richards–Wolf, mcdo.twobeam) at the
         same α_t = 0, 1, 4, at NA 0.1, 0.3, 0.5, with the Richards–Wolf engine
         of the rest of the analysis (mcdo.rw_integrals) overlaid. At low NA
         all must coincide.

    python scripts/fig_lim2002_axial_truncation.py
    -> output/08_two_color/lim2002/axial_lim_vs_truncation.png, axial_scalar_vs_vector_truncation.png
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

from mcdo.apodization import gaussian
from mcdo.rw_integrals import compute_integrals
from mcdo.twobeam import beam_field, intensity

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002')
LAM = 0.750


def axial(na, at, model):
    z = np.linspace(-3.0 * 2 * LAM / na ** 2, 3.0 * 2 * LAM / na ** 2, 1201)
    ap = gaussian(at, na ** 2) if at else None
    if model == 'mcdo':
        I0, I1, I2 = compute_integrals(np.array([0.0]), z, 2 * np.pi / LAM, np.arcsin(na), apodization=ap)
        I = np.abs(I0[:, 0]) ** 2
    elif model == 'scalar':
        I = intensity(beam_field(0 * z, z, LAM, na, apodization=ap))
    else:
        I = intensity(beam_field(0 * z, z, LAM, na, model='rw', psi=0.0, apodization=ap))
    return z, I / I.max()


# ── set 1: Lim & Saloma against truncation, scalar ──
fig, axes = plt.subplots(1, 2, figsize=(18.2, 6.0))     # twice its width on the slide: 24-pt text shows at 12 pt
cols = {0.5: '#ff7f0e', 1: '#2ca02c', 2: '#9467bd', 4: '#d62728'}
for a, na in zip(axes, (0.3, 0.5)):
    z, I = axial(na, 0, 'scalar')
    a.plot(z, I, '-', color='k', lw=5, label='Uniform input')
    for at in (0.5, 1, 2, 4):
        z, I = axial(na, at, 'scalar')
        a.plot(z, I, '--', color=cols[at], lw=3.5, label=f'α$_t$ = {at}')
    a.set_xlabel('z (µm)'); a.set_ylabel('On-axis intensity')
    a.set_title(f'NA {na}')
    a.set_ylim(0, 1.05)
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, loc='lower center', ncol=5, bbox_to_anchor=(0.5, -0.14), frameon=False)
plt.tight_layout()
fig.savefig(os.path.join(OUT, 'axial_lim_vs_truncation.png'), dpi=600, bbox_inches='tight')
plt.close(fig)

# ── set 2: scalar against vector at the same truncation ──
NAS, ATS = (0.1, 0.3, 0.5), (0, 4)                     # rows: uniform and α_t = 4; columns: NA
fig, axes = plt.subplots(len(ATS), len(NAS), figsize=(15.0, 6.0))   # about twice its width on the slide
for c, na in enumerate(NAS):
    for r, at in enumerate(ATS):
        a = axes[r, c]
        for model, lab, col, ls, lw in (('scalar', 'Paraxial scalar', '#d62728', '-', 5),
                                        ('rw', 'Vector, two-beam code', '#1f77b4', '--', 3.5),
                                        ('mcdo', 'Vector, analysis code', 'k', ':', 3.5)):
            z, I = axial(na, at, model)
            a.plot(z, I, ls, color=col, lw=lw, label=lab)
        s = axial(na, at, 'scalar')[1]; v = axial(na, at, 'rw')[1]
        print(f'NA {na} α_t={at}: max |scalar − vector| on axis = {np.abs(s - v).max():.4f}; '
              f'max |twobeam − rw_integrals| = {np.abs(v - axial(na, at, "mcdo")[1]).max():.2e}', flush=True)
        a.set_title(f'NA {na}, α$_t$ = {at}', fontsize=28)
        a.set_ylim(0, 1.05)
        if r == len(ATS) - 1:
            a.set_xlabel('z (µm)')

h, l = axes[0, 0].get_legend_handles_labels()
fig.legend(h, l, loc='lower center', ncol=3, bbox_to_anchor=(0.5, -0.1), frameon=False)
fig.supylabel('On-axis intensity, normalized', fontsize=28)
fig.suptitle('Scalar against vector on axis, uniform and α$_t$ = 4', fontsize=32, y=1.03)
plt.tight_layout()
fig.savefig(os.path.join(OUT, 'axial_scalar_vs_vector_truncation.png'), dpi=600, bbox_inches='tight')
plt.close(fig)
print('Saved -> axial_lim_vs_truncation.png, axial_scalar_vs_vector_truncation.png')
