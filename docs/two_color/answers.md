---
title: "Answers to your questions · two-color excitation"
subtitle: "Collected from the working session of 2026-10-20 to 22 · slide numbers: 2ce_meeting_cambaliza.pptx (77 slides) · dashboard tabs as named on 2color-excitation.vercel.app"
---

::: {.part}
# Main results
:::

::: card
::: sl
Q1
:::

## Are the main results the replication, with minor differences, plus the two extensions?

::: say
Yes. The replication reproduces every published profile; the differences are minor and do not change the paper's
conclusions. Then two extensions: high NA and optical pulses. Fig. 8 (scattering) is still a preview.
:::

- **Replication (Figs. 2–7, NA 0.5).** Minor differences:
  - Eq. 1 as printed turns beam 2 in (u, v) without the NA factors; the paper's own figures follow the real-space turn, as ours do.
  - Figs. 6a and 7a plot the 2PE excitation |U₁ + U₂|², not Eq. 6 (the equation is right).
  - Fig. 5: slopes 5–9% apart; its caption equations do not match its plotted lines.
  - Three ratios written in the text (pp. 28, 29, 32) disagree with the paper's own curves.
- **High NA:** the 2CE–2PE comparisons hold in the vector model; the paraxial depth of focus with facing lenses is too
  long above NA 0.43 in air.
- **Optical pulses:** shorter 2CE focus with facing lenses at low NA only; 2PE barely changes.
- **Fig. 8** depends on a slab thickness the paper does not give, and its noise differs: listed under next steps.
:::

::: card
::: sl
Q2
:::

## Practical, high-level results: is it more robust at high NA or not?

| Question | Answer |
|---|---|
| Is the paper's paraxial model good enough at high NA? | Across the axis and with crossed lenses (θ = π/2): yes, within 5% of the vector focus. Along the axis with facing lenses (θ = 0, π): no, the focus is too long above NA 0.43 in air (0.57 in water). |
| Do the paper's conclusions hold at high NA? | Yes, in both models. The 2CE spot is 2.9× the 2PE spot at NA 0.5, 2.0× at NA 0.7. |
| How sensitive is 2CE to the wavelength choice? | About 6% across the full gap, at every NA; a ±5 nm laser tolerance is ±0.7%. |
| What do pulses do to 2CE? | Shorten the focus with facing lenses at low NA only: 0.57 of continuous at NA 0.5, 0.96 at NA 0.9 (10 fs). |
| What do pulses do to 2PE? | Almost nothing: the depth of focus changes by 0.5% at 10 fs, at every NA. |

**Robustness, point by point:** circular pupils, 2PE better, robust up to high NA · wavelength gap, 2CE robust ·
annular pupils, 2CE better along the axis at θ = π/2 only · scattering, 2CE lower background, not yet robust (depends
on h) · high NA, comparisons robust, paraxial depth of focus not · pulses, 2CE changes at low NA, 2PE robust.
:::

::: {.part}
# Replication
:::

::: card
::: sl
Q3
:::

## Are the side lobes given in the original paper?

::: say
Only in words. The paper says 2PE has stronger side lobes than 2CE; it gives no heights or positions.
:::

| Page | The paper's statement |
|---|---|
| 28 | 2PE across, θ = π/2: spot about 0.67× that at θ = 0, "however … exhibits stronger side lobes that decay slowly with r due to the second-order interference between the two 2PE beams." |
| 29 | 2CE across "does not show second-order interference effects unlike [2PE], but its central spot diameter is 1.58 times wider." |
| 29 | 2PE along, θ = π: "significantly narrower … However, it also exhibits strong side lobes." |
| 30 | 2CE along "has weaker side lobes than [2PE] but with a broader DOF." |
| 34 | Conclusions: "Both [2PE along and across] … exhibit stronger side lobes than their respective 2CE counterparts." |

- "2PE has the sharper spot; 2CE only has weaker side lobes" matches the paper.
- Current work, not the paper: side lobes against NA (slide 47) and the numbers on slides 9–12.
:::

::: card
::: sl
Q4
:::

## Did the paper measure the FWHM, or something else? Can that explain 1.58?

::: say
No. The paper defines the FWHM only for Fig. 5; elsewhere it says "central spot diameter" without a definition. No
consistent width definition gives 1.58.
:::

2CE over 2PE at θ = π/2 (stated 1.58; 2CE FWHM 0.763 µm):

