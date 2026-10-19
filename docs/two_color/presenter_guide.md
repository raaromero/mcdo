---
title: "Presenter guide: two-color excitation with two confocal beams"
subtitle: "Cambaliza & Saloma, Opt. Commun. 184 (2000) 25–35, with current work"
geometry: margin=2cm
fontsize: 10.5pt
---

# 1. The question (pp. 25–27)

- Two lenses focus two beams to one point; the angle between the lens axes is θ (0 collinear, π/2 crossed, π facing).
- **2CE** (two-color excitation): one photon from each beam, 750 nm and 656 nm, absorbed together. The signal is the
  product I₁I₂. The colors differ, so the beams do not interfere.
- **2PE** (two-photon excitation): both beams at 700 nm. The signal is |U₁ + U₂|⁴. The beams interfere.
- The authors ask where 2CE is better than 2PE: resolution, depth discrimination, or imaging through scattering media.

# 2. Their model (Section 2)

- Paraxial scalar focus of each lens (Eq. 1, Lommel functions), NA 0.5. Beam 2 is the same focus turned by θ.
- 2CE: Eq. 2 (circular) and Eq. 5 (annular). 2PE: Eq. 3 and Eq. 6. Annular pupil = difference of two circular
  pupils (Eq. 4), ε = 0.99.
- **Current work:** computed Eqs. 1–6 as written.
  - Eq. 1 writes the rotation of beam 2 in the optical coordinates (u, v). Because u scales as NA²z and v as NA·x, a rotation
    in (u, v) is not a rotation of the lens.
  - The published curves follow the rotation in real space (x, z): along the axis at θ = π/2 the published width is
    0.67 µm, which (x, z) gives; (u, v) gives 1.31 µm. Current work rotates in (x, z).

> *Transition:* With the model in hand, the authors start from the simplest pupil, a full circular lens, and compare the two signals at the three angles.

# 3. Circular pupils, Figs. 2–3 (Section 3.1)

- **What they did:** plotted 2PE and 2CE across (Fig. 2) and along (Fig. 3) the axis at θ = 0, π/2, π.
- **What they found:**
  - 2PE at θ = π/2 has the sharpest central spot but stronger side lobes, from the interference of the two beams.
  - 2CE has no interference side lobes. At θ = 0 and π its profiles equal the 2PE profile at θ = 0.
  - 2PE at θ = π along the axis is modulated by fringes; its envelope is the 2CE profile at θ = 0.
  - Conclusion: with circular pupils 2CE gives **no definite advantage in resolution** (pp. 29–30).
- **Current work:** identical curves.
- **Not consistent with their own figures** (current work and the published curves give the same values):
  - p. 28, "0.67 times" (2PE spot at π/2 over θ = 0): 0.49 (0.256 / 0.517 µm).
  - p. 29, "1.58 times wider" (2CE over 2PE spot at π/2): 2.98 (0.763 / 0.256 µm).
  - Other width measures (1/e², zero to zero) do not reach the stated values either.

> *Transition:* With circular pupils the 2CE spot at θ = π/2 is wider than the 2PE one. 2CE has a free parameter 2PE does not: the two wavelengths can be chosen apart as long as they still reach the same transition. The authors ask how far apart they can be, and what that does to the spot.

# 4. The gap between the two wavelengths, Figs. 4–5 (Section 3.1)

- **What they changed:** the gap Δλ = λ₁ − λ₂ (10, 39, 94 nm), keeping 1/λ₁ + 1/λ₂ = 1/350 nm, so the same
  transition is excited. θ = π/2.
- **What they found:** a wider gap widens the spot by less than 6% and shortens the depth of focus: a trade-off.
- **Why (current work):** at θ = π/2 the spot across the axis follows beam 1, which scales with λ₁ (+6.4% from 705
  to 750 nm; FWHM +6.1%); along the axis it follows beam 2, which scales with λ₂ (−5.6%; depth of focus −5.5%).
- **Fig. 5:**
  - Current work lies within 0.004 µm of the published points.
  - FWHM slope: 5.24 ×10⁻⁴ µm/nm (current) against 4.86 ×10⁻⁴ (fit to the published points, digitized).
  - The published points scatter by 0.0016 µm rms, so their slope is uncertain by about ±0.2 ×10⁻⁴: about half the
    gap. The rest is not identified. The scaling above predicts about ±5 ×10⁻⁴.
  - The caption fits do not describe the plot: the FWHM fit (2.4 ×10⁻⁴ Δλ + 0.0356) lies off the plot; the DOF fit
    (+4.81 ×10⁻⁴ Δλ + 0.7112) rises and runs through the FWHM points, while the plotted DOF falls.

> *Transition:* Changing the wavelengths moves the widths by only about 6%, so it does not change the conclusion that circular pupils give 2CE no clear advantage. The authors next change the pupil itself: a thin ring stretches each focus along its own axis, which matters most at θ = π/2, where each beam crosses the other's long focus.

# 5. Annular pupils, Figs. 6–7 (Section 3.2)

- **What they changed:** each lens has a thin ring pupil (ε = 0.99, same outer diameter). A thin ring gives a very
  long focus along the axis.
- **What they found:**
  - θ = 0 and π: the 2CE profile is flat along the axis (no optical sectioning); 2PE at π has uniform fringes.
  - θ = π/2: 2CE has zeros and weaker side lobes; its central spot is about 1 µm; a **better axial response** than
    2PE. 2PE has a narrower spot (35%) but no zeros (minimum 0.08).
  - Conclusion: for thick samples, where depth discrimination matters, 2CE is the better option with annular
    pupils; for thin samples 2PE is.
