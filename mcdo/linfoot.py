r"""Linfoot figures of merit for comparing two intensity distributions.

The Linfoot criteria — fidelity :math:`F`, structural content :math:`S`, and
correlation quality :math:`Q` — quantify how a *test* distribution
:math:`a = \{a(m)\}` deviates from a *reference* :math:`r = \{r(m)\}`. In this
package the reference is the CW point-spread function and the test is the
pulsed (or otherwise modified) PSF, both peak-normalized and sampled on a
common grid centred at the geometric focus [Rom03]_.

With :math:`\langle\cdot\rangle` an average over samples,

.. math::

    F = 1 - \frac{\langle (r-a)^2\rangle}{\langle r^2\rangle}, \quad
    S = \frac{\langle a^2\rangle}{\langle r^2\rangle}, \quad
    Q = \frac{\langle |a|\,|r|\rangle}{\langle r^2\rangle},

and the three obey :math:`2Q - S = F`. Perfect reproduction gives
:math:`F = S = Q = 1`; :math:`S > 1` means the test is broader (smeared).

References
----------
.. [Huck85] F. Huck, C. Fales, N. Halyo, R. Samms & K. Stacey, "Image quality
   metrics", J. Opt. Soc. Am. A **2**, 1644 (1985).
.. [Nam98] M. Nazario & C. Saloma, Appl. Opt. **37**, 2953 (1998).
.. [Rom03] K. M. Romallosa, J. Bantang & C. Saloma, "Three-dimensional light
   distribution near the focus of a tightly focused beam of few-cycle optical
   pulses", Phys. Rev. A **68**, 033812 (2003).
"""

import numpy as np


def fidelity(ref, test):
    r"""Linfoot fidelity ``F = 1 - <(r-a)^2> / <r^2>``.

    Measures the overall similarity between reference and test; ``F = 1`` for
    perfect reproduction and decreases as they differ. Equivalent to one minus
    the normalized mean-squared error.

    Parameters
    ----------
    ref : array_like
        Reference distribution :math:`r` (e.g. the CW PSF). Flattened
        internally; any shape accepted.
    test : array_like
        Test distribution :math:`a`, same shape as `ref`.

    Returns
    -------
    float
        The fidelity ``F``, or ``nan`` if ``<r^2> == 0``.
    """
    ref = np.asarray(ref, dtype=float).ravel()
    test = np.asarray(test, dtype=float).ravel()
    denom = np.sum(ref ** 2)
    if denom == 0:
        return np.nan
    return float(1.0 - np.sum((ref - test) ** 2) / denom)


def structural_content(ref, test):
    r"""Linfoot structural content ``S = <a^2> / <r^2>``.

    Compares the relative sharpness/energy of the two profiles. ``S = 1`` for
    perfect reproduction; ``S > 1`` indicates a broader (smeared) test
    distribution and ``S < 1`` a narrower one.

    Parameters
    ----------
    ref : array_like
        Reference distribution :math:`r`. Flattened internally.
    test : array_like
        Test distribution :math:`a`, same shape as `ref`.

    Returns
    -------
    float
        The structural content ``S``, or ``nan`` if ``<r^2> == 0``.
    """
    ref = np.asarray(ref, dtype=float).ravel()
    test = np.asarray(test, dtype=float).ravel()
    denom = np.sum(ref ** 2)
    if denom == 0:
        return np.nan
    return float(np.sum(test ** 2) / denom)


def correlation_quality(ref, test):
    r"""Linfoot correlation quality ``Q = <|a||r|> / <r^2>``.

    Measures alignment of peaks and troughs; ``Q = 1`` for perfectly aligned
    profiles and drops when peaks are misaligned or spurious peaks appear.
    For non-negative intensities ``|a| = a`` and ``|r| = r``.

    Parameters
    ----------
    ref : array_like
        Reference distribution :math:`r`. Flattened internally.
    test : array_like
        Test distribution :math:`a`, same shape as `ref`.

    Returns
    -------
    float
        The correlation quality ``Q``, or ``nan`` if ``<r^2> == 0``.
    """
    ref = np.asarray(ref, dtype=float).ravel()
    test = np.asarray(test, dtype=float).ravel()
    denom = np.sum(ref ** 2)
    if denom == 0:
        return np.nan
    return float(np.sum(np.abs(test) * np.abs(ref)) / denom)


def all_criteria(ref, test):
    """Compute all three Linfoot criteria at once.

    Parameters
    ----------
    ref, test : array_like
        Reference and test distributions (same shape).

    Returns
    -------
    dict
        ``{'F': fidelity, 'S': structural_content, 'Q': correlation_quality}``.

    See Also
    --------
    fidelity, structural_content, correlation_quality
    """
    return {
        "F": fidelity(ref, test),
        "S": structural_content(ref, test),
        "Q": correlation_quality(ref, test),
    }


def linfoot_profile(I_cw, I_pulsed):
    """Linfoot criteria for two intensity profiles, peak-normalized first.

    Convenience wrapper that normalizes each input to its own maximum before
    evaluating the criteria — the convention used throughout [Rom03]_.

    Parameters
    ----------
    I_cw : array_like
        Reference (CW) intensity, any shape; flattened internally.
    I_pulsed : array_like
        Test (pulsed) intensity, same shape as `I_cw`.

    Returns
    -------
    dict
        ``{'F', 'S', 'Q'}`` as in :func:`all_criteria`.
    """
    ref = np.asarray(I_cw, dtype=float).ravel()
    test = np.asarray(I_pulsed, dtype=float).ravel()
    if ref.max() > 0:
        ref = ref / ref.max()
    if test.max() > 0:
        test = test / test.max()
    return all_criteria(ref, test)
