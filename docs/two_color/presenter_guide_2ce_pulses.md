---
title: "Presenter guide: two-color excitation with femtosecond pulses at high NA"
subtitle: "Slide numbers are those of 2ce_pulses.pptx (39 slides); the concise deck 2ce_pulses_main.pptx (16 slides) takes its slides from it with the same titles and bullets. The guide that pairs each slide with the dashboard is 2ce_pulses_guide.pdf."
---

<!-- Build (as presenter_guide.md): pandoc presenter_guide_2ce_pulses.md -s --embed-resources --css presenter_guide.css
     -o /Users/raaromero/mcdo_dev/output/08_two_color/decks/presenter_guide_2ce_pulses.html, then print it to PDF with
     headless Chromium: Chromium --headless=new --no-pdf-header-footer
     --print-to-pdf=/Users/raaromero/mcdo_dev/output/08_two_color/decks/presenter_guide_2ce_pulses.pdf
     file:///Users/raaromero/mcdo_dev/output/08_two_color/decks/presenter_guide_2ce_pulses.html. Each ::: card is one
     slide: the slide number in the margin, the slide title word for word, whether the slide is in the concise deck,
     the main point in one sentence (say), what to say, then the likely questions with short answers. Numbers come from
     the speaker notes of the deck, docs/progress/work_to_date.tex, docs/two_color/pulse_derivations.tex,
     docs/review/07_two_color_pulses/review_07.tex and the stored data files beside the figures (checked 2026-11-18).
     The cards of slides 4 to 10, 15 to 20, 22 to 32 and 36 to 39 are those of presenter_guide_high_na_pulses.md
     (slides 30 to 36, 39 to 44, 46 to 56 and 61 to 64), renumbered. No run-in labels or arrows in this file. -->

::: {.card .story}
::: sl
How
:::

## How to use this guide

- Each card is one slide of 2ce_pulses.pptx. Its number is the number of the slide in that deck, which is also printed in
  the corner of the slide.
- The line under the title says whether the slide is also in the concise deck 2ce_pulses_main.pptx, and at which
  number.
- The yellow box is the main point of the slide in one sentence, the paragraph under it is what to say, and the list
  at the end gives the questions that are likely and a short answer to each.
- The numbers that are not on the slide are in its speaker notes, with the equations in LaTeX.
- The title slide, the dividers and the glossary have no card.
:::

::: card
::: sl
2
:::

## Summary

*This slide is slide 2 of the concise deck.*

::: say
With pulses, the lens angle and the NA decide how much of the continuous-beam 2CE is kept: collinear and crossed lenses keep the continuous-beam focus, and facing lenses shorten it, more so at lower NA.
:::

Read the five bullets in order: the extension to pulses, the three lens angles, the pairs from one beam below 15 fs and the delay between the pulses. With facing lenses at NA 0.5 the pulsed 2CE depth of focus is about 80% of the continuous-beam value at 20 fs. The pulse width that matches continuous beams grows from 25 fs at NA 0.9 to 610 fs at NA 0.2.

::: qa
- **Which model is used?** The vector (Richards–Wolf) model in air with the circular pupil, both beams polarized perpendicular to the plane of the lens axes, unless a slide says otherwise. The slides of 100-fs pulses use the paraxial model at NA 0.5, the setting of Cambaliza & Saloma (2000).
- **What kind of pulses are assumed?** Transform-limited Gaussian pulses, phase-locked to each other, and a 350-nm level that is narrow compared to their spectra; chirped pulses and a broad absorption band are among the next steps.
:::
:::

::: {.part}
# 1. Optical pulses: 2PE and 2CE point spread functions with transform-limited femtosecond pulses, from NA 0.1 to 0.95 (slides 4 to 20)
:::

::: card
::: sl
4
:::

## An optical pulse in time

*This slide is not in the concise deck.*

::: say
A short pulse has a Gaussian spectrum about its carrier frequency, and each frequency of the spectrum is a continuous wave.
:::

