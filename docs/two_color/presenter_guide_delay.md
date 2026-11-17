---
title: "Presenter guide for the deck on the delay between the pulses"
subtitle: "Slide numbers are those of pulse_delay.pptx (11 slides); the guide that pairs each slide with the dashboard is delay_guide.pdf."
---

<!-- Build (as presenter_guide.md): pandoc presenter_guide_delay.md -s --embed-resources --css presenter_guide.css
     -o /Users/raaromero/mcdo_dev/output/08_two_color/cambaliza2000/deck/presenter_guide_delay.html, then print it to
     PDF with headless Chromium (--headless=new --no-pdf-header-footer --print-to-pdf=<…>/presenter_guide_delay.pdf).
     Each ::: card is one slide: the slide number in the margin, the slide title word for word, the main point in one
     sentence (say), what to say, then the likely questions with short answers. Numbers come from the speaker notes of
     the deck, docs/progress/work_to_date.tex (Section 7), docs/two_color/pulse_derivations.tex (Sections 6 to 8) and
     docs/review/07_two_color_pulses/review_07.tex. Cards 3 to 11 are also Part 4 of presenter_guide_high_na_pulses.md
     (slides 46 to 54 there). No run-in labels or arrows in this file. -->

::: {.card .story}
::: sl
How
:::

## How to use this guide

- Each card is one slide. The yellow box is the main point of the slide in one sentence, the paragraph under it is what
  to say, and the list at the end gives the questions that are likely and a short answer to each.
- All results are for the vector (Richards–Wolf) model in air, both beams polarized perpendicular to the plane of the
  lens axes, unless a slide says otherwise. The 656-nm pulse is delayed by Δt relative to the 750-nm pulse.
- The results are written as Lim & Saloma (2002) write the misalignment of the two foci: the peak 2CE fluorescence
  against the misalignment, here a misalignment of the two pulses in time.
:::

::: card
::: sl
2
:::

## Summary: delay between the two pulses

::: say
A delay reduces the peak 2CE fluorescence as the temporal overlap of the two pulses, except with facing lenses at low
NA, where the delayed pulses still meet inside the long depth of focus and the peak moves along the axis.
:::

The 656-nm pulse is delayed relative to the 750-nm pulse by up to twice the pulse width, for collinear, crossed and
facing lenses from NA 0.1 to 0.95. With facing lenses and 100-fs pulses the peak at a delay of one pulse width is 0.93
of the peak without delay at NA 0.1, 0.51 at NA 0.2 and 0.25 at NA 0.9.

::: qa
- **Which pairs carry the 2CE signal here?** The 350-nm pairs, one photon from each beam, because Lim & Saloma (2003)
  note that probes are chosen to minimize two-photon excitation by either beam alone. All pairs are shown on the slides
  of the fringes.
- **Were the results checked?** Sixteen samples were recomputed directly from the field integrals, without the tables
  of the fields, and their peaks agree to 1.8e-10. The total with all pairs was recomputed as a sum over pairs of
  frequencies and agrees to 1.1e-4 of the peak.
:::
:::

::: card
::: sl
3
:::

## Delay between the two pulses and their temporal overlap

::: say
At a fixed point the peak 2CE fluorescence of the 350-nm pairs decreases with the delay as the temporal overlap of the
two pulses: a delay of 0.40 τ reduces the peak by 20%, a delay of 0.71 τ by one half and a delay of τ by 75%.
:::

A delay is a misalignment of the two pulses in time, as Lim & Saloma (2002) misalign the two foci in space. Lim & Saloma
(2003) state that spatio-temporal simultaneity of the two confocal beams is a necessary condition for 2CE. For two
Gaussian pulses of width τ the overlap is F(Δt)/F(0) = exp(−2 ln2 Δt²/τ²). With collinear lenses the stored peaks
follow it to 1e-5 at 100 fs, at all NAs.

::: qa
- **Why exp(−2 ln2 Δt²/τ²) and not exp(−4 ln2 Δt²/τ²)?** The signal is the integral of the product of two Gaussian
  pulses of width τ, which is a Gaussian in Δt that is √2 times wider than each pulse.
