"""
Compare Tanaka analytical theory vs Richards-Wolf for different fill factors.
Low NA (0.1) only - paraxial regime where both should agree.
"""

import sys
sys.path.insert(0, '.')

import numpy as np
import matplotlib.pyplot as plt
from monte_carlo.richards_wolf import RichardsWolfSimulator
from monte_carlo.gaussian_beam_theory import FocusedGaussianBeamTheory

print("="*70)
print("Tanaka vs Richards-Wolf: Fill Factor Comparison (Low NA)")
print("="*70)

# Parameters
wavelength = 0.532
n_medium = 1.0
polarization = 'x'
NA = 0.1  # Low NA only

# Fill factors to test
fill_factors = [0.5, 0.6, 0.7, 0.8, 0.95]

# Focal length matching
aperture_default = 1500.0
theta = np.arcsin(NA / n_medium)
focal_length = (aperture_default / 2) / np.tan(theta)

print(f"\nNA = {NA}")
print(f"Wavelength = {wavelength} μm")
print(f"Focal length = {focal_length:.2f} μm")
print(f"Aperture = {aperture_default:.2f} μm")
print(f"\nFill factors: {fill_factors}")

# Storage
results = []

for ff in fill_factors:
    print(f"\n{'-'*70}")
    print(f"Fill factor = {ff} (α = {1.0/(ff**2):.2f})")
    print(f"{'-'*70}")

    # Richards-Wolf
    rw_sim = RichardsWolfSimulator(
        wavelength=wavelength,
        numerical_aperture=NA,
        n_medium=n_medium,
        polarization=polarization,
        input_field='gaussian',
        fill_factor=ff
    )

    # Analytical theory
    truncation_coeff = 1.0 / (ff**2)
    theory = FocusedGaussianBeamTheory(
        numerical_aperture=NA,
        wavelength=wavelength,
        n_medium=n_medium,
        focal_length=focal_length,
        z_focus=0.0,
        truncation_coeff=truncation_coeff
    )

    # Compute radial profiles
    n_points = 100
    r_max = 3 * rw_sim.airy_radius
    r = np.linspace(0, r_max, n_points)

    print(f"  Computing Richards-Wolf...")
    I_rw = rw_sim.focal_plane_intensity_pattern(r, np.zeros_like(r))
    I_rw = I_rw / I_rw.max()

    print(f"  Computing Tanaka theory...")
    I_theory = theory.focal_plane_intensity(r, z=0.0)

    # Metrics
    mse = np.mean((I_rw - I_theory)**2)
    corr = np.corrcoef(I_rw, I_theory)[0, 1]

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

    print(f"  MSE: {mse:.6f}")
    print(f"  Correlation: {corr:.6f}")
    print(f"  FWHM RW: {fwhm_rw:.4f} μm")
    print(f"  FWHM Theory: {fwhm_theory:.4f} μm")

    results.append({
        'fill_factor': ff,
        'truncation_coeff': truncation_coeff,
        'r': r,
        'I_rw': I_rw,
        'I_theory': I_theory,
        'mse': mse,
        'corr': corr,
        'fwhm_rw': fwhm_rw,
        'fwhm_theory': fwhm_theory,
        'airy_radius': rw_sim.airy_radius
    })

print(f"\n{'='*70}")
print("Creating plots...")
print(f"{'='*70}")

# Create comprehensive figure
fig = plt.figure(figsize=(18, 12))

# Colors for each fill factor
colors = ['purple', 'blue', 'green', 'orange', 'red']
airy_r = results[0]['airy_radius']

# Row 1: Individual comparisons (5 subplots)
for i, res in enumerate(results):
    ax = plt.subplot(3, 5, i+1)
    ax.plot(res['r'], res['I_rw'], 'b-', linewidth=2, label='RW')
    ax.plot(res['r'], res['I_theory'], 'r--', linewidth=2, label='Tanaka')
    ax.set_xlabel('r (μm)', fontsize=9)
    ax.set_ylabel('Intensity', fontsize=9)
    ax.set_title(f"fill={res['fill_factor']}\nMSE={res['mse']:.6f}", fontsize=10, fontweight='bold')
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, res['r'].max()])

# Row 2: Log scale comparisons
for i, res in enumerate(results):
    ax = plt.subplot(3, 5, 5+i+1)
    I_rw_clip = np.clip(res['I_rw'], 1e-4, 1)
    I_theory_clip = np.clip(res['I_theory'], 1e-4, 1)
    ax.semilogy(res['r'], I_rw_clip, 'b-', linewidth=2, label='RW')
    ax.semilogy(res['r'], I_theory_clip, 'r--', linewidth=2, label='Tanaka')
    ax.set_xlabel('r (μm)', fontsize=9)
    ax.set_ylabel('Intensity (log)', fontsize=9)
    ax.set_title(f"α={res['truncation_coeff']:.2f}\nCorr={res['corr']:.4f}", fontsize=10)
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3, which='both')
    ax.set_xlim([0, res['r'].max()])
    ax.set_ylim([1e-4, 2])

# Row 3: Summary plots

