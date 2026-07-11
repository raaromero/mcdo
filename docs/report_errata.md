# Review of `parallel_progress_report.pdf` (2026-02-09) against the rebuilt, validated code

Reviewed 2026-06-12 against `romallosa2003/` Phase-1/2 validated results
(`output/02_na_apodization/check*.png`, `docs/theory/01–02`).

## Confirmed correct in the report

- RW field components & integrals as written on slides 9–10 (with kernels) ✓
- A(θ) = exp(−α·sin²θ/sin²α_max) apodization (slide 15) — same physically
  correct aplanatic form we validated ✓
- Horváth & Bor truncation conventions, α=(r_ap/w)², edge values (16–18) ✓
- Low-NA agreement RW(Gaussian) = Debye(Gaussian) at NA=0.1 (slide 19) ✓
  (our check 1: all theories coincide with Airy to 10⁻⁴ at X_NA=0.1)
- Annular Babinet at the field level, ε definition (slide 30) ✓
- DOF(ε) = DOF₀/(1−ε²) at low NA; measured DOF falling below the paraxial
  theory at NA=0.9 (slide 32) ✓ physically expected
- Window-truncation caveat for ε=0.99 DOF handled by re-measuring with a
  larger window (slides 33–34): 88.4×λ/NA² vs theory ≈ 90 ✓ consistent
- Few-cycle pulse facts (slide 13): τ<1.2 fs criticality, coherence/Nyquist ✓

## Slide-level errors (typos / labeling)

1. **Slide 7**: E_x = −j(I₀ − I₂cos φ) is wrong — must be −j(I₀ + I₂cos 2φ);
   E_y must carry sin 2φ. (Slide 9 has the correct forms — internal
   inconsistency.) Slide 7's compact integral I_m ∝ sin^{m+1}θ J_m drops the
   (1±cosθ) kernels of I₀ and I₂ (slide 10 has them correctly).
2. **Slide 11**: u = (2π/λ)sin²α·z, v = (2π/λ)sinα·r omit the refractive
   index — k = 2πn/λ in the image medium. (Harmless for the report's n=1
   studies, wrong for the Romallosa n=1.3 case.)
3. **Slide 20**: title says "α = 4, NA = 0.1" but the plot is NA = 0.9; the
   bullet about Gaussian E_z appears on a slide titled "Uniform".

## Substantive issue — the NA-threshold study (slides 24–28) needs redoing

The headline claims were:
  - Gaussian α=4: RMSE>0.01 at NA≈0.30, >0.05 at NA≈0.55
  - Uniform: RMSE>0.01 at NA≈0.75, >0.05 at NA≈0.95
  - "Uniform illumination allows scalar approximation at much higher NA"

Two problems:

**(a) Inconsistent scalar reference for the Gaussian case.** Slide 24 quotes
RW FWHM 0.442 μm vs "Debye" 0.199 μm at NA=0.9 (+122%). But 0.199 μm is
*smaller* than the uniform Airy FWHM (0.304 μm) — an underfilled (α=4)
pupil cannot focus tighter than a filled one. 0.199 μm matches the *paraxial
Gaussian-beam* formula w₀=λ/(π·NA) instead, which is invalid at NA=0.9.
Slide 20's own plot (proper Gaussian-Debye) shows RW(Gaussian) and
Debye(Gaussian) nearly overlapping at NA=0.9 — contradicting slide 24's
+122%. The "Gaussian fails much earlier" conclusion measures the breakdown
of the paraxial reference formula, not of scalar diffraction.

**(b) The lenient uniform thresholds hide polarization.** The report's RW
runs used circular polarization / azimuthally-symmetric |Ex|², which
averages away the strongest vector signature. For linear polarization the
anisotropy is the dominant effect (our check 6: FWHM_x/FWHM_y → 1.4 at
X_NA=1.2; x-cut deviates from scalar by 1% already at X_NA≈0.30 and 5% at
≈0.60, n=1.3). "When is vector theory necessary" therefore depends on
polarization convention and measured cut — a single threshold number is
not well-posed without stating both. Also NA values at n=1 (report) and
n=1.3 (Romallosa) are not comparable; quote sinα alongside NA.

**Redo plan (notebook 02):** RW vs scalar Debye *with the same A(θ)* for
uniform and Gaussian, linear polarization, both cuts + azimuthal average,
thresholds quoted vs sinα. Our scalar module already supports this.
