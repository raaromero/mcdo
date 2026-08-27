r"""Scattering kernel for Phase 6b — free paths, Henyey-Greenstein deflection,
and the correct local-frame direction update.

A photon is advected in straight steps; between steps it may scatter, sampling
a deflection from the Henyey-Greenstein phase function and rotating its
direction *vector* in its own local frame (the MCML update [MCML95]_). This is
the physically correct form of this operation (a common failure mode is a
issue C1 was a scalar angle addition with an elevation/polar convention
scalar/vector mismatch); rotating the vector
composes rotations correctly on the sphere.

References
----------
.. [HG41] L. C. Henyey & J. L. Greenstein, "Diffuse radiation in the galaxy",
   Astrophys. J. **93**, 70 (1941).
.. [MCML95] L. Wang, S. L. Jacques & L. Zheng, "MCML — Monte Carlo modeling of
   light transport in multi-layered tissues", Comput. Methods Programs Biomed.
   **47**, 131 (1995).
"""

import numpy as np


def hg_sample(g, n, rng):
    r"""Sample deflection angles from the Henyey-Greenstein phase function.

    The polar deflection is drawn by inverse-CDF sampling of

    .. math::

        \cos\theta = \frac{1}{2g}\Big[1 + g^2 -
        \Big(\frac{1-g^2}{1-g+2g\xi}\Big)^2\Big], \quad \xi\sim U(0,1),

    reducing to the isotropic ``cosθ = 2ξ−1`` when ``g = 0``. The azimuth is
    uniform, ``φ = 2πη``.

    Parameters
    ----------
    g : float or array_like
        Anisotropy ``⟨cosθ⟩`` in ``[0, 1)``. A scalar is broadcast to all
        photons; an array must have length `n` (per-photon anisotropy).
    n : int
        Number of deflections to sample.
    rng : numpy.random.Generator
        Random generator.

    Returns
    -------
    cos_t : ndarray, shape (n,)
        Cosine of the polar deflection angle, clipped to ``[-1, 1]``.
    phi : ndarray, shape (n,)
        Azimuthal angle in ``[0, 2π)``.
    """
    g = np.atleast_1d(np.asarray(g, float))
    if g.size == 1:
        g = np.full(n, g[0])
    xi = rng.random(n)
    cos_t = np.empty(n)
    iso = g == 0.0
    cos_t[iso] = 2.0 * xi[iso] - 1.0
    gg = g[~iso]
    cos_t[~iso] = (1 + gg**2
                   - ((1 - gg**2) / (1 - gg + 2 * gg * xi[~iso]))**2) / (2 * gg)
    cos_t = np.clip(cos_t, -1.0, 1.0)
    phi = 2 * np.pi * rng.random(n)
    return cos_t, phi


def rotate(mu, cos_t, phi):
    r"""Rotate unit directions by a deflection ``(cosθ, φ)`` in each local frame.

    Applies the MCML scattering update [MCML95]_: the new direction makes polar
    angle ``θ`` with the old direction and azimuth ``φ`` about it. Near the
    poles (``|μ_z| > 0.99999``) the degenerate simple frame is used.

    Parameters
    ----------
    mu : ndarray, shape (3, N)
        Current unit direction cosines (columns are photons).
    cos_t : ndarray, shape (N,)
        Cosine of the polar deflection (e.g. from :func:`hg_sample`).
    phi : ndarray, shape (N,)
        Azimuthal scattering angle.

    Returns
    -------
    ndarray, shape (3, N)
        New unit direction cosines (renormalized).
    """
    mu = np.asarray(mu, float)
    ux, uy, uz = mu[0], mu[1], mu[2]
    sin_t = np.sqrt(np.clip(1 - cos_t**2, 0, 1))
    cphi, sphi = np.cos(phi), np.sin(phi)
    out = np.empty_like(mu)

    near_pole = np.abs(uz) > 0.99999
    s = ~near_pole
    den = np.sqrt(np.clip(1 - uz[s]**2, 1e-300, None))
    out[0, s] = sin_t[s] * (ux[s]*uz[s]*cphi[s] - uy[s]*sphi[s]) / den + ux[s]*cos_t[s]
    out[1, s] = sin_t[s] * (uy[s]*uz[s]*cphi[s] + ux[s]*sphi[s]) / den + uy[s]*cos_t[s]
    out[2, s] = -sin_t[s]*cphi[s]*den + uz[s]*cos_t[s]
    p = near_pole
    sgn = np.sign(uz[p]); sgn[sgn == 0] = 1.0
    out[0, p] = sin_t[p]*cphi[p]
    out[1, p] = sin_t[p]*sphi[p]
    out[2, p] = sgn*cos_t[p]
    out /= np.sqrt(np.sum(out**2, axis=0))   # guard against drift
    return out


