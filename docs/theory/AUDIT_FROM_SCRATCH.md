# From-scratch audit — every formula re-derived, every check independent

*2026-06-28. A ground-up review of the whole `mcdo/` package: each implemented
equation re-derived against its primary reference, then subjected to
**first-principles checks that depend on no prior reference** (Maxwell/Helmholtz
residuals with deliberately-broken controls, independent adaptive quadrature,
exact scattering statistics). Companion figure:
`output/00_overview/audit_first_principles.png`; machine-checked table printed by
`scripts/audit_first_principles.py`. Findings — including two errors this audit
itself made and then corrected — are logged at the end; honesty is the point.*

## 1. Module-by-module formula audit

| module | implemented | re-derived against | verdict |
|---|---|---|---|
| `rw_integrals.py` | I₀,I₁,I₂ with kernels √cosθ·sinθ(1+cosθ)J₀ / √cosθ·sin²θ·J₁ / √cosθ·sinθ(1−cosθ)J₂, phase e^{ikz cosθ}, Bessel argument kr sinθ (via u,v optical coords); Simpson weights | Richards–Wolf 1959; Novotny–Hecht Eqs. 3.58–3.60 | ✓ exact |
| `polarization.py` | \|E\|² = \|I₀+I₂cos2φ\|² + \|I₂\|²sin²2φ + 4\|I₁\|²cos²φ; x-cut, y-cut; circular = \|I₀\|²+\|I₂\|²+2\|I₁\|² | expand \|E\|² from E=(I₀+I₂cos2φ, I₂sin2φ, −2iI₁cosφ); azimuthal average re-derived | ✓ exact (average: ⟨cos²2φ⟩=⟨sin²2φ⟩=⟨cos²φ⟩·2=1) |
| `debye.py` | scalar U = ∫A√cosθ sinθ J₀(kr sinθ)e^{ikz cosθ}dθ; Airy [2J₁(v)/v]² | scalar Debye integral; paraxial limit | ✓ (bridged to an inline re-implementation at 5×10⁻¹⁵) |
| `annular.py` | field-level Babinet: I_m^ann = I_m(α)−I_m(α_in), sinθ_in=ε·sinα | linearity of the integral; both disks reduce to the same physical integrand J_m(kr sinθ)e^{ikz cosθ} regardless of each call's own (u,v) scaling | ✓ exact |
| `apodization.py` | A(θ)=e^{−α_t sin²θ/sin²α}; axicon e^{+iβ sinθ/sinα}; Gaussian ring | Horváth–Bor (sine condition r=f sinθ ⇒ Gaussian in sinθ); cone phase ∝ pupil radius | ✓ |
| `config.py` | a=2ln2/τ², \|E(ω)\|²=e^{−(ω−ω_c)²/2a}, FWHM=4ln2/τ; k=nω/c; ω-grid (0,2ω_c] | transform-limited Gaussian: FWHM_t·FWHM_ω = 4ln2 ⇔ Δν·Δt = 2ln2/π ≈ 0.441 — re-derived from E(t)∝e^{−t²/2σ_t²} | ✓ exact TBP |
| `intensity.py` | Eq. 10: I = Σ\|E(ω)\|² I_cw(ω) Δω | frequencies add incoherently in time-integrated intensity | ✓ (convention: no k² radiometric prefactor — same on both sides of every comparison, validated against the paper's Linfoot anchors) |
| `linfoot.py` | F=1−⟨(r−a)²⟩/⟨r²⟩, S=⟨a²⟩/⟨r²⟩, Q=⟨ar⟩/⟨r²⟩ | algebra: F = 2Q−S identically for a,r ≥ 0 | ✓ exact identity |
| `montecarlo.py` | θ ~ \|A\|√cosθ sinθ (inverse CDF), φ uniform, weight = pupil phase (scalar) or refracted 3-vector (vector); coherent sum | importance sampling of the Debye integrand (unbiased for any covering density); Novotny–Hecht 3.66 polarization | ✓ (vector kernels *independently* pinned by the ∇·E check below) |
| `montecarlo.mc_pulsed_intensity` | multinomial λ~\|E(ω)\|², coherent within / incoherent across ω, per-node \|Û\|²/n_m² | the angular density is λ-independent, so the per-node normalization constant is common and cancels on peak normalization | ✓ |
| `scatter.py` | HG inverse-CDF cosθ; MCML local-frame rotation; free path −lnξ/μ_s; boundary exit; weight e^{−μ_a·path} | HG41/MCML95; exponential free-path law | ✓ (statistics re-checked exactly below) |
| `focus_scatter.py` | entrance (−d tanθ cosφ, −d tanθ sinφ, −d); ballistic amplitude e^{−μ_s L/2}, L=d/cosθ; halo = forward-scattered, incoherent | ray through focus pierces z=−d there; Beer–Lambert in intensity = amplitude²; ensemble-mean halo | ✓ |
| `trials.py` | mean/std(ddof=1)/sem over ≥10 seeds | — | ✓ |

## 2. First-principles checks (no reference implementation, no literature)

Each check has a **deliberately-broken control** proving it can fail.

| check | result | control (broken) |
|---|---|---|
| **Helmholtz + dispersion** — (∇²+k²)U = 0 for the scalar Debye field; catches any u/v off-shell inconsistency (each component must satisfy k_⊥²+k_z²=k²) | residual 2.1×10⁻⁴ at h=5 nm = the FD floor (kh)²/12, falling ∝h² | operator at 1.05k → 0.093 = 1−1.05⁻² exactly |
| **Maxwell transversality** — ∇·E = 0 for the vector RW field; pins the (1±cosθ)/sin²θ kernels and the E_z factor to Maxwell itself | 1.5×10⁻⁴ at h=5 nm (FD floor) | E_z factor 2→1 → 0.102 (~700× the floor) |
| **Independent quadrature** — I₀,I₁,I₂ via scipy adaptive Gauss–Kronrod (shares nothing with our Simpson code), 18 integrals across focus/off-axis/defocus | max rel dev 7.1×10⁻¹¹ | — (agreement of two unrelated integrators) |
| **HG sampling** — bin counts vs *exact bin probabilities* from the analytic CDF F(μ)=(1−g²)/(2g)[(1+g²−2gμ)^{−1/2}−(1+g)^{−1}] | within sampling noise (≈3σ) at 4×10⁵ draws; F(1)−F(−1)=1 to 10⁻¹² | — |
| **Exact single-scatter probability** — P(1) as the 4-fold quadrature ⟨∫μ_s e^{−μ_s s}⟨e^{−μ_s L₂}⟩_HG ds⟩ with L₂ along the **deflected** exit direction, at τ=0.5; P(≥2)=1−P(0)−P(1) follows | MC within ~4σ of the exact quadrature | naive straight-path formula visibly off at τ=0.5 (shown in-figure) |
| **Regression tests** | Maxwell ∇·E and thin-slab Poisson checks added to the suite | broken variants asserted to fail |

## 3. Findings — what the audit itself got wrong first (kept, deliberately)

1. **"Energy conservation" (rung 3) was partly a tautology.** As coded,
   ballistic+forward+back+absorbed sums to 1 *by construction* (exhaustive
   partition). It still catches lost/double-counted photons, but it is
   bookkeeping, not physics. **Resolution:** added the non-trivial check —
   a purely absorbing slab's transmittance must equal the analytic
   ⟨e^{−μ_a d/cosθ}⟩ (`test_pure_absorber_transmittance_analytic`), which
   validates the absorption path-length integral independently.
2. **The audit's own naive Poisson P(2) formula was wrong physics** (it FAILed
   at 6σ, correctly!). ⟨(μ_sL)ⁿ/n!·e^{−μ_sL}⟩ along the *straight* path is
   exact only for n=0: the first scattering event changes the direction, hence
   the remaining in-slab path (deflected photons travel farther → more second
   scatters; MC P(2)=0.0067 vs naive 0.0056 at τ=0.1). **Resolution:** the
   exact deflection-coupled quadrature above; the straight-path P(1) used in
   rung 4 remains valid as a *thin-limit* statement with O(τ²) error (its
   measured residual, 0.0017 at τ=0.1, is exactly this physics).
