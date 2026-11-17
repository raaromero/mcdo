---
title: "Dashboard guide: two-color excitation at high NA and with optical pulses"
subtitle: "This guide pairs 2ce_high_na_pulses.pptx with the dashboard, slide by slide. The links open the local dashboard on port 4317 until it is deployed again."
---

<!-- Source of high_na_pulses_guide.pdf. The local dashboard is started with npm run dev in dashboard/cambaliza (port 4317). Build: python build.py high_na_pulses (fills each [[id]] from steps_high_na_pulses.json with the
     link, the settings as a sentence and the screenshot; screenshots: node shoot.mjs steps_high_na_pulses.json img_high_na_pulses with
     vite preview on 4173 and headless Chromium on 9333). The steps b46 to b54b of Part 4 use the screenshots of
     steps_delay.json (d03 to d11b), copied from img_delay/. Where a card of the tab Highlights shows the result, the step
     opens that card. Each card is one slide; its title and the bullets in the blue box are those of the deck, word for
     word. No run-in labels or arrows anywhere in this file. -->

::: {.card .story}
::: sl
How
:::

## How to use this guide

- Each card is one slide. Its number is the position of the slide in 2ce_high_na_pulses.pptx, as Keynote and
  PowerPoint count the slides; the number printed in the corner of a slide skips the title slide and the dividers, so
  it is smaller.
- Each step says which tab to open, which controls to set and which point to click; all other controls stay at their
  defaults. The link Open in each step loads all of these settings at once.
- Where a result has a card on the tab Highlights, the step opens that card. Its banner gives the result in one
  sentence, and the dashboard brings the plot of the result into view.
- The yellow box under the title of each slide states the main result of that slide. The yellow box under each
  screenshot states the main point of the step, and the text below it says what to point at. The blue box repeats the
  bullets of the slide.
- The slides of Part 1, the focus of one beam with the Richards–Wolf theory, have no view in the dashboard, and neither
  do the slides on the misalignment and the aberration of the two foci in Part 2 (slides 16 to 20). Their cards give the
  main result and what to say.
:::

::: {.part}
# 1. Replication of Romallosa et al. (2003) and its extension to Gaussian input and annular pupils: intensity distribution near focus with the Richards–Wolf theory (slides 4 to 11)
:::

::: card
::: sl
4
:::

## Intensity distributions near focus with a 1-fs pulse, NA 0.8

::: say
With a 1-fs pulse the intensity distributions near focus have no zero points, and current work reproduces the
distributions of Romallosa et al. (2003).
:::

The dashboard has no view of this slide. Say that the left panel is the transverse distribution at z = 0 and the right
panel the axial distribution at r = 0, for 750 nm, NA 0.8 and n = 1.3, with a continuous beam and a 1-fs pulse. The
structural content of the axial distribution at 1 fs is 1.058, compared to 1.057 published, and the transverse FWHM is
472.8 nm. The remaining differences are within 1% for Fig. 4 and about 3% for Fig. 3 at 1 fs.

::: deck

These are the bullets of slide 4.

- With a 1-fs pulse, the transverse and axial intensity distributions contain no zero points and decrease more slowly from the maximum at the geometrical focus than with a continuous beam.
- The distributions of Romallosa et al. (2003) are reproduced: the structural content of the axial distribution at 1 fs is 1.058, compared to 1.057 published.

:::
:::

::: card
::: sl
5
:::

## Fidelity and structural content against NA and pulse width

::: say
The fidelity and the structural content of the pulsed distribution do not depend on NA, and they deteriorate for
pulses shorter than about 2 fs, because the spectral bandwidth increases as the pulse width decreases.
:::

The dashboard has no view of this slide. Say that the left panel gives the criteria at 1 fs against NA and the right
panel the criteria against the pulse width at NA 0.8, as in Fig. 4 of Romallosa et al. (2003). The criteria do not
depend on NA because the Linfoot arrays are in optical coordinates.

::: deck

These are the bullets of slide 5.

- At a pulse width of 1 fs, the fidelity F and the structural content S of the pulsed distribution relative to the continuous-beam one are insensitive to NA from 0.1 to 1.2, as reported by Romallosa et al. (2003).
- At NA 0.8, F and S stay within about 1% of unity for pulse widths down to 2 fs and deteriorate rapidly for shorter pulses, because the spectral bandwidth increases as the pulse width decreases.

:::
:::

::: card
::: sl
6
:::

## Focal spot FWHM against NA: scalar Debye and vector theory

::: say
As NA increases the vector focal spot becomes wider than the scalar Debye spot, first along the polarization, because
of the longitudinal field component E~z~.
:::

The dashboard has no view of this slide. Say that at NA 0.1 the vector theory, the scalar Debye integral and the Airy
pattern agree to 1e-4. Along the polarization the FWHM of the two theories differs by 1% at NA 0.30 and by 5% at
NA 0.60, while along the axis the difference reaches 1% at NA 1.15. The right panel shows the three field components at
NA 1.2.

::: deck

These are the bullets of slide 6.

- As NA increases, the FWHM of the vector focal spot in optical units rises above the Airy value of 3.23, while that of the scalar Debye spot falls below it.
- The vector spot is wider because of the longitudinal field component E~z~, which is largest along the polarization and fills the zero points of the transverse intensity (right, NA 1.2).

:::
:::

::: card
::: sl
7
:::

## Transverse intensity distribution at NA 0.3 and NA 0.9

::: say
At NA 0.9 the vector distribution along the polarization is 14% wider than the scalar one and has no zero points,
because E~z~ is largest in that direction.
:::

The dashboard has no view of this slide. Say that at NA 0.3 the FWHM along the polarization is 3.27 in optical units
against 3.23 for the scalar field, about 1% wider. At NA 0.9 it is 3.62 against 3.19, and the first zero along the
polarization is filled to 1e-2 of the peak. Across the polarization the vector spot keeps its zeros, because E~z~ is
zero in that direction.

::: deck

These are the bullets of slide 7.

- At NA 0.3, the scalar Debye and vector intensity distributions coincide; along the polarization, the vector FWHM is about 1% larger.
- At NA 0.9, the vector distribution along the polarization is 14% wider than the scalar one and has no zero points, because the longitudinal field component E~z~ is largest in that direction; across the polarization the two coincide.

