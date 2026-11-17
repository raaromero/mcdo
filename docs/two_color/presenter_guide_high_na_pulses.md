---
title: "Presenter guide: two-color excitation at high NA and with optical pulses"
subtitle: "Two-color excitation at high NA and with optical pulses. Slide numbers are the positions of the slides in 2ce_high_na_pulses.pptx (65 slides); the guide that pairs each slide with the dashboard is high_na_pulses_guide.pdf."
---

<!-- Build (as presenter_guide.md): pandoc presenter_guide_high_na_pulses.md -s --embed-resources --css presenter_guide.css
     -o /Users/raaromero/mcdo_dev/output/08_two_color/decks/presenter_guide_high_na_pulses.html, then print it to PDF with
     headless Chromium: Chromium --headless=new --no-pdf-header-footer --print-to-pdf=<…>/presenter_guide_high_na_pulses.pdf
     file://<…>/presenter_guide_high_na_pulses.html. Each ::: card is one slide: the slide number in the margin, the slide
     title word for word, the main point in one sentence (say), what to say, then the likely questions with short answers.
     Numbers come from the speaker notes of the deck, docs/progress/work_to_date.tex, docs/two_color/pulse_derivations.tex,
     docs/review/07_two_color_pulses/review_07.tex and the stored data files beside the figures (checked 2026-11-17). The
     cards of Part 4 are those of presenter_guide_delay.md, renumbered. No run-in labels or arrows in this file. -->

::: {.card .story}
::: sl
How
:::

## How to use this guide

- Each card is one slide. Its number is the position of the slide in the deck, as Keynote and PowerPoint count the
  slides; the number printed in the corner of a slide skips the title slide and the dividers, so it is smaller.
- The yellow box is the main point of the slide in one sentence, the paragraph under it is what to say, and the list at
  the end gives the questions that are likely and a short answer to each.
- The numbers that are not on the slide are in its speaker notes, with the equations in LaTeX.
- The title slide, the dividers and the glossary have no card.
:::

::: card
::: sl
2
:::

## Summary

::: say
I reproduced the focus of few-cycle pulses and the two-color studies of the group, extended them to high NA and to
optical pulses, and found that the lens angle decides what a pulse and a delay change.
:::

Read the seven bullets in order: the Richards–Wolf focus of one beam, then two-color excitation (2CE) at high NA, then
pulses, then the delay between the two pulses. The paraxial depth of focus of 2CE with collinear and facing lenses is 5%
longer than the vector one from NA 0.43 in air, 7% longer at NA 0.5 and 36% longer at NA 0.9. With facing lenses at
NA 0.5, the pulsed 2CE depth of focus is about 80% of the continuous-beam value at 20 fs.

::: qa
- **Which model is used where?** The paraxial scalar model of Cambaliza & Saloma (2000) is used for the replications at
  NA 0.5, and in Part 2 it is compared with the vector (Richards–Wolf) model at higher NA to show where it departs. In
  the figures of the pulse results the paraxial curves are drawn up to NA 0.5.
- **How much does the paraxial model overestimate the depth of focus?** The paraxial 2CE depth of focus is 5% longer
  than the vector one from NA 0.43 in air, 7% longer at NA 0.5 and 36% longer at NA 0.9.
:::
:::

::: {.part}
# 1. Replication of Romallosa et al. (2003) and its extension to Gaussian input and annular pupils: intensity distribution near focus with the Richards–Wolf theory
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

The left panel is the transverse distribution at z = 0 and the right panel the axial distribution at r = 0, at 750 nm,
NA 0.8 and n = 1.3. The structural content of the axial distribution at 1 fs is 1.058, compared to 1.057 published, and
the transverse FWHM is 472.8 nm. The remaining differences are within 1% for Fig. 4 and about 3% for Fig. 3 at 1 fs.

::: qa
- **Which spectral window did you integrate?** The whole positive spectrum, from 0 to 2ω~c~. The band that
  Romallosa et al. (2003) quote, 483 nm to 1.67 µm, is the FWHM of the spectrum; with that band alone 24% of the
  spectral weight is lost and the quoted values are not reproduced.
