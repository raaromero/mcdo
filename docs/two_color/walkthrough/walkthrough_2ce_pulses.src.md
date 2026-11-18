---
title: "Dashboard guide: two-color excitation with femtosecond pulses at high NA"
subtitle: "This guide pairs 2ce_pulses.pptx and its concise version 2ce_pulses_main.pptx with the dashboard, slide by slide. The links open the local dashboard on port 4317 until it is deployed again."
---

<!-- Source of 2ce_pulses_guide.pdf. The local dashboard is started with npm run dev in dashboard/cambaliza (port 4317).
     Build: python build.py 2ce_pulses (fills each [[id]] from steps_2ce_pulses.json with the link, the settings as a sentence
     and the screenshot). Screenshots: node shoot.mjs steps_2ce_pulses.json img_2ce_pulses, with vite preview on 4173 and
     headless Chromium on 9333. The steps of slides 4 to 10, 12 (second step), 15 to 20 and 22 to 30 are those of steps_high_na_pulses.json
     (b30 to b54b), renumbered, with their screenshots copied from img_high_na_pulses/; the steps p11, p12a, p13,
     p14 and p36 to p39 were taken on 2026-11-18. Each card is one slide of 2ce_pulses.pptx; its title and the bullets in the blue box
     are those of the deck, word for word (read with python-pptx, 2026-11-18). No run-in labels or arrows anywhere in
     this file. -->

::: {.card .story}
::: sl
How
:::

## How to use this guide

- Each card is one slide of 2ce_pulses.pptx. Its number is the number of the slide in that deck, which is also printed in
  the corner of the slide.
- The concise deck 2ce_pulses_main.pptx takes 16 of these slides with the same titles and bullets, so a slide of
  the concise deck has the card of the same title here.
- Each step says which tab to open, which controls to set and which point to click; all other controls stay at their
  defaults. The link Open in each step loads all of these settings at once.
- Where a result has a card on the tab Highlights, the step opens that card. Its banner gives the result in one
  sentence.
- The yellow box under the title of each slide states the result of that slide in one sentence. The yellow box under
  each screenshot states the main point of the step, and the text below it says what to point at. The blue box
  repeats the bullets of the slide.
- Slides 2, 31 and 32 have no view in the dashboard; their cards give the result and what to say. The title slide,
  the dividers and the glossary have no card.
:::

::: card
::: sl
2
:::

## Summary

::: say
With pulses, the lens angle and the NA decide how much of the continuous-beam 2CE is kept: collinear and crossed lenses keep the continuous-beam focus, and facing lenses shorten it, more so at lower NA.
:::

The dashboard has no view of this slide. Say that the results are for the vector (Richards–Wolf) model in air unless a slide says otherwise. At 10 fs the 375- and 328-nm pairs have 18% and 14% of the amplitude of the 350-nm pairs, and at 20 fs both are below 1%.

::: deck

These are the bullets of slide 2.

- Extended the 2CE and 2PE point spread functions from continuous beams to transform-limited femtosecond pulses of 4 to 1000 fs, from NA 0.1 to 0.95 in air, to 1.25 in water and to 1.45 in oil, with circular and annular pupils and Gaussian input.
- Found that at 100 fs pulsed 2CE is the same as with continuous beams at all three lens angles, and that with collinear and crossed lenses it keeps the continuous-beam depth of focus to within a few percent.
- Found that with facing lenses pulsed 2CE forms where the two pulses meet, so its depth of focus is shorter than with continuous beams, more so at lower NA: the pulse width that matches continuous beams grows from 25 fs at NA 0.9 to 610 fs at NA 0.2.
- Found that below about 15 fs one beam alone also excites the 350-nm level, so 2CE carries fringes and starts to lose its weak background in scattering media.
- Delayed one pulse relative to the other: the peak 2CE fluorescence decreases as their temporal overlap, except with facing lenses at low NA, where the peak moves along the axis and is largely retained.

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

::: say
A short pulse has a Gaussian spectrum about its carrier frequency, and each frequency of the spectrum is a continuous wave.
:::

[[p04|4]]

::: main
The spectra of the two 10-fs pulses are Gaussians centred at 400 THz (750 nm) and 457 THz (656 nm).
:::

::: look
Point at the chart “Spectrum arriving at the focus now”: the dashed curves are the full spectra, and the solid curves are the part of each spectrum that reaches the focus at this instant.
:::

::: deck

These are the bullets of slide 4.

- The optical spectrum of a short pulse is a Gaussian in frequency about the carrier frequency (left), and each frequency is a continuous wave (right).

:::
:::

