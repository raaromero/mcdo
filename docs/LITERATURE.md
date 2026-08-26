# Literature & reading roadmap — owning this research

*Compiled 2026-06-28, largely offline — treat exact volume/page/year as
**to-be-verified** against a database (Google Scholar, ADS, journal DOI)
before citing. Confidence is marked: ★★★ well-established / core, ★★ confident
on existence, ★ verify carefully. See also
[`theory/FIELD_HISTORY.md`](theory/FIELD_HISTORY.md) — the pre-2003 story of
how the field was built, move by move.*

This is a roadmap to *mastery* of the physics behind `mcdo` — high-NA vector
focusing, structured pupils, pulsed fields, and light transport through
scattering media — organized so you can read in dependency order.

---

## 0. How to read this (the fast path to fluency)

**If you want exactly ONE textbook, it is:**

> **Novotny & Hecht, *Principles of Nano-Optics* (2nd ed., Cambridge, 2012) —
> read chapters 1–4 in order.** Ch. 2 re-derives the needed electromagnetics
> from Maxwell (a self-contained EM refresher at exactly quals level); ch. 3–4
> derive the angular spectrum and the Richards–Wolf focal fields — i.e. the
> entire deterministic engine of this project, in the notation the code uses
> (their Eq. 3.66 is literally `sample_photons_vector`). One book, ~150 pages,
> covers Moves 0–5 of `theory/FIELD_HISTORY.md`. Everything else below is
> optional depth or lookup.
>
> *Note the two Hechts:* Novotny & **Bert** Hecht (above) is unrelated to
> **Eugene** Hecht's undergraduate *Optics* (skippable at this level). If you
> want one book that isn't a Hecht at all: **Min Gu, *Advanced Optical Imaging
> Theory* (Springer, 2000)** — ~200 pages, nearly a manual for this project
> (Debye focusing, apodization, vector RW, and a chapter on focusing ultrashort
> pulses), drier than N&H but the closest single text to the Romallosa toolkit.
>
> **"Between Hecht and Born & Wolf — B&W scope, Hecht readability":**
> **Lipson, Lipson & Lipson, *Optical Physics* (4th ed., CUP 2010)** — the
> canonical occupant of exactly that niche: full physical-optics scope
> (interference, diffraction, coherence, Abbe imaging) with physical insight
> and readable prose; ~550 pages one can read linearly. Runner-up for the
> diffraction→focusing chain specifically: Goodman (scalar only).

**If Born & Wolf feels daunting — correct instinct. It is the *reference*, not
the on-ramp.** Nobody masters this by reading B&W linearly; you consult it
(§8.8, §8.6) to settle fine points after you already have the picture. The
fuller on-ramp, in order of payoff per page:

1. **Novotny & Hecht ch. 3–4 first** (~60 pages). The best-matched text in
   existence for this project: modern notation, readable, derives exactly the
   Richards–Wolf machinery in `mcdo/` — their Eq. 3.66 is *literally* the code
   in `sample_photons_vector`. The highest-value 60 pages available to you.
2. **Goodman ch. 3 (angular spectrum)** alongside — makes "field = sum of plane
   waves = our photons" click; light math.
3. **The two 1959 papers** (Wolf I, Richards–Wolf II; ~25 pages total). After
   N&H they read easily. This is the one *paper* to know cold.
4. **Born & Wolf as targeted lookup only**: §8.8 (Debye focusing, ~15 pages)
   after step 3; §8.6 (Babinet) when an annular question arises. Never
   cover-to-cover.
5. **Learn through `mcdo` itself** (the secret weapon): every module docstring
   cites its source; `docs/theory/` maps each equation; the tests assert each
   limit. Loop: read a section → find it in the code → re-derive one kernel by
   hand → run its test. Active derivation, not passive reading.

**Calibration:** "master of the fundamentals" for THIS research = able to
re-derive five things unaided — (i) the angular spectrum, (ii) the RW integrals
and their (1±cosθ) kernels, (iii) the pulsed incoherent sum + the
time–bandwidth product, (iv) field-level Babinet, (v) HG/MCML transport with
Beer–Lambert and the diffusion limit. Five derivations, not five books.
Everything else is lookup.

Then the lineage and breadth:
- **Your lineage** (§6): Romallosa 2003 (the anchor) + Blanca & Saloma 1998.
- **The transport half** (§5): Wang MCML + Henyey–Greenstein — that's `scatter.py`.
- Breadth (§3 structured, §4 pulsed, §7 modern scattering optics) as needed.

---

## 1. Foundations — the textbook backbone (own these)

- ★★★ **M. Born & E. Wolf, *Principles of Optics*** (7th ed., CUP 1999). The
  canon. Ch. 3 (foundations), **Ch. 8.8 (Debye/aplanatic focusing)**, Ch. 8.6
  (Babinet — your annular apertures), Ch. 10 (partial coherence). This is the
  book you cite for the diffraction integral, Babinet, and the aplanatic sine
  condition.
