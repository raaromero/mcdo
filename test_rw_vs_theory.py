"""
Validate Richards-Wolf Gaussian implementation against analytical theory.

Compares Richards-Wolf vectorial diffraction with Gaussian input field
against analytical formulas from Tanaka et al. (1985) for focused
Gaussian beams through circular apertures.
"""

import sys
sys.path.insert(0, '.')

import numpy as np
import matplotlib.pyplot as plt
from monte_carlo.richards_wolf import RichardsWolfSimulator
from monte_carlo.gaussian_beam_theory import FocusedGaussianBeamTheory

print("="*70)
print("Richards-Wolf vs Analytical Theory: Focused Gaussian Beam")
print("="*70)

# Parameters
wavelength = 0.532  # microns
n_medium = 1.0
polarization = 'x'

# Test cases: Low and High NA
test_cases = [
    {
        'NA': 0.1,
        'fill_factor': 0.6,
        'focal_length': 50000.0,  # 50mm
        'name': 'Low NA'
    },
    {
        'NA': 0.9,
        'fill_factor': 0.6,
        'focal_length': 5000.0,  # 5mm
        'name': 'High NA'
    }
]

fig, axes = plt.subplots(2, 3, figsize=(18, 10))

for case_idx, case in enumerate(test_cases):
    NA = case['NA']
    fill_factor = case['fill_factor']
    focal_length = case['focal_length']
    name = case['name']

    print(f"\n{'='*70}")
    print(f"{name}: NA={NA}, fill_factor={fill_factor}")
    print(f"{'='*70}")

    # Create Richards-Wolf simulator with Gaussian input
    rw_sim = RichardsWolfSimulator(
        wavelength=wavelength,
        numerical_aperture=NA,
        n_medium=n_medium,
        polarization=polarization,
        input_field='gaussian',
        fill_factor=fill_factor
    )

    print(f"\n  Richards-Wolf Parameters:")
    print(f"    Airy radius: {rw_sim.airy_radius:.4f} μm")
    print(f"    Angular aperture: {np.degrees(rw_sim.angular_aperture):.2f}°")

    # Create analytical theory model
    # Relationship between fill_factor and truncation_coeff:
    # fill_factor = w_incident / r_aperture
    # For Gaussian: w_incident = (aperture/2) / sqrt(trunc_coeff)
    # So: fill_factor = 1 / sqrt(trunc_coeff)
    # Therefore: trunc_coeff = 1 / fill_factor²

    truncation_coeff = 1.0 / (fill_factor**2)

    theory = FocusedGaussianBeamTheory(
        numerical_aperture=NA,
        wavelength=wavelength,
        n_medium=n_medium,
        focal_length=focal_length,
        z_focus=0.0,
        truncation_coeff=truncation_coeff
    )

    params = theory.get_parameters()
    print(f"\n  Analytical Theory Parameters:")
    print(f"    Focal length: {params['focal_length']:.2f} μm")
    print(f"    Aperture diameter: {params['aperture']:.2f} μm")
    print(f"    Beam waist w0: {params['w0']:.4f} μm")
    print(f"    Rayleigh range z_R: {params['z_R']:.2f} μm")
    print(f"    Truncation coeff: {params['truncation_coeff']:.2f}")
    print(f"    Airy radius (ref): {params['airy_radius']:.4f} μm")

    # Compute radial profiles at focal plane
    n_points = 100
    r_max = 3 * rw_sim.airy_radius if NA < 0.5 else 1.5 * rw_sim.airy_radius
    r = np.linspace(0, r_max, n_points)

    print(f"\n  Computing focal plane intensity (r=0 to {r_max:.2f} μm)...")

    # Richards-Wolf
    print(f"    Richards-Wolf...")
    I_rw = rw_sim.focal_plane_intensity_pattern(r, np.zeros_like(r))
    I_rw = I_rw / I_rw.max()

    # Analytical theory
    print(f"    Analytical theory...")
    I_theory = theory.focal_plane_intensity(r, z=0.0)

    print(f"  ✓ Done")

    # Compute metrics
    def compute_fwhm(r, I):
        half_max = 0.5
        above_half = I > half_max
        if above_half.any():
            r_half = r[above_half]
            if len(r_half) > 0:
                return 2 * r_half[-1]
        return 0

    fwhm_rw = compute_fwhm(r, I_rw)
    fwhm_theory = compute_fwhm(r, I_theory)

    # Mean squared error
    mse = np.mean((I_rw - I_theory)**2)

    # Correlation
    corr = np.corrcoef(I_rw, I_theory)[0, 1]

    print(f"\n  Metrics:")
    print(f"    RW FWHM: {fwhm_rw:.4f} μm")
    print(f"    Theory FWHM: {fwhm_theory:.4f} μm")
    print(f"    FWHM ratio (RW/Theory): {fwhm_rw/fwhm_theory:.4f}")
    print(f"    MSE: {mse:.6f}")
    print(f"    Correlation: {corr:.6f}")

    # Plotting
    row = case_idx

    # Left: Radial profiles comparison
    axes[row, 0].plot(r, I_rw, 'b-', linewidth=2, label='Richards-Wolf')
    axes[row, 0].plot(r, I_theory, 'r--', linewidth=2, label='Theory (Tanaka et al.)')
    axes[row, 0].axhline(0.5, color='gray', ls=':', alpha=0.5)
    axes[row, 0].axvline(fwhm_rw/2, color='blue', ls=':', alpha=0.5)
    axes[row, 0].axvline(fwhm_theory/2, color='red', ls=':', alpha=0.5)
    axes[row, 0].set_xlabel('Radial distance r (μm)', fontsize=11)
    axes[row, 0].set_ylabel('Normalized Intensity', fontsize=11)
    axes[row, 0].set_title(f'{name} (NA={NA}): Focal Plane', fontsize=12, fontweight='bold')
    axes[row, 0].legend(fontsize=9)
    axes[row, 0].grid(True, alpha=0.3)
    axes[row, 0].set_xlim([0, r_max])

    # Middle: Residual
    residual = I_rw - I_theory
    axes[row, 1].plot(r, residual, 'g-', linewidth=2)
    axes[row, 1].axhline(0, color='black', ls='--', alpha=0.5)
    axes[row, 1].fill_between(r, residual, alpha=0.3, color='green')
    axes[row, 1].set_xlabel('Radial distance r (μm)', fontsize=11)
    axes[row, 1].set_ylabel('Residual (RW - Theory)', fontsize=11)
    axes[row, 1].set_title(f'Difference (MSE={mse:.6f})', fontsize=12, fontweight='bold')
    axes[row, 1].grid(True, alpha=0.3)
    axes[row, 1].set_xlim([0, r_max])

    # Right: Log scale comparison
    axes[row, 2].semilogy(r, I_rw, 'b-', linewidth=2, label='Richards-Wolf')
    axes[row, 2].semilogy(r, I_theory, 'r--', linewidth=2, label='Theory')
    axes[row, 2].set_xlabel('Radial distance r (μm)', fontsize=11)
    axes[row, 2].set_ylabel('Normalized Intensity (log)', fontsize=11)
    axes[row, 2].set_title(f'Log Scale (Correlation={corr:.4f})', fontsize=12, fontweight='bold')
    axes[row, 2].legend(fontsize=9)
    axes[row, 2].grid(True, alpha=0.3, which='both')
    axes[row, 2].set_xlim([0, r_max])
    axes[row, 2].set_ylim([1e-4, 1])

plt.tight_layout()
plt.savefig('data/rw_vs_theory_validation.png', dpi=200, bbox_inches='tight')
print(f"\n✓ Saved: data/rw_vs_theory_validation.png")

print(f"\n{'='*70}")
print("OVERALL ASSESSMENT")
print(f"{'='*70}")
print("Comparing Richards-Wolf with analytical Gaussian beam theory:")
print("  - Low NA: Should match well (paraxial, scalar dominates)")
print("  - High NA: May differ (vectorial effects, depolarization)")
print("\nKey observations:")
print("  - MSE shows quantitative agreement")
print("  - Correlation measures shape similarity")
print("  - Log plot reveals tail behavior")
print(f"{'='*70}")

plt.show()
