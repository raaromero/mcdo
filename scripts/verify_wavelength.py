"""Does the scalar-to-vector threshold depend on wavelength?

Two statements that are easy to confuse, separated here:

  (a) In normalized (optical) coordinates the comparison is wavelength-free.
      The Richards-Wolf integrand depends on wavelength only through u and v,
      so the RMSE-against-scalar curves for different wavelengths must lie on
      top of one another and the threshold numerical apertures are identical.

  (b) The focus itself is not wavelength-free. Its physical width scales with
      wavelength, so the same numerical aperture gives a proportionally larger
      spot at a longer wavelength.

Wavelengths: 532, 633 and 750 nm, for uniform and truncated-Gaussian input.

Output: output/02_na_apodization/verify_wavelength.png (+ panels/)
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo.style import apply as _apply_style
_apply_style()

from mcdo import SimConfig
from mcdo.rw_integrals import compute_integrals
from mcdo.apodization import gaussian
from mcdo.components import full as vec_intensity
from mcdo.debye import scalar_debye
from mcdo.figio import save_panels

LAMS = [0.532, 0.633, 0.750]        # μm
N_MED, NT = 1.3, 601
XNA_VALS = np.linspace(0.1, 1.2, 23)
ALPHA_T = 4.0
V_MAX = 8.0
OUTDIR = os.path.join(os.path.dirname(__file__), '..', 'output', '02_na_apodization')
Z0 = np.array([0.0])
COLORS = {0.532: '#2E9BE0', 0.633: '#e8820c', 0.750: '#c0504d'}


def fwhm_v(v, I):
    I = I / I.max()
    below = np.where(I < 0.5)[0]
    if len(below) == 0:
        return np.nan
    i = below[0]
    return 2 * (v[i - 1] + (v[i] - v[i - 1]) * (I[i - 1] - 0.5) / (I[i - 1] - I[i]))


def measure(lam, xna, alpha_t):
    """RMSE against scalar, and the physical focal width in nanometres."""
    cfg = SimConfig(lam_c=lam, X_NA=xna, n=N_MED, tau=np.inf, N_freq=3, N_theta=NT)
    v = np.linspace(0.0, V_MAX, 321)
    r = v / (cfg.k_c * cfg.sin_alpha)
    apod = gaussian(alpha_t, cfg.sin2_alpha) if alpha_t > 0 else None
    I0, I1, I2 = compute_integrals(r, Z0, cfg.k_c, cfg.alpha, NT, apodization=apod)
    # independent scalar Debye theory (no vector obliquity factor)
    sca = scalar_debye(r, Z0, cfg.k_c, cfg.alpha, NT, apodization=apod)[0]
    vec = vec_intensity(I0[0], I1[0], I2[0])
    sca, vec = sca / sca.max(), vec / vec.max()
    rmse = float(np.sqrt(np.mean((vec - sca) ** 2)))
    width_nm = fwhm_v(v, vec) / (cfg.k_c * cfg.sin_alpha) * 1000.0
    return rmse, width_nm


def crossing(xs, ys, level):
    ys = np.asarray(ys)
    idx = np.where(ys > level)[0]
    if len(idx) == 0 or idx[0] == 0:
        return np.nan
    i = idx[0]
    return xs[i - 1] + (xs[i] - xs[i - 1]) * (level - ys[i - 1]) / (ys[i] - ys[i - 1])


data = {}
for alpha_t, name in [(0.0, 'uniform'), (ALPHA_T, f'Gaussian, truncation coefficient {ALPHA_T:g}')]:
    for lam in LAMS:
        rows = [measure(lam, x, alpha_t) for x in XNA_VALS]
        data[(name, lam)] = (np.array([r for r, _ in rows]), np.array([w for _, w in rows]))

print('Threshold numerical aperture (RMSE against scalar):')
print(f"{'illumination':>44} {'lambda':>8} {'>0.01':>7} {'>0.05':>7}")
for (name, lam), (rmse, _w) in data.items():
    print(f'{name:>44} {lam * 1000:>6.0f} nm {crossing(XNA_VALS, rmse, 0.01):>7.2f} '
          f'{crossing(XNA_VALS, rmse, 0.05):>7.2f}')

fig, axes = plt.subplots(1, 2, figsize=(20.5, 6.5))

ax = axes[0]
for (name, lam), (rmse, _w) in data.items():
    style = '-' if name == 'uniform' else '--'
    ax.plot(XNA_VALS, rmse, style, color=COLORS[lam], lw=2.0,
            label=f'{"uniform" if name == "uniform" else "Gaussian"}, {lam * 1000:.0f} nm')
for lvl in (0.01, 0.05):
    ax.axhline(lvl, color='#999', ls=':', lw=1.2)
ax.set_yscale('log')
ax.set_xlabel('Numerical aperture')
ax.set_ylabel('RMSE against scalar')
ax.set_title('(a) Error against scalar theory', fontsize=10)
ax.grid(alpha=0.25)
ax.legend(fontsize=8, loc='upper left', bbox_to_anchor=(1.02, 1.0), frameon=False)

ax = axes[1]
for (name, lam), (_r, width) in data.items():
    style = '-' if name == 'uniform' else '--'
    ax.plot(XNA_VALS, width, style, color=COLORS[lam], lw=2.0,
            label=f'{"uniform" if name == "uniform" else "Gaussian"}, {lam * 1000:.0f} nm')
ax.set_yscale('log')
ax.set_xlabel('Numerical aperture')
ax.set_ylabel('Focal-spot FWHM (nm)')
ax.set_title('(b) Focal-spot width against numerical aperture', fontsize=10)
# on a logarithmic axis proportional scaling appears as a constant offset,
# so the three wavelengths sit as parallel curves
ax.annotate('parallel curves: the spot scales\nin proportion to wavelength',
            xy=(0.9, 430), xytext=(0.52, 1500), fontsize=8, color='#555',
            arrowprops=dict(arrowstyle='->', lw=1.0, color='#555'))
ax.grid(alpha=0.25)
ax.legend(fontsize=8, loc='upper left', bbox_to_anchor=(1.02, 1.0), frameon=False)

plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUTDIR, 'panels'), 'verify_wavelength')
out = os.path.join(OUTDIR, 'verify_wavelength.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f'Saved → {out}')