3. **Two audit-tooling artifacts** (not physics): trapz cannot resolve the HG
   peak (p(1)≈95 at g=0.9) — normalization is analytically 1; and pointwise
   pdf-at-bin-center comparisons fail where p varies 10× within a bin — the
   CDF bin-integral is the correct comparison. Both corrected in the script.

## 4. Documented conventions (choices, not errors)

- **No k² radiometric prefactor** in the spectral sum (both the deterministic
  reference and the MC omit it identically); validated end-to-end against the
  paper's Linfoot anchors (S_ax 1.058 vs 1.057).
- **Intensity cut conventions** per figure (y-cut / x-cut / azimuthal average)
  — see `CONSISTENCY.md`.
- **Diffuse halo = ensemble mean** over trials (speckle lives in the per-trial
  SD, which the ≥10-trial standard records).
- **Debye + aplanatic assumptions** (high Fresnel number, sine condition) —
  valid for real objectives; boundaries documented in
  `direction_sampling_explained.md`.

**Verdict:** all field physics and transport statistics pass first-principles
checks with functioning controls; the two real weaknesses found were in the
*validation layer* (a tautological rung; a naive audit formula) and both are
fixed and regression-locked. Remaining known gaps are unchanged and tracked in
`ACCURACY.md`: diffusion/MCML cross-checks (rungs 5–6) and any
experiment/full-wave comparison.
