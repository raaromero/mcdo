"""One framework from the focus of one beam (Romallosa et al. 2003) to two-color excitation (Cambaliza & Saloma 2000;
Lim & Saloma 2002, 2003), its extension to high NA, optical pulses and a delay between the pulses.

Two kinds of tests:

* The implementations agree with each other: the field of one beam in the two-beam code equals the Richards–Wolf
  integrals of the Romallosa replication; the field tables used for the sweeps equal the direct field; the pulsed signal
  summed in time equals the sum over photon pairs in frequency; long pulses give the continuous-beam signal.
* The verified numbers stay as they were verified (the review documents docs/review/01 and 07, the stored result files
  under output/08_two_color, docs/progress/work_to_date.pdf). If a change of implementation moves one of them, the test
  fails with the old and the new value: find the cause before changing the number.

Each test runs in a few seconds; the file runs in about one minute.
"""
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, '..'))
sys.path.insert(0, os.path.join(HERE, '..', 'scripts'))

from mcdo.rw_integrals import compute_integrals  # noqa: E402
from mcdo.twobeam import beam_field, intensity, two_color, two_photon  # noqa: E402

L1, L2, LP = 0.750, 0.656, 0.700


def fwhm(s, y):
    """FWHM of the lobe that holds the maximum (the convention of every width in the decks)."""
    from cambaliza2000_pulses_sweep import fwhm as f
    return f(s, y)


# ── 1. the implementations agree with each other ───────────────────────────────────────────────────────────────────

def test_two_beam_field_is_the_romallosa_field():
    """The vector field of one beam in mcdo.twobeam is the Richards–Wolf field of the Romallosa replication
    (mcdo.rw_integrals), across the axis for both input polarizations and along the axis: NA 0.8, n = 1.3, 750 nm."""
    lam, na, n, nt = 0.750, 0.8, 1.3, 801
    k, alpha = 2 * np.pi * n / lam, np.arcsin(na / n)
    r, z = np.linspace(0.0, 1.5, 301), np.linspace(-3.0, 3.0, 301)
    I0, I1, I2 = (a[0] for a in compute_integrals(r, np.array([0.0]), k, alpha, nt))
    J0, J1, J2 = (a[:, 0] for a in compute_integrals(np.array([0.0]), z, k, alpha, nt))
    ref = {'across, polarization along the cut': np.abs(I0 + I2) ** 2 + 4 * np.abs(I1) ** 2,
           'across, polarization across the cut': np.abs(I0 - I2) ** 2,
           'along the axis': np.abs(J0) ** 2}
    two = {'across, polarization along the cut': intensity(beam_field(r, 0 * r, lam, na, n, model='rw', psi=0.0, n_theta=nt)),
           'across, polarization across the cut': intensity(beam_field(r, 0 * r, lam, na, n, model='rw', psi=np.pi / 2,
                                                                       n_theta=nt)),
           'along the axis': intensity(beam_field(0 * z, z, lam, na, n, model='rw', psi=0.0, n_theta=nt))}
    for key in ref:
        a, b = ref[key] / ref[key].max(), two[key] / two[key].max()
        assert np.abs(a - b).max() < 1e-9, f'{key}: the two engines differ by {np.abs(a - b).max():.1e}'


def test_romallosa_width_through_the_two_beam_engine():
    """472.8 nm, the transverse FWHM of Romallosa et al. (2003) (NA 0.8, n = 1.3, 750 nm), from the two-beam code."""
    r = np.linspace(-1.0, 1.0, 8001)
    y = intensity(beam_field(r, 0 * r, 0.750, 0.8, 1.3, model='rw', psi=np.pi / 2, n_theta=801))
    w = fwhm(r, y) * 1000
    assert abs(w - 472.8) < 1.0, f'{w:.1f} nm, verified 472.8 nm'


def test_paraxial_debye_and_vector_coincide_at_low_na():
    """At NA 0.1 the paraxial field of Cambaliza & Saloma (2000, Eq. 1), the scalar Debye field and the vector field
    (unpolarized) give the same profiles across and along the axis."""
    x, z = np.linspace(-6, 6, 401), np.linspace(-120, 120, 401)
    for X, Z in ((x, 0 * x), (0 * z, z)):
        p = np.abs(beam_field(X, Z, L1, 0.1)) ** 2
        d = np.abs(beam_field(X, Z, L1, 0.1, model='debye')) ** 2
        v = 0.5 * sum(intensity(beam_field(X, Z, L1, 0.1, model='rw', psi=s)) for s in (0.0, np.pi / 2))
        for a, b in ((p, d), (p, v)):
            assert np.abs(a / a.max() - b / b.max()).max() < 3e-3


