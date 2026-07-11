# How we know the simulation is accurate — the validation audit

"Accuracy" of a simulator is not one number; it is a **ladder of independent
checks, each against something we already know**. A result is trusted when it
sits between validated limits, is statistically converged, and its regression
test passes. Below is every check, its reference, our measured value, and where
to verify it. The honest gaps are listed last — read them.

All deviations are the *measured* discrepancy from the known reference.

## A. Analytic limits (a closed form exists — match it)
| check | reference | our deviation | where |
|---|---|---|---|
| low-NA transverse | Airy `[2J₁(v)/v]²` | < 5×10⁻³ | `test_optics`, review 02 |
| scalar Debye low-NA | Airy | < 5×10⁻³ | `test_optics` |
| thin annulus, low NA | Durnin `J₀²(v)` | < 0.05 | `test_optics`, review 03 |
| Babinet at ε=0 | full disk (identical) | < 1×10⁻¹² | `test_optics`, review 03 |
| Gaussian α_t→0 | uniform (identical) | < 1×10⁻⁹ | `test_optics` |
| spectral power half-width | FWHM = 4ln2/τ | < 1×10⁻⁹ | `test_optics` |
| ω-grid support | (0, 2ω_c) | < 1×10⁻⁶ | `test_optics` |
| axicon transverse | Durnin `J₀²` (SPA) | 0.134→0.006 as β 5→2560 (∝1/β) | `axicon_validity.png`, FLAGS |
| Linfoot criteria | identity 2Q−S=F | < 1×10⁻¹² | `test_optics` |

## B. Conservation laws / invariants (must hold regardless of the answer)
| check | reference | our value | where |
|---|---|---|---|
| MC photon accounting (6b) | ballistic+fwd+back+abs = 1 | dev 2×10⁻¹⁶ (*exhaustive partition — bookkeeping, not full physics; see B2*) | `test_focus_scatter`, `verify_mc_scatter.png` |
| absorption path integral (B2) | pure-absorber transmittance = ⟨e^{−μ_a d/cosθ}⟩ | < 0.002 | `test_focus_scatter` |
| Beer–Lambert ballistic | exp(−μ_s L) | 0.607/0.368/0.135/0.018 exact; focused < 0.001 | `test_scatter`, `test_focus_scatter` |
| HG mean cosine | ⟨cosθ⟩ = g | asserted | `test_scatter` |
| isotropic 2nd moment | ⟨μ_z²⟩ = 1/3 | asserted | `test_scatter` |
| scatter directions | unit norm | asserted | `test_scatter` |

## B★. First-principles (no reference implementation, no literature — pure Maxwell)
Each with a deliberately-broken control proving the check has teeth
(`audit_first_principles.png`, `docs/theory/AUDIT_FROM_SCRATCH.md`):
| check | result | broken control |
|---|---|---|
| Helmholtz (∇²+k²)U=0, scalar Debye field | 2.1×10⁻⁴ @ h=5 nm = FD floor, ∝h² | wrong k (1.05k) → 0.093 |
| Maxwell ∇·E=0, vector RW field (pins the kernels + E_z factor) | 1.5×10⁻⁴ @ h=5 nm | E_z factor 2→1 → 0.102 |
| Simpson vs independent adaptive quadrature (18 integrals) | 7.1×10⁻¹¹ | — |
| HG sampling vs exact CDF bin probabilities | within 3σ @ 4×10⁵ | — |
| exact deflection-coupled P(1), P(≥2) @ τ=0.5 (4-fold quadrature) | MC within 0.4σ / 4σ | naive straight-path P(1) off by 12σ (shown) |

## C. Published-literature benchmarks (independent groups)
| check | published | ours | where |
|---|---|---|---|
| Romallosa 2003 axial S | 1.057 | 1.058 | review 01 |
| Romallosa transverse FWHM | — | 472.8 nm | `test_optics`, review 01 |
| Romallosa zero rings | — | 0.555 / 3.05 µm | review 01 |
| Romallosa Figs 1–5 | — | all reproduced | review 01 |
| Sheppard–Wilson 1978 annular axial | Eq. 33 | 0.8% | review 03 |
| Tanaka paraxial apodization | — | closer than old report | review 02 |