:::
:::

::: card
::: sl
8
:::

## Gaussian and uniform input: vector against scalar focal width

::: say
A Gaussian input with truncation parameter α = 4 keeps scalar theory accurate up to a higher NA than uniform input,
because it gives less weight to the marginal rays.
:::

The dashboard has no view of this slide. Say that for uniform input the deviation of the vector focal width from the
scalar one passes 1% near NA 0.45 and 5% near NA 0.90, and for α = 4 near NA 0.55 and 1.15. Along the polarization the
1% and 5% points are NA 0.40 and 0.85 for α = 4, against 0.30 and 0.60 for uniform input. The right panel shows the
profile along the axis at NA 0.9.

::: deck

These are the bullets of slide 8.

- As NA increases, the FWHM of the vector focal spot deviates from that of scalar theory; with a Gaussian input of truncation parameter α = 4, the deviation is smaller than with uniform input at all NAs.
- A Gaussian input gives less weight to the marginal rays, so scalar theory stays accurate up to a higher NA and the depth of focus is longer (right, NA 0.9).

:::
:::

::: card
::: sl
9
:::

## Annular pupils: depth of focus and peak intensity against ε

::: say
An annular pupil lengthens the depth of focus as 1/(1 − ε²) at low NA and lowers the peak intensity as (1 − ε²)²,
because the field at the focus is proportional to the open area of the pupil.
:::

The dashboard has no view of this slide. Say that the field of an annular pupil is the field of the full pupil minus
that of the obstructed part. At ε = 0.99 the depth of focus over that of the full pupil is 50.13 at low NA, against
50.25 from 1/(1 − ε²), and 30.4 at sin α = 0.9.

::: deck

These are the bullets of slide 9.

- As the obstruction ratio ε increases, the depth of focus of an annular pupil grows as 1/(1 − ε²) at low NA; at high NA (sin α = 0.9) it grows more slowly.
- The peak intensity decreases as (1 − ε²)² at low and at high NA, because the field at the focus is proportional to the open area of the pupil.

:::
:::

::: card
::: sl
10
:::

## Annular pupils with few-cycle pulses: depth of focus

::: say
Few-cycle pulses retain the longer depth of focus of an annular pupil: at ε = 0.99 and 1 fs it is within about 1% of
its continuous-beam value.
:::

The dashboard has no view of this slide. Say that at NA 0.8 and ε = 0.99 the depth of focus over that of the full pupil
is 44.35 for a continuous beam and 44.33 at 1 fs. Along the axis the focus at 1 fs is 1.010 times longer than with a
continuous beam.

::: deck

These are the bullets of slide 10.

- The extension of the depth of focus by an annular pupil is retained with few-cycle pulses: at ε = 0.99, the depth of focus at 1 fs is within about 1% of its continuous-beam value.
- Beyond the half-maximum point, the axial intensity decreases more slowly as the pulse width decreases (right), as with the circular pupil.

:::
:::

::: card
::: sl
11
:::

## Transverse intensity distribution with few-cycle pulses

::: say
As the pulse width decreases from 5 fs to 1 fs, the zero points between the transverse rings fill in, for the circular
pupil and for the annular pupil.
:::

The dashboard has no view of this slide. Say that the structural content across the axis is about 1.06 at 1 fs for both
pupils, so the loss of contrast that Romallosa et al. (2003) report for the circular pupil also occurs with annular
pupils.

::: deck

These are the bullets of slide 11.

- As the pulse width decreases from 5 fs to 1 fs, the zero points of the transverse intensity distribution fill in and the contrast of the rings decreases, for the circular pupil (left) and the annular pupil with ε = 0.99 (right).
- The loss of contrast reported by Romallosa et al. (2003) for the circular pupil therefore also occurs with annular pupils.

:::
:::

::: {.part}
# 2. Two-color excitation with continuous beams: replication of Cambaliza & Saloma (2000) and Lim & Saloma (2002, 2003), and extension to high NA (slides 13 to 28)
:::

::: card
::: sl
13
:::

## Two-color excitation with two confocal beams at an angle θ

::: say
2CE absorbs one photon of each color, so it forms where the two beams overlap and its signal is the product of the two
intensities.
:::

[[b13|13]]

::: main
The tab Focal spot shows the two foci and the 2CE and 2PE maps at any angle θ.
:::

::: look
Point at the setup drawing at the top, where L2 is L1 rotated by θ about the focus. Then move the angle slider from 0
to 180°: the 2CE map changes from a long focus to a small crossed region and back to a long focus.
:::

::: deck

These are the bullets of slide 13.

- Lens L2 is lens L1 rotated by θ about the common focus O; L1 focuses 750 nm and L2 656 nm.
- 2CE absorbs one photon of each color, so the signal is the product of the two intensities.
- 2PE uses 700 nm in both beams, so the two fields add first and interfere.

The line under the equations reads as follows.

> where λ~e~ = 350 nm; I~1~ and I~2~ are the focused intensities and U~1~ and U~2~ the fields; θ = 0, π/2 and π are collinear, crossed and facing lenses.

:::
:::

::: card
::: sl
14
:::

## Transverse 2CE PSF, circular pupils, NA 0.5: θ = 0, π/2 and π

::: say
Current work lies on the transverse 2CE curves of Cambaliza & Saloma (2000), and with crossed lenses the central spot is
wider than with collinear and facing lenses.
:::

[[b14|14]]

::: main
With crossed lenses the 2CE spot is 0.763 µm wide, against 0.516 µm with collinear and facing lenses.
:::

::: look
Point at the left chart, which gives the width across the axis against θ, at θ = 90°, and then at the published
Fig. 2b below the view.
:::

::: deck

These are the bullets of slide 14.

- At θ = 0 and π, the transverse 2CE distributions are identical and nearly equal to the 2PE distribution at θ = 0.
- At θ = π/2, the central spot is wider and shows no second-order interference effects, so 2CE with circular pupils does not offer a definite advantage in transverse resolution (Cambaliza & Saloma, 2000, p. 29).

:::
:::

::: card
::: sl
15
:::

