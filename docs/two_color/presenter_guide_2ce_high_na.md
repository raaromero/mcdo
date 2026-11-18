---
title: "Presenter guide: two-color excitation at high NA"
subtitle: "Slide numbers are those of 2ce_high_na.pptx (38 slides); the concise deck 2ce_high_na_main.pptx (16 slides) takes its slides from it with the same titles and bullets. The guide that pairs each slide with the dashboard is 2ce_high_na_guide.pdf."
---

<!-- Build (as presenter_guide.md): pandoc presenter_guide_2ce_high_na.md -s --embed-resources --css presenter_guide.css
     -o /Users/raaromero/mcdo_dev/output/08_two_color/decks/presenter_guide_2ce_high_na.html, then print it to PDF with
     headless Chromium: Chromium --headless=new --no-pdf-header-footer
     --print-to-pdf=/Users/raaromero/mcdo_dev/output/08_two_color/decks/presenter_guide_2ce_high_na.pdf
     file:///Users/raaromero/mcdo_dev/output/08_two_color/decks/presenter_guide_2ce_high_na.html. Each ::: card is one
     slide: the slide number in the margin, the slide title word for word, whether the slide is in the concise deck,
     the main point in one sentence (say), what to say, then the likely questions with short answers. Numbers come from
     the speaker notes of the deck, docs/progress/work_to_date.tex, docs/two_color/pulse_derivations.tex,
     docs/review/07_two_color_pulses/review_07.tex and the stored data files beside the figures (checked 2026-11-18).
     The cards of slides 3, 6, 8, 12, 15, 18, 19, 22, 23, 27 and 36 to 38 are those of
     presenter_guide_high_na_pulses.md, renumbered. No run-in labels or arrows in this file. -->

::: {.card .story}
::: sl
How
:::

## How to use this guide

- Each card is one slide of 2ce_high_na.pptx. Its number is the number of the slide in that deck, which is also printed in
  the corner of the slide.
- The line under the title says whether the slide is also in the concise deck 2ce_high_na_main.pptx, and at which
  number.
- The yellow box is the main point of the slide in one sentence, the paragraph under it is what to say, and the list
  at the end gives the questions that are likely and a short answer to each.
- The numbers that are not on the slide are in its speaker notes, with the equations in LaTeX.
- The title slide, the dividers and the glossary have no card.
:::

::: card
::: sl
2
:::

## Summary

*This slide is slide 2 of the concise deck.*

::: say
The conclusions of Cambaliza & Saloma (2000) hold at high NA with the vector (Richards–Wolf) focus, while their paraxial model overestimates the depth of focus above NA 0.43 in air, by 36% at NA 0.9.
:::

Read the five bullets in order: the extension, the comparison of the two models, the depth of focus, the crossed lenses and the conclusions of Cambaliza & Saloma (2000). The slides are for air unless they say otherwise; the same comparisons in water are on the slides of the widths against NA. The paraxial depth of focus is 7% longer than the vector one at NA 0.5 and 36% longer at NA 0.9.

::: qa
- **Which models are compared?** The paraxial scalar model is Eq. (1) of Cambaliza & Saloma (2000). The vector model is the Richards–Wolf focus of each lens, with both beams polarized perpendicular to the plane of the lens axes.
- **Why is the depth of focus wrong while the spot is right?** The small-angle phase of the paraxial model lengthens the focus along the axis by about 1 + tan²(α/2). Across the axis the two models differ by 1.2% at NA 0.5 and 5.9% at NA 0.9.
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

*This slide is slide 3 of the concise deck.*

::: say
2CE absorbs one photon of each color, so it forms where the two beams overlap and its signal is the product of the two intensities.
:::

Lens L2 is lens L1 rotated by θ about the common focus O, with θ = 0 for collinear, π/2 for crossed and π for facing lenses; L1 focuses 750 nm and L2 656 nm. Two-photon excitation (2PE) uses 700 nm in both lenses, so the two fields add and interfere before the fourth power.

::: qa
- **Why 750 and 656 nm?** One photon of each adds up to the 350-nm level, 1/λ~e~ = 1/λ~1~ + 1/λ~2~, as in Cambaliza & Saloma (2000).
- **How is beam 2 rotated?** In real space (x, z). A rotation of the optical coordinates (u, v), as written by Cambaliza & Saloma, is not a rotation of real space at π/2, and it does not reproduce the fits of Lim & Saloma (2002).
:::
:::

