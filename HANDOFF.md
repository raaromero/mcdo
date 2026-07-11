# HANDOFF — read this fully before touching anything

Notes for anyone (or any automation) picking this project up. The rules below
encode hard-won conventions; deviating *will* cause rework. When unsure,
re-read `README.md` → `docs/REVIEW_GUIDE.md` → `docs/ACCURACY.md`, then ask
rather than guess.

---

## 0. THE HARD RULES (never violate)

1. **Every Monte-Carlo experiment runs ≥10 independent trials and SAVES the
   per-trial data** (mean/std/sem/seeds), *including no-scattering ones*. Use
   `mcdo.trials.run_trials` + `save_trials` → `output/.../trials/*.npz`.
2. **NEVER commit or push `docs/gbp_mc_external_review.md`.** It is git-ignored
   on purpose — a critique of a *named* colleague's code, and this repo is
   **PUBLIC**. Do not remove it from `.gitignore`. After any `git add -A`,
   verify: `git ls-files | grep -c gbp_mc_external` → must be **0**.
3. **Do not import any concepts from the external `gbp-mc` code** into the core
   `mcdo` physics. Keep everything in the project's own Richards–Wolf /
   Debye–Wolf framework.
4. **Review happens via compiled PDFs.** For any phase, the deliverable is
   `docs/review/NN/review_NN.pdf` (built from `review_NN.tex` with `tectonic`).
   Keep plots legible at PDF size (large fonts, no speckly 2-D histograms).
5. **2-D field slices use BOTH a heat map AND Romallosa-style iso-value contour
   lines.**
6. **Commit only to the `refactor` branch** of the public `mcdo` remote
   (`origin`). Never main. Plain commit messages — no automated trailers.
7. **Validation-first / honesty ethos.** Never overstate. Report deviations
   with numbers. If a check fails, say so. When a flaw is found (even in the
   validation layer itself), fix it and *log it* — see
   `docs/theory/AUDIT_FROM_SCRATCH.md` for the standard. Never fabricate
   citations (see §5).
8. **Generalize, don't piecemeal.** A flagged problem is a whole *class*; fix
   the class in one pass, not just the cited instance.

## 1. Environment (exact)

- **Python:** `/opt/homebrew/Caskroom/miniforge/base/envs/dev/bin/python`
  (conda env `dev`, Python 3.11). Has numpy(2.x), scipy, matplotlib, ruff.
- **NumPy 2.x:** use `np.trapezoid`, NOT `np.trapz` (removed). Guard:
  `_TRAPZ = np.trapezoid if hasattr(np,'trapezoid') else np.trapz`.
- **Known env quirk:** a shell hook on this machine sometimes swallows command
  stdout (tools appear to print nothing). Commands still RUN. Workaround:
  redirect to a file (`ruff … > /tmp/x 2>&1`) and read the file, or rely on
  exit codes. Fix: `brew reinstall node`.
- **Lint:** `ruff check mcdo/ scripts/ tests/` must be clean. Style config in
  `pyproject.toml` deliberately ignores E702/E741/E401/E731/E402/E501 — the
  compact scientific style (`a; b`, `I`=intensity) is intentional; do not
  "fix" it. Real issues (F401/F841/undefined) still flag — fix those.
- **`N_theta` must be ODD** (Simpson rule asserts it).

## 2. Commands you will use

```bash
PY=/opt/homebrew/Caskroom/miniforge/base/envs/dev/bin/python
$PY -m pytest tests/ -q            # MUST stay green (currently 40 passed)
$PY -m ruff check mcdo/ scripts/ tests/   # MUST stay clean
$PY scripts/<name>.py              # run a study (many are 1–5 min; background them)
cd docs/review/NN && tectonic review_NN.tex   # rebuild a review PDF
# commit:
git add -A && git ls-files | grep -c gbp_mc_external   # MUST print 0
git commit -q -m "…" -m "…"
git push origin refactor
```
Run tests **before and after** any change to `mcdo/`. Long scripts: launch in
background and poll the output file.