# MSE vs fill factor
ax_mse = plt.subplot(3, 5, 11)
ff_vals = [r['fill_factor'] for r in results]
mse_vals = [r['mse'] for r in results]
ax_mse.plot(ff_vals, mse_vals, 'o-', linewidth=2, markersize=8, color='green')
ax_mse.set_xlabel('Fill Factor', fontsize=10)
ax_mse.set_ylabel('MSE', fontsize=10)
ax_mse.set_title('MSE: RW vs Tanaka', fontsize=11, fontweight='bold')
ax_mse.grid(True, alpha=0.3)
ax_mse.axhline(0.001, color='red', ls='--', lw=1, alpha=0.5, label='Good threshold')
ax_mse.legend(fontsize=8)

# Correlation vs fill factor
ax_corr = plt.subplot(3, 5, 12)
corr_vals = [r['corr'] for r in results]
ax_corr.plot(ff_vals, corr_vals, 'o-', linewidth=2, markersize=8, color='blue')
ax_corr.set_xlabel('Fill Factor', fontsize=10)
ax_corr.set_ylabel('Correlation', fontsize=10)
ax_corr.set_title('Correlation: RW vs Tanaka', fontsize=11, fontweight='bold')
ax_corr.grid(True, alpha=0.3)
ax_corr.set_ylim([0.98, 1.005])

# FWHM comparison
ax_fwhm = plt.subplot(3, 5, 13)
fwhm_rw_vals = [r['fwhm_rw'] for r in results]
fwhm_theory_vals = [r['fwhm_theory'] for r in results]
x_pos = np.arange(len(ff_vals))
width = 0.35
ax_fwhm.bar(x_pos - width/2, fwhm_rw_vals, width, label='RW', alpha=0.7, color='blue')
ax_fwhm.bar(x_pos + width/2, fwhm_theory_vals, width, label='Tanaka', alpha=0.7, color='red')
ax_fwhm.set_xlabel('Fill Factor', fontsize=10)
ax_fwhm.set_ylabel('FWHM (μm)', fontsize=10)
ax_fwhm.set_title('FWHM Comparison', fontsize=11, fontweight='bold')
ax_fwhm.set_xticks(x_pos)
ax_fwhm.set_xticklabels([f'{ff:.2f}' for ff in ff_vals], fontsize=8)
ax_fwhm.legend(fontsize=8)
ax_fwhm.grid(True, alpha=0.3, axis='y')

# FWHM ratio
ax_ratio = plt.subplot(3, 5, 14)
fwhm_ratios = [fwhm_rw_vals[i]/fwhm_theory_vals[i] for i in range(len(ff_vals))]
ax_ratio.plot(ff_vals, fwhm_ratios, 'o-', linewidth=2, markersize=8, color='purple')
ax_ratio.axhline(1.0, color='black', ls='--', lw=1, alpha=0.5, label='Perfect match')
ax_ratio.set_xlabel('Fill Factor', fontsize=10)
ax_ratio.set_ylabel('FWHM Ratio (RW/Tanaka)', fontsize=10)
ax_ratio.set_title('FWHM Agreement', fontsize=11, fontweight='bold')
ax_ratio.grid(True, alpha=0.3)
ax_ratio.legend(fontsize=8)
ax_ratio.set_ylim([0.95, 1.15])

# Summary text
ax_text = plt.subplot(3, 5, 15)
ax_text.axis('off')
summary_text = f"NA = {NA}\\n"
summary_text += f"λ = {wavelength} μm\\n"
summary_text += f"f = {focal_length/1000:.1f} mm\\n\\n"
summary_text += "Best Match:\\n"
best_idx = np.argmin(mse_vals)
summary_text += f"  fill = {ff_vals[best_idx]}\\n"
summary_text += f"  MSE = {mse_vals[best_idx]:.6f}\\n"
summary_text += f"  Corr = {corr_vals[best_idx]:.6f}\\n"
ax_text.text(0.1, 0.5, summary_text, fontsize=10, family='monospace',
            verticalalignment='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig('data/tanaka_vs_rw_fill_comparison.png', dpi=200, bbox_inches='tight')
print("✓ Saved: data/tanaka_vs_rw_fill_comparison.png")

# Print summary table
print(f"\n{'='*70}")
print("SUMMARY TABLE")
print(f"{'='*70}")
print(f"\n{'Fill':<8} {'α':<8} {'MSE':<12} {'Corr':<10} {'FWHM RW':<12} {'FWHM Tanaka':<12} {'Ratio':<8}")
print(f"{'-'*78}")
for res in results:
    ratio = res['fwhm_rw'] / res['fwhm_theory']
    print(f"{res['fill_factor']:<8.2f} {res['truncation_coeff']:<8.2f} {res['mse']:<12.6f} "
          f"{res['corr']:<10.6f} {res['fwhm_rw']:<12.4f} {res['fwhm_theory']:<12.4f} {ratio:<8.4f}")

print(f"\n{'='*70}")
print("CONCLUSION")
print(f"{'='*70}")
best_idx = np.argmin(mse_vals)
print(f"\nBest agreement at fill_factor = {ff_vals[best_idx]}")
print(f"  MSE: {mse_vals[best_idx]:.6f}")
print(f"  Correlation: {corr_vals[best_idx]:.6f}")
print(f"\nAs fill_factor increases (α decreases):")
print(f"  → Less truncation")
print(f"  → Better RW-Tanaka agreement")
print(f"  → Both see nearly the same Gaussian beam")
print(f"{'='*70}")

plt.show()
