# mcdo — Monte Carlo Diffraction Optics

A validated toolkit for **high-NA vector focusing + few-cycle pulses +
structured pupils + Monte-Carlo transport through scattering media** — built
bottom-up and checked phase by phase against analytics, published literature,
and (now) first-principles Maxwell/Helmholtz residuals before each layer is
reused. The end goal: a *validated* Monte-Carlo simulator of tightly focused
optical pulses, shaped by annular/axicon pupils, propagating through turbid
media — the Saloma-lineage problem, generalized. No single existing tool spans
all four axes.

Clean rebuild of the older `~/Projects/Research/mcdo` (its errors are documented
and fixed). Pushed to **github.com/raaromero/mcdo**, branch `refactor`.

> **New here? Start with [`docs/REVIEW_GUIDE.md`](docs/REVIEW_GUIDE.md)** — a
> single start-to-finish checklist through the whole repo. For "how do I know
> it's accurate," read [`docs/ACCURACY.md`](docs/ACCURACY.md).
>
> **Picking this project up (or automating against it)? Read
> [`HANDOFF.md`](HANDOFF.md) first** — the hard rules and conventions
> (multi-trial standard, never-push-the-external-review, PDF review workflow,
> the ballistic-amplitude physics) so you don't break things.

## Status

| # | Phase | Checkpoint | Status |
|---|-------|-----------|--------|
| 1 | Romallosa 2003 replication (RW + pulse engine) | 5 paper figures + Linfoot values | ✅ |
| 2 | Apodization + scalar Debye / NA convergence | Airy + Tanaka analytics; anisotropic NA thresholds | ✅ |
| 3 | Annular apertures (field-level Babinet) | DOF=1/(1−ε²); Strehl=(1−ε²)²; Sheppard 1978 | ✅ |
| 4 | Axicon / Bessel beams (conical pupil phase) | Durnin J₀²; SPA error ∝1/β (verified) | ✅ |
| 5 | Pulsed × structured pupils (new science) | DOF pulse-invariant; ring contrast (verified) | ✅ |
| 6a | Monte Carlo, clear limit (scalar + vector + pulsed launcher) | μ_s→0 = Richards–Wolf field (RMS 8e-4) | ✅ |
| 6b | Monte Carlo, scattering (ballistic core + diffuse halo) | rungs 1–4 pass (continuity, Beer–Lambert, energy, Born) | ✅ rungs 1–4; 5–6 next |

**38 tests pass** (`pytest tests/ -q`); **ruff clean**; every MC result is
**K≥10 trials with saved per-trial data** (mean ± SD).

## Repository map

