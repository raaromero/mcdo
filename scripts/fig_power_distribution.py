"""Distribution of optical power as the obstruction ratio increases.

The peak intensity of an annular focus falls much faster than the pupil
transmission alone would suggest. Two separate effects are stacked and they are
worth separating, because only one of them is a loss:

  at the pupil     the obstruction blocks light, and that light never arrives
  in the focal plane   what does arrive is redistributed, spreading along the
                       axis and outward into the side lobes

This traces both. For each obstruction ratio it reports the fraction of the
incident power transmitted, the fraction of the transmitted power that lands in
the central lobe, and the resulting on-axis peak, so the drop in peak can be
attributed to blocking against redistribution rather than quoted as one number.

Energy in the focal plane is the intensity weighted by the area element 2 pi r,
so a ring at large radius carries far more than its height on a profile plot
suggests.
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

LAM, N_MED, NT = 0.750, 1.3, 1001
XNA = 0.8
EPS = [0.0, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99]
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '03_annular')

cfg = SimConfig(lam_c=LAM, X_NA=XNA, n=N_MED, tau=np.inf, N_freq=3, N_theta=NT)
r = np.linspace(0.0, 6.0 * LAM / XNA, 1400)
z0 = np.array([0.0])


def _transmission(eps, apod):
    """Fraction of the incident power that gets past the pupil."""
    th = np.linspace(0.0, cfg.alpha, 4001)
    A = np.ones_like(th) if apod is None else np.abs(np.asarray(apod(th)))
    w = A ** 2 * np.sin(th) * np.cos(th)
    th_in = np.arcsin(eps * np.sin(cfg.alpha))
    return float(np.trapezoid(w[th >= th_in], th[th >= th_in]) / np.trapezoid(w, th))


def _profile(eps, apod):
    if eps == 0.0:
        I0, I1, I2 = compute_integrals(r, z0, cfg.k_c, cfg.alpha, NT, apodization=apod)
    else:
        I0, I1, I2 = compute_integrals_annular(r, z0, cfg.k_c, cfg.alpha, eps, NT,
                                               apodization=apod)
    return vec_intensity(I0[0], I1[0], I2[0])


def _first_minimum(I):
    """Index of the first minimum: the edge of the central lobe."""
    d = np.diff(I)
    rising = np.where(d > 0)[0]
    return rising[0] if len(rising) else len(I) - 1


rows = []
for label, at in (('uniform', None),
                  ('Gaussian, alpha = 4', 4.0)):
    apod = None if at is None else gaussian(at, cfg.sin2_alpha)
    ref_peak = None
    for eps in EPS:
        I = _profile(eps, apod)
        if ref_peak is None:
            ref_peak = I[0]
        edge = _first_minimum(I)
        energy = I * 2.0 * np.pi * r              # area element of the focal plane
        total = np.trapezoid(energy, r)
        core = np.trapezoid(energy[:edge + 1], r[:edge + 1])
        rows.append(dict(input=label, eps=eps,
                         transmission=_transmission(eps, apod),
                         core_fraction=core / total,
                         peak=I[0] / ref_peak,
                         lobe_edge_um=r[edge]))

print(f"{'input':<38} {'eps':>5} {'transmitted':>12} {'in core':>9} "
      f"{'peak':>7} {'predicted':>10}")
for row in rows:
    pred = row['transmission'] * row['core_fraction']
    print(f"{row['input']:<38} {row['eps']:>5.2f} {row['transmission']:>12.4f} "
          f"{row['core_fraction']:>9.3f} {row['peak']:>7.4f} {pred:>10.4f}")

# ── figure: transmission, retained fraction, then the profiles ───────────
fig, axes = plt.subplots(1, 3, figsize=(30.8, 7.0))
eps_arr = np.array(EPS)
STYLE = {'uniform': ('#1f77b4', 'o-'),
         'Gaussian, alpha = 4': ('#d62728', 's--')}

ax = axes[0]
for label, _ in (('uniform', None), ('Gaussian, alpha = 4', 4.0)):
    c, st = STYLE[label]
    y = [x['transmission'] for x in rows if x['input'] == label]
    short = 'uniform' if label == 'uniform' else 'Gaussian, alpha = 4'
    ax.plot(eps_arr, y, st, color=c, lw=2.0, ms=7, label=short)
ax.plot(eps_arr, 1.0 - eps_arr ** 2, 'k:', lw=2.0, label='One minus eps squared')
ax.set_yscale('log')
ax.set_xlabel('Obstruction ratio')
ax.set_ylabel('Fraction of incident power transmitted')
ax.set_title('(a) Blocked at the pupil', fontsize=12)
ax.legend(fontsize=10)
ax.grid(alpha=0.25, which='both')

ax = axes[1]
for label, _ in (('uniform', None), ('Gaussian, alpha = 4', 4.0)):
    c, st = STYLE[label]
    y = [x['core_fraction'] for x in rows if x['input'] == label]
    short = 'uniform' if label == 'uniform' else 'Gaussian, alpha = 4'
    ax.plot(eps_arr, y, st, color=c, lw=2.0, ms=7, label=short)
ax.set_xlabel('Obstruction ratio')
ax.set_ylabel('Fraction of transmitted power in the central lobe')
ax.set_ylim(0, 1)
ax.set_title('(b) Redistributed in the focal plane', fontsize=12)
ax.legend(fontsize=10)
ax.grid(alpha=0.25)

ax = axes[2]
COL = {0.0: '#999999', 0.5: '#1f77b4', 0.9: '#d62728', 0.99: '#2ca02c'}
for eps in (0.0, 0.5, 0.9, 0.99):
    I = _profile(eps, None)
    energy = I * 2.0 * np.pi * r
    ax.plot(r * 1000.0, energy / energy.max(), '-', color=COL[eps],
            lw=2.6 if eps == 0 else 2.0,
            label='No obstruction' if eps == 0 else f'ratio {eps:g}')
ax.set_xlim(0, 2500)
ax.set_xlabel('Radial position r (nm)')
ax.set_ylabel('Energy per unit radius, normalized')
ax.set_title('(c) Where the transmitted power lands, uniform input', fontsize=12)
ax.legend(fontsize=10)
ax.grid(alpha=0.25)

plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUT, 'panels'), 'fig_power_distribution')
out = os.path.join(OUT, 'fig_power_distribution.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f"\nSaved → {out}")
