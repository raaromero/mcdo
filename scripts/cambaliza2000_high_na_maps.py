r"""2CE and 2PE point spread functions in the x–z plane at NA 0.5 and at a higher NA: the paraxial scalar model of
Cambaliza & Saloma (2000) against the vector (Richards–Wolf) focus, for each lens angle.

One figure per signal and lens angle, two panels: NA 0.5 and NA 0.9 (NA 0.7 for crossed lenses, which fit up to NA 0.71
in air). Each panel shows the vector PSF as a heat map with its contours at 10, 50 and 90% of the peak (solid lines) and
the contours of the paraxial scalar PSF at the same levels (dashed lines). Air, circular pupils, uniform input, both
beams polarized along y (perpendicular to the plane of the lens axes); 2CE with 750 and 656 nm, 2PE with 700 nm.

    python scripts/cambaliza2000_high_na_maps.py
    -> output/08_two_color/cambaliza2000/high_na/maps/psf_<2ce|2pe>_<0|pi2|pi>.png and widths.txt (FWHM across and along)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from mcdo.style import apply as _apply_style
from mcdo.twobeam import beam_field, two_color, two_photon
from cambaliza2000_pulses_sweep import fwhm

_apply_style()
matplotlib.rcParams.update({'font.size': 34, 'axes.titlesize': 38, 'axes.labelsize': 36, 'xtick.labelsize': 30,
                            'ytick.labelsize': 30, 'legend.fontsize': 32, 'axes.grid': False})   # legible at a third of the slide
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'cambaliza2000', 'high_na', 'maps')
os.makedirs(OUT, exist_ok=True)
L1, L2, LP = 0.750, 0.656, 0.700
TH = {'0': 0.0, 'pi2': np.pi / 2, 'pi': np.pi}
TLAB = {'0': 'θ = 0', 'pi2': 'θ = π/2', 'pi': 'θ = π'}
LEVELS = (0.1, 0.5, 0.9)
N = 241


def field(X, Z, lam, na, theta, model):
    """beam_field on a grid, in blocks of points (the vector field holds one row per point and ray angle)."""
    kw = dict(model='rw', psi=np.pi / 2) if model == 'vector' else {}
    x, z = X.ravel(), Z.ravel()
    parts = [beam_field(x[i:i + 4000], z[i:i + 4000], lam, na, theta=theta, **kw) for i in range(0, x.size, 4000)]
    E = np.concatenate(parts, axis=-1)
    return E.reshape(E.shape[:-1] + X.shape)


def psf(X, Z, sig, tk, na, model):
    if sig == '2ce':
        F = two_color(field(X, Z, L1, na, 0.0, model), field(X, Z, L2, na, TH[tk], model))
    else:
        F = two_photon(field(X, Z, LP, na, 0.0, model), field(X, Z, LP, na, TH[tk], model))
    return F / F.max()


def window(tk, na):
    """Half-widths of the window (µm): the spot scales as 1/NA across the axis and 1/NA² along it."""
    if tk == 'pi2':
        return 1.4 * 0.5 / na, 1.4 * 0.5 / na
    return 1.1 * 0.5 / na, 4.6 * (0.5 / na) ** 2


def main():
    lines = []
    for sig, tk in (('2ce', '0'), ('2ce', 'pi2'), ('2pe', '0'), ('2pe', 'pi2'), ('2pe', 'pi')):
        nas = (0.5, 0.7) if tk == 'pi2' else (0.5, 0.9)
        fig, axes = plt.subplots(1, 2, figsize=(22, 10))
        for ax, na in zip(axes, nas):
            hx, hz = window(tk, na)
            x, z = np.linspace(-hx, hx, N), np.linspace(-hz, hz, N)
            X, Z = np.meshgrid(x, z)
            Fv, Fs = psf(X, Z, sig, tk, na, 'vector'), psf(X, Z, sig, tk, na, 'scalar')
            im = ax.pcolormesh(X, Z, Fv, cmap='Blues', vmin=0, vmax=1, shading='gouraud', rasterized=True)
            ax.contour(X, Z, Fv, levels=LEVELS, colors='k', linewidths=(2.0, 3.5, 2.0))
            ax.contour(X, Z, Fs, levels=LEVELS, colors='#d62728', linewidths=(2.0, 3.5, 2.0), linestyles='--')
            ax.set(xlabel='x (µm)', ylabel='z (µm)', title=f'NA {na:g}')
            ax.locator_params(nbins=5)
            i0 = N // 2
            w = {m: (fwhm(x, F[i0, :]), fwhm(z, F[:, i0])) for m, F in (('vector', Fv), ('scalar', Fs))}
            lines.append(f'{sig} {tk} NA {na:g}: FWHM across the axis, vector {w["vector"][0]:.3f} µm, scalar '
                         f'{w["scalar"][0]:.3f} µm ({100 * (w["scalar"][0] / w["vector"][0] - 1):+.1f}%); along the axis, vector '
                         f'{w["vector"][1]:.3f} µm, scalar {w["scalar"][1]:.3f} µm ({100 * (w["scalar"][1] / w["vector"][1] - 1):+.1f}%); '
                         f'largest difference of the two normalized PSFs {np.abs(Fs - Fv).max():.3f}')
            print(lines[-1], flush=True)
        fig.subplots_adjust(left=0.08, right=0.89, wspace=0.3, top=0.74, bottom=0.13)   # room for the key above the titles
        cb = fig.colorbar(im, cax=fig.add_axes([0.91, 0.13, 0.018, 0.61]))
        cb.set_label('Vector PSF (of its peak)')
        fig.legend([Line2D([], [], color='k', lw=3.5), Line2D([], [], color='#d62728', lw=3.5, ls='--')],
                   ['vector (Richards–Wolf)', 'paraxial scalar'], loc='upper center', bbox_to_anchor=(0.48, 1.0), ncol=2,
                   frameon=False,
                   title=f'{sig.upper()}, {TLAB[tk]}: contours at 10, 50 and 90% of the peak', title_fontsize=32)
        fig.savefig(os.path.join(OUT, f'psf_{sig}_{tk}.png'), dpi=600)
        plt.close(fig)
    with open(os.path.join(OUT, 'widths.txt'), 'w') as f:
        f.write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
