# Start here: two-color excitation (2CE) with focused beams and optical pulses

Written 2026-11-16 for any session, of any model, that picks this work up with no memory of the earlier ones.
Read this file first. Then read, in this order:

1. `docs/progress/work_to_date.pdf` (6 pages): what has been done and the results, by lens angle.
2. `docs/two_color/REVIEW_LOG.md`: what is open right now, in order, and what each review pass found.
   `docs/two_color/NEXT_STEPS.md`: the checks (H1 to H6) with commands and pass numbers, and the build commands.
3. `docs/two_color/pulse_derivations.pdf` and `docs/review/07_two_color_pulses/review_07.pdf` when a physics question
   comes up.
4. The user's rules: `/Users/raaromero/.claude/projects/-Users-raaromero/memory/MEMORY.md` and the files it links,
   above all `deck-rules.md` and `feedback-approved-summary-language.md`.

## 1. Background in one page

**The physics.** Two beams of different wavelength, λ₁ = 750 nm and λ₂ = 656 nm, are focused by two lenses whose
axes make an angle θ (0 collinear, π/2 crossed, π facing). A molecule absorbs one photon from each beam, as if it
had absorbed one photon of λₑ = 350 nm (1/λₑ = 1/λ₁ + 1/λ₂). The fluorescence is F₂c = κ I₁ I₂, so it forms where
the two beams overlap in space and time. Two-photon excitation (2PE) uses one wavelength, 700 nm, and
F₂p = κ′ |U₁ + U₂|⁴, so the two beams interfere.

**The papers the work extends** (PDFs on this machine):
- Romallosa, Bantang & Saloma, Phys. Rev. A 68, 033812 (2003): focus of few-cycle pulses, Richards–Wolf theory.
  `~/Desktop/Romallosa2003_3D-light-distribution-few-cycle.pdf`
- Cambaliza & Saloma, Opt. Commun. 184, 25 (2000): 2CE against 2PE, circular and annular pupils, scattering.
  `~/Projects/Research/refs/optics/papers/Cambaliza2000_two-color-excitation-confocal.pdf`
- Lim & Saloma, Opt. Commun. 207, 121 (2002): the two foci displaced. `~/Downloads/Research/two_color/may-lim-confocality-condition-in-two-color-excitation.pdf`
- Lim & Saloma, Appl. Opt. 42, 3398 (2003): spherical aberration. `~/Downloads/Research/two_color/may-lim-primary-spherical-aberration-in-two-color-two.pdf`

**The people.** The user is Roland Albert A. Romero (PhD student, National Institute of Physics, UP Diliman). The
advisers are Dr. Caesar Saloma and Dr. Johnrob Bantang. Research meetings are on Mondays and Thursdays.

**What the current work adds.** (a) The vector (Richards–Wolf) focus in place of the paraxial scalar one, so NA up
to 0.95 in air, 1.25 in water, 1.45 in oil. (b) Gaussian input and annular pupils. (c) Optical pulses of width τ
(FWHM of the intensity) in place of continuous beams. (d) A delay Δt between the two pulses.

**Terms that are fixed** (never invent another word for these): depth of focus (FWHM along the axis); obstruction
ratio ε (annular pupil); truncation parameter α (Gaussian input); 350-nm pairs (750 + 656 nm), 375-nm pairs
(750 + 750), 328-nm pairs (656 + 656); collinear, crossed, facing lenses; "Current work" for own results.

## 2. Map of the repository

Work in `/Users/raaromero/mcdo_2ce` (git worktree, branch `two-color`; the remote is PUBLIC). `output/` is a link to
`/Users/raaromero/mcdo_dev/output` and is not in git. Python is
`/opt/homebrew/Caskroom/miniforge/base/envs/dev/bin/python` (`$P` below).

