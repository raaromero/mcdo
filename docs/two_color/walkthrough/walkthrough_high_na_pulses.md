---
title: "Dashboard guide: two-color excitation at high NA and with optical pulses"
subtitle: "This guide pairs 2ce_high_na_pulses.pptx with the dashboard, slide by slide. The links open the local dashboard (npm run dev in dashboard/cambaliza, port 4317) until it is deployed again."
---

<!-- Source of high_na_pulses_guide.pdf. Build: python build.py high_na_pulses (fills each [[id]] from steps_high_na_pulses.json with the
     link, the settings as a sentence and the screenshot; screenshots: node shoot.mjs steps_high_na_pulses.json img_high_na_pulses with
     vite preview on 4173 and headless Chromium on 9333). Where a card of the tab Highlights shows the result, the step
     opens that card. The slides of Part 1 (Richards–Wolf focus of one beam) have no view in the dashboard, so their
     cards give the main result and what to say. No run-in labels or arrows anywhere in this file. -->

::: {.card .story}
::: sl
How
:::

## How to use this guide

- Each step says which tab to open, which controls to set and which point to click; all other controls stay at their
  defaults. The button Open ↗ loads all of these settings at once.
- Where a result has a card on the tab Highlights, the step opens that card. Its banner gives the result in one
  sentence, and the dashboard brings the plot of the result into view.
- The yellow box under the title of each slide states the main result of that slide. The yellow box under each
  screenshot states the main point of the step, and the text below it says what to point at. The blue box repeats the
  bullets of the slide.
- The slides of Part 1, the focus of one beam with the Richards–Wolf theory, have no view in the dashboard. Their cards
  give the main result and what to say. The same holds for the slides of Lim & Saloma (2002, 2003) in Part 2, the
  displacement and the aberration of L2.
:::

::: {.part}
# Part 1. The focus at high NA with the Richards–Wolf theory (slides 4 to 11)
:::

::: card
::: sl
4–5
:::

## Focus of a 1-fs pulse and Linfoot's criteria

::: say
The five figures of Romallosa, Bantang & Saloma (2003) are reproduced, and pulses shorter than about 2 fs change the
focus in the same way at all NAs.
:::

Say that a 1-fs pulse fills the zeros of the continuous-beam focus, and that the structural content along the axis is
1.058 against 1.057 in Romallosa et al. (2003). The criteria do not depend on NA because the Linfoot arrays are in
optical coordinates.

::: deck

These are the bullets of slides 4 and 5.

- A 1-fs pulse fills the zeros of the continuous-beam focus, as in Romallosa et al. (2003).
- The structural content along the axis is 1.058, against 1.057 in Romallosa et al. (2003).
- Fidelity and structural content do not depend on NA, as in Romallosa et al. (2003).
- Below about 2 fs the fidelity falls below 1 and the structural content rises above 1.

:::
:::

::: card
::: sl
6–7
:::

## Spot width against NA, and the focal spot at NA 0.3 and 0.9

::: say
As NA increases the vector spot widens along the polarization and its zeros fill, because of the longitudinal field
E~z~.
:::

Say that at NA 0.3 the vector and scalar spots have the same width to about 1% (3.27 against 3.23 optical units), and
that at NA 0.9 the vector spot is 14% wider along the polarization (3.62 against 3.19) with its first zero filled to
1e-2 of the peak. Across the polarization the vector spot keeps its zeros.

::: deck

These are the bullets of slides 6 and 7.

- As NA increases the vector spot becomes wider than the scalar Debye spot.
- The difference is the longitudinal field E~z~, which fills the zeros and widens the spot.
- At NA 0.3 the scalar and vector spots have the same width, to about 1%.
- At NA 0.9 the vector spot is wider along the polarization and its zeros fill, because of E~z~.

:::
:::

::: card
::: sl
8
:::

## Gaussian input against uniform input at high NA

::: say
A Gaussian input (α = 4) keeps the scalar theory accurate to a higher NA, because it gives less weight to the marginal
rays.
:::