- **Did anything have to be inferred?** Three conventions were found from the figures: the panel labels of Fig. 2 are
  exchanged, Fig. 3 is an integral along a line, and the Linfoot arrays are in optical coordinates.
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

The left panel gives the criteria at 1 fs against NA and the right panel the criteria against the pulse width at NA 0.8,
as in Fig. 4 of Romallosa et al. (2003). Open symbols are the fidelity F and filled symbols the structural content S,
along and across the axis.

::: qa
- **Why do the criteria not depend on NA?** The Linfoot arrays are in optical coordinates, which scale out the NA.
- **What do F and S measure?** F = 1 − Σ(a − r)²/Σr² and S = Σa²/Σr², with r the continuous-beam distribution and a the
  pulsed one; both are 1 for identical distributions.
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

At NA 0.1 the vector theory, the scalar Debye integral and the Airy pattern agree to 1e-4. Along the polarization the
FWHM of the two theories differs by 1% at NA 0.30 and by 5% at NA 0.60; along the axis the difference reaches 1% at
NA 1.15. The right panel shows the three field components at NA 1.2.

::: qa
- **Why is the difference larger along the polarization?** The longitudinal field E~z~ = −2I~1~ cos φ is zero across
  the polarization and largest along it, so it widens the spot in that direction.
- **Was E~z~ checked?** Yes. With E~z~ = −2I~1~ cos φ the divergence of the field at NA 0.9 is 1.9e-8 k|E|. The
  two-beam calculation had the factor −2i until 2026-11-10, which gives 0.77 k|E|; it was corrected, and the factor does
  not change the intensity of one beam (review_07, Sections 3 and 4).
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

The figure shows the intensity in the focal plane on a log scale against the optical radius v = k r sin α, at 750 nm and
n = 1.3. At NA 0.3 the FWHM along the polarization is 3.27 in optical units against 3.23 for the scalar field, about 1%
wider. At NA 0.9 it is 3.62 against 3.19, and the first zero along the polarization is filled to 1e-2 of the peak.
Across the polarization the vector spot keeps its zeros.

::: qa
- **Why plot against v and not in µm?** In optical units the Airy spot has the same width, 3.23, at all NAs, so the
  departures from it are the high-NA effects; the scalar Debye spot falls slightly below it (3.19 at NA 0.9), and the
  vector spot rises above it along the polarization.
- **Does the spot change across the polarization?** Very little: across the polarization the vector spot is about 1%
  narrower than the scalar one.
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

For uniform input the deviation of the vector focal width from the scalar one passes 1% near NA 0.45 and 5% near
NA 0.90; for α = 4 it passes them near NA 0.55 and 1.15. Along the polarization the 1% and 5% points are NA 0.40 and
0.85 for α = 4, against 0.30 and 0.60 for uniform input. The right panel shows the profile along the axis at NA 0.9,
where the Gaussian input gives a longer depth of focus.

::: qa
- **What is α?** The truncation parameter of the Gaussian input, A(ρ) = exp(−αρ²) over the pupil; α = 0 is uniform
  input.
- **Is this the reverse of the older progress report?** Yes. The older comparison used a paraxial Gaussian reference
  that was not valid; with a consistent scalar reference the Gaussian input extends the range of scalar theory.
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

The field of an annular pupil is the field of the full pupil minus that of the obstructed part. At ε = 0.99 the depth
of focus over that of the full pupil is 50.13 at low NA, against 50.25 from 1/(1 − ε²), and 30.4 at sin α = 0.9.

::: qa
- **How large is the gain at high NA?** At ε = 0.99 the depth of focus is 30.4 times that of the full pupil at
  sin α = 0.9, against 50.25 from 1/(1 − ε²).
- **Does a thin annulus give a Bessel beam?** At low NA it gives the J~0~² profile of Durnin; at high NA the vector
  profile is narrower than the scalar one (FWHM 2.06 against 2.25 optical units).
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

At NA 0.8 and ε = 0.99 the depth of focus over that of the full pupil is 44.35 for a continuous beam and 44.33 at 1 fs.
Along the axis the focus at 1 fs is 1.010 times longer than with a continuous beam, and beyond the half-maximum point the
axial intensity decreases more slowly as the pulse width decreases.

