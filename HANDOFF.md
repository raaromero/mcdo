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
**257 tests, ruff clean; the `refactor` push predates the current rebuild.** Paper-1 draft v0.1 compiles
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

## 6. Slide deck (added 2026-08-20)

The results deck is a **package artifact**, not a script that lives beside the
repo. It computes nothing: every figure is produced by a canonical script in
`scripts/`, and `mcdo/deck.py` only assembles them.

```
python -m mcdo.deck                 # -> output/deck/mcdo_results_deck.pptx
python run_all.py                   # regenerate every figure, then rebuild
python run_all.py --stale --list    # what is missing or out of date
python scripts/sanity_check.py      # 15 physics invariants (also run by pytest)

python -m mcdo.deck --list-stages   # the five review stages and their outputs
python run_all.py --stage 1         # regenerate only that stage's figures
python -m mcdo.deck --stage 1       # that stage's review deck
python scripts/make_review_folder.py --stage 1   # its figures, in slide order
```

Work is reviewed and merged **one stage at a time** — `docs/STAGES.md` holds the
workflow and the definition of done. `STAGES` lives in `mcdo/deck.py`, and
`stage_outputs()` derives each stage's figures and scripts from that stage's own
slides, so the listing cannot drift from the deck.

**Rules that keep it honest**

- Never hand-draw a figure that a `scripts/` file already produces. Find the
  script and re-run it. This has been the single biggest source of wasted work.
- Declare each figure in `mcdo.deck.FIGURES` as
  `key -> (path under output/, script that regenerates it)`. A missing figure
  makes the build print that command instead of degrading silently.
- `run_all.py` derives its work list from `FIGURES`, so declaring a figure in
  the deck automatically enrols it — the two cannot drift apart.
- Multi-panel figures call `mcdo.figio.save_panels`, which also writes each
  panel alone (panel letters stripped) so one plot can carry one slide.
- `mcdo.figio.trim_xlim` trims an axis to where the curves still carry signal;
  needed because converting optical to physical units leaves stale windows.
- `mcdo.components` is the single definition of focal intensity by component:
  `scalar` (|I0|²), `ex_only` (|I0|²+½|I2|²), `full` (|I0|²+|I2|²+2|I1|²).
  A single-azimuth slice (`y_cut`) is reproduction-only — Romallosa plots it,
  our own results do not.
- **Scalar theory means `mcdo.debye.scalar_debye`**, which has no (1±cosθ)
  kernel. `|I0|²` is the vector m=0 term and is *not* a scalar reference; using
  it silently understates the comparison.
- `mcdo/equations.py` renders the LaTeX in `deck.LX` to images so equations
  appear on the slide. What an equation *means* goes in the slide bullets
  (`deck.LX_CAPTION`), never burnt into the image.
- `save_panels` writes `<prefix>_panels.json` recording what each panel index
  holds, and deletes its own previous panels first. Changing a figure's layout
  renumbers its panels, and without this a slide keeps its index while silently
  showing a different plot — this bug has been caught three times.
- Atlas scripts take `--component {full,ex,scalar,ycut}` and write each choice
  to its own directory, so one output type never overwrites another.

**Presentation conventions** live in `docs/STANDARDS.md` and are enforced by
`tests/test_standards.py`: no code identifiers or "Phase N" in rendered text,
no "x-cut"/"y-cut" jargon, data lines at least 1.6 pt, no orphaned manifest
entries, every declared figure present on disk, slide and panel agreeing on the
setting they name, figures inside the slide, no picture/text overlap, no text
overrunning its box. `tests/test_physics.py` runs the sanity harness, so the
invariants fail the suite rather than waiting to be noticed in a figure.

**Branch note.** Section 0 rule 6 says commit only to `refactor`. The current
rebuild work sits on the orphan branch `rebuild` at the user's request, and is
**uncommitted** — confirm with the user before committing anywhere. `.gitignore`
now excludes `output/` (278 MB of regenerable figures) and the superseded
`slides_review/`, so a first commit is about 15 MB of source, docs and review
PDFs. `docs/gbp_mc_external_review.md` stays ignored and untracked: verify with
`git ls-files | grep -c gbp_mc_external` returning 0 after any `git add -A`.