Say that along the polarization the 1% and 5% points are NA 0.40 and 0.85 for α = 4, against 0.30 and 0.60 for
uniform input.

::: deck

These are the bullets of slide 8.

- A Gaussian input (α = 4) keeps the scalar theory accurate to a higher NA.
- It gives less weight to the marginal rays, which carry the longitudinal field.

:::
:::

::: card
::: sl
9–11
:::

## Annular pupils, with continuous beams and with few-cycle pulses

::: say
An annular pupil lengthens the focus and lowers the peak, and few-cycle pulses keep the longer focus down to 1 fs.
:::

Say that at ε = 0.99 the depth of focus over that of the full pupil is 50.13 at low NA against 50.25 from 1/(1 − ε²),
and 30.4 at sin α = 0.9. At NA 0.8 it is 44.35 with a continuous beam and 44.33 at 1 fs. Shorter pulses fill the zeros
between the transverse rings for both pupils.

::: deck

These are the bullets of slides 9 to 11.

- At low NA the depth of focus grows as 1/(1 − ε²); at high NA it grows less.
- The peak intensity falls as (1 − ε²)², the cost of the longer focus.
- The longer depth of focus of an annular pupil is kept with few-cycle pulses, down to 1 fs.
- The contrast of the transverse rings decreases with shorter pulses, for both pupils.
- This is the loss of focal quality of Romallosa et al. (2003), here with annular pupils.

:::
:::

::: {.part}
# Part 2. Two-color excitation with continuous beams (slides 13 to 28)
:::

::: card
::: sl
13
:::

## Two beams focused at an angle θ

::: say
2CE absorbs one photon of each color, so it forms where the two beams overlap.
:::

