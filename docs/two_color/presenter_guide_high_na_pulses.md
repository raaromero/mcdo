---
title: "Presenter guide: two-color excitation at high NA and with optical pulses"
subtitle: "Two-color excitation at high NA and with optical pulses. Slide numbers are those of 2ce_high_na_pulses.pptx; the guide that pairs each slide with the dashboard is high_na_pulses_guide.pdf."
---

<!-- Build (as presenter_guide.md): pandoc presenter_guide_high_na_pulses.md -s --embed-resources --css presenter_guide.css
     -o /Users/raaromero/mcdo_dev/output/08_two_color/decks/presenter_guide_high_na_pulses.html, then print it to PDF with
     headless Chromium: Chromium --headless=new --no-pdf-header-footer --print-to-pdf=<…>/presenter_guide_high_na_pulses.pdf
     file://<…>/presenter_guide_high_na_pulses.html. Each ::: card is one slide: the slide number in the margin, the main point
     in one sentence (say), what to say, then the likely questions with short answers. Numbers come from the speaker
     notes of the deck, docs/progress/work_to_date.tex, docs/two_color/pulse_derivations.tex and
     docs/review/07_two_color_pulses/review_07.tex. No run-in labels or arrows in this file. -->

::: {.card .story}
::: sl
How
:::

## How to use this guide

- Each card is one slide. The yellow box is the main point of the slide in one sentence, the paragraph under it is what
  to say, and the list at the end gives the questions that are likely and a short answer to each.
- The numbers that are not on the slide are in its speaker notes, with the equations in LaTeX.
- The title, the dividers and the glossary have no card. The backup slides have a short card at the end.
:::

::: card
::: sl
2
:::

## Summary

::: say
I extended three studies of the group to high NA and to optical pulses, and the lens angle decides what a pulse changes.
:::

Read the six bullets in order: the Richards–Wolf focus, then two-color excitation (2CE) at high NA, then pulses. The
delay between the two pulses is in a separate deck, pulse_delay.pptx.

::: qa
- **Which model is used where?** The paraxial scalar model of Cambaliza & Saloma (2000) is used for NA up to 0.5,
  where it holds; the vector (Richards–Wolf) model is used at all NAs.
- **What does "too long a depth of focus" mean in numbers?** The paraxial 2CE depth of focus is 5% longer than the
  vector one from NA 0.43 in air, 7% at NA 0.5 and 36% at NA 0.9.
:::
:::

::: {.part}
# Part 1. The focus at high NA with the Richards–Wolf theory
:::

::: card
::: sl
4
:::

## Focus of a 1-fs pulse and a continuous beam, NA 0.8

::: say
The five figures of Romallosa, Bantang & Saloma (2003) are reproduced, and a 1-fs pulse fills the zeros of the focus.
:::

The left panel is across the axis and the right one along it, at 750 nm, NA 0.8 and n = 1.3. The structural content
along the axis is 1.058 against 1.057 in Romallosa et al. (2003); Fig. 4 agrees within 1% and Fig. 3 within
about 3% at 1 fs.

::: qa
- **Which spectral window did you integrate?** The whole positive spectrum, from 0 to 2ω~c~. The band quoted in the
  paper, 483 nm to 1.67 µm, is the FWHM of the spectrum; with that band alone 24% of the spectral weight is lost and the
  quoted values are not reproduced.
- **Did anything have to be guessed?** Three conventions were found from the figures: the panel labels of Fig. 2 are
  exchanged, Fig. 3 is an integral along a line, and the Linfoot arrays are in optical coordinates.
:::
:::

::: card
::: sl
5
:::

## Linfoot's criteria against NA and against pulse width

::: say
Pulses shorter than about 2 fs change the focus, and the change does not depend on NA.
:::

The left panel gives the criteria at 1 fs against NA and the right one against the pulse width at NA 0.8, as in Fig. 4
of Romallosa et al. (2003). Below about 2 fs the fidelity falls below 1 and the structural content rises above 1.

