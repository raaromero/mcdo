"""
Annular Aperture Depth of Field Study.

Computes:
1. Focal plane profiles for ε = 0.5, 0.99 at NA = 0.1, 0.9 with α = 4.0
2. Axial profiles I(r=0, z) to measure DOF
3. DOF vs epsilon plot for both NAs

Uses Babinet's principle: E_annular = E_outer - E_inner
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
    # Outer disk (full NA)
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
        # Inner disk (NA_inner = ε * NA_outer)
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

        # Babinet subtraction
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

    I_total = np.abs(Ex)**2 + np.abs(Ey)**2 + np.abs(Ez)**2
    I_ex = np.abs(Ex)**2

    # Normalize
    I_total = I_total / np.max(I_total)
    I_ex = I_ex / np.max(I_ex)

    return r_airy, I_total, I_ex


def compute_axial_profile(NA, epsilon, input_field='gaussian', alpha=4.0, n_points=100, z_max_dof=10):
    """Compute axial profile I(r=0, z) for DOF measurement."""
    # DOF scale: λ/NA² for circular
    dof_scale = wavelength / (NA**2)
    z_um = np.linspace(-z_max_dof * dof_scale, z_max_dof * dof_scale, n_points)
    r = np.zeros_like(z_um)

    Ex, Ey, Ez, _ = compute_annular_field(NA, epsilon, r, z_um, input_field, alpha)

    I_total = np.abs(Ex)**2 + np.abs(Ey)**2 + np.abs(Ez)**2

    # Normalize to peak (should be at z=0)
    I_total = I_total / np.max(I_total)

    # Convert z to DOF units
    z_dof = z_um / dof_scale

    return z_dof, I_total, z_um


def measure_dof(z_dof, intensity, threshold=0.5):
    """Measure DOF as FWHM (where intensity drops to threshold of peak)."""
    # Find where intensity crosses threshold
    above_threshold = intensity >= threshold

    if not np.any(above_threshold):
        return np.nan

    # Find first and last indices above threshold
    indices = np.where(above_threshold)[0]
    if len(indices) < 2:
        return np.nan

    # Interpolate for better accuracy
    z_min = z_dof[indices[0]]
    z_max = z_dof[indices[-1]]

    # Refine with interpolation at boundaries
    for i in range(len(intensity) - 1):
        if intensity[i] < threshold <= intensity[i+1]:
            # Rising edge
            frac = (threshold - intensity[i]) / (intensity[i+1] - intensity[i])
            z_min = z_dof[i] + frac * (z_dof[i+1] - z_dof[i])
            break

    for i in range(len(intensity) - 1, 0, -1):
        if intensity[i] < threshold <= intensity[i-1]:
            # Falling edge
            frac = (threshold - intensity[i]) / (intensity[i-1] - intensity[i])
            z_max = z_dof[i] + frac * (z_dof[i-1] - z_dof[i])
            break

    return z_max - z_min


def main():
    nas = [0.1, 0.9]
    epsilons_main = [0.0, 0.5, 0.99]

    # =========================================================================
    # Part 1: Focal plane profiles for ε = 0, 0.5, 0.99
    # =========================================================================
    print("=" * 60)
    print("Part 1: Focal Plane Profiles")
    print("=" * 60)

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    colors = {'0.0': 'k', '0.5': 'tab:blue', '0.99': 'tab:orange'}
    linestyles = {'0.0': '-', '0.5': '--', '0.99': ':'}

    for row, na in enumerate(nas):
        print(f"\nNA = {na}")
        print("-" * 40)

        # Left: Radial profiles
        ax = axes[row, 0]
        for eps in epsilons_main:
            print(f"  ε = {eps}: computing radial profile...")
            r_airy, I_total, I_ex = compute_radial_profile(na, eps, 'gaussian', alpha)
            label = f'ε={eps}' if eps > 0 else 'Circular (ε=0)'
            ax.plot(r_airy, I_ex, color=colors[str(eps)], ls=linestyles[str(eps)],
                    lw=2, label=label)

        ax.set_xlabel('r / r_Airy', fontsize=11)
        ax.set_ylabel('Normalized Intensity (Ex)', fontsize=11)
        ax.set_title(f'Focal Plane Profile (NA={na}, α={alpha})', fontsize=12, fontweight='bold')
        ax.set_xlim(0, 4)
        ax.set_ylim(0, 1.05)
        ax.axhline(0.5, color='gray', ls=':', alpha=0.5)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)

        # Right: Axial profiles
        ax = axes[row, 1]
        for eps in epsilons_main:
            print(f"  ε = {eps}: computing axial profile...")
            z_dof, I_axial, z_um = compute_axial_profile(na, eps, 'gaussian', alpha, n_points=80)
            dof = measure_dof(z_dof, I_axial)
            label = f'ε={eps} (DOF={dof:.2f})' if eps > 0 else f'Circular (DOF={dof:.2f})'
            ax.plot(z_dof, I_axial, color=colors[str(eps)], ls=linestyles[str(eps)],
                    lw=2, label=label)

        ax.set_xlabel('z / (λ/NA²)', fontsize=11)
        ax.set_ylabel('Normalized Axial Intensity', fontsize=11)
        ax.set_title(f'Axial Profile (NA={na}, α={alpha})', fontsize=12, fontweight='bold')
        ax.set_xlim(-5, 5)
        ax.set_ylim(0, 1.05)
        ax.axhline(0.5, color='gray', ls=':', alpha=0.5, label='50% threshold')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)

    plt.suptitle(f'Annular Aperture: Gaussian α={alpha}', fontsize=14, y=1.01)
    plt.tight_layout()
    save_path = OUTPUT_DIR / "annular_profiles.png"
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\nSaved: {save_path}")

    # =========================================================================
    # Part 2: DOF vs Epsilon
    # =========================================================================
    print("\n" + "=" * 60)
    print("Part 2: DOF vs Epsilon")
    print("=" * 60)

    epsilons_sweep = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99]

    dof_results = {0.1: [], 0.9: []}

    for na in nas:
        print(f"\nNA = {na}")
        for eps in epsilons_sweep:
            print(f"  ε = {eps}...", end=" ")
            # Extend z range for high epsilon (DOF grows as 1/(1-ε²))
            z_max = 15 if eps < 0.9 else (30 if eps < 0.95 else 100)
            z_dof, I_axial, _ = compute_axial_profile(na, eps, 'gaussian', alpha, n_points=100, z_max_dof=z_max)
            dof = measure_dof(z_dof, I_axial)
            dof_results[na].append(dof)
            print(f"DOF = {dof:.3f}")

    # Theoretical prediction: DOF_annular / DOF_circular = 1 / (1 - ε²)
    eps_theory = np.array(epsilons_sweep)
    dof_theory_ratio = 1 / (1 - eps_theory**2 + 1e-10)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Left: Absolute DOF
    ax = axes[0]
    ax.plot(epsilons_sweep, dof_results[0.1], 'o-', color='tab:blue', lw=2, markersize=8, label='NA = 0.1')
    ax.plot(epsilons_sweep, dof_results[0.9], 's-', color='tab:orange', lw=2, markersize=8, label='NA = 0.9')
    ax.set_xlabel('ε (obstruction ratio)', fontsize=12)
    ax.set_ylabel('DOF (in units of λ/NA²)', fontsize=12)
    ax.set_title(f'Depth of Field vs Obstruction Ratio (α={alpha})', fontsize=13)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 1)

    # Right: DOF ratio (normalized to circular)
    ax = axes[1]
    dof_ratio_01 = np.array(dof_results[0.1]) / dof_results[0.1][0]
    dof_ratio_09 = np.array(dof_results[0.9]) / dof_results[0.9][0]

    ax.plot(epsilons_sweep, dof_ratio_01, 'o-', color='tab:blue', lw=2, markersize=8, label='NA = 0.1 (simulated)')
    ax.plot(epsilons_sweep, dof_ratio_09, 's-', color='tab:orange', lw=2, markersize=8, label='NA = 0.9 (simulated)')
    ax.plot(eps_theory, dof_theory_ratio, 'k--', lw=1.5, label='Theory: 1/(1-ε²)')
    ax.set_xlabel('ε (obstruction ratio)', fontsize=12)
    ax.set_ylabel('DOF / DOF_circular', fontsize=12)
    ax.set_title('DOF Enhancement vs Theory', fontsize=13)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 15)

    plt.tight_layout()
    save_path = OUTPUT_DIR / "dof_vs_epsilon.png"
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\nSaved: {save_path}")

    # Print summary table
    print("\n" + "=" * 60)
    print("Summary: DOF in units of λ/NA²")
    print("=" * 60)
    print(f"{'ε':<8} {'NA=0.1':<12} {'NA=0.9':<12} {'Theory ratio':<12}")
    print("-" * 44)
    for i, eps in enumerate(epsilons_sweep):
        theory = 1 / (1 - eps**2 + 1e-10)
        print(f"{eps:<8.2f} {dof_results[0.1][i]:<12.3f} {dof_results[0.9][i]:<12.3f} {theory:<12.2f}")


if __name__ == "__main__":
    main()
