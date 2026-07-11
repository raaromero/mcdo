# Progress talk — pre-Monte-Carlo research (Phases 1–5)

*Slide-by-slide plan for the next-semester progress presentation. Doubles as
the paper's narrative skeleton (same arc as `paper/draft/main.tex`). Every
figure is an existing file — paths relative to repo root. ~35–40 min + Q&A;
sections C–D are the core if time is cut. Backup slides at the end for the
predictable committee questions.*

Build note: assemble as beamer/tectonic later; each slide below = title,
content, EXACT figure(s), and a one-line talk track.

---

## Section A — Motivation & background science (the "textbook" slides)

**A1. Title.** "Few-cycle pulses through structured pupils at high NA — a
validated toolkit and first results." Name, adviser, date. *(no figure)*

**A2. The physical setting.** Cartoon: objective → focal region → (later)
scattering medium. Bullets: why tight focusing matters (two-photon microscopy,
micromachining); why few-cycle pulses (bandwidth ~ carrier); why structured
pupils (depth-of-focus engineering).
Figure: `output/00_overview/models_schematic.png` (top pipeline band only —
crop). *Talk track: "one pipeline, every model in this talk lives in it."*

**A3. Background I — a focus is interference (1835–1909).** Airy pattern;
Lommel's 3-D focal region and the optical coordinates u = kz sin²α,
v = kr sinα; Debye's pivot: the focus as a cone of plane waves.
Figure: `output/02_na_apodization/check1_lowNA_convergence.png` (our engine
reproducing Airy — background *and* validation in one).
*Track: "everything downstream is bookkeeping of plane waves filling a cone."*

**A4. Background II — the vector focus (Richards–Wolf 1959).** The I₀,I₁,I₂
integrals (one displayed equation); the (1±cosθ) kernels; the longitudinal E_z;
polarization-dependent cuts |I₀−I₂|² vs |I₀+I₂|²+4|I₁|².
Figure: `output/02_na_apodization/check2_highNA_vector.png`.
*Track: "at NA 0.8 light is a vector; E_z is not a correction, it's a lobe."*

**A5. Background III — few-cycle pulses (Eq. 10).** Gaussian spectrum,
a = 2ln2/τ², time–bandwidth product; detectors are slow ⇒ frequencies add
incoherently: I = ∫|E(ω)|² I_cw(ω) dω; each ω sees the same cone at its own
scale v ∝ ω.
Figure: `output/05_pulsed_pupils/spectral_sampling.png` (panels A/B: the
spectrum and the λ-Jacobian).
*Track: "the pulse doesn't move the focus — it superimposes rescaled copies."*

**A6. Background IV — scoring a focal pattern (Linfoot).** F, S, Q definitions
(one line each), 2Q−S=F; reference = cw, test = pulsed.
Figure: `output/01_romallosa/fig4_linfoot.png`.
*Track: "image-quality metrics pointed at the focus itself — Romallosa's move."*

**A7. The anchor paper + the gap.** Romallosa/Bantang/Saloma PRA 68, 033812
(2003): few-cycle × vector focus, unstructured pupil. The two literatures that
never met: pulsed-focus (unstructured) and structured-pupil DOF (monochromatic).
Gap = their combination at high NA. *(table slide, no figure — or reuse
models_schematic phase cards).*

## Section B — Methods & the validation philosophy

**B1. The toolkit.** RW integrals + apodization A(θ) + field-level Babinet
annulus + axicon phase + Eq.-10 spectral sum; 40-test regression suite; every
result ≥10-trial error bars where stochastic.
Figure: `output/00_overview/models_schematic.png` (full).

**B2. Validation ladder (why you should believe the rest of the talk).**
Analytic limits → conservation laws → published anchors → first-principles
Maxwell residuals *with deliberately broken controls*.
Figure: `output/00_overview/audit_first_principles.png`.
*Track: "the fields satisfy Helmholtz and ∇·E=0 at the finite-difference floor;
break one kernel factor and the check fails 700× louder — the checks have
teeth."*

## Section C — Results, phase by phase

**C1. Phase 1 — the Romallosa replication (the license to proceed).** All five
paper figures reproduced; S_ax 1.058 vs 1.057; FWHM 472.8 nm; zeros 0.555/3.05 µm.
Figures: `output/01_romallosa/fig1_contours.png` + `fig2_profiles.png`
(side-by-side).

**C2. Phase 1 discovery — the spectral window.** FWHM-band integration loses
24% of the weight and fails every anchor; the paper integrates ω∈(0,2ω_c).
Figure: `output/01_romallosa/fig3_energy.png`.
*Track: "a reproducibility finding worth an appendix (or a Comment)."*

