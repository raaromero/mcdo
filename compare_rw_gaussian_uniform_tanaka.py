"""
Compare Richards-Wolf (Gaussian input) vs Tanaka vs Richards-Wolf (Uniform input).

Three methods on the same plot:
1. Richards-Wolf with Gaussian input field
2. Tanaka (analytical Gaussian beam theory)
3. Richards-Wolf with uniform input field
"""

import sys
sys.path.insert(0, '.')

import numpy as np
import matplotlib.pyplot as plt
from monte_carlo.richards_wolf import RichardsWolfSimulator
from monte_carlo.gaussian_beam_theory import FocusedGaussianBeamTheory

print("="*80)
print("Comparison: Richards-Wolf (Gaussian) vs Tanaka vs Richards-Wolf (Uniform)")
print("="*80)

# Parameters
wavelength = 0.532
n_medium = 1.0
polarization = 'x'
NA = 0.1  # Low NA for paraxial regime where Tanaka is valid

# Truncation coefficient for Gaussian beam (Horvath & Bor, 2003)
# truncation_coeff ~1.1 corresponds to high fill factor (~0.95) for best agreement with theory
truncation_coeff = 1.108  # Equivalent to fill_factor=0.95

# Focal length (needed for Tanaka)
aperture_default = 1500.0
theta = np.arcsin(NA / n_medium)
focal_length = (aperture_default / 2) / np.tan(theta)

print(f"\nParameters:")
print(f"  Wavelength (λ):      {wavelength} μm")
print(f"  Numerical aperture:  {NA}")
print(f"  Refractive index:    {n_medium}")
print(f"  Polarization:        {polarization}")
print(f"  Truncation coeff:    {truncation_coeff:.3f}")
print(f"  Focal length:        {focal_length:.1f} μm")
print(f"  Equiv. fill factor:  {1/np.sqrt(truncation_coeff):.3f}")

# Create simulators

# 1. Richards-Wolf with Gaussian input
print("\n1. Creating Richards-Wolf simulator (Gaussian input)...")
rw_gaussian = RichardsWolfSimulator(
    wavelength=wavelength,
    numerical_aperture=NA,
    n_medium=n_medium,
    polarization=polarization,
    input_field='gaussian',
    truncation_coeff=truncation_coeff
)

# 2. Tanaka analytical theory
print("2. Creating Tanaka (analytical Gaussian beam theory)...")
tanaka = FocusedGaussianBeamTheory(
    numerical_aperture=NA,
    wavelength=wavelength,
    n_medium=n_medium,
    focal_length=focal_length,
    z_focus=0.0,
    truncation_coeff=truncation_coeff
)

# 3. Richards-Wolf with uniform input
print("3. Creating Richards-Wolf simulator (Uniform input)...")
rw_uniform = RichardsWolfSimulator(
    wavelength=wavelength,
    numerical_aperture=NA,
    n_medium=n_medium,
    polarization=polarization,
    input_field='uniform',
    truncation_coeff=1.0  # Not used for uniform, but set to 1.0
)

# Compute intensity profiles
print("\nComputing intensity profiles...")

# User requested x-axis to go to 6.4 μm
r_max = 6.4
r = np.linspace(0, r_max, 100)  # Reduced to 100 points for faster computation
z = np.zeros_like(r)  # Focal plane

# Richards-Wolf Gaussian
print("  - Richards-Wolf (Gaussian)...")
I_rw_gaussian = rw_gaussian.focal_plane_intensity_pattern(r, z)
I_rw_gaussian = I_rw_gaussian / I_rw_gaussian.max()

# Tanaka
print("  - Tanaka...")
I_tanaka = tanaka.focal_plane_intensity(r, z=0.0)
# Already normalized by Tanaka

# Richards-Wolf Uniform
print("  - Richards-Wolf (Uniform)...")
I_rw_uniform = rw_uniform.focal_plane_intensity_pattern(r, z)
I_rw_uniform = I_rw_uniform / I_rw_uniform.max()

# Compute metrics
print("\nComputing metrics...")

# MSE between RW-Gaussian and Tanaka
mse_rw_tanaka = np.mean((I_rw_gaussian - I_tanaka)**2)

# MSE between RW-Gaussian and RW-Uniform
mse_rw_gaussian_uniform = np.mean((I_rw_gaussian - I_rw_uniform)**2)

# MSE between Tanaka and RW-Uniform
mse_tanaka_uniform = np.mean((I_tanaka - I_rw_uniform)**2)

