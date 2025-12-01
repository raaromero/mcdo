"""
Validate Richards-Wolf Gaussian implementation against theoretical focused Gaussian beam.

Compares numerical Richards-Wolf integration with Gaussian input field against
analytical predictions for focused Gaussian beam focal plane intensity.
"""

import sys
sys.path.insert(0, '.')

import numpy as np
import matplotlib.pyplot as plt
from monte_carlo.richards_wolf import RichardsWolfSimulator

print("="*70)
print("Richards-Wolf Gaussian: Comparison with Theory")
print("="*70)

# Parameters
wavelength = 0.532  # microns
n_medium = 1.0
polarization = 'x'

# Test both low and high NA
test_cases = [
    {'NA': 0.1, 'fill_factor': 0.6, 'name': 'Low NA'},
    {'NA': 0.9, 'fill_factor': 0.6, 'name': 'High NA'}
]

for case in test_cases:
    NA = case['NA']
    fill_factor = case['fill_factor']
    name = case['name']

    print(f"\n{'='*70}")
    print(f"{name}: NA={NA}, fill_factor={fill_factor}")
    print(f"{'='*70}")

    # Create Richards-Wolf simulator with Gaussian input
    sim = RichardsWolfSimulator(
        wavelength=wavelength,
        numerical_aperture=NA,
        n_medium=n_medium,
        polarization=polarization,
        input_field='gaussian',
        fill_factor=fill_factor
    )

    print(f"  Airy radius: {sim.airy_radius:.4f} μm")
    print(f"  Angular aperture: {np.degrees(sim.angular_aperture):.2f}°")

    # Theoretical focused Gaussian beam parameters
    # For a Gaussian beam truncated by aperture:
    # - Incident beam waist at lens: w_incident = fill_factor * aperture_radius
    # - Effective focal spot size depends on truncation

    # Aperture radius
    aperture_radius = NA * wavelength / (n_medium * np.sin(np.arcsin(NA/n_medium)))
    # Actually simpler: from geometry
    focal_length = sim.airy_radius * np.pi / (1.22 * 2)  # rough estimate
    # Better: use NA = n*sin(theta) ~ n*r/f for small angles
    if NA < 0.3:
        focal_length = aperture_radius * n_medium / NA  # paraxial
    else:
        focal_length = aperture_radius / np.tan(np.arcsin(NA/n_medium))

    # Incident beam waist (1/e^2 radius)
    w_incident = fill_factor * aperture_radius

    # For a Gaussian beam through a lens, the focal spot size is:
    # w0 = (λ*f) / (π*w_incident) for w_incident >> λ
    # This is the diffraction-limited spot size
    w0_theory = (wavelength * focal_length) / (np.pi * w_incident)

    print(f"\n  Theoretical Parameters:")
    print(f"    Focal length (estimated): {focal_length:.2f} μm")
    print(f"    Incident beam waist: {w_incident:.4f} μm")
    print(f"    Expected focal spot w0: {w0_theory:.4f} μm")

    # Compute radial profile with Richards-Wolf
    n_points = 100
    r_max = 5 * w0_theory if w0_theory > 0.5 else 2.0
    r = np.linspace(0, r_max, n_points)

    print(f"\n  Computing Richards-Wolf radial profile (r=0 to {r_max:.2f} μm)...")
    I_rw = sim.focal_plane_intensity_pattern(r, np.zeros_like(r))

    # Theoretical Gaussian intensity at focal plane
    # I(r) = exp(-2*r^2 / w0^2)
    I_theory = np.exp(-2 * r**2 / w0_theory**2)

    # Normalize both to peak = 1
    I_rw = I_rw / I_rw.max()
    I_theory = I_theory / I_theory.max()

    print(f"  ✓ Done")

    # Compute FWHM for both
    def compute_fwhm(r, I):
        half_max = 0.5
        above_half = I > half_max
        if above_half.any():
            r_half = r[above_half]
            return 2 * r_half[-1]
        return 0

    fwhm_rw = compute_fwhm(r, I_rw)
    fwhm_theory = compute_fwhm(r, I_theory)

    # For Gaussian, FWHM = 2*sqrt(ln(2)) * w0 ≈ 1.177 * w0
    fwhm_theory_exact = 2 * np.sqrt(np.log(2)) * w0_theory

    print(f"\n  FWHM Comparison:")
    print(f"    Richards-Wolf: {fwhm_rw:.4f} μm")
    print(f"    Theory (from profile): {fwhm_theory:.4f} μm")
    print(f"    Theory (exact Gaussian): {fwhm_theory_exact:.4f} μm")
    print(f"    RW/Theory ratio: {fwhm_rw/fwhm_theory_exact:.3f}")

    # Compute mean squared error
    mse = np.mean((I_rw - I_theory)**2)
    print(f"\n  Mean Squared Error: {mse:.6f}")

    # Plot comparison
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Radial profiles
    axes[0].plot(r, I_rw, 'b-', linewidth=2, label='Richards-Wolf (Gaussian input)')
    axes[0].plot(r, I_theory, 'r--', linewidth=2, label=f'Theory (Gaussian w0={w0_theory:.3f} μm)')
    axes[0].axhline(0.5, color='gray', ls=':', alpha=0.5)
    axes[0].axvline(fwhm_rw/2, color='blue', ls=':', alpha=0.5, label=f'RW FWHM/2={fwhm_rw/2:.3f}')
    axes[0].axvline(fwhm_theory_exact/2, color='red', ls=':', alpha=0.5, label=f'Theory FWHM/2={fwhm_theory_exact/2:.3f}')
    axes[0].set_xlabel('Radial distance r (μm)', fontsize=12)
    axes[0].set_ylabel('Normalized Intensity', fontsize=12)
    axes[0].set_title(f'{name} (NA={NA}): Radial Profile', fontsize=14, fontweight='bold')
    axes[0].legend(fontsize=9)
    axes[0].grid(True, alpha=0.3)
    axes[0].set_xlim([0, r_max])

    # Residuals
    residual = I_rw - I_theory
    axes[1].plot(r, residual, 'g-', linewidth=2)
    axes[1].axhline(0, color='black', ls='--', alpha=0.5)
    axes[1].fill_between(r, residual, alpha=0.3, color='green')
    axes[1].set_xlabel('Radial distance r (μm)', fontsize=12)
    axes[1].set_ylabel('Residual (RW - Theory)', fontsize=12)
    axes[1].set_title(f'Difference (MSE={mse:.6f})', fontsize=14, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    axes[1].set_xlim([0, r_max])

    plt.tight_layout()

    filename = f'data/rw_gaussian_theory_{name.lower().replace(" ", "_")}_NA{NA}.png'
    plt.savefig(filename, dpi=200, bbox_inches='tight')
    print(f"\n  ✓ Saved: {filename}")
    plt.close()

print(f"\n{'='*70}")
print("OVERALL CONCLUSIONS")
print(f"{'='*70}")
print("Comparing Richards-Wolf Gaussian implementation with theory:")
print("  - Low NA: Should match Gaussian beam theory well (paraxial)")
print("  - High NA: May deviate due to vectorial effects and tight focusing")
print(f"{'='*70}")
