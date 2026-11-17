---
title: "Dashboard guide for the deck on the delay between the pulses"
subtitle: "This guide pairs pulse_delay.pptx with the section Delay between the pulses, against NA of the tab Pulse results, slide by slide. The links open the local dashboard on port 4317 until it is deployed again."
---

<!-- Source of delay_guide.pdf. The local dashboard is started with npm run dev in dashboard/cambaliza (port 4317). Build: python build.py delay (fills each [[id]] from steps_delay.json with the link,
     the settings as a sentence and the screenshot; screenshots: node shoot.mjs steps_delay.json img_delay with vite
     preview on 4173 and headless Chromium on 9333). The data of the section are written by
     scripts/export_pulse_delay_sweep_dashboard.py. No run-in labels or arrows anywhere in this file. -->

::: {.card .story}
::: sl
How
:::

## How to use this guide

- Each card is one slide of pulse_delay.pptx; its title and the bullets in the blue box are those of the deck, word
  for word.
- Each step says which tab to open, which controls to set and which point to click; all other controls stay at their
  defaults. The link Open in each step loads all of these settings at once.
- Where a result has a card on the tab Highlights, the step opens that card, and the dashboard brings the plot of the
  result into view.
- The section Delay between the pulses, against NA is at the bottom of the tab Pulse results. It has four charts. The
  first gives the peak 2CE fluorescence of the 350-nm pairs against Δt/τ, with one curve per NA and the temporal overlap
  as a dotted line. The second gives the position of that peak against Δt, with the position cΔt/2 where facing pulses
  meet. The third gives the peak at Δt = τ against NA for the circular pupil, the Gaussian input and two annular pupils.
  The fourth compares all photon pairs with the 350-nm pairs on a grid of delays 0.1 fs apart.
- Its controls are the angle, τ, the NAs drawn, and the NA and the polarization of the chart of all pairs. The data
  are those of the deck, 2CE in the vector model in air.
- The yellow box under the title of each slide states the main result of that slide. The yellow box under each
  screenshot states the main point of the step, and the text below it says what to point at. The blue box repeats the
  bullets of the slide.
:::

::: card
::: sl
3
:::

## Delay between the two pulses and their temporal overlap

::: say
At a fixed point the peak 2CE fluorescence of the 350-nm pairs decreases with the delay as the temporal overlap of the
two pulses: a delay of 0.40 τ reduces the peak by 20%, and a delay of τ by 75%.
:::

[[d03|3]]

::: main
With collinear lenses the peak 2CE fluorescence follows the temporal overlap at all NAs.
:::

::: look
Point at the chart of the peak against Δt/τ: the curves of the six NAs lie on the dotted temporal overlap,
exp(−2 ln2 (Δt/τ)²), which is 0.25 at Δt/τ = 1.
:::

::: deck

These are the bullets of slide 3.

- 2CE needs the two pulses at the same place and at the same time: Lim & Saloma (2003) note that achieving optimal temporal overlap of the 2CE pulses is crucial.
- At a fixed point, the 2CE of the 350-nm pairs decreases with the delay Δt as the overlap in time of two Gaussian pulses of width τ.

The line under the equation reads as follows.

> where F is the peak 2CE fluorescence, Δt the delay of the 656-nm pulse relative to the 750-nm pulse and τ the pulse width. A delay of 0.40 τ reduces the peak by 20%, a delay of 0.71 τ by one half and a delay of τ by 75%.

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

[[d04|4]]

::: main
At low NA the peak moves along the axis towards the position where the pulses meet.
:::

::: look
Point at the chart of the position of the peak against Δt and at the dashed line cΔt/2: the curve of NA 0.1 follows the
line, while the curves of higher NA stay near the focus.
:::

::: deck

These are the bullets of slide 4.

- With facing lenses, the delayed pulses meet at z~m~ = cΔt/2n, and 2CE forms over a stretch of length G = cτ/(√2 n) about that position.
- With D the continuous-beam depth of focus of 2CE, the peak 2CE fluorescence at a delay Δt follows from the product of the focus and this stretch.

The line under the equations reads as follows.

> where z~m~ is the position where the delayed pulses meet and G the length of the stretch over which they overlap. A long focus (D much larger than G) retains the peak, which moves with z~m~; a short focus holds the peak at the focus, where it decreases as the temporal overlap.

:::
:::

::: card
::: sl
5
:::

## Peak 2CE fluorescence and its position against the delay, θ = π

::: say
With facing lenses at low NA the peak 2CE fluorescence moves along the axis and is largely retained, while at NA 0.5 and
above it stays at the focus and decreases as the temporal overlap.
:::

[[d05a|5]]

::: main
At NA 0.1 and 100 fs, a delay of one pulse width reduces the peak by 7% and moves it 14 µm from the focus.
:::

::: look
Point at the curve of NA 0.1 on the chart of the position at Δt = 100 fs, and at the same NA on the chart of the peak
beside it, at Δt/τ = 1.
:::

[[d05b|5]]

::: main
At NA 0.5 and above the peak decreases as the temporal overlap; at NA 0.5 a delay of one pulse width reduces it by 74%.
:::

::: look
Point at the curves of NA 0.5, 0.7 and 0.9, which lie on the dotted temporal overlap.
:::

::: deck

These are the bullets of slide 5.

- With facing lenses at low NA, the delayed pulses still meet inside the long depth of focus, so the peak 2CE fluorescence moves along the axis and is largely retained: at NA 0.1 and 100 fs, a delay of one pulse width reduces the peak by 7%.
- At NA 0.5 and above, the peak stays at the focus and decreases as the temporal overlap of the two pulses (dotted line), by 74% at a delay of one pulse width.

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