::: card
::: sl
4
:::

## Paraxial scalar model and vector (Richards–Wolf) focus

*This slide is slide 4 of the concise deck.*

::: say
The paraxial model of Cambaliza & Saloma (2000) uses the small-angle form of the phase of each ray, so its depth of focus exceeds that of the vector focus by about 1 + tan²(α/2), which is 1.07 at NA 0.5 and 1.39 at NA 0.9.
:::

The paraxial model writes the phase of each ray as −uρ²/2, the small-angle form of kz cos ϑ; with 1 − cos α replaced by sin²α/2 the depth of focus is lengthened by 1 + tan²(α/2). The vector focus keeps the exact phase and the three field components, with both beams polarized perpendicular to the plane of the lens axes. The computed 2CE depth of focus of the paraxial model is 7.1% longer at NA 0.5 and 36.3% longer at NA 0.9 in air, close to the factor.

::: qa
- **Is the difference due to the polarization?** No. The scalar Debye integral with the exact phase gives the vector profile along the axis, so the small-angle phase of the paraxial model causes the difference.
- **What are u and v?** The optical coordinates along and across the axis, u = (2π/λ) NA² z/n and v = (2π/λ) NA r; α is the half-angle of the focusing cone, sin α = NA/n.
:::
:::

::: card
::: sl
5
:::

## 2CE PSF in the x–z plane at NA 0.5 and NA 0.9, θ = 0 and π

*This slide is slide 5 of the concise deck.*

::: say
At high NA the paraxial 2CE PSF with collinear and facing lenses is longer than the vector one, by 7% at NA 0.5 and 36% at NA 0.9, so the paraxial model overestimates the depth of focus.
:::

The heat map is the vector PSF; the solid contours are the vector PSF at 10, 50 and 90% of the peak and the dashed contours the paraxial PSF. At NA 0.5 the central spot is 0.510 µm in the vector model and 0.516 µm in the paraxial one, and the depth of focus 3.33 µm against 3.56 µm. At NA 0.9 the spot is 0.270 µm against 0.286 µm, and the depth of focus 0.81 µm against 1.10 µm.

::: qa
- **Why one figure for θ = 0 and π?** The 2CE PSF is the same with collinear and facing lenses, since I~1~I~2~ does not depend on the direction of beam 2.
- **How large is the difference over the whole profile?** Along the axis the root-mean-square difference of the two normalized profiles is 6% at NA 0.5 and 25% at NA 0.9; across the axis it is 1% and 5% (slide 17).
:::
:::

::: card
::: sl
6
:::

## Central spot and depth of focus against NA: 2CE, θ = 0 and π

*This slide is slide 6 of the concise deck.*

::: say
As NA increases the paraxial depth of focus of 2CE shrinks more slowly than the vector one, so it is 5% longer from NA 0.43 in air, while the central spot stays within 5% up to NA 0.86.
:::

The vector 2CE depth of focus in air is 3.33 µm at NA 0.5 and 0.81 µm at NA 0.9. The 5% point, NA 0.43 in air and 0.57 in water, lies below the NA 0.7 stated by Cambaliza & Saloma (2000, p. 27). The paraxial model uses sin²α/2 for 1 − cos α, which lengthens the depth of focus by about 1 + tan²(α/2).

::: qa
- **Why does the paraxial model hold to a higher NA in water?** At the same NA the focusing cone is narrower in water, sin α = NA/n, and the paraxial error grows with α, so the 5% point moves from NA 0.43 in air to 0.57 in water.
- **Which NA do Cambaliza & Saloma (2000) give for the paraxial model?** NA 0.7, on p. 27; along the axis the paraxial depth of focus is already 5% longer than the vector one from NA 0.43 in air.
:::
:::

::: card
::: sl
7
:::

## 2CE PSF in the x–z plane at NA 0.5 and NA 0.7, θ = π/2

*This slide is slide 7 of the concise deck.*

::: say
With crossed lenses the paraxial and vector 2CE PSFs coincide within 1.4% at NA 0.5 and 3.4% at NA 0.7, because each width is set by the narrow transverse spot of the other beam.
:::