@pytest.mark.parametrize('model', ['paraxial', 'rw'])
def test_field_tables_are_the_direct_field(model):
    """The tables of cambaliza2000_fast_field.py, used for every pulse sweep, give the field of beam_field at each
    frequency, on the axis and in the focal plane, for the three lens angles."""
    from cambaliza2000_fast_field import Focus
    from mcdo.pulsed2ce import C_UM_FS
    na = 0.7
    F = Focus(na, 1.0, model)
    w = 2 * np.pi * C_UM_FS / np.array([0.70, 0.75, 0.80])
    s = np.linspace(-2.0, 2.0, 41)
    kw = dict(model='rw', psi=np.pi / 2) if model == 'rw' else {}
    for th in (0.0, np.pi / 2, np.pi):
        for x, z in ((0 * s, s), (s, 0 * s)):
            got = F.fields(w, th, x, z)
            ref = np.stack([np.atleast_2d(beam_field(x, z, 2 * np.pi * C_UM_FS / wm, na, theta=th, **kw)) for wm in w])
            assert np.abs(got - ref).max() < 1e-8 * np.abs(ref).max()


def test_long_pulses_give_the_continuous_beam_signal():
    """At 1000 fs the pulsed 2CE (all photon pairs, and the 350-nm pairs alone) is I1 I2 of Cambaliza & Saloma (2000)."""
    import cambaliza2000_pulses_delay as P
    import cambaliza2000_pulses_na_sweep as S
    s = np.linspace(-5, 5, 201)
    p = P.pulsed(0.5, 1000.0, np.pi, s, 'z', '2ce')
    cw = intensity(S.field(L1, 0.5, 0.0, 0 * s, s)) * intensity(S.field(L2, 0.5, np.pi, 0 * s, s))
    for q in (0, 2):
        assert np.abs(p[q] / p[q].max() - cw / cw.max()).max() < 2e-3


def test_pairs_summed_in_frequency_equal_the_time_integral():
    """The total with all photon pairs from the time integral of the sweeps equals the sum over pairs of frequencies
    that add to the 350-nm level (scripts/cambaliza2000_delay_allpairs_check.py), at 10 fs, with a delay."""
    import cambaliza2000_pulses_delay as P
    from cambaliza2000_delay_allpairs_check import total
    s = np.linspace(-3, 3, 61)
    d = np.array([0.0, 1.3])
    F = total('paraxial', 0.5, '2ce', np.pi, 0 * s, s, 10.0, d)
    for i, dl in enumerate(d):
        p = P.pulsed(0.5, 10.0, np.pi, s, 'z', '2ce', dl)[0]
        p0 = P.pulsed(0.5, 10.0, np.pi, s, 'z', '2ce', 0.0)[0].max()
        assert np.abs(F[i] / F[0].max() - p / p0).max() < 1e-3


# ── 2. the verified numbers ────────────────────────────────────────────────────────────────────────────────────────

def _widths(sig, theta, na, model, n=1.0, half=(1.5, 6.0), pts=6001):
    kw = dict(model='rw', psi=np.pi / 2) if model == 'rw' else {}
    out = []
    for h, cut in zip(half, ('x', 'z')):
        s = np.linspace(-h, h, pts)
        X, Z = (s, 0 * s) if cut == 'x' else (0 * s, s)
        if sig == '2ce':
            F = two_color(beam_field(X, Z, L1, na, n, **kw), beam_field(X, Z, L2, na, n, theta=theta, **kw))
        else:
            F = two_photon(beam_field(X, Z, LP, na, n, **kw), beam_field(X, Z, LP, na, n, theta=theta, **kw))
        out.append(fwhm(s, F))
    return out


@pytest.mark.parametrize('sig, theta, wx, wz', [
    ('2pe', 0.0, 0.517, 3.572), ('2pe', np.pi / 2, 0.256, 0.256), ('2pe', np.pi, 0.517, 0.136),
    ('2ce', 0.0, 0.516, 3.562), ('2ce', np.pi / 2, 0.763, 0.670), ('2ce', np.pi, 0.516, 3.562)])
def test_cambaliza_widths_at_na_0p5(sig, theta, wx, wz):
    """Central spot and depth of focus of the replication of Cambaliza & Saloma (2000), paraxial scalar model, NA 0.5
    (output/08_two_color/replication_numbers.txt)."""
    gx, gz = _widths(sig, theta, 0.5, 'paraxial')
    assert abs(gx - wx) < 0.002 and abs(gz - wz) < 0.002, f'{sig} θ = {theta:.2f}: {gx:.3f}, {gz:.3f} µm'