## Axial 2CE PSF, circular pupils, NA 0.5: θ = 0, π/2 and π

::: say
With crossed lenses the 2CE depth of focus is shorter than with collinear and facing lenses, and the 2CE side lobes are
weaker than those of 2PE.
:::

[[b15|15]]

::: main
With crossed lenses the 2CE depth of focus is 0.67 µm, against 3.56 µm with collinear and facing lenses.
:::

::: look
The left chart now gives the width along the axis against θ, and the published Fig. 3b is below the view.
:::

::: deck

These are the bullets of slide 15.

- At θ = 0 and π, the axial 2CE distributions are identical and nearly equal to the 2PE distribution at θ = 0.
- At θ = π/2, the 2CE distribution has weaker side lobes than the 2PE one, but a broader depth of focus (Cambaliza & Saloma, 2000, p. 30).

:::
:::

::: card
::: sl
16
:::

## Peak 2CE fluorescence against misalignment of the foci, θ = π

::: say
With facing lenses the peak 2CE fluorescence tolerates a larger misalignment along the axis than across it, because the
focus is longer than it is wide.
:::

The dashboard has no view of this slide. Say that in the paraxial scalar model at NA 0.5, with x~c~ and z~c~ in units of
λ~1~, the fits of current work are −0.601 x~c~² + 0.888 across the axis and −0.027 z~c~² + 0.998 along it.

::: deck

These are the bullets of slide 16.

- With facing lenses, a misalignment of 0.37 λ~1~ across the axis of L1 reduces the peak 2CE fluorescence by 18%, compared to the 20% reported by Lim & Saloma (2002).
- Along the axis, a misalignment of 2.7 λ~1~ reduces the peak by 19%, because the focus is longer than it is wide.

:::
:::

::: card
::: sl
17
:::

## Peak 2CE fluorescence against misalignment of the foci, θ = π/2

::: say
With crossed lenses a misalignment within the focal plane of L1 reduces the peak 2CE fluorescence more slowly than with
facing lenses, because it lies along the axis of L2, where its focus is long.
:::

The dashboard has no view of this slide. Say that across the axis the fit of current work is −0.063 x~c~² + 0.999,
against −0.06 x~c~² + 1 in Lim & Saloma (2002), and that along the axis it is −0.045 z~c~² + 0.995, against
−0.045 z~c~² + 0.986.

::: deck

These are the bullets of slide 17.

- With crossed lenses, a misalignment of 1.33 λ~1~ within the focal plane of L1 reduces the peak 2CE fluorescence by 11%, as reported by Lim & Saloma (2002).
- Within the focal plane of L1, the peak deteriorates at a slower rate than with facing lenses, because the misalignment lies along the axis of L2, where its focus is long.

:::
:::

::: card
::: sl
18
:::

## Peak 2CE fluorescence against spherical aberration, θ = 0 and π

::: say
Spherical aberration of the same sign in the two beams keeps the peak 2CE fluorescence with collinear lenses, and
aberration of the opposite sign keeps it with facing lenses.
:::

The dashboard has no view of this slide. Say that at θ = 0 the peak at φ~1~ = φ~2~ = ±60 is 0.84 of the peak without
aberration, and at φ~1~ = −φ~2~ = ±60 it is 0.07; at θ = π the two cases are exchanged. With crossed lenses the 2CE
fidelity stays above 0.9 for coefficients up to 40, as in Lim & Saloma (2003).

::: deck

These are the bullets of slide 18.

- At θ = 0, the decrease of the peak 2CE fluorescence due to the spherical aberration of one beam is compensated by an aberration of the same magnitude and sign in the other beam (φ~1~ = φ~2~).
- At θ = π, it is compensated by an aberration of the same magnitude and opposite sign (φ~1~ = −φ~2~), as reported by Lim & Saloma (2003).

:::
:::

::: card
::: sl
19
:::

## Misalignment for a 20% loss of the 2CE peak against NA, θ = π

::: say
As NA increases, the misalignment that reduces the peak 2CE fluorescence by 20% decreases as about 1/NA across the axis
and 1/NA² along it, because it follows the width and the length of the focus.
:::

The dashboard has no view of this slide. Say that the fitted exponents from NA 0.1 to 0.5 are −0.99 across the axis and
−2.04 along it. The paraxial model gives a larger tolerated misalignment along the axis than the vector model, by 7% at
NA 0.5 and 47% near NA 0.95, and a Gaussian input (α = 4) makes the tolerances about 1.4 times larger.

::: deck

These are the bullets of slide 19.

- As NA increases, the misalignment that reduces the peak 2CE fluorescence by 20% decreases as about 1/NA across the axis and 1/NA² along it, following the width and the length of the focus.
- The paraxial scalar model overestimates the tolerated misalignment along the axis, by 7% at NA 0.5 and by 47% near NA 0.95.

:::
:::

::: card
::: sl
20
:::

## Misalignment for a 20% loss of the 2CE peak against NA, θ = π/2

::: say
With crossed lenses both tolerated misalignments decrease as about 1/NA², because each lies along the length of the
focus of one of the two beams.
:::

The dashboard has no view of this slide. Say that the fitted exponents from NA 0.1 to 0.5 are −2.03 and −2.04, and that
the vector focus is computed in air up to NA 0.71, where two crossed lenses fit, and in water up to NA 0.94.

::: deck

These are the bullets of slide 20.

- With crossed lenses, both tolerated misalignments decrease as about 1/NA², because each lies along the length of the focus of one of the two beams.
- The vector focus is computed in air up to NA 0.71, where two crossed lenses fit, and in water up to NA 0.94.

:::
:::

::: card
::: sl
21
:::

## Central spot and depth of focus against NA: 2CE, θ = 0 and π

::: say
As NA increases the paraxial depth of focus of 2CE shrinks more slowly than the vector one, so it is 5% longer from
NA 0.43 in air, while the central spot stays within 5% up to NA 0.86.
:::

[[b21|21]]

::: main
In the vector model the 2CE depth of focus is 3.33 µm at NA 0.5 and 0.81 µm at NA 0.9.
:::

::: look
Point at the left chart, which gives the depth of focus against NA on log axes: the dashed scalar curve lies above the
solid vector curve from about NA 0.4. The profiles at NA 0.9 are on the right.
:::

