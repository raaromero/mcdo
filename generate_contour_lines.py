"""
Generate 2D contour LINE plots for Richards-Wolf diffraction patterns.

Creates three versions for each configuration:
1. x,y coordinates (μm) with Airy reference circle
2. u,v optical units with reference circle
3. x,y without reference circle

Configurations:
- Uniform circular (NA=0.1, 0.9)
- Uniform annular (NA=0.1, 0.9; ε=0.5, 0.99)
- Gaussian circular (NA=0.1, 0.9; α=1, 2, 4)
- Gaussian annular (NA=0.1, 0.9; α=1, 2, 4; ε=0.5, 0.99)

IMPORTANT: Uses corrected gaussian_reference_na for Gaussian annular apertures
to ensure inner and outer disks sample the SAME physical Gaussian beam.
"""

import sys
sys.path.insert(0, '.')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from monte_carlo.richards_wolf import RichardsWolfSimulator
import os

print("="*80)
print("GENERATING CONTOUR LINE PLOTS (Corrected Gaussian Annular)")
print("="*80)

# Parameters
wavelength = 0.532  # μm
n_medium = 1.0
polarization = 'x'

# Output directories
output_dirs = {
    'xy': 'data/comprehensive_comparison/contour_lines_xy',
    'uv': 'data/comprehensive_comparison/contour_lines_uv',
    'noring': 'data/comprehensive_comparison/contour_lines_noring'
}

for d in output_dirs.values():
    os.makedirs(d, exist_ok=True)

