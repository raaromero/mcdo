"""Check that numbers quoted on slides still match the computed data.

Slide text is written by hand and the sweeps are rerun often. A number that
was right when it was typed can drift silently when a script changes. This
pins the ones the argument rests on.
"""

import os
import sys

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

BASE = os.path.join(ROOT, "output", "03_annular", "annular_baseline.npz")

# (aperture, illumination prefix, obstruction ratio, field, quoted value, tolerance)
QUOTED = [
    (0.8, "uniform", 0.0, "depth_um", 2.42, 0.01),
    (0.8, "uniform", 0.5, "depth_um", 3.14, 0.01),
    (0.8, "uniform", 0.9, "depth_um", 11.5, 0.05),
    (0.8, "uniform", 0.99, "depth_um", 107.0, 1.0),
    (0.8, "Gaussian", 0.0, "depth_um", 3.85, 0.01),
    (0.8, "Gaussian", 0.5, "depth_um", 4.14, 0.01),
    (0.8, "uniform", 0.5, "gain", 1.30, 0.01),
    (0.8, "uniform", 0.9, "gain", 4.76, 0.01),
    (0.8, "Gaussian", 0.5, "gain", 1.07, 0.01),
    (0.8, "Gaussian", 0.9, "gain", 3.05, 0.01),
    (1.2, "uniform", 0.9, "gain", 3.49, 0.02),
]


@pytest.mark.skipif(not os.path.exists(BASE), reason="baseline sweep not run")
@pytest.mark.parametrize("xna,inp,eps,field,quoted,tol", QUOTED)
def test_slide_number_matches_data(xna, inp, eps, field, quoted, tol):
    d = np.load(BASE, allow_pickle=True)
    names = [str(v) for v in d["input"]]
    rows = [
        i for i in range(len(d["eps"]))
        if d["na"][i] == xna and names[i].startswith(inp) and d["eps"][i] == eps
    ]
    assert rows, f"no row for aperture {xna}, {inp}, ratio {eps}"
    value = float(d[field][rows[0]])
    assert abs(value - quoted) <= tol, (
        f"slides quote {quoted} for {field} at aperture {xna}, {inp}, "
        f"ratio {eps}; the data gives {value:.4f}"
    )


PULSED = os.path.join(ROOT, "output", "05_pulsed_pupils", "pulsed_annular_grid.npz")

# The stage-7 argument rests on how the extension changes between continuous
# wave and a 1 fs pulse, and those numbers came from a different sweep than the
# baseline above. Uniform illumination is quoted as unchanged; the truncated
# Gaussian is quoted as eroding monotonically. Both are pinned here, because a
# rerun that shifted either would leave the slides making a claim the data no
# longer supports.
EROSION = [
    ("uniform", 0.3, 0.0, 0.1),
    ("uniform", 0.5, 0.0, 0.1),
    ("uniform", 0.9, 0.0, 0.1),
    ("uniform", 0.99, 0.0, 0.1),
    ("Gaussian", 0.3, 0.8, 0.1),
    ("Gaussian", 0.5, 2.6, 0.1),
    ("Gaussian", 0.9, 7.2, 0.1),
    ("Gaussian", 0.99, 7.5, 0.1),
]


def _pulsed_gain(d, inp, eps, tau):
    names = [str(v) for v in d["input"]]
    taus = [str(v) for v in d["tau"]]
    for i in range(len(d["eps"])):
        if (names[i].startswith(inp) and float(d["eps"][i]) == eps
                and taus[i] == tau):
            return float(d["gain"][i])
    raise AssertionError(f"no row for {inp}, ratio {eps}, {tau}")


@pytest.mark.skipif(not os.path.exists(PULSED), reason="pulsed sweep not run")
@pytest.mark.parametrize("inp,eps,quoted_pct,tol", EROSION)
def test_slide_bandwidth_erosion_matches_data(inp, eps, quoted_pct, tol):
    d = np.load(PULSED, allow_pickle=True)
    cw = _pulsed_gain(d, inp, eps, "continuous wave")
    fs1 = _pulsed_gain(d, inp, eps, "1 fs")
    erosion = 100.0 * (1.0 - fs1 / cw)
    assert abs(erosion - quoted_pct) <= tol, (
        f"slides quote {quoted_pct}% erosion for {inp} at ratio {eps}; "
        f"the data gives {erosion:.2f}%"
    )


# Continuous-wave extensions quoted on the stage-7 field slides that the
# baseline pins above do not already cover.
PULSED_CW = [
    ("uniform", 0.99, "gain", 44.3, 0.1),
    ("Gaussian", 0.9, "depth_um", 11.7, 0.1),
    ("Gaussian", 0.99, "gain", 27.8, 0.1),
]


@pytest.mark.skipif(not os.path.exists(PULSED), reason="pulsed sweep not run")
@pytest.mark.parametrize("inp,eps,field,quoted,tol", PULSED_CW)
def test_slide_continuous_wave_number_matches_pulsed_sweep(inp, eps, field,
                                                           quoted, tol):
    d = np.load(PULSED, allow_pickle=True)
    names = [str(v) for v in d["input"]]
    taus = [str(v) for v in d["tau"]]
    rows = [i for i in range(len(d["eps"]))
            if names[i].startswith(inp) and float(d["eps"][i]) == eps
            and taus[i] == "continuous wave"]
    assert rows, f"no continuous-wave row for {inp}, ratio {eps}"
    value = float(d[field][rows[0]])
    assert abs(value - quoted) <= tol, (
        f"slides quote {quoted} for {field} at {inp}, ratio {eps}; "
        f"the data gives {value:.4f}"
    )