| Same definition for both | 2PE as Eq. 6 (\|U₁+U₂\|⁴) | 2PE as \|U₁+U₂\|² |
|---|---|---|
| FWHM | 2.98 | 2.15 |
| 1/e | 2.97 | 2.17 |
| 1/e² | 2.93 | 2.21 |
| 10% of the peak | 2.92 | 2.22 |
| first minimum to first minimum | 2.51 | 2.51 |

- 1.58 appears only when two different definitions are mixed (not plausible). Closest sensible: against 2PE at θ = 0, 1.47 (FWHM).
- Other stated numbers, all definitions: p. 31, 35% narrower → **34%** with |U₁+U₂|²; p. 32, 40% shorter → **37.5%**
  between first minima; Fig. 6b, 0.82 → 0.875 between first minima. p. 28 (0.67), p. 29 (1.58) and p. 32 (20%): no definition fits.
:::

::: card
::: sl
Q4b
:::

## What could "central spot diameter" mean? What are 1/e and 1/e²?

::: say
The width of the central peak, cut at some fraction of its height. The usual choices cut at 1/2, 1/e or 1/e² of the peak,
or at the first zeros.
:::

| Definition | Cut at (of the peak) | Where it is used |
|---|---|---|
| FWHM | 1/2 = 50% | microscopy resolution, our widths |
| 1/e width | 1/e ≈ 36.8% | some optics texts |
| 1/e² width | 1/e² ≈ 13.5% | laser beams: the Gaussian beam radius w (waist) |
| first zero to first zero | 0 | the Airy disk: radius 0.61 λ/NA |

- e = 2.718…, so 1/e ≈ 0.368 and 1/e² ≈ 0.135. Lower cuts give wider diameters.
- For a Gaussian spot I = exp(−2r²/w²), the diameters are fixed multiples of w: FWHM 1.18 w, 1/e 1.41 w, 1/e² 2 w.
- **Ratios hardly change with the definition when the two profiles have the same shape;** they only move when the
  shapes differ (side lobes, fringes). That is why every definition gives 2.15–2.98 for the p. 29 ratio, never 1.58 (Q4).
- The paper's wording ("central spot", "zero points") suggests an Airy-like reading (first zeros), but that gives 2.51.

:::

::: card
::: sl
Q5
:::

## Explain: "At θ = π/2 the central spot is near λ₂ₚ, without zeros; its 0.25 background is that of |U₁ + U₂|², not Eq. 6"

Fig. 7a: 2PE along the axis, annular pupils, crossed beams.

- **Beam 1** (along z, annular) is a long needle: on the axis |U₁|² ≈ 1 everywhere. **Beam 2** crosses the axis: a
  narrow peak at z = 0, near 0 elsewhere. Same 700 nm, so they interfere.
- **Central spot:** one interference fringe, about λ/2 = 0.36 µm, on the order of λ₂ₚ = 0.7 µm. **No zeros:** beam 1
  never vanishes on the axis, so the fields cannot cancel (minimum 0.09).

| | Value | Why |
|---|---|---|
| Centre | (1 + 1)² = 4 | equal fields in phase |
| Away from the centre | 1 | beam 1 alone |
| Background / peak, \|U₁ + U₂\|² | 1/4 = **0.25** (computed 0.257) | the published curve |
| Same with Eq. 6, \|U₁ + U₂\|⁴ | (1/4)² ≈ **0.06** (computed 0.068) | |

- Fig. 6a gives the same test: minimum 0.08 with |U₁+U₂|², 0.007 with Eq. 6; the paper shows 0.08.
- **Eq. 6 is right:** two photons, rate ∝ I², I = |U₁ + U₂|². |U₁ + U₂|² is the excitation light, |U₁ + U₂|⁴ the 2PE signal.
:::

::: card
::: sl
Q5b
:::

## What is the |U₁ + U₂|⁴ equation?

::: say
It is the 2PE signal: the light of the two beams added as fields, |U₁ + U₂|², and then squared, because two-photon
absorption goes as the square of the light intensity. In the paper: Eq. 3 (circular pupils) and Eq. 6 (annular).
:::

**Step 1, the field.** U₁ and U₂ are the complex field amplitudes of the two focused beams at a point P (from Eq. 1: an
amplitude and a phase). In 2PE both beams come from the same 700-nm laser, so they interfere: the fields add first,

$$U = U_1 + U_2 .$$