The left panel is the Gaussian spectrum of a 10-fs pulse at 750 nm, with nine frequencies marked. The right panel shows the waves at those frequencies, each with its weight; they are in phase at t = 0 and out of phase at 15 fs.

::: qa
- **Is the pulse chirped?** No. The pulses are transform-limited Gaussians, so all frequencies are in phase at t = 0.
:::
:::

::: card
::: sl
5
:::

## Sum of the frequencies of a 10-fs optical pulse

*This slide is not in the concise deck.*

::: say
At t = 0 the frequencies are in phase and add up, and away from t = 0 they drift out of phase, so their sum is a pulse of width τ.
:::

The figure shows the field E(t) and its envelope, summed over the whole spectrum of the 10-fs pulse at 750 nm. At 15 fs the waves are out of phase and the envelope has fallen to a few percent of its peak.

::: qa
- **What is τ?** The pulse width, the full width at half maximum of the intensity |E(t)|².
:::
:::

::: card
::: sl
6
:::

## Pulse width and spectral bandwidth

*This slide is not in the concise deck.*

::: say
A transform-limited Gaussian pulse has a spectral bandwidth Δν = 0.441/τ, so a shorter pulse has a wider spectrum.
:::

The spectral bandwidth is 88 THz at 5 fs, 44 THz at 10 fs, 22 THz at 20 fs and 4.4 THz at 100 fs. The dotted line in the right panel is 428 THz, which is 700 nm.

::: qa
- **Where does 0.441 come from?** For a Gaussian pulse the product of the two FWHMs is Δν τ = 4 ln 2/2π = 0.441.
:::
:::

::: card
::: sl
7
:::

## Pulse spectra against wavelength, τ = 5, 10, 20 and 100 fs

*This slide is not in the concise deck.*

::: say
Below about 15 fs the spectra reach 700 nm, where two photons of one pulse add up to 350 nm.
:::

Against wavelength both colors lie at the red edge of the visible range, 380 to 750 nm. At 10 fs each spectrum has 31% of its peak at 700 nm; at 20 fs and longer it has almost none.

::: qa
- **Why does 700 nm matter?** Two photons of 700 nm add up to 350 nm, so a pulse whose spectrum reaches 700 nm can excite the 350-nm level by itself.
:::
:::

::: card
::: sl
8
:::

## Photon pairs that excite the 350-nm level

*This slide is slide 3 of the concise deck.*

::: say
The excitation adds the amplitudes of all photon pairs that sum to the 350-nm level and then squares the total, so the 375- and 328-nm pairs enter beside the 350-nm pairs.
:::

The amplitude is A = A^11^ + 2A^12^ + A^22^ with A^ab^ = ∫E~a~E~b~e^iω~e~t^dt, and F = |A|². The term 2A^12^ takes one photon from each beam, the 350-nm pairs; A^11^ and A^22^ take both photons from one beam, the 375- and 328-nm pairs. For long pulses F becomes I~1~I~2~, the result of Cambaliza & Saloma (2000).

::: qa
- **Why not add the intensities of the frequencies, as Romallosa et al. (2003) do?** Their sum is the intensity integrated over time; for a two-photon signal ∫I²dt is not (∫I dt)², and 2CE depends on when the two pulses arrive.
- **Which polarization is used?** Both beams are polarized perpendicular to the plane of the lens axes, in the vector model in air with the circular pupil, unless a slide says otherwise.
:::
:::

::: card
::: sl
9
:::

## 2CE with 100-fs pulses and with continuous beams, θ = 0 and π

*This slide is slide 4 of the concise deck.*

::: say
At 100 fs pulsed 2CE is the same as with continuous beams, so the continuous-beam results of Cambaliza & Saloma (2000) hold for pulses of that length.
:::

In the paraxial model at NA 0.5 the depth of focus is 3.56 µm with collinear lenses. With facing lenses it is 3.52 µm against 3.56 µm, because the pulses overlap over 21 µm, six times the focus.