- **What changes with unequal pulse widths?** The overlap becomes exp[−4 ln2 Δt²/(τ~1~² + τ~2~²)]; this is a candidate
  for later work.
:::
:::

::: card
::: sl
4
:::

## Facing lenses: position where the delayed pulses meet

::: say
With facing lenses the delayed pulses meet at z~m~ = cΔt/2n, and 2CE forms over a stretch of length G = cτ/(√2 n) about
that position.
:::

The peak 2CE fluorescence at a delay is exp[−4 ln2 z~m~²/(D² + G²)], with D the continuous-beam depth of focus. At
100 fs in air G = 21.2 µm, and at a delay of one pulse width the pulses meet at z~m~ = 15.0 µm. The formula gives 0.928
at NA 0.1 against 0.930 computed, 0.518 at NA 0.2 against 0.513 and 0.260 at NA 0.5 against 0.258.

::: qa
- **What are the two limits?** When D is much longer than G, at low NA, the peak moves with z~m~ and is retained; when D
  is much shorter, at high NA, the peak stays at the focus and the formula becomes the temporal overlap.
- **Why does the formula take D from the scalar model?** It is the value of the derivation (3.56 µm at NA 0.5, growing
  as 1/NA²); the computed peaks are those of the vector model, and the two agree to within 0.01.
:::
:::

::: card
::: sl
5
:::

## Peak 2CE fluorescence and its position against the delay, θ = π

::: say
With facing lenses at low NA the delayed pulses still meet inside the long depth of focus, so the peak 2CE fluorescence
moves along the axis and is largely retained; at NA 0.5 and above it stays at the focus and decreases as the temporal
overlap.
:::

With 100-fs pulses and a delay of one pulse width, the peak is 0.93 of its value without delay at NA 0.1, 0.32 at NA 0.3
and 0.25 at NA 0.9, and it has moved by 14.2, 2.6 and 0.02 µm. The delay that reduces the peak by 20% is 0.40 τ at
NA 0.9 and 0.41 τ at NA 0.5, the value of the temporal overlap, and it grows to 0.58 τ at NA 0.2 and 1.74 τ at NA 0.1.

::: qa
- **Why does the peak not follow cΔt/2 exactly at NA 0.2?** The 2CE there is the product of the focus and the stretch
  where the pulses meet, so the peak lies between the focus and the position where the pulses meet.
- **Is the reduction of 74% at NA 0.5 different from the 75% of the temporal overlap?** By 0.01 of the peak; from
  NA 0.5 up the peak is within 0.01 of the temporal overlap.
:::
:::

::: card
::: sl
6
:::

## Peak 2CE fluorescence at a delay of one pulse width against NA

::: say
As NA increases the peak 2CE fluorescence that remains at a delay of one pulse width decreases to one quarter, and
shorter pulses and pupils with a longer depth of focus retain more of it.
:::

At NA 0.5 the peak that remains at a delay of one pulse width is 0.26 at 100 fs, 0.41 at 20 fs and 0.87 at 5 fs,
because the position where the pulses meet moves by a shorter distance. At NA 0.3 and 100 fs it is 0.32 for the
circular pupil, 0.38 for the Gaussian input (α = 4) and 0.80 for the annular pupil with ε = 0.9.

::: qa
- **What is the use of this?** Cambaliza & Saloma (2000) propose annular lenses, with their long depth of field, to keep
  the two beams aligned in space; the same holds here for their alignment in time.
:::
:::

::: card
::: sl
7
:::

## Peak 2CE fluorescence against the delay, τ = 5 fs, NA 0.5

::: say
With all photon pairs and phase-locked pulses the peak 2CE fluorescence oscillates with the delay, because the delay
changes the phase of the 350-nm pairs relative to the 375- and 328-nm pairs; the 350-nm pairs alone decrease smoothly.
:::

The fringes are 2.19 fs apart for the 350-nm pairs with the 375-nm pairs (the period of 656 nm), 2.50 fs for the
350-nm pairs with the 328-nm pairs (the period of 750 nm) and 1.17 fs for the 375-nm pairs with the 328-nm pairs (the
period of 350 nm). The left panel is for collinear lenses and the right panel for crossed lenses.