::: card
::: sl
5
:::

## Sum of the frequencies of a 10-fs optical pulse

::: say
At t = 0 the frequencies are in phase and add up, and away from t = 0 they drift out of phase, so their sum is a pulse of width τ.
:::

[[p05|5]]

::: main
The two pulses pass the focus as short packets of intensity, one from each lens.
:::

::: look
Point at the chart of I~1~ and I~2~ along the axis, and press Play to show the two pulses moving through the focus.
:::

::: deck

These are the bullets of slide 5.

- At t = 0 all the frequencies are in phase and add up; away from t = 0 they drift out of phase, so their sum falls off as a Gaussian of width τ, the pulse.

:::
:::

::: card
::: sl
6
:::

## Pulse width and spectral bandwidth

::: say
A transform-limited Gaussian pulse has a spectral bandwidth Δν = 0.441/τ, so a shorter pulse has a wider spectrum.
:::

[[p06|6]]

::: main
At 20 fs the two spectra barely reach 700 nm.
:::

::: look
In the spectrum chart, both spectra have fallen almost to zero at the line at 428 THz, which is 700 nm.
:::

::: deck

These are the bullets of slide 6.

- A transform-limited Gaussian pulse is Gaussian in time (left) and in frequency (right), with spectral bandwidth Δν = 0.441/τ.

:::
:::

::: card
::: sl
7
:::

## Pulse spectra against wavelength, τ = 5, 10, 20 and 100 fs

::: say
Below about 15 fs the spectra reach 700 nm, where two photons of one pulse add up to 350 nm.
:::

[[p07|7]]

::: main
At 5 fs the two spectra overlap strongly at 700 nm.
:::

::: look
Both spectra cross the line at 428 THz at well above a third of their peak, so two photons of one pulse can reach the 350-nm level.
:::

::: deck

These are the bullets of slide 7.

- Against wavelength, both colors lie at the red edge of the visible range.
- Below about 15 fs the spectra reach 700 nm, where two photons of one pulse add up to 350 nm.

:::
:::

::: card
::: sl
8
:::

## Photon pairs that excite the 350-nm level

::: say
The excitation adds the amplitudes of all photon pairs that sum to the 350-nm level and then squares the total, so the 375- and 328-nm pairs enter beside the 350-nm pairs.
:::

[[p08|8]]

::: main
At 10 fs the 375- and 328-nm pairs add a visible part to the signal of the 350-nm pairs.
:::

::: look
Point at the chart “Pair sums at the focus, accumulated up to t”, where each kind of pair has its own curve.
:::

::: deck

These are the bullets of slide 8.

- Each lens focuses a transform-limited Gaussian pulse of width τ; the centres of both pulses reach the focus at t = 0.
- The excitation adds the amplitudes of all photon pairs that sum to the 350-nm level, then squares the total: the 350-nm pairs (750 + 656 nm), the 375-nm pairs (750 + 750 nm) and the 328-nm pairs (656 + 656 nm).

The line under the equations reads as follows.

> where E~1~ and E~2~ are the fields of the 750- and 656-nm pulses at a point, ω~e~ is the frequency of the 350-nm level and F is the total 2CE accumulated as the pulses pass the focus. For long pulses F becomes I~1~ I~2~, the result of Cambaliza & Saloma (2000).

:::
:::

::: card
::: sl
9
:::

## 2CE with 100-fs pulses and with continuous beams, θ = 0 and π

::: say
At 100 fs pulsed 2CE is the same as with continuous beams, so the continuous-beam results of Cambaliza & Saloma (2000) hold for pulses of that length.
:::

[[p09|9]]

::: main
With facing lenses the 100-fs profile along the axis lies on the continuous-beam profile.
:::

::: look
Point at the profile at τ = 100 fs: the red total and the dashed continuous-beam curve coincide, with depths of focus of 3.52 µm and 3.56 µm on the slide.
:::

::: deck

These are the bullets of slide 9.

- At 100 fs, pulsed 2CE is the same as with continuous beams at all three lens angles, so the continuous-beam results of Cambaliza & Saloma (2000) hold for pulses of that length.

:::
:::

::: card
::: sl
10
:::

## 2CE with 100-fs pulses and with continuous beams, θ = π/2

::: say
With crossed lenses the pulsed 2CE across the axis at 100 fs is also the same as with continuous beams.
:::

[[p10|10]]

::: main
With crossed lenses the 100-fs profile across the axis lies on the continuous-beam profile.
:::

::: look
The red total and the dashed continuous-beam curve coincide across the axis, with a width of 0.76 µm.
:::

::: deck

These are the bullets of slide 10.

