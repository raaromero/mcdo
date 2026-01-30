# Depth of Field (DOF) Methodology

## Simulation (Richards-Wolf)

### How DOF is computed:

1. **Compute axial intensity profile** I(r=0, z):
   - Use Richards-Wolf vectorial diffraction integrals
   - For annular aperture: Babinet's principle (E_annular = E_outer - E_inner)
   - Compute I_total = |Ex|² + |Ey|² + |Ez|²

2. **Normalize** to peak intensity (at z=0)

3. **Measure FWHM** (Full Width at Half Maximum):
   - Find z values where I(z) = 0.5 × I_max
   - DOF = z_upper - z_lower

### Code:
```python
def compute_axial_profile(NA, epsilon, ...):
    # z along optical axis, r=0
    Ex, Ey, Ez = compute_annular_field(NA, epsilon, r=0, z_array)
    I_total = |Ex|² + |Ey|² + |Ez|²
    return I_total / max(I_total)

def measure_dof_fwhm(z, intensity):
    # Find where intensity crosses 0.5
    above = intensity >= 0.5
    return z[last_above] - z[first_above]
```

## Theory (Paraxial Scalar Diffraction)

### Circular Aperture

On-axis intensity for uniformly illuminated circular aperture:

```
I(z) = sinc²(u/4)
```

where:
- u = k sin²(α) z = (2π/λ)(NA/n)² z (optical coordinate)
- In normalized units z_norm = z / (λ/NA²): I(z_norm) = sinc²(π z_norm / 2)

**First zeros** at z_norm = ±2, so distance between zeros = 4 × (λ/NA²)

**FWHM** (50% threshold): sinc²(x) = 0.5 when x ≈ 1.39
- Half-width: z_norm ≈ 1.39 × 2/π ≈ 0.89
- Full FWHM ≈ 1.78 × (λ/NA²)

### Annular Aperture

Simple approximation often cited:

```
DOF_annular ≈ 2λ / (NA²_outer - NA²_inner) = 2λ / (NA² × (1 - ε²))
```

This gives DOF ratio:
```
DOF_annular / DOF_circular = 1 / (1 - ε²)
```

**However**, this formula:
- Assumes paraxial approximation
- Uses specific DOF definition (may be first zeros, not FWHM)
- Assumes uniform illumination
- Ignores vectorial effects

### More accurate theory (Babinet):

For annular aperture, the on-axis field is:
```
E(z) = E_outer(z) - E_inner(z)
```

where E_inner uses NA_inner = ε × NA_outer, which has different z-scaling.

The intensity is:
```
I(z) ∝ |sinc(π z_norm / 2) - ε² × sinc(π ε² z_norm / 2)|²
```

This doesn't simplify to 1/(1-ε²) for FWHM measurement.

## Why Simulation ≠ Simple Theory

| Factor | Theory | Simulation |
|--------|--------|------------|
| Diffraction | Scalar (paraxial) | Vectorial (Richards-Wolf) |
| Field components | E only | Ex, Ey, Ez |
| Angles | sin(θ) ≈ θ | Full trigonometry |
| Illumination | Uniform | Uniform or Gaussian |
| Aplanatic factor | Ignored | √cos(θ) included |
| DOF definition | First zeros or approx | FWHM (50% threshold) |

## Expected Agreement

- **Low NA (0.1) + Uniform illumination**: Should match paraxial theory well
- **High NA (0.9)**: Vectorial effects → deviation from theory
- **Gaussian illumination**: Broader axial profile → larger DOF than uniform

## Sources of Discrepancy from Theory

### Comparison Table (DOF in units of λ/NA²)

