"""
Comprehensive plots for Richards-Wolf diffraction presentation.

Generates:
1. Gaussian aperture profiles (relative to disk geometry)
2. ε=0 circular baseline comparisons
3. Uniform vs Gaussian direct comparisons
4. r-z axial cross-sections
5. Circular vs linear polarization
6. Quantitative metrics table
"""

import sys
sys.path.insert(0, '.')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Annulus
from monte_carlo.richards_wolf import RichardsWolfSimulator
import os

print("="*80)
print("GENERATING PRESENTATION PLOTS")
print("="*80)

# Parameters
wavelength = 0.532  # μm
n_medium = 1.0

# Output directory
output_dir = 'data/comprehensive_comparison/presentation'
os.makedirs(output_dir, exist_ok=True)

# =============================================================================
# PART 1: GAUSSIAN APERTURE PROFILES
# =============================================================================
print("\n" + "="*80)
print("PART 1: Gaussian Aperture Profiles")
print("="*80)

def plot_gaussian_profiles():
    """Plot Gaussian beam profiles relative to aperture geometry."""

    alpha_values = [1.0, 2.0, 4.0]
    epsilon_values = [0, 0.5, 0.99]

    # Normalized radial coordinate (0 to 1 = aperture edge)
    rho = np.linspace(0, 1.2, 200)

    # Figure 1: Gaussian profiles for different α (circular aperture)
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['#e41a1c', '#377eb8', '#4daf4a']

    for alpha, color in zip(alpha_values, colors):
        A = np.exp(-alpha * rho**2)
        ax.plot(rho, A, color=color, lw=2.5, label=f'α = {alpha}')

    ax.axvline(1.0, color='black', ls='--', lw=2, label='Aperture edge')
    ax.axhline(np.exp(-1), color='gray', ls=':', lw=1, alpha=0.7, label='1/e level')
    ax.fill_between(rho, 0, 1, where=rho <= 1, alpha=0.1, color='blue')

    ax.set_xlabel('Normalized radius ρ = r/r_aperture', fontsize=12)
    ax.set_ylabel('Gaussian Amplitude A(ρ)', fontsize=12)
    ax.set_title('Gaussian Beam Truncation: Effect of α', fontsize=13, fontweight='bold')
    ax.legend(loc='upper right', fontsize=11)
    ax.set_xlim([0, 1.2])
    ax.set_ylim([0, 1.1])
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f'{output_dir}/gaussian_profiles_alpha.png', dpi=200)
    plt.close()
    print(f"  ✓ Saved: gaussian_profiles_alpha.png")

    # Figure 2: Gaussian on annular aperture (showing same profile for inner/outer)
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    alpha = 2.0
    A = np.exp(-alpha * rho**2)

    for i, eps in enumerate(epsilon_values):
        ax = axes[i]

        # Plot Gaussian
        ax.plot(rho, A, 'b-', lw=2.5, label=f'Gaussian (α={alpha})')

        # Shade regions
        if eps > 0:
            ax.fill_between(rho, 0, A, where=rho <= eps, alpha=0.3, color='red',
                           label=f'Blocked (ε={eps})')
            ax.fill_between(rho, 0, A, where=(rho > eps) & (rho <= 1), alpha=0.3,
                           color='green', label='Transmitted')
            ax.axvline(eps, color='red', ls='--', lw=2)
        else:
            ax.fill_between(rho, 0, A, where=rho <= 1, alpha=0.3, color='green',
                           label='Transmitted')

        ax.axvline(1.0, color='black', ls='--', lw=2, label='Outer edge')

        eps_label = '0 (Circular)' if eps == 0 else eps
        ax.set_title(f'ε = {eps_label}', fontsize=12, fontweight='bold')
        ax.set_xlabel('ρ = r/r_outer', fontsize=11)
        if i == 0:
            ax.set_ylabel('Amplitude', fontsize=11)
        ax.legend(loc='upper right', fontsize=9)
        ax.set_xlim([0, 1.2])
        ax.set_ylim([0, 1.1])
        ax.grid(True, alpha=0.3)

    fig.suptitle(f'Gaussian Illumination on Annular Apertures (α = {alpha})\n'
                 'Same physical beam, different obstruction ratios',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/gaussian_on_annular.png', dpi=200)
    plt.close()
    print(f"  ✓ Saved: gaussian_on_annular.png")

    # Figure 3: 2D aperture visualization
    fig, axes = plt.subplots(2, 3, figsize=(14, 9))

    x = np.linspace(-1.3, 1.3, 300)
    y = np.linspace(-1.3, 1.3, 300)
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2)

    for row, alpha in enumerate([2.0, 4.0]):
        G = np.exp(-alpha * R**2)

        for col, eps in enumerate(epsilon_values):
            ax = axes[row, col]

            # Apply aperture mask
            if eps > 0:
                mask = (R >= eps) & (R <= 1)
            else:
                mask = R <= 1

            G_masked = np.where(mask, G, 0)

            im = ax.imshow(G_masked, extent=[-1.3, 1.3, -1.3, 1.3],
                          cmap='hot', vmin=0, vmax=1, origin='lower')

            # Draw aperture boundaries
            circle_outer = plt.Circle((0, 0), 1.0, fill=False, color='cyan', lw=2)
            ax.add_patch(circle_outer)
            if eps > 0:
                circle_inner = plt.Circle((0, 0), eps, fill=False, color='cyan', lw=2, ls='--')
                ax.add_patch(circle_inner)

            eps_label = '0' if eps == 0 else eps
            ax.set_title(f'α={alpha}, ε={eps_label}', fontsize=11)
            ax.set_xlabel('x/r_outer')
            if col == 0:
                ax.set_ylabel('y/r_outer')
            ax.set_aspect('equal')

    fig.suptitle('2D Gaussian Aperture Illumination', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/gaussian_2d_apertures.png', dpi=200)
    plt.close()
    print(f"  ✓ Saved: gaussian_2d_apertures.png")

plot_gaussian_profiles()

# =============================================================================
# PART 2: BASELINE COMPARISONS (ε=0 CIRCULAR)
# =============================================================================
print("\n" + "="*80)
print("PART 2: Circular Baseline (ε=0) Comparisons")
print("="*80)

def compute_radial_intensity(NA, input_field, alpha=1.0, epsilon=0, polarization='x',
                             gaussian_reference_na=None, n_points=150):
    """Compute radial intensity profile."""
    airy_r = 0.61 * wavelength / NA
    r_max = 3 * airy_r
    r = np.linspace(0, r_max, n_points)
    z = np.zeros_like(r)

    # Outer aperture
    rw_outer = RichardsWolfSimulator(
        wavelength=wavelength,
        numerical_aperture=NA,
        n_medium=n_medium,
        polarization=polarization,
        input_field=input_field,
        truncation_coeff=alpha,
        gaussian_reference_na=gaussian_reference_na
    )

    Ex_out, Ey_out, Ez_out = rw_outer.compute_field(r, z)

    if epsilon > 0.001:
        NA_inner = NA * epsilon
        ref_na = gaussian_reference_na if gaussian_reference_na else NA
        rw_inner = RichardsWolfSimulator(
            wavelength=wavelength,
            numerical_aperture=NA_inner,
            n_medium=n_medium,
            polarization=polarization,
            input_field=input_field,
            truncation_coeff=alpha,
            gaussian_reference_na=ref_na if input_field == 'gaussian' else None
        )
        Ex_in, Ey_in, Ez_in = rw_inner.compute_field(r, z)
        Ex = Ex_out - Ex_in
        Ey = Ey_out - Ey_in
        Ez = Ez_out - Ez_in
    else:
        Ex, Ey, Ez = Ex_out, Ey_out, Ez_out

    I_total = np.abs(Ex)**2 + np.abs(Ey)**2 + np.abs(Ez)**2
    I_Ex = np.abs(Ex)**2
    I_Ey = np.abs(Ey)**2
    I_Ez = np.abs(Ez)**2

    return {
        'r': r,
        'airy_r': airy_r,
        'I_total': I_total / I_total.max(),
        'I_Ex': I_Ex / I_Ex.max() if I_Ex.max() > 0 else I_Ex,
        'I_Ey': I_Ey / I_total.max(),  # Normalized to total for comparison
        'I_Ez': I_Ez / I_total.max(),
    }

def plot_circular_baselines():
    """Plot circular aperture (ε=0) as baseline."""

    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    # Low NA
    NA = 0.1
    for ax_row, (input_type, alphas) in enumerate([
        ('uniform', [None]),
        ('gaussian', [1.0, 2.0, 4.0])
    ]):
        ax = axes[0, ax_row]

        for alpha in alphas:
            result = compute_radial_intensity(NA, input_type, alpha=alpha if alpha else 1.0)
            label = f'Uniform' if input_type == 'uniform' else f'Gaussian α={alpha}'
            ax.plot(result['r'], result['I_total'], lw=2, label=label)

        ax.axvline(result['airy_r'], color='gray', ls='--', lw=1.5, alpha=0.7)
        ax.set_xlabel('r (μm)', fontsize=11)
        ax.set_ylabel('Normalized Intensity', fontsize=11)
        title = 'Uniform' if input_type == 'uniform' else 'Gaussian (varying α)'
        ax.set_title(f'Low NA = {NA}: {title}', fontsize=12, fontweight='bold')
        ax.legend(fontsize=10)
        ax.set_xlim([0, result['r'].max()])
        ax.set_ylim([0, 1.05])
        ax.grid(True, alpha=0.3)

    # High NA
    NA = 0.9
    for ax_row, (input_type, alphas) in enumerate([
        ('uniform', [None]),
        ('gaussian', [1.0, 2.0, 4.0])
    ]):
        ax = axes[1, ax_row]

        for alpha in alphas:
            result = compute_radial_intensity(NA, input_type, alpha=alpha if alpha else 1.0)
            label = f'Uniform' if input_type == 'uniform' else f'Gaussian α={alpha}'
            ax.plot(result['r'], result['I_total'], lw=2, label=label)

        ax.axvline(result['airy_r'], color='gray', ls='--', lw=1.5, alpha=0.7)
        ax.set_xlabel('r (μm)', fontsize=11)
        ax.set_ylabel('Normalized Intensity', fontsize=11)
        title = 'Uniform' if input_type == 'uniform' else 'Gaussian (varying α)'
        ax.set_title(f'High NA = {NA}: {title}', fontsize=12, fontweight='bold')
        ax.legend(fontsize=10)
        ax.set_xlim([0, result['r'].max()])
        ax.set_ylim([0, 1.05])
        ax.grid(True, alpha=0.3)

    fig.suptitle('Circular Aperture Baseline (ε = 0): Total Intensity',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/circular_baseline.png', dpi=200)
    plt.close()
    print(f"  ✓ Saved: circular_baseline.png")

plot_circular_baselines()

# =============================================================================
# PART 3: UNIFORM vs GAUSSIAN DIRECT COMPARISON
# =============================================================================
print("\n" + "="*80)
print("PART 3: Uniform vs Gaussian Direct Comparison")
print("="*80)

def plot_uniform_vs_gaussian():
    """Direct comparison of uniform vs Gaussian for same ε."""

    epsilon_values = [0, 0.5, 0.99]
    NA_values = [0.1, 0.9]
    alpha = 2.0

    for NA in NA_values:
        fig, axes = plt.subplots(1, 3, figsize=(16, 5))
        na_label = 'Low' if NA < 0.5 else 'High'

        for i, eps in enumerate(epsilon_values):
            ax = axes[i]

            # Uniform
            res_uni = compute_radial_intensity(NA, 'uniform', epsilon=eps)
            ax.plot(res_uni['r'], res_uni['I_total'], 'b-', lw=2.5, label='Uniform')

            # Gaussian
            res_gauss = compute_radial_intensity(NA, 'gaussian', alpha=alpha, epsilon=eps,
                                                  gaussian_reference_na=NA)
            ax.plot(res_gauss['r'], res_gauss['I_total'], 'r--', lw=2.5,
                   label=f'Gaussian α={alpha}')

            ax.axvline(res_uni['airy_r'], color='gray', ls=':', lw=1.5, alpha=0.7)

            eps_label = '0 (Circular)' if eps == 0 else eps
            ax.set_title(f'ε = {eps_label}', fontsize=12, fontweight='bold')
            ax.set_xlabel('r (μm)', fontsize=11)
            if i == 0:
                ax.set_ylabel('Normalized Intensity', fontsize=11)
            ax.legend(fontsize=10)
            ax.set_xlim([0, res_uni['r'].max()])
            ax.set_ylim([0, 1.05])
            ax.grid(True, alpha=0.3)

        fig.suptitle(f'{na_label} NA = {NA}: Uniform vs Gaussian Illumination',
                     fontsize=14, fontweight='bold')
        plt.tight_layout()
        filename = f'uniform_vs_gaussian_NA{str(NA).replace(".", "p")}.png'
        plt.savefig(f'{output_dir}/{filename}', dpi=200)
        plt.close()
        print(f"  ✓ Saved: {filename}")

plot_uniform_vs_gaussian()

# =============================================================================
# PART 4: FIELD COMPONENTS (Ex, Ey, Ez)
# =============================================================================
print("\n" + "="*80)
print("PART 4: Field Components (Ex, Ey, Ez)")
print("="*80)

def plot_field_components():
    """Show Ex, Ey, Ez contributions at low and high NA."""

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    for row, NA in enumerate([0.1, 0.9]):
        for col, input_type in enumerate(['uniform', 'gaussian']):
            ax = axes[row, col]

            alpha = 2.0 if input_type == 'gaussian' else 1.0
            result = compute_radial_intensity(NA, input_type, alpha=alpha)

            ax.plot(result['r'], result['I_Ex'], 'b-', lw=2.5, label='|Ex|²')
            ax.plot(result['r'], result['I_Ey'], 'g--', lw=2, label='|Ey|²')
            ax.plot(result['r'], result['I_Ez'], 'r:', lw=2.5, label='|Ez|²')
            ax.axvline(result['airy_r'], color='gray', ls='--', lw=1, alpha=0.5)

            na_label = 'Low' if NA < 0.5 else 'High'
            ax.set_title(f'{na_label} NA={NA}, {input_type.capitalize()}',
                        fontsize=12, fontweight='bold')
            ax.set_xlabel('r (μm)', fontsize=11)
            ax.set_ylabel('Intensity (norm. to total max)', fontsize=11)
            ax.legend(fontsize=10, loc='upper right')
            ax.set_xlim([0, result['r'].max()])
            ax.grid(True, alpha=0.3)

    fig.suptitle('Field Component Contributions (x-polarized input)\n'
                 'Low NA: |Ey|, |Ez| ≈ 0 (scalar);  High NA: |Ez| significant (vectorial)',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/field_components.png', dpi=200)
    plt.close()
    print(f"  ✓ Saved: field_components.png")

plot_field_components()

# =============================================================================
# PART 5: CIRCULAR vs LINEAR POLARIZATION
# =============================================================================
print("\n" + "="*80)
print("PART 5: Circular vs Linear Polarization")
print("="*80)

def plot_polarization_comparison():
    """Compare linear (x) vs circular polarization at high NA."""

    NA = 0.9

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    for col, input_type in enumerate(['uniform', 'gaussian']):
        ax = axes[col]
        alpha = 2.0 if input_type == 'gaussian' else 1.0

        # Linear x-polarization
        res_x = compute_radial_intensity(NA, input_type, alpha=alpha, polarization='x')
        ax.plot(res_x['r'], res_x['I_total'], 'b-', lw=2.5, label='Linear (x-pol)')

        # Circular polarization
        res_circ = compute_radial_intensity(NA, input_type, alpha=alpha, polarization='circular')
        ax.plot(res_circ['r'], res_circ['I_total'], 'r--', lw=2.5, label='Circular')

        ax.axvline(res_x['airy_r'], color='gray', ls=':', lw=1.5, alpha=0.7)
        ax.set_title(f'{input_type.capitalize()} Illumination', fontsize=12, fontweight='bold')
        ax.set_xlabel('r (μm)', fontsize=11)
        ax.set_ylabel('Normalized Intensity', fontsize=11)
        ax.legend(fontsize=11)
        ax.set_xlim([0, res_x['r'].max()])
        ax.set_ylim([0, 1.05])
        ax.grid(True, alpha=0.3)

    fig.suptitle(f'High NA = {NA}: Linear vs Circular Polarization\n'
                 'Circular gives rotationally symmetric PSF', fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/polarization_comparison.png', dpi=200)
    plt.close()
    print(f"  ✓ Saved: polarization_comparison.png")

plot_polarization_comparison()

# =============================================================================
# PART 6: r-z AXIAL CROSS-SECTIONS
# =============================================================================
print("\n" + "="*80)
print("PART 6: r-z Axial Cross-Sections")
print("="*80)

def compute_rz_intensity(NA, input_field, alpha=1.0, epsilon=0, polarization='x',
                          n_r=50, n_z=100):
    """Compute r-z intensity distribution."""
    airy_r = 0.61 * wavelength / NA

    # Axial range (depth of focus scales with 1/NA²)
    dof = wavelength / (NA**2)  # Approximate depth of focus

    r = np.linspace(0, 2 * airy_r, n_r)
    z = np.linspace(-3 * dof, 3 * dof, n_z)

    R, Z = np.meshgrid(r, z)
    r_flat = R.flatten()
    z_flat = Z.flatten()

    # Outer aperture
    rw_outer = RichardsWolfSimulator(
        wavelength=wavelength,
        numerical_aperture=NA,
        n_medium=n_medium,
        polarization=polarization,
        input_field=input_field,
        truncation_coeff=alpha
    )

    Ex_out, Ey_out, Ez_out = rw_outer.compute_field(r_flat, z_flat)

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
        Ex_in, Ey_in, Ez_in = rw_inner.compute_field(r_flat, z_flat)
        Ex = Ex_out - Ex_in
        Ey = Ey_out - Ey_in
        Ez = Ez_out - Ez_in
    else:
        Ex, Ey, Ez = Ex_out, Ey_out, Ez_out

    I = np.abs(Ex)**2 + np.abs(Ey)**2 + np.abs(Ez)**2
    I = I.reshape(R.shape)
    I = I / I.max()

    return R, Z, I, airy_r, dof

def plot_rz_sections():
    """Plot r-z axial cross-sections."""

    # Compare NA
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    for i, NA in enumerate([0.1, 0.9]):
        R, Z, I, airy_r, dof = compute_rz_intensity(NA, 'uniform', n_r=40, n_z=80)

        ax = axes[i]
        im = ax.contourf(Z, R, I, levels=20, cmap='hot')
        ax.contour(Z, R, I, levels=[0.5], colors='cyan', linewidths=2)
        plt.colorbar(im, ax=ax, label='Normalized Intensity')

        ax.set_xlabel('z (μm)', fontsize=12)
        ax.set_ylabel('r (μm)', fontsize=12)
        ax.set_title(f'NA = {NA}\nAiry r = {airy_r:.3f} μm, DOF ≈ {dof:.2f} μm',
                    fontsize=12, fontweight='bold')

    fig.suptitle('Axial (r-z) PSF Structure: Uniform Circular Aperture\n'
                 'Cyan line = FWHM contour', fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/rz_NA_comparison.png', dpi=200)
    plt.close()
    print(f"  ✓ Saved: rz_NA_comparison.png")

    # Compare epsilon at high NA
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    NA = 0.9

    for i, eps in enumerate([0, 0.5, 0.99]):
        R, Z, I, airy_r, dof = compute_rz_intensity(NA, 'uniform', epsilon=eps, n_r=40, n_z=80)

        ax = axes[i]
        im = ax.contourf(Z, R, I, levels=20, cmap='hot')
        ax.contour(Z, R, I, levels=[0.5], colors='cyan', linewidths=2)
        plt.colorbar(im, ax=ax, label='I/I₀')

        ax.set_xlabel('z (μm)', fontsize=11)
        if i == 0:
            ax.set_ylabel('r (μm)', fontsize=11)
        eps_label = '0 (Circular)' if eps == 0 else eps
        ax.set_title(f'ε = {eps_label}', fontsize=12, fontweight='bold')

    fig.suptitle(f'Axial PSF: Effect of Central Obstruction (NA = {NA}, Uniform)\n'
                 'Annular apertures have extended depth of focus', fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/rz_epsilon_comparison.png', dpi=200)
    plt.close()
    print(f"  ✓ Saved: rz_epsilon_comparison.png")

plot_rz_sections()

# =============================================================================
# PART 7: QUANTITATIVE METRICS TABLE
# =============================================================================
print("\n" + "="*80)
print("PART 7: Quantitative Metrics")
print("="*80)

def compute_fwhm(r, I):
    """Compute FWHM from intensity profile."""
    half_max = 0.5
    above_half = I >= half_max
    if above_half.any():
        indices = np.where(above_half)[0]
        if len(indices) > 0:
            return 2 * r[indices[-1]]
    return np.nan

def compute_sidelobe(I):
    """Compute first sidelobe level relative to peak."""
    # Find first minimum after peak
    peak_idx = np.argmax(I)
    if peak_idx < len(I) - 1:
        # Find local minimum
        for i in range(peak_idx + 1, len(I) - 1):
            if I[i] < I[i-1] and I[i] < I[i+1]:
                min_idx = i
                break
        else:
            return np.nan
        # Find next local maximum (first sidelobe)
        for i in range(min_idx + 1, len(I) - 1):
            if I[i] > I[i-1] and I[i] > I[i+1]:
                return I[i] * 100  # As percentage
        return np.nan
    return np.nan

def generate_metrics_table():
    """Generate quantitative metrics for all configurations."""

    configs = []

    # Configurations to test
    NA_values = [0.1, 0.9]
    epsilon_values = [0, 0.5, 0.99]

    for NA in NA_values:
        for eps in epsilon_values:
            # Uniform
            res = compute_radial_intensity(NA, 'uniform', epsilon=eps, n_points=200)
            fwhm = compute_fwhm(res['r'], res['I_total'])
            sidelobe = compute_sidelobe(res['I_total'])
            configs.append({
                'NA': NA, 'ε': eps, 'Type': 'Uniform', 'α': '-',
                'FWHM (μm)': fwhm, 'Sidelobe (%)': sidelobe,
                'Airy (μm)': res['airy_r']
            })

            # Gaussian
            for alpha in [1.0, 2.0, 4.0]:
                res = compute_radial_intensity(NA, 'gaussian', alpha=alpha, epsilon=eps,
                                               gaussian_reference_na=NA, n_points=200)
                fwhm = compute_fwhm(res['r'], res['I_total'])
                sidelobe = compute_sidelobe(res['I_total'])
                configs.append({
                    'NA': NA, 'ε': eps, 'Type': 'Gaussian', 'α': alpha,
                    'FWHM (μm)': fwhm, 'Sidelobe (%)': sidelobe,
                    'Airy (μm)': res['airy_r']
                })

    # Print table
    print("\n  Quantitative Metrics Summary")
    print("  " + "="*80)
    print(f"  {'NA':>4} {'ε':>5} {'Type':>10} {'α':>4} {'FWHM(μm)':>10} {'Sidelobe%':>10} {'Airy(μm)':>10}")
    print("  " + "-"*80)

    for c in configs:
        alpha_str = f"{c['α']:.1f}" if c['α'] != '-' else '-'
        fwhm_str = f"{c['FWHM (μm)']:.4f}" if not np.isnan(c['FWHM (μm)']) else 'N/A'
        side_str = f"{c['Sidelobe (%)']:.2f}" if not np.isnan(c['Sidelobe (%)']) else 'N/A'
        print(f"  {c['NA']:>4.1f} {c['ε']:>5.2f} {c['Type']:>10} {alpha_str:>4} "
              f"{fwhm_str:>10} {side_str:>10} {c['Airy (μm)']:>10.4f}")

    print("  " + "="*80)

    # Save to file
    with open(f'{output_dir}/metrics_table.txt', 'w') as f:
        f.write("Quantitative Metrics Summary\n")
        f.write("="*80 + "\n")
        f.write(f"{'NA':>4} {'ε':>5} {'Type':>10} {'α':>4} {'FWHM(μm)':>10} {'Sidelobe%':>10} {'Airy(μm)':>10}\n")
        f.write("-"*80 + "\n")
        for c in configs:
            alpha_str = f"{c['α']:.1f}" if c['α'] != '-' else '-'
            fwhm_str = f"{c['FWHM (μm)']:.4f}" if not np.isnan(c['FWHM (μm)']) else 'N/A'
            side_str = f"{c['Sidelobe (%)']:.2f}" if not np.isnan(c['Sidelobe (%)']) else 'N/A'
            f.write(f"{c['NA']:>4.1f} {c['ε']:>5.2f} {c['Type']:>10} {alpha_str:>4} "
                   f"{fwhm_str:>10} {side_str:>10} {c['Airy (μm)']:>10.4f}\n")

    print(f"\n  ✓ Saved: metrics_table.txt")

generate_metrics_table()

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "="*80)
print("COMPLETE: All presentation plots generated")
print("="*80)
print(f"\nOutput directory: {output_dir}/")
print("\nFiles generated:")
for f in sorted(os.listdir(output_dir)):
    print(f"  - {f}")
