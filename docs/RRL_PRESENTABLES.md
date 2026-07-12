# RRL presentables — papers you can present to the group

*Curated for journal-club / RRL presentations: ISI or comparably respected
venues, ranked by digestibility. Each entry lists its **main points** (what to
put on the slides) plus how it ties to the thesis. **Coverage note:** this list
is deliberately NOT Saloma-lineage-only — the Saloma-group papers (Romallosa,
Blanca) are just the anchors; the bulk here (Richards–Wolf, Durnin, Vellekoop–
Mosk, Denk, MCML, Farrell–Patterson, Novotny–Hecht, Gu, etc.) are independent
foundations of the field you should own regardless of lineage.*

*Status flags: [V] = citation verified · [L] = strong lead, confirm exact
page/year before presenting · (~verify) = from domain knowledge, verify first.*

---

## Tier 1 — easiest wins (short, visual, story-driven)

### Vellekoop & Mosk, "Focusing coherent light through opaque strongly scattering media," Opt. Lett. 32, 2309 (2007) [V]
*Non-lineage.* — Opt. Lett., ~3 pp.
- **Main points**: (1) a spatial light modulator shapes the input wavefront so
  that light *focuses through* a strongly scattering layer (paint, ground glass);
  (2) the medium is treated as a deterministic (if complex) linear system, not
  random noise — you can invert it; (3) a single, unforgettable figure: a bright
  focus appears behind an opaque wall. Launched the entire wavefront-shaping /
  "imaging through turbidity" field.
- **Tie**: the conceptual flip our MC phase heads toward — scattering as a
  controllable channel; the downstream frontier (pulsed structured inputs).

### Durnin, Miceli & Eberly, "Diffraction-free beams," PRL 58, 1499 (1987) + Durnin, JOSA A 4, 651 (1987) [V]
*Non-lineage.* — PRL / JOSA A.
- **Main points**: (1) an ideal J₀ Bessel beam propagates without spreading —
  "diffraction-free"; (2) it is produced by an annulus in the back focal plane
  (a ring of plane waves on a cone — same Debye picture as our engine); (3) the
  famous caveat: a true Bessel beam carries infinite power, so real beams are
  finite-aperture approximations with a long but bounded non-diffracting range.
- **Tie**: the physical origin of our Phase 3–4 annular/axicon results; the
  DOF ∝ 1/(1−ε²) law is the finite-aperture version of this.

### Denk, Strickler & Webb, "Two-photon laser scanning fluorescence microscopy," Science 248, 73 (1990) [V]
*Non-lineage.* — Science, ~3 pp.
- **Main points**: (1) two-photon absorption confines excitation to the focal
  volume (signal ∝ intensity²), giving intrinsic optical sectioning without a
  pinhole; (2) it requires femtosecond pulses at high peak power — this is *why*
  ultrafast focal fields matter; (3) longer (red/IR) wavelengths penetrate
  tissue deeper with less scatter.
- **Tie**: the application motivating the whole lineage — few-cycle focal
  volumes in scattering tissue; the "why bother" slide for the thesis.

### Betzig-lab Bessel-beam plane-illumination / two-photon volumetric imaging (Planchon et al., Nat. Methods 8, 417 (2011); Gao et al. 2012–2014) [L — pin exact figure]
*Non-lineage.* — Nat. Methods.
- **Main points**: (1) a scanned Bessel beam gives an ultra-thin, extended
  light sheet → fast 3-D imaging of live cells; (2) the extended DOF of the
  Bessel/annular beam is the enabling feature; (3) gorgeous volumetric data.
- **Tie**: the real-lab payoff of extended-DOF structured beams; our headline
  (bandwidth-invariant DOF) de-risks doing this with few-cycle sources.

---

## Tier 2 — moderate effort, high relevance (the core set)

### Romallosa, Bantang & Saloma, "Three-dimensional light distribution near the focus of a tightly focused beam of few-cycle optical pulses," PRA 68, 033812 (2003) [V]
*Saloma lineage — THE anchor.*
- **Main points**: (1) computes the vector focal field of few-cycle pulses via
  Richards–Wolf + an incoherent spectral sum (their Eq. 10); (2) shows how the
  focal distribution and axial Strehl change as the pulse shortens toward
  single-cycle; (3) unstructured (full) pupil only.