def test_slide_bandwidth_matches_config():
    """The settings slide quotes the 1 fs bandwidth and its ratio to the carrier.

    Both are read off `SimConfig`, so they move if the spectrum's definition
    ever does. The slide is where a reader checks whether the pulse is still
    few-cycle, which is the premise of everything after it.
    """
    from mcdo import SimConfig
    cfg = SimConfig(lam_c=0.750, X_NA=0.8, n=1.3, tau=1e-15,
                    N_freq=101, N_theta=501)
    thz = cfg.spectral_bandwidth / (2.0 * np.pi) / 1e12
    carrier = cfg.omega_c / (2.0 * np.pi) / 1e12
    assert abs(thz - 441.0) <= 1.0, f"slides quote 441 THz; config gives {thz:.1f}"
    assert abs(thz / carrier - 1.10) <= 0.01, (
        f"slides quote 1.10 times the carrier; config gives {thz / carrier:.3f}")


def test_spectral_bandwidth_agrees_with_the_spectrum_it_describes():
    """The quoted FWHM has to be the FWHM of the spectrum actually integrated.

    These are two separate expressions in `config.py`, and a mismatch would be
    invisible: every pulsed result would still run, just with a bandwidth
    labelled differently from the one being sampled.
    """
    from mcdo import SimConfig
    cfg = SimConfig(lam_c=0.750, X_NA=0.8, n=1.3, tau=1e-15,
                    N_freq=101, N_theta=501)
    w = cfg.omega_c + np.linspace(-3e15, 3e15, 400001)
    s = cfg.spectral_power(w)
    s = s / s.max()
    above = np.where(s >= 0.5)[0]
    measured = w[above[-1]] - w[above[0]]
    assert abs(measured / cfg.spectral_bandwidth - 1.0) < 1e-3, (
        f"spectral_power has FWHM {measured:.4e} rad/s but "
        f"spectral_bandwidth reports {cfg.spectral_bandwidth:.4e}")


def test_exact_extension_law_beats_the_paraxial_one():
    """The exact law has to be the better predictor at every aperture.

    It is only worth stating if it holds where the paraxial law fails, so this
    checks both: the exact expression stays within a few percent of the
    computed extension at numerical aperture 1.2, and the paraxial one does
    not. If a future change to the sweep broke that, the claim would have to
    go rather than the test being loosened.
    """
    import numpy as np
    from mcdo.extension import exact, paraxial
    d = np.load(BASE, allow_pickle=True)
    names = [str(v) for v in d["input"]]
    worst_exact = worst_paraxial = 0.0
    for i in range(len(d["eps"])):
        if names[i] != "uniform" or float(d["eps"][i]) == 0.0:
            continue
        xna, eps = float(d["na"][i]), float(d["eps"][i])
        m = float(d["gain"][i])
        worst_exact = max(worst_exact, abs(exact(eps, xna) / m - 1))
        worst_paraxial = max(worst_paraxial, abs(paraxial(eps) / m - 1))
    assert worst_exact < 0.05, f"exact law off by {100 * worst_exact:.1f}%"
    assert worst_paraxial > 0.5, (
        "the paraxial law no longer fails, so the comparison is pointless")


def test_exact_law_reduces_to_the_paraxial_one_at_small_angle():
    """The paraxial law must be recoverable as the limit, not a rival claim."""
    from mcdo.extension import exact, paraxial
    for eps in (0.3, 0.5, 0.9, 0.99):
        assert abs(exact(eps, 0.01) / paraxial(eps) - 1) < 1e-3, (
            f"laws disagree at vanishing aperture for ratio {eps}")


def test_exact_law_is_documented_as_uniform_only():
    """The law is derived assuming every transmitted ray carries equal weight.

    A Gaussian pupil breaks that assumption, and the expression then overstates
    the extension by up to 88%. This pins the scope limit so the law is never
    quietly applied to an apodized pupil.
    """
    import numpy as np
    from mcdo.extension import exact
    d = np.load(BASE, allow_pickle=True)
    names = [str(v) for v in d["input"]]
    worst = 0.0
    for i in range(len(d["eps"])):
        if not names[i].startswith("Gaussian") or float(d["eps"][i]) == 0.0:
            continue
        worst = max(worst, abs(exact(float(d["eps"][i]),
                                     float(d["na"][i])) / float(d["gain"][i]) - 1))
    assert worst > 0.2, (
        "the law now matches an apodized pupil too; the uniform-only scope "
        "note in mcdo/extension.py needs revisiting")


# Every extension quoted on a stage-7 pulsed field slide, against the sweep.
FIELD_SLIDE = [
    ("uniform", 0.9, "continuous wave", 4.76),
    ("uniform", 0.9, "1 fs", 4.76),
    ("Gaussian", 0.9, "continuous wave", 3.05),
    ("Gaussian", 0.9, "1 fs", 2.83),
]


@pytest.mark.skipif(not os.path.exists(PULSED), reason="pulsed sweep not run")
@pytest.mark.parametrize("inp,eps,tau,quoted", FIELD_SLIDE)
def test_pulsed_field_slide_extension(inp, eps, tau, quoted):
    """These sit beside a picture, where a wrong number is hardest to notice."""
    d = np.load(PULSED, allow_pickle=True)
    value = _pulsed_gain(d, inp, eps, tau)
    assert abs(value - quoted) <= 0.01, (
        f"slides quote {quoted} for {inp} at ratio {eps}, {tau}; "
        f"the data gives {value:.4f}")