- ★★★ **J. W. Goodman, *Introduction to Fourier Optics*** (3rd/4th ed.). The
  angular-spectrum representation, the pupil→PSF Fourier relationship, and the
  transfer-function view. Read *before* Born & Wolf — it makes the "photon = a
  plane-wave component" picture obvious.
- ★★★ **L. Novotny & B. Hecht, *Principles of Nano-Optics*** (2nd ed., CUP
  2012). **Ch. 3 (tightly focused fields)** and **Ch. 4 (angular spectrum)** are
  the *direct* reference for your vector launcher — Eq. 3.66 (refracted
  polarization) is literally in `montecarlo.sample_photons_vector`. The single
  most useful modern text for this project.
- ★★★ **L. Mandel & E. Wolf, *Optical Coherence and Quantum Optics*** (CUP
  1995). For the coherent/incoherent bookkeeping (temporal coherence, the
  spectrum ↔ time relationship behind Eq. 10). Reference, not cover-to-cover.
- ★★ **E. Hecht, *Optics*** (5th ed.) — the gentle warm-up if any of the above
  feels steep; good on physical intuition for diffraction and polarization.
- ★★ **B. Saleh & M. Teich, *Fundamentals of Photonics*** — excellent on
  Gaussian beams, Bessel beams, and pulse propagation; a friendlier bridge to
  the structured-pupil and pulsed material.

**Electromagnetism substrate** (you already used ∇·E and Helmholtz as audit
checks — know why they hold):
- ★★★ **D. J. Griffiths, *Introduction to Electrodynamics*** (4th ed.). Ch. 9
  (EM waves), the wave equation, polarization. The floor everything stands on.
- ★★ **J. D. Jackson, *Classical Electrodynamics*** (3rd ed.). Ch. 7–10 for the
  rigorous vector-diffraction and multipole background when Griffiths isn't
  enough. Reference depth.

---

## 2. High-NA vector focusing — the deterministic engine

- ★★★ **B. Richards & E. Wolf, "Electromagnetic diffraction in optical systems
  II," Proc. R. Soc. Lond. A 253, 358 (1959).** THE paper. Your I₀, I₁, I₂ and
  the (1±cosθ) kernels are Eqs. herein. Read line by line.
- ★★★ **E. Wolf, "Electromagnetic diffraction in optical systems I," Proc. R.
  Soc. Lond. A 253, 349 (1959).** The companion (the Debye–Wolf integral
  framework). Read together with the above.
- ★★ **B. Boruah & M. Neil**, and ★★ **Leutenegger et al., "Fast focus field
  calculations," Opt. Express 14, 11277 (2006)** — efficient numerical
  evaluation of the RW integrals (chirp-z / FFT methods); useful when you scale
  to large 3-D volumes (relevant to your "NUFFT would speed this up" note).
- ★★ **Youngworth & Brown, "Focusing of high numerical aperture
  cylindrical-vector beams," Opt. Express 7, 77 (2000)** — vector beams at the
  focus; the natural extension of your linear-x input to radial/azimuthal.

---

## 3. Structured pupils — annular & axicon / Bessel

- ★★★ **J. Durnin, "Exact solutions for nondiffracting beams I," J. Opt. Soc.
  Am. A 4, 651 (1987)** and **Durnin, Miceli & Eberly, PRL 58, 1499 (1987).**
  The Bessel beam. Your axicon J₀² prediction is from here.
- ★★ **C. J. R. Sheppard & T. Wilson, "Gaussian-beam theory of lenses with
  annular aperture," Microw. Opt. Acoust. 2, 105 (1978).** Your Phase-3
  Gaussian-ring checkpoint anchor.
- ★★ **J. H. McLeod, "The axicon: a new type of optical element," J. Opt. Soc.
  Am. 44, 592 (1954).** The origin of the axicon.
- ★★ **Sheppard & Choudhury**, and the annular-aperture DOF-extension line
  (superresolution / focal-depth engineering) — for the DOF = 1/(1−ε²) law and
  its limits.
- ★ **Grosjean, Courjon et al.** on Bessel-beam behavior at high NA (vector
  corrections) — relevant to your Phase-3 "vector deformation of the Bessel
  core" candidate result; check whether the specific high-NA annular
  deformation metric is already published.

---

## 4. Pulsed / few-cycle focusing (the temporal axis)

- ★★★ **K. M. Romallosa, J. Bantang & C. Saloma, "Three-dimensional light
  distribution near the focus of a tightly focused beam of few-cycle optical
  pulses," Phys. Rev. A 68, 033812 (2003).** YOUR ANCHOR. Eq. 10 (spectral
  integration), the |I₀−I₂|² cut, the Linfoot analysis. Know it better than the
  authors.