::: qa
- **Is 100 fs long enough at all NAs?** With facing lenses it is not at low NA: the pulse width needed to match continuous beams is 87 fs at NA 0.5 and 264 fs at NA 0.3 (slide 17).
:::
:::

::: card
::: sl
10
:::

## 2CE with 100-fs pulses and with continuous beams, θ = π/2

*This slide is not in the concise deck.*

::: say
With crossed lenses the pulsed 2CE across the axis at 100 fs is also the same as with continuous beams.
:::

With crossed lenses the width across the axis is 0.76 µm with pulses and with continuous beams, and the widths at the three lens angles agree to within 1%.

::: qa
- **Does this hold in the vector model too?** Yes. The stored 100-fs profiles at NA 0.5 match the continuous-beam ones at the three angles (review_07, Section 2.4).
:::
:::

::: card
::: sl
11
:::

## 2CE depth of focus against pulse width, facing lenses

*This slide is slide 5 of the concise deck.*

::: say
With facing lenses the pulsed 2CE depth of focus falls below the continuous-beam value as the pulses get shorter, and more at lower NA, because 2CE forms where the two pulses meet.
:::

Each curve is one NA, from 0.1 to 0.95, in the vector model in air, and the depth of focus is taken through the fringe crests with all photon pairs. At 20 fs the ratio is 0.19 at NA 0.2 and 0.81 at NA 0.5. At NA 0.9 it is 0.99 at 20 fs and 0.97 at 10 fs, and at NA 0.2 it is 0.70 at 100 fs.

::: qa
- **Why does a lower NA shorten more?** The continuous-beam focus grows as 1/NA² while the stretch where the pulses meet, cτ/√2, stays the same, so the overlap cuts a larger part of the focus.
- **Why through the fringe crests?** Below about 15 fs the 375- and 328-nm pairs add fringes 350 nm apart along the axis; the width through their crests measures the length of the 2CE and not that of the central fringe.
:::
:::

::: card
::: sl
12
:::

## 2CE depth of focus against pulse width, collinear and crossed lenses

*This slide is slide 6 of the concise deck.*

::: say
With collinear and crossed lenses pulsed 2CE keeps the continuous-beam depth of focus to within a few percent, because the pulses overlap over the whole focus.
:::

With collinear lenses the ratio stays within 0.5% of 1 down to 4 fs at all NAs, because the two pulses travel together. With crossed lenses it is within 1% from 20 fs at NA 0.3 and above. Below 15 fs it grows by up to 7% at high NA (1.07 at NA 0.7 and 5 fs), because the 375-nm pairs of L1 alone extend along its axis, and at NA 0.2 and 4 fs it is 0.88.

::: qa
- **What happens with crossed lenses at NA 0.2 and below?** The depth of focus needs longer pulses to come within 1% of the continuous-beam value: 26 fs at NA 0.2, 36 fs at NA 0.15 and 54 fs at NA 0.1.
:::
:::

::: card
::: sl
13
:::

## 2CE depth of focus against NA, facing lenses

*This slide is not in the concise deck.*

::: say
As NA increases the 2CE depth of focus with pulses returns to the continuous-beam value with facing lenses at each pulse width, because the focus becomes shorter than the stretch where the pulses overlap.
:::

Each curve is one pulse width, from 4 to 1000 fs, in the vector model in air. The stretch where the pulses overlap has FWHM cτ/√2, 4.2 µm at 20 fs, which is longer than the focus from about NA 0.5. At 20 fs the ratio rises from 0.41 at NA 0.3 to 0.99 at NA 0.9.

::: qa
- **Is this the same result as slide 11?** Yes, the same depths of focus drawn against NA, one curve per pulse width; slide 17 gives the pulse width at which the profiles match continuous beams to 1%.
:::
:::

::: card
::: sl
14
:::

## 2CE along the axis with pulses at NA 0.5 and NA 0.9, facing lenses

*This slide is slide 7 of the concise deck.*

::: say
At NA 0.9 the focus is shorter than the stretch where the pulses meet, so 100- and 20-fs pulses give nearly the continuous-beam 2CE profile along the axis, while at NA 0.5 20-fs pulses shorten it.
:::