::: qa
- **How much longer is the focus at 1 fs?** It is 1.010 times the continuous-beam focus along the axis at ε = 0.99.
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

The structural content across the axis is about 1.06 at 1 fs for both pupils, so the loss of contrast that
Romallosa et al. (2003) report for the circular pupil also occurs with annular pupils.

::: qa
- **Why do the zeros fill?** Each frequency of the pulse has its zeros at a different radius, so the sum over the
  spectrum has none.
:::
:::

::: {.part}
# 2. Two-color excitation with continuous beams: replication of Cambaliza & Saloma (2000) and Lim & Saloma (2002, 2003), and extension to high NA
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

Lens L2 is lens L1 rotated by θ about the common focus O, with θ = 0 for collinear, π/2 for crossed and π for facing
lenses; L1 focuses 750 nm and L2 656 nm. Two-photon excitation (2PE) uses 700 nm in both lenses, so the two fields add
and interfere before the fourth power.

::: qa
- **Why 750 and 656 nm?** One photon of each adds up to the 350-nm level, 1/λ~e~ = 1/λ~1~ + 1/λ~2~, as in
  Cambaliza & Saloma (2000).
- **How is beam 2 rotated?** In real space (x, z). A rotation of the optical coordinates (u, v), as written by
  Cambaliza & Saloma, is not a rotation of real space at π/2, and it does not reproduce the fits of Lim & Saloma (2002).
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

In the paraxial scalar model at NA 0.5, the 2CE central spot is 0.763 µm wide with crossed lenses and 0.516 µm with
collinear and facing lenses. With crossed lenses the spot shows no second-order interference effects.

::: qa
- **Do the ratios in the text of Cambaliza & Saloma (2000) agree too?** Several ratios quoted in the text at θ = π/2
  differ from their own curves (for example 0.67 against 0.49 for the 2PE spot at π/2 over that at 0), while the plotted
  widths agree with current work. This is known and accepted.
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

The 2CE depth of focus is 3.56 µm with collinear and facing lenses and 0.67 µm with crossed lenses, in the paraxial
scalar model at NA 0.5.

::: qa
- **Where does 0.67 µm for the depth of focus at π/2 come from?** It is the value with beam 2 rotated in (x, z); a
  rotation in the optical coordinates (u, v) gives 1.31 µm.
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

In the paraxial scalar model at NA 0.5, with x~c~ and z~c~ in units of λ~1~, the fits of current work are
−0.601 x~c~² + 0.888 across the axis and −0.027 z~c~² + 0.998 along it. A misalignment of 0.37 λ~1~ across the axis
reduces the peak by 18%, compared to the 20% reported by Lim & Saloma (2002).

::: qa
- **Why 18% and not 20%?** The peak at 0.37 λ~1~ is 0.824 of the aligned peak in current work; Lim & Saloma (2002)
  quote 20%.
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

Across the axis the fit of current work is −0.063 x~c~² + 0.999, against −0.06 x~c~² + 1 in Lim & Saloma (2002); along
the axis it is −0.045 z~c~² + 0.995, against −0.045 z~c~² + 0.986. A misalignment of 1.33 λ~1~ within the focal plane of
L1 reduces the peak by 11%.

::: qa
- **Why does the crossed-lens peak decrease with z~c~?** The focus of L2 then moves along the axis of L1, so the length
  of the focus of L1 sets the loss.
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

At θ = 0 the peak at φ~1~ = φ~2~ = ±60 is 0.84 of the peak without aberration, and at φ~1~ = −φ~2~ = ±60 it is 0.07; at
θ = π the two cases are exchanged. With crossed lenses the 2CE fidelity stays above 0.9 for coefficients up to 40, as in
Lim & Saloma (2003).

::: qa
- **Is the aberration the primary spherical aberration of each beam?** Yes, with coefficients φ~1~ and φ~2~, in the
  paraxial scalar model at NA 0.5, as in Lim & Saloma (2003).
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

With facing lenses the fitted exponents from NA 0.1 to 0.5 are −0.99 across the axis and −2.04 along it. The paraxial
scalar model gives a larger tolerated misalignment along the axis than the vector model, by 7% at NA 0.5 and by 47%
near NA 0.95.

