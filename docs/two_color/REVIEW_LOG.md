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
2. **Guides of that deck** repeat its bullets (`docs/two_color/walkthrough/walkthrough_high_na_pulses.src.md`,
   `docs/two_color/presenter_guide_high_na_pulses.md`). After item 1, copy the new titles and bullets into them and
   rebuild (commands in `NEXT_STEPS.md`, "Guides"). The built HTML and PDF files still carry the old title text.
3. **Presenter guides: check each number and each answer** against the stored data and the derivations. They were
   written by a subagent and have not been reviewed line by line.
4. **Derivations, piece by piece, in LaTeX** (asked 2026-11-16: "review everything including derivations (have latex
   docs piece by piece)"). Existing: `docs/two_color/two_color_plan.tex` (background from Maxwell's equations, brief),
   `docs/two_color/pulse_derivations.tex` (pulses, delay, the E_z factor; slow steps). Wanted: one document per piece,
   each with slow steps and a check against stored numbers: (1) the scalar focal field (Debye integral, paraxial form,
   sinc² on the axis and Airy in the focal plane, the widths at NA 0.5); (2) the vector field (aplanatic factor,
   I₀, I₁, I₂, the components, E_z = −2 I₁ cos φ, ∇·E = 0); (3) two beams (rotation in real space, 2CE = I₁I₂,
   2PE = |U₁+U₂|⁴, the fringe of 2PE at θ = π and π/2, the crossed-lens limit NA = n sin 45°, displacement,
   aberration, Linfoot's criteria); (4) pulses; (5) delay. Pieces 4 and 5 are the sections of
   `pulse_derivations.tex`. Keep each topic in one place.
5. **Delay deck** (`pulse_delay.pptx`): the same wording review as item 1. Not needed for the meeting of 2026-11-17.
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

### 2026-11-17, midday
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