The profiles are those of all photon pairs in the vector model in air. At NA 0.5 the depth of focus through the fringe crests is 3.33 µm for continuous beams and 2.70 µm at 20 fs, and at NA 0.9 it is 0.81 µm and 0.80 µm. At 10 fs the 375- and 328-nm pairs add fringes 350 nm apart at both NAs.

::: qa
- **Where do the fringes at 10 fs come from?** From the 375- and 328-nm pairs, whose amplitude interferes with that of the 350-nm pairs along the axis; at 20 fs their amplitude is below 1% of that of the 350-nm pairs (slide 16).
:::
:::

::: card
::: sl
15
:::

## Overlap in time of the two facing pulses

*This slide is not in the concise deck.*

::: say
The facing pulses overlap in time over a stretch of cτ/√2 about the focus, 4.2 µm at 20 fs, and the pulsed 2CE is the continuous-beam profile times this overlap.
:::

The stretch has FWHM G = cτ/(√2 n), 4.2 µm at 20 fs and 21 µm at 100 fs. With D the continuous-beam depth of focus the pulsed one is DG/√(D² + G²). At 20 fs this product gives 2.74 µm, and the full calculation gives 2.78 µm with all pairs and 2.81 µm with the 350-nm pairs.

::: qa
- **Why is the computed depth of focus at 10 fs longer than the product?** The 375- and 328-nm pairs need no overlap of the two pulses, so the computed 2CE is 2.14 µm long against 1.83 µm from the product.
:::
:::

::: card
::: sl
16
:::

## Signal added by the 375- and 328-nm pairs

*This slide is slide 8 of the concise deck.*

::: say
Below about 15 fs two photons of one pulse also excite the 350-nm level, so one beam alone excites and 2CE starts to lose the weak background of continuous beams.
:::

With continuous beams 2CE needs both beams, which gives its weak background in scattering media. At 10 fs the amplitude of the 375-nm pairs is 18% and that of the 328-nm pairs 14% of the amplitude of the 350-nm pairs; at 20 fs both are below 1%. The peak of the total over that of the 350-nm pairs is 1.02 at 20 fs, 1.15 at 15 fs, 1.73 at 10 fs and 3.1 at 5 fs.

::: qa
- **Do real probes absorb these pairs?** Lim & Saloma (2003) note that probes are chosen to minimize two-photon excitation by λ~1~ or λ~2~ alone; the model keeps all pairs, so it gives the case with no such selection.
:::
:::

::: card
::: sl
17
:::

## Pulse width that matches continuous beams against NA, θ = π

*This slide is slide 9 of the concise deck.*

::: say
With facing lenses the pulse width needed to match continuous beams grows as NA decreases, because a lower NA gives a longer focus for the pulses to overlap over.
:::

With facing lenses in air the pulse width is about 25 fs at NA 0.9, 87 fs at NA 0.5, 264 fs at NA 0.3 and 610 fs at NA 0.2. At NA 0.5 it is 87 fs in air, 164 fs in water and 216 fs in oil. For 2PE it is shorter, 62 fs at NA 0.5, because the 350-nm pairs within one pulse need no overlap.

::: qa
- **What is the tolerance?** The largest difference between the pulsed and continuous-beam profiles, each scaled to its peak, stays below 1% of the peak.
- **Why do water and oil need longer pulses at the same NA?** The focus depends on NA/n, so at the same NA it is longer in a medium of higher refractive index.
:::
:::

::: card
::: sl
18
:::

## Pulse width that matches continuous beams, θ = 0 and π/2

*This slide is not in the concise deck.*

::: say
With collinear lenses pulsed 2CE matches continuous beams down to 4 fs, and with crossed lenses it matches once the pulses are longer than about 28 fs at NA 0.2 and 21 fs at NA 0.7.
:::

