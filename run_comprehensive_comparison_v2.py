"""
Comprehensive Method Comparison: Debye vs Richards-Wolf

Compares three diffraction models across different NA and truncation coefficients:
1. Debye - Scalar analytical theory for Gaussian beams (Horvath & Bor, 2003)
2. Richards-Wolf (Gaussian) - Vector diffraction with Gaussian input field
3. Richards-Wolf (Uniform) - Vector diffraction with uniform input field
"""

import sys
sys.path.insert(0, '.')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from monte_carlo.richards_wolf import RichardsWolfSimulator
from monte_carlo.gaussian_beam_theory import FocusedGaussianBeamTheory
import os

sns.set_theme(style="whitegrid", font_scale=1.3)

output_dir = 'data/comprehensive_comparison'
os.makedirs(output_dir, exist_ok=True)

print("="*80)
print("COMPREHENSIVE METHOD COMPARISON (v2 - Fixed Gaussian Apodization)")
print("="*80)
print("✓ Imports successful\n")

# Fixed parameters
wavelength = 0.532
n_medium = 1.0
polarization = 'x'

# NA values
NA_values = [0.1, 0.5, 0.8]

# Truncation coefficients
truncation_coeffs = [1.1, 2.0, 2.778, 4.0, 6.25]

aperture_default = 1500.0

print(f"Wavelength: {wavelength} μm ({wavelength*1000:.0f} nm)")
print(f"NA values: {NA_values}")
print(f"Truncation coefficients (α): {truncation_coeffs}\n")

# Helper functions
def compute_fwhm(r, I):
    half_max = 0.5
    above_half = I > half_max
    if above_half.any():
        r_half = r[above_half]
        if len(r_half) > 0:
            return 2 * r_half[-1]
    return np.nan

def compute_metrics(I1, I2):
    mse = np.mean((I1 - I2)**2)
    corr = np.corrcoef(I1, I2)[0, 1]
    max_diff = np.max(np.abs(I1 - I2))
    return {'mse': mse, 'corr': corr, 'max_diff': max_diff}

# Storage
all_results = {}

print("\n" + "="*80)
print("RUNNING COMPARISONS")
print("="*80)

for NA in NA_values:
    print(f"\n{'='*70}")
    print(f"NA = {NA}")
    print(f"{'='*70}")

    theta = np.arcsin(NA / n_medium)
    focal_length = (aperture_default / 2) / np.tan(theta)
    print(f"Focal length: {focal_length:.2f} μm")

    all_results[NA] = {}

    for trunc_coeff in truncation_coeffs:
        print(f"\n  α = {trunc_coeff:.3f}")

        # 1. Debye
        debye = FocusedGaussianBeamTheory(
            numerical_aperture=NA,
            wavelength=wavelength,
            n_medium=n_medium,
            focal_length=focal_length,
            z_focus=0.0,
            truncation_coeff=trunc_coeff
        )

        # 2. RW Gaussian
        rw_gaussian = RichardsWolfSimulator(
            wavelength=wavelength,
            numerical_aperture=NA,
            n_medium=n_medium,
            polarization=polarization,
            input_field='gaussian',
            truncation_coeff=trunc_coeff
        )

        # 3. RW Uniform
        rw_uniform = RichardsWolfSimulator(
            wavelength=wavelength,
            numerical_aperture=NA,
            n_medium=n_medium,
            polarization=polarization,
            input_field='uniform',
            truncation_coeff=1.0
        )

        # Radial grid
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

        # Metrics
        fwhm_debye = compute_fwhm(r, I_debye)
        fwhm_rw_gauss = compute_fwhm(r, I_rw_gauss)
        fwhm_rw_uniform = compute_fwhm(r, I_rw_uniform)

        metrics_dg = compute_metrics(I_debye, I_rw_gauss)
        metrics_du = compute_metrics(I_debye, I_rw_uniform)

        print(f"    FWHM - Debye: {fwhm_debye:.4f}, RW-Gauss: {fwhm_rw_gauss:.4f}, RW-Uniform: {fwhm_rw_uniform:.4f} μm")
        print(f"    MSE (Debye-RWGauss): {metrics_dg['mse']:.6f}, Corr: {metrics_dg['corr']:.6f}")

        # Store
        all_results[NA][trunc_coeff] = {
            'r': r,
            'I_debye': I_debye,
            'I_rw_gauss': I_rw_gauss,
            'I_rw_uniform': I_rw_uniform,
            'fwhm_debye': fwhm_debye,
            'fwhm_rw_gauss': fwhm_rw_gauss,
            'fwhm_rw_uniform': fwhm_rw_uniform,
            'metrics_dg': metrics_dg,
            'metrics_du': metrics_du,
            'airy_radius': airy_r
        }