The heat map is the vector PSF and the contours are at 10, 50 and 90% of the peak, solid for the vector and dashed for the paraxial model. The crossed-lens 2CE spot is 0.752 by 0.662 µm in the vector model and 0.763 by 0.670 µm in the paraxial model at NA 0.5. At NA 0.7, the largest NA at which two crossed lenses fit in air, it is 0.521 by 0.461 µm against 0.539 by 0.476 µm.

::: qa
- **Why do the two models agree with crossed lenses?** Across the axis of L1 the 2CE is limited by the transverse spot of L1, and along that axis by the transverse spot of L2. The paraxial model gives these transverse spots within a few percent, while its error lies in the length of each focus.
- **Why stop at NA 0.7?** Two crossed lenses fit while the half-angle of each cone is at most 45°, so NA ≤ n sin 45°, 0.71 in air (slide 27).
:::
:::

::: card
::: sl
8
:::

## Central spot and depth of focus against NA: 2CE, θ = π/2

*This slide is not in the concise deck.*

::: say
With crossed lenses both 2CE widths shrink as NA increases, and the paraxial model follows the vector focus within 4%, because each width is set by the narrow transverse spot of the other beam.
:::

The crossed-lens 2CE spot is 0.75 by 0.66 µm at NA 0.5. Its depth of focus is shorter than with collinear lenses, and this advantage decreases as NA increases: 13 times shorter at NA 0.2 and 3.4 times shorter at NA 0.7.

::: qa
- **Why do the widths decrease as 1/NA and not 1/NA²?** Each 2CE width is set by the transverse spot of the other beam, which scales as 1/NA.
- **How close are the two models?** Within 3.4% in air up to NA 0.7 and within 3.1% in water up to NA 0.9, the largest differences being across the axis.
:::
:::

::: card
::: sl
9
:::

## 2PE PSF in the x–z plane at NA 0.5 and NA 0.9, θ = 0

*This slide is not in the concise deck.*

::: say
With collinear lenses the 2PE PSF has the shape of the 2CE PSF, so the paraxial 2PE focus is too long in the same way, by 7% at NA 0.5 and 36% at NA 0.9.
:::

With collinear lenses the two 700-nm beams have the same focus, so 2PE is the square of one intensity and has nearly the shape of the 2CE PSF, I~1~I~2~. The vector 2PE PSF is 0.511 µm wide and 3.33 µm long at NA 0.5, and 0.271 µm wide and 0.81 µm long at NA 0.9. The paraxial one is 3.57 µm long at NA 0.5 and 1.10 µm at NA 0.9.

::: qa
- **Why show 2PE at θ = 0?** It is the reference of the 2PE comparisons of Cambaliza & Saloma (2000) at θ = π/2 (p. 28), and it departs from the vector focus as 2CE does.
:::
:::

::: card
::: sl
10
:::

## Central spot and depth of focus against NA: 2PE, θ = 0

*This slide is not in the concise deck.*

::: say
2PE at θ = 0 changes with NA as 2CE at θ = 0, so its paraxial depth of focus is 5% longer than the vector one from NA 0.43 in air.
:::

The figure repeats that of 2CE on slide 6 for 2PE. Across the axis the two models agree within 5% up to NA 0.86 in air, and along the axis the paraxial depth of focus is 5% longer from NA 0.43 in air (0.57 in water).

::: qa
- **Is 2PE at θ = 0 identical with 2CE at θ = 0?** Nearly: its widths differ from those of 2CE by less than 0.01 µm at NA 0.5 and 0.9, for example 0.511 against 0.510 µm across the axis at NA 0.5.
:::
:::

::: card
::: sl
11
:::

## 2PE PSF in the x–z plane at NA 0.5 and NA 0.7, θ = π/2

*This slide is slide 8 of the concise deck.*

::: say
With crossed lenses the 2PE central spot is one interference fringe of the two beams, 0.256 µm wide in both models at NA 0.5 and at NA 0.7, and the fringes beside it weaken as NA increases.
:::

