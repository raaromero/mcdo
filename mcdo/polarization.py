r"""Focal-plane intensity for different input polarizations.

For the same aplanatic Richards-Wolf integrals :math:`I_0, I_1, I_2`, the
input polarization only changes how the three combine [RW59]_, [Rom03]_.

Linear x-polarized input (the package default; Romallosa's configuration):

.. math::

    |E(v,\phi)|^2 = |I_0 + I_2\cos 2\phi|^2 + |I_2|^2\sin^2 2\phi
                    + 4|I_1|^2\cos^2\phi,

with the meridional cuts
``x-cut (φ=0): |I0+I2|^2 + 4|I1|^2`` (the longitudinal :math:`E_z` fills the
zeros) and ``y-cut (φ=π/2): |I0-I2|^2`` (true zeros — Romallosa Figs 1–2).

Circular input :math:`(\hat{x}+i\hat{y})/\sqrt2` has a φ-independent
time-averaged intensity equal to the azimuthal average,
``|I0|^2 + |I2|^2 + 2|I1|^2`` (no zeros). This was the old ``mcdo``
``polarization='circular'`` default — which is why it could not reproduce
Romallosa's zero structure.

All functions take the complex integrals ``I0, I1, I2`` (any common shape,
e.g. from :func:`mcdo.rw_integrals.compute_integrals`) and return a real
intensity array of that shape.

References
----------
.. [RW59] B. Richards & E. Wolf, Proc. R. Soc. Lond. A **253**, 358 (1959).
.. [Rom03] K. M. Romallosa, J. Bantang & C. Saloma, Phys. Rev. A **68**,
   033812 (2003).
"""

import numpy as np


def linear_x(I0, I1, I2, phi):
    r"""Intensity for linear x-polarized input at azimuth ``phi``.

    Parameters
    ----------
    I0, I1, I2 : ndarray (complex)
        Richards-Wolf integrals, common shape.
    phi : float or ndarray
        Azimuthal observation angle (radians) measured from the polarization
        (x) axis.

    Returns
    -------
    ndarray
        ``|I0 + I2 cos2φ|² + |I2|² sin²2φ + 4|I1|² cos²φ``.
    """
    return (np.abs(I0 + I2 * np.cos(2 * phi)) ** 2
            + np.abs(I2) ** 2 * np.sin(2 * phi) ** 2
            + 4 * np.abs(I1) ** 2 * np.cos(phi) ** 2)


def linear_x_xcut(I0, I1, I2):
    r"""x-axis cut (φ=0) of linear-x input: ``|I0+I2|² + 4|I1|²``.

    Parameters
    ----------
    I0, I1, I2 : ndarray (complex)

    Returns
    -------
    ndarray
        Intensity along the polarization axis (the longitudinal :math:`E_z`
        lobe fills the on-axis zeros).
    """
    return np.abs(I0 + I2) ** 2 + 4 * np.abs(I1) ** 2


def linear_x_ycut(I0, I1, I2):
    r"""y-axis cut (φ=π/2) of linear-x input: ``|I0-I2|²``.

    Parameters
    ----------
    I0, I1, I2 : ndarray (complex)

    Returns
    -------
    ndarray
        Intensity perpendicular to the polarization axis — the cut with true
        zeros used for the Romallosa figures.
    """
    return np.abs(I0 - I2) ** 2


def circular(I0, I1, I2):
    r"""Circular-input (or azimuthally-averaged) intensity: ``|I0|²+|I2|²+2|I1|²``.

    Parameters
    ----------
    I0, I1, I2 : ndarray (complex)

    Returns
    -------
    ndarray
        φ-independent intensity (no zeros).
    """
    return np.abs(I0) ** 2 + np.abs(I2) ** 2 + 2 * np.abs(I1) ** 2
