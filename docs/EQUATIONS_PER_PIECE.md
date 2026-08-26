# Equations per piece — with code-verification status

*Specs held consistent everywhere: NA = 0.8, λ_c = 750 nm, n = 1.33 (low-NA
checks use NA = 0.1–0.3). Each equation below is the one to put on the slide,
followed by how the current code was verified to implement it.*

## Symbol glossary — DEFINE every symbol used on each equation slide
- **P (x,y,z)** — observation point near focus · **r, z** — radial/axial position (µm) · **φ** — azimuth
- **θ** — ray convergence angle (integration variable 0→α) · **α = arcsin(NA/n)** — max half-angle
- **NA** — numerical aperture · **n** — medium refractive index · **k = n·2π/λ = nω/c** — wavenumber
- **λ, λ_c** — wavelength / carrier wavelength (750 nm) · **ω** — angular frequency · **ω_c = 2πc/λ_c** — carrier
- **u = k sin²α·z, v = k sinα·r** — optical coordinates · (u,v)=(0,0) is geometric focus
- **I_m (m=0,1,2)** — Richards–Wolf diffraction integrals · **J_m** — Bessel function order m
- **E_x, E_y, E_z** — field components · **j = √−1**
- **τ** — pulse FWHM duration · **a = 2ln2/τ²** — spectral width param · **σ = √a** — std of |E(ω)|²
- **Ω** — spectral bandwidth · window ω∈(0,2ω_c) = ±full-support (±4σ) capped at ω>0
- **A(θ)** — pupil apodization · **α_t = (r_ap/w)²** — Gaussian truncation coeff · **w** — beam waist · **ρ = sinθ/sinα**
- **ε** — annular obstruction ratio (inner/outer) · **F, S, Q** — Linfoot fidelity / structural content / correlation quality; 2Q−S=F

---

## Piece 4 — Scalar limit → Airy
**Scalar Debye (drop polarization):**
  U(u,v) = ∫₀^α √cosθ · sinθ (1+cosθ) · J₀(v sinθ/sinα) · exp(i u cosθ/sin²α) dθ

**Paraxial focal plane (Airy):**  I(v) = [2 J₁(v)/v]²
**Paraxial on-axis (defocus):**   I(u) = [sin(u/4)/(u/4)]²

**Verified:** `verify_tanaka_paraxial` scalar = paraxial to 1.2e-4 (all α_t);
`verify_na_convergence` scalar→Airy 1e-4 at NA 0.1; `verify_mc_clear` MC = Airy 0.0015.

## Piece 5 — Richards–Wolf vector integrals
**Diffraction integrals (m = 0,1,2):**
  I_m(u,v) = ∫₀^α √cosθ · sinθ · gₘ(θ) · J_m(v sinθ/sinα) · exp(i u cosθ/sin²α) dθ
  g₀ = (1+cosθ),  g₁ = sinθ,  g₂ = (1−cosθ)   ⇒ I₁ integrand carries sin²θ.

**Field components (x-polarized input):**
  Eₓ = −i(I₀ + I₂cos2φ),  E_y = −i I₂ sin2φ,  E_z = −2i I₁ cosφ

**Verified:** `rw_integrals.py` lines 84,99–101 match (√cosθ; B0,B1,B2 kernels;
phase exp(i u cosθ/sin²α) with u=k sin²α z; Bessel arg v sinθ/sinα = k r sinθ).
`audit_first_principles` Maxwell ∇·E = 1.5e-4, Helmholtz 2.1e-4 (both at FD floor);
broken Ez-factor and wrong-k controls correctly fail. FWHM y-cut 475 nm ≈ 472.8.

## Piece 6 — Optical coordinates
  u = (2π/λ) sin²α · z = k sin²α · z
  v = (2π/λ) sinα · r  = k sinα · r
  α = arcsin(NA / n)
**Verified:** same u,v used in `rw_integrals.compute_integrals` (lines 76–77);
results scale-invariant → one calc serves all λ, NA.

## Piece 7 — Few-cycle pulse   (all CONFIRMED vs Romallosa 2003 PRA 68 033812)
**Gaussian spectral weight (Eq. 9 → power spectrum):**
  |E(ω)|² ∝ exp[ −(ω−ω_c)² / (2a) ],   a = 2 ln2 / τ²   ✓ Eq.(9): τ=(2ln2/a)^½
**Incoherent spectral sum (Eq. 10):**
  |E(P)|² = ∫ |E(ω)|² · |E(P;ω)|² dω,  over the FULL spectral support ω ∈ (0, 2ω_c)
  (= half-width min(4σ, ω_c), σ=√a; the ω_c cap keeps ω>0). 201 samples, RK4, b=0.
