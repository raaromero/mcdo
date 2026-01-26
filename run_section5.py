"""Run Section 5: High NA Annular Aperture

Generates plots for ε = 0.5 and ε = 0.99:
- Uniform illumination
- Gaussian illumination at α=1, 2, 4

Each configuration generates:
- 1D profiles (Total Intensity, Ex, Ey, Ez) with Debye & Uniform comparisons
- 2D x-y (contour + heatmap) - physical units, z=0 focal plane
- 2D u-v (contour + heatmap) - optical units
- 2D r-z (contour + heatmap) - axial cross-section, portrait orientation

Parameters:
- λ = 532 nm
- NA = 0.9
- ε = 0.5, 0.99 (annular apertures)
"""

import sys
sys.path.insert(0, '.')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme(style='whitegrid', font_scale=1.5)
from monte_carlo.richards_wolf import RichardsWolfSimulator
from scipy.special import jv
from scipy import integrate
import os

# Parameters
wavelength = 0.532  # μm
n_medium = 1.0
k = 2 * np.pi / wavelength

# Base output directory
base_dir = 'data/presentation_slides'
os.makedirs(base_dir, exist_ok=True)

def compute_debye_intensity(r_array, NA, input_field='gaussian', alpha=1.0, epsilon=0):
    """Debye scalar diffraction integral."""
    theta_max = np.arcsin(NA / n_medium)
    sin2_alpha = np.sin(theta_max) ** 2
    intensity = np.zeros_like(r_array)

    for i, r in enumerate(r_array):
        def integrand(theta):
            if abs(np.sin(theta)) < 1e-15:
                return 0.0
            cos_t = np.cos(theta)
            sin_t = np.sin(theta)
            if input_field == 'gaussian':
                apod = np.exp(-alpha * sin_t**2 / sin2_alpha)
            else:
                apod = 1.0
            aplanatic = np.sqrt(cos_t)
            geo = sin_t
            bessel = jv(0, k * r * sin_t)
            return apod * aplanatic * geo * bessel

        if epsilon > 0.001:
            theta_inner = np.arcsin(NA * epsilon / n_medium)
            I_val, _ = integrate.quad(integrand, theta_inner, theta_max, limit=100)
        else:
            I_val, _ = integrate.quad(integrand, 0, theta_max, limit=100)
        intensity[i] = np.abs(I_val)**2
    return intensity

def compute_rw_field(NA, input_field, alpha=1.0, epsilon=0, polarization='x',
                     r_array=None, z_val=0):
    """Compute Richards-Wolf field for given parameters."""
    if r_array is None:
        airy_r = 0.61 * wavelength / NA
        r_array = np.linspace(0, 3 * airy_r, 150)

    z_array = np.full_like(r_array, z_val)

    rw_outer = RichardsWolfSimulator(
        wavelength=wavelength, numerical_aperture=NA, n_medium=n_medium,
        polarization=polarization, input_field=input_field, truncation_coeff=alpha
    )
    Ex_out, Ey_out, Ez_out = rw_outer.compute_field(r_array, z_array)

    if epsilon > 0.001:
        NA_inner = NA * epsilon
        rw_inner = RichardsWolfSimulator(
            wavelength=wavelength, numerical_aperture=NA_inner, n_medium=n_medium,
            polarization=polarization, input_field=input_field, truncation_coeff=alpha,
            gaussian_reference_na=NA if input_field == 'gaussian' else None
        )
        Ex_in, Ey_in, Ez_in = rw_inner.compute_field(r_array, z_array)
        Ex = Ex_out - Ex_in
        Ey = Ey_out - Ey_in
        Ez = Ez_out - Ez_in
    else:
        Ex, Ey, Ez = Ex_out, Ey_out, Ez_out

    return Ex, Ey, Ez, rw_outer.airy_radius

