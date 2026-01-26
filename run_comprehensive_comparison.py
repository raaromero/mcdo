"""
Comprehensive Method Comparison: Debye vs Richards-Wolf

Compares three diffraction models across different NA and truncation coefficients:
1. Debye (Tanaka analytical theory for Gaussian beams)
2. Richards-Wolf (Gaussian) - Vector diffraction with Gaussian input field
3. Richards-Wolf (Uniform) - Vector diffraction with uniform input field
"""

import sys
sys.path.insert(0, '.')

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from monte_carlo.richards_wolf import RichardsWolfSimulator
from monte_carlo.gaussian_beam_theory import FocusedGaussianBeamTheory
import os

# Set style
sns.set_theme(style="whitegrid", font_scale=1.3)

# Create output directory
output_dir = 'data/comprehensive_comparison'
os.makedirs(output_dir, exist_ok=True)

print("="*80)
print("COMPREHENSIVE METHOD COMPARISON")
print("="*80)
print("✓ Imports successful\n")

# Fixed parameters
wavelength = 0.532  # μm (532 nm)
n_medium = 1.0
polarization = 'x'

# NA values to test
NA_values = [0.1, 0.5, 0.8]

# Truncation coefficients (Horvath & Bor, 2003)
truncation_coeffs = [1.1, 2.0, 2.778, 4.0, 6.25]

# Focal length for Tanaka
aperture_default = 1500.0  # μm

print(f"Wavelength: {wavelength} μm ({wavelength*1000:.0f} nm)")
print(f"NA values: {NA_values}")
print(f"Truncation coefficients: {truncation_coeffs}\n")
print("Equivalent fill factors:")
for tc in truncation_coeffs:
    ff = 1 / np.sqrt(tc)
    status = "untruncated" if tc >= 4 else "truncated"
    print(f"  α={tc:5.2f} → fill={ff:.3f} ({status})")

# Helper functions
def compute_fwhm(r, I):
    """Compute Full Width at Half Maximum."""
    half_max = 0.5
    above_half = I > half_max
    if above_half.any():
        r_half = r[above_half]
        if len(r_half) > 0:
            return 2 * r_half[-1]
    return np.nan

def compute_metrics(I1, I2):
    """Compute comparison metrics between two intensity profiles."""
    mse = np.mean((I1 - I2)**2)
    corr = np.corrcoef(I1, I2)[0, 1]
    max_diff = np.max(np.abs(I1 - I2))
    return {'mse': mse, 'corr': corr, 'max_diff': max_diff}

# Storage for all results
all_results = {}

print("\n" + "="*80)
print("RUNNING COMPARISONS")
print("="*80)

for NA in NA_values:
    print(f"\n{'='*70}")
    print(f"NA = {NA}")
    print(f"{'='*70}")

    # Calculate focal length for this NA
    theta = np.arcsin(NA / n_medium)
    focal_length = (aperture_default / 2) / np.tan(theta)
    print(f"Focal length: {focal_length:.2f} μm")

    all_results[NA] = {}

    for trunc_coeff in truncation_coeffs:
        print(f"\n  α = {trunc_coeff:.3f} (fill = {1/np.sqrt(trunc_coeff):.3f})")

        # Create simulators
        # 1. Debye (Tanaka analytical)
        debye = FocusedGaussianBeamTheory(
            numerical_aperture=NA,
            wavelength=wavelength,
            n_medium=n_medium,
            focal_length=focal_length,
            z_focus=0.0,
            truncation_coeff=trunc_coeff
        )

        # 2. Richards-Wolf with Gaussian
        rw_gaussian = RichardsWolfSimulator(
            wavelength=wavelength,
            numerical_aperture=NA,
            n_medium=n_medium,
            polarization=polarization,
            input_field='gaussian',
            truncation_coeff=trunc_coeff
        )

        # 3. Richards-Wolf with Uniform
        rw_uniform = RichardsWolfSimulator(
            wavelength=wavelength,
            numerical_aperture=NA,
            n_medium=n_medium,
            polarization=polarization,
            input_field='uniform',
            truncation_coeff=1.0
        )

        # Set up radial grid
        airy_r = rw_uniform.airy_radius
        n_points = 150
        r_max = 4 * airy_r if NA < 0.3 else 2 * airy_r
        r = np.linspace(0, r_max, n_points)

        # Compute intensities
        print(f"    Computing Debye...", end=" ")
        I_debye = debye.focal_plane_intensity(r, z=0.0)
        print("✓")

        print(f"    Computing RW-Gaussian...", end=" ")
        I_rw_gauss = rw_gaussian.focal_plane_intensity_pattern(r, np.zeros_like(r))
        print("✓")

        print(f"    Computing RW-Uniform...", end=" ")
        I_rw_uniform = rw_uniform.focal_plane_intensity_pattern(r, np.zeros_like(r))
        print("✓")

        # Normalize
        I_debye = I_debye / I_debye.max()
        I_rw_gauss = I_rw_gauss / I_rw_gauss.max()
        I_rw_uniform = I_rw_uniform / I_rw_uniform.max()

        # Compute metrics
        fwhm_debye = compute_fwhm(r, I_debye)
        fwhm_rw_gauss = compute_fwhm(r, I_rw_gauss)
        fwhm_rw_uniform = compute_fwhm(r, I_rw_uniform)

        metrics_debye_vs_rw_gauss = compute_metrics(I_debye, I_rw_gauss)
        metrics_debye_vs_rw_uniform = compute_metrics(I_debye, I_rw_uniform)

        print(f"    FWHM - Debye: {fwhm_debye:.4f}, RW-Gauss: {fwhm_rw_gauss:.4f}, RW-Uniform: {fwhm_rw_uniform:.4f} μm")
        print(f"    MSE (Debye vs RW-Gauss): {metrics_debye_vs_rw_gauss['mse']:.6f}")
        print(f"    Corr (Debye vs RW-Gauss): {metrics_debye_vs_rw_gauss['corr']:.6f}")

        # Store results
        all_results[NA][trunc_coeff] = {
            'r': r,
            'I_debye': I_debye,
            'I_rw_gauss': I_rw_gauss,
            'I_rw_uniform': I_rw_uniform,
            'fwhm_debye': fwhm_debye,
            'fwhm_rw_gauss': fwhm_rw_gauss,
            'fwhm_rw_uniform': fwhm_rw_uniform,
            'metrics_dg': metrics_debye_vs_rw_gauss,
            'metrics_du': metrics_debye_vs_rw_uniform,
            'airy_radius': airy_r
        }

