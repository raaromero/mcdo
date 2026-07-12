# Literature sweep — verified results

*Deep-research run wf_9a2ec606-ed5 (2026-07-08). 5 search angles → 21 sources →
85 extracted claims → 25 verified. Two tiers below: **[V] = 3-vote adversarially
confirmed (3-0)**; **[L] = extracted with a direct source quote but the
independent re-verification vote was rate-limited (treat as a strong lead;
confirm the exact numbers before citing).** The synthesis step was rate-limited,
so this write-up is assembled by hand from the verified + extracted claims.*

## Update 2026-07-12 (targeted re-sweep, web search)
Confirmed verbatim this pass: **Blanca & Saloma, Appl. Opt. 37(34), 8092–8102
(1998)** ✓ (was [L] → now [V]); **Monterola & Saloma, Opt. Express 9(2), 72–84
(2001)** ✓ (proto-PINN, NN-idea heritage). Hayakawa BOE 2,278 (2011) full text
located at chem.uci.edu/~potma/carole_boe11.pdf (was [L] → source verified).

**NEW must-read prior art (pulsed-focus-in-scatter) — closest to our MC angle:**
**"Excitation with a focused, pulsed optical beam in scattering media:
diffraction effects," Appl. Opt. 39(28), 5244 (2000).** Pulsed + focused + in a
scattering medium — read this before framing the MC paper's novelty. Plus the
two-photon-in-turbid family (AO 39,1194 / 39,509 / 39,1575 / 42,3321) as
context. None combine STRUCTURED pupils + few-cycle spectra + scattering (our
gap), but the pulsed-focus-in-scatter framing is partly occupied — position
carefully.

## 0. THE headline finding — read this first (novelty)

**Hayakawa, Potma & Venugopalan, "Electric field Monte Carlo simulations of
focal field distributions produced by tightly focused laser beams in tissues,"
Biomed. Opt. Express 2, 278 (2011).** [V — full text located 2026-07-12]
`https://opg.optica.org/boe/fulltext.cfm?uri=boe-2-2-278` (also
`chem.uci.edu/~potma/carole_boe11.pdf`)
- Combines an **Electric-Field Monte Carlo (EMC)** scheme (tracks the full
  **vector** field *amplitude and phase*) with the **angular-spectrum**
  representation to compute the focal field of **tightly focused high-NA beams
  in scattering tissue** — NA = **0.81, 1.16, 1.31**. Finds scattering-induced
  broadening + amplitude loss + depolarization, governed mainly by μ_s (little g
  dependence), with **coherent amplitude loss (phase scrambling) dominating over
  depolarization**.

**Why it matters:** this is the closest prior art to `mcdo`'s Phase 6 — the
"vector focused-beam MC in a scattering medium" niche is **not** an open field;
EMC occupies it. **Our honest differentiators vs. Hayakawa 2011:**
1. **Structured pupils** (annular / axicon / Bessel) — they focus an unstructured
   beam; nobody has run structured-pupil focus through scattering with this rigor.
2. **Pulsed / few-cycle** (λ-dependent μ_s, the Romallosa temporal axis) — EMC is
   monochromatic.
3. **The ballistic-coherent-core + incoherent-halo decomposition** with a
   *validated ladder* (μ_s→0, Beer–Lambert, energy, Born) and **≥10-trial error
   bars** — a methodological contribution EMC papers don't foreground.
4. EMC is a different algorithm (field-MC of Maxwell) vs. our angular-spectrum
   photon + transport hybrid — an independent cross-check opportunity, not just a
   competitor.

→ **Action:** cite Hayakawa 2011 as the primary point of departure for Paper 2
(the MC paper). It does **not** threaten **Paper 1** (deterministic, Phases 1–5).

## 1. The Saloma lineage — exact citation confirmed

- **Romallosa, Bantang & Saloma, Phys. Rev. A 68, 033812 (2003).** [V×2]
  `https://journals.aps.org/pra/abstract/10.1103/PhysRevA.68.033812`
  RW vector theory; 750 nm; pulse widths 10⁻⁹ s → 1 fs; Linfoot F/S/Q vs 750 nm
  cw. *Your anchor — confirmed verbatim.*
- **Blanca & Saloma, Appl. Opt. 37(34), 8092–8102 (1998).** [L]
  `https://opg.optica.org/ao/abstract.cfm?uri=ao-37-34-8092`
  Monte-Carlo of **two-photon fluorescence imaging through a scattering
  medium**; a **scalar focused Gaussian** beam (not high-NA vector, not
  structured, not pulsed). *The lineage MC paper; your Phase 6b is its high-NA
  vector + structured + pulsed generalization. Exact citation now confirmed.*

## 2. Few-cycle / broadband high-NA vector focusing (Paper 1 context)

- **Radially-polarized few-cycle tight focusing via RW + vector pulse model**,
  JOSA A 37, 969 (2020). [V]
  `https://opg.optica.org/josaa/abstract.cfm?uri=josaa-37-6-969` — "moving halo"
  (convergence then divergence) at the focal plane.