# Correlation
corr_rw_tanaka = np.corrcoef(I_rw_gaussian, I_tanaka)[0, 1]
corr_rw_gaussian_uniform = np.corrcoef(I_rw_gaussian, I_rw_uniform)[0, 1]
corr_tanaka_uniform = np.corrcoef(I_tanaka, I_rw_uniform)[0, 1]

print(f"  MSE (RW-Gaussian vs Tanaka):        {mse_rw_tanaka:.6f}")
print(f"  MSE (RW-Gaussian vs RW-Uniform):    {mse_rw_gaussian_uniform:.6f}")
print(f"  MSE (Tanaka vs RW-Uniform):         {mse_tanaka_uniform:.6f}")
print(f"  Correlation (RW-Gaussian vs Tanaka):     {corr_rw_tanaka:.6f}")
print(f"  Correlation (RW-Gaussian vs RW-Uniform): {corr_rw_gaussian_uniform:.6f}")
print(f"  Correlation (Tanaka vs RW-Uniform):      {corr_tanaka_uniform:.6f}")

# Create plot (single panel, linear scale only)
print("\nCreating comparison plot...")

fig, ax = plt.subplots(1, 1, figsize=(10, 7))

ax.plot(r, I_rw_gaussian, 'b-', linewidth=2.5, label='Richards-Wolf (Gaussian)', alpha=0.8)
ax.plot(r, I_tanaka, 'r--', linewidth=2.5, label='Tanaka', alpha=0.8)
ax.plot(r, I_rw_uniform, 'g-.', linewidth=2.5, label='Richards-Wolf (Uniform)', alpha=0.8)
ax.axhline(0.5, color='gray', linestyle=':', linewidth=1, alpha=0.5)
ax.axvline(rw_gaussian.airy_radius, color='cyan', linestyle=':', linewidth=1.5, alpha=0.7,
           label=f'Airy radius = {rw_gaussian.airy_radius:.3f} μm')
ax.set_xlabel('Radial distance r (μm)', fontsize=13)
ax.set_ylabel('Normalized Intensity', fontsize=13)
ax.set_title(f'Comparison: NA={NA}, fill={fill_factor}\n' +
             f'MSE (RW-Gauss vs Tanaka)={mse_rw_tanaka:.6f}, Corr={corr_rw_tanaka:.6f}',
             fontsize=12, fontweight='bold')
ax.legend(fontsize=11, loc='upper right')
ax.grid(True, alpha=0.3)
ax.set_xlim([0, r_max])
ax.set_ylim([0, 1.1])

plt.tight_layout()
plt.savefig('data/rw_gaussian_uniform_tanaka_comparison.png', dpi=300, bbox_inches='tight')
print("\n✓ Saved: data/rw_gaussian_uniform_tanaka_comparison.png")

# Summary table
print(f"\n{'='*80}")
print("SUMMARY")
print(f"{'='*80}")
print(f"\nMethod Comparison:")
print(f"  1. Richards-Wolf (Gaussian):  Uses Gaussian apodization with fill={fill_factor}")
print(f"  2. Tanaka:                    Analytical Gaussian beam theory (paraxial)")
print(f"  3. Richards-Wolf (Uniform):   Uniform illumination (Airy pattern)")
print(f"\nAgreement:")
print(f"  RW-Gaussian vs Tanaka:         MSE = {mse_rw_tanaka:.6f}, Corr = {corr_rw_tanaka:.6f}")
print(f"  RW-Gaussian vs RW-Uniform:     MSE = {mse_rw_gaussian_uniform:.6f}, Corr = {corr_rw_gaussian_uniform:.6f}")
print(f"  Tanaka vs RW-Uniform:          MSE = {mse_tanaka_uniform:.6f}, Corr = {corr_tanaka_uniform:.6f}")
print(f"\nInterpretation:")
if mse_rw_tanaka < 1e-4:
    print(f"  ✓ Excellent agreement between RW-Gaussian and Tanaka!")
    print(f"    (MSE < 1e-4 indicates nearly perfect match)")
else:
    print(f"  Note: MSE = {mse_rw_tanaka:.6f} indicates some difference")
    print(f"        This may be due to numerical integration errors or fill_factor")

if mse_rw_gaussian_uniform > mse_rw_tanaka:
    print(f"  ✓ RW-Uniform differs more from RW-Gaussian than Tanaka does")
    print(f"    This shows the effect of Gaussian vs uniform illumination")

print(f"\n{'='*80}")

plt.show()