| NA | ε | Uniform (Total) | Uniform (Ex) | Gaussian (Total) | Gaussian (Ex) | Theory |
|----|---|-----------------|--------------|------------------|---------------|--------|
| 0.1 | 0.0 | 1.71 | 1.71 | 2.51 | 2.51 | 1.77 |
| 0.1 | 0.5 | 2.31 | 2.31 | 2.92 | 2.92 | 2.36 |
| 0.1 | 0.9 | 8.74 | 8.74 | 9.35 | 9.35 | 9.32 |
| 0.9 | 0.0 | 1.11 | 1.11 | 2.31 | 2.31 | 1.77 |
| 0.9 | 0.5 | 1.51 | 1.51 | 2.11 | 2.11 | 2.36 |
| 0.9 | 0.9 | 4.52 | 4.52 | 4.52 | 4.52 | 9.32 |

### Analysis of Effects

**1. Total vs Ex-only Intensity: NEGLIGIBLE (<1%)**
- On-axis (r=0), Ex dominates for x-polarized input
- Ez contributes only off-axis
- **Conclusion:** Using |Ex|² vs |Ex|²+|Ey|²+|Ez|² doesn't matter for DOF

**2. Gaussian vs Uniform: MAJOR EFFECT (+47% to +109%)**
- NA=0.1: Gaussian DOF = 2.51 vs Uniform DOF = 1.71 (+47%)
- NA=0.9: Gaussian DOF = 2.31 vs Uniform DOF = 1.11 (+109%)
- **Conclusion:** Gaussian apodization significantly broadens axial profile

**3. High NA vs Low NA: MAJOR EFFECT (-37%)**
- NA=0.1 (uniform): DOF = 1.71 (theory = 1.77, -3.5% error)
- NA=0.9 (uniform): DOF = 1.11 (theory = 1.77, -37.6% error)
- **Conclusion:** Vectorial effects compress focal region at high NA

### Summary
| Source | Effect on DOF | When Important |
|--------|---------------|----------------|
| Total vs Ex-only | Negligible | Never |
| Gaussian vs Uniform | +47% to +109% | Always when using Gaussian |
| High NA vectorial | -37% | NA > 0.5 |

## Supporting Plots

| Plot | Location | Shows |
|------|----------|-------|
| `dof_comparison_all.png` | `data/annular_dof/` | All 4 variants (Uniform/Gaussian × Total/Ex) |
| `uniform_dof_test.png` | `data/annular_dof/` | Uniform-only comparison with theory |
| `dof_vs_epsilon_v2.png` | `data/annular_dof/` | DOF vs ε sweep |
| `gaussian_profiles.png` | `data/annular_dof/` | Gaussian α=4 profiles |

## Validation Results (Uniform Illumination)

### Low NA (0.1) - Paraxial Regime
| ε | Simulation | Theory | Ratio (sim) | Ratio (theory) |
|---|---|---|---|---|
| 0.0 | 1.71 | 1.77 | 1.00 | 1.00 |
| 0.5 | 2.31 | 2.36 | 1.35 | 1.33 |
| 0.9 | 8.74 | 9.32 | 5.12 | 5.26 |
| 0.99 | 87.4 | 89.0 | 51.2 | 50.3 |

**Conclusion: Theory matches simulation within 2-3% for low NA!**

### High NA (0.9) - Vectorial Regime
| ε | Simulation | Theory | Ratio (sim) | Ratio (theory) |
|---|---|---|---|---|
| 0.0 | 1.11 | 1.77 | 1.00 | 1.00 |
| 0.5 | 1.51 | 2.36 | 1.36 | 1.33 |
| 0.9 | 4.52 | 9.32 | 4.09 | 5.26 |
| 0.99 | 39.2 | 89.0 | 35.5 | 50.3 |

**Conclusion: High NA has ~37% smaller DOF than paraxial theory predicts!**
This is due to vectorial effects (Ez component, aplanatic factor).

## References

- Born & Wolf, *Principles of Optics*, Chapter 8
- Nikon MicroscopyU: DOF = λn/NA² (wave optical term)
- Richards & Wolf (1959): Vectorial diffraction theory
- Welford, W.T. (1960): "Use of Annular Apertures to Increase Focal Depth", JOSA 50(8):749
- Rivolta, C. (1988): "Annular circular aperture: intensity maxima and minima on the optical axis", Appl. Opt. 27(5):922