- With crossed lenses, the pulsed 2CE distribution across the axis at 100 fs is also the same as with continuous beams.

:::
:::

::: card
::: sl
11
:::

## 2CE depth of focus against pulse width, facing lenses

::: say
With facing lenses the pulsed 2CE depth of focus falls below the continuous-beam value as the pulses get shorter, and more at lower NA, because 2CE forms where the two pulses meet.
:::

[[p11|11]]

::: main
At 20 fs the depth of focus with pulses is 0.81 of the continuous-beam value at NA 0.5 and 0.19 at NA 0.2.
:::

::: look
Scroll down to the chart “Depth of focus of 2CE against the pulse width, Richards–Wolf, air, θ = π”, which has one curve per NA. Point at the curves of low NA, which reach 1 at long pulses, and at those of high NA, which stay near 1 down to 10 fs (0.97 at NA 0.9).
:::

::: deck

These are the bullets of slide 11.

- With facing lenses, the pulsed 2CE depth of focus falls below the continuous-beam value as the pulses get shorter, and more at lower NA, because 2CE forms where the two pulses meet.
- At NA 0.9 it is 97% of the continuous-beam value at 10 fs; at NA 0.5 it is 81% at 20 fs, and at NA 0.2 it is 70% at 100 fs.

:::
:::

::: card
::: sl
12
:::

## 2CE depth of focus against pulse width, collinear and crossed lenses

::: say
With collinear and crossed lenses pulsed 2CE keeps the continuous-beam depth of focus to within a few percent, because the pulses overlap over the whole focus.
:::

[[p12a|12]]

::: main
With collinear lenses the depth of focus with pulses stays within 0.5% of the continuous-beam value at all NAs, down to 4 fs.
:::

::: look
Scroll down to the chart “Depth of focus of 2CE against the pulse width, Richards–Wolf, air, θ = 0”, where all curves lie on 1.
:::

[[p12b|12]]

::: main
With crossed lenses the depth of focus with pulses is 1.07 times the continuous-beam value at 5 fs and NA 0.7, and 0.88 times at 4 fs and NA 0.2.
:::

::: look
Point at the chart of the depth of focus against τ on the right, θ = π/2, whose curves come within 1% of 1 from 20 fs at NA 0.3 and above; the chart on the left gives the pulse width at which the profiles match the continuous-beam ones to 1%.
:::

::: deck

These are the bullets of slide 12.

- With collinear lenses, pulsed 2CE keeps the continuous-beam depth of focus to within 0.5% down to 4 fs, because the two pulses travel together and overlap over the whole focus.
- With crossed lenses, it stays within 1% from 20 fs at NA 0.3 and above (2% at NA 0.2); below 15 fs it grows by up to 7% at high NA, because the 375-nm pairs of L1 alone extend along its axis.

:::
:::

::: card
::: sl
13
:::

## 2CE depth of focus against NA, facing lenses

::: say
As NA increases the 2CE depth of focus with pulses returns to the continuous-beam value with facing lenses at each pulse width, because the focus becomes shorter than the stretch where the pulses overlap.
:::

[[p13|13]]

::: main
At 20 fs the depth of focus with pulses is 0.41 of the continuous-beam value at NA 0.3 and 0.99 at NA 0.9.
:::

::: look
Scroll down to the chart “Depth of focus of 2CE against NA, Richards–Wolf, air, θ = π”, which has one curve per pulse width. Point at the curve of 20 fs, which rises towards 1 as NA increases, and at the curves of shorter pulses, which rise later.
:::

::: deck

These are the bullets of slide 13.

- As NA increases, the ratio of the 2CE depth of focus with pulses to that with continuous beams returns to 1 with facing lenses at each pulse width, because the focus becomes shorter than the stretch where the pulses overlap.

:::
:::

::: card
::: sl
14
:::

## 2CE along the axis with pulses at NA 0.5 and NA 0.9, facing lenses

::: say
At NA 0.9 the focus is shorter than the stretch where the pulses meet, so 100- and 20-fs pulses give nearly the continuous-beam 2CE profile along the axis, while at NA 0.5 20-fs pulses shorten it.
:::

[[p14|14]]

::: main
The largest difference between the pulsed and continuous-beam 2CE profiles falls below 1% of the peak from 87 fs at NA 0.5 and from 25 fs at NA 0.9.
:::

::: look
Scroll down to the chart “Largest difference of 2CE against the pulse width, Richards–Wolf, air, θ = π”. Point at the curves of NA 0.5 and NA 0.9: at 20 fs the curve of NA 0.9 is at about 3% and that of NA 0.5 at about 16%, and at 10 fs both are above 50%, because of the fringes of the 375- and 328-nm pairs.
:::

