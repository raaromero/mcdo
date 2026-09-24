"""Enforce docs/STANDARDS.md so presentation defects cannot regress.

These caught real problems repeatedly: underscored display strings leaking into
figures (``X_NA``, ``alpha_t``), internal planning vocabulary in figure titles
("Phase 3"), and deck entries pointing at figures nothing produces.
"""

import os
import re
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
SCRIPTS = os.path.join(ROOT, "scripts")

# Calls whose string argument is rendered for a reader.
DISPLAY_CALL = re.compile(
    r"(?:set_title|set_xlabel|set_ylabel|suptitle)\(\s*[a-z]?(['\"])(.*?)\1", re.S
)
# Underscored identifiers that must never appear in rendered text.
BAD_TOKEN = re.compile(r"(?<![\\$])\b(?:X_NA|alpha_t|N_theta|N_freq|lam_c|r_ap|w_beam)\b|α_t")
PHASE = re.compile(r"\bPhase\s+\d", re.I)


def _script_files():
    return sorted(
        os.path.join(SCRIPTS, f)
        for f in os.listdir(SCRIPTS)
        if f.endswith(".py") and not f.startswith("_")
    )


def _display_strings(path):
    with open(path, encoding="utf-8") as fh:
        src = fh.read()
    return [m.group(2) for m in DISPLAY_CALL.finditer(src)]


@pytest.mark.parametrize("path", _script_files(), ids=os.path.basename)
def test_no_underscored_identifiers_in_rendered_text(path):
    """Axis labels and titles must not expose code identifiers."""
    offenders = [s for s in _display_strings(path) if BAD_TOKEN.search(s)]
    assert not offenders, (
        f"{os.path.basename(path)} renders code identifiers: {offenders}. "
        "Use reader-facing wording (see docs/STANDARDS.md)."
    )


@pytest.mark.parametrize("path", _script_files(), ids=os.path.basename)
def test_no_internal_phase_vocabulary_in_titles(path):
    """'Phase N' is planning vocabulary, not physics; it must not reach a figure."""
    offenders = [s for s in _display_strings(path) if PHASE.search(s)]
    assert not offenders, (
        f"{os.path.basename(path)} puts internal phase labels in a figure: {offenders}"
    )


def test_deck_manifest_is_consistent():
    """Every declared figure is used, every used figure is declared."""
    from mcdo.deck import DECK, FIGURES

    used = set()
    for item in DECK:
        if item[0] == "slide" and item[3]:
            used.update([item[3]] if isinstance(item[3], str) else item[3])
    undeclared = used - set(FIGURES)
    assert not undeclared, f"deck slides reference undeclared figures: {sorted(undeclared)}"

    unused = set(FIGURES) - used
    assert not unused, f"FIGURES declares figures no slide uses: {sorted(unused)}"


def test_deck_figures_name_a_real_generating_script():
    """A missing figure must be recoverable: the named script has to exist."""
    from mcdo.deck import FIGURES

    missing = [
        (key, script)
        for key, (_rel, script) in FIGURES.items()
        if not os.path.exists(os.path.join(ROOT, script))
    ]
    assert not missing, f"figures name scripts that do not exist: {missing}"


def test_deck_latex_keys_resolve():
    """Slides may only reference equations that exist."""
    from mcdo.deck import DECK, LX

    referenced = {item[4] for item in DECK if item[0] == "slide" and item[4]}
    unknown = referenced - set(LX)
    assert not unknown, f"slides reference unknown equations: {sorted(unknown)}"


