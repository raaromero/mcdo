# Review log and handoff

The running record of what is being reviewed, what was found, and what is left. Update it at the end of every
working pass. Newest pass first. Read `START_HERE.md` before this file.

## Open items (do these, in this order)

1. **Optional, for the user to decide** (found 2026-11-19, no change needed): the slide "Facing lenses: position where the delayed pulses meet"
   (`scripts/pulse_delay_slides.py`) writes z_m = cΔt/2n and G = cτ/(√2 n), for pulses at c/n. Near a focus a pulse
   travels at c/(n⟨cos ϑ⟩) (pulse_derivations.pdf, Section 3), so both are longer by 1/⟨cos ϑ⟩: 0.25% at NA 0.1, 1% at
   NA 0.2, 7% at NA 0.5. The slide uses the formula where the focus is longer than G (NA ≤ 0.3), so its statements
   hold, and its notes cite the numbers of the c/n form, which Section 7, Step 9 still gives (the notes have 0.518
   at NA 0.2 from D rounded to 22.3 µm; unrounded it is 0.517). If the user wants it, one sentence in the notes can
   state the speed. The dashboard draws the same reference line ("meeting point of the pulses, cΔt/2", chart of the
   peak position at θ = π in `main.ts`), and so does `cambaliza2000_pulses_delay_plot.py` (label cΔt/2); the same
   holds for both, and a change there would need a deploy.
2. **Push**: `two-color` was pushed on 2026-11-19 at the user's go-ahead. Push later commits only when the user says so.
3. **Lint**: `ruff check` reports 15 unused imports or variables in older scripts (list: run it on `scripts/`). They
   change no result. `scripts/make_lim2002_progress_deck.py` is frozen: leave its six findings as they are.

## Done, and the rules that keep it so

