---
title: "Dashboard guide: two-color excitation at high NA"
subtitle: "This guide pairs 2ce_high_na.pptx and its concise version 2ce_high_na_main.pptx with the dashboard, slide by slide. The links open the local dashboard on port 4317 until it is deployed again."
---

<!-- Source of 2ce_high_na_guide.pdf. The local dashboard is started with npm run dev in dashboard/cambaliza (port 4317).
     Build: python build.py 2ce_high_na (fills each [[id]] from steps_2ce_high_na.json with the link, the settings as a sentence
     and the screenshot). Screenshots: node shoot.mjs steps_2ce_high_na.json img_2ce_high_na, with vite preview on 4173 and
     headless Chromium on 9333. The steps h03, h06, h08, h15a, h18, h19, h23, h27 and h36 are the steps b13, b21, b23, b24, b25, b26, b27, b28
     and b22 of steps_high_na_pulses.json, with their screenshots copied from img_high_na_pulses/; the other
     screenshots were taken on 2026-11-18. Each card is one slide of 2ce_high_na.pptx; its title and the bullets in the blue box
     are those of the deck, word for word (read with python-pptx, 2026-11-18). No run-in labels or arrows anywhere in
     this file. -->

::: {.card .story}
::: sl
How
:::

## How to use this guide

- Each card is one slide of 2ce_high_na.pptx. Its number is the number of the slide in that deck, which is also printed in
  the corner of the slide.
- The concise deck 2ce_high_na_main.pptx takes 16 of these slides with the same titles and bullets, so a slide of
  the concise deck has the card of the same title here.
- Each step says which tab to open, which controls to set and which point to click; all other controls stay at their
  defaults. The link Open in each step loads all of these settings at once.
- Where a result has a card on the tab Highlights, the step opens that card. Its banner gives the result in one
  sentence.
- The yellow box under the title of each slide states the result of that slide in one sentence. The yellow box under
  each screenshot states the main point of the step, and the text below it says what to point at. The blue box
  repeats the bullets of the slide.
- Slides 2, 4, 28, 37 and 38 have no view in the dashboard; their cards give the result and what to say. The title
  slide, the divider of the backup slides and the glossary have no card.
:::

::: card
::: sl
2
:::

## Summary

::: say
The conclusions of Cambaliza & Saloma (2000) hold at high NA with the vector (Richards–Wolf) focus, while their paraxial model overestimates the depth of focus above NA 0.43 in air, by 36% at NA 0.9.
:::

The dashboard has no view of this slide. Say that the slides compare the paraxial scalar model of Cambaliza & Saloma (2000) with the vector focus, in air unless a slide says otherwise, and that two crossed lenses fit up to NA 0.71 in air and 0.94 in water. The central spot of the paraxial model stays within 5% of the vector one up to NA 0.86 in air (1.14 in water), and its depth of focus is 5% longer from NA 0.43 in air (0.57 in water).

::: deck

These are the bullets of slide 2.

- Extended the 2CE and 2PE point spread functions of Cambaliza & Saloma (2000) from NA 0.5 to high NA, with the vector (Richards–Wolf) focus in place of the paraxial scalar model, in air and in water.
- Compared the two models for collinear, crossed and facing lenses, at NA 0.5 and as NA increases, with the central spot, the depth of focus, the side lobes and Linfoot's criteria.
- Found that the paraxial model gives the central spot of the vector focus up to NA 0.86 in air, but overestimates the depth of focus above NA 0.43, by 7% at NA 0.5 and by 36% at NA 0.9.
- Found that with crossed lenses the paraxial and vector PSFs agree within 4% wherever the two lenses fit, and the 2PE central spot keeps its width of 0.26 µm at all NAs.
- Found that the conclusions of Cambaliza & Saloma (2000) hold at high NA, while the differences between 2PE and 2CE shrink: the 2PE side lobes weaken and the 2CE spot approaches the 2PE one.

:::
:::

::: {.part}
# Extension of Cambaliza & Saloma (2000) from the paraxial scalar model to the vector (Richards–Wolf) focus (slides 3 to 28)
:::

::: card
::: sl
3
:::

## Two-color excitation with two confocal beams at an angle θ

::: say
2CE absorbs one photon of each color, so it forms where the two beams overlap and its signal is the product of the two intensities.
:::

::: step
[Slide 3]{.slide} [Step 1]{.num} [Open ↗](http://localhost:4317/#mode=live){.open} Open the tab “Focal spot” with all controls at their defaults.

![](img_2ce_high_na/h03.jpg)
:::

::: main
The tab Focal spot shows the two foci and the 2CE and 2PE maps at any angle θ.
:::

::: look
Point at the drawing of the setup at the top of the left panel, where L2 is L1 rotated by θ about the focus. Then move the angle slider from 0 to 180°: the 2CE map changes from a long focus to a small crossed region and back to a long focus.
:::

::: deck

These are the bullets of slide 3.

- Lens L2 is lens L1 rotated by θ about the common focus O; L1 focuses 750 nm and L2 656 nm.
- 2CE absorbs one photon of each color, so the signal is the product of the two intensities.
- 2PE uses 700 nm in both beams, so the two fields add first and interfere.

The line under the equations reads as follows.

> where λ~e~ = 350 nm; I~1~ and I~2~ are the focused intensities and U~1~ and U~2~ the fields; θ = 0, π/2 and π are collinear, crossed and facing lenses.

:::
:::

::: card
::: sl
4
:::

## Paraxial scalar model and vector (Richards–Wolf) focus

::: say
The paraxial model of Cambaliza & Saloma (2000) uses the small-angle form of the phase of each ray, so its depth of focus exceeds that of the vector focus by about 1 + tan²(α/2), which is 1.07 at NA 0.5 and 1.39 at NA 0.9.
:::

The dashboard has no view of this slide. Say that Eq. (4) is the paraxial field of Cambaliza & Saloma (2000, Eq. 1) in the optical coordinates u and v, and that Eq. (5) replaces 1 − cos α by sin²α/2, which lengthens the depth of focus by 1 + tan²(α/2). The scalar Debye integral with the exact phase gives the vector profile along the axis, so the phase, not the polarization, causes the difference along the axis. The computed 2CE depths of focus of the two models differ by 7.1% at NA 0.5 and by 36.3% at NA 0.9 in air, close to the factor.

::: deck

These are the bullets of slide 4.

- The paraxial model of Cambaliza & Saloma (2000, Eq. 1) uses the small-angle form of the phase of each ray, which makes the focus too long at high NA.
- The vector (Richards–Wolf) focus keeps the exact phase and the three field components; both beams are polarized perpendicular to the plane of the lens axes.

The line under the equations reads as follows.

> where u = (2π/λ) NA² z/n and v = (2π/λ) NA r are the optical coordinates along and across the axis, and α is the half-angle of the focusing cone, sin α = NA/n. At NA 0.5 the factor 1 + tan²(α/2) is 1.07 and at NA 0.9 it is 1.39.

:::
:::

::: card
::: sl
5
:::

## 2CE PSF in the x–z plane at NA 0.5 and NA 0.9, θ = 0 and π

::: say
At high NA the paraxial 2CE PSF with collinear and facing lenses is longer than the vector one, by 7% at NA 0.5 and 36% at NA 0.9, so the paraxial model overestimates the depth of focus.
:::

::: step
[Slide 5]{.slide} [Step 2]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=width&sig=2CE&ths=0&axis=z&na=0.5){.open} Open the tab “Scalar vs vector at high NA”, set the plot to width, set the signal to 2CE, set the angles to 0, set the direction to along and click NA 0.5 on the left chart; the other controls stay at their defaults.

