# Monte Carlo Refactor Design

## Goal
Create a simple, modular Monte Carlo simulation framework that:
1. Is easy to understand and use
2. Has individual pieces that can be demoed independently
3. Integrates core functionality from gbp-mc (without corrections)
4. Supports multiple intensity calculation methods (Richards-Wolf, Tanaka, MC ray tracing)

## Modular Architecture

```
monte_carlo/
├── beam/
│   ├── __init__.py
│   ├── gaussian.py          # Gaussian beam initialization and parameters
│   └── properties.py        # Beam property calculations (w0, z_R, etc.)
│
├── propagation/
│   ├── __init__.py
│   ├── analytical.py        # Tanaka analytical formulas
│   ├── richards_wolf.py     # Richards-Wolf vectorial diffraction
│   ├── ray_tracing.py       # Monte Carlo ray tracing (from gbp-mc)
│   └── utils.py             # Shared propagation utilities
│
├── scattering/
│   ├── __init__.py
│   ├── phase_functions.py   # Henyey-Greenstein, Mie scattering
│   ├── medium.py            # Scattering medium (particles, geometry)
│   └── monte_carlo.py       # MC scattering simulation loop
│
├── optical_systems/
│   ├── __init__.py
│   ├── microscope.py        # Complete microscope configuration
│   └── base.py              # Base optical system class
│
└── utils/
    ├── __init__.py
    ├── geometry.py          # Geometric calculations
    └── intersections.py     # Ray-sphere, ray-box intersections
```

## Core Components from gbp-mc

### 1. Gaussian Beam Initialization (`beam/gaussian.py`)
**From**: `gbp-mc/src/core/gaussian_beam_propagation.py::FocusedGaussianBeam.__init__`

```python
class GaussianBeam:
    """Simple Gaussian beam with standard parameters."""

    def __init__(self, wavelength, NA, n_medium=1.0,
                 focal_length=None, aperture=None,
                 truncation_coeff=4.0):
        """
        Parameters:
            wavelength: wavelength in microns
            NA: numerical aperture
            n_medium: refractive index
            focal_length: focal length (auto-calculated if None)
            aperture: aperture diameter (auto-calculated if None)
            truncation_coeff: beam truncation (α = 1/fill_factor²)
        """

    def beam_radius(self, z):
        """Beam radius at position z."""

    def intensity(self, r, z):
        """Transverse intensity at (r, z)."""
```

### 2. Ray Tracing Propagation (`propagation/ray_tracing.py`)
**From**: `gbp-mc/src/core/gaussian_beam_propagation.py::FocusedGaussianBeamMC`

```python
class RayTracingPropagation:
    """Monte Carlo ray tracing for Gaussian beam."""

    def __init__(self, beam, num_photons, num_steps,
                 curvature_correction=False):
        """
        Parameters:
            beam: GaussianBeam object
            num_photons: number of rays to trace
            num_steps: number of propagation steps
            curvature_correction: use wavefront curvature (gbp-mc feature)
        """

    def init_collimated(self):
        """Initialize photon positions at lens (Gaussian distribution)."""

    def init_directions(self, positions):
        """Calculate initial ray directions pointing toward focus."""

    def propagate(self):
        """Propagate rays through free space."""
        return ray_positions  # shape: (3, num_photons, num_steps)
```

### 3. Monte Carlo Scattering (`scattering/monte_carlo.py`)
**From**: `gbp-mc/src/core/ray_scatter.py::sim2_unwrap`

```python
class MonteCarloScattering:
    """Monte Carlo scattering simulation (NO corrections)."""

    def __init__(self, beam, medium, num_photons, num_steps):
        """
        Parameters:
            beam: GaussianBeam object
            medium: ScatteringMedium object
            num_photons: number of photons
            num_steps: max propagation steps
        """

    def simulate(self):
        """
        Run MC simulation with scattering.

        Returns:
            rays: ray positions (3, num_photons, num_steps)
            scattered_history: scattering events per photon
        """
```

### 4. Scattering Medium (`scattering/medium.py`)
**From**: `gbp-mc/src/core/scatterer.py::RandomScatteringMedium`

```python
class ScatteringMedium:
    """Scattering medium with particles."""

    def __init__(self, bounds, particle_radius, scattering_degree,
                 particle_index, env_index, wavelength):
        """
        Parameters:
            bounds: [[xmin, xmax], [ymin, ymax], [zmin, zmax]]
            particle_radius: particle radius in microns
            scattering_degree: number of mean free paths
            particle_index: particle refractive index
            env_index: environment refractive index
            wavelength: wavelength in microns
        """
        self.particle_centers = ...  # calculated from scattering_degree
        self.anisotropy = ...        # Mie theory g parameter
```