## D. Internal consistency (the MC must reduce to the deterministic core)
| check | reference | our deviation | where |
|---|---|---|---|
| clear-limit gate (RMS) | `scalar_debye` | 8×10⁻⁴ @ N=10⁵ | `test_montecarlo`, review 06 |
| per-configuration | deterministic | < 0.2% (uniform 6e-4 … axicon 1.8e-3) | review 06 |
| vector MC, both RW cuts | `compute_integrals` | 6×10⁻⁴ | `test_montecarlo` |
| launcher angular density | Debye–Wolf integrand | KS 9×10⁻⁴ ≈ 1/√N | `test_montecarlo`, `verify_launcher.png` |
| pulsed λ-MC | deterministic Eq. 10 | 3–5×10⁻⁴ | `test_montecarlo`, `verify_mc_pulsed.png` |
| parallel ≡ serial | additive sum | 8.7×10⁻¹⁶ | `test_montecarlo` |
| scattering μ_s→0 | clear focus | recovered exactly | `test_focus_scatter`, `verify_mc_scatter.png` |

## E. Statistical convergence (every result carries an error bar)
Every MC experiment is run over **K≥10 seeds** with per-trial data saved
(`output/06_monte_carlo/trials/`). The ±1σ band shrinks ∝1/√N — e.g. the
transverse profile σ is 0.0058 / 0.0017 / 0.00054 at N=10³/10⁴/10⁵
(`profiles_vs_N.png`). A result is "good enough" when its SD is below the
tolerance that makes it decisive and the mean has stopped drifting.

## F. Regression (accuracy is locked, not a one-time claim)
**39 tests** (`python -m pytest tests/ -q`), each asserting a fundamental result
above — so any future change that degrades accuracy fails loudly.

## First-principles guarantee (not just curve-fitting)
The Monte Carlo is not a fit to the deterministic result — it is
importance-sampled quadrature of the **same** Debye–Wolf integral, with a
**provably unbiased** estimator, so N→∞ convergence is guaranteed before running
(the gate RMS only confirms the implementation). See
`docs/theory/direction_sampling_explained.md`.

---

## What is NOT yet validated (the honest gaps)
1. **Scattering middle regime — rung 4 now CLOSED, rungs 5–6 remain.**
   Rung 4 (single-scatter Born, `verify_scatter_born.png` + the exact
   deflection-coupled P(1) in `audit_first_principles.png`): Poisson counts
   match analytics (P0 < 0.001 everywhere; P1 < 0.002 thin; exact-quadrature
   P(1) at τ=0.5 within 0.4σ), and the thin halo matches an independent
   one-step computation to 0.3%. Rungs 5 & 6 (diffusion): PASS — the transport **similarity relation**
   (μ_s,g=0.9≡μ_s′,g=0) holds, MC→analytic diffusion slab T_d
   (`verify_scatter_diffusion.png`), and the isotropic point-source **diffusion
   Green’s function** μ_eff=√(3μ_aμ_tr) matches to 1.5–3% (first absorption
   test, `verify_scatter_mcml.png`). **The scattering ladder is fully closed
   (rungs 1–6).**
2. **No experiment / no independent full-wave solver.** Everything here is
   theory vs analytic-limit / vs published-theory / vs our own deterministic
   core. The gold-standard checks — against a measurement, or an independent
   **FDTD / Mie** computation for a known scatterer — have **not** been done.
3. **Modeling assumptions** (valid for real focusing, but assumptions): the
   **Debye** approximation (high Fresnel number) and the **aplanatic / Abbe
   sine** lens. They fail only at very low Fresnel number or sub-wavelength
   near-field — outside our regime — but they are assumed, not tested here.
4. **Incoherent halo = ensemble mean.** The diffuse halo is the trial-averaged
   intensity; single-realization speckle lives in the SD, not separately
   validated against a coherent-transport reference.

**Bottom line.** The deterministic core and the clear-limit MC (scalar +
vector + pulsed) are validated to analytic / machine / literature precision and
regression-locked. The scattering is validated at its known limits but not yet
through its middle regime, and nothing has been checked against experiment or an
independent full-wave method. Those are the next things that would raise
confidence further.