::: qa
- **Why do the two curves nearly coincide with facing lenses?** Along the axis the peak follows the fringes of the
  350-nm pairs in space as the delay moves them, so the fringes against the delay are shallow; at NA 0.5 the largest
  difference between the two curves is 0.03.
:::
:::

::: card
::: sl
8
:::

## Peak 2CE fluorescence against the delay, τ = 10 fs, NA 0.5

::: say
At 10 fs the peak 2CE fluorescence with all photon pairs still oscillates with the delay, with the same three periods as
at 5 fs.
:::

With collinear lenses the fringe depth is 0.71 at 10 fs, against 0.92 at 5 fs. Two of the three fringes decrease with
the overlap of the pulses as the delay grows, while the fringe of the 375-nm pairs with the 328-nm pairs keeps its
depth, because neither of these pairs needs the two pulses to overlap.

::: qa
- **Would two separate lasers show these fringes?** No. With two lasers that are not phase-locked the fringes average
  out and the 350-nm pairs remain.
:::
:::

::: card
::: sl
9
:::

## Peak 2CE fluorescence against the delay, τ = 20 fs, NA 0.5

::: say
At 20 fs the amplitude of the 375- and 328-nm pairs is below 1% of that of the 350-nm pairs, so the total peak 2CE
fluorescence follows that of the 350-nm pairs and decreases smoothly with the delay.
:::

At 20 fs the fringe depth is at most 0.04 in all cases. Lim & Saloma (2003) state that spectral broadening is negligible
for pulse widths longer than 10 fs; in amplitude the 375-nm pairs are 18% of the 350-nm pairs at 10 fs and below 1% at
20 fs.

::: qa
- **Why does the total follow the 350-nm pairs at 20 fs?** The 375- and 328-nm pairs reach the 350-nm level through
  the edges of the spectra, and at 20 fs the spectra barely reach 700 nm.
:::
:::

::: card
::: sl
10
:::

## Fringe depth of the 2CE peak against NA, τ = 5, 10 and 20 fs

::: say
With crossed and facing lenses the fringes against the delay deepen as NA increases, because the delay moves the
interference fringes in space across a smaller focal spot; with collinear lenses the depth is the same at all NAs.
:::

With collinear lenses the depth is 0.92 at 5 fs and 0.71 at 10 fs at all NAs. With crossed lenses at 5 fs it is 0.20
at NA 0.3 and 0.65 at NA 0.7; with facing lenses at 5 fs it is 0.03 at NA 0.5 and 0.27 at NA 0.95. At 20 fs it is at
most 0.04.

::: qa
- **Why does NA matter?** With crossed and facing lenses the delay moves the interference fringes in space; a focal
  spot at high NA is about one fringe wide, so the peak follows the fringes. With collinear lenses the three kinds of
  pairs have the same carrier in space, so they have no fringes in space.
- **Along which line is the crossed-lens depth taken?** Yes, along the x axis through the focus. Over the whole x–z plane
  it is about two thirds of this (0.28 against 0.42 at NA 0.5 and 5 fs).
:::
:::

::: card
::: sl
11
:::

## Peak 2CE fluorescence against the delay for two polarizations

::: say
With crossed lenses and the polarization in the plane of the two lens axes, the fields of the two beams are
perpendicular at the focus, so the three kinds of photon pairs interfere less and the fringes against the delay are
about a quarter as deep.
:::

At NA 0.5 and 5 fs the amplitude of the oscillating part is about 0.05, against 0.21 with the polarization perpendicular
to that plane. The 350-nm pairs decrease with the delay in the same way for both polarizations, and the 2CE spot is
wider, 0.83 µm against 0.75 µm at NA 0.5.

::: qa
- **Why are the fringes not absent?** The longitudinal field away from the focus mixes the components.
- **Do real molecules respond in the same way to both polarizations?** Not in general: the absorption of two photons
  with perpendicular polarizations differs from that of parallel ones by a factor that depends on the molecule, which
  the model does not include.
- **How is the amplitude measured?** As half the swing of the total after a 5-fs smooth (Savitzky–Golay, 51 points,
  order 3) is subtracted.
:::
:::
