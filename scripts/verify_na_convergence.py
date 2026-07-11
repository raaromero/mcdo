"""
Verification: vector RW vs scalar Debye vs paraxial Airy across NA.

Theory chain (each step removes one physical ingredient):
  1. Vector Richards-Wolf      — exact aplanatic solution (Eqs. 5–7).
  2. Scalar angular Debye      — drops polarization (vector kernels);
                                 keeps exact wide-angle geometry + √cosθ.
  3. Paraxial Airy / sinc²     — additionally takes the α → 0 limit.

So:  RW − scalar  isolates POLARIZATION (vector) effects;
     scalar − Airy isolates WIDE-ANGLE geometry effects.

Checks
------
A. Low-NA convergence (X_NA = 0.1): all four focal-plane profiles
   (RW y-cut, RW x-cut, scalar, Airy) must coincide — validates both our
   high-NA machinery and the scalar module against the analytic limit.
B. High-NA divergence (X_NA = 1.2, n = 1.3): RW x/y asymmetry appears;
   scalar sits between; quantifies where vector theory is REQUIRED.
C. FWHM (in v units) vs NA for all methods → NA thresholds at 1% and 5%
   deviation from Airy (FWHM_v = 3.2326).
D. Axial first zero u₀ vs NA (paraxial limit u₀ = 4π).
E. Gaussian apodization: α_t = 0 regression (must equal uniform) and
   spot broadening for α_t = 1, 4 at X_NA = 0.8.

All profiles plotted in optical coordinates so every NA is comparable.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo import SimConfig
from mcdo.rw_integrals import compute_integrals
from mcdo.debye import scalar_debye, airy_intensity
from mcdo.apodization import gaussian as gaussian_apod

LAM = 0.750
N_MED = 1.3
NT = 1001

v_arr = np.linspace(0.0, 10.0, 401)
u_arr = np.linspace(0.0, 20.0, 801)

AIRY_FWHM_V = 3.2326  # FWHM of [2J1(v)/v]^2


def fwhm_x(x, y):
    half = y.max() / 2.0
    i = np.where(np.diff((y >= half).astype(int)))[0][0]
    return 2.0 * np.interp(half, [y[i + 1], y[i]], [x[i + 1], x[i]])


def rw_profiles(cfg, apod=None):
    """Focal-plane RW intensities along y (perp. to pol.) and x (par.) in v."""
    r = v_arr / (cfg.k_c * cfg.sin_alpha)
    I0, I1, I2 = compute_integrals(r, np.array([0.0]), cfg.k_c, cfg.alpha,
                                   NT, apodization=apod)
    I0, I1, I2 = I0[0], I1[0], I2[0]
    I_y = np.abs(I0 - I2) ** 2                       # φ=π/2: Ex only
    I_x = np.abs(I0 + I2) ** 2 + 4 * np.abs(I1) ** 2  # φ=0: Ex and Ez
    return I_y / I_y.max(), I_x / I_x.max()


def scalar_profile(cfg, apod=None):
    r = v_arr / (cfg.k_c * cfg.sin_alpha)
    I = scalar_debye(r, np.array([0.0]), cfg.k_c, cfg.alpha, NT,
                     apodization=apod)[0]
    return I / I.max()


def rw_axial(cfg):
    z = u_arr / (cfg.k_c * cfg.sin2_alpha)
    I0, I1, I2 = compute_integrals(np.array([0.0]), z, cfg.k_c, cfg.alpha, NT)
    I = np.abs(I0[:, 0] - I2[:, 0]) ** 2
    return I / I.max()


def scalar_axial(cfg):
    z = u_arr / (cfg.k_c * cfg.sin2_alpha)
    I = scalar_debye(np.array([0.0]), z, cfg.k_c, cfg.alpha, NT)[:, 0]
    return I / I.max()


def first_min_u(I):
    """First local minimum beyond the main lobe: position and depth.

    At low NA this is a true zero near u=4π; at high NA the minimum is
    non-zero (the apodized axial 'sinc' loses its exact zeros).
    """
    interior = np.where((I[1:-1] < I[:-2]) & (I[1:-1] <= I[2:]))[0] + 1
    interior = interior[u_arr[interior] > 2.0]
    i = int(interior[0])
    return u_arr[i], I[i]


airy = airy_intensity(v_arr)

# ── A & B: profiles at low and high NA ─────────────────────────────────────
profiles = {}
for xna in [0.1, 0.8, 1.2]:
    cfg = SimConfig(lam_c=LAM, X_NA=xna, n=N_MED, tau=np.inf,
                    N_freq=3, N_theta=NT)
    I_y, I_x = rw_profiles(cfg)
    I_s = scalar_profile(cfg)
    profiles[xna] = (I_y, I_x, I_s)
    dev = lambda I: np.max(np.abs(I - airy))
    print(f"X_NA={xna}:  max|RW_y − Airy|={dev(I_y):.4f}  "
          f"max|RW_x − Airy|={dev(I_x):.4f}  max|scalar − Airy|={dev(I_s):.4f}")

# ── C: FWHM vs NA ──────────────────────────────────────────────────────────
XNA_vals = np.arange(0.05, 1.26, 0.05)
fw = {'RW_y': [], 'RW_x': [], 'scalar': []}
for xna in XNA_vals:
    cfg = SimConfig(lam_c=LAM, X_NA=xna, n=N_MED, tau=np.inf,
                    N_freq=3, N_theta=NT)
    I_y, I_x = rw_profiles(cfg)
    I_s = scalar_profile(cfg)
    fw['RW_y'].append(fwhm_x(v_arr, I_y))
    fw['RW_x'].append(fwhm_x(v_arr, I_x))
    fw['scalar'].append(fwhm_x(v_arr, I_s))
fw = {k: np.array(o) for k, o in fw.items()}

print("\nFWHM (v units) vs X_NA — deviation from Airy 3.2326:")
print(f"{'X_NA':>5} {'RW_y':>8} {'RW_x':>8} {'scalar':>8} "
      f"{'dev_y%':>7} {'dev_x%':>7} {'dev_s%':>7}")
for i, xna in enumerate(XNA_vals):
    dy = 100 * (fw['RW_y'][i] / AIRY_FWHM_V - 1)
    dx = 100 * (fw['RW_x'][i] / AIRY_FWHM_V - 1)
    ds = 100 * (fw['scalar'][i] / AIRY_FWHM_V - 1)
    print(f"{xna:>5.2f} {fw['RW_y'][i]:>8.4f} {fw['RW_x'][i]:>8.4f} "
          f"{fw['scalar'][i]:>8.4f} {dy:>7.2f} {dx:>7.2f} {ds:>7.2f}")

for thresh in [1.0, 5.0]:
    devx = 100 * np.abs(fw['RW_x'] / fw['scalar'] - 1)
    idx = np.where(devx > thresh)[0]
    na_t = XNA_vals[idx[0]] if len(idx) else None
    print(f"vector-vs-scalar x-FWHM deviation exceeds {thresh}% at X_NA = {na_t}")

# ── D: axial first minimum ─────────────────────────────────────────────────
print("\nAxial first minimum u₀ (paraxial limit: true zero at 4π = 12.566):")
for xna in [0.1, 0.4, 0.8, 1.2]:
    cfg = SimConfig(lam_c=LAM, X_NA=xna, n=N_MED, tau=np.inf,
                    N_freq=3, N_theta=NT)
    ur, dr = first_min_u(rw_axial(cfg))
    us, ds = first_min_u(scalar_axial(cfg))
    print(f"  X_NA={xna}:  RW u₀={ur:.3f} (depth {dr:.2e})   "
          f"scalar u₀={us:.3f} (depth {ds:.2e})")

# ── E: apodization ─────────────────────────────────────────────────────────
cfg8 = SimConfig(lam_c=LAM, X_NA=0.8, n=N_MED, tau=np.inf, N_freq=3, N_theta=NT)
I_uni, _ = rw_profiles(cfg8)
apod_profiles = {0.0: I_uni}
print("\nGaussian apodization at X_NA=0.8 (RW y-cut):")
A0 = gaussian_apod(1e-12, cfg8.sin2_alpha)
I_reg, _ = rw_profiles(cfg8, apod=A0)
print(f"  regression α_t→0 vs uniform: max diff = {np.max(np.abs(I_reg - I_uni)):.2e}")
for at in [1.0, 2.0, 4.0]:
    A = gaussian_apod(at, cfg8.sin2_alpha)
    I_a, _ = rw_profiles(cfg8, apod=A)
    apod_profiles[at] = I_a
    print(f"  α_t={at}: FWHM_v = {fwhm_x(v_arr, I_a):.4f} "
          f"(uniform {fwhm_x(v_arr, I_uni):.4f})")

# ── Figure ─────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(12, 9))
fig.suptitle('NA-convergence verification: vector RW vs scalar Debye vs Airy '
             f'(λ={LAM} μm, n={N_MED})', fontsize=12)

ax = axes[0, 0]
I_y, I_x, I_s = profiles[0.1]
ax.plot(v_arr, airy, 'k-', lw=2.2, alpha=0.35, label='Airy [2J₁(v)/v]²')
ax.plot(v_arr, I_y, 'C0-', lw=1.0, label='RW y-cut')
ax.plot(v_arr, I_x, 'C1--', lw=1.0, label='RW x-cut')
ax.plot(v_arr, I_s, 'C2:', lw=1.4, label='scalar Debye')
ax.set_title('(a) X_NA = 0.1 — all theories must coincide')
ax.set_xlabel('v'); ax.set_ylabel('normalized intensity')
ax.set_yscale('log'); ax.set_ylim(1e-6, 1.5); ax.legend(fontsize=8)

ax = axes[0, 1]
I_y, I_x, I_s = profiles[1.2]
ax.plot(v_arr, airy, 'k-', lw=2.2, alpha=0.35, label='Airy')
ax.plot(v_arr, I_y, 'C0-', lw=1.0, label='RW y-cut')
ax.plot(v_arr, I_x, 'C1--', lw=1.0, label='RW x-cut')
ax.plot(v_arr, I_s, 'C2:', lw=1.4, label='scalar Debye')
ax.set_title('(b) X_NA = 1.2 — vector splitting (x vs y) appears')
ax.set_xlabel('v'); ax.set_ylabel('normalized intensity')
ax.set_yscale('log'); ax.set_ylim(1e-6, 1.5); ax.legend(fontsize=8)

ax = axes[1, 0]
ax.axhline(AIRY_FWHM_V, color='k', alpha=0.35, lw=2.2, label='Airy 3.233')
ax.plot(XNA_vals, fw['RW_y'], 'C0o-', ms=3, lw=1, label='RW y-cut')
ax.plot(XNA_vals, fw['RW_x'], 'C1s--', ms=3, lw=1, label='RW x-cut')
ax.plot(XNA_vals, fw['scalar'], 'C2^:', ms=3, lw=1, label='scalar Debye')
ax.set_title('(c) focal-spot FWHM (v units) vs NA')
ax.set_xlabel('X_NA'); ax.set_ylabel('FWHM (v)'); ax.legend(fontsize=8)

ax = axes[1, 1]
ax.plot(v_arr, apod_profiles[0.0], 'k-', lw=1.4, label='uniform (α_t=0)')
for at, style in [(1.0, 'C0--'), (2.0, 'C1-.'), (4.0, 'C3:')]:
    ax.plot(v_arr, apod_profiles[at], style, lw=1.2, label=f'Gaussian α_t={at:g}')
ax.set_title('(d) Gaussian apodization broadens the spot (X_NA=0.8, RW y-cut)')
ax.set_xlabel('v'); ax.set_ylabel('normalized intensity')
ax.set_yscale('log'); ax.set_ylim(1e-6, 1.5); ax.legend(fontsize=8)

plt.tight_layout()
out = os.path.join(os.path.dirname(__file__), '..', 'output', '02_na_apodization',
                   'verify_na_convergence.png')
fig.savefig(out, dpi=150, bbox_inches='tight')
plt.close(fig)
print(f"\nSaved → {out}")
