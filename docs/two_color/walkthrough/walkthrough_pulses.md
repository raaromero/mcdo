---
title: "Dashboard walkthrough for the pulse results"
subtitle: "This guide pairs pulse_results.pptx with the dashboard, slide by slide. The links open the local dashboard (npm run dev in dashboard/cambaliza, port 4317) until it is deployed again."
---

<!-- Source of pulse_walkthrough.pdf. Build: python build.py pulses (fills each [[id]] from steps_pulses.json with the
     link, the settings as a sentence and the screenshot; screenshots: node shoot.mjs steps_pulses.json img_pulses with
     vite preview on 4173 and headless Chromium on 9333). Numbers were read off the dashboard when the screenshots were
     taken. No run-in labels, arrows or "·" anywhere in this file. -->

::: {.card .story}
::: sl
How
:::

## How to use this guide

- Each step says which tab to open, which controls to set and which point to click; every other control stays at its
  default. The button Open ↗ loads all of these settings at once.
- The box under the title of each slide states the main result of that slide. The yellow box under each screenshot
  states the main point of the step, and the text below it says what to point at.
- The blue box repeats the bullets of the slide that the step belongs to. The green box gives the continuous-beam result
  of Cambaliza & Saloma (2000) that the slide is compared with.
- Each card first shows the view that matches the slide. The steps after "Beyond the slide" change one setting at a
  time, such as τ, the angle or the NA, so that each difference can be seen on its own.
- The tab "Pulses in time" computes one run in the browser for any angle, pulse length, delay, NA from 0.3 to 0.5, and
  air or water. Its time slider and the button Play step through the run, and the button Load the video shows the
  rendered video where one exists.
- The tab "Pulse results" shows the precomputed results at NA 0.5: the widths against τ for the three angles, the x–z
  maps at the picked τ, and the delay. Clicking a point on a width chart or a delay chart picks that τ or N for the
  whole tab, and clicking a legend entry hides that line.
- Slides 3, 7 and 8, the continuous-beam results of Cambaliza & Saloma (2000), the model and its assumptions, are
  hidden in the deck and can be shown if they are asked for.
:::

::: {.paper .summary}

- With circular pupils, the sharpest 2PE and 2CE profiles are obtained with crossed lenses (θ = π/2). 2PE has the
  narrower depth of focus and FWHM, but stronger side lobes.
- With annular pupils, the 2CE profile along the axis at θ = π/2 has a higher contrast and weaker side lobes than the
  2PE one.
- The main advantage of 2CE is in observing objects through highly scattering media. 2CE needs both beams to overlap
  in space and time, so it produces no strong fluorescence background far from the focus.

:::

::: {.deck .summary}

These are the bullets of the summary slide, slide 19.

- At 100 fs, pulsed 2CE is the same as with continuous beams.
- With facing lenses, pulsed 2CE forms only where the pulses meet, so its depth of focus is shorter than with
  continuous beams, more so at lower NA; 2PE shortens less.
- With collinear and crossed lenses, pulsed 2CE keeps the continuous-beam depth of focus and spot to within a few percent.
- Below about 15 fs one beam alone also excites the 350-nm level, so 2CE carries fringes and starts to lose its weak
  background.
- With facing lenses, a delay between the pulses moves the 2CE along the axis and weakens it.
- The results assume phase-locked, transform-limited pulses, a narrow 350-nm level and the paraxial model at NA ≤ 0.5.

:::

::: {.part}
# Part 1. Pulses and the lens arrangements (slides 4 to 6)
:::

::: card
::: sl
4
:::

## A pulse in time

::: say
A pulse contains its whole spectrum at once, and its frequencies add up only near t = 0.
:::