The two crossed 700-nm beams interfere, so the 2PE PSF is a set of fringes whose central one sets the width, 0.256 µm in both models; the two differ by 0.1% at NA 0.5 and 0.4% at NA 0.7. The side lobe falls from 0.11 of the peak at NA 0.5 to 0.04 at NA 0.7, because it lies on the narrow spot of the other beam, which narrows with NA.

::: qa
- **Why does the 2PE spot not shrink with NA?** It is one fringe of the interference of the two crossed beams, so its width is set by the wavelength in the medium, λ~2p~/n, not by the NA.
:::
:::

::: card
::: sl
12
:::

## Central spot and depth of focus against NA: 2PE, θ = π/2

*This slide is not in the concise deck.*

::: say
As NA increases the 2PE central spot at θ = π/2 keeps its width, 0.26 µm in air and 0.19 µm in water, because it is one interference fringe of the two crossed beams.
:::

The 2PE central spot stays at 0.256 µm in air at all NAs and at 0.19 µm in water, in both models within 0.4%. 2PE is narrower than 2CE and has stronger side lobes, as in Cambaliza & Saloma (2000).

::: qa
- **Why is the spot narrower in water?** The fringe spacing follows the wavelength in the medium, λ~2p~/n, so with n = 1.33 the spot is 1.33 times narrower, 0.19 µm against 0.26 µm.
:::
:::

::: card
::: sl
13
:::

## 2PE PSF in the x–z plane at NA 0.5 and NA 0.9, θ = π

*This slide is slide 9 of the concise deck.*

::: say
With facing lenses the 2PE PSF is a standing wave along the axis in both models, and at NA 0.9 the longer paraxial envelope keeps side fringes above 10% of the peak where the vector PSF has none.
:::

The two 700-nm beams travel in opposite directions, so they form fringes about λ~2p~/2 = 350 nm apart along the axis, under the envelope of the focus. The central fringe is 0.136 µm long at NA 0.5 in both models, and 0.166 µm (vector) against 0.158 µm (paraxial) at NA 0.9. Across the axis the paraxial spot is 1.2% wider at NA 0.5 and 5.9% wider at NA 0.9.

::: qa
- **Why does the spacing widen with NA?** Because the converging waves cross the axis at an angle; the spacing is 0.37 µm at NA 0.5 and 0.44 µm at NA 0.9, against λ/2n = 0.35 µm in air.
- **How high are the side fringes at NA 0.9?** The first side fringe is 0.42 of the peak in the vector model and 0.65 in the paraxial model, because the vector focus, which sets the envelope of the fringes, is shorter.
:::
:::

::: card
::: sl
14
:::

## Central spot and depth of focus against NA: 2PE, θ = π

*This slide is not in the concise deck.*

::: say
As NA increases fewer fringes of the 2PE standing wave fit inside the focus, about 9 at NA 0.5 and 2 at NA 0.9 in air, because the focus shortens as 1/NA² while the fringes stay about λ/2n apart.
:::

Across the axis F~2p~(x, 0, 0; π) is identical with F~2p~(x, 0, 0; 0). Along the axis the width is that of the central fringe, which widens from 0.13 to 0.17 µm as NA increases; paraxial and vector agree within 5% up to NA 0.91 in air. In water the focus holds about 17 fringes at NA 0.5 and 4 at NA 0.9.

::: qa
- **Why does the central fringe widen with NA?** The converging waves cross the axis at an angle, so the fringes spread slightly: the central fringe is 0.13 µm at NA 0.2 and 0.17 µm at NA 0.9.
:::
:::

::: card
::: sl
15
:::

## Paraxial over vector widths of 2CE against NA

*This slide is slide 10 of the concise deck.*

::: say
As NA increases the paraxial 2CE widths become larger than the vector ones, first along the axis, where the difference reaches 5% at NA 0.43 in air.
:::

Along the axis with collinear and facing lenses the difference reaches 5% at NA 0.43 in air and 0.57 in water; across the axis it reaches 5% at NA 0.86 in air and 1.14 in water. With crossed lenses it stays within 4%.

::: qa
- **What do the diamonds mark?** The NA at which the difference reaches 5%, interpolated between the computed NAs.
:::
:::

::: card
::: sl
16
:::

## Paraxial over vector widths of 2PE against NA

*This slide is not in the concise deck.*