### 5. Phase Functions (`scattering/phase_functions.py`)
**From**: `gbp-mc/src/core/ray_scatter.py::henyey_greenstein`

```python
def henyey_greenstein(g, size):
    """
    Sample scattering angles from Henyey-Greenstein phase function.

    Parameters:
        g: anisotropy parameter (0=isotropic, 1=forward)
        size: number of samples

    Returns:
        theta: scattering angles
        phi: azimuthal angles
    """
```

## Optical System Classes

```python
class OpticalSystem:
    """Base class for optical setups."""

    def __init__(self, beam, propagation_method='analytical'):
        """
        Parameters:
            beam: GaussianBeam object
            propagation_method: 'analytical', 'richards_wolf', or 'ray_tracing'
        """

    def focal_plane_intensity(self, r):
        """Calculate intensity at focal plane."""

    def axial_intensity(self, z):
        """Calculate intensity along optical axis."""


class Microscope(OpticalSystem):
    """Microscope configuration with optional scattering medium."""

    def __init__(self, wavelength, NA, scattering_medium=None):
        beam = GaussianBeam(wavelength=wavelength, NA=NA)
        super().__init__(beam)
        self.medium = scattering_medium

    def simulate(self, num_photons=10000):
        """Run full simulation (with or without scattering)."""
```

## Demo Notebooks

See `NOTEBOOK_ORGANIZATION.md` for complete specifications.

### 01_richards_wolf_uniform.ipynb
- Richards-Wolf vectorial diffraction theory
- Uniform illumination (traditional setup)
- Compare low NA (0.1) vs high NA (0.9)
- Show depolarization effects
- Focal plane intensity patterns
- Polarization components (Ex, Ey, Ez)

### 02_richards_wolf_gaussian.ipynb
- Gaussian input field with apodization
- Effect of fill_factor (0.5, 0.6, 0.8, 0.95)
- Beam truncation effects
- Comparison: uniform vs Gaussian illumination
- FWHM vs fill_factor analysis

### 03_gaussian_beam_theory.ipynb
- Tanaka analytical formulas for focused Gaussian beams
- Basic parameters (w0, z_R, Rayleigh range)
- Truncation coefficient α
- Focal plane and axial intensity
- 3D intensity distribution

### 04_validation_rw_vs_tanaka.ipynb
- Validate Richards-Wolf against analytical theory
- Low NA (paraxial) and high NA (vectorial) regimes
- Parameter sweep: optimize fill_factor
- Quantitative metrics (MSE, correlation, FWHM)
- Shows optimal fill_factor = 0.95

### 05_monte_carlo_ray_tracing.ipynb
- Ray-based Monte Carlo (from gbp-mc)
- Initialize rays with Gaussian distribution
- Propagate through free space (no scattering)
- Render intensity from ray positions
- Compare to analytical/RW results
- Convergence analysis

### 06_scattering_medium.ipynb
- Create and visualize scattering media
- Scattering degree and Mie theory
- Random particle placement
- Henyey-Greenstein phase function
- Single scattering demonstration

### 07_monte_carlo_with_scattering.ipynb
- Full MC simulation with scattering
- Ray-sphere intersection detection
- Track scattered vs unscattered photons
- Different scattering degrees (0, 2, 4, 6)
- Intensity broadening analysis

## Key Simplifications

1. **No corrections**: Port gbp-mc functionality WITHOUT the curvature correction by default
2. **No numba**: Remove all `@jit` decorators - pure NumPy/Python implementations
3. **Modular intensity methods**: Easy to switch between analytical, RW, MC
4. **Clear separation**: Beam parameters, propagation, scattering are separate modules
5. **Simple API**: Each component can be used independently
6. **Demo-driven**: Every module has a corresponding demo notebook

## Migration from Current mcdo

**Keep**:
- `monte_carlo/gaussian_beam_theory.py` → becomes `propagation/analytical.py`
- `monte_carlo/richards_wolf.py` → becomes `propagation/richards_wolf.py` (cleaned up)

**Remove/Archive**:
- Old endpoint MC sampling code
- Test scripts (consolidate into notebooks)

**New**:
- Everything in `beam/`, `scattering/`, `optical_systems/`
- Ray tracing from gbp-mc

## Implementation Order

1. Create directory structure
2. Port GaussianBeam initialization (simple, no MC)
3. Port analytical formulas (Tanaka)
4. Clean up Richards-Wolf
5. Port ray tracing (no scattering)
6. Port scattering medium
7. Port MC scattering
8. Create optical system classes
9. Create demo notebooks (one at a time)
