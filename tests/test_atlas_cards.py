"""Atlas cards must show the field, not a corner of it.

The cards are drawn on a crop of a much wider computed window, so the map is
not mostly empty. Choosing that crop badly is invisible by eye: a card can look
well framed while a third of the field's energy sits outside it, and every side
lobe read off it is then wrong. The crop is bounded on energy for exactly this
reason, and that bound is what this checks.
"""

import glob
import os

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ATLAS = os.path.join(ROOT, "output", "atlas")

FAMILIES = ("annular_grid", "truncation_grid", "pulsed_grid",
            "pulsed_illumination")


def _fields():
    out = []
    for fam in FAMILIES:
        out += sorted(glob.glob(os.path.join(ATLAS, fam, "field_*.npz")))
    return out


@pytest.mark.skipif(not _fields(), reason="atlas not built")
def test_crop_keeps_almost_all_of_the_field_energy():
    """No card may hide more than 5% of its own energy outside the frame."""
    from mcdo.atlascard import _crop
    worst = []
    for f in _fields():
        d = np.load(f)
        I = d["intensity"].astype(float)
        h, v = d["h"], d["v"]
        total = (I * np.abs(h)[None, :]).sum()
        hc, _vc, Ic = _crop(h, v, I)
        kept = (Ic * np.abs(hc)[None, :]).sum()
        lost = 1.0 - kept / total if total > 0 else 0.0
        if lost > 0.05:
            worst.append(f"{os.path.basename(f)}: {100 * lost:.1f}%")
    assert not worst, f"cards clipping real energy: {worst[:6]}"


def test_crop_trims_a_compact_field_and_leaves_a_spread_one_alone():
    """The crop's contract, stated on fields whose right answer is known.

    Real cards cannot test this: an annulus genuinely fills its window, so most
    of them are legitimately left uncropped and a blanket "must be trimmed"
    rule would be false. A narrow focus in a wide window must shrink; a field
    spread across the whole window must not.
    """
    from mcdo.atlascard import _crop
    h = np.linspace(-5.0, 5.0, 301)
    v = np.linspace(-15.0, 15.0, 481)
    H, V = np.meshgrid(h, v)

    tight = np.exp(-(H ** 2) / 0.02 - (V ** 2) / 0.5)
    hc, vc, _ = _crop(h, v, tight)
    area = len(hc) * len(vc) / (len(h) * len(v))
    assert area < 0.25, f"a narrow focus was left on a wide window ({area:.2f})"

    spread = np.exp(-(H ** 2) / 40.0 - (V ** 2) / 300.0)
    hs, vs, _ = _crop(h, v, spread)
    assert len(hs) * len(vs) / (len(h) * len(v)) > 0.7, (
        "a field filling the window was cropped into")


@pytest.mark.skipif(not _fields(), reason="atlas not built")
def test_crop_never_grows_a_card():
    """Cropping may trim or do nothing; it may never widen the window."""
    from mcdo.atlascard import _crop
    for f in _fields():
        d = np.load(f)
        h, v = d["h"], d["v"]
        hc, vc, _ = _crop(h, v, d["intensity"].astype(float))
        assert len(hc) <= len(h) and len(vc) <= len(v), os.path.basename(f)


def _window_limited(path):
    """The on-axis profile is still above half maximum where the card ends."""
    d = np.load(path)
    I = d["intensity"].astype(float)
    ax = I[:, int(np.argmin(np.abs(d["h"])))]
    ax = ax / ax.max()
    return bool(ax[0] >= 0.5 or ax[-1] >= 0.5)


def test_no_deck_figure_shows_a_clipped_focus():
    """A field map on a slide has to contain the depth the slide quotes.

    The truncation-grid window is sized from the unobstructed depth, and at
    obstruction ratio 0.99 the focus is 44 times longer than that. Two stage-7
    slides quoted 107 um beside a map spanning 30 um, where the whole visible
    field sat above half maximum and the half-maximum contour never closed.
    """
    from mcdo.deck import FIGURES, OUT as DECK_OUT, stage_deck
    bad = []
    for item in stage_deck("7"):
        if item[0] != "slide" or not item[3]:
            continue
        rel = FIGURES[item[3]][0]
        if "/atlas/" not in "/" + rel:
            continue
        npz = os.path.join(DECK_OUT, rel).replace(".png", ".npz")
        npz = os.path.join(os.path.dirname(npz),
                           "field_" + os.path.basename(npz))
        if os.path.exists(npz) and _window_limited(npz):
            bad.append(f"{item[1][:40]}: {os.path.basename(rel)}")
    assert not bad, f"slides showing a clipped focus: {bad}"


@pytest.mark.skipif(not _fields(), reason="atlas not built")
def test_no_card_clips_its_own_focus():
    """Every card's axial window must contain the focus it shows.

    Each family sizes its window from the unobstructed depth, which is wrong
    wherever the ring extends the focus past it: at obstruction ratio 0.99 the
    focus is 44 times longer, and 18 cards showed a flat-topped bar whose
    half-maximum contour never closed. Windows are now sized from the depth
    each cell actually has.
    """
    clipped = [os.path.basename(f) for f in _fields() if _window_limited(f)]
    assert not clipped, f"{len(clipped)} cards clip their focus: {clipped[:6]}"