::: deck

These are the bullets of slide 14.

- At NA 0.5, 20-fs pulses shorten the 2CE along the axis, and at 10 fs the 375- and 328-nm pairs add fringes 350 nm apart.
- At NA 0.9 the focus is shorter than the stretch where the pulses meet, so 100- and 20-fs pulses give the continuous-beam profile; at 10 fs the fringes remain.

:::
:::

::: card
::: sl
15
:::

## Overlap in time of the two facing pulses

::: say
The facing pulses overlap in time over a stretch of cτ/√2 about the focus, 4.2 µm at 20 fs, and the pulsed 2CE is the continuous-beam profile times this overlap.
:::

[[p15|15]]

::: main
At 20 fs the total 2CE along the axis is shorter than the continuous-beam profile.
:::

::: look
Point at the red total and the dashed continuous-beam curve. The overlap of the pulses, 4.2 µm wide at 20 fs, shortens the depth of focus to 2.78 µm with all pairs.
:::

::: deck

These are the bullets of slide 15.

- Pulse 1 passes a point z at t = z/c and pulse 2 at t = −z/c, so their intensities overlap in time over a stretch of cτ/√2 about the focus, 4.2 µm at 20 fs.
- The pulsed 2CE is the continuous-beam profile times this overlap: at 20 fs the product gives 2.74 µm and the full calculation 2.78 µm.

:::
:::

::: card
::: sl
16
:::

## Signal added by the 375- and 328-nm pairs

::: say
Below about 15 fs two photons of one pulse also excite the 350-nm level, so one beam alone excites and 2CE starts to lose the weak background of continuous beams.
:::

[[p16|16]]

::: main
The signal added by the 375- and 328-nm pairs rises steeply as the pulse width decreases below 15 fs.
:::

::: look
Point at the chart “Signal added by the 375- and 328-nm pairs” on its log axes. The total over the 350-nm pairs is 1.02 at 20 fs and 1.73 at 10 fs, as on the slide.
:::

::: deck

These are the bullets of slide 16.

- Below about 15 fs the spectra reach 700 nm, so two photons of one pulse also excite the 350-nm level, through the 375- and 328-nm pairs.
- Their amplitude interferes with that of the 350-nm pairs, which gives the fringes, and one beam alone now excites, so 2CE starts to lose the weak background of continuous beams.

:::
:::

::: card
::: sl
17
:::

## Pulse width that matches continuous beams against NA, θ = π

::: say
With facing lenses the pulse width needed to match continuous beams grows as NA decreases, because a lower NA gives a longer focus for the pulses to overlap over.
:::

[[p17|17]]

::: main
With facing lenses in air the pulse width needed is about 25 fs at NA 0.9, 87 fs at NA 0.5 and 610 fs at NA 0.2.
:::

::: look
Point at the chart of the pulse width against NA, with curves for air, water and oil. The curves of water and oil lie at a higher NA for the same pulse width, so at the same NA they need a longer pulse.
:::

::: deck

These are the bullets of slide 17.

- With facing lenses, the pulsed 2CE matches the continuous-beam 2CE once the pulses are longer than about 25 fs at NA 0.9, 87 fs at NA 0.5 and 264 fs at NA 0.3 in air, because a lower NA gives a longer focus for the pulses to overlap over.
- In water and in oil a longer pulse is needed at the same NA (164 fs and 216 fs at NA 0.5), because the focus is longer in a medium of higher refractive index.

:::
:::

::: card
::: sl
18
:::

## Pulse width that matches continuous beams, θ = 0 and π/2

::: say
With collinear lenses pulsed 2CE matches continuous beams down to 4 fs, and with crossed lenses it matches once the pulses are longer than about 28 fs at NA 0.2 and 21 fs at NA 0.7.
:::

[[p18|18]]

::: main
With crossed lenses 2CE matches continuous beams from about 20 to 28 fs, from NA 0.2 up.
:::

::: look
The chart of the pulse width against NA at θ = π/2 is nearly flat. At θ = 0 it lies at 4 fs, the shortest pulse computed.
:::

::: deck

These are the bullets of slide 18.

- With collinear lenses, the pulsed 2CE matches the continuous-beam 2CE at all pulse widths computed, down to 4 fs, because the two pulses travel together and overlap over the whole focus.
- With crossed lenses, it matches once the pulses are longer than about 28 fs at NA 0.2 and 21 fs at NA 0.7.

:::
:::

::: card
::: sl
19
:::