![](img_2ce_high_na/h05a.jpg)
:::

::: main
At NA 0.5 the paraxial and vector 2CE maps nearly coincide; the paraxial depth of focus is 3.562 µm against 3.326 µm.
:::

::: look
Point at the two maps on the right, the paraxial (scalar) map on the left and the vector map on the right, and at the orange half-maximum contour of each. The profiles below the maps give the central spot, 0.516 µm against 0.510 µm, and the depth of focus.
:::

::: step
[Slide 5]{.slide} [Step 3]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=width&sig=2CE&ths=0&axis=z&na=0.9){.open} Open the tab “Scalar vs vector at high NA”, set the plot to width, set the signal to 2CE, set the angles to 0, set the direction to along and click NA 0.9 on the left chart; the other controls stay at their defaults.

![](img_2ce_high_na/h05b.jpg)
:::

::: main
At NA 0.9 the half-maximum contour of the paraxial map is longer along z than that of the vector map: the depth of focus is 1.099 µm against 0.807 µm.
:::

::: look
Compare the orange half-maximum contours of the two maps along z, then the profile along the axis below them. Across the axis the paraxial spot is 6% wider, 0.286 µm against 0.270 µm. With facing lenses the 2CE maps are the same, since I~1~I~2~ does not depend on the direction of beam 2.
:::

::: deck

These are the bullets of slide 5.

- At NA 0.5, the paraxial and vector 2CE PSFs with collinear and facing lenses coincide across the axis, and the paraxial PSF is 7% longer along it.
- At NA 0.9, the paraxial PSF is 6% wider and 36% longer than the vector one, so the paraxial model overestimates the depth of focus at high NA.

:::
:::

::: card
::: sl
6
:::

## Central spot and depth of focus against NA: 2CE, θ = 0 and π

::: say
As NA increases the paraxial depth of focus of 2CE shrinks more slowly than the vector one, so it is 5% longer from NA 0.43 in air, while the central spot stays within 5% up to NA 0.86.
:::

::: step
[Slide 6]{.slide} [Step 4]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=width&sig=2CE&ths=0&axis=z&na=0.9&hl=cw-dof-collinear){.open} Open the tab “Highlights” and click the card that begins “With collinear lenses, as NA increases, the”. It opens the tab “Scalar vs vector at high NA”, sets the plot to width, sets the signal to 2CE, sets the angles to 0, sets the direction to along and picks NA 0.9 on the left chart.

![](img_2ce_high_na/h06.jpg)
:::

::: main
In the vector model the 2CE depth of focus is 3.33 µm at NA 0.5 and 0.81 µm at NA 0.9.
:::

::: look
Point at the left chart, which gives the depth of focus against NA on log axes: the dashed scalar curve lies above the solid vector curve from about NA 0.4. The profiles at NA 0.9 are on the right.
:::

::: deck

These are the bullets of slide 6.

- As NA increases both widths shrink, but the paraxial depth of focus shrinks more slowly than the vector one and becomes too long.
- The paraxial DOF of F2c(0, 0, z; 0) is 5% longer from NA 0.43 in air (0.57 in water), below the NA 0.7 stated on p. 27; the central spot stays within 5% up to NA 0.86.
- Eq. (1) uses sin²α/2 for 1 − cos α, which lengthens the DOF by the factor 1 + tan²(α/2).

:::
:::

::: card
::: sl
7
:::

## 2CE PSF in the x–z plane at NA 0.5 and NA 0.7, θ = π/2

::: say
With crossed lenses the paraxial and vector 2CE PSFs coincide within 1.4% at NA 0.5 and 3.4% at NA 0.7, because each width is set by the narrow transverse spot of the other beam.
:::

::: step
[Slide 7]{.slide} [Step 5]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=width&sig=2CE&ths=pi2&axis=x&na=0.5){.open} Open the tab “Scalar vs vector at high NA”, set the plot to width, set the signal to 2CE, set the angles to π/2, set the direction to across and click NA 0.5 on the left chart; the other controls stay at their defaults.

![](img_2ce_high_na/h07a.jpg)
:::

::: main
At NA 0.5 the crossed-lens 2CE maps of the two models coincide: the central spot is 0.763 µm in the paraxial model and 0.752 µm in the vector model.
:::

::: look
Point at the two maps, which are nearly round, and at the profiles below them, which give the depth of focus as well, 0.670 µm against 0.662 µm.
:::

::: step
[Slide 7]{.slide} [Step 6]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=width&sig=2CE&ths=pi2&axis=x&na=0.7&hl=cw-2ce-crossed){.open} Open the tab “Highlights” and click the card that begins “With crossed lenses, as NA increases, both”. It opens the tab “Scalar vs vector at high NA”, sets the plot to width, sets the signal to 2CE, sets the angles to π/2, sets the direction to across and picks NA 0.7 on the left chart.

![](img_2ce_high_na/h07b.jpg)
:::

::: main
At NA 0.7 the paraxial 2CE spot is 3.4% wider than the vector one, 0.539 µm against 0.521 µm.
:::

::: look
Point at the half-maximum contours of the two maps, and at the left chart of the width across the axis against NA, where the dashed scalar curve stays on the solid vector curve up to NA 0.7.
:::

::: deck

These are the bullets of slide 7.

- With crossed lenses, the paraxial and vector 2CE PSFs coincide within 1.4% at NA 0.5 and 3.4% at NA 0.7, the largest NA at which two crossed lenses fit in air.
- Each width of the crossed-lens PSF is set by the narrow transverse spot of the other beam, which the paraxial model reproduces.

:::
:::

::: card
::: sl
8
:::

## Central spot and depth of focus against NA: 2CE, θ = π/2

::: say
With crossed lenses both 2CE widths shrink as NA increases, and the paraxial model follows the vector focus within 4%, because each width is set by the narrow transverse spot of the other beam.
:::

::: step
[Slide 8]{.slide} [Step 7]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=width&sig=2CE&ths=0.pi2&axis=z&na=0.7&hl=cw-dof-crossed){.open} Open the tab “Highlights” and click the card that begins “With crossed lenses the depth of focus”. It opens the tab “Scalar vs vector at high NA”, sets the plot to width, sets the signal to 2CE, sets the angles to 0 and π/2, sets the direction to along and picks NA 0.7 on the left chart.

![](img_2ce_high_na/h08.jpg)
:::

::: main
With crossed lenses the 2CE depth of focus is 13 times shorter than with collinear lenses at NA 0.2, and 3.4 times shorter at NA 0.7.
:::

::: look
Point at the two curves of the left chart, θ = 0 above and θ = π/2 below, and at the gap between them, which narrows as NA increases.
:::

::: deck

These are the bullets of slide 8.

- As NA increases both widths of F2c at θ = π/2 shrink, and the paraxial model follows the vector focus within 4% wherever crossed lenses fit (NA 0.71 in air, 0.94 in water).
- Each width is set by the narrow transverse spot of the other beam, which Eq. (1) reproduces.

:::
:::

