r"""Pupil illumination (apodization) functions :math:`A(\theta)`.

For an aplanatic objective obeying the sine condition, a pupil radius
:math:`r` maps to the focal cone angle :math:`\theta` via
:math:`r = f\sin\theta`. A collimated Gaussian beam with :math:`1/e^2`
intensity radius :math:`w` at a pupil of radius :math:`r_{ap}` therefore
produces the angular amplitude

.. math::

    A(\theta) = \exp\!\big(-\alpha_t\,\sin^2\theta / \sin^2\alpha\big),
    \qquad \alpha_t = (r_{ap}/w)^2

[HB03]_: :math:`\alpha_t\to0` is uniform illumination; :math:`\alpha_t=1` puts
the waist at the pupil edge (amplitude :math:`e^{-1}\approx37\%`);
:math:`\alpha_t\ge4` is effectively untruncated (<2% at the edge).

Each factory returns a callable ``A(theta)`` (with a ``.label`` attribute) that
the diffraction solvers (:mod:`mcdo.rw_integrals`, :mod:`mcdo.debye`) accept via
their ``apodization=`` argument. The :math:`\sqrt{\cos\theta}` aplanatic
factor is **not** part of :math:`A(\theta)` — it is applied inside the
integrals. The same callables serve as Monte-Carlo photon launchers: the
sampling density :math:`\propto |A(\theta)|\sqrt{\cos\theta}\sin\theta` reuses
them (:mod:`mcdo.montecarlo`).

References
----------
.. [HB03] Z. L. Horváth & Z. Bor, "Focusing of truncated Gaussian beams",
   Opt. Commun. **222**, 51 (2003).
.. [RW59] B. Richards & E. Wolf, Proc. R. Soc. Lond. A **253**, 358 (1959).
.. [Dur87] J. Durnin, "Exact solutions for nondiffracting beams", J. Opt. Soc.
   Am. A **4**, 651 (1987).
.. [She78] C. J. R. Sheppard & T. Wilson, "Gaussian-beam theory of lenses with
   annular aperture", Microw. Opt. Acoust. **2**, 105 (1978).
"""

import numpy as np


def uniform():
    """Uniform (flat) illumination, ``A(θ) = 1``.

    Returns
    -------
    callable
        ``A(theta) -> ndarray`` of ones, with ``.label = 'uniform'``.
    """
    def A(theta):
        return np.ones_like(np.asarray(theta, dtype=float))
    A.label = "uniform"
    return A


def gaussian(alpha_t, sin2_alpha_ref):
    r"""Truncated-Gaussian illumination ``A(θ) = exp(−α_t sin²θ / sin²α_ref)``.

    Parameters
    ----------
    alpha_t : float
        Truncation coefficient :math:`(r_{ap}/w)^2` [HB03]_. ``0`` → uniform.
    sin2_alpha_ref : float
        :math:`\sin^2\alpha` of the **reference** aperture. For a plain disk
        this is the system's own value; for annular apertures via Babinet both
        the inner and outer disks must reference the *outer* aperture so they
        sample the same physical beam.

    Returns
    -------
    callable
        ``A(theta) -> ndarray`` (real), with a descriptive ``.label``.
    """
    def A(theta):
        return np.exp(-alpha_t * np.sin(np.asarray(theta, dtype=float)) ** 2
                      / sin2_alpha_ref)
    A.label = f"gaussian(α_t={alpha_t:g})"
    return A


def axicon(beta, sin_alpha_ref):
    r"""Axicon (conical) pupil phase ``A(θ) = exp(+jβ sinθ / sinα_ref)``.

    A true axicon is a cone (phase ∝ pupil radius ∝ sinθ), turning the focal
    point into a focal segment. Stationary phase selects the contributing cone
    angle :math:`\theta^*` at axial position :math:`u` via
    :math:`u = \beta\sin\alpha\,\cot\theta^*`, with local transverse profile
    :math:`J_0^2(v\sin\theta^*/\sin\alpha)` [Dur87]_.

    Parameters
    ----------
    beta : float
        Conical phase depth (radians) at the pupil edge. ``0`` → plain disk.
    sin_alpha_ref : float
        :math:`\sin\alpha` of the reference aperture.

    Returns
    -------
    callable
        ``A(theta) -> ndarray`` (complex; the solvers accept complex A).
    """
    def A(theta):
        return np.exp(1j * beta * np.sin(np.asarray(theta, dtype=float))
                      / sin_alpha_ref)
    A.label = f"axicon(β={beta:g})"
    return A


def gaussian_ring(sin_theta0, sigma_s):
    r"""Gaussian annular illumination centred on cone angle :math:`\theta_0`.

    A Gaussian ring in the pupil,
    :math:`A(\theta) = \exp[-(\sin\theta-\sin\theta_0)^2/(2\sigma_s^2)]`, used
    for the Sheppard & Wilson annular checkpoint [She78]_. Narrow rings
    (:math:`\sigma_s \ll \sin\theta_0`) approach the δ-ring → :math:`J_0(v)`
    focal field.

    Parameters
    ----------
    sin_theta0 : float
        Ring centre, in :math:`\sin\theta`.
    sigma_s : float
        1/e-amplitude half-width in :math:`\sin\theta`.

    Returns
    -------
    callable
        ``A(theta) -> ndarray`` (real).
    """
    s0 = float(sin_theta0)
    def A(theta):
        s = np.sin(np.asarray(theta, dtype=float))
        return np.exp(-(s - s0) ** 2 / (2.0 * sigma_s ** 2))
    A.label = f"gaussian_ring(sinθ₀={s0:g}, σ={sigma_s:g})"
    return A
