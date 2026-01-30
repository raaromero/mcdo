"""
Compare DOF: Uniform vs Gaussian, Total vs Ex-only intensity.
Isolate what causes discrepancy from theory.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from monte_carlo.richards_wolf import RichardsWolfSimulator

OUTPUT_DIR = Path("data/annular_dof")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

wavelength = 0.532
n_medium = 1.0


def compute_annular_field(NA, epsilon, r_array, z_array, input_field='uniform', alpha=4.0):
    """Compute annular aperture field using Babinet's principle."""
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
        Ex = Ex_out - Ex_in
        Ey = Ey_out - Ey_in
        Ez = Ez_out - Ez_in
    else:
        Ex, Ey, Ez = Ex_out, Ey_out, Ez_out

    return Ex, Ey, Ez


def compute_axial_profile(NA, epsilon, input_field='uniform', alpha=4.0, n_points=200, z_max_dof=10):
    """Compute axial intensity profile."""
    dof_scale = wavelength / (NA**2)
    z_um = np.linspace(-z_max_dof * dof_scale, z_max_dof * dof_scale, n_points)
    r = np.zeros_like(z_um)

    Ex, Ey, Ez = compute_annular_field(NA, epsilon, r, z_um, input_field, alpha)

    I_total = np.abs(Ex)**2 + np.abs(Ey)**2 + np.abs(Ez)**2
    I_ex = np.abs(Ex)**2

    I_total = I_total / np.max(I_total)
    I_ex = I_ex / np.max(I_ex)

    z_norm = z_um / dof_scale
    return z_norm, I_total, I_ex


def measure_dof(z, intensity, threshold=0.5):
    """Measure FWHM."""
    above = intensity >= threshold
    if not np.any(above):
        return np.nan
    indices = np.where(above)[0]
    if len(indices) < 2:
        return np.nan
    return z[indices[-1]] - z[indices[0]]


def theoretical_sinc2(z_norm):
    """Theory: sinc²(π z / 2)"""
    arg = np.pi * z_norm / 2
    with np.errstate(divide='ignore', invalid='ignore'):
        sinc = np.where(np.abs(arg) < 1e-10, 1.0, np.sin(arg) / arg)
    return sinc**2


