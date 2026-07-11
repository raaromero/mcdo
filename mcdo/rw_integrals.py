"""
Vectorized Richards-Wolf diffraction integrals I₀, I₁, I₂.

Implements Romallosa (2003) Eqs. (5–7) using an efficient matrix-multiply
formulation.  For a grid of (z, r) points the integrals factor as

    I_m(z, r) = Σ_j  P[j, z] · B_m[j, r] · w_j

where
    P[j, z]  = exp(i · u(z) · cosθ_j / sin²α)      (N_θ × N_z)
    B_m[j,r] = √cosθ_j · kernel_m(θ_j) · J_m(ξ)   (N_θ × N_r)
    ξ = v(r) · sinθ_j / sinα

and u = k·sin²α·z,  v = k·sinα·r  [R&W59 Eq. 2.6].

The outer integral is evaluated via matrix multiplication:
    I_m = P.T @ (w * B_m)   →  shape (N_z, N_r)

References
----------
[R&W59]  Richards & Wolf (1959), Proc. R. Soc. London A 253, 358.
[Rom03]  Romallosa, Bantang & Saloma (2003), Phys. Rev. A 68, 033812.
"""

import numpy as np
from scipy.special import jv


def _simpson_weights(n: int, endpoint: float) -> np.ndarray:
    """Simpson 1/3-rule weights for n equally spaced points on [0, endpoint].

    Requires n odd and n ≥ 3.
    """
    assert n >= 3 and n % 2 == 1, "N_theta must be odd and ≥ 3"
    h = endpoint / (n - 1)
    w = np.ones(n)
    w[1:-1:2] = 4.0   # odd interior
    w[2:-2:2] = 2.0   # even interior
    return w * h / 3.0


def compute_integrals(
    r_arr: np.ndarray,
    z_arr: np.ndarray,
    k: float,
    alpha: float,
    N_theta: int = 501,
    apodization=None,
) -> tuple:
    """Compute I₀, I₁, I₂ on a 2-D (z × r) grid.

    Simpson quadrature over θ ∈ [0, α].

    Parameters
    ----------
    r_arr   : (N_r,)  radial positions (μm); negative values are mirrored via |r|
    z_arr   : (N_z,)  axial positions (μm)
    k       : wave number in medium (μm⁻¹), k = n·2π/λ
    alpha   : half-angle of focusing cone (rad), α = arcsin(X_NA / n)
    N_theta : quadrature points (must be odd)
    apodization : callable θ → amplitude, optional
        Pupil illumination A(θ) (see romallosa.apodization). None = uniform.
        The √cosθ aplanatic factor is applied here regardless.

    Returns
    -------
    I0, I1, I2 : complex arrays of shape (N_z, N_r)
    """
    r_arr = np.asarray(r_arr, dtype=float)
    z_arr = np.asarray(z_arr, dtype=float)

    sin_a = np.sin(alpha)
    sin2_a = sin_a ** 2

    # Optical coordinates  [R&W59 Eq. 2.6]
    u = k * sin2_a * z_arr          # (N_z,)
    v = k * sin_a * np.abs(r_arr)   # (N_r,) — magnitude (|r| → symmetric)

    # θ quadrature
    theta = np.linspace(0.0, alpha, N_theta)
    weights = _simpson_weights(N_theta, alpha)  # (N_theta,)
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)
    amp = np.sqrt(np.maximum(cos_t, 0.0))  # √cosθ aplanatic factor
    if apodization is not None:
        amp = amp * apodization(theta)     # pupil illumination A(θ)

    # Phase matrix  P[j, iz] = exp(i · cosθ_j/sin²α · u[iz])
    #   outer(cos_t/sin2_a, u)  →  (N_theta, N_z)
    P = np.exp(1j * np.outer(cos_t / sin2_a, u))   # (N_theta, N_z)

    # Bessel argument  xi[j, ir] = sinθ_j/sinα · v[ir]
    xi = np.outer(sin_t / sin_a, v)                 # (N_theta, N_r)

    # Pre-weighted amplitude kernels  (N_theta,)
    w_amp = weights * amp

    # Bessel matrices  (N_theta, N_r)
    B0 = (w_amp * sin_t * (1.0 + cos_t))[:, None] * jv(0, xi)
    B1 = (w_amp * sin_t ** 2)[:, None]             * jv(1, xi)
    B2 = (w_amp * sin_t * (1.0 - cos_t))[:, None]  * jv(2, xi)

    # Matrix multiply: I_m = P.T @ B_m  →  (N_z, N_r)
    I0 = P.T @ B0
    I1 = P.T @ B1
    I2 = P.T @ B2

    return I0, I1, I2


def integrals_to_intensity(I0: np.ndarray, I1: np.ndarray, I2: np.ndarray) -> np.ndarray:
    """Convert I₀, I₁, I₂ to intensity for x-polarized beam observed at φ=π/2.

    At φ=π/2 (y-axis): Ex = -j(I₀−I₂), Ey=0, Ez=0.
    Returns |I₀ − I₂|² — gives the dark ring (true zero) in the CW transverse
    profile, matching the zero-point behaviour stated in [Rom03 Sec. III].
    """
    return np.abs(I0 - I2) ** 2
