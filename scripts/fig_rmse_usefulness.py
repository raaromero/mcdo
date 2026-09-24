r"""Is the root-mean-square error useful next to the focal width?

The width criterion and the root-mean-square criterion are applied to the same
pair of profiles - vector Richards-Wolf against the scalar Debye integral with
the same pupil amplitude - at low and at high numerical aperture, under both
normalizations. Whichever criterion fires at the lower aperture is the more
sensitive one.

    python scripts/fig_rmse_usefulness.py
    -> output/02_na_apodization/rmse_usefulness.png
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
from mcdo.components import full as vec_intensity
from mcdo.debye import scalar_debye
from mcdo.figio import save_panels
from mcdo.rw_integrals import compute_integrals

LAM, N_MED, NT = 0.750, 1.3, 1001
NA_LOW, NA_HIGH = 0.10, 1.20
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '02_na_apodization')
v = np.linspace(0.0, 10.0, 401)


def _fwhm(x, y):
    y = y / y.max()
    i = np.where(y < 0.5)[0][0]
    return 2.0 * np.interp(0.5, [y[i], y[i - 1]], [x[i], x[i - 1]])


def _radius(xna):
    cfg = SimConfig(lam_c=LAM, X_NA=xna, n=N_MED, tau=np.inf, N_freq=3,
                    N_theta=NT)
    return v / (cfg.k_c * cfg.sin_alpha)


def _pair(xna):
    cfg = SimConfig(lam_c=LAM, X_NA=xna, n=N_MED, tau=np.inf, N_freq=3,
                    N_theta=NT)
    r = v / (cfg.k_c * cfg.sin_alpha)
    I0, I1, I2 = compute_integrals(r, np.array([0.0]), cfg.k_c, cfg.alpha, NT)
    return (vec_intensity(I0[0], I1[0], I2[0]),
            scalar_debye(r, np.array([0.0]), cfg.k_c, cfg.alpha, NT)[0])


def _by_peak(a, b):
    return a / a.max(), b / b.max()


def _by_energy(a, b, r=None):
    """Divide by the transmitted power, integral of I 2 pi r dr."""
    r = v if r is None else r
    tp = 2.0 * np.pi
    return a / (tp * np.trapezoid(a * r, r)), b / (tp * np.trapezoid(b * r, r))


def _rmse(a, b, weighted):
    if not weighted:
        return float(np.sqrt(np.mean((a - b) ** 2)))
    return float(np.sqrt(np.trapezoid((a - b) ** 2 * v, v) /
                         np.trapezoid(v, v)))


XNA = np.arange(0.10, 1.26, 0.05)
dev, rp, re, rpa, rea = [], [], [], [], []
for xna in XNA:
    vec, sca = _pair(xna)
    dev.append(100.0 * abs(_fwhm(v, vec) / _fwhm(v, sca) - 1.0))
    pv, ps = _by_peak(vec, sca)
    ev, es = _by_energy(vec, sca)
    sc = max(ev.max(), es.max())
    rp.append(_rmse(pv, ps, False))
    re.append(_rmse(ev / sc, es / sc, False))
    rpa.append(_rmse(pv, ps, True))
    rea.append(_rmse(ev / sc, es / sc, True))
dev, rp, re = np.array(dev), np.array(rp), np.array(re)
rpa, rea = np.array(rpa), np.array(rea)


def _cross(y, level):
    above = np.where(y > level)[0]
    if not len(above) or above[0] == 0:
        return np.nan
    i = above[0]
    return XNA[i - 1] + (XNA[i] - XNA[i - 1]) * (level - y[i - 1]) / (y[i] - y[i - 1])


NA_FIRE = [(_cross(dev, 1.0), 'Full width at half maximum'),
           (_cross(re, 0.01), 'Root-mean-square, energy normalized'),
           (_cross(rp, 0.01), 'Root-mean-square, peak normalized')]

fig, axes = plt.subplots(1, 4, figsize=(38.0, 7.0))

for ax, (xna, crit), tag in zip(axes, NA_FIRE, '(a)(b)(c)'.split(')')):
    vec, sca = _pair(xna)
    pv, ps = _by_peak(vec, sca)
    ev, es = _by_energy(vec, sca)
    sc = max(ev.max(), es.max())
    rr = _radius(xna)
    hi = rr[np.searchsorted(v, 8.0)]
    ax.plot(rr, pv, '-', color='#1f77b4', lw=2.4, label='Vector, peak normalized')
    ax.plot(rr, ps, '--', color='#c0504d', lw=2.4,
            label='Scalar Debye, peak normalized')
    ax.plot(rr, ev / sc, '-', color='#2ca02c', lw=2.4,
            label='Vector, energy normalized')
    ax.plot(rr, es / sc, '--', color='#9467bd', lw=2.4,
            label='Scalar Debye, energy normalized')
    ax.set_xlim(0, hi)
    ax.set_xlabel('Radial position r (µm)')
    ax.set_ylabel('Normalized intensity')
    ax.set_title(f'{tag}) Numerical aperture {xna:.2f} — where {crit.lower()} fires',
                 fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.25)

ax = axes[3]
series = [(dev / 100.0, 1.0 / 100.0, '#1f77b4', '-o',
           'Full width at half maximum'),
          (re, 0.01, '#2ca02c', '--^', 'Root-mean-square, energy normalized'),
          (rp, 0.01, '#c0504d', '--s', 'Root-mean-square, peak normalized')]
for y, lvl, col, sty, lab in series:
    ax.plot(XNA, y, sty, color=col, lw=2.2, ms=5, label=lab)
    xc = _cross(y, lvl)
    if np.isfinite(xc):
        ax.plot([xc], [lvl], '*', color=col, ms=22, mec='k', mew=0.8, zorder=5)
ax.axhline(0.01, color='#555555', lw=1.6, ls='-')
ax.set_yscale('log')
ax.set_xlabel('NA')
ax.set_ylabel('Relative deviation from scalar theory')
ax.set_title('Relative deviation from scalar theory against numerical '
             'aperture\nStars mark where each criterion crosses 0.01 — '
             'uniform illumination, 750 nm', fontsize=12)
ax.yaxis.set_major_formatter(matplotlib.ticker.LogFormatterMathtext())
ax.legend(fontsize=9, loc='lower right')
ax.grid(alpha=0.25, which='both')

plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUT, 'panels'), 'rmse_usefulness')
out = os.path.join(OUT, 'rmse_usefulness.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f'Saved -> {out}')

print(f"\n{'NA':>5} {'FWHM dev %':>11} {'RMSE peak':>11} {'RMSE energy':>12}")
for i in range(0, len(XNA), 3):
    print(f'{XNA[i]:>5.2f} {dev[i]:>11.3f} {rp[i]:>11.5f} {re[i]:>12.5f}')

# ── figure 1: what the normalization does, at one aperture ───────────────
fig1, ax1 = plt.subplots(1, 2, figsize=(19.0, 7.0))
vec, sca = _pair(NA_HIGH)
pv, ps = _by_peak(vec, sca)
rr = _radius(NA_HIGH)
ev, es = _by_energy(vec, sca, rr)
# dimensionless: both divided by the scalar peak, so the vector-to-scalar
# peak ratio the normalization preserves is what the axis shows
ev, es = ev / es.max(), es / es.max()
hi = rr[np.searchsorted(v, 8.0)]
for ax, (a_, b_, tag, ylab) in zip(ax1, (
        (pv, ps, 'Peak normalized:  $I\\,/\\,I_{max}$',
         'Intensity, divided by its own peak'),
        (ev, es, r'Energy normalized:  $I\,/\,\int_0^\infty I(r)\,r\,dr$',
         'Intensity, relative to the scalar peak'))):
    ax.plot(rr, a_, '-', color='#1f77b4', lw=3.0, label='Vector')
    ax.plot(rr, b_, '--', color='#c0504d', lw=3.0, dashes=(5, 4),
            label='Scalar Debye')
    ax.set_xlim(0, hi)
    ax.set_ylim(bottom=0)
    ax.set_xlabel('Radial position r (µm)')
    ax.set_ylabel(ylab)
    ax.set_title(tag, fontsize=13)
    ax.legend(fontsize=11)
    ax.grid(alpha=0.25)
fig1.suptitle(f'What the normalization changes - NA {NA_HIGH:g}, uniform '
              f'illumination, 750 nm', fontsize=14)
plt.tight_layout()
out1 = os.path.join(OUT, 'normalization_difference.png')
fig1.savefig(out1, dpi=300, bbox_inches='tight')
plt.close(fig1)
print(f'Saved -> {out1}')

# ── figure 2: vector against scalar, one column per firing aperture ──────
COLS = [_cross(dev, 1.0), _cross(re, 0.01), _cross(rp, 0.01), 0.90, NA_HIGH]

fig2, ax2 = plt.subplots(2, len(COLS), figsize=(5.4 * len(COLS), 9.6),
                         sharey='row')
for col, xna in enumerate(COLS):
    vec, sca = _pair(xna)
    pv, ps = _by_peak(vec, sca)
    ev, es = _by_energy(vec, sca)
    sc = max(ev.max(), es.max())
    rr = _radius(xna)
    hi = rr[np.searchsorted(v, 8.0)]
    d_fw = 100.0 * abs(_fwhm(v, vec) / _fwhm(v, sca) - 1.0)
    r_pk = _rmse(pv, ps, False)
    r_en = _rmse(ev / sc, es / sc, False)
    for row, (a_, b_) in enumerate(((pv, ps), (ev / sc, es / sc))):
        ax = ax2[row, col]
        ax.plot(rr, a_, '-', color='#1f77b4', lw=3.0, label='Vector')
        ax.plot(rr, b_, '--', color='#c0504d', lw=3.0, dashes=(5, 4),
                label='Scalar Debye')
        ax.set_xlim(0, hi)
        ax.set_ylim(0, 1.05)
        ax.grid(alpha=0.25)
        if row == 1:
            ax.set_xlabel('Radial position r (µm)')
        if col == 0:
            ax.set_ylabel(('Peak normalized\n$I\\,/\\,I_{max}$'
                           if row == 0 else
                           'Energy normalized\n'
                           r'$I\,/\,\int_0^\infty I(r)\,r\,dr$')
                          + '\n\nNormalized intensity', fontsize=12)
        if row == 0:
            ax.set_title(f'NA {xna:.2f}: FWHM difference {d_fw:.2f}%, '
                         f'RMSE {r_pk:.4f}',
                         fontsize=12)
        else:
            ax.set_title(f'FWHM difference {d_fw:.2f}%, RMSE {r_en:.4f}',
                         fontsize=12)
        if row == 0 and col == 0:
            ax.legend(fontsize=10)
fig2.suptitle('Vector against scalar under each normalization - uniform '
              'illumination, 750 nm', fontsize=14, y=0.98)
plt.tight_layout()
out2 = os.path.join(OUT, 'normalization_pair.png')
fig2.savefig(out2, dpi=300, bbox_inches='tight')
plt.close(fig2)
print(f'Saved -> {out2}')

print('\nNumerical aperture at which each criterion first fires:')
print(f'  Full width at half maximum, 1%             {_cross(dev, 1.0):.2f}')
print(f'  Root-mean-square, peak normalized          {_cross(rp, 0.01):.2f}')
print(f'  Root-mean-square, energy normalized        {_cross(re, 0.01):.2f}')

