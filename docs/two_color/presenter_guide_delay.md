---
title: "Presenter guide for the deck on the delay between the pulses"
subtitle: "Slide numbers are those of pulse_delay.pptx; the guide that pairs each slide with the dashboard is delay_guide.pdf."
---

<!-- Build (as presenter_guide.md): pandoc presenter_guide_delay.md -s --embed-resources --css presenter_guide.css
     -o /Users/raaromero/mcdo_dev/output/08_two_color/cambaliza2000/deck/presenter_guide_delay.html, then print it to
     PDF with headless Chromium (--headless=new --no-pdf-header-footer --print-to-pdf=<…>/presenter_guide_delay.pdf).
     Each ::: card is one slide: the slide number in the margin, the main point in one sentence (say), what to say, then
     the likely questions with short answers. Numbers come from the speaker notes of the deck,
     docs/progress/work_to_date.tex (Section 7), docs/two_color/pulse_derivations.tex (Sections 6 to 8) and
     docs/review/07_two_color_pulses/review_07.tex. No run-in labels or arrows in this file. -->

::: {.card .story}
::: sl
How
:::

## How to use this guide

- Each card is one slide. The yellow box is the main point of the slide in one sentence, the paragraph under it is what
  to say, and the list at the end gives the questions that are likely and a short answer to each.
- All results are for the vector (Richards–Wolf) model in air, both beams polarized perpendicular to the plane of the
  lens axes, unless a slide says otherwise. The 656-nm pulse is delayed by Δt against the 750-nm pulse.
:::

::: card
::: sl
2
:::

## Summary: delay between the pulses

::: say
A delay weakens 2CE through the temporal overlap of the two pulses, except with facing lenses at low NA, where it
moves the 2CE along the axis instead.
:::

The delays go up to twice the pulse width, for the three lens angles from NA 0.1 to 0.95. With facing lenses and
100-fs pulses the peak at a delay of one pulse width is 0.93 of the peak without delay at NA 0.1, 0.51 at NA 0.2 and
0.25 at NA 0.9.

::: qa
- **Which pairs carry the 2CE signal here?** The 350-nm pairs, one photon from each beam, as Lim & Saloma (2003) note
  that probes are chosen to minimize two-photon excitation by either beam alone. All pairs are shown where the fringes
  are discussed.
- **Were the results checked?** Sixteen samples were recomputed with the original code (peaks within 1.8e-10), and the
  total with all pairs was recomputed as a sum over pairs of frequencies (within 1.1e-4 of the peak).
:::
:::

::: card
::: sl
3
:::

## Delay and temporal overlap

::: say
At a fixed point the 350-nm pairs fall with the overlap of the two pulses, to one half at Δt = 0.71τ and one quarter at
Δt = τ.
:::

Lim & Saloma (2003) state that spatio-temporal simultaneity of the two beams is a necessary condition for 2CE. For two
Gaussian pulses of width τ the overlap is F(Δt)/F(0) = exp(−2 ln2 Δt²/τ²). With collinear lenses the stored peaks
follow it to 1e-5 at 100 fs, at all NAs.

::: qa
- **Why exp(−2 ln2 Δt²/τ²) and not exp(−4 ln2 Δt²/τ²)?** The signal is the integral of the product of two Gaussians
  of width τ, which is a Gaussian in Δt that is √2 times wider than each pulse.
- **What changes with unequal pulse widths?** The overlap becomes exp[−4 ln2 Δt²/(τ~1~² + τ~2~²)]; this is a candidate
  for later work.
:::
:::

::: card
::: sl
4
:::

## Facing lenses: where the pulses meet

::: say
With facing lenses the delayed pulses meet at z~m~ = cΔt/2n, and the 2CE forms over a stretch of length G about that
point.
:::

The peak at a delay is exp[−4 ln2 z~m~²/(D² + G²)], with G = cτ/(√2 n) and D the continuous-beam depth of focus. At
100 fs in air G = 21.2 µm and z~m~ = 15.0 µm at Δt = τ. The formula gives 0.928 at NA 0.1 against 0.930 computed,
0.518 at NA 0.2 against 0.513 and 0.260 at NA 0.5 against 0.258.

::: qa
- **What are the two limits?** When D is much longer than G (low NA) the peak moves to z~m~ and is kept; when D is
  much shorter (high NA) the formula becomes the temporal overlap.
- **Why does the formula take D from the scalar model?** It is the value of the derivation (3.56 µm at NA 0.5,
  growing as 1/NA²); the computed peaks are those of the vector model, and the two agree to within 0.01.
:::
:::

::: card
::: sl
5
:::

## 2CE peak and position against the delay, θ = π, 100 fs