::: qa
- **What does a Gaussian input do?** A Gaussian input with α = 4 makes the tolerated misalignments about 1.4 times
  larger.
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

The fitted exponents from NA 0.1 to 0.5 are −2.03 and −2.04. The vector focus is computed in air up to NA 0.71, where
two crossed lenses fit, and in water up to NA 0.94.

::: qa
- **Why 1/NA² in both directions?** Each misalignment moves one focus along the length of the other beam, and in the
  paraxial model the length of a focus scales as 1/NA².
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

The vector 2CE depth of focus in air is 3.33 µm at NA 0.5 and 0.81 µm at NA 0.9. The 5% point, NA 0.43 in air and 0.57
in water, lies below the NA 0.7 stated by Cambaliza & Saloma (2000, p. 27). The paraxial model uses sin²α/2 for
1 − cos α, which lengthens the depth of focus by about 1 + tan²(α/2).

::: qa
- **Is the difference due to the polarization?** No. The scalar Debye integral with the exact phase gives the vector
  depth of focus, so the small-angle phase of the paraxial model causes the difference.
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

The paraxial and vector depths of focus are 3.56 and 3.33 µm at NA 0.5, and 1.10 and 0.81 µm at NA 0.9. The profile
along the axis is the same with collinear and facing lenses, since I~1~I~2~ does not depend on the direction of beam 2.

::: qa
- **Why show the profiles and not the widths?** The widths of the previous slide are the FWHM of these profiles; the
  profiles show that the whole paraxial focus is longer, not its half-maximum width alone.
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

The crossed-lens 2CE spot is 0.75 by 0.66 µm at NA 0.5. Its depth of focus is shorter than with collinear lenses, and
this advantage decreases as NA increases: 13 times shorter at NA 0.2 and 3.4 times shorter at NA 0.7.

::: qa
- **Why do the widths decrease as 1/NA and not 1/NA²?** Each 2CE width is set by the transverse spot of the other beam,
  which scales as 1/NA.
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

Along the axis with collinear and facing lenses the difference reaches 5% at NA 0.43 in air and 0.57 in water; across
the axis it reaches 5% at NA 0.86 in air and 1.14 in water. With crossed lenses it stays within 4%.

::: qa
- **Is the difference due to the polarization?** No. The scalar Debye integral with the exact phase gives the vector
  widths along the axis, so the small-angle phase causes the difference.
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

Along the axis C is below 0.95 from NA 0.44 in air and 0.58 in water, where the depth of focus departs by 5%. The
fidelity F stays above 0.99 up to NA 0.63 in air and 0.84 in water, and across the axis F stays at 0.996 or above at all
NAs.

::: qa
- **Why does C fall before F?** Each profile is normalized to unit energy, so the longer paraxial focus has a lower peak
  and Σa² drops below Σr²; F stays above 0.99 up to a higher NA.
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

These bounds hold up to NA 0.71 in air and 0.94 in water. With crossed lenses the paraxial model gives the profiles of
the vector focus.

::: qa
- **What are F, C and Q?** The fidelity, the structural content and the correlation quality of Linfoot, computed for
  the paraxial profile against the vector profile.
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

At ε = 0.99 the 2CE depth of focus at θ = 0 is 155 µm in the vector model against 179 µm in the scalar one at NA 0.5,
and 25 against 55 µm at NA 0.9. The annular depth of focus is 47 times the circular one at NA 0.5 and 31 times at
NA 0.9, against 50 in the paraxial model.

::: qa
- **Why is the edge of the pupil the problem?** The paraxial phase error grows with the angle of the ray, and a thin
  ring has all of its rays at the largest angle.
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

The condition is NA ≤ n sin 45° = n/√2. Cambaliza & Saloma (2000) note on p. 34 that dual-beam excitation with two
identical objectives is possible for NA ≤ 0.7.

::: qa
- **What happens above NA 0.71 in air?** The two cones overlap and the two lenses cannot both be placed, so the vector
  results with crossed lenses above that NA are computed in water, up to NA 0.94.
:::
:::

::: {.part}
# 3. Extension to optical pulses: 2PE and 2CE point spread functions with transform-limited femtosecond pulses
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

