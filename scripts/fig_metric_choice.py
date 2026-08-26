"""Why the focal width is the metric, and the other two are not.

Three ways of comparing the vector focus against the scalar prediction, for
uniform illumination, as the numerical aperture is raised:

    focal-width difference   the spot-size prediction error
    root-mean-square error   the point-by-point difference
    Pearson correlation      the shape similarity

All three are computed from the same pair of profiles, so the comparison is
like for like. The width difference registers the departure long before the
other two move at all: correlation in particular stays above 0.99 well past the
point where the predicted spot size is already wrong by tens of per cent, which
is exactly the failure mode that matters in an imaging application.

Output: output/02_na_apodization/fig_metric_choice.png (+ panels/)
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
from mcdo.debye import scalar_debye
from mcdo.components import full as vec_intensity
from mcdo.figio import save_panels

LAM, N_MED, NT = 0.750, 1.3, 601
XNA_VALS = np.arange(0.05, 1.26, 0.05)
V_MAX = 8.0
OUTDIR = os.path.join(os.path.dirname(__file__), '..', 'output', '02_na_apodization')
Z0 = np.array([0.0])


def fwhm_v(v, I):
    I = I / I.max()
    below = np.where(I < 0.5)[0]
    if len(below) == 0:
        return np.nan
    i = below[0]
    return 2 * (v[i - 1] + (v[i] - v[i - 1]) * (I[i - 1] - 0.5) / (I[i - 1] - I[i]))


dev, rmse, one_minus_corr = [], [], []
for xna in XNA_VALS:
    cfg = SimConfig(lam_c=LAM, X_NA=xna, n=N_MED, tau=np.inf, N_freq=3, N_theta=NT)
    v = np.linspace(0.0, V_MAX, 321)
    r = v / (cfg.k_c * cfg.sin_alpha)
    I0, I1, I2 = compute_integrals(r, Z0, cfg.k_c, cfg.alpha, NT)
    vec = vec_intensity(I0[0], I1[0], I2[0])
    sca = scalar_debye(r, Z0, cfg.k_c, cfg.alpha, NT)[0]
    vec, sca = vec / vec.max(), sca / sca.max()
    dev.append(100 * abs(fwhm_v(v, vec) / fwhm_v(v, sca) - 1))
    rmse.append(float(np.sqrt(np.mean((vec - sca) ** 2))))
    one_minus_corr.append(1.0 - float(np.corrcoef(vec, sca)[0, 1]))

dev, rmse, one_minus_corr = np.array(dev), np.array(rmse), np.array(one_minus_corr)


def crossing(y, level):
    idx = np.where(y > level)[0]
    if len(idx) == 0 or idx[0] == 0:
        return np.nan
    i = idx[0]
    return XNA_VALS[i - 1] + 0.05 * (level - y[i - 1]) / (y[i] - y[i - 1])


na_dev = crossing(dev, 1.0)
na_rmse = crossing(rmse, 0.01)
na_corr = crossing(one_minus_corr, 0.01)

fig, ax = plt.subplots(figsize=(10.3, 6.5))
ax.plot(XNA_VALS, dev / 100, '-o', color='#1f77b4', ms=4, lw=2.0,
        label='focal-width difference')
ax.plot(XNA_VALS, rmse, '--s', color='#e8820c', ms=4, lw=2.0,
        label='root-mean-square error')
ax.plot(XNA_VALS, one_minus_corr, ':^', color='#c0504d', ms=4, lw=2.0,
        label='one minus Pearson correlation')
ax.axhline(0.01, color='#999', ls=':', lw=1.2)
ax.text(0.06, 0.012, 'one per cent level', fontsize=9, color='#666')
for x, c in [(na_dev, '#1f77b4'), (na_rmse, '#e8820c'), (na_corr, '#c0504d')]:
    if np.isfinite(x):
        ax.axvline(x, color=c, lw=1.2, alpha=0.5)
ax.set_yscale('log'); ax.set_ylim(1e-6, 1.0)
ax.set_xlabel('Numerical aperture')
ax.set_ylabel('Departure from the scalar prediction')
ax.set_title('Departure from scalar theory by metric, uniform input at 750 nm', fontsize=12)
ax.grid(alpha=0.25, which='both')
ax.legend(fontsize=10, loc='lower right')

print('Numerical aperture at which each metric first exceeds one per cent:')
print(f'  focal-width difference        {na_dev:.2f}')
print(f'  root-mean-square error        {na_rmse:.2f}')
print(f'  one minus Pearson correlation {na_corr:.2f}')
i08 = int(np.argmin(np.abs(XNA_VALS - 0.8)))
print(f'\nAt numerical aperture 0.8: width off by {dev[i08]:.1f} per cent, '
      f'while correlation is still {1 - one_minus_corr[i08]:.4f}')

plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUTDIR, 'panels'), 'fig_metric_choice')
out = os.path.join(OUTDIR, 'fig_metric_choice.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f'Saved → {out}')
