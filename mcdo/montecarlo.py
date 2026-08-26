r"""Monte-Carlo photon model of the focal field (Phase 6).

Photons are the plane-wave (angular-spectrum) components of the converging
focal field. Each photon carries a launch direction :math:`\hat{k}` in the
focusing cone, a complex weight (apodization, and polarization for the vector
case), and a phase referenced to the geometric focus. The field is their
coherent superposition

.. math::

    \mathbf{U}(P) = \sum_j \mathbf{w}_j\, e^{\,i k\,\hat{k}_j\cdot P}, \qquad
    I(P) = |\mathbf{U}(P)|^2 .

In a clear medium this is a Monte-Carlo evaluation of the (Debye-Wolf)
diffraction integral, so it converges to the deterministic Richards-Wolf
result as :math:`N\to\infty` — the validation gate before scattering
(:mod:`mcdo.scatter`) is added.

Both a **scalar** field (:func:`sample_photons`, :func:`coherent_intensity`)
and the **full vector** field for x-polarized input
(:func:`sample_photons_vector`, :func:`coherent_intensity_vector`) are
provided. An opt-in parallel evaluator (:func:`coherent_intensity_parallel`)
gives results identical to serial up to floating-point round-off.

Direction sampling draws :math:`\theta` from
:math:`p(\theta)\propto |A(\theta)|\sqrt{\cos\theta}\,\sin\theta` (the radiant
amplitude of the converging wave times the solid-angle element) and
:math:`\phi` uniformly; the same pupil object :math:`A(\theta)` used by the
deterministic solver (:mod:`mcdo.apodization`) is reused as the launcher.

References
----------
.. [RW59] B. Richards & E. Wolf, Proc. R. Soc. Lond. A **253**, 358 (1959).
.. [NH06] L. Novotny & B. Hecht, *Principles of Nano-Optics*, Eq. 3.66
   (Cambridge, 2006) — refracted polarization for an aplanatic lens.
"""

import numpy as np


def _direction_cdf(cfg, apod):
    """Build the inverse-CDF sampler for the polar angle θ.

    Returns the θ grid and the normalized CDF of
    ``p(θ) ∝ |A(θ)|·√cosθ·sinθ`` on ``[0, α]``. ``A(θ)`` may be complex (e.g.
    an axicon phase) or vanish on part of the interval (an annular top-hat);
    importance sampling folds ``|A|`` into the density while the phase of
    ``A`` is carried separately in the photon weight, keeping the estimator of
    ``∫ A √cosθ sinθ e^{ik·P} dθ dφ`` unbiased.
    """
    th = np.linspace(0.0, cfg.alpha, 4001)
    Ath = (np.ones_like(th, dtype=complex) if apod is None
           else np.asarray(apod(th), dtype=complex) * np.ones_like(th))
    pdf = np.abs(Ath) * np.sqrt(np.maximum(np.cos(th), 0.0)) * np.sin(th)
    cdf = np.cumsum(pdf)
    cdf -= cdf[0]
    if cdf[-1] <= 0:
        raise ValueError("apodization gives zero pupil throughput")
    cdf /= cdf[-1]
    return th, cdf


def _pupil_phase(apod, theta):
    """Per-photon phase factor ``exp(i·arg A(θ))`` (unity for real/None A)."""
    if apod is None:
        return np.ones(theta.shape, dtype=complex)
    A = np.asarray(apod(theta), dtype=complex) * np.ones(theta.shape)
    return np.exp(1j * np.angle(A))


