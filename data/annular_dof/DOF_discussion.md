# Depth of Field (DOF) Discussion

## What is Depth of Field?

- **Definition:** Axial range where focused intensity stays above threshold (50% of peak)
- **Physical meaning:** How "long" the focal region extends along optical axis
- **Trade-off:** Larger DOF → lower peak intensity

## How DOF is Computed

### Simulation (Richards-Wolf)
1. Compute E(r=0, z) using vectorial diffraction integrals
2. Annular apertures: E_annular = E_outer - E_inner (Babinet)
3. Intensity: I(z) = |Ex|² + |Ey|² + |Ez|²
4. **FWHM:** z-range where I ≥ 0.5 × I_max

### Theory (Paraxial)
- I(z) = sinc²(πz/2) where z in units of λ/NA²
- **DOF_circular ≈ 1.77 × λ/NA²**
- **DOF_annular ≈ DOF_circular / (1-ε²)**

## Key Results

### 1. Uniform + Low NA matches theory
| ε | Simulation | Theory | Error |
|---|------------|--------|-------|
| 0.0 | 1.71 | 1.77 | -3% |
| 0.5 | 2.31 | 2.36 | -2% |
| 0.9 | 8.74 | 9.32 | -6% |

### 2. High NA gives smaller DOF than theory
- NA=0.9, ε=0: Sim=1.11 vs Theory=1.77 (**-37%**)
- Vectorial effects compress focal region

### 3. Gaussian illumination increases DOF
| NA | Uniform | α=0.4 | α=4.0 |
|----|---------|-------|-------|
| 0.1 | 1.71 | 1.71 (0%) | 2.51 (+47%) |
| 0.9 | 1.11 | 1.31 (+18%) | 2.31 (+109%) |

### 4. α≤0.25 approximates uniform
- From alpha sweep: α≤0.25 gives <1% RMS difference from uniform
- DOF results confirm: α=0.4 ≈ uniform for low NA

## Summary Table

| Effect | Impact | When |
|--------|--------|------|
| Uniform vs Theory | ~3% | Low NA |
| High NA vectorial | -37% | NA > 0.5 |
| Gaussian α=4 | +50-110% | Always |
| α=0.4 vs uniform | 0-18% | Depends on NA |

## Supporting Plots

| Plot | Shows |
|------|-------|
| `uniform_dof_test.png` | Uniform vs theory |
| `axial_profiles_comparison.png` | Uniform vs α=0.4 vs α=4.0 |
| `dof_vs_epsilon_comparison.png` | DOF vs ε for all illuminations |
| `dof_comparison_all.png` | All variants side-by-side |

## References

- Born & Wolf, *Principles of Optics*, Ch. 8
- Richards & Wolf (1959)
- Welford (1960): JOSA 50(8):749
- Rivolta (1988): Appl. Opt. 27(5):922
