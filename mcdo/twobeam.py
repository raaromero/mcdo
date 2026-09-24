r"""Two focused beams: two-color (2CE) and two-photon (2PE) excitation.

Two lenses focus two beams toward a common region. Beam 1 propagates along the
lab +z axis with its geometric focus at the origin. Beam 2 propagates along
the direction rotated by an angle ``theta`` about the lab y axis,

.. math::

    \hat{d}_2 = (\sin\theta,\ 0,\ \cos\theta),

with its geometric focus at :math:`O' = (x_c, 0, z_c)` [CS00]_ [LS02]_.
``theta = 0`` is collinear, ``pi/2`` perpendicular, ``pi`` counter-propagating.

Each beam's field is computed in its own frame and then expressed in the lab
frame. The fluorescence signals are [CS00]_ (Eqs. 2-3):

.. math::

    F_{2c}(P) = \kappa\, I_1(P)\, I_2(P), \qquad
    F_{2p}(P) = \kappa'\, |U_1(P) + U_2(P)|^4 .

2CE multiplies two intensities (different colors do not interfere). 2PE adds
the fields first, so the two beams interfere.

Field models
------------
``'paraxial'``
    Scalar paraxial Debye field (the Lommel-function field of [BW99]_ §8.8,
    used in [CS00]_ [LS02]_ [LS03]_), including the carrier ``exp(ikz)`` so
    that 2PE interference between beams is represented:

    .. math::

        U(u, v) = e^{ikz}\, 2\!\int_0^1 J_0(v\rho)\,
        e^{-iu\rho^2/2}\,\rho\, d\rho,\qquad
        u = k\,(\mathrm{NA}/n)^2 z,\ \ v = k\,\mathrm{NA}\, r/n,\ \ k = 2\pi n/\lambda .

``'debye'``
    Scalar non-paraxial Debye integral, as :func:`mcdo.debye.scalar_debye_field`.

``'rw'``
    Full vector Richards-Wolf field, as :func:`mcdo.rw_integrals.compute_integrals`
    with the component formulas of [Rom03]_ Eqs. 2-4, for linear input
    polarization at angle ``psi`` about the beam's own axis.

Rotation convention
-------------------
``'geometric'`` (default) rotates real space: the lab point is transformed into
the beam frame by a true rotation. ``'optical'`` reproduces the rotation written
in [LS02]_ and [CS00]_, applied to the optical coordinates themselves,
:math:`u_r = u\cos\theta - v\sin\theta`, :math:`v_r = v\cos\theta + u\sin\theta`.
The two agree at ``theta = 0`` and ``pi``; at ``pi/2`` they differ because u and v
scale differently with NA. The optical convention exists only for replication.

References
----------
.. [CS00] M. O. Cambaliza & C. Saloma, Opt. Commun. 184, 25 (2000).
.. [LS02] M. Lim & C. Saloma, Opt. Commun. 207, 121 (2002).
.. [LS03] M. Lim & C. Saloma, Appl. Opt. 42, 3398 (2003).
.. [BW99] M. Born & E. Wolf, Principles of Optics, 7th ed. (1999).
.. [Rom03] K. M. Romallosa, J. Bantang & C. Saloma, Phys. Rev. A 68, 033812 (2003).
"""

from __future__ import annotations

import numpy as np
from scipy.special import jv

from .rw_integrals import _simpson_weights


def _beam_frame(x, z, theta, xc, zc):
    """Lab (x, y=0, z) → beam-frame (xb, yb, zb) for a beam rotated about y."""
    dx, dz = x - xc, z - zc
    c, s = np.cos(theta), np.sin(theta)
    zb = s * dx + c * dz
    xb = c * dx - s * dz
    return xb, np.zeros_like(xb), zb


def _to_lab(E, theta):
    """Rotate a beam-frame vector field (3, ...) into the lab frame."""
    c, s = np.cos(theta), np.sin(theta)
    ex, ey, ez = E
    return np.stack([c * ex + s * ez, ey, -s * ex + c * ez])


def _paraxial(rb, zb, k, na, n, n_rho=401, eps=0.0, sa=0.0):
    """Scalar paraxial Debye field with carrier, at beam-frame (r, z).

    ``eps`` is the obstruction ratio: the pupil integral runs over ρ ∈ [ε, 1],
    which is the Babinet difference U_R − U_εR of [CS00]_ Eq. 4. ``sa`` is the
    primary spherical aberration coefficient φ of [LS03]_: the aberration
    function Φ = (φ/100) λ ρ⁴ adds the pupil phase exp(i 2π (φ/100) ρ⁴).
    """
    u = k * (na / n) ** 2 * zb             # (2π/λ) NA² z / n
    v = (k / n) * na * rb                  # (2π/λ) NA r
    rho = np.linspace(eps, 1.0, n_rho)
    w = _simpson_weights(n_rho, 1.0 - eps)
    flat_u, flat_v = u.ravel(), v.ravel()
    phase = np.exp(-0.5j * np.outer(flat_u, rho ** 2))
    bes = jv(0, np.outer(flat_v, rho))
    ab = np.exp(2j * np.pi * (sa / 100.0) * rho ** 4)
    U = 2.0 * (phase * bes) @ (w * rho * ab)
    return (np.exp(1j * k * zb.ravel()) * U).reshape(zb.shape)


