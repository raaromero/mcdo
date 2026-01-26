"""
Comprehensive standalone plots for Richards-Wolf presentation.

For each configuration generates:
1. 1D radial profile (I vs r)
2. 2D x-y contour (physical units μm)
3. 2D u-v contour (optical units)
4. 2D r-z contour (axial cross-section)

Organized by sections for step-by-step slide building.
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

def compute_debye_intensity(r_array, NA, input_field='gaussian', alpha=1.0, epsilon=0):
    """
    Debye scalar diffraction integral with Gaussian or uniform apodization.
    This is the scalar limit of Richards-Wolf (ignores vector/polarization effects).

    I(r) = |∫ A(θ) √cos(θ) sin(θ) J₀(k r sin θ) dθ|²
    """
    theta_max = np.arcsin(NA / n_medium)
    sin2_alpha = np.sin(theta_max) ** 2

    intensity = np.zeros_like(r_array)

    for i, r in enumerate(r_array):
        def integrand(theta):
            if abs(np.sin(theta)) < 1e-15:
                return 0.0
            cos_t = np.cos(theta)
            sin_t = np.sin(theta)

            # Apodization (same as Richards-Wolf)
            if input_field == 'gaussian':
                apod = np.exp(-alpha * sin_t**2 / sin2_alpha)
            else:
                apod = 1.0

            # Aplanatic factor (same as RW)
            aplanatic = np.sqrt(cos_t)

            # Geometric factor (scalar version)
            geo = sin_t

            # Bessel function
            bessel = jv(0, k * r * sin_t)

            return apod * aplanatic * geo * bessel

        # Integrate
        if epsilon > 0.001:
            theta_inner = np.arcsin(NA * epsilon / n_medium)
            I_val, _ = integrate.quad(integrand, theta_inner, theta_max, limit=100)
        else:
            I_val, _ = integrate.quad(integrand, 0, theta_max, limit=100)

        intensity[i] = np.abs(I_val)**2

    return intensity

# Base output directory
base_dir = 'data/presentation_slides'
os.makedirs(base_dir, exist_ok=True)

print("="*70)
print("GENERATING ALL PRESENTATION PLOTS")
print("="*70)

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def compute_rw_field(NA, input_field, alpha=1.0, epsilon=0, polarization='x',
                     r_array=None, z_val=0):
    """Compute Richards-Wolf field for given parameters."""

    if r_array is None:
        airy_r = 0.61 * wavelength / NA
        r_array = np.linspace(0, 3 * airy_r, 150)

    z_array = np.full_like(r_array, z_val)

    # Outer aperture
    rw_outer = RichardsWolfSimulator(
        wavelength=wavelength,
        numerical_aperture=NA,
        n_medium=n_medium,
        polarization=polarization,
        input_field=input_field,
        truncation_coeff=alpha
    )

    Ex_out, Ey_out, Ez_out = rw_outer.compute_field(r_array, z_array)

    if epsilon > 0.001:
        NA_inner = NA * epsilon
        rw_inner = RichardsWolfSimulator(
            wavelength=wavelength,
            numerical_aperture=NA_inner,
            n_medium=n_medium,
            polarization=polarization,
            input_field=input_field,
            truncation_coeff=alpha,
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

    # Outer
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

    # Optical coordinates
    k = 2 * np.pi / wavelength
    U = k * NA * X
    V = k * NA * Y
    u_airy = k * NA * airy_r

    return X, Y, U, V, I_total, I_Ex, I_Ey, I_Ez, airy_r, u_airy

def compute_2d_rz(NA, input_field, alpha=1.0, epsilon=0, polarization='x', n_r=40, n_z=60):
    """Compute 2D r-z intensity distribution with all field components.
    Returns symmetric r from -r_max to +r_max.
    """
    airy_r = 0.61 * wavelength / NA
    dof = wavelength / (NA**2)

    # Compute for positive r only
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
    # r goes from -r_max to +r_max
    r_sym = np.concatenate([-r_pos[::-1], r_pos[1:]])
    R_sym, Z_sym = np.meshgrid(r_sym, z)

    # Mirror intensity (flip along r axis and concatenate)
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
                    I_uniform_ref=None, I_debye=None):
    """Plot 1D radial intensity profile with optional uniform and Debye references.
    Shows symmetric r from -r_max to +r_max.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    I_total_norm = safe_normalize(I_total)

    # Create symmetric arrays (mirror around r=0)
    r_sym = np.concatenate([-r[::-1], r[1:]])  # avoid duplicate at r=0
    I_sym = np.concatenate([I_total_norm[::-1], I_total_norm[1:]])

    ax.plot(r_sym, I_sym, 'b-', lw=2.5, label='RW (this config)')

    # Add Debye reference for Gaussian plots
    if I_debye is not None:
        I_debye_norm = safe_normalize(I_debye)
        I_debye_sym = np.concatenate([I_debye_norm[::-1], I_debye_norm[1:]])
        ax.plot(r_sym, I_debye_sym, 'r--', lw=2, label='Debye (scalar)')

    # Add uniform RW reference if provided (for Gaussian plots)
    if I_uniform_ref is not None:
        I_ref_norm = safe_normalize(I_uniform_ref)
        I_ref_sym = np.concatenate([I_ref_norm[::-1], I_ref_norm[1:]])
        ax.plot(r_sym, I_ref_sym, 'g:', lw=2, label='RW Uniform')

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
    """Plot 2D r-z axial cross-section - both contour and heatmap."""
    I_norm = safe_normalize(I)
    levels = [0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

    # Contour plot
    fig, ax = plt.subplots(figsize=(10, 6))
    cs = ax.contour(Z, R, I_norm, levels=levels, colors='black', linewidths=1.0)
    ax.clabel(cs, inline=True, fmt='%.2f')
    ax.axhline(airy_r, color='red', ls='--', lw=1.5)
    ax.set_xlabel('z (μm)')
    ax.set_ylabel('r (μm)')
    ax.set_title(f'{title}\nAiry r = {airy_r:.3f} μm, DOF ≈ {dof:.2f} μm', fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/{filename}_rz_contour.png', dpi=200)
    plt.close()

    # Heatmap plot
    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.contourf(Z, R, I_norm, levels=20, cmap='hot')
    ax.contour(Z, R, I_norm, levels=[0.5], colors='cyan', linewidths=2)
    plt.colorbar(im, ax=ax, label='Normalized Intensity')
    ax.axhline(airy_r, color='white', ls='--', lw=1, alpha=0.7)
    ax.set_xlabel('z (μm)')
    ax.set_ylabel('r (μm)')
    ax.set_title(f'{title}\nAiry r = {airy_r:.3f} μm, DOF ≈ {dof:.2f} μm', fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/{filename}_rz_heatmap.png', dpi=200)
    plt.close()

def generate_config_plots(NA, input_field, alpha, epsilon, polarization, output_dir, prefix,
                          I_uniform_ref=None):
    """Generate all plots for a single configuration in its own subfolder."""

    # Create subfolder for this configuration
    config_dir = f'{output_dir}/{prefix}'
    os.makedirs(config_dir, exist_ok=True)

    # Build title
    na_str = f'NA={NA}'
    if input_field == 'gaussian':
        field_str = f'Gaussian α={alpha}'
    else:
        field_str = 'Uniform'
    eps_str = f'ε={epsilon}' if epsilon > 0 else 'Circular'

    base_title = f'{field_str}, {na_str}, {eps_str}'

    # 1D profile (all components)
    airy_r = 0.61 * wavelength / NA
    r = np.linspace(0, 3 * airy_r, 150)
    Ex, Ey, Ez, _ = compute_rw_field(NA, input_field, alpha, epsilon, polarization, r, 0)
    I_total = np.abs(Ex)**2 + np.abs(Ey)**2 + np.abs(Ez)**2
    I_Ex_1d = np.abs(Ex)**2
    I_Ey_1d = np.abs(Ey)**2
    I_Ez_1d = np.abs(Ez)**2

    # Compute uniform reference for this config if not provided
    if I_uniform_ref is None and input_field != 'uniform':
        Ex_u, Ey_u, Ez_u, _ = compute_rw_field(NA, 'uniform', 1.0, epsilon, polarization, r, 0)
        I_uniform_ref = np.abs(Ex_u)**2 + np.abs(Ey_u)**2 + np.abs(Ez_u)**2

    # Compute Debye (scalar) reference for Gaussian configurations
    I_debye = None
    if input_field == 'gaussian':
        I_debye = compute_debye_intensity(r, NA, input_field='gaussian', alpha=alpha, epsilon=epsilon)

    # Profile plots for each component
    for comp_name, I_comp in [('total', I_total), ('Ex', I_Ex_1d), ('Ey', I_Ey_1d), ('Ez', I_Ez_1d)]:
        title = f'{base_title} - {comp_name}'
        ref = I_uniform_ref if comp_name == 'total' else None
        debye = I_debye if comp_name == 'total' else None
        plot_1d_profile(r, I_comp, I_comp, airy_r, title, f'profile_{comp_name}', config_dir, ref, debye)

    print(f"    ✓ {prefix}/profile_*.png (4 files)")

    # 2D x-y and u-v
    X, Y, U, V, I_2d_total, I_2d_Ex, I_2d_Ey, I_2d_Ez, airy_r, u_airy = compute_2d_xy(
        NA, input_field, alpha, epsilon, polarization, n_points=51
    )

    for comp_name, I_2d in [('total', I_2d_total), ('Ex', I_2d_Ex), ('Ey', I_2d_Ey), ('Ez', I_2d_Ez)]:
        title = f'{base_title} - {comp_name}'
        plot_2d_xy(X, Y, I_2d, airy_r, title, f'xy_{comp_name}', config_dir)
        plot_2d_uv(U, V, I_2d, u_airy, title, f'uv_{comp_name}', config_dir)

    print(f"    ✓ {prefix}/xy_*_contour.png, xy_*_heatmap.png (8 files)")
    print(f"    ✓ {prefix}/uv_*_contour.png, uv_*_heatmap.png (8 files)")

    # 2D r-z
    R, Z, I_rz_total, I_rz_Ex, I_rz_Ey, I_rz_Ez, airy_r, dof = compute_2d_rz(
        NA, input_field, alpha, epsilon, polarization, n_r=30, n_z=50
    )

    for comp_name, I_rz in [('total', I_rz_total), ('Ex', I_rz_Ex), ('Ey', I_rz_Ey), ('Ez', I_rz_Ez)]:
        title = f'{base_title} - {comp_name}'
        plot_2d_rz(R, Z, I_rz, airy_r, dof, title, f'rz_{comp_name}', config_dir)

    print(f"    ✓ {prefix}/rz_*_contour.png, rz_*_heatmap.png (8 files)")

# =============================================================================
# SECTION 1: GAUSSIAN APERTURE PROFILES (no diffraction, just aperture)
# =============================================================================
print("\n" + "="*70)
print("SECTION 1: Gaussian Aperture Profiles")
print("="*70)

sec1_dir = f'{base_dir}/sec1_gaussian_aperture'
os.makedirs(sec1_dir, exist_ok=True)

# Symmetric rho for cross-section view
rho = np.linspace(-1.3, 1.3, 600)
rho_pos = np.linspace(0, 1.3, 300)

# Individual α profiles (symmetric)
for alpha in [1.0, 2.0, 4.0]:
    fig, ax = plt.subplots(figsize=(8, 6))
    A = np.exp(-alpha * rho**2)
    ax.plot(rho, A, 'b-', lw=3)
    ax.axvline(1.0, color='red', ls='--', lw=2, label='Aperture edge')
    ax.axvline(-1.0, color='red', ls='--', lw=2)
    ax.fill_between(rho, 0, A, where=np.abs(rho) <= 1, alpha=0.2, color='blue')
    edge_val = np.exp(-alpha)
    ax.annotate(f'Edge = {edge_val:.3f}', xy=(1.0, edge_val), xytext=(1.1, edge_val+0.15),
                arrowprops=dict(arrowstyle='->', color='gray'))
    ax.set_xlabel('ρ = r / r_aperture')
    ax.set_ylabel('Amplitude A(ρ)')
    ax.set_title(f'Gaussian Profile: α = {alpha}', fontweight='bold')
    ax.legend(loc='upper right')
    ax.set_xlim([-1.3, 1.3])
    ax.set_ylim([0, 1.1])
    plt.tight_layout()
    alpha_str = str(alpha).replace('.', 'p')
    plt.savefig(f'{sec1_dir}/gaussian_alpha{alpha_str}.png', dpi=200)
    plt.close()
    print(f"  ✓ gaussian_alpha{alpha_str}.png")

# All alphas overlaid (symmetric)
fig, ax = plt.subplots(figsize=(8, 6))
for alpha, color in zip([1.0, 2.0, 4.0], ['#e41a1c', '#377eb8', '#4daf4a']):
    A = np.exp(-alpha * rho**2)
    ax.plot(rho, A, color=color, lw=2.5, label=f'α = {alpha}')
ax.axvline(1.0, color='black', ls='--', lw=2, label='Aperture edge')
ax.axvline(-1.0, color='black', ls='--', lw=2)
ax.set_xlabel('ρ = r / r_aperture')
ax.set_ylabel('Amplitude A(ρ)')
ax.set_title('Gaussian Truncation: Effect of α', fontweight='bold')
ax.legend(loc='upper right')
ax.set_xlim([-1.3, 1.3])
ax.set_ylim([0, 1.1])
plt.tight_layout()
plt.savefig(f'{sec1_dir}/gaussian_all_alphas.png', dpi=200)
plt.close()
print(f"  ✓ gaussian_all_alphas.png")

# Annular regions visualization (symmetric)
for eps in [0.5, 0.99]:
    fig, ax = plt.subplots(figsize=(9, 6))
    alpha = 2.0
    A = np.exp(-alpha * rho**2)
    ax.plot(rho, A, 'b-', lw=3, label=f'Gaussian (α={alpha})')
    ax.fill_between(rho, 0, A, where=np.abs(rho) <= eps, alpha=0.4, color='red', label=f'Blocked (|ρ|<{eps})')
    ax.fill_between(rho, 0, A, where=(np.abs(rho) > eps) & (np.abs(rho) <= 1), alpha=0.4, color='green', label='Transmitted')
    ax.axvline(eps, color='red', ls='--', lw=2)
    ax.axvline(-eps, color='red', ls='--', lw=2)
    ax.axvline(1.0, color='black', ls='--', lw=2, label='Outer edge')
    ax.axvline(-1.0, color='black', ls='--', lw=2)
    ax.set_xlabel('ρ = r / r_outer')
    ax.set_ylabel('Amplitude A(ρ)')
    ax.set_title(f'Gaussian on Annular Aperture (ε = {eps})', fontweight='bold')
    ax.legend(loc='upper right')
    ax.set_xlim([-1.3, 1.3])
    ax.set_ylim([0, 1.1])
    plt.tight_layout()
    eps_str = str(eps).replace('.', 'p')
    plt.savefig(f'{sec1_dir}/gaussian_annular_eps{eps_str}.png', dpi=200)
    plt.close()
    print(f"  ✓ gaussian_annular_eps{eps_str}.png")

# 2D aperture visualizations
x = np.linspace(-1.3, 1.3, 300)
y = np.linspace(-1.3, 1.3, 300)
X, Y = np.meshgrid(x, y)
R = np.sqrt(X**2 + Y**2)

for alpha in [1.0, 2.0, 4.0]:
    G = np.exp(-alpha * R**2)
    G_masked = np.where(R <= 1, G, 0)

    fig, ax = plt.subplots(figsize=(8, 8))
    im = ax.imshow(G_masked, extent=[-1.3, 1.3, -1.3, 1.3], cmap='hot', vmin=0, vmax=1, origin='lower')
    circle = plt.Circle((0, 0), 1.0, fill=False, color='cyan', lw=2)
    ax.add_patch(circle)
    plt.colorbar(im, ax=ax, label='Amplitude', shrink=0.8)
    ax.set_xlabel('x / r_aperture')
    ax.set_ylabel('y / r_aperture')
    ax.set_title(f'2D Gaussian (α = {alpha}) on Circular Aperture', fontweight='bold')
    ax.set_aspect('equal')
    plt.tight_layout()
    alpha_str = str(alpha).replace('.', 'p')
    plt.savefig(f'{sec1_dir}/gaussian_2d_circular_alpha{alpha_str}.png', dpi=200)
    plt.close()
    print(f"  ✓ gaussian_2d_circular_alpha{alpha_str}.png")

for eps in [0.5, 0.99]:
    alpha = 2.0
    G = np.exp(-alpha * R**2)
    mask = (R >= eps) & (R <= 1)
    G_masked = np.where(mask, G, 0)

    fig, ax = plt.subplots(figsize=(8, 8))
    im = ax.imshow(G_masked, extent=[-1.3, 1.3, -1.3, 1.3], cmap='hot', vmin=0, vmax=1, origin='lower')
    circle_out = plt.Circle((0, 0), 1.0, fill=False, color='cyan', lw=2)
    circle_in = plt.Circle((0, 0), eps, fill=False, color='cyan', lw=2, ls='--')
    ax.add_patch(circle_out)
    ax.add_patch(circle_in)
    plt.colorbar(im, ax=ax, label='Amplitude', shrink=0.8)
    ax.set_xlabel('x / r_outer')
    ax.set_ylabel('y / r_outer')
    ax.set_title(f'2D Gaussian (α=2) on Annular (ε={eps})', fontweight='bold')
    ax.set_aspect('equal')
    plt.tight_layout()
    eps_str = str(eps).replace('.', 'p')
    plt.savefig(f'{sec1_dir}/gaussian_2d_annular_eps{eps_str}.png', dpi=200)
    plt.close()
    print(f"  ✓ gaussian_2d_annular_eps{eps_str}.png")

# =============================================================================
# SECTION 2: LOW NA CIRCULAR (baseline, ε=0)
# =============================================================================
print("\n" + "="*70)
print("SECTION 2: Low NA Circular Aperture (ε=0)")
print("="*70)

sec2_dir = f'{base_dir}/sec2_lowNA_circular'
os.makedirs(sec2_dir, exist_ok=True)

NA = 0.1
epsilon = 0

# Compute uniform reference for this NA/epsilon
airy_r = 0.61 * wavelength / NA
r_ref = np.linspace(0, 3 * airy_r, 150)
Ex_u, Ey_u, Ez_u, _ = compute_rw_field(NA, 'uniform', 1.0, epsilon, 'x', r_ref, 0)
I_uniform_ref = np.abs(Ex_u)**2 + np.abs(Ey_u)**2 + np.abs(Ez_u)**2

# Uniform
print("  Uniform:")
generate_config_plots(NA, 'uniform', 1.0, epsilon, 'x', sec2_dir, 'uniform')

# Gaussian at different α (with uniform reference)
for alpha in [1.0, 2.0, 4.0]:
    print(f"  Gaussian α={alpha}:")
    alpha_str = str(alpha).replace('.', 'p')
    generate_config_plots(NA, 'gaussian', alpha, epsilon, 'x', sec2_dir, f'gaussian_alpha{alpha_str}',
                          I_uniform_ref=I_uniform_ref)

# =============================================================================
# SECTION 3: LOW NA ANNULAR
# =============================================================================
print("\n" + "="*70)
print("SECTION 3: Low NA Annular Aperture")
print("="*70)

sec3_dir = f'{base_dir}/sec3_lowNA_annular'
os.makedirs(sec3_dir, exist_ok=True)

NA = 0.1

for epsilon in [0.5, 0.99]:
    eps_str = str(epsilon).replace('.', 'p')

    # Compute uniform reference for this NA/epsilon
    airy_r = 0.61 * wavelength / NA
    r_ref = np.linspace(0, 3 * airy_r, 150)
    Ex_u, Ey_u, Ez_u, _ = compute_rw_field(NA, 'uniform', 1.0, epsilon, 'x', r_ref, 0)
    I_uniform_ref = np.abs(Ex_u)**2 + np.abs(Ey_u)**2 + np.abs(Ez_u)**2

    # Uniform
    print(f"  Uniform ε={epsilon}:")
    generate_config_plots(NA, 'uniform', 1.0, epsilon, 'x', sec3_dir, f'uniform_eps{eps_str}')

    # Gaussian (with uniform reference)
    for alpha in [1.0, 2.0, 4.0]:
        print(f"  Gaussian α={alpha}, ε={epsilon}:")
        alpha_str = str(alpha).replace('.', 'p')
        generate_config_plots(NA, 'gaussian', alpha, epsilon, 'x', sec3_dir,
                            f'gaussian_alpha{alpha_str}_eps{eps_str}',
                            I_uniform_ref=I_uniform_ref)

# =============================================================================
# SECTION 4: HIGH NA CIRCULAR (baseline, ε=0)
# =============================================================================
print("\n" + "="*70)
print("SECTION 4: High NA Circular Aperture (ε=0)")
print("="*70)

sec4_dir = f'{base_dir}/sec4_highNA_circular'
os.makedirs(sec4_dir, exist_ok=True)

NA = 0.9
epsilon = 0

# Compute uniform reference for this NA/epsilon
airy_r = 0.61 * wavelength / NA
r_ref = np.linspace(0, 3 * airy_r, 150)
Ex_u, Ey_u, Ez_u, _ = compute_rw_field(NA, 'uniform', 1.0, epsilon, 'x', r_ref, 0)
I_uniform_ref = np.abs(Ex_u)**2 + np.abs(Ey_u)**2 + np.abs(Ez_u)**2

# Uniform
print("  Uniform:")
generate_config_plots(NA, 'uniform', 1.0, epsilon, 'x', sec4_dir, 'uniform')

# Gaussian (with uniform reference)
for alpha in [1.0, 2.0, 4.0]:
    print(f"  Gaussian α={alpha}:")
    alpha_str = str(alpha).replace('.', 'p')
    generate_config_plots(NA, 'gaussian', alpha, epsilon, 'x', sec4_dir, f'gaussian_alpha{alpha_str}',
                          I_uniform_ref=I_uniform_ref)

# =============================================================================
# SECTION 5: HIGH NA ANNULAR
# =============================================================================
print("\n" + "="*70)
print("SECTION 5: High NA Annular Aperture")
print("="*70)

sec5_dir = f'{base_dir}/sec5_highNA_annular'
os.makedirs(sec5_dir, exist_ok=True)

NA = 0.9

for epsilon in [0.5, 0.99]:
    eps_str = str(epsilon).replace('.', 'p')

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

# =============================================================================
# SECTION 6: FIELD COMPONENTS
# =============================================================================
print("\n" + "="*70)
print("SECTION 6: Field Components (Ex, Ey, Ez)")
print("="*70)

sec6_dir = f'{base_dir}/sec6_field_components'
os.makedirs(sec6_dir, exist_ok=True)

for NA in [0.1, 0.9]:
    na_str = 'lowNA' if NA < 0.5 else 'highNA'

    for input_field in ['uniform', 'gaussian']:
        alpha = 2.0 if input_field == 'gaussian' else 1.0

        airy_r = 0.61 * wavelength / NA
        r = np.linspace(0, 3 * airy_r, 150)
        Ex, Ey, Ez, _ = compute_rw_field(NA, input_field, alpha, 0, 'x', r, 0)

        I_total = np.abs(Ex)**2 + np.abs(Ey)**2 + np.abs(Ez)**2
        I_Ex = np.abs(Ex)**2
        I_Ey = np.abs(Ey)**2
        I_Ez = np.abs(Ez)**2

        fig, ax = plt.subplots(figsize=(9, 6))
        ax.plot(r, I_Ex / I_total.max(), 'b-', lw=2.5, label='|Ex|²')
        ax.plot(r, I_Ey / I_total.max(), 'g--', lw=2, label='|Ey|²')
        ax.plot(r, I_Ez / I_total.max(), 'r:', lw=2.5, label='|Ez|²')
        ax.axvline(airy_r, color='gray', ls=':', lw=1.5)

        title = f'{input_field.capitalize()}, NA={NA}'
        ax.set_xlabel('r (μm)', fontsize=13)
        ax.set_ylabel('Intensity (normalized to total max)', fontsize=13)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.set_xlim([0, r.max()])
        ax.grid(True, alpha=0.3)
        plt.tight_layout()

        plt.savefig(f'{sec6_dir}/components_{na_str}_{input_field}.png', dpi=200)
        plt.close()
        print(f"  ✓ components_{na_str}_{input_field}.png")

# =============================================================================
# SECTION 7: POLARIZATION COMPARISON
# =============================================================================
print("\n" + "="*70)
print("SECTION 7: Linear vs Circular Polarization")
print("="*70)

sec7_dir = f'{base_dir}/sec7_polarization'
os.makedirs(sec7_dir, exist_ok=True)

NA = 0.9

for input_field in ['uniform', 'gaussian']:
    alpha = 2.0 if input_field == 'gaussian' else 1.0

    airy_r = 0.61 * wavelength / NA
    r = np.linspace(0, 2 * airy_r, 150)

    # Linear x
    Ex_x, Ey_x, Ez_x, _ = compute_rw_field(NA, input_field, alpha, 0, 'x', r, 0)
    I_linear = np.abs(Ex_x)**2 + np.abs(Ey_x)**2 + np.abs(Ez_x)**2

    # Circular
    Ex_c, Ey_c, Ez_c, _ = compute_rw_field(NA, input_field, alpha, 0, 'circular', r, 0)
    I_circular = np.abs(Ex_c)**2 + np.abs(Ey_c)**2 + np.abs(Ez_c)**2

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(r, I_linear / I_linear.max(), 'b-', lw=2.5, label='Linear (x-pol)')
    ax.plot(r, I_circular / I_circular.max(), 'r--', lw=2.5, label='Circular')
    ax.axvline(airy_r, color='gray', ls=':', lw=1.5)

    title = f'{input_field.capitalize()}, NA={NA}'
    ax.set_xlabel('r (μm)', fontsize=13)
    ax.set_ylabel('Normalized Intensity', fontsize=13)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.set_xlim([0, r.max()])
    ax.set_ylim([0, 1.05])
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig(f'{sec7_dir}/polarization_{input_field}.png', dpi=200)
    plt.close()
    print(f"  ✓ polarization_{input_field}.png")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "="*70)
print("ALL PLOTS COMPLETE")
print("="*70)
print(f"\nOutput directories:")
for i in range(1, 8):
    sec_dir = f'{base_dir}/sec{i}_*'
    import glob
    dirs = glob.glob(sec_dir)
    for d in dirs:
        n_files = len([f for f in os.listdir(d) if f.endswith('.png')])
        print(f"  {d}: {n_files} files")