::: step
[Slide 13]{.slide} [Step 1]{.num} [Open ↗](http://localhost:4317/#mode=live){.open} Open the tab “Focal spot” with all controls at their defaults.

![](img_high_na_pulses/b13.jpg)
:::

::: main
The tab Focal spot computes the two foci and the 2CE and 2PE maps at any angle θ.
:::

::: look
Point at the setup drawing at the top, where L2 is L1 turned by θ about the focus, and move the angle slider from 0 to
180° to show the 2CE map change from a long focus to a small crossed region and back.
:::

::: deck

These are the bullets of slide 13, "Two beams focused at an angle θ".

- Lens L2 is lens L1 turned by θ about the focus O, with θ = 0, π/2 or π.
- 2CE absorbs one photon of each color, so the signal is the product of the two intensities.

:::
:::

::: card
::: sl
14–15
:::

## Transverse and axial 2CE profiles, NA 0.5 (Figs. 2b and 3b)

::: say
Current work lies on the published 2CE curves of Cambaliza & Saloma (2000).
:::

::: step
[Slide 14]{.slide} [Step 2]{.num} [Open ↗](http://localhost:4317/#mode=theta&wdir=x&pk=90){.open} Open the tab “Lens angle θ”, set the width to across (FWHM) and click θ = 90° on the left chart; the other controls stay at their defaults.

![](img_high_na_pulses/b14.jpg)
:::

::: main
With crossed lenses the 2CE spot is wider than with collinear and facing lenses.
:::

::: look
Point at the left chart, the width across the axis against θ, at θ = 90°, and at the published Fig. 2b below the view.
:::

::: step
[Slide 15]{.slide} [Step 3]{.num} [Open ↗](http://localhost:4317/#mode=theta&wdir=z&pk=90){.open} Open the tab “Lens angle θ”, set the width to along (DOF) and click θ = 90° on the left chart; the other controls stay at their defaults.

![](img_high_na_pulses/b15.jpg)
:::

::: main
With crossed lenses the 2CE depth of focus is shorter.
:::

::: look
The left chart now gives the width along the axis; the published Fig. 3b is below the view.
:::

::: deck

These are the bullets of slides 14 and 15.

- At θ = π/2 the 2CE spot is wider; at θ = 0 and π the profiles are identical.
- At θ = π/2 the 2CE depth of focus is shorter; at θ = 0 and π the profiles are identical.

:::
:::

::: card
::: sl
16–20
:::

## Displacement and aberration of L2 (Lim & Saloma 2002, 2003)

::: say
Displacing or aberrating the focus of L2 lowers the 2CE peak, and the tolerated displacement falls as about 1/NA across
the axis and 1/NA² along it.
:::

The dashboard has no view of these slides. Say that with facing lenses the fits of current work are −0.601 x~c~² + 0.888
across the axis and −0.027 z~c~² + 0.998 along it, and that the fitted exponents against NA are −0.99 and −2.04. Equal
aberration coefficients keep the peak at θ = 0 and opposite ones at θ = π.

::: deck

These are the bullets of slides 16 to 20.

- Displacing the focus of L2 lowers the 2CE peak, more slowly along the axis than across it.
- With crossed lenses the peak falls along z~c~, set by the length of the focus of L1.
- The 2CE peak is kept when the two coefficients are equal at θ = 0 and opposite at θ = π.
- The tolerated displacement falls as about 1/NA across the axis and 1/NA² along it.
- With crossed lenses both displacements fall as about 1/NA², along the length of a beam.

:::
:::

::: card
::: sl
21
:::

## Spot and depth of focus against NA: 2CE, θ = 0 and π

::: say
Along the axis the paraxial model gives too long a 2CE focus at high NA.
:::

::: step
[Slide 21]{.slide} [Step 4]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=width&sig=2CE&ths=0&axis=z&na=0.9&hl=cw-dof-collinear){.open} Open the tab “Highlights” and click the card that begins “With collinear lenses, as NA increases, the”. It opens the tab “Scalar vs vector at high NA”, sets the plot to width, sets the signal to 2CE, sets the angles to 0, sets the direction to along and picks NA 0.9 on the left chart.

![](img_high_na_pulses/b21.jpg)
:::

::: main
The 2CE depth of focus is 3.33 µm at NA 0.5 and 0.81 µm at NA 0.9 in the vector model.
:::

::: look
Point at the left chart, the depth of focus against NA on log axes: the dashed scalar curve lies above the solid vector
curve from about NA 0.4. The profiles at NA 0.9 are on the right.
:::

::: deck

These are the bullets of slide 21.

- As NA increases the paraxial depth of focus shrinks more slowly than the vector one.
- The scalar model gives a longer depth of focus, by 7% at NA 0.5 and 36% at NA 0.9.

:::
:::

::: card
::: sl
22
:::

## 2CE along the axis at NA 0.5 and 0.9, θ = 0 and π

::: say
At NA 0.9 the paraxial 2CE focus is 36% longer than the vector one, against 7% at NA 0.5.
:::

::: step
[Slide 22]{.slide} [Step 5]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=gap&sig=2CE&ths=0&axis=z&model=both&na=0.9&hl=cw-scalar-dof){.open} Open the tab “Highlights” and click the card that begins “At NA 0.9 the paraxial 2CE depth”. It opens the tab “Scalar vs vector at high NA”, sets the plot to scalar / vector, sets the signal to 2CE, sets the angles to 0, sets the direction to along, sets the model to both and picks NA 0.9 on the left chart, and brings the plot of the result into view.

![](img_high_na_pulses/b22.jpg)
:::

::: main
At NA 0.9 the paraxial 2CE depth of focus is 1.10 µm against 0.81 µm for the vector one.
:::

::: look
Point at the profile along the axis, where the legend gives the two depths of focus, and at the left chart, the scalar
over vector width minus 1, which reaches 36% at NA 0.9. Clicking NA 0.5 on the left chart gives 3.56 against 3.33 µm.
:::

::: deck

These are the bullets of slide 22.

- At NA 0.9 the paraxial 2CE focus is 36% longer than the vector one, and 7% at NA 0.5.

:::
:::

::: card
::: sl
23
:::

## Spot and depth of focus against NA: 2CE, θ = π/2

::: say
With crossed lenses both 2CE widths decrease as about 1/NA, and the paraxial model follows the vector one.
:::

::: step
[Slide 23]{.slide} [Step 6]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=width&sig=2CE&ths=0.pi2&axis=z&na=0.7&hl=cw-dof-crossed){.open} Open the tab “Highlights” and click the card that begins “With crossed lenses the depth of focus”. It opens the tab “Scalar vs vector at high NA”, sets the plot to width, sets the signal to 2CE, sets the angles to 0 and π/2, sets the direction to along and picks NA 0.7 on the left chart.

