"""
Annular apertures via Babinet's principle at the FIELD level.

In physical variables the RW integrals read
    I_m(r,z) = ∫_{θ_in}^{α} A(θ)√cosθ · kern_m(θ) · J_m(k r sinθ) · e^{jkz cosθ} dθ
so by linearity an annulus (central obstruction ε = r_in/r_out = sinθ_in/sinα,
via the sine condition) is the difference of two disks evaluated at the SAME
(r, z, k):

    I_m^ann = I_m(α_out) − I_m(α_in),     sinθ_in = ε·sinα_out

The subtraction happens on the complex integrals (fields), before squaring,
so coherent cross terms are kept. Any apodization A(θ) must reference the
OUTER aperture so both disks sample the same physical beam.

Checkpoints: ε→0 reduces to the full disk (machine precision); paraxial DOF
extension DOF(ε)/DOF(0) = 1/(1−ε²); thin-annulus transverse profile → J₀²(v)
(Durnin nondiffracting limit).

References
----------
[B&W99]  Born & Wolf (1999), §8.6.2 (Babinet).
[She78]  Sheppard & Wilson (1978), annular pupils.
[Dur87]  Durnin (1987), J. Opt. Soc. Am. A 4, 651 (Bessel beams).
"""

import numpy as np

from .rw_integrals import compute_integrals


def compute_integrals_annular(
    r_arr: np.ndarray,
    z_arr: np.ndarray,
    k: float,
    alpha: float,
    eps: float,
    N_theta: int = 501,
    apodization=None,
) -> tuple:
    """I₀, I₁, I₂ for an annular aperture with obstruction ratio ε.

    Parameters as compute_integrals, plus
    eps : float in [0, 1) — r_inner/r_outer; sinθ_in = ε·sinα.
    apodization : callable referenced to the OUTER aperture (pass the same
        callable used for the full disk; it is evaluated on each disk's own
        θ grid, which is correct because A is a function of θ only).

    Returns complex (N_z × N_r) arrays.
    """
    I0o, I1o, I2o = compute_integrals(r_arr, z_arr, k, alpha, N_theta,
                                      apodization=apodization)
    if eps <= 0.0:
        return I0o, I1o, I2o

    alpha_in = np.arcsin(eps * np.sin(alpha))
    # inner disk needs its own (odd) quadrature count; scale with angle
    N_in = max(51, int(N_theta * alpha_in / alpha) | 1)
    I0i, I1i, I2i = compute_integrals(r_arr, z_arr, k, alpha_in, N_in,
                                      apodization=apodization)

    # compute_integrals evaluates in optical coordinates of ITS alpha, but
    # u = k sin²α z and v = k sinα r combine with the kernels to give the
    # physical integrand J_m(k r sinθ)·e^{jkz cosθ} independent of alpha —
    # so the two results subtract directly at the same (r, z, k).
    return I0o - I0i, I1o - I1i, I2o - I2i
