# Review guide — everything, start to finish (tick as you go)

*A single sequential walkthrough of the whole `mcdo` project with checkboxes.
Work top to bottom. Each item says **what to open**, **what "correct" looks
like**, and any **flag**. Catalog view (every artifact by category) lives in
`REVIEW_INDEX.md`; this guide is the ordered path. Numbers current 2026-07-07:
6 review PDFs, 38 tests, 13 package modules, 42 scripts.*

---

## Stage 0 — Setup & smoke test (5 min)

- [ ] **Environment**: runs on the `dev` conda env
      (`/opt/homebrew/Caskroom/miniforge/base/envs/dev/bin/python`).
- [ ] **Tests pass**: `python -m pytest tests/ -q` → **38 passed**. Each test is
      a named physical result; a failure = a real regression, not drift.
- [ ] **Lint clean**: `ruff check mcdo/ scripts/ tests/` → *All checks passed!*
      (style config in `pyproject.toml` — compact scientific style is deliberate).
- [ ] **Nothing else to install**: package imports via repo root on `sys.path`.

## Stage 1 — Orient: read these first, in order (30 min)

- [ ] `README.md` — project orientation + status.
- [ ] `docs/ACCURACY.md` — **the answer to "how do I know it's accurate"**: the
      full validation ladder (analytic / conservation / literature / convergence
      / first-principles) **and the honest gaps**. Read the gaps section.
- [ ] `docs/theory/AUDIT_FROM_SCRATCH.md` — the ground-up re-derivation of every
      module + the Maxwell/Helmholtz checks; note the **two validation-layer
      flaws it found and fixed** (honesty check).
- [ ] `docs/theory/CONSISTENCY.md` — does the flow serve the goal (scalar→vector
      gap now closed).
- [ ] `docs/QA_LOG.md` — the running Q&A thread; each row has a "verify-here".

## Stage 2 — Phase-by-phase (the science) — open each PDF, tick the checks

Read the compiled PDFs; they are the reviewable artifacts.

**Phase 1 — Romallosa 2003 replication** — `docs/review/01_romallosa/review_01.pdf`
- [ ] All 5 paper figures reproduced; S_ax = 1.058 (paper 1.057); FWHM 472.8 nm;
      zero rings 0.555 / 3.05 µm.
- [ ] **Spectral-window finding**: the paper integrates ω∈(0, 2ω_c); FWHM-only
      truncation loses 24% weight and fails the anchors. (Load-bearing — this is
      a paper subsection / possible separate Comment.)

**Phase 2 — NA + apodization** — `docs/review/02_na_apodization/review_02.pdf`
- [ ] Engine = analytics: RW = scalar Debye = Airy to 1e-4 at low NA.
- [ ] **Anisotropic thresholds** table (a single "NA threshold" is ill-posed).
- [ ] Gaussian apodization **extends** scalar validity (reverses the old report).

**Phase 3 — Annular (Babinet)** — `docs/review/03_annular/review_03.pdf`
- [ ] DOF(ε)/DOF(0) = 1/(1−ε²) exact at low NA, ~40% short at sinα=0.9.
- [ ] Thin annulus → Durnin J₀²; **vector-deformed at high NA** (0.163 vs 0.004).
- [ ] Sheppard–Wilson 1978 anchor to 0.8%.

**Phase 4 — Axicon / Bessel** — `docs/review/04_axicon/review_04.pdf`
- [ ] Focal segment; position-dependent J₀² scale.
- [ ] **Flag → now VERIFIED**: the 4–8% J₀² deviation is stationary-phase error,
      not vector — it shrinks ∝1/β (0.134→0.006 over β 5→2560), physical Debye
      ceiling at β≈160 (see `axicon_validity.png` in the PDF).

**Phase 5 — Pulsed × pupils (the headline science)** —
`docs/review/05_pulsed_pupils/review_05.pdf`
- [ ] **DOF extension is bandwidth-invariant** (44.35 cw → 44.33 at 1 fs, ε=0.99).
- [ ] Transverse ring contrast erodes; **S(τ) non-monotonic — now VERIFIED real**
      (smooth in τ, flat vs N_freq, present in y-cut/x-cut/full-vector).
- [ ] Spectral sampling + Jacobian figure (`spectral_sampling.png`).