::: card
::: sl
9
:::

## 2PE PSF in the x–z plane at NA 0.5 and NA 0.9, θ = 0

::: say
With collinear lenses the 2PE PSF has the shape of the 2CE PSF, so the paraxial 2PE focus is too long in the same way, by 7% at NA 0.5 and 36% at NA 0.9.
:::

::: step
[Slide 9]{.slide} [Step 8]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=width&sig=2PE&ths=0&axis=z&na=0.5){.open} Open the tab “Scalar vs vector at high NA”, set the plot to width, set the signal to 2PE, set the angles to 0, set the direction to along and click NA 0.5 on the left chart; the other controls stay at their defaults.

![](img_2ce_high_na/h09a.jpg)
:::

::: main
At NA 0.5 the 2PE maps of the two models nearly coincide, with depths of focus of 3.572 µm (paraxial) and 3.335 µm (vector).
:::

::: look
Point at the two maps and at the profile along the axis below them; the 2PE widths at θ = 0 are those of 2CE to within 0.01 µm.
:::

::: step
[Slide 9]{.slide} [Step 9]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=width&sig=2PE&ths=0&axis=z&na=0.9&hl=cw-2pe-collinear){.open} Open the tab “Highlights” and click the card that begins “With collinear lenses 2CE and 2PE have”. It opens the tab “Scalar vs vector at high NA”, sets the plot to width, sets the signal to 2PE, sets the angles to 0, sets the direction to along and picks NA 0.9 on the left chart.

![](img_2ce_high_na/h09b.jpg)
:::

::: main
At NA 0.9 the paraxial 2PE depth of focus is 36% longer than the vector one, 1.102 µm against 0.809 µm.
:::

::: look
Compare the half-maximum contours of the two maps along z, and the dashed and solid curves of the left chart, which separate from about NA 0.4.
:::

::: deck

These are the bullets of slide 9.

- With collinear lenses the 2PE PSF has the shape of the 2CE PSF, and the paraxial model departs from the vector focus in the same way: 7% longer at NA 0.5 and 36% longer at NA 0.9.

:::
:::

::: card
::: sl
10
:::

## Central spot and depth of focus against NA: 2PE, θ = 0

::: say
2PE at θ = 0 changes with NA as 2CE at θ = 0, so its paraxial depth of focus is 5% longer than the vector one from NA 0.43 in air.
:::

::: step
[Slide 10]{.slide} [Step 10]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=width&sig=2PE&ths=0&axis=z&na=0.9&hl=cw-2pe-collinear){.open} Open the tab “Highlights” and click the card that begins “With collinear lenses 2CE and 2PE have”. It opens the tab “Scalar vs vector at high NA”, sets the plot to width, sets the signal to 2PE, sets the angles to 0, sets the direction to along and picks NA 0.9 on the left chart.

![](img_2ce_high_na/h09b.jpg)
:::

::: main
The left chart gives the 2PE depth of focus against NA at θ = 0, solid for the vector model and dashed for the paraxial model.
:::

::: look
Point at the NA where the dashed curve leaves the solid one, about NA 0.4, and compare the chart with that of 2CE on slide 6, which it repeats. Setting the direction to across gives the central spot, which stays within 5% up to NA 0.86.
:::

::: deck

These are the bullets of slide 10.

- F2p at θ = 0 is identical with F2c at θ = 0, so it changes with NA in the same way: the paraxial DOF is 5% longer from NA 0.43 in air.

:::
:::

::: card
::: sl
11
:::

## 2PE PSF in the x–z plane at NA 0.5 and NA 0.7, θ = π/2

::: say
With crossed lenses the 2PE central spot is one interference fringe of the two beams, 0.256 µm wide in both models at NA 0.5 and at NA 0.7, and the fringes beside it weaken as NA increases.
:::

::: step
[Slide 11]{.slide} [Step 11]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=width&sig=2PE&ths=pi2&axis=x&na=0.5){.open} Open the tab “Scalar vs vector at high NA”, set the plot to width, set the signal to 2PE, set the angles to π/2, set the direction to across and click NA 0.5 on the left chart; the other controls stay at their defaults.

![](img_2ce_high_na/h11a.jpg)
:::

::: main
At NA 0.5 the crossed-lens 2PE maps of the two models coincide, with a central spot of 0.256 µm.
:::

::: look
Point at the central fringe of each map and at the weaker fringes beside it, and at the profile across the axis below the maps.
:::

::: step
[Slide 11]{.slide} [Step 12]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=width&sig=2PE&ths=pi2&axis=x&na=0.7&hl=cw-2pe-crossed){.open} Open the tab “Highlights” and click the card that begins “With crossed lenses, the 2PE central spot”. It opens the tab “Scalar vs vector at high NA”, sets the plot to width, sets the signal to 2PE, sets the angles to π/2, sets the direction to across and picks NA 0.7 on the left chart.

![](img_2ce_high_na/h11b.jpg)
:::

::: main
At NA 0.7 the central spot is still 0.256 µm wide, while the fringes beside it are weaker than at NA 0.5.
:::

::: look
Point at the fringes beside the central spot in the two maps. The side lobe is 0.11 of the peak at NA 0.5 and 0.04 at NA 0.7; the plot side-lobe height gives it against NA.
:::

::: deck

These are the bullets of slide 11.

- With crossed lenses the 2PE central spot is one interference fringe of the two beams, 0.256 µm wide in both models at NA 0.5 and at NA 0.7.
- As NA increases, the fringes beside the central spot weaken, so the 2PE PSF approaches a single spot.

:::
:::

::: card
::: sl
12
:::

## Central spot and depth of focus against NA: 2PE, θ = π/2

::: say
As NA increases the 2PE central spot at θ = π/2 keeps its width, 0.26 µm in air and 0.19 µm in water, because it is one interference fringe of the two crossed beams.
:::

::: step
[Slide 12]{.slide} [Step 13]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=width&sig=2PE&ths=pi2&axis=x&na=0.7&hl=cw-2pe-crossed){.open} Open the tab “Highlights” and click the card that begins “With crossed lenses, the 2PE central spot”. It opens the tab “Scalar vs vector at high NA”, sets the plot to width, sets the signal to 2PE, sets the angles to π/2, sets the direction to across and picks NA 0.7 on the left chart.

![](img_2ce_high_na/h11b.jpg)
:::

::: main
The left chart gives the 2PE width across the axis at θ = π/2 against NA, flat at 0.256 µm in both models.
:::

::: look
Point at the flat curve of the left chart; it ends at NA 0.7, below the NA 0.71 at which two crossed lenses fit in air. Switching the medium to water gives 0.19 µm up to NA 0.9.
:::

::: deck

These are the bullets of slide 12.

- As NA increases the central spot of F2p at θ = π/2 keeps its width, 0.26 µm in air and 0.19 µm in water, in both models (within 0.4%).
- The spot is one interference fringe of the two crossed beams, so its width is set by the wavelength in the medium, λ2p/n (n = 1 air, 1.33 water), not by the NA.
- It stays the sharpest distribution at every NA, as at NA 0.5 (p. 28).

:::
:::

::: card
::: sl
13
:::

## 2PE PSF in the x–z plane at NA 0.5 and NA 0.9, θ = π

::: say
With facing lenses the 2PE PSF is a standing wave along the axis in both models, and at NA 0.9 the longer paraxial envelope keeps side fringes above 10% of the peak where the vector PSF has none.
:::