def _has_rings(d, inp, eps, tau):
    """A transverse profile with a usable first minimum still shows rings.

    Guarded, so a minimum found far outside the transverse null - which is
    longitudinal structure, not a ring - does not count as one.
    """
    from mcdo.profiles import first_minimum
    p = d[f"0.8|{inp}|{eps}|{tau}|r"]
    return not np.isnan(first_minimum(p[0], p[1])[0])


@pytest.mark.skipif(not os.path.exists(PULSED), reason="pulsed sweep not run")
def test_bandwidth_erases_the_transverse_rings():
    """The slides say the rings fill in under the pulse. They do more than that.

    At 1 fs the transverse profile is monotonic at every configuration: no
    first minimum survives anywhere in the window, so there are no rings left
    to fill. Continuous wave keeps them everywhere. Both halves are asserted,
    because the claim is only meaningful as a contrast.
    """
    d = np.load(PULSED, allow_pickle=True)
    for inp in ("uniform", "Gaussian, alpha = 4"):
        for eps in (0.0, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99):
            assert _has_rings(d, inp, eps, "continuous wave"), (
                f"continuous wave lost its rings at {inp}, ratio {eps}")
            assert not _has_rings(d, inp, eps, "1 fs"), (
                f"a 1 fs pulse still shows rings at {inp}, ratio {eps}")


@pytest.mark.skipif(not os.path.exists(PULSED), reason="pulsed sweep not run")
def test_obstruction_protects_the_rings_at_two_femtoseconds():
    """2 fs is the duration where the obstruction ratio decides the outcome.

    A thin ring spaces its zeros more widely, so they survive spectral
    averaging that erases the full disk's. This is the threshold behavior:
    at 2 fs the unobstructed pattern is already smooth while the obstructed
    one is not.
    """
    d = np.load(PULSED, allow_pickle=True)
    assert not _has_rings(d, "uniform", 0.0, "2 fs"), (
        "the unobstructed disk still shows rings at 2 fs")
    assert _has_rings(d, "uniform", 0.9, "2 fs"), (
        "the ring's structure no longer survives 2 fs")


APERTURES = os.path.join(ROOT, "output", "05_pulsed_pupils",
                         "pulsed_annular_apertures.npz")


@pytest.mark.skipif(not os.path.exists(APERTURES), reason="backup sweep not run")
def test_uniform_extension_is_bandwidth_invariant_at_every_aperture():
    """The backup sweep is what answers a question about other apertures.

    It is not on any slide, so nothing else checks it, and it would be quoted
    from cold. Uniform illumination has to stay invariant at 0.1 and 1.2 for
    the deck's claim at 0.8 to be about physics rather than about one setting.
    """
    d = np.load(APERTURES, allow_pickle=True)
    names = [str(v) for v in d["input"]]
    taus = [str(v) for v in d["tau"]]

    def gain(na, inp, eps, tau):
        for i in range(len(d["eps"])):
            if (float(d["na"][i]) == na and names[i].startswith(inp)
                    and float(d["eps"][i]) == eps and taus[i] == tau):
                return float(d["gain"][i])
        raise AssertionError(f"no row for {na}, {inp}, {eps}, {tau}")

    for na in (0.1, 1.2):
        for eps in (0.5, 0.9, 0.99):
            cw = gain(na, "uniform", eps, "continuous wave")
            fs1 = gain(na, "uniform", eps, "1 fs")
            assert abs(1.0 - fs1 / cw) < 0.01, (
                f"uniform is no longer bandwidth invariant at aperture {na}, "
                f"ratio {eps}: {100 * (1 - fs1 / cw):+.2f}%")

    # and the Gaussian erosion has to grow with aperture, which is the
    # statement that makes the deck's single-aperture number generalizable
    lo = 1.0 - gain(0.1, "Gaussian", 0.99, "1 fs") / gain(
        0.1, "Gaussian", 0.99, "continuous wave")
    hi = 1.0 - gain(1.2, "Gaussian", 0.99, "1 fs") / gain(
        1.2, "Gaussian", 0.99, "continuous wave")
    assert hi > lo > 0.03, (
        f"Gaussian erosion no longer grows with aperture: "
        f"{100 * lo:.1f}% at 0.1 against {100 * hi:.1f}% at 1.2")


@pytest.mark.skipif(not os.path.exists(PULSED), reason="pulsed sweep not run")
def test_illuminations_converge_at_the_thinnest_ring():
    """A slide claims both illuminations give the same focus by ratio 0.99.

    The reason is that a thin ring transmits only rays near the rim, where the
    apodization has almost no variation left to impose. If the two ever parted
    company there, the explanation on that slide would be wrong even though
    each number on it stayed right.
    """
    d = np.load(PULSED, allow_pickle=True)
    names = [str(v) for v in d["input"]]
    taus = [str(v) for v in d["tau"]]

    def depth(inp, eps):
        for i in range(len(d["eps"])):
            if (names[i].startswith(inp) and float(d["eps"][i]) == eps
                    and taus[i] == "continuous wave"):
                return float(d["depth_um"][i])
        raise AssertionError(f"no row for {inp} at ratio {eps}")

    near = abs(depth("uniform", 0.99) / depth("Gaussian", 0.99) - 1)
    far = abs(depth("uniform", 0.0) / depth("Gaussian", 0.0) - 1)
    assert near < 0.01, (
        f"the illuminations no longer converge at ratio 0.99: {100 * near:.2f}%")
    assert far > 0.3, (
        "the illuminations no longer differ without an obstruction, so the "
        "convergence at 0.99 says nothing")


