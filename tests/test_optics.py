"""Tests for the deterministic diffraction core, tied to fundamental results.

Each test asserts a known analytic limit, conservation law, or published
checkpoint — so a failure flags a real physics regression, not just a numeric
drift.
"""

import numpy as np

from mcdo import SimConfig
from mcdo.rw_integrals import compute_integrals
from mcdo.debye import scalar_debye, airy_intensity
from mcdo.annular import compute_integrals_annular
from mcdo.apodization import gaussian, axicon
from mcdo import linfoot

LAM, N_MED = 0.750, 1.3


def _ycut(I0, I1, I2):
    return np.abs(I0 - I2) ** 2


# ── diffraction limits ─────────────────────────────────────────────────────

def test_low_NA_transverse_is_airy():
    """At low NA the focal-plane intensity must equal the Airy pattern."""
    cfg = SimConfig(lam_c=LAM, X_NA=0.1, n=N_MED, N_theta=801)
    v = np.linspace(0, 10, 200)
    r = v / (cfg.k_c * cfg.sin_alpha)
    I0, I1, I2 = compute_integrals(r, np.array([0.0]), cfg.k_c, cfg.alpha, 801)
    I = _ycut(I0[0], I1[0], I2[0]); I /= I.max()
    assert np.max(np.abs(I - airy_intensity(v))) < 5e-3


def test_scalar_debye_matches_airy_low_NA():
    """Scalar Debye integral → Airy at low NA (independent of the vector cut)."""
    cfg = SimConfig(lam_c=LAM, X_NA=0.1, n=N_MED, N_theta=801)
    v = np.linspace(0, 10, 200)
    r = v / (cfg.k_c * cfg.sin_alpha)
    I = scalar_debye(r, np.array([0.0]), cfg.k_c, cfg.alpha, 801)[0]
    I /= I.max()
    assert np.max(np.abs(I - airy_intensity(v))) < 5e-3


def test_cw_transverse_fwhm_romallosa():
    """Romallosa checkpoint: CW transverse FWHM ≈ 472.8 nm (NA=0.8, λ=750, n=1.3)."""
    cfg = SimConfig(lam_c=LAM, X_NA=0.8, n=N_MED, N_theta=801)
    r = np.linspace(0, 1.0, 600)
    I0, I1, I2 = compute_integrals(r, np.array([0.0]), cfg.k_c, cfg.alpha, 801)
    I = _ycut(I0[0], I1[0], I2[0]); I /= I.max()
    i = np.argmax(I < 0.5)
    half_r = np.interp(0.5, [I[i], I[i-1]], [r[i], r[i-1]])
    assert abs(2 * half_r * 1e3 - 472.8) < 3.0


def test_cw_transverse_has_true_zero_ring():
    """The |I0-I2|^2 cut has a true zero ring near r = 0.555 μm (NA=0.8)."""
    cfg = SimConfig(lam_c=LAM, X_NA=0.8, n=N_MED, N_theta=801)
    r = np.linspace(0, 1.0, 800)
    I0, I1, I2 = compute_integrals(r, np.array([0.0]), cfg.k_c, cfg.alpha, 801)
    I = _ycut(I0[0], I1[0], I2[0]); I /= I.max()
    r_zero = r[np.argmin(I)]
    assert I.min() < 1e-3 and abs(r_zero - 0.555) < 0.02


# ── spectral / config ──────────────────────────────────────────────────────

def test_spectral_power_fwhm_is_half_at_edge():
    """|E(ω)|² drops to 1/2 at ω_c ± Ω/2 with Ω = 4 ln2 / τ."""
    cfg = SimConfig(tau=1e-15)
    Om = 4 * np.log(2) / cfg.tau
    edge = cfg.spectral_power(np.array([cfg.omega_c + Om / 2]))[0]
    assert abs(edge - 0.5) < 1e-9


def test_omega_grid_full_positive_spectrum():
    """For a few-cycle pulse the grid spans (0, 2 ω_c) (full positive support)."""
    cfg = SimConfig(tau=1e-15)
    g = cfg.omega_grid()
    assert g[0] >= 0 and abs(g[-1] - 2 * cfg.omega_c) / cfg.omega_c < 1e-6


# ── apodization ────────────────────────────────────────────────────────────

def test_gaussian_apodization_zero_limit_is_uniform():
    """α_t → 0 Gaussian apodization reproduces uniform illumination exactly."""
    cfg = SimConfig(X_NA=0.8, n=N_MED, N_theta=801)
    r = np.linspace(0, 1.0, 200); z0 = np.array([0.0])
    Iu = _ycut(*[a[0] for a in compute_integrals(r, z0, cfg.k_c, cfg.alpha, 801)])
    A = gaussian(1e-12, cfg.sin2_alpha)
    Ig = _ycut(*[a[0] for a in compute_integrals(r, z0, cfg.k_c, cfg.alpha, 801, apodization=A)])
    assert np.max(np.abs(Iu / Iu.max() - Ig / Ig.max())) < 1e-9


# ── annular / Babinet ──────────────────────────────────────────────────────