def _estimated_text_height(shape):
    """Rough rendered height of a text box, in inches.

    Approximates the wrapped line count from the character count and the box
    width, using an average glyph advance of about 0.5 em for Helvetica. It is
    deliberately conservative: it catches bullets that clearly overrun their
    box, not borderline cases.
    """
    width_in = shape.width / 914400
    total = 0.0
    for para in shape.text_frame.paragraphs:
        text = "".join(r.text for r in para.runs)
        if not text:
            continue
        size_pt = max((r.font.size.pt for r in para.runs if r.font.size), default=18)
        indent_in = 0.35 * para.level
        # 0.5 em under-counts real advance widths; 0.58 matches what
        # PowerPoint actually wraps at, and the +1 accounts for the fact
        # that a wrapped line rarely fills to the last character.
        chars_per_line = max(8, int((width_in - indent_in) * 72 / (size_pt * 0.58)))
        lines = max(1, -(-len(text) // chars_per_line))
        total += lines * size_pt * 1.22 / 72 + 9 / 72       # line height + paragraph space
    return total


def test_slide_text_fits_its_box():
    """Bullet text must not obviously overrun the box it was given."""
    from pptx import Presentation

    deck = os.path.join(ROOT, "output", "deck", "mcdo_results_deck.pptx")
    if not os.path.exists(deck):
        pytest.skip("deck not built yet")

    offenders = []
    for index, slide in enumerate(Presentation(deck).slides, start=1):
        for shape in slide.shapes:
            if not shape.has_text_frame or not shape.text_frame.text.strip():
                continue
            if shape.top <= 500000:            # the title band, single line
                continue
            box_in = shape.height / 914400
            needed = _estimated_text_height(shape)
            if needed > box_in * 1.15:         # 15 per cent slack for the estimate
                first = shape.text_frame.text.strip().split("\n")[0][:44]
                offenders.append(f"slide {index}: needs ~{needed:.1f} in of {box_in:.1f} in — {first}")
    assert not offenders, "text overruns its box on:\n  " + "\n  ".join(offenders[:12])


def _deck_scripts():
    from mcdo.deck import FIGURES

    return sorted({os.path.join(ROOT, script) for _rel, script in FIGURES.values()})


def _titles(path):
    pattern = re.compile(r"(?:set_title|suptitle)\(\s*f?(['\"])(.*?)\1", re.S)
    with open(path, encoding="utf-8") as fh:
        return [m.group(2) for m in pattern.finditer(fh.read())]


@pytest.mark.parametrize("path", _deck_scripts(), ids=os.path.basename)
def test_figure_titles_are_plain_and_descriptive(path):
    """Deck figure titles: descriptive, no asides, no line breaks, sentence case."""
    offenders = []
    for raw in _titles(path):
        # f-string placeholders are code, not rendered text
        title = re.sub(r"\{[^{}]*\}", "", raw)
        core = re.sub(r"^\([a-zA-Z0-9]\)\s*", "", title).strip()
        if "[" in title:
            offenders.append(f"bracketed aside: {title[:60]}")
        elif "\\n" in title:
            offenders.append(f"line break: {title[:60]}")
        elif re.search(r"[A-Za-z]_[A-Za-z]", title):
            offenders.append(f"underscore: {title[:60]}")
        elif core[:1].islower():
            offenders.append(f"lowercase start: {title[:60]}")
    assert not offenders, f"{os.path.basename(path)}:\n  " + "\n  ".join(offenders)


@pytest.mark.parametrize("path", _deck_scripts(), ids=os.path.basename)
def test_figures_are_high_resolution(path):
    """Every saved figure must be at least 300 dpi."""
    with open(path, encoding="utf-8") as fh:
        src = fh.read()
    low = [d for d in re.findall(r"dpi\s*[=:]\s*(\d+)", src) if int(d) < 300]
    assert not low, f"{os.path.basename(path)} saves at dpi {low}, below the 300 standard"


CUT_WORD = re.compile(r"[xy][- ]cut", re.I)


@pytest.mark.parametrize("path", _deck_scripts(), ids=os.path.basename)
def test_no_cut_jargon_in_rendered_text(path):
    """'x-cut'/'y-cut' is internal jargon; rendered text names the component."""
    pattern = re.compile(
        r"(?:label\s*=|set_title|set_xlabel|set_ylabel|suptitle)\(?\s*f?(['\"])(.*?)\1", re.S
    )
    with open(path, encoding="utf-8") as fh:
        src = fh.read()
    offenders = [m.group(2)[:60] for m in pattern.finditer(src) if CUT_WORD.search(m.group(2))]
    assert not offenders, f"{os.path.basename(path)} renders cut jargon: {offenders}"


@pytest.mark.parametrize("path", _deck_scripts(), ids=os.path.basename)
def test_plot_line_widths_meet_standard(path):
    """Data curves are at least 1.6 pt so they survive projection."""
    offenders = []
    with open(path, encoding="utf-8") as fh:
        for number, line in enumerate(fh, start=1):
            if re.search(r"\.(?:plot|semilogy|loglog|semilogx)\(", line) \
                    and "axhline" not in line and "axvline" not in line:
                for w in re.findall(r"lw=([\d.]+)", line):
                    if 0 < float(w) < 1.6:   # lw=0 is a marker-only series
                        offenders.append(f"line {number}: lw={w}")
    assert not offenders, f"{os.path.basename(path)} has thin data lines: {offenders}"



def test_declared_figures_exist_on_disk():
    """A slide must never be built around a figure that is not there."""
    from mcdo.deck import FIGURES, OUT
    missing = [rel for rel, _ in FIGURES.values()
               if not os.path.exists(os.path.join(OUT, rel))]
    assert not missing, f"declared but absent: {sorted(missing)[:8]}"


def test_panel_index_matches_panel_content():
    """A slide's figure must be the panel it means, not whatever took that index.

    Every panel records its own title. Where a panel title carries a numeric
    setting (a numerical aperture, an obstruction ratio, a pulse duration), the
    slide that uses it has to name the same value.
    """
    import json
    from mcdo.deck import DECK, FIGURES, OUT

    titles = {}
    for root, _dirs, files in os.walk(OUT):
        for name in files:
            if name.endswith("_panels.json"):
                with open(os.path.join(root, name)) as fh:
                    for panel, title in json.load(fh).items():
                        rel = os.path.relpath(os.path.join(root, panel), OUT)
                        titles[rel] = title

    number = re.compile(r"\d+\.\d+")
    offenders = []
    for item in DECK:
        if item[0] != "slide" or not item[3]:
            continue
        keys = [item[3]] if isinstance(item[3], str) else list(item[3])
        if len(keys) != 1 or keys[0] not in FIGURES:
            continue
        rel = FIGURES[keys[0]][0]
        panel_title = titles.get(rel)
        if not panel_title:
            continue
        wanted = set(number.findall(panel_title))
        if not wanted:
            continue
        text = item[1] + " " + " ".join(b[1] for b in item[2])
        if not wanted & set(number.findall(text)):
            offenders.append(f"{item[3]}: slide {item[1]!r} vs panel {panel_title!r}")
    assert not offenders, "slide and panel disagree:\n  " + "\n  ".join(offenders[:10])


@pytest.mark.parametrize("path", _deck_scripts(), ids=os.path.basename)
def test_no_figure_numbers_in_titles(path):
    """A plot title names what is shown, never 'Fig. N' from a source paper."""
    pattern = re.compile(
        r"(?:set_title|suptitle)\(\s*r?f?(['\"])(.*?)\1", re.S)
    with open(path, encoding="utf-8") as fh:
        src = fh.read()
    bad = re.compile(r"\b(fig|figure)\.?\s*\d", re.I)
    offenders = [m.group(2)[:60] for m in pattern.finditer(src) if bad.search(m.group(2))]
    assert not offenders, f"{os.path.basename(path)} names a figure number: {offenders}"


@pytest.mark.parametrize("path", _deck_scripts(), ids=os.path.basename)
def test_legend_labels_are_capitalized(path):
    """Legend entries read as labels, not as sentence fragments.

    The first version of this only matched labels whose literal text began
    with a lowercase letter, so an f-string label starting with a placeholder
    slipped through and shipped a lowercase legend. It now strips the
    placeholders and checks the literal text that remains.
    """
    pattern = re.compile(r"label\s*=\s*r?f?(['\"])(.*?)\1", re.S)
    with open(path, encoding="utf-8") as fh:
        src = fh.read()
    offenders = []
    for m in pattern.finditer(src):
        text = m.group(2)
        literal = re.sub(r"\{[^}]*\}", "", text).strip()
        if not literal or literal.startswith(("$", "\\")):
            continue
        if literal[0].islower():
            offenders.append(text[:50])
    assert not offenders, f"{os.path.basename(path)} lowercase legends: {offenders}"


SYMBOLS = {"epsilon": "ε", "theta": "θ", "lambda": "λ", "omega": "ω",
           "tau": "τ", "alpha": "α"}


@pytest.mark.parametrize("path", _deck_scripts(), ids=os.path.basename)
def test_greek_letters_are_written_as_symbols(path):
    """Anything a reader of the figure sees uses the symbol, not the word.

    Generalized from the truncation coefficient, which was corrected several
    times by hand: the same rule applies to every Greek letter this work uses.
    Docstrings and comments are prose and are left alone.
    """
    with open(path, encoding="utf-8") as fh:
        src = fh.read()
    drawn = re.findall(r"(?:label|set_xlabel|set_ylabel|set_title|suptitle)"
                       r"\s*\(\s*r?f?(['\"])(.*?)\1", src, re.S)
    offenders = []
    for _q, text in drawn:
        for word, sym in SYMBOLS.items():
            if (re.search(rf"\b{word}\b", text) and sym not in text
                    and f"{word}_" not in text):
                offenders.append(f"{word}: {text[:50]}")
    assert not offenders, (
        f"{os.path.basename(path)} spells out a symbol in drawn text: "
        f"{offenders}")


@pytest.mark.parametrize("path", _deck_scripts(), ids=os.path.basename)
def test_truncation_is_written_as_a_symbol(path):
    """The truncation coefficient is alpha, and it is spelled with the symbol.

    Writing it out as a word in a legend or an axis label has been corrected
    repeatedly. Prose in docstrings and comments is left alone; this checks
    only text that reaches a reader of the figure.
    """
    with open(path, encoding="utf-8") as fh:
        src = fh.read()
    drawn = re.findall(r"(?:label|set_xlabel|set_ylabel|set_title)\s*\(\s*"
                       r"r?f?(['\"])(.*?)\1", src, re.S)
    offenders = [t[:60] for _q, t in drawn
                 if re.search(r"\balpha\b", t) and "α" not in t
                 and "alpha_" not in t]
    assert not offenders, (
        f"{os.path.basename(path)} spells out alpha in drawn text: {offenders}")


def test_figure_slides_state_the_source():
    """A figure slide names the source condition it was computed under.

    Center wavelength or pulse duration is the one setting a reader cannot
    infer from the plot, and every result here depends on it.
    """
    from mcdo.deck import DECK
    offenders = []
    for item in DECK:
        if item[0] != "slide" or not item[3]:
            continue
        text = " ".join(b[1] for b in item[2])
        if not any(k in text for k in ("750", " nm", " fs", "wavelength")):
            offenders.append(item[1][:60])
    assert not offenders, f"figure slides not stating the source: {offenders[:8]}"


BRITISH = re.compile(
    r"\b(centre|colour|normalise[sd]?|analyse[sd]?|behaviour|favour|modelling"
    r"|artefact|apodised|generalised)\b", re.I)


@pytest.mark.parametrize("path", _deck_scripts(), ids=os.path.basename)
def test_us_spelling_in_scripts(path):
    """US spelling throughout: center, color, normalize."""
    with open(path, encoding="utf-8") as fh:
        found = sorted({m.group(0) for m in BRITISH.finditer(fh.read())})
    assert not found, f"{os.path.basename(path)} uses {found}"


def test_us_spelling_everywhere_else():
    """The rule covers the package and the tests, not only the scripts.

    British spellings kept reappearing in module docstrings and test messages,
    which the scripts-only sweep never looked at.
    """
    import glob
    offenders = {}
    for base in ("mcdo", "tests"):
        for path in glob.glob(os.path.join(ROOT, base, "*.py")):
            if os.path.basename(path) == "test_standards.py":
                continue
            with open(path, encoding="utf-8") as fh:
                found = sorted({m.group(0) for m in BRITISH.finditer(fh.read())})
            if found:
                offenders[os.path.basename(path)] = found
    assert not offenders, f"British spellings: {offenders}"


def test_us_spelling_in_deck():
    with open(os.path.join(ROOT, "mcdo", "deck.py"), encoding="utf-8") as fh:
        found = sorted({m.group(0) for m in BRITISH.finditer(fh.read())})
    assert not found, f"deck.py uses {found}"


PER_CENT = re.compile(r"per\s+cent", re.I)


@pytest.mark.parametrize("path", _deck_scripts(), ids=os.path.basename)
def test_percent_sign_not_spelled_out(path):
    """Write %, never 'per cent'."""
    with open(path, encoding="utf-8") as fh:
        assert not PER_CENT.search(fh.read()), f"{os.path.basename(path)} spells out per cent"


def test_percent_sign_not_spelled_out_in_deck():
    with open(os.path.join(ROOT, "mcdo", "deck.py"), encoding="utf-8") as fh:
        assert not PER_CENT.search(fh.read()), "deck.py spells out per cent"


INFORMAL = re.compile(
    r"\b(budget|knobs?|buys?|spoil\w*|sensational\w*|octaves?|optimistic)\b", re.I)


def test_no_informal_terms_in_deck():
    """Slide text uses the vocabulary of an optics paper."""
    with open(os.path.join(ROOT, "mcdo", "deck.py"), encoding="utf-8") as fh:
        found = sorted({m.group(0).lower() for m in INFORMAL.finditer(fh.read())})
    assert not found, f"deck.py uses informal terms: {found}"


@pytest.mark.parametrize("path", _deck_scripts(), ids=os.path.basename)
def test_no_informal_terms_in_scripts(path):
    """The same vocabulary rule, in the scripts and their docstrings.

    Slide text is not the only thing anyone reads. A word rejected on a slide
    is rejected in the module that produced it, so the two cannot drift apart.
    """
    with open(path, encoding="utf-8") as fh:
        found = sorted({m.group(0).lower() for m in INFORMAL.finditer(fh.read())})
    assert not found, f"{os.path.basename(path)} uses informal terms: {found}"


# Only the signatures a mid-word cut actually leaves. A sentence may legitimately
# end in a preposition ("falls short of", "fills in"), so those are not flagged.
TRUNCATED = re.compile(r"(?:[=,(]|\s(?:the|a|an|and|with the|of the|at|from|into))\s*$")


def test_no_truncated_bullets():
    """A bullet is a whole sentence, never a sentence cut off mid-clause."""
    from mcdo.deck import DECK
    offenders = []
    for item in DECK:
        if item[0] != "slide":
            continue
        for _lvl, text in item[2]:
            if TRUNCATED.search(text):
                offenders.append(f"{item[1][:34]}: ...{text[-42:]}")
    assert not offenders, "bullets cut mid-clause:\n  " + "\n  ".join(offenders[:8])


def test_scripts_do_not_share_output_paths():
    """Two scripts writing the same file will silently overwrite each other."""
    import collections
    from mcdo.deck import FIGURES
    owners = collections.defaultdict(set)
    for rel, script in FIGURES.values():
        owners[rel].add(script)
    clashes = {rel: sorted(s) for rel, s in owners.items() if len(s) > 1}
    assert not clashes, f"figures written by more than one script: {clashes}"


WIDTH_TALK = re.compile(r"\b(focal|transverse)\s+width\b", re.I)


def test_stage7_compares_on_depth_of_focus_only():
    """The working deck reports depth of focus, never a transverse width.

    Earlier stages measured focal width legitimately and still quote it, so
    this is not a repository-wide ban. It is scoped to the stage the annular
    results are argued in, where every comparison was asked to rest on depth
    of focus alone: quoting a width there invites a second, unasked-for
    conclusion alongside the one the slide is making.
    """
    from mcdo.deck import stage_deck
    offenders = []
    for item in stage_deck("7"):
        if item[0] != "slide":
            continue
        for _, text in item[2]:
            if WIDTH_TALK.search(text):
                offenders.append(f"{item[1][:40]}: {text[:70]}")
        if WIDTH_TALK.search(item[1]):
            offenders.append(item[1][:60])
    assert not offenders, f"stage 7 quotes a width: {offenders[:6]}"


def test_optical_coordinate_equation_carries_the_refractive_index():
    """The slide equation for u and v has to use the same k the code does.

    `SimConfig.k_c` is 2*pi*n/lambda with lambda the vacuum wavelength, and the
    settings slide quotes 750 nm and index 1.3 separately. An equation written
    as 2*pi/lambda is then wrong by the index for anyone who copies it out,
    which is what these notes are for.
    """
    from mcdo.deck import LX
    coords = LX["coords"]
    assert r"\frac{2\pi n}{\lambda}" in coords, (
        f"optical coordinates omit the refractive index: {coords[:80]}")
    assert r"\frac{2\pi}{\lambda}" not in coords, (
        "optical coordinates still show a vacuum wave number somewhere")


def test_nothing_imports_from_a_script():
    """Scripts run top to bottom, so importing one runs it.

    Most scripts here have no main guard by design: they are figure recipes,
    executed once. That is safe only while nothing imports them. A test that
    pulled a helper out of a figure script would silently recompute that figure
    on every run, which has cost real time twice. Shared code belongs in mcdo/.
    """
    offenders = []
    for base in ("tests", "mcdo", "scripts"):
        root = os.path.join(ROOT, base)
        for dirpath, _dirs, files in os.walk(root):
            for fn in files:
                if not fn.endswith(".py"):
                    continue
                path = os.path.join(dirpath, fn)
                with open(path, encoding="utf-8") as fh:
                    for n, line in enumerate(fh, 1):
                        if re.match(r"\s*(from scripts[. ]|import scripts\b)",
                                    line):
                            offenders.append(
                                f"{os.path.relpath(path, ROOT)}:{n}")
    assert not offenders, (
        f"importing a script executes it; move the shared code into mcdo/: "
        f"{offenders}")


def test_field_map_legend_matches_what_is_drawn():
    """The settings slide tells the reader how to read every field map.

    It names two markings by color, and nothing otherwise ties that sentence
    to the drawing code. A palette change would leave the slide describing
    something the maps no longer show.
    """
    import inspect
    from mcdo.figio import mark_focus
    src = inspect.getsource(mark_focus)
    assert '"#ff7f0e"' in src, "the half-maximum contour is no longer orange"
    assert 'color="red", ls="--"' in src, (
        "the Airy radius is no longer a red dashed line")
    assert "levels=[level]" in src and "level=0.5" in src, (
        "the marked contour is no longer the half maximum")

    from mcdo.deck import stage_deck
    said = [t for item in stage_deck("7") if item[0] == "slide"
            for _, t in item[2] if "orange" in t.lower()]
    assert said, "the field-map legend has gone from the settings slide"
    for line in said:
        assert "half maximum" in line.lower() and "airy" in line.lower(), line


def test_built_decks_embed_the_current_figures():
    """The deck build checks that figures exist, not that they are the ones in it.

    Rebuilding a figure after building a deck leaves the deck valid by that
    check and wrong on screen. Four stage-7 field maps were stale this way
    after the atlas cards were reframed: the file was present, the image
    inside the deck was the old one.
    """
    import hashlib
    import zipfile
    from mcdo.deck import FIGURES, OUT as DECK_OUT, stage_deck

    def digest(rel):
        path = os.path.join(DECK_OUT, rel)
        if not os.path.exists(path):
            return None
        with open(path, "rb") as fh:
            return hashlib.md5(fh.read()).hexdigest()

    decks = [(os.path.join(ROOT, "output", "deck", "mcdo_results_deck.pptx"),
              list(FIGURES), "full deck")]
    stage7 = os.path.join(os.path.expanduser("~"), "Downloads",
                          "stage7_rebuilt.pptx")
    if os.path.exists(stage7):
        decks.append((stage7,
                      [it[3] for it in stage_deck("7")
                       if it[0] == "slide" and it[3]], "stage 7"))

    for path, keys, name in decks:
        if not os.path.exists(path):
            continue
        with zipfile.ZipFile(path) as z:
            media = {hashlib.md5(z.read(n)).hexdigest()
                     for n in z.namelist() if n.startswith("ppt/media/")}
        stale = [k for k in keys
                 if digest(FIGURES[k][0]) and digest(FIGURES[k][0]) not in media]
        assert not stale, f"{name} embeds outdated figures: {stale[:6]}"


def test_presentation_index_matches_its_folder():
    """The index is what someone builds slides from, so it must not lie.

    Two of its filenames were wrong on the first pass - it named a ratio as
    0.90 where the file says 0.9 - which would send someone hunting for a
    figure that exists under another name mid-preparation.
    """
    import glob
    folder = os.path.join(ROOT, "output", "presentation")
    index = os.path.join(folder, "README.md")
    if not os.path.exists(index):
        pytest.skip("presentation folder not assembled")
    with open(index, encoding="utf-8") as fh:
        text = fh.read()
    named = {n for n in re.findall(r"`([A-Za-z0-9_./]+\.png)`", text)
             if ".." not in n}
    have = {os.path.basename(f) for f in glob.glob(os.path.join(folder, "*.png"))}
    have |= {"field_maps/" + os.path.basename(f)
             for f in glob.glob(os.path.join(folder, "field_maps", "*.png"))}
    missing = sorted(n for n in named if n not in have)
    assert not missing, f"the index names figures that are not there: {missing}"
    unindexed = sorted(h for h in have
                       if not h.startswith("field_maps/") and h not in named)
    assert not unindexed, f"figures present but not in the index: {unindexed}"


def test_slides_carry_one_panel_when_panels_exist():
    """A slide shows one plot, not a composite of four.

    Every figure script writes its panels individually as well as together, so
    a slide pointing at the composite is choosing the harder-to-read option.
    This has been corrected by hand more than once; the check is cheap.

    Composites are allowed only where no panel breakdown was written, which is
    the case for the single-axis figures.
    """
    import json
    from mcdo.deck import DECK, FIGURES, OUT as DECK_OUT

    offenders = []
    for item in DECK:
        if item[0] != "slide" or len(item) < 4:
            continue
        key = item[3]
        if not key or not isinstance(key, str):
            continue
        rel = FIGURES[key][0]
        if "/panels/" in rel:
            continue
        stem = os.path.basename(rel)[:-4]
        manifest = os.path.join(DECK_OUT, os.path.dirname(rel), "panels",
                                f"{stem}_panels.json")
        if not os.path.exists(manifest):
            continue
        with open(manifest, encoding="utf-8") as fh:
            panels = json.load(fh)
        if len(panels) > 1:
            offenders.append(f"{item[1][:44]} -> {stem} ({len(panels)} panels)")
    assert not offenders, (
        "slides showing a multi-panel composite where single panels exist: "
        f"{offenders[:8]}")
