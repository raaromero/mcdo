---
title: "Presenter guide · two-color excitation with two confocal beams"
subtitle: "Cambaliza & Saloma, Opt. Commun. 184 (2000) 25–35, and current work · slide numbers: 2ce_meeting_cambaliza.pptx · dashboard: 2color-excitation.vercel.app"
---

<!-- Build: pandoc presenter_guide.md -s --embed-resources --css presenter_guide.css -o guide.html, then print to PDF
     (headless Chromium --print-to-pdf). Each ::: card is one slide group: slide numbers in the margin, the takeaway
     first (say), the details, the dashboard step (demo), the transition (next). -->

::: {.card .story}
::: sl
Story
:::

## The story in six lines, and how robust each answer is

1. **The question.** Two lenses focus two beams on one point, at angle θ. Is 2CE better than 2PE, and does the answer
   hold when the conditions change? *(2)*
2. **Circular pupils.** 2PE is better: the sharper spot at all θ; 2CE has weaker side lobes. **Robust:** the same in the
   vector model up to high NA. *(9–12)*
3. **Wavelength gap.** **2CE is robust to it:** spot +6%, focus −5.5% across the full gap, at all NA; a ±5 nm laser
   tolerance moves them by ±0.7%. *(14–16)*
4. **Annular pupils.** 2CE is better along the axis at θ = π/2 (zeros, weak side lobes). **Not at θ = 0 or π:** there
   2CE has no optical sectioning. *(19–22)*
5. **Scattering, the paper's main point.** 2CE has the lower out-of-focus background. **Not yet robust:** our preview
   agrees in direction (0.07 against 0.09) but depends on the slab thickness, which the paper does not give. *(69–74)*
6. **Our extensions.** **High NA:** the 2CE–2PE comparisons are robust (within 4% between the models); the paraxial
   depth of focus is not (too long above NA 0.43 in air). *(29–53)* **Pulses:** 2CE changes with facing lenses at low NA
   (shorter focus) and is robust at high NA (4% or less); 2PE is robust at all NA (0.5%). *(55–68)*
:::

::: {.card .story}
::: sl
In practice
:::

## What the results mean

- **The paper's model at high NA:** good across the axis and with crossed lenses (θ = π/2), within 5% of the vector
  focus. Along the axis with facing lenses (θ = 0, π) its focus is too long above **NA 0.43** in air: use the vector focus.
  *Tab: Scalar vs vector at high NA; Focal spot with Model vector.*
- **The paper's conclusions** (2CE against 2PE) hold in both models; the 2CE spot stays wider (2.0× at NA 0.7). *Tab: Scalar vs vector → paper's comparisons.*
- **Wavelength choice:** the gap changes the 2CE widths by about 6% at every NA; a ±5 nm laser tolerance is ±0.7%. *Tab: Wavelength gap Δλ.*
- **Pulses:** shorten the 2CE focus only with facing lenses at low NA, while the focus is longer than the 2.1-µm overlap.
  2PE barely changes (0.5%): its focus is one interference fringe, and one beam alone still excites it. *(60)* *Tab: Femtosecond pulses.*
:::

::: {.card .story}
::: sl
Inset
:::

## The small map on every plot

- Its **red caption** says what is measured and where: "FWHM at z = 0" (across the axis) or "DOF at x = 0" (along it).
- The **computed focal spot** in (x, z), x to the right and z down, with its half-maximum contour in black.
- The **red line** is the cut that is plotted; the **black dimension line** beside the spot is the measured width.
- A **scale bar** in µm. In crowded figures the map sits outside the plots, at the right.

:::

::: {.part}
# Part 1 · Replication · slides 3–27
:::

::: open
**Say first:** we computed every published profile from Eqs. 1–6. They match, except for one 2PE convention and a few
numbers stated in the text.
:::

::: card
::: sl
5–8
:::

## Model, setup, rotation

::: say
The printed Eq. 1 lacks the NA factors. The authors' figures use the real-space turn, as ours do.
:::