def propagate_slab(pos, mu, mu_s, g, z_slab, n_steps, rng, mu_a=0.0):
    r"""March photons through a homogeneous scattering slab.

    Each alive photon samples a free path :math:`s = -\ln\xi/\mu_s`. If that
    path would carry it past the near/far slab face it exits unscattered for
    that segment; otherwise it advances to the event point and scatters
    (Henyey-Greenstein deflection + local-frame rotation). The ballistic
    (unscattered) fraction therefore follows Beer-Lambert, ``exp(-μ_s L)``.

    Parameters
    ----------
    pos : ndarray, shape (3, N)
        Initial photon positions (μm); photons should start at/within the slab.
    mu : ndarray, shape (3, N)
        Initial unit direction cosines.
    mu_s : float
        Scattering coefficient (μm⁻¹); ``0`` disables scattering.
    g : float or array_like
        Henyey-Greenstein anisotropy (see :func:`hg_sample`).
    z_slab : tuple of float
        Slab extent ``(z0, z1)`` along the optic axis (μm).
    n_steps : int
        Maximum number of scatter steps to iterate.
    rng : numpy.random.Generator
        Random generator.
    mu_a : float, optional
        Absorption coefficient (μm⁻¹); attenuates the photon weight along the
        path. Default 0 (non-absorbing).

    Returns
    -------
    pos : ndarray, shape (3, N)
        Final positions.
    mu : ndarray, shape (3, N)
        Final direction cosines.
    n_scatter : ndarray, shape (N,), int
        Number of scattering events per photon (0 = ballistic).
    weight : ndarray, shape (N,)
        Surviving weight from absorption (1 if ``mu_a = 0``).
    path : ndarray, shape (N,)
        Cumulative path length travelled inside the slab (μm).
    """
    pos = pos.copy().astype(float)
    mu = mu.copy().astype(float)
    N = pos.shape[1]
    n_scatter = np.zeros(N, int)
    weight = np.ones(N)
    path = np.zeros(N)
    z0, z1 = z_slab
    alive = (pos[2] >= z0) & (pos[2] <= z1)
    for _ in range(n_steps):
        if not alive.any():
            break
        idx = np.where(alive)[0]
        s = (-np.log(rng.random(idx.size)) / mu_s if mu_s > 0
             else np.full(idx.size, np.inf))
        muz = mu[2, idx]
        pz = pos[2, idx]
        # signed distance to the boundary the photon is heading toward
        with np.errstate(divide='ignore', invalid='ignore'):
            d = np.where(muz > 0, (z1 - pz) / muz,
                         np.where(muz < 0, (z0 - pz) / muz, np.inf))
        d = np.where(d > 0, d, np.inf)
        exits = s >= d                      # leaves the slab before next scatter
        adv = np.where(exits, d, s)
        pos[:, idx] += mu[:, idx] * adv
        path[idx] += adv
        if mu_a > 0:
            weight[idx] *= np.exp(-mu_a * adv)
        sc = ~exits
        if sc.any():
            scidx = idx[sc]
            cos_t, phi = hg_sample(g, int(scidx.size), rng)
            mu[:, scidx] = rotate(mu[:, scidx], cos_t, phi)
            n_scatter[scidx] += 1
        alive[idx[exits]] = False
    return pos, mu, n_scatter, weight, path
