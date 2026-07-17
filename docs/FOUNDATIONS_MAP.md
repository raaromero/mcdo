# Foundations map — concept ⇄ math ⇄ textbook ⇄ mcdo

*The study syllabus for owning this field. For each physics pillar of the
thesis: the **concept**, the **one equation you must be able to derive from
scratch**, **where to learn it** (gentle → rigorous, with chapters), and **where
it lives in mcdo**. Complements the other two docs — `LITERATURE.md` §0 tells you
*which book to buy*; `theory/FIELD_HISTORY.md` gives the *chronological story*;
this is the *topic-by-topic learning path*.*

**Chapter numbers**: confident ones are given plainly; where an edition may
differ the section is named so you can find it. Books by short name:
- **Griffiths** = *Introduction to Electrodynamics* (4th ed.) — EM at quals level.
- **Hecht** = Eugene Hecht, *Optics* (5th ed.) — gentlest optics.
- **Goodman** = *Introduction to Fourier Optics* (4th ed.) — scalar diffraction.
- **N&H** = Novotny & (Bert) Hecht, *Principles of Nano-Optics* (2nd ed.) — the
  high-NA focusing bible; **the single most important book for this thesis.**
- **B&W** = Born & Wolf, *Principles of Optics* — the reference.
- **Gu** = Min Gu, *Advanced Optical Imaging Theory* — closest single text to
  the Romallosa toolkit (vector Debye + apodization + ultrashort-pulse focusing).
- **S&T** = Saleh & Teich, *Fundamentals of Photonics*; **Ishimaru** = *Wave
  Propagation and Scattering in Random Media* (transport).

**Mastery test** (not "I read it" but): can you re-derive the boxed equation of
each pillar on a blank page, and say in one sentence why each term is there?
Five re-derivations beat five books skimmed.

---

## Pillar 0 — Electromagnetic foundation *(do this first — doubles as EM-quals review)*
**Concept.** Light is a transverse EM wave; Maxwell's equations in a
source-free medium give a wave equation, whose plane-wave solutions carry
polarization and energy flow. Everything downstream is bookkeeping of these
plane waves.
**Own this equation.**
$$\nabla^2\mathbf{E} - \frac{n^2}{c^2}\frac{\partial^2\mathbf{E}}{\partial t^2}=0,\qquad \mathbf{E}=\mathbf{E}_0\,e^{i(\mathbf{k}\cdot\mathbf{r}-\omega t)},\ \ |\mathbf{k}|=nk_0,\ \ \mathbf{k}\cdot\mathbf{E}_0=0.$$
Derive the wave equation from ∇×E and ∇×B; get the transversality
(k·E₀=0), the polarization states, and the Poynting vector S = E×H.
**Learn it.** Griffiths Ch 9 (9.2 waves in vacuum, 9.3 in matter, polarization
9.2 end, energy/Poynting 9.2.3) — start here. Then **N&H Ch 2** (same content,
compressed to exactly what focusing needs). Rigorous: Jackson Ch 7.
**In mcdo.** The ∇·E = 0 and Helmholtz residual checks in
`scripts/audit_first_principles.py` — the audit literally tests this pillar.

## Pillar 1 — Scalar diffraction & the angular spectrum
**Concept.** A field on a plane propagates by summing spherical wavelets
(Huygens–Fresnel), equivalently by propagating each plane-wave component with a
phase e^{i k_z z} (angular spectrum). The two pictures are one Fourier transform
apart.
**Own this equation.** Angular-spectrum propagation:
$$U(x,y,z)=\iint \tilde U(k_x,k_y;0)\,e^{i k_z z}\,e^{i(k_x x+k_y y)}\,dk_x\,dk_y,\quad k_z=\sqrt{k^2-k_x^2-k_y^2}.$$
Know how this reduces to Fresnel (paraxial e^{ik_z z}≈e^{ikz}e^{-i(k_x^2+k_y^2)z/2k})
and Fraunhofer (far-field = Fourier transform of the aperture).
**Learn it.** **Goodman Ch 3** (Huygens–Fresnel, Rayleigh–Sommerfeld; angular
spectrum in §3.10) then Ch 4 (Fresnel/Fraunhofer). Gentle first pass: Hecht
Ch 10. Rigorous: B&W Ch 8.
**In mcdo.** The conceptual substrate of the whole Debye picture; the low-NA
limit your engine reproduces (Airy pattern, `check1_lowNA_convergence`).