def compute_2d_xy(NA, input_field, alpha=1.0, epsilon=0, polarization='x', n_points=61):
    """Compute 2D x-y intensity distribution with all field components."""
    airy_r = 0.61 * wavelength / NA
    extent = 2.0 * airy_r

    x = np.linspace(-extent, extent, n_points)
    y = np.linspace(-extent, extent, n_points)
    X, Y = np.meshgrid(x, y)

    r_flat = np.sqrt(X.flatten()**2 + Y.flatten()**2)
    z_flat = np.zeros_like(r_flat)

    rw_outer = RichardsWolfSimulator(
        wavelength=wavelength, numerical_aperture=NA, n_medium=n_medium,
        polarization=polarization, input_field=input_field, truncation_coeff=alpha
    )
    Ex_out, Ey_out, Ez_out = rw_outer.compute_field(r_flat, z_flat)

    if epsilon > 0.001:
        NA_inner = NA * epsilon
        rw_inner = RichardsWolfSimulator(
            wavelength=wavelength, numerical_aperture=NA_inner, n_medium=n_medium,
            polarization=polarization, input_field=input_field, truncation_coeff=alpha,
            gaussian_reference_na=NA if input_field == 'gaussian' else None
        )
        Ex_in, Ey_in, Ez_in = rw_inner.compute_field(r_flat, z_flat)
        Ex = Ex_out - Ex_in
        Ey = Ey_out - Ey_in
        Ez = Ez_out - Ez_in
    else:
        Ex, Ey, Ez = Ex_out, Ey_out, Ez_out

    I_total = (np.abs(Ex)**2 + np.abs(Ey)**2 + np.abs(Ez)**2).reshape(X.shape)
    I_Ex = np.abs(Ex).reshape(X.shape)**2
    I_Ey = np.abs(Ey).reshape(X.shape)**2
    I_Ez = np.abs(Ez).reshape(X.shape)**2

    k = 2 * np.pi / wavelength
    U = k * NA * X
    V = k * NA * Y
    u_airy = k * NA * airy_r

    return X, Y, U, V, I_total, I_Ex, I_Ey, I_Ez, airy_r, u_airy

def compute_2d_rz(NA, input_field, alpha=1.0, epsilon=0, polarization='x', n_r=40, n_z=60):
    """Compute 2D r-z intensity distribution. Returns symmetric r from -r_max to +r_max."""
    airy_r = 0.61 * wavelength / NA
    dof = wavelength / (NA**2)

    r_pos = np.linspace(0, 2 * airy_r, n_r)
    z = np.linspace(-3 * dof, 3 * dof, n_z)
    R_pos, Z_pos = np.meshgrid(r_pos, z)

    r_flat = R_pos.flatten()
    z_flat = Z_pos.flatten()

    rw_outer = RichardsWolfSimulator(
        wavelength=wavelength, numerical_aperture=NA, n_medium=n_medium,
        polarization=polarization, input_field=input_field, truncation_coeff=alpha
    )
    Ex_out, Ey_out, Ez_out = rw_outer.compute_field(r_flat, z_flat)

    if epsilon > 0.001:
        NA_inner = NA * epsilon
        rw_inner = RichardsWolfSimulator(
            wavelength=wavelength, numerical_aperture=NA_inner, n_medium=n_medium,
            polarization=polarization, input_field=input_field, truncation_coeff=alpha,
            gaussian_reference_na=NA if input_field == 'gaussian' else None
        )
        Ex_in, Ey_in, Ez_in = rw_inner.compute_field(r_flat, z_flat)
        Ex = Ex_out - Ex_in
        Ey = Ey_out - Ey_in
        Ez = Ez_out - Ez_in
    else:
        Ex, Ey, Ez = Ex_out, Ey_out, Ez_out

    I_total_pos = (np.abs(Ex)**2 + np.abs(Ey)**2 + np.abs(Ez)**2).reshape(R_pos.shape)
    I_Ex_pos = np.abs(Ex).reshape(R_pos.shape)**2
    I_Ey_pos = np.abs(Ey).reshape(R_pos.shape)**2
    I_Ez_pos = np.abs(Ez).reshape(R_pos.shape)**2

    # Mirror to create symmetric r
    r_sym = np.concatenate([-r_pos[::-1], r_pos[1:]])
    R_sym, Z_sym = np.meshgrid(r_sym, z)

    I_total = np.concatenate([I_total_pos[:, ::-1], I_total_pos[:, 1:]], axis=1)
    I_Ex = np.concatenate([I_Ex_pos[:, ::-1], I_Ex_pos[:, 1:]], axis=1)
    I_Ey = np.concatenate([I_Ey_pos[:, ::-1], I_Ey_pos[:, 1:]], axis=1)
    I_Ez = np.concatenate([I_Ez_pos[:, ::-1], I_Ez_pos[:, 1:]], axis=1)

    return R_sym, Z_sym, I_total, I_Ex, I_Ey, I_Ez, airy_r, dof