**Step 2, the light intensity** (the "excitation PSF", what the paper's Figs. 6a and 7a plot):

$$I = |U_1 + U_2|^2 = I_1 + I_2 + 2\sqrt{I_1 I_2}\,\cos\varphi, \qquad I_i = |U_i|^2,$$

with φ the phase difference between the two beams at P. The cos φ term is the interference: along the axis at θ = π,
φ = 2kz, so I has fringes λ/2n apart (0.35 µm in air).

**Step 3, two photons.** A 2PE molecule must absorb two photons at the same moment, so its rate goes as the square of
the photon density, i.e. the square of I:

$$F_{2p} = \kappa' I^2 = \kappa' |U_1 + U_2|^4 ,$$

κ′ = the 2PE fluorescence cross-section of the dye (a constant; we normalize to the peak).

**What the fourth power contains** (squaring Step 2):

$$|U_1 + U_2|^4 = \underbrace{I_1^2 + I_2^2}_{\text{one beam alone}} + \underbrace{2 I_1 I_2 + 4 I_1 I_2 \cos^2\varphi}_{\text{one photon from each beam}} + \underbrace{4 (I_1 + I_2)\sqrt{I_1 I_2}\,\cos\varphi}_{\text{interference with each beam}}$$

| Term | Meaning |
|---|---|
| I₁², I₂² | each beam excites 2PE on its own (both photons from one beam) |
| 2 I₁I₂ + 4 I₁I₂ cos² φ | one photon from each beam; strongest where the fringes are bright |
| 4 (I₁ + I₂)√(I₁I₂) cos φ | the cross term between interference and each beam |

**Against 2CE (Eq. 2).** The two 2CE beams have different colours (750 and 656 nm), so their interference averages out,
and the transition needs one photon of each colour. So only the product of the two intensities is left:

$$F_{2c} = \kappa\, |U_1|^2 |U_2|^2 = \kappa\, I_1 I_2 .$$

No single-beam term and no fringes: 2CE is made only where both beams are present (and, with pulses, where both pulses
meet; Q11).

**Why it matters:**

- 2PE has fringes and side lobes (from cos φ) and an out-of-focus background (from I₁², I₂²); 2CE has neither.
- Squared or fourth power: |U₁ + U₂|² is the light, |U₁ + U₂|⁴ the 2PE signal. The paper's Eq. 3/6 is right; its
  Figs. 6a and 7a plot the light (Q5).

:::

::: card
::: sl
Q6
:::

## What is the wavelength difference? Is only the second wavelength changed?

::: say
Both change. Δλ = λ₁ − λ₂, with 1/λ₁ + 1/λ₂ = 1/350 nm fixed (the same transition as two 700-nm photons).
:::

| Δλ | λ₁ (lens L1) | λ₂ (lens L2) |
|---|---|---|
| 0 nm | 700 | 700 |
| 10 nm | 705 | 695 |
| 39 nm | 720 | 681 |
| 94 nm | 750 | 656 |

λ₁ goes up and λ₂ goes down. Across the axis the 2CE spot follows λ₁ (+6%); along the axis the focus follows λ₂ (−5.5%).
:::

::: card
::: sl
Q7
:::

## How does the wavelength difference affect 2PE?

::: say
It does not. 2PE uses one 700-nm laser for both beams; Δλ only chooses the two colours of 2CE.
:::

- 2PE at 700 nm is the reference: it is what 2CE becomes at Δλ = 0 (700 + 700 nm), apart from interference.
- In the **Wavelength gap Δλ** tab the 2PE curve is flat; only 2CE moves.
:::

::: card
::: sl
Q8
:::

## Simpson's rule against RK4: what is the advantage?

::: say
For our integrals they are the same method: RK4 applied to y′ = f(t) is Simpson's rule.
:::

- One RK4 step of y′ = f(t): y(t + h) = y(t) + (h/6)[f(t) + 4 f(t + h/2) + f(t + h)], which is Simpson on [t, t + h], error O(h⁴).
- **No differential equation:** each field is a definite integral, U ∝ ∫₀¹ J₀(vρ) e^{−iuρ²/2} ρ dρ; "RK4" suggests an ODE we do not solve.
- **One grid for every point** (whole maps at once); RK4 would also evaluate the midpoint twice.
- **Adaptive (RK45):** helps for sharp integrands; ours is smooth over a finite pupil. We refined the fixed grid until
  the widths stopped changing; browser (161 nodes) and mcdo (301) agree to 4–5 digits.
- **Faster option:** Gauss–Legendre needs fewer nodes for the same accuracy; it would not change any result.
- One line for the adviser: "RK4 applied to a plain integral is Simpson's rule; we integrate, we don't solve an ODE, and
  we refined the grid until the widths stopped changing."
:::

::: card
::: sl
Q8b
:::

## Did we look at the distance between peaks as a function of wavelength?

::: say
Yes, through the units: slide 47 gives the side-lobe distance in units of λ/n, and at a fixed NA every distance in
the focus scales with λ, so the same curves hold for any wavelength.
:::

- Check (paraxial, NA 0.5, 2PE): first side lobe at **0.533 λ** with facing lenses (θ = π) and **0.932 λ** with crossed
  lenses (θ = π/2), for λ = 0.6, 0.7 and 0.8 µm alike; heights 0.97 and 0.12, also unchanged.
- In µm: at λ = 0.7 µm, 0.37 µm (facing) and 0.65 µm (crossed); at λ = 0.8 µm, 0.43 and 0.75 µm.
- What changes the distance in λ/n is the NA (slide 47): facing 0.5 → 0.63 λ/n at NA 0.9 in air; crossed 1 → 0.83 λ/n at NA 0.7.
- 2CE has no side lobes to measure (below 10⁻³ of the peak), and its two wavelengths are set by Δλ (Q6).

:::

::: {.part}
# High NA
:::

::: card
::: sl
Q9
:::

## What does "Scalar over vector − 1 (%)" mean?

$$\Delta = \left(\frac{w_\text{scalar}}{w_\text{vector}} - 1\right) \times 100\%$$

- w = width (FWHM across, DOF along) from each model. 0% = the models agree; +5% = the scalar width is 5% larger.
- Example: 2CE along the axis, NA 0.9, air: 1.099 / 0.807 − 1 = **+36%**: the paraxial focus is 36% too long.
- The grey band on the chart is ±5%.
:::

::: card
::: sl
Q10
:::

## Fidelity F, C, Q: definitions, and the message they give

Both profiles scaled to the same energy (Σ a Δs = Σ r Δs = 1); a = scalar, r = vector:

$$\mathrm{NRMSE} = \sqrt{\frac{\sum (a - r)^2}{\sum r^2}}, \quad F = 1 - \frac{\sum (a - r)^2}{\sum r^2}, \quad C = \frac{\sum a^2}{\sum r^2}, \quad Q = \frac{\sum a\,r}{\sum r^2}$$

F = 2Q − C and NRMSE = √(1 − F). Identical profiles: F = C = Q = 1.

| Case | F | C, Q |
|---|---|---|
| Across the axis (all) | ≥ 0.996 at all NA | C ≥ 0.92 |
| Crossed lenses, θ = π/2 | ≥ 0.997 where the lenses fit | C ≥ 0.9 |
| Along the axis, facing lenses | < 0.99 from NA 0.63 in air (0.84 water); 0.58 for 2PE at θ = π | C < 0.95 from NA 0.44 in air (0.58 water); Q < 0.95 from NA 0.59 |

**Message:** C is the most sensitive and drops below 0.95 where the depth of focus departs by 5%; F reacts later. All
three agree with the widths: the paraxial model fails only along the axis with facing lenses. (Slides 37, 40–46.)
:::

::: {.part}
# Optical pulses
:::

::: card
::: sl
Q11
:::

## How does a pulse act on 2PE, and how is it different from 2CE? Why does 2PE barely change?

∫|E₁ + E₂|⁴ dt = ∫(I₁² + I₂²) dt + ∫[4(I₁ + I₂)√(I₁I₂) cos φ + 4 I₁I₂ cos² φ] dt

| Term | What it is | Needs the pulses to meet? |
|---|---|---|
| I₁², I₂² | both photons from one beam | **no** |
| 4 I₁I₂, and the terms in cos φ | one photon from each beam; the fringes (period λ/2n) | yes |

- **2CE** is I₁I₂ only: fully gated by the pulse overlap (2.1 µm long at 10 fs in air, θ = π).
- **2PE depth of focus** at θ = π is one fringe (0.14–0.17 µm), set by λ, far shorter than the overlap: it changes by
  **0.5%**. Only the outer fringes fade where the pulses do not meet. (Slide 60.)
:::

::: card
::: sl
Q11b
:::

## Is 2PE unaffected by pulses because it has one pair, while 2CE has many?

::: say
Mostly unaffected, yes, but not because of the number of pairs. Both have many pairs. What matters is whether a pair
needs photons from both beams.
:::

- **Both have many pairs.** A 10-fs pulse spans about 40 nm. Any two photons whose frequencies add up to the transition
  (ν_a + ν_b = c / 350 nm) can excite: for 2PE, e.g. 690 + 710 nm or 700 + 700 nm, all from the same 700-nm spectrum.
- **2CE: every pair takes one photon from each beam.** Two 750-nm photons (or two 656-nm photons) do not reach the
  transition. So every pair needs both pulses at the molecule at the same time: 2CE is gated by the overlap of the
  pulses (2.1 µm at θ = π, 10 fs, air).
- **2PE: a pair can come from one beam.** Both photons from the same pulse arrive together automatically (a pulse
  always overlaps itself). These are the I₁² and I₂² terms of |U₁ + U₂|⁴ (Q5b): they need no overlap and are not gated.
- **But not all of 2PE is ungated.** The pairs with one photon from each beam (2I₁I₂, and the interference terms with
  cos φ) need the two pulses to meet. So away from the focus the fringes fade, and only the smooth single-beam part stays.
- **The 2PE focus at θ = π is one fringe** (0.14–0.17 µm), set by λ and well inside the 2.1-µm overlap, so its width
  changes by 0.5%. **2CE's focus** (3.3 µm at NA 0.5) is longer than the overlap, so the pulses cut it to 1.9 µm.

| | 2CE | 2PE |
|---|---|---|
| Pairs | many; each one photon from each beam | many; from one beam or from both |
| Needs the pulses to meet? | always | only the two-beam part (fringes) |
| Effect of 10-fs pulses, θ = π, NA 0.5 | focus 3.3 → 1.9 µm | focus unchanged (0.5%); outer fringes fade |

:::

::: {.part}
# Monte Carlo (Fig. 8)
:::

::: card
::: sl
Q12
:::

## Why is our Monte Carlo so clean, and why is the paper's noisy?

::: say
Our noise is there but smooth along z; the paper's counting rule, which it does not state, is noisier.
:::

- **Ours (Blanca & Saloma as written):** photons crossing each plane inside w(z). The run-to-run spread matches counting
  statistics: 5.3% at the focus (about 390 photons), 0.6% at z = 19 µm. A photon crosses many 0.25-µm planes between
  scatterings (free path about 12 µm), so neighbouring points are 97% correlated: a slow drift, not jitter.
- **Three counting rules, 5 runs of 10⁶ photons:**

| Rule | SD at the focus | SD at z = −17 µm | neighbours correlated |
|---|---|---|---|
| Crossings inside w(z) (ours) | 2.5% | 0.3% | 0.95 |
| Crossings inside a fixed radius w₀ | 2.5% | **5.5%** | 0.84 |
| Only at scattering events | **30%** | 2.5% | **−0.04** |

- The paper's noise (5–10% point to point, larger away from the focus) fits a fixed small counting area or counting at
  scattering events. Its text gives only "10⁷ photons for each excitation beam" (p. 33).
:::

::: {.part}
# Dashboard and reports
:::

::: card
::: sl
Q13
:::

## Where is the reset button? Which tab shows what?

- **Reset parameters:** top of the side panel, on every tab (keeps the tab). Each map has "Cuts back to the focus" once the cuts are moved.
- **Panels:** hover a panel, ⤢ makes it full width, ⠿ drags it to another place; drag a chart's bottom-right corner to make it taller.
- **Tabs:** Focal spot (2D maps, setup) · Lens angle θ · Wavelength gap Δλ · Annular pupil ε · Scalar vs vector at high NA
  (widths, comparisons, NRMSE, F, C, Q, side lobes, 2D maps) · Femtosecond pulses (against τ, with continuous dashed) ·
  Scattering (Fig. 8). Every replication tab has NA, Model and Beams (continuous or pulses).
- The presenter guide names the tab and clicks for every slide.
:::

::: card
::: sl
Q14
:::

## What were the bug reports?

Two drafts, queued locally; send with `/feedback` after review (nothing is sent without your approval):

1. Installed an npm package (KaTeX) without asking first.
2. Shipped figure insets that did not say what they show, over several corrections.
:::
