# Review index — work through these step by step

Everything produced, in review order. Each row: what it is, where, what to check.
✅ = validated/expected; ⚠ = has a flag to read first.

> **For a sequential, tickable walkthrough of the whole repo, use
> [`REVIEW_GUIDE.md`](REVIEW_GUIDE.md)** (Stage 0 → sign-off). This index is the
> flat catalog; the guide is the ordered path. Repo map: [`../README.md`](../README.md).

## Phase reviews (compiled PDFs — start here)
| # | open | check |
|---|------|-------|
| 1 | `docs/review/01_romallosa/review_01.pdf` | 5 paper figures reproduced; scorecard |
| 2 | `docs/review/02_na_apodization/review_02.pdf` | NA thresholds (anisotropic); Gaussian extends scalar; Tanaka closer |
| 3 | `docs/review/03_annular/review_03.pdf` | DOF=1/(1−ε²); Strehl=(1−ε²)²; Sheppard 1978 anchor |
| 4 | `docs/review/04_axicon/review_04.pdf` | focal segment; Durnin J₀² ⚠ (SPA-limited, not vector) |
| 5 | `docs/review/05_pulsed_pupils/review_05.pdf` | DOF pulse-invariant; ring contrast erodes ⚠ (non-monotonic) |
| 6 | `docs/review/06_monte_carlo/review_06.pdf` | MC clear-limit gate + launcher initialization proof (1st-principles) + sampling/N + voxel + vector + scatter-kernel; opens with the pipeline schematic |

**Overview schematic** of every model since Romallosa (pupil → focusing cone →
focal signature + the shared pipeline): `output/00_overview/models_schematic.png`
(also page 1 of review 06).

## Notebooks (narrative + figures)
`notebooks/01_romallosa2003.ipynb` … `05_pulsed_pupils.ipynb` (executed).

## Atlas — every configuration, Romallosa-style cards
- `output/atlas/{NA,gaussian,annular,axicon,pulsed}/*.png` — heat map + contours
  + transverse/axial cuts vs uniform-CW baseline. (NA 0.1–1.2, α_t 0–4,
  ε 0–0.99, β 0–40, τ cw–1 fs.)