**C3. Phase 2 — a single 'NA threshold' is ill-posed.** The thresholds table
(1%/5% by polarization × cut × direction); the anisotropy IS E_z.
Figures: `output/02_na_apodization/check3_fwhm_thresholds.png` +
`check6_anisotropy.png`.

**C4. Phase 2 — apodization *extends* scalar validity.** Gaussian underfilling
de-weights marginal rays (corrects the earlier report).
Figure: `output/02_na_apodization/verify_apod_thresholds.png`.

**C5. Phase 3 — annular apertures: the DOF law and its high-NA limits.**
DOF = 1/(1−ε²) to 3 digits paraxially, ~40% short at sinα=0.9; Strehl (1−ε²)².
Figures: `output/03_annular/verify_annular.png` + `annular_energy_cost.png`.
Optional: atlas cards `output/atlas/annular/eps0.9.png` for visual intuition.

**C6. Phase 3 — the vector Bessel core.** Thin annulus → J₀² (dev 0.004 low
NA) but vector-deformed at high NA (0.163) — the clean isolated vector effect.
Figure: `output/03_annular/verify_sheppard.png` (+ Sheppard–Wilson anchor).

**C7. Phase 4 — the axicon and an honest flag resolved.** Focal segment with
position-dependent Bessel scale; the 4–8% J₀² gap is stationary-phase error —
proven by the β-scan (∝1/β, 0.134→0.006) with the physical Debye ceiling.
Figures: `output/04_axicon/verify_axicon.png` + `axicon_validity.png`.
*Track: "we chased our own discrepancy to ground — it was the analytic model,
not the field."*

**C8. Phase 5 — THE HEADLINE.** Pulsed × annular: DOF(ε)/DOF(0) invariant
cw→1 fs (44.35→44.33 at ε=0.99) while the transverse rings erode.
Figure: `output/05_pulsed_pupils/verify_pulsed_annular.png`.

**C9. Headline robustness.** Spread ≤0.10% across ε=0.5–0.99 × NA=0.6/0.8/1.0.
Figure: `output/05_pulsed_pupils/paper_robustness.png`.
*Track: "invariance is geometric — every color sees the same cone, so the
*ratio* is achromatic."*

**C10. The non-monotonic ring contrast — verified real.** S(τ) dips then
rises; smooth in τ, flat vs N_freq, present in all polarization cuts; the
core/ring decomposition explains it (rings wash out at 7% weight; 1-fs central
skirt overfills them).
Figures: `output/05_pulsed_pupils/pulsed_S_diagnostic.png` +
`ring_decomposition.png`.

## Section D — Synthesis & where this goes

**D1. What this adds up to.** One validated framework spanning vector ×
pulsed × structured pupils; the three candidate contributions ranked honestly
(headline / thresholds table / vector-Bessel demonstration).
*(summary table, no figure.)*

**D2. The paper.** Draft v0.1 exists (`paper/draft/main.pdf`): target
JOSA A / Opt. Express / PRA; what remains (citation verification, figure pass,
template). *(screenshot of the draft's page 1 as the figure.)*

**D3. The road ahead (one slide only — next semester's work).** These fields
become the *source* for Monte-Carlo transport through scattering media (engine
already validated through its own 6-rung ladder — one teaser panel:
`output/06_monte_carlo/verify_mc_scatter.png`). Applications: extended-DOF
deep two-photon.

**D4. Ask/discussion.** Feedback on: venue choice, the errata-handling
decision (appendix vs Comment), and the scattering-phase priorities.

## Backup slides (for the predictable questions)

- **BK1** "How converged are the integrals?" —
  `output/02_na_apodization/verify_na_convergence.png`.
- **BK2** "Paraxial comparisons?" —
  `output/02_na_apodization/verify_tanaka_paraxial.png`.
- **BK3** "Axial behavior vs NA?" — `check4_axial.png` + `check7_axial_vs_na.png`.
- **BK4** "Other polarizations?" — `check8_polarization.png`.
- **BK5** "The whole configuration space?" — atlas contact sheet
  (`output/atlas/*/*.png`, pick 6).
- **BK6** "Numerical trust?" — the ACCURACY.md ladder as a table +
  `audit_first_principles.png` revisited.
- **BK7** "Pulsed sampling choices?" — `spectral_sampling.png` panels C/D.

---
*Figure-availability check: every path above exists in `output/` as of
2026-07-08. When building the deck, re-render C8's headline figure at
publication quality first (it's also Paper-1 Fig. 6 — one effort, two uses).*