::: deck

These are the bullets of slide 21.

- As NA increases both widths shrink, but the paraxial depth of focus shrinks more slowly than the vector one and becomes too long.
- The paraxial depth of focus of F~2c~(0, 0, z; 0) is 5% longer from NA 0.43 in air (0.57 in water), below the NA 0.7 stated by Cambaliza & Saloma (2000, p. 27); the central spot stays within 5% up to NA 0.86.

:::
:::

::: card
::: sl
22
:::

## Axial 2CE PSF at NA 0.5 and NA 0.9: paraxial and vector focus

::: say
At NA 0.9 the paraxial depth of focus of 2CE is 36% longer than the vector one, against 7% at NA 0.5, because the
paraxial model uses the small-angle form of the phase of each ray.
:::

[[b22|22]]

::: main
At NA 0.9 the paraxial 2CE depth of focus is 1.10 µm, against 0.81 µm for the vector focus.
:::

::: look
Point at the profile along the axis, whose legend gives the two depths of focus, and at the left chart, which gives the
scalar width over the vector width minus 1 and reaches 36% at NA 0.9. Clicking NA 0.5 on the left chart gives 3.56 µm
against 3.33 µm.
:::

::: deck

These are the bullets of slide 22.

- At NA 0.5, the paraxial scalar and vector 2CE distributions along the axis nearly coincide: the paraxial depth of focus is 7% longer.
- At NA 0.9, the paraxial depth of focus is 36% longer than the vector one (1.10 µm compared to 0.81 µm), because the paraxial model uses the small-angle form of the phase of each ray.

:::
:::

::: card
::: sl
23
:::

## Central spot and depth of focus against NA: 2CE, θ = π/2

::: say
With crossed lenses both 2CE widths shrink as NA increases, and the paraxial model follows the vector focus within 4%,
because each width is set by the narrow transverse spot of the other beam.
:::

[[b23|23]]

::: main
With crossed lenses the 2CE depth of focus is 13 times shorter than with collinear lenses at NA 0.2, and 3.4 times
shorter at NA 0.7.
:::

::: look
Point at the two curves of the left chart, θ = 0 above and θ = π/2 below, and at the gap between them, which narrows as
NA increases.
:::

::: deck

These are the bullets of slide 23.

- As NA increases both widths of F~2c~ at θ = π/2 shrink, and the paraxial model follows the vector focus within 4% wherever crossed lenses fit (NA 0.71 in air, 0.94 in water).
- Each width is set by the narrow transverse spot of the other beam, which the paraxial model reproduces.

:::
:::

::: card
::: sl
24
:::

## Paraxial over vector widths of 2CE against NA

::: say
As NA increases the paraxial 2CE widths become larger than the vector ones, first along the axis, where the difference
reaches 5% at NA 0.43 in air.
:::

[[b24|24]]

::: main
Along the axis the difference passes 5% at NA 0.43 in air with collinear and facing lenses, and it stays within 4% with
crossed lenses.
:::

::: look
Point at the grey band of ±5% and at the NA where the curves of θ = 0 and π leave it; the curve of θ = π/2 stays inside
the band. Switching the direction to across moves the 5% point to NA 0.86.
:::

::: deck

These are the bullets of slide 24.

- As NA increases the paraxial 2CE widths become larger than the vector ones, first along the axis.
- Along the axis at θ = 0 and π the difference reaches 5% at NA 0.43 in air (0.57 in water); across the axis at NA 0.86 (1.14); with crossed lenses it stays within 4%.

:::
:::

::: card
::: sl
25
:::

## Linfoot's criteria against NA: 2CE, θ = 0 and π

::: say
As NA increases the paraxial 2CE along the axis becomes longer and lower than the vector one, so the structural content C
falls first, below 0.95 from NA 0.44 in air.
:::

[[b25|25]]

::: main
With collinear and facing lenses the structural content C along the axis falls below 0.95 from NA 0.44 in air.
:::

::: look
Point at the curve of C against NA and at the NA where it crosses 0.95.
:::

::: deck

These are the bullets of slide 25.

- As NA increases, the paraxial F~2c~(0, 0, z; π) becomes longer and lower than the vector one, so the structural content C falls first: below 0.95 from NA 0.44 in air (0.58 in water).
- The fidelity F stays above 0.99 up to NA 0.63 (0.84 in water); across the axis, F ≥ 0.996 at all NA.

:::
:::

::: card
::: sl
26
:::

## Linfoot's criteria against NA: 2CE, θ = π/2

::: say
With crossed lenses the paraxial and vector 2CE stay alike wherever the lenses fit, with F ≥ 0.999, C ≥ 0.97 and
Q ≥ 0.98.
:::

[[b26|26]]

::: main
With crossed lenses the fidelity F stays at 0.999 or above wherever the lenses fit.
:::

::: look
Point at the curve of F against NA, which ends at NA 0.71 in air, where the cones of the two lenses touch.
:::

::: deck

These are the bullets of slide 26.

- As NA increases the paraxial and vector F~2c~ at θ = π/2 stay alike: F ≥ 0.999, C ≥ 0.97 and Q ≥ 0.98 wherever crossed lenses fit (NA 0.71 in air, 0.94 in water).
- With crossed lenses, the paraxial model gives the profiles of the vector focus.

:::
:::

::: card
::: sl
27
:::

## Annular pupils: depth of focus against NA, air

::: say
As NA increases the paraxial depth of focus of an annular pupil departs from the vector one sooner than that of the
circular pupil, because a thin ring uses the edge of the pupil, where the paraxial phase error is largest.
:::

[[b27|27]]

::: main
With the annular pupil of ε = 0.99 the paraxial depth of focus is 15% too long at NA 0.5 and 2.2 times too long at
NA 0.9.
:::

::: look
Point at the gap between the dashed scalar curve and the solid vector curve at NA 0.9, which the slide gives as 55 µm
against 25 µm.
:::

::: deck

These are the bullets of slide 27.

- As NA increases the paraxial annular depth of focus departs sooner than the circular one: 15% too long at NA 0.5 and 2.2 times at NA 0.9 in air.
- A thin ring uses the edge of the pupil, where the paraxial phase error is largest.

