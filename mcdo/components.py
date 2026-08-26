"""Focal intensity from the Richards-Wolf integrals, by field component.

For a linearly x-polarized input the focal field at azimuth ``phi`` is
[Rom03 Eqs. 2-4]::

    Ex = -i (I0 + I2 cos 2phi)
    Ey = -i  I2 sin 2phi
    Ez = -2i I1 cos phi

Averaging the squared modulus over azimuth removes the (arbitrary) choice of
observation direction and leaves two rotationally symmetric quantities:

    ex_only(I0, I1, I2) = <|Ex|^2>          = |I0|^2 + 1/2 |I2|^2
    full(I0, I1, I2)    = <|Ex|^2+|Ey|^2+|Ez|^2>
                                            = |I0|^2 + |I2|^2 + 2 |I1|^2

`ex_only` is the transverse, scalar-like part; `full` is the measurable
intensity including the longitudinal field. On axis I1 = I2 = 0, so the two
coincide there — a useful consistency check — and they separate off axis by an
amount that grows with numerical aperture.

A single-azimuth slice such as ``|I0 - I2|^2`` (the y-axis, where Ey and Ez
vanish) is a cut through one direction rather than a component decomposition;
it is kept only where a published figure is being reproduced.
"""

from __future__ import annotations

import numpy as np


def ex_only(I0, I1=None, I2=None):
    """Azimuthally averaged transverse intensity, ``|I0|^2 + |I2|^2 / 2``."""
    if I2 is None:
        return np.abs(I0) ** 2
    return np.abs(I0) ** 2 + 0.5 * np.abs(I2) ** 2


def full(I0, I1, I2):
    """Azimuthally averaged total intensity, ``|I0|^2 + |I2|^2 + 2|I1|^2``."""
    return np.abs(I0) ** 2 + np.abs(I2) ** 2 + 2 * np.abs(I1) ** 2


def scalar(I0, I1=None, I2=None):
    """Pure scalar (Debye) intensity, ``|I0|^2`` — no polarization at all."""
    return np.abs(I0) ** 2


def y_cut(I0, I1, I2):
    """Intensity along the y-axis, ``|I0 - I2|^2``.

    Reproduction convention only (Romallosa 2003 plots this cut, where Ey and
    Ez vanish). Prefer :func:`ex_only` / :func:`full` for new results.
    """
    return np.abs(I0 - I2) ** 2


def x_cut(I0, I1, I2):
    """Intensity along the x-axis, ``|I0 + I2|^2 + 4|I1|^2`` (carries Ez)."""
    return np.abs(I0 + I2) ** 2 + 4 * np.abs(I1) ** 2