```
mcdo/                       the package (13 modules, full docstrings + citations)
  config.py                 SimConfig: parameters, spectral grid/weights, k(ω)
  rw_integrals.py           Richards–Wolf I₀,I₁,I₂ (the engine); Simpson quadrature
  debye.py                  scalar Debye integral + Airy analytics
  apodization.py            A(θ): uniform / gaussian / gaussian_ring / axicon
  annular.py                annular apertures via field-level Babinet
  polarization.py           linear-x cuts (y/x) + circular / azimuthal-average
  intensity.py              CW + pulsed (Eq. 10) intensity on (r,z) grids
  linfoot.py                Fidelity F, Structural content S, Correlation Q
  montecarlo.py             photon launcher (scalar + vector), coherent sum,
                            wavelength-sampling MC, opt-in parallel
  scatter.py                Henyey–Greenstein sampling, MCML rotation, slab march
  focus_scatter.py          Phase-6b: focused beam → ballistic core + diffuse halo
  trials.py                 multi-trial harness (≥10 seeds, save mean/std/sem)

scripts/                    42 scripts — one per figure / verification / study
                            (verify_*, study_*, make_*, audit_*; the source of truth)
tests/                      38 tests, each asserting a fundamental physical result
notebooks/                  narrative runners (01–05)

docs/
  REVIEW_GUIDE.md           ← start here: full start-to-finish review checklist
  REVIEW_INDEX.md           catalog of every artifact by category
  ACCURACY.md               the validation audit (how we know it's accurate) + gaps
  QA_LOG.md                 running Q&A, each with a "verify-here" pointer
  KEY_RESULTS.md            every numbered result, one line each
  LITERATURE.md             reading roadmap to mastery + gap/future analysis
  report_errata.md          review of the old progress-report PDF
  gbp_mc_external_review.md  (git-ignored; separate task — not in the public repo)
  theory/
    00–06_*.md              equations + validated conventions, per phase
    FLAGS.md                the two flags — both now VERIFIED
    CONSISTENCY.md          does the flow serve the goal (scalar→vector closed)
    AUDIT_FROM_SCRATCH.md   ground-up re-derivation + Maxwell/Helmholtz checks
    scattering_validation_plan.md   the 6b validation ladder (rungs 1–6)
    direction_sampling_explained.md why the launch is correct (first principles)
  review/NN/review_NN.pdf   compiled visual review per phase (tectonic) — 6 PDFs

output/
  00_overview/              pipeline schematic + first-principles audit figure
  01_romallosa/ … 05_pulsed_pupils/   figures per phase
  06_monte_carlo/           MC figures + trials/*.npz (the saved per-trial data)
  atlas/, atlas_components/ configuration atlas (every pupil, Romallosa-style)

paper/
  PAPER_PLAN.md             Paper-1 readiness verdict + figure plan + ISI targets
  literature/               deep verified literature sweep (in progress)
  figures/ draft/ notes/    manuscript workspace
```

## How to run

```bash
PY=/opt/homebrew/Caskroom/miniforge/base/envs/dev/bin/python
$PY -m pytest tests/ -q                 # 38 pass
$PY scripts/verify_mc_scatter.py        # e.g. the Phase-6b scattering run
cd docs/review/06_monte_carlo && tectonic review_06.tex   # rebuild a review PDF
```

## Headline physics

- **Spectral window (Phase 1):** Romallosa Eq. 10 integrates the *full positive
  spectrum* ω∈(0,2ω_c), not the FWHM band the text implies (that loses 24% of
  the weight and fails every Linfoot anchor).
- **Anisotropic vector thresholds (Phase 2):** a single "NA threshold" is
  ill-posed — it depends on polarization, cut, and direction; the deviation *is*
  the longitudinal E_z. Gaussian illumination *extends* scalar validity.
- **Annular (Phase 3):** DOF = 1/(1−ε²) (paraxial); thin annulus → Durnin J₀²
  with a genuine high-NA vector deformation of the Bessel core.
- **Axicon (Phase 4):** conical phase → focal segment; the J₀² deviation is
  **stationary-phase error ∝1/β** (verified: 0.134→0.006 over β 5→2560).
- **Pulsed × annular (Phase 5, new science):** the annular DOF extension is
  **immune to few-cycle bandwidth** (44.35→44.33 cw→1 fs), while transverse ring
  contrast erodes — the Romallosa trade, for structured pupils.
- **Scattering (Phase 6b):** ballistic coherent core (Beer–Lambert amplitude)
  + diffuse incoherent halo; validated at μ_s→0, Beer–Lambert, energy, and the
  single-scatter Born limit; the ballistic focus dims and broadens ~5% with τ.

## How we know it's right (the short version)

Analytic limits (Airy/Durnin/Babinet, to machine precision) · conservation laws
· published benchmarks (Romallosa, Sheppard) · internal consistency (MC =
deterministic) · statistical convergence (∝1/√N over ≥10 trials) · **and
first-principles Maxwell ∇·E = 0 + Helmholtz residuals with deliberately-broken
controls** — full audit in `docs/ACCURACY.md` and
`docs/theory/AUDIT_FROM_SCRATCH.md`. Honest open gaps: scattering rungs 5–6
(diffusion, MCML) and any experiment / full-wave comparison.
