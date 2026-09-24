"""The dashboard must offer exactly what has been computed.

Two failures are possible and both are silent. A field can be computed and
never reach the page, because each atlas family needs its own reader and a
missing one drops the whole family. Or the page can offer a control value it
has no field for, which used to blank the figure with no explanation.

These check both directions against the files actually on disk.
"""

import json
import os
import re

import numpy as np

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, "output", "03_annular", "field_map_dashboard.html")
ATLAS = os.path.join(ROOT, "output", "atlas")

NA = ["0.1", "0.8", "1.2"]
INP = ["uniform", "gaussian"]
ALPHA = ["alpha0.0", "alpha1.0", "alpha2.0", "alpha4.0", "alpha8.0"]
EPS = ["0.0", "0.3", "0.5", "0.7", "0.9", "0.95", "0.99"]
TAU = ["cw", "2fs", "1fs"]


def _reachable():
    """Every key the controls can select, honouring the alpha sweep's pinning."""
    keys = {f"{a}|{i}|{e}|{t}"
            for a in NA for i in INP for e in EPS for t in TAU}
    keys |= {f"0.8|{i}|{e}|cw" for i in ALPHA for e in EPS}
    return keys


def _data():
    with open(HTML, encoding="utf-8") as fh:
        text = fh.read()
    m = re.search(r"const DATA = (\{.*?\});\nconst MEAS", text, re.S)
    assert m, "dashboard has no DATA block"
    return json.loads(m.group(1))


def _tag(x):
    return str(x).replace(".", "p")


def _fields_on_disk():
    """The key each saved atlas field should appear under, by family."""
    want = {}
    for na in NA:
        for inp in INP:
            for eps in EPS:
                f = f"annular_grid/field_na{_tag(na)}_{inp}_eps{_tag(eps)}.npz"
                want[f"{na}|{inp}|{eps}|cw"] = f
                for tau in ("2fs", "1fs"):
                    g = (f"pulsed_grid/field_na{_tag(na)}_{inp}"
                         f"_eps{_tag(eps)}_{tau}.npz")
                    want[f"{na}|{inp}|{eps}|{tau}"] = g
    for at in ALPHA:
        for eps in EPS:
            f = f"truncation_grid/field_at{_tag(at[5:])}_eps{_tag(eps)}.npz"
            want[f"0.8|{at}|{eps}|cw"] = f
    for inp in INP:
        for eps in EPS:
            for tau in ("cw", "1fs"):
                f = f"pulsed_illumination/field_{inp}_eps{_tag(eps)}_{tau}.npz"
                want.setdefault(f"0.8|{inp}|{eps}|{tau}", f)
    return {k: v for k, v in want.items()
            if os.path.exists(os.path.join(ATLAS, v))}


def _stale():
    """Field files written after the page was built, if any."""
    built = os.path.getmtime(HTML)
    return [k for k, rel in _fields_on_disk().items()
            if os.path.getmtime(os.path.join(ATLAS, rel)) > built]


@pytest.mark.skipif(not os.path.exists(HTML), reason="dashboard not built")
def test_every_computed_field_reaches_the_page():
    """A family without a reader would vanish from the page entirely.

    Fields written after the page was built are excluded: that is a stale
    dashboard, reported separately, not a missing reader.
    """
    data = _data()
    fresh = set(_fields_on_disk()) - set(_stale())
    missing = sorted(k for k in fresh if k not in data)
    assert not missing, (
        f"{len(missing)} computed fields never reach the dashboard, "
        f"e.g. {missing[:6]}")


@pytest.mark.skipif(not os.path.exists(HTML), reason="dashboard not built")
def test_dashboard_is_not_stale():
    """Every computed field should be in the published page.

    This fails while a sweep is still writing, which is the correct reading:
    the page on disk does not yet show everything that has been computed.
    """
    stale = sorted(_stale())
    assert not stale, (
        f"{len(stale)} fields are newer than the dashboard; rerun "
        f"scripts/dashboard_field_maps.py (e.g. {stale[:4]})")


@pytest.mark.skipif(not os.path.exists(HTML), reason="dashboard not built")
def test_no_configuration_is_offered_without_data():
    """Nothing in DATA may sit outside what the controls can actually select."""
    orphans = sorted(set(_data()) - _reachable())
    assert not orphans, f"unreachable configurations in DATA: {orphans[:6]}"


@pytest.mark.skipif(not os.path.exists(HTML), reason="dashboard not built")
def test_unavailable_controls_are_disabled():
    """The page greys out what it cannot draw rather than blanking the figure."""
    with open(HTML, encoding="utf-8") as fh:
        text = fh.read()
    assert "refreshAvailability" in text, "no availability pass in the page"
    assert "classList.contains('off')" in text, (
        "disabled controls are still clickable")