| What | Where |
|---|---|
| Field of one or two beams (scalar, vector) | `mcdo/twobeam.py` |
| Pulses: spectrum, pair sums, closed forms | `mcdo/pulsed2ce.py` |
| Deck helpers (slide, bullets, figure, equation) | `mcdo/deckstyle.py` |
| Richards–Wolf decks (stages 1 to 6) | `mcdo/deck.py`; `python -m mcdo.deck`; output `output/deck/` |
| Replications | `scripts/replicate_cambaliza2000.py`, `scripts/fig_lim2002*.py` |
| High NA, pupils, polarization (continuous beams) | `scripts/cambaliza2000_high_na*.py`, `scripts/fig_lim2002_*na*.py` |
| Pulses against NA | `scripts/cambaliza2000_pulses_na_sweep*.py`, `…_na_sweep_plot.py` |
| Pulses with a delay | `scripts/cambaliza2000_pulses_delay.py`, `…_delay_plot.py` |
| Checks of the delay runs | `scripts/cambaliza2000_delay_sample_check.py`, `…_delay_allpairs_check.py` |
| Main 2CE deck (77 slides, FROZEN) | `scripts/make_lim2002_progress_deck.py` → `output/08_two_color/decks/2ce_meeting_cambaliza.pptx` |
| Pulse deck (20 slides, FROZEN) | `scripts/make_pulse_results_deck.py` → `output/08_two_color/cambaliza2000/deck/pulse_results.pptx` |
| Delay deck (the delay alone) | `scripts/make_pulse_delay_deck.py` → `…/deck/pulse_delay.pptx` |
| **The two current decks** (2026-11-18) | `DECK=high_na` or `DECK=pulses python scripts/make_2ce_decks.py` → `output/08_two_color/decks/2ce_high_na.pptx`, `2ce_pulses.pptx`; `MAIN=1` for the concise decks `*_main.pptx` |
| Text of slides already reviewed by the user | `scripts/approved_slides_2ce_meeting.py` (word for word from the meeting of 2026-10-29) |
| Consistency of the whole framework | `tests/test_unified_framework.py` (one engine from Romallosa to 2CE; verified numbers pinned) |
| Dashboard (Vite + TypeScript) | `dashboard/cambaliza/`; data from `scripts/dashboard_cambaliza_*.py`, `scripts/export_pulse_*_dashboard.py` |
| Guides paired with the dashboard | `docs/two_color/walkthrough/` (`build.py`, `steps*.json`, `shoot.mjs`) |
| Data of every 2CE study | `output/08_two_color/` (numbers in the `*.txt` and `*.csv` files beside the figures) |

## 3. Rules (the user has corrected each of these more than once)

**Never do without asking:** install anything; change the two FROZEN decks; deploy the dashboard; push; delete or
reorganize files outside the task.

**Do exactly what was asked.** No extra figures, panels, runs or slides. If something asked for looks physically
wrong, say so first.

**Never remake existing work.** Find the script that made a figure and run it again. Reuse the bullets of the
existing decks where a slide is carried over; they were reviewed line by line.

**Language, everywhere (chat, slides, notes, documents):**
- Full sentences. No "Label: fragment" bullets, no arrows (→), no "·" titles.
- "I", never "we". Summary bullets start with a past-tense verb (Recomputed, Found, Extended).
- Neutral. Never "only", "far", "every", "fails", "main result", "the paper"; no dramatic or story titles.
- Name the condition first, then what happens, then the reason after "so" or "because", against the
  continuous-beam or published result. At most two numbers per sentence. Template:
  `feedback-approved-summary-language.md`.
- Software words stay out of slides: engine, code, run, sweep, test, script.
- Never shorten a sentence to fit a line ("no telegraphed phrases or sentences", user, 2026-11-17). No title or
  heading starts with "The …". A slide carried over from an approved deck keeps that deck's title and bullets word
  for word (`REVIEW_LOG.md`, item 1).
- Never name a file, a deck or a guide after a person.
- Cite as "Cambaliza & Saloma (2000)", never "the paper"; "compared to", never "over".

**Slides** (`deck-rules.md` has all 29 rules; the ones broken most often):
- One or two one-line bullets (≤ about 90 characters at 13 pt) and one figure that fills the slide. Numbers and
  details go in the speaker notes, with equations as LaTeX there.
- At most two panels across. More panels means more slides.
- Titles are plain labels of what is shown ("2CE peak against the delay, θ = π, 100 fs").
- Helvetica Neue; call `mcdo.deckstyle.keynote_fonts()` before saving. The user opens decks in Keynote.
- Paraxial scalar results are drawn for NA ≤ 0.5.
- No renderer is installed (no LibreOffice). Check layout by numbers: figure fill, bullet length, no overlap.

