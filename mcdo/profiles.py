"""Measurements read off a focal profile, and where they stop meaning what they
appear to mean.

`first_minimum` finds the first upturn in a transverse profile. At high aperture
that upturn is not always the transverse null: the longitudinal field fills the
null, and the search then locks onto structure in the longitudinal lobe,
returning a number that looks like the same quantity while measuring a different
feature. At numerical aperture 1.2 the reported minimum jumps from 0.32 to 0.59
micrometres between obstruction ratios 0.9 and 0.99, where the longitudinal
share of the intensity at that point is 0.80. The transverse field alone is
monotonic across the same range, so the jump is in the metric, not the physics.

There is deliberately no radius guard here. A cutoff on distance cannot separate
the two cases: measured against each profile's own width, the spurious minimum
at aperture 1.2 sits at 1.83 widths while the genuine minimum of an unobstructed
truncated Gaussian sits further out still, at 2.27. Distance is not the
discriminator - whether the transverse field nulls there is, and that needs the
component integrals, not a total-intensity profile.

Callers working at high aperture with thin rings should therefore treat a first
minimum as a number that may be describing the longitudinal lobe, and check the
decomposition before quoting it. `scripts/verify_annular_baseline._sidelobe`
applies a radius cutoff for this reason; by the argument above that cutoff also
rejects the genuine Gaussian minimum, so its not-a-number means "not checked",
not "not present".
"""

import numpy as np


def airy_radius(wavelength, X_NA):
    """First dark ring of the Airy pattern, 0.61 lambda / NA  [B&W99 8.5.2]."""
    return 0.61 * wavelength / X_NA


def first_minimum(r, intensity):
    """Radius and depth of the first upturn in a transverse profile.

    Returns
    -------
    (radius_um, fraction_of_peak), or (nan, nan) if the profile is monotonic.
    """
    r = np.asarray(r, dtype=float)
    y = np.asarray(intensity, dtype=float)
    y = y / y.max()
    rising = np.where(np.diff(y) > 0)[0]
    if not len(rising):
        return float("nan"), float("nan")
    idx = int(rising[0])
    return float(r[idx]), float(y[idx])


def longitudinal_share(I0, I1, I2):
    """Fraction of the phi-averaged intensity carried by the longitudinal field.

    This is the quantity that says whether a first minimum is a transverse null
    or longitudinal structure. Near 0.8 the minimum is not describing the
    transverse pattern at all.
    """
    ex = np.abs(I0) ** 2 + np.abs(I2) ** 2 / 2.0
    ey = np.abs(I2) ** 2 / 2.0
    ez = 2.0 * np.abs(I1) ** 2
    return ez / (ex + ey + ez)
