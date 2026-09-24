"""Physics tests for the two-beam focal fields (mcdo.twobeam) and the
Lim & Saloma (2002) reconstruction built on them.

Each test asserts an analytic limit, a symmetry of the geometry, or a number
the paper states, so a failure flags a physics regression.
"""

from functools import lru_cache

import numpy as np
from scipy.special import j1

from mcdo import linfoot
from mcdo.twobeam import beam_field

NA, N = 0.5, 1.0
L1, L2, L2P = 0.750, 0.656, 0.700            # µm: 2CE pair and the 2PE wavelength

# the paper's 100 × 100 point x–z window, ±1 µm across and ±5 µm along (LS02 p. 126)
DX, DZ = 0.02, 0.1
XW, ZW = np.meshgrid(np.arange(-50, 50) * DX, np.arange(-50, 50) * DZ)
# beam 2 is computed once on a grid 50 steps larger on every side; an offset of
# (ix, iz) steps is then a shift of that grid, as in scripts/fig_lim2002.py
XE, ZE = np.meshgrid(np.arange(-100, 100) * DX, np.arange(-100, 100) * DZ)


@lru_cache(maxsize=None)
def _I1():
    return np.abs(beam_field(XW, ZW, L1, NA, N)) ** 2


@lru_cache(maxsize=None)
def _I2_extended(theta):
    return np.abs(beam_field(XE, ZE, L2, NA, N, theta=theta)) ** 2


def _two_color(theta, ix=0, iz=0):
    """2CE signal with beam 2's focus moved by ix steps of 0.02 µm and iz of 0.1 µm."""
    I2 = _I2_extended(theta)[50 - iz:150 - iz, 50 - ix:150 - ix]
    return _I1() * I2


# ── one beam: analytic limits ─────────────────────────────────────────────

def test_on_axis_intensity_is_sinc_squared():
    """Along the axis the paraxial intensity is sinc²(u/4), u = k NA² z / n."""
    z = np.linspace(-8.0, 8.0, 321)
    I = np.abs(beam_field(np.zeros_like(z), z, L1, NA, N)) ** 2
    u = 2 * np.pi / L1 * NA ** 2 * z
    expected = np.sinc(u / (4 * np.pi)) ** 2          # np.sinc(x) = sin(πx)/(πx)
    assert np.max(np.abs(I / I.max() - expected)) < 1e-6


def test_focal_plane_intensity_is_airy():
    """In the focal plane the intensity is [2 J1(v)/v]², v = 2π NA r / λ."""
    r = np.linspace(1e-6, 3.0, 301)
    I = np.abs(beam_field(r, np.zeros_like(r), L1, NA, N)) ** 2
    v = 2 * np.pi / L1 * NA * r
    assert np.max(np.abs(I / I.max() - (2 * j1(v) / v) ** 2)) < 1e-6


# ── geometry of beam 2 ────────────────────────────────────────────────────

def test_offset_translates_the_field():
    """Moving the focus to O′ = (xc, zc) translates the whole field."""
    xc, zc = 0.3, 1.2
    U = beam_field(XW, ZW, L2, NA, N, theta=np.pi / 2, xc=xc, zc=zc)
    U0 = beam_field(XW - xc, ZW - zc, L2, NA, N, theta=np.pi / 2)
    assert np.allclose(U, U0)


def test_perpendicular_beam_swaps_the_axes():
    """At θ = π/2 beam 2 runs along x: its intensity is beam 1's with x and z swapped."""
    I2 = np.abs(beam_field(XW, ZW, L1, NA, N, theta=np.pi / 2)) ** 2
    I1s = np.abs(beam_field(ZW, XW, L1, NA, N)) ** 2
    assert np.allclose(I2, I1s)


def test_opposed_beam_is_the_mirror_image():
    """At θ = π beam 2 propagates along −z: its intensity is beam 1's mirrored in z."""
    I2 = np.abs(beam_field(XW, ZW, L1, NA, N, theta=np.pi)) ** 2
    I1m = np.abs(beam_field(XW, -ZW, L1, NA, N)) ** 2
    assert np.allclose(I2, I1m)


