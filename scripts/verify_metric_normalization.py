"""Which normalization to use when comparing two focal profiles.

Root-mean-square error and correlation were reported as poor discriminators
next to the change in full width at half maximum. That conclusion depends on a
choice that was never examined: both profiles were divided by their own peak
before differencing.

Peak normalization forces the two curves to agree exactly at r = 0, which is
where they are largest. What is left for the metric to see is the wings, where
the intensity is small, so the difference is weighted towards the part of the
profile that carries least energy. The result is a metric that reports small
numbers for profiles whose widths differ substantially.

Energy normalization instead matches the transmitted power, leaving the peaks
free to differ. A vector focus that is broader than its scalar prediction then
also has a lower peak, and both differences enter the metric.

This compares the two on the same profiles: vector Richards-Wolf against the
scalar Debye integral with the same pupil amplitude, over numerical aperture.
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
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '02_na_apodization')
v = np.linspace(0.0, 10.0, 401)


def _fwhm(x, y):
    y = y / y.max()
    i = np.where(y < 0.5)[0][0]
    return 2.0 * np.interp(0.5, [y[i], y[i - 1]], [x[i], x[i - 1]])


def _pair(xna):
    """Vector and scalar transverse profiles at one numerical aperture."""
    cfg = SimConfig(lam_c=LAM, X_NA=xna, n=N_MED, tau=np.inf, N_freq=3, N_theta=NT)
    r = v / (cfg.k_c * cfg.sin_alpha)
    I0, I1, I2 = compute_integrals(r, np.array([0.0]), cfg.k_c, cfg.alpha, NT)
    return vec_intensity(I0[0], I1[0], I2[0]), \
        scalar_debye(r, np.array([0.0]), cfg.k_c, cfg.alpha, NT)[0]


def _by_peak(a, b):
    return a / a.max(), b / b.max()


def _by_energy(a, b):
    """Match transmitted power. The radial weight is the 2-D area element."""
    wa = np.trapezoid(a * v, v)
    wb = np.trapezoid(b * v, v)
    return a / wa, b / wb


def _rmse(a, b, weighted):
    """Root-mean-square difference, optionally weighted by the area element.

    These are profiles on a plane: the difference at radius r occupies an
    annulus of area proportional to r. An unweighted average over radial
    samples counts a point at r = 0 as heavily as one far out, which
    over-represents the near-axis region.
    """
    if not weighted:
        return float(np.sqrt(np.mean((a - b) ** 2)))
    return float(np.sqrt(np.trapezoid((a - b) ** 2 * v, v) / np.trapezoid(v, v)))


XNA = np.arange(0.1, 1.26, 0.05)
rows = []
for xna in XNA:
    vec, sca = _pair(xna)
    dev = 100.0 * abs(_fwhm(v, vec) / _fwhm(v, sca) - 1.0)
    pv, ps = _by_peak(vec, sca)
    ev, es = _by_energy(vec, sca)
    scale = max(ev.max(), es.max())
    rows.append(dict(
        xna=xna, dev=dev,
        rmse_peak=_rmse(pv, ps, False),
        rmse_energy=_rmse(ev / scale, es / scale, False),
        rmse_peak_area=_rmse(pv, ps, True),
        rmse_energy_area=_rmse(ev / scale, es / scale, True),
        peak_ratio=float(ev.max() / es.max())))

dev = np.array([r['dev'] for r in rows])
rp = np.array([r['rmse_peak'] for r in rows])
re = np.array([r['rmse_energy'] for r in rows])
rpa = np.array([r['rmse_peak_area'] for r in rows])
rea = np.array([r['rmse_energy_area'] for r in rows])


def _crossing(y, level):
    above = np.where(y > level)[0]
    return XNA[above[0]] if len(above) else np.nan


print(f"{'X_NA':>5} {'FWHM dev %':>11} {'RMSE peak':>11} {'RMSE energy':>12} "
      f"{'peak ratio':>11}")
for r in rows[::3]:
    print(f"{r['xna']:>5.2f} {r['dev']:>11.2f} {r['rmse_peak']:>11.5f} "
          f"{r['rmse_energy']:>12.5f} {r['peak_ratio']:>11.4f}")

print("\nNumerical aperture at which each metric first exceeds 0.01:")
print(f"  peak normalization, unweighted      {_crossing(rp, 0.01):.2f}")
print(f"  energy normalization, unweighted    {_crossing(re, 0.01):.2f}")
print(f"  peak normalization, area weighted   {_crossing(rpa, 0.01):.2f}")
print(f"  energy normalization, area weighted {_crossing(rea, 0.01):.2f}")
print(f"  full width at half maximum, 1%   {_crossing(dev, 1.0):.2f}")

# ── figure ─────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(30.8, 7.0))

# Both normalizations of the same pair belong on one axes: the point is that
# they differ, and that is invisible when they sit in separate panels.
vec, sca = _pair(1.2)
pv, ps = _by_peak(vec, sca)
ev, es = _by_energy(vec, sca)
scale = max(ev.max(), es.max())

ax = axes[0]
ax.plot(v, pv, '-', color='#1f77b4', lw=2.4, label='Vector, peak normalized')
ax.plot(v, ps, '--', color='#c0504d', lw=2.4, label='Scalar Debye, peak normalized')
ax.plot(v, ev / scale, '-', color='#2ca02c', lw=2.4, label='Vector, energy normalized')
ax.plot(v, es / scale, '--', color='#9467bd', lw=2.4,
        label='Scalar Debye, energy normalized')
ax.set_xlim(0, 8)
ax.set_xlabel('Optical radial coordinate v')
ax.set_ylabel('Normalized intensity')
ax.set_title('(a) Both normalizations, numerical aperture 1.2', fontsize=12)
ax.legend(fontsize=10)
ax.grid(alpha=0.25)

ax = axes[1]
ax.plot(v, pv - ps, '-', color='#1f77b4', lw=2.4, label='Peak normalized')
ax.plot(v, (ev - es) / scale, '-', color='#2ca02c', lw=2.4, label='Energy normalized')
ax.axhline(0.0, color='#888', lw=1.2)
ax.set_xlim(0, 8)
ax.set_xlabel('Optical radial coordinate v')
ax.set_ylabel('Vector minus scalar')
ax.set_title('(b) The difference each normalization measures', fontsize=12)
ax.legend(fontsize=10)
ax.grid(alpha=0.25)

ax = axes[2]
ax.plot(XNA, rp, 'o-', color='#e8820c', lw=2.0, ms=6, label='Root-mean-square error, peak normalized')
ax.plot(XNA, re, 's--', color='#1f77b4', lw=2.0, ms=6, label='Root-mean-square error, energy normalized')
ax.plot(XNA, rpa, 'o-', color='#8c564b', lw=2.0, ms=6,
        label='Peak normalized, area weighted')
ax.plot(XNA, rea, 's--', color='#17becf', lw=2.0, ms=6,
        label='Energy normalized, area weighted')
ax.plot(XNA, dev / 100.0, '^:', color='#2ca02c', lw=2.0, ms=6,
        label='Fractional change in width')
ax.axhline(0.01, color='gray', ls=':', lw=1.2)
# the claim on this panel is that two of the three cross at the same place,
# so mark where each one crosses rather than leaving it to be inferred
for y, col, name in ((rp, '#e8820c', 'peak'),
                     (re, '#1f77b4', 'energy'),
                     (rpa, '#8c564b', 'peak area'),
                     (rea, '#17becf', 'energy area'),
                     (dev / 100.0, '#2ca02c', 'width')):
    xc = _crossing(y, 0.01)
    if np.isfinite(xc):
        ax.axvline(xc, color=col, ls='--', lw=1.6, alpha=0.7)
        ax.annotate(f'{xc:.2f}', xy=(xc, 2e-4), color=col, fontsize=11,
                    ha='center', va='bottom', rotation=90)
ax.set_yscale('log')
ax.set_ylim(1e-4, 1)
ax.set_xlabel('Numerical aperture')
ax.set_ylabel('Metric value')
ax.set_title('(c) Numerical aperture at which each criterion is first met', fontsize=12)
ax.legend(fontsize=10, loc='lower right')
ax.grid(alpha=0.25, which='both')

plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUT, 'panels'), 'verify_metric_normalization')
out = os.path.join(OUT, 'verify_metric_normalization.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f"\nSaved → {out}")
