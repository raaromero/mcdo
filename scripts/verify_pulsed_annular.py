"""
Phase 5 — pulsed sources × annular apertures (the new science).

Question (the progress report's "immediate next step"): how does few-cycle
spectral broadening interact with the annular DOF extension?

Method: Eq.-10 spectral sum (validated full-spectrum grid) over annular
fields (validated field-level Babinet). For each (τ, ε):
  - axial profile on a fixed physical z-grid (labeled in central-frequency
    optical units u_c = k_c sin²α z)  →  DOF(τ, ε)
  - transverse profile at z=0  →  zero-filling of the Bessel-like rings
    (Linfoot S vs the CW annular reference)

X_NA = 0.8, λc = 750 nm, n = 1.3, linear-x y-cut, N_freq = 201, N_theta = 501.
Output: output/05_pulsed_pupils/verify_pulsed_annular.png + tables.
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
from mcdo.linfoot import structural_content
from mcdo.figio import save_panels

LAM, N_MED, NT, NFREQ = 0.750, 1.3, 501, 201
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '05_pulsed_pupils')
os.makedirs(OUT, exist_ok=True)

C_UM = 2.99792458e14
v_arr = np.linspace(0.0, 12.0, 361)
u_arr = np.linspace(0.0, 700.0, 3501)

ydir = lambda I0, I1, I2: np.abs(I0 - I2) ** 2

EPS = [0.0, 0.5, 0.9, 0.99]
TAUS = [np.inf, 5e-15, 2e-15, 1e-15]
TAU_LABELS = ['cw', '5 fs', '2 fs', '1 fs']


_cfg_ref = SimConfig(lam_c=LAM, X_NA=0.8, n=N_MED, tau=np.inf, N_freq=1, N_theta=NT)
r_um = v_arr / (_cfg_ref.k_c * _cfg_ref.sin_alpha)      # physical radius (μm)
z_um = u_arr / (_cfg_ref.k_c * _cfg_ref.sin2_alpha)     # physical defocus (μm)


def profiles(tau, eps):
    """(transverse@z=0, axial@r=0) for pulse width tau and obstruction eps."""
    cfg = SimConfig(lam_c=LAM, X_NA=0.8, n=N_MED, tau=tau,
                    N_freq=NFREQ, N_theta=NT)
    r = v_arr / (cfg.k_c * cfg.sin_alpha)
    z = u_arr / (cfg.k_c * cfg.sin2_alpha)
    if np.isinf(tau):
        I0, I1, I2 = compute_integrals_annular(r, np.array([0.0]), cfg.k_c,
                                               cfg.alpha, eps, NT)
        tr = ydir(I0[0], I1[0], I2[0])
        I0, I1, I2 = compute_integrals_annular(np.array([0.0]), z, cfg.k_c,
                                               cfg.alpha, eps, NT)
        ax = ydir(I0[:, 0], I1[:, 0], I2[:, 0])
    else:
        omegas = cfg.omega_grid()
        S = cfg.spectral_power(omegas)
        tr = np.zeros_like(v_arr)
        ax = np.zeros_like(u_arr)
        for om, s in zip(omegas, S):
            k = cfg.n * om / C_UM
            if k <= 0:
                continue
            I0, I1, I2 = compute_integrals_annular(r, np.array([0.0]), k,
                                                   cfg.alpha, eps, NT)
            tr += s * ydir(I0[0], I1[0], I2[0])
            I0, I1, I2 = compute_integrals_annular(np.array([0.0]), z, k,
                                                   cfg.alpha, eps, NT)
            ax += s * ydir(I0[:, 0], I1[:, 0], I2[:, 0])
    return tr / tr.max(), ax / ax.max()


def fwhm(x, y):
    half = y.max() / 2.0
    above = y >= half
    i = np.where(np.diff(above.astype(int)))[0]
    if len(i) == 0:
        return np.nan
    return 2 * (np.interp(half, [y[i[-1] + 1], y[i[-1]]],
                          [x[i[-1] + 1], x[i[-1]]])) if y[0] >= half else np.nan


def fwhm_axial(I):
    """Axial FWHM on the one-sided u grid (profile peaks at u=0)."""
    half = I.max() / 2.0
    i = np.where(np.diff((I >= half).astype(int)))[0]
    if len(i) == 0:
        return np.nan
    return 2.0 * np.interp(half, [I[i[0] + 1], I[i[0]]],
                           [u_arr[i[0] + 1], u_arr[i[0]]])


print("computing (τ, ε) grid …")
data = {}
for tau, tl in zip(TAUS, TAU_LABELS):
    for e in EPS:
        data[(tl, e)] = profiles(tau, e)
        print(f"  τ={tl:>4}  ε={e:4.2f}  done")

print("\nDOF (axial FWHM, u_c units) and ratio to its own CW:")
print(f"{'ε':>5} " + "".join(f"{tl:>10}" for tl in TAU_LABELS) + f"{'1fs/cw':>9}")
dof = {}
for e in EPS:
    row = [fwhm_axial(data[(tl, e)][1]) for tl in TAU_LABELS]
    dof[e] = row
    print(f"{e:>5.2f} " + "".join(f"{d:>10.2f}" for d in row)
          + f"{row[-1]/row[0]:>9.3f}")

print("\nDOF extension ratio DOF(ε)/DOF(0) — does pulsing degrade it?")
print(f"{'ε':>5} " + "".join(f"{tl:>10}" for tl in TAU_LABELS))
for e in EPS:
    print(f"{e:>5.2f} " + "".join(
        f"{dof[e][j]/dof[0.0][j]:>10.2f}" for j in range(len(TAU_LABELS))))

print("\nTransverse Linfoot S (pulsed vs CW, same ε) — ring-contrast loss:")
for e in EPS:
    cw_tr = data[('cw', e)][0]
    vals = [structural_content(cw_tr, data[(tl, e)][0])
            for tl in TAU_LABELS[1:]]
    print(f"  ε={e:4.2f}:  " + "  ".join(
        f"S({tl})={s:.3f}" for tl, s in zip(TAU_LABELS[1:], vals)))

# ── Figure ─────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(16.9, 12.2))
fig.suptitle('Pulsed annular apertures, numerical aperture 0.8, 750 nm', fontsize=13)

ax = axes[0, 0]
for tl, c in zip(TAU_LABELS, ['k', 'C2', 'C1', 'C3']):
    ax.plot(r_um, data[(tl, 0.99)][0], color=c, lw=2.0, label=tl)
ax.set_yscale('log'); ax.set_ylim(1e-4, 1.5)
ax.set_xlabel('Radial position r (μm)'); ax.set_ylabel('Normalized intensity')
ax.set_title('(a) Transverse profile, obstruction ratio 0.99', fontsize=11)
ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1.0), frameon=False, borderaxespad=0.0)

ax = axes[0, 1]
for tl, c in zip(TAU_LABELS, ['k', 'C2', 'C1', 'C3']):
    ax.plot(r_um, data[(tl, 0.0)][0], color=c, lw=2.0, label=tl)
ax.set_yscale('log'); ax.set_ylim(1e-4, 1.5)
ax.set_xlabel('Radial position r (μm)'); ax.set_ylabel('Normalized intensity')
ax.set_title('(b) Transverse profile, full disk', fontsize=11)
ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1.0), frameon=False, borderaxespad=0.0)

ax = axes[1, 0]
for tl, c in zip(TAU_LABELS, ['k', 'C2', 'C1', 'C3']):
    ax.plot(z_um, data[(tl, 0.99)][1], color=c, lw=2.0, label=tl)
ax.set_xlim(0, z_um[-1])
ax.set_xlabel('Axial position z (μm)'); ax.set_ylabel('Normalized on-axis intensity')
ax.set_title('(c) Axial profile, obstruction ratio 0.99', fontsize=11)
ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1.0), frameon=False, borderaxespad=0.0)

ax = axes[1, 1]
for j, (tl, c) in enumerate(zip(TAU_LABELS, ['k', 'C2', 'C1', 'C3'])):
    ratios = [dof[e][j] / dof[0.0][j] for e in EPS]
    ax.plot(EPS, ratios, 'o-', color=c, ms=4, lw=2.0, label=tl)
e_th = np.linspace(0, 0.992, 200)
ax.plot(e_th, 1 / (1 - e_th ** 2), 'k--', lw=2.0, alpha=0.5,
        label='paraxial 1/(1−ε²)')
ax.set_yscale('log')
ax.set_xlabel('Obstruction ratio'); ax.set_ylabel('Depth of focus, relative')
ax.set_title('(d) Depth of focus against obstruction ratio', fontsize=11)
ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1.0), frameon=False, borderaxespad=0.0)

plt.tight_layout()
out = os.path.join(OUT, 'verify_pulsed_annular.png')
save_panels(fig, fig.axes, os.path.join(os.path.dirname(__file__), '..', 'output', '05_pulsed_pupils', 'panels'), 'verify_pulsed_annular')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f"\nSaved → {out}")
