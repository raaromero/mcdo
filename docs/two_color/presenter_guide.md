---
title: "Presenter guide: two-color excitation with two confocal beams"
subtitle: "Cambaliza & Saloma, Opt. Commun. 184 (2000) 25–35, and current work · slide numbers refer to 2ce_meeting_cambaliza.pptx"
geometry: margin=2cm
fontsize: 10.5pt
---

# The story in six lines

1. **The question.** Two lenses focus two beams on one point, their axes at angle θ. Is two-color excitation (2CE)
   better than two-photon excitation (2PE)? *(slide 2)*
2. **Circular pupils.** No: 2PE has the sharper spot; 2CE only has weaker side lobes. *(slides 8–11)*
3. **Two wavelengths further apart.** The spot widens by about 6% and the focus shortens: a small trade-off.
   *(slides 13–15)*
4. **Annular pupils.** At θ = π/2, 2CE gets the better axial response (zeros, weak side lobes). *(slides 18–21)*
5. **Scattering (the paper's main point).** 2CE has little out-of-focus background. This is our next step.
   *(slides 55–59)*
6. **Our extensions.** The paraxial model gives too long a focus at high NA, but the comparisons of the paper still
   hold *(slides 28–41)*. Short pulses shorten the 2CE focus with facing lenses, at low NA only *(slides 43–54)*.

# Part 1 · Replication (slides 3–26)

**What to say first:** we computed every published profile from Eqs. 1–6. They match, except for one 2PE
convention and a few numbers stated in the text.

**Slides 5–7 · The model**

- Slide 5: paraxial scalar focus of each lens (Eq. 1); beam 2 is the same focus turned by θ. 2CE = I₁I₂, 2PE =
  |U₁ + U₂|⁴.
- Slide 6: Eq. 1 writes the turn in optical coordinates (u, v). Since u scales as NA²z and v as NA·x, that is
  not a turned lens.
- Slide 7: the published Fig. 3b follows a turn in real space (x, z): 0.67 µm. The (u, v) turn would give
  1.31 µm. At θ = 0 and π the two agree. **Conclusion: the authors turned the lens in real space, as we do.**

**Slides 8–11 · Circular pupils (Figs. 2–3)**

- Slide 8 (2PE across): at θ = π/2 the spot is sharpest, with side lobes from interference.
- Slide 9 (2CE across): at θ = π/2 the spot is wider, with no interference lobes.
- Slide 10 (2PE along): at θ = π the facing beams give fringes.
- Slide 11 (2CE along): θ = 0 and π equal 2PE at θ = 0.
- **Conclusion: identical to the published curves. With circular pupils 2CE has no resolution advantage
  (pp. 29–30).**

> *Move on:* 2CE has a freedom 2PE lacks. The two wavelengths can be pulled apart, as long as they still reach the
> same transition (1/λ₁ + 1/λ₂ = 1/350 nm).

**Slides 12–16 · Gap between the two wavelengths (Figs. 4–5)**

- Slide 12: Δλ = 10, 39, 94 nm at θ = π/2.
- Slide 13 (across): the spot widens by 6%. *Why:* across the axis the spot follows beam 1, which scales with λ₁
  (+6.4%).
- Slide 14 (along): the depth of focus shortens by 5.5%. *Why:* it follows beam 2, which scales with λ₂
  (−5.6%).
- Slide 15 (Fig. 5): same linear trends; our values are within 0.004 µm of the published points.
- Slide 16: our curve on their plot. Our FWHM slope is 5.2, theirs 4.9 (×10⁻⁴ µm/nm). Their points scatter enough
  to explain about half of that difference. Their caption equations match neither plotted line.
- **Conclusion: replicated; the published slope and caption are slightly off.**

> *Move on:* changing the wavelengths moves things by about 6%, so 2CE still has no clear advantage. Next the authors
> change the pupil: a thin ring gives each beam a long focus.

**Slides 17–22 · Annular pupils (Figs. 6–7)**

- Slide 18 (2PE across, θ = π/2): the spot is 0.71 times as wide as at θ = 0, with no zeros.
- Slide 19 (2CE across): zeros at all angles.
- Slide 20 (2PE along): flat at θ = 0, fringes at π, a peak on a background at π/2.
- Slide 21 (2CE along): flat at θ = 0 and π (no sectioning); a 1-µm peak with zeros at π/2.
- Slide 22: the published 2PE curves in Figs. 6a and 7a are |U₁ + U₂|² (the excitation), not Eq. 6. Fig. 6a's
  minimum (0.08) and Fig. 7a's background (0.25) only come out with |U₁ + U₂|².
- **Conclusion: 2CE identical. 2PE matches once we plot the excitation. At θ = π/2, 2CE has the better axial
  response (p. 32).**

**Slides 23–26 · Numbers in the text**

- Slide 23: most stated values match the figures. Three do not:

  | Page | Stated | On the published curves (and ours) | Slide |
  |---|---|---|---|
  | 28 | 2PE spot at π/2 is 0.67 × that at 0 | 0.49 | 24 |
  | 29 | 2CE spot 1.58 × wider than 2PE at π/2 | 2.98 | 25 |
  | 32 | annular 2CE focus 20% longer than circular 2PE | 85% | 26 |

- **Conclusion: we measured on their own curves; the text disagrees with them.**

> *Move on:* everything so far is at NA 0.5 with the paraxial model, which the paper trusts below NA 0.7. How far can
> it be trusted?

# Part 2 · High NA (slides 27–41)

**What to say first:** we compared the paraxial model with the exact vector (Richards–Wolf) focus, up to NA 0.95 in
air and 1.25 in water.

- Slide 28: summary.
- Slide 29 (2CE, θ = 0 and π): across the axis they agree. Along the axis the paraxial focus is too long: by 5% at
  NA 0.43 (air), 36% at 0.9. *Why:* the paraxial phase lengthens the focus by tan²(α/2).
- Slide 30 (2CE, θ = π/2): within 4% up to where crossed lenses fit (NA 0.71 air, 0.94 water).
- Slides 31–33 (2PE): θ = 0 as 2CE. At π/2 and at π along the axis, the width is an interference fringe set by the
  wavelength, so the models agree.
- Slides 34–35: the gap against NA, with the NA where it reaches 5%. In water the gap is smaller, because the cone is
  narrower at the same NA.
- Slides 36–37: the 2CE–2PE comparisons hold; scalar and vector agree within 4%.
- Slide 38: with annular pupils the paraxial focus is 2.2 times too long at NA 0.9, because only the pupil edge is used.
- Slides 39–40: the annular comparisons. Stars are the text values; crosses are values read off the published curves.
- Slide 41: the wavelength-gap trend holds at every NA.
- **Conclusion: the paraxial model is good across the axis and at θ = π/2. Along the axis at θ = 0 and π it
  departs from NA 0.43 (air) or 0.57 (water). The paper's comparisons hold at high NA.**

> *Move on:* 2CE needs both photons at the same place **and time** (p. 26), but the paper uses continuous beams.
> With femtosecond pulses, time enters.

# Part 3 · Optical pulses (slides 42–54)

**What to say first:** a pulse adds a duration τ, a spread of frequencies, and an arrival time at each point.

- Slide 44: what a pulse adds. 10 fs gives about 40 nm of bandwidth.
- Slide 45: **photon pairs.** One photon from each laser, with frequencies adding up to the transition. Each pair is
  weighted by its joint probability p₁p₂. The pairs add in amplitude.
- Slide 46: summing the pairs gives the continuous PSF × the overlap of the two pulses in time. **This is the same
  as the time-overlap calculation at zero delay.** At θ = π the pulses meet only within 2.1 µm of the focus (10 fs,
  air).
- Slide 47 (NA 0.5): the 2CE focus shortens from 3.6 to 1.9 µm at 10 fs.
- Slide 48: the effect fades with NA. *Why:* the focus becomes shorter than the 2.1-µm overlap, so the pulse has
  nothing left to cut. This is not a larger tolerance to a time delay; that is the next study.
- Slides 49–54: one slide per NA, in air and in water. 2PE keeps its central fringe; its outer fringes drop where
  the pulses do not meet.
- **Conclusion: pulses shorten the 2CE focus with facing lenses, at low NA only. At θ = 0 and π/2 they change
  little (≤ 2%).**

# Next steps and preview (slides 55–59)

- Slide 55: Monte Carlo for Fig. 8; a time delay between the pulses.
- Slides 57–58: Fig. 8 preview. 2PE has an out-of-focus background (0.09; published 0.1–0.2). The 2CE
  background is 0.07 (published near 0).
- Slide 59: the result depends on the slab thickness h, which the paper does not give.
- If asked why our Fig. 8 is smoother: we average 10 runs and count each photon at every plane it crosses.

# Likely questions

- **Is the replication exact?** Yes for Figs. 2–4, 6b and 7b. Figs. 6a and 7a match with |U₁ + U₂|². Fig. 5 is
  within 0.004 µm. *(slides 8–22)*
- **Why not the stated numbers?** Three ratios in the text disagree with the authors' own curves. *(slides 23–26)*
- **Why turn beam 2 in (x, z)?** That is a turned lens, and the published Fig. 3b follows it. *(slides 6–7)*
- **Are θ = 0 and π the same?** For 2CE, yes. For 2PE, yes across the axis; along it, π gives fringes.
  *(slides 8–11)*
- **Is high NA more tolerant with pulses?** No: the focus is already shorter than the pulse overlap. Tolerance to a
  delay comes next. *(slide 48)*