def _j0_deviation(r, y, xna, span):
    """Root-mean-square gap between a transverse profile and J0 squared."""
    from scipy.special import j0
    k = 2.0 * np.pi * 1.3 / 0.750
    m = r <= span
    ideal = j0(k * np.sin(np.arcsin(xna / 1.3)) * r[m]) ** 2
    return float(np.sqrt(np.mean((y[m] / y.max() - ideal) ** 2)))


@pytest.mark.skipif(not os.path.exists(APERTURES), reason="backup sweep not run")
def test_thin_annulus_approaches_a_bessel_beam_only_at_low_aperture():
    """mcdo/annular.py names the Durnin limit as a checkpoint. Nothing checked it.

    A thin ring should approach J0 squared, and at aperture 0.1 it does, to
    0.003. It does not at aperture 1.2, because the longitudinal field fills
    the nulls that the scalar result has as zeros. Asserting only the first
    half would make a vector code look broken; asserting only the second would
    let a broken Babinet subtraction pass.
    """
    d = np.load(APERTURES, allow_pickle=True)
    names = [str(v) for v in d["input"]]
    taus = [str(v) for v in d["tau"]]

    def profile(na, eps):
        key = f"{na}|uniform|{eps}|continuous wave|r"
        assert key in d.files, key
        return d[key]

    lo_full = _j0_deviation(*profile(0.1, 0.0), 0.1, 12.0)
    lo_thin = _j0_deviation(*profile(0.1, 0.99), 0.1, 12.0)
    assert lo_thin < 0.01, f"thin ring is not Bessel-like at aperture 0.1: {lo_thin:.4f}"
    assert lo_full > 10 * lo_thin, (
        "the full disk is as Bessel-like as the ring, so the limit says nothing")

    hi_thin = _j0_deviation(*profile(1.2, 0.99), 1.2, 1.0)
    assert hi_thin > 0.05, (
        f"the vector field no longer fills the nulls at aperture 1.2: {hi_thin:.4f}")


def _lengthening(na, inp, eps, tau="1 fs"):
    """DOF at this pulse duration over DOF at continuous wave, same pupil."""
    src = PULSED if na == 0.8 else APERTURES
    d = np.load(src, allow_pickle=True)
    names = [str(v) for v in d["input"]]
    taus = [str(v) for v in d["tau"]]
    has_na = "na" in d.files
    out = {}
    for i in range(len(d["eps"])):
        if (names[i].startswith(inp) and float(d["eps"][i]) == eps
                and (not has_na or float(d["na"][i]) == na)):
            out[taus[i]] = float(d["depth_um"][i])
    assert "continuous wave" in out and tau in out, (na, inp, eps)
    return out[tau] / out["continuous wave"]


@pytest.mark.skipif(not os.path.exists(APERTURES), reason="backup sweep not run")
def test_thin_ring_bandwidth_response_is_aperture_independent():
    """At the thinnest ring, bandwidth lengthens the focus by the same 0.9%
    at every aperture.

    Only rays near the rim are transmitted there, so the apodization has
    nothing left to weight and the aperture drops out. This is what makes the
    Gaussian erosion at high obstruction a statement about the unobstructed
    pupil's response rather than about the ring: erosion is 1 - R(eps)/R(0),
    and R(0.99) is common to all apertures while R(0) is not.
    """
    thin = [_lengthening(na, "Gaussian", 0.99) for na in (0.1, 0.8, 1.2)]
    assert max(thin) - min(thin) < 0.002, (
        f"the thin-ring response is no longer aperture independent: {thin}")

    full = [_lengthening(na, "Gaussian", 0.0) for na in (0.1, 0.8, 1.2)]
    assert full[2] - full[0] > 0.02, (
        f"the unobstructed response no longer varies with aperture: {full}")
    assert all(f > t for f, t in zip(full, thin)), (
        "the unobstructed pupil must lengthen more than the thin ring")


@pytest.mark.skipif(not os.path.exists(APERTURES), reason="backup sweep not run")
def test_exact_law_predicts_the_pulsed_extension_as_well_as_the_monochromatic_one():
    """Why uniform illumination is bandwidth invariant, rather than that it is.

    The closed form (1 - cos alpha) / (cos theta_in - cos alpha) contains no
    wavelength: the extension is fixed by the angular band the annulus
    transmits. Every spectral component of a pulse therefore receives the same
    extension, and so does their weighted sum. If the law ever predicted the
    continuous-wave case well and the pulsed case badly, that reasoning would
    be wrong even though both measurements stayed correct.
    """
    from mcdo.extension import exact
    d = np.load(APERTURES, allow_pickle=True)
    names = [str(v) for v in d["input"]]
    taus = [str(v) for v in d["tau"]]
    worst_cw = worst_pulsed = 0.0
    for i in range(len(d["eps"])):
        eps, na = float(d["eps"][i]), float(d["na"][i])
        if not names[i].startswith("uniform") or eps == 0.0:
            continue
        g = float(d["gain"][i])
        if not np.isfinite(g) or g == 0:
            continue
        err = abs(exact(eps, na) / g - 1.0)
        if taus[i] == "continuous wave":
            worst_cw = max(worst_cw, err)
        elif taus[i] == "1 fs":
            worst_pulsed = max(worst_pulsed, err)
    assert worst_pulsed < 0.05, (
        f"the law no longer predicts the pulsed extension: {100 * worst_pulsed:.1f}%")
    assert abs(worst_pulsed - worst_cw) < 0.01, (
        f"the law now fits the two cases differently ({100 * worst_cw:.2f}% "
        f"against {100 * worst_pulsed:.2f}%), so it is not the wavelength "
        f"independence that explains the invariance")