::: say
As NA increases the paraxial 2PE widths at θ = 0 depart from the vector ones as the 2CE widths do, while with crossed lenses they stay within 0.4%.
:::

With collinear lenses the 2PE difference reaches 5% at NA 0.43 in air along the axis and NA 0.86 across it, as for 2CE. With facing lenses the paraxial central fringe becomes narrower than the vector one, by 5% at NA 0.91 in air (1.21 in water). Across the axis 2PE at θ = π equals 2PE at θ = 0 and is not drawn twice.

::: qa
- **Why do the crossed-lens 2PE widths of the two models agree within 0.4%?** The central fringe is set by the wavelength in the medium in both models, not by the phase of the rays at the edge of the pupil.
:::
:::

::: card
::: sl
17
:::

## Whole-profile difference of 2CE, paraxial against vector

*This slide is not in the concise deck.*

::: say
As NA increases the whole paraxial 2CE profile departs from the vector one along the axis much more than across it: by 25% at NA 0.9 along the axis and by 5% across it, in air.
:::

The measure is the normalized root-mean-square difference (NRMSE) of the two profiles, each scaled to unit area over the plotted window, relative to the vector profile; it equals √(1 − F), with F the fidelity of Linfoot. Along the axis with collinear and facing lenses it is 6% at NA 0.5 and 25% at NA 0.9 in air, and across the axis 1% and 5%. With crossed lenses it is 3% or less wherever the lenses fit.

::: qa
- **Why compare whole profiles and not the widths alone?** The widths compare the profiles at half maximum, while the NRMSE also counts the tails and side lobes; both show the same split between the two directions.
:::
:::

::: card
::: sl
18
:::

## Linfoot’s criteria against NA: 2CE, θ = 0 and π

*This slide is not in the concise deck.*

::: say
As NA increases the paraxial 2CE along the axis becomes longer and lower than the vector one, so the structural content C falls first, below 0.95 from NA 0.44 in air.
:::

Along the axis C is below 0.95 from NA 0.44 in air and 0.58 in water, where the depth of focus departs by 5%. The fidelity F stays above 0.99 up to NA 0.63 in air and 0.84 in water, and across the axis F stays at 0.996 or above at all NAs.

::: qa
- **What are F, C and Q?** The fidelity F = 1 − Σ(a − r)²/Σr², the structural content C = Σa²/Σr² and the correlation quality Q = Σar/Σr² of Linfoot, with r the vector profile and a the paraxial one, both at unit energy; all three are 1 for identical profiles.
- **Why does C fall before F?** Each profile is normalized to unit energy, so the longer paraxial focus has a lower peak and Σa² drops below Σr²; F stays above 0.99 up to a higher NA.
:::
:::

::: card
::: sl
19
:::

## Linfoot’s criteria against NA: 2CE, θ = π/2

*This slide is not in the concise deck.*

::: say
With crossed lenses the paraxial and vector 2CE stay alike wherever the lenses fit, with the fidelity F at 0.999 or above.
:::

These bounds hold at the computed NAs up to NA 0.7 in air and 0.9 in water, below the NAs 0.71 and 0.94 at which crossed lenses stop fitting, so with crossed lenses the paraxial model gives the profiles of the vector focus. The lowest structural content is C = 0.967, across the axis at NA 0.7 in air, which the slide gives as 0.97.

::: qa
- **Why are the crossed-lens profiles alike?** Each width is set by the narrow transverse spot of the other beam, which the paraxial model reproduces (slide 8).
:::
:::

::: card
::: sl
20
:::

## 2PE and 2CE central spots against NA, circular pupils

*This slide is slide 11 of the concise deck.*

::: say
As NA increases the 2CE spot at θ = π/2 shrinks while the 2PE spot keeps its width, so 2PE at θ = π/2 stays the sharpest distribution, as at NA 0.5 (p. 28).
:::

The left panel gives the 2PE spot at θ = π/2 over that at θ = 0: 0.50 at NA 0.5 and 0.71 at NA 0.7 in air. The right panel gives the 2CE spot over the 2PE spot at θ = π/2: 2.9 at NA 0.5 and 2.0 at NA 0.7. Scalar and vector agree within 4%.