The measure is the same as on the previous slide. With collinear lenses the two pulses travel together and overlap over the whole focus, so the shortest pulse computed, 4 fs, already matches. With crossed lenses at NA 0.1 the pulse width needed is 54 fs.

::: qa
- **How is the match measured?** As on slide 17: the largest difference between the pulsed and continuous-beam profiles, each scaled to its peak, stays below 1% of the peak.
:::
:::

::: card
::: sl
19
:::

## Pulse width that matches continuous beams: pupils, θ = π

*This slide is not in the concise deck.*

::: say
With facing lenses a pupil or an input that gives a longer depth of focus needs a longer pulse to match continuous beams.
:::

The figure gives the pulse width from which the 2CE depth of focus stays within 1% of its continuous-beam value: at NA 0.5, 100 fs for the circular pupil, 162 fs for the Gaussian input (α = 4) and 466 fs for the annular pupil with ε = 0.9. By the largest difference between the profiles, the measure of the slides before, the same three are 87, 139 and 405 fs.

::: qa
- **Why two sets of numbers?** This slide uses the depth of focus and the slides before use the largest difference between the profiles; both give the same order of the pupils.
:::
:::

::: card
::: sl
20
:::

## Pulse width that matches continuous beams: pupils, θ = 0, π/2

*This slide is not in the concise deck.*

::: say
With collinear lenses the 2CE depth of focus matches continuous beams at all pulse widths computed, and with crossed lenses it matches from about 11 to 16 fs at NA 0.4 and above, for all pupils and inputs.
:::

With crossed lenses the pulse width is 13 to 15 fs for the circular pupil from NA 0.4 to 0.7, 14 to 16 fs for the annular pupils and 11 to 14 fs for the Gaussian input (α = 4). Below NA 0.4 it rises, to 82 fs for the Gaussian input and 54 fs for the circular pupil at NA 0.1.

::: qa
- **Does the pupil matter with crossed lenses?** Little: from NA 0.4 up the pulse width needed lies between 11 and 16 fs for all pupils and inputs.
:::
:::

::: {.part}
# 2. Delay between the two pulses: peak 2CE fluorescence against a misalignment of the two pulses in time, at θ = 0, π/2 and π (slides 22 to 30)
:::

::: card
::: sl
22
:::

## Delay between the two pulses and their temporal overlap

*This slide is slide 10 of the concise deck.*

::: say
At a fixed point the peak 2CE fluorescence of the 350-nm pairs decreases with the delay as the temporal overlap of the two pulses: a delay of 0.40 τ reduces the peak by 20%, and a delay of τ by 75%.
:::

A delay is a misalignment of the two pulses in time, as Lim & Saloma (2002) misalign the two foci in space. Lim & Saloma (2003) state that spatio-temporal simultaneity of the two confocal beams is a necessary condition for 2CE. For two Gaussian pulses of width τ the overlap is F(Δt)/F(0) = exp(−2 ln2 Δt²/τ²); with collinear lenses the stored peaks follow it to 10⁻⁵ at 100 fs, at all NAs.

::: qa
- **Why exp(−2 ln2 Δt²/τ²) and not exp(−4 ln2 Δt²/τ²)?** The signal is the integral of the product of two Gaussian pulses of width τ, which is a Gaussian in Δt that is √2 times wider than each pulse.
- **What changes with unequal pulse widths?** The overlap becomes exp[−4 ln2 Δt²/(τ~1~² + τ~2~²)]; this is a candidate for later work.
:::
:::

::: card
::: sl
23
:::

## Facing lenses: position where the delayed pulses meet

*This slide is not in the concise deck.*

::: say
With facing lenses the delayed pulses meet at z~m~ = cΔt/2n, and 2CE forms over a stretch of length G = cτ/(√2 n) about that position.
:::

The peak 2CE fluorescence at a delay is exp[−4 ln2 z~m~²/(D² + G²)], with D the continuous-beam depth of focus. At 100 fs in air G = 21.2 µm, and at a delay of one pulse width the pulses meet at z~m~ = 15.0 µm. The formula gives 0.928 at NA 0.1 against 0.930 computed, 0.518 at NA 0.2 against 0.513 and 0.260 at NA 0.5 against 0.258.

