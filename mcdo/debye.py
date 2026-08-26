"""
Scalar Debye diffraction and paraxial (Airy) analytics — the low-NA
references that the vector Richards-Wolf solution must converge to.

Scalar Debye integral (aplanatic, with apodization):

    U(u, v) = ∫₀^α A(θ) √cosθ · J₀(v·sinθ/sinα) · exp(j·u·cosθ/sin²α)
              · sinθ dθ
    I(u, v) = |U|²

This is the Richards-Wolf I₀ integral without the vector kernels
(1±cosθ) — i.e., polarization ignored. In the paraxial limit (α → 0,
uniform A) it reduces to the classical results [B&W99 §8.8]:

    focal plane:  I(v) = [2·J₁(v)/v]²        (Airy pattern)
    optical axis: I(u) = [sin(u/4)/(u/4)]²   (sinc²)

with optical coordinates u = k·sin²α·z, v = k·sinα·r.

References
----------
[B&W99]  Born & Wolf (1999), Principles of Optics, §8.8.
[R&W59]  Richards & Wolf (1959), Proc. R. Soc. London A 253, 358.
[Rom03]  Romallosa et al. (2003), Phys. Rev. A 68, 033812.
"""

import numpy as np
from scipy.special import jv, j1

from .rw_integrals import _simpson_weights


def scalar_debye(
    r_arr: np.ndarray,
    z_arr: np.ndarray,
    k: float,
    alpha: float,
    N_theta: int = 501,
    apodization=None,
) -> np.ndarray:
    """Scalar Debye intensity |U|² on a (N_z × N_r) grid.

    Same conventions as rw_integrals.compute_integrals (Simpson quadrature,
    optical coordinates, √cosθ aplanatic factor, optional A(θ)).
    """
    r_arr = np.asarray(r_arr, dtype=float)
    z_arr = np.asarray(z_arr, dtype=float)

    sin_a = np.sin(alpha)
    sin2_a = sin_a ** 2
    u = k * sin2_a * z_arr
    v = k * sin_a * np.abs(r_arr)

    theta = np.linspace(0.0, alpha, N_theta)
    weights = _simpson_weights(N_theta, alpha)
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)
    amp = np.sqrt(np.maximum(cos_t, 0.0))
    if apodization is not None:
        amp = amp * apodization(theta)

    P = np.exp(1j * np.outer(cos_t / sin2_a, u))        # (N_theta, N_z)
    xi = np.outer(sin_t / sin_a, v)                      # (N_theta, N_r)
    B = (weights * amp * sin_t)[:, None] * jv(0, xi)     # (N_theta, N_r)

    U = P.T @ B                                          # (N_z, N_r)
    return np.abs(U) ** 2


def scalar_debye_field(r_arr, z_arr, k, alpha, N_theta=501, apodization=None):
    """Complex scalar Debye field U (not the intensity).

    Needed to build an annular scalar reference by Babinet subtraction,
    U_ring = U(alpha_outer) - U(alpha_inner), which cannot be done on
    intensities.
    """
    r_arr = np.asarray(r_arr, dtype=float)
    z_arr = np.asarray(z_arr, dtype=float)
    sin_a = np.sin(alpha); sin2_a = sin_a ** 2
    u = k * sin2_a * z_arr
    v = k * sin_a * np.abs(r_arr)
    theta = np.linspace(0.0, alpha, N_theta)
    weights = _simpson_weights(N_theta, alpha)
    cos_t = np.cos(theta); sin_t = np.sin(theta)
    amp = np.sqrt(np.maximum(cos_t, 0.0))
    if apodization is not None:
        amp = amp * apodization(theta)
    P = np.exp(1j * np.outer(cos_t / sin2_a, u))
    xi = np.outer(sin_t / sin_a, v)
    B = (weights * amp * sin_t)[:, None] * jv(0, xi)
    return P.T @ B


def airy_intensity(v: np.ndarray) -> np.ndarray:
    """Paraxial focal-plane intensity [2·J₁(v)/v]², normalized to 1 at v=0."""
    v = np.asarray(v, dtype=float)
    out = np.ones_like(v)
    nz = v != 0
    out[nz] = (2.0 * j1(v[nz]) / v[nz]) ** 2
    return out


def axial_sinc2(u: np.ndarray) -> np.ndarray:
    """Paraxial on-axis intensity [sin(u/4)/(u/4)]², normalized to 1 at u=0."""
    u = np.asarray(u, dtype=float)
    x = u / 4.0
    out = np.ones_like(u)
    nz = x != 0
    out[nz] = (np.sin(x[nz]) / x[nz]) ** 2
    return out