::: say
At low NA the pulses still meet inside the long focus, so the peak moves along the axis and is kept; at NA 0.5 and
above it stays at the focus and falls with the temporal overlap.
:::

At a delay of one pulse width the peak is 0.93 of its value without delay at NA 0.1, 0.32 at NA 0.3 and 0.25 at NA
0.9, and it has moved by 14.2, 2.6 and 0.02 µm. The dashed line on the right is the meeting point cΔt/2.

::: qa
- **Why does the peak not follow cΔt/2 exactly at NA 0.2?** The 2CE there is the product of the focus and the stretch
  where the pulses meet, so the peak sits between the focus and the meeting point.
- **Is 0.26 at NA 0.5 different from the overlap, 0.25?** By 0.01; the peak is within 0.01 of the temporal overlap from
  NA 0.5 up.
:::
:::

::: card
::: sl
6
:::

## 2CE peak at a delay of τ against NA, θ = π

::: say
Shorter pulses and pupils with a longer depth of focus keep more of the 2CE peak at Δt = τ.
:::

At NA 0.5 the peak at Δt = τ is 0.26 at 100 fs, 0.41 at 20 fs and 0.87 at 5 fs, since the meeting point moves a
shorter distance. At NA 0.3 and 100 fs it is 0.32 for the circular pupil, 0.38 for the Gaussian input and 0.80 for the
annular pupil with ε = 0.9.

::: qa
- **What is the use of this?** It is the use that Cambaliza & Saloma (2000) propose for annular lenses, a longer focus,
  here applied to the timing of the pulses: a longer focus tolerates a larger delay.
:::
:::

::: card
::: sl
7–9
:::

## 2CE peak against the delay at 5, 10 and 20 fs, NA 0.5

::: say
Below 20 fs phase-locked pulses with all photon pairs give fringes against the delay, with periods of 2.19, 2.50 and
1.17 fs, while the 350-nm pairs alone fall smoothly.
:::

The delay changes the phase between the 350-nm pairs and the 375- and 328-nm pairs. The fringes are 2.19 fs apart
against the 375-nm pairs (the period of 656 nm), 2.50 fs against the 328-nm pairs (the period of 750 nm) and 1.17 fs
between the 375- and 328-nm pairs (the period of 350 nm). At 20 fs the fringes are shallow.

::: qa
- **Would two separate lasers show these fringes?** No. With two lasers that are not phase-locked the fringes average
  out and the 350-nm pairs remain.
- **Why do the facing-lens curves nearly coincide?** Along the axis the peak follows the 350-nm fringes in space as
  the delay moves them, so the fringes against the delay are shallow there.
:::
:::

::: card
::: sl
10
:::

## Fringe depth against NA, 5 to 20 fs

::: say
With crossed and facing lenses the fringes against the delay deepen with NA; with collinear lenses their depth is the
same at all NAs.
:::

With collinear lenses the depth is 0.92 at 5 fs and 0.71 at 10 fs at all NAs. With crossed lenses at 5 fs it is 0.20
at NA 0.3 and 0.65 at NA 0.7; with facing lenses at 5 fs it is 0.03 at NA 0.5 and 0.27 at NA 0.95. At 20 fs it is at
most 0.04.

::: qa
- **Why does NA matter?** The delay moves the interference fringes in space with crossed and facing lenses; a high-NA
  spot is about one fringe wide, so the peak follows the fringes. With collinear lenses the three kinds of pairs have
  the same carrier in space.
- **Is the crossed-lens depth taken along x only?** Yes, along the x axis through the focus. Over the whole x–z plane
  it is about two thirds of this (0.28 against 0.42 at NA 0.5 and 5 fs).
:::
:::

::: card
::: sl
11
:::

## 2CE peak against the delay, two polarizations, θ = π/2

::: say
With crossed lenses and the polarization in the plane of the lens axes, the fringes against the delay are about a
quarter as deep, because the two fields are perpendicular at the focus.
:::

The amplitude of the oscillating part is about 0.05 against 0.21 at NA 0.5 and 5 fs. The 350-nm pairs fall with the
delay in the same way for both polarizations, and the 2CE spot is wider (0.83 against 0.75 µm at NA 0.5).

::: qa
- **Why are the fringes not absent?** The longitudinal field away from the focus mixes the components.
- **Do real molecules respond in the same way to both polarizations?** Not in general: the absorption of two photons
  with perpendicular polarizations differs from that of parallel ones by a factor that depends on the molecule, which
  the model does not include.
- **How is the amplitude measured?** As half the swing of the total after a 5-fs smooth (Savitzky–Golay, 51 points,
  order 3) is subtracted.
:::
:::