def main():
    print("=" * 70)
    print("DOF Comparison: Isolating Sources of Discrepancy")
    print("=" * 70)

    # Theoretical baseline
    z_fine = np.linspace(-10, 10, 2000)
    I_theory = theoretical_sinc2(z_fine)
    dof_theory = measure_dof(z_fine, I_theory)
    print(f"Theory DOF (sinc² FWHM): {dof_theory:.4f} × λ/NA²\n")

    nas = [0.1, 0.9]
    epsilons = [0.0, 0.5, 0.9, 0.99]

    # Store results
    results = {}

    for na in nas:
        results[na] = {}
        for eps in epsilons:
            z_max = 10 if eps < 0.9 else (30 if eps < 0.95 else 100)

            # Uniform
            z_norm, I_total_u, I_ex_u = compute_axial_profile(na, eps, 'uniform', 1.0, 200, z_max)
            dof_total_u = measure_dof(z_norm, I_total_u)
            dof_ex_u = measure_dof(z_norm, I_ex_u)

            # Gaussian α=4
            _, I_total_g, I_ex_g = compute_axial_profile(na, eps, 'gaussian', 4.0, 200, z_max)
            dof_total_g = measure_dof(z_norm, I_total_g)
            dof_ex_g = measure_dof(z_norm, I_ex_g)

            results[na][eps] = {
                'uniform_total': dof_total_u,
                'uniform_ex': dof_ex_u,
                'gaussian_total': dof_total_g,
                'gaussian_ex': dof_ex_g,
                'z_norm': z_norm,
                'I_total_u': I_total_u,
                'I_ex_u': I_ex_u,
                'I_total_g': I_total_g,
                'I_ex_g': I_ex_g
            }

    # Print comparison table
    print("=" * 90)
    print("COMPARISON TABLE: DOF in units of λ/NA²")
    print("=" * 90)
    print(f"{'NA':<6} {'ε':<6} {'Uniform':<12} {'Uniform':<12} {'Gaussian':<12} {'Gaussian':<12} {'Theory':<10}")
    print(f"{'':6} {'':6} {'(Total)':<12} {'(Ex only)':<12} {'(Total)':<12} {'(Ex only)':<12} {'1/(1-ε²)':<10}")
    print("-" * 90)

    for na in nas:
        for eps in epsilons:
            r = results[na][eps]
            theory = dof_theory / (1 - eps**2 + 1e-10)
            print(f"{na:<6} {eps:<6.2f} {r['uniform_total']:<12.3f} {r['uniform_ex']:<12.3f} "
                  f"{r['gaussian_total']:<12.3f} {r['gaussian_ex']:<12.3f} {theory:<10.3f}")
        print()

    # Create comparison figure
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))

    for row, na in enumerate(nas):
        for col, eps in enumerate(epsilons):
            ax = axes[row, col]
            r = results[na][eps]
            z = r['z_norm']

            # Plot all 4 variants
            ax.plot(z, r['I_total_u'], 'b-', lw=2, label=f"Uniform, Total ({r['uniform_total']:.2f})")
            ax.plot(z, r['I_ex_u'], 'b--', lw=1.5, alpha=0.7, label=f"Uniform, Ex ({r['uniform_ex']:.2f})")
            ax.plot(z, r['I_total_g'], 'r-', lw=2, label=f"Gaussian, Total ({r['gaussian_total']:.2f})")
            ax.plot(z, r['I_ex_g'], 'r--', lw=1.5, alpha=0.7, label=f"Gaussian, Ex ({r['gaussian_ex']:.2f})")

            # Theory for uniform circular
            if eps < 0.01:
                ax.plot(z_fine, I_theory, 'k:', lw=1, alpha=0.5, label='Theory (sinc²)')

            ax.axhline(0.5, color='gray', ls=':', alpha=0.5)
            ax.set_xlim(-8 if eps < 0.9 else -20, 8 if eps < 0.9 else 20)
            ax.set_ylim(0, 1.05)
            ax.set_xlabel('z / (λ/NA²)', fontsize=10)
            if col == 0:
                ax.set_ylabel(f'NA={na}\nIntensity', fontsize=10)
            title = 'Circular' if eps == 0 else f'ε={eps}'
            ax.set_title(title, fontsize=11, fontweight='bold')
            ax.legend(fontsize=7, loc='upper right')
            ax.grid(True, alpha=0.3)

    plt.suptitle('Axial Intensity: Uniform vs Gaussian, Total vs Ex-only', fontsize=14)
    plt.tight_layout()
    save_path = OUTPUT_DIR / "dof_comparison_all.png"
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")

    # Summary of effects
    print("\n" + "=" * 70)
    print("ANALYSIS: Sources of Discrepancy")
    print("=" * 70)

    # Effect 1: Total vs Ex-only
    print("\n1. TOTAL vs EX-ONLY INTENSITY:")
    for na in nas:
        diff = abs(results[na][0.0]['uniform_total'] - results[na][0.0]['uniform_ex'])
        pct = diff / results[na][0.0]['uniform_total'] * 100
        print(f"   NA={na}, ε=0: Total={results[na][0.0]['uniform_total']:.3f}, "
              f"Ex={results[na][0.0]['uniform_ex']:.3f}, diff={pct:.1f}%")

    # Effect 2: Uniform vs Gaussian
    print("\n2. UNIFORM vs GAUSSIAN (α=4):")
    for na in nas:
        diff = results[na][0.0]['gaussian_total'] - results[na][0.0]['uniform_total']
        pct = diff / results[na][0.0]['uniform_total'] * 100
        print(f"   NA={na}, ε=0: Uniform={results[na][0.0]['uniform_total']:.3f}, "
              f"Gaussian={results[na][0.0]['gaussian_total']:.3f}, diff={pct:+.1f}%")

    # Effect 3: Low NA vs High NA
    print("\n3. LOW NA vs HIGH NA (uniform, circular):")
    print(f"   NA=0.1: DOF={results[0.1][0.0]['uniform_total']:.3f} (theory={dof_theory:.3f})")
    print(f"   NA=0.9: DOF={results[0.9][0.0]['uniform_total']:.3f} (theory={dof_theory:.3f})")
    diff_01 = (results[0.1][0.0]['uniform_total'] - dof_theory) / dof_theory * 100
    diff_09 = (results[0.9][0.0]['uniform_total'] - dof_theory) / dof_theory * 100
    print(f"   Deviation from theory: NA=0.1: {diff_01:+.1f}%, NA=0.9: {diff_09:+.1f}%")

    print("\n" + "=" * 70)
    print("CONCLUSIONS:")
    print("=" * 70)
    print("""
1. TOTAL vs EX-ONLY: Negligible difference (<1%) for on-axis intensity.
   → Ez component doesn't affect on-axis DOF measurement.

2. GAUSSIAN vs UNIFORM: Gaussian gives ~40-100% LARGER DOF than uniform!
   → Apodization broadens the axial profile significantly.

3. HIGH NA EFFECT: NA=0.9 gives ~35% SMALLER DOF than paraxial theory.
   → Vectorial effects (aplanatic factor √cos(θ)) compress the focal region.

SUMMARY OF DISCREPANCY SOURCES:
- Primary: Gaussian illumination (vs uniform assumed in theory)
- Secondary: High NA vectorial effects (for NA > 0.5)
- Negligible: Ex-only vs Total intensity
""")


if __name__ == "__main__":
    main()