:::
:::

::: card
::: sl
28
:::

## Largest NA of two crossed lenses

::: say
Two lenses with crossed axes fit side by side while the half-angle of each focusing cone is at most 45°, so their NA is
at most 0.71 in air and 0.94 in water.
:::

[[b28|28]]

::: main
The curve of θ = π/2 ends at NA 0.71 in air, where the cones of the two lenses touch.
:::

::: look
Point at the end of the curve. Switching the medium to water extends the curve to NA 0.94.
:::

::: deck

These are the bullets of slide 28.

- Two lenses with crossed axes (θ = π/2) fit side by side while the half-angle of each focusing cone is at most 45°, so NA ≤ n sin 45°: 0.71 in air and 0.94 in water.
- Cambaliza & Saloma (2000) note that dual-beam excitation with two identical objectives is possible for NA ≤ 0.7 (p. 34).

:::
:::

::: {.part}
# 3. Extension to optical pulses: 2PE and 2CE point spread functions with transform-limited femtosecond pulses (slides 30 to 44)
:::

::: card
::: sl
30
:::

## An optical pulse in time

::: say
A short pulse has a Gaussian spectrum about its carrier frequency, and each frequency of the spectrum is a continuous
wave.
:::

[[b30|30]]

::: main
The spectra of the two 10-fs pulses are Gaussians centred at 400 THz (750 nm) and 457 THz (656 nm).
:::

::: look
Point at the chart “Spectrum arriving at the focus now”: the dashed curves are the full spectra, and the solid curves
are the part of each spectrum that reaches the focus at this instant.
:::

::: deck

These are the bullets of slide 30.

- The optical spectrum of a short pulse is a Gaussian in frequency about the carrier frequency (left), and each frequency is a continuous wave (right).

:::
:::

::: card
::: sl
31
:::

## Sum of the frequencies of a 10-fs optical pulse

::: say
At t = 0 the frequencies are in phase and add up, and away from t = 0 they drift out of phase, so their sum is a pulse
of width τ.
:::

[[b31|31]]

::: main
The two pulses pass the focus as short packets of intensity, one from each lens.
:::

::: look
Point at the chart of I~1~ and I~2~ along the axis, and press Play to show the two pulses moving through the focus.
:::

::: deck

These are the bullets of slide 31.

- At t = 0 all the frequencies are in phase and add up; away from t = 0 they drift out of phase, so their sum falls off as a Gaussian of width τ, the pulse.

:::
:::

::: card
::: sl
32
:::

## Pulse width and spectral bandwidth

::: say
A transform-limited Gaussian pulse has a spectral bandwidth Δν = 0.441/τ, so a shorter pulse has a wider spectrum.
:::

[[b32|32]]

::: main
At 20 fs the two spectra barely reach 700 nm.
:::

::: look
In the spectrum chart, both spectra have fallen almost to zero at the line at 428 THz, which is 700 nm.
:::

::: deck

These are the bullets of slide 32.

- A transform-limited Gaussian pulse is Gaussian in time (left) and in frequency (right), with spectral bandwidth Δν = 0.441/τ.

:::
:::

::: card
::: sl
33
:::

## Pulse spectra against wavelength, τ = 5, 10, 20 and 100 fs

::: say
Below about 15 fs the spectra reach 700 nm, where two photons of one pulse add up to 350 nm.
:::

[[b33|33]]

::: main
At 5 fs the two spectra overlap strongly at 700 nm.
:::

::: look
Both spectra cross the line at 428 THz at well above a third of their peak, so two photons of one pulse can reach the
350-nm level.
:::

::: deck

These are the bullets of slide 33.

- Against wavelength, both colors lie at the red edge of the visible range.
- Below about 15 fs the spectra reach 700 nm, where two photons of one pulse add up to 350 nm.

:::
:::

::: card
::: sl
34
:::

## Photon pairs that excite the 350-nm level

::: say
The excitation adds the amplitudes of all photon pairs that sum to the 350-nm level and then squares the total, so the
375- and 328-nm pairs enter beside the 350-nm pairs.
:::

[[b34|34]]

::: main
At 10 fs the 375- and 328-nm pairs add a visible part to the signal of the 350-nm pairs.
:::

::: look
Point at the chart “Pair sums at the focus, accumulated up to t”, where each kind of pair has its own curve.
:::

::: deck

These are the bullets of slide 34.

- Each lens focuses a transform-limited Gaussian pulse of width τ; the centres of both pulses reach the focus at t = 0.
- The excitation adds the amplitudes of all photon pairs that sum to the 350-nm level, then squares the total: the 350-nm pairs (750 + 656 nm), the 375-nm pairs (750 + 750 nm) and the 328-nm pairs (656 + 656 nm).

The line under the equations reads as follows.

> where E~1~ and E~2~ are the fields of the 750- and 656-nm pulses at a point, ω~e~ is the frequency of the 350-nm level and F is the total 2CE accumulated as the pulses pass the focus. For long pulses F becomes I~1~ I~2~, the result of Cambaliza & Saloma (2000).

:::
:::

::: card
::: sl
35
:::

## 2CE with 100-fs pulses and with continuous beams, θ = 0 and π

::: say
At 100 fs the pulsed 2CE along the axis is the same as with continuous beams, with collinear and with facing lenses.
:::

[[b35|35]]

::: main
With facing lenses the 100-fs profile along the axis lies on the continuous-beam profile.
:::

::: look
Point at the profile at τ = 100 fs: the red total and the dashed continuous-beam curve coincide, with depths of focus of
3.52 µm and 3.56 µm on the slide.
:::

::: deck

These are the bullets of slide 35.

- At 100 fs, the pulsed 2CE distribution along the axis is the same as with continuous beams, with collinear (θ = 0) and with facing (θ = π) lenses.

:::
:::

::: card
::: sl
36
:::

## 2CE with 100-fs pulses and with continuous beams, θ = π/2

::: say
At 100 fs pulsed 2CE is the same as with continuous beams at the three lens angles, so the continuous-beam results of
Cambaliza & Saloma (2000) hold for pulses of that length.
:::

[[b36|36]]