def _theta_kernel(rb, zb, k, alpha, n_theta, apodization):
    th = np.linspace(0.0, alpha, n_theta)
    w = _simpson_weights(n_theta, alpha)
    amp = np.sqrt(np.maximum(np.cos(th), 0.0))
    if apodization is not None:
        amp = amp * apodization(th)
    ph = np.exp(1j * k * np.outer(zb.ravel(), np.cos(th)))
    arg = k * np.outer(rb.ravel(), np.sin(th))
    return th, w * amp, ph, arg


def _debye(rb, zb, k, alpha, n_theta=301, apodization=None):
    th, wa, ph, arg = _theta_kernel(rb, zb, k, alpha, n_theta, apodization)
    U = (ph * jv(0, arg)) @ (wa * np.sin(th))
    return U.reshape(zb.shape)


def _rw(rb, phib, zb, k, alpha, psi, n_theta=301, apodization=None):
    """Vector Richards-Wolf field, input linearly polarized at angle psi."""
    th, wa, ph, arg = _theta_kernel(rb, zb, k, alpha, n_theta, apodization)
    st, ct = np.sin(th), np.cos(th)
    I0 = (ph * jv(0, arg)) @ (wa * st * (1 + ct))
    I1 = (ph * jv(1, arg)) @ (wa * st ** 2)
    I2 = (ph * jv(2, arg)) @ (wa * st * (1 - ct))
    phi = (phib - psi).ravel()
    # x-polarized solution [Rom03 Eqs. 2-4] in the frame rotated by psi
    ex = -1j * (I0 + I2 * np.cos(2 * phi))
    ey = -1j * I2 * np.sin(2 * phi)
    ez = -2j * I1 * np.cos(phi)
    c, s = np.cos(psi), np.sin(psi)
    E = np.stack([c * ex - s * ey, s * ex + c * ey, ez])
    return E.reshape((3,) + zb.shape)


def beam_field(x, z, lam, na, n=1.0, theta=0.0, xc=0.0, zc=0.0, model='paraxial',
               rotation='geometric', psi=np.pi / 2, apodization=None, n_theta=301,
               eps=0.0, sa=0.0):
    """Field of one focused beam on lab points (x, y=0, z), in micrometres.

    Returns a complex scalar array for the scalar models and a (3, ...) lab-frame
    vector for ``'rw'``. ``psi`` is the input polarization angle about the beam's
    own axis; the default pi/2 is polarization along the lab y axis for every
    ``theta``, perpendicular to both beam axes, so two beams can interfere fully.
    """
    x, z = np.broadcast_arrays(np.asarray(x, float), np.asarray(z, float))
    k = n * 2.0 * np.pi / lam
    alpha = np.arcsin(na / n)

    if rotation == 'optical':
        if model != 'paraxial':
            raise ValueError("the optical-coordinate rotation is defined only "
                             "for the paraxial model")
        kk = 2.0 * np.pi / lam
        u = kk * na ** 2 * (z - zc)
        v = kk * na * (x - xc)
        c, s = np.cos(theta), np.sin(theta)
        ur, vr = u * c - v * s, v * c + u * s
        zb = ur / (kk * na ** 2)
        rb = np.abs(vr) / (kk * na)
        return _paraxial(rb, zb, k, na, n, eps=eps, sa=sa)

    xb, yb, zb = _beam_frame(x, z, theta, xc, zc)
    rb = np.hypot(xb, yb)
    if model == 'paraxial':
        return _paraxial(rb, zb, k, na, n, eps=eps, sa=sa)
    if model == 'debye':
        return _debye(rb, zb, k, alpha, n_theta, apodization)
    if model == 'rw':
        phib = np.arctan2(yb, xb)
        return _to_lab(_rw(rb, phib, zb, k, alpha, psi, n_theta, apodization), theta)
    raise ValueError(f"unknown model {model!r}")


def intensity(U, vector=None):
    """|U|^2 for a scalar field, |Ex|^2 + |Ey|^2 + |Ez|^2 for a vector field.

    A vector field is a (3, ...) array as returned by ``beam_field(model='rw')``.
    ``vector=None`` infers it from a leading axis of length 3 on an array of two
    or more dimensions; pass ``vector=False`` for a scalar grid with three rows.
    """
    U = np.asarray(U)
    if vector is None:
        vector = U.ndim >= 2 and U.shape[0] == 3
    if vector:
        return np.sum(np.abs(U) ** 2, axis=0)
    return np.abs(U) ** 2


def two_color(U1, U2):
    """Two-color excitation signal I1·I2 (unnormalized)."""
    return intensity(U1) * intensity(U2)


def two_photon(U1, U2):
    """Two-photon excitation signal |U1 + U2|^4 (vector: (|E1 + E2|^2)^2)."""
    return intensity(np.asarray(U1) + np.asarray(U2)) ** 2