# Contour levels
levels = [0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

def compute_2d_field(rw_sim, X, Y, component='total'):
    """Compute 2D intensity field."""
    shape = X.shape
    x_flat = X.flatten()
    y_flat = Y.flatten()
    r_flat = np.sqrt(x_flat**2 + y_flat**2)
    z_flat = np.zeros_like(r_flat)

    Ex, Ey, Ez = rw_sim.compute_field(r_flat, z_flat)

    if component == 'total':
        I = np.abs(Ex)**2 + np.abs(Ey)**2 + np.abs(Ez)**2
    elif component == 'x':
        I = np.abs(Ex)**2
    else:
        raise ValueError(f"Unknown component: {component}")

    return I.reshape(shape)

def compute_gaussian_annular_field(NA_outer, epsilon, alpha, X, Y, component='total'):
    """
    Compute Gaussian annular aperture field using Babinet's principle.

    IMPORTANT: Uses gaussian_reference_na to ensure inner and outer disks
    sample the SAME physical Gaussian beam.
    """
    # Outer disk
    rw_outer = RichardsWolfSimulator(
        wavelength=wavelength,
        numerical_aperture=NA_outer,
        n_medium=n_medium,
        polarization=polarization,
        input_field='gaussian',
        truncation_coeff=alpha
    )

    shape = X.shape
    x_flat = X.flatten()
    y_flat = Y.flatten()
    r_flat = np.sqrt(x_flat**2 + y_flat**2)
    z_flat = np.zeros_like(r_flat)

    Ex_outer, Ey_outer, Ez_outer = rw_outer.compute_field(r_flat, z_flat)

    if epsilon > 0.001:
        # Inner disk with gaussian_reference_na = NA_outer (CORRECTED)
        NA_inner = NA_outer * epsilon
        rw_inner = RichardsWolfSimulator(
            wavelength=wavelength,
            numerical_aperture=NA_inner,
            n_medium=n_medium,
            polarization=polarization,
            input_field='gaussian',
            truncation_coeff=alpha,
            gaussian_reference_na=NA_outer  # KEY FIX: same Gaussian as outer
        )

        Ex_inner, Ey_inner, Ez_inner = rw_inner.compute_field(r_flat, z_flat)

        # Babinet's principle
        Ex = Ex_outer - Ex_inner
        Ey = Ey_outer - Ey_inner
        Ez = Ez_outer - Ez_inner
    else:
        Ex, Ey, Ez = Ex_outer, Ey_outer, Ez_outer

    if component == 'total':
        I = np.abs(Ex)**2 + np.abs(Ey)**2 + np.abs(Ez)**2
    elif component == 'x':
        I = np.abs(Ex)**2
    else:
        raise ValueError(f"Unknown component: {component}")

    return I.reshape(shape)

def compute_uniform_annular_field(NA_outer, epsilon, X, Y, component='total'):
    """Compute uniform annular aperture field using Babinet's principle."""
    rw_outer = RichardsWolfSimulator(
        wavelength=wavelength,
        numerical_aperture=NA_outer,
        n_medium=n_medium,
        polarization=polarization,
        input_field='uniform'
    )

    shape = X.shape
    x_flat = X.flatten()
    y_flat = Y.flatten()
    r_flat = np.sqrt(x_flat**2 + y_flat**2)
    z_flat = np.zeros_like(r_flat)

    Ex_outer, Ey_outer, Ez_outer = rw_outer.compute_field(r_flat, z_flat)

    if epsilon > 0.001:
        NA_inner = NA_outer * epsilon
        rw_inner = RichardsWolfSimulator(
            wavelength=wavelength,
            numerical_aperture=NA_inner,
            n_medium=n_medium,
            polarization=polarization,
            input_field='uniform'
        )

        Ex_inner, Ey_inner, Ez_inner = rw_inner.compute_field(r_flat, z_flat)

        Ex = Ex_outer - Ex_inner
        Ey = Ey_outer - Ey_inner
        Ez = Ez_outer - Ez_inner
    else:
        Ex, Ey, Ez = Ex_outer, Ey_outer, Ez_outer

    if component == 'total':
        I = np.abs(Ex)**2 + np.abs(Ey)**2 + np.abs(Ez)**2
    elif component == 'x':
        I = np.abs(Ex)**2
    else:
        raise ValueError(f"Unknown component: {component}")

    return I.reshape(shape)

def generate_contour_plots(I_data, X, Y, U, V, airy_r, u_airy, title, filename_base):
    """Generate all three versions of contour plots."""
    I_norm = I_data / np.max(I_data)

    # VERSION 1: x,y (μm) with Airy ring
    fig, ax = plt.subplots(figsize=(8, 8))
    cs = ax.contour(X, Y, I_norm, levels=levels, colors='black', linewidths=1.0)
    ax.clabel(cs, inline=True, fontsize=8, fmt='%.2f')
    circle = plt.Circle((0, 0), airy_r, fill=False, color='red', linestyle='--', linewidth=1.5)
    ax.add_patch(circle)
    ax.set_xlabel('x (μm)', fontsize=12)
    ax.set_ylabel('y (μm)', fontsize=12)
    ax.set_title(f'{title}\nTotal Intensity', fontsize=11)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.legend([circle], [f'Airy radius = {airy_r:.3f} μm'], loc='upper right')
    plt.tight_layout()
    plt.savefig(f'{output_dirs["xy"]}/{filename_base}.png', dpi=150)
    plt.close()

    # VERSION 2: u,v (optical units) with reference circle
    fig, ax = plt.subplots(figsize=(8, 8))
    cs = ax.contour(U, V, I_norm, levels=levels, colors='black', linewidths=1.0)
    ax.clabel(cs, inline=True, fontsize=8, fmt='%.2f')
    circle = plt.Circle((0, 0), u_airy, fill=False, color='red', linestyle='--', linewidth=1.5)
    ax.add_patch(circle)
    ax.set_xlabel('u = k·NA·x (optical units)', fontsize=12)
    ax.set_ylabel('v = k·NA·y (optical units)', fontsize=12)
    ax.set_title(f'{title}\nTotal Intensity (Optical Units)', fontsize=11)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.legend([circle], [f'u_Airy ≈ {u_airy:.2f}'], loc='upper right')
    plt.tight_layout()
    plt.savefig(f'{output_dirs["uv"]}/{filename_base}.png', dpi=150)
    plt.close()

    # VERSION 3: x,y without ring
    fig, ax = plt.subplots(figsize=(8, 8))
    cs = ax.contour(X, Y, I_norm, levels=levels, colors='black', linewidths=1.0)
    ax.clabel(cs, inline=True, fontsize=8, fmt='%.2f')
    ax.set_xlabel('x (μm)', fontsize=12)
    ax.set_ylabel('y (μm)', fontsize=12)
    ax.set_title(f'{title}\nTotal Intensity', fontsize=11)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'{output_dirs["noring"]}/{filename_base}.png', dpi=150)
    plt.close()