@pytest.mark.skipif(not os.path.exists(PULSED), reason="pulsed sweep not run")
def test_uniform_bandwidth_broadening_does_not_depend_on_the_obstruction():
    """The mechanism behind uniform invariance, stated as the quantity itself.

    A 1 fs pulse lengthens the uniform focus by 0.9% at every obstruction
    ratio, to within 0.02%. Extension is a ratio of two depths that both
    broaden by that same factor, so it cancels. The Gaussian case needs no
    separate mechanism: its broadening decays from 9.1% unobstructed onto the
    uniform 0.9% as the ring thins, because at ratio 0.99 the two pupils
    transmit the same rim rays, and the erosion is exactly that decay.
    """
    d = np.load(PULSED, allow_pickle=True)
    names = [str(v) for v in d["input"]]
    taus = [str(v) for v in d["tau"]]

    def ratio(inp, eps):
        got = {}
        for i in range(len(d["eps"])):
            if names[i].startswith(inp) and float(d["eps"][i]) == eps:
                got[taus[i]] = float(d["depth_um"][i])
        return got["1 fs"] / got["continuous wave"]

    eps_all = [0.0, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99]
    uni = [ratio("uniform", e) for e in eps_all]
    assert max(uni) - min(uni) < 0.001, (
        f"uniform broadening now varies with the obstruction: {uni}")

    gau = [ratio("Gaussian", e) for e in eps_all]
    assert gau[0] > 1.05, f"the Gaussian focus no longer broadens strongly: {gau[0]}"
    assert abs(gau[-1] - uni[-1]) < 0.001, (
        "the two illuminations no longer converge at the thinnest ring, so the "
        "erosion is not the decay onto the uniform response")
    assert all(x >= y - 1e-9 for x, y in zip(gau, gau[1:])), (
        f"the Gaussian broadening is no longer monotonic in the ratio: {gau}")


@pytest.mark.skipif(not os.path.exists(APERTURES), reason="backup sweep not run")
def test_uniform_invariance_is_exact_only_where_the_field_is_scalar():
    """Invariance is not equally exact at every aperture, and should not be
    described as if it were.

    The uniform broadening factor is flat to 0.02% at numerical aperture 0.1
    and drifts by 0.35% at 1.2, which is the residual erosion seen in that row
    of the sweep. Stating the invariance without that caveat would overclaim in
    exactly the regime this work operates in.
    """
    d = np.load(APERTURES, allow_pickle=True)
    names = [str(v) for v in d["input"]]
    taus = [str(v) for v in d["tau"]]

    def spread(na):
        by_eps = {}
        for i in range(len(d["eps"])):
            if not names[i].startswith("uniform") or float(d["na"][i]) != na:
                continue
            by_eps.setdefault(float(d["eps"][i]), {})[taus[i]] = float(
                d["depth_um"][i])
        r = [v["1 fs"] / v["continuous wave"] for v in by_eps.values()
             if "1 fs" in v and "continuous wave" in v]
        return max(r) - min(r)

    lo, hi = spread(0.1), spread(1.2)
    assert lo < 0.0005, f"aperture 0.1 is no longer flat: spread {lo:.5f}"
    assert hi > lo, (
        "the invariance no longer degrades with aperture, so the scalar-limit "
        "reading of it is wrong")
    assert hi < 0.01, f"aperture 1.2 drifts further than reported: {hi:.5f}"


@pytest.mark.skipif(not os.path.exists(PULSED), reason="pulsed sweep not run")
def test_thin_ring_matches_a_one_dimensional_analytic_model():
    """An independent check on the whole annular chain.

    A thin ring transmits essentially a single cone angle, so its axial profile
    is sinc squared in k z (cos theta_in - cos alpha). That model is not the
    code under test: it has no Bessel functions, no vector components and no
    quadrature over the pupil. It reproduces the swept depth of focus at
    obstruction ratio 0.99 to better than a percent, and reproduces the 1 fs
    broadening as well, which is what justifies reading the closed-form
    extension law as a derivation rather than a fit.
    """
    from mcdo import SimConfig
    cfg = SimConfig(lam_c=0.750, X_NA=0.8, n=1.3, tau=1e-15,
                    N_freq=401, N_theta=801)
    eps = 0.99
    delta = np.cos(np.arcsin(eps * np.sin(cfg.alpha))) - np.cos(cfg.alpha)

    om = cfg.omega_grid()
    w = cfg.spectral_power(om)
    keep = om > 0
    k = cfg.n * om[keep] / 2.99792458e14

    z = np.linspace(0.0, 400.0, 100001)

    def sinc2(kz):
        x = kz * delta / 2.0
        return np.where(np.abs(x) < 1e-12, 1.0, (np.sin(x) / np.maximum(np.abs(x), 1e-300)) ** 2)

    def width(y):
        y = y / y.max()
        below = np.where(y < 0.5)[0]
        i = below[0]
        return 2.0 * np.interp(0.5, [y[i], y[i - 1]], [z[i], z[i - 1]])

    mono = width(sinc2(cfg.k_c * z))
    total = np.zeros_like(z)
    for ki, wi in zip(k, w[keep]):
        total += wi * sinc2(ki * z)
    broadening = width(total) / mono

    d = np.load(PULSED, allow_pickle=True)
    names = [str(v) for v in d["input"]]
    taus = [str(v) for v in d["tau"]]
    swept = {}
    for i in range(len(d["eps"])):
        if names[i].startswith("uniform") and float(d["eps"][i]) == eps:
            swept[taus[i]] = float(d["depth_um"][i])

    assert abs(mono / swept["continuous wave"] - 1.0) < 0.01, (
        f"model depth {mono:.2f} um against swept "
        f"{swept['continuous wave']:.2f} um")
    measured = swept["1 fs"] / swept["continuous wave"]
    assert abs(broadening - measured) < 0.005, (
        f"model broadening {broadening:.4f} against measured {measured:.4f}")