**Phase 6a — Monte Carlo, clear limit** — `docs/review/06_monte_carlo/review_06.pdf`
- [ ] Clear-limit gate: MC → deterministic field, RMS 8e-4 at N=1e5.
- [ ] Per-config < 0.2%; vector MC both RW cuts 6e-4; launcher KS ≈ 1/√N.
- [ ] Pulsed wavelength-sampling MC ≡ deterministic Eq.10 (3–5e-4).
- [ ] Understand **why ~10³ photons suffice** (importance-sampled coherent
      quadrature) — QA_LOG #24.

**Phase 6b — Scattering** — `review_06.pdf` §9 + `verify_mc_scatter.png`,
`verify_scatter_born.png`
- [ ] Rungs 1–4 **PASS**: μ_s→0=clear; Beer–Lambert <0.001; energy=1 to 2e-16;
      **Born** (Poisson counts, thin halo vs independent single-scatter 0.3%).
- [ ] Physics sane: ballistic focus dims (below e^−τ), broadens ~5%, halo grows.
- [ ] Open: rungs 5–6 (diffusion, MCML) — tracked, not yet done.

## Stage 3 — First-principles audit (the "is it really right" tier)

- [ ] Open `output/00_overview/audit_first_principles.png`.
- [ ] Panel 1: scalar field satisfies **Helmholtz** at exactly k (FD floor);
      wrong-k control fails at 0.093. ✔ has teeth.
- [ ] Panel 2: vector field is **divergence-free (Maxwell)**; broken E_z factor
      (2→1) fails at 0.102. ✔ pins the kernels to Maxwell.
- [ ] Panel 4: HG sampling ≡ exact CDF; slab counts match **exact
      deflection-coupled** quadrature (the MC beat the audit's first formula).
- [ ] Cross-check: Simpson ≡ independent adaptive quadrature to 7e-11.

## Stage 4 — Code review (the implementation)

Read modules in dependency order; each has a full docstring + citations.
- [ ] `mcdo/config.py` — parameters, spectral power, ω-grid (0,2ω_c).
- [ ] `mcdo/rw_integrals.py` — I₀,I₁,I₂ (the engine); Simpson quadrature.
- [ ] `mcdo/debye.py`, `mcdo/annular.py`, `mcdo/apodization.py`,
      `mcdo/polarization.py`, `mcdo/linfoot.py`.
- [ ] `mcdo/montecarlo.py` — launcher (scalar + vector), coherent sum,
      wavelength MC, opt-in parallel.
- [ ] `mcdo/scatter.py` — HG sampling, MCML rotation, free-path slab march.
- [ ] `mcdo/focus_scatter.py` — 6b composition (ballistic core + diffuse halo).
- [ ] `mcdo/trials.py` — the ≥10-trial harness.
- [ ] `tests/` — each test asserts a fundamental result (open `test_optics.py`,
      `test_montecarlo.py`, `test_scatter.py`, `test_focus_scatter.py`,
      `test_trials.py`).

## Stage 5 — Reproducibility & data

- [ ] **Multi-trial standard**: every MC result is K≥10 seeds with per-trial
      data saved — `output/06_monte_carlo/trials/*.npz` (mean/std/sem/seeds).
- [ ] `profiles_vs_N.png` — the ±1σ band shrinks ∝1/√N.
- [ ] Regenerate any study from its `scripts/*.py` and confirm it reproduces.

## Stage 6 — Paper readiness (Paper 1: Phases 1–5)

- [ ] `paper/PAPER_PLAN.md` — read the verdict (**enough material, framed around
      the pulsed-annular headline**), figure plan, ISI journal targets
      (Opt. Express / JOSA A / PRA), and the gap list.
- [ ] Decide: proceed to draft after the literature novelty check confirms.

## Stage 7 — Literature (in progress)

- [ ] `docs/LITERATURE.md` — reading roadmap to mastery (Born & Wolf,
      Novotny–Hecht, Richards–Wolf, the **Saloma lineage**) + gap/future-
      directions analysis. ⚠ exact citations marked *to-verify*.
- [ ] `paper/literature/` — the deep verified sweep (**pending**: rate-limited;
      re-running when the API limit resets). Novelty verdicts land here.

## Sign-off

- [ ] I have run the tests (38 pass) and spot-checked at least Phases 1, 5, 6b.
- [ ] I understand what is validated vs the honest gaps (`ACCURACY.md`).
- [ ] I agree with the Paper-1 scope and target journal, **or** noted changes.
- [ ] Next actions I want: ______________________________________________

*Anything that fails a check → note it here and I'll fix it as a class, not just
the cited instance.*