- **Decks** `2ce_high_na(.pptx|_main.pptx)` and `2ce_pulses(.pptx|_main.pptx)` (2026-11-18), built by
  `scripts/make_2ce_decks.py`; they replace `2ce_high_na_pulses.pptx` and its guides. The user rejected deck language
  three times ("The focus at X", "scientific presentation", "no telegraphed phrases or sentences"). For any change:
  - Never shorten a sentence to fit a line. A bullet may take two lines. One or two bullets per slide.
  - A slide carried over keeps the approved wording word for word: from `scripts/approved_slides_2ce_meeting.py`
    (meeting of 2026-10-29), changed only through `fix=`, which states the change in the notes; pulse slides from
    `pulse_results.pptx` (read with python-pptx; do not import its script).
  - New slides use the vocabulary of the paper they extend (Romallosa et al. (2003): "intensity distribution near
    focus", "spectral bandwidth"; Lim & Saloma: "misalignment", "peak 2CE fluorescence"). No title starts with "The";
    the script sizes each title to one line.
  - After any change: rebuild, run `scripts/pptx_resave_pdf.py` on the deck, then LOOK at the PDF pages
    (`pdftoppm -r 100 -png`) before telling the user anything.
- **Guides** of the two decks (2026-11-18): `2ce_high_na_guide.pdf`, `2ce_pulses_guide.pdf` and the two presenter
  guides. If the wording of a slide changes, copy the new title and bullets into the cards (`steps_2ce_*.json`,
  `presenter_guide_2ce_*.md`) and rebuild (`build.py` modes `2ce_high_na`, `2ce_pulses`).
- **Delay slides** (2026-11-17): written once in `scripts/pulse_delay_slides.py` for the pulse deck and
  `pulse_delay.pptx`, in the framework of Lim & Saloma (2002): the peak 2CE fluorescence against a misalignment in time.
- **Derivations, piece by piece** (asked 2026-11-16, done 2026-11-19): `docs/two_color/derivations/`
  `1_scalar_focal_field.pdf` (Debye integral, the same integral of the intensity in all planes, paraxial field, sinc²
  and Airy, widths, annular pupil, why the paraxial depth of focus is too long), `2_vector_focal_field.pdf` (aplanatic
  factor, the ray field, I₀, I₁, I₂, E_z = −2I₁ cos ψ, the same integral for the vector field,
  Gauss's law, the spot across and along the polarization), `3_two_beams.pdf` (rotation, 2CE and 2PE, facing and
  crossed lenses, displacement, aberration, Linfoot's criteria); pulses and delay in `pulse_derivations.pdf`. Every
  number in a Check of the three parts, and in Sections 3 and 7 of `pulse_derivations`, is printed by
  `scripts/derivation_checks.py`. Each topic is in one place: the E_z factor is in
  Part 2, and Section 9 of `pulse_derivations` points there.

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

### 2026-11-19, deck corrections (approved by the user)
- No stored result changed. The two corrections proposed in the first pass are made, as the user approved them.
- α_t for the truncation parameter of the Gaussian input, wherever the decks used α for it: the glossary (2/2) of
  `2ce_high_na` and `2ce_pulses` (and of their concise decks), the bullet of the pulse slide "Pulse width that matches
  continuous beams: pupils, θ = π", the notes of five slides (one in `2ce_high_na`, three in `2ce_pulses`, one in
  `pulse_delay.pptx`, written once in `pulse_delay_slides.py`), and the legends of the figures on those slides:
  `tau_cw_vs_na_pupils_<2ce|2pe>_<pi|0_pi2>.png` (`PANELS=1 cambaliza2000_pulses_na_sweep_plot.py`) and
  `delay_retained_vs_na.png` (its function `retained_vs_na` in `cambaliza2000_pulses_delay_plot.py`). α keeps its one
  meaning, the half-angle of the cone (glossary 1/2). The redrawn figures differ from the old ones inside the legend
  box alone; the other four figures of the same run are identical to the pixel. The dashboard still writes
  "Gaussian input α = 4" (`main.ts`); changing it needs a deploy.
- "C ≥ 0.96" on "Linfoot’s criteria against NA: 2CE, θ = π/2", through `fix=`; its notes state the change (the lowest
  C is 0.967, air, NA 0.7, across the axis; F ≥ 0.999 and Q ≥ 0.98 hold as written, lowest 0.9990 and 0.9828).
- Rebuilt the five decks (38, 16, 39, 16 and 11 slides, as before), re-saved them through PowerPoint, and looked at the
  twelve changed pages; compared the text, notes and pictures of each slide with the decks before the change: the
  differences are the ones above. Brought the cards of the four guides and of the delay presenter guide in line and
  rebuilt them (same page counts).

### 2026-11-19, fifth pass
- No stored result changed. The output of `derivation_checks.py` is the same line for line, with three lines added to
  check 3e.
- Lim & Saloma (2002), p. 126: for facing lenses and a displacement across the axis they fit a quartic, printed as
  −0.37 x_c⁴ + 0.01 x_c³ − 1.14 x_c² + 0.98 (labelled F2cp(0), though a misalignment needs θ ≠ 0; the next sentence
  calls the same case F2cp(π)). The same least-squares fit of the engine's peak over the range of their Fig. 4
  (|x_c| ≤ 4/3 λ₁, that is ±1 µm, read off the figure) gives 0.360 x_c⁴ − 1.132 x_c² + 0.979, with no odd terms since
  the peak is even in x_c: each coefficient within 0.01 of theirs, with the opposite sign of the quartic term. With
  the printed sign the polynomial is zero at x_c = 0.84 and negative beyond, which a peak intensity cannot be, so the
  sign is a typesetting slip, like the cos φ of Romallosa et al. (2003). Their Fig. 4(a) also agrees with the engine:
  its 80% and 10% contours cross the line z_c = 0 at about 0.4 and 1.2 λ₁, and the engine's peak falls to 0.8 at
  0.398 λ₁ and to 0.1 at 1.22 λ₁. `docs/lim2002/lim2002_equations.tex` and the older replication slides quote the printed form as a
  quotation, and no code evaluates it. Part 3, Section 5 now gives the comparison; rebuilt.
- Found the cause of the two stored quadratic fits of the same case that the pass of 2026-11-17 noted:
  −0.588 x_c² + 0.883 (`replication_numbers.txt`, from `verify_2ce_replication.py`) and −0.601 x_c² + 0.888
  (`lim2002_numbers.txt`, from `fig_lim2002.py`, quoted in the older presenter guide). Both are right for their
  samples, which end at 1.30 and at 1.28 λ₁. Over this range the profile is not quadratic, and the coefficient of a
  quadratic fit changes by about 0.07 for each 0.1 λ₁ of range. The engine's peak, with its maximum refined, gives
  −0.588 x_c² + 0.884 and −0.601 x_c² + 0.888 on the same samples (check 3e).
- Lim & Saloma (2002), 2PE with crossed lenses (between 1 and 0.7 for |x_c| ≤ 1.5 λ, with a period of about λ): the
  stored range 0.72 to 1.00 holds over the whole stored row (±1.43 λ_2p) as well as over |x_c| ≤ 1, with the minima at
  ±0.57 λ_2p. On a grid ten times finer along z than the paper's 100 × 100 points, which the stored maps use, the
  minimum is 0.727 and the value at 0.5 λ_2p is 0.742 (stored 0.732). Nothing to correct.

### 2026-11-19, fourth pass
- FLAG, stored results changed (at the user's request, after the first report of this pass): the widths of the high-NA
  pupil study are now measured at half the maximum of the central lobe, not at half the value at the centre
  (`cambaliza2000_high_na_pupils.py`, re-run with `--rerun`). 220 of the 5712 widths changed, all to smaller values;
  no other row, `dlambda.csv` and all figures but one are identical. 208 are 2PE with crossed lenses in polarization
  p, whose centre is a shallow minimum between two equal maxima 0.11 to 0.22 µm from it (at the focus the two fields
  are orthogonal, x and z, and off the centre the longitudinal field of each beam interferes with the main field of
  the other): with the circular pupil in air 0.781 to 0.764 µm at NA 0.5 and 0.729 to 0.699 µm at NA 0.7, in water
  0.667 to 0.657 µm at NA 0.5 and 0.550 to 0.529 µm at NA 0.9; 0.1% to 4.6% smaller with the circular pupil and up to
  10.5% with the annular one. The other 12 are the annular pupil (ε = 0.99) in polarization p, across the axis at
  θ = 0 and π, at the highest NA of each medium, where the longitudinal field along the polarization peaks off the
  axis above the centre value: 2CE 0.522 to 0.502 µm in air at NA 0.95 and 0.383 to 0.373 µm in water at NA 1.25. The
  figure that changed is `polarization_2ce_annular.png`, at its last point in the panel "FWHM, p / s" (3.05 to 2.93
  in air, 2.95 to 2.88 in water). No slide, guide or dashboard view uses these widths or that figure. The pulse
  study (polarizations s and unpolarized), `cambaliza2000_high_na.py` (s) and the dashboard (y) keep the width at half
  the centre value, which is the maximum in all their cases.
- The output of `derivation_checks.py` without `--widths` is the same line for line.
- Checked all 5712 widths of the high-NA pupil study (`high_na/pupils/widths.csv`) against the fields written out
  again from Parts 1 to 3, with Gauss–Legendre integrals in the angle or the pupil radius in place of the engine's
  Simpson grids and the half-maximum point found as a root (Part 5 of `derivation_checks.py`, option `--widths`,
  output in `derivation_checks_widths.txt`). They agree to 1.3e-5 for 2CE and for 2PE at θ = 0, to 4.5e-5 for the 2PE
  fringe at θ = π, and to 2.3e-4 for 2PE at θ = π/2, where the same fields on the stored grid of 2001 points give the
  stored values to six digits; both find no width for the same 304 rows. These are the numbers after the correction
  above; before it, with the width at half the centre value in both, they were the same with 1.6e-4 at θ = π/2. The rows cover air and water, NA 0.2 to
  1.25, circular and annular (ε = 0.99) pupils, uniform and Gaussian (α_t = 4) input, and the paraxial field and the
  vector field in polarizations s, p and unpolarized, across and along the axis. The check therefore tests the medium,
  the Gaussian apodization, the annular limits, the rotation of beam 2 and the window search together.
- Lim & Saloma (2003): resolved note (v) of `two_color_plan.tex`. For φ₁ = φ₂ = 16 their Fig. 3(a) and (d) place the
  peak at about +0.9 µm, as stored (0.90 µm), and their Fig. 3(b) shows the 2PE spot at θ = π/2 spread toward +z, as
  the stored map `aberration_psf16.png` does. Their text calls both changes "toward L1", while their Fig. 1 draws L1
  on the side of negative z. Their Eq. 1, with the sign convention of Born & Wolf that the engine uses, and their
  figures agree with the engine. Part 3, Section 6 now states the direction (Step 3) and the comparison (Check);
  rebuilt Part 3 and the plan.
- Romallosa et al. (2003), Section II: the band of a 1-fs pulse (4.4 × 10¹⁴ Hz, 483 nm to 1.67 µm) and the coherence
  length 359.7 nm at 1.2 fs follow from Δν τ = 0.44 and ν_c = 3.997 × 10¹⁴ Hz.

### 2026-11-19, third pass
- No stored result changed. The output of `derivation_checks.py` is the same line for line, with two checks added.
- Added a physics check that no earlier pass had: the integral of the intensity over a plane z is the same in all
  planes, since the plane waves of the Debye integral keep their amplitudes and change their phases (Parseval's theorem
  for the Hankel transform). With the aplanatic factor it is 4π²(1 − cos α)/k² for the scalar field (Part 1, Section
  1, Step 6), proportional to the solid angle of the cone; 2 for the paraxial field in the variable v (Section 2,
  Step 6); and 4(1 − cos α)/k² for the mean of |E|² over ψ (Part 2, Section 3, Step 8), where (1 + cos ϑ)² +
  2 sin²ϑ + (1 − cos ϑ)² = 4 shows that E_x, E_y and E_z share the integral of the scalar field. The engine gives
  all three to 2.3e-4 at NA 0.5 and 0.9, in the focal plane and 2 µm from it (checks 1f and 2e; 3e-5 with a grid
  twice as fine). The check tests the aplanatic factor and the weights of I₀, I₁ and I₂ against a law the field must
  obey, apart from the stored widths that the tests pin.
- Lim & Saloma (2002), Sections 3.2 and 4, read again against the stored values: the drops of 11%, 20% and 30%, the
  ranges |z_c| < 1.8 λ₁ and 2.7 λ₁, and the 2PE statements (between 1 and 0.7 with a period of about λ₁; 30% at
  0.5 λ₁) agree with Part 3, Section 5, and `lim2002_numbers.txt` (0.72 to 1.00; 0.732 at 0.5 λ₁). Nothing to
  correct.
- Open item 1 now also names the reference line cΔt/2 of the dashboard and of the stored delay figure.

- No stored result changed. Full suite passes (count in the commit message).
- Physics corrected in `pulse_derivations` (Sections 3, 7 and 8) and in the docstrings of `mcdo/pulsed2ce.py`: a
  pulse does not cross a focus at c/n. The focal phase of a lens of fixed NA (−u/4 in the paraxial field) grows in
  proportion to ω, so near the focus the pulse travels along the axis at v = c/(n⟨cos ϑ⟩), with ⟨cos ϑ⟩ the mean
  cosine of the rays weighted by their amplitudes (1 − NA²/4 paraxial; weight √t (1 + t) in the vector model): 0.25%
  faster than c/n at NA 0.1, 7% at NA 0.5, 33% at NA 0.9. It is the factor k_e of the 2PE standing wave in Part 3.
  The engine always had it, since it adds the frequencies with their focal fields: the centroid in time of the pulse
  at 0.25 µm from the focus is n z ⟨cos ϑ⟩/c to 0.003 at NA 0.9 and to 1e-4 at NA 0.7 and below.
- With this speed, the closed form I₁I₂ exp[−2 ln2 (2z/v − Δt)²/τ²] matches the stored facing-lens profiles of the
  delay sweep to 0.002 of the peak at NA 0.1 to 0.9, 10 to 100 fs, both models; with c/n the differences were 0.004
  (100 fs), 0.019 (20 fs) and 0.039 (10 fs), the numbers the document quoted. The table of Section 7, Step 9 now
  uses the depth of focus of the vector model (the stored values are vector) and ⟨cos ϑ⟩: position 0.34 µm at NA 0.5
  as stored (0.41 before), FWHM 3.29 µm as stored (3.51 before). The old numbers stay in one sentence, because the
  notes of the pulse deck cite them.
- The fringes of Section 8, Step 4 are λ_e/(n⟨cos ϑ⟩) apart near the focus, slightly more than 350 nm, as Part 3
  has for the 2PE standing wave.
- Section 6, Step 5 said the factor ω/ω₀ makes the spectrum wider. It narrows the product of the two spectra (term
  −x²/ω₁ω₂) and adds an imaginary part (term bx), and both make the overlap fall more slowly with the delay. Written
  out, it gives 0.710944, 0.255448 and 0.004252 at 5 fs and Δt = 0.5τ, τ, 2τ; stored 0.710947, 0.255451, 0.004252
  (check 4d), the same in both models, all media and NAs.
- Section 4, Step 2 now states the condition for the equal weight of the three kinds of pairs: the intermediate
  states are far from both carriers (by more than ω₂ − ω₁ = 0.36 rad/fs) as well as outside each bandwidth. It is the
  assumption behind |U₁ + U₂|⁴ in [CS00] Eq. 3. The fringe-depth table of Section 8 matches the stored delay sweep.
- Added Part 4 to `scripts/derivation_checks.py` (pulse arrival, the gate against the stored profiles, the table of
  Step 9, the overlap at 5 fs) and the test `test_pulses_cross_a_high_na_focus_faster_than_c_over_n` (NA 0.9, 10 fs: 0.002 with v, 0.03
  with c/n; stored peak 0.280). The other pulse tests were at NA 0.1, where the two speeds differ by 0.25%.
- `pulse_derivations.tex`: emergencystretch and hidden link boxes, as in the three parts; the two overfull lines it
  had are gone.

### 2026-11-19
- No stored result changed. Full suite 1113 pass.
- Wrote the derivations in three parts with a closed form for each result, checked against the engine and the stored
  numbers (`scripts/derivation_checks.py`). They reproduce: the replication widths at NA 0.5 (2PE 0.5171 / 3.5719 µm,
  2CE 0.5157 / 3.5620 µm; stored 0.517 / 3.572 and 0.516 / 3.562); the vector depth of focus of 2CE from the weight
  √t (1 + t) of the axial integral (3.326 and 0.807 µm at NA 0.5 and 0.9, as stored); the ratio of the paraxial to
  the exact depth of focus, 1 + tan²(α/2) for a uniform weight; the annular spots at ε = 0.99 (0.3648 and 0.3638 µm;
  stored 0.365 and 0.364); the crossed-lens widths (2CE 0.7626 / 0.6703 µm, 2PE 0.2558 µm; stored 0.763 / 0.670 and
  0.256); the 2PE fringes with facing lenses (0.37 µm at NA 0.5, 0.44 µm at NA 0.9).
- Lim & Saloma (2002): the peak 2CE fluorescence against a displacement d falls as exp(−κ_r d²), with κ_r = κ₁κ₂/(κ₁ +
  κ₂) the reduced curvature of the two profiles along the displacement. It gives the stored values within 0.01 at the
  paper's offsets in seven of eight cases (0.084 against 0.061 at 1.33 λ₁ across both axes, where the Airy pattern is
  not Gaussian), and the paper's coefficients 0.027, 0.06 and 0.045 from 0.029, 0.065 and 0.051.
- Lim & Saloma (2003): the focus of an aberrated beam moves by 2Aλ/NA² (A = φ/100), and Maréchal's approximation gives
  the peak: 0.845 and 0.081 at |φ| = 60 for equal and opposite aberrations (engine 0.844 and 0.066; stored 0.84, 0.07),
  and the peak position at φ = 16, 0.89 µm (stored 0.90).
- Romallosa et al. (2003): Eqs. 2 and 3 as printed read I₀ + 2I₂ cos φ and I₂ sin φ, where Richards and Wolf have
  cos 2φ and sin 2φ. Their 472.8 nm is the width with cos 2φ (|I₀ − I₂|²); the printed form gives 482.1 nm. The paper's
  numbers therefore come from the correct field, which the engine uses; the printed equations are a typesetting slip.
- Linfoot's criteria: F = 2Q − C holds on all 216 stored rows (to 0.0013, the rounding of the printed values).
- Found on the glossary slides of both decks that α stands for two quantities, and kept "C ≥ 0.97" against the stored
  0.967; both proposed to the user (open item 1).
- Corrected in Part 3 and in the docstring of `mcdo/twobeam.py`: the rotation of optical coordinates does not reproduce
  the figures of Cambaliza & Saloma (2000). Their Fig. 3b follows the rotation of real space (2CE depth of focus at
  θ = π/2 about 0.67 µm; 0.670 µm with it, 1.313 µm with the optical rotation), as `answers.md` had found. The four
  ratios stated in their text at θ = π/2 (0.67, 0.75, 1.58, about 2) match neither rotation (real space 0.49, 0.68,
  2.98, 2.62; optical 0.26, 0.70, 5.51, 4.91), which confirms that those ratios disagree with their own curves.
- `pulse_derivations.tex`: Section 9 (the E_z factor) now points to Part 2, where the derivation is complete and its
  Gauss's-law step is written out; rebuilt.

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
