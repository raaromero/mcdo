# Notebook Organization

## Existing Notebooks - Categorization

### KEEP (Important Results)
These contain key validation results and should be preserved:

1. **validate_rw_gaussian_theory_optimized.ipynb**
   - Final validation: Richards-Wolf Gaussian vs Tanaka analytical theory
   - Shows optimal fill_factor = 0.95 gives perfect agreement
   - MSE ≈ 0, Correlation = 1.0
   - **Status**: Key result, keep in `notebooks/validation/`

2. **compare_methods_executed.ipynb**
   - Comparison of different propagation methods
   - **Status**: Review content, likely keep

3. **richards_wolf_gaussian_field.ipynb**
   - Initial implementation of Gaussian input field for RW
   - **Status**: Keep as reference, but will be replaced by cleaner demo

### ARCHIVE (Debug/Intermediate Work)
Move these to `notebooks/archive/` - they were part of the development process:

1. **debug_angular_spectrum*.ipynb** (3 notebooks)
   - Debugging angular spectrum issues

2. **test_angular_spectrum*.ipynb** (5 notebooks)
   - Multiple attempts at fixing angular spectrum

3. **angular_spectrum_convergence*.ipynb** (2 notebooks)
   - Convergence testing

4. **diagnose_angular_spectrum_step_by_step.ipynb**
   - Step-by-step debugging

5. **test_analytical_angular_spectrum*.ipynb** (4 notebooks)
   - Multiple versions of analytical tests

6. **optimize_fft_grid.ipynb**
   - FFT grid optimization tests

7. **debug_hybrid_scaling.ipynb**
   - Hybrid approach debugging

8. **test_hybrid_approach.ipynb**
   - Hybrid method tests

9. **test_fraunhofer_fix.ipynb**
   - Fraunhofer approximation fixes

10. **aperture_convergence*.ipynb** (2 notebooks)
    - Aperture parameter convergence

11. **validate_rw_gaussian_theory_executed.ipynb**
    - Older version, superseded by optimized version

12. **validate_rw_gaussian_theory.ipynb**
    - Original version, superseded

13. **test_rw_gaussian_simple.ipynb**
    - Simple test, superseded by optimized validation

### REPLACE WITH DEMOS
These show basic functionality but should be replaced with cleaner, modular demos:

1. **richards_wolf_demo.ipynb**
   - Basic Richards-Wolf demonstration
   - **Replace with**: `demos/01_richards_wolf_uniform.ipynb`

2. **test_gaussian_vs_uniform.ipynb**
   - Comparing Gaussian vs uniform illumination
   - **Replace with**: `demos/02_richards_wolf_gaussian.ipynb`

3. **monte_carlo_with_richards_wolf.ipynb**
   - MC sampling with RW
   - **Replace with**: `demos/05_monte_carlo_sampling.ipynb`

### REVIEW (Need to Check Content)
Need to look at these to decide:

1. **compare_ray_vs_fraunhofer.ipynb**
2. **vector_vs_scalar.ipynb**
3. **visualize_kspace_directions.ipynb**
4. **test_theoretical_sampling.ipynb**

---

## NEW Demo Notebooks Structure

```
notebooks/
├── demos/                          # Clean, modular demonstrations
│   ├── 01_richards_wolf_uniform.ipynb
│   ├── 02_richards_wolf_gaussian.ipynb
│   ├── 03_gaussian_beam_theory.ipynb
│   ├── 04_validation_rw_vs_tanaka.ipynb
│   ├── 05_monte_carlo_ray_tracing.ipynb
│   ├── 06_scattering_medium.ipynb
│   └── 07_monte_carlo_with_scattering.ipynb
│
├── validation/                     # Important validation results
│   └── validate_rw_gaussian_theory_optimized.ipynb
│
└── archive/                        # Development/debug history
    └── [all debug and intermediate notebooks]
```

---

## Demo Notebook Specifications

### Demo 01: Richards-Wolf Uniform Field
**File**: `demos/01_richards_wolf_uniform.ipynb`

**Purpose**: Introduce Richards-Wolf vectorial diffraction with uniform illumination