def safe_normalize(I):
    """Normalize intensity, handling zero case."""
    max_val = I.max()
    if max_val > 0:
        return I / max_val
    return np.zeros_like(I)

def plot_1d_profile(r, I_total, I_Ex, airy_r, title, filename, output_dir,
                    I_uniform_ref=None, I_debye=None, input_field='gaussian'):
    """Plot 1D radial intensity profile - symmetric r from -r_max to +r_max."""
    fig, ax = plt.subplots(figsize=(10, 6))

    I_total_norm = safe_normalize(I_total)
    r_sym = np.concatenate([-r[::-1], r[1:]])
    I_sym = np.concatenate([I_total_norm[::-1], I_total_norm[1:]])

    # Label based on input field type
    if input_field == 'gaussian':
        main_label = 'Richards-Wolf (Gaussian)'
    else:
        main_label = 'Richards-Wolf (Uniform)'
    ax.plot(r_sym, I_sym, 'b-', lw=2.5, label=main_label)

    if I_debye is not None:
        I_debye_norm = safe_normalize(I_debye)
        I_debye_sym = np.concatenate([I_debye_norm[::-1], I_debye_norm[1:]])
        ax.plot(r_sym, I_debye_sym, 'r--', lw=2, label='Debye (Total)')

    if I_uniform_ref is not None:
        I_ref_norm = safe_normalize(I_uniform_ref)
        I_ref_sym = np.concatenate([I_ref_norm[::-1], I_ref_norm[1:]])
        ax.plot(r_sym, I_ref_sym, 'g:', lw=2, label='Richards-Wolf (Uniform)')

    ax.axvline(airy_r, color='gray', ls=':', lw=1.5, alpha=0.7)
    ax.axvline(-airy_r, color='gray', ls=':', lw=1.5, alpha=0.7)
    ax.axhline(0.5, color='gray', ls='--', lw=1, alpha=0.5)

    ax.set_xlabel('r (μm)')
    ax.set_ylabel('Normalized Intensity')
    ax.set_title(title, fontweight='bold')
    ax.legend()
    ax.set_xlim([-r.max(), r.max()])
    ax.set_ylim([0, 1.05])

    plt.tight_layout()
    plt.savefig(f'{output_dir}/{filename}_profile.png', dpi=200)
    plt.close()

