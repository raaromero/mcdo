"""
Visual verification plots for Phase 2 (one focused figure per question).

  check1_lowNA_convergence.png — do all theories coincide at low NA?
  check2_highNA_vector.png     — how does the vector splitting grow with NA?
  check3_fwhm_thresholds.png   — where does vector theory become necessary?
  check4_axial.png             — axial behavior vs NA (zeros migrate & fill)
  check5_apodization.png       — pupil A(θ) and the resulting focal spots
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo import SimConfig
from mcdo.rw_integrals import compute_integrals
from mcdo.debye import scalar_debye, airy_intensity, axial_sinc2
from mcdo.apodization import gaussian as gaussian_apod

LAM, N_MED, NT = 0.750, 1.3, 1001
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '02_na_apodization')

v_arr = np.linspace(0.0, 10.0, 401)
u_arr = np.linspace(0.0, 25.0, 1001)
AIRY_FWHM_V = 3.2326


def cfg_at(xna):
    return SimConfig(lam_c=LAM, X_NA=xna, n=N_MED, tau=np.inf, N_freq=3, N_theta=NT)


def rw_profiles(cfg, apod=None):
    r = v_arr / (cfg.k_c * cfg.sin_alpha)
    I0, I1, I2 = compute_integrals(r, np.array([0.0]), cfg.k_c, cfg.alpha,
                                   NT, apodization=apod)
    I0, I1, I2 = I0[0], I1[0], I2[0]
    I_y = np.abs(I0 - I2) ** 2
    I_x = np.abs(I0 + I2) ** 2 + 4 * np.abs(I1) ** 2
    return I_y / I_y.max(), I_x / I_x.max()


def scalar_profile(cfg):
    r = v_arr / (cfg.k_c * cfg.sin_alpha)
    I = scalar_debye(r, np.array([0.0]), cfg.k_c, cfg.alpha, NT)[0]
    return I / I.max()


def rw_axial(cfg):
    z = u_arr / (cfg.k_c * cfg.sin2_alpha)
    I0, _, I2 = compute_integrals(np.array([0.0]), z, cfg.k_c, cfg.alpha, NT)
    I = np.abs(I0[:, 0] - I2[:, 0]) ** 2
    return I / I.max()


def fwhm_x(x, y):
    half = y.max() / 2.0
    i = np.where(np.diff((y >= half).astype(int)))[0][0]
    return 2.0 * np.interp(half, [y[i + 1], y[i]], [x[i + 1], x[i]])


airy = airy_intensity(v_arr)

# ── check 1: low-NA convergence ────────────────────────────────────────────
cfg = cfg_at(0.1)
I_y, I_x = rw_profiles(cfg)
I_s = scalar_profile(cfg)

fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
fig.suptitle('Check 1 — X_NA = 0.1: every theory must coincide with the Airy analytic',
             fontsize=11)
for ax, scale in zip(axes, ['linear', 'log']):
    ax.plot(v_arr, airy, '-', color='0.65', lw=4, label='Airy [2J₁(v)/v]²')
    ax.plot(v_arr, I_y, 'C0-', lw=1.2, label='vector RW, y-cut')
    ax.plot(v_arr, I_x, 'C1--', lw=1.2, label='vector RW, x-cut')
    ax.plot(v_arr, I_s, 'C2:', lw=1.8, label='scalar Debye')
    ax.set_xlabel('v (optical units)'); ax.set_ylabel('normalized intensity')
    ax.set_yscale(scale)
    if scale == 'log':
        ax.set_ylim(1e-7, 1.5)
        ax.set_title('log scale — zeros and sidelobes align too')
    else:
        ax.set_title('linear scale')
    ax.legend(fontsize=8)
plt.tight_layout()
fig.savefig(os.path.join(OUT, 'check1_lowNA_convergence.png'), dpi=150,
            bbox_inches='tight'); plt.close(fig)

# ── check 2: vector splitting growth ───────────────────────────────────────
# One panel per quantity, NA as the line family — makes the NA evolution of
# each cut directly visible.
NA_FAMILY = [0.3, 0.6, 0.9, 1.2]
NA_COLORS = plt.cm.viridis(np.linspace(0.0, 0.85, len(NA_FAMILY)))

fam = {xna: (*rw_profiles(cfg_at(xna)), scalar_profile(cfg_at(xna)))
       for xna in NA_FAMILY}

fig, axes = plt.subplots(1, 3, figsize=(14, 4.4), sharey=True)
fig.suptitle('Check 2 — how each cut evolves with NA '
             '(x-cut broadens & loses zeros; y-cut narrows, keeps zeros; '
             'scalar barely moves)', fontsize=11)
panels = [('RW x-cut (∥ polarization)', 1),
          ('RW y-cut (⊥ polarization)', 0),
          ('scalar Debye', 2)]
for ax, (title, idx) in zip(axes, panels):
    ax.plot(v_arr, airy, '-', color='0.7', lw=4, label='Airy (NA→0)')
    for xna, col in zip(NA_FAMILY, NA_COLORS):
        ax.plot(v_arr, fam[xna][idx], color=col, lw=1.3,
                label=f'X_NA = {xna}')
    ax.set_yscale('log'); ax.set_ylim(1e-6, 1.5)
    ax.set_xlabel('v (optical units)')
    ax.set_title(title, fontsize=10)
    ax.legend(fontsize=8)
axes[0].set_ylabel('normalized intensity')
plt.tight_layout()
fig.savefig(os.path.join(OUT, 'check2_highNA_vector.png'), dpi=150,
            bbox_inches='tight'); plt.close(fig)

# ── check 3: FWHM thresholds ───────────────────────────────────────────────
XNA_vals = np.arange(0.05, 1.26, 0.05)
fw = {'RW y-cut': [], 'RW x-cut': [], 'scalar': []}
for xna in XNA_vals:
    cfg = cfg_at(xna)
    I_y, I_x = rw_profiles(cfg)
    fw['RW y-cut'].append(fwhm_x(v_arr, I_y))
    fw['RW x-cut'].append(fwhm_x(v_arr, I_x))
    fw['scalar'].append(fwhm_x(v_arr, scalar_profile(cfg)))
fw = {k: np.array(o) for k, o in fw.items()}

fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
fig.suptitle('Check 3 — focal-spot FWHM vs NA: where is vector theory necessary?',
             fontsize=11)
ax = axes[0]
ax.axhline(AIRY_FWHM_V, color='0.65', lw=3, label='Airy 3.233')
for (k, o), st in zip(fw.items(), ['C0o-', 'C1s--', 'C2^:']):
    ax.plot(XNA_vals, o, st, ms=3.5, lw=1.1, label=k)
ax.set_xlabel('X_NA'); ax.set_ylabel('FWHM (v units)')
ax.legend(fontsize=8); ax.set_title('absolute FWHM', fontsize=10)

ax = axes[1]
dev = 100 * np.abs(fw['RW x-cut'] / fw['scalar'] - 1)
dev_y = 100 * np.abs(fw['RW y-cut'] / fw['scalar'] - 1)
ax.plot(XNA_vals, dev, 'C1s--', ms=3.5, lw=1.1, label='x-cut vs scalar')
ax.plot(XNA_vals, dev_y, 'C0o-', ms=3.5, lw=1.1, label='y-cut vs scalar')
for th, na_t in [(1.0, 0.30), (5.0, 0.60)]:
    ax.axhline(th, color='k', lw=0.6, ls=':')
    ax.axvline(na_t, color='r', lw=0.8, ls=':')
    ax.annotate(f'{th:.0f}% @ X_NA≈{na_t}', (na_t, th), textcoords='offset points',
                xytext=(6, 4), fontsize=8, color='r')
ax.set_xlabel('X_NA'); ax.set_ylabel('|FWHM deviation| from scalar (%)')
ax.set_yscale('log'); ax.legend(fontsize=8)
ax.set_title('vector effect magnitude (thresholds marked)', fontsize=10)
plt.tight_layout()
fig.savefig(os.path.join(OUT, 'check3_fwhm_thresholds.png'), dpi=150,
            bbox_inches='tight'); plt.close(fig)

# ── check 4: axial behavior ────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 4.6))
fig.suptitle('Check 4 — axial profile vs NA: minima migrate from u=4π and fill in',
             fontsize=11)
ax.plot(u_arr, axial_sinc2(u_arr), '-', color='0.65', lw=4,
        label='paraxial sinc²(u/4)')
for xna, c in zip([0.1, 0.4, 0.8, 1.2], ['C0', 'C2', 'C1', 'C3']):
    ax.plot(u_arr, rw_axial(cfg_at(xna)), color=c, lw=1.2, label=f'RW X_NA={xna}')
ax.axvline(4 * np.pi, color='k', lw=0.7, ls=':')
ax.annotate('u = 4π', (4 * np.pi, 0.5), textcoords='offset points',
            xytext=(5, 0), fontsize=9)
ax.set_yscale('log'); ax.set_ylim(1e-7, 1.5)
ax.set_xlabel('u (optical units)'); ax.set_ylabel('normalized intensity')
ax.legend(fontsize=8)
plt.tight_layout()
fig.savefig(os.path.join(OUT, 'check4_axial.png'), dpi=150,
            bbox_inches='tight'); plt.close(fig)

# ── check 5: apodization ───────────────────────────────────────────────────
cfg8 = cfg_at(0.8)
theta = np.linspace(0, cfg8.alpha, 200)

fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
fig.suptitle('Check 5 — Gaussian apodization (X_NA=0.8): pupil profile → focal spot',
             fontsize=11)
ax = axes[0]
ax.plot(np.degrees(theta), np.ones_like(theta), 'k-', lw=1.4,
        label='uniform (α_t=0)')
for at, st in [(1.0, 'C0--'), (2.0, 'C1-.'), (4.0, 'C3:')]:
    A = gaussian_apod(at, cfg8.sin2_alpha)
    ax.plot(np.degrees(theta), A(theta), st, lw=1.4, label=f'α_t = {at:g}')
ax.set_xlabel('θ (deg)'); ax.set_ylabel('pupil amplitude A(θ)')
ax.set_title('illumination at the pupil', fontsize=10)
ax.legend(fontsize=8)

ax = axes[1]
I_uni, _ = rw_profiles(cfg8)
ax.plot(v_arr, I_uni, 'k-', lw=1.4,
        label=f'uniform  (FWHM_v {fwhm_x(v_arr, I_uni):.2f})')
for at, st in [(1.0, 'C0--'), (2.0, 'C1-.'), (4.0, 'C3:')]:
    I_a, _ = rw_profiles(cfg8, apod=gaussian_apod(at, cfg8.sin2_alpha))
    ax.plot(v_arr, I_a, st, lw=1.4,
            label=f'α_t={at:g}  (FWHM_v {fwhm_x(v_arr, I_a):.2f})')
ax.set_yscale('log'); ax.set_ylim(1e-7, 1.5)
ax.set_xlabel('v'); ax.set_ylabel('normalized intensity')
ax.set_title('resulting focal spot (RW y-cut)', fontsize=10)
ax.legend(fontsize=8)
plt.tight_layout()
fig.savefig(os.path.join(OUT, 'check5_apodization.png'), dpi=150,
            bbox_inches='tight'); plt.close(fig)

# ── check 6: vector anisotropy fleshed out ─────────────────────────────────
# Physics: along the y-axis (φ=π/2) only Ex = −j(I₀−I₂) survives.  Along the
# x-axis (φ=0) the longitudinal component Ez = −2I₁ adds intensity displaced
# along the polarization direction — this elongates the spot along x and
# fills the zeros.  The anisotropy is therefore a direct measure of the
# longitudinal-field strength.

cfg12 = cfg_at(1.2)

# (a) 2-D focal-plane map at X_NA=1.2
ext = 6.0
xy = np.linspace(-ext, ext, 241)
X, Y = np.meshgrid(xy, xy)
Vg = np.sqrt(X**2 + Y**2)
PHI = np.arctan2(Y, X)
r_g = np.unique(Vg) / (cfg12.k_c * cfg12.sin_alpha)
I0g, I1g, I2g = compute_integrals(r_g, np.array([0.0]), cfg12.k_c,
                                  cfg12.alpha, NT)
interp = lambda M: np.interp(Vg.ravel(), np.unique(Vg), M).reshape(Vg.shape)
I0m = interp(I0g[0].real) + 1j * interp(I0g[0].imag)
I1m = interp(I1g[0].real) + 1j * interp(I1g[0].imag)
I2m = interp(I2g[0].real) + 1j * interp(I2g[0].imag)
Ex2 = np.abs(I0m + I2m * np.cos(2 * PHI)) ** 2
Ey2 = np.abs(I2m * np.sin(2 * PHI)) ** 2
Ez2 = 4 * np.abs(I1m * np.cos(PHI)) ** 2
Itot = Ex2 + Ey2 + Ez2
Itot /= Itot.max()

# (b) component decomposition along the x-cut at X_NA=1.2
cfg = cfg12
r = v_arr / (cfg.k_c * cfg.sin_alpha)
I0, I1, I2 = compute_integrals(r, np.array([0.0]), cfg.k_c, cfg.alpha, NT)
I0, I1, I2 = I0[0], I1[0], I2[0]
Ex2_x = np.abs(I0 + I2) ** 2          # |Ex|² along x
Ez2_x = 4 * np.abs(I1) ** 2           # |Ez|² along x
tot_x = Ex2_x + Ez2_x
norm = tot_x.max()

# (c) anisotropy ratio + Ez energy share vs NA
ratio, ez_share = [], []
for xna in XNA_vals:
    c = cfg_at(xna)
    rr = v_arr / (c.k_c * c.sin_alpha)
    a0, a1, a2 = compute_integrals(rr, np.array([0.0]), c.k_c, c.alpha, NT)
    a0, a1, a2 = a0[0], a1[0], a2[0]
    Iy = np.abs(a0 - a2) ** 2
    Ix = np.abs(a0 + a2) ** 2 + 4 * np.abs(a1) ** 2
    ratio.append(fwhm_x(v_arr, Ix / Ix.max()) / fwhm_x(v_arr, Iy / Iy.max()))
    # energy share of Ez along the x-cut (v-line integral, focal plane)
    ez = np.trapezoid(4 * np.abs(a1) ** 2 * v_arr, v_arr)
    ex = np.trapezoid((np.abs(a0 + a2) ** 2) * v_arr, v_arr)
    ez_share.append(ez / (ez + ex))

fig = plt.figure(figsize=(13, 4.4))
fig.suptitle('Check 6 — vector anisotropy: the longitudinal field E_z elongates '
             'the spot along the polarization (x) axis', fontsize=11)

ax = fig.add_subplot(1, 3, 1)
cs = ax.contour(X, Y, Itot, levels=[0.01, 0.03, 0.1, 0.3, 0.5, 0.8],
                colors='k', linewidths=0.8)
ax.clabel(cs, fmt='%.2g', fontsize=7)
ax.set_aspect('equal')
ax.set_xlabel('v_x (∥ polarization)'); ax.set_ylabel('v_y (⊥ polarization)')
ax.set_title('(a) focal spot, X_NA=1.2 — elliptical', fontsize=10)

ax = fig.add_subplot(1, 3, 2)
ax.plot(v_arr, tot_x / norm, 'k-', lw=1.4, label='total (x-cut)')
ax.plot(v_arr, Ex2_x / norm, 'C0--', lw=1.2, label='|E_x|²')
ax.plot(v_arr, Ez2_x / norm, 'C3-.', lw=1.2, label='|E_z|² (longitudinal)')
ax.set_yscale('log'); ax.set_ylim(1e-6, 1.5)
ax.set_xlabel('v along x'); ax.set_ylabel('normalized intensity')
ax.set_title('(b) X_NA=1.2: E_z fills the zeros along x', fontsize=10)
ax.legend(fontsize=8)

ax = fig.add_subplot(1, 3, 3)
ax.plot(XNA_vals, ratio, 'C1o-', ms=4, lw=1.1, label='FWHM_x / FWHM_y')
ax.set_xlabel('X_NA'); ax.set_ylabel('FWHM anisotropy ratio', color='C1')
ax.axhline(1.0, color='k', lw=0.6, ls=':')
ax2 = ax.twinx()
ax2.plot(XNA_vals, 100 * np.array(ez_share), 'C3s--', ms=4, lw=1.1,
         label='E_z energy share')
ax2.set_ylabel('E_z energy share along x-cut (%)', color='C3')
ax.set_title('(c) anisotropy tracks the E_z fraction', fontsize=10)
plt.tight_layout()
fig.savefig(os.path.join(OUT, 'check6_anisotropy.png'), dpi=150,
            bbox_inches='tight'); plt.close(fig)

print("saved checks 1-6 →", OUT)
