"""Extension and transmission against obstruction ratio, for several
alphas.

The illumination is compared elsewhere at a single alpha. This
sweeps it, so the trend from uniform illumination to a strongly truncated
Gaussian is visible as a family of curves rather than as two cases.

One curve per alpha, over the obstruction ratio, at fixed
numerical aperture and wavelength. The paraxial expression is drawn for
reference on the extension panel.
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

from mcdo import SimConfig
from mcdo.annular import compute_integrals_annular
from mcdo.apodization import gaussian
from mcdo.components import full as vec_intensity
from mcdo.figio import save_panels
from mcdo.rw_integrals import compute_integrals

LAM, XNA, NT = 0.750, 0.8, 801
ALPHAS = [0.0, 1.0, 2.0, 4.0, 8.0]
EPS = [0.0, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99]
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '02_na_apodization')

cfg = SimConfig(lam_c=LAM, X_NA=XNA, n=1.3, tau=np.inf, N_freq=3, N_theta=NT)
r = np.linspace(0.0, 4.0 * LAM / XNA, 900)
z = np.linspace(0.0, 40.0 * 2.0 * LAM / XNA ** 2, 4000)
r0, z0 = np.array([0.0]), np.array([0.0])


def _fwhm(x, y):
    y = y / y.max()
    below = np.where(y < 0.5)[0]
    if not len(below):
        return np.nan
    i = below[0]
    return 2.0 * np.interp(0.5, [y[i], y[i - 1]], [x[i], x[i - 1]])


def _run(at, eps):
    apod = None if at == 0 else gaussian(at, cfg.sin2_alpha)
    if eps == 0.0:
        A0, A1, A2 = compute_integrals(r0, z, cfg.k_c, cfg.alpha, NT, apodization=apod)
        B0, B1, B2 = compute_integrals(r, z0, cfg.k_c, cfg.alpha, NT, apodization=apod)
    else:
        A0, A1, A2 = compute_integrals_annular(r0, z, cfg.k_c, cfg.alpha, eps, NT,
                                               apodization=apod)
        B0, B1, B2 = compute_integrals_annular(r, z0, cfg.k_c, cfg.alpha, eps, NT,
                                               apodization=apod)
    depth = _fwhm(z, vec_intensity(A0[:, 0], A1[:, 0], A2[:, 0]))
    width = _fwhm(r, vec_intensity(B0[0], B1[0], B2[0])) * 1000.0

    th = np.linspace(0.0, cfg.alpha, 4001)
    A = np.ones_like(th) if apod is None else np.abs(np.asarray(apod(th)))
    w = A ** 2 * np.sin(th) * np.cos(th)
    th_in = np.arcsin(eps * np.sin(cfg.alpha))
    trans = float(np.trapezoid(w[th >= th_in], th[th >= th_in]) / np.trapezoid(w, th))
    return depth, width, trans


res = {}
print(f"{'alpha':>6} {'eps':>6} {'depth um':>10} {'width nm':>10} "
      f"{'extension':>10} {'transmission':>13}")
for at in ALPHAS:
    base = None
    for eps in EPS:
        d, wid, t = _run(at, eps)
        if eps == 0.0:
            base = d
        res[(at, eps)] = dict(depth=d, width=wid, gain=d / base, transmission=t)
        print(f"{at:>6.1f} {eps:>6.2f} {d:>10.3f} {wid:>10.1f} "
              f"{d / base:>10.2f} {t:>13.4f}")

# saved so the dashboard can show these numbers beside the alpha-sweep fields;
# it had the maps for those cells but no measured quantities to put with them
np.savez_compressed(
    os.path.join(OUT, 'truncation_sweep.npz'),
    alpha_t=np.array([k[0] for k in res]),
    eps=np.array([k[1] for k in res]),
    **{q: np.array([v[q] for v in res.values()])
       for q in ('depth', 'width', 'gain', 'transmission')})

fig, axes = plt.subplots(1, 3, figsize=(30.8, 7.0))
eps_arr = np.array(EPS)
COLORS = plt.cm.viridis(np.linspace(0.0, 0.85, len(ALPHAS)))

for ax, key, ylab, title in (
        (axes[0], 'gain', 'Depth-of-focus extension',
         '(a) Extension against obstruction ratio'),
        (axes[1], 'transmission', 'Fraction of incident power transmitted',
         '(b) Transmitted power against obstruction ratio'),
        (axes[2], 'width', 'Transverse full width at half maximum (nm)',
         '(c) Focal width against obstruction ratio')):
    for at, c in zip(ALPHAS, COLORS):
        lab = 'Uniform' if at == 0 else f'alpha {at:g}'
        ax.plot(eps_arr, [res[(at, e)][key] for e in EPS], 'o-',
                color=c, lw=2.0, ms=7, label=lab)
    if key == 'gain':
        ax.plot(eps_arr, 1.0 / (1.0 - eps_arr ** 2), 'k:', lw=2.0,
                label='Paraxial expression')
        ax.set_yscale('log')
    if key == 'transmission':
        ax.set_yscale('log')
    ax.set_xlabel('Obstruction ratio')
    ax.set_ylabel(ylab)
    ax.set_title(f'{title}, numerical aperture {XNA:g}, 750 nm', fontsize=12)
    ax.grid(alpha=0.25, which='both')
    ax.legend(fontsize=10)

plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUT, 'panels'), 'fig_truncation_sweep')
out = os.path.join(OUT, 'fig_truncation_sweep.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f"\nSaved -> {out}")