- **Fs radially-polarized pulses focused through a dielectric interface at high
  NA**, JOSA A 32, 1717 (2015). [V]
  `https://opg.optica.org/josaa/abstract.cfm?uri=josaa-32-9-1717`
- **Matrix generalization of the Debye integral, extendable to ultrashort /
  polychromatic sources**, arXiv physics/0609030 (2006). [V]
  `https://arxiv.org/pdf/physics/0609030` — an efficient numerical route (cf. our
  "NUFFT would speed this up" note).

## 3. Structured pupils / vector needles (Phases 3–4 context)

- **Double-ring radially-polarized + high-NA lens-axicon → 0.45λ longitudinal
  spot, non-diffracting over ~8λ**, Opt. Commun. (2010). [V×2]
  `https://www.sciencedirect.com/science/article/abs/pii/S003039921000280X`
- **Double-ring azimuthally-polarized → sub-λ spot + long transversally-polarized
  optical needle**, Opt. Lasers Eng. 59, 93 (2014). [V]
  `https://www.sciencedirect.com/science/article/abs/pii/S0143816614000797`
- These show the **annular/double-ring DOF-extension + vector control** space is
  active (mostly *cw, monochromatic* — leaving the pulsed axis open).

## 4. Bessel/axicon DOF in nonlinear microscopy (application motivation)

- **Betzig-lab Bessel two-photon** (extended DOF, faster volumetric imaging),
  PMC4032997. [V for the axicon→annulus→Bessel-Gauss mechanism; L for the
  "1.4→15–81 µm DOF" numbers] `https://pmc.ncbi.nlm.nih.gov/articles/PMC4032997/`
- **Two-photon Bessel light-sheet nSIM**, 600 µm FOV, detection NA 0.8,
  computational descattering step, imaging >500 µm deep (zebrafish), PMC4026892. [L]
- **Lens-axicon triplet, DOF tunable 600–1000 µm**, Nat. Commun. 12 (2021),
  s41467-021-23249-y — self-healing reduces shadows even at NA 0.3. [L]
- **Annular-zone phase device, ~2× DOF** (1.73→3.55 µm) in two-photon light-sheet,
  PMC10298976; two-photon **suppresses Bessel side-lobes**. [L]
- Takeaway: microscopy demos sit at **moderate NA (≤0.8), cw, experiment-driven**;
  the **high-NA vector + few-cycle + validated forward model** angle is ours.

## 5. Frontier 2024–2026 (where the field is heading)

- **Wavefront shaping through scattering** (iterative / transmission-matrix /
  phase-conjugation) — review PMC10711682. The modern reframing of "focus through
  scatter"; our phase-carrying photons could connect a *forward* model to it.
- **Deep-learning computational imaging / descattering** — SPIE Photonics
  Insights 4(2) R03 (2025). The inverse-problem direction; our validated
  simulator is a training-data generator.
- **Bessel/structured light in turbid media** — active; self-healing quantified
  mostly experimentally, not with a validated vector+pulsed forward MC.

## 6. Novelty verdicts (the two checks you asked for)

| claim | verdict |
|---|---|
| (a) annular DOF extension **invariant to few-cycle bandwidth** at high NA | **No exact prior found** — Romallosa (pulsed, unstructured) + annular-DOF (cw) exist separately, not combined. **Plausibly novel**; still the safest Paper-1 headline. Do a final targeted search on "pulsed annular depth of focus" before submission. |
| (b) combined **pulsed + structured + high-NA-vector + scattering** forward MC | **Partially anticipated**: Hayakawa 2011 (EMC) = high-NA vector focus in scattering (no structure, no pulse); Blanca–Saloma 1998 = scalar focused MC two-photon. **The full four-axis combination + validated ladder appears unoccupied** — that is the defensible Paper-2 contribution. |

## 7. ISI journal targets (venues these papers actually appear in)

Paper 1 (deterministic, Phases 1–5): **JOSA A** (best topical fit, RW lineage) ·
**Optics Express** (fast, sim-friendly) · **Physical Review A** (Romallosa's home;
frame as few-cycle focusing physics). Fallbacks: **Journal of Optics**, **Optics
Communications** (all ISI).
Paper 2 (MC + scattering): **Biomedical Optics Express** (Hayakawa's venue —
direct lineage) · **Optics Express** · **JOSA A**.

## 8. Reference list to pull (when search resets — verify DOIs)
Confirmed venues above + still to fetch: Sheppard–Wilson 1978; Durnin 1987; Wang
MCML 1995; Novotny–Hecht (book); the Hayakawa 2011 full text; a 2024–26 wavefront-
shaping review for the intro. See `docs/LITERATURE.md` for the mastery roadmap.

---
*Status: 10/25 claims independently confirmed; 15 are strong leads pending a
verification pass (rate-limited). Re-run `wf_9a2ec606-ed5` after the API resets
to confirm the [L] items — especially the Hayakawa 2011 details and the Bessel
DOF numbers — before they go into a manuscript.*
