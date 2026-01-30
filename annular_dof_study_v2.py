"""
Annular Aperture Depth of Field Study - Version 2.

Improved version with:
1. Clear comparison of DOF definitions
2. Profile plots similar to alpha sweep
3. Both uniform and Gaussian illumination for comparison

DOF definitions:
- FWHM: Full width at half maximum (50% intensity)
- First zero: Distance to first axial zero
- Rayleigh: 80% intensity threshold
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from monte_carlo.richards_wolf import RichardsWolfSimulator

OUTPUT_DIR = Path("data/annular_dof")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Parameters
wavelength = 0.532  # μm
n_medium = 1.0
alpha = 4.0  # Gaussian truncation coefficient


def compute_annular_field(NA, epsilon, r_array, z_array, input_field='gaussian', alpha=4.0):
    """
    Compute annular aperture field using Babinet's principle.
    E_annular = E_outer_disk - E_inner_disk
    """
    rw_outer = RichardsWolfSimulator(
        wavelength=wavelength,
        numerical_aperture=NA,
        n_medium=n_medium,
        polarization='x',
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
            polarization='x',
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


def compute_radial_profile(NA, epsilon, input_field='gaussian', alpha=4.0, n_points=150, r_max_airy=5):
    """Compute radial focal plane profile (z=0)."""
    airy_r = 0.61 * wavelength / NA
    r_airy = np.linspace(0, r_max_airy, n_points)
    r_um = r_airy * airy_r
    z = np.zeros_like(r_um)

    Ex, Ey, Ez, _ = compute_annular_field(NA, epsilon, r_um, z, input_field, alpha)
    I_ex = np.abs(Ex)**2
    I_ex = I_ex / np.max(I_ex)

    return r_airy, I_ex


def compute_axial_profile(NA, epsilon, input_field='gaussian', alpha=4.0, n_points=150, z_max_um=None):
    """Compute axial profile I(r=0, z)."""
    dof_scale = wavelength / (NA**2)  # λ/NA² in μm

    if z_max_um is None:
        z_max_um = 10 * dof_scale

    z_um = np.linspace(-z_max_um, z_max_um, n_points)
    r = np.zeros_like(z_um)

    Ex, Ey, Ez, _ = compute_annular_field(NA, epsilon, r, z_um, input_field, alpha)
    I_total = np.abs(Ex)**2 + np.abs(Ey)**2 + np.abs(Ez)**2
    I_total = I_total / np.max(I_total)

    z_normalized = z_um / dof_scale  # In units of λ/NA²

    return z_normalized, I_total, z_um


def measure_dof_fwhm(z, intensity):
    """Measure DOF as FWHM (50% threshold)."""
    above = intensity >= 0.5
    if not np.any(above):
        return np.nan
    indices = np.where(above)[0]
    if len(indices) < 2:
        return np.nan
    return z[indices[-1]] - z[indices[0]]


def theoretical_axial_intensity_circular(z_normalized):
    """
    Theoretical axial intensity for uniformly illuminated circular aperture.
    I(z) = sinc²(π z / 2) where z is in units of λ/NA²

    Derivation: For paraxial, on-axis intensity is:
    I(u) ∝ sinc²(u/4) where u = k sin²(α) z = (2π/λ)(NA²/n²)(z) ≈ 2π NA² z / λ
    So u/4 = π NA² z / (2λ) = π z_norm / 2
    """
    arg = np.pi * z_normalized / 2
    # Avoid division by zero
    with np.errstate(divide='ignore', invalid='ignore'):
        sinc = np.where(np.abs(arg) < 1e-10, 1.0, np.sin(arg) / arg)
    return sinc**2


def theoretical_axial_intensity_annular(z_normalized, epsilon):
    """
    Theoretical axial intensity for uniformly illuminated annular aperture.

    For annular aperture, using Babinet: I_annular ∝ |sinc(outer) - ε² sinc(inner)|²
    where the inner has scaled argument.

    More precisely, for annular with obstruction ε:
    E(z) ∝ sinc(π z / 2) - ε² sinc(π ε² z / 2)
    """
    arg_out = np.pi * z_normalized / 2
    arg_in = np.pi * epsilon**2 * z_normalized / 2

    with np.errstate(divide='ignore', invalid='ignore'):
        sinc_out = np.where(np.abs(arg_out) < 1e-10, 1.0, np.sin(arg_out) / arg_out)
        sinc_in = np.where(np.abs(arg_in) < 1e-10, 1.0, np.sin(arg_in) / arg_in)

    # Amplitude subtraction (Babinet)
    E = sinc_out - epsilon**2 * sinc_in
    I = np.abs(E)**2
    return I / np.max(I)


def compute_2d_rz(NA, epsilon, input_field='gaussian', alpha=4.0, n_r=50, n_z=80, z_max_dof=5):
    """Compute 2D r-z intensity distribution."""
    airy_r = 0.61 * wavelength / NA
    dof_scale = wavelength / (NA**2)

    # r from 0 to 3 Airy radii
    r_um = np.linspace(0, 3 * airy_r, n_r)
    # z symmetric around focus
    z_um = np.linspace(-z_max_dof * dof_scale, z_max_dof * dof_scale, n_z)

    R, Z = np.meshgrid(r_um, z_um)
    r_flat = R.flatten()
    z_flat = Z.flatten()

    Ex, Ey, Ez, _ = compute_annular_field(NA, epsilon, r_flat, z_flat, input_field, alpha)

    I_total = (np.abs(Ex)**2 + np.abs(Ey)**2 + np.abs(Ez)**2).reshape(R.shape)
    I_total = I_total / np.max(I_total)

    # Normalize coordinates
    R_airy = R / airy_r
    Z_dof = Z / dof_scale

    return R_airy, Z_dof, I_total


def main():
    nas = [0.1, 0.9]
    epsilons = [0.0, 0.5, 0.99]
    colors = {'0.0': 'k', '0.5': 'tab:blue', '0.99': 'tab:orange'}
    linestyles = {'0.0': '-', '0.5': '--', '0.99': ':'}

    # =========================================================================
    # Figure 1: Compare simulation vs theory for UNIFORM illumination
    # =========================================================================
    print("=" * 60)
    print("Figure 1: Simulation vs Theory (Uniform Illumination)")
    print("=" * 60)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    for row, na in enumerate(nas):
        print(f"\nNA = {na}")

        # Determine z range
        z_max_um = 15 * wavelength / (na**2)

        # Left: Radial profiles
        ax = axes[row, 0]
        for eps in epsilons:
            r_airy, I_ex = compute_radial_profile(na, eps, 'uniform', alpha=1.0)
            label = f'ε={eps}' if eps > 0 else 'Circular (ε=0)'
            ax.plot(r_airy, I_ex, color=colors[str(eps)], ls='-', lw=2, label=label)

        ax.set_xlabel('r / r_Airy', fontsize=11)
        ax.set_ylabel('Normalized Intensity', fontsize=11)
        ax.set_title(f'Radial Profile - Uniform (NA={na})', fontsize=12, fontweight='bold')
        ax.set_xlim(0, 4)
        ax.set_ylim(0, 1.05)
        ax.axhline(0.5, color='gray', ls=':', alpha=0.5)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)

        # Right: Axial profiles - simulation vs theory
        ax = axes[row, 1]
        for eps in epsilons:
            z_norm, I_sim, _ = compute_axial_profile(na, eps, 'uniform', alpha=1.0, n_points=150,
                                                      z_max_um=z_max_um)

            # Theoretical
            if eps < 0.01:
                I_theory = theoretical_axial_intensity_circular(z_norm)
            else:
                I_theory = theoretical_axial_intensity_annular(z_norm, eps)

            label_sim = f'ε={eps} (RW)' if eps > 0 else 'Circular (RW)'
            label_th = f'ε={eps} (theory)' if eps > 0 else 'Circular (theory)'

            ax.plot(z_norm, I_sim, color=colors[str(eps)], ls='-', lw=2, label=label_sim)
            ax.plot(z_norm, I_theory, color=colors[str(eps)], ls='--', lw=1, alpha=0.7)

            # Measure DOF
            dof_sim = measure_dof_fwhm(z_norm, I_sim)
            dof_theory = measure_dof_fwhm(z_norm, I_theory)
            print(f"  ε={eps}: DOF_sim={dof_sim:.3f}, DOF_theory={dof_theory:.3f}")

        ax.set_xlabel('z / (λ/NA²)', fontsize=11)
        ax.set_ylabel('Normalized Axial Intensity', fontsize=11)
        ax.set_title(f'Axial Profile - Uniform (NA={na})\nSolid=RW, Dashed=Theory', fontsize=12, fontweight='bold')
        ax.set_xlim(-8, 8)
        ax.set_ylim(0, 1.05)
        ax.axhline(0.5, color='gray', ls=':', alpha=0.5)
        ax.legend(fontsize=8, loc='upper right')
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    save_path = OUTPUT_DIR / "uniform_sim_vs_theory.png"
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\nSaved: {save_path}")

    # =========================================================================
    # Figure 2: Gaussian illumination (α=4) profiles
    # =========================================================================
    print("\n" + "=" * 60)
    print(f"Figure 2: Gaussian Illumination (α={alpha})")
    print("=" * 60)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    for row, na in enumerate(nas):
        print(f"\nNA = {na}")
        z_max_um = 15 * wavelength / (na**2) if na > 0.5 else 20 * wavelength / (na**2)

        # Left: Radial profiles
        ax = axes[row, 0]
        for eps in epsilons:
            r_airy, I_ex = compute_radial_profile(na, eps, 'gaussian', alpha)
            label = f'ε={eps}' if eps > 0 else 'Circular (ε=0)'
            ax.plot(r_airy, I_ex, color=colors[str(eps)], ls=linestyles[str(eps)], lw=2, label=label)

        ax.set_xlabel('r / r_Airy', fontsize=11)
        ax.set_ylabel('Normalized Intensity (Ex)', fontsize=11)
        ax.set_title(f'Radial Profile - Gaussian α={alpha} (NA={na})', fontsize=12, fontweight='bold')
        ax.set_xlim(0, 4)
        ax.set_ylim(0, 1.05)
        ax.axhline(0.5, color='gray', ls=':', alpha=0.5)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)

        # Right: Axial profiles
        ax = axes[row, 1]
        for eps in epsilons:
            # Extend z range for high epsilon
            z_max_this = z_max_um * (5 if eps > 0.9 else 1)
            z_norm, I_sim, _ = compute_axial_profile(na, eps, 'gaussian', alpha, n_points=150,
                                                      z_max_um=z_max_this)

            dof = measure_dof_fwhm(z_norm, I_sim)
            label = f'ε={eps} (DOF={dof:.2f})' if eps > 0 else f'Circular (DOF={dof:.2f})'
            ax.plot(z_norm, I_sim, color=colors[str(eps)], ls=linestyles[str(eps)], lw=2, label=label)
            print(f"  ε={eps}: DOF={dof:.3f}")

        ax.set_xlabel('z / (λ/NA²)', fontsize=11)
        ax.set_ylabel('Normalized Axial Intensity', fontsize=11)
        ax.set_title(f'Axial Profile - Gaussian α={alpha} (NA={na})', fontsize=12, fontweight='bold')
        ax.set_xlim(-10, 10)
        ax.set_ylim(0, 1.05)
        ax.axhline(0.5, color='gray', ls=':', alpha=0.5)
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    save_path = OUTPUT_DIR / "gaussian_profiles.png"
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\nSaved: {save_path}")

    # =========================================================================
    # Figure 3: DOF vs Epsilon with proper theory comparison
    # =========================================================================
    print("\n" + "=" * 60)
    print("Figure 3: DOF vs Epsilon")
    print("=" * 60)

    epsilons_sweep = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99]

    # Compute theoretical DOF for uniform circular (baseline)
    z_test = np.linspace(-10, 10, 500)
    I_circ_theory = theoretical_axial_intensity_circular(z_test)
    dof_theory_circular = measure_dof_fwhm(z_test, I_circ_theory)
    print(f"Theoretical DOF (uniform circular): {dof_theory_circular:.3f} × λ/NA²")

    results = {
        'uniform': {0.1: [], 0.9: []},
        'gaussian': {0.1: [], 0.9: []},
        'theory': []
    }

    # Compute theoretical DOF ratio for each epsilon
    for eps in epsilons_sweep:
        z_range = 50 if eps > 0.9 else 15
        z_test = np.linspace(-z_range, z_range, 500)
        if eps < 0.01:
            I_th = theoretical_axial_intensity_circular(z_test)
        else:
            I_th = theoretical_axial_intensity_annular(z_test, eps)
        dof_th = measure_dof_fwhm(z_test, I_th)
        results['theory'].append(dof_th)

    # Compute simulated DOF
    for na in nas:
        print(f"\nNA = {na}")
        for eps in epsilons_sweep:
            z_max = 15 if eps < 0.9 else (50 if eps < 0.95 else 150)
            z_max_um = z_max * wavelength / (na**2)

            # Uniform
            z_norm, I_sim, _ = compute_axial_profile(na, eps, 'uniform', 1.0, n_points=150, z_max_um=z_max_um)
            dof_u = measure_dof_fwhm(z_norm, I_sim)
            results['uniform'][na].append(dof_u)

            # Gaussian
            z_norm, I_sim, _ = compute_axial_profile(na, eps, 'gaussian', alpha, n_points=150, z_max_um=z_max_um)
            dof_g = measure_dof_fwhm(z_norm, I_sim)
            results['gaussian'][na].append(dof_g)

            print(f"  ε={eps}: Uniform={dof_u:.2f}, Gaussian={dof_g:.2f}, Theory={results['theory'][epsilons_sweep.index(eps)]:.2f}")

    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Left: Absolute DOF
    ax = axes[0]
    ax.plot(epsilons_sweep, results['theory'], 'k--', lw=2, label='Theory (paraxial, uniform)')
    ax.plot(epsilons_sweep, results['uniform'][0.1], 'o-', color='tab:blue', lw=2, markersize=6,
            label='NA=0.1, Uniform (RW)')
    ax.plot(epsilons_sweep, results['gaussian'][0.1], 's--', color='tab:blue', lw=1.5, markersize=5,
            alpha=0.7, label=f'NA=0.1, Gaussian α={alpha}')
    ax.plot(epsilons_sweep, results['uniform'][0.9], 'o-', color='tab:orange', lw=2, markersize=6,
            label='NA=0.9, Uniform (RW)')
    ax.plot(epsilons_sweep, results['gaussian'][0.9], 's--', color='tab:orange', lw=1.5, markersize=5,
            alpha=0.7, label=f'NA=0.9, Gaussian α={alpha}')

    ax.set_xlabel('ε (obstruction ratio)', fontsize=12)
    ax.set_ylabel('DOF (in units of λ/NA²)', fontsize=12)
    ax.set_title('Depth of Field vs Obstruction Ratio', fontsize=13)
    ax.legend(fontsize=9, loc='upper left')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 50)

    # Right: Ratio to circular
    ax = axes[1]
    theory_ratio = np.array(results['theory']) / results['theory'][0]
    ax.plot(epsilons_sweep, theory_ratio, 'k--', lw=2, label='Theory (paraxial)')

    for na, color in [(0.1, 'tab:blue'), (0.9, 'tab:orange')]:
        ratio_u = np.array(results['uniform'][na]) / results['uniform'][na][0]
        ratio_g = np.array(results['gaussian'][na]) / results['gaussian'][na][0]
        ax.plot(epsilons_sweep, ratio_u, 'o-', color=color, lw=2, markersize=6, label=f'NA={na}, Uniform')
        ax.plot(epsilons_sweep, ratio_g, 's--', color=color, lw=1.5, markersize=5, alpha=0.7,
                label=f'NA={na}, Gaussian')

    # Simple theory: 1/(1-ε²)
    eps_fine = np.linspace(0, 0.99, 100)
    simple_ratio = 1 / (1 - eps_fine**2)
    ax.plot(eps_fine, simple_ratio, 'r:', lw=1.5, alpha=0.5, label='Simple: 1/(1-ε²)')

    ax.set_xlabel('ε (obstruction ratio)', fontsize=12)
    ax.set_ylabel('DOF / DOF_circular', fontsize=12)
    ax.set_title('DOF Enhancement Ratio', fontsize=13)
    ax.legend(fontsize=8, loc='upper left')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 30)

    plt.tight_layout()
    save_path = OUTPUT_DIR / "dof_vs_epsilon_v2.png"
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\nSaved: {save_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY: Why Theory vs Simulation Differ")
    print("=" * 60)
    print(f"""
The simple formula DOF = 2λ/(NA²(1-ε²)) comes from:
  - Paraxial approximation (small angles)
  - Uniform illumination
  - Scalar diffraction (ignores polarization)

Our Richards-Wolf simulation includes:
  - Full vectorial diffraction (Ex, Ey, Ez components)
  - High NA effects (large angles)
  - Gaussian apodization (α={alpha})

For LOW NA (0.1):
  - Paraxial valid → Uniform RW ≈ Theory
  - Small deviation from simple 1/(1-ε²) due to exact sinc formula

For HIGH NA (0.9):
  - Vectorial effects significant
  - Ez component becomes large
  - Aplanatic factor (√cos θ) matters
  - DOF behavior deviates from paraxial prediction

Note: 2D contour plots already exist in data/presentation_slides/sec3_lowNA_annular/ and sec5_highNA_annular/
""")


if __name__ == "__main__":
    main()
