---
title: "Dashboard guide for the deck on the delay between the pulses"
subtitle: "This guide pairs pulse_delay.pptx with the section Delay between the pulses, against NA of the tab Pulse results, slide by slide. The links open the local dashboard (npm run dev in dashboard/cambaliza, port 4317) until it is deployed again."
---

<!-- Source of delay_guide.pdf. Build: python build.py delay (fills each [[id]] from steps_delay.json with the link,
     the settings as a sentence and the screenshot; screenshots: node shoot.mjs steps_delay.json img_delay with vite
     preview on 4173 and headless Chromium on 9333). The data of the section are written by
     scripts/export_pulse_delay_sweep_dashboard.py. No run-in labels or arrows anywhere in this file. -->

::: {.card .story}
::: sl
How
:::

## How to use this guide

- Each step says which tab to open, which controls to set and which point to click; all other controls stay at their
  defaults. The button Open ↗ loads all of these settings at once.
- Where a result has a card on the tab Highlights, the step opens that card, and the dashboard brings the plot of the
  result into view.
- The section Delay between the pulses, against NA is at the bottom of the tab Pulse results. It has four charts: the
  2CE peak of the 350-nm pairs against Δt/τ with one curve per NA and the temporal overlap dotted; the position of that
  peak against Δt with the meeting point cΔt/2 for facing lenses; the peak at Δt = τ against NA for the circular pupil,
  the Gaussian input and two annular pupils; and all pairs against the 350-nm pairs on the grid of 0.1 fs.
- Its controls are the angle, τ, the NAs drawn, and the NA and the polarization of the chart of all pairs. The data
  are those of the deck: the vector model in air, 2CE.
- The yellow box under the title of each slide states the main result of that slide. The yellow box under each
  screenshot states the main point of the step, and the text below it says what to point at. The blue box repeats the
  bullets of the slide.
:::

::: card
::: sl
3
:::

## Delay and temporal overlap

::: say
At a fixed point the 350-nm pairs fall with the overlap of the two pulses, to one quarter at Δt = τ.
:::