## Pillar 2 — Focusing & the 3-D focal region (Debye, Lommel)
**Concept.** A lens converts an aperture field into a converging cone of plane
waves; near focus the field is the Debye integral over that cone. Along the axis
and in the focal plane the scalar result is Lommel's U,V functions — the Airy
pattern is the in-focus slice.
**Own this equation.** Debye approximation (scalar):
$$U(\mathbf{r})\propto \iint_{\text{cone}} A(s_x,s_y)\,e^{i k \mathbf{s}\cdot\mathbf{r}}\,d\Omega,$$
with optical coordinates u = kz sin²α, v = kr sinα organizing the focal region.
**Learn it.** **B&W §8.8** ("three-dimensional light distribution near focus" —
the Lommel U_n,V_n functions live here). Modern/compact: **Gu** (Debye focusing
chapter) and **N&H Ch 3** intro. Goodman Ch 5 for the lens-as-Fourier-transform
view.
**In mcdo.** `mcdo/debye.py`, the (u,v) coordinates; Phase-1 axial/transverse
profiles.

## Pillar 3 — Vector high-NA focusing (Richards–Wolf) ★ the engine's core
**Concept.** At high NA the plane-wave polarizations in the cone cannot stay
parallel; carrying the full vector field through the Debye integral gives the
Richards–Wolf result — the I₀, I₁, I₂ integrals and a real longitudinal E_z.
**Own this equation.** The RW integrals (linearly polarized input):
$$I_n(r,z)=\int_0^\alpha A(\theta)\sqrt{\cos\theta}\,\sin\theta\,g_n(\theta)\,J_n(kr\sin\theta)\,e^{ikz\cos\theta}\,d\theta,$$
with g₀=(1+cosθ), g₁=sinθ, g₂=(1−cosθ); then
E ∝ (I₀+I₂cos2φ, I₂sin2φ, −2iI₁cosφ). Know where √cosθ (aplanatic/energy) and
each g_n come from.
**Learn it.** **N&H Ch 3 (§3.5–3.6)** — the cleanest modern derivation, *read
this one*. Original: Richards & Wolf, Proc. R. Soc. A 253, 358 (1959). Also Gu
(vector Debye chapter).
**In mcdo.** `mcdo/rw_integrals.py` — this pillar *is* the engine. Phase 2.

## Pillar 4 — Pupil engineering: apodization, annulus, axicon, Bessel
**Concept.** Shaping A(θ) reshapes the cone's weighting: Gaussian apodization
softens edges; an annulus (A=0 below θ_in) extends depth of focus and pushes
toward a J₀ Bessel core; a conical phase (axicon) makes a non-diffracting focal
segment.
**Own these.** Thin-annulus → Bessel: I ∝ J₀²(kr sinα); annular DOF law
DOF ∝ 1/(1−ε²); ideal Bessel J₀(k_r ρ) is diffraction-free (infinite power
caveat). Axicon phase φ(θ) = β sinθ/sinα.
**Learn it.** Bessel beams: **S&T** beam-optics chapter + Durnin, PRL 58, 1499
(1987). Apodization & annular pupils: **Gu** (apodization chapter), N&H Ch 4.
Axicon: McLeod, JOSA 44, 592 (1954); Sheppard & Wilson, IEE J. MOA 2, 105 (1978).
**In mcdo.** `mcdo/apodization.py`, `mcdo/annular.py` (field-level Babinet),
axicon phase; Phases 3–4 and `verify_annular.py`, `verify_axicon.py`.

