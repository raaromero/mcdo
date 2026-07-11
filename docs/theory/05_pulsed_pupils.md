# Pulsed sources × annular apertures
*(Phase 5 — the new science: how few-cycle bandwidth interacts with
annular DOF extension. The progress report's "immediate next step".)*

## 1. Method

Compose the two validated primitives: the Eq.-10 spectral sum (full positive
spectrum ω∈(0,2ω_c), Phase 1) over annular fields (field-level Babinet,
Phase 3). For each (τ, ε) at $X_{NA}=0.8$, λc=750 nm, linear-x y-cut,
N_freq=201: axial profile on a fixed physical z-grid (labelled in
central-frequency units $u_c=k_c\sin^2\alpha\,z$) → DOF(τ,ε); transverse at
z=0 → Bessel-ring contrast via Linfoot S vs the CW annular reference at the
same ε.

## 2. Headline results (`output/05_pulsed_pupils/verify_pulsed_annular.png`)

**(i) The annular DOF extension is immune to few-cycle bandwidth.**

| ε | cw | 5 fs | 2 fs | 1 fs |
|---|---|---|---|---|
| DOF(ε)/DOF(0) | — | — | — | — |
| 0.50 | 1.30 | 1.30 | 1.30 | 1.30 |
| 0.90 | 4.76 | 4.76 | 4.76 | 4.76 |
| 0.99 | 44.35 | 44.35 | 44.34 | 44.33 |

The extension ratio is invariant to 3 digits down to a 1-fs pulse. Physically
expected — the $1/(1-\varepsilon^2)$ factor is purely geometric and NA is
fixed across all spectral components — but a clean, useful design statement:
**few-cycle pulses keep the full axial benefit of an annular/Bessel pupil.**
Each configuration's own DOF lengthens only ~1.0% from cw to 1 fs (the red
spectral components stretch slightly in $u_c$ units).

**(ii) Transverse ring contrast erodes with pulsing**, exactly as the
Romallosa cw zeros filled in: Linfoot $S(1\text{ fs})\to1.058$ across all ε.
Cross-check: at ε=0 (full disk) $S(1\text{ fs})=1.056$, matching the Phase-1
single-photon value (1.053–1.062) — independent confirmation of the pipeline.

## 3. Flag — non-monotonic ring metric at high ε

At ε=0.9–0.99 the transverse $S(\tau)$ is **non-monotonic**:
$S=0.988\to0.987\to1.058$ for 5/2/1 fs (dips below 1 before rising above).
Interpretation: moderate pulses average Bessel beams of different scales,
**washing out the rings** (lower ring energy → S<1); only the 1-fs pulse's
large central broadening pushes S>1. This is plausible ring-physics and the
S(cw,cw)=1 / ε=0 cross-checks argue against a bug, but it is a subtlety beyond
the simple "contrast degrades" story and is worth a dedicated look (encircled
ring energy vs τ) if it becomes load-bearing.

## 4. Significance

This closes the loop the progress report opened: **pulsing preserves the
axial DOF-extension benefit of annular/Bessel pupils but costs transverse
contrast** — the same trade the single-photon Romallosa study showed for the
plain disk, now quantified for structured pupils. It is the result that feeds
Phase 6 (Monte Carlo): the pulsed structured-pupil focal field is the source,
validated in the clear-medium limit before scattering is switched on.
