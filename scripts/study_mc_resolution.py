"""
MC sampling study — what voxel size (dx,dy,dz) and photon count N are needed?
Uses the validated clear-limit coherent MC (Phase 6a). Two independent
requirements:

  (A) N_photons  — statistical: RMS(MC − deterministic) and the null floor vs N.
      Expect RMS ∝ 1/√N and null floor ∝ 1/N (random-walk residual at zeros).
  (B) voxel size — representational (Nyquist): the field's max spatial freqs are
      k·sinα (transverse) and k·(1−cosα) (axial), so to resolve the *intensity*
      (twice the field freq) dx ≲ λ/(4·NA), dz ≲ λ/(4n(1−cosα)). Shown by the
      error in recovered FWHM / first-zero vs dx (deterministic — no MC noise).

Run for uniform, Gaussian α_t=2, annular ε=0.9 (NA=0.8, scalar). Output:
output/06_monte_carlo/study_resolution.png + printed recommendations.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo import SimConfig
from mcdo.debye import scalar_debye
from mcdo.montecarlo import sample_photons, coherent_intensity
from mcdo.apodization import gaussian

LAM, N_MED = 0.750, 1.3
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '06_monte_carlo')
rng = np.random.default_rng(0)
cfg = SimConfig(lam_c=LAM, X_NA=0.8, n=N_MED, tau=np.inf, N_freq=3, N_theta=1201)
theta_in = np.arcsin(0.9 * cfg.sin_alpha)
CONFIGS = [('uniform', None),
           ('Gaussian α_t=2', gaussian(2.0, cfg.sin2_alpha)),
           ('annular ε=0.9', (lambda th: (np.asarray(th) >= theta_in).astype(float)))]

# ── (A) N-photon convergence on an x–z slice ───────────────────────────────
dx = LAM / (8 * cfg.X_NA)
dz = LAM / (8 * cfg.n * (1 - np.cos(cfg.alpha)))
x = np.arange(-1.2, 1.2 + dx, dx)
z = np.arange(-4.0, 4.0 + dz, dz)
Z, X = np.meshgrid(z, x, indexing='ij')
Y = np.zeros_like(X)
Ns = [1000, 3000, 10000, 30000, 100000, 300000]

print(f"voxel (¼-Nyquist): dx=dy={dx*1e3:.0f} nm, dz={dz*1e3:.0f} nm")
print("\n(A) N-photon convergence (RMS vs deterministic, null floor):")
rms = {k: [] for k, _ in CONFIGS}
floor = {k: [] for k, _ in CONFIGS}
for label, apod in CONFIGS:
    ref = scalar_debye(np.abs(x), z, cfg.k_c, cfg.alpha, cfg.N_theta, apodization=apod)
    ref /= ref.max()
    nullmask = ref < 1e-3
    for N in Ns:
        kx, ky, kz, w = sample_photons(cfg, N, apod=apod, rng=rng)
        I = coherent_intensity(kx, ky, kz, w, X, Y, Z); I /= I.max()
        rms[label].append(np.sqrt(np.mean((I - ref) ** 2)))
        floor[label].append(I[nullmask].mean() if nullmask.any() else np.nan)
    # N for RMS≈1%
    r = np.array(rms[label])
    iN = np.argmax(r < 0.01) if (r < 0.01).any() else -1
    nrec = Ns[iN] if iN >= 0 else '>3e5'
    print(f"  {label:<16} RMS {r[0]:.3f}→{r[-1]:.4f};  N for 1% ≈ {nrec}")

# ── (B) voxel-size / Nyquist (deterministic FWHM & first-zero vs dx) ────────
print("\n(B) transverse resolution — recovered FWHM/zero vs dx (deterministic):")
nyq_int = LAM / (4 * cfg.X_NA)   # ¼-period intensity-Nyquist target
print(f"  intensity-Nyquist target dx ≈ λ/(4·NA) = {nyq_int*1e3:.0f} nm")
dx_mults = [0.5, 1.0, 2.0, 4.0, 8.0]   # dx = (λ/2NA)/m  → m large = fine
res = {}
for label, apod in CONFIGS:
    fwhms = []
    for m in dx_mults:
        d = (LAM / (2 * cfg.X_NA)) / m
        xr = np.arange(0, 1.5 + d, d)
        I = scalar_debye(xr, np.array([0.0]), cfg.k_c, cfg.alpha, cfg.N_theta, apodization=apod)[0]
        I /= I.max()
        half = 0.5
        i = np.argmax(I < half)
        fw = 2 * np.interp(half, [I[i], I[i-1]], [xr[i], xr[i-1]]) if i > 0 else np.nan
        fwhms.append(fw * 1e3)
    res[label] = fwhms
    print(f"  {label:<16} FWHM(nm) vs dx-mult {dx_mults}: "
          f"{['%.0f' % f for f in fwhms]}")

# ── Figure ─────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(14, 4.4))
fig.suptitle('MC sampling study — photon count N and voxel size (NA=0.8, scalar)',
             fontsize=12)
ax = axes[0]
for label, _ in CONFIGS:
    ax.loglog(Ns, rms[label], 'o-', ms=4, label=label)
ax.loglog(Ns, 0.4 * np.array(Ns, float) ** -0.5, 'k:', lw=1, label='∝ N^(−1/2)')
ax.axhline(0.01, color='gray', lw=0.6, ls='--')
ax.set_xlabel('N photons'); ax.set_ylabel('RMS vs deterministic')
ax.set_title('(A) accuracy vs N', fontsize=10); ax.legend(fontsize=7)

ax = axes[1]
for label, _ in CONFIGS:
    ax.loglog(Ns, floor[label], 's-', ms=4, label=label)
ax.loglog(Ns, 5 * np.array(Ns, float) ** -1.0, 'k:', lw=1, label='∝ 1/N')
ax.set_xlabel('N photons'); ax.set_ylabel('null floor (zeros fill to)')
ax.set_title('(B) zero-depth floor vs N', fontsize=10); ax.legend(fontsize=7)

ax = axes[2]
dxs = [(LAM / (2 * cfg.X_NA)) / m * 1e3 for m in dx_mults]
for label, _ in CONFIGS:
    ax.plot(dxs, res[label], 'o-', ms=4, label=label)
ax.axvline(nyq_int * 1e3, color='r', lw=0.8, ls=':')
ax.annotate('λ/4NA', (nyq_int * 1e3, ax.get_ylim()[1]), fontsize=8, color='r')
ax.set_xlabel('voxel dx (nm)'); ax.set_ylabel('recovered FWHM (nm)')
ax.set_title('(C) FWHM error vs voxel size', fontsize=10); ax.legend(fontsize=7)

plt.tight_layout()
out = os.path.join(OUT, 'study_resolution.png')
fig.savefig(out, dpi=150, bbox_inches='tight'); plt.close(fig)
print(f"\nSaved → {out}")
