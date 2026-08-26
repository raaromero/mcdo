# Paper 1 plan — the pre-Monte-Carlo (deterministic) paper

*Scope: Phases 1–5 (everything before the MC code). Assessment date 2026-07-07.*

## Is there enough material? YES — for one solid full-length paper.

**Comfortably enough volume** (≈7 figures, 3 tables, all validated + regression-
locked), **provided it is framed around Phase 5 as the headline** with Phases
2–4 as supporting results, and provided the novelty check (literature sweep in
`paper/literature/`) confirms no prior pulsed-annular work. Realistic target:
**JOSA A / Optics Express / Phys. Rev. A** — a rigorous theory/simulation paper.
Not a Nature-Photonics-class paper (no experiment, known-physics regime); don't
frame it as one.

### The headline result (the paper's spine)
**Few-cycle bandwidth does not degrade the annular depth-of-focus extension
(DOF(ε)/DOF(0) invariant to 3 digits cw→1 fs), while the transverse Bessel ring
structure erodes non-monotonically in pulse width** — with the ring/core
decomposition explaining the non-monotonicity, and all of it at high NA with
the full vector field. Nobody appears to have combined few-cycle pulses ×
annular/conical pupils × high-NA vector focusing (verify via lit sweep).

### Supporting results (sections, not the headline)
1. **Anisotropic scalar-validity thresholds** (Phase 2): a single "NA threshold"
   is ill-posed — it depends on polarization, cut, and direction (table);
   Gaussian apodization *extends* scalar validity. (Corrects a prior report.)
2. **Annular high-NA deviations** (Phase 3): DOF=1/(1−ε²) exact paraxially,
   ~40% short at sinα=0.9; thin-annulus Bessel core vector-deformed (0.163 vs
   0.004) — the clean isolated vector effect.
3. **Axicon validity map** (Phase 4): position-dependent Bessel scale; the J₀²
   deviation is stationary-phase error ∝1/β (0.134→0.006 over β 5→2560), with
   the physical (Debye) β-ceiling — a practical validity chart.
4. **Methods rigor** (Phase 1 + audit): full Romallosa replication including the
   **spectral-window finding** (the paper integrates ω∈(0,2ω_c); FWHM-only
   truncation fails all anchors — worth a short subsection or appendix; possibly
   its own Comment/erratum note to PRA separately).

### What "paper ready" still needs (gap list)
- [x] Literature positioning vs the sweep results — `literature/LITERATURE_SWEEP.md`
      (10 verified claims; novelty verdicts; Hayakawa 2011 = Paper-2 prior art,
      Paper-1 headline unthreatened). Final targeted search before submission.
- [x] Robustness map — **done, stronger than hoped**: DOF-ratio cw→1 fs spread
      ≤ **0.10%** across ε=0.5–0.99 × NA=0.6/0.8/1.0
      (`output/05_pulsed_pupils/paper_robustness.png` + `.npz`,
      `scripts/study_paper_robustness.py`).
- [x] Draft v0.1 written & compiling — `draft/main.tex` → `main.pdf` (tectonic):
      abstract, intro, theory/methods (incl. first-principles validation ¶),
      4 results sections, prior-work, discussion, spectral-window appendix,
      bibliography with [V]/TODO-verify flags.
- [ ] Verify all TODO-marked citations (rate-limited sweep leads) + final
      targeted novelty search ("pulsed annular depth of focus").
- [ ] Publication-quality figure pass (re-render Fig. 1 headline panel; unify
      fonts/sizes, letter panels).
- [ ] Decide the Romallosa-errata handling (currently Appendix A; alternative:
      separate short Comment to PRA).
- [ ] Author list/affiliations; port to journal template; Zenodo DOI for code.

### Figure plan (mostly existing)
| # | content | source |
|---|---|---|
| 1 | system + pipeline schematic | `output/00_overview/models_schematic.png` |
| 2 | validation panel (Airy/Durnin/Romallosa anchors) | phase 1–2 outputs |
| 3 | anisotropic thresholds + apodization extension | `02_na_apodization/` |
| 4 | annular DOF + vector Bessel deformation | `03_annular/` |
| 5 | axicon segment + SPA validity (β-scan) | `04_axicon/axicon_validity.png` |
| 6 | **pulsed×annular invariance + S(τ) + ring decomposition** | `05_pulsed_pupils/` |
| 7 | spectral window / Jacobian | `05_pulsed_pupils/spectral_sampling.png` |

### Folder layout (this workspace)
- `paper/literature/` — the high-impact literature sweep + novelty verdicts
- `paper/figures/` — publication-quality exports
- `paper/draft/` — manuscript sources
- `paper/notes/` — referee-anticipation notes, scope decisions

*Paper 2 (later): the validated Monte-Carlo engine + scattering (Phase 6),
targeted after rungs 5–6 close and the first integration result (structured
pupils vs μ_s) exists.*
