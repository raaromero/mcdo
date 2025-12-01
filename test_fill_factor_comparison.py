"""
Compare focal plane intensity patterns for different fill factors.

Shows how Gaussian beam truncation affects the focal spot for:
- Low NA (0.1) - paraxial regime
- High NA (0.9) - vectorial regime
"""

import sys
sys.path.insert(0, '.')

import numpy as np
import matplotlib.pyplot as plt
from monte_carlo.richards_wolf import RichardsWolfSimulator
from monte_carlo.gaussian_beam_theory import FocusedGaussianBeamTheory

print("="*70)
print("Fill Factor Comparison: Low vs High NA")
print("="*70)

# Parameters
wavelength = 0.532
n_medium = 1.0
polarization = 'x'

# Test different fill factors
fill_factors = [0.4, 0.6, 0.8, 0.95]

# Two NAs
NA_values = [0.1, 0.9]

# Colors for plots
colors = ['purple', 'blue', 'green', 'red']
labels = ['fill=0.4 (truncated)', 'fill=0.6 (moderate)', 'fill=0.8 (minimal)', 'fill=0.95 (untruncated)']

print(f"\nWavelength: {wavelength} μm")
print(f"Fill factors: {fill_factors}")
print(f"NAs: {NA_values}")

# Storage
results = {}

for NA in NA_values:
    print(f"\n{'='*70}")
    print(f"Computing NA = {NA}")
    print(f"{'='*70}")

    results[NA] = {}

    # Set up radial grid
    n_points = 150

    # Reference simulator for Airy radius
    ref_sim = RichardsWolfSimulator(
        wavelength=wavelength,
        numerical_aperture=NA,
        n_medium=n_medium,
        polarization=polarization,
        input_field='gaussian',
        fill_factor=0.6
    )

    r_max = 4 * ref_sim.airy_radius if NA < 0.5 else 1.5 * ref_sim.airy_radius
    r = np.linspace(0, r_max, n_points)

    for ff in fill_factors:
        print(f"  Computing fill_factor = {ff}...")

        # Richards-Wolf
        rw_sim = RichardsWolfSimulator(
            wavelength=wavelength,
            numerical_aperture=NA,
            n_medium=n_medium,
            polarization=polarization,
            input_field='gaussian',
            fill_factor=ff
        )

        I = rw_sim.focal_plane_intensity_pattern(r, np.zeros_like(r))
        I = I / I.max()

        # Compute FWHM
        def compute_fwhm(r, I):
            half_max = 0.5
            above_half = I > half_max
            if above_half.any():
                r_half = r[above_half]
                if len(r_half) > 0:
                    return 2 * r_half[-1]
            return 0

        fwhm = compute_fwhm(r, I)

        results[NA][ff] = {
            'r': r,
            'I': I,
            'fwhm': fwhm,
            'airy_radius': rw_sim.airy_radius
        }

        print(f"    FWHM: {fwhm:.4f} μm, Peak: {I.max():.4f}")

print(f"\n{'='*70}")
print("Creating plots...")
print(f"{'='*70}")

# Create figure with 2 rows (one per NA) x 3 columns
fig = plt.figure(figsize=(18, 10))

