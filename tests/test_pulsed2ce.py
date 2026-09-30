"""Physics tests for pulsed two-color excitation (mcdo.pulsed2ce).

Each test asserts an analytic limit of the time overlap ∫ I1(t) I2(t − Δt) dt.
"""

import numpy as np

from mcdo.pulsed2ce import C_UM_FS, gate_fwhm, spectrum, two_color_cw, two_color_pulsed


def _fwhm(z, p):
    p = p / p.max()
    above = np.nonzero(p >= 0.5)[0]
    i, j = above[0], above[-1]
    zl = z[i - 1] + (z[i] - z[i - 1]) * (0.5 - p[i - 1]) / (p[i] - p[i - 1])
    zr = z[j] + (z[j + 1] - z[j]) * (p[j] - 0.5) / (p[j] - p[j + 1])
    return zr - zl


def test_spectrum_period_covers_the_window():
    w, a, dw = spectrum(0.75, 20.0, t_window=300.0)
    assert 2 * np.pi / dw > 300.0
    assert a[0] / a.max() < 3e-3 and a[-1] / a.max() < 3e-3      # ±3.5 standard deviations


def test_long_pulses_give_the_cw_signal():
    """τ ≫ transit time: the overlap is the CW product, up to a constant."""
    x = np.linspace(-0.8, 0.8, 9)
    z = np.linspace(-3.0, 3.0, 13)
    X, Z = np.meshgrid(x, z)
    for model in ('paraxial', 'rw'):
        p = two_color_pulsed(X, Z, 0.5, tau1=2000.0, model=model)
        c = two_color_cw(X, Z, 0.5, model=model)
        assert np.max(np.abs(p / p.max() - c / c.max())) < 5e-3


def test_counterpropagating_gate_width_and_position():
    """θ = π, low NA (focus much longer than the gate): the signal along z is the
    cross-correlation gate, FWHM c√(τ1² + τ2²)/2n, centred at z = cΔt/2n."""
    z = np.linspace(-8.0, 8.0, 161)
    x = np.zeros_like(z)
    tau, delay = 20.0, 15.0
    p = two_color_pulsed(x, z, 0.1, tau1=tau, model='paraxial', delay=delay)
    c = two_color_cw(x, z, 0.1, model='paraxial')
    g = p / c
    assert abs(_fwhm(z, g) - gate_fwhm(tau)) / gate_fwhm(tau) < 0.02
    assert abs(z[np.argmax(g)] - C_UM_FS * delay / 2) < 0.15


def test_crossed_beams_are_nearly_insensitive_to_20_fs_pulses():
    """θ = π/2: the gate (6 µm across x − z) is far wider than the crossed spot."""
    x = np.linspace(-0.6, 0.6, 13)
    X, Z = np.meshgrid(x, x)
    p = two_color_pulsed(X, Z, 0.5, theta=np.pi / 2, tau1=20.0, model='paraxial')
    c = two_color_cw(X, Z, 0.5, theta=np.pi / 2, model='paraxial')
    assert np.max(np.abs(p / p.max() - c / c.max())) < 0.02