- ★★ **Z. L. Horváth & Z. Bor, "Focusing of truncated Gaussian beams," Opt.
  Commun. 222, 51 (2003).** Your apodization A(θ) = exp(−α_t sin²θ/sin²α).
- ★★ **M. Kempe, U. Stamm, B. Wilhelmi & W. Rudolph**, "Spatial and temporal
  transformation of femtosecond laser pulses by lenses," J. Opt. Soc. Am. B ~9
  (1992) — space-time coupling of focused ultrashort pulses; the classic on
  pulse-front distortion at a focus.
- ★★ **Gu & Sheppard** and the general "focusing of pulsed/broadband beams"
  literature — for the DOF-vs-bandwidth question (verify your bandwidth-
  invariance claim against this).
- ★ **I. Walmsley / ultrafast metrology texts** — for the transform-limited
  Gaussian pulse relations you re-derived (Δν·Δt = 0.441).

---

## 5. Monte Carlo light transport (the scattering engine)

- ★★★ **L. Wang, S. L. Jacques & L. Zheng, "MCML — Monte Carlo modeling of
  light transport in multi-layered tissues," Comput. Methods Programs Biomed.
  47, 131 (1995).** Your `scatter.rotate` local-frame update is the MCML
  algorithm. The standard reference for photon-packet transport.
- ★★★ **L. G. Henyey & J. L. Greenstein, "Diffuse radiation in the galaxy,"
  Astrophys. J. 93, 70 (1941).** The HG phase function in `hg_sample`.
- ★★ **S. A. Prahl, M. Keijzer, S. L. Jacques & A. J. Welch, "A Monte Carlo
  model of light propagation in tissue," (1989)** — the foundational photon-
  transport MC before MCML; good for the physical reasoning.
- ★★ **A. Ishimaru, *Wave Propagation and Scattering in Random Media*** (1978).
  The radiative-transfer-equation ↔ wave-equation bridge; the diffusion
  approximation (your rung-5 target) is derived here. Essential for the
  thick-slab limit.
- ★★ **C. F. Bohren & D. R. Huffman, *Absorption and Scattering of Light by
  Small Particles*** (Wiley 1983). Mie theory — needed if you replace HG with a
  real particle phase function (a future direction).

---

## 6. The Saloma school — your direct lineage (read all of these)