## Pulse width that matches continuous beams: pupils, θ = π

::: say
With facing lenses a pupil or an input that gives a longer depth of focus needs a longer pulse to match continuous beams.
:::

[[p19|19]]

::: main
At NA 0.5 the annular pupil with ε = 0.9 needs 405 fs by the largest difference between the profiles, against 87 fs for the circular pupil. By the depth of focus, the measure of the slide, the two are 466 fs and 100 fs.
:::

::: look
Point at the largest difference against τ for the annular pupil, with one curve per NA, and at the pulse width where each curve falls below 1%.
:::

::: deck

These are the bullets of slide 19.

- With facing lenses, a pupil or an input that gives a longer depth of focus needs a longer pulse to match continuous beams: at NA 0.5, 100 fs for the circular pupil, 162 fs for the Gaussian input (α = 4) and 466 fs for the annular pupil with ε = 0.9.

:::
:::

::: card
::: sl
20
:::

## Pulse width that matches continuous beams: pupils, θ = 0, π/2

::: say
With collinear lenses the 2CE depth of focus matches continuous beams at all pulse widths computed, and with crossed lenses it matches from about 11 to 16 fs at NA 0.4 and above, for all pupils and inputs.
:::

[[p20|20]]

::: main
With crossed lenses the depth of focus of the annular pupil matches continuous beams from about 15 fs.
:::

::: look
Point at the curves of the depth of focus against τ at θ = π/2, which reach the line at 1 from about 15 fs.
:::

::: deck

These are the bullets of slide 20.

- With collinear lenses, the 2CE depth of focus matches its continuous-beam value at all pulse widths computed, for all pupils and inputs.
- With crossed lenses, it matches once the pulses are longer than about 11 to 16 fs at NA 0.4 and above, for all pupils and inputs.

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

::: say
At a fixed point the peak 2CE fluorescence of the 350-nm pairs decreases with the delay as the temporal overlap of the two pulses: a delay of 0.40 τ reduces the peak by 20%, and a delay of τ by 75%.
:::

[[p22|22]]

::: main
With collinear lenses the peak 2CE fluorescence follows the temporal overlap at all NAs.
:::

::: look
Point at the chart of the peak against Δt/τ: the curves of the six NAs lie on the dotted temporal overlap, exp(−2 ln2 (Δt/τ)²), which is 0.25 at Δt/τ = 1.
:::

::: deck

These are the bullets of slide 22.

- 2CE needs the two pulses at the same place and at the same time: Lim & Saloma (2003) note that achieving optimal temporal overlap of the 2CE pulses is crucial.
- At a fixed point, the 2CE of the 350-nm pairs decreases with the delay Δt as the overlap in time of two Gaussian pulses of width τ.

The line under the equation reads as follows.

> where F is the peak 2CE fluorescence, Δt the delay of the 656-nm pulse relative to the 750-nm pulse and τ the pulse width. A delay of 0.40 τ reduces the peak by 20%, a delay of 0.71 τ by one half and a delay of τ by 75%.

:::
:::

::: card
::: sl
23
:::

## Facing lenses: position where the delayed pulses meet

::: say
With facing lenses the delayed pulses meet at z~m~ = cΔt/2n, and 2CE forms over a stretch of length G = cτ/(√2 n) about that position.
:::

[[p23|23]]

::: main
At low NA the peak moves along the axis towards the position where the pulses meet.
:::

::: look
Point at the chart of the position of the peak against Δt and at the dashed line cΔt/2: the curve of NA 0.1 follows the line, while the curves of higher NA stay near the focus.
:::

::: deck

These are the bullets of slide 23.

- With facing lenses, the delayed pulses meet at z~m~ = cΔt/2n, and 2CE forms over a stretch of length G = cτ/(√2 n) about that position.
- With D the continuous-beam depth of focus of 2CE, the peak 2CE fluorescence at a delay Δt follows from the product of the focus and this stretch.

The line under the equations reads as follows.

> where z~m~ is the position where the delayed pulses meet and G the length of the stretch over which they overlap. A long focus (D much larger than G) retains the peak, which moves with z~m~; a short focus holds the peak at the focus, where it decreases as the temporal overlap.

:::
:::

::: card
::: sl
24
:::

## Peak 2CE fluorescence and its position against the delay, θ = π

::: say
With facing lenses at low NA the delayed pulses still meet inside the long depth of focus, so the peak 2CE fluorescence moves along the axis and is largely retained; at NA 0.5 and above it stays at the focus and decreases as the temporal overlap.
:::

[[p24a|24]]