::: qa
- **Do these ratios agree with those stated by Cambaliza & Saloma (2000)?** The ratios stated in the text at θ = π/2 (0.67 and 1.58) differ from those measured on their own curves (0.49 and 2.98), while current work agrees with the curves. This is known and accepted.
:::
:::

::: card
::: sl
21
:::

## 2CE and 2PE depth of focus against NA, θ = π/2

*This slide is not in the concise deck.*

::: say
As NA increases the 2CE depth of focus at θ = π/2 shortens while the 2PE depth of focus stays one fringe, so the broader depth of focus of 2CE (p. 30) remains at high NA but the difference shrinks.
:::

The 2CE depth of focus at θ = π/2 is 2.6 times that of 2PE at NA 0.5 and 1.8 times at NA 0.7 in air. In water it is 3.5 times at NA 0.5 and 1.9 times at NA 0.9. Scalar and vector agree within 4%.

::: qa
- **Why does the ratio fall?** The 2PE width is that of the central fringe, which does not change with NA, so the ratio falls as the 2CE focus shortens.
:::
:::

::: card
::: sl
22
:::

## Side lobes of 2PE against NA: distance from the peak and height

*This slide is slide 12 of the concise deck.*

::: say
As NA increases the 2PE side lobes weaken, so the drawback of 2PE that Cambaliza & Saloma (2000) report at NA 0.5 becomes smaller at high NA.
:::

At θ = π/2 the side lobe falls from 0.11 of the peak at NA 0.5 to 0.04 at NA 0.7 in air; at θ = π it falls from 0.97 to 0.42 at NA 0.9. The distance of the side lobes from the peak is λ/2n with facing lenses and λ/n with crossed lenses at low NA. The 2CE side lobes stay below 10⁻³ of the peak.

::: qa
- **Why do weaker side lobes matter?** Weaker side lobes give images of higher contrast.
- **Why do the facing-lens side lobes weaken?** The vector focus, which sets the envelope of the fringes, shortens with NA; at NA 0.9 the first side fringe is 0.42 of the peak in the vector model against 0.65 in the paraxial model.
:::
:::

::: card
::: sl
23
:::

## Annular pupils: depth of focus against NA, air

*This slide is not in the concise deck.*

::: say
As NA increases the paraxial depth of focus of an annular pupil departs from the vector one sooner than that of the circular pupil, because a thin ring uses the edge of the pupil, where the paraxial phase error is largest.
:::

At ε = 0.99 the 2CE depth of focus at θ = 0 is 155 µm in the vector model against 179 µm in the scalar one at NA 0.5, and 25 against 55 µm at NA 0.9. The annular depth of focus is 47 times the circular one at NA 0.5 and 31 times at NA 0.9, against 50 in the paraxial model.

::: qa
- **Why is the edge of the pupil the problem?** The paraxial phase error grows with the angle of the ray, and a thin ring has all of its rays at the largest angle.
:::
:::

::: card
::: sl
24
:::

## Annular central spots against NA: the comparisons of p. 31

*This slide is not in the concise deck.*

::: say
As NA increases the annular 2CE spot at θ = 0 stays 0.67 of that at θ = π/2, while the annular 2PE spot at θ = π/2 loses its lead over the annular 2CE spot.
:::

The left panel gives the annular 2CE spot at θ = 0 over that at θ = π/2: 0.67 at all NAs, as on the published Fig. 6b, while the text of p. 31 states 0.82. The right panel gives how much narrower the annular 2PE spot is than the 2CE spot at θ = π/2: 53% at NA 0.5 and 34% at NA 0.7 in the paraxial model, and 52% and 31% in the vector model. The text of p. 31 states 35%, close to the 34% of Fig. 6a, which plots the excitation |U~1~ + U~2~|².

::: qa
- **Are the 53% and 34% on the slide those of the vector focus?** They are the values of the paraxial model; the vector model gives 52% at NA 0.5 and 31% at NA 0.7 (high_na/pupils/widths.csv).
- **Why do the stated and plotted values differ?** Several ratios in the text of Cambaliza & Saloma (2000) differ from their own curves at θ = π/2, while current work agrees with the curves; this is known and accepted.
:::
:::

::: card
::: sl
25
:::

## Annular depth of focus against NA: the comparisons of p. 32

*This slide is not in the concise deck.*