def sample_photons(cfg, n_photons, apod=None, rng=None, k=None):
    r"""Sample scalar plane-wave photons over the focusing cone.

    Parameters
    ----------
    cfg : SimConfig
        Configuration supplying the wavenumber ``k_c`` and cone half-angle
        ``alpha``.
    n_photons : int
        Number of photons to sample.
    apod : callable, optional
        Pupil illumination ``A(θ)`` (see :mod:`mcdo.apodization`). ``None``
        means uniform. May be complex (carries a pupil phase).
    rng : numpy.random.Generator, optional
        Random generator; a fresh default is created if omitted.
    k : float, optional
        Wavevector magnitude (μm⁻¹). Defaults to ``cfg.k_c`` (centre
        wavelength); pass a per-frequency value for pulsed wavelength sampling
        (the angular density is wavelength-independent — it depends only on
        ``alpha`` and ``A`` — so only the magnitude changes).

    Returns
    -------
    kx, ky, kz : ndarray, shape (n_photons,)
        Wavevector components ``k·k̂`` (μm⁻¹).
    w : ndarray, shape (n_photons,), complex
        Per-photon weights (unit magnitude; carry the pupil phase).
    """
    rng = np.random.default_rng() if rng is None else rng
    th, cdf = _direction_cdf(cfg, apod)
    theta = np.interp(rng.random(n_photons), cdf, th)
    phi = rng.uniform(0.0, 2.0 * np.pi, n_photons)
    k = cfg.k_c if k is None else k
    st, ct = np.sin(theta), np.cos(theta)
    kx = k * st * np.cos(phi)
    ky = k * st * np.sin(phi)
    kz = k * ct
    w = _pupil_phase(apod, theta)
    return kx, ky, kz, w


def sample_photons_vector(cfg, n_photons, apod=None, rng=None):
    r"""Sample vector photons for x-polarized input (full Richards-Wolf field).

    The aplanatic lens maps the input :math:`\hat{x}` at pupil angle
    :math:`(\theta,\phi)` to the refracted unit field [NH06]_

    .. math::

        \mathbf{p} = \big[\cos\theta\cos^2\phi + \sin^2\phi,\;
        (\cos\theta-1)\sin\phi\cos\phi,\; -\sin\theta\cos\phi\big],

    which on azimuthal integration reproduces the Richards-Wolf
    :math:`I_0, I_1, I_2` structure. Accumulating ``Ex, Ey, Ez`` separately and
    summing :math:`|\cdot|^2` (via :func:`coherent_intensity_vector`) gives the
    full vector intensity — e.g. ``|I0-I2|^2`` on the y-axis and
    ``|I0+I2|^2 + 4|I1|^2`` on the x-axis in the clear limit.

    Parameters
    ----------
    cfg : SimConfig
    n_photons : int
    apod : callable, optional
        Pupil illumination ``A(θ)``; ``None`` = uniform.
    rng : numpy.random.Generator, optional

    Returns
    -------
    kx, ky, kz : ndarray, shape (n_photons,)
        Wavevector components ``k·k̂`` (μm⁻¹).
    wvec : tuple of 3 ndarray (complex)
        Per-photon ``(wx, wy, wz)`` = refracted polarization × pupil phase.
    """
    rng = np.random.default_rng() if rng is None else rng
    th, cdf = _direction_cdf(cfg, apod)
    theta = np.interp(rng.random(n_photons), cdf, th)
    phi = rng.uniform(0.0, 2.0 * np.pi, n_photons)
    k = cfg.k_c
    st, ct = np.sin(theta), np.cos(theta)
    cp, sp = np.cos(phi), np.sin(phi)
    kx, ky, kz = k * st * cp, k * st * sp, k * ct
    px = ct * cp ** 2 + sp ** 2           # refracted x-polarization unit vector
    py = (ct - 1.0) * sp * cp
    pz = -st * cp
    phase = _pupil_phase(apod, theta)
    return kx, ky, kz, (px * phase, py * phase, pz * phase)


def _accumulate_field(weights, kx, ky, kz, xf, yf, zf, chunk):
    """Coherent sum ``Σ_j weights_j exp(i k̂_j·P)`` over flat points (helper).

    `weights` is a 1-D complex array (one scalar component). Photons are summed
    in chunks of `chunk` to bound the ``(chunk × N_points)`` phase matrix.
    """
    U = np.zeros(xf.size, dtype=complex)
    for s in range(0, len(kx), chunk):
        e = min(s + chunk, len(kx))
        phase = (np.outer(kx[s:e], xf) + np.outer(ky[s:e], yf)
                 + np.outer(kz[s:e], zf))
        U += weights[s:e] @ np.exp(1j * phase)
    return U