::: main
With crossed lenses the 100-fs profile across the axis lies on the continuous-beam profile.
:::

::: look
The red total and the dashed continuous-beam curve coincide across the axis, with a width of 0.76 µm.
:::

::: deck

These are the bullets of slide 36.

- At 100 fs, pulsed 2CE is the same as with continuous beams at all three lens angles, so the continuous-beam results of Cambaliza & Saloma (2000) hold for pulses of that length.

:::
:::

::: card
::: sl
37
:::

## Depth of focus, collinear and crossed lenses

::: say
With collinear and crossed lenses pulsed 2CE keeps the continuous-beam depth of focus and spot to within a few percent,
because the pulses overlap over the whole focus.
:::

[[b37|37]]

::: main
With collinear lenses the width along the axis does not change with τ.
:::

::: look
Point at the three width charts against τ. With θ = 0 and π/2 the curve “through the fringe crests” (orange) stays
within a few percent of the dashed continuous-beam line, while with θ = π it falls at short pulses.
:::

::: deck

These are the bullets of slide 37.

- With collinear and crossed lenses, pulsed 2CE keeps the continuous-beam depth of focus and spot to within a few percent, because the pulses overlap over the whole focus.
- Crossed lenses therefore keep the sharpest profiles, as with continuous beams.

:::
:::

::: card
::: sl
38
:::

## Depth of focus, facing lenses

::: say
With facing lenses pulsed 2CE forms where the two pulses meet, so its depth of focus is shorter than with continuous
beams, and the shortening is larger at lower NA.
:::

[[b38|38]]

::: main
At NA 0.5 in the scalar model the 2CE depth of focus is 3.56 µm for continuous beams and 2.81 µm at 20 fs.
:::

::: look
Point at the width along the axis against τ at θ = π, and at the profile at 20 fs beside it.
:::

::: deck

These are the bullets of slide 38.

- With facing lenses, pulsed 2CE forms where the two pulses meet, so its depth of focus is shorter than with continuous beams.
- The shortening is larger at lower NA, because the continuous-beam focus grows while the stretch where the pulses meet stays the same.

:::
:::

::: card
::: sl
39
:::

## Overlap in time of the two facing pulses

::: say
The facing pulses overlap in time over a stretch of cτ/√2 about the focus, 4.2 µm at 20 fs, and the pulsed 2CE is the
continuous-beam profile times this overlap.
:::

[[b39|39]]

::: main
At 20 fs the total 2CE along the axis is shorter than the continuous-beam profile.
:::

::: look
Point at the red total and the dashed continuous-beam curve. The overlap of the pulses, 4.2 µm wide at 20 fs, shortens
the depth of focus to 2.78 µm with all pairs.
:::

::: deck

These are the bullets of slide 39.

- Pulse 1 passes a point z at t = z/c and pulse 2 at t = −z/c, so their intensities overlap in time over a stretch of cτ/√2 about the focus, 4.2 µm at 20 fs.
- The pulsed 2CE is the continuous-beam profile times this overlap: at 20 fs the product gives 2.74 µm and the full calculation 2.78 µm.

:::
:::

::: card
::: sl
40
:::

## Signal added by the 375- and 328-nm pairs

::: say
Below about 15 fs two photons of one pulse also excite the 350-nm level, so one beam alone excites and 2CE starts to
lose the weak background of continuous beams.
:::

[[b40|40]]

::: main
The signal added by the 375- and 328-nm pairs rises steeply as the pulse width decreases below 15 fs.
:::

::: look
Point at the chart “Signal added by the 375- and 328-nm pairs” on its log axes. The total over the 350-nm pairs is 1.02
at 20 fs and 1.73 at 10 fs, as on the slide.
:::

::: deck

These are the bullets of slide 40.

- Below about 15 fs the spectra reach 700 nm, so two photons of one pulse also excite the 350-nm level, through the 375- and 328-nm pairs.
- Their amplitude interferes with that of the 350-nm pairs, which gives the fringes, and one beam alone now excites, so 2CE starts to lose the weak background of continuous beams.

:::
:::

::: card
::: sl
41
:::

## Pulse width that matches continuous beams against NA, θ = π

::: say
With facing lenses the pulse width needed to match continuous beams grows as NA decreases, because a lower NA gives a
longer focus for the pulses to overlap over.
:::

[[b41|41]]

::: main
With facing lenses in air the pulse width needed is about 25 fs at NA 0.9, 87 fs at NA 0.5 and 610 fs at NA 0.2.
:::

::: look
Point at the chart of the pulse width against NA, with curves for air, water and oil. The curves of water and oil lie
at a higher NA for the same pulse width, so at the same NA they need a longer pulse.
:::

::: deck

These are the bullets of slide 41.

- With facing lenses, the pulsed 2CE matches the continuous-beam 2CE once the pulses are longer than about 25 fs at NA 0.9, 87 fs at NA 0.5 and 264 fs at NA 0.3 in air, because a lower NA gives a longer focus for the pulses to overlap over.
- In water and in oil a longer pulse is needed at the same NA (164 fs and 216 fs at NA 0.5), because the focus is longer in a medium of higher refractive index.

:::
:::

::: card
::: sl
42
:::

## Pulse width that matches continuous beams, θ = 0 and π/2

::: say
With collinear lenses pulsed 2CE matches continuous beams down to 4 fs, and with crossed lenses it matches once the
pulses are longer than about 28 fs at NA 0.2 and 21 fs at NA 0.7.
:::

[[b42|42]]

::: main
With crossed lenses 2CE matches continuous beams from about 20 to 28 fs, from NA 0.2 up.
:::

::: look
The same chart at θ = π/2 is nearly flat. At θ = 0 it lies at 4 fs, the shortest pulse computed.
:::

::: deck

These are the bullets of slide 42.

- With collinear lenses, the pulsed 2CE matches the continuous-beam 2CE at all pulse widths computed, down to 4 fs, because the two pulses travel together and overlap over the whole focus.
- With crossed lenses, it matches once the pulses are longer than about 28 fs at NA 0.2 and 21 fs at NA 0.7.

:::
:::

::: card
::: sl
43
:::

## Pulse width that matches continuous beams: pupils, θ = π

