# Validating the scattering MC when there is no closed-form answer

*Pre-6b plan: how we will know the scattering result is correct and "good
enough" even though — unlike the clear limit — there is no deterministic field
to compare against.*

## The problem
In the clear limit we validate against the exact Debye–Wolf field (RMS < 0.1%).
With scattering, the focal field is exactly what the MC is *for*: there is no
closed form for the general case, so "matches the expected result" is no longer
available as the test. Validation instead stands on two legs — **known limits**
and **statistical convergence**.

## Forward expectation (what we expect to see)
A focused beam through a slab of scattering strength μ_s (optical depth
τ = μ_s·d) splits into two parts:
- a **ballistic / coherent core** — the *same* Richards–Wolf focal pattern, its
  peak attenuated by Beer–Lambert exp(−μ_s L) in intensity (amplitude
  exp(−μ_s L/2)); the *shape* is unchanged;
- a **diffuse / incoherent halo** — a broad background carrying the scattered
  energy (1 − exp(−μ_s L)), widening with τ.

As τ → 0 the core → the clear field and the halo → 0; as τ grows the core decays
exponentially while the halo dominates (the focus washes out). The core/halo
contrast ∝ exp(−μ_s L)/(1 − exp(−μ_s L)) is the quantity we plot against
scattering depth. These are *quantitative* expectations, so a deviation
flags a bug.

## Validation ladder — every rung is something we DO know
1. **Continuity (μ_s → 0).** Must recover the clear-limit Debye field (already
   validated to < 0.1%). The single most important gate.
2. **Beer–Lambert ballistic.** The unscattered fraction / coherent-core peak must
   follow exp(−μ_s L) (the kernel already gives 0.607/0.368/0.135/0.018 =
   exp(−μ_s) exactly).
3. **Energy conservation.** launched = ballistic + scattered + absorbed, to ~1/√N.
   A hard invariant, independent of the field.
4. **Single scattering (thin, τ ≪ 1).** The first-order halo has an analytic
   first-Born form ∝ μ_s × phase function — compare directly.
5. **Diffusion (thick, many events).** The diffuse fluence → the analytic
   diffusion-equation solution (slab transmittance/reflectance; van de Hulst /
   MCML benchmark numbers).
6. **Cross-method.** The incoherent part, where coherence is irrelevant, matches
   an independent transport solver (e.g. MCML) on a benchmark slab.
7. **Invariants.** phase-function norm ∫p dΩ = 1, ⟨cosθ⟩ = g (done), reciprocity,
   slab symmetry.

The unknown middle regime is then trustworthy by interpolation between validated
limits.

## "Good enough" criterion (the answer to "how do I know?")
For the quantity of interest Q — e.g. core/halo contrast, axial FWHM, or on-axis
peak vs μ_s:
- run K independent seeds → report Q = mean ± SD (the `mc_variance.png` method);
- increase N until the SD is below the tolerance Q needs to be *decisive*
  (SD ∝ 1/√N) **and** the mean has stopped drifting;
- confirm Q is insensitive to the free-path step and voxel size (numerical
  convergence);
- confirm the limit rungs (at least 1–3) pass for the same configuration.

Q is "good enough" when it is **converged within its statistical error** *and*
the **known-limit checks pass** — not when it matches a closed form (there isn't
one). This is the standard discipline for any MC whose answer is unknown a priori.

## What is already set up (inventory)
| piece | status |
|---|---|
| photon launcher (scalar + vector), correct initialization | ✓ validated (clear gate, KS, field RMS) |
| clear-limit reference (the μ_s→0 target) | ✓ Debye–Wolf, RMS < 0.1% |
| scatter kernel: HG sampling, MCML local-frame rotation, free-path march, Beer–Lambert | ✓ validated in isolation (⟨cosθ⟩=g, ⟨μz²⟩=1/3, exp(−μ_s L)) |
| wavelength sampling (for λ-dependent μ_s) | ✓ `mc_pulsed_intensity` ≡ Eq. 10 |
| coherent accumulation (+ optional parallel) | ✓ |
| sampling / photon budgets quantified | ✓ |
| **composition**: launcher → slab march → coherent core + incoherent halo | ✓ `mcdo/focus_scatter.py` (slab z∈[−d,0], focus at back face) |
| **ballistic/diffuse split** (amplitude exp(−μ_s L/2) core + incoherent halo) | ✓ implemented + tested |
| **scattering validation harness** rungs 1–3 (continuity, Beer–Lambert, energy) | ✓ PASS (`verify_mc_scatter.png`, K=10) — *rung 3 as coded is exhaustive-partition bookkeeping; the non-trivial energy check is the pure-absorber transmittance test* |
| **rung 4 — single-scatter Born** | ✓ PASS (`verify_scatter_born.png`): P0 exact <0.001 all τ; P1 thin-limit <0.002; Born slope E_scat/τ→⟨1/cosθ⟩; halo vs independent one-step 0.3%; exact deflection-coupled P(1) @τ=0.5 within 0.4σ (`audit_first_principles.png`) |
| **rung 5 — diffusion thick limit** | ✓ PASS (`verify_scatter_diffusion.png`): transport **similarity relation** (μ_s,g=0.9 ≡ μ_s',g=0) |ΔT|→0.001 for N≥8; MC → analytic diffusion transmittance (rel err 0.068→0.027, decreasing); radial spread matches to 0.7% |
| **rung 6 — MCML/Farrell-Patterson diffusion Green's function** | ✓ PASS (`verify_scatter_mcml.png`): isotropic point-source fluence φ(r)∝exp(−μ_eff r)/r; fitted μ_eff = √(3μ_aμ_tr) to 1.5–3.1% in the diffusion regime (first **absorption** test); correctly deviates at high μ_a (diffusion breakdown); similarity again 4% |

**Status (2026-07-08). The scattering validation ladder is FULLY CLOSED (rungs
1–6).** All K≥8–10 trials with per-trial data saved. The from-scratch audit
(`docs/theory/AUDIT_FROM_SCRATCH.md`) additionally pinned the field physics to
Maxwell directly (Helmholtz + ∇·E at the FD floor with broken controls) and
exposed + fixed two validation-layer weaknesses (rung-3 tautology; naive
straight-path Poisson). **Only remaining project gap: an experiment or an
independent full-wave (FDTD / Mie) comparison** — the gold-standard check that no
part of this simulator has yet faced (tracked in `ACCURACY.md`).
