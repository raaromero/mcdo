"""
Phase 6a completion — sampling requirements for the clear-limit MC:
how many photons N, and what voxel sizes (dx, dy, dz), are sufficient?

Two independent requirements (they don't trade off):

  (A) SUFFICIENT N (statistical).  RMS(MC − deterministic) and the null floor
      vs N, per configuration. The null floor (depth the true zeros fill to)
      ∝ 1/N; the RMS ∝ 1/√N. We report the N that reaches 1% and 0.5% RMS —
      "when the MC approximates the expected (deterministic) result".

  (B) VOXEL SIZE (representational / Nyquist).  The field's highest spatial
      frequencies are k·sinα (transverse) and k·(1−cosα) (axial). Resolving the
      *intensity* (twice the field frequency) needs
          dx, dy ≤ λ/(4·NA),        dz ≤ λ/(4·n·(1−cosα)).
      Shown by the error in the recovered FWHM and first-zero position vs voxel
      size (deterministic — no MC noise), separately for the transverse (dx=dy)
      and axial (dz) directions.

NA=0.8, λ_c=750 nm, n=1.3, scalar field (the sampling requirement is set by the
field's spatial frequencies, identical for scalar and vector). Output:
output/06_monte_carlo/study_sampling.png + a printed recommendations table.
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
from mcdo.apodization import gaussian, axicon

LAM, N_MED = 0.750, 1.3
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '06_monte_carlo')
cfg = SimConfig(lam_c=LAM, X_NA=0.8, n=N_MED, tau=np.inf, N_freq=3, N_theta=1201)
rng = np.random.default_rng(0)

th_in = np.arcsin(0.9 * cfg.sin_alpha)
CONFIGS = [
    ('uniform', None),
    ('Gaussian α_t=2', gaussian(2.0, cfg.sin2_alpha)),
    ('annular ε=0.9', lambda th: (np.asarray(th) >= th_in).astype(float)),
    ('axicon β=20', axicon(20.0, cfg.sin_alpha)),
]

# Nyquist-derived voxel targets
dx_int = LAM / (4 * cfg.X_NA)                       # transverse intensity-Nyquist
dz_int = LAM / (4 * cfg.n * (1 - np.cos(cfg.alpha)))  # axial intensity-Nyquist
print("Nyquist voxel targets (intensity):")
print(f"  transverse dx=dy ≤ λ/(4NA)           = {dx_int*1e3:.0f} nm")
print(f"  axial      dz    ≤ λ/(4n(1−cosα))    = {dz_int*1e3:.0f} nm")

# ── (A) sufficient N ───────────────────────────────────────────────────────
dx = LAM / (8 * cfg.X_NA)
dz = LAM / (8 * cfg.n * (1 - np.cos(cfg.alpha)))
x = np.arange(-1.2, 1.2 + dx, dx)
z = np.arange(-4.0, 4.0 + dz, dz)
Z, X = np.meshgrid(z, x, indexing='ij'); Y = np.zeros_like(X)
Ns = np.array([1000, 3000, 10000, 30000, 100000, 300000])

print("\n(A) sufficient N — RMS(MC−deterministic); N for 1% / 0.5%:")
rms_all, floor_all = {}, {}
for label, apod in CONFIGS:
    ref = scalar_debye(np.abs(x), z, cfg.k_c, cfg.alpha, cfg.N_theta, apodization=apod)
    ref /= ref.max()
    nullmask = ref < 1e-3
    rms, floor = [], []
    for N in Ns:
        kx, ky, kz, w = sample_photons(cfg, int(N), apod=apod, rng=rng)
        I = coherent_intensity(kx, ky, kz, w, X, Y, Z); I /= I.max()
        rms.append(np.sqrt(np.mean((I - ref) ** 2)))
        floor.append(I[nullmask].mean() if nullmask.any() else np.nan)
    rms_all[label] = np.array(rms); floor_all[label] = np.array(floor)
    r = np.array(rms)
    n1 = int(Ns[np.argmax(r < 0.01)]) if (r < 0.01).any() else None
    n05 = int(Ns[np.argmax(r < 0.005)]) if (r < 0.005).any() else None
    print(f"  {label:<16} N(1%)≈{n1}, N(0.5%)≈{n05}")

# ── (B) transverse resolution (dx=dy): FWHM & first-zero vs dx ─────────────
def transverse_metrics(apod, d):
    xr = np.arange(0, 1.6 + d, d)
    I = scalar_debye(xr, np.array([0.0]), cfg.k_c, cfg.alpha, cfg.N_theta, apodization=apod)[0]
    I /= I.max()
    i = np.argmax(I < 0.5)
    fw = 2 * np.interp(0.5, [I[i], I[i-1]], [xr[i], xr[i-1]]) if i > 0 else np.nan
    # first interior minimum (zero ring) position
    mins = np.where((I[1:-1] < I[:-2]) & (I[1:-1] <= I[2:]))[0] + 1
    vz = xr[mins[0]] if mins.size else np.nan
    return fw * 1e3, vz * 1e3

def axial_metrics(apod, d):
    zr = np.arange(-6, 6 + d, d)
    I = scalar_debye(np.array([0.0]), zr, cfg.k_c, cfg.alpha, cfg.N_theta, apodization=apod)[:, 0]
    I /= I.max()
    above = I >= 0.5
    idx = np.where(np.diff(above.astype(int)))[0]
    if len(idx) >= 2:
        lo = np.interp(0.5, [I[idx[0]], I[idx[0]+1]], [zr[idx[0]], zr[idx[0]+1]])
        hi = np.interp(0.5, [I[idx[-1]+1], I[idx[-1]]], [zr[idx[-1]+1], zr[idx[-1]]])
        fw = hi - lo
    else:
        fw = np.nan
    return fw * 1e3

dx_list = np.array([dx_int*m for m in (2.0, 1.5, 1.0, 0.75, 0.5, 0.25)])  # nm-ish
print("\n(B) transverse FWHM (nm) vs dx (uniform); converged ~", end=" ")
fw_dx = {lab: [transverse_metrics(ap, d)[0] for d in dx_list] for lab, ap in CONFIGS}
print(f"{fw_dx['uniform'][-1]:.0f}")
dz_list = np.array([dz_int*m for m in (2.0, 1.5, 1.0, 0.75, 0.5, 0.25)])
fw_dz = {lab: [axial_metrics(ap, d) for d in dz_list] for lab, ap in CONFIGS}

# ── Figure ─────────────────────────────────────────────────────────────────
plt.rcParams.update({'font.size': 12, 'axes.titlesize': 13, 'axes.labelsize': 11,
                     'legend.fontsize': 9, 'xtick.labelsize': 10,
                     'ytick.labelsize': 10, 'axes.grid': True, 'grid.alpha': 0.25})
fig, axes = plt.subplots(1, 3, figsize=(16, 4.8))
fig.suptitle('Sufficient N and voxel size '
             '(NA=0.8, λ=750 nm, n=1.3)', fontsize=14)
ax = axes[0]
for lab in rms_all:
    ax.loglog(Ns, rms_all[lab], 'o-', ms=5, lw=1.6, label=lab)
ax.loglog(Ns, 0.5*Ns**-0.5, 'k:', lw=1.3, label='∝ N^(−1/2)')
ax.axhline(0.01, color='gray', ls='--', lw=0.8)
ax.text(Ns[0], 0.0105, '1% RMS', color='gray', fontsize=8, va='bottom')
ax.axhline(0.005, color='gray', ls=':', lw=0.8)
ax.set_xlabel('N photons'); ax.set_ylabel('RMS vs deterministic field')
ax.set_title('(A) sufficient N: accuracy vs N'); ax.legend()

# normalised FWHM (each config ÷ its finest-voxel value) so all configs share
# one scale — the message is "flat below the Nyquist voxel, degrades above".
ax = axes[1]
for lab in fw_dx:
    f = np.array(fw_dx[lab]); ax.plot(dx_list*1e3, f/f[-1], 'o-', ms=5, lw=1.6, label=lab)
ax.axvline(dx_int*1e3, color='r', ls='--', lw=1.2)
ax.text(dx_int*1e3-6, 1.18, 'λ/4NA\n(234 nm)', color='r', fontsize=9, ha='right', va='top')
ax.axhline(1.0, color='k', lw=0.6); ax.set_ylim(0.6, 1.3)
ax.set_xlabel('voxel  dx = dy  (nm)'); ax.set_ylabel('FWHM / converged value')
ax.set_title('(B) transverse resolution'); ax.legend()

ax = axes[2]
for lab in fw_dz:
    f = np.array(fw_dz[lab]); ax.plot(dz_list*1e3, f/f[-1], 'o-', ms=5, lw=1.6, label=lab)
ax.axvline(dz_int*1e3, color='r', ls='--', lw=1.2)
ax.text(dz_int*1e3-18, 1.18, 'λ/4n(1−cosα)\n(681 nm)', color='r', fontsize=9, ha='right', va='top')
ax.axhline(1.0, color='k', lw=0.6); ax.set_ylim(0.6, 1.3)
ax.set_xlabel('voxel  dz  (nm)'); ax.set_ylabel('FWHM / converged value')
ax.set_title('(C) axial resolution'); ax.legend()

plt.tight_layout()
out = os.path.join(OUT, 'study_sampling.png')
fig.savefig(out, dpi=300, bbox_inches='tight'); plt.close(fig)

print("\n" + "=" * 64)
print("RECOMMENDATIONS (NA=0.8, λ=750 nm, n=1.3):")
print(f"  voxel:  dx = dy ≤ {dx_int*1e3:.0f} nm (λ/4NA); {dx_int*1e3/2:.0f} nm safe")
print(f"          dz      ≤ {dz_int*1e3:.0f} nm (λ/4n(1−cosα)); {dz_int*1e3/2:.0f} nm safe")
print("  photons: ~3×10³ (1% RMS) to ~3×10⁴ (0.5%, clean zeros) per slice;")
print("           scale ∝ grid volume for full 3-D.")
print("=" * 64)
print(f"Saved → {out}")