def _sinc_depth(na, eps, zmax, n=1.3, lam=0.750):
    """Depth of focus of a flat window in cos theta, the model behind the law."""
    from mcdo import SimConfig
    cfg = SimConfig(lam_c=lam, X_NA=na, n=n, tau=np.inf, N_freq=3, N_theta=801)
    delta = np.cos(np.arcsin(eps * np.sin(cfg.alpha))) - np.cos(cfg.alpha)
    z = np.linspace(0.0, zmax, 200001)
    x = cfg.k_c * z * delta / 2.0
    y = np.where(np.abs(x) < 1e-12, 1.0,
                 (np.sin(x) / np.maximum(np.abs(x), 1e-300)) ** 2)
    below = np.where(y < 0.5)[0]
    i = below[0]
    return 2.0 * np.interp(0.5, [y[i], y[i - 1]], [z[i], z[i - 1]])


@pytest.mark.skipif(not os.path.exists(APERTURES), reason="backup sweep not run")
def test_the_extension_law_is_the_flat_window_approximation():
    """Where the closed-form law loses accuracy, and why.

    The law treats the pupil as a flat window in cos theta. Its error is
    therefore the aplanatic weighting varying across the transmitted band:
    largest at a wide cone with no obstruction, and vanishing as the ring
    narrows the band, whatever the aperture. Asserting the pattern rather than
    a single tolerance is what ties the law's accuracy to a reason.
    """
    d = np.load(APERTURES, allow_pickle=True)
    names = [str(v) for v in d["input"]]
    taus = [str(v) for v in d["tau"]]

    def swept(na, eps):
        for i in range(len(d["eps"])):
            if (names[i].startswith("uniform") and float(d["na"][i]) == na
                    and float(d["eps"][i]) == eps
                    and taus[i] == "continuous wave"):
                return float(d["depth_um"][i])
        raise AssertionError((na, eps))

    wide_open = abs(_sinc_depth(1.2, 0.0, 200.0) / swept(1.2, 0.0) - 1.0)
    wide_thin = abs(_sinc_depth(1.2, 0.99, 200.0) / swept(1.2, 0.99) - 1.0)
    narrow_open = abs(_sinc_depth(0.1, 0.0, 20000.0) / swept(0.1, 0.0) - 1.0)

    assert wide_open > 0.01, (
        f"the flat-window model no longer errs at a wide cone: {wide_open:.4f}")
    assert wide_thin < 0.005, (
        f"a thin ring no longer rescues the model at aperture 1.2: {wide_thin:.4f}")
    assert narrow_open < 0.005, (
        f"the model no longer holds in the scalar limit: {narrow_open:.4f}")
    assert wide_open > 5 * wide_thin, (
        "the obstruction no longer controls the model's error, so the "
        "aplanatic-weighting explanation does not hold")


WAVELENGTH = os.path.join(ROOT, "output", "03_annular", "wavelength_sweep.npz")
WAVELENGTH_PULSED = os.path.join(ROOT, "output", "05_pulsed_pupils",
                                 "wavelength_pulsed.npz")


@pytest.mark.skipif(not os.path.exists(WAVELENGTH), reason="sweep not run")
def test_continuous_wave_result_is_exactly_colour_independent():
    """Scale invariance, asserted rather than assumed.

    The integrand depends on z only through k z and on r only through k r, so
    changing wavelength is a coordinate rescaling: every extension is identical
    and every length is proportional to lambda. Both halves are checked,
    because the first alone would also pass on a sweep that silently ran one
    wavelength three times.
    """
    d = np.load(WAVELENGTH, allow_pickle=True)
    names = [str(v) for v in d["input"]]
    lams = sorted({float(v) for v in d["lam"]})
    assert len(lams) >= 3, "the sweep no longer spans several wavelengths"

    def rows(lam, na, inp, eps):
        for i in range(len(d["eps"])):
            if (float(d["lam"][i]) == lam and float(d["na"][i]) == na
                    and names[i].startswith(inp) and float(d["eps"][i]) == eps):
                return float(d["gain"][i]), float(d["depth_um"][i])
        raise AssertionError((lam, na, inp, eps))

    worst_gain = 0.0
    for na in (0.1, 0.8, 1.2):
        for inp in ("uniform", "Gaussian"):
            for eps in (0.3, 0.5, 0.9, 0.99):
                g = [rows(lam, na, inp, eps)[0] for lam in lams]
                worst_gain = max(worst_gain, max(g) / min(g) - 1.0)
    assert worst_gain < 1e-4, (
        f"the extension now depends on color by {100 * worst_gain:.4f}%")

    # and the depth must actually move, proportionally, or the sweep is inert
    for na in (0.1, 0.8, 1.2):
        depths = [rows(lam, na, "uniform", 0.0)[1] for lam in lams]
        scaled = [depths[i] / lams[i] for i in range(len(lams))]
        assert max(scaled) / min(scaled) - 1.0 < 1e-4, (
            f"depth is not proportional to wavelength at aperture {na}")
        assert max(depths) / min(depths) > 1.5, (
            "the depths did not change, so the sweep ran one color")