- **Tie**: Phase 1 — you reproduced every figure (S_ax 1.058 vs 1.057, FWHM
  472.8 nm). Present it better than anyone alive; end on your reproduction.

### Blanca & Saloma, "Monte Carlo analysis of two-photon fluorescence imaging through a scattering medium," Appl. Opt. 37(34), 8092–8102 (1998) [V]
*Saloma lineage.*
- **Main points**: (1) Monte-Carlo transport of a focused Gaussian excitation
  beam through tissue; (2) tracks axial/transverse excitation distributions vs
  NA and vs scattering-depth/mean-free-path, for isotropic AND anisotropic
  scatterers; (3) quantifies how scattering degrades the two-photon focus.
- **Tie**: the *forward* problem our MC phase extends (structured + pulsed) and
  that idea 01 (descattering) inverts. Group lineage.

### Hayakawa, Potma & Venugopalan, "Electric-field Monte Carlo simulations of focal field distributions produced by tightly focused laser beams in tissues," Biomed. Opt. Express 2, 278 (2011) [V]
*Non-lineage — the key modern prior art.*
- **Main points**: (1) propagates the *electric field* (amplitude + phase), not
  just photon weights, through a scattering medium — coherent MC; (2) tightly
  focused beams over NA 0.81–1.31; (3) shows how the focal field degrades with
  depth.
- **Tie**: the closest thing to our Phase 6 — present honestly as "prior art we
  extend with structured pupils + few-cycle spectra as the source." Positioning.

### Wang, Jacques & Zheng, "MCML — Monte Carlo modeling of light transport in multi-layered tissues," Comput. Methods Programs Biomed. 47, 131 (1995) [V]
*Non-lineage — the methods classic.*
- **Main points**: (1) the canonical analog photon-transport algorithm: step
  sampling from µₜ, Henyey–Greenstein deflection, local-frame rotation, Russian
  roulette; (2) fully specified and reproducible — every transport MC descends
  from it; (3) validated against diffusion theory.
- **Tie**: the recipe behind our `scatter.py`; validation rungs 4–6.

### Farrell, Patterson & Wilson, "A diffusion theory model of spatially resolved, steady-state diffuse reflectance," Med. Phys. 19, 879 (1992) (~verify)
*Non-lineage.*
- **Main points**: (1) closed-form diffusion Green's function for a semi-infinite
  turbid medium; (2) links measurable diffuse reflectance to µ_a, µ_s′; (3) a
  clean theory-meets-experiment story.
- **Tie**: our rung-6 anchor (µ_eff = √(3µ_a µ_tr)); an MC-phase RRL.

### Chen, Wang, Yuan & Zhan, "Longitudinally polarized optical needle by annulus + phase," Opt. Lasers Eng. 59, 93 (2014) [L]
*Non-lineage.*
- **Main points**: (1) an annular pupil plus engineered phase makes a sub-
  wavelength, long "needle" of longitudinally polarized light; (2) the DOF is
  tens of wavelengths; (3) pure vector-diffraction design, no exotic materials.
- **Tie**: where annular engineering leads beyond our ε-scan; a Phase 3 sequel.

### "Moving-halo" polychromatic high-NA focus, JOSA A 37, 969 (2020) [V]
*Non-lineage — nearest neighbor of our Phase 5.*
- **Main points**: (1) treats broadband/polychromatic tight focusing directly;
  (2) shows wavelength-dependent structure ("moving halo") in the focal region;
  (3) modern, short.
- **Tie**: the closest modern work to our pulsed-focus physics — cite to
  position the headline (note: it does NOT report the DOF-ratio invariance).

---

## Tier 3 — foundations (present once, cite forever)