::: step
[Slide 3]{.slide} [Step 1]{.num} [Open ↗](http://localhost:4317/#mode=psum&xth=0&xtau=100){.open} Open the tab “Pulse results”, set the angle for the delay against NA to θ = 0 and set τ for the delay against NA to 100 fs; the other controls stay at their defaults.

![](img_delay/d03.jpg)
:::

::: main
With collinear lenses the peak follows the temporal overlap at all NAs.
:::

::: look
Point at the chart of the peak against Δt/τ: the curves of all six NAs lie on the dotted temporal overlap,
exp(−2 ln2 (Δt/τ)²), which is 0.25 at Δt/τ = 1.
:::

::: deck

These are the bullets of slide 3, "Delay and temporal overlap".

- Lim & Saloma (2003) note that 2CE needs the two pulses at the same place and time.
- At a fixed point, the 350-nm pairs fall with the overlap of two Gaussian pulses of width τ.

:::
:::

::: card
::: sl
4
:::

## Facing lenses: where the pulses meet

::: say
With facing lenses the delayed pulses meet at z~m~ = cΔt/2n, and the 2CE forms about that point.
:::

::: step
[Slide 4]{.slide} [Step 2]{.num} [Open ↗](http://localhost:4317/#mode=psum&xth=180&xtau=100){.open} Open the tab “Pulse results”, set the angle for the delay against NA to θ = π and set τ for the delay against NA to 100 fs; the other controls stay at their defaults.

![](img_delay/d04.jpg)
:::

::: main
At low NA the peak moves along the axis towards the meeting point of the pulses.
:::

::: look
Point at the position of the peak against Δt and at the dashed line cΔt/2: the curve of NA 0.1 follows the line, and
those of higher NA stay near the focus.
:::

::: deck

These are the bullets of slide 4, "Facing lenses: where the pulses meet".

- The delayed pulses meet at z~m~, and the 2CE forms over a stretch of length G about it.

:::
:::

::: card
::: sl
5
:::

## 2CE peak and position against the delay, θ = π, 100 fs

::: say
At low NA the 2CE peak moves along the axis and is kept; at NA 0.5 and above it stays at the focus and falls with the
temporal overlap.
:::

::: step
[Slide 5]{.slide} [Step 3]{.num} [Open ↗](http://localhost:4317/#mode=psum&xth=180&xtau=100&xnas=10.20.30.50.70.90&hl=delay-facing-lowna){.open} Open the tab “Highlights” and click the card that begins “With facing lenses at low NA, the”. It opens the tab “Pulse results”, sets the angle for the delay against NA to θ = π, sets τ for the delay against NA to 100 fs and draws NA 0.1, NA 0.2, NA 0.3, NA 0.5, NA 0.7 and NA 0.9 against the delay, and brings the plot of the result into view.

![](img_delay/d05a.jpg)
:::

::: main
At NA 0.1 and 100 fs the peak at Δt = τ is 0.93 of the peak without delay, 14 µm from the focus.
:::

::: look
Point at the curve of NA 0.1 on the chart of the position at Δt = 100 fs, and at the same NA on the chart of the peak
beside it, at Δt/τ = 1.
:::

::: step
[Slide 5]{.slide} [Step 4]{.num} [Open ↗](http://localhost:4317/#mode=psum&xth=180&xtau=100&xnas=50.70.90&hl=delay-facing-highna){.open} Open the tab “Highlights” and click the card that begins “With facing lenses at NA 0.5 and”. It opens the tab “Pulse results”, sets the angle for the delay against NA to θ = π, sets τ for the delay against NA to 100 fs and draws NA 0.5, NA 0.7 and NA 0.9 against the delay, and brings the plot of the result into view.

![](img_delay/d05b.jpg)
:::

::: main
At NA 0.5 and above the peak falls with the temporal overlap, to 0.26 at Δt = τ and NA 0.5.
:::

::: look
Point at the curves of NA 0.5, 0.7 and 0.9 on the dotted temporal overlap.
:::

::: deck

These are the bullets of slide 5, "2CE peak and position against the delay, θ = π, 100 fs".

- At low NA the pulses still meet inside the long focus, so the peak moves along the axis.
- At NA 0.5 and above, the peak stays at the focus and falls with the temporal overlap.

:::
:::

::: card
::: sl
6
:::

## 2CE peak at a delay of τ against NA, θ = π

::: say
Pupils with a longer depth of focus and shorter pulses keep more of the peak at Δt = τ.
:::

::: step
[Slide 6]{.slide} [Step 5]{.num} [Open ↗](http://localhost:4317/#mode=psum&xth=180&xtau=100&hl=delay-pupils){.open} Open the tab “Highlights” and click the card that begins “With facing lenses, pupils with a longer”. It opens the tab “Pulse results”, sets the angle for the delay against NA to θ = π and sets τ for the delay against NA to 100 fs, and brings the plot of the result into view.

![](img_delay/d06a.jpg)
:::

::: main
At NA 0.3 and 100 fs the peak at Δt = τ is 0.32 for the circular pupil and 0.80 for the annular pupil with ε = 0.9.
:::

::: look
Point at the green curve of the annular pupil with ε = 0.9, which stays high to a larger NA than the others, and at the
dotted line of the temporal overlap, 0.25, that all curves reach at high NA.
:::

::: step
[Slide 6]{.slide} [Step 6]{.num} [Open ↗](http://localhost:4317/#mode=psum&xth=180&xtau=30){.open} Open the tab “Pulse results”, set the angle for the delay against NA to θ = π and set τ for the delay against NA to 30 fs; the other controls stay at their defaults.

![](img_delay/d06b.jpg)
:::

::: main
At 30 fs all pupils keep more of the peak than at 100 fs at the same NA.
:::

::: look
The curves move to lower NA as τ decreases, because the meeting point moves a shorter distance.
:::

::: deck

These are the bullets of slide 6, "2CE peak at a delay of τ against NA, θ = π".

- Shorter pulses keep more of the peak, since they travel a shorter distance during the delay.
- Pupils with a longer depth of focus keep more of the peak at the same NA.

:::
:::

::: card
::: sl
7
:::

## 2CE peak against the delay, 5 fs, NA 0.5

::: say
Below 20 fs phase-locked pulses with all photon pairs give fringes against the delay, while the 350-nm pairs alone fall
smoothly.
:::

::: step
[Slide 7]{.slide} [Step 7]{.num} [Open ↗](http://localhost:4317/#mode=psum&xth=0&xtau=5&xna=0.5&xpol=s&hl=delay-fringes){.open} Open the tab “Highlights” and click the card that begins “Below 20 fs, phase-locked pulses with all”. It opens the tab “Pulse results”, sets the angle for the delay against NA to θ = 0, sets τ for the delay against NA to 5 fs, sets the NA of the chart of all pairs to 0.5 and sets the polarization of the chart of all pairs to perpendicular to the plane of the lens axes, and brings the plot of the result into view.

![](img_delay/d07a.jpg)
:::

::: main
With collinear lenses at 5 fs the fringes are deep, with periods of 2.19, 2.50 and 1.17 fs.
:::

::: look
Point at the blue curve of all pairs, which swings about the red curve of the 350-nm pairs by up to 0.92 of the peak.
:::

::: step
[Slide 7]{.slide} [Step 8]{.num} [Open ↗](http://localhost:4317/#mode=psum&xth=90&xtau=5&xna=0.5){.open} Open the tab “Pulse results”, set the angle for the delay against NA to θ = π/2, set τ for the delay against NA to 5 fs and set the NA of the chart of all pairs to 0.5; the other controls stay at their defaults.

![](img_delay/d07b.jpg)
:::

::: main
With crossed lenses the fringes are shallower at NA 0.5.
:::

::: look
The swing of the blue curve about the red one is about 0.4 of the peak along x.
:::

::: deck

These are the bullets of slide 7, "2CE peak against the delay, 5 fs, NA 0.5".

- Phase-locked pulses with all pairs give fringes one optical period (2.2 to 2.5 fs) apart.
- The 350-nm pairs alone fall smoothly; with facing lenses the two curves nearly coincide.

:::
:::

::: card
::: sl
8–9
:::

## 2CE peak against the delay, 10 and 20 fs, NA 0.5

::: say
The fringes become shallower as the pulses lengthen, and at 20 fs all pairs follow the 350-nm pairs.
:::

::: step
[Slide 8]{.slide} [Step 9]{.num} [Open ↗](http://localhost:4317/#mode=psum&xth=0&xtau=10&xna=0.5){.open} Open the tab “Pulse results”, set the angle for the delay against NA to θ = 0, set τ for the delay against NA to 10 fs and set the NA of the chart of all pairs to 0.5; the other controls stay at their defaults.

![](img_delay/d08.jpg)
:::

::: main
At 10 fs the fringes with collinear lenses still swing by about 0.7 of the peak.
:::

::: look
Point at the fringes of the blue curve near Δt = 0, which fade as the two pulses separate.
:::

::: step
[Slide 9]{.slide} [Step 10]{.num} [Open ↗](http://localhost:4317/#mode=psum&xth=0&xtau=20&xna=0.5){.open} Open the tab “Pulse results”, set the angle for the delay against NA to θ = 0, set τ for the delay against NA to 20 fs and set the NA of the chart of all pairs to 0.5; the other controls stay at their defaults.

![](img_delay/d09.jpg)
:::

::: main
At 20 fs the blue and red curves nearly coincide.
:::

::: look
The largest gap between them is about 0.04 of the peak.
:::

::: deck

These are the bullets of slides 8 and 9.

- Phase-locked pulses with all pairs give fringes one optical period (2.2 to 2.5 fs) apart.
- At 20 fs the fringes are shallow, and all pairs follow the 350-nm pairs.
- The 350-nm pairs alone fall smoothly; with facing lenses the two curves nearly coincide.

:::
:::

::: card
::: sl
10
:::

## Fringe depth against NA, 5 to 20 fs

::: say
With crossed and facing lenses the fringes against the delay deepen with NA.
:::

::: step
[Slide 10]{.slide} [Step 11]{.num} [Open ↗](http://localhost:4317/#mode=psum&xth=90&xtau=5&xna=0.3){.open} Open the tab “Pulse results”, set the angle for the delay against NA to θ = π/2, set τ for the delay against NA to 5 fs and set the NA of the chart of all pairs to 0.3; the other controls stay at their defaults.

![](img_delay/d10a.jpg)
:::

::: main
With crossed lenses at 5 fs and NA 0.3 the fringes are shallow, about 0.2 of the peak.
:::

::: look
Point at the small swing of the blue curve about the red one.
:::

::: step
[Slide 10]{.slide} [Step 12]{.num} [Open ↗](http://localhost:4317/#mode=psum&xth=90&xtau=5&xna=0.7){.open} Open the tab “Pulse results”, set the angle for the delay against NA to θ = π/2, set τ for the delay against NA to 5 fs and set the NA of the chart of all pairs to 0.7; the other controls stay at their defaults.

![](img_delay/d10b.jpg)
:::

::: main
At NA 0.7 the same fringes swing by about 0.65 of the peak.
:::

::: look
Compare the swing with that of the previous step: a smaller spot holds fewer of the fringes in space, so the peak
follows them.
:::

::: deck

These are the bullets of slide 10, "Fringe depth against NA, 5 to 20 fs".

- With crossed and facing lenses the fringes deepen with NA, as they cross a smaller spot.
- With collinear lenses the fringes stay fixed in space, so their depth is the same at any NA.

:::
:::

::: card
::: sl
11
:::

## 2CE peak against the delay, two polarizations, θ = π/2

::: say
With crossed lenses and the polarization in the plane of the lens axes, the fringes against the delay are about a
quarter as deep.
:::

::: step
[Slide 11]{.slide} [Step 13]{.num} [Open ↗](http://localhost:4317/#mode=psum&xth=90&xtau=5&xna=0.5&xpol=p&hl=delay-polarization){.open} Open the tab “Highlights” and click the card that begins “With crossed lenses and the polarization in”. It opens the tab “Pulse results”, sets the angle for the delay against NA to θ = π/2, sets τ for the delay against NA to 5 fs, sets the NA of the chart of all pairs to 0.5 and sets the polarization of the chart of all pairs to in the plane of the lens axes, and brings the plot of the result into view.

![](img_delay/d11a.jpg)
:::

::: main
With the polarization in the plane of the lens axes the fringes are shallow, an amplitude of about 0.05.
:::

::: look
Point at the blue curve of all pairs; both curves are divided by all pairs at no delay, so the red curve of the 350-nm
pairs starts below 1.
:::

::: step
[Slide 11]{.slide} [Step 14]{.num} [Open ↗](http://localhost:4317/#mode=psum&xth=90&xtau=5&xna=0.5&xpol=s){.open} Open the tab “Pulse results”, set the angle for the delay against NA to θ = π/2, set τ for the delay against NA to 5 fs, set the NA of the chart of all pairs to 0.5 and set the polarization of the chart of all pairs to perpendicular to the plane of the lens axes; the other controls stay at their defaults.

![](img_delay/d11b.jpg)
:::

::: main
With the polarization perpendicular to that plane the amplitude is about 0.21.
:::

::: look
Switch the polarization control between the two settings to compare the depth of the fringes; each curve is now
divided by its own value at no delay.
:::

::: deck

These are the bullets of slide 11, "2CE peak against the delay, two polarizations, θ = π/2".

- Polarized in the plane of the lens axes, the beams have perpendicular fields at the focus.
- The fringes are then about a quarter as deep, and the 350-nm pairs fall in the same way.

:::
:::
