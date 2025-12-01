# Archived Notebooks

This directory contains development history - debug notebooks, intermediate implementations, and reference notebooks that have been superseded by cleaner demos.

## Categories

### Debug/Development Notebooks
These were part of the development process for fixing angular spectrum issues:
- `debug_angular_spectrum*.ipynb` - Debugging angular spectrum
- `test_angular_spectrum*.ipynb` - Testing fixes
- `diagnose_angular_spectrum_step_by_step.ipynb` - Step-by-step diagnosis
- `test_analytical_angular_spectrum*.ipynb` - Analytical tests
- `angular_spectrum_convergence*.ipynb` - Convergence testing
- `aperture_convergence*.ipynb` - Aperture parameter tests
- `optimize_fft_grid.ipynb` - FFT optimization
- `debug_hybrid_scaling.ipynb` - Hybrid approach debugging
- `test_hybrid_approach.ipynb` - Hybrid method tests
- `test_fraunhofer_fix.ipynb` - Fraunhofer fixes

### Superseded Validation Notebooks
Older versions replaced by optimized validation:
- `validate_rw_gaussian_theory.ipynb` - Original validation
- `validate_rw_gaussian_theory_executed.ipynb` - Intermediate version
- `test_rw_gaussian_simple.ipynb` - Simple test version

### Reference Implementations
Early implementations replaced by modular demos:
- `richards_wolf_demo.ipynb` - Original RW demo
- `test_gaussian_vs_uniform.ipynb` - Gaussian vs uniform comparison
- `monte_carlo_with_richards_wolf.ipynb` - Original MC demo
- `richards_wolf_gaussian_field.ipynb` - First Gaussian field implementation
- `compare_ray_vs_fraunhofer.ipynb` - Ray vs Fraunhofer comparison
- `vector_vs_scalar.ipynb` - Vectorial vs scalar comparison
- `visualize_kspace_directions.ipynb` - K-space visualization
- `test_theoretical_sampling.ipynb` - Theoretical sampling tests

## Why Archived?

These notebooks served their purpose during development but are not needed for the final modular framework. They are preserved for historical reference.

The functionality has been replaced by:
- Clean, modular code in `monte_carlo/`
- Self-contained demo notebooks in `notebooks/demos/`
- Validated results in `notebooks/validation/`
