"""Monte-Carlo tests tied to fundamental results.

The clear-limit MC must reproduce the deterministic field (the validation
gate), the vector MC must match both Richards-Wolf cuts, and the parallel path
must be identical to serial.
"""

import numpy as np

from mcdo import SimConfig
from mcdo.rw_integrals import compute_integrals
from mcdo.debye import scalar_debye
from mcdo.montecarlo import (sample_photons, coherent_intensity,
                             coherent_intensity_parallel,
                             sample_photons_vector, coherent_intensity_vector,
                             mc_pulsed_intensity, mc_focal_intensity)
from mcdo.apodization import gaussian

LAM, N_MED = 0.750, 1.3


def test_clear_limit_matches_scalar_debye():
    """μ_s=0 coherent MC converges to the scalar Debye field (the gate)."""
    cfg = SimConfig(lam_c=LAM, X_NA=0.8, n=N_MED, N_theta=801)
    rng = np.random.default_rng(0)
    x = np.linspace(-1.0, 1.0, 41); z = np.linspace(-3, 3, 41)
    Z, X = np.meshgrid(z, x, indexing="ij"); Y = np.zeros_like(X)
    ref = scalar_debye(np.abs(x), z, cfg.k_c, cfg.alpha, 801); ref /= ref.max()
    kx, ky, kz, w = sample_photons(cfg, 30000, rng=rng)
    I = coherent_intensity(kx, ky, kz, w, X, Y, Z); I /= I.max()
    assert np.sqrt(np.mean((I - ref) ** 2)) < 0.02


def test_mc_converges_with_N():
    """RMS vs the deterministic field decreases as N grows (∝ 1/√N trend)."""
    cfg = SimConfig(lam_c=LAM, X_NA=0.8, n=N_MED, N_theta=801)
    x = np.linspace(-1.0, 1.0, 41); z = np.linspace(-3, 3, 41)
    Z, X = np.meshgrid(z, x, indexing="ij"); Y = np.zeros_like(X)
    ref = scalar_debye(np.abs(x), z, cfg.k_c, cfg.alpha, 801); ref /= ref.max()
    rms = []
    for N in (3000, 30000):
        rng = np.random.default_rng(1)
        kx, ky, kz, w = sample_photons(cfg, N, rng=rng)
        I = coherent_intensity(kx, ky, kz, w, X, Y, Z); I /= I.max()
        rms.append(np.sqrt(np.mean((I - ref) ** 2)))
    assert rms[1] < rms[0]


def test_sufficient_N_reaches_one_percent():
    """A sufficient photon count (N=3e4) reaches ≤1% RMS vs the deterministic
    field — the empirical 'enough photons to approximate the expected result'."""
    cfg = SimConfig(lam_c=LAM, X_NA=0.8, n=N_MED, N_theta=801)
    rng = np.random.default_rng(7)
    x = np.linspace(-1.0, 1.0, 41); z = np.linspace(-3, 3, 41)
    Z, X = np.meshgrid(z, x, indexing="ij"); Y = np.zeros_like(X)
    ref = scalar_debye(np.abs(x), z, cfg.k_c, cfg.alpha, 801); ref /= ref.max()
    kx, ky, kz, w = sample_photons(cfg, 30000, rng=rng)
    I = coherent_intensity(kx, ky, kz, w, X, Y, Z); I /= I.max()
    assert np.sqrt(np.mean((I - ref) ** 2)) < 0.01


def test_zeros_get_cleaner_and_clean_at_sufficient_N():
    """More photons fill the true zeros less (random-walk residual decreases),
    and at a sufficient count the zeros are clean (floor < 1.5e-3). Measured on
    an x–z slice where the |I0-I2|^2 zero ring is well sampled."""
    cfg = SimConfig(lam_c=LAM, X_NA=0.8, n=N_MED, N_theta=801)
    x = np.linspace(-1.0, 1.0, 41); z = np.linspace(-3, 3, 41)
    Z, X = np.meshgrid(z, x, indexing="ij"); Y = np.zeros_like(X)
    I0, I1, I2 = compute_integrals(np.abs(x), z, cfg.k_c, cfg.alpha, 801)
    ref = np.abs(I0 - I2) ** 2; ref /= ref.max()
    nullmask = ref < 1e-3
    floors = []
    for N in (3000, 30000):
        rng = np.random.default_rng(8)
        kx, ky, kz, w = sample_photons(cfg, N, rng=rng)
        I = coherent_intensity(kx, ky, kz, w, X, Y, Z); I /= I.max()
        floors.append(I[nullmask].mean())
    assert floors[1] < floors[0]      # cleaner with more photons
    assert floors[1] < 1.5e-3         # clean at sufficient N


def test_pulsed_wavelength_mc_matches_deterministic():
    """Per-photon wavelength-sampling MC reproduces the deterministic scalar
    Eq. 10 spectral sum (clear limit) — the gate for wavelength sampling."""
    cfg = SimConfig(lam_c=LAM, X_NA=0.8, n=N_MED, tau=2e-15, N_freq=31, N_theta=601)
    x = np.linspace(-1.2, 1.2, 81)
    omes = cfg.omega_grid()
    W = np.where(omes > 0, cfg.spectral_power(omes), 0.0)
    det = np.zeros_like(x)
    for om, w in zip(omes, W):
        if w == 0:
            continue
        det += w * scalar_debye(np.abs(x), np.array([0.0]), cfg.k_for_omega(om),
                                cfg.alpha, cfg.N_theta)[0]
    det /= det.max()
    mc = mc_pulsed_intensity(cfg, x, np.zeros_like(x), np.zeros_like(x), 120000,
                             rng=np.random.default_rng(0))
    assert np.sqrt(np.mean((mc - det) ** 2)) < 0.02