::: step
[Slide 13]{.slide} [Step 14]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=width&sig=2PE&ths=pi&axis=z&na=0.5){.open} Open the tab “Scalar vs vector at high NA”, set the plot to width, set the signal to 2PE, set the angles to π, set the direction to along and click NA 0.5 on the left chart; the other controls stay at their defaults.

![](img_2ce_high_na/h13a.jpg)
:::

::: main
At NA 0.5 the fringes of the paraxial and vector maps coincide, with a central fringe 0.136 µm long in both models.
:::

::: look
Point at the fringes along z in the two maps, about 0.37 µm apart, and at the profile along the axis below them, where the fringes lie under the long envelope of the focus.
:::

::: step
[Slide 13]{.slide} [Step 15]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=width&sig=2PE&ths=pi&axis=z&na=0.9&hl=cw-2pe-facing){.open} Open the tab “Highlights” and click the card that begins “With facing lenses and continuous beams, 2CE”. It opens the tab “Scalar vs vector at high NA”, sets the plot to width, sets the signal to 2PE, sets the angles to π, sets the direction to along and picks NA 0.9 on the left chart.

![](img_2ce_high_na/h13b.jpg)
:::

::: main
At NA 0.9 the vector map has fewer strong fringes than the paraxial map, because its envelope along the axis is shorter.
:::

::: look
Point at the outer fringes, about 0.8 µm from the focus: in the paraxial map they reach the 10% contour, and in the vector map the 1% contour. The first side fringes reach the orange half-maximum contour in the paraxial map and stay below it in the vector map (0.65 against 0.42 of the peak).
:::

::: deck

These are the bullets of slide 13.

- With facing lenses the 2PE PSF is a standing wave along the axis, with fringes about λ~2p~/2 = 350 nm apart in both models; the spacing widens slightly as NA increases, because the converging waves cross the axis at an angle.
- At NA 0.9, the paraxial envelope is longer than the vector one, so the paraxial PSF has side fringes above 10% of the peak (dashed) where the vector PSF has none.

:::
:::

::: card
::: sl
14
:::

## Central spot and depth of focus against NA: 2PE, θ = π

::: say
As NA increases fewer fringes of the 2PE standing wave fit inside the focus, about 9 at NA 0.5 and 2 at NA 0.9 in air, because the focus shortens as 1/NA² while the fringes stay about λ/2n apart.
:::

::: step
[Slide 14]{.slide} [Step 16]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=width&sig=2PE&ths=pi&axis=z&na=0.9&hl=cw-2pe-facing){.open} Open the tab “Highlights” and click the card that begins “With facing lenses and continuous beams, 2CE”. It opens the tab “Scalar vs vector at high NA”, sets the plot to width, sets the signal to 2PE, sets the angles to π, sets the direction to along and picks NA 0.9 on the left chart.

![](img_2ce_high_na/h13b.jpg)
:::

::: main
The left chart gives the length of the central fringe against NA at θ = π, which grows from 0.13 µm to 0.17 µm.
:::

::: look
Point at the solid vector curve and the dashed paraxial curve, which agree within 5% up to NA 0.91 in air. The profile along the axis below the maps shows the central fringe and the fringes beside it at NA 0.9.
:::

::: deck

These are the bullets of slide 14.

- Across the axis, F2p(x, 0, 0; π) is identical with F2p(x, 0, 0; 0).
- As NA increases fewer fringes fit inside the focus, about 9 at NA 0.5 and 2 at NA 0.9 in air: the focus shortens as 1/NA², while the fringes stay about λ/2n apart, half the wavelength in the medium (0.37 µm at NA 0.5, 0.44 µm at NA 0.9; λ/2n = 0.35 µm in air).
- The fringes spread slightly with NA because the converging waves cross the axis at an angle; the central fringe widens from 0.13 to 0.17 µm, and paraxial and vector agree within 5% up to NA 0.91 in air.

:::
:::

::: card
::: sl
15
:::

## Paraxial over vector widths of 2CE against NA

::: say
As NA increases the paraxial 2CE widths become larger than the vector ones, first along the axis, where the difference reaches 5% at NA 0.43 in air.
:::

::: step
[Slide 15]{.slide} [Step 17]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=gap&sig=2CE&ths=0.pi2.pi&axis=z&na=0.9){.open} Open the tab “Scalar vs vector at high NA”, set the plot to scalar / vector, set the signal to 2CE, set the angles to 0, π/2 and π, set the direction to along and click NA 0.9 on the left chart; the other controls stay at their defaults.

![](img_2ce_high_na/h15a.jpg)
:::

::: main
Along the axis the difference passes 5% at NA 0.43 in air with collinear and facing lenses, and it stays within 4% with crossed lenses.
:::

::: look
Point at the grey band of ±5% and at the NA where the curves of θ = 0 and π leave it; the curve of θ = π/2 stays inside the band.
:::

::: step
[Slide 15]{.slide} [Step 18]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=gap&sig=2CE&ths=0&axis=x&na=0.85&hl=cw-scalar-5pct){.open} Open the tab “Highlights” and click the card that begins “The 2CE and 2PE profiles of the scalar”. It opens the tab “Scalar vs vector at high NA”, sets the plot to scalar / vector, sets the signal to 2CE, sets the angles to 0, sets the direction to across and picks NA 0.85 on the left chart.

![](img_2ce_high_na/h15b.jpg)
:::

::: main
Across the axis the difference reaches 5% at NA 0.86 in air.
:::

::: look
Point at the curve of θ = 0 against NA and at the grey band of ±5%, which the curve leaves near NA 0.85, where the view opens. Switching the medium to water moves the 5% point to NA 1.14.
:::

::: deck

These are the bullets of slide 15.

- As NA increases the paraxial 2CE widths become larger than the vector ones, first along the axis.
- Along the axis at θ = 0 and π the difference reaches 5% at NA 0.43 in air (0.57 in water); across the axis at NA 0.86 (1.14); with crossed lenses it stays within 4%.

:::
:::

::: card
::: sl
16
:::

## Paraxial over vector widths of 2PE against NA

::: say
As NA increases the paraxial 2PE widths at θ = 0 depart from the vector ones as the 2CE widths do, while with crossed lenses they stay within 0.4%.
:::

::: step
[Slide 16]{.slide} [Step 19]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=gap&sig=2PE&ths=0.pi2.pi&axis=z&na=0.9){.open} Open the tab “Scalar vs vector at high NA”, set the plot to scalar / vector, set the signal to 2PE, set the angles to 0, π/2 and π, set the direction to along and click NA 0.9 on the left chart; the other controls stay at their defaults.

![](img_2ce_high_na/h16.jpg)
:::

::: main
Along the axis at NA 0.9 the paraxial 2PE depth of focus at θ = 0 is 36% longer than the vector one, while the paraxial central fringe at θ = π is narrower, 0.158 µm against 0.166 µm.
:::

::: look
Point at the three curves and the grey band of ±5%: θ = 0 rises out of the band from about NA 0.43, θ = π falls to the lower edge of the band near NA 0.9, and θ = π/2 stays at zero up to NA 0.7.
:::

::: deck

These are the bullets of slide 16.