## Pillar 5 — Time domain: pulses, bandwidth, the incoherent spectral sum
**Concept.** A short pulse is a coherent superposition of monochromatic fields
over a Gaussian spectrum; a slow detector time-averages, so the measured focal
intensity is an **incoherent weighted sum of CW solutions** — Romallosa's
Eq. 10. Each color focuses at its own scale v ∝ ω.
**Own this equation.**
$$I(\mathbf{r})=\int |E(\omega)|^2\, I_{\rm cw}(\mathbf{r};\omega)\,d\omega,\qquad |E(\omega)|^2\propto e^{-(\omega-\omega_c)^2/2a},\ a=\tfrac{2\ln2}{\tau^2},$$
plus the transform-limited time–bandwidth product Δν·τ ≈ 0.44 (Gaussian).
Know why the sum is over |E(ω)|² and why no extra ω-prefactor is needed (the
CW field already carries the k-scaling — the bug fixed in the dashboard).
**Learn it.** Fourier transform of a pulse & TBP: **S&T** (pulsed/ultrafast
sections) or Diels & Rulofson, *Ultrashort Laser Pulse Phenomena* Ch 1.
Focusing of ultrashort pulses specifically: **Gu** (ultrashort-pulse chapter);
Romallosa, Bantang & Saloma, PRA 68, 033812 (2003).
**In mcdo.** `mcdo/intensity.py` `pulsed_intensity`; `config.py` `spectral_power`,
`omega_grid`; Phase 5. Convergence proof in the dashboard.

## Pillar 6 — Image-quality metrics (Strehl, Linfoot)
**Concept.** Reduce a focal pattern to numbers: Strehl = peak-intensity ratio
vs the ideal; Linfoot's F (fidelity), S (structural content), Q (correlation
quality) compare a test pattern to a reference, with 2Q − S = F.
**Own these.** Strehl S = |⟨e^{iΔφ}⟩|² (aberration form); Linfoot F, S, Q as the
normalized overlap integrals of test vs reference intensity.
**Learn it.** Strehl/aberrations: **B&W Ch 9**; N&H Ch 4. Linfoot: Linfoot,
*Fourier Methods in Optical Image Evaluation* (1964) — the primary source (short).
**In mcdo.** `mcdo/linfoot.py`; Phase-1 `fig4_linfoot`.

## Pillar 7 — Scattering & photon transport *(the MC phase)*
**Concept.** A medium removes ballistic light exponentially (Beer–Lambert) and
redistributes it by single/multiple scattering; the ensemble obeys the
radiative-transfer equation, which in the thick limit reduces to diffusion.
Monte-Carlo samples photon paths directly: step from µ_t, deflect by the
Henyey–Greenstein phase function, repeat.
**Own these.** Beer–Lambert I = I₀e^{−µ_t d}, µ_t = µ_s+µ_a; HG phase function
p(cosθ) = (1−g²)/[2(1+g²−2g cosθ)^{3/2}]; similarity relation µ_s′ = µ_s(1−g);
diffusion µ_eff = √(3µ_a µ_tr). Know how the RTE → diffusion approximation goes.
**Learn it.** Transport & diffusion: **Ishimaru** Vol. 1 (single scattering,
RTE) and the diffusion-approximation chapter. Tissue-optics specifics + the MC
algorithm: Wang, Jacques & Zheng, "MCML," Comput. Methods Programs Biomed. 47,
131 (1995); Farrell, Patterson & Wilson, Med. Phys. 19, 879 (1992). EM cross-
sections/scattering background: Jackson Ch 10 or B&W Ch 14 (Mie).
**In mcdo.** `mcdo/scatter.py`, `mcdo/focus_scatter.py`; validation ladder
rungs 2–6; the `mc.html` / `focus_scatter.html` dashboards.

---

## Suggested learning order (maps to an 8-week arc)
1. **Pillar 0** (Griffiths 9 / N&H 2) — the EM footing; also your EM-quals review.
2. **Pillar 1** (Goodman 3–4) — scalar diffraction & angular spectrum.
3. **Pillar 2** (B&W §8.8 / Gu) — the focal region, Debye, Lommel.
4. **Pillar 3** (N&H 3) — Richards–Wolf. *The keystone; spend the most time here.*
5. **Pillar 4** (S&T + Durnin/McLeod) — pupil engineering.
6. **Pillar 5** (Gu + Romallosa) — pulses & the spectral sum.
7. **Pillar 6** (B&W 9 + Linfoot) — metrics.
8. **Pillar 7** (Ishimaru + MCML) — transport, when you reach the MC phase.

Each week: read the chapter, then **re-derive that pillar's boxed equation on
paper**, then open the matching mcdo file and confirm the code is that equation.
When all three click for a pillar, you own it.

*Cross-refs: book-choice rationale → `LITERATURE.md` §0; the same content as a
historical narrative → `theory/FIELD_HISTORY.md`; presentable papers per topic
→ `RRL_PRESENTABLES.md`.*