def _flatten_points(x, y, z):
    """Broadcast (x, y, z) to a common shape; return (shape, xf, yf, zf)."""
    x = np.asarray(x, float)
    shape = np.broadcast(x, np.asarray(y, float), np.asarray(z, float)).shape
    xf = np.broadcast_to(x, shape).ravel()
    yf = np.broadcast_to(np.asarray(y, float), shape).ravel()
    zf = np.broadcast_to(np.asarray(z, float), shape).ravel()
    return shape, xf, yf, zf


def coherent_intensity(kx, ky, kz, w, x, y, z, chunk=4000):
    r"""Scalar coherent intensity ``|Σ_j w_j e^{i k̂_j·P}|²`` at points P.

    Parameters
    ----------
    kx, ky, kz : ndarray, shape (N,)
        Photon wavevector components (μm⁻¹).
    w : ndarray, shape (N,), complex
        Photon weights (from :func:`sample_photons`).
    x, y, z : array_like
        Observation coordinates (μm), broadcast to a common shape.
    chunk : int, optional
        Photons processed per block (memory/speed trade-off).

    Returns
    -------
    ndarray
        Real intensity with the broadcast shape of ``(x, y, z)``
        (un-normalized).
    """
    shape, xf, yf, zf = _flatten_points(x, y, z)
    U = _accumulate_field(w, kx, ky, kz, xf, yf, zf, chunk)
    return (np.abs(U) ** 2).reshape(shape)


def coherent_intensity_vector(kx, ky, kz, wvec, x, y, z, chunk=4000):
    r"""Full vector intensity ``|Ex|² + |Ey|² + |Ez|²`` from vector photons.

    Parameters
    ----------
    kx, ky, kz : ndarray, shape (N,)
        Photon wavevector components (μm⁻¹).
    wvec : tuple of 3 ndarray (complex)
        Per-photon ``(wx, wy, wz)`` from :func:`sample_photons_vector`.
    x, y, z : array_like
        Observation coordinates (μm), broadcast to a common shape.
    chunk : int, optional
        Photons processed per block.

    Returns
    -------
    ndarray
        Real total intensity with the broadcast shape of ``(x, y, z)``.
    """
    shape, xf, yf, zf = _flatten_points(x, y, z)
    I = sum(np.abs(_accumulate_field(wc, kx, ky, kz, xf, yf, zf, chunk)) ** 2
            for wc in wvec)
    return I.reshape(shape)


def mc_focal_intensity(cfg, x, y, z, n_photons, apod=None, rng=None,
                       normalize=True):
    """Sample scalar photons and evaluate the focal intensity in one call.

    Parameters
    ----------
    cfg : SimConfig
    x, y, z : array_like
        Observation coordinates (μm).
    n_photons : int
    apod : callable, optional
        Pupil illumination ``A(θ)``; ``None`` = uniform.
    rng : numpy.random.Generator, optional
    normalize : bool, optional
        Divide by the peak value (default True).

    Returns
    -------
    ndarray
        Focal intensity over ``(x, y, z)``.

    See Also
    --------
    sample_photons, coherent_intensity
    """
    kx, ky, kz, w = sample_photons(cfg, n_photons, apod=apod, rng=rng)
    I = coherent_intensity(kx, ky, kz, w, x, y, z)
    if normalize and I.max() > 0:
        I = I / I.max()
    return I


