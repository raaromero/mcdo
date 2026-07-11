# Overview — research path and validation status

**Goal.** Quantitative design rules for beam-scanning (especially two-photon)
microscopy under realistic conditions — few-cycle pulsed sources, Gaussian
(apodized) illumination, annular apertures and axicons — culminating in Monte
Carlo photon transport in scattering media that uses these vector focal fields
as sources.

**Method.** Each phase is a module + validation script + notebook + figures,
checkpointed against literature or analytics before the next phase builds on
it. Predecessor codebases (`mcdo`, `optical-diffraction`, `gbp-mc`) are used
as references only; known bugs found in them are documented here and fixed on
`mcdo`'s `cleanup` branch.

## Phases

| # | Phase | Doc | Checkpoint | Status |
|---|-------|-----|------------|--------|
| 1 | Romallosa 2003 replication (RW + pulse engine) | `01_richards_wolf_pulse.md` | all 5 paper figures + Linfoot values | ✅ done (notebook 01) |
| 2 | Apodization + scalar Debye / NA convergence | `02_apodization_scalar_debye.md` | Airy analytic at low NA; NA thresholds | ✅ verification done |
| 3 | Annular apertures (Babinet) | `03_annular_babinet.md` | DOF=1/(1−ε²); Strehl=(1−ε²)² | ✅ verified |
| 4 | Axicon / Bessel beams | `04_axicon.md` | Durnin J₀² (SPA-limited) | ✅ verified |
| 5 | Pulsed × structured pupils (new science) | `05_pulsed_pupils.md` | DOF pulse-invariant; ring contrast | ✅ verified |
| 6 | Monte Carlo: (a) ballistic replication, (b) scattering | — | μ_s→0 limit must equal RW | next |

## Results layout — one folder per main result

```
output/01_romallosa/        Phase 1: the five paper figures
output/02_na_apodization/   Phase 2: checks 1–8 + Tanaka + NA thresholds
output/03_annular/          Phase 3: DOF/profiles + energy-cost
output/04_axicon/           Phase 4: focal segment + Durnin checks
output/05_pulsed_pupils/    Phase 5: pulsed × annular (new science)
…
```
Scripts write into their phase folder; notebooks display from there.

## Package layout (`mcdo/` (package))

- `config.py` — `SimConfig`: physical parameters, spectral grid & weights
- `rw_integrals.py` — Richards-Wolf I₀, I₁, I₂ (vectorized Simpson quadrature)
- `intensity.py` — CW and pulsed (Eq. 10) intensity on (r, z) grids
- `apodization.py` — pupil illumination functions A(θ); future MC photon launchers
- `debye.py` — scalar Debye integral + paraxial Airy/sinc² analytics
- `linfoot.py` — fidelity F, structural content S, correlation quality Q

## Monte Carlo design intent (Phase 6)

1. **Stage 1 — no scattering**: photons launched from the pupil with
   density given by |A(θ)|², refracted by the aplanatic lens; the MC
   intensity estimate must converge to the RW ballistic result for every
   configuration of Phases 1–5. This is the MC's validation gate.
2. **Stage 2 — scattering**: free-path sampling, Henyey-Greenstein/Mie
   phase functions, absorption. Pulses enter as per-ω transport
   (time-resolved MC), reusing the validated spectral machinery.
3. **Caveat**: MC transports intensity (radiative transfer) and cannot
   reproduce interference; the focal spot is an interference pattern. The
   hybrid used in the literature (Blanca & Saloma 1998; Gao 2020;
   Arjonillo 2023): RW wave treatment for the ballistic component + MC for
   the scattered background.