def test_annular_eps_zero_equals_full_disk():
    """Babinet construction at ε=0 is identical to the full disk."""
    cfg = SimConfig(X_NA=0.8, n=N_MED, N_theta=801)
    r = np.linspace(0, 1.0, 200); z = np.linspace(-2, 2, 50)
    full = compute_integrals(r, z, cfg.k_c, cfg.alpha, 801)
    ann = compute_integrals_annular(r, z, cfg.k_c, cfg.alpha, 0.0, 801)
    assert max(np.max(np.abs(f - a)) for f, a in zip(full, ann)) < 1e-12


def test_thin_annulus_approaches_bessel_low_NA():
    """A thin annulus → Durnin J₀²(v) in the low-NA (scalar) limit."""
    from scipy.special import j0
    cfg = SimConfig(X_NA=0.13, n=N_MED, N_theta=1001)
    v = np.linspace(0, 12, 300)
    r = v / (cfg.k_c * cfg.sin_alpha)
    I0, I1, I2 = compute_integrals_annular(r, np.array([0.0]), cfg.k_c, cfg.alpha, 0.99, 1001)
    I = _ycut(I0[0], I1[0], I2[0]); I /= I.max()
    assert np.max(np.abs(I - j0(v) ** 2)) < 0.05


def test_axicon_j0_deviation_shrinks_with_beta():
    """Axicon transverse profile → Durnin J₀²(v·sinθ*/sinα); the residual is
    stationary-phase error and SHRINKS as β grows — so the 4–8% flag is a model
    approximation, not the method. Low NA (scalar regime), θ*=0.7α."""
    from scipy.special import j0
    cfg = SimConfig(X_NA=0.3, n=N_MED, N_theta=2001)
    v = np.linspace(0, 12, 200)
    r = v / (cfg.k_c * cfg.sin_alpha)
    frac = 0.7
    scale = np.sin(frac * cfg.alpha) / cfg.sin_alpha

    def dev(beta):
        u0 = beta * cfg.sin_alpha / np.tan(frac * cfg.alpha)
        z0 = u0 / (cfg.k_c * cfg.sin2_alpha)
        I = scalar_debye(r, np.array([z0]), cfg.k_c, cfg.alpha, 2001,
                         apodization=axicon(beta, cfg.sin_alpha))[0]
        I /= I.max()
        return np.max(np.abs(I - j0(v * scale) ** 2))

    d_lo, d_hi = dev(10), dev(160)
    assert d_lo > 0.05                    # a real SPA error at small β
    assert d_hi < d_lo and d_hi < 0.04    # clearly shrinks as β grows


# ── Maxwell (first principles) ─────────────────────────────────────────────

def test_vector_field_is_divergence_free():
    """Maxwell: the RW vector field E = (I0+I2cos2φ, I2sin2φ, −2i·I1cosφ) is a
    superposition of transverse plane waves, so ∇·E = 0. The finite-difference
    residual must sit at the FD floor — and breaking the E_z factor (2→1) must
    blow it up. This pins the (1±cosθ)/sin²θ kernel bookkeeping to Maxwell
    itself, independent of any literature benchmark."""
    cfg = SimConfig(lam_c=LAM, X_NA=0.8, n=N_MED, N_theta=801)
    k = cfg.k_c

    def E(x, y, z, ez=2.0):
        r = np.hypot(x, y); phi = np.arctan2(y, x)
        I0, I1, I2 = compute_integrals(np.array([r]), np.array([z]),
                                       k, cfg.alpha, 801)
        return np.array([I0[0, 0] + I2[0, 0] * np.cos(2 * phi),
                         I2[0, 0] * np.sin(2 * phi),
                         -ez * 1j * I1[0, 0] * np.cos(phi)])

    def div_res(ez):
        x, y, z, h = 0.30, 0.20, 0.50, 0.005
        d = ((E(x + h, y, z, ez)[0] - E(x - h, y, z, ez)[0])
             + (E(x, y + h, z, ez)[1] - E(x, y - h, z, ez)[1])
             + (E(x, y, z + h, ez)[2] - E(x, y, z - h, ez)[2])) / (2 * h)
        return abs(d) / (k * np.linalg.norm(E(x, y, z, ez)))

    assert div_res(2.0) < 3e-3          # at the finite-difference floor
    assert div_res(1.0) > 0.03          # broken bookkeeping fails loudly


# ── Linfoot identities ─────────────────────────────────────────────────────

def test_linfoot_identity_on_self():
    """F = S = Q = 1 when test equals reference."""
    rng = np.random.default_rng(0)
    a = rng.random(200) ** 2
    out = linfoot.all_criteria(a, a)
    assert all(abs(out[k] - 1.0) < 1e-12 for k in "FSQ")


def test_linfoot_relation_2Q_minus_S_equals_F():
    """The Linfoot identity 2Q − S = F must hold for any pair."""
    rng = np.random.default_rng(1)
    r, a = rng.random(200), rng.random(200)
    o = linfoot.all_criteria(r, a)
    assert abs(2 * o["Q"] - o["S"] - o["F"]) < 1e-12


def test_structural_content_broader_exceeds_one():
    """A broadened test distribution gives S > 1."""
    x = np.linspace(-5, 5, 401)
    ref = np.exp(-x ** 2)
    broad = np.exp(-(x / 1.5) ** 2)
    assert linfoot.structural_content(ref / ref.max(), broad / broad.max()) > 1.0