![](img_high_na_pulses/b23.jpg)
:::

::: main
The 2CE depth of focus is shorter with crossed lenses, 13 times at NA 0.2 and 3.4 times at NA 0.7.
:::

::: look
Point at the two curves of the left chart, θ = 0 above and θ = π/2 below, and at how the gap between them narrows as
NA increases.
:::

::: deck

These are the bullets of slide 23.

- As NA increases both 2CE widths decrease as about 1/NA, set by the spot of the other beam.
- The paraxial model follows the vector focus within 4% wherever crossed lenses fit.

:::
:::

::: card
::: sl
24
:::

## Paraxial over vector widths of 2CE against NA

::: say
The paraxial 2CE widths depart from the vector ones first along the axis.
:::

::: step
[Slide 24]{.slide} [Step 7]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=gap&sig=2CE&ths=0.pi2.pi&axis=z&na=0.9){.open} Open the tab “Scalar vs vector at high NA”, set the plot to scalar / vector, set the signal to 2CE, set the angles to 0, π/2 and π, set the direction to along and click NA 0.9 on the left chart; the other controls stay at their defaults.

![](img_high_na_pulses/b24.jpg)
:::

::: main
Along the axis the gap passes 5% at NA 0.43 in air with collinear and facing lenses, and stays within 4% with crossed
lenses.
:::

::: look
Point at the grey band of ±5% and at where the curves of θ = 0 and π leave it; the curve of θ = π/2 stays inside.
Switching the direction to across moves the 5% point to NA 0.86.
:::

::: deck

These are the bullets of slide 24.

- As NA increases the paraxial 2CE widths exceed the vector ones, first along the axis.
- The difference comes from the paraxial phase, not from the polarization.

:::
:::

::: card
::: sl
25–26
:::

## Linfoot's criteria against NA: 2CE

::: say
The structural content shows the paraxial error along the axis first, and with crossed lenses the two models stay
alike.
:::

::: step
[Slide 25]{.slide} [Step 8]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=C&sig=2CE&ths=0.pi&axis=z&na=0.7){.open} Open the tab “Scalar vs vector at high NA”, set the plot to Linfoot C, set the signal to 2CE, set the angles to 0 and π, set the direction to along and click NA 0.7 on the left chart; the other controls stay at their defaults.

![](img_high_na_pulses/b25.jpg)
:::

::: main
Along the axis with collinear and facing lenses, C falls below 0.95 from NA 0.44 in air.
:::

::: look
Point at the curve of C against NA and at where it crosses 0.95.
:::

::: step
[Slide 26]{.slide} [Step 9]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=F&sig=2CE&ths=pi2&axis=x&na=0.7){.open} Open the tab “Scalar vs vector at high NA”, set the plot to Linfoot F, set the signal to 2CE, set the angles to π/2, set the direction to across and click NA 0.7 on the left chart; the other controls stay at their defaults.

![](img_high_na_pulses/b26.jpg)
:::

::: main
With crossed lenses the fidelity F stays at 0.999 or above wherever the lenses fit.
:::

::: look
Point at the curve of F against NA, which ends at NA 0.71 in air.
:::

::: deck

These are the bullets of slides 25 and 26.

- The paraxial focus becomes longer and lower, so the structural content C falls first.
- Across the axis the fidelity F stays at 0.996 or above at all NA.
- With crossed lenses the paraxial and vector 2CE stay alike wherever the lenses fit.

:::
:::

::: card
::: sl
27
:::

## Annular pupils: depth of focus against NA, air

::: say
With an annular pupil the paraxial depth of focus departs sooner than with the circular one.
:::