::: qa
- **What are the two limits?** When D is much longer than G, at low NA, the peak moves with z~m~ and is retained; when D is much shorter, at high NA, the peak stays at the focus and the formula becomes the temporal overlap.
- **Why does the formula take D from the scalar model?** It is the value of the derivation (3.56 µm at NA 0.5, growing as 1/NA²); the computed peaks are those of the vector model, and the two agree to within 0.01.
:::
:::

::: card
::: sl
24
:::

## Peak 2CE fluorescence and its position against the delay, θ = π

*This slide is slide 11 of the concise deck.*

::: say
With facing lenses at low NA the delayed pulses still meet inside the long depth of focus, so the peak 2CE fluorescence moves along the axis and is largely retained; at NA 0.5 and above it stays at the focus and decreases as the temporal overlap.
:::

With 100-fs pulses and a delay of one pulse width, the peak is 0.93 of its value without delay at NA 0.1, 0.32 at NA 0.3 and 0.25 at NA 0.9, and it has moved by 14.2, 2.6 and 0.02 µm. The delay that reduces the peak by 20% is 0.40 τ at NA 0.9 and 0.41 τ at NA 0.5, the value of the temporal overlap, and it grows to 0.58 τ at NA 0.2 and 1.74 τ at NA 0.1.

::: qa
- **Why does the peak not follow cΔt/2 exactly at NA 0.2?** The 2CE there is the product of the focus and the stretch where the pulses meet, so the peak lies between the focus and the position where the pulses meet.
- **Is the reduction of 74% at NA 0.5 different from the 75% of the temporal overlap?** By 0.01 of the peak; from NA 0.5 up the peak is within 0.01 of the temporal overlap.
:::
:::

::: card
::: sl
25
:::

## Peak 2CE fluorescence at a delay of one pulse width against NA

*This slide is slide 12 of the concise deck.*

::: say
As NA increases the peak 2CE fluorescence that remains at a delay of one pulse width decreases to one quarter, and shorter pulses and pupils with a longer depth of focus retain more of it.
:::

At NA 0.5 the peak that remains at a delay of one pulse width is 0.26 at 100 fs, 0.41 at 20 fs and 0.87 at 5 fs, because the position where the pulses meet moves by a shorter distance. At NA 0.3 and 100 fs it is 0.32 for the circular pupil, 0.38 for the Gaussian input (α = 4) and 0.80 for the annular pupil with ε = 0.9.

::: qa
- **What is the use of this?** Cambaliza & Saloma (2000) propose annular lenses, with their long depth of field, to keep the two beams aligned in space; the same holds here for their alignment in time.
:::
:::

::: card
::: sl
26
:::

## Peak 2CE fluorescence against the delay, τ = 5 fs, NA 0.5

*This slide is not in the concise deck.*

::: say
With all photon pairs and phase-locked pulses the peak 2CE fluorescence oscillates with the delay, while the peak of the 350-nm pairs alone decreases smoothly as the temporal overlap.
:::

The fringes are 2.19 fs apart for the 350-nm pairs with the 375-nm pairs (the period of 656 nm), 2.50 fs for the 350-nm pairs with the 328-nm pairs (the period of 750 nm) and 1.17 fs for the 375-nm pairs with the 328-nm pairs (the period of 350 nm). The left panel is for collinear lenses and the right panel for crossed lenses.

::: qa
- **Why do the two curves nearly coincide with facing lenses?** Along the axis the peak follows the fringes of the 350-nm pairs in space as the delay moves them, so the fringes against the delay are shallow; at NA 0.5 the largest difference between the two curves is 0.03.
:::
:::

::: card
::: sl
27
:::

## Peak 2CE fluorescence against the delay, τ = 10 fs, NA 0.5

*This slide is not in the concise deck.*

::: say
At 10 fs the peak 2CE fluorescence with all photon pairs still oscillates with the delay, with the same three periods as at 5 fs.
:::

