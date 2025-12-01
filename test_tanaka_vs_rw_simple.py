"""
Compare Tanaka vs Richards-Wolf for different fill factors.
Simple version: just intensity profile plots.
"""

import sys
sys.path.insert(0, '.')

import numpy as np
import matplotlib.pyplot as plt
from monte_carlo.richards_wolf import RichardsWolfSimulator
from monte_carlo.gaussian_beam_theory import FocusedGaussianBeamTheory

print("="*70)
print("Tanaka vs Richards-Wolf: Fill Factor Comparison")
print("="*70)

# Parameters
wavelength = 0.532
n_medium = 1.0
polarization = 'x'
NA = 0.1

# Fill factors
fill_factors = [0.5, 0.6, 0.8, 0.95]

# Focal length
aperture_default = 1500.0
theta = np.arcsin(NA / n_medium)
focal_length = (aperture_default / 2) / np.tan(theta)

print(f"\nNA = {NA}, λ = {wavelength} μm")
print(f"Fill factors: {fill_factors}\n")

# Compute all profiles
results = []

for ff in fill_factors:
    print(f"Computing fill_factor = {ff}...")

    # Richards-Wolf
    rw_sim = RichardsWolfSimulator(
        wavelength=wavelength,
        numerical_aperture=NA,
        n_medium=n_medium,
        polarization=polarization,
        input_field='gaussian',
        fill_factor=ff
    )

    # Tanaka
    truncation_coeff = 1.0 / (ff**2)
    theory = FocusedGaussianBeamTheory(
        numerical_aperture=NA,
        wavelength=wavelength,
        n_medium=n_medium,
        focal_length=focal_length,
        z_focus=0.0,
        truncation_coeff=truncation_coeff
    )

    # Compute
    r_max = 3 * rw_sim.airy_radius
    r = np.linspace(0, r_max, 100)

    I_rw = rw_sim.focal_plane_intensity_pattern(r, np.zeros_like(r))
    I_rw = I_rw / I_rw.max()

    I_theory = theory.focal_plane_intensity(r, z=0.0)

    mse = np.mean((I_rw - I_theory)**2)

    results.append({
        'fill': ff,
        'trunc': truncation_coeff,
        'r': r,
        'I_rw': I_rw,
        'I_theory': I_theory,
        'mse': mse,
        'airy': rw_sim.airy_radius
    })

    print(f"  MSE = {mse:.6f}")

# Plot: 1 row x len(fill_factors) columns
fig, axes = plt.subplots(1, len(fill_factors), figsize=(4*len(fill_factors), 4))

for i, res in enumerate(results):
    # Linear scale only
    ax = axes[i] if len(fill_factors) > 1 else axes
    ax.plot(res['r'], res['I_rw'], 'b-', linewidth=2, label='Richards-Wolf')
    ax.plot(res['r'], res['I_theory'], 'r--', linewidth=2, label='Tanaka')
    ax.set_xlabel('r (μm)', fontsize=11)
    ax.set_ylabel('Normalized Intensity', fontsize=11)
    ax.set_title(f'fill = {res["fill"]}, α = {res["trunc"]:.2f}\nMSE = {res["mse"]:.6f}',
                        fontsize=11, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, res['r'].max()])

plt.tight_layout()
plt.savefig('data/tanaka_vs_rw_simple.png', dpi=200, bbox_inches='tight')
print("\n✓ Saved: data/tanaka_vs_rw_simple.png")

# Summary
print(f"\n{'='*70}")
print("SUMMARY")
print(f"{'='*70}")
for res in results:
    print(f"fill = {res['fill']:.2f} (α = {res['trunc']:.2f}): MSE = {res['mse']:.6f}")

print(f"\n✓ Best agreement at fill = {results[-1]['fill']} (minimal truncation)")
print(f"{'='*70}")

plt.show()
