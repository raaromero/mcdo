r"""Two-color excitation with pulses: photon pairs from two focused pulses.

A 2CE event takes one photon from each pulse, ω_a from beam 1 and ω_b from beam 2,
and excites the transition ω_e when ω_a + ω_b = ω_e. The two-photon amplitude adds
these pairs with their phases, and the signal is its square
(:func:`two_color_pairs`, a transition narrower than the pulse spectra):

.. math::

    A(P) = \int \tilde{E}_1(P, \omega)\, \tilde{E}_2(P, \omega_e - \omega)\, d\omega,
    \qquad F_{2c}(P) \propto |A(P)|^2 .

For Gaussian pulses |A|² is the probability that a pair reaches ω_e times the
overlap in time of the two pulses, times the continuous-beam product I₁I₂.
Summed over all transition frequencies (a flat absorption band) |A|² gives the
time overlap of the two intensities at a delay Δt (Parseval), the signal of
[LS02]_ Eq. 2 with time-dependent intensities (:func:`two_color_pulsed`):

.. math::

    F_{2c}(P, \Delta t) = \kappa \int I_1(P, t)\, I_2(P, t - \Delta t)\, dt .

This is not the product of the time-integrated intensities. Each intensity is
built coherently from its spectrum,

.. math::

    \mathbf{E}(P, t) = \int a(\omega)\, \frac{\omega}{\omega_0}\,
        \mathbf{E}_\omega(P)\, e^{-i(\omega - \omega_0) t}\, d\omega ,

with :math:`\mathbf{E}_\omega` the monochromatic focal field of
:func:`mcdo.twobeam.beam_field` (which carries the propagation phase, so each
pulse travels through the focus at c/n and reaches its geometric focus at
t = 0), :math:`\omega/\omega_0` the frequency prefactor of the Debye integral,
and the carrier :math:`e^{-i\omega_0 t}` dropped since only |E|² enters.
The input pulse is transform-limited with intensity FWHM τ, so

.. math::

    a(\omega) = \exp\!\left[-\frac{(\omega - \omega_0)^2 \tau^2}{8 \ln 2}\right] .

Frequencies are sampled uniformly in ω (not in λ) over ±3.5 spectral standard
deviations, finely enough that the implied period 2π/δω exceeds the time window,
so the discrete sum reproduces the continuous overlap.

Physics this captures, with the scale to expect:

* θ = π: the pulses meet head on, so the overlap is confined along z to a gate
  of FWHM √2 c τ / (2n) centred at z = c Δt / (2n) (4.2 µm for τ = 20 fs in air).
* θ = π/2: the gate lies across the diagonal x − z, of width c τ / n (6 µm for
  20 fs), far wider than the crossed spot; pulses barely change it.
* The spread of spot sizes over the bandwidth (a few percent at 20 fs).

The two colours are kept as separate beams, as in [LS02]_: the signal is the
I₁I₂ term only. That holds while their spectra do not overlap (τ ≳ 8 fs for
750 and 656 nm).

.. [LS02] M. Lim & C. Saloma, Opt. Commun. 207, 121 (2002).
"""

from __future__ import annotations

import numpy as np

from .twobeam import beam_field, intensity

C_UM_FS = 0.299792458                      # speed of light, µm/fs


def spectrum(lam0, tau, n_min=21, t_window=None):
    """Frequencies (rad/fs), amplitudes a(ω)·ω/ω0 and step for a pulse of intensity FWHM τ (fs)."""
    w0 = 2 * np.pi * C_UM_FS / lam0
    s = 2 * np.sqrt(np.log(2)) / tau       # a(ω) = exp(−(ω−ω0)²/2s²), rad/fs
    span = 7.0 * s
    n = n_min
    if t_window is not None:               # period 2π/δω must exceed the whole time window
        n = max(n, int(np.ceil(span * 1.25 * t_window / (2 * np.pi))) + 1)
    w = w0 + np.linspace(-span / 2, span / 2, n)
    a = np.exp(-(w - w0) ** 2 * tau ** 2 / (8 * np.log(2))) * w / w0
    return w, a, w[1] - w[0]


def _fields(x, z, lam0, tau, t_window, na, n, theta, xc, zc, model, psi, apodization):
    w, a, dw = spectrum(lam0, tau, t_window=t_window)
    kw = {} if model == 'paraxial' else dict(model=model)
    if model == 'rw':
        kw['psi'] = psi
    E = np.stack([beam_field(x, z, 2 * np.pi * C_UM_FS / wm, na, n, theta=theta, xc=xc, zc=zc,
                             apodization=apodization, **kw) for wm in w])       # (n_ω, [3,] ...)
    return w - w.mean(), a * dw, E


def _intensity_t(dw, c, E, t):
    """|E(P, t)|² at one time from the spectral samples."""
    ph = c * np.exp(-1j * dw * t)
    return intensity(np.tensordot(ph, E, axes=(0, 0)))