print(f"\n{'='*70}")
print("✓ All computations complete")
print(f"{'='*70}")

# Individual plots
print("\n" + "="*80)
print("GENERATING INDIVIDUAL PLOTS")
print("="*80 + "\n")

for NA in NA_values:
    for trunc_coeff in truncation_coeffs:
        data = all_results[NA][trunc_coeff]

        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # Linear
        ax = axes[0]
        ax.plot(data['r'], data['I_debye'], 'b-', linewidth=2.5, label='Debye (Gaussian)', alpha=0.8)
        ax.plot(data['r'], data['I_rw_gauss'], 'r--', linewidth=2, label='Richards-Wolf (Gaussian)', alpha=0.8)
        ax.plot(data['r'], data['I_rw_uniform'], 'g:', linewidth=2, label='Richards-Wolf (Uniform)', alpha=0.8)
        ax.axvline(data['airy_radius'], color='gray', ls='-.', lw=1.5, alpha=0.5, label=f'Airy r={data["airy_radius"]:.3f} μm')
        ax.axhline(0.5, color='gray', ls='--', lw=1, alpha=0.3)
        ax.set_xlabel('Radial distance r (μm)', fontsize=12)
        ax.set_ylabel('Normalized Intensity', fontsize=12)
        ax.set_title(f'NA={NA}, α={trunc_coeff:.2f}', fontsize=13, fontweight='bold')
        ax.legend(fontsize=10, loc='upper right')
        ax.grid(True, alpha=0.3)
        ax.set_xlim([0, data['r'].max()])
        ax.set_ylim([0, 1.1])

        # Log
        ax = axes[1]
        ax.semilogy(data['r'], np.clip(data['I_debye'], 1e-4, 1), 'b-', linewidth=2.5, label='Debye (Gaussian)', alpha=0.8)
        ax.semilogy(data['r'], np.clip(data['I_rw_gauss'], 1e-4, 1), 'r--', linewidth=2, label='Richards-Wolf (Gaussian)', alpha=0.8)
        ax.semilogy(data['r'], np.clip(data['I_rw_uniform'], 1e-4, 1), 'g:', linewidth=2, label='Richards-Wolf (Uniform)', alpha=0.8)
        ax.axvline(data['airy_radius'], color='gray', ls='-.', lw=1.5, alpha=0.5)
        ax.set_xlabel('Radial distance r (μm)', fontsize=12)
        ax.set_ylabel('Normalized Intensity (log)', fontsize=12)
        ax.set_title('Log Scale (shows tails)', fontsize=13, fontweight='bold')
        ax.legend(fontsize=10, loc='upper right')
        ax.grid(True, alpha=0.3, which='both')
        ax.set_xlim([0, data['r'].max()])
        ax.set_ylim([1e-4, 2])

        # Metrics text
        metrics_text = f"FWHM: Debye={data['fwhm_debye']:.3f}, RW={data['fwhm_rw_gauss']:.3f}, RW-Uniform={data['fwhm_rw_uniform']:.3f} μm\n"
        metrics_text += f"MSE(Debye vs RW Gaussian)={data['metrics_dg']['mse']:.5f}, Corr={data['metrics_dg']['corr']:.4f}"
        fig.text(0.5, 0.02, metrics_text, ha='center', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

        plt.tight_layout(rect=[0, 0.05, 1, 1])

        filename = f'{output_dir}/NA_{NA:.1f}_alpha_{trunc_coeff:.2f}.png'
        plt.savefig(filename, dpi=200, bbox_inches='tight')
        plt.close()

        print(f"  ✓ Saved: {filename}")

print(f"\n✓ All individual plots saved")

# Aperture-plane Gaussian comparison
print("\n" + "="*80)
print("GENERATING APERTURE-PLANE GAUSSIAN PROFILES")
print("="*80 + "\n")

for NA in NA_values:
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))

    theta = np.arcsin(NA / n_medium)
    focal_length = (aperture_default / 2) / np.tan(theta)

    # Radial coordinate at aperture (normalized to aperture radius)
    rho = np.linspace(0, 1, 200)  # 0 to aperture radius

    for trunc_coeff in truncation_coeffs:
        # Gaussian amplitude at aperture: A(ρ) = exp(-α * ρ²)
        A_aperture = np.exp(-trunc_coeff * rho**2)
        ax.plot(rho, A_aperture, linewidth=2, label=f'α={trunc_coeff:.2f}', alpha=0.8)

    ax.axvline(1.0, color='k', ls='--', lw=1.5, alpha=0.5, label='Aperture edge')
    ax.set_xlabel('Normalized radial position (ρ = r/r_aperture)', fontsize=12)
    ax.set_ylabel('Gaussian Amplitude', fontsize=12)
    ax.set_title(f'Aperture-Plane Gaussian Profiles (NA={NA})', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, 1.2])
    ax.set_ylim([0, 1.1])

    plt.tight_layout()
    filename = f'{output_dir}/aperture_gaussians_NA_{NA:.1f}.png'
    plt.savefig(filename, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {filename}")

# 2D Gaussian visualization (different alphas for each NA)
print("\n" + "="*80)
print("GENERATING 2D GAUSSIAN VISUALIZATIONS")
print("="*80 + "\n")

# 2D grid
x = np.linspace(-1.2, 1.2, 300)
y = np.linspace(-1.2, 1.2, 300)
X, Y = np.meshgrid(x, y)
R = np.sqrt(X**2 + Y**2)

for NA in NA_values:
    fig, axes = plt.subplots(1, len(truncation_coeffs), figsize=(4*len(truncation_coeffs), 4))

    for i, trunc_coeff in enumerate(truncation_coeffs):
        ax = axes[i]
        # Gaussian: exp(-α * r²)
        G = np.exp(-trunc_coeff * R**2)
        im = ax.contourf(X, Y, G, levels=20, cmap='hot')
        circle = plt.Circle((0, 0), 1.0, fill=False, color='cyan', linewidth=2, linestyle='--')
        ax.add_patch(circle)
        ax.set_xlabel('x/r_aperture', fontsize=11)
        if i == 0:
            ax.set_ylabel('y/r_aperture', fontsize=11)
        ax.set_title(f'α={trunc_coeff:.2f}', fontsize=12, fontweight='bold')
        ax.set_aspect('equal')
        ax.set_xlim([-1.2, 1.2])
        ax.set_ylim([-1.2, 1.2])
        plt.colorbar(im, ax=ax, label='Amplitude')

    fig.suptitle(f'2D Gaussian Beam at Aperture (NA={NA})', fontsize=14, fontweight='bold')
    plt.tight_layout()

    filename = f'{output_dir}/gaussian_2d_NA_{NA:.1f}.png'
    plt.savefig(filename, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {filename}")

# Summary grid
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

        ax.plot(data['r'], data['I_debye'], 'b-', linewidth=2, label='Debye (Gaussian)', alpha=0.8)
        ax.plot(data['r'], data['I_rw_gauss'], 'r--', linewidth=1.5, label='Richards-Wolf (Gaussian)', alpha=0.8)
        ax.plot(data['r'], data['I_rw_uniform'], 'g:', linewidth=1.5, label='Richards-Wolf (Uniform)', alpha=0.7)
        ax.axvline(data['airy_radius'], color='gray', ls='-.', lw=1, alpha=0.4)

        if j == 0:
            ax.set_ylabel(f'NA={NA}\nIntensity', fontsize=11, fontweight='bold')
        if i == n_rows - 1:
            ax.set_xlabel(f'α={trunc_coeff:.2f}\nr (μm)', fontsize=10)
        if i == 0 and j == 0:
            ax.legend(fontsize=7, loc='upper right')

        if i == 0:
            ax.set_title(f'α={trunc_coeff:.2f}', fontsize=10)

        ax.grid(True, alpha=0.25)
        ax.set_xlim([0, data['r'].max()])
        ax.set_ylim([0, 1.1])

plt.tight_layout()
plt.savefig(f'{output_dir}/summary_grid.png', dpi=200, bbox_inches='tight')
print(f"✓ Saved: {output_dir}/summary_grid.png")

# Summary table
print("\n" + "="*80)
print("SUMMARY: Debye vs Richards-Wolf Gaussian Agreement")
print("="*80)

for NA in NA_values:
    print(f"\nNA = {NA}:")
    print(f"  {'α':>6} {'MSE':>10} {'Corr':>8} {'FWHM Diff':>12}")
    print(f"  {'-'*42}")

    for trunc_coeff in truncation_coeffs:
        data = all_results[NA][trunc_coeff]
        mse = data['metrics_dg']['mse']
        corr = data['metrics_dg']['corr']
        fwhm_diff = abs(data['fwhm_debye'] - data['fwhm_rw_gauss'])

        print(f"  {trunc_coeff:6.2f} {mse:10.6f} {corr:8.5f} {fwhm_diff:12.4f} μm")

print("\n" + "="*80)
print("✓ ANALYSIS COMPLETE!")
print("="*80)
print(f"\nAll plots saved to: {output_dir}/")
print(f"  - {len(NA_values) * len(truncation_coeffs)} individual comparison plots")
print(f"  - {len(NA_values)} aperture-plane Gaussian plots")
print(f"  - {len(NA_values)} 2D Gaussian visualizations (per NA)")
print(f"  - 1 summary grid plot")
print("="*80)
