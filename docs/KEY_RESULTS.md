# Key results — mcdo_dev (as of 2026-06-14)

One line each; details in `docs/theory/`, figures in `output/`, reviews in
`docs/review/NN_*/review_NN.pdf`. All at λc=750 nm, n=1.3 unless noted;
**input polarization is linear-x throughout** (circular variants in check 8).

## Phase 1 — Romallosa 2003 replication (`output/01_romallosa/`)

1. **All 5 paper figures reproduced**; anchors: S_ax=1.058 (paper 1.057),
   2-photon S(1fs)=0.970 (exactly the caption curve), FWHM 472.8 nm, zeros
   0.555/3.05 μm. Residuals ≤1% (S_tr) and ~3% (Fig 3 @1 fs), traced to
   undocumented paper conventions.
2. **Spectral window discovery**: the paper integrates the FULL positive
   spectrum ω∈(0,2ω_c); the quoted "483 nm–1.67 μm" is the FWHM, not the
   window. FWHM-only truncation loses 24% of spectral weight and fails all
   anchors (S_tr=1.020 vs 1.062).
3. **Paper errata found**: Fig 2 panel labels swapped; Fig 3 is a 1-D line
   integral; Linfoot arrays live in optical coordinates (the source of
   NA-flatness); Fig 1 axes are ±2.0/±6.0 μm.
4. **Old-mcdo bugs fixed** (its `cleanup` branch): spectral power √2 too
   narrow (double-squaring), FWHM-truncated default window, circular-pol
   default that cannot show the zero structure.

## Phase 2 — NA convergence & apodization (`output/02_na_apodization/`)

5. **Engine validated against analytics**: RW (both cuts) = scalar Debye =
   Airy to 1e-4 at X_NA=0.1 (zeros aligned on log scale).
6. **Vector thresholds are anisotropic** (uniform, FWHM vs scalar):

   | quantity | 1% | 5% |
   |---|---|---|
   | radial, linear-x x-cut (worst case) | X_NA 0.30 | 0.60 |
   | radial, circular input | 0.45 | 0.90 |
   | radial, linear-x y-cut | 0.85 | — |
   | axial (any pol) | 1.15 | — |

   A single "NA threshold" is ill-posed: it depends on polarization,
   measured cut, and direction.
7. **The anisotropy IS the longitudinal field**: E_z fills the x-cut zeros
   and elongates the spot along polarization; FWHM_x/FWHM_y → 1.4 at
   X_NA=1.2, tracking the E_z energy fraction.
8. **Gaussian apodization EXTENDS scalar validity** (x-cut 1%/5% at
   0.40/0.85 for α_t=4 vs 0.30/0.60 uniform; 12.6% vs 32.1% at sinα=0.9) —
   underfilling de-weights marginal rays. **Reverses the old progress
   report**, whose comparison used an invalid paraxial Gaussian reference
   (errata: `docs/report_errata.md`). Axial direction is the exception:
   α_t=4 crosses 1% earlier (0.60) via kernel reweighting.
9. **Apodization regression**: α_t→0 ≡ uniform at machine precision;
   FWHM_v 3.17→4.80 for α_t 0→4 with Airy-ring suppression.

## Phase 3 — annular apertures (`output/03_annular/`)

10. **Field-level Babinet validated**: ε=0 regression exact; DOF(ε)/DOF(0) =
    1/(1−ε²) to 3 digits at low NA (50.13 vs 50.25 @ ε=0.99), ~40% short at
    sinα=0.9 (30.4). Central lobe narrows (FWHM_v 3.05→2.06).
11. **Thin annulus → Durnin J₀²** at low NA (dev 0.004) but **vector-deformed**
    at high NA (dev 0.163, FWHM 2.06 vs scalar 2.25) — clean isolated vector
    effect. Strehl cost tracks (1−ε²)²; central-lobe energy 0.76→0.055.
11b. **Sheppard & Wilson 1978 anchor**: Gaussian-ring pupil, a=0.200 fitted from
    the focal envelope predicts the axial profile (Eq. 33, independent) to 0.8%.

## Phase 4 — axicon / Bessel (`output/04_axicon/`)

12. Conical pupil phase → focal segment with **position-dependent Bessel
    scale**: transverse @ predicted u(θ*) = J₀²(v·sinθ*/sinα) to 4–8% at three
    θ*. Axicon ≡ thin annulus at matched θ. **Flag**: the 4–8% is SPA error
    (low≈high NA), *not* vector — the annulus is the clean vector-Bessel probe.

## Phase 5 — pulsed × annular (`output/05_pulsed_pupils/`) — NEW SCIENCE

13. **Annular DOF extension is immune to few-cycle bandwidth**: DOF(ε)/DOF(0) =
    44.35(cw) → 44.33(1 fs) at ε=0.99, invariant to 3 digits.
14. **Transverse ring contrast erodes with pulsing** (Linfoot S→1.058 at 1 fs,
    all ε) — the Romallosa trade, now for structured pupils. Cross-check:
    ε=0 S(1fs)=1.056 = Phase-1 value. **Flag**: S(τ) non-monotonic at high ε
    (rings wash out at moderate τ, S<1, before 1-fs broadening, S>1).