::: qa
- **Why do the criteria not depend on NA?** The Linfoot arrays are in optical coordinates, which scale out the NA.
- **What do F and S measure?** F = 1 − Σ(a − r)²/Σr² and S = Σa²/Σr², with r the reference and a the profile
  compared; both are 1 for identical profiles.
:::
:::

::: card
::: sl
6
:::

## Spot width against NA, scalar and vector theory

::: say
As NA increases the vector spot becomes wider than the scalar one, first along the polarization.
:::

At NA 0.1 the vector theory, the scalar Debye integral and the Airy pattern agree to 1e-4. Along the polarization the
FWHM differs by 1% at NA 0.30 and by 5% at NA 0.60; along the axis the difference reaches 1% at NA 1.15. The right panel
shows the three field components at NA 1.2.

::: qa
- **Why is the difference anisotropic?** The longitudinal field E~z~ = −2I~1~ cos φ is zero across the polarization
  and largest along it, so it widens the spot in that direction.
- **Was E~z~ checked?** Yes. With this factor the divergence of the field is zero to 2e-8 k|E|; the earlier factor −2i
  gave 0.77 k|E| and was corrected (review_07, Section 4).
:::
:::

::: card
::: sl
7
:::

## Focal spot at NA 0.3 and 0.9, scalar and vector

::: say
At NA 0.3 the scalar and vector spots agree, and at NA 0.9 the vector spot is 14% wider along the polarization and its
zeros fill.
:::

The figure shows the intensity in the focal plane on a log scale, against the optical radius v = k r sin α, at 750 nm and
n = 1.3. At NA 0.3 the FWHM along the polarization is 3.27 against 3.23 optical units for the scalar field; at NA 0.9 it
is 3.62 against 3.19, and the first zero along the polarization is filled to 1e-2 of the peak. Across the polarization
the vector spot keeps its zeros.

::: qa
- **Why plot against v and not in µm?** In optical units the scalar spot is the same at all NAs, so the change that
  remains is the vector effect.
- **Does the spot change across the polarization?** Very little: it is about 1% narrower than the scalar spot at NA 0.9.
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

For uniform input the deviation of the vector focal width from the scalar one passes 1% near NA 0.45 and 5% near 0.90;
for α = 4 it passes them near 0.55 and 1.15. Along the polarization the 1% and 5% points are NA 0.40 and 0.85 for
α = 4, against 0.30 and 0.60 for uniform input.

::: qa
- **What is α?** The truncation parameter of the Gaussian input, A(ρ) = exp(−αρ²) over the pupil.
- **Is this the reverse of the older progress report?** Yes. The older comparison used a paraxial Gaussian reference
  that was not valid; with a consistent scalar reference the Gaussian input extends the scalar range.
:::
:::

::: card
::: sl
9
:::

## Depth of focus and peak against ε, annular pupils

::: say
An annular pupil lengthens the focus as 1/(1 − ε²) at low NA and lowers the peak as (1 − ε²)².
:::

The field of an annular pupil is the field of the full pupil minus that of the obstructed part. At ε = 0.99 the depth
of focus over that of the full pupil is 50.13 at low NA against 50.25 from 1/(1 − ε²), and 30.4 at sin α = 0.9.

::: qa
- **How large is the gain at high NA?** 30.4 at sin α = 0.9 for ε = 0.99, against 50.25 from 1/(1 − ε²).
- **Does a thin annulus give a Bessel beam?** At low NA it gives the J~0~² profile of Durnin; at high NA the vector
  profile is narrower than the scalar one (FWHM 2.06 against 2.25 optical units).
:::
:::

::: card
::: sl
10
:::

## Depth of focus of annular pupils with few-cycle pulses

::: say
Few-cycle pulses keep the longer depth of focus of an annular pupil, down to 1 fs.
:::

At NA 0.8 and ε = 0.99 the depth of focus over that of the full pupil is 44.35 for a continuous beam and 44.33 at 1 fs.
On the axis the focus at 1 fs is 1.010 times longer than with a continuous beam.

::: qa
- **How much longer is the focus at 1 fs?** 1.010 times the continuous-beam focus on the axis at ε = 0.99.
:::
:::

::: card
::: sl
11
:::

