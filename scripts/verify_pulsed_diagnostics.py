r"""
Diagnostic for the pulsed Linfoot-S non-monotonicity flag (Phase 5): is the
dip-then-rise of S(τ) at high ε a real parameter effect, a spectral-sampling
artifact, or an artifact of using only ONE polarization cut?

Three tests (annular ε, transverse profile at z=0, S vs the CW reference at the
same ε; S = structural_content = Σtest²/Σref²):

  (A) PARAMETER — S vs τ on a DENSE grid (cw, 10…1 fs) for ε = 0.5/0.9/0.99.
      A smooth dip-then-rise is physical; a jagged jump would signal numerics.
  (B) SAMPLING — S vs N_freq (51…801) at ε=0.9, τ = 2 fs and 1 fs. Flat ⇒ the
      effect is NOT spectral undersampling.
  (C) POLARIZATION — S vs τ at ε=0.9 for the y-cut |I₀−I₂|² (current), the
      x-cut |I₀+I₂|²+4|I₁|², and the full azimuth-averaged |I₀|²+|I₂|²+2|I₁|²
      (all of E_x,E_y,E_z). Does the non-monotonicity depend on the cut?

Output: output/05_pulsed_pupils/pulsed_S_diagnostic.png
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo import SimConfig
from mcdo.annular import compute_integrals_annular
from mcdo.linfoot import structural_content

plt.rcParams.update({'font.size': 12, 'axes.titlesize': 12, 'axes.labelsize': 11,
                     'legend.fontsize': 9, 'axes.grid': True, 'grid.alpha': 0.25,
                     'savefig.dpi': 200})

LAM, N_MED, NT = 0.750, 1.3, 501
C_UM = 2.99792458e14
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '05_pulsed_pupils')
os.makedirs(OUT, exist_ok=True)
v_arr = np.linspace(0.0, 12.0, 220)


def measures(tau, eps, N_freq=201):
    """Transverse (z=0) profiles for the y-cut, x-cut and full vector, pulsed."""
    cfg = SimConfig(lam_c=LAM, X_NA=0.8, n=N_MED, tau=tau, N_freq=N_freq, N_theta=NT)
    r = v_arr / (cfg.k_c * cfg.sin_alpha)
    if np.isinf(tau):
        oms, Sw = np.array([cfg.omega_c]), np.array([1.0])
    else:
        oms = cfg.omega_grid(); Sw = cfg.spectral_power(oms)
    ay = np.zeros_like(v_arr); ax_ = np.zeros_like(v_arr); af = np.zeros_like(v_arr)
    for o, s in zip(oms, Sw):
        if o <= 0:
            continue
        I0, I1, I2 = compute_integrals_annular(r, np.array([0.0]),
                                               cfg.n * o / C_UM, cfg.alpha, eps, NT)
        a, b, c = I0[0], I1[0], I2[0]
        ay += s * np.abs(a - c) ** 2
        ax_ += s * (np.abs(a + c) ** 2 + 4 * np.abs(b) ** 2)
        af += s * (np.abs(a) ** 2 + np.abs(c) ** 2 + 2 * np.abs(b) ** 2)
    return [m / m.max() for m in (ay, ax_, af)]


TAUS_FS = [10, 7, 5, 4, 3, 2.5, 2, 1.5, 1]
fig, axes = plt.subplots(1, 3, figsize=(16, 4.8))
fig.suptitle('Pulsed Linfoot-S non-monotonicity — diagnostic '
             '(annular, transverse z=0, S vs CW same ε)', fontsize=13)

# (A) S vs τ for three ε (y-cut)
ax = axes[0]
known = {}
for eps, col in [(0.5, 'C0'), (0.9, 'C1'), (0.99, 'C3')]:
    cw_y = measures(np.inf, eps)[0]
    Sy = []
    cache = {}
    for fs in TAUS_FS:
        my = measures(fs * 1e-15, eps)
        cache[fs] = my
        Sy.append(structural_content(cw_y, my[0]))
    if eps == 0.9:
        eps09 = (cw_y, cache)                 # reuse for panel C
    ax.plot(TAUS_FS, Sy, 'o-', color=col, lw=1.8, ms=6, label=f'ε = {eps}')
    known[eps] = {fs: s for fs, s in zip(TAUS_FS, Sy)}
ax.axhline(1.0, color='k', ls='--', lw=1)
ax.set_xlabel('pulse width τ (fs)'); ax.set_ylabel('Linfoot S (pulsed vs CW)')
ax.set_title('(A) parameter: S vs τ (dense) — smooth dip-then-rise?')
ax.legend()

# (B) S vs N_freq at ε=0.9 for τ = 2 fs and 1 fs (y-cut)
ax = axes[1]
NFS = [51, 101, 201, 401, 801]
cw_y09 = measures(np.inf, 0.9)[0]
for fs, col in [(2, 'C1'), (1, 'C3')]:
    Sn = [structural_content(cw_y09, measures(fs * 1e-15, 0.9, nf)[0]) for nf in NFS]
    ax.plot(NFS, Sn, 'o-', color=col, lw=1.8, ms=6, label=f'τ = {fs} fs')
ax.axhline(1.0, color='k', ls='--', lw=1)
ax.set_xscale('log')
ax.set_xlabel('N_freq (spectral samples)'); ax.set_ylabel('Linfoot S')
ax.set_title('(B) sampling: S vs N_freq (ε=0.9) — flat ⇒ not undersampling')
ax.legend()

# (C) S vs τ at ε=0.9 for y-cut / x-cut / full vector
ax = axes[2]
cw_y, cache = eps09
cw_x = measures(np.inf, 0.9)[1]; cw_f = measures(np.inf, 0.9)[2]
Sy = [structural_content(cw_y, cache[fs][0]) for fs in TAUS_FS]
Sx = [structural_content(cw_x, cache[fs][1]) for fs in TAUS_FS]
Sf = [structural_content(cw_f, cache[fs][2]) for fs in TAUS_FS]
ax.plot(TAUS_FS, Sy, 'o-', color='C1', lw=1.8, ms=6, label='y-cut |I₀−I₂|² (current)')
ax.plot(TAUS_FS, Sx, 's-', color='C2', lw=1.8, ms=6, label='x-cut |I₀+I₂|²+4|I₁|²')
ax.plot(TAUS_FS, Sf, '^-', color='C4', lw=1.8, ms=6, label='full |I₀|²+|I₂|²+2|I₁|²')
ax.axhline(1.0, color='k', ls='--', lw=1)
ax.set_xlabel('pulse width τ (fs)'); ax.set_ylabel('Linfoot S')
ax.set_title('(C) polarization: y-cut vs x-cut vs full E_x,E_y,E_z (ε=0.9)')
ax.legend()

plt.tight_layout()
out = os.path.join(OUT, 'pulsed_S_diagnostic.png')
fig.savefig(out, bbox_inches='tight'); plt.close(fig)

print("Cross-check vs known Phase-5 values (ε=0.9, y-cut): "
      "S(5fs)=0.988, S(2fs)=0.987, S(1fs)=1.058 expected")
print(f"  this run: S(5fs)={known[0.9][5]:.3f}, S(2fs)={known[0.9][2]:.3f}, "
      f"S(1fs)={known[0.9][1]:.3f}")
print(f"Saved → {out}")