def mc_pulsed_intensity(cfg, x, y, z, n_photons, apod=None, rng=None,
                        normalize=True):
    r"""Pulsed focal intensity by per-photon **wavelength** sampling (Eq. 10).

    The physical, broadband-ensemble counterpart of the deterministic spectral
    sum. Each photon's wavelength is drawn from the power spectrum
    :math:`|E(\omega)|^2`: the photon budget is allocated across the spectral
    nodes by a multinomial draw with probabilities :math:`\propto |E(\omega)|^2`.
    Within one wavelength the photons interfere **coherently**; different
    wavelengths add **incoherently** — i.e. the time-integrated intensity

    .. math::

        I(P) = \int |E(\omega)|^2\,|U(P,\omega)|^2\, d\omega ,

    with :math:`U(P,\omega)` the (normalised) monochromatic field. As
    :math:`N\to\infty` this converges to the deterministic
    :func:`mcdo.intensity.pulsed_intensity`; for CW (``cfg.tau`` infinite) it
    falls back to the monochromatic :func:`mc_focal_intensity`.

    Why a separate routine from the deterministic sum? They have different uses:
    the deterministic sum is exact and cheap in a **clear** medium (the spectrum
    factors out); per-photon wavelength sampling is what a **scattering** medium
    needs, where each photon's :math:`\lambda` sets its own :math:`\mu_s(\lambda)`
    and phase function and the spectrum can no longer be factored out.

    Parameters
    ----------
    cfg : SimConfig
        Must carry the pulse width ``tau`` and the node count ``N_freq``.
    x, y, z : array_like
        Observation coordinates (μm).
    n_photons : int
        Total photons, distributed across wavelengths ``∝ |E(ω)|²``.
    apod : callable, optional
        Pupil illumination ``A(θ)``; ``None`` = uniform.
    rng : numpy.random.Generator, optional
    normalize : bool, optional
        Divide by the peak (default True).

    Returns
    -------
    ndarray
        Scalar pulsed intensity over ``(x, y, z)``.

    See Also
    --------
    mc_focal_intensity, mcdo.intensity.pulsed_intensity
    """
    rng = np.random.default_rng() if rng is None else rng
    if np.isinf(cfg.tau):                       # CW → single wavelength
        return mc_focal_intensity(cfg, x, y, z, n_photons, apod=apod, rng=rng,
                                  normalize=normalize)
    omegas = cfg.omega_grid()
    W = np.where(omegas > 0, cfg.spectral_power(omegas), 0.0)
    counts = rng.multinomial(int(n_photons), W / W.sum())   # sample λ ∝ |E(ω)|²
    shape, xf, yf, zf = _flatten_points(x, y, z)
    I = np.zeros(xf.size)
    for omega, n_m, w_m in zip(omegas, counts, W):
        if n_m == 0:
            continue
        kx, ky, kz, wt = sample_photons(cfg, int(n_m), apod=apod, rng=rng,
                                        k=cfg.k_for_omega(omega))
        U = _accumulate_field(wt, kx, ky, kz, xf, yf, zf, 4000)
        I += w_m * (np.abs(U) ** 2) / (n_m ** 2)   # |Û(ω)|² weighted by |E(ω)|²
    I = I.reshape(shape)
    if normalize and I.max() > 0:
        I = I / I.max()
    return I


# ---------------------------------------------------------------------------
# Optional parallelism (opt-in).
# ---------------------------------------------------------------------------

def _partial_field(args):
    """Worker entry point: partial coherent field for a photon subset."""
    kx, ky, kz, w, xf, yf, zf = args
    return _accumulate_field(w, kx, ky, kz, xf, yf, zf, 4000)


def coherent_intensity_parallel(kx, ky, kz, w, x, y, z, n_jobs=1):
    r"""Scalar coherent intensity, optionally split over ``n_jobs`` processes.

    Because the coherent field is an additive sum over photons, partitioning
    the photons across workers and summing the partial complex fields is
    mathematically identical to the serial result — only the summation order
    differs, so results agree to floating-point round-off (~1e-15 relative).

    Parameters
    ----------
    kx, ky, kz : ndarray, shape (N,)
    w : ndarray, shape (N,), complex
    x, y, z : array_like
        Observation coordinates (μm).
    n_jobs : int, optional
        Number of worker processes. ``n_jobs=1`` (default) is the serial path.
        Callers using ``n_jobs>1`` must guard the entry point with
        ``if __name__ == "__main__":`` (multiprocessing ``spawn`` re-imports).

    Returns
    -------
    ndarray
        Real intensity with the broadcast shape of ``(x, y, z)``.

    See Also
    --------
    coherent_intensity
    """
    shape, xf, yf, zf = _flatten_points(x, y, z)
    if n_jobs <= 1:
        U = _accumulate_field(w, kx, ky, kz, xf, yf, zf, 4000)
        return (np.abs(U) ** 2).reshape(shape)

    import multiprocessing as mp
    idx = np.array_split(np.arange(len(kx)), n_jobs)
    tasks = [(kx[i], ky[i], kz[i], w[i], xf, yf, zf) for i in idx]
    with mp.Pool(n_jobs) as pool:
        partials = pool.map(_partial_field, tasks)
    U = np.sum(partials, axis=0)
    return (np.abs(U) ** 2).reshape(shape)