for row, NA in enumerate(NA_values):

    # Get data
    data = results[NA]
    airy_r = data[fill_factors[0]]['airy_radius']

    # Column 1: Linear scale radial profiles
    ax1 = plt.subplot(2, 3, row*3 + 1)
    for i, ff in enumerate(fill_factors):
        r = data[ff]['r']
        I = data[ff]['I']
        ax1.plot(r, I, color=colors[i], linewidth=2, label=labels[i])

    ax1.axvline(airy_r, color='cyan', ls=':', lw=1.5, alpha=0.7, label=f'Airy r={airy_r:.3f} μm')
    ax1.axhline(0.5, color='gray', ls='--', lw=1, alpha=0.5)
    ax1.set_xlabel('Radial distance r (μm)', fontsize=11)
    ax1.set_ylabel('Normalized Intensity', fontsize=11)
    ax1.set_title(f'NA={NA}: Radial Profiles', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=8, loc='upper right')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([0, data[fill_factors[0]]['r'].max()])
    ax1.set_ylim([0, 1.1])

    # Column 2: Log scale (shows tails)
    ax2 = plt.subplot(2, 3, row*3 + 2)
    for i, ff in enumerate(fill_factors):
        r = data[ff]['r']
        I = data[ff]['I']
        I_log = np.clip(I, 1e-4, 1)  # Clip for log plot
        ax2.semilogy(r, I_log, color=colors[i], linewidth=2, label=labels[i])

    ax2.axvline(airy_r, color='cyan', ls=':', lw=1.5, alpha=0.7)
    ax2.set_xlabel('Radial distance r (μm)', fontsize=11)
    ax2.set_ylabel('Normalized Intensity (log)', fontsize=11)
    ax2.set_title(f'NA={NA}: Log Scale', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=8, loc='upper right')
    ax2.grid(True, alpha=0.3, which='both')
    ax2.set_xlim([0, data[fill_factors[0]]['r'].max()])
    ax2.set_ylim([1e-4, 2])

    # Column 3: FWHM comparison
    ax3 = plt.subplot(2, 3, row*3 + 3)
    fwhm_values = [data[ff]['fwhm'] for ff in fill_factors]
    trunc_coeffs = [1.0/(ff**2) for ff in fill_factors]

    ax3.bar(range(len(fill_factors)), fwhm_values, color=colors, alpha=0.7, edgecolor='black')
    ax3.axhline(airy_r, color='cyan', ls='--', lw=2, label=f'Airy radius')
    ax3.set_xticks(range(len(fill_factors)))
    ax3.set_xticklabels([f'{ff}' for ff in fill_factors])
    ax3.set_xlabel('Fill Factor', fontsize=11)
    ax3.set_ylabel('FWHM (μm)', fontsize=11)
    ax3.set_title(f'NA={NA}: FWHM vs Fill Factor', fontsize=12, fontweight='bold')
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3, axis='y')

    # Add truncation coefficient as secondary labels
    for i, (ff, tc) in enumerate(zip(fill_factors, trunc_coeffs)):
        ax3.text(i, fwhm_values[i] + 0.05*max(fwhm_values), f'α={tc:.2f}',
                ha='center', va='bottom', fontsize=8)

plt.tight_layout()
plt.savefig('data/fill_factor_comparison_na.png', dpi=200, bbox_inches='tight')
print("\n✓ Saved: data/fill_factor_comparison_na.png")

# Summary table
print(f"\n{'='*70}")
print("SUMMARY TABLE")
print(f"{'='*70}")

for NA in NA_values:
    print(f"\nNA = {NA}:")
    print(f"  {'Fill':<8} {'α':<8} {'FWHM (μm)':<12} {'FWHM/Airy':<12}")
    print(f"  {'-'*44}")
    airy_r = results[NA][fill_factors[0]]['airy_radius']
    for ff in fill_factors:
        trunc_coeff = 1.0/(ff**2)
        fwhm = results[NA][ff]['fwhm']
        ratio = fwhm / airy_r
        print(f"  {ff:<8.2f} {trunc_coeff:<8.2f} {fwhm:<12.4f} {ratio:<12.4f}")

print(f"\n{'='*70}")
print("KEY OBSERVATIONS")
print(f"{'='*70}")

print("\nLow NA (0.1):")
print("  - Higher fill factor → Narrower FWHM")
print("  - fill=0.95 approaches uniform illumination (sharpest spot)")
print("  - Minimal differences (paraxial regime)")

print("\nHigh NA (0.9):")
print("  - More dramatic differences between fill factors")
print("  - Vectorial effects modify the relationship")
print("  - Lower fill (more truncation) → broader, smoother spot")

print(f"\n{'='*70}")

plt.show()