def test_pulsed_mc_cw_reduces_to_monochromatic():
    """For CW (tau=inf) the pulsed MC falls back to the monochromatic MC
    exactly (same rng → identical)."""
    cfg = SimConfig(lam_c=LAM, X_NA=0.8, n=N_MED, tau=np.inf, N_theta=601)
    x = np.linspace(-1, 1, 41); zero = np.zeros_like(x)
    a = mc_pulsed_intensity(cfg, x, zero, zero, 20000, rng=np.random.default_rng(5))
    b = mc_focal_intensity(cfg, x, zero, zero, 20000, rng=np.random.default_rng(5))
    assert np.allclose(a, b)


def test_parallel_identical_to_serial():
    """Splitting photons across workers is identical to serial (FP round-off)."""
    cfg = SimConfig(lam_c=LAM, X_NA=0.8, n=N_MED, N_theta=401)
    rng = np.random.default_rng(2)
    x = np.linspace(-1, 1, 21); z = np.zeros_like(x); y = np.zeros_like(x)
    kx, ky, kz, w = sample_photons(cfg, 20000, rng=rng)
    Is = coherent_intensity_parallel(kx, ky, kz, w, x, y, z, n_jobs=1)
    Ip = coherent_intensity_parallel(kx, ky, kz, w, x, y, z, n_jobs=2)
    assert np.max(np.abs(Is - Ip)) / Is.max() < 1e-10


def test_launcher_samples_debye_wolf_density():
    """The photon launcher must draw θ from the Debye-Wolf integrand density
    p(θ) ∝ |A(θ)|√cosθ sinθ — the basis of the whole MC. Checked for uniform
    AND Gaussian input by a Kolmogorov-Smirnov distance to the analytic CDF
    (≈1/√N for a correct sampler)."""
    cfg = SimConfig(lam_c=LAM, X_NA=0.8, n=N_MED, N_theta=801)
    for apod in (None, gaussian(2.0, cfg.sin2_alpha)):
        rng = np.random.default_rng(0)
        kx, ky, kz, w = sample_photons(cfg, 50000, apod=apod, rng=rng)
        theta = np.arccos(np.clip(kz / cfg.k_c, -1.0, 1.0))
        th = np.linspace(0.0, cfg.alpha, 4001)
        A = np.ones_like(th) if apod is None else np.abs(apod(th))
        pdf = A * np.sqrt(np.cos(th)) * np.sin(th)
        cdf = np.cumsum(pdf); cdf -= cdf[0]; cdf /= cdf[-1]
        s = np.sort(theta)
        ks = np.max(np.abs(np.arange(1, s.size + 1) / s.size
                           - np.interp(s, th, cdf)))
        assert ks < 0.02


def test_launcher_azimuth_uniform():
    """φ is uniform on [0, 2π) (rotational symmetry of the input pupil):
    the φ-histogram is flat to within histogram (Poisson) noise."""
    cfg = SimConfig(lam_c=LAM, X_NA=0.8, n=N_MED, N_theta=801)
    rng = np.random.default_rng(0)
    kx, ky, kz, w = sample_photons(cfg, 50000, rng=rng)
    phi = np.mod(np.arctan2(ky, kx), 2 * np.pi)
    counts, _ = np.histogram(phi, bins=36, range=(0, 2 * np.pi))
    norm = counts / counts.mean()
    assert np.max(np.abs(norm - 1.0)) < 0.15


def test_vector_mc_matches_both_RW_cuts():
    """Vector MC reproduces |I0-I2|^2 (y-axis) and |I0+I2|^2+4|I1|^2 (x-axis)."""
    cfg = SimConfig(lam_c=LAM, X_NA=0.8, n=N_MED, N_theta=801)
    rng = np.random.default_rng(3)
    s = np.linspace(-1.0, 1.0, 41); z = np.linspace(-3, 3, 41)
    Z, S = np.meshgrid(z, s, indexing="ij"); O = np.zeros_like(S)
    I0, I1, I2 = compute_integrals(np.abs(s), z, cfg.k_c, cfg.alpha, 801)
    det_y = np.abs(I0 - I2) ** 2; det_y /= det_y.max()
    det_x = np.abs(I0 + I2) ** 2 + 4 * np.abs(I1) ** 2; det_x /= det_x.max()
    kx, ky, kz, wv = sample_photons_vector(cfg, 50000, rng=rng)
    mc_y = coherent_intensity_vector(kx, ky, kz, wv, O, S, Z); mc_y /= mc_y.max()
    mc_x = coherent_intensity_vector(kx, ky, kz, wv, S, O, Z); mc_x /= mc_x.max()
    assert np.sqrt(np.mean((mc_y - det_y) ** 2)) < 0.02
    assert np.sqrt(np.mean((mc_x - det_x) ** 2)) < 0.02