@pytest.mark.parametrize('sig, theta, na, model, wx, wz', [
    ('2ce', 0.0, 0.5, 'rw', 0.510, 3.326), ('2ce', 0.0, 0.9, 'rw', 0.270, 0.807), ('2ce', 0.0, 0.9, 'paraxial', 0.286, 1.099),
    ('2ce', np.pi / 2, 0.7, 'rw', 0.521, 0.461), ('2pe', np.pi / 2, 0.7, 'rw', 0.256, 0.256),
    ('2pe', np.pi, 0.9, 'rw', 0.271, 0.166)])
def test_high_na_widths(sig, theta, na, model, wx, wz):
    """The extension to high NA (output/08_two_color/cambaliza2000/high_na/maps/widths.txt and widths.csv): the
    paraxial depth of focus is 7% too long at NA 0.5 and 36% at NA 0.9; with crossed lenses the 2PE spot keeps its width."""
    gx, gz = _widths(sig, theta, na, model, half=(0.8, 3.0))
    assert abs(gx - wx) < 0.002 and abs(gz - wz) < 0.002, f'{sig} θ = {theta:.2f} NA {na} {model}: {gx:.3f}, {gz:.3f} µm'


def test_lim2003_aberration_compensation():
    """Lim & Saloma (2003): with collinear lenses the 2CE peak is kept when the two aberrations are equal, and lost when
    they are opposite (0.84 and 0.07 of the aberration-free peak at |φ| = 60; aberration_numbers.txt)."""
    x, z = np.linspace(-1.0, 1.0, 101), np.linspace(-5.0, 5.0, 101)
    X, Z = np.meshgrid(x, z)
    peak = lambda a, b: two_color(beam_field(X, Z, L1, 0.5, sa=a), beam_field(X, Z, L2, 0.5, sa=b)).max()
    p0 = peak(0, 0)
    assert abs(peak(60, 60) / p0 - 0.84) < 0.01 and abs(peak(60, -60) / p0 - 0.07) < 0.01


def test_pulsed_depth_of_focus_with_facing_lenses():
    """Paraxial model, NA 0.5, facing lenses: the 2CE depth of focus is 3.52 µm at 100 fs (3.56 µm for continuous
    beams), and at 20 fs 2.81 µm for the 350-nm pairs and 2.78 µm with all pairs (allpairs/numbers.txt)."""
    import cambaliza2000_pulses_delay as P
    s = np.linspace(-5, 5, 501)
    p100, p20 = P.pulsed(0.5, 100.0, np.pi, s, 'z', '2ce'), P.pulsed(0.5, 20.0, np.pi, s, 'z', '2ce')
    got = (fwhm(s, p100[2]), fwhm(s, p20[2]), fwhm(s, p20[0]))
    for g, w in zip(got, (3.52, 2.811, 2.781)):
        assert abs(g - w) < 0.012, f'depth of focus {g:.3f} µm, verified {w}'


def test_delay_follows_the_temporal_overlap():
    """At a fixed point the 2CE of the 350-nm pairs falls as exp(−2 ln2 Δt²/τ²): 0.7071 at Δt = τ/2 and 0.2500 at
    Δt = τ (collinear lenses, 100 fs; the delay sweep stores 0.70712 and 0.25001)."""
    import cambaliza2000_pulses_delay as P
    s = np.linspace(-0.4, 0.4, 9)
    p = [P.pulsed(0.5, 100.0, 0.0, s, 'z', '2ce', d)[2].max() for d in (0.0, 50.0, 100.0)]
    assert abs(p[1] / p[0] - 0.70711) < 5e-4 and abs(p[2] / p[0] - 0.25) < 5e-4


def test_delay_moves_the_peak_with_facing_lenses_at_low_na(monkeypatch):
    """Vector model in air, NA 0.1, facing lenses, 100 fs: at a delay of one pulse width the peak of the 350-nm pairs is
    0.930 of the peak without delay, 14.2 µm from the focus (delay sweep, rw_air; close to cΔt/2 = 15.0 µm)."""
    import cambaliza2000_pulses_delay as P
    import cambaliza2000_pulses_na_sweep as S
    import cambaliza2000_pulses_na_sweep_fast as SF
    monkeypatch.setattr(S, 'MODEL', 'rw')
    monkeypatch.setattr(SF, 'FOCUS', {})
    s = np.linspace(-30, 40, 701)
    p0, p1 = P.pulsed(0.1, 100.0, np.pi, s, 'z', '2ce', 0.0)[2], P.pulsed(0.1, 100.0, np.pi, s, 'z', '2ce', 100.0)[2]
    assert abs(p1.max() / p0.max() - 0.930) < 0.003 and abs(s[np.argmax(p1)] - 14.2) < 0.2