## 3. Physics you must not get wrong

- **Ballistic (coherent) core attenuates in AMPLITUDE** as `exp(−μ_s L/2)`
  (L = d/cosθ), giving Beer–Lambert `exp(−μ_s L)` in intensity. Do **NOT**
  implement scattering by *killing* photons and coherently summing survivors —
  that double-attenuates the intensity. Ballistic core = deterministic
  amplitude attenuation; the MC stochasticity is for the **incoherent** diffuse
  halo. (See `mcdo/focus_scatter.py`.)
- **The launcher is correct by first principles** (importance-sampled
  Debye–Wolf quadrature; provably unbiased) — validated by KS + the clear-limit
  gate + the Maxwell/Helmholtz audit. Don't "improve" the sampling density
  without checking the gate still passes.
- **Spectral window:** the pulsed sum integrates ω∈(0, 2ω_c) (full positive
  spectrum), not the FWHM band.
- **Clear-limit pulsed:** use the deterministic spectral sum (exact, cheap);
  per-photon λ-sampling (`mc_pulsed_intensity`) is only *needed* once
  scattering makes μ_s(λ) couple λ to the path.

## 4. Current state (2026-07-08) & what's next

**Done & validated:** Phases 1–5 (deterministic, in review PDFs 01–05); 6a
(clear-limit MC scalar+vector+pulsed launcher); **6b scattering — the ENTIRE
validation ladder rungs 1–6 CLOSED** (continuity, Beer–Lambert, energy,
single-scatter Born, diffusion slab + similarity, and the
MCML/Farrell-Patterson diffusion Green's function with absorption).
First-principles audit (Maxwell ∇·E + Helmholtz with broken controls).
**40 tests, ruff clean, pushed to `refactor`.** Paper-1 draft v0.1 compiles
(`paper/draft/main.pdf`); headline robustness ≤0.10% across NA 0.6–1.0.

**Next, in priority order:**
1. **Paper 1 to submission** — plan + gap list in `paper/PAPER_PLAN.md`;
   verify all TODO-marked citations; publication figure pass; journal template.
2. **Verify the literature** in `paper/literature/LITERATURE_SWEEP.md` —
   ESPECIALLY confirm **Hayakawa, Potma & Venugopalan, Biomed. Opt. Express 2,
   278 (2011)** (the key prior art — a vector focused-beam MC in tissue) and
   the Bessel-DOF numbers.
3. **The one remaining validation gap: experiment or independent full-wave
   (FDTD / Mie).** A Mie spot-check for one sphere is the cheapest first step.

**Honest open gaps** (do not paper over): no experiment and no independent
full-wave comparison; Debye + aplanatic assumptions. Tracked in
`docs/ACCURACY.md`.

## 5. Docs map (where the truth lives)

- `README.md` — repo map. `docs/REVIEW_GUIDE.md` — start-to-finish checklist.
- `docs/ACCURACY.md` — the validation audit + honest gaps.
- `docs/theory/AUDIT_FROM_SCRATCH.md` — module-by-module re-derivation + the
  two validation-layer flaws found & fixed.
- `docs/QA_LOG.md` — running Q&A + verify-here pointers (append to it).
- `docs/KEY_RESULTS.md` — numbered results. `docs/theory/FLAGS.md` — the 2
  (verified) flags. `docs/theory/scattering_validation_plan.md` — the ladder.
- `docs/theory/FIELD_HISTORY.md` — how the field was built (pre-2003 pedigree).
- `docs/LITERATURE.md` — reading roadmap (citations marked *to-verify*).
- `paper/` — Paper-1 workspace + the literature sweep.

---
*If you change any hard rule above, it must be because the project owner
explicitly asked — not an inference. Keep the tests green and the branch
honest.*