## Transverse profile with pulses, full and annular pupils

::: say
Shorter pulses fill the zeros between the transverse rings, with the full pupil and with the annular one.
:::

The structural content across the axis is about 1.06 at 1 fs for both pupils. This is the loss of focal quality of
Romallosa et al. (2003), here with annular pupils.

::: qa
- **Why do the zeros fill?** Each frequency has its zeros at a different radius, so their sum has none.
:::
:::

::: {.part}
# Part 2. Two-color excitation with continuous beams
:::

::: card
::: sl
13
:::

## Two beams focused at an angle θ

::: say
2CE absorbs one photon of each color, so it forms where the two beams overlap and the signal is I~1~I~2~.
:::

Lens L2 is lens L1 turned by θ about the focus, with θ = 0 (collinear), π/2 (crossed) or π (facing). 2PE uses 700 nm
in both lenses, so the two fields add and interfere before the fourth power.

::: qa
- **Why 750 and 656 nm?** They add to the 350-nm level, 1/λ~e~ = 1/λ~1~ + 1/λ~2~, as in Cambaliza & Saloma (2000).
- **How is beam 2 turned?** In real space (x, z). Turning the optical coordinates (u, v) is not a rotation of real
  space at π/2, and it does not reproduce the fits of Lim & Saloma (2002).
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

With crossed lenses the 2CE spot is wider (0.763 µm against 0.517 µm) and the depth of focus shorter. With collinear
and facing lenses the 2CE profiles are identical, with a depth of focus of 3.56 µm.

::: qa
- **Do the ratios in the text agree too?** Several ratios quoted in the text at θ = π/2 differ from the published
  curves (for example 0.67 against 0.49 for the 2PE spot at π/2 over that at 0), while the plotted widths agree with
  current work. This is known and accepted.
- **Where does 0.67 µm for the axial width at π/2 come from?** It is beam 2 turned in (x, z); the (u, v) turn gives
  1.31 µm.
:::
:::

::: card
::: sl
16–17
:::

## 2CE peak against displacement of L2, θ = π and π/2

::: say
Displacing the focus of L2 lowers the 2CE peak, more slowly along the axis than across it with facing lenses.
:::

With facing lenses the fits of current work are −0.601 x~c~² + 0.888 across the axis and −0.027 z~c~² + 0.998 along it.
With crossed lenses the fit across the axis is −0.063 x~c~² + 0.999, against −0.06 x~c~² + 1 in Lim & Saloma (2002).

::: qa
- **Why does crossed-lens 2CE fall along z~c~?** The focus of L2 then moves across the long focus of L1, so the length
  of the focus of L1 sets the loss.
:::
:::

::: card
::: sl
18
:::

## 2CE peak against aberration, θ = 0 and π

::: say
Equal spherical aberration in the two beams keeps the 2CE peak at θ = 0, and opposite aberration keeps it at θ = π.
:::

At θ = 0 the peak at φ~1~ = φ~2~ = ±60 is 0.84 of the peak without aberration and at φ~1~ = −φ~2~ = ±60 it is 0.07; at
θ = π the two cases are exchanged. With crossed lenses the 2CE fidelity stays above 0.9 for coefficients up to 40, as in
Lim & Saloma (2003).

::: qa
- **Is the aberration the primary spherical aberration of each beam?** Yes, with coefficients φ~1~ and φ~2~, in the
  paraxial scalar model at NA 0.5, as in Lim & Saloma (2003).
:::
:::

::: card
::: sl
19–20
:::

## Displacement for 20% peak loss against NA

::: say
As NA increases the displacement that 2CE tolerates decreases as about 1/NA across the axis and 1/NA² along it.
:::

The fitted exponents from NA 0.1 to 0.5 are −0.99 across the axis and −2.04 along it with facing lenses, and −2.03 and
−2.04 with crossed lenses. The paraxial model gives a larger tolerance along the axis than the vector model, by 7% at
NA 0.5 and 47% near NA 0.95.

::: qa
- **Why 1/NA² with crossed lenses in both directions?** Both displacements move one focus along the length of the
  other beam, and the length of a focus scales as 1/NA².
