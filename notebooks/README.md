# Notebooks

This directory contains Jupyter notebooks for demonstrations, validation, and archived development work.

## Structure

```
notebooks/
├── demos/                          # Clean demonstrations of each module
├── validation/                     # Important validation results
├── archive/                        # Development history and debug notebooks
└── [comparison notebooks]          # Method comparison notebooks (to review)
```

## Demos (To Be Created)

Clean, modular demonstrations:

1. **01_richards_wolf_uniform.ipynb** - Richards-Wolf with uniform illumination
2. **02_richards_wolf_gaussian.ipynb** - Richards-Wolf with Gaussian input field
3. **03_gaussian_beam_theory.ipynb** - Tanaka analytical formulas
4. **04_validation_rw_vs_tanaka.ipynb** - Validate numerical vs analytical
5. **05_monte_carlo_ray_tracing.ipynb** - MC ray tracing (no scattering)
6. **06_scattering_medium.ipynb** - Create and visualize scattering media
7. **07_monte_carlo_with_scattering.ipynb** - Full MC with scattering

Each demo:
- Runs independently
- Is self-contained
- Includes clear explanations
- Has publication-quality figures
- Links to relevant papers

## Validation

**validate_rw_gaussian_theory_optimized.ipynb** - Key validation result showing:
- Richards-Wolf Gaussian implementation is correct
- Optimal fill_factor = 0.95 gives perfect agreement with Tanaka theory
- MSE ≈ 0, Correlation = 1.0 at low NA

## Comparison Notebooks (To Review)

These contain method comparisons that may be worth keeping:
- `compare_methods_executed.ipynb`
- `compare_methods.ipynb`

## Archive

See `archive/README.md` for details on archived notebooks.
Contains development history: debug notebooks, intermediate implementations, and superseded versions.
