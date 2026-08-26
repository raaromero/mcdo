r"""
Paper-1 robustness map — the headline claim tested across NA, ε and τ.

Claim: the annular depth-of-focus extension DOF(ε)/DOF(0) is invariant to
few-cycle bandwidth. The existing verification is at NA=0.8; a referee will ask
whether that survives at other apertures and on a denser pulse grid. Here we
compute the axial y-cut |I₀−I₂|² profile for every (NA, ε, τ) in

    NA ∈ {0.6, 0.8, 1.0},  ε ∈ {0, 0.5, 0.9, 0.99},  τ ∈ {cw, 5, 2, 1} fs

via the validated Eq.-10 spectral sum (full window; N_freq=101 — the pulsed-S
diagnostic showed results are flat in N_freq from 51 up), and report the DOF
ratio's spread across τ at fixed (NA, ε). Deterministic — no Monte Carlo.

Output: output/05_pulsed_pupils/paper_robustness.png + .npz + printed table.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo import SimConfig
from mcdo.annular import compute_integrals_annular

plt.rcParams.update({'font.size': 12, 'axes.titlesize': 12, 'axes.labelsize': 11,
                     'legend.fontsize': 9, 'axes.grid': True, 'grid.alpha': 0.25,
                     'savefig.dpi': 300})

LAM, N_MED, NT, NFREQ = 0.750, 1.3, 501, 101
C_UM = 2.99792458e14
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '05_pulsed_pupils')
NAS = [0.6, 0.8, 1.0]
EPS = [0.0, 0.5, 0.9, 0.99]
TAUS = [np.inf, 5e-15, 2e-15, 1e-15]
TLAB = ['cw', '5 fs', '2 fs', '1 fs']
u_arr = np.linspace(0.0, 700.0, 3501)


def axial_profile(cfg, eps, tau):
    """Pulsed axial y-cut |I0-I2|^2 at r=0 (Eq. 10, full spectral window)."""
    z = u_arr / (cfg.k_c * cfg.sin2_alpha)
    if np.isinf(tau):
        oms, W = np.array([cfg.omega_c]), np.array([1.0])
    else:
        oms = cfg.omega_grid(); W = cfg.spectral_power(oms)
    ax = np.zeros_like(u_arr)
    for om, w in zip(oms, W):
        if om <= 0:
            continue
        I0, I1, I2 = compute_integrals_annular(np.array([0.0]), z,
                                               cfg.n * om / C_UM, cfg.alpha, eps, NT)
        ax += w * np.abs(I0[:, 0] - I2[:, 0]) ** 2
    return ax / ax.max()


def fwhm_u(I):
    half = I.max() / 2.0
    i = np.where(np.diff((I >= half).astype(int)))[0]
    if len(i) == 0:
        return np.nan
    return 2.0 * np.interp(half, [I[i[0] + 1], I[i[0]]], [u_arr[i[0] + 1], u_arr[i[0]]])


dof = np.full((len(NAS), len(EPS), len(TAUS)), np.nan)
print("Paper-1 robustness — DOF(ε)/DOF(0) across NA × ε × τ (Eq.10, N_freq=101):\n")
for i, na in enumerate(NAS):
    cfg = SimConfig(lam_c=LAM, X_NA=na, n=N_MED, tau=1e-15, N_freq=NFREQ, N_theta=NT)
    for j, e in enumerate(EPS):
        for k, (tau, tl) in enumerate(zip(TAUS, TLAB)):
            c = cfg.with_tau(tau)
            dof[i, j, k] = fwhm_u(axial_profile(c, e, tau))
    ratios = dof[i] / dof[i, 0]           # ratio to ε=0 at the SAME τ
    print(f"NA={na}:  DOF(ε)/DOF(0)  [rows ε, cols {TLAB}]")
    for j, e in enumerate(EPS[1:], 1):
        r = ratios[j]
        spread = (r.max() - r.min()) / r.mean()
        print(f"   ε={e:<5}: " + "  ".join(f"{x:7.3f}" for x in r)
              + f"   spread {100*spread:.2f}%")
    print()

np.savez_compressed(os.path.join(OUT, 'paper_robustness.npz'),
                    dof=dof, NAS=NAS, EPS=EPS, TLAB=TLAB, u_arr=u_arr)

# ── figure: DOF ratio vs τ, per ε, one panel per NA ─────────────────────────
fig, axes = plt.subplots(1, len(NAS), figsize=(5 * len(NAS), 4.6), sharey=True)
fig.suptitle('Headline robustness — annular DOF extension is bandwidth-invariant '
             'at every aperture (Eq. 10, y-cut)', fontsize=13)
xpos = np.arange(len(TAUS))
cols = {0.5: 'C0', 0.9: 'C1', 0.99: 'C3'}
for i, (na, a) in enumerate(zip(NAS, axes)):
    for j, e in enumerate(EPS[1:], 1):
        r = dof[i, j] / dof[i, 0]
        a.plot(xpos, r / r[0], 'o-', color=cols[e], lw=1.8, ms=6,
               label=f'ε={e}' if i == 0 else None)
    a.axhline(1.0, color='k', ls='--', lw=1)
    a.set_xticks(xpos, TLAB); a.set_ylim(0.97, 1.03)
    a.set_xlabel('pulse width τ'); a.set_title(f'NA = {na}')
    if i == 0:
        a.set_ylabel('[DOF(ε)/DOF(0)](τ) / [DOF(ε)/DOF(0)](cw)')
        a.legend()
plt.tight_layout()
out = os.path.join(OUT, 'paper_robustness.png')
fig.savefig(out, bbox_inches='tight'); plt.close(fig)
print(f"Saved → {out}\n      → {OUT}/paper_robustness.npz")