@pytest.mark.skipif(not os.path.exists(WAVELENGTH_PULSED),
                    reason="pulsed sweep not run")
def test_pulsed_result_does_depend_on_centre_wavelength():
    """A pulse breaks the scale invariance, and in the stated direction.

    Bandwidth is fixed by duration, so at 1 fs the same 441 THz is a larger
    fraction of a smaller carrier: the fractional bandwidth doubles from 500 nm
    to 1000 nm. The truncated pupil should therefore lose more extension in the
    infrared, while the uniform one stays invariant at every color.
    """
    d = np.load(WAVELENGTH_PULSED, allow_pickle=True)
    names = [str(v) for v in d["input"]]
    taus = [str(v) for v in d["tau"]]

    def gain(lam, na, inp, eps, tau):
        for i in range(len(d["eps"])):
            if (float(d["lam"][i]) == lam and float(d["na"][i]) == na
                    and names[i].startswith(inp) and float(d["eps"][i]) == eps
                    and taus[i] == tau):
                return float(d["gain"][i])
        raise AssertionError((lam, na, inp, eps, tau))

    def erosion(lam, inp):
        return 1.0 - gain(lam, 0.8, inp, 0.99, "1 fs") / gain(
            lam, 0.8, inp, 0.99, "continuous wave")

    blue, red = erosion(0.500, "Gaussian"), erosion(1.000, "Gaussian")
    assert red > 1.8 * blue, (
        f"the truncated erosion no longer grows with wavelength: "
        f"{100 * blue:.2f}% at 500 nm against {100 * red:.2f}% at 1000 nm")

    for lam in (0.500, 0.750, 1.000):
        assert abs(erosion(lam, "uniform")) < 0.005, (
            f"uniform is no longer color independent at {lam * 1000:.0f} nm")


def test_axial_results_do_not_depend_on_the_polarization_convention():
    """Every depth quoted in this work is convention free, and exactly so.

    On axis the Bessel arguments vanish, so I1 and I2 are identically zero and
    the azimuthal average, the Romallosa y-cut, the x-cut and the pure scalar
    intensity all collapse to |I0|^2. The depth of focus and the extension are
    therefore the same number whichever convention is quoted; only transverse
    quantities differ. This is asserted rather than argued because the sweeps
    use the azimuthal average while the replication anchor uses the y-cut.
    """
    from mcdo import SimConfig
    from mcdo.annular import compute_integrals_annular
    from mcdo.rw_integrals import compute_integrals

    cfg = SimConfig(lam_c=0.750, X_NA=0.8, n=1.3, tau=np.inf,
                    N_freq=3, N_theta=801)
    z = np.linspace(0.0, 60.0, 6001)
    r0 = np.array([0.0])

    def width(y):
        y = y / y.max()
        i = np.where(y < 0.5)[0][0]
        return 2.0 * np.interp(0.5, [y[i], y[i - 1]], [z[i], z[i - 1]])

    for eps in (0.0, 0.5, 0.9):
        if eps == 0.0:
            A = compute_integrals(r0, z, cfg.k_c, cfg.alpha, 801)
        else:
            A = compute_integrals_annular(r0, z, cfg.k_c, cfg.alpha, eps, 801)
        I0, I1, I2 = A[0][:, 0], A[1][:, 0], A[2][:, 0]
        assert np.abs(I1).max() < 1e-12, "I1 is not zero on axis"
        assert np.abs(I2).max() < 1e-12, "I2 is not zero on axis"
        conventions = [
            np.abs(I0) ** 2 + np.abs(I2) ** 2 + 2 * np.abs(I1) ** 2,
            np.abs(I0 - I2) ** 2,
            np.abs(I0 + I2) ** 2 + 4 * np.abs(I1) ** 2,
            np.abs(I0) ** 2,
        ]
        depths = [width(c) for c in conventions]
        assert max(depths) - min(depths) < 1e-9, (
            f"the axial depth depends on the convention at ratio {eps}: {depths}")


def test_unobstructed_annulus_is_the_plain_disk():
    """The no-blocking annular cases are the earlier stages, not a rerun of them.

    `compute_integrals_annular` returns the unobstructed result unchanged at
    eps = 0, so every baseline in the annular sweeps is the same computation
    the replication and aperture stages used.
    """
    from mcdo import SimConfig
    from mcdo.annular import compute_integrals_annular
    from mcdo.rw_integrals import compute_integrals

    cfg = SimConfig(lam_c=0.750, X_NA=0.8, n=1.3, tau=np.inf,
                    N_freq=3, N_theta=801)
    r = np.linspace(0.0, 2.0, 500)
    z = np.array([0.0])
    a = compute_integrals(r, z, cfg.k_c, cfg.alpha, 801)
    b = compute_integrals_annular(r, z, cfg.k_c, cfg.alpha, 0.0, 801)
    for x, y in zip(a, b):
        assert np.abs(x - y).max() == 0.0, "the eps = 0 annulus is not the disk"


def test_romallosa_focal_width_is_reproduced():
    """The published 472.8 nm, in the convention the paper uses."""
    from mcdo import SimConfig
    from mcdo.rw_integrals import compute_integrals

    cfg = SimConfig(lam_c=0.750, X_NA=0.8, n=1.3, tau=np.inf,
                    N_freq=3, N_theta=801)
    r = np.linspace(0.0, 2.0, 4000)
    A = compute_integrals(r, np.array([0.0]), cfg.k_c, cfg.alpha, 801)
    I0, I2 = A[0][0], A[2][0]
    y = np.abs(I0 - I2) ** 2
    y = y / y.max()
    i = np.where(y < 0.5)[0][0]
    w = 2.0 * np.interp(0.5, [y[i], y[i - 1]], [r[i], r[i - 1]]) * 1000.0
    assert abs(w - 472.8) < 1.0, f"y-cut focal width is {w:.1f} nm, not 472.8"