::: say
With facing lenses a pupil or an input that gives a longer depth of focus needs a longer pulse to match continuous
beams.
:::

[[b43|43]]

::: main
At NA 0.5 the annular pupil with ε = 0.9 needs 405 fs by the largest difference between the profiles, against 87 fs for
the circular pupil. By the depth of focus, the measure of the slide, the two are 466 fs and 100 fs.
:::

::: look
Point at the largest difference against τ for the annular pupil, with one curve per NA, and at the pulse width where
each curve falls below 1%.
:::

::: deck

These are the bullets of slide 43.

- With facing lenses, a pupil or an input that gives a longer depth of focus needs a longer pulse to match continuous beams: at NA 0.5, 100 fs for the circular pupil, 162 fs for the Gaussian input (α = 4) and 466 fs for the annular pupil with ε = 0.9.

:::
:::

::: card
::: sl
44
:::

## Pulse width that matches continuous beams: pupils, θ = 0, π/2

::: say
With collinear lenses the 2CE depth of focus matches continuous beams at all pulse widths computed, and with crossed
lenses it matches from about 11 to 16 fs at NA 0.4 and above, for all pupils and inputs.
:::

[[b44|44]]

::: main
With crossed lenses the depth of focus of the annular pupil matches continuous beams from about 15 fs.
:::

::: look
Point at the curves of the depth of focus against τ at θ = π/2, which reach the line at 1 from about 15 fs.
:::

::: deck

These are the bullets of slide 44.

- With collinear lenses, the 2CE depth of focus matches its continuous-beam value at all pulse widths computed, for all pupils and inputs.
- With crossed lenses, it matches once the pulses are longer than about 11 to 16 fs at NA 0.4 and above, for all pupils and inputs.

:::
:::

::: {.part}
# 4. Delay between the two pulses: peak 2CE fluorescence against a misalignment of the two pulses in time, at θ = 0, π/2 and π (slides 46 to 54)
:::

::: card
::: sl
46
:::

## Delay between the two pulses and their temporal overlap

::: say
At a fixed point the peak 2CE fluorescence of the 350-nm pairs decreases with the delay as the temporal overlap of the
two pulses: a delay of 0.40 τ reduces the peak by 20%, and a delay of τ by 75%.
:::

[[b46|46]]

::: main
With collinear lenses the peak 2CE fluorescence follows the temporal overlap at all NAs.
:::

::: look
Point at the chart of the peak against Δt/τ: the curves of the six NAs lie on the dotted temporal overlap,
exp(−2 ln2 (Δt/τ)²), which is 0.25 at Δt/τ = 1.
:::

::: deck

These are the bullets of slide 46.

- 2CE needs the two pulses at the same place and at the same time: Lim & Saloma (2003) note that achieving optimal temporal overlap of the 2CE pulses is crucial.
- At a fixed point, the 2CE of the 350-nm pairs decreases with the delay Δt as the overlap in time of two Gaussian pulses of width τ.

The line under the equation reads as follows.

> where F is the peak 2CE fluorescence, Δt the delay of the 656-nm pulse relative to the 750-nm pulse and τ the pulse width. A delay of 0.40 τ reduces the peak by 20%, a delay of 0.71 τ by one half and a delay of τ by 75%.

:::
:::

::: card
::: sl
47
:::

## Facing lenses: position where the delayed pulses meet

::: say
With facing lenses the delayed pulses meet at z~m~ = cΔt/2n, and 2CE forms over a stretch of length G = cτ/(√2 n) about
that position.
:::

[[b47|47]]

::: main
At low NA the peak moves along the axis towards the position where the pulses meet.
:::

::: look
Point at the chart of the position of the peak against Δt and at the dashed line cΔt/2: the curve of NA 0.1 follows the
line, while the curves of higher NA stay near the focus.
:::

::: deck

These are the bullets of slide 47.

- With facing lenses, the delayed pulses meet at z~m~ = cΔt/2n, and 2CE forms over a stretch of length G = cτ/(√2 n) about that position.
- With D the continuous-beam depth of focus of 2CE, the peak 2CE fluorescence at a delay Δt follows from the product of the focus and this stretch.

The line under the equations reads as follows.

> where z~m~ is the position where the delayed pulses meet and G the length of the stretch over which they overlap. A long focus (D much larger than G) retains the peak, which moves with z~m~; a short focus holds the peak at the focus, where it decreases as the temporal overlap.

:::
:::

::: card
::: sl
48
:::

## Peak 2CE fluorescence and its position against the delay, θ = π

::: say
With facing lenses at low NA the peak 2CE fluorescence moves along the axis and is largely retained, while at NA 0.5 and
above it stays at the focus and decreases as the temporal overlap.
:::

[[b48a|48]]

::: main
At NA 0.1 and 100 fs, a delay of one pulse width reduces the peak by 7% and moves it 14 µm from the focus.
:::

::: look
Point at the curve of NA 0.1 on the chart of the position at Δt = 100 fs, and at the same NA on the chart of the peak
beside it, at Δt/τ = 1.
:::

[[b48b|48]]

::: main
At NA 0.5 and above the peak decreases as the temporal overlap; at NA 0.5 a delay of one pulse width reduces it by 74%.
:::

::: look
Point at the curves of NA 0.5, 0.7 and 0.9, which lie on the dotted temporal overlap.
:::

::: deck

These are the bullets of slide 48.

- With facing lenses at low NA, the delayed pulses still meet inside the long depth of focus, so the peak 2CE fluorescence moves along the axis and is largely retained: at NA 0.1 and 100 fs, a delay of one pulse width reduces the peak by 7%.
- At NA 0.5 and above, the peak stays at the focus and decreases as the temporal overlap of the two pulses (dotted line), by 74% at a delay of one pulse width.

:::
:::

::: card
::: sl
49
:::

## Peak 2CE fluorescence at a delay of one pulse width against NA

::: say
As NA increases the peak 2CE fluorescence that remains at a delay of one pulse width decreases to one quarter, and
shorter pulses and pupils with a longer depth of focus retain more of it.
:::

[[b49a|49]]

::: main
At NA 0.3 and 100 fs the peak that remains at a delay of one pulse width is 0.32 for the circular pupil and 0.80 for the
annular pupil with ε = 0.9.
:::