With collinear lenses the fringe depth is 0.71 at 10 fs, against 0.92 at 5 fs. Two of the three fringes decrease with the overlap of the pulses as the delay grows, while the fringe of the 375-nm pairs with the 328-nm pairs keeps its depth, because neither of these pairs needs the two pulses to overlap.

::: qa
- **Would two separate lasers show these fringes?** No. With two lasers that are not phase-locked the fringes average out and the 350-nm pairs remain.
:::
:::

::: card
::: sl
28
:::

## Peak 2CE fluorescence against the delay, τ = 20 fs, NA 0.5

*This slide is not in the concise deck.*

::: say
At 20 fs the amplitude of the 375- and 328-nm pairs is below 1% of that of the 350-nm pairs, so the total peak 2CE fluorescence follows that of the 350-nm pairs and decreases smoothly with the delay.
:::

At 20 fs the fringe depth is at most 0.04 in all cases. Lim & Saloma (2003) state that spectral broadening is negligible for pulse widths longer than 10 fs; in amplitude the 375-nm pairs are 18% of the 350-nm pairs at 10 fs and below 1% at 20 fs.

::: qa
- **Why does the total follow the 350-nm pairs at 20 fs?** The 375- and 328-nm pairs reach the 350-nm level through the edges of the spectra, and at 20 fs the spectra barely reach 700 nm.
:::
:::

::: card
::: sl
29
:::

## Fringe depth of the 2CE peak against NA, τ = 5, 10 and 20 fs

*This slide is not in the concise deck.*

::: say
With crossed and facing lenses the fringes against the delay deepen as NA increases, because the delay moves the interference fringes in space across a smaller focal spot; with collinear lenses the depth is the same at all NAs.
:::

With collinear lenses the depth is 0.92 at 5 fs and 0.71 at 10 fs at all NAs. With crossed lenses at 5 fs it is 0.20 at NA 0.3 and 0.65 at NA 0.7; with facing lenses at 5 fs it is 0.03 at NA 0.5 and 0.27 at NA 0.95. At 20 fs it is at most 0.04.

::: qa
- **Why does NA matter?** With crossed and facing lenses the delay moves the interference fringes in space; a focal spot at high NA is about one fringe wide, so the peak follows the fringes. With collinear lenses the three kinds of pairs have the same carrier in space, so they have no fringes in space.
- **Along which line is the crossed-lens depth taken?** Along the x axis through the focus. Over the whole x–z plane it is about two thirds of this (0.28 against 0.42 at NA 0.5 and 5 fs).
:::
:::

::: card
::: sl
30
:::

## Peak 2CE fluorescence against the delay for two polarizations

*This slide is not in the concise deck.*

::: say
With crossed lenses and the polarization in the plane of the two lens axes, the fields of the two beams are perpendicular at the focus, so the fringes against the delay are about a quarter as deep.
:::

At NA 0.5 and 5 fs the amplitude of the oscillating part is about 0.05, against 0.21 with the polarization perpendicular to that plane. The 350-nm pairs decrease with the delay in the same way for both polarizations, and the 2CE spot is wider, 0.83 µm against 0.75 µm at NA 0.5.

::: qa
- **Why are the fringes not absent?** The longitudinal field away from the focus mixes the components.
- **Do real molecules respond in the same way to both polarizations?** Not in general: the absorption of two photons with perpendicular polarizations differs from that of parallel ones by a factor that depends on the molecule, which the model does not include.
- **How is the amplitude measured?** As half the swing of the total after a 5-fs smooth (Savitzky–Golay, 51 points, order 3) is subtracted.
:::
:::

::: {.part}
# Summary and next steps (slides 31 and 32)
:::

::: card
::: sl
31
:::

## Summary: 2CE with optical pulses

*This slide is slide 13 of the concise deck.*

::: say
The lens angle decides what a pulse and a delay change: collinear and crossed lenses keep the continuous-beam focus, facing lenses shorten it, and a delay reduces the peak as the temporal overlap except with facing lenses at low NA.
:::