*This is the group you are extending; owning this section is how you own the
research. Exact citations ★ = verify (I couldn't run live search).*

- ★★ **C. M. Blanca & C. Saloma, "Monte Carlo analysis of two-photon
  fluorescence imaging through a scattering medium," Appl. Opt. 37, 8092
  (1998).** **The most directly relevant precedent to your work** — MC of a
  focused beam's fate in a turbid medium for two-photon microscopy. Read this
  next after Romallosa 2003; your Phase-6b is its natural high-NA vector +
  structured-pupil generalization.
- ★ **C. M. Blanca & C. Saloma**, follow-on Applied Optics papers (~1999–2001)
  on signal/resolution in two-photon and confocal imaging through scattering
  media, and temporal broadening of focused pulses in turbid media — *verify
  titles/vols*; several are directly on your topic.
- ★ **V. R. Daria, C. M. Blanca, C. Saloma et al.** — confocal/two-photon
  microscopy instrumentation and imaging through turbid media.
- ★ **C. Palmes-Saloma & C. Saloma** — biological deep imaging applications
  (the "why" motivation: imaging into tissue).
- ★ **C. Saloma et al.** on optical superresolution, photodetection statistics,
  and spatial signal recovery — the broader methodological context of the group.
- ★★ **K. Romallosa & J. Bantang** — the co-authors of your anchor paper; check
  for related focusing/pulse work.

**Action when search resets:** pull Blanca & Saloma 1998 + every Saloma-group
paper with "scattering," "turbid," "two-photon," "focus," or "pulse" in the
title (Google Scholar "cited by" from Romallosa 2003 and Blanca–Saloma 1998
will surface the cluster). Build the citation graph — that *is* your field map.

---

## 7. Modern scattering optics — where the frontier is (breadth + future)

*You are not currently doing these; they define the surrounding landscape and
the genuine open gaps (§8).*

- ★★★ **I. M. Vellekoop & A. P. Mosk, "Focusing coherent light through opaque
  strongly scattering media," Opt. Lett. 32, 2309 (2007).** Launched
  wavefront-shaping. The modern reframing of "focus through scatter."
- ★★ **A. P. Mosk, A. Lagendijk, G. Lerosey & M. Fink, "Controlling waves in
  space and time…," Nat. Photonics 6, 283 (2012).** The review — read for the
  whole landscape.
- ★★ **S. Feng, C. Kane, P. A. Lee & A. D. Stone**, and **I. Freund et al.** —
  the **optical memory effect** (angular/spatial correlations of speckle). A
  coherent-transport phenomenon your *incoherent* halo currently cannot capture
  (see §8).
- ★★ **Yoo & Alfano** / time-gated **ballistic imaging** — the ballistic vs
  diffuse separation you already compute is the theory behind this technique.
- ★★ **Akbulut, Popoff, Rotter, Gigan, Cao** — transmission-matrix and
  disordered-photonics reviews; the state of the art for coherent control
  through scattering.
- ★ **Coherent backscattering / weak localization** (van Albada & Lagendijk;
  Wolf & Maret, 1985) — the enhanced-backscatter cone, a pure coherent-MC
  signature.

---

## 8. Literature gaps & future directions (verified against §1–7)

**First, verifying the current novelty claims** (`docs/KEY_RESULTS.md` "3
candidates") against the above — honest assessment:

| current claim | prior art | verdict |
|---|---|---|
| Pulsed-annular DOF bandwidth-invariance (Phase 5) | Romallosa 2003 (pulsed full disk); Sheppard (annular DOF) — but *not combined* | **plausibly novel** as a combined statement; verify no pulsed-annular paper exists |
| Vector Bessel deformation at high NA (Phase 3) | vector Bessel beams known (Novotny–Hecht; Youngworth–Brown) | **known physics**, but your isolated annular metric may be a clean *demonstration*, not new physics — frame modestly |
| Corrected anisotropic NA thresholds (Phase 2) | RW anisotropy is textbook (Novotny–Hecht) | a **correction of a specific prior report**, not a field-level novelty |

**Honest overall:** the individual pieces are largely known; **the novelty is
the integration** — a *single* framework doing high-NA **vector** + **pulsed**
+ **structured-pupil** focusing **through a scattering medium** with validated
limits. No single prior work spans all four axes (Romallosa: no scattering;
Blanca–Saloma: scalar, unstructured; wavefront-shaping: coherent control, not
this forward model). That integrated forward model is the defensible
contribution — plus the rigorously *validated* MC (your first-principles audit
is itself a methodological contribution most transport-MC papers lack).

**Genuine open gaps / future directions (beyond the current plan):**

1. **Coherent diffuse halo (the biggest one).** Your halo is the *incoherent*
   ensemble mean — so it cannot reproduce **speckle**, the **memory effect**, or
   the **coherent-backscattering cone**. Keeping the phase along scattered paths
   (you already carry it for the ballistic core) would bridge "incoherent
   transport MC" and "full-wave," and connect your model to the entire §7
   wavefront-shaping field. *High-impact, natural for your phase-carrying
   photons.*
2. **Self-healing of Bessel/axicon beams in scattering media**, quantified. Your
   axicon segment + `propagate_slab` can measure reconstruction length vs μ_s —
   a clean, publishable, under-quantified question.
3. **Vector depolarization through scattering** — track the 3-vector amplitude
   (you already have it) through scatter events → degree-of-polarization vs
   depth for a tightly focused beam. Largely unexplored at high NA.
4. **Pulsed structured light for deep two-photon** — combine all threads: does a
   pulsed annular/Bessel beam preserve two-photon signal (∝∫I²) deeper than a
   Gaussian? Directly extends Blanca–Saloma with your structured pupils.
5. **Temporal broadening of the focused pulse in the medium** — Blanca–Saloma
   and Kempe touched pulse distortion; your λ-sampling MC can give the
   arrival-time spread of ballistic vs scattered photons (time-gating theory).
6. **Real particle phase functions (Mie)** instead of HG — wavelength- and
   size-dependent scattering; couples to your λ-sampling for chromatic effects.
7. **Inverse problem / descattering** — given the forward model, learn to
   recover the object (the modern ML-for-optics direction; your validated
   simulator is a training-data generator).

---

## 9. A 6-week reading plan to fluency

- **Wk 1** — Goodman (angular spectrum, Fourier optics) + Griffiths ch. 9.
- **Wk 2** — Born & Wolf ch. 8.8 + Wolf 1959 I + Richards & Wolf 1959 II (derive
  I₀,I₁,I₂ yourself; check against `rw_integrals.py`).
- **Wk 3** — Novotny–Hecht ch. 3–4 (re-derive Eq. 3.66; check vs
  `sample_photons_vector`).
- **Wk 4** — Romallosa 2003 (reproduce its figures — you already have) + Durnin
  1987 + Sheppard–Wilson 1978.
- **Wk 5** — Wang MCML 1995 + Henyey–Greenstein + Ishimaru (diffusion approx).
- **Wk 6** — Blanca & Saloma 1998 + the Saloma-group citation graph +
  Vellekoop–Mosk 2007 (know where the frontier is).

By the end, every line of `mcdo/` traces to a paper you have read and can
re-derive — that is what "owning it" means.
