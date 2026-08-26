"""Focal plane intensity for a Gaussian input, at low and at high numerical
aperture, against the scalar Debye result.

For each numerical aperture two panels are produced:
  profile — transverse intensity for the Gaussian vector field, the Gaussian
            scalar field, and the uniform vector field, with the Airy radius
            marked
  contour — iso-intensity contours in the r-z plane, with the Airy radius marked

At numerical aperture 0.1 the vector and scalar curves coincide, which validates
the apodized implementation. At 0.9 they separate, because the longitudinal
component is absent from the scalar theory.

Airy radius: r = 0.61 lambda / NA.

Output: output/02_na_apodization/fig_focal_plane_gaussian.png (+ panels/)
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
from mcdo.rw_integrals import compute_integrals
from mcdo.apodization import gaussian
from mcdo.debye import scalar_debye
from mcdo.components import full as vec_intensity
from mcdo.figio import save_panels, mark_focus

LAM, N_MED, NT = 0.750, 1.3, 801
ALPHA_T = 4.0
NA_CASES = [0.1, 0.9]
LEVELS = [0.01, 0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90]
OUTDIR = os.path.join(os.path.dirname(__file__), '..', 'output', '02_na_apodization')

fig, axes = plt.subplots(2, 3, figsize=(30.8, 13.0))

for row, xna in enumerate(NA_CASES):
    cfg = SimConfig(lam_c=LAM, X_NA=xna, n=N_MED, tau=np.inf, N_freq=3, N_theta=NT)
    apod = gaussian(ALPHA_T, cfg.sin2_alpha)
    airy_r = 0.61 * LAM / xna                        # micrometres

    # ── transverse profile ────────────────────────────────────────────────
    r_half = np.linspace(0.0, 3.0 * airy_r, 500)
    z0 = np.array([0.0])
    I0, I1, I2 = compute_integrals(r_half, z0, cfg.k_c, cfg.alpha, NT, apodization=apod)
    g_vec = vec_intensity(I0[0], I1[0], I2[0])
    g_sca = scalar_debye(r_half, z0, cfg.k_c, cfg.alpha, NT, apodization=apod)[0]
    U0, U1, U2 = compute_integrals(r_half, z0, cfg.k_c, cfg.alpha, NT)
    u_vec = vec_intensity(U0[0], U1[0], U2[0])
    rr = np.concatenate([-r_half[::-1], r_half[1:]])

    def mirror(y):
        y = y / y.max()
        return np.concatenate([y[::-1], y[1:]])

    ax = axes[row, 0]
    ax.plot(rr, mirror(g_vec), '-', color='#1f77b4', lw=2.0, label='Richards-Wolf, Gaussian')
    ax.plot(rr, mirror(g_sca), '--', color='#c0504d', lw=2.0, label='Debye, Gaussian')
    ax.plot(rr, mirror(u_vec), ':', color='#2ca02c', lw=2.0, label='Richards-Wolf, uniform')
    for x in (-airy_r, airy_r):
        ax.axvline(x, color='#888', ls=':', lw=1.2)
    ax.axhline(0.5, color='#bbb', ls='--', lw=1.2)
    ax.set_xlim(rr[0], rr[-1]); ax.set_ylim(0, 1.05)
    ax.set_xlabel('Radial position r (μm)')
    ax.set_ylabel('Normalized intensity')
    ax.set_title(f'Focal plane, numerical aperture {xna:g}, truncation coefficient {int(ALPHA_T)}, 750 nm',
                 fontsize=11)
    ax.grid(alpha=0.25)
    ax.legend(fontsize=9)

    dev = 100 * abs(np.trapezoid(np.abs(g_vec / g_vec.max() - g_sca / g_sca.max()), r_half)
                    / np.trapezoid(g_sca / g_sca.max(), r_half))
    print(f'NA {xna:g}: Airy radius {airy_r * 1000:.0f} nm, '
          f'vector against scalar area difference {dev:.2f} per cent')

    # ── axial profile ─────────────────────────────────────────────────────
    z_span_ax = 4.0 * LAM / (xna ** 2)
    z_line = np.linspace(0.0, z_span_ax, 500)
    A0, A1, A2 = compute_integrals(np.array([0.0]), z_line, cfg.k_c, cfg.alpha, NT,
                                   apodization=apod)
    g_ax = vec_intensity(A0[:, 0], A1[:, 0], A2[:, 0])
    s_ax = scalar_debye(np.array([0.0]), z_line, cfg.k_c, cfg.alpha, NT,
                        apodization=apod)[:, 0]
    U0a, U1a, U2a = compute_integrals(np.array([0.0]), z_line, cfg.k_c, cfg.alpha, NT)
    u_ax = vec_intensity(U0a[:, 0], U1a[:, 0], U2a[:, 0])
    zz = np.concatenate([-z_line[::-1], z_line[1:]])
    ax = axes[row, 1]
    ax.plot(zz, mirror(g_ax), '-', color='#1f77b4', lw=2.4, label='Richards-Wolf, Gaussian')
    ax.plot(zz, mirror(s_ax), '--', color='#c0504d', lw=2.0, label='Debye, Gaussian')
    ax.plot(zz, mirror(u_ax), ':', color='#2ca02c', lw=2.0, label='Richards-Wolf, uniform')
    ax.axhline(0.5, color='#bbb', ls='--', lw=1.2)
    ax.set_xlim(zz[0], zz[-1]); ax.set_ylim(0, 1.05)
    ax.set_xlabel('Axial position z (μm)')
    ax.set_ylabel('Normalized intensity')
    ax.set_title(f'Axial profile, numerical aperture {xna:g}, 750 nm', fontsize=11)
    ax.grid(alpha=0.25)
    ax.legend(fontsize=9)

    # ── r-z contour map ───────────────────────────────────────────────────
    z_span = 4.0 * LAM / (xna ** 2)
    z_arr = np.linspace(-z_span, z_span, 260)
    r_map = np.linspace(0.0, 2.0 * airy_r, 160)
    M0, M1, M2 = compute_integrals(r_map, z_arr, cfg.k_c, cfg.alpha, 401, apodization=apod)
    I = vec_intensity(M0, M1, M2)
    I = I / I.max()
    r_full = np.concatenate([-r_map[::-1], r_map[1:]])
    I_full = np.concatenate([I[:, ::-1], I[:, 1:]], axis=1)

    ax = axes[row, 2]
    cs = ax.contour(r_full, z_arr, I_full, levels=LEVELS, colors='k', linewidths=0.9)
    ax.clabel(cs, inline=True, fontsize=7, fmt='%.2f')
    mark_focus(ax, r_full, z_arr, I_full, airy_um=airy_r)
    ax.set_xlabel('Radial position r (μm)')
    ax.set_ylabel('Axial position z (μm)')
    ax.set_title(f'Iso-intensity contours, numerical aperture {xna:g}, '
                 f'Airy radius {airy_r:.3f} μm', fontsize=11)
    ax.grid(alpha=0.2)

plt.tight_layout()
save_panels(fig, fig.axes, os.path.join(OUTDIR, 'panels'), 'fig_focal_plane_gaussian')
out = os.path.join(OUTDIR, 'fig_focal_plane_gaussian.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f'Saved → {out}')