::: step
[Slide 27]{.slide} [Step 10]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=width&sig=2CE&ths=0&axis=z&pupil=ann&na=0.9){.open} Open the tab “Scalar vs vector at high NA”, set the plot to width, set the signal to 2CE, set the angles to 0, set the direction to along, set the pupil to annular and click NA 0.9 on the left chart; the other controls stay at their defaults.

![](img_high_na_pulses/b27.jpg)
:::

::: main
The annular depth of focus is many times the circular one, and the scalar curve leaves the vector one at a lower NA.
:::

::: look
Point at the gap between the dashed scalar and the solid vector curve at NA 0.9, 55 against 25 µm on the slide.
:::

::: deck

These are the bullets of slide 27.

- As NA increases the paraxial annular depth of focus departs sooner than the circular one.
- A thin ring uses the edge of the pupil, where the paraxial phase error is largest.

:::
:::

::: card
::: sl
28
:::

## Crossed lenses above NA 0.71

::: say
Two lenses of the same NA fit at right angles up to NA 0.71 in air and 0.94 in water.
:::

::: step
[Slide 28]{.slide} [Step 11]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=width&sig=2CE&ths=pi2&axis=x&na=0.7){.open} Open the tab “Scalar vs vector at high NA”, set the plot to width, set the signal to 2CE, set the angles to π/2, set the direction to across and click NA 0.7 on the left chart; the other controls stay at their defaults.

![](img_high_na_pulses/b28.jpg)
:::

::: main
The curve of θ = π/2 ends at NA 0.71 in air, where the cones of the two lenses touch.
:::

::: look
Point at the end of the curve; switching the medium to water extends it to NA 0.94.
:::

::: deck

These are the bullets of slide 28.

- Two lenses of the same NA fit at right angles up to NA 0.71 in air, where the cones touch.
- In water the limit is NA 0.94; Cambaliza & Saloma (2000) note NA 0.7 on p. 34.

:::
:::

::: {.part}
# Part 3. Two-color excitation with optical pulses (slides 30 to 44)
:::

::: card
::: sl
30–31
:::

## Spectrum and waves of a 10-fs pulse, and the pulse in time

::: say
A pulse is a sum of continuous waves that are in phase near t = 0.
:::