- **What does a Gaussian input do?** It makes the tolerances about 1.4 times larger.
:::
:::

::: card
::: sl
21
:::

## Spot and depth of focus against NA: 2CE, θ = 0 and π

::: say
Along the axis the paraxial model gives too long a 2CE focus at high NA, by 7% at NA 0.5 and 36% at NA 0.9.
:::

The depth of focus is 3.33 µm at NA 0.5 and 0.81 µm at NA 0.9 in the vector model in air. The central spot stays within
5% up to NA 0.86. The paraxial model uses sin²α/2 for 1 − cos α, which lengthens the depth of focus by about
1 + tan²(α/2).

::: qa
- **Is the difference from the polarization?** No. The scalar Debye integral with the exact phase gives the vector
  depth of focus, so the small-angle phase causes it.
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

The two profiles are 3.56 against 3.33 µm at NA 0.5 and 1.10 against 0.81 µm at NA 0.9. The profile along the axis is
the same with collinear and facing lenses, since I~1~I~2~ does not depend on the direction of beam 2.

::: qa
- **Why show the profiles and not the widths?** The widths of the previous slide are the FWHM of these curves; the
  profiles show that the whole focus is longer, as well as its half-maximum width.
:::
:::

::: card
::: sl
23
:::

## Spot and depth of focus against NA: 2CE, θ = π/2

::: say
With crossed lenses both 2CE widths decrease as about 1/NA, and the paraxial model gives them within 4%.
:::

The 2CE spot is 0.75 by 0.66 µm at NA 0.5. The depth of focus is shorter than with collinear lenses, 13 times at NA 0.2
and 3.4 times at NA 0.7.

::: qa
- **Why 1/NA and not 1/NA²?** Each 2CE width is set by the transverse spot of the other beam, which scales as 1/NA.
:::
:::

::: card
::: sl
24–26
:::

## Paraxial over vector widths and Linfoot's criteria against NA

::: say
The paraxial 2CE departs from the vector one first along the axis with collinear and facing lenses, and stays close
with crossed lenses.
:::

Along the axis the gap reaches 5% at NA 0.43 in air (0.57 in water), across the axis at NA 0.86 (1.14). The structural
content C falls below 0.95 from NA 0.44 in air, while the fidelity across the axis stays at 0.996 or above. With crossed
lenses F ≥ 0.999, C ≥ 0.97 and Q ≥ 0.98 wherever the lenses fit.

::: qa
- **Why does C fall and not F?** Each profile is normalized to unit energy, so the longer paraxial focus has a lower
  peak and Σa² drops below Σr²; F, which measures the difference, changes more slowly.
:::
:::

::: card
::: sl
27
:::

## Annular pupils: depth of focus against NA, air

::: say
With an annular pupil the paraxial depth of focus departs sooner than with the circular one, because a thin ring uses
the edge of the pupil.
:::

At ε = 0.99 the 2CE depth of focus at θ = 0 is 155 µm in the vector model against 179 µm in the scalar one at NA 0.5,
and 25 against 55 µm at NA 0.9. Annular over circular, the depth of focus is 47 times at NA 0.5 and 31 at NA 0.9,
against 50 in the paraxial model.

::: qa
- **Why is the edge of the pupil the problem?** The paraxial phase error grows with the angle of the ray, and a thin
  ring has all of its rays at the largest angle.
:::
:::

::: card
::: sl
28
:::

## Crossed lenses above NA 0.71

::: say
Two lenses of the same NA fit at right angles up to NA n/√2, 0.71 in air and 0.94 in water.
:::

The half-angle of each cone must be at most 45°. Cambaliza & Saloma (2000) note on p. 34 that dual-beam excitation
with two identical objectives for θ up to π/2 is possible for NA up to 0.7.

::: qa
- **What happens above NA 0.71 in air?** The cones overlap and the two lenses cannot both be placed; the crossed-lens
  results above that NA are computed in water.
:::
:::

::: {.part}
# Part 3. Two-color excitation with optical pulses
:::

::: card
::: sl
30–31
:::

