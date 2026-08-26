"""When does scalar theory fail for an ANNULAR pupil?

The uniform-disk answer is known (see verify_apod_thresholds). Here the same
question is asked with a central obstruction, for uniform and truncated-Gaussian
illumination, because the ring weights the steep marginal rays that generate the
longitudinal field — so the scalar approximation is expected to fail earlier.

Scalar and vector come from the same annular integrals, so the comparison is
exact rather than two different models:
    scalar        independent scalar Debye theory (no vector obliquity factor)
    vector total  |I0|^2 + |I2|^2 + 2|I1|^2     (all three components)

Metric: RMSE between peak-normalized transverse profiles, and the focal-width
difference, both against the scalar profile. Reported crossing points are the
numerical apertures where RMSE first exceeds 0.01 and 0.05.

Output: output/03_annular/verify_annular_scalar.png (+ panels/)
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
from mcdo.annular import compute_integrals_annular
from mcdo.apodization import gaussian
from mcdo.components import full as vec_intensity
from mcdo.debye import scalar_debye_field
from mcdo.figio import save_panels

LAM, N_MED, NT = 0.750, 1.3, 601
XNA_VALS = np.linspace(0.1, 1.2, 23)
EPS_VALS = [0.0, 0.5, 0.9]
ALPHA_T = 4.0
V_MAX = 8.0                      # window in optical units, so every NA is fair
OUTDIR = os.path.join(os.path.dirname(__file__), '..', 'output', '03_annular')
Z0 = np.array([0.0])


def fwhm_v(v, I):
    I = I / I.max()
    below = np.where(I < 0.5)[0]
    if len(below) == 0:
        return np.nan
    i = below[0]
    return 2 * (v[i - 1] + (v[i] - v[i - 1]) * (I[i - 1] - 0.5) / (I[i - 1] - I[i]))


def profiles(xna, eps, alpha_t):
    """Peak-normalized scalar and vector x-cut transverse profiles."""
    cfg = SimConfig(lam_c=LAM, X_NA=xna, n=N_MED, tau=np.inf, N_freq=3, N_theta=NT)
    v = np.linspace(0.0, V_MAX, 321)
    r = v / (cfg.k_c * cfg.sin_alpha)
    apod = gaussian(alpha_t, cfg.sin2_alpha) if alpha_t > 0 else None
    I0, I1, I2 = compute_integrals_annular(r, Z0, cfg.k_c, cfg.alpha, eps, NT, apodization=apod)
    # independent scalar theory for the same ring, by Babinet on the field
    U = scalar_debye_field(r, Z0, cfg.k_c, cfg.alpha, NT, apodization=apod)[0]
    if eps > 0:
        a_in = np.arcsin(eps * np.sin(cfg.alpha))
        U = U - scalar_debye_field(r, Z0, cfg.k_c, a_in, max(51, int(NT * a_in / cfg.alpha) | 1),
                                   apodization=apod)[0]
    sca = np.abs(U) ** 2
    vec = vec_intensity(I0[0], I1[0], I2[0])
    return v, sca / sca.max(), vec / vec.max()


def crossing(xs, ys, level):
    """First x where y exceeds level (linear interpolation), or nan."""
    ys = np.asarray(ys)
    idx = np.where(ys > level)[0]
    if len(idx) == 0 or idx[0] == 0:
        return np.nan
    i = idx[0]
    x0, x1, y0, y1 = xs[i - 1], xs[i], ys[i - 1], ys[i]
    return x0 + (x1 - x0) * (level - y0) / (y1 - y0)


results = {}
for label, alpha_t in [('uniform', 0.0), (f'Gaussian, truncation coefficient {ALPHA_T:g}', ALPHA_T)]:
    for eps in EPS_VALS:
        rmse, dfw = [], []
        for xna in XNA_VALS:
            v, sca, vec = profiles(xna, eps, alpha_t)
            rmse.append(float(np.sqrt(np.mean((vec - sca) ** 2))))
            f_s, f_v = fwhm_v(v, sca), fwhm_v(v, vec)
            dfw.append(100.0 * (f_v - f_s) / f_s)
        results[(label, eps)] = (np.array(rmse), np.array(dfw))

print('Numerical aperture at which the vector result departs from scalar:')
print(f"{'illumination':>44} {'eps':>5} {'RMSE>0.01':>10} {'RMSE>0.05':>10}")
for (label, eps), (rmse, _dfw) in results.items():
    print(f'{label:>44} {eps:>5g} {crossing(XNA_VALS, rmse, 0.01):>10.2f} '
          f'{crossing(XNA_VALS, rmse, 0.05):>10.2f}')

fig, axes = plt.subplots(1, 2, figsize=(20.5, 6.5))
colors = {0.0: '#1f77b4', 0.5: '#e8820c', 0.9: '#c0504d'}

ax = axes[0]
for (label, eps), (rmse, _d) in results.items():
    style = '-' if label == 'uniform' else '--'
    ax.plot(XNA_VALS, rmse, style, color=colors[eps], lw=2.0,
            label=f'{"uniform" if label == "uniform" else "Gaussian"}, ε={eps:g}')
for lvl in (0.01, 0.05):
    ax.axhline(lvl, color='#999', ls=':', lw=1.2)
ax.set_yscale('log')
ax.set_xlabel('Numerical aperture')
ax.set_ylabel('RMSE against scalar')
ax.set_title('(a) Error against scalar theory, 750 nm', fontsize=10)
# the two thinnest-ring curves lie on top of one another; that coincidence is
# the result, so say so rather than leaving a curve apparently missing
ax.annotate('the two ε=0.9 curves coincide:\nonly marginal rays remain,\nso the input no longer matters',
            xy=(1.05, 0.085), xytext=(0.42, 0.16), fontsize=8, color='#7a3b38',
            arrowprops=dict(arrowstyle='->', lw=1.0, color='#7a3b38'))
ax.grid(alpha=0.25)
ax.legend(fontsize=8, loc='upper left', bbox_to_anchor=(1.02, 1.0), frameon=False)

ax = axes[1]
for (label, eps), (_r, dfw) in results.items():
    style = '-' if label == 'uniform' else '--'
    ax.plot(XNA_VALS, dfw, style, color=colors[eps], lw=2.0,
            label=f'{"uniform" if label == "uniform" else "Gaussian"}, ε={eps:g}')
ax.axhline(0, color='#999', ls=':', lw=1.2)
ax.set_xlabel('Numerical aperture')
ax.set_ylabel('Focal-width difference from scalar (%)')
ax.set_title('(b) Focal-width difference from scalar, 750 nm', fontsize=10)
ax.grid(alpha=0.25)
ax.legend(fontsize=8, loc='upper left', bbox_to_anchor=(1.02, 1.0), frameon=False)

plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUTDIR, 'panels'), 'verify_annular_scalar')
out = os.path.join(OUTDIR, 'verify_annular_scalar.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f'Saved → {out}')
