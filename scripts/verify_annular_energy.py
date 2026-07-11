"""
Phase 3 closer — the COST side of the annular trade-off.

For ε 0→1 the central lobe narrows and the DOF extends, but:
  (i)  encircled energy within the first zero collapses (sidelobes take it),
  (ii) the on-axis peak intensity drops (paraxial Strehl ∝ (1−ε²)² at fixed
       pupil fluence).

Outputs output/03_annular/annular_energy_cost.png + printed table.
Linear-x y-cut, X_NA=1.17 (sinα=0.9) and X_NA=0.13 for the paraxial check.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.integrate import trapezoid

from mcdo import SimConfig
from mcdo.annular import compute_integrals_annular

LAM, N_MED, NT = 0.750, 1.3, 1001
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '03_annular')
os.makedirs(OUT, exist_ok=True)

v_arr = np.linspace(0.0, 20.0, 801)
ydir = lambda I0, I1, I2: np.abs(I0 - I2) ** 2


def profile_raw(cfg, eps):
    """UN-normalized transverse intensity (for Strehl) + normalized copy."""
    r = v_arr / (cfg.k_c * cfg.sin_alpha)
    I = ydir(*[a[0] for a in compute_integrals_annular(
        r, np.array([0.0]), cfg.k_c, cfg.alpha, eps, NT)])
    return I


def encircled_first_zero(I):
    """2-D encircled energy within the first minimum of the central lobe."""
    interior = np.where((I[1:-1] < I[:-2]) & (I[1:-1] <= I[2:]))[0] + 1
    i0 = int(interior[0])
    E_in = trapezoid(I[:i0] * v_arr[:i0], v_arr[:i0])
    E_tot = trapezoid(I * v_arr, v_arr)
    return E_in / E_tot, v_arr[i0]


EPS = np.array([0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 0.95, 0.99])

print("Annular cost metrics (X_NA=1.17 unless noted):")
print(f"{'eps':>5} {'Strehl':>8} {'(1-e^2)^2':>10} {'E_circ(1st zero)':>17} "
      f"{'v_zero':>7}")
res = {'strehl': [], 'ecirc': [], 'strehl_lo': []}
cfg_hi, cfg_lo = (SimConfig(lam_c=LAM, X_NA=x, n=N_MED, tau=np.inf,
                            N_freq=3, N_theta=NT) for x in (1.17, 0.13))
I0_hi = profile_raw(cfg_hi, 0.0)
I0_lo = profile_raw(cfg_lo, 0.0)
for e in EPS:
    I_hi = profile_raw(cfg_hi, e)
    I_lo = profile_raw(cfg_lo, e)
    strehl = I_hi[0] / I0_hi[0]
    res['strehl'].append(strehl)
    res['strehl_lo'].append(I_lo[0] / I0_lo[0])
    ec, vz = encircled_first_zero(I_hi / I_hi.max())
    res['ecirc'].append(ec)
    print(f"{e:>5.2f} {strehl:>8.4f} {(1-e**2)**2:>10.4f} {ec:>17.3f} {vz:>7.2f}")

fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
fig.suptitle('Phase 3 — the price of annular DOF extension (linear-x y-cut)',
             fontsize=11)

ax = axes[0]
e_th = np.linspace(0, 0.99, 200)
ax.plot(e_th, (1 - e_th ** 2) ** 2, 'k--', lw=1.3, label='paraxial (1−ε²)²')
ax.plot(EPS, res['strehl_lo'], 'C0o-', ms=4, lw=1.1, label='X_NA=0.13')
ax.plot(EPS, res['strehl'], 'C3s-', ms=4, lw=1.1, label='X_NA=1.17')
ax.set_yscale('log')
ax.set_xlabel('ε'); ax.set_ylabel('on-axis peak / full-disk peak')
ax.set_title('(a) Strehl cost of the annulus', fontsize=10)
ax.legend(fontsize=8)

ax = axes[1]
ax.plot(EPS, res['ecirc'], 'C3s-', ms=4, lw=1.1)
ax.axhline(res['ecirc'][0], color='gray', lw=0.7, ls=':')
ax.annotate(f"full disk {res['ecirc'][0]:.3f} (y-cut)", (0.05, res['ecirc'][0]+0.01), fontsize=8, color='gray')
ax.set_xlabel('ε'); ax.set_ylabel('encircled energy within first zero')
ax.set_title('(b) central-lobe energy collapses as ε→1', fontsize=10)

plt.tight_layout()
out = os.path.join(OUT, 'annular_energy_cost.png')
fig.savefig(out, dpi=150, bbox_inches='tight')
plt.close(fig)
print(f"Saved → {out}")