**Window subtlety (documented, validated):** the paper *writes* ±Ω/2 with Ω the
  FWHM bandwidth (4ln2/τ), but integrating only that band DISCARDS ~24% of the
  Gaussian weight → S_tr=1.020, missing the paper's own S_tr=1.062. Integrating the
  full support (0,2ω_c) reproduces the paper: S_ax=1.058 (paper 1.057), F≈0.96.
  ⇒ Slide states (0,2ω_c); footnote the FWHM-band caveat.
**Critical pulse width (paper conclusion):** τ_crit = λ_c/2c = 1.25 fs.
  Coherence cτ = 359.7 nm < Nyquist λ_c/2 = 375 nm → aliasing.
**Verified:** pulsed FWHM 479.0 nm > CW 472.8 (`verify_physics`); S_ax 1.058 vs
paper 1.057 with full-support window; sum converges <0.1% at ~11 nodes.

## Piece 8 — Gaussian apodization
  A(θ) = exp( −α_t · sin²θ / sin²α_max )   ≡  A(ρ) = exp(−α_t ρ²),  ρ = sinθ/sinα
  α_t = (r_aperture / w_beam)²   ·   α_t→0 uniform,  α_t ≳ 4 untruncated
Inserted into every I_m integrand: I_m ∝ ∫ A(θ) √cosθ … dθ
**Source:** Horváth & Bor, "Focusing of truncated Gaussian beams," Opt. Commun.
222, 51–68 (2003) — "truncation coefficient" (VERIFIED via ADS/Optica; supersedes
the earlier erroneous PRE 63,026601 note). Companion: Appl. Opt. 43(3), 620 (2004).
**Verified:** `verify_apod_thresholds` (uniform/α_t=1/α_t=4 thresholds);
`verify_na_convergence` regression α_t→0 vs uniform = 7.7e-14 (identical).

## Piece 9 (added, verified) — Annular pupil / extended DOF
**Annular limit:** integrate θ ∈ [θ_in, α] with sinθ_in = ε sinα.
**DOF scaling:**  DOF(ε)/DOF(0) → 1/(1−ε²)   (thin-ring limit)
**Thin ring → Bessel:** I(v) → J₀²(v)  (Sheppard)
**Verified:** `verify_annular` ε=0 regression 0.0 (exact), DOF ratio measured;
`verify_sheppard` focal |I−J₀²·e^{−a²v²}| = 0.015, axial vs Sheppard Eq.33a = 0.008.

---
## Citations — verified 2026-08-15
- Richards & Wolf, Proc. R. Soc. A **253**(1274), 358–379 (1959) — VERIFIED (Royal Society, ADS).
- Romallosa, Bantang & Saloma, Phys. Rev. A **68**, 033812 (2003) — VERIFIED (title page + DOI).
- Horváth & Bor, Opt. Commun. **222**, 51–68 (2003) — VERIFIED (ADS/Optica). NOT PRE 2001.

## Flag status (checked vs Romallosa 2003 PDF, 2026-08-15)
- RESOLVED — (1±cosθ) kernels: confirmed verbatim = paper Eqs (5)–(7).
- RESOLVED — a = 2 ln2/τ²: confirmed = paper Eq (9)/power spectrum.
- RESOLVED — spectral window: code uses full support (0,2ω_c) and is VALIDATED to
  reproduce the paper (S_ax 1.058 vs 1.057). Paper's literal ±Ω/2 FWHM band loses
  24% of weight → wrong Linfoot. (My interim "quote ±Ω/2" note was wrong; corrected.)
- RESOLVED — S_tr residual: it was the TRANSVERSE Linfoot window. Paper Fig 2a spans
  ±6 µm; fig4 used ±1 µm. At ±6 µm S_tr=1.060 vs paper 1.062 (0.2%), F_tr=0.957 vs
  0.955–0.96. S=⟨a²⟩/⟨r²⟩ weights the slow pulsed pedestal, so it saturates ~1.060
  once the full pedestal is captured (plateau by 3–4 µm). NOT sampling, NOT n. FIX
  fig4_linfoot transverse window 1 µm → 6 µm.
- STILL PARAXIAL — DOF ∝ 1/(1−ε²): paraxial/thin-ring only; vector-deformed at NA 0.8 (dev 0.163).

*All physics reproduced from the current refactored engine on 2026-08-15;
40/40 tests + audit ALL PASS.*
