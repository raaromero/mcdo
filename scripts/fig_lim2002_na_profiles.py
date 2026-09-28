r"""Lim & Saloma's scalar focus against the Debye integrals: axial and radial
profiles of the aligned 2CE PSF at the NAs where the scalar error fires.

Three models, 2CE (λ1 = 750 nm, λ2 = 656 nm), air, uniform input:
    paraxial scalar   Lim & Saloma's model (Lommel form)
    scalar Debye      the full Debye integral, exact kz cos ϑ phase and the
                      aplanatic √cos ϑ, but no polarization
    vector Debye      Richards–Wolf (Debye–Wolf), unpolarized beams
The middle model splits the scalar model's error into its paraxial part
(paraxial against scalar Debye) and its polarization part (scalar Debye
against vector).

NAs: 0.45 and 0.6, where the axial scalar error first exceeds 5% and 10%
(fig_lim2002_na_breakdown.py); 0.5, the paper's; and at θ = π also 0.8, where
the lateral error reaches 5%, and 0.95. θ = π/2 stops at 0.70.

    python scripts/fig_lim2002_na_profiles.py
    -> output/08_two_color/lim2002/na_profiles_theta_pi.png, na_profiles_theta_pi2.png
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
MODELS = [('paraxial', 'paraxial scalar (Lim & Saloma)', '#d62728', '--'),
          ('debye', 'scalar Debye', '#ff7f0e', ':'),
          ('rw', 'vector Debye (Richards–Wolf)', '#1f77b4', '-')]
CASES = {'pi': (np.pi, 'θ = π', (0.45, 0.5, 0.6, 0.8, 0.95)),
         'pi2': (np.pi / 2, 'θ = π/2', (0.45, 0.5, 0.6, 0.7))}


def I(x, z, lam, na, theta, model):
    if model == 'rw':
        return 0.5 * sum(intensity(beam_field(x, z, lam, na, 1.0, theta=theta, model='rw', psi=p))
                         for p in (0.0, np.pi / 2))
    return intensity(beam_field(x, z, lam, na, 1.0, theta=theta, model=model))


def fwhm(c, g):
    c = c / c.max(); i = int(np.argmax(c)); l = r = i
    while l > 0 and c[l] >= 0.5:
        l -= 1
    while r < len(c) - 1 and c[r] >= 0.5:
        r += 1
    return (np.interp(0.5, [c[r], c[r - 1]], [g[r], g[r - 1]])
            - np.interp(0.5, [c[l], c[l + 1]], [g[l], g[l + 1]]))


for key, (th, tl, nas) in CASES.items():
    fig, axes = plt.subplots(len(nas), 2, figsize=(16.0, 4.6 * len(nas)))
    for r, na in enumerate(nas):
        hx = 1.2 * 0.5 / na
        hz = (5.0 * (0.5 / na) ** 2) if th == np.pi else 1.2 * 0.5 / na
        xs, zs = np.linspace(-hx, hx, 2001), np.linspace(-hz, hz, 4001)
        w = {}
        for m, lab, col, ls in MODELS:
            px = I(xs, 0 * xs, L1, na, 0.0, m) * I(xs, 0 * xs, L2, na, th, m)
            pz = I(0 * zs, zs, L1, na, 0.0, m) * I(0 * zs, zs, L2, na, th, m)
            axes[r, 0].plot(xs, px / px.max(), ls, color=col, lw=3.5, label=lab)
            axes[r, 1].plot(zs, pz / pz.max(), ls, color=col, lw=3.5)
            w[m] = (fwhm(px, xs), fwhm(pz, zs))
        for c, (ax, d) in enumerate(((axes[r, 0], 'x'), (axes[r, 1], 'z'))):
            e_p = 100 * (w['paraxial'][c] / w['rw'][c] - 1)
            e_d = 100 * (w['debye'][c] / w['rw'][c] - 1)
            ax.text(0.03, 0.95, f'NA {na}\nparaxial {e_p:+.1f}%\nscalar Debye {e_d:+.1f}%',
                    transform=ax.transAxes, va='top', fontsize=20)
            ax.set_xlabel(f'{d} (µm)')
            ax.set_ylabel('2CE, normalized')
            ax.set_ylim(0, 1.05)
        print(f'{tl} NA {na}: FWHM x paraxial/scalar Debye/vector {w["paraxial"][0]*1e3:.0f}/{w["debye"][0]*1e3:.0f}/'
              f'{w["rw"][0]*1e3:.0f} nm; z {w["paraxial"][1]*1e3:.0f}/{w["debye"][1]*1e3:.0f}/{w["rw"][1]*1e3:.0f} nm',
              flush=True)
    axes[0, 0].set_title('Across the axis, z = 0')
    axes[0, 1].set_title('Along the axis, x = 0')
    h, l = axes[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc='lower center', ncol=1, bbox_to_anchor=(0.5, -0.07))
    fig.suptitle(f'2CE aligned PSF profiles, {tl}; width error relative to vector', fontsize=32, y=1.01)
    plt.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(os.path.join(OUT, f'na_profiles_theta_{key}.png'), dpi=600, bbox_inches='tight')
    plt.close(fig)
print('Saved -> na_profiles_theta_pi.png, na_profiles_theta_pi2.png')