# Configuration lists
NA_values = [0.1, 0.9]
NA_labels = {0.1: 'lowNA', 0.9: 'highNA'}
epsilon_values = [0, 0.5, 0.99]
alpha_values = [1.0, 2.0, 4.0]

n_points = 81
count = 0

print(f"\nGenerating plots...")

for NA in NA_values:
    airy_r = 0.61 * wavelength / NA
    r_max = 1.5 * airy_r  # Extend bounds

    # Grid
    x = np.linspace(-r_max, r_max, n_points)
    y = np.linspace(-r_max, r_max, n_points)
    X, Y = np.meshgrid(x, y)

    # Optical coordinates
    k = 2 * np.pi / wavelength
    U = k * NA * X
    V = k * NA * Y
    u_airy = k * NA * airy_r  # ≈ 3.83

    na_label = NA_labels[NA]

    # 1. UNIFORM CIRCULAR (ε=0)
    print(f"  Uniform circular NA={NA}...", end=" ", flush=True)
    for component, comp_suffix in [('total', 'total'), ('x', 'Ex')]:
        I = compute_uniform_annular_field(NA, 0, X, Y, component)
        title = f'Uniform Circular: NA={NA}'
        filename = f'uniform_circular_{na_label}_eps0_{comp_suffix}'
        generate_contour_plots(I, X, Y, U, V, airy_r, u_airy, title, filename)
        count += 3
    print("✓")

    # 2. UNIFORM ANNULAR (ε=0.5, 0.99)
    for eps in [0.5, 0.99]:
        eps_label = f'eps{str(eps).replace(".", "p")}'
        print(f"  Uniform annular NA={NA}, ε={eps}...", end=" ", flush=True)
        for component, comp_suffix in [('total', 'total'), ('x', 'Ex')]:
            I = compute_uniform_annular_field(NA, eps, X, Y, component)
            title = f'Uniform Annular: NA={NA}, ε={eps}'
            filename = f'uniform_annular_{na_label}_{eps_label}_{comp_suffix}'
            generate_contour_plots(I, X, Y, U, V, airy_r, u_airy, title, filename)
            count += 3
        print("✓")

    # 3. GAUSSIAN CIRCULAR (ε=0, varying α)
    for alpha in alpha_values:
        alpha_label = f'alpha{str(alpha).replace(".", "p")}'
        print(f"  Gaussian circular NA={NA}, α={alpha}...", end=" ", flush=True)
        for component, comp_suffix in [('total', 'total'), ('x', 'Ex')]:
            I = compute_gaussian_annular_field(NA, 0, alpha, X, Y, component)
            title = f'Gaussian Circular: NA={NA}, α={alpha}'
            filename = f'gaussian_circular_{na_label}_eps0_{alpha_label}_{comp_suffix}'
            generate_contour_plots(I, X, Y, U, V, airy_r, u_airy, title, filename)
            count += 3
        print("✓")

    # 4. GAUSSIAN ANNULAR (ε=0.5, 0.99; varying α)
    for eps in [0.5, 0.99]:
        eps_label = f'eps{str(eps).replace(".", "p")}'
        for alpha in alpha_values:
            alpha_label = f'alpha{str(alpha).replace(".", "p")}'
            print(f"  Gaussian annular NA={NA}, ε={eps}, α={alpha}...", end=" ", flush=True)
            for component, comp_suffix in [('total', 'total'), ('x', 'Ex')]:
                I = compute_gaussian_annular_field(NA, eps, alpha, X, Y, component)
                title = f'Gaussian Annular: NA={NA}, ε={eps}, α={alpha}'
                filename = f'gaussian_annular_{na_label}_{eps_label}_{alpha_label}_{comp_suffix}'
                generate_contour_plots(I, X, Y, U, V, airy_r, u_airy, title, filename)
                count += 3
            print("✓")

print(f"\n{'='*80}")
print(f"COMPLETE: Generated {count} plots total")
print(f"  - {count//3} configurations × 3 versions (xy, uv, noring)")
print(f"{'='*80}")
print(f"\nOutput directories:")
for name, path in output_dirs.items():
    n_files = len([f for f in os.listdir(path) if f.endswith('.png')])
    print(f"  {path}: {n_files} files")