# ── two colors against one ────────────────────────────────────────────────

def test_energy_condition_gives_350_nm():
    """1/λe = 1/λ1 + 1/λ2 puts 750 + 656 nm at the 350 nm transition, as does 700 + 700 nm."""
    assert abs(1 / (1 / L1 + 1 / L2) - 0.350) < 1e-3
    assert abs(L2P / 2 - 0.350) < 1e-12


def test_opposed_one_color_beams_form_a_standing_wave_two_colors_do_not():
    """At θ = π, 2PE |U1 + U2|² has nodes λ/2 apart near focus; 2CE I1 I2 has none."""
    z = np.linspace(0.0, L2P / 2, 401)
    x = np.zeros_like(z)
    Ua = beam_field(x, z, L2P, NA, N)
    Ub = beam_field(x, z, L2P, NA, N, theta=np.pi)
    s = np.abs(Ua + Ub) ** 2
    assert s.min() < 1e-3 * s.max()                  # a node within one half-wavelength
    I1 = np.abs(beam_field(x, z, L1, NA, N)) ** 2
    I2 = np.abs(beam_field(x, z, L2, NA, N, theta=np.pi)) ** 2
    c = I1 * I2
    assert c.min() > 0.9 * c.max()                   # the product has no fringe


# ── Linfoot's criteria ────────────────────────────────────────────────────

def test_fidelity_equals_twice_correlation_minus_structure():
    """F = 2Q − C for non-negative PSFs (LS02 p. 126); hence F ≥ −C."""
    t = _two_color(np.pi / 2); t = t / t.max()
    a = _two_color(np.pi / 2, ix=20, iz=10); a = a / a.max()   # (0.4, 1.0) µm
    c = linfoot.all_criteria(t, a)
    assert abs(c['F'] - (2 * c['Q'] - c['S'])) < 1e-12
    assert c['F'] >= -c['S']


def test_axial_misalignment_collapses_q_not_c():
    """2CE, θ = π/2, |zc| = 1.33 λ1: the paper's F ≈ −0.8 and "C" ≈ 0 (p. 128).

    F is reproduced; the quantity that falls to zero is Q, while C stays at 1,
    because a shifted spot keeps its sharpness. This is the C/Q label swap.
    """
    t = _two_color(np.pi / 2); t = t / t.max()
    a = _two_color(np.pi / 2, iz=10); a = a / a.max()            # zc = 1.0 µm = 1.33 λ1
    c = linfoot.all_criteria(t, a)
    assert abs(c['F'] - (-0.8)) < 0.15
    assert c['Q'] < 0.1
    assert c['S'] > 0.9


# ── numbers the paper states (LS02 Section 3.2) ───────────────────────────

def test_perpendicular_2ce_peak_falls_as_0p06_xc_squared():
    """F2c^p(π/2) = −0.06 xc² + 1 for in-plane offsets |xc| ≤ 1.33 λ1 (p. 126)."""
    peak0 = _two_color(np.pi / 2).max()
    ix = np.arange(-50, 51, 5)                                     # |xc| ≤ 1.0 µm = 1.33 λ1
    p = [_two_color(np.pi / 2, ix=i).max() / peak0 for i in ix]
    a2 = np.polyfit(ix * DX / L1, p, 2)[0]
    assert abs(a2 - (-0.06)) < 0.01


def test_opposed_2ce_loses_a_fifth_of_its_peak_at_0p37_lambda():
    """At θ = π an in-plane offset of 0.37 λ1 lowers the 2CE peak by about 20% (p. 126)."""
    drop = 1 - _two_color(np.pi, ix=14).max() / _two_color(np.pi).max()   # 0.28 µm = 0.37 λ1
    assert abs(drop - 0.20) < 0.03
