"""Scattering-kernel tests tied to fundamental results.

The phase function must reproduce its anisotropy, isotropic scattering must be
uniform on the sphere, directions must stay unit-norm, and the ballistic
fraction must obey Beer-Lambert.
"""

import numpy as np

from mcdo.scatter import hg_sample, rotate, propagate_slab


def test_hg_mean_cosine_equals_g():
    """⟨cosθ⟩ of Henyey-Greenstein samples equals the anisotropy g."""
    rng = np.random.default_rng(0)
    for g in (0.0, 0.3, 0.55, 0.9):
        cos_t, _ = hg_sample(g, 200000, rng)
        assert abs(cos_t.mean() - g) < 0.01


def test_isotropic_scatter_is_uniform_on_sphere():
    """A g=0 scatter of a +z beam yields ⟨μz⟩≈0, ⟨μz²⟩≈1/3 (uniform sphere)."""
    rng = np.random.default_rng(1)
    N = 200000
    mu = np.tile(np.array([[0.0], [0.0], [1.0]]), (1, N))
    cos_t, phi = hg_sample(0.0, N, rng)
    out = rotate(mu, cos_t, phi)
    assert abs(out[2].mean()) < 0.01
    assert abs((out[2] ** 2).mean() - 1 / 3) < 0.01


def test_rotation_preserves_unit_norm():
    """Rotated directions remain unit vectors."""
    rng = np.random.default_rng(2)
    N = 5000
    mu = rng.normal(size=(3, N)); mu /= np.linalg.norm(mu, axis=0)
    cos_t, phi = hg_sample(0.6, N, rng)
    out = rotate(mu, cos_t, phi)
    assert np.max(np.abs(np.linalg.norm(out, axis=0) - 1.0)) < 1e-12


def test_forward_scatter_preserves_direction():
    """A zero-deflection (cosθ=1) scatter leaves the direction unchanged."""
    mu = np.array([[0.3], [-0.4], [np.sqrt(1 - 0.25)]])
    out = rotate(mu, np.array([1.0]), np.array([1.234]))
    assert np.max(np.abs(out - mu)) < 1e-12


def test_beer_lambert_ballistic_fraction():
    """Unscattered fraction through a slab of thickness L equals exp(−μ_s L)."""
    rng = np.random.default_rng(4)
    N = 200000
    L = 1.0
    pos = np.zeros((3, N))
    mu = np.tile(np.array([[0.0], [0.0], [1.0]]), (1, N))
    for mu_s in (0.5, 1.0, 2.0):
        _, _, nsc, _, _ = propagate_slab(pos, mu, mu_s, 0.5, (0.0, L), 200, rng)
        assert abs(np.mean(nsc == 0) - np.exp(-mu_s * L)) < 0.01