def two_color_pulsed(x, z, na, n=1.0, theta=np.pi, xc=0.0, zc=0.0, tau1=20.0, tau2=None, delay=0.0,
                     lam1=0.750, lam2=0.656, model='rw', apodization=None, dt=None):
    """Pulsed 2CE signal ∫ I1(P,t) I2(P,t−Δt) dt on lab points (x, z), µm and fs.

    Beam 2's pulse arrives ``delay`` after beam 1's; ``delay`` may be an array, in
    which case the result has a leading delay axis and the fields are computed once.
    For ``model='rw'`` each beam is unpolarized: its intensity is averaged over two
    perpendicular input polarizations.
    """
    tau2 = tau1 if tau2 is None else tau2
    delays = np.atleast_1d(np.asarray(delay, float))
    x, z = np.broadcast_arrays(np.asarray(x, float), np.asarray(z, float))
    reach = n * (np.sqrt(np.max(x ** 2 + z ** 2)) + np.hypot(xc, zc)) / C_UM_FS   # transit through the grid
    tw = 3 * max(tau1, tau2) + reach + np.abs(delays).max()            # half-width of the time window
    dt = min(tau1, tau2) / 15 if dt is None else dt
    t = np.arange(-tw, tw + dt / 2, dt)
    psis = (0.0, np.pi / 2) if model == 'rw' else (None,)

    def beam(lam, tau, th, a, b):
        return [_fields(x, z, lam, tau, 2 * tw, na, n, th, a, b, model, p, apodization) for p in psis]

    B1, B2 = beam(lam1, tau1, 0.0, 0.0, 0.0), beam(lam2, tau2, theta, xc, zc)
    S = np.zeros((len(delays),) + x.shape)
    for tt in t:
        I1 = sum(_intensity_t(*f, tt) for f in B1) / len(B1)
        for i, d in enumerate(delays):
            S[i] += I1 * (sum(_intensity_t(*f, tt - d) for f in B2) / len(B2)) * dt
    return S if np.ndim(delay) else S[0]


def pair_grid(lam1=0.750, lam2=0.656, tau1=20.0, tau2=None, n_pairs=41, span=10.0, detuning=0.0):
    """The photon pairs that reach the transition: ω_a from beam 1 and ω_b = ω_e − ω_a from beam 2.

    The transition sits at ω_e = ω_1 + ω_2 + δ (δ = ``detuning``, rad/fs). Each amplitude spectrum has unit
    energy, ∫|a_i(ω)|² dω = 1, and carries the Debye prefactor ω/ω_i. Their product a_1(ω_a) a_2(ω_e − ω_a) is
    a Gaussian in ω_a of standard deviation s_p = s_1 s_2 / √(s_1² + s_2²) (s_i = 2√ln2/τ_i); ``n_pairs``
    samples cover ``span`` standard deviations of it. Returns ω_a, ω_b, the pair weights a_1 a_2 dω and the
    offsets u = ω_a − ω_1.
    """
    tau2 = tau1 if tau2 is None else tau2
    w1, w2 = 2 * np.pi * C_UM_FS / lam1, 2 * np.pi * C_UM_FS / lam2
    s1, s2 = 2 * np.sqrt(np.log(2)) / tau1, 2 * np.sqrt(np.log(2)) / tau2
    sp = s1 * s2 / np.hypot(s1, s2)
    u = detuning * s1 ** 2 / (s1 ** 2 + s2 ** 2) + np.linspace(-span / 2, span / 2, n_pairs) * sp
    wa, wb = w1 + u, w2 + detuning - u
    a1 = (np.pi * s1 ** 2) ** -0.25 * np.exp(-u ** 2 / (2 * s1 ** 2)) * wa / w1
    a2 = (np.pi * s2 ** 2) ** -0.25 * np.exp(-(detuning - u) ** 2 / (2 * s2 ** 2)) * wb / w2
    return wa, wb, a1 * a2 * (u[1] - u[0]), u


def pair_signal(c, E1, E2, vector):
    """|A|², A = Σ_k c_k E1_k E2_k over the pairs k, for scalar fields (n_pairs, ...); Σ_ij |A_ij|² over the
    field components for vector fields (n_pairs, 3, ...)."""
    if not vector:
        return np.abs(np.tensordot(c, E1 * E2, axes=(0, 0))) ** 2
    A = np.einsum('k,kip,kjp->ijp', c, E1.reshape(E1.shape[:2] + (-1,)), E2.reshape(E2.shape[:2] + (-1,)))
    return (np.abs(A) ** 2).sum(axis=(0, 1)).reshape(E1.shape[2:])


