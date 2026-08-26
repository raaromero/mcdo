r"""
Multi-trial data for every Monte-Carlo experiment (the project standard: ≥10
independent seeds, per-trial data saved with mean ± SD). Even in the clear
(no-scattering) limit each result is now a statistic, not a single run — and the
saved ``.npz`` makes it reproducible and gives the error bar that the scattering
runs will rely on.

Covers: clear-limit field, per-configuration RMS, vector RMS (both cuts),
launcher distribution metrics (KS, φ-flatness), and the pulsed wavelength MC.
K=10 trials each. Output: output/06_monte_carlo/trials/*.npz + a summary table.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np

from mcdo import SimConfig
from mcdo.debye import scalar_debye
from mcdo.rw_integrals import compute_integrals
from mcdo.montecarlo import (sample_photons, coherent_intensity,
                             sample_photons_vector, coherent_intensity_vector,
                             mc_pulsed_intensity)
from mcdo.apodization import gaussian, axicon
from mcdo.trials import run_trials, save_trials, summarize

K = 10
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '06_monte_carlo', 'trials')
cfg = SimConfig(lam_c=0.750, X_NA=0.8, n=1.3, N_theta=801)
x = np.linspace(-1.2, 1.2, 51)
z = np.linspace(-3.0, 3.0, 51)
Z, X = np.meshgrid(z, x, indexing='ij'); Y = np.zeros_like(X)
rows = []   # (experiment, metric, mean, std) for the summary table


def annular_apod(eps):
    th_in = np.arcsin(eps * cfg.sin_alpha)
    return lambda th: (np.asarray(th, float) >= th_in).astype(float)


# ── 1. clear-limit field (NA=0.8, uniform, N=30k) — save the field trials ───
ref = scalar_debye(np.abs(x), z, cfg.k_c, cfg.alpha, cfg.N_theta); ref /= ref.max()

def f_field(rng):
    kx, ky, kz, w = sample_photons(cfg, 30000, rng=rng)
    I = coherent_intensity(kx, ky, kz, w, X, Y, Z); return I / I.max()

fields, seeds = run_trials(f_field, K)
rms_field = np.sqrt(((fields - ref) ** 2).mean(axis=(1, 2)))
save_trials(os.path.join(OUT, 'clear_field_NA08.npz'), fields, seeds,
            ref=ref, x=x, z=z, N=30000, rms=rms_field, label='clear field NA=0.8')
rows.append(('clear field NA=0.8', 'RMS vs deterministic', rms_field.mean(), rms_field.std(ddof=1)))

# ── 2. per-configuration RMS (N=30k) ────────────────────────────────────────
CONFIGS = [('uniform', None),
           ('gaussian_at2', gaussian(2.0, cfg.sin2_alpha)),
           ('annular_eps0.9', annular_apod(0.9)),
           ('axicon_b20', axicon(20.0, cfg.sin_alpha))]
for name, apod in CONFIGS:
    r = scalar_debye(np.abs(x), z, cfg.k_c, cfg.alpha, cfg.N_theta, apodization=apod)
    r = r / r.max()
    def f_rms(rng, apod=apod, r=r):
        kx, ky, kz, w = sample_photons(cfg, 30000, apod=apod, rng=rng)
        I = coherent_intensity(kx, ky, kz, w, X, Y, Z); I /= I.max()
        return np.sqrt(np.mean((I - r) ** 2))
    tr, seeds = run_trials(f_rms, K)
    save_trials(os.path.join(OUT, f'config_{name}.npz'), tr, seeds, label=name, N=30000)
    rows.append((f'config {name}', 'RMS', tr.mean(), tr.std(ddof=1)))

# ── 3. vector RMS, both RW cuts (N=50k) ─────────────────────────────────────
s = np.linspace(-1.0, 1.0, 41); zc = np.linspace(-3.0, 3.0, 41)
Zc, S = np.meshgrid(zc, s, indexing='ij'); O = np.zeros_like(S)
I0, I1, I2 = compute_integrals(np.abs(s), zc, cfg.k_c, cfg.alpha, cfg.N_theta)
det_y = np.abs(I0 - I2) ** 2; det_y /= det_y.max()
det_x = np.abs(I0 + I2) ** 2 + 4 * np.abs(I1) ** 2; det_x /= det_x.max()

def f_vec(rng):
    kx, ky, kz, wv = sample_photons_vector(cfg, 50000, rng=rng)
    my = coherent_intensity_vector(kx, ky, kz, wv, O, S, Zc); my /= my.max()
    mx = coherent_intensity_vector(kx, ky, kz, wv, S, O, Zc); mx /= mx.max()
    return np.array([np.sqrt(np.mean((my - det_y) ** 2)),
                     np.sqrt(np.mean((mx - det_x) ** 2))])

vtr, seeds = run_trials(f_vec, K)
save_trials(os.path.join(OUT, 'vector_rms.npz'), vtr, seeds,
            cuts=np.array(['y |I0-I2|^2', 'x |I0+I2|^2+4|I1|^2']), N=50000)
m, sd, _ = summarize(vtr)
rows.append(('vector y-cut', 'RMS', m[0], sd[0]))
rows.append(('vector x-cut', 'RMS', m[1], sd[1]))

# ── 4. launcher distribution metrics (N=100k) ───────────────────────────────
def ks_stat(theta, apod):
    th = np.linspace(0, cfg.alpha, 4001)
    A = np.ones_like(th) if apod is None else np.abs(apod(th))
    cdf = np.cumsum(A * np.sqrt(np.cos(th)) * np.sin(th)); cdf -= cdf[0]; cdf /= cdf[-1]
    si = np.sort(theta)
    return float(np.max(np.abs(np.arange(1, si.size + 1) / si.size - np.interp(si, th, cdf))))

gA = gaussian(2.0, cfg.sin2_alpha)
def f_launch(rng):
    kx, ky, kz, w = sample_photons(cfg, 100000, rng=rng)
    th = np.arccos(np.clip(kz / cfg.k_c, -1, 1)); ph = np.mod(np.arctan2(ky, kx), 2 * np.pi)
    c, _ = np.histogram(ph, 36, (0, 2 * np.pi))
    ksu = ks_stat(th, None); phiflat = float(np.max(np.abs(c / c.mean() - 1)))
    kxg, kyg, kzg, wg = sample_photons(cfg, 100000, apod=gA, rng=rng)
    ksg = ks_stat(np.arccos(np.clip(kzg / cfg.k_c, -1, 1)), gA)
    return np.array([ksu, ksg, phiflat])

ltr, seeds = run_trials(f_launch, K)
save_trials(os.path.join(OUT, 'launcher_metrics.npz'), ltr, seeds,
            metrics=np.array(['KS_uniform', 'KS_gauss', 'phi_flatness']), N=100000)
m, sd, _ = summarize(ltr)
for i, nm in enumerate(['KS θ (uniform)', 'KS θ (Gaussian)', 'φ flatness']):
    rows.append(('launcher', nm, m[i], sd[i]))

# ── 5. pulsed wavelength MC RMS vs deterministic Eq.10 (τ=2 fs, N=100k) ──────
cfgp = SimConfig(lam_c=0.750, X_NA=0.8, n=1.3, tau=2e-15, N_freq=41, N_theta=801)
xr = np.linspace(-1.5, 1.5, 121)
oms = cfgp.omega_grid(); W = np.where(oms > 0, cfgp.spectral_power(oms), 0.0)
det_p = np.zeros_like(xr)
for om, w in zip(oms, W):
    if w:
        det_p += w * scalar_debye(np.abs(xr), np.array([0.0]), cfgp.k_for_omega(om),
                                  cfgp.alpha, cfgp.N_theta)[0]
det_p /= det_p.max()
def f_pulsed(rng):
    mc = mc_pulsed_intensity(cfgp, xr, np.zeros_like(xr), np.zeros_like(xr), 100000, rng=rng)
    return np.sqrt(np.mean((mc - det_p) ** 2))
ptr, seeds = run_trials(f_pulsed, K)
save_trials(os.path.join(OUT, 'pulsed_rms.npz'), ptr, seeds, tau_fs=2, N=100000)
rows.append(('pulsed λ-MC (τ=2fs)', 'RMS vs Eq.10', ptr.mean(), ptr.std(ddof=1)))

# ── summary ─────────────────────────────────────────────────────────────────
print(f"\nMulti-trial Monte-Carlo summary (K={K} seeds each; saved to {OUT}/):\n")
print(f"{'experiment':<24}{'metric':<22}{'mean':>11}{'std':>11}")
print('-' * 68)
for exp, met, mean, std in rows:
    print(f"{exp:<24}{met:<22}{mean:>11.5f}{std:>11.5f}")
print(f"\n{len(rows)} metrics; per-trial arrays + mean/std/sem/seeds in each .npz.")