def plot_2d_xy(X, Y, I, airy_r, title, filename, output_dir):
    """Plot 2D x-y in physical units - both contour and heatmap."""
    I_norm = safe_normalize(I)
    levels = [0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

    # Contour plot
    fig, ax = plt.subplots(figsize=(8, 8))
    cs = ax.contour(X, Y, I_norm, levels=levels, colors='black', linewidths=1.0)
    ax.clabel(cs, inline=True, fmt='%.2f')
    circle = plt.Circle((0, 0), airy_r, fill=False, color='red', ls='--', lw=1.5)
    ax.add_patch(circle)
    ax.set_xlabel('x (μm)')
    ax.set_ylabel('y (μm)')
    ax.set_title(f'{title}\nAiry r = {airy_r:.3f} μm', fontweight='bold')
    ax.set_aspect('equal')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/{filename}_xy_contour.png', dpi=200)
    plt.close()

    # Heatmap plot
    fig, ax = plt.subplots(figsize=(8, 8))
    im = ax.imshow(I_norm, extent=[X.min(), X.max(), Y.min(), Y.max()],
                   origin='lower', cmap='hot', vmin=0, vmax=1)
    circle = plt.Circle((0, 0), airy_r, fill=False, color='cyan', ls='--', lw=1.5)
    ax.add_patch(circle)
    plt.colorbar(im, ax=ax, label='Normalized Intensity', shrink=0.8)
    ax.set_xlabel('x (μm)')
    ax.set_ylabel('y (μm)')
    ax.set_title(f'{title}\nAiry r = {airy_r:.3f} μm', fontweight='bold')
    ax.set_aspect('equal')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/{filename}_xy_heatmap.png', dpi=200)
    plt.close()

def plot_2d_uv(U, V, I, u_airy, title, filename, output_dir):
    """Plot 2D u-v in optical units - both contour and heatmap."""
    I_norm = safe_normalize(I)
    levels = [0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

    # Contour plot
    fig, ax = plt.subplots(figsize=(8, 8))
    cs = ax.contour(U, V, I_norm, levels=levels, colors='black', linewidths=1.0)
    ax.clabel(cs, inline=True, fmt='%.2f')
    circle = plt.Circle((0, 0), u_airy, fill=False, color='red', ls='--', lw=1.5)
    ax.add_patch(circle)
    ax.set_xlabel('u = k·NA·x (optical units)')
    ax.set_ylabel('v = k·NA·y (optical units)')
    ax.set_title(f'{title}\nu_Airy ≈ {u_airy:.2f}', fontweight='bold')
    ax.set_aspect('equal')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/{filename}_uv_contour.png', dpi=200)
    plt.close()

    # Heatmap plot
    fig, ax = plt.subplots(figsize=(8, 8))
    im = ax.imshow(I_norm, extent=[U.min(), U.max(), V.min(), V.max()],
                   origin='lower', cmap='hot', vmin=0, vmax=1)
    circle = plt.Circle((0, 0), u_airy, fill=False, color='cyan', ls='--', lw=1.5)
    ax.add_patch(circle)
    plt.colorbar(im, ax=ax, label='Normalized Intensity', shrink=0.8)
    ax.set_xlabel('u = k·NA·x (optical units)')
    ax.set_ylabel('v = k·NA·y (optical units)')
    ax.set_title(f'{title}\nu_Airy ≈ {u_airy:.2f}', fontweight='bold')
    ax.set_aspect('equal')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/{filename}_uv_heatmap.png', dpi=200)
    plt.close()

def plot_2d_rz(R, Z, I, airy_r, dof, title, filename, output_dir):
    """Plot 2D r-z axial cross-section - both contour and heatmap. Portrait orientation (r on x, z on y)."""
    I_norm = safe_normalize(I)
    levels = [0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

    # Contour plot - portrait (r on x-axis, z on y-axis)
    fig, ax = plt.subplots(figsize=(6, 10))
    cs = ax.contour(R, Z, I_norm, levels=levels, colors='black', linewidths=1.0)
    ax.clabel(cs, inline=True, fmt='%.2f')
    ax.axvline(airy_r, color='red', ls='--', lw=1.5)
    ax.axvline(-airy_r, color='red', ls='--', lw=1.5)
    ax.set_xlabel('r (μm)')
    ax.set_ylabel('z (μm)')
    ax.set_title(f'{title}\nAiry r = {airy_r:.3f} μm', fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/{filename}_rz_contour.png', dpi=200)
    plt.close()

    # Heatmap plot - portrait (r on x-axis, z on y-axis)
    fig, ax = plt.subplots(figsize=(6, 10))
    im = ax.contourf(R, Z, I_norm, levels=20, cmap='hot')
    ax.contour(R, Z, I_norm, levels=[0.5], colors='cyan', linewidths=2)
    plt.colorbar(im, ax=ax, label='Normalized Intensity')
    ax.axvline(airy_r, color='white', ls='--', lw=1, alpha=0.7)
    ax.axvline(-airy_r, color='white', ls='--', lw=1, alpha=0.7)
    ax.set_xlabel('r (μm)')
    ax.set_ylabel('z (μm)')
    ax.set_title(f'{title}\nAiry r = {airy_r:.3f} μm', fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/{filename}_rz_heatmap.png', dpi=200)
    plt.close()

def generate_config_plots(NA, input_field, alpha, epsilon, polarization, output_dir, prefix,
                          I_uniform_ref=None):
    """Generate all plots for a single configuration in its own subfolder."""

    config_dir = f'{output_dir}/{prefix}'
    os.makedirs(config_dir, exist_ok=True)

    na_str = f'NA={NA}'
    if input_field == 'gaussian':
        field_str = f'Gaussian α={alpha}'
    else:
        field_str = 'Uniform'
    eps_str = f'ε={epsilon}' if epsilon > 0 else 'Circular'

    base_title = f'{field_str}, {na_str}, {eps_str}'

    # 1D profile
    airy_r = 0.61 * wavelength / NA
    r = np.linspace(0, 3 * airy_r, 150)
    Ex, Ey, Ez, _ = compute_rw_field(NA, input_field, alpha, epsilon, polarization, r, 0)
    I_total = np.abs(Ex)**2 + np.abs(Ey)**2 + np.abs(Ez)**2
    I_Ex_1d = np.abs(Ex)**2
    I_Ey_1d = np.abs(Ey)**2
    I_Ez_1d = np.abs(Ez)**2

    if I_uniform_ref is None and input_field != 'uniform':
        Ex_u, Ey_u, Ez_u, _ = compute_rw_field(NA, 'uniform', 1.0, epsilon, polarization, r, 0)
        I_uniform_ref = np.abs(Ex_u)**2 + np.abs(Ey_u)**2 + np.abs(Ez_u)**2

    I_debye = None
    if input_field == 'gaussian':
        I_debye = compute_debye_intensity(r, NA, input_field='gaussian', alpha=alpha, epsilon=epsilon)

    # Compute uniform Ex, Ey, Ez references for component comparisons
    I_Ex_uniform = None
    I_Ey_uniform = None
    I_Ez_uniform = None
    if input_field != 'uniform':
        Ex_u, Ey_u, Ez_u, _ = compute_rw_field(NA, 'uniform', 1.0, epsilon, polarization, r, 0)
        I_Ex_uniform = np.abs(Ex_u)**2
        I_Ey_uniform = np.abs(Ey_u)**2
        I_Ez_uniform = np.abs(Ez_u)**2

    for comp_name, I_comp, file_suffix, I_ref_comp in [
        ('Total Intensity', I_total, 'total', I_uniform_ref),
        ('Ex', I_Ex_1d, 'Ex', I_Ex_uniform),
        ('Ey', I_Ey_1d, 'Ey', I_Ey_uniform),
        ('Ez', I_Ez_1d, 'Ez', I_Ez_uniform)
    ]:
        title = f'{base_title} - {comp_name}'
        # Debye is scalar (total only), but show it on all plots marked as "Total"
        plot_1d_profile(r, I_comp, I_comp, airy_r, title, f'profile_{file_suffix}', config_dir, I_ref_comp, I_debye, input_field)

    print(f"    ✓ {prefix}/profile_*.png (4 files)")

    # 2D x-y and u-v
    X, Y, U, V, I_2d_total, I_2d_Ex, I_2d_Ey, I_2d_Ez, airy_r, u_airy = compute_2d_xy(
        NA, input_field, alpha, epsilon, polarization, n_points=51
    )

    for comp_name, I_2d, file_suffix in [('Total Intensity', I_2d_total, 'total'), ('Ex', I_2d_Ex, 'Ex'), ('Ey', I_2d_Ey, 'Ey'), ('Ez', I_2d_Ez, 'Ez')]:
        title = f'{base_title} - {comp_name}'
        plot_2d_xy(X, Y, I_2d, airy_r, title, f'xy_{file_suffix}', config_dir)
        plot_2d_uv(U, V, I_2d, u_airy, title, f'uv_{file_suffix}', config_dir)

    print(f"    ✓ {prefix}/xy_*_contour.png, xy_*_heatmap.png (8 files)")
    print(f"    ✓ {prefix}/uv_*_contour.png, uv_*_heatmap.png (8 files)")

    # 2D r-z
    R, Z, I_rz_total, I_rz_Ex, I_rz_Ey, I_rz_Ez, airy_r, dof = compute_2d_rz(
        NA, input_field, alpha, epsilon, polarization, n_r=30, n_z=50
    )

    for comp_name, I_rz, file_suffix in [('Total Intensity', I_rz_total, 'total'), ('Ex', I_rz_Ex, 'Ex'), ('Ey', I_rz_Ey, 'Ey'), ('Ez', I_rz_Ez, 'Ez')]:
        title = f'{base_title} - {comp_name}'
        plot_2d_rz(R, Z, I_rz, airy_r, dof, title, f'rz_{file_suffix}', config_dir)

    print(f"    ✓ {prefix}/rz_*_contour.png, rz_*_heatmap.png (8 files)")


# =============================================================================
# SECTION 5: HIGH NA ANNULAR
# =============================================================================
print("="*70)
print("SECTION 5: High NA Annular Aperture")
print("="*70)
print(f"λ = {wavelength} μm, NA = 0.9, ε = 0.5, 0.99")
print()

sec5_dir = f'{base_dir}/sec5_highNA_annular'
os.makedirs(sec5_dir, exist_ok=True)

NA = 0.9

for epsilon in [0.5, 0.99]:
    eps_str = str(epsilon).replace('.', 'p')
    print(f"\n--- ε = {epsilon} ---")

    # Compute uniform reference for this NA/epsilon
    airy_r = 0.61 * wavelength / NA
    r_ref = np.linspace(0, 3 * airy_r, 150)
    Ex_u, Ey_u, Ez_u, _ = compute_rw_field(NA, 'uniform', 1.0, epsilon, 'x', r_ref, 0)
    I_uniform_ref = np.abs(Ex_u)**2 + np.abs(Ey_u)**2 + np.abs(Ez_u)**2

    # Uniform
    print(f"  Uniform ε={epsilon}:")
    generate_config_plots(NA, 'uniform', 1.0, epsilon, 'x', sec5_dir, f'uniform_eps{eps_str}')

    # Gaussian (with uniform reference)
    for alpha in [1.0, 2.0, 4.0]:
        print(f"  Gaussian α={alpha}, ε={epsilon}:")
        alpha_str = str(alpha).replace('.', 'p')
        generate_config_plots(NA, 'gaussian', alpha, epsilon, 'x', sec5_dir,
                            f'gaussian_alpha{alpha_str}_eps{eps_str}',
                            I_uniform_ref=I_uniform_ref)

print("\n" + "="*70)
print("SECTION 5 COMPLETE")
print("="*70)
print(f"\nOutput directory: {sec5_dir}")

# Count files
total_files = 0
for subdir in sorted(os.listdir(sec5_dir)):
    subdir_path = f'{sec5_dir}/{subdir}'
    if os.path.isdir(subdir_path):
        n_files = len([f for f in os.listdir(subdir_path) if f.endswith('.png')])
        print(f"  {subdir}: {n_files} PNG files")
        total_files += n_files
print(f"\nTotal: {total_files} PNG files")