Read the six bullets in order, with collinear θ = 0, crossed θ = π/2 and facing θ = π. The results assume phase-locked, transform-limited pulses and a 350-nm level that is narrow compared to the pulse spectra.

::: qa
- **Has any of this been compared with experiment?** No. No comparison with an experiment or a full-wave calculation is planned for now.
:::
:::

::: card
::: sl
32
:::

## Next steps

*This slide is slide 14 of the concise deck.*

::: say
Pulsed 2CE through a highly scattering medium is the first candidate, because Cambaliza & Saloma (2000) found the advantage of 2CE compared to 2PE there.
:::

The scattering medium combines the Monte Carlo model of the focus with the pulse model, and it would show whether 2CE with pulses keeps its weak background. With unequal pulse widths the overlap becomes exp[−4 ln2 Δt²/(τ~1~² + τ~2~²)], and for a broad absorption band the signal of the 350-nm pairs is the integral of I~1~I~2~ over time.

::: qa
- **Why a scattering medium first?** Below about 15 fs one beam alone also excites the 350-nm level, so a scattering medium would show how much of the weak background of 2CE remains with pulses.
:::
:::

::: {.part}
# Backup (slides 36 to 39)
:::

::: card
::: sl
36
:::

## Pulse width that matches continuous beams: 2PE, θ = π

*This slide is not in the concise deck.*

::: say
With facing lenses pulsed 2PE matches continuous beams at a shorter pulse width than 2CE, 62 fs against 87 fs at NA 0.5 in air, because pairs of photons from one pulse need no overlap.
:::

The measure is the largest difference between the pulsed and continuous-beam 2PE profiles, below 1% of the peak. The scalar curves are drawn up to NA 0.5.

::: qa
- **Why does 2PE need shorter pulses than 2CE?** Its photon pairs from one pulse need no overlap of the two pulses, while with facing lenses the overlap is what shortens 2CE.
:::
:::

::: card
::: sl
37
:::

## Pulse width that matches continuous beams: 2PE, θ = 0, π/2

*This slide is not in the concise deck.*

::: say
With collinear lenses pulsed 2PE matches continuous beams down to 4 fs, and with crossed lenses once the pulses are longer than 37 fs at NA 0.1 and 6 fs at NA 0.5.
:::

With crossed lenses in air the pulse width is 37 fs at NA 0.1, 5.7 fs at NA 0.5 and 4 fs, the shortest computed, from NA 0.6.

::: qa
- **Does 2PE with collinear lenses change with the pulse width?** No: it matches continuous beams down to 4 fs, the shortest pulse computed, because the two pulses travel together.
:::
:::

::: card
::: sl
38
:::

## Pulse width that matches continuous beams: 2PE, pupils, θ = π

*This slide is not in the concise deck.*

::: say
With facing lenses a pupil or an input that gives a longer depth of focus also needs a longer pulse for 2PE to match continuous beams.
:::

By the depth of focus within 1% of its continuous-beam value, the pulse width at NA 0.5 is 72 fs for the circular pupil.

::: qa
- **How much longer a pulse does the annular pupil need for 2PE?** At NA 0.5 with facing lenses, 334 fs for the annular pupil with ε = 0.9 against 72 fs for the circular pupil, by the depth of focus within 1%.
:::
:::

::: card
::: sl
39
:::

## Pulse width that matches continuous beams: 2PE, pupils, θ = 0, π/2

*This slide is not in the concise deck.*

::: say
With collinear lenses the 2PE depth of focus matches continuous beams at all pulse widths computed, and with crossed lenses the pulse width needed is largest at low NA and falls below 10 fs at NA 0.7.
:::

With crossed lenses the pulse width at NA 0.1 is 68 fs for the Gaussian input and 44 fs for the circular pupil.

::: qa
- **Which input needs the longest pulse with crossed lenses?** The Gaussian input at low NA: 68 fs at NA 0.1, against 44 fs for the circular pupil.
:::
:::
