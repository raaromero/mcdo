r"""
Phase 6a — proof that the photon *initialization* is sampled correctly, in the
clear (no-scattering) limit. The scattering MC inherits this launcher unchanged,
so if the launch already reproduces the deterministic focal field, scattering
only removes/redirects photons from an already-correct starting ensemble.

A photon is a plane-wave (angular-spectrum) component of the converging field.
Its launch state is (direction k̂, azimuth φ, pupil phase). The aplanatic sine
condition maps the pupil radius to the cone angle, ρ = f·sinθ, so the launch
direction *is* the pupil location: ρ̂ = sinθ/sinα ∈ [0,1], φ preserved.

Two figures:

  verify_launcher.png           — the DISTRIBUTION proof:
     (1) direction θ ~ p(θ) ∝ |A(θ)|√cosθ sinθ (Debye-Wolf integrand); KS to the
         analytic CDF. (2) recovered input amplitude A(θ) (geometry divided out):
         flat / Gaussian. (3) azimuth φ uniform. (4) recovered radial input
         intensity |A(ρ̂)|²: flat disk vs Gaussian. (5,6) 2-D pupil maps.

  verify_launcher_intensity.png — the FIELD/INTENSITY proof:
     transverse & axial cuts (MC vs expected, both inputs) and the x–z field
     gates (MC heat map + deterministic Romallosa iso-contours), uniform & Gaussian.

NA=0.8, λ_c=750 nm, n=1.3.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter

from mcdo import SimConfig
from mcdo.debye import scalar_debye
from mcdo.montecarlo import sample_photons, coherent_intensity
from mcdo.apodization import gaussian

from mcdo.style import apply as _apply_style
_apply_style()

_TRAPZ = np.trapezoid if hasattr(np, 'trapezoid') else np.trapz

LAM, N_MED = 0.750, 1.3
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '06_monte_carlo')
cfg = SimConfig(lam_c=LAM, X_NA=0.8, n=N_MED, tau=np.inf, N_freq=3, N_theta=1201)

N_DIST = 400_000       # photons for the distribution checks (smooth histograms)
N_FIELD = 120_000      # photons for the field gates / cuts

CONFIGS = [('uniform', None), ('Gaussian, truncation coefficient 2', gaussian(2.0, cfg.sin2_alpha))]
COLOR = {'uniform': '#1f77b4', 'Gaussian, truncation coefficient 2': '#d62728'}
MARKER = {'uniform': 'o', 'Gaussian, truncation coefficient 2': 's'}


def amp(apod, th):
    """Pupil amplitude |A(θ)| (1 for uniform)."""
    return np.ones_like(th) if apod is None else np.abs(np.asarray(apod(th)))


def target_pdf(apod, th):
    """Debye-Wolf integrand density p(θ) ∝ |A(θ)|·√cosθ·sinθ."""
    return amp(apod, th) * np.sqrt(np.maximum(np.cos(th), 0.0)) * np.sin(th)


def ks_statistic(theta, apod, ngrid=4001):
    """KS distance between sampled θ and the target CDF."""
    th = np.linspace(0.0, cfg.alpha, ngrid)
    cdf = np.cumsum(target_pdf(apod, th)); cdf -= cdf[0]; cdf /= cdf[-1]
    s = np.sort(theta)
    return float(np.max(np.abs(np.arange(1, s.size + 1) / s.size
                                - np.interp(s, th, cdf))))


# ── sample once per config ──────────────────────────────────────────────────
samp = {}
for label, apod in CONFIGS:
    rng = np.random.default_rng(0)
    kx, ky, kz, w = sample_photons(cfg, N_DIST, apod=apod, rng=rng)
    theta = np.arccos(np.clip(kz / cfg.k_c, -1.0, 1.0))
    phi = np.mod(np.arctan2(ky, kx), 2 * np.pi)
    samp[label] = dict(theta=theta, phi=phi)

print("Launcher initialization checks (NA=0.8, λ=750 nm, n=1.3):\n")
print(f"{'config':<16} {'KS(θ)':>9} {'φ flatness':>11}")

th_fine = np.linspace(0, cfg.alpha, 600)
adeg = np.degrees(cfg.alpha)

# ═══ FIGURE 1 — distribution proof ══════════════════════════════════════════
fig = plt.figure(figsize=(21.6, 12.2))
gs = fig.add_gridspec(2, 3, hspace=0.36, wspace=0.30)
fig.suptitle('Photon initialization sampling, numerical aperture 0.8, 750 nm', fontsize=15, y=0.98)

ax_th = fig.add_subplot(gs[0, 0])
ax_A = fig.add_subplot(gs[0, 1])
ax_phi = fig.add_subplot(gs[0, 2])
ax_rad = fig.add_subplot(gs[1, 0])

for label, apod in CONFIGS:
    th = samp[label]['theta']; ph = samp[label]['phi']; c = COLOR[label]

    # (1) direction θ density vs target
    counts, edges = np.histogram(th, bins=70, range=(0, cfg.alpha), density=True)
    ctr = 0.5 * (edges[:-1] + edges[1:])
    tgt = target_pdf(apod, th_fine)
    tgt = tgt / _TRAPZ(tgt, th_fine)
    ax_th.plot(np.degrees(th_fine), tgt, '-', color=c, lw=2.2, zorder=2)
    ax_th.plot(np.degrees(ctr), counts, MARKER[label], ms=5, color=c, mfc='white',
               mew=1.3, label=f'{label}', zorder=3)
    ks = ks_statistic(th, apod)

    # (2) recovered input amplitude A(θ)
    geom = np.sqrt(np.cos(ctr)) * np.sin(ctr)
    A_rec = counts / geom
    valid = (ctr > 0.06 * cfg.alpha) & (ctr < 0.97 * cfg.alpha)
    A_rec = A_rec / np.nanmedian(A_rec[valid][:6])
    ax_A.plot(np.degrees(th_fine), amp(apod, th_fine), '-', color=c, lw=2.2)
    ax_A.plot(np.degrees(ctr[valid]), A_rec[valid], MARKER[label], ms=5, color=c,
              mfc='white', mew=1.3, label=label)

    # (3) azimuth φ uniformity — BOTH inputs are φ-uniform (symmetry is
    # independent of the radial A(θ)), so they overlap; distinct markers + a
    # small vertical offset keep both visible.
    pc, pe = np.histogram(ph, bins=48, range=(0, 2 * np.pi), density=True)
    pctr = 0.5 * (pe[:-1] + pe[1:])
    off = 0.012 if label == 'uniform' else -0.012
    ax_phi.plot(np.degrees(pctr), pc * 2 * np.pi + off, MARKER[label], ms=5,
                color=c, mfc='white', mew=1.2, alpha=0.85, label=label)
    phi_dev = float(np.max(np.abs(pc * 2 * np.pi - 1.0)))

    # (4) recovered radial input intensity |A(ρ̂)|² (areal density)
    rho = np.sin(th) / cfg.sin_alpha
    wgt = amp(apod, th) * np.sqrt(np.cos(th))      # → weighted areal density ∝ |A|²
    cw, re = np.histogram(rho, bins=60, range=(0, 1.0), weights=wgt)
    rc = 0.5 * (re[:-1] + re[1:])
    area = np.pi * (re[1:] ** 2 - re[:-1] ** 2)
    dens = cw / area; dens /= np.nanmedian(dens[2:8])
    ax_rad.plot(rc, amp(apod, np.arcsin(np.clip(rc * cfg.sin_alpha, 0, 1))) ** 2,
                '-', color=c, lw=2.2)
    ax_rad.plot(rc[rc > 0.04], dens[rc > 0.04], MARKER[label], ms=5, color=c,
                mfc='white', mew=1.2, label=label)

    print(f"{label:<16} {ks:>9.4f} {phi_dev:>11.3f}")

ax_th.axvline(adeg, color='gray', ls='--', lw=1.0)
ax_th.text(adeg - 0.6, ax_th.get_ylim()[1] * 0.55, f'Cone edge α={adeg:.0f}°',
           color='gray', fontsize=9, ha='right', rotation=90, va='center')
ax_th.set_xlabel('Launch angle θ (degrees)'); ax_th.set_ylabel('Probability density')
ax_th.set_title('(a) Launch direction, sampled against expected')
ax_th.legend(loc='upper left')

ax_A.set_ylim(-0.05, 1.15)
ax_A.set_xlabel('Launch angle θ (degrees)'); ax_A.set_ylabel('Recovered pupil amplitude')
ax_A.set_title('(b) Recovered pupil amplitude with the geometry divided out')
ax_A.legend(loc='lower left')

ax_phi.axhline(1.0, color='k', ls='--', lw=1.4, zorder=0, label='expected (uniform)')
ax_phi.set_ylim(0.7, 1.3)
ax_phi.set_xlabel('Azimuth φ (degrees)'); ax_phi.set_ylabel('Density relative to uniform')
ax_phi.set_title('(c) Azimuth density against the uniform expectation')
ax_phi.legend(loc='upper right', ncol=1)

ax_rad.set_ylim(-0.05, 1.15)
ax_rad.set_xlabel('Normalized pupil radius')
ax_rad.set_ylabel(r'Recovered input intensity $|A|^2$')
ax_rad.set_title('(d) Recovered radial intensity profile of the pupil')
ax_rad.legend(loc='lower left')

# (5,6) 2-D pupil maps — smoothed for legibility
def pupil_map(label, apod, nbins=80):
    th = samp[label]['theta']; ph = samp[label]['phi']
    rho = np.sin(th) / cfg.sin_alpha
    xp, yp = rho * np.cos(ph), rho * np.sin(ph)
    wgt = amp(apod, th) * np.sqrt(np.cos(th))
    H, xe, ye = np.histogram2d(xp, yp, bins=nbins,
                               range=[[-1.05, 1.05], [-1.05, 1.05]], weights=wgt)
    H = gaussian_filter(H.T, 1.6)
    mask = (np.add.outer(0.5 * (ye[:-1] + ye[1:]) ** 2,
                         0.5 * (xe[:-1] + xe[1:]) ** 2)) > 1.0
    H[mask] = np.nan
    H = H / np.nanmax(H)
    return 0.5 * (xe[:-1] + xe[1:]), 0.5 * (ye[:-1] + ye[1:]), H

for col, (label, apod) in enumerate(CONFIGS):
    ax = fig.add_subplot(gs[1, col + 1])
    xc, yc, H = pupil_map(label, apod)
    pm = ax.pcolormesh(xc, yc, H, cmap='magma', shading='auto', vmin=0, vmax=1)
    ax.contour(xc, yc, np.nan_to_num(H), levels=[0.2, 0.4, 0.6, 0.8],
               colors='cyan', linewidths=1.0, alpha=0.9)
    ax.add_patch(plt.Circle((0, 0), 1.0, fill=False, color='w', ls='--', lw=1.0))
    ax.set_aspect('equal'); ax.grid(False)
    ax.set_xlabel('x / ρ_max'); ax.set_ylabel('y / ρ_max')
    ax.set_title(f'Two-dimensional pupil map, {label}')
    fig.colorbar(pm, ax=ax, fraction=0.046, pad=0.04)

out = os.path.join(OUT, 'verify_launcher.png')
fig.savefig(out, bbox_inches='tight'); plt.close(fig)

# ═══ FIGURE 2 — field / intensity proof ═════════════════════════════════════
xr = np.linspace(-1.5, 1.5, 161)
zr = np.linspace(-4.0, 4.0, 201)
x = np.linspace(-1.2, 1.2, 121)
z = np.linspace(-4.0, 4.0, 161)
Z, X = np.meshgrid(z, x, indexing='ij'); Y = np.zeros_like(X)

fig2 = plt.figure(figsize=(17.6, 12.2))
gs2 = fig2.add_gridspec(2, 2, hspace=0.32, wspace=0.26)
fig2.suptitle('Intensity after MC launching matches the expected '
              'field (coherent clear limit)', fontsize=15, y=0.98)
axt = fig2.add_subplot(gs2[0, 0]); axa = fig2.add_subplot(gs2[0, 1])

gate_rms = {}
fields = {}
for label, apod in CONFIGS:
    c = COLOR[label]
    rng = np.random.default_rng(2)
    kx, ky, kz, w = sample_photons(cfg, N_FIELD, apod=apod, rng=rng)
    det_t = scalar_debye(np.abs(xr), np.array([0.0]), cfg.k_c, cfg.alpha,
                         cfg.N_theta, apodization=apod)[0]; det_t /= det_t.max()
    mc_t = coherent_intensity(kx, ky, kz, w, xr, np.zeros_like(xr),
                              np.zeros_like(xr)); mc_t /= mc_t.max()
    axt.semilogy(xr, det_t, '-', color=c, lw=2.0, label=f'{label} — expected')
    axt.semilogy(xr, mc_t, 'o', color=c, ms=3.2, mfc='none', mew=0.8, alpha=0.8)
    det_a = scalar_debye(np.array([0.0]), zr, cfg.k_c, cfg.alpha,
                         cfg.N_theta, apodization=apod)[:, 0]; det_a /= det_a.max()
    mc_a = coherent_intensity(kx, ky, kz, w, np.zeros_like(zr),
                              np.zeros_like(zr), zr); mc_a /= mc_a.max()
    axa.semilogy(zr, det_a, '-', color=c, lw=2.0, label=f'{label} — expected')
    axa.semilogy(zr, mc_a, 'o', color=c, ms=3.2, mfc='none', mew=0.8, alpha=0.8)

    det = scalar_debye(np.abs(x), z, cfg.k_c, cfg.alpha, cfg.N_theta,
                       apodization=apod); det /= det.max()
    rng = np.random.default_rng(1)
    kx, ky, kz, w = sample_photons(cfg, N_FIELD, apod=apod, rng=rng)
    I = coherent_intensity(kx, ky, kz, w, X, Y, Z); I /= I.max()
    gate_rms[label] = float(np.sqrt(np.mean((I - det) ** 2)))
    fields[label] = (det, I)

axt.set_ylim(1e-4, 2); axt.set_xlabel('x (µm)'); axt.set_ylabel('intensity (norm.)')
axt.set_title('Transverse cut at focus, Monte Carlo against expected'); axt.legend()
axa.set_ylim(1e-3, 2); axa.set_xlabel('z (µm)'); axa.set_ylabel('intensity (norm.)')
axa.set_title('Axial cut on axis, Monte Carlo against expected'); axa.legend()

for col, (label, apod) in enumerate(CONFIGS):
    ax = fig2.add_subplot(gs2[1, col])
    det, I = fields[label]
    pm = ax.pcolormesh(x, z, I, cmap='viridis', shading='auto', vmin=0, vmax=1)
    cs = ax.contour(x, z, det, levels=[0.02, 0.05, 0.1, 0.25, 0.5, 0.8],
                    colors='white', linewidths=1.0)
    ax.clabel(cs, fmt='%.2f', fontsize=7, inline=True)
    ax.grid(False); ax.set_xlabel('x (µm)'); ax.set_ylabel('z (µm)')
    ax.set_title(f'Monte Carlo focal map with expected contours, {label}')
    ax.text(0.04, 0.96, f"RMS = {gate_rms[label]:.4f}", transform=ax.transAxes,
            va='top', color='w', fontsize=11,
            bbox=dict(facecolor='k', alpha=0.55, boxstyle='round'))
    fig2.colorbar(pm, ax=ax, fraction=0.046, pad=0.04)

out2 = os.path.join(OUT, 'verify_launcher_intensity.png')
fig2.savefig(out2, bbox_inches='tight'); plt.close(fig2)

print("\nend-to-end field gate (coherent MC vs deterministic Debye, x–z slice):")
for label in gate_rms:
    print(f"  {label:<16} RMS = {gate_rms[label]:.4f}")
print(f"\nSaved → {out}\n      → {out2}")