## Spectrum and waves of a 10-fs pulse, and the pulse in time

::: say
A pulse is a sum of continuous waves that are in phase at t = 0, and their sum falls off as a Gaussian of width τ.
:::

The nine waves span the Gaussian spectrum of a 10-fs pulse at 750 nm. They are in phase at t = 0 and out of phase at
15 fs, where the envelope has fallen to a few percent of its peak.

::: qa
- **Is the pulse chirped?** No. The pulses are transform-limited Gaussians, so all frequencies are in phase at t = 0.
:::
:::

::: card
::: sl
32–33
:::

## Pulse width and spectral bandwidth, and the spectra against wavelength

::: say
Shorter pulses have wider spectra, Δν = 0.441/τ, and below about 15 fs they reach 700 nm.
:::

The bandwidth is 88 THz at 5 fs, 44 THz at 10 fs, 22 THz at 20 fs and 4.4 THz at 100 fs. At 10 fs each spectrum has
31% of its peak at 700 nm (428 THz); at 20 fs and longer it has almost none.

::: qa
- **Why does 700 nm matter?** Two photons of 700 nm make 350 nm, so a pulse whose spectrum reaches 700 nm can excite
  the 350-nm level by itself.
:::
:::

::: card
::: sl
34
:::

## Photon pairs at the 350-nm level

::: say
The excitation adds the amplitudes of all photon pairs that reach 350 nm and then squares the sum.
:::

A = A^11^ + 2A^12^ + A^22^ with A^ab^ = ∫E~a~E~b~e^iω~e~t^dt, and F = |A|². 2A^12^ takes one photon from each beam
(the 350-nm pairs); A^11^ and A^22^ take both from one beam (the 375- and 328-nm pairs). For long pulses F becomes
I~1~I~2~, the result of Cambaliza & Saloma (2000).

::: qa
- **Why not add the intensities of the frequencies, as Romallosa et al. do?** Their sum is the time-integrated
  intensity; for a two-photon signal ∫I²dt is not (∫I dt)², and 2CE depends on when the two pulses arrive.
- **Which polarization is used?** Both beams are polarized perpendicular to the plane of the lens axes unless a slide
  says otherwise.
:::
:::

::: card
::: sl
35–36
:::

## 2CE at 100 fs and with continuous beams

::: say
At 100 fs pulsed 2CE is the same as with continuous beams at the three lens angles, so the results of Cambaliza &
Saloma (2000) hold for pulses of that length.
:::

The depth of focus is 3.56 µm with collinear lenses and 3.52 against 3.56 µm with facing lenses, where the pulses
overlap over 21 µm, six times the focus. With crossed lenses the spot is 0.76 µm in both cases.

::: qa
- **Is 100 fs long enough at all NAs?** With facing lenses it is not at low NA: the pulse width needed to match
  continuous beams to 1% is 87 fs at NA 0.5 but 260 fs at NA 0.3 (slide 41).
:::
:::

::: card
::: sl
37
:::

## Depth of focus, collinear and crossed lenses

::: say
With collinear and crossed lenses the 2CE depth of focus stays within a few percent of the continuous-beam value.
:::

With collinear lenses the two pulses travel together and overlap over the whole focus, so 2CE keeps its profile down to
4 fs. With crossed lenses the depth of focus grows by up to 6% below 10 fs, because the 375-nm pairs from L1 alone extend
along its axis.

::: qa
- **Then are crossed lenses the best choice with pulses?** They keep the sharpest profile, and their lenses fit up to
  NA 0.71 in air.
:::
:::

::: card
::: sl
38–39
:::

## Depth of focus with facing lenses, and the overlap of the facing pulses

::: say
With facing lenses 2CE forms where the two pulses meet, so its depth of focus is shorter, more so at lower NA.
:::

The facing pulses overlap over a stretch of FWHM G = cτ/(√2 n), 4.2 µm at 20 fs and 21 µm at 100 fs. At NA 0.5 the 2CE
depth of focus is 3.56 µm with continuous beams, 2.81 µm at 20 fs and 1.92 µm at 10 fs for the 350-nm pairs; with all
pairs it is 2.78 µm at 20 fs. With D the continuous-beam depth of focus the pulsed one is DG/√(D² + G²).

