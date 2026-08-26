"""
Fig. 3 — Fraction of energy contained within the FWHM of the central spot of
the transverse intensity distribution (z=0), vs pulse width τ, for
X_NA = 0.1 … 1.2.

Definition (validated against the paper's values):
    E_frac = ∫ I(r) dr over |r| ≤ r_FWHM/2   /   ∫ I(r) dr over the array
i.e. a 1-D line integral over the 201-point profile array — NOT a cylindrical
∫I·r dr integral. The 1-D definition gives the paper's plateau ≈0.78 and the
τ=1 fs drop to ≈0.62–0.66; the cylindrical one gives ≈0.46 (wrong).

Array window: fixed in optical coordinates, v ∈ ±6.70 (= ±1 μm at X_NA=0.8,
the paper's Fig-2 transverse window), scaled per NA.

Reference curve (paper): E_frac = 0.11·τ + 0.54  (valid τ ≲ 2 fs).
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo.style import apply as _apply_style
_apply_style()
from scipy.integrate import trapezoid

from mcdo import SimConfig, transverse_profile

LAM_C = 0.750
N_MED = 1.3
V_MAX = 6.702          # = k_c·sinα·(1 μm) at X_NA=0.8

XNA_vals = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2])
tau_vals_fs = np.arange(1, 12)        # 1 … 11 fs


def efrac_1d(r, I):
    """1-D energy fraction within the FWHM (one-sided profile, symmetric)."""
    half = I.max() / 2.0
    above = I >= half
    idx = np.where(np.diff(above.astype(int)))[0]
    if len(idx) == 0:
        return np.nan
    i = idx[0]   # first downward crossing
    r_half = np.interp(half, [I[i + 1], I[i]], [r[i + 1], r[i]])
    mask = r <= r_half
    r_in = np.concatenate([r[mask], [r_half]])
    I_in = np.concatenate([I[mask], [half]])
    E_in = trapezoid(I_in, r_in)
    E_tot = trapezoid(I, r)
    return float(E_in / E_tot) if E_tot > 0 else np.nan


results = {}
for xna in XNA_vals:
    cfg0 = SimConfig(lam_c=LAM_C, X_NA=xna, n=N_MED, tau=1e-15, N_freq=201, N_theta=501)
    r_max = V_MAX / (cfg0.k_c * cfg0.sin_alpha)
    r_arr = np.linspace(0.0, r_max, 101)
    print(f"  X_NA = {xna:.1f}  (window ±{r_max:.2f} μm) …")
    for tau_fs in tau_vals_fs:
        cfg = cfg0.with_tau(tau_fs * 1e-15)
        I = transverse_profile(r_arr, cfg, pulsed=True)
        ef = efrac_1d(r_arr, I)
        results[(f"{xna:.1f}", tau_fs)] = ef
        print(f"    τ={tau_fs:2d} fs  E_frac={ef:.4f}")

# ── Plot (paper's marker set) ──────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9.5, 6.8))

styles = [
    ('s', 'white'), ('s', 'k'), ('o', 'white'), ('o', 'k'),
    ('D', 'white'), ('D', 'k'), ('^', 'white'), ('^', 'k'),
    ('v', 'white'), ('v', 'k'), ('P', 'white'), ('X', 'white'),
]
for (marker, mfc), xna in zip(styles, XNA_vals):
    ef_vals = [results[(f"{xna:.1f}", t)] for t in tau_vals_fs]
    ax.plot(tau_vals_fs, ef_vals, marker=marker, ms=6, lw=0,
            mfc=mfc, mec='k', mew=0.8, label=f'{xna:.1f}')

tau_ref = np.linspace(1, 11, 100)
ax.plot(tau_ref, 0.11 * tau_ref + 0.54, 'k-', lw=2.0, label='0.11τ+0.54')

ax.set_xlabel('Pulse width (fs)')
ax.set_ylabel('Energy fraction')
ax.set_title('Energy within the central-spot full width at half maximum')
# the paper's Fig. 3 frame, so the two can be laid side by side
ax.set_xlim(1, 11)
ax.set_ylim(0.63, 0.81)
ax.set_xticks(range(1, 12))
ax.set_yticks(np.arange(0.63, 0.8101, 0.03))
ax.legend(fontsize=8, ncol=2, loc='lower right', title='Numerical aperture')
plt.tight_layout()

out = os.path.join(os.path.dirname(__file__), '..', 'output', '01_romallosa', 'fig3_energy.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f"Saved → {out}")