::: step
[Slide 30]{.slide} [Step 12]{.num} [Open ↗](http://localhost:4317/#mode=ptime){.open} Open the tab “Pulses in time” with all controls at their defaults.

![](img_high_na_pulses/b30.jpg)
:::

::: main
The two spectra of a pair of 10-fs pulses are Gaussians about 400 THz (750 nm) and 457 THz (656 nm).
:::

::: look
Point at the chart "Spectrum arriving at the focus now": the dashed curves are the full spectra and the solid curves the
part arriving at the focus at this instant.
:::

::: step
[Slide 31]{.slide} [Step 13]{.num} [Open ↗](http://localhost:4317/#mode=ptime){.open} Open the tab “Pulses in time” with all controls at their defaults.

![](img_high_na_pulses/b31.jpg)
:::

::: main
The two pulses pass the focus as short packets of intensity.
:::

::: look
Point at the chart of I~1~ and I~2~ along the axis, and press Play to show the two pulses move through the focus.
:::

::: deck

These are the bullets of slides 30 and 31.

- A pulse is a sum of continuous waves, in phase at t = 0 and out of phase away from it.
- The sum of the waves falls off away from t = 0 as a Gaussian of width τ, which is the pulse.

:::
:::

::: card
::: sl
32–33
:::

## Pulse width and spectral bandwidth, and the spectra against wavelength

::: say
Shorter pulses have wider spectra, and below about 15 fs they reach 700 nm.
:::

::: step
[Slide 32]{.slide} [Step 14]{.num} [Open ↗](http://localhost:4317/#mode=ptime&qtau=20){.open} Open the tab “Pulses in time”, set the pulse width τ to 20 fs; the other controls stay at their defaults.

![](img_high_na_pulses/b32.jpg)
:::

::: main
At 20 fs the spectra barely reach 700 nm.
:::

::: look
In the spectrum chart the two spectra fall almost to zero at the line at 428 THz (700 nm).
:::

::: step
[Slide 33]{.slide} [Step 15]{.num} [Open ↗](http://localhost:4317/#mode=ptime&qtau=5){.open} Open the tab “Pulses in time”, set the pulse width τ to 5 fs; the other controls stay at their defaults.

![](img_high_na_pulses/b33.jpg)
:::

::: main
At 5 fs the two spectra overlap strongly at 700 nm.
:::

::: look
Both spectra cross the line at 428 THz well above a third of their peak.
:::

::: deck

These are the bullets of slides 32 and 33.

- A transform-limited Gaussian pulse of width τ has a spectral bandwidth Δν = 0.441/τ.
- Below about 15 fs the spectra reach 700 nm, where two photons of one pulse make 350 nm.

:::
:::

::: card
::: sl
34
:::

## Photon pairs at the 350-nm level

::: say
The excitation adds the amplitudes of all photon pairs that reach 350 nm, then squares the sum.
:::

::: step
[Slide 34]{.slide} [Step 16]{.num} [Open ↗](http://localhost:4317/#mode=ptime&qtau=10){.open} Open the tab “Pulses in time”, set the pulse width τ to 10 fs; the other controls stay at their defaults.

![](img_high_na_pulses/b34.jpg)
:::

::: main
At 10 fs the 375- and 328-nm pairs add a visible part to the 350-nm pairs.
:::

::: look
Point at the chart "Pair sums at the focus, accumulated up to t", where each kind of pair has its own curve.
:::

::: deck

These are the bullets of slide 34.

- The signal adds the amplitudes of all photon pairs that reach 350 nm, then squares the sum.
- The 350-nm pairs are 750 + 656 nm; the 375- and 328-nm pairs are 750 + 750 and 656 + 656 nm.

:::
:::

::: card
::: sl
35–36
:::

## 2CE at 100 fs and with continuous beams

::: say
At 100 fs pulsed 2CE is the same as with continuous beams at the three lens angles.
:::

::: step
[Slide 35]{.slide} [Step 17]{.num} [Open ↗](http://localhost:4317/#mode=psum&rk=100){.open} Open the tab “Pulse results”, click τ = 100 fs on a width chart; the other controls stay at their defaults.

![](img_high_na_pulses/b35.jpg)
:::

::: main
With facing lenses the 100-fs profile along the axis lies on the continuous-beam one.
:::

::: look
Point at the profile at τ = 100 fs: the red total and the dashed continuous-beam curve coincide (3.52 against 3.56 µm on
the slide).
:::

::: step
[Slide 36]{.slide} [Step 18]{.num} [Open ↗](http://localhost:4317/#mode=psum&rcut=x&rpth=90&rk=100){.open} Open the tab “Pulse results”, set the direction to across, set the profile at the picked τ to θ = π/2 and click τ = 100 fs on a width chart; the other controls stay at their defaults.

![](img_high_na_pulses/b36.jpg)
:::

::: main
With crossed lenses the 100-fs profile across the axis lies on the continuous-beam one.
:::

::: look
The red total and the dashed continuous-beam curve coincide across the axis.
:::

::: deck

These are the bullets of slides 35 and 36.

- At 100 fs, pulsed 2CE is the same as with continuous beams with collinear and facing lenses.
- At 100 fs, pulsed 2CE is the same as with continuous beams with crossed lenses.

:::
:::

::: card
::: sl
37
:::

## Depth of focus, collinear and crossed lenses

::: say
With collinear and crossed lenses the 2CE depth of focus stays within a few percent.
:::

::: step
[Slide 37]{.slide} [Step 19]{.num} [Open ↗](http://localhost:4317/#mode=psum){.open} Open the tab “Pulse results” with all controls at their defaults.

![](img_high_na_pulses/b37.jpg)
:::

::: main
With collinear lenses the width along the axis does not change with τ.
:::

::: look
Point at the three width charts against τ: with θ = 0 and π/2 the width through the fringe crests (orange) stays within a few percent of the
dashed continuous-beam line, while with θ = π it falls at short pulses.
:::

::: deck

These are the bullets of slide 37.

- With collinear and crossed lenses the 2CE depth of focus stays within a few percent.

:::
:::

::: card
::: sl
38–39
:::

## Depth of focus with facing lenses, and the overlap of the facing pulses

::: say
With facing lenses 2CE forms where the two pulses meet, so its depth of focus is shorter.
:::

::: step
[Slide 38]{.slide} [Step 20]{.num} [Open ↗](http://localhost:4317/#mode=psum&rcut=z&rpth=180&rk=20&hl=pulse-facing-dof){.open} Open the tab “Highlights” and click the card that begins “With facing lenses and pulses, 2CE forms”. It opens the tab “Pulse results”, sets the direction to along the axis, sets the profile at the picked τ to θ = π and picks τ = 20 fs on a width chart, and brings the plot of the result into view.

![](img_high_na_pulses/b38.jpg)
:::

::: main
At NA 0.5 the 2CE depth of focus is 3.56 µm for continuous beams and 2.81 µm at 20 fs (scalar model).
:::

::: look
Point at the width along the axis against τ at θ = π, and at the profile at 20 fs beside it.
:::

::: step
[Slide 39]{.slide} [Step 21]{.num} [Open ↗](http://localhost:4317/#mode=psum&rk=20){.open} Open the tab “Pulse results”, click τ = 20 fs on a width chart; the other controls stay at their defaults.

![](img_high_na_pulses/b39.jpg)
:::

::: main
At 20 fs the total 2CE along the axis is shorter than the continuous-beam profile.
:::

::: look
Point at the red total and the dashed continuous-beam curve; the overlap of the pulses, 4.2 µm wide at 20 fs, cuts the
focus to 2.78 µm with all pairs.
:::

::: deck

These are the bullets of slides 38 and 39.

- With facing lenses, 2CE forms where the pulses meet, so its depth of focus is shorter.
- It shortens more at lower NA, because the focus grows while that stretch stays the same.
- At 20 fs the facing pulses overlap over 4.2 µm, which cuts the 2CE focus to 2.78 µm.

:::
:::

::: card
::: sl
40
:::

## Signal added by the 375- and 328-nm pairs

::: say
Below about 15 fs one beam alone also excites the 350-nm level.
:::

::: step
[Slide 40]{.slide} [Step 22]{.num} [Open ↗](http://localhost:4317/#mode=psum){.open} Open the tab “Pulse results” with all controls at their defaults.

![](img_high_na_pulses/b40.jpg)
:::

::: main
The part added by the 375- and 328-nm pairs rises steeply below 15 fs.
:::

::: look
Point at the chart "Signal added by the 375- and 328-nm pairs" on its log axes: the total over the 350-nm pairs is 1.02
at 20 fs and 1.73 at 10 fs on the slide.
:::

::: deck

These are the bullets of slide 40.

- Below about 15 fs one beam alone also excites, through the 375- and 328-nm pairs.
- 2CE then carries fringes and starts to lose the weak background of continuous beams.

:::
:::

::: card
::: sl
41–42
:::

## Pulse width to match continuous beams against NA

::: say
With facing lenses the pulse width needed to match continuous beams grows as NA decreases.
:::

::: step
[Slide 41]{.slide} [Step 23]{.num} [Open ↗](http://localhost:4317/#mode=psum&rpth=180&nth=180&nm=diff&nset=rw_air&nx=tau&ny=diff&hl=pulse-facing-na){.open} Open the tab “Highlights” and click the card that begins “With facing lenses, the pulse width from”. It opens the tab “Pulse results”, sets the profile at the picked τ to θ = π, sets the angle for the plots against NA to θ = π, sets the measure of the pulse width against NA to largest difference, sets the model, medium and pupil of the plot of one measure against another to Richards–Wolf, air, sets its x axis to pulse width τ and sets its y axis to largest difference, and brings the plot of the result into view.

![](img_high_na_pulses/b41.jpg)
:::

::: main
With facing lenses it is about 25 fs at NA 0.9, 87 fs at NA 0.5 and 610 fs at NA 0.2.
:::

::: look
Point at the chart of the pulse width against NA, with air, water and oil, and at the shift of the water and oil curves
to higher NA.
:::

::: step
[Slide 42]{.slide} [Step 24]{.num} [Open ↗](http://localhost:4317/#mode=psum&rpth=90&rk=10&nth=90&nm=diff&nset=rw_air&nx=tau&ny=dof&hl=pulse-crossed){.open} Open the tab “Highlights” and click the card that begins “With crossed lenses and pulses, the 2CE”. It opens the tab “Pulse results”, sets the profile at the picked τ to θ = π/2, picks τ = 10 fs on a width chart, sets the angle for the plots against NA to θ = π/2, sets the measure of the pulse width against NA to largest difference, sets the model, medium and pupil of the plot of one measure against another to Richards–Wolf, air, sets its x axis to pulse width τ and sets its y axis to depth of focus, and brings the plot of the result into view.

![](img_high_na_pulses/b42.jpg)
:::

::: main
With crossed lenses 2CE matches continuous beams from about 20 to 28 fs from NA 0.2 up.
:::

::: look
The same chart at θ = π/2 is nearly flat; at θ = 0 it sits at 4 fs, the shortest pulse computed.
:::

::: deck

These are the bullets of slides 41 and 42.

- With facing lenses the pulse width needed to match continuous beams grows as NA decreases.
- In water and oil the same results hold at a higher NA, since the focus depends on NA/n.
- With collinear lenses 4-fs pulses, the shortest computed, give the continuous-beam profiles.
- With crossed lenses, from NA 0.2 up, 2CE matches continuous beams from about 20 to 28 fs.

:::
:::

::: card
::: sl
43–44
:::

## Pulse width to match continuous beams, pupils

::: say
With facing lenses a longer depth of focus needs a longer pulse; with collinear and crossed lenses the pupil changes
little.
:::

::: step
[Slide 43]{.slide} [Step 25]{.num} [Open ↗](http://localhost:4317/#mode=psum&rpth=180&nth=180&nm=diff&nset=rw_air_eps0.9&nx=tau&ny=diff&hl=pulse-facing-pupil){.open} Open the tab “Highlights” and click the card that begins “With facing lenses, a longer depth of”. It opens the tab “Pulse results”, sets the profile at the picked τ to θ = π, sets the angle for the plots against NA to θ = π, sets the measure of the pulse width against NA to largest difference, sets the model, medium and pupil of the plot of one measure against another to Richards–Wolf, air, ε = 0.9, sets its x axis to pulse width τ and sets its y axis to largest difference, and brings the plot of the result into view.

![](img_high_na_pulses/b43.jpg)
:::

::: main
At NA 0.5 the annular pupil with ε = 0.9 needs 405 fs, against 87 fs for the circular pupil.
:::

::: look
Point at the largest difference against τ for the annular pupil, one curve per NA, and at where each curve falls below
1%.
:::

::: step
[Slide 44]{.slide} [Step 26]{.num} [Open ↗](http://localhost:4317/#mode=psum&nth=90&nm=dof&nset=rw_air_eps0.9&ny=dof){.open} Open the tab “Pulse results”, set the angle for the plots against NA to θ = π/2, set the measure of the pulse width against NA to depth of focus, set the model, medium and pupil of the plot of one measure against another to Richards–Wolf, air, ε = 0.9 and set its y axis to depth of focus; the other controls stay at their defaults.

![](img_high_na_pulses/b44.jpg)
:::

::: main
With crossed lenses the depth of focus of the annular pupil matches continuous beams from about 15 fs.
:::

::: look
Point at the curves of the depth of focus against τ at θ = π/2, which reach the line at 1 from about 15 fs.
:::

::: deck

These are the bullets of slides 43 and 44.

- A longer depth of focus needs a longer pulse to match continuous beams with facing lenses.
- With collinear lenses the depth of focus matches continuous beams at 4 fs for all pupils.
- With crossed lenses it matches from about 11 to 16 fs at NA 0.4 and above, for all pupils.

:::
:::