- **Current work:** the 2CE curves are identical.
- **Difference:** the published annular 2PE curves (Figs. 6a, 7a) are the excitation |U₁ + U₂|², not Eq. 6
  (|U₁ + U₂|⁴).
  - Fig. 6a minimum 0.08: |U₁ + U₂|² gives 0.086; Eq. 6 gives 0.007.
  - Fig. 7a background 0.25: |U₁ + U₂|² gives 0.25; Eq. 6 gives 0.06.
  - Fig. 7a side peaks fall where |U₁ + U₂|² puts them (within 0.02 µm).
  - The circular 2PE panels (Figs. 2a, 3a) follow Eq. 6.
- "20% longer" (p. 32, annular 2CE over circular 2PE depth of focus at π/2): the curves give 85% (0.473 / 0.256 µm).

> *Transition:* Annular pupils give 2CE a better axial response, but 2PE keeps the narrower spot, so resolution alone does not decide. The authors then turn to where they expect 2CE to help: imaging through a scattering medium, where 2PE gains out-of-focus background.

# 6. Scattering media, Fig. 8 (Section 3.3, Monte Carlo)

- **What they did:** facing beams (θ = π) through a scattering slab (g = 0.9, h/d_s = 8), photon Monte Carlo
  (Blanca & Saloma 1998), 10⁷ photons per beam.
- **What they found:** scattering raises the out-of-focus 2PE background; the 2CE background stays near 0, because
  2CE needs both beams at the same point.
- **Main conclusion of the paper (Sections 4–5):** the advantage of 2CE is in imaging through scattering media, not
  in resolution. Annular lenses (axicons) can ease the alignment of the two beams.
- **Current work (preview, next step):** the slab half-thickness h is not given. With h = 100 µm the 2PE background
  is 0.09 (published 0.1–0.2) and the 2CE background 0.07 (published near 0); no h gives both.
  - Our curves are smoother: 10 runs averaged, and each photon counted at every plane it crosses inside w(z).

> *Transition:* Everything above is at NA 0.5 with the paraxial scalar model, which the paper says holds below NA 0.7 (p. 27). Current work first asks how far that model can be trusted, by comparing it with the vector focus up to the highest NA.

# 7. Extension to high NA (current work)

- **What we changed:** the paraxial scalar focus against the vector (Richards–Wolf) focus, NA up to 0.95 in air and
  1.25 in water.
- **Results:**
  - Along the axis the paraxial depth of focus is too long: 5% at NA 0.43 (air) and 0.57 (water); 36% (air) and
    15% (water) at NA 0.9.
  - Why: the paraxial phase replaces 1 − cos α by sin²α/2; the depth of focus is then too long by tan²(α/2). In
    water the cone is narrower at the same NA, so the error is smaller.
  - Across the axis the two agree within 5% up to NA 0.86 (air) and 1.14 (water).
  - At θ = π/2 they agree within 4% up to the NA at which crossed lenses fit (0.71 air, 0.94 water): each beam is
    cut by the other beam's narrow spot, which the paraxial model gets right.
  - The 2CE–2PE comparisons of the paper hold at high NA; their size changes because the 2PE fringe keeps its
    width while the 2CE spot shrinks.
  - θ = 0 and π give the same widths, except 2PE along the axis (fringes at π).

> *Transition:* 2CE needs both photons at the same place at the same time (p. 26), but the paper treats the beams as continuous, so only the place enters. With femtosecond pulses the time enters too: a pulse lasts τ, and the two pulses must meet. This extension adds that.

# 8. Extension to optical pulses (current work)

- **What a pulse adds:** a duration τ, a spread of frequencies Δν = 0.441/τ, and an arrival time at each point.
- **Photon pairs:** 2CE needs one photon from each laser with ν_a + ν_b = ν_e (the 350 nm transition). Each pair is
  weighted by its joint probability p₁(ν_a)p₂(ν_e − ν_a); the pairs add in amplitude with the phase of their arrival
  times.
- **Result of the sum:** the continuous PSF times the overlap of the two pulses in time. At zero delay this equals
  the time-overlap calculation.
- **Results (transform-limited, zero delay):**
  - θ = π: facing pulses meet only within $\sqrt{2}c\tau/2n$ of the focus (2.1 µm in air at 10 fs), so the 2CE depth of
    focus shortens: 3.3 to 1.9 µm at NA 0.5 in air, 4.6 to 1.6 µm in water.
  - θ = 0 and π/2: changes of 2% or less (co-propagating pulses travel together; at π/2 the focus is short).
  - High NA: the focus is already shorter than the overlap; 4% change at NA 0.9 (air) and 1.2 (water).
  - This is not a larger tolerance: the pulse has less to cut. A time delay moves the meeting point by cΔt/2n
    and lowers the signal at the focus by exp(−2 ln2 (Δt/τ)²) at every NA (the time-delay study comes next).
  - 2PE at θ = π: the central fringe is unchanged; the outer fringes drop where the pulses no longer overlap.

> *Transition:* The replication and both extensions use beams without scattering. The remaining figure of the paper, Fig. 8, needs the Monte Carlo of scattering; and the pulses so far meet at the focus with no delay.

# 9. Next steps

- Fig. 8: Monte Carlo with a choice of h; compare the 2PE and 2CE backgrounds.
- Optical pulses: a time delay between the pulses.

# 10. Questions to expect

- **Is your replication exact?** Yes for Figs. 2–4, 6b, 7b; Figs. 6a and 7a with |U₁ + U₂|²; Fig. 5 within
  0.004 µm.
- **Why not the stated numbers?** Three ratios in the text disagree with the authors' own curves; we measured on
  their curves.
- **Why rotate in (x, z)?** That is a turned lens; the published Fig. 3b follows it.
- **Are θ = 0 and π the same?** For 2CE yes; for 2PE across the axis yes; along the axis no (fringes at π).