- **5** · Paraxial scalar focus of each lens (Eq. 1). Beam 2 is the same focus turned by θ. 2CE = I₁I₂, 2PE = |U₁ + U₂|⁴.
- **6** · Both foci at O; with pulses, both reach O together. Lab: move one lens until the 2CE signal of a thin layer
  peaks; set a delay line the same way.
- **6 · Method:** Simpson's rule over the pupil (401 radii paraxial, 301 angles vector); pulses as sums over
  frequency and time. **No ODE, so no RK4** (correct the meeting's "RK4" here).
- **7** · A turned lens gives u_r = u cos θ − NA·v sin θ, v_r = v cos θ + (u/NA) sin θ. Direction: tan θ_opt = tan θ / NA
  (Dr. Bantang's hint): **45° appears as 63° at NA 0.5**.
- **8** · Fig. 3b follows the (x, z) turn: **0.67 µm**. The (u, v) turn gives **1.31 µm**. Equal at θ = 0 and π.

::: demo
**Focal spot** → θ = 45°, Rotation of beam 2: switch (x, z) ↔ (u, v) (slide 7). Slide 8: **Lens angle θ** → Width along, click 90°, switch the rotation.
:::
:::

::: card
::: sl
9–12
:::

## Circular pupils · Figs. 2–3 · NA 0.5

::: say
Identical to the published curves. With circular pupils 2CE has no resolution advantage (pp. 29–30).
:::

- **9** · 2PE across: sharpest at θ = π/2, with interference side lobes.
- **10** · 2CE across: wider at θ = π/2, no interference lobes.
- **11** · 2PE along: fringes at θ = π (facing beams).
- **12** · 2CE along: θ = 0 and π equal 2PE at θ = 0.

::: demo
**Lens angle θ** → Width across, click θ = 0, 90, 180 (9–10); Width along (11–12). Click a published figure below to load its settings.
:::

::: next
2CE has a freedom 2PE lacks: the two wavelengths can be pulled apart, as long as 1/λ₁ + 1/λ₂ = 1/350 nm.
:::
:::

::: card
::: sl
13–17
:::

## Gap between the wavelengths · Figs. 4–5

::: say
Replicated. Wider gap: spot **+6%**, focus **−5.5%**. The published slope and caption are slightly off.
:::

- **13 · What Δλ is:** Δλ = λ₁ − λ₂, with 1/λ₁ + 1/λ₂ = 1/350 nm fixed (the same transition as two 700-nm photons).
  So **both** wavelengths change: 0 nm = 700 + 700, 10 = 705 + 695, 39 = 720 + 681, 94 = 750 + 656 nm.
  λ₁ (lens L1) goes up, λ₂ (lens L2) goes down. The paper uses 10, 39 and 94 nm, at θ = π/2.
- **14** · Across: spot +6%. *Why:* it follows beam 1, which scales with λ₁ (+6.4%).
- **15** · Along: focus −5.5%. *Why:* it follows beam 2, which scales with λ₂ (−5.6%).
- **16** · Our values within **0.004 µm** of the published points.
- **16 · "Typical laser error?"** ±5 nm moves the spot by **±0.7%**. Bare diodes ±3–5 nm, packaged modules ±10–15 nm.
- **17** · FWHM slope: ours **5.2**, theirs **4.9** (×10⁻⁴ µm/nm). Their scatter explains about half. Their caption
  equations match neither line.

::: demo
**Wavelength gap Δλ** → Width both, click 10, 39, 94 nm (13–15); the left chart is Fig. 5 (16–17).
:::

::: next
About 6% either way, so still no clear advantage. Next the authors change the pupil: a thin ring gives each beam a
long focus.
:::
:::

::: card
::: sl
18–23
:::

## Annular pupils · Figs. 6–7

::: say
2CE identical. 2PE matches once we plot the excitation. At θ = π/2, 2CE has the better axial response (p. 32).
:::

- **19** · 2PE across, θ = π/2: spot **0.71×** that at θ = 0, no zeros.
- **20** · 2CE across: zeros at all angles.
- **21** · 2PE along: flat at θ = 0, fringes at π, a peak on a background at π/2. At π/2 the peak is one fringe of the
  two crossing waves (about λ/2 = 0.36 µm, on the order of λ₂ₚ) with no zeros, because beam 1 never vanishes on the axis.
- **22** · 2CE along: flat at θ = 0 and π (no sectioning); a 1-µm peak with zeros at π/2.
- **23 · Why 0.25 means |U₁ + U₂|²** (Fig. 7a, along the axis, θ = π/2). Beam 1 (annular) is a long needle along z, so
  |U₁|² = 1 all along the axis. Beam 2 crosses the axis: a narrow peak at z = 0, near 0 elsewhere.
  - Centre: the two equal fields add in phase, |U₁ + U₂|² = (1 + 1)² = **4**. Away from it: only beam 1, **1**.
  - Background / peak = 1/4 = **0.25** with |U₁ + U₂|² (we compute 0.257).
  - Eq. 6 squares it: (1/4)² = 1/16 ≈ **0.06** (we compute 0.068). The published curve sits at 0.25.
  - Fig. 6a's minimum, the same test: **0.08** with |U₁ + U₂|², **0.007** with Eq. 6; the paper shows 0.08.
- **23 · "4th power or squared?"** Eq. 6 is right: 2PE absorbs two photons, so the rate goes as I², and
  I = |U₁ + U₂|² is the intensity of the two beams together. |U₁ + U₂|² is the excitation light; |U₁ + U₂|⁴ is the
  2PE signal. The figures plot the light, not the signal.

::: demo
**Lens angle θ** → Pupil ε 0.99; Width across (19–20), along (21–22). Slide 23: "2PE plotted as" |U₁ + U₂|² gives the 0.25 background of Fig. 7a. **Annular pupil ε** → click ε 0 and 0.99 to compare.
:::
:::

::: card
::: sl
24–27
:::

## Numbers stated in the text

::: say
We measured on their own curves; three stated numbers disagree with them, with either width definition.
:::

| Page | Stated | FWHM on curves | 1/e² on curves | Slide |
|---|---|---|---|---|
| 28 | 2PE spot at π/2 = 0.67 × at 0 | **0.49** | 0.49 | 25 |
| 29 | 2CE spot 1.58 × 2PE at π/2 | **2.98** | 2.93 | 26 |
| 32 | annular 2CE focus 20% longer than circular 2PE | **85%** | 76% | 27 |

- **"Spot definition?"** The 1/e² width leaves all three far from the text, so the definition is not the cause.

::: demo
**Scalar vs vector at high NA** → Plot: paper's comparisons → pick the p. 28, p. 29 or p. 32 ratio; star = stated, cross = on the curves. The widths themselves: **Lens angle θ**, legend FWHMs at θ = 0 and 90.
:::

::: next
All of this is at NA 0.5 with the paraxial model, which the paper trusts below NA 0.7. How far can it be trusted?
:::
:::

::: {.part}
# Part 2 · High NA · slides 28–53
:::

::: open
**Say first:** we compared the paraxial model with the exact vector (Richards–Wolf) focus, up to NA 0.95 in air and
1.25 in water.
:::

::: card
::: sl
29–36
:::

## Widths against NA

::: say
Across the axis and at θ = π/2 they agree. Along the axis at θ = 0 and π the paraxial focus is too long from
**NA 0.43 (air)**, **0.57 (water)**.
:::

- **30** · 2CE, θ = 0 and π, along: paraxial too long by **5% at NA 0.43**, **36% at 0.9** (air). *Why:* the paraxial
  phase lengthens the focus by tan²(α/2).
- **31** · 2CE, θ = π/2: within **4%** up to where crossed lenses fit (NA 0.71 air, 0.94 water).
- **32–34** · 2PE: θ = 0 as 2CE. At π/2, and at π along the axis, the width is a fringe set by λ: models agree.
- **35–36** · The gap against NA, with the NA where it reaches 5%. Smaller in water: narrower cone at the same NA.

::: demo
**Scalar vs vector at high NA** → Plot width; Signal 2CE, Angle 0 and π, along, click NA 0.9 (30); Angle π/2 (31); Signal 2PE (32–34); Plot "scalar / vector" (35–36). The 2D spot at high NA: **Focal spot** → NA 0.9 (vector).
:::
:::

::: card
::: sl
37–47
:::

## Whole profiles, Linfoot, side lobes

::: say
Whole profiles tell the same story as the widths: 2CE along the axis departs, θ = π/2 stays close.
:::

- **37 · Definitions:** both profiles scaled to the same energy; a = scalar, r = vector.
  NRMSE = √(Σ(a − r)²/Σr²); **F** = 1 − Σ(a − r)²/Σr² (fidelity); **C** = Σa²/Σr² (structural content);
  **Q** = Σar/Σr² (correlation quality). F = 2Q − C and NRMSE = √(1 − F). All are 1 (NRMSE 0) for identical profiles.
- **38–39 · NRMSE** (Dr. Bantang's request), unit-energy profiles: 2CE along **6% at NA 0.5**, **25% at 0.9** (air);
  θ = π/2 stays ≤ 3%.
- **40–46 · Linfoot's criteria (own section):** one slide per signal and angle, as the width slides. F stays near 1;
  C and Q show the difference first, along the axis with facing lenses: at NA 0.9 in air F = **0.94**, C = **0.74**,
  Q = **0.84** (2CE); 2PE at θ = π: F = 0.91. Crossed lenses: all above 0.9. Water: the same values at a higher NA.
- **47 · Side lobes:** facing lenses at λ/2n (0.35 µm, air), crossed at λ/n. High NA: facing lobe moves out
  (0.63 λ/n at 0.9) as k⟨cos α⟩ falls; crossed lobe moves in and drops (0.42 → 0.04 of the peak).
- **47 · "Against wavelength?"** At a fixed NA every distance in the focus scales with λ: at NA 0.5 the first lobe sits
  at 0.533 λ (facing) and 0.932 λ (crossed) for λ = 0.6, 0.7 and 0.8 µm. So the curves in λ/n hold for any wavelength.
  2CE has no side lobes to measure (below 10⁻³ of the peak).

::: demo
**Scalar vs vector at high NA** → How it is measured: show (37, the equations drawn on a real profile); Plot NRMSE (38–39); Plot Linfoot F, C or Q with Signal and Angle as on each slide (40–46); Plot side-lobe distance or height, Signal 2PE (47).
:::
:::

::: card
::: sl
48–53
:::

## The paper's comparisons at high NA

::: say
The paper's comparisons hold at high NA: scalar and vector agree within 4%.
:::

- **48–49** · 2CE against 2PE at θ = π/2, across and along.
- **50** · Annular: paraxial focus **2.2× too long** at NA 0.9 (only the pupil edge is used).
- **51–52 · Star** = number in the text. **Cross** = same ratio on the paper's figures. Our paraxial curve passes
  through the cross. Text against figures: **40% vs 30%**, **20% vs 85%**; 35% and 34% agree.
- **53** · The wavelength-gap trend holds at every NA.

::: demo
**Scalar vs vector at high NA** → Plot: paper's comparisons (48–49, 51–52); Pupil annular, Direction along (50). **Wavelength gap Δλ** → the bottom charts (53).
:::

::: next
2CE needs both photons at the same place **and time** (p. 26), but the paper uses continuous beams. With
femtosecond pulses, time enters.
:::
:::

::: {.part}
# Part 3 · Optical pulses · slides 54–68
:::

::: open
**Say first:** a pulse adds a duration τ, a spread of frequencies, and an arrival time at each point.
:::

::: card
::: sl
56–59
:::

## What a pulse adds

::: say
The two photons must arrive within about τ of each other.
:::

- **56** · 10 fs gives about **40 nm** of bandwidth.
- **57 · Joint probability** (Dr. Bantang's framing): intensity = probability of a photon at (r, t); normalized
  spectrum = probability of its frequency. Independent lasers → product; over t: exp(−2 ln 2 (t₁ − t₂)²/τ²).
- **58 · Photon pairs:** one photon per laser, frequencies adding to the transition, weighted by p₁p₂, added in
  amplitude.
- **59** · Sum = continuous PSF × the time overlap. At θ = π the pulses meet only within **2.1 µm** (10 fs, air).

::: demo
**Femtosecond pulses** → θ = 180°, Width along, click τ = 10 fs: the 2CE map shrinks along z to the overlap of the pulses (59). Any tab: Beams → 10 fs.
:::
:::

::: card
::: sl
60–68
:::

## Pulses against NA

::: say
Pulses shorten the 2CE focus with facing lenses, at low NA only. At θ = 0 and π/2: 2% or less.
:::

- **60 · Pulsed 2PE:** |E₁ + E₂|⁴ has single-beam terms (I₁², I₂²: both photons from one pulse, no overlap needed)
  and two-beam terms (one photon from each pulse: only where the pulses meet). So the 2PE depth of focus changes by
  **0.5%** at 10 fs at every NA; only the outer fringes fade. 2CE (I₁I₂ only) is gated completely.
- **61** · NA 0.5: 2CE focus **3.6 → 1.9 µm** at 10 fs (paraxial). Vector, as in 62–68 and the dashboard:
  **3.3 → 1.9 µm**.
- **62** · Fades with NA. *Why:* the focus becomes shorter than the 2.1-µm overlap. **Not** a larger tolerance to a
  delay; that is the next study.
- **63–68** · One slide per NA, air and water. 2PE keeps its central fringe; outer fringes drop where the pulses
  do not meet.

::: demo
**Femtosecond pulses** → θ = 180°, Width along, click τ = 10 fs: maps pulsed (top) against continuous (below), profiles with continuous dashed (60–61); Left chart → pulsed / continuous for the ratio; the bottom chart is slide 62; set NA 0.7, 0.9, Medium water for 63–68. Model vector above NA 0.5.
:::
:::

::: {.part}
# Next steps and preview · slides 69–74
:::

::: card
::: sl
69–74
:::

## Fig. 8, scattering (preview)

::: say
2PE has an out-of-focus background; 2CE has less. The result depends on a slab thickness the paper does not give.
:::

- **69** · Next: Monte Carlo for Fig. 8 (one-count-per-photon test); a time delay between pulses; oil immersion
  (n = 1.515) to reach NA 1.4.
- **71–72** · Background: 2PE **0.09** (published 0.1–0.2); 2CE **0.07** (published near 0). 10 runs × 10⁶ photons per
  beam, as in the paper.
- **73 · Why so clean?** Each photon is counted at every plane it crosses, so neighbouring points share photons
  (97% correlated): the noise shows as a slow drift, not jitter, about 5% per run at the focus and 0.6% far from it.
  The paper's spiky noise fits counting in a fixed small area or only at scattering events; it does not say which.
- **74** · Depends on the slab half-thickness h.

::: demo
**Scattering (Fig. 8)** → h = 100 (71–72: beam from L1 red, L2 blue, no scattering grey); Show "one run" (73); click h on the left chart (74).
:::
:::

::: {.part}
# Likely questions
:::

::: {.card .qa}
::: sl
Q
:::

- **Is the replication exact?** Yes for Figs. 2–4, 6b, 7b. 6a and 7a match with |U₁ + U₂|². Fig. 5 within 0.004 µm. *Tab: Lens angle θ, click the published figures.*
  *(9–23)*
- **Why not the stated numbers?** Three ratios in the text disagree with the authors' own curves, with FWHM and 1/e². *Tab: Scalar vs vector → paper's comparisons.*
  *(24–27)*
- **Why turn beam 2 in (x, z)?** That is a turned lens, and Fig. 3b follows it; printed Eq. 1 lacks the NA factors. *Tab: Focal spot → Rotation of beam 2.*
  *(7–8)*
- **Which integrator?** Simpson's rule over the pupil, sums over frequency and time. No ODE, so no RK4 or RK45.
  *(6)*
- **Are θ = 0 and π the same?** 2CE: yes. 2PE: yes across; along, π gives fringes. *Tab: Lens angle θ.* *(9–12)*
- **Is high NA more tolerant with pulses?** No: the focus is already shorter than the overlap. Delay tolerance comes
  next. *(62)* *Tab: Femtosecond pulses, left chart.*
:::