print(f"\n{'='*70}")
print("✓ All computations complete")
print(f"{'='*70}")

# Generate individual plots
print("\n" + "="*80)
print("GENERATING INDIVIDUAL PLOTS")
print("="*80 + "\n")

for NA in NA_values:
    for trunc_coeff in truncation_coeffs:
        data = all_results[NA][trunc_coeff]

        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # Linear scale
        ax = axes[0]
        ax.plot(data['r'], data['I_debye'], 'b-', linewidth=2.5, label='Debye (Tanaka)', alpha=0.8)
        ax.plot(data['r'], data['I_rw_gauss'], 'r--', linewidth=2, label='RW-Gaussian', alpha=0.8)
        ax.plot(data['r'], data['I_rw_uniform'], 'g:', linewidth=2, label='RW-Uniform', alpha=0.8)
        ax.axvline(data['airy_radius'], color='gray', ls='-.', lw=1.5, alpha=0.5, label=f'Airy r={data["airy_radius"]:.3f} μm')
        ax.axhline(0.5, color='gray', ls='--', lw=1, alpha=0.3)
        ax.set_xlabel('Radial distance r (μm)', fontsize=12)
        ax.set_ylabel('Normalized Intensity', fontsize=12)
        ax.set_title(f'NA={NA}, α={trunc_coeff:.2f} (fill={1/np.sqrt(trunc_coeff):.2f})',
                     fontsize=13, fontweight='bold')
        ax.legend(fontsize=10, loc='upper right')
        ax.grid(True, alpha=0.3)
        ax.set_xlim([0, data['r'].max()])
        ax.set_ylim([0, 1.1])

        # Log scale
        ax = axes[1]
        ax.semilogy(data['r'], np.clip(data['I_debye'], 1e-4, 1), 'b-', linewidth=2.5, label='Debye', alpha=0.8)
        ax.semilogy(data['r'], np.clip(data['I_rw_gauss'], 1e-4, 1), 'r--', linewidth=2, label='RW-Gauss', alpha=0.8)
        ax.semilogy(data['r'], np.clip(data['I_rw_uniform'], 1e-4, 1), 'g:', linewidth=2, label='RW-Uniform', alpha=0.8)
        ax.axvline(data['airy_radius'], color='gray', ls='-.', lw=1.5, alpha=0.5)
        ax.set_xlabel('Radial distance r (μm)', fontsize=12)
        ax.set_ylabel('Normalized Intensity (log)', fontsize=12)
        ax.set_title('Log Scale (shows tails)', fontsize=13, fontweight='bold')
        ax.legend(fontsize=10, loc='upper right')
        ax.grid(True, alpha=0.3, which='both')
        ax.set_xlim([0, data['r'].max()])
        ax.set_ylim([1e-4, 2])

        # Add metrics text
        metrics_text = f"FWHM: D={data['fwhm_debye']:.3f}, RG={data['fwhm_rw_gauss']:.3f}, RU={data['fwhm_rw_uniform']:.3f} μm\n"
        metrics_text += f"MSE(D-RG)={data['metrics_dg']['mse']:.5f}, Corr={data['metrics_dg']['corr']:.4f}"
        fig.text(0.5, 0.02, metrics_text, ha='center', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

        plt.tight_layout(rect=[0, 0.05, 1, 1])

        # Save
        filename = f'{output_dir}/NA_{NA:.1f}_alpha_{trunc_coeff:.2f}.png'
        plt.savefig(filename, dpi=200, bbox_inches='tight')
        plt.close()

        print(f"  ✓ Saved: {filename}")

print(f"\n✓ All individual plots saved to {output_dir}/")

# Summary grid plot
print("\n" + "="*80)
print("GENERATING SUMMARY GRID")
print("="*80 + "\n")

n_rows = len(NA_values)
n_cols = len(truncation_coeffs)

fig, axes = plt.subplots(n_rows, n_cols, figsize=(5*n_cols, 4*n_rows))

for i, NA in enumerate(NA_values):
    for j, trunc_coeff in enumerate(truncation_coeffs):
        ax = axes[i, j] if n_rows > 1 else axes[j]
        data = all_results[NA][trunc_coeff]

        # Plot
        ax.plot(data['r'], data['I_debye'], 'b-', linewidth=2, label='Debye', alpha=0.8)
        ax.plot(data['r'], data['I_rw_gauss'], 'r--', linewidth=1.5, label='RW-Gauss', alpha=0.8)
        ax.plot(data['r'], data['I_rw_uniform'], 'g:', linewidth=1.5, label='RW-Uniform', alpha=0.7)
        ax.axvline(data['airy_radius'], color='gray', ls='-.', lw=1, alpha=0.4)

        # Labels
        if j == 0:
            ax.set_ylabel(f'NA={NA}\nIntensity', fontsize=11, fontweight='bold')
        if i == n_rows - 1:
            ax.set_xlabel(f'α={trunc_coeff:.2f}\nr (μm)', fontsize=10)
        if i == 0 and j == 0:
            ax.legend(fontsize=8, loc='upper right')

        # Title on top row
        if i == 0:
            fill_eq = 1 / np.sqrt(trunc_coeff)
            ax.set_title(f'fill={fill_eq:.2f}', fontsize=10)

        ax.grid(True, alpha=0.25)
        ax.set_xlim([0, data['r'].max()])
        ax.set_ylim([0, 1.1])

plt.tight_layout()
plt.savefig(f'{output_dir}/summary_grid.png', dpi=200, bbox_inches='tight')
print(f"✓ Saved: {output_dir}/summary_grid.png")

# Metrics summary
print("\n" + "="*80)
print("SUMMARY: Debye vs Richards-Wolf Gaussian Agreement")
print("="*80)

for NA in NA_values:
    print(f"\nNA = {NA}:")
    print(f"  {'α':>6} {'fill':>6} {'MSE':>10} {'Corr':>8} {'FWHM Diff':>12}")
    print(f"  {'-'*50}")

    for trunc_coeff in truncation_coeffs:
        data = all_results[NA][trunc_coeff]
        fill = 1 / np.sqrt(trunc_coeff)
        mse = data['metrics_dg']['mse']
        corr = data['metrics_dg']['corr']
        fwhm_diff = abs(data['fwhm_debye'] - data['fwhm_rw_gauss'])

        print(f"  {trunc_coeff:6.2f} {fill:6.3f} {mse:10.6f} {corr:8.5f} {fwhm_diff:12.4f} μm")

print("\n" + "="*80)
print("KEY OBSERVATIONS")
print("="*80)
print("")
print("1. **Low NA (0.1)**: Debye and RW-Gaussian should agree well (paraxial regime)")
print("2. **High NA (0.5-0.8)**: Vector effects become important, some divergence expected")
print("3. **Truncation effects**:")
print("   - α ≥ 4 (untruncated): Cleanest Gaussian beam behavior")
print("   - α < 4 (truncated): Beam clipped by aperture, approaches uniform")
print("   - α → 1 (heavily truncated): RW-Gaussian → RW-Uniform")
print("="*80)

# Convergence analysis
print("\n" + "="*80)
print("CONVERGENCE: RW-Gaussian → RW-Uniform as α → 1")
print("="*80)

for NA in NA_values:
    print(f"\nNA = {NA}:")
    print(f"  {'α':>6} {'MSE(RG-RU)':>15} {'Corr(RG-RU)':>15}")
    print(f"  {'-'*40}")

    for trunc_coeff in truncation_coeffs:
        data = all_results[NA][trunc_coeff]
        metrics_rg_ru = compute_metrics(data['I_rw_gauss'], data['I_rw_uniform'])

        print(f"  {trunc_coeff:6.2f} {metrics_rg_ru['mse']:15.6f} {metrics_rg_ru['corr']:15.6f}")

print("\n→ As α → 1, Gaussian input becomes heavily truncated and approaches uniform")
print("→ MSE and correlation show convergence behavior")
print("="*80)

print("\n" + "="*80)
print("✓ ANALYSIS COMPLETE!")
print("="*80)
print(f"\nAll plots saved to: {output_dir}/")
print(f"  - {len(NA_values) * len(truncation_coeffs)} individual comparison plots")
print(f"  - 1 summary grid plot")
print("="*80)