::: look
Point at the green curve of the annular pupil with ε = 0.9, which stays high up to a larger NA than the others, and at
the dotted line of the temporal overlap, 0.25, which all curves reach at high NA.
:::

[[b49b|49]]

::: main
At 30 fs all pupils retain more of the peak than at 100 fs at the same NA.
:::

::: look
The curves move to lower NA as τ decreases, because the position where the pulses meet moves by a shorter distance.
:::

::: deck

These are the bullets of slide 49.

- As NA increases, the peak 2CE fluorescence that remains at a delay of one pulse width decreases to one quarter, the temporal overlap of the two pulses; shorter pulses retain more, because the position where they meet moves by a shorter distance (left).
- A Gaussian input and annular pupils, which give a longer depth of focus, retain more of the peak at the same NA (right).

:::
:::

::: card
::: sl
50
:::

## Peak 2CE fluorescence against the delay, τ = 5 fs, NA 0.5

::: say
With all photon pairs and phase-locked pulses the peak 2CE fluorescence oscillates with the delay, while the peak of the
350-nm pairs alone decreases smoothly as the temporal overlap.
:::

[[b50a|50]]

::: main
With collinear lenses at 5 fs the fringes are deep, with periods of 2.19, 2.50 and 1.17 fs.
:::

::: look
Point at the blue curve of all pairs, which swings about the red curve of the 350-nm pairs by up to 0.92 of the peak.
:::

[[b50b|50]]

::: main
With crossed lenses at NA 0.5 the fringes are shallower than with collinear lenses.
:::

::: look
Along x, the blue curve swings about the red one by about 0.4 of the peak.
:::

::: deck

These are the bullets of slide 50.

- With all photon pairs and phase-locked pulses, the peak 2CE fluorescence oscillates with the delay, with periods of 2.19, 2.50 and 1.17 fs, because the delay changes the phase of the 350-nm pairs relative to the 375- and 328-nm pairs.
- The 2CE of the 350-nm pairs alone decreases smoothly with the delay, as the temporal overlap of the two pulses.

:::
:::

::: card
::: sl
51
:::

## Peak 2CE fluorescence against the delay, τ = 10 fs, NA 0.5

::: say
At 10 fs the peak 2CE fluorescence with all photon pairs still oscillates with the delay, with the same periods as at
5 fs.
:::

[[b51|51]]

::: main
At 10 fs the fringes with collinear lenses still swing by about 0.7 of the peak.
:::

::: look
Point at the fringes of the blue curve near Δt = 0, which fade as the two pulses separate.
:::

::: deck

These are the bullets of slide 51.

- With all photon pairs and phase-locked pulses, the peak 2CE fluorescence oscillates with the delay, with periods of 2.19, 2.50 and 1.17 fs, because the delay changes the phase of the 350-nm pairs relative to the 375- and 328-nm pairs.
- The 2CE of the 350-nm pairs alone decreases smoothly with the delay, as the temporal overlap of the two pulses.

:::
:::

::: card
::: sl
52
:::

## Peak 2CE fluorescence against the delay, τ = 20 fs, NA 0.5

::: say
At 20 fs the amplitude of the 375- and 328-nm pairs is below 1% of that of the 350-nm pairs, so the total peak 2CE
fluorescence follows that of the 350-nm pairs and decreases smoothly with the delay.
:::

[[b52|52]]

::: main
At 20 fs the blue and red curves nearly coincide.
:::

::: look
The largest gap between the two curves is about 0.04 of the peak.
:::

::: deck

These are the bullets of slide 52.

- At 20 fs, the amplitude of the 375- and 328-nm pairs is below 1% of that of the 350-nm pairs, so the total 2CE follows the 2CE of the 350-nm pairs.
- The peak decreases smoothly with the delay, as the temporal overlap of the two pulses.

:::
:::

::: card
::: sl
53
:::

## Fringe depth of the 2CE peak against NA, τ = 5, 10 and 20 fs

::: say
With crossed and facing lenses the fringes against the delay deepen as NA increases, because the delay moves the
interference fringes in space across a smaller focal spot; with collinear lenses the depth is the same at all NAs.
:::

[[b53a|53]]

::: main
With crossed lenses at 5 fs and NA 0.3 the fringes are shallow, with a depth of about 0.2 of the peak.
:::

::: look
Point at the small swing of the blue curve about the red one.
:::

[[b53b|53]]

::: main
At NA 0.7 the same fringes swing by about 0.65 of the peak.
:::

::: look
Compare this swing with that of the previous step. A smaller focal spot holds fewer of the fringes in space, so the peak
follows them as the delay moves them.
:::

::: deck

These are the bullets of slide 53.

- With crossed and facing lenses, the fringes of the peak against the delay deepen as NA increases, because the delay moves the interference fringes in space across a smaller focal spot.
- With collinear lenses, the three kinds of photon pairs have no fringes in space, so the fringe depth is the same at all NAs: 0.92 at 5 fs and 0.71 at 10 fs.

:::
:::

::: card
::: sl
54
:::

## Peak 2CE fluorescence against the delay for two polarizations

::: say
With crossed lenses and the polarization in the plane of the two lens axes, the fields of the two beams are
perpendicular at the focus, so the fringes against the delay are about a quarter as deep.
:::

[[b54a|54]]

::: main
With the polarization in the plane of the lens axes the fringes are shallow, with an amplitude of about 0.05.
:::

::: look
Point at the blue curve of all pairs. Both curves are divided by the value of all pairs at no delay, so the red curve of
the 350-nm pairs starts below 1.
:::

[[b54b|54]]

::: main
With the polarization perpendicular to that plane the amplitude is about 0.21.
:::

::: look
Switch the polarization control between the two settings to compare the depth of the fringes; each curve is then
divided by its own value at no delay.
:::

::: deck

These are the bullets of slide 54.

- With the polarization in the plane of the two lens axes, the fields of the two beams are perpendicular at the focus, so the three kinds of photon pairs fall in different field components and interfere less.
- The fringes against the delay are then about a quarter as deep, while the 2CE of the 350-nm pairs decreases with the delay in the same way for both polarizations.

:::
:::