::: say
As NA increases the annular 2CE depth of focus at θ = π/2 stays about 30% shorter than the circular one, and its lead over the 2PE depth of focus shrinks.
:::

The left panel gives how much shorter the annular 2CE depth of focus is than the circular one at θ = π/2: about 30% at all NAs, as on the published curves, while the text of p. 32 states 40%. The right panel gives how much longer the annular 2CE depth of focus is than the circular 2PE one. At NA 0.5 it is 85% in the paraxial model, as on the published curves, and 81% in the vector model, while the text states 20%.

::: qa
- **Is the 85% on the slide that of the vector focus?** It is the value of the paraxial model and of the published curves; the vector model gives 81% at NA 0.5 and 26% at NA 0.7 (high_na/pupils/widths.csv).
:::
:::

::: card
::: sl
26
:::

## 2CE response to the wavelength gap Δλ against NA, θ = π/2

*This slide is not in the concise deck.*

::: say
As NA increases the effect of the wavelength gap on 2CE at θ = π/2 stays the same, so the trade-off of p. 30 between the central spot and the depth of focus holds at high NA.
:::

From Δλ = 10 to 94 nm the 2CE central spot at θ = π/2 grows by 6.1% at NA 0.5 and 5.7% at NA 0.7 in air, and the depth of focus shrinks by 5.4% and 5.2%. The central spot follows λ~1~ and the depth of focus follows λ~2~ at all NAs, with 1/λ~1~ + 1/λ~2~ = 1/350 nm fixed. The vector, unpolarized and scalar models agree within 0.3% in this relative change.

::: qa
- **Why does the spot follow λ~1~ and the depth of focus λ~2~?** With crossed lenses the width across the axis of L1 is set by the transverse spot of L1 (λ~1~) and the width along that axis by the transverse spot of L2 (λ~2~); a larger gap lengthens λ~1~ and shortens λ~2~.
:::
:::

::: card
::: sl
27
:::

## Largest NA of two crossed lenses

*This slide is slide 13 of the concise deck.*

::: say
Two lenses with crossed axes fit side by side while the half-angle of each focusing cone is at most 45°, so their NA is at most 0.71 in air and 0.94 in water.
:::

The condition is NA ≤ n sin 45° = n/√2. Cambaliza & Saloma (2000) note on p. 34 that dual-beam excitation with two identical objectives is possible for NA ≤ 0.7.

::: qa
- **What happens above NA 0.71 in air?** The two cones overlap and the two lenses cannot both be placed, so the vector results with crossed lenses above that NA are computed in water, up to NA 0.94.
:::
:::

::: card
::: sl
28
:::

## Summary: high NA

*This slide is slide 14 of the concise deck.*

::: say
The conclusions of Cambaliza & Saloma (2000) hold at high NA, while the differences between 2PE and 2CE shrink and the paraxial model overestimates the depth of focus.
:::

Read the five bullets in order. The vector focus has both beams polarized perpendicular to the plane of the lens axes. The paraxial error of the depth of focus grows as tan²(α/2) and is about half as large in water as in air at the same NA; with annular pupils the paraxial depth of focus is 2.2 times too long at NA 0.9 in air.

::: qa
- **Up to which NA can the paraxial model be used?** In air, up to NA 0.86 for the central spot and up to NA 0.43 for the depth of focus, within 5% of the vector focus; with crossed lenses within 4% wherever the lenses fit.
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

*This slide is not in the concise deck.*

::: say
As NA increases the whole paraxial 2PE profile departs from the vector one as 2CE does at θ = 0, and along the axis at θ = π by 7% at NA 0.5 and 29% at NA 0.9 in air.
:::

With crossed lenses the difference stays at 5% or less, because the fringes are set by the wavelength in both models. Across the axis at θ = π the 2PE profile equals that at θ = 0 and is not drawn twice.

::: qa
- **Why is the facing-lens 2PE difference the largest?** The paraxial envelope is too long, so the paraxial profile keeps side fringes that the vector profile does not have (slide 13).
:::
:::

::: card
::: sl
33
:::

## Linfoot’s criteria against NA: 2PE, θ = 0

*This slide is not in the concise deck.*