NUMBERS = os.path.join(ROOT, "output", "presentation", "NUMBERS.md")


@pytest.mark.skipif(not os.path.exists(NUMBERS), reason="sheet not generated")
def test_numbers_sheet_matches_the_sweeps():
    """The reference sheet is generated, so it must agree with its source.

    It exists to be typed onto slides, which makes a stale copy worse than no
    copy: a number that was right when generated and wrong after a rerun would
    be quoted with confidence. This re-derives a sample of its entries.
    """
    with open(NUMBERS, encoding="utf-8") as fh:
        text = fh.read()

    d = np.load(BASE, allow_pickle=True)
    names = [str(v) for v in d["input"]]

    def baseline(field, eps, na=0.8, inp="uniform"):
        for i in range(len(d["eps"])):
            if (float(d["na"][i]) == na and names[i].startswith(inp)
                    and float(d["eps"][i]) == eps):
                return float(d[field][i])
        raise AssertionError((field, eps))

    # the headline extension series
    for eps in (0.5, 0.9, 0.99):
        want = f"{baseline('gain', eps):.2f}x"
        assert want in text, f"sheet is missing the extension {want} at ratio {eps}"

    # the cost columns
    assert f"{baseline('depth_um', 0.99):.2f}" in text
    assert f"{baseline('width_nm', 0.99):.1f}" in text

    # the anchors that are stated rather than computed in the sheet
    for anchor in ("472.8 nm", "0.23%", "13.35%", "1.009"):
        assert anchor in text, f"sheet no longer states {anchor}"


DURATION = os.path.join(ROOT, "output", "05_pulsed_pupils", "duration_sweep.npz")
BREAKDOWN = os.path.join(ROOT, "output", "02_na_apodization",
                         "scalar_breakdown.npz")


@pytest.mark.skipif(not os.path.exists(DURATION), reason="sweep not run")
def test_pulse_becomes_continuous_wave_above_a_few_femtoseconds():
    """The bound that keeps the result honest about its own scope.

    The departure from continuous wave falls as the inverse square of the
    duration, so a pulse longer than about five femtoseconds behaves as
    continuous light for depth of focus. Asserting the falloff as well as the
    crossing matters: a crossing alone would also pass on data that jumped to
    zero for the wrong reason.
    """
    d = np.load(DURATION, allow_pickle=True)
    names = [str(v) for v in d["input"]]

    def depth(inp, tau_fs, eps=0.0):
        for i in range(len(d["eps"])):
            if (names[i].startswith(inp) and float(d["eps"][i]) == eps
                    and ((not np.isfinite(d["tau_fs"][i]) and tau_fs is None)
                         or (np.isfinite(d["tau_fs"][i])
                             and float(d["tau_fs"][i]) == tau_fs))):
                return float(d["depth_um"][i])
        raise AssertionError((inp, tau_fs))

    for inp, within_one_percent in (("uniform", 2.0), ("Gaussian", 5.0)):
        cw = depth(inp, None)
        dev = abs(depth(inp, within_one_percent) / cw - 1.0)
        assert dev <= 0.01, (
            f"{inp} is not within 1% of continuous wave at "
            f"{within_one_percent} fs: {100 * dev:.2f}%")

    # and the falloff is quadratic in duration, not linear
    cw = depth("Gaussian", None)
    a = abs(depth("Gaussian", 2.0) / cw - 1.0)
    b = abs(depth("Gaussian", 10.0) / cw - 1.0)
    ratio = a / b
    assert 15.0 < ratio < 35.0, (
        f"the departure no longer falls as the inverse square of duration: "
        f"2 fs against 10 fs gives a ratio of {ratio:.1f}, expected near 25")


@pytest.mark.skipif(not os.path.exists(BREAKDOWN), reason="sweep not run")
def test_truncation_delays_the_scalar_breakdown():
    """Where a scalar model stops being adequate, and why that moves.

    A truncated pupil concentrates the light near the axis, so the rays that
    carry energy converge at shallower angles than the rim allows and the
    scalar description survives to a higher stated aperture. Both the ordering
    and the size of the shift are checked, since the ordering alone would pass
    on a sweep that barely moved.
    """
    d = np.load(BREAKDOWN)

    def crossing(at, field, threshold):
        m = d["alpha_t"] == at
        order = np.argsort(d["na"][m])
        x, y = d["na"][m][order], d[field][m][order]
        hit = np.where(y >= threshold)[0]
        return float(x[hit[0]]) if len(hit) else float("nan")

    uniform = crossing(0.0, "fwhm_dev", 1.0)
    truncated = crossing(8.0, "fwhm_dev", 1.0)
    assert abs(uniform - 0.45) < 0.03, f"uniform crossing moved to {uniform}"
    assert truncated > uniform + 0.2, (
        f"truncation no longer delays the breakdown: {uniform} against "
        f"{truncated}")

    # the width criterion fires earlier than the root-mean-square ones, at
    # every truncation, and by roughly a factor of two
    for at in (0.0, 2.0, 4.0):
        width = crossing(at, "fwhm_dev", 1.0)
        shape = crossing(at, "rmse_peak", 0.01)
        assert shape > width, (
            f"at truncation {at} the shape criterion no longer outlasts the "
            f"width criterion: {shape} against {width}")