::: main
At NA 0.1 and 100 fs, a delay of one pulse width reduces the peak by 7% and moves it 14 µm from the focus.
:::

::: look
Point at the curve of NA 0.1 on the chart of the position at Δt = 100 fs, and at the same NA on the chart of the peak beside it, at Δt/τ = 1.
:::

[[p24b|24]]

::: main
At NA 0.5 and above the peak decreases as the temporal overlap; at NA 0.5 a delay of one pulse width reduces it by 74%.
:::

::: look
Point at the curves of NA 0.5, 0.7 and 0.9, which lie on the dotted temporal overlap.
:::

::: deck

These are the bullets of slide 24.

- With facing lenses at low NA, the delayed pulses still meet inside the long depth of focus, so the peak 2CE fluorescence moves along the axis and is largely retained: at NA 0.1 and 100 fs, a delay of one pulse width reduces the peak by 7%.
- At NA 0.5 and above, the peak stays at the focus and decreases as the temporal overlap of the two pulses (dotted line), by 74% at a delay of one pulse width.

:::
:::

::: card
::: sl
25
:::

## Peak 2CE fluorescence at a delay of one pulse width against NA

::: say
As NA increases the peak 2CE fluorescence that remains at a delay of one pulse width decreases to one quarter, and shorter pulses and pupils with a longer depth of focus retain more of it.
:::

[[p25a|25]]

::: main
At NA 0.3 and 100 fs the peak that remains at a delay of one pulse width is 0.32 for the circular pupil and 0.80 for the annular pupil with ε = 0.9.
:::

::: look
Point at the green curve of the annular pupil with ε = 0.9, which stays high up to a larger NA than the others, and at the dotted line of the temporal overlap, 0.25, which all curves reach at high NA.
:::

[[p25b|25]]

::: main
At 30 fs all pupils retain more of the peak than at 100 fs at the same NA.
:::

::: look
The curves move to lower NA as τ decreases, because the position where the pulses meet moves by a shorter distance.
:::

::: deck

These are the bullets of slide 25.

- As NA increases, the peak 2CE fluorescence that remains at a delay of one pulse width decreases to one quarter, the temporal overlap of the two pulses; shorter pulses retain more, because the position where they meet moves by a shorter distance (left).
- A Gaussian input and annular pupils, which give a longer depth of focus, retain more of the peak at the same NA (right).

:::
:::

::: card
::: sl
26
:::

## Peak 2CE fluorescence against the delay, τ = 5 fs, NA 0.5

::: say
With all photon pairs and phase-locked pulses the peak 2CE fluorescence oscillates with the delay, while the peak of the 350-nm pairs alone decreases smoothly as the temporal overlap.
:::

[[p26a|26]]

::: main
With collinear lenses at 5 fs the fringes are deep, with periods of 2.19, 2.50 and 1.17 fs.
:::

::: look
Point at the blue curve of all pairs, which swings about the red curve of the 350-nm pairs by up to 0.92 of the peak.
:::

[[p26b|26]]

::: main
With crossed lenses at NA 0.5 the fringes are shallower than with collinear lenses.
:::

::: look
Along x, the blue curve swings about the red one by about 0.4 of the peak.
:::

::: deck

These are the bullets of slide 26.

- With all photon pairs and phase-locked pulses, the peak 2CE fluorescence oscillates with the delay, with periods of 2.19, 2.50 and 1.17 fs, because the delay changes the phase of the 350-nm pairs relative to the 375- and 328-nm pairs.
- The 2CE of the 350-nm pairs alone decreases smoothly with the delay, as the temporal overlap of the two pulses.

:::
:::

::: card
::: sl
27
:::

## Peak 2CE fluorescence against the delay, τ = 10 fs, NA 0.5

::: say
At 10 fs the peak 2CE fluorescence with all photon pairs still oscillates with the delay, with the same three periods as at 5 fs.
:::

[[p27|27]]

::: main
At 10 fs the fringes with collinear lenses still swing by about 0.7 of the peak.
:::

::: look
Point at the fringes of the blue curve near Δt = 0, which fade as the two pulses separate.
:::

::: deck

These are the bullets of slide 27.

- With all photon pairs and phase-locked pulses, the peak 2CE fluorescence oscillates with the delay, with periods of 2.19, 2.50 and 1.17 fs, because the delay changes the phase of the 350-nm pairs relative to the 375- and 328-nm pairs.
- The 2CE of the 350-nm pairs alone decreases smoothly with the delay, as the temporal overlap of the two pulses.

:::
:::

::: card
::: sl
28
:::

## Peak 2CE fluorescence against the delay, τ = 20 fs, NA 0.5