::: say
F~2p~ at θ = 0 departs from the vector focus as F~2c~ at θ = 0, with C below 0.95 from NA 0.44 in air and F below 0.99 from NA 0.63.
:::

Across the axis F stays at 0.996 or above at all NAs. At NA 0.9 along the axis F is 0.94 and C is 0.74, the values of 2CE.

::: qa
- **Why do F~2p~ and F~2c~ agree at θ = 0?** With collinear lenses the 2PE PSF has nearly the shape of the 2CE PSF (slide 9), so the same paraxial error enters both.
:::
:::

::: card
::: sl
34
:::

## Linfoot’s criteria against NA: 2PE, θ = π/2

*This slide is not in the concise deck.*

::: say
With crossed lenses the paraxial 2PE keeps the fidelity F at 0.997 or above wherever the lenses fit, while along the axis the structural content C falls to 0.91.
:::

Across the axis F, C and Q stay above 0.97. Along the axis C is 0.915 at NA 0.7 in air and 0.91 at NA 0.9 in water.

::: qa
- **What is the difference between F and C?** F = 1 − Σ(a − r)²/Σr² counts the squared difference of the two profiles, while C = Σa²/Σr² compares their heights at unit energy, so C responds first when the paraxial profile is lower or flatter.
:::
:::

::: card
::: sl
35
:::

## Linfoot’s criteria against NA: 2PE, θ = π

*This slide is not in the concise deck.*

::: say
As NA increases the paraxial envelope of the 2PE fringes along the axis with facing lenses becomes too long, so C falls below 0.95 from NA 0.44 in air and F below 0.99 from NA 0.58.
:::

In water the two NAs are 0.58 and 0.78. At NA 0.95 in air F = 0.85, the lowest of all cases, and at NA 0.9 it is 0.91.

::: qa
- **Why is this the lowest case?** The facing-lens 2PE profile along the axis has fringes under the envelope of the focus, and the paraxial envelope is too long, so the paraxial profile keeps side fringes that the vector profile does not have (slide 13).
:::
:::

::: card
::: sl
36
:::

## Axial 2CE PSF at NA 0.5 and NA 0.9: paraxial and vector focus

*This slide is not in the concise deck.*

::: say
At NA 0.9 the paraxial depth of focus of 2CE is 36% longer than the vector one, against 7% at NA 0.5, because the paraxial model uses the small-angle form of the phase of each ray.
:::

The paraxial and vector depths of focus are 3.56 and 3.33 µm at NA 0.5, and 1.10 and 0.81 µm at NA 0.9. The profile along the axis is the same with collinear and facing lenses, since I~1~I~2~ does not depend on the direction of beam 2.

::: qa
- **Why show the profiles and not the widths?** The widths of slide 6 are the FWHM of these profiles; the profiles show that the whole paraxial focus is longer, not its half-maximum width alone.
:::
:::

::: card
::: sl
37
:::

## Misalignment for a 20% loss of the 2CE peak against NA, θ = π

*This slide is not in the concise deck.*

::: say
As NA increases, the misalignment that reduces the peak 2CE fluorescence by 20% decreases as about 1/NA across the axis and 1/NA² along it, because it follows the width and the length of the focus.
:::

With facing lenses the fitted exponents from NA 0.1 to 0.5 are −0.99 across the axis and −2.04 along it. The paraxial scalar model gives a larger tolerated misalignment along the axis than the vector model, by 7% at NA 0.5 and by 47% near NA 0.95.

::: qa
- **What does a Gaussian input do?** A Gaussian input with α = 4 makes the tolerated misalignments about 1.4 times larger.
:::
:::

::: card
::: sl
38
:::

## Misalignment for a 20% loss of the 2CE peak against NA, θ = π/2

*This slide is not in the concise deck.*

::: say
With crossed lenses both tolerated misalignments decrease as about 1/NA², because each lies along the length of the focus of one of the two beams.
:::

The fitted exponents from NA 0.1 to 0.5 are −2.03 and −2.04. The vector focus is computed in air up to NA 0.71, where two crossed lenses fit, and in water up to NA 0.94.

::: qa
- **Why 1/NA² in both directions?** Each misalignment moves one focus along the length of the other beam, and in the paraxial model the length of a focus scales as 1/NA².
:::
:::