- As NA increases the paraxial 2PE widths at θ = 0 depart as the 2CE ones; with crossed lenses they stay within 0.4%.
- At θ = π the paraxial central fringe becomes narrower than the vector one, by 5% at NA 0.91 in air (1.21 in water).

:::
:::

::: card
::: sl
17
:::

## Whole-profile difference of 2CE, paraxial against vector

::: say
As NA increases the whole paraxial 2CE profile departs from the vector one along the axis much more than across it: by 25% at NA 0.9 along the axis and by 5% across it, in air.
:::

::: step
[Slide 17]{.slide} [Step 20]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=nrmse&sig=2CE&ths=0.pi2.pi&axis=z&na=0.9){.open} Open the tab “Scalar vs vector at high NA”, set the plot to NRMSE, set the signal to 2CE, set the angles to 0, π/2 and π, set the direction to along and click NA 0.9 on the left chart; the other controls stay at their defaults.

![](img_2ce_high_na/h17.jpg)
:::

::: main
Along the axis the NRMSE of the paraxial 2CE profile against the vector one is 6% at NA 0.5 and 25% at NA 0.9 with collinear and facing lenses.
:::

::: look
Point at the curves of θ = 0 and π, which lie on each other, and at the curve of θ = π/2, which stays at 3% or less up to NA 0.7. Switching the direction to across gives 1% at NA 0.5 and 5% at NA 0.9.
:::

::: deck

These are the bullets of slide 17.

- As NA increases the paraxial F2c departs from the vector one along the axis much more than across it.
- Along the axis at θ = 0 and π: 6% at NA 0.5 and 25% at NA 0.9 in air; across the axis 1% and 5%; with crossed lenses 3% or less.

:::
:::

::: card
::: sl
18
:::

## Linfoot’s criteria against NA: 2CE, θ = 0 and π

::: say
As NA increases the paraxial 2CE along the axis becomes longer and lower than the vector one, so the structural content C falls first, below 0.95 from NA 0.44 in air.
:::

::: step
[Slide 18]{.slide} [Step 21]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=C&sig=2CE&ths=0.pi&axis=z&na=0.7){.open} Open the tab “Scalar vs vector at high NA”, set the plot to Linfoot C, set the signal to 2CE, set the angles to 0 and π, set the direction to along and click NA 0.7 on the left chart; the other controls stay at their defaults.

![](img_2ce_high_na/h18.jpg)
:::

::: main
With collinear and facing lenses the structural content C along the axis falls below 0.95 from NA 0.44 in air.
:::

::: look
Point at the curve of C against NA and at the NA where it crosses 0.95. At NA 0.9 the fidelity F is 0.94 and C is 0.74.
:::

::: deck

These are the bullets of slide 18.

- As NA increases the paraxial F2c(0, 0, z; π) becomes longer and lower than the vector one, so C falls first: below 0.95 from NA 0.44 in air (0.58 in water).
- F stays above 0.99 up to NA 0.63 (0.84 in water); across the axis F ≥ 0.996 at all NA.

:::
:::

::: card
::: sl
19
:::

## Linfoot’s criteria against NA: 2CE, θ = π/2

::: say
With crossed lenses the paraxial and vector 2CE stay alike wherever the lenses fit, with the fidelity F at 0.999 or above.
:::

::: step
[Slide 19]{.slide} [Step 22]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=F&sig=2CE&ths=pi2&axis=x&na=0.7){.open} Open the tab “Scalar vs vector at high NA”, set the plot to Linfoot F, set the signal to 2CE, set the angles to π/2, set the direction to across and click NA 0.7 on the left chart; the other controls stay at their defaults.

![](img_2ce_high_na/h19.jpg)
:::

::: main
With crossed lenses the fidelity F stays at 0.999 or above wherever the lenses fit.
:::

::: look
Point at the curve of F against NA, which ends at NA 0.7 in air, below the NA 0.71 at which the cones of the two lenses touch.
:::

::: deck

These are the bullets of slide 19.

- As NA increases the paraxial and vector F2c at θ = π/2 stay alike: F ≥ 0.999, C ≥ 0.97 and Q ≥ 0.98 wherever crossed lenses fit (NA 0.71 in air, 0.94 in water).
- With crossed lenses, Eq. (1) gives the profiles of the vector focus.

:::
:::

::: card
::: sl
20
:::

## 2PE and 2CE central spots against NA, circular pupils

::: say
As NA increases the 2CE spot at θ = π/2 shrinks while the 2PE spot keeps its width, so 2PE at θ = π/2 stays the sharpest distribution, as at NA 0.5 (p. 28).
:::

::: step
[Slide 20]{.slide} [Step 23]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=cmp&cmp=r1&na=0.7){.open} Open the tab “Scalar vs vector at high NA”, set the plot to “paper's comparisons”, set the comparison to “2PE spot, θ = π/2 over θ = 0 (p. 28)” and click NA 0.7 on the left chart; the other controls stay at their defaults.

![](img_2ce_high_na/h20a.jpg)
:::

::: main
Relative to θ = 0, the 2PE spot at θ = π/2 is 0.50 times as wide at NA 0.5 and 0.71 times at NA 0.7, because the spot at θ = 0 shrinks with NA.
:::

::: look
Point at the vector and scalar curves of the left chart, which agree within 4%. The star at NA 0.5 is the ratio stated on p. 28, 0.67, and the cross, under the curves, the ratio on the published curves, 0.49.
:::

::: step
[Slide 20]{.slide} [Step 24]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=cmp&cmp=r2&na=0.7){.open} Open the tab “Scalar vs vector at high NA”, set the plot to “paper's comparisons”, set the comparison to “2CE spot over 2PE spot, θ = π/2 (p. 29)” and click NA 0.7 on the left chart; the other controls stay at their defaults.

![](img_2ce_high_na/h20b.jpg)
:::

::: main
The 2CE spot at θ = π/2 is 2.9 times the 2PE spot at NA 0.5 and 2.0 times at NA 0.7 in air.
:::

::: look
Point at the falling curves of the left chart and at the two vector maps on the right, the 2CE spot and the 2PE spot at NA 0.7. The star at NA 0.5 is the ratio stated on p. 29, 1.58, and the cross the ratio on the published curves, 2.98.
:::

::: deck

These are the bullets of slide 20.

- As NA increases the 2CE spot at θ = π/2 shrinks while the 2PE spot keeps its width: 2.9 times the 2PE spot at NA 0.5, 2.0 at NA 0.7 in air.
- Relative to θ = 0, the 2PE spot at θ = π/2 is 0.50 times as wide at NA 0.5 and 0.71 at NA 0.7.
- 2PE at θ = π/2 stays the sharpest distribution at every NA, as on p. 28; scalar and vector agree within 4%.

:::
:::

::: card
::: sl
21
:::

## 2CE and 2PE depth of focus against NA, θ = π/2

::: say
As NA increases the 2CE depth of focus at θ = π/2 shortens while the 2PE depth of focus stays one fringe, so the broader depth of focus of 2CE (p. 30) remains at high NA but the difference shrinks.
:::

::: step
[Slide 21]{.slide} [Step 25]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=cmp&cmp=r3&na=0.7){.open} Open the tab “Scalar vs vector at high NA”, set the plot to “paper's comparisons”, set the comparison to “2CE DOF over 2PE DOF, θ = π/2” and click NA 0.7 on the left chart; the other controls stay at their defaults.