15. **Net**: pulsing keeps the axial benefit of annular/Bessel pupils, costs
    transverse contrast → this pulsed structured-pupil field is the MC source.

## Phase 6a — Monte Carlo, clear limit (`output/06_monte_carlo/`)

16. **Coherent angular-spectrum MC reproduces the deterministic field**: photons
    = plane-wave components (direction + phase weight), coherent sum = Debye-Wolf
    integral. Clear-limit RMS vs scalar_debye → 0.0008 at N=10⁵; null floor ∝ 1/N;
    low-NA = Airy to 0.0015.
17. **Per-configuration proof** (RMS, N=10⁵): uniform 0.0006, Gaussian α_t=2
    0.0010, annular ε=0.5 0.0009, axicon β=20 0.0018 — the launcher correctly
    encodes apodization (density), obstruction (support), pupil phase (weight).
18. **Resolution rule**: dx,dy ≤ λ/(2NA), dz ≤ λ/(2n(1−cosα)); ¼-Nyquist gives
    dx=dy=117 nm, dz=341 nm at NA=0.8. Photons are vectors → traceable in time
    (phase = ωt). Pulsed: sample λ ~ |E(ω)|², same-λ coherent / different-λ
    incoherent (= Eq. 10).

19. **MC sampling study** (`study_sampling.png`, supersedes `study_resolution.png`):
    the two requirements are independent and don't trade off.
    (A) *Sufficient N* (statistical): RMS ∝ 1/√N, null floor ∝ 1/N. Per config,
    N(1%)/N(0.5%) RMS = uniform 3000/3000, Gaussian α_t=2 1000/3000,
    annular ε=0.9 3000/3000, axicon β=20 3000/**10⁴** (the structured-phase
    case needs the most photons to clean its zeros). (B) *Voxel size* (Nyquist on
    the **intensity**, twice the field frequency): dx=dy ≤ λ/(4·NA) = 234 nm,
    dz ≤ λ/(4·n(1−cosα)) = 681 nm; half those (117 nm / 341 nm) are the safe
    settings used elsewhere. FWHM recovery is flat below the Nyquist voxel and
    degrades above it (panel B/C). Scale N ∝ grid volume for full 3-D.
20. **Optional parallelism** (`coherent_intensity_parallel`, opt-in n_jobs):
    results identical to serial to FP round-off (8.7e-16 relative); speedup
    1.7×/2.9×/3.6× at 2/4/8 jobs (grid-pickling overhead → sub-linear).
21. **Launcher initialization certified** (`verify_launcher.png`,
    `verify_launcher_intensity.png`) — the pre-scattering prerequisite. (a)
    Direction: sampled θ follows the Debye-Wolf integrand density |A|√cosθ sinθ
    to the sampling limit (KS=0.0018≈1/√N, uniform & Gaussian); directions span
    the cone θ∈[0,α=38°]. (b) Azimuth: φ uniform (flatness 0.04). (c) Input: out
    drops the √cosθ sinθ geometry → recovered A(θ) flat (uniform) / Gaussian; 2-D
    pupil maps show the flat disk vs the Gaussian spot. (d) Intensity gate: MC
    matches deterministic Debye on transverse/axial cuts (through peak, zeros,
    side-lobes) and x–z slice, RMS 0.0007 both inputs. So scattering only
    removes/redirects photons from an already-correct ensemble (μ_s→0 exact).
22. **Photons needed per model** (`photons_per_model.png`): N for 1% RMS (scalar
    MC vs scalar Debye on an x–z slice, extrapolated ∝1/√N). Most models are
    cheap — NA 0.1–1.2: ~200–2100; Gaussian α_t 0→4: 0.9k→2.4k; annular ε 0→0.99:
    0.9k→1.3k. The **axicon is the cost driver**: β=0/5/10 ≈ 0.9k, but β=20 ≈ 40k
    and β=40 ≈ 370k — the oscillating conical phase makes the coherent sum largely
    cancel, so variance is set by how fast the pupil *phase* winds, not by NA.
23. **Multi-trial standard** (`mcdo.trials`, `output/06_monte_carlo/trials/`): every
    MC experiment runs **K=10 independent seeds** with per-trial data saved (mean ±
    SD/SEM + seeds), the clear limit included. Clear-field RMS 0.0015±0.0005;
    per-config 0.0015–0.0057; vector cuts 0.0011±0.0002; launcher KS 0.0023–0.0026;
    pulsed λ-MC 0.0007±0.0002. Reproducible error bars are the basis for judging the
    scattering runs (which have no closed-form answer).

## Phase 6b — focused beam through a scattering slab (`output/06_monte_carlo/`)

24. **First scattering run, validated** (`verify_mc_scatter.png`, K=10 trials).
    Slab z∈[−d,0] (d=20 µm, g=0.9), focus at the back face: **ballistic coherent
    core** (amplitude exp(−μ_s L/2), L=d/cosθ) + **diffuse incoherent halo**
    (forward-scattered photons). All three validation rungs pass — μ_s→0 recovers
    the clear focus; the MC ballistic fraction equals the analytic cone-averaged
    ⟨exp(−μ_s d/cosθ)⟩ to **<0.001**; energy (ballistic+forward+back+absorbed) is
    conserved to **2×10⁻¹⁶**. Physics: as τ=μ_s·d grows the ballistic focus dims
    (E_ball = 0.89/0.57/0.33/0.011 at τ=0.1/0.5/1/4, **below** the normal-incidence
    e⁻ᵗ because the cone-averaged path d/cosθ > d), forward-scatter dominates
    (g=0.9; backscatter ≤0.15), the diffuse halo grows (~16–22 µm RMS), and the
    ballistic core **broadens ~5%** (478→501 nm) as steep rays are preferentially
    scattered. The corrected, error-barred analogue of Arjonillo Fig 4.1.
25. **Rung 4 (single-scatter Born) + from-scratch physics audit** (2026-06-28,
    `verify_scatter_born.png`, `audit_first_principles.png`,
    `docs/theory/AUDIT_FROM_SCRATCH.md`). Poisson scatter counts: P0 = ⟨e^{−μ_sL}⟩
    to <0.001 at every τ; P1 thin-limit to <0.002; thin halo = independent
    one-step computation to 0.3%. First-principles: the scalar field satisfies
    **Helmholtz** and the vector field **∇·E=0 (Maxwell)** at the FD floor —
    broken controls (wrong k; E_z factor) fail at ~0.1; Simpson ≡ independent
    adaptive quadrature to 7×10⁻¹¹; HG sampling ≡ exact CDF. The audit also
    caught + fixed two validation-layer flaws: the rung-3 "energy" tautology
    (→ new pure-absorber ⟨e^{−μ_a d/cosθ}⟩ test) and the naive straight-path
    Poisson for n≥1 (→ exact deflection-coupled quadrature: MC P(1) @τ=0.5
    within 0.4σ of exact, 12σ from the naive formula — the simulator beat the
    audit's first formula).
26. **Rung 5 — diffusion thick limit** (`verify_scatter_diffusion.png`, K=10).
    The **transport similarity relation** — a pure diffusion-theory prediction —
    holds: a forward-peaked slab (μ_s, g=0.9) transmits identically to an
    isotropic one at matched reduced coefficient μ_s'=μ_s(1−g) (g=0), with
    |ΔT| shrinking 0.034→0.0019 as N=μ_s'·d goes 1→16 (thin→thick), and the
    radial spread matching to 0.7%. The MC transmittance converges to the
    analytic extrapolated-boundary diffusion result T_d=(1+z*)/(N+2z*)
    (relative error 0.068→0.027, decreasing). Scattering ladder now 5/6 closed;
    only the independent MCML cross-check (rung 6) remains.
27. **Rung 6 — diffusion Green's function (the MCML/Farrell-Patterson benchmark)**
    (`verify_scatter_mcml.png`, K=8). An isotropic point source in an infinite
    medium: the fluence decays as φ(r)∝exp(−μ_eff r)/r; the **fitted μ_eff matches
    √(3 μ_a μ_tr) to 1.5%/3.1%** in the diffusion regime (μ_a≤0.1, albedo≥0.9) —
    the **first check to exercise absorption**, in an independent geometry. The
    deviation grows to 13% at μ_a=0.5 (albedo 0.67) because **diffusion theory
    legitimately breaks down when μ_a is not ≪ μ_s'** — the MC is exact transport,
    diffusion is the approximation. Similarity holds again (g=0.9≡g=0, 4%).
    **The scattering validation ladder is now fully closed (rungs 1–6).** Remaining
    project gap: an experiment / independent full-wave (FDTD/Mie) comparison.

## Configuration atlas (`output/atlas/{NA,gaussian,annular,axicon,pulsed}/`)

Individual Romallosa-style card per configuration (2-D heat map + contour lines
+ transverse/axial cross-sections vs the uniform-CW baseline): NA 0.1–1.2,
α_t 0–4, ε 0–0.99, β 0–40, τ cw–1 fs. The growing visual record.

## Pipeline status

| phase | status |
|---|---|
| 01 Romallosa | ✅ validated (notebook 01 executed) |
| 02 NA + apodization | ✅ checks 1–8, Tanaka closer, corrected thresholds |
| 03 annular (Babinet) | ✅ verified + energy-cost + Sheppard anchor |
| 04 axicon/Bessel | ✅ verified (SPA-limited flag) |
| 05 pulsed × pupils | ✅ verified (new science) |
| 06a MC clear limit | ✅ validated globally + per configuration |
| 06b MC scattering | next — clear-limit gate passed |

Each phase: `output/NN/`, `docs/theory/NN`, `docs/review/NN/review_NN.pdf`.
Atlas: `output/atlas/`. Notebooks 01–05 executed.
