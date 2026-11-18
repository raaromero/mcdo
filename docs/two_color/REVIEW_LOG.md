# Review log and handoff

The running record of what is being reviewed, what was found, and what is left. Update it at the end of every
working pass. Newest pass first. Read `START_HERE.md` before this file.

## Open items (do these, in this order)

1. **Wording of the deck `2ce_high_na_pulses.pptx`: done 2026-11-17, keep it that way.** The user rejected its
   language three times ("The focus at X", "scientific presentation", "no telegraphed phrases or sentences"): titles
   and bullets had been shortened to fit one line and had lost their subject, verb or reason. All titles and bullets
   were rewritten (commit 36ed3a8). The rules for any later change:
   - Never shorten a sentence to fit a line. A bullet may take two lines. One or two bullets per slide.
   - A slide carried over keeps the approved wording word for word: Part 3 (pulses) from `pulse_results.pptx` (read
     the file with python-pptx; do not import its script); Part 2 from the `title` and `items` of
     `output/08_two_color/decks/2ce_meeting_manifest.json`.
   - New slides use the vocabulary of the paper they extend (Romallosa et al. (2003): "intensity distribution near
     focus", "zero points", "spectral bandwidth"; Lim & Saloma: "misalignment", "peak 2CE fluorescence").
   - No title starts with "The". The deck script sizes each title from its measured width so that it stays on one
     line (19 to 24 pt).
   - After any change: rebuild, run `scripts/pptx_resave_pdf.py` on the deck (it opens PowerPoint on the user's
     screen, re-saves the file so that Keynote loads it, and writes the PDF beside it), then LOOK at the PDF pages
     (`pdftoppm -r 100 -png`) before telling the user anything.
   Still open in this deck: the figures of Part 1 (slides 4 to 11) are in the older style, with small fonts and
   titles inside the figure; redraw them at the figure standards with the scripts that made them
   (`scripts/validate_romallosa.py`, `scripts/visual_na_checks.py`, `scripts/verify_*.py`), as new files.
2. **Guides of that deck: done 2026-11-17, midday.** The two guides of `2ce_high_na_pulses.pptx` and the two of
   `pulse_delay.pptx` now have one card per slide, with the slide number (position in the deck), the title and the
   bullets word for word from the decks (checked by script against the text read with python-pptx), Part 4 (slides 46
   to 54) added from the delay guides, and every other sentence rewritten as a full sentence. Steps b46 to b54b of
   `steps_high_na_pulses.json` reuse the screenshots of `img_delay/` (copied). All four are rebuilt
   (`high_na_pulses_guide`, 49 pages; `presenter_guide_high_na_pulses`, 37; `delay_guide`, 13;
   `presenter_guide_delay`, 9). Remains: the user's reading of them. If the wording of a slide changes again, copy
   the new title and bullets into the cards and rebuild; the number printed in the corner of a slide is smaller than
   its position, because it skips the title and the dividers.
3. **Presenter guides: numbers and answers checked 2026-11-17, midday**, against the speaker notes,
   `work_to_date.tex`, `pulse_derivations.tex`, `review_07.tex`, `KEY_RESULTS.md`, `widths.csv`, `tau_cw.txt` and the
   numbers files. Corrected in the guides: the 2CE spot at θ = 0 and π is 0.516 µm (was 0.517, the 2PE value); the
   facing-lens pulse width at NA 0.3 is 264 fs (was 260); at 10 fs the 375-nm pairs are 18% and the 328-nm pairs 14%
   of the 350-nm pairs in amplitude (was "18%" for both); with crossed lenses the focus of L2 moves along, not across,
   the axis of L1 for a misalignment z_c; the scalar Debye spot in optical units is not constant (3.23 at NA 0.3,
   3.19 at NA 0.9); the E_z error was in the two-beam calculation, not in the one-beam focus of Part 1. Remains, in
   the deck notes (not changed, the decks are not mine to edit): slide 14 notes give 0.517 µm for 2CE at θ = 0 and π
   (stored 0.516); slides 2 and 38 notes give "about 60%" at 10 fs next to 1.92 µm, which is 54% of 3.56 µm (60% is
   the value with all pairs, 2.14 µm); slides 2 and 40 notes give "18%" for the 375- and 328-nm pairs together;
   slide 50 notes give 0.95 for the collinear fringe at 5 fs where slide 53 and the derivations give 0.92 (different
   normalization). Answers without a written source are listed in the pass below.
4. **Derivations, piece by piece, in LaTeX** (asked 2026-11-16: "review everything including derivations (have latex
   docs piece by piece)"). Existing: `docs/two_color/two_color_plan.tex` (background from Maxwell's equations, brief),
   `docs/two_color/pulse_derivations.tex` (pulses, delay, the E_z factor; slow steps). Wanted: one document per piece,
   each with slow steps and a check against stored numbers: (1) the scalar focal field (Debye integral, paraxial form,
   sinc² on the axis and Airy in the focal plane, the widths at NA 0.5); (2) the vector field (aplanatic factor,
   I₀, I₁, I₂, the components, E_z = −2 I₁ cos φ, ∇·E = 0); (3) two beams (rotation in real space, 2CE = I₁I₂,
   2PE = |U₁+U₂|⁴, the fringe of 2PE at θ = π and π/2, the crossed-lens limit NA = n sin 45°, displacement,
   aberration, Linfoot's criteria); (4) pulses; (5) delay. Pieces 4 and 5 are the sections of
   `pulse_derivations.tex`. Keep each topic in one place.
5. **Delay slides: done 2026-11-17.** The user asked for the delay results in the same deck, as their own slides.
   They are Part 4 of `2ce_high_na_pulses.pptx` (slides 45 to 54) and also the deck `pulse_delay.pptx`; both take
   them from `scripts/pulse_delay_slides.py`, so edit the wording there and rebuild both decks. They are written
   in the framework of Lim & Saloma (2002): the peak 2CE fluorescence against a misalignment, here in time
   ("a delay of 0.40 τ reduces the peak by 20%"). The user, 2026-11-17: "we write and look for results in the
   same framework as the original papers; this time we just extended it to high NA and optical pulses."
6. **Push**: nothing has been pushed since the annular slides. Push only when the user says so.
7. **Lint**: `ruff check` reports 15 unused imports or variables in older scripts (list: run it on `scripts/`). They
   change no result. `scripts/make_lim2002_progress_deck.py` is frozen: leave its six findings as they are.

## Standing facts for whoever continues

- The deck for the adviser meetings is named by its content, `2ce_high_na_pulses`, never after a person: the
  meetings recur (user, 2026-11-16).
- A recurring job in the user's session re-enters this work every two hours with the prompt "continue anything
  unfinished and review … FLAG if results change …". If a review changes a stored result, say so at the top of the
  report to the user, with the old and the new number.
- The user reads the deck in PowerPoint as soon as it opens, so never open a deck that has not been checked.
- Results stored so far: 16 sets (scalar and vector; air, water, oil; circular pupil, Gaussian input α = 4, annular
  pupils ε = 0.5, 0.9, 0.99), 159 set-and-NA combinations with 15 to 18 pulse widths (4 fs to 1000 or 5000 fs) without
  delay; with delay, 451 416 rows over 11 256 cases (6 pulse widths, 21 delays each, and a 0.1-fs grid at 5, 10 and
  20 fs), plus polarization p at three NAs.

## Passes

### 2026-11-18
- FLAG (wording, not a stored result): two slides of the meeting of 2026-10-29 (annular comparisons of pp. 31 and 32)
  quoted the paraxial values at NA 0.5 and 0.7 (53%, 34%, 85%); the vector values are 52%, 31% and 81%. The new
  high-NA deck gives the vector values and says so in the notes. No stored result changed.
- Corrected on the new slides: the 2PE standing-wave fringes widen with NA (0.37 µm at NA 0.5, 0.44 µm at NA 0.9);
  with crossed lenses the pulsed 2CE depth of focus is within 1% from 20 fs at NA ≥ 0.3 and from 26 to 54 fs at NA
  0.2 to 0.1.
- Dashboard: added highlights pulse-facing-dof-tau, pulse-facing-dof-na and delay-fringes-10fs and pointed the slides
  at them; slides with no matching view (profiles at NA 0.5 and 0.9; pulse width against NA for the pupils) carry no
  link. Checked the new links in a headless browser.
- tests/test_unified_framework.py added (23 tests); full suite 1111 pass.
- Wrote the dashboard guide and the presenter guide of each of the two new decks, one card per slide of the full deck with the title and bullets word for word (checked by script against the decks read with python-pptx after their rebuild of 15:00) and, in the presenter guides, whether the slide is in the concise deck: `2ce_high_na_guide.pdf` (41 pages, 39 steps), `2ce_pulses_guide.pdf` (39 pages, 36 steps), `presenter_guide_2ce_high_na.pdf` (28) and `presenter_guide_2ce_pulses.pdf` (28), with the modes `2ce_high_na` and `2ce_pulses` in `build.py`; added the highlights `cw-2pe-collinear` and `cw-2ce-crossed` for the maps of slides 9 and 7 of the high-NA deck; loaded the 39 dashboard links of the four decks (16 distinct) in headless Chromium, where all open and show their banner, and found that slide 7 of the high-NA deck (`cw-dof-crossed`) draws the maps of θ = 0, slide 27 of the pulses deck (`delay-fringes`) opens 5 fs instead of 10 fs, and the links of pulse slides 11, 13, 14 and 19 open a related measure rather than the plotted one; found that the annular numbers on high-NA slides 24 (53%, 34%) and 25 (85%) are those of the paraxial model (vector 52%, 31% and 81%, `high_na/pupils/widths.csv`) and that slide 19 rounds C = 0.967 to 0.97; updated the Decks and Guides subsections of `NEXT_STEPS.md`.

### 2026-11-17, midday
- Brought the four guides in line with the rewritten decks (items 2 and 3): one card per slide, titles and bullets
  word for word, Part 4 added, numbers checked; rebuilt all four. Answers in the presenter guides without a written
  source, kept: why the zeros fill with pulses (slide 11), why profiles and not widths (slide 22), the Savitzky–Golay
  parameters of the fringe amplitude (delay slide 11, main slide 54), "no comparison with experiment is planned"
  (from START_HERE.md, not from the listed sources). `replication_numbers.txt` and `lim2002_numbers.txt` give
  different fits for θ = π across the axis (−0.588 x_c² + 0.883 against −0.601 x_c² + 0.888); the deck and guides
  use the second.
- Added the delay results to the deck as Part 4 (65 slides now) from one shared module, and rewrote the delay deck
  with it. The delay that reduces the peak by 20% with facing lenses at 100 fs is 0.40 τ at NA 0.9, 0.41 τ at NA 0.5,
  0.44 τ at NA 0.3, 0.58 τ at NA 0.2 and 1.74 τ at NA 0.1.
- Rewrote all titles and bullets of the deck from the approved wording; fixed stray panel labels (a LaTeX string
  passed as labels); titles sized to one line; axis labels of the pulse-width figures written out; verified the
  focal-spot numbers of the NA 0.3 and 0.9 slide (1.1% and 13.7% wider along the polarization). Commits 16e9777, 36ed3a8.
- Renamed the deck, its script and its guides (were named after the adviser).
- Added `scripts/pptx_resave_pdf.py`.
- The user rejected the wording of the deck (item 1). Rewrite in progress.

### 2026-11-16
- Built the deck (55 slides), extended the delay deck (11 slides), added the Highlights tab and the section "Delay
  between the pulses, against NA" to the dashboard, wrote the guides. Split slides with three panels across.

### 2026-11-10 to 2026-11-13
- Review against the four papers (`docs/review/07_two_color_pulses/review_07.pdf`): the longitudinal field of
  `mcdo/twobeam.py` had a factor −2i in place of −2; corrected; one stored case changed (2PE, crossed lenses,
  polarization in the plane of the lens axes; 208 of 5712 widths), shown on no slide.
- Checks added: long-way samples, closed forms, the total with all pairs summed in frequency (`NEXT_STEPS.md`, H1–H6).