::: step
[Slide 4]{.slide} [Step 1]{.num} [Open ↗](http://localhost:4317/#mode=ptime){.open} Open the tab “Pulses in time” with every control at its default.

![](img_pulses/p04a.jpg)
:::

::: main
The two spectra of a pair of 10-fs pulses are Gaussians about 400 THz (750 nm) and 457 THz (656 nm).
:::

::: look
Point at the bottom chart, "Spectrum arriving at the focus now", at t = 0. The dashed curves are the full spectra, the
solid curves are the part arriving at the focus at this instant, and the blue vertical line marks 428 THz (700 nm).

When you press Play, the solid curves rise as each pulse arrives at the focus and fall as it leaves, while their shape
stays the same, because all the frequencies arrive together.
:::

::: deck

These are the bullets of slide 4, "A pulse in time".

- The optical spectrum of a short pulse is a Gaussian in frequency about the carrier frequency (a), and each frequency
  is a continuous wave (b).
- At t = 0 all the frequencies are at their maximum and add up; at other times they cancel, so their sum is a short
  pulse (c).

:::

::: beyond
Beyond the slide
:::

::: step
[Slide 4, beyond the slide]{.slide} [Step 2]{.num} [Open ↗](http://localhost:4317/#mode=ptime&qtau=100){.open} Open the tab “Pulses in time”, set the pulse length τ to 100 fs; the other controls stay at their defaults.

![](img_pulses/p04b.jpg)
:::

::: main
A 100-fs pulse has a spectrum ten times narrower than a 10-fs pulse.
:::

::: look
The two spectra become narrow lines at 400 and 457 THz, far from 428 THz.
:::
:::

::: card
::: sl
5
:::

## Pulse length and spectral width

::: say
A shorter pulse has a wider spectrum, and below about 15 fs the spectra reach 700 nm.
:::

::: step
[Slide 5]{.slide} [Step 3]{.num} [Open ↗](http://localhost:4317/#mode=ptime&qtau=20){.open} Open the tab “Pulses in time”, set the pulse length τ to 20 fs; the other controls stay at their defaults.

![](img_pulses/p05a.jpg)
:::

::: main
At 20 fs the spectra barely reach 700 nm, so two photons of one pulse hardly reach 350 nm.
:::

::: look
In the spectrum chart the two spectra are half as wide as at 10 fs, 22 THz against 44 THz, and they fall almost to zero
at the line at 428 THz.
:::

::: deck

These are the bullets of slide 5, "Pulse length and spectral width".

- A transform-limited Gaussian pulse is Gaussian in time and in frequency, and its spectral width is 0.441/τ.
- Below about 15 fs the spectra reach 700 nm, where two photons of one pulse add up to 350 nm.

:::

::: beyond
Beyond the slide
:::

::: step
[Slide 5, beyond the slide]{.slide} [Step 4]{.num} [Open ↗](http://localhost:4317/#mode=ptime&qtau=5){.open} Open the tab “Pulses in time”, set the pulse length τ to 5 fs; the other controls stay at their defaults.

![](img_pulses/p05b.jpg)
:::

::: main
At 5 fs the two spectra overlap strongly at 700 nm.
:::

::: look
In the spectrum chart both spectra cross the line at 428 THz well above a third of their peak.
:::
:::

::: card
::: sl
6
:::

## Collinear, crossed and facing lenses

::: say
These are the three lens arrangements, with both beams polarized the same way at every angle.
:::

::: step
[Slide 6]{.slide} [Step 5]{.num} [Open ↗](http://localhost:4317/#mode=ptime&qth=0){.open} Open the tab “Pulses in time”, set the angle θ to 0°; the other controls stay at their defaults.

![](img_pulses/p06a.jpg)
:::

::: main
With collinear lenses the two pulses travel together along z.
:::

::: look
In the top row, the maps of I₁ and I₂ at t = 0 show both pulses on the focus, travelling in the same direction.
:::

::: step
[Slide 6]{.slide} [Step 6]{.num} [Open ↗](http://localhost:4317/#mode=ptime&qth=90){.open} Open the tab “Pulses in time”, set the angle θ to 90°; the other controls stay at their defaults.

![](img_pulses/p06b.jpg)
:::

::: main
With crossed lenses pulse 2 crosses the axis of L1 sideways.
:::

::: look
In the maps, I₂ is focused along x and I₁ along z, and I₁·I₂ is the small region where the two cross.
:::

::: step
[Slide 6]{.slide} [Step 7]{.num} [Open ↗](http://localhost:4317/#mode=ptime){.open} Open the tab “Pulses in time” with every control at its default.

![](img_pulses/p06c.jpg)
:::

::: main
With facing lenses the two pulses travel towards each other along z.
:::

::: look
The maps at t = 0 show the two pulses meeting at the focus. Moving the time slider shows them approach and leave in
opposite directions.
:::

::: deck

These are the bullets of slide 6, "Collinear, crossed and facing lenses".

- Lens L2 is lens L1 rotated by θ about the common focus O; L1 focuses 750 nm and L2 656 nm (700 nm in both for 2PE).
- Both beams are linearly polarized along y, perpendicular to the plane of the two lens axes, so their polarizations
  are parallel at every θ.

:::
:::

::: {.part}
# Part 2. Depth of focus against pulse length (slides 9 to 13)
:::

::: card
::: sl
9
:::

## 2CE with 100-fs pulses and with continuous beams

::: say
At 100 fs, pulsed 2CE is the same as with continuous beams.
:::

::: step
[Slide 9]{.slide} [Step 8]{.num} [Open ↗](http://localhost:4317/#mode=psum&rk=100){.open} Open the tab “Pulse results”, click τ = 100 fs on a width chart; the other controls stay at their defaults.

![](img_pulses/p09n.jpg)
:::

::: main
At 100 fs the map of the total 2CE is the same as the continuous-beam map.
:::

::: look
In the top row, compare the continuous-beam map on the left with the total 2CE of 100-fs pulses beside it; the profile
across the axis on the right shows the two on top of each other. In the width charts below, the points at 100 fs lie
on the dashed lines of the continuous beams for all three angles.
:::

::: deck

These are the bullets of slide 9, "2CE with 100-fs pulses and with continuous beams".

- At 100 fs, pulsed 2CE is the same as with continuous beams at all three lens angles, so the continuous-beam results
  of Cambaliza & Saloma (2000) hold for pulses of that length.

:::
:::

::: card
::: sl
10
:::

## Depth of focus, facing lenses

::: say
With facing lenses, pulses shorten the 2CE depth of focus, more at lower NA, and 2PE shortens less.
:::

::: step
[Slide 10]{.slide} [Step 9]{.num} [Open ↗](http://localhost:4317/#mode=psum){.open} Open the tab “Pulse results” with every control at its default.

![](img_pulses/p09a.jpg)
:::

::: main
The 2CE depth of focus with facing lenses falls from 3.56 µm with continuous beams to 2.82 µm at 20 fs and 2.14 µm at
10 fs.
:::

::: look
Point at the third width chart, "2CE width along the axis, θ = π". The orange curve, measured through the fringe
crests, falls below the dashed line of the continuous beams as τ shortens. The red curve is the central fringe alone,
which narrows sharply below 15 fs because of the fringes.
:::

::: step
[Slide 10]{.slide} [Step 10]{.num} [Open ↗](http://localhost:4317/#mode=psum&rsig=2PE){.open} Open the tab “Pulse results”, set the signal to 2PE; the other controls stay at their defaults.

![](img_pulses/p09b.jpg)
:::

::: main
The 2PE depth of focus falls less, to 3.14 µm at 20 fs and 2.47 µm at 10 fs.
:::

::: look
In the same chart for 2PE, the orange curve stays closer to the dashed line than it does for 2CE.
:::

::: paper

With circular pupils and continuous beams, 2CE offers no definite advantage in resolution over 2PE. At θ = π the two
have the same depth of focus through the fringe crests.

:::

::: deck

These are the bullets of slide 10, "Depth of focus, facing lenses".

- With facing lenses, pulsed 2CE forms only where the two pulses meet, so its depth of focus is shorter than with
  continuous beams.
- The shortening is larger at lower NA, because the continuous-beam focus grows while the stretch where the pulses meet
  stays the same.
- 2PE shortens less, because pairs of photons from one pulse need no overlap.

:::

::: beyond
Beyond the slide
:::

::: step
[Slide 10, beyond the slide]{.slide} [Step 11]{.num} [Open ↗](http://localhost:4317/#mode=ptime&qna=0.3&qtau=20){.open} Open the tab “Pulses in time”, set the NA to 0.3 and set the pulse length τ to 20 fs; the other controls stay at their defaults.

![](img_pulses/p09c.jpg)
:::

::: main
At NA 0.3 the continuous-beam focus is almost three times longer, so 20-fs pulses cut off a larger part of it.
:::

::: look
The line of text under the charts gives the FWHM of the total along the axis, 3.98 µm, against 9.89 µm for continuous
beams. At 20 fs the fringes are weak, so this FWHM is the depth of focus of the slide, 0.40 of the continuous-beam
value.
:::
:::

::: card
::: sl
11–12
:::

## Why the facing pulses shorten the 2CE

::: say
The pulses overlap in time only near the focus, which is why the 2CE gets shorter. At 100 fs they overlap over the whole focus, and at 10 fs only near it.
:::

::: step
[Slide 11]{.slide} [Step 12]{.num} [Open ↗](http://localhost:4317/#mode=ptime&qtau=20){.open} Open the tab “Pulses in time”, set the pulse length τ to 20 fs; the other controls stay at their defaults.

![](img_pulses/p11n.jpg)
:::

::: main
At 20 fs the total 2CE along the axis is shorter than the continuous-beam profile, as the overlap of the pulses predicts.
:::

::: look
In the chart "2CE along the axis, accumulated up to t", the grey total lies inside the dashed continuous beams. The line
of text below the charts gives its FWHM, 2.78 µm against 3.56 µm. Moving the time slider shows I₁·I₂ appearing only
while the pulses are near the focus together.
:::

::: step
[Slide 12]{.slide} [Step 13]{.num} [Open ↗](http://localhost:4317/#mode=ptime&qtau=100){.open} Open the tab “Pulses in time”, set the pulse length τ to 100 fs; the other controls stay at their defaults.

![](img_pulses/p12n.jpg)
:::

::: main
At 100 fs the pulses overlap over the whole focus, so the total 2CE follows the continuous beams.
:::

::: look
In the same chart at 100 fs, the grey total lies on the dashed continuous beams. The video of slide 12 shows these two
runs side by side.
:::

::: deck

These are the bullets of slides 14 and 15.

- Pulse 1 passes a point z at t = z/c and pulse 2 at t = −z/c, so their intensities overlap in time only over a
  stretch of cτ/√2 about the focus, 4.2 µm at 20 fs (slide 11).
- The pulsed 2CE is the continuous-beam profile times this overlap: at 20 fs the product gives 2.74 µm and the full
  calculation 2.78 µm (slide 11).
- At 100 fs the pulses overlap over the whole focus and the 2CE follows the continuous beams; at 10 fs they overlap
  only near the focus (slide 12, video).

:::
:::

::: card
::: sl
13
:::

## Depth of focus, collinear and crossed lenses

::: say
Collinear and crossed lenses keep their depth of focus to within a few percent.
:::

::: step
[Slide 13]{.slide} [Step 14]{.num} [Open ↗](http://localhost:4317/#mode=psum){.open} Open the tab “Pulse results” with every control at its default.

![](img_pulses/p10a.jpg)
:::

::: main
With collinear lenses the depth of focus stays at the continuous-beam value at every τ.
:::

::: look
In the first width chart, "2CE width along the axis, θ = 0", all the points lie on the dashed line.
:::

::: step
[Slide 13]{.slide} [Step 15]{.num} [Open ↗](http://localhost:4317/#mode=psum&rcut=x){.open} Open the tab “Pulse results”, set the direction to across; the other controls stay at their defaults.

![](img_pulses/p10b.jpg)
:::

::: main
With crossed lenses the width across the axis also stays at the continuous-beam value down to 20 fs.
:::

::: look
In the second width chart, "2CE width across, θ = π/2", the orange curve leaves the dashed line only below 15 fs, by
about 2% at 10 fs.
:::

::: paper

With circular pupils and continuous beams, the sharpest 2PE and 2CE profiles are obtained with crossed lenses
(θ = π/2).

:::

::: deck

These are the bullets of slide 13, "Depth of focus, collinear and crossed lenses".

- With collinear and crossed lenses, pulsed 2CE keeps the continuous-beam depth of focus and spot to within a few
  percent, because the pulses overlap over the whole focus.
- Crossed lenses therefore keep the sharpest profiles, as with continuous beams.

:::
:::

::: {.part}
# Part 3. 10-fs pulses with facing lenses (slides 14 to 18)
:::

::: card
::: sl
14–15
:::

## 2CE with 10-fs pulses, θ = π

::: say
At 10 fs the 2CE is shorter than with continuous beams and has fringes 350 nm apart. It builds up only where the pulses overlap.
:::

::: step
[Slide 14]{.slide} [Step 16]{.num} [Open ↗](http://localhost:4317/#mode=psum&rk=10){.open} Open the tab “Pulse results”, click τ = 10 fs on a width chart; the other controls stay at their defaults.

![](img_pulses/p11a.jpg)
:::

::: main
The x–z maps show the 2CE of continuous beams, the total 2CE of 10-fs pulses, and I₁·I₂ at the instant the pulse
centres meet.
:::

::: look
From left to right, the top row shows the continuous beams as one long spot, the total with 10-fs pulses as a shorter
spot with fringes along z, and I₁·I₂ at t ≈ 0 as a short spot without fringes. The chart on the right is the profile
across the axis at z = 0, which is the same for all three.
:::

::: step
[Slide 14]{.slide} [Step 17]{.num} [Open ↗](http://localhost:4317/#mode=psum&rk=10){.open} Open the tab “Pulse results”, click τ = 10 fs on a width chart; the other controls stay at their defaults.

![](img_pulses/p11b.jpg)
:::

::: main
Along the axis, the total 2CE carries fringes inside an envelope shorter than the continuous-beam profile.
:::

::: look
The chart "2CE along the axis, τ = 10 fs, θ = π" shows the continuous beams as a dashed line, the total in red and
I₁·I₂ at t = 0 in blue.
:::

::: deck

These are the bullets of slides 11 and 12.

- The total 2CE is shorter than with continuous beams and carries fringes 350 nm apart (slide 14).
- The two pulses pass through the focus; the 2CE builds up only where they overlap (slide 15, video).

:::

::: step
[Slide 15]{.slide} [Step 18]{.num} [Open ↗](http://localhost:4317/#mode=ptime&qvid=1){.open} Open the tab “Pulses in time”, press Load the video; the other controls stay at their defaults.

![](img_pulses/p12a.jpg)
:::

::: main
The video of slide 15 plays in the dashboard, and the button Play steps through the same run computed in the browser.
:::

::: look
The screenshot is a frame of the video, taken as the pulses meet at the focus. In the dashboard the video sits at the
top of the tab, and below it the maps and charts follow the time slider: I₁ and I₂ approach, I₁·I₂ appears only while
they overlap, and the 2CE accumulated up to t grows into the total.
:::

::: beyond
Beyond the slide
:::

::: step
[Slide 14, beyond the slide]{.slide} [Step 19]{.num} [Open ↗](http://localhost:4317/#mode=psum&rk=5){.open} Open the tab “Pulse results”, click τ = 5 fs on a width chart; the other controls stay at their defaults.

![](img_pulses/p11c.jpg)
:::

::: main
At 5 fs the 2CE is shorter still and its fringes are deeper.
:::

::: look
In the top row the total 2CE is a short stack of fringes, to be compared with the continuous-beam map on its left.
:::
:::

::: card
::: sl
16–17
:::

## 2PE with 10-fs pulses, θ = π

::: say
At 10 fs the 2PE keeps its fringes but is shorter than with continuous beams. Each pulse excites on its own.
:::

::: step
[Slide 16]{.slide} [Step 20]{.num} [Open ↗](http://localhost:4317/#mode=psum&rsig=2PE&rk=10){.open} Open the tab “Pulse results”, set the signal to 2PE and click τ = 10 fs on a width chart; the other controls stay at their defaults.

![](img_pulses/p13a.jpg)
:::

::: main
The 2PE maps keep the standing-wave fringes of continuous beams, inside a shorter envelope.
:::

::: look
The top row shows the continuous beams, the total 2PE with 10-fs pulses, and |E₁ + E₂|⁴ at t ≈ 0.
:::

::: step
[Slide 16]{.slide} [Step 21]{.num} [Open ↗](http://localhost:4317/#mode=psum&rsig=2PE&rk=10){.open} Open the tab “Pulse results”, set the signal to 2PE and click τ = 10 fs on a width chart; the other controls stay at their defaults.

![](img_pulses/p13b.jpg)
:::

::: main
Along the axis, the 2PE fringes fade beyond about 2 µm, where the pulses no longer overlap.
:::

::: look
In the chart "2PE along the axis, τ = 10 fs, θ = π", the red total follows the dashed continuous beams near the focus
and falls below them further out.
:::

::: step
[Slide 17]{.slide} [Step 22]{.num} [Open ↗](http://localhost:4317/#mode=ptime&qsig=2PE&qvid=1){.open} Open the tab “Pulses in time”, set the signal to 2PE and press Load the video; the other controls stay at their defaults.

![](img_pulses/p14a.jpg)
:::

::: main
In the 2PE video, each pulse excites on its own as it passes, and the fringes form where the two overlap.
:::

::: look
The screenshot is a frame of the video. The map of |E₁ + E₂|⁴ at that instant is present wherever either pulse is,
with fringes only while the two overlap.
:::

::: deck

These are the bullets of slides 16 and 17.

- The 2PE keeps its fringes 350 nm apart but is shorter than with continuous beams (slide 16).
- Each pulse excites alone as it passes; the fringes form where the two pulses overlap (slide 17, video).

:::
:::

::: card
::: sl
18
:::

## Signal added by the 375- and 328-nm pairs

::: say
Below about 15 fs one beam alone also excites the 350-nm level, which adds fringes and works against the weak background of 2CE.
:::

::: step
[Slide 18]{.slide} [Step 23]{.num} [Open ↗](http://localhost:4317/#mode=psum){.open} Open the tab “Pulse results” with every control at its default.

![](img_pulses/p15a.jpg)
:::

::: main
The 375- and 328-nm pairs add about 2% to the 2CE peak at 20 fs and 73% at 10 fs.
:::

::: look
Point at the charts "Signal added by the 375- and 328-nm pairs", on a log scale, and "Fringe depth (θ ≠ 0)". Both rise
below 15 fs, and the fringe depth is 0.02 at 20 fs, 0.57 at 10 fs and 0.96 at 5 fs.
:::

::: step
[Slide 18]{.slide} [Step 24]{.num} [Open ↗](http://localhost:4317/#mode=ptime){.open} Open the tab “Pulses in time” with every control at its default.

![](img_pulses/p15b.jpg)
:::

::: main
At the focus, the 375- and 328-nm pairs reach the 350-nm level through the edges of their spectra.
:::

::: look
In the chart "Pair sums at the focus", the red curve (375-nm pairs) and the blue curve (328-nm pairs) still have weight
at the vertical line at 350 nm, next to the purple curve of the 350-nm pairs (750 + 656 nm).
:::

::: paper

The main advantage of 2CE is in observing objects through highly scattering media. 2CE needs both beams to overlap in
space and time, so it produces no strong fluorescence background far from the focus.

:::

::: deck

These are the bullets of slide 18, "Signal added by the 375- and 328-nm pairs".

- Below about 15 fs the spectra reach 700 nm, so two photons of one pulse also excite the 350-nm level, through the
  375- and 328-nm pairs.
- Their amplitude interferes with that of the 350-nm pairs, which gives the fringes, and one beam alone now excites, so
  2CE starts to lose the weak background of continuous beams.

:::
:::

::: {.part}
# Part 4. Next steps and the backup (slides 20 to 23)
:::

::: card
::: sl
20
:::

## Next steps, high NA and the delay between the pulses

::: say
The next steps are high NA and the delay between the pulses. A delay moves the 2CE along the axis and weakens it.
:::

::: step
[Slide 20]{.slide} [Step 25]{.num} [Open ↗](http://localhost:4317/#mode=psum&rdt=20){.open} Open the tab “Pulse results”, set τ for the maps and delay to 20 fs; the other controls stay at their defaults.

![](img_pulses/p17a.jpg)
:::

::: main
At 20 fs the 2CE peak halves at a path difference of about 8 wavelengths, which is 19 fs.
:::

::: look
Point at the charts "Peak of the total 2CE against the delay", for 10, 20 and 100 fs, and "2CE centre along the axis
against the delay", where the dashed line is the meeting point Nλ₀/2. The centre follows the meeting point only within
the focus.
:::

::: step
[Slide 20]{.slide} [Step 26]{.num} [Open ↗](http://localhost:4317/#mode=psum&rsig=2PE&rdt=20){.open} Open the tab “Pulse results”, set the signal to 2PE and set τ for the maps and delay to 20 fs; the other controls stay at their defaults.

![](img_pulses/p17b.jpg)
:::

::: main
The 2PE peak levels off at a quarter, because the L1 + L1 and L2 + L2 pairs need no overlap.
:::

::: look
These are the same charts for 2PE.
:::

::: deck

These are the bullets of slide 20, "Next steps".

- Extend the pulse results to high NA with the vector (Richards–Wolf) focus, in air and water.
- Study the delay between the two pulses. With continuous beams the timing does not matter; with facing lenses a delay
  moves the 2CE along the axis, within the focus, and weakens it.

:::

::: beyond
Beyond the slide
:::

::: step
[Slide 20, beyond the slide]{.slide} [Step 27]{.num} [Open ↗](http://localhost:4317/#mode=ptime&qtau=20&qdel=8){.open} Open the tab “Pulses in time”, set the pulse length τ to 20 fs and set the delay of pulse 2 to 8 λ; the other controls stay at their defaults.

![](img_pulses/p17c.jpg)
:::

::: main
In the tab "Pulses in time", the delay slider moves the meeting point of the pulses live.
:::

::: look
With a delay of 8 λ (18.7 fs) at 20 fs, I₁·I₂ forms below the focus, towards L2, and the total 2CE, the grey curve
along the axis, is shifted the same way against the dashed continuous beams.
:::
:::

::: card
::: sl
22–23
:::

## Backup, the delay profiles and the three angles

::: say
As the delay grows the 2CE moves towards L2 and weakens. With collinear and crossed lenses it weakens faster.
:::

::: step
[Slide 22]{.slide} [Step 28]{.num} [Open ↗](http://localhost:4317/#mode=psum&rdt=20&rdn=8){.open} Open the tab “Pulse results”, set τ for the maps and delay to 20 fs and click N = 8 on a delay chart; the other controls stay at their defaults.

![](img_pulses/p19a.jpg)
:::

::: main
The x–z maps at N = 0 and N = 8 show the 2CE moving along the axis and weakening to 0.47 of its peak.
:::

::: look
The row of maps shows the total 2CE at N = 0 and at N = 8, and the chart beside them is the profile across the axis at
the z of the peak.
:::

::: step
[Slide 22]{.slide} [Step 29]{.num} [Open ↗](http://localhost:4317/#mode=psum&rdt=20&rdn=8){.open} Open the tab “Pulse results”, set τ for the maps and delay to 20 fs and click N = 8 on a delay chart; the other controls stay at their defaults.

![](img_pulses/p19b.jpg)
:::

::: main
Along the axis, the 2CE at N = 8 is centred at about 1.1 µm, while the pulses meet at 2.8 µm.
:::

::: look
The chart "Total 2CE along the axis, τ = 20 fs, N = 8" shows N = 0 as a dashed line and N = 8 in red. Clicking other
points on the delay charts shows N = 4 and N = 12.
:::

::: step
[Slide 23]{.slide} [Step 30]{.num} [Open ↗](http://localhost:4317/#mode=psum&rdth=0&rdt=20){.open} Open the tab “Pulse results”, set the angle for the maps and delay to θ = 0 and set τ for the maps and delay to 20 fs; the other controls stay at their defaults.

![](img_pulses/p20a.jpg)
:::

::: main
With collinear lenses the 2CE peak falls faster with the delay than with facing lenses.
:::

::: look
Compare the 20-fs curve of the chart "Peak of the total 2CE against the delay, θ = 0" with that of the previous step.
:::

::: step
[Slide 23]{.slide} [Step 31]{.num} [Open ↗](http://localhost:4317/#mode=psum&rdth=90&rdt=20){.open} Open the tab “Pulse results”, set the angle for the maps and delay to θ = π/2 and set τ for the maps and delay to 20 fs; the other controls stay at their defaults.

![](img_pulses/p20b.jpg)
:::

::: main
Crossed lenses give the same fall as collinear lenses.
:::

::: look
This is the same chart at θ = π/2.
:::

::: deck

These are the bullets of slides 22 and 23.

- As the delay grows the 2CE moves towards L2 and weakens, as the meeting point leaves the focus (slide 22).
- With collinear and crossed lenses a delay only weakens the 2CE, without moving it, and it falls faster than with
  facing lenses (slide 23).

:::
:::