- `output/atlas_components/full/{family}/*.png` — total intensity, by
  configuration (pass `--component ex` to vector_atlas.py for |Ex|² vs
  |Ex|²+|Ey|²+|Ez|² (the vector breakdown; axial profiles coincide on-axis).

## Monte Carlo (Phase 6a — clear limit)
| open | check |
|---|---|
| `output/06_monte_carlo/verify_mc_clear.png` | MC→deterministic; RMS→8e-4 at N=1e5; low-NA=Airy |
| `output/06_monte_carlo/verify_mc_configs.png` | per-config proof (uniform/Gaussian/annular/axicon all RMS<0.2%) |
| `output/06_monte_carlo/study_resolution.png` | N≈3000 for 1% RMS; voxel λ/4NA≈234 nm; null floor ∝1/N |
| `output/06_monte_carlo/study_sampling.png` | full sampling study: per-config N (axicon N(0.5%)≈10⁴); intensity-Nyquist dx=dy≤234 nm, dz≤681 nm; FWHM recovery vs voxel |
| `output/06_monte_carlo/profile_parallel.png` | parallel speedup + identical results (≈FP round-off) |
| `output/06_monte_carlo/verify_launcher.png` | initialization proof: θ-density=Debye-Wolf integrand (KS≈1/√N), φ uniform, recovered A(θ) flat/Gaussian, 2-D pupil maps, field gate |
| `output/06_monte_carlo/verify_launcher_intensity.png` | MC intensity vs expected: transverse+axial cuts (both inputs) on the deterministic curve; Gaussian 2-D gate (RMS 7e-4) |
| `output/06_monte_carlo/mc_variance.png` | per-point mean ±1σ over K=40 runs (transverse+axial, N=2k/20k); band shrinks ∝1/√N |
| `output/06_monte_carlo/verify_mc_pulsed.png` | per-photon wavelength-sampling MC ≡ deterministic Eq.10 (RMS 3–5e-4); pulse fills the CW zeros |
| `output/06_monte_carlo/photons_per_model.png` | N needed per model (1%/0.5% RMS): NA/Gaussian/annular all ~10³; axicon is the cost driver (β=20≈40k, β=40≈370k — phase cancellation) |
| `output/06_monte_carlo/profiles_vs_N.png` | profile mean ± 1σ (K=10 trials) for N=10³/10⁴/10⁵, transverse + axial — band tightens ∝1/√N (transverse σ 0.0058→0.0017→0.0005) |
| `output/06_monte_carlo/verify_mc_scatter.png` | **6b scattering** — ballistic core + diffuse halo through a slab; rungs PASS (μ_s→0=clear, Beer-Lambert <0.001, energy=1 to 2e-16); core dims & broadens, halo grows vs τ (K=10) |
| `output/06_monte_carlo/verify_scatter_born.png` | **rung 4 (Born)** — Poisson P0 exact <0.001, P1 thin <0.002, P(≥2)∝τ²; Born slope →⟨1/cosθ⟩; thin halo vs independent single-scatter 0.3% |
| `output/06_monte_carlo/verify_scatter_diffusion.png` | **rung 5 (diffusion)** — transport similarity μ_s,g=0.9≡μ_s',g=0 (|ΔT|→0.001); MC → analytic diffusion T_d (rel err 0.068→0.027) |
| `output/00_overview/audit_first_principles.png` | **from-scratch physics audit** — Helmholtz & Maxwell ∇·E at the FD floor with broken controls (wrong-k 0.093, E_z 2→1 0.102); Simpson vs adaptive quad 7e-11; HG vs exact CDF; exact deflection-coupled P(1) @τ=0.5 (naive formula off 12σ, MC on the exact value) |

**Pulsed / spectral diagnostics** (Phase 5):
`output/05_pulsed_pupils/spectral_sampling.png` — wavelength probability P(ω),
P(λ) (with |dω/dλ| Jacobian), and focus-vs-λ (position fixed, scale ∝ λ);
`output/05_pulsed_pupils/pulsed_S_diagnostic.png` — the S non-monotonicity is
real (smooth in τ, flat vs N_freq, present in y-cut/x-cut/full-vector).

## Multi-trial data (project standard: ≥10 seeds, saved with mean ± SD)
Every MC experiment — clear limit included — is run over **K=10 independent
trials** and the per-trial data saved (mean/std/sem/seeds), via
`mcdo.trials.run_trials`/`save_trials`. Regenerate with `scripts/run_mc_trials.py`;
data in `output/06_monte_carlo/trials/*.npz`. Summary (RMS unless noted, mean ± SD over 10):

| experiment | mean ± SD |
|---|---|
| clear field NA=0.8 | 0.00151 ± 0.00049 |
| uniform / Gaussian α_t2 / annular ε0.9 / axicon β20 | 0.0015 / 0.0018 / 0.0016 / 0.0057 (±~0.0005–0.0016) |
| vector y-cut / x-cut | 0.00117 / 0.00109 ± 0.0002 |
| launcher KS θ (uniform/Gaussian) | 0.0023 / 0.0026 |
| pulsed λ-MC (τ=2 fs) vs Eq.10 | 0.00067 ± 0.00024 |

## Tests (fundamental-result regression suite)
`tests/` — run `python -m pytest tests/ -q` (40 tests, ~25 s, all pass).
Each asserts a fundamental result:
- `test_optics.py` — low-NA→Airy, FWHM 472.8 nm, zero ring 0.555 μm, spectral
  FWHM, Babinet ε=0 exact, thin annulus→J₀², axicon J₀² deviation shrinks with β
  (SPA), **Maxwell: vector field divergence-free (broken E_z factor fails)**,
  Linfoot 2Q−S=F identity.
- `test_montecarlo.py` — clear-limit→Debye, convergence with N, sufficient N
  reaches 1% RMS, zeros clean at sufficient N, launcher samples the Debye-Wolf
  density (KS) + azimuth uniform, pulsed wavelength MC ≡ deterministic Eq.10
  (+ CW reduces to monochromatic), parallel≡serial, vector MC matches both RW cuts.
- `test_scatter.py` — ⟨cosθ⟩=g, isotropic ⟨μz²⟩=1/3, unit-norm, Beer-Lambert.
- `test_trials.py` — multi-trial harness reproducible + independent, summarize matches numpy, save/load round-trip.
- `test_focus_scatter.py` — 6b rungs: μ_s→0 recovers the focus, photon accounting exact, MC ballistic fraction = analytic Beer-Lambert, absorption partition, **thin-slab Poisson counts (rung 4)**, **diffusion similarity relation (rung 5)**, **MCML diffusion Green’s function μ_eff (rung 6)**, **pure-absorber transmittance = ⟨e^{−μ_a d/cosθ}⟩ (non-trivial energy check)**.

## Documents (the written record)
| open | what |
|---|---|
| `README.md` | project orientation + status |
| `docs/ACCURACY.md` | **how we know it's accurate** — the full validation audit (analytic / conservation / literature / convergence / first-principles) + the honest gaps |
| `docs/theory/AUDIT_FROM_SCRATCH.md` | ground-up re-derivation of every module + Maxwell/Helmholtz first-principles checks; two validation-layer flaws found & fixed |
| `docs/LITERATURE.md` | reading roadmap to mastery (**the one book: Novotny–Hecht ch. 1–4**; B&W as lookup; the Saloma school) + literature-gap & future-directions analysis |
| `docs/theory/FIELD_HISTORY.md` | the field before Romallosa — 7 conceptual moves (Maxwell→Debye→Richards–Wolf→Linfoot→ultrafast), each mapped to its `mcdo` module + timeline |
| `docs/KEY_RESULTS.md` | 26 numbered results |
| `docs/QA_LOG.md` | running list of your questions + answers + where to verify each |
| `docs/theory/direction_sampling_explained.md` | plain-language: why directions are sampled correctly without the focal intensity |
| `docs/theory/scattering_validation_plan.md` | how to validate 6b with no closed-form answer (known limits + convergence); what's already set up |
| `docs/theory/00–06 + FLAGS.md + CONSISTENCY.md` | equations + conventions per phase (06 §3 = first-principles launch); the 2 flags; the audit |
| `docs/report_errata.md` | review of your old progress-report PDF (the reversed NA-threshold) |

## Separate tasks (not part of our research)
| open | what |
|---|---|
| `docs/gbp_mc_external_review.md` | review of Arjonillo gbp-mc — C1 scattering-direction bug, C2 expit≠exp |

## The 3 candidate-publishable results (to highlight later)
1. Pulsed-annular DOF extension bandwidth-invariant while transverse contrast erodes (Phase 5).
2. Vector deformation of the Bessel beam at high NA (Phase 3; dev 0.16 vs 0.004 scalar).
3. Corrected anisotropic NA-thresholds (Phase 2; overturned the earlier conclusion).

## Two flags — now both VERIFIED (read `FLAGS.md`)
- **Axicon (Phase 4):** J₀² deviation is stationary-phase error, not vector.
  *Verified:* β-scan shows it shrinks 0.134→0.006 as β→2560 while MC=deterministic
  stays ≤0.019 (`output/04_axicon/axicon_validity.png`). Validity ceilings: N_theta
  resolves to β>2560; physical Debye (real f≈2mm) binds at β≈160.
- **Pulsed ring contrast (Phase 5):** Linfoot S non-monotonic at high ε (ring-washing).
  *Verified:* smooth in τ, flat vs N_freq, present in y-cut/x-cut/full-vector
  (`output/05_pulsed_pupils/pulsed_S_diagnostic.png`).