![](img_2ce_high_na/h21.jpg)
:::

::: main
The 2CE depth of focus at θ = π/2 is 2.6 times that of 2PE at NA 0.5 and 1.8 times at NA 0.7 in air.
:::

::: look
Point at the falling curves of the left chart. Switching the medium to water extends them to NA 0.9, where the ratio is 1.9.
:::

::: deck

These are the bullets of slide 21.

- As NA increases the 2CE DOF shortens while the 2PE DOF stays one fringe: 2.6 times the 2PE DOF at NA 0.5, 1.8 at NA 0.7 in air.
- The “broader DOF” of 2CE at θ = π/2 (p. 30) remains at high NA, but the difference shrinks.

:::
:::

::: card
::: sl
22
:::

## Side lobes of 2PE against NA: distance from the peak and height

::: say
As NA increases the 2PE side lobes weaken, so the drawback of 2PE that Cambaliza & Saloma (2000) report at NA 0.5 becomes smaller at high NA.
:::

::: step
[Slide 22]{.slide} [Step 26]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=lobe&sig=2PE&ths=pi&axis=z&na=0.9&how=1){.open} Open the tab “Scalar vs vector at high NA”, set the plot to side-lobe distance, set the signal to 2PE, set the angles to π, set the direction to along, click NA 0.9 on the left chart and set “How it is measured” to “show, with equations”; the other controls stay at their defaults.

![](img_2ce_high_na/h22a.jpg)
:::

::: main
With facing lenses the first side lobe of 2PE lies about 0.53 λ/n from the peak at NA 0.5, near λ/2n, the spacing of the standing wave, and moves out to 0.63 λ/n at NA 0.9.
:::

::: look
Point at the drawing of how the distance is measured, from the centre down to the first minimum and up to the next peak, and at the curve of the distance against NA below it.
:::

::: step
[Slide 22]{.slide} [Step 27]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=lobeh&sig=2PE&ths=pi2&axis=x&na=0.7){.open} Open the tab “Scalar vs vector at high NA”, set the plot to side-lobe height, set the signal to 2PE, set the angles to π/2, set the direction to across and click NA 0.7 on the left chart; the other controls stay at their defaults.

![](img_2ce_high_na/h22b.jpg)
:::

::: main
With crossed lenses the first side lobe of 2PE falls from 0.11 of the peak at NA 0.5 to 0.04 at NA 0.7.
:::

::: look
Point at the curve of the side-lobe height against NA, and at the weak fringes beside the central spot in the two maps at NA 0.7.
:::

::: deck

These are the bullets of slide 22.

- As NA increases the 2PE side lobes weaken: at θ = π/2 from 0.11 of the peak at NA 0.5 to 0.04 at NA 0.7 (air); at θ = π from 0.97 to 0.42 at NA 0.9.
- Their distance from the peak follows the wavelength in the medium (n = 1 air, 1.33 water): λ/2n with facing lenses (the standing-wave fringe) and λ/n with crossed lenses, at low NA.
- Weaker side lobes give images of higher contrast, so the drawback of 2PE reported at NA 0.5 (pp. 28–29) shrinks at high NA.

:::
:::

::: card
::: sl
23
:::

## Annular pupils: depth of focus against NA, air

::: say
As NA increases the paraxial depth of focus of an annular pupil departs from the vector one sooner than that of the circular pupil, because a thin ring uses the edge of the pupil, where the paraxial phase error is largest.
:::

::: step
[Slide 23]{.slide} [Step 28]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=width&sig=2CE&ths=0&axis=z&pupil=ann&na=0.9){.open} Open the tab “Scalar vs vector at high NA”, set the plot to width, set the signal to 2CE, set the angles to 0, set the direction to along, set the pupil to annular and click NA 0.9 on the left chart; the other controls stay at their defaults.

![](img_2ce_high_na/h23.jpg)
:::

::: main
With the annular pupil of ε = 0.99 the paraxial depth of focus is 15% too long at NA 0.5 and 2.2 times too long at NA 0.9.
:::

::: look
Point at the gap between the dashed scalar curve and the solid vector curve at NA 0.9, which the speaker notes give as 55 µm against 25 µm.
:::

::: deck

These are the bullets of slide 23.

- As NA increases the paraxial annular DOF departs sooner than the circular one: 15% too long at NA 0.5 and 2.2 times at NA 0.9 in air.
- A thin ring uses the edge of the pupil, where the paraxial phase error is largest.

:::
:::

::: card
::: sl
24
:::

## Annular central spots against NA: the comparisons of p. 31

::: say
As NA increases the annular 2CE spot at θ = 0 stays 0.67 of that at θ = π/2, while the annular 2PE spot at θ = π/2 loses its lead over the annular 2CE spot.
:::

::: step
[Slide 24]{.slide} [Step 29]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=cmp&cmp=a1&na=0.7){.open} Open the tab “Scalar vs vector at high NA”, set the plot to “paper's comparisons”, set the comparison to “Annular 2CE spot, θ = 0 over θ = π/2 (Fig. 6b, p. 31)” and click NA 0.7 on the left chart; the other controls stay at their defaults.

![](img_2ce_high_na/h24a.jpg)
:::

::: main
The annular 2CE spot at θ = 0 is 0.67 of that at θ = π/2 at all NAs, as on the published Fig. 6b, while the text of p. 31 states 0.82.
:::

::: look
Point at the flat curves of the left chart, at the star at 0.82 and at the cross at 0.67, on the curves at NA 0.5.
:::

::: step
[Slide 24]{.slide} [Step 30]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=cmp&cmp=a2&na=0.7){.open} Open the tab “Scalar vs vector at high NA”, set the plot to “paper's comparisons”, set the comparison to “Annular, θ = π/2: 2PE spot narrower than 2CE, 1 − ratio (p. 31)” and click NA 0.7 on the left chart; the other controls stay at their defaults.

![](img_2ce_high_na/h24b.jpg)
:::

::: main
The annular 2PE spot at θ = π/2 is narrower than the 2CE spot by 53% at NA 0.5 and by 34% at NA 0.7 in the paraxial model.
:::

::: look
Point at the falling curves of the left chart, dashed for the paraxial and solid for the vector model; the vector curve lies lower, at 52% and 31%. The star is the 35% stated on p. 31 and the cross the 34% of the published Fig. 6a.
:::

::: deck

These are the bullets of slide 24.

- As NA increases the annular 2CE spot at θ = 0 stays 0.67 of that at θ = π/2, and the annular 2PE spot loses its lead over 2CE: 53% narrower at NA 0.5, 34% at NA 0.7 in air.
- Star: value stated on p. 31; cross: the same ratio on the published curves. 0.82 stated, 0.67 on Fig. 6b; 35% stated, 34% on Fig. 6a, which plots the excitation (Eq. (6) gives 53%).

:::
:::

::: card
::: sl
25
:::

## Annular depth of focus against NA: the comparisons of p. 32

::: say
As NA increases the annular 2CE depth of focus at θ = π/2 stays about 30% shorter than the circular one, and its lead over the 2PE depth of focus shrinks.
:::

::: step
[Slide 25]{.slide} [Step 31]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=cmp&cmp=a3&na=0.7){.open} Open the tab “Scalar vs vector at high NA”, set the plot to “paper's comparisons”, set the comparison to “θ = π/2: 2CE DOF shorter, annular than circular, 1 − ratio (p. 32)” and click NA 0.7 on the left chart; the other controls stay at their defaults.