::: say
At 20 fs the amplitude of the 375- and 328-nm pairs is below 1% of that of the 350-nm pairs, so the total peak 2CE fluorescence follows that of the 350-nm pairs and decreases smoothly with the delay.
:::

[[p28|28]]

::: main
At 20 fs the blue and red curves nearly coincide.
:::

::: look
The largest gap between the two curves is about 0.04 of the peak.
:::

::: deck

These are the bullets of slide 28.

- At 20 fs, the amplitude of the 375- and 328-nm pairs is below 1% of that of the 350-nm pairs, so the total 2CE follows the 2CE of the 350-nm pairs.
- The peak decreases smoothly with the delay, as the temporal overlap of the two pulses.

:::
:::

::: card
::: sl
29
:::

## Fringe depth of the 2CE peak against NA, τ = 5, 10 and 20 fs

::: say
With crossed and facing lenses the fringes against the delay deepen as NA increases, because the delay moves the interference fringes in space across a smaller focal spot; with collinear lenses the depth is the same at all NAs.
:::

[[p29a|29]]

::: main
With crossed lenses at 5 fs and NA 0.3 the fringes are shallow, with a depth of about 0.2 of the peak.
:::

::: look
Point at the small swing of the blue curve about the red one.
:::

[[p29b|29]]

::: main
At NA 0.7 the same fringes swing by about 0.65 of the peak.
:::

::: look
Compare this swing with that of the previous step. A smaller focal spot holds fewer of the fringes in space, so the peak follows them as the delay moves them.
:::

::: deck

These are the bullets of slide 29.

- With crossed and facing lenses, the fringes of the peak against the delay deepen as NA increases, because the delay moves the interference fringes in space across a smaller focal spot.
- With collinear lenses, the three kinds of photon pairs have no fringes in space, so the fringe depth is the same at all NAs: 0.92 at 5 fs and 0.71 at 10 fs.

:::
:::

::: card
::: sl
30
:::

## Peak 2CE fluorescence against the delay for two polarizations

::: say
With crossed lenses and the polarization in the plane of the two lens axes, the fields of the two beams are perpendicular at the focus, so the fringes against the delay are about a quarter as deep.
:::

[[p30a|30]]

::: main
With the polarization in the plane of the lens axes the fringes are shallow, with an amplitude of about 0.05.
:::

::: look
Point at the blue curve of all pairs. Both curves are divided by the value of all pairs at no delay, so the red curve of the 350-nm pairs starts below 1.
:::

[[p30b|30]]

::: main
With the polarization perpendicular to that plane the amplitude is about 0.21.
:::

::: look
Switch the polarization control between the two settings to compare the depth of the fringes; each curve is then divided by its own value at no delay.
:::

::: deck

These are the bullets of slide 30.

- With the polarization in the plane of the two lens axes, the fields of the two beams are perpendicular at the focus, so the three kinds of photon pairs fall in different field components and interfere less.
- The fringes against the delay are then about a quarter as deep, while the 2CE of the 350-nm pairs decreases with the delay in the same way for both polarizations.

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

::: say
The lens angle decides what a pulse and a delay change: collinear and crossed lenses keep the continuous-beam focus, facing lenses shorten it, and a delay reduces the peak as the temporal overlap except with facing lenses at low NA.
:::

The dashboard has no view of this slide. Read the six bullets in order, with collinear θ = 0, crossed θ = π/2 and facing θ = π. The results assume phase-locked, transform-limited pulses and a 350-nm level that is narrow compared to the pulse spectra.

::: deck

These are the bullets of slide 31.

- At 100 fs, pulsed 2CE is the same as with continuous beams.
- With collinear and crossed lenses, pulsed 2CE keeps the continuous-beam depth of focus and spot to within a few percent.
- With facing lenses, pulsed 2CE forms where the pulses meet, so its depth of focus is shorter than with continuous beams, more so at lower NA; 2PE shortens less.
- Below about 15 fs one beam alone also excites the 350-nm level, so 2CE carries fringes and starts to lose its weak background.
- With a delay between the two pulses, the peak 2CE fluorescence decreases as their temporal overlap, to one quarter at a delay of one pulse width; with facing lenses at low NA the peak moves along the axis and is largely retained.
- The results assume phase-locked, transform-limited pulses and a 350-nm level that is narrow compared to the pulse spectra.

:::
:::

::: card
::: sl
32
:::

## Next steps

::: say
Pulsed 2CE through a highly scattering medium is the first candidate, because Cambaliza & Saloma (2000) found the advantage of 2CE compared to 2PE there.
:::