The left panel is the Gaussian spectrum of a 10-fs pulse at 750 nm, with nine frequencies marked. The right panel shows
the waves at those frequencies, each with its weight; they are in phase at t = 0 and out of phase at 15 fs.

::: qa
- **Is the pulse chirped?** No. The pulses are transform-limited Gaussians, so all frequencies are in phase at t = 0.
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

The figure shows the field E(t) and its envelope, summed over the whole spectrum of the 10-fs pulse at 750 nm. At 15 fs
the waves are out of phase and the envelope has fallen to a few percent of its peak.

::: qa
- **What is τ?** The pulse width, the full width at half maximum of the intensity |E(t)|².
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

The spectral bandwidth is 88 THz at 5 fs, 44 THz at 10 fs, 22 THz at 20 fs and 4.4 THz at 100 fs. The dotted line in the
right panel is 428 THz, which is 700 nm.

::: qa
- **Where does 0.441 come from?** For a Gaussian pulse the product of the two FWHMs is Δν τ = 4 ln 2/2π = 0.441.
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

Against wavelength both colors lie at the red edge of the visible range, 380 to 750 nm. At 10 fs each spectrum has 31%
of its peak at 700 nm; at 20 fs and longer it has almost none.

::: qa
- **Why does 700 nm matter?** Two photons of 700 nm add up to 350 nm, so a pulse whose spectrum reaches 700 nm can
  excite the 350-nm level by itself.
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

The amplitude is A = A^11^ + 2A^12^ + A^22^ with A^ab^ = ∫E~a~E~b~e^iω~e~t^dt, and F = |A|². The term 2A^12^ takes
one photon from each beam, the 350-nm pairs; A^11^ and A^22^ take both photons from one beam, the 375- and 328-nm pairs.
For long pulses F becomes I~1~I~2~, the result of Cambaliza & Saloma (2000).

::: qa
- **Why not add the intensities of the frequencies, as Romallosa et al. (2003) do?** Their sum is the intensity
  integrated over time; for a two-photon signal ∫I²dt is not (∫I dt)², and 2CE depends on when the two pulses arrive.
- **Which polarization is used?** Both beams are polarized perpendicular to the plane of the lens axes, in the vector
  model in air with the circular pupil, unless a slide says otherwise.
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

In the paraxial model at NA 0.5 the depth of focus is 3.56 µm with collinear lenses. With facing lenses it is 3.52 µm
against 3.56 µm, because the pulses overlap over 21 µm, six times the focus.

::: qa
- **Is 100 fs long enough at all NAs?** With facing lenses it is not at low NA: the pulse width needed to match
  continuous beams is 87 fs at NA 0.5 but 264 fs at NA 0.3 (slide 41).
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

With crossed lenses the width across the axis is 0.76 µm with pulses and with continuous beams, and the widths at the
three lens angles agree to within 1%.

::: qa
- **Does this hold in the vector model too?** Yes. The stored 100-fs profiles at NA 0.5 match the continuous-beam ones
  at the three angles (review_07, Section 2.4).
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

With collinear lenses the two pulses travel together and overlap over the whole focus, so 2CE keeps its profile down to
4 fs. With crossed lenses the depth of focus changes by a few percent below about 20 fs; it grows by up to 6% below
10 fs, because the 375-nm pairs from L1 alone extend along its axis. Crossed lenses therefore keep the sharpest profiles.

::: qa
- **Are crossed lenses then the best choice with pulses?** They keep the sharpest profile, as with continuous beams,
  and two of them fit up to NA 0.71 in air.
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

In the paraxial model at NA 0.5 the 2CE depth of focus is 3.56 µm for continuous beams, 2.81 µm at 20 fs and 1.92 µm at
10 fs for the 350-nm pairs. At NA 0.3 and 20 fs it is 40% of the continuous-beam value. 2PE shortens less, because the
350-nm pairs within one pulse need no overlap.

::: qa
- **Why is the shortening larger at lower NA?** The continuous-beam focus grows as 1/NA² while the stretch where the
  pulses meet stays the same, so the overlap cuts a larger part of the focus.
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