![](img_2ce_high_na/h25a.jpg)
:::

::: main
The annular 2CE depth of focus at θ = π/2 is about 30% shorter than the circular one at all NAs, while the text of p. 32 states 40%.
:::

::: look
Point at the flat curves of the left chart, the star at 0.40 and the cross at 0.30 on the published curves.
:::

::: step
[Slide 25]{.slide} [Step 32]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=cmp&cmp=a4&na=0.7){.open} Open the tab “Scalar vs vector at high NA”, set the plot to “paper's comparisons”, set the comparison to “θ = π/2: annular 2CE DOF longer than circular 2PE, ratio − 1 (p. 32)” and click NA 0.7 on the left chart; the other controls stay at their defaults.

![](img_2ce_high_na/h25b.jpg)
:::

::: main
The annular 2CE depth of focus at θ = π/2 is longer than the circular 2PE one by 85% at NA 0.5 in the paraxial model and by 81% in the vector model.
:::

::: look
Point at the falling curves of the left chart, which reach 26% at NA 0.7 in the vector model, at the star at the 20% stated on p. 32 and at the cross at 85% on the published curves.
:::

::: deck

These are the bullets of slide 25.

- As NA increases the annular 2CE DOF at θ = π/2 stays about 30% shorter than the circular one, and its lead over the 2PE DOF shrinks: 85% longer at NA 0.5.
- Star: value stated on p. 32; cross: the same ratio on the published curves. 40% stated, 30% on the curves; 20% stated, 85%.

:::
:::

::: card
::: sl
26
:::

## 2CE response to the wavelength gap Δλ against NA, θ = π/2

::: say
As NA increases the effect of the wavelength gap on 2CE at θ = π/2 stays the same, so the trade-off of p. 30 between the central spot and the depth of focus holds at high NA.
:::

::: step
[Slide 26]{.slide} [Step 33]{.num} [Open ↗](http://localhost:4317/#mode=dl&wdir=xz){.open} Open the tab “Wavelength gap Δλ”, set the width to both; the other controls stay at their defaults.

![](img_2ce_high_na/h26.jpg)
:::

::: main
From Δλ = 10 to 94 nm the 2CE central spot at θ = π/2 grows by about 6% and the depth of focus shrinks by about 5%, at NA 0.3 to 0.9, in air and in water.
:::

::: look
Scroll down below the published Figs. 4 and 5 to the two charts “2CE width at θ = π/2 and higher NA, relative to its value at Δλ = 10 nm”. Point at the curves of the different NAs and media, which lie on each other, solid for the vector and dashed for the scalar model.
:::

::: deck

These are the bullets of slide 26.

- As NA increases the effect of Δλ stays the same: from 10 to 94 nm the central spot grows by about 6% and the DOF shrinks by about 5%, from NA 0.3 to 0.9, in air and water.
- At θ = π/2 the central spot follows λ1 and the DOF follows λ2 at all NA, so the trade-off of p. 30 holds.

:::
:::

::: card
::: sl
27
:::

## Largest NA of two crossed lenses

::: say
Two lenses with crossed axes fit side by side while the half-angle of each focusing cone is at most 45°, so their NA is at most 0.71 in air and 0.94 in water.
:::

::: step
[Slide 27]{.slide} [Step 34]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=width&sig=2CE&ths=pi2&axis=x&na=0.7){.open} Open the tab “Scalar vs vector at high NA”, set the plot to width, set the signal to 2CE, set the angles to π/2, set the direction to across and click NA 0.7 on the left chart; the other controls stay at their defaults.

![](img_2ce_high_na/h27.jpg)
:::

::: main
The curve of θ = π/2 ends at NA 0.7 in air, below the NA 0.71 at which the cones of the two lenses touch.
:::

::: look
Point at the end of the curve. Switching the medium to water extends the curve to NA 0.9.
:::

::: deck

These are the bullets of slide 27.

- Two lenses with crossed axes (θ = π/2) fit side by side while the half-angle of each focusing cone is at most 45°, so NA ≤ n sin 45°: 0.71 in air and 0.94 in water.
- Cambaliza & Saloma (2000) note that dual-beam excitation with two identical objectives is possible for NA ≤ 0.7 (p. 34).

:::
:::

::: card
::: sl
28
:::

## Summary: high NA

::: say
The conclusions of Cambaliza & Saloma (2000) hold at high NA, while the differences between 2PE and 2CE shrink and the paraxial model overestimates the depth of focus.
:::

The dashboard has no view of this slide. Say that the vector focus has both beams polarized perpendicular to the plane of the lens axes, that the paraxial error of the depth of focus grows as tan²(α/2) and is about half as large in water as in air at the same NA, and that with annular pupils the paraxial depth of focus is 2.2 times too long at NA 0.9 in air.

::: deck

These are the bullets of slide 28.

- The conclusions of Cambaliza & Saloma hold at high NA, but the differences between 2PE and 2CE shrink.
- 2PE at θ = π/2 stays the sharpest distribution at all NA: its spot is one interference fringe, 0.26 µm in air, while the 2CE spot shrinks with NA, from 2.9 times the 2PE spot at NA 0.5 to 2.0 at NA 0.7.
- The 2PE side lobes weaken with NA, from 0.11 to 0.04 of the peak at θ = π/2 (NA 0.5 to 0.7) and from 0.97 to 0.42 at θ = π (NA 0.5 to 0.9), so 2PE images gain contrast.
- Crossed lenses (θ = π/2) fit only up to NA 0.71 in air and 0.94 in water, the limit of NA 0.7 noted on p. 34.
- The paraxial Eq. (1) gives the right spot width up to NA 0.86 in air, but overestimates the depth of focus above NA 0.43 (by 36% at NA 0.9).

:::
:::

::: {.part}
# Backup (slides 32 to 38)
:::

::: card
::: sl
32
:::

## Whole-profile difference of 2PE, paraxial against vector

::: say
As NA increases the whole paraxial 2PE profile departs from the vector one as 2CE does at θ = 0, and along the axis at θ = π by 7% at NA 0.5 and 29% at NA 0.9 in air.
:::

::: step
[Slide 32]{.slide} [Step 35]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=nrmse&sig=2PE&ths=0.pi2.pi&axis=z&na=0.9){.open} Open the tab “Scalar vs vector at high NA”, set the plot to NRMSE, set the signal to 2PE, set the angles to 0, π/2 and π, set the direction to along and click NA 0.9 on the left chart; the other controls stay at their defaults.

![](img_2ce_high_na/h32.jpg)
:::

::: main
Along the axis the NRMSE of the paraxial 2PE profile is 25% at NA 0.9 with collinear lenses and 29% with facing lenses.
:::

::: look
Point at the curves of θ = 0 and π, which rise with NA, and at the curve of θ = π/2, which stays at 5% or less up to NA 0.7.
:::

::: deck

These are the bullets of slide 32.

- As NA increases the paraxial F2p departs as F2c at θ = 0; along the axis at θ = π by 7% at NA 0.5 and 29% at NA 0.9 in air.
- With crossed lenses it differs by 5% or less: the fringes are set by the wavelength in both models.

:::
:::

