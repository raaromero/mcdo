"""
Phase 5 — confirm the non-monotonic ring-contrast flag by decomposing the
transverse Linfoot S into central-lobe and ring contributions vs τ.

At ε=0.9 the cw profile is Bessel-like (many rings). Hypothesis: moderate
pulses average Bessel beams of different scales and WASH OUT the rings
(ring mean-square drops → S_ring<1), while only the 1-fs central broadening
raises the central mean-square (S_central>1). The total S is their
energy-weighted combination, hence dips below 1 before rising above.

Output: output/05_pulsed_pupils/ring_decomposition.png + table.
X_NA=0.8, ε=0.9, linear-x y-cut, N_freq=201.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo import SimConfig
from mcdo.annular import compute_integrals_annular

LAM, N_MED, NT, NFREQ = 0.750, 1.3, 501, 201
C_UM = 2.99792458e14
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '05_pulsed_pupils')
EPS = 0.9
v_arr = np.linspace(0.0, 14.0, 561)
ydir = lambda I0, I1, I2: np.abs(I0 - I2) ** 2


def transverse(tau):
    cfg = SimConfig(lam_c=LAM, X_NA=0.8, n=N_MED, tau=tau, N_freq=NFREQ, N_theta=NT)
    r = v_arr / (cfg.k_c * cfg.sin_alpha)
    if np.isinf(tau):
        I0, I1, I2 = compute_integrals_annular(r, np.array([0.0]), cfg.k_c,
                                               cfg.alpha, EPS, NT)
        I = ydir(I0[0], I1[0], I2[0])
    else:
        omegas = cfg.omega_grid(); S = cfg.spectral_power(omegas)
        I = np.zeros_like(v_arr)
        for om, s in zip(omegas, S):
            kk = cfg.n * om / C_UM
            if kk <= 0:
                continue
            I0, I1, I2 = compute_integrals_annular(r, np.array([0.0]), kk,
                                                   cfg.alpha, EPS, NT)
            I += s * ydir(I0[0], I1[0], I2[0])
    return I / I.max()


TAUS = [np.inf, 5e-15, 3e-15, 2e-15, 1.5e-15, 1e-15]
LAB = ['cw', '5 fs', '3 fs', '2 fs', '1.5 fs', '1 fs']
prof = {l: transverse(t) for t, l in zip(TAUS, LAB)}

# first zero of cw profile → central/ring split
cw = prof['cw']
mins = np.where((cw[1:-1] < cw[:-2]) & (cw[1:-1] <= cw[2:]))[0] + 1
v0 = v_arr[mins[0]]
cen = v_arr <= v0
print(f"ε={EPS}: central/ring split at first cw zero v0={v0:.2f}")
print(f"{'τ':>6} {'S_total':>9} {'S_central':>10} {'S_ring':>9} "
      f"{'ring wt':>8}")
cw_cen = np.sum(cw[cen] ** 2); cw_ring = np.sum(cw[~cen] ** 2)
ring_wt = cw_ring / (cw_cen + cw_ring)
rows = {}
for l in LAB[1:]:
    a = prof[l]
    S_tot = np.sum(a ** 2) / np.sum(cw ** 2)
    S_cen = np.sum(a[cen] ** 2) / cw_cen
    S_ring = np.sum(a[~cen] ** 2) / cw_ring
    rows[l] = (S_tot, S_cen, S_ring)
    print(f"{l:>6} {S_tot:>9.3f} {S_cen:>10.3f} {S_ring:>9.3f} {ring_wt:>8.3f}")

# ── Figure ─────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
fig.suptitle('Phase 5 flag confirmed — non-monotonic S is ring-washing '
             f'(ε={EPS}, X_NA=0.8)', fontsize=11)

ax = axes[0]
for l, c in zip(['cw', '2 fs', '1 fs'], ['k', 'C1', 'C3']):
    ax.plot(v_arr, prof[l], color=c, lw=1.3, label=l)
ax.axvline(v0, color='0.6', lw=0.7, ls=':')
ax.annotate('v₀ (split)', (v0, 1.0), fontsize=8, color='0.4')
ax.set_yscale('log'); ax.set_ylim(1e-4, 1.5)
ax.set_xlabel('v'); ax.set_ylabel('normalized intensity')
ax.set_title('(a) Bessel rings wash out with pulsing', fontsize=10)
ax.legend(fontsize=8)

ax = axes[1]
tau_fs = [5, 3, 2, 1.5, 1]
ax.plot(tau_fs, [rows[l][0] for l in LAB[1:]], 'ko-', ms=5, lw=1.2, label='S total')
ax.plot(tau_fs, [rows[l][1] for l in LAB[1:]], 'C0s--', ms=5, lw=1.1, label='S central')
ax.plot(tau_fs, [rows[l][2] for l in LAB[1:]], 'C3^--', ms=5, lw=1.1, label='S ring')
ax.axhline(1.0, color='gray', lw=0.7, ls=':')
ax.invert_xaxis()
ax.set_xlabel('pulse width τ (fs)  →  shorter')
ax.set_ylabel('Linfoot S (pulsed vs cw)')
ax.set_title(f'(b) ring S<1 (washing) vs central S>1 (broadening);\n'
             f'ring carries {ring_wt:.0%} of the weight', fontsize=10)
ax.legend(fontsize=8)

plt.tight_layout()
out = os.path.join(OUT, 'ring_decomposition.png')
fig.savefig(out, dpi=150, bbox_inches='tight')
plt.close(fig)
print(f"Saved → {out}")