**Figures:** 600 DPI; fonts 32 (title), 28 (axis labels), 24 (ticks); line width ≥ 2; about 11 × 10 in per panel;
legend inside a free region or one row above, never over data.

**Computation:** tables of the fields are allowed for sweeps, and samples are recomputed the long way after every
sweep (NEXT_STEPS.md, H3). A result without its check is not reported as a result.

## 4. How to work so that nothing stalls

1. Before and after changing any field, pulse or signal code, run `$P -m pytest tests/test_unified_framework.py -q`
   (about one minute). It pins the verified numbers from Romallosa et al. (2003) through Cambaliza & Saloma (2000) and
   Lim & Saloma (2002, 2003) to the pulses and the delay; if one moves, find the cause before changing the number.
   Then run H1 (`$P -m pytest tests -q -x`, about 2 min; 1076 pass on 2026-11-13).
2. Long runs go in the background with a log file and a last line that says done; write the queue as a script in
   the output folder so it can be restarted (examples: `output/…/delay_sweep/run_delay_*.sh`).
3. After a run: the sample check, then the plot script, then the deck script. Never edit a `.pptx` by hand.
4. Report outcomes with the numbers. If a check does not pass, say so and stop.
5. Keep three files current when something changes: this file (map and rules), `NEXT_STEPS.md` (state and steps),
   `docs/progress/work_to_date.tex` (results; rebuild with `tectonic work_to_date.tex`).
6. Division of labour the user asked for (2026-11-16): the main session plans and reviews; building and running
   that need no judgement go to subagents, whose output is reviewed before it is shown to the user.

**Known traps**
- `git` stops with "Xcode license" after a macOS update; the user runs `sudo xcodebuild -license accept`.
- `docs/two_color/walkthrough/walkthrough.src.md` and `walkthrough.md` state the dashboard password; the remote is
  public. Do not commit them until the user decides (NEXT_STEPS.md, Step 3).
- `docs/gbp_mc_external_review.md` is never committed (see `HANDOFF.md`).
- In `mcdo/twobeam.py` the longitudinal field is E_z = −2 I₁ cos φ (real factor). A factor −2i is the old error.
- `rel_total` of the delay tables is over the value at no delay; with polarization p and facing lenses that value
  is near a minimum, so use `peak_total` there.
- The Cambaliza & Saloma spot-size ratios at θ = π/2 (0.67, 0.75, 1.58) are not reproduced under any width
  definition, while its plotted widths are. This is known and accepted; do not spend time on it.

## 5. State on 2026-11-16 and the work in progress

Done and checked: the replications; the high-NA extension; pulses against NA; the delay sweep (16 sets) and its
checks; polarization p for crossed lenses; the review against the four papers (one error found and corrected).

Done on 2026-11-16 (asked by the user that day; see NEXT_STEPS.md, "Decks", "Dashboard highlights" and "Guides"):
1. A deck covering the Richards–Wolf work, then 2CE at high NA, then pulses, with at most two panels
   across: `scripts/make_2ce_high_na_pulses_deck.py` → `output/08_two_color/decks/2ce_high_na_pulses.pptx` (55 slides).
2. The delay results as their own deck, with the closed formula and the two polarizations: `pulse_delay.pptx` (11 slides).
3. A presenter guide and a dashboard guide for each of the two decks: `docs/two_color/presenter_guide_{high_na_pulses,delay}.md`
   and `docs/two_color/walkthrough/walkthrough_{high_na_pulses,delay}.src.md`, built beside the decks.
4. A "Highlights" tab in the dashboard (19 cards), and a section "Delay between the pulses, against NA" in Pulse
   results with the delay sweep (`scripts/export_pulse_delay_sweep_dashboard.py`).

Still open: the commit and push of the branch, which waits on three answers from the user (NEXT_STEPS.md, Step 3);
the user's review of the decks and guides.

Candidates after that, for the user to choose: pulsed 2CE through a scattering medium (recommended), unequal pulse
widths, chirped pulses, a broad absorption band. No comparison with experiment or a full-wave solver is planned for
now (user, 2026-11-13).