### Richards & Wolf, "Electromagnetic diffraction in optical systems. II. Structure of the image field in an aplanatic system," Proc. R. Soc. A 253, 358–379 (1959) [V]
*Non-lineage — THE vector-focus paper; the engine's core.*
- **Main points**: (1) derives the full vector E and H fields near the focus of
  a high-aperture aplanatic lens for linearly polarized input — the I₀, I₁, I₂
  integrals; (2) valid for ANY semi-aperture 0–90° (not paraxial), reducing to
  scalar theory in the low-NA limit; (3) maps energy density and Poynting flow
  in the focal region, revealing the longitudinal component and asymmetry.
- **Tie**: literally the mathematics your engine implements; Phase 2 reproduces
  its figures. Heavy, but you own it.

### Sheppard & Wilson, thin-annulus focal field / J₀ limit (late-1970s) [L — pin exact citation]
*Non-lineage.*
- **Main points**: (1) an infinitely thin annulus yields a J₀²-type focal core;
  (2) geometric, short derivation; (3) the bridge from Durnin's ideal Bessel
  beam to real high-NA vector focusing.
- **Tie**: Phase 3's analytic anchor (our thin-ring dev 0.004 at low NA, vector-
  deformed 0.163 at high NA). Pairs naturally with Durnin.

### Novotny & Hecht, *Principles of Nano-Optics* (CUP), ch. 3–4 [book]
*Non-lineage — the recommended on-ramp.*
- **Main points**: (1) the cleanest modern derivation of angular-spectrum
  representation and high-NA focusing; (2) self-contained vector diffraction;
  (3) worked examples close to our engine's conventions.
- **Tie**: the single best background text (see LITERATURE.md §0). Good for a
  "foundations" RRL slot rather than a paper.

### Gu, *Advanced Optical Imaging Theory* (Springer) [book] — optional alternative
*Non-lineage.*
- **Main points**: (1) systematic 3-D vectorial PSF / focal-field theory; (2)
  strong on apodization and pupil engineering; (3) complementary conventions.
- **Tie**: a second reference for Phases 2–3; cite if Novotny–Hecht is scarce.

---

## How to run these as RRL sessions (practical)
1. **Lead with the anchor you can demo**: any Tier-2 paper tied to a phase can
   end with one slide of OUR reproduction ("here is their Fig. X, from our
   engine") — memorable, and it advertises the toolkit.
2. **One paper per session**, 15–20 min: problem → one key equation → one key
   figure → what it enabled → how it touches the thesis.
3. **Semester order (8 sessions)** — the thesis narrative in literature form:
   Denk (why) → Richards–Wolf (the tool) → Durnin (structured beams) →
   Romallosa (pulsed foci) → Blanca (scattering) → MCML (transport method) →
   Hayakawa (coherent MC) → Vellekoop–Mosk (control). Non-lineage papers carry
   5 of the 8 slots — by design.
4. Verify every (~verify)/[L] citation before its session.

## The main advancement of the field, relative to this thesis

**Pre-MC (Phases 1–5).** Two literatures matured *separately*: (i) vector
high-NA focusing theory (Richards–Wolf 1959 → Novotny–Hecht) including pulsed
foci (Romallosa 2003; polychromatic-focus numerics 2006–2020), and (ii)
structured-pupil DOF engineering (Durnin 1987 → annular DOF ∝ 1/(1−ε²) →
"needle" beams 2008–2014 → Bessel two-photon imaging 2011–2017). Their open
meeting-edge: **what broadband/few-cycle light does to engineered foci** —
treated only piecemeal. Our step: the first systematic vector-exact map of
pulsed × structured pupils at high NA, headlined by the DOF-ratio invariance
(≤0.10% cw→1 fs).

**MC phase (6+).** Transport MC is mature (MCML 1995) but *radiometric* — it
propagates weights, not fields. The advancement toward coherent-beam MC is
Hayakawa–Potma–Venugopalan (BOE 2011). Our step beyond: structured pupils +
few-cycle spectra as the SOURCE, ballistic field kept coherently (amplitude
attenuation, not photon killing), validated rung-by-rung. Frontier we can then
touch: wavefront-shaping through turbidity (Vellekoop–Mosk 2007 →) with pulsed
structured inputs — essentially untouched.
