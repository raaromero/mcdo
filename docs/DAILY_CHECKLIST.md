# Daily checklist — what's set up & verified

*A glanceable inventory of everything built and its verification evidence.
Read it in a minute; it answers "what exists and do I trust it?" Distinct from
the 6-hourly cloud sweep (which hunts for *gaps*) — this is the positive
inventory. Update the date + any changed rows when you touch something.*

**Last verified: 2026-07-13** · repo `raaromero/mcdo` @ `refactor` (4f7a0df) ·
**40/40 tests pass** · gbp external review excluded (0 tracked) ✓

---

## Core engine & physics (mcdo package)
- [x] **Validation ladder rungs 1–6 closed** — continuity, Beer–Lambert,
  energy, single-scatter Born, diffusion similarity + slab, diffusion Green's
  function. *Evidence: `scripts/verify_scatter_*.py`, `docs/scattering_validation_plan.md`.*
- [x] **First-principles audit** — Helmholtz + ∇·E residuals at the FD floor,
  with deliberately-broken controls. *Evidence: `scripts/audit_first_principles.py`, `docs/theory/AUDIT_FROM_SCRATCH.md`.*
- [x] **40 regression tests pass** — *`pytest tests/` → 40 passed.*
- [x] **ruff clean, tree clean.**

## Paper 1 (pre-Monte-Carlo)
- [x] **Draft v0.1 compiles** tectonic-clean — *`paper/draft/main.pdf` (~9 pp).*
- [x] **Phases 1–5 results validated** — Romallosa replication (S_ax 1.058 vs
  1.057), NA/apodization thresholds, annular Babinet, axicon validity, pulsed ×
  structured (DOF spread ≤0.10%).
- [x] **Citations verified this pass** — Richards–Wolf 1959, Blanca–Saloma 1998,
  Monterola–Saloma 2001, McLeod 1954, Sheppard–Wilson 1978, Planchon–Betzig
  2011, Durnin 1987; **Horváth–Bor corrected** to PRE 63, 026601 (2001).
- [x] **Novelty sweep done** — no exact collision on the bandwidth-invariant DOF
  headline; closest prior art logged (AO 39,5244; Hayakawa BOE 2011).
- [ ] **8 submission-time TODOs remain** (not blockers): author list, Zenodo
  DOI, headline-figure re-render, 3 minor citation confirmations.
  *See `\todo{}` in `paper/draft/main.tex`.*

## Dashboards (self-contained, website-ready)
- [x] **`index.html` Focal Field Explorer** — live vector RW; **CW matches mcdo
  <1.6%, pulsed matches 0.01–0.03%** (after the spectral-prefactor fix).
  Engine-check card self-validates CW **and** pulsed rows on load.
- [x] **`mc.html` Monte Carlo Slab** — HG transport, animated trajectories,
  10-trial bands; Beer–Lambert within 3σ, energy conserved, ⟨cos⟩=0.90 at g=0.9.
- [x] **`focus_scatter.html` Focus Through Scatter** — coherent core + MC halo;
  MC ballistic matches quadrature (10.80% vs 10.80%).
- [x] **Spectral-convergence proof** in `index.html` — 11 nodes <0.1% error.

## NN-for-optics side track (local: `~/Downloads/nn-optics-ideas/`)
*Not in the repo — cloud sweep can't see this; check locally.*
- [x] **Feasibility ran** — descattering NN gains ×5.5–10.7 (v1); MC-denoiser
  honest negative (clear limit too cheap). *`01_descattering/`, `02_mc_denoiser/`.*
- [x] **Novelty logged** — `NOVELTY.md` (01 risk MED-HIGH, 03 HIGH; lineage
  citations confirmed).
- [x] **Pitches + proposal plan** — `PITCHES.md`, `PROPOSAL_PLAN.md`.
- [ ] **Before any adviser pitch**: multi-seed error bars; read AO 39,5244.

## Automation
- [x] **Cloud routine live** — "mcdo — outstanding-task sweep," every 6 h,
  read-only, reports cut-off/pending work with per-item ETA.
  *`trig_01CkRfPaqPkyd4m8dYfWAZX7` · claude.ai/code/routines/trig_01CkRfPaqPkyd4m8dYfWAZX7.*

## Standing guardrails (verify never regressed)
- [x] **gbp external review NEVER tracked** — `git ls-files | grep -c gbp_mc_external` = 0.
- [x] **No AI-attribution traces** in commits/docs (single orphan root history).
- [x] **Every MC experiment ≥10 trials** with saved per-trial data.

---
*Quick re-verify (paste to refresh this doc's top line):*
`cd ~/mcdo_dev && git log --oneline -1 && python -m pytest tests/ -q | tail -1 && git ls-files | grep -c gbp_mc_external`