@pytest.mark.skipif(not os.path.exists(HTML), reason="dashboard not built")
def test_no_data_message_does_not_describe_stale_coverage():
    """The empty-state text must not name a coverage that has since changed.

    It used to tell the viewer which combinations existed, listing two
    obstruction ratios at one aperture. That was true when 66 of 161
    combinations were computed and became false, silently, once the rest were
    filled in - the page would have been telling a viewer its data was missing
    while showing them the data.
    """
    with open(HTML, encoding="utf-8") as fh:
        text = fh.read()
    for stale in ("obstruction ratio '", "0.5 and 0.9", "Pulsed fields exist"):
        assert stale not in text, f"empty-state text still claims: {stale}"


@pytest.mark.skipif(not os.path.exists(HTML), reason="dashboard not built")
def test_packed_maps_decode_to_the_field_they_came_from():
    """Maps are stored as base64 bytes; a mismatched writer would be invisible.

    Five separate places in the collector emit a map. If one kept the old
    float form, or packed a different shape than it declared, the page would
    still load and that configuration alone would draw nonsense. This decodes
    a map the same way the browser does and compares it against the atlas
    field it was built from.
    """
    import base64
    data = _data()
    key = "0.8|uniform|0.9|cw"
    if key not in data:
        pytest.skip("reference configuration not built")
    z = data[key]["z"]
    raw = np.frombuffer(base64.b64decode(z["b"]), dtype=np.uint8).astype(float)
    assert raw.size == z["r"] * z["c"], "declared shape does not match the bytes"
    got = (raw - 200).reshape(z["r"], z["c"]) / 50.0
    assert -4.001 <= got.min() and got.max() <= 0.001, (
        f"decoded range {got.min():.2f}..{got.max():.2f} is outside one to 1e-4")

    src = os.path.join(ATLAS, "pulsed_illumination",
                       "field_uniform_eps0p9_cw.npz")
    if not os.path.exists(src):
        pytest.skip("source field not built")
    I = np.load(src)["intensity"].astype(float)
    I = I / I.max()
    ref = np.log10(np.maximum(I[::4, ::4], 1e-4))
    assert got.shape == ref.shape, f"{got.shape} against {ref.shape}"
    assert np.abs(got - ref).max() <= 0.011, (
        f"decoded map differs from the field by "
        f"{np.abs(got - ref).max():.4f} decades")


@pytest.mark.skipif(not os.path.exists(HTML), reason="dashboard not built")
def test_every_map_declares_a_shape_matching_its_bytes():
    """Cheap structural check across all of them, not just the sampled one."""
    import base64
    for key, entry in _data().items():
        z = entry["z"]
        assert len(base64.b64decode(z["b"])) == z["r"] * z["c"], key


@pytest.mark.skipif(not os.path.exists(HTML), reason="dashboard not built")
def test_compare_view_is_wired_end_to_end():
    """The comparison feature needs four pieces present together.

    A second selector whose values reach the reference key, a panel that
    appears when it is chosen, a difference map, and paired measurements. Any
    one missing leaves a control that looks live and does nothing, which is
    how the first attempt shipped.
    """
    with open(HTML, encoding="utf-8") as fh:
        text = fh.read()

    for group in ("bna", "binp", "beps", "btau"):
        assert f'data-group="{group}"' in text, (
            f"the second selector has no {group} control")

    assert "sel.ref === 'pick'" in text, "the second selector is not read"
    assert "getElementById('bcontrols')" in text, "the panel never appears"
    assert "Plotly.react('diff'" in text, "no difference map"
    assert 'id="diff"' in text, "the difference map has no element to draw into"
    assert "getElementById('diffstats')" in text, "no paired measurements"
    assert "RdBu" in text, "the difference map is not on a diverging scale"


@pytest.mark.skipif(not os.path.exists(HTML), reason="dashboard not built")
def test_every_control_value_reaches_the_selection_state():
    """A control whose group is not in `sel` silently does nothing when clicked."""
    import re
    with open(HTML, encoding="utf-8") as fh:
        text = fh.read()
    groups = set(re.findall(r'data-group="([a-z]+)"', text))
    m = re.search(r"const sel = \{(.*?)\};", text, re.S)
    assert m, "no selection state in the page"
    keys = set(re.findall(r"(\w+)\s*:", m.group(1)))
    orphans = sorted(groups - keys)
    assert not orphans, f"controls with no state behind them: {orphans}"