The stretch has FWHM G = cτ/(√2 n), 4.2 µm at 20 fs and 21 µm at 100 fs. With D the continuous-beam depth of focus the
pulsed one is DG/√(D² + G²). At 20 fs this product gives 2.74 µm, and the full calculation gives 2.78 µm with all pairs
and 2.81 µm with the 350-nm pairs.

::: qa
- **Why is the computed depth of focus at 10 fs longer than the product?** The 375- and 328-nm pairs need no overlap of
  the two pulses, so the computed 2CE is 2.14 µm long against 1.83 µm from the product.
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

With continuous beams 2CE needs both beams, which gives its weak background in scattering media. At 10 fs the amplitude
of the 375-nm pairs is 18% and that of the 328-nm pairs 14% of the amplitude of the 350-nm pairs; at 20 fs both are below
1%. The peak of the total over that of the 350-nm pairs is 1.02 at 20 fs, 1.15 at 15 fs, 1.73 at 10 fs and 3.1 at 5 fs.

::: qa
- **Do real probes absorb these pairs?** Lim & Saloma (2003) note that probes are chosen to minimize two-photon
  excitation by λ~1~ or λ~2~ alone; the model keeps all pairs, so it gives the case with no such selection.
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

With facing lenses in air the pulse width is about 25 fs at NA 0.9, 87 fs at NA 0.5, 264 fs at NA 0.3 and 610 fs at
NA 0.2. At NA 0.5 it is 87 fs in air, 164 fs in water and 216 fs in oil. For 2PE it is shorter, 62 fs at NA 0.5,
because the 350-nm pairs within one pulse need no overlap.

::: qa
- **What is the tolerance?** The largest difference between the pulsed and continuous-beam profiles, each scaled to
  its peak, stays below 1% of the peak.
- **Why do water and oil need longer pulses at the same NA?** The focus depends on NA/n, so at the same NA it is
  longer in a medium of higher refractive index.
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

The measure is the same as on the previous slide. With collinear lenses the two pulses travel together and overlap over
the whole focus, so the shortest pulse computed, 4 fs, already matches. With crossed lenses at NA 0.1 the pulse width
needed is 54 fs.

::: qa
- **How is the match measured?** As on slide 41: the largest difference between the pulsed and continuous-beam
  profiles, each scaled to its peak, stays below 1% of the peak.
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

The figure gives the pulse width from which the 2CE depth of focus stays within 1% of its continuous-beam value: at
NA 0.5, 100 fs for the circular pupil, 162 fs for the Gaussian input (α = 4) and 466 fs for the annular pupil with
ε = 0.9. By the largest difference between the profiles, the measure of the slides before, the same three are 87, 139
and 405 fs.

::: qa
- **Why two sets of numbers?** This slide uses the depth of focus and the slides before use the largest difference
  between the profiles; both give the same order of the pupils.
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

With crossed lenses the pulse width is 13 to 15 fs for the circular pupil from NA 0.4 to 0.7, 14 to 16 fs for the
annular pupils and 11 to 14 fs for the Gaussian input (α = 4). Below NA 0.4 it rises, to 82 fs for the Gaussian input
and 54 fs for the circular pupil at NA 0.1.

::: qa
- **Does the pupil matter with crossed lenses?** Little: from NA 0.4 up the pulse width needed lies between 11 and 16 fs
  for all pupils and inputs.
:::
:::

::: {.part}
# 4. Delay between the two pulses: peak 2CE fluorescence against a misalignment of the two pulses in time, at θ = 0, π/2 and π
:::

::: card
::: sl
46
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
47
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
48
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
49
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
50
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
51
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
52
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
53
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
54
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

::: card
::: sl
55
:::

## Summary: 2CE with optical pulses

::: say
The lens angle decides what a pulse and a delay change: collinear and crossed lenses keep the continuous-beam focus,
facing lenses shorten it, and a delay reduces the peak as the temporal overlap except with facing lenses at low NA.
:::

Read the six bullets in order, with collinear θ = 0, crossed θ = π/2 and facing θ = π. The results assume phase-locked,
transform-limited pulses and a 350-nm level that is narrow compared to the pulse spectra.