def two_color_pairs(x, z, na, n=1.0, theta=np.pi, xc=0.0, zc=0.0, tau1=20.0, tau2=None, delay=0.0,
                    lam1=0.750, lam2=0.656, model='rw', apodization=None, n_pairs=41, span=10.0, detuning=0.0):
    """Pulsed 2CE signal from the photon pairs that reach the transition, ω_a + ω_b = ω_e (narrow line).

    The two-photon amplitude at P sums every pair coherently,

        A(P) = ∫ Ẽ_1(P, ω) Ẽ_2(P, ω_e − ω) e^{i(ω_e − ω)Δt} dω,      F_2c(P) ∝ |A(P)|²,

    with Ẽ_i(P, ω) = a_i(ω) E_ω(P) (unit-energy spectra, :func:`pair_grid`). Beam 2's pulse arrives ``delay``
    after beam 1's (a phase ω_b Δt on each of its photons). For ``model='rw'`` the components add as
    Σ_ij |A_ij|² and each beam is unpolarized (average over two perpendicular input polarizations), so a long
    pulse gives the continuous-wave product I_1 I_2. Integrating |A|² over ω_e gives the time overlap
    ∫ I_1 I_2 dt of :func:`two_color_pulsed` (all pairs, Parseval).
    """
    wa, wb, wt, u = pair_grid(lam1, lam2, tau1, tau2, n_pairs, span, detuning)
    delays = np.atleast_1d(np.asarray(delay, float))
    x, z = np.broadcast_arrays(np.asarray(x, float), np.asarray(z, float))
    psis = (0.0, np.pi / 2) if model == 'rw' else (None,)

    def fields(ws, th, a, b, psi):
        kw = {} if model == 'paraxial' else dict(model=model)
        if model == 'rw':
            kw['psi'] = psi
        return np.stack([beam_field(x, z, 2 * np.pi * C_UM_FS / w, na, n, theta=th, xc=a, zc=b,
                                    apodization=apodization, **kw) for w in ws])
    F1 = [fields(wa, 0.0, 0.0, 0.0, p) for p in psis]
    F2 = [fields(wb, theta, xc, zc, p) for p in psis]
    S = np.zeros((len(delays),) + x.shape)
    for i, d in enumerate(delays):
        c = wt * np.exp(-1j * u * d)                 # e^{iω_bΔt} up to a common phase
        S[i] = sum(pair_signal(c, E1, E2, model == 'rw') for E1 in F1 for E2 in F2) / (len(F1) * len(F2))
    return S if np.ndim(delay) else S[0]


def two_color_cw(x, z, na, n=1.0, theta=np.pi, xc=0.0, zc=0.0, lam1=0.750, lam2=0.656, model='rw',
                 apodization=None):
    """The continuous-wave signal I1·I2 with the same conventions, for comparison."""
    def I(lam, th, a, b):
        if model == 'rw':
            return 0.5 * sum(intensity(beam_field(x, z, lam, na, n, theta=th, xc=a, zc=b, model='rw', psi=p,
                                                  apodization=apodization)) for p in (0.0, np.pi / 2))
        kw = {} if model == 'paraxial' else dict(model=model)
        return intensity(beam_field(x, z, lam, na, n, theta=th, xc=a, zc=b, apodization=apodization, **kw))
    return I(lam1, 0.0, 0.0, 0.0) * I(lam2, theta, xc, zc)


def gate_fwhm(tau1, tau2=None, n=1.0, theta=np.pi):
    """Width of the time-overlap gate for Gaussian pulses: along z at θ = π, across x − z at θ = π/2 (µm)."""
    tau2 = tau1 if tau2 is None else tau2
    tc = np.hypot(tau1, tau2)               # FWHM of the cross-correlation of two Gaussian intensities
    return C_UM_FS * tc / (2 * n) if np.isclose(theta, np.pi) else C_UM_FS * tc / (np.sqrt(2) * n)


def closed_form_2ce(I1, I2, z_b1, z_b2, delay, tau1, tau2=None, n=1.0):
    """Closed form of the pulsed 2CE signal for transform-limited Gaussian pulses (envelope approximation).

    Pulse i reaches point P at t_i = n z_bi / c (z_bi = distance along beam i from its focus), pulse 2 a time
    ``delay`` later. The time overlap of two Gaussian intensities of FWHM τ1, τ2 is a Gaussian of FWHM
    √(τ1² + τ2²) in their arrival-time difference, so

        F_2c(P, Δt) ∝ I_1(P) I_2(P) exp[−4 ln2 (n (z_b1 − z_b2)/c − Δt)² / (τ1² + τ2²)]

    with I_1, I_2 the continuous-beam intensities. It neglects the change of spot size across the spectrum.
    """
    tau2 = tau1 if tau2 is None else tau2
    s = n * (np.asarray(z_b1) - np.asarray(z_b2)) / C_UM_FS - delay
    return I1 * I2 * np.exp(-4 * np.log(2) * s ** 2 / (tau1 ** 2 + tau2 ** 2))