[[d06a|6]]

::: main
At NA 0.3 and 100 fs the peak that remains at a delay of one pulse width is 0.32 for the circular pupil and 0.80 for the
annular pupil with ε = 0.9.
:::

::: look
Point at the green curve of the annular pupil with ε = 0.9, which stays high up to a larger NA than the others, and at
the dotted line of the temporal overlap, 0.25, which all curves reach at high NA.
:::

[[d06b|6]]

::: main
At 30 fs all pupils retain more of the peak than at 100 fs at the same NA.
:::

::: look
The curves move to lower NA as τ decreases, because the position where the pulses meet moves by a shorter distance.
:::

::: deck

These are the bullets of slide 6.

- As NA increases, the peak 2CE fluorescence that remains at a delay of one pulse width decreases to one quarter, the temporal overlap of the two pulses; shorter pulses retain more, because the position where they meet moves by a shorter distance (left).
- A Gaussian input and annular pupils, which give a longer depth of focus, retain more of the peak at the same NA (right).

:::
:::

::: card
::: sl
7
:::

## Peak 2CE fluorescence against the delay, τ = 5 fs, NA 0.5

::: say
With all photon pairs and phase-locked pulses the peak 2CE fluorescence oscillates with the delay, while the peak of the
350-nm pairs alone decreases smoothly as the temporal overlap.
:::

[[d07a|7]]

::: main
With collinear lenses at 5 fs the fringes are deep, with periods of 2.19, 2.50 and 1.17 fs.
:::

::: look
Point at the blue curve of all pairs, which swings about the red curve of the 350-nm pairs by up to 0.92 of the peak.
:::

[[d07b|7]]

::: main
With crossed lenses at NA 0.5 the fringes are shallower than with collinear lenses.
:::

::: look
Along x, the blue curve swings about the red one by about 0.4 of the peak.
:::

::: deck

These are the bullets of slide 7.

- With all photon pairs and phase-locked pulses, the peak 2CE fluorescence oscillates with the delay, with periods of 2.19, 2.50 and 1.17 fs, because the delay changes the phase of the 350-nm pairs relative to the 375- and 328-nm pairs.
- The 2CE of the 350-nm pairs alone decreases smoothly with the delay, as the temporal overlap of the two pulses.

:::
:::

::: card
::: sl
8
:::

## Peak 2CE fluorescence against the delay, τ = 10 fs, NA 0.5

::: say
At 10 fs the peak 2CE fluorescence with all photon pairs still oscillates with the delay, with the same periods as at
5 fs.
:::

[[d08|8]]

::: main
At 10 fs the fringes with collinear lenses still swing by about 0.7 of the peak.
:::

::: look
Point at the fringes of the blue curve near Δt = 0, which fade as the two pulses separate.
:::

::: deck

These are the bullets of slide 8.

- With all photon pairs and phase-locked pulses, the peak 2CE fluorescence oscillates with the delay, with periods of 2.19, 2.50 and 1.17 fs, because the delay changes the phase of the 350-nm pairs relative to the 375- and 328-nm pairs.
- The 2CE of the 350-nm pairs alone decreases smoothly with the delay, as the temporal overlap of the two pulses.

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

[[d09|9]]

::: main
At 20 fs the blue and red curves nearly coincide.
:::

::: look
The largest gap between the two curves is about 0.04 of the peak.
:::

::: deck

These are the bullets of slide 9.

- At 20 fs, the amplitude of the 375- and 328-nm pairs is below 1% of that of the 350-nm pairs, so the total 2CE follows the 2CE of the 350-nm pairs.
- The peak decreases smoothly with the delay, as the temporal overlap of the two pulses.

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

[[d10a|10]]

::: main
With crossed lenses at 5 fs and NA 0.3 the fringes are shallow, with a depth of about 0.2 of the peak.
:::

::: look
Point at the small swing of the blue curve about the red one.
:::

[[d10b|10]]

::: main
At NA 0.7 the same fringes swing by about 0.65 of the peak.
:::

::: look
Compare this swing with that of the previous step. A smaller focal spot holds fewer of the fringes in space, so the peak
follows them as the delay moves them.
:::

::: deck

These are the bullets of slide 10.

- With crossed and facing lenses, the fringes of the peak against the delay deepen as NA increases, because the delay moves the interference fringes in space across a smaller focal spot.
- With collinear lenses, the three kinds of photon pairs have no fringes in space, so the fringe depth is the same at all NAs: 0.92 at 5 fs and 0.71 at 10 fs.

:::
:::

::: card
::: sl
11
:::

## Peak 2CE fluorescence against the delay for two polarizations

::: say
With crossed lenses and the polarization in the plane of the two lens axes, the fields of the two beams are
perpendicular at the focus, so the fringes against the delay are about a quarter as deep.
:::

[[d11a|11]]

::: main
With the polarization in the plane of the lens axes the fringes are shallow, with an amplitude of about 0.05.
:::

::: look
Point at the blue curve of all pairs. Both curves are divided by the value of all pairs at no delay, so the red curve of
the 350-nm pairs starts below 1.
:::

[[d11b|11]]

::: main
With the polarization perpendicular to that plane the amplitude is about 0.21.
:::

::: look
Switch the polarization control between the two settings to compare the depth of the fringes; each curve is then
divided by its own value at no delay.
:::

::: deck

These are the bullets of slide 11.

- With the polarization in the plane of the two lens axes, the fields of the two beams are perpendicular at the focus, so the three kinds of photon pairs fall in different field components and interfere less.
- The fringes against the delay are then about a quarter as deep, while the 2CE of the 350-nm pairs decreases with the delay in the same way for both polarizations.

:::
:::