::: card
::: sl
33
:::

## Linfoot’s criteria against NA: 2PE, θ = 0

::: say
F~2p~ at θ = 0 departs from the vector focus as F~2c~ at θ = 0, with C below 0.95 from NA 0.44 in air and F below 0.99 from NA 0.63.
:::

::: step
[Slide 33]{.slide} [Step 36]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=C&sig=2PE&ths=0&axis=z&na=0.7){.open} Open the tab “Scalar vs vector at high NA”, set the plot to Linfoot C, set the signal to 2PE, set the angles to 0, set the direction to along and click NA 0.7 on the left chart; the other controls stay at their defaults.

![](img_2ce_high_na/h33.jpg)
:::

::: main
Along the axis the structural content C of 2PE at θ = 0 falls below 0.95 from NA 0.44 in air, as that of 2CE.
:::

::: look
Point at the curve of C against NA and at the NA where it crosses 0.95; at NA 0.7 it is 0.86.
:::

::: deck

These are the bullets of slide 33.

- As NA increases F2p at θ = 0 departs as F2c at θ = 0: along the axis C \< 0.95 from NA 0.44 in air and F \< 0.99 from NA 0.63.
- Across the axis F ≥ 0.996 at all NA.

:::
:::

::: card
::: sl
34
:::

## Linfoot’s criteria against NA: 2PE, θ = π/2

::: say
With crossed lenses the paraxial 2PE keeps the fidelity F at 0.997 or above wherever the lenses fit, while along the axis the structural content C falls to 0.91.
:::

::: step
[Slide 34]{.slide} [Step 37]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=C&sig=2PE&ths=pi2&axis=z&na=0.7){.open} Open the tab “Scalar vs vector at high NA”, set the plot to Linfoot C, set the signal to 2PE, set the angles to π/2, set the direction to along and click NA 0.7 on the left chart; the other controls stay at their defaults.

![](img_2ce_high_na/h34.jpg)
:::

::: main
Along the axis the structural content C of the crossed-lens 2PE is 0.915 at NA 0.7 in air.
:::

::: look
Point at the curve of C and compare it with that of the fidelity F (the plot Linfoot F), which stays at 0.997 or above.
:::

::: deck

These are the bullets of slide 34.

- As NA increases the paraxial F2p at θ = π/2 keeps F ≥ 0.997 wherever the lenses fit.
- Along the axis C falls to 0.91; across the axis F, C and Q stay above 0.97.

:::
:::

::: card
::: sl
35
:::

## Linfoot’s criteria against NA: 2PE, θ = π

::: say
As NA increases the paraxial envelope of the 2PE fringes along the axis with facing lenses becomes too long, so C falls below 0.95 from NA 0.44 in air and F below 0.99 from NA 0.58.
:::

::: step
[Slide 35]{.slide} [Step 38]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=F&sig=2PE&ths=pi&axis=z&na=0.95){.open} Open the tab “Scalar vs vector at high NA”, set the plot to Linfoot F, set the signal to 2PE, set the angles to π, set the direction to along and click NA 0.95 on the left chart; the other controls stay at their defaults.

![](img_2ce_high_na/h35.jpg)
:::

::: main
With facing lenses the fidelity F of the 2PE profile along the axis falls to 0.85 at NA 0.95 in air.
:::

::: look
Point at the curve of F against NA, which leaves 0.99 near NA 0.58, and at the two maps at NA 0.95, where the side fringes of the paraxial map are stronger than those of the vector map.
:::

::: deck

These are the bullets of slide 35.

- As NA increases the paraxial envelope of the F2p(0, 0, z; π) fringes becomes too long: C \< 0.95 from NA 0.44 in air (0.58 in water), F \< 0.99 from NA 0.58 (0.78).
- At NA 0.95 in air F = 0.85, the lowest of all cases.

:::
:::

::: card
::: sl
36
:::

## Axial 2CE PSF at NA 0.5 and NA 0.9: paraxial and vector focus

::: say
At NA 0.9 the paraxial depth of focus of 2CE is 36% longer than the vector one, against 7% at NA 0.5, because the paraxial model uses the small-angle form of the phase of each ray.
:::

::: step
[Slide 36]{.slide} [Step 39]{.num} [Open ↗](http://localhost:4317/#mode=na&metric=gap&sig=2CE&ths=0&axis=z&model=both&na=0.9&hl=cw-scalar-dof){.open} Open the tab “Highlights” and click the card that begins “At NA 0.9 the paraxial 2CE depth”. It opens the tab “Scalar vs vector at high NA”, sets the plot to scalar / vector, sets the signal to 2CE, sets the angles to 0, sets the direction to along, sets the model to both and picks NA 0.9 on the left chart, and brings the plot of the result into view.

![](img_2ce_high_na/h36.jpg)
:::

::: main
At NA 0.9 the paraxial 2CE depth of focus is 1.10 µm, against 0.81 µm for the vector focus.
:::

::: look
Point at the profile along the axis, whose legend gives the two depths of focus, and at the left chart, which gives the scalar width over the vector width minus 1 and reaches 36% at NA 0.9. Clicking NA 0.5 on the left chart gives 3.56 µm against 3.33 µm.
:::

::: deck

These are the bullets of slide 36.

- At NA 0.5, the paraxial scalar and vector 2CE distributions along the axis nearly coincide: the paraxial depth of focus is 7% longer.
- At NA 0.9, the paraxial depth of focus is 36% longer than the vector one (1.10 µm compared to 0.81 µm), because the paraxial model uses the small-angle form of the phase of each ray.

:::
:::

::: card
::: sl
37
:::

## Misalignment for a 20% loss of the 2CE peak against NA, θ = π

::: say
As NA increases, the misalignment that reduces the peak 2CE fluorescence by 20% decreases as about 1/NA across the axis and 1/NA² along it, because it follows the width and the length of the focus.
:::

The dashboard has no view of this slide. Say that the fitted exponents from NA 0.1 to 0.5 are −0.99 across the axis and −2.04 along it. The paraxial model gives a larger tolerated misalignment along the axis than the vector model, by 7% at NA 0.5 and 47% near NA 0.95, and a Gaussian input (α = 4) makes the tolerances about 1.4 times larger.

::: deck

These are the bullets of slide 37.

- As NA increases, the misalignment that reduces the peak 2CE fluorescence by 20% decreases as about 1/NA across the axis and 1/NA² along it, following the width and the length of the focus.
- The paraxial scalar model overestimates the tolerated misalignment along the axis, by 7% at NA 0.5 and by 47% near NA 0.95.

:::
:::

::: card
::: sl
38
:::

## Misalignment for a 20% loss of the 2CE peak against NA, θ = π/2

::: say
With crossed lenses both tolerated misalignments decrease as about 1/NA², because each lies along the length of the focus of one of the two beams.
:::

The dashboard has no view of this slide. Say that the fitted exponents from NA 0.1 to 0.5 are −2.03 and −2.04, and that the vector focus is computed in air up to NA 0.71, where two crossed lenses fit, and in water up to NA 0.94.

::: deck

These are the bullets of slide 38.

- With crossed lenses, both tolerated misalignments decrease as about 1/NA², because each lies along the length of the focus of one of the two beams.
- The vector focus is computed in air up to NA 0.71, where two crossed lenses fit, and in water up to NA 0.94.

:::
:::
