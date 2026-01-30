"""
Compare DOF: Uniform vs Gaussian α=0.4 (near-uniform) vs Gaussian α=4.0
Similar format to uniform_dof_test.png
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from monte_carlo.richards_wolf import RichardsWolfSimulator

OUTPUT_DIR = Path("data/annular_dof")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

wavelength = 0.532
n_medium = 1.0


def compute_annular_field(NA, epsilon, r_array, z_array, input_field='uniform', alpha=1.0):
    rw_outer = RichardsWolfSimulator(
        wavelength=wavelength, numerical_aperture=NA, n_medium=n_medium,
        polarization='x', input_field=input_field, truncation_coeff=alpha
    )
    Ex_out, Ey_out, Ez_out = rw_outer.compute_field(r_array, z_array)

    if epsilon > 0.001:
        NA_inner = NA * epsilon
        rw_inner = RichardsWolfSimulator(
            wavelength=wavelength, numerical_aperture=NA_inner, n_medium=n_medium,
            polarization='x', input_field=input_field, truncation_coeff=alpha,
            gaussian_reference_na=NA if input_field == 'gaussian' else None
        )
        Ex_in, Ey_in, Ez_in = rw_inner.compute_field(r_array, z_array)
        Ex, Ey, Ez = Ex_out - Ex_in, Ey_out - Ey_in, Ez_out - Ez_in
    else:
        Ex, Ey, Ez = Ex_out, Ey_out, Ez_out
    return Ex, Ey, Ez


def compute_axial_profile(NA, epsilon, input_field='uniform', alpha=1.0, n_points=200, z_max_dof=10):
    dof_scale = wavelength / (NA**2)
    z_um = np.linspace(-z_max_dof * dof_scale, z_max_dof * dof_scale, n_points)
    r = np.zeros_like(z_um)
    Ex, Ey, Ez = compute_annular_field(NA, epsilon, r, z_um, input_field, alpha)
    I = np.abs(Ex)**2 + np.abs(Ey)**2 + np.abs(Ez)**2
    return z_um / dof_scale, I / np.max(I)


def measure_dof(z, intensity, threshold=0.5):
    above = intensity >= threshold
    if not np.any(above):
        return np.nan
    indices = np.where(above)[0]
    return z[indices[-1]] - z[indices[0]] if len(indices) >= 2 else np.nan


def theoretical_sinc2(z_norm):
    arg = np.pi * z_norm / 2
    with np.errstate(divide='ignore', invalid='ignore'):
        sinc = np.where(np.abs(arg) < 1e-10, 1.0, np.sin(arg) / arg)
    return sinc**2


def main():
    print("=" * 70)
    print("DOF Comparison: Uniform vs Gaussian α=0.4 vs Gaussian α=4.0")
    print("=" * 70)

    # Theory
    z_fine = np.linspace(-10, 10, 2000)
    I_theory = theoretical_sinc2(z_fine)
    dof_theory = measure_dof(z_fine, I_theory)
    print(f"Theory DOF (sinc² FWHM): {dof_theory:.4f} × λ/NA²\n")

    nas = [0.1, 0.9]
    epsilons = [0.0, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99]

    configs = [
        ('uniform', 1.0, 'Uniform', 'tab:blue'),
        ('gaussian', 0.4, 'Gaussian α=0.4', 'tab:green'),
        ('gaussian', 4.0, 'Gaussian α=4.0', 'tab:red'),
    ]

    results = {c[2]: {na: [] for na in nas} for c in configs}

    # Compute all
    for na in nas:
        print(f"\nNA = {na}")
        print("-" * 50)
        for input_field, alpha, label, _ in configs:
            print(f"  {label}:")
            for eps in epsilons:
                z_max = 10 if eps < 0.9 else (30 if eps < 0.95 else 100)
                z_norm, I_z = compute_axial_profile(na, eps, input_field, alpha, 200, z_max)
                dof = measure_dof(z_norm, I_z)
                results[label][na].append(dof)
                print(f"    ε={eps:.2f}: DOF={dof:.3f}")

    # =========================================================================
    # Figure 1: Axial profiles for circular aperture (ε=0)
    # =========================================================================
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    for col, na in enumerate(nas):
        ax = axes[col]

        # Theory
        ax.plot(z_fine, I_theory, 'k--', lw=1.5, alpha=0.7, label=f'Theory sinc² (DOF={dof_theory:.2f})')

        # Each config
        for input_field, alpha, label, color in configs:
            z_norm, I_z = compute_axial_profile(na, 0.0, input_field, alpha, 200, 10)
            dof = measure_dof(z_norm, I_z)
            ax.plot(z_norm, I_z, color=color, lw=2, label=f'{label} (DOF={dof:.2f})')

        ax.axhline(0.5, color='gray', ls=':', alpha=0.5)
        ax.set_xlabel('z / (λ/NA²)', fontsize=11)
        ax.set_ylabel('Normalized Intensity', fontsize=11)
        ax.set_title(f'Circular Aperture (ε=0), NA={na}', fontsize=12, fontweight='bold')
        ax.set_xlim(-6, 6)
        ax.set_ylim(0, 1.05)
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)

    plt.suptitle('Axial Profiles: Comparing Illumination Types', fontsize=14)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "axial_profiles_comparison.png", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\nSaved: {OUTPUT_DIR}/axial_profiles_comparison.png")

    # =========================================================================
    # Figure 2: DOF vs epsilon for each illumination type
    # =========================================================================
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    for col, na in enumerate(nas):
        ax = axes[col]

        # Theory line
        eps_arr = np.array(epsilons)
        theory_dof = dof_theory / (1 - eps_arr**2 + 1e-10)
        ax.plot(epsilons, theory_dof, 'k--', lw=2, label='Theory: DOF₀/(1-ε²)')

        # Each config
        for input_field, alpha, label, color in configs:
            ax.plot(epsilons, results[label][na], 'o-', color=color, lw=2, markersize=7, label=label)

        ax.set_xlabel('ε (obstruction ratio)', fontsize=11)
        ax.set_ylabel('DOF (× λ/NA²)', fontsize=11)
        ax.set_title(f'DOF vs ε, NA={na}', fontsize=12, fontweight='bold')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 100)

    plt.suptitle('DOF vs Obstruction Ratio: Comparing Illumination Types', fontsize=14)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "dof_vs_epsilon_comparison.png", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {OUTPUT_DIR}/dof_vs_epsilon_comparison.png")

    # =========================================================================
    # Figure 3: ZOOMED DOF vs epsilon (ε ≤ 0.7, DOF ≤ 10)
    # =========================================================================
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    for col, na in enumerate(nas):
        ax = axes[col]

        # Theory line (finer sampling for smooth curve)
        eps_fine = np.linspace(0, 0.7, 100)
        theory_fine = dof_theory / (1 - eps_fine**2 + 1e-10)
        ax.plot(eps_fine, theory_fine, 'k--', lw=2, label='Theory: DOF₀/(1-ε²)')

        # Each config - filter to ε ≤ 0.7
        for input_field, alpha, label, color in configs:
            eps_plot = [e for e in epsilons if e <= 0.7]
            dof_plot = [results[label][na][i] for i, e in enumerate(epsilons) if e <= 0.7]
            ax.plot(eps_plot, dof_plot, 'o-', color=color, lw=2, markersize=8, label=label)

        ax.set_xlabel('ε (obstruction ratio)', fontsize=12)
        ax.set_ylabel('DOF (× λ/NA²)', fontsize=12)
        ax.set_title(f'DOF vs ε (zoomed), NA={na}', fontsize=12, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 0.75)
        ax.set_ylim(0, 10)

    plt.suptitle('DOF vs Obstruction Ratio (Zoomed: ε ≤ 0.7)', fontsize=14)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "dof_vs_epsilon_zoomed.png", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {OUTPUT_DIR}/dof_vs_epsilon_zoomed.png")

    # =========================================================================
    # Summary Table
    # =========================================================================
    print("\n" + "=" * 90)
    print("SUMMARY TABLE: DOF in units of λ/NA²")
    print("=" * 90)
    print(f"\n{'NA':<6} {'ε':<6} {'Uniform':<12} {'Gauss α=0.4':<14} {'Gauss α=4.0':<14} {'Theory':<10}")
    print("-" * 72)

    for na in nas:
        for i, eps in enumerate(epsilons):
            theory = dof_theory / (1 - eps**2 + 1e-10)
            u = results['Uniform'][na][i]
            g04 = results['Gaussian α=0.4'][na][i]
            g40 = results['Gaussian α=4.0'][na][i]
            print(f"{na:<6} {eps:<6.2f} {u:<12.3f} {g04:<14.3f} {g40:<14.3f} {theory:<10.3f}")
        print()

    # Analysis
    print("=" * 70)
    print("ANALYSIS")
    print("=" * 70)
    print("\nFor circular aperture (ε=0):")
    for na in nas:
        u = results['Uniform'][na][0]
        g04 = results['Gaussian α=0.4'][na][0]
        g40 = results['Gaussian α=4.0'][na][0]
        diff_04 = (g04 - u) / u * 100
        diff_40 = (g40 - u) / u * 100
        print(f"  NA={na}: Uniform={u:.3f}, α=0.4={g04:.3f} ({diff_04:+.1f}%), α=4.0={g40:.3f} ({diff_40:+.1f}%)")

    print("\nConclusion:")
    print("  - Gaussian α=0.4 is very close to uniform (within ~5%)")
    print("  - Gaussian α=4.0 gives significantly larger DOF (+40-100%)")
    print("  - Use α≤0.25 to approximate uniform illumination")


if __name__ == "__main__":
    main()