The dashboard has no view of this slide. Say that the scattering medium combines the Monte Carlo model of the focus with the pulse model, and that it would show whether 2CE with pulses keeps its weak background. With unequal pulse widths the overlap becomes exp[−4 ln2 Δt²/(τ~1~² + τ~2~²)], and for a broad absorption band the signal of the 350-nm pairs is the integral of I~1~I~2~ over time.

::: deck

These are the bullets of slide 32.

- Compute pulsed 2CE through a highly scattering medium, where Cambaliza & Saloma (2000) found the main advantage of 2CE compared to 2PE.
- Compute pulses of unequal width and chirped pulses, which change the overlap in time of the two pulses.
- Replace the narrow 350-nm level with a broad absorption band.

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

::: say
With facing lenses pulsed 2PE matches continuous beams at a shorter pulse width than 2CE, 62 fs against 87 fs at NA 0.5 in air, because pairs of photons from one pulse need no overlap.
:::

[[p36|36]]

::: main
The chart gives the pulse width from which the 2PE profiles match the continuous-beam ones to 1%, against NA, in air, water and oil.
:::

::: look
Point at the solid curve of air at NA 0.5, at 62 fs; the 2CE curve of slide 17 is at 87 fs there. The dashed scalar curves are drawn to NA 0.95 in the dashboard and to NA 0.5 on the slide.
:::

::: deck

These are the bullets of slide 36.

- With facing lenses, the pulsed 2PE matches the continuous-beam 2PE at shorter pulse widths than 2CE (62 fs compared to 87 fs at NA 0.5 in air), because pairs of photons from one pulse need no overlap.

:::
:::

::: card
::: sl
37
:::

## Pulse width that matches continuous beams: 2PE, θ = 0, π/2

::: say
With collinear lenses pulsed 2PE matches continuous beams down to 4 fs, and with crossed lenses once the pulses are longer than 37 fs at NA 0.1 and 6 fs at NA 0.5.
:::

[[p37|37]]

::: main
With crossed lenses the pulse width needed for 2PE falls from 37 fs at NA 0.1 to 4 fs, the shortest computed, from NA 0.6.
:::

::: look
Point at the falling curve of air. Setting the angle for the plots against NA to θ = 0 gives a flat line at 4 fs.
:::

::: deck

These are the bullets of slide 37.

- With collinear lenses, the pulsed 2PE matches the continuous-beam 2PE at all pulse widths computed, down to 4 fs.
- With crossed lenses, it matches once the pulses are longer than 37 fs at NA 0.1 and 6 fs at NA 0.5.

:::
:::

::: card
::: sl
38
:::

## Pulse width that matches continuous beams: 2PE, pupils, θ = π

::: say
With facing lenses a pupil or an input that gives a longer depth of focus also needs a longer pulse for 2PE to match continuous beams.
:::

[[p38|38]]

::: main
At NA 0.5 the 2PE depth of focus comes within 1% of its continuous-beam value from 72 fs for the circular pupil and from 334 fs for the annular pupil with ε = 0.9.
:::

::: look
Scroll down to the chart “Depth of focus of 2PE against the pulse width, Richards–Wolf, air, ε = 0.9, θ = π”, which has one curve per NA, and compare it with the same chart for the circular pupil (Richards–Wolf, air) in the menu of the model, medium and pupil.
:::

::: deck

These are the bullets of slide 38.

- With facing lenses, a pupil or an input that gives a longer depth of focus also needs a longer pulse for 2PE to match continuous beams.

:::
:::

::: card
::: sl
39
:::

## Pulse width that matches continuous beams: 2PE, pupils, θ = 0, π/2

::: say
With collinear lenses the 2PE depth of focus matches continuous beams at all pulse widths computed, and with crossed lenses the pulse width needed is largest at low NA and falls below 10 fs at NA 0.7.
:::

[[p39|39]]

::: main
With crossed lenses and the annular pupil with ε = 0.9, the 2PE depth of focus comes within 1% of its continuous-beam value from 6.2 fs at NA 0.5 and 4.4 fs at NA 0.7.
:::

::: look
Scroll down to the chart of the depth of focus of 2PE against τ at θ = π/2 for ε = 0.9. The menu of the model, medium and pupil switches to the Gaussian input, which needs the longest pulses at low NA.
:::

::: deck

These are the bullets of slide 39.

- With collinear lenses, the 2PE depth of focus matches its continuous-beam value at all pulse widths computed, for all pupils and inputs.
- With crossed lenses, the pulse width needed is largest at low NA (68 fs for the Gaussian input at NA 0.1) and falls below 10 fs at NA 0.7.

:::
:::