::: qa
- **Has any of this been compared with experiment?** No. No comparison with an experiment or a full-wave calculation
  is planned for now.
:::
:::

::: card
::: sl
56
:::

## Next steps

::: say
Pulsed 2CE through a highly scattering medium is the first candidate, because Cambaliza & Saloma (2000) found the main
advantage of 2CE compared to 2PE there.
:::

The scattering medium combines the Monte Carlo model of the focus with the pulse model, and it would show whether 2CE
with pulses keeps its weak background. With unequal pulse widths the overlap becomes exp[−4 ln2 Δt²/(τ~1~² + τ~2~²)],
and for a broad absorption band the signal of the 350-nm pairs is the integral of I~1~I~2~ over time.

::: qa
- **Why a scattering medium first?** Below about 15 fs one beam alone also excites the 350-nm level, so a scattering
  medium would show how much of the weak background of 2CE remains with pulses.
:::
:::

::: {.part}
# Backup
:::

::: card
::: sl
60
:::

## Central spot and depth of focus against NA: 2PE, θ = π/2

::: say
With crossed lenses the 2PE central spot keeps its width as NA increases, 0.26 µm in air and 0.19 µm in water, because
it is one interference fringe of the two beams.
:::

The 2PE central spot stays at 0.256 µm in air at all NAs and at 0.19 µm in water, in both models within 0.4%. 2PE is
narrower than 2CE and has stronger side lobes, as in Cambaliza & Saloma (2000).

::: qa
- **Why does the 2PE spot not shrink with NA at θ = π/2?** It is one interference fringe of the two crossed beams, so
  its width is set by the wavelength in the medium, λ~2p~/n.
:::
:::

::: card
::: sl
61
:::

## Pulse width that matches continuous beams: 2PE, θ = π

::: say
With facing lenses pulsed 2PE matches continuous beams at a shorter pulse width than 2CE, 62 fs against 87 fs at NA 0.5
in air, because pairs of photons from one pulse need no overlap.
:::

The measure is the largest difference between the pulsed and continuous-beam 2PE profiles, below 1% of the peak. The
scalar curves are drawn up to NA 0.5.
:::

::: card
::: sl
62
:::

## Pulse width that matches continuous beams: 2PE, θ = 0, π/2

::: say
With collinear lenses pulsed 2PE matches continuous beams down to 4 fs, and with crossed lenses once the pulses are
longer than 37 fs at NA 0.1 and 6 fs at NA 0.5.
:::

With crossed lenses in air the pulse width is 37 fs at NA 0.1, 5.7 fs at NA 0.5 and 4 fs, the shortest computed, from
NA 0.6.
:::

::: card
::: sl
63
:::

## Pulse width that matches continuous beams: 2PE, pupils, θ = π

::: say
With facing lenses a pupil or an input that gives a longer depth of focus also needs a longer pulse for 2PE to match
continuous beams.
:::

By the depth of focus within 1% of its continuous-beam value, the pulse width at NA 0.5 is 72 fs for the circular pupil.
:::

::: card
::: sl
64
:::

## Pulse width that matches continuous beams: 2PE, pupils, θ = 0, π/2

::: say
With collinear lenses the 2PE depth of focus matches continuous beams at all pulse widths computed, and with crossed
lenses the pulse width needed is largest at low NA and falls below 10 fs at NA 0.7.
:::

With crossed lenses the pulse width at NA 0.1 is 68 fs for the Gaussian input and 44 fs for the circular pupil.
:::

::: card
::: sl
65
:::

## Side lobes of 2PE against NA: distance from the peak and height

::: say
As NA increases the 2PE side lobes weaken, so the drawback of 2PE that Cambaliza & Saloma (2000) report at NA 0.5
becomes smaller at high NA.
:::

At θ = π/2 the side lobe falls from 0.11 of the peak at NA 0.5 to 0.04 at NA 0.7 in air; at θ = π it falls from 0.97 to
0.42 at NA 0.9. The distance of the side lobes from the peak is λ/2n with facing lenses and λ/n with crossed lenses at
low NA. The 2CE side lobes stay below 1e-3 of the peak.

::: qa
- **Why do weaker side lobes matter?** Weaker side lobes give images of higher contrast.
:::
:::