**Content**:
- What is Richards-Wolf theory?
- Set up basic parameters (NA, wavelength, polarization)
- Compute focal plane intensity (uniform illumination)
- Compare low NA (0.1) vs high NA (0.9)
- Show depolarization effects at high NA
- Plot radial intensity profiles
- Show 2D intensity patterns

**Key visualizations**:
- Focal plane intensity (linear and log scale)
- Comparison of different NAs
- Polarization components (Ex, Ey, Ez)

---

### Demo 02: Richards-Wolf Gaussian Field
**File**: `demos/02_richards_wolf_gaussian.ipynb`

**Purpose**: Show how Gaussian illumination affects focal spot

**Content**:
- Gaussian input field (apodization function)
- What is fill_factor?
- Compare different fill_factors (0.5, 0.6, 0.8, 0.95)
- Low NA vs high NA with Gaussian illumination
- Effects of beam truncation

**Key visualizations**:
- Focal plane intensity for different fill_factors
- Side-by-side comparison: uniform vs Gaussian
- FWHM vs fill_factor plots

---

### Demo 03: Gaussian Beam Theory (Tanaka)
**File**: `demos/03_gaussian_beam_theory.ipynb`

**Purpose**: Analytical theory for focused Gaussian beams

**Content**:
- Tanaka et al. (1985) formulas
- Basic Gaussian beam parameters (w0, z_R, Rayleigh range)
- Truncation coefficient α
- Focal plane intensity (analytical)
- Axial intensity distribution
- 3D intensity distribution

**Key visualizations**:
- Beam radius vs z
- Axial intensity
- Focal plane radial profiles
- Effect of truncation (different α values)

---

### Demo 04: Validation - Richards-Wolf vs Tanaka
**File**: `demos/04_validation_rw_vs_tanaka.ipynb`

**Purpose**: Validate Richards-Wolf implementation against analytical theory

**Content**:
- Low NA regime (paraxial, both should agree)
- High NA regime (vectorial effects)
- Parameter sweep: fill_factor optimization
- Optimal agreement at fill_factor = 0.95
- Quantitative metrics (MSE, correlation, FWHM)

**Key visualizations**:
- Side-by-side intensity comparisons
- Residual plots
- MSE vs fill_factor
- Correlation vs fill_factor

---

### Demo 05: Monte Carlo Ray Tracing (No Scattering)
**File**: `demos/05_monte_carlo_ray_tracing.ipynb`

**Purpose**: Ray-based Monte Carlo through free space

**Content**:
- Initialize rays from Gaussian distribution at lens
- Calculate ray directions toward focus
- Propagate rays through free space
- Render intensity from ray positions
- Compare to analytical/RW results
- Effect of num_photons on convergence

**Key visualizations**:
- Ray trajectories (3D)
- Rendered intensity vs analytical
- Convergence: intensity vs num_photons

---

### Demo 06: Scattering Medium
**File**: `demos/06_scattering_medium.ipynb`

**Purpose**: Create and visualize scattering media

**Content**:
- Define scattering medium parameters
- Scattering degree (mean free paths)
- Mie theory: calculate g from particle properties
- Random particle placement
- Henyey-Greenstein phase function
- Single scattering event demonstration

**Key visualizations**:
- 3D particle positions
- Phase function plots (different g values)
- Scattering angle distributions
- Mean free path illustration

---

### Demo 07: Monte Carlo with Scattering
**File**: `demos/07_monte_carlo_with_scattering.ipynb`

**Purpose**: Full MC simulation with scattering

**Content**:
- Combine beam + medium
- Ray-sphere intersection detection
- Scattering events
- Track scattered vs unscattered photons
- Compare different scattering degrees (0, 2, 4, 6)
- Analyze intensity broadening

**Key visualizations**:
- Ray trajectories with scattering
- Intensity: no scattering vs with scattering
- Scattering degree effects
- Scattered photon distribution

---

## Implementation Plan

1. Create directory structure
2. Archive old notebooks
3. Implement modular code
4. Create demos one by one (in order)
5. Each demo should:
   - Run independently
   - Be self-contained
   - Include markdown explanations
   - Have clear visualizations
   - Link to relevant theory/papers