::: qa
- **Why is the shortening larger at lower NA?** The focus grows as 1/NA² while the stretch where the pulses meet stays
  the same, so the overlap cuts a larger part of it. At NA 0.3 and 20 fs it is 40% of the continuous-beam value.
- **Why is the computed width at 10 fs longer than the product?** The 375- and 328-nm pairs need no overlap of the two
  pulses (2.14 against 1.83 µm).
:::
:::

::: card
::: sl
40
:::

## Signal added by the 375- and 328-nm pairs

::: say
Below about 15 fs one beam alone also excites the 350-nm level, so 2CE starts to lose its weak background.
:::

The amplitude of the 375- and 328-nm pairs is 18% of that of the 350-nm pairs at 10 fs and below 1% at 20 fs. The peak
of the total over that of the 350-nm pairs is 1.02 at 20 fs, 1.15 at 15 fs, 1.73 at 10 fs and 3.1 at 5 fs.

::: qa
- **Do real probes absorb these pairs?** Lim & Saloma (2003) note that probes are chosen to minimize two-photon
  excitation by λ~1~ or λ~2~ alone; the model keeps all pairs, so it gives the case with no such selection.
:::
:::

::: card
::: sl
41–42
:::

## Pulse width to match continuous beams against NA

::: say
With facing lenses the pulse width needed to match continuous beams grows as NA decreases; with collinear and crossed
lenses short pulses already match.
:::

Facing lenses, vector model in air: about 25 fs at NA 0.9, 87 fs at NA 0.5, 260 fs at NA 0.3 and 610 fs at NA 0.2. At
NA 0.5 it is 87 fs in air, 164 fs in water and 216 fs in oil. With collinear lenses 4-fs pulses match, and with crossed
lenses 2CE matches from about 20 to 28 fs from NA 0.2 up. The scalar curves are drawn up to NA 0.5.

::: qa
- **What is the tolerance?** The largest difference between the pulsed and continuous-beam profiles, each scaled to its
  peak, stays below 1% of the peak.
- **Why do water and oil need longer pulses at the same NA?** The focus depends on NA/n, so at the same NA it is longer
  in water and oil.
:::
:::

::: card
::: sl
43–44
:::

## Pulse width to match continuous beams, pupils

::: say
With facing lenses a pupil with a longer depth of focus needs a longer pulse; with collinear and crossed lenses the
pupil changes the pulse width needed by little.
:::

The figure gives the pulse width from which the 2CE depth of focus stays within 1%: at NA 0.5 with facing lenses,
100 fs for the circular pupil, 162 fs for the Gaussian input and 466 fs for the annular pupil with ε = 0.9. By the
largest difference between the profiles the same three are 87, 139 and 405 fs.

::: qa
- **Why two sets of numbers?** The figure uses the depth of focus and the slide before uses the largest difference;
  both give the same order of the pupils.
:::
:::

::: card
::: sl
45–46
:::

## Summary by lens angle, and next steps

::: say
With collinear lenses a pulse changes nothing down to 4 fs, with crossed lenses a few percent below about 20 fs, and
with facing lenses it shortens the 2CE focus.
:::

Pulsed 2CE through a scattering medium is the first candidate for the next step, since it would show whether 2CE with
pulses keeps its weak background.

::: qa
- **Has any of this been compared with experiment?** No. No comparison with experiment or a full-wave solver is
  planned for now.
:::
:::

::: card
::: sl
50–55
:::

## Backup: 2PE

::: say
For 2PE the same trends hold with shorter pulses, because the pairs within one pulse need no overlap.
:::

The 2PE central spot with crossed lenses stays at 0.256 µm in air at all NAs. With facing lenses 2PE matches
continuous beams from 62 fs at NA 0.5, against 87 fs for 2CE. The 2PE side lobes weaken as NA increases.

::: qa
- **Why does the 2PE spot not shrink with NA at θ = π/2?** It is one interference fringe of the two beams, set by the
  wavelength in the medium.
:::
:::
