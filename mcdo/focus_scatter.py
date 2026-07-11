r"""Phase 6b — a focused beam through a scattering slab.

A focused Debye-Wolf beam converges to a focus at the origin through a
homogeneous scattering slab :math:`z\in[-d, 0]` (the focus sits at the back
face). Each photon is the converging *ray* of one angular-spectrum component:
unit direction :math:`\hat{k}(\theta,\varphi)` toward the focus, entering the
slab at :math:`(-d\tan\theta\cos\varphi, -d\tan\theta\sin\varphi, -d)` — the
point where the ray through the origin pierces the entrance face.

By construction the focal-plane field splits into

* a **ballistic coherent core** — the clear Debye field with each component
  amplitude-attenuated by Beer-Lambert :math:`\exp(-\mu_s L(\theta)/2)`,
  :math:`L(\theta)=d/\cos\theta` (deterministic given the launcher; carries
  ballistic energy :math:`\langle e^{-\mu_s L}\rangle`), and
* a **diffuse incoherent halo** — the forward-scattered photons, walked through
  the slab by :func:`mcdo.scatter.propagate_slab` (Henyey-Greenstein + MCML
  rotation) and binned on the focal plane.

:math:`\mu_s\to0` recovers the clear focus (halo→0); energy is conserved
(ballistic + forward-scattered + back-scattered + absorbed = 1). The amplitude
:math:`\exp(-\mu_s L/2)` for the coherent core — rather than killing photons —
is what keeps the ballistic *intensity* at Beer-Lambert :math:`\exp(-\mu_s L)`
(killing would double-attenuate it). The scattered light is added incoherently,
i.e. the ensemble-mean diffuse halo (speckle averages out over the trials).
"""

import numpy as np

from .montecarlo import sample_photons, _accumulate_field
from .scatter import propagate_slab

_TRAPZ = np.trapezoid if hasattr(np, "trapezoid") else np.trapz


def slab_path(theta, d):
    r"""Path length :math:`L(\theta)=d/\cos\theta` through a slab of thickness ``d`` (μm)."""
    return d / np.maximum(np.cos(theta), 1e-9)


def ballistic_fraction_analytic(cfg, mu_s, d, apod=None, ngrid=4001):
    r"""Deterministic ballistic energy fraction :math:`\langle e^{-\mu_s d/\cos\theta}\rangle`.

    Averaged over the launcher's angular density
    :math:`p(\theta)\propto|A(\theta)|\sqrt{\cos\theta}\sin\theta` — the
    Beer-Lambert target the Monte-Carlo ballistic count must reproduce.
    """
    th = np.linspace(0.0, cfg.alpha, ngrid)
    A = np.ones_like(th) if apod is None else np.abs(np.asarray(apod(th)))
    p = A * np.sqrt(np.maximum(np.cos(th), 0.0)) * np.sin(th)
    w = np.exp(-mu_s * slab_path(th, d))
    return float(_TRAPZ(p * w, th) / _TRAPZ(p, th))


# layout of the flat per-trial vector returned by focal_scatter_trial:
#   [0] core peak attenuation  I_core(0)/I_clear(0)
#   [1:5] energy partition (ballistic, forward-scattered, back-scattered, absorbed)
#   [5] halo RMS radius (μm)
#   [6 : 6+Lx] ballistic core transverse profile (normalised to the clear peak)
#   [6+Lx : ] diffuse halo radial profile (energy per bin)
_N_SCALAR = 6


def focal_scatter_trial(cfg, n_photons, mu_s, g, d, x_line, halo_r_edges,
                        apod=None, rng=None, mu_a=0.0, n_steps=400):
    r"""One Monte-Carlo trial of the focused beam through the slab.

    Returns a flat float vector (see the module-level layout comment) so the
    multi-trial harness :func:`mcdo.trials.run_trials` can stack trials; use
    :func:`split_trial` to unpack.
    """
    rng = np.random.default_rng() if rng is None else rng
    kx, ky, kz, w = sample_photons(cfg, n_photons, apod=apod, rng=rng)
    mu = np.vstack([kx, ky, kz]) / cfg.k_c                 # unit directions
    theta = np.arccos(np.clip(mu[2], -1.0, 1.0))
    L = slab_path(theta, d)

    # --- ballistic coherent core (transverse profile on the focal plane) -----
    zero = np.zeros_like(x_line)
    w_att = w * np.exp(-0.5 * mu_s * L)                    # amplitude attenuation
    core = np.abs(_accumulate_field(w_att, kx, ky, kz, x_line, zero, zero, 4000)) ** 2
    clear_peak = np.abs(_accumulate_field(w, kx, ky, kz, zero[:1], zero[:1], zero[:1], 4000))[0] ** 2
    peak_atten = core.max() / clear_peak

    # --- scattering walk: energy partition + diffuse halo --------------------
    pos = (-d / mu[2])[None, :] * mu                       # entrance on z=-d face
    pos2, _, nsc, weight, _ = propagate_slab(pos, mu, mu_s, g, (-d, 0.0),
                                             n_steps, rng, mu_a=mu_a)
    ball = nsc == 0
    fwd = (nsc >= 1) & (pos2[2] > -0.5 * d)                # forward exit (z≈0)
    back = (nsc >= 1) & (pos2[2] <= -0.5 * d)              # back exit (z≈-d)
    part = np.array([weight[ball].sum(), weight[fwd].sum(),
                     weight[back].sum(), (1.0 - weight).sum()]) / n_photons

    r_exit = np.hypot(pos2[0, fwd], pos2[1, fwd])
    halo, _ = np.histogram(r_exit, bins=halo_r_edges, weights=weight[fwd])
    halo = halo / n_photons
    halo_rms = (np.sqrt(np.average(r_exit ** 2, weights=weight[fwd]))
                if fwd.any() else 0.0)

    return np.concatenate([[peak_atten], part, [halo_rms],
                           core / clear_peak, halo])


def split_trial(vec, n_x, n_halo):
    """Unpack a focal_scatter_trial vector → dict of named pieces."""
    vec = np.asarray(vec)
    return dict(peak_atten=vec[..., 0],
                partition=vec[..., 1:5],            # ballistic, fwd, back, absorbed
                halo_rms=vec[..., 5],
                core=vec[..., _N_SCALAR:_N_SCALAR + n_x],
                halo=vec[..., _N_SCALAR + n_x:_N_SCALAR + n_x + n_halo])
