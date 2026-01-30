"""
Test DOF with UNIFORM illumination only to verify theory.

Theory: DOF_circular = ~1.77 × λ/NA² (FWHM of sinc²)
Theory ratio: DOF_annular / DOF_circular ≈ 1/(1-ε²) [approximation]
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from monte_carlo.richards_wolf import RichardsWolfSimulator

OUTPUT_DIR = Path("data/annular_dof")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

wavelength = 0.532  # μm
n_medium = 1.0


def compute_annular_field(NA, epsilon, r_array, z_array, input_field='uniform'):
    """Compute annular aperture field using Babinet's principle."""
    rw_outer = RichardsWolfSimulator(
        wavelength=wavelength,
        numerical_aperture=NA,
        n_medium=n_medium,
        polarization='x',
        input_field=input_field,
        truncation_coeff=1.0  # Not used for uniform
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
            truncation_coeff=1.0
        )
        Ex_in, Ey_in, Ez_in = rw_inner.compute_field(r_array, z_array)
        Ex = Ex_out - Ex_in
        Ey = Ey_out - Ey_in
        Ez = Ez_out - Ez_in
    else:
        Ex, Ey, Ez = Ex_out, Ey_out, Ez_out

    return Ex, Ey, Ez


def compute_axial_profile(NA, epsilon, n_points=200, z_max_dof=10):
    """Compute axial intensity profile I(r=0, z)."""
    dof_scale = wavelength / (NA**2)
    z_um = np.linspace(-z_max_dof * dof_scale, z_max_dof * dof_scale, n_points)
    r = np.zeros_like(z_um)

    Ex, Ey, Ez = compute_annular_field(NA, epsilon, r, z_um, 'uniform')

    # Total intensity
    I_total = np.abs(Ex)**2 + np.abs(Ey)**2 + np.abs(Ez)**2
    I_total = I_total / np.max(I_total)

    # Also just Ex component (dominant for x-polarized, low NA)
    I_ex = np.abs(Ex)**2
    I_ex = I_ex / np.max(I_ex)

    z_norm = z_um / dof_scale
    return z_norm, I_total, I_ex, z_um


def theoretical_sinc2(z_norm):
    """Theoretical: I(z) = sinc²(π z_norm / 2)"""
    arg = np.pi * z_norm / 2
    with np.errstate(divide='ignore', invalid='ignore'):
        sinc = np.where(np.abs(arg) < 1e-10, 1.0, np.sin(arg) / arg)
    return sinc**2


def measure_dof(z, intensity, threshold=0.5):
    """Measure DOF as width at given threshold."""
    above = intensity >= threshold
    if not np.any(above):
        return np.nan
    indices = np.where(above)[0]
    if len(indices) < 2:
        return np.nan

    # Simple: just use the indices
    return z[indices[-1]] - z[indices[0]]


def main():
    print("=" * 70)
    print("DOF Test: UNIFORM Illumination Only")
    print("=" * 70)

    # Theoretical FWHM for sinc²(π z / 2)
    z_fine = np.linspace(-10, 10, 2000)
    I_theory = theoretical_sinc2(z_fine)
    dof_theory_circular = measure_dof(z_fine, I_theory)
    print(f"\nTheoretical DOF (sinc² FWHM): {dof_theory_circular:.4f} × λ/NA²")

    nas = [0.1, 0.9]
    epsilons = [0.0, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99]

    results = {na: {'dof_total': [], 'dof_ex': []} for na in nas}

    # Figure 1: Axial profiles comparison
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    for row, na in enumerate(nas):
        print(f"\n{'='*50}")
        print(f"NA = {na}")
        print(f"{'='*50}")

        # Left plot: Simulation profiles
        ax = axes[row, 0]
        colors = plt.cm.viridis(np.linspace(0, 0.9, len(epsilons)))

        for i, eps in enumerate(epsilons):
            z_max = 10 if eps < 0.9 else (30 if eps < 0.95 else 100)
            z_norm, I_total, I_ex, _ = compute_axial_profile(na, eps, n_points=200, z_max_dof=z_max)

            dof_total = measure_dof(z_norm, I_total)
            dof_ex = measure_dof(z_norm, I_ex)
            results[na]['dof_total'].append(dof_total)
            results[na]['dof_ex'].append(dof_ex)

            print(f"  ε={eps:.2f}: DOF(total)={dof_total:.3f}, DOF(Ex)={dof_ex:.3f}")

            label = f'ε={eps}' if eps > 0 else 'Circular'
            ax.plot(z_norm, I_total, color=colors[i], lw=1.5, label=label)

        # Add theory for circular
        ax.plot(z_fine, I_theory, 'k--', lw=1, alpha=0.5, label='Theory (sinc²)')

        ax.set_xlabel('z / (λ/NA²)', fontsize=11)
        ax.set_ylabel('Normalized Intensity', fontsize=11)
        ax.set_title(f'Axial Profiles - Uniform, NA={na}', fontsize=12, fontweight='bold')
        ax.set_xlim(-6, 6)
        ax.set_ylim(0, 1.05)
        ax.axhline(0.5, color='gray', ls=':', alpha=0.5)
        ax.legend(fontsize=8, loc='upper right')
        ax.grid(True, alpha=0.3)

        # Right plot: DOF comparison
        ax = axes[row, 1]

        # Simulation
        ax.plot(epsilons, results[na]['dof_total'], 'bo-', lw=2, markersize=8,
                label='RW Simulation (I_total)')
        ax.plot(epsilons, results[na]['dof_ex'], 'gs--', lw=1.5, markersize=6,
                alpha=0.7, label='RW Simulation (I_Ex only)')

        # Theory: simple 1/(1-ε²) scaling
        eps_arr = np.array(epsilons)
        dof_simple_theory = dof_theory_circular / (1 - eps_arr**2 + 1e-10)
        ax.plot(epsilons, dof_simple_theory, 'r--', lw=2, label='Theory: DOF₀/(1-ε²)')

        ax.set_xlabel('ε (obstruction ratio)', fontsize=11)
        ax.set_ylabel('DOF (× λ/NA²)', fontsize=11)
        ax.set_title(f'DOF vs ε - NA={na}', fontsize=12, fontweight='bold')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 1)
        if na == 0.1:
            ax.set_ylim(0, 100)
        else:
            ax.set_ylim(0, 50)

    plt.tight_layout()
    save_path = OUTPUT_DIR / "uniform_dof_test.png"
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\nSaved: {save_path}")

    # Print summary table
    print("\n" + "=" * 70)
    print("SUMMARY TABLE")
    print("=" * 70)
    print(f"{'ε':<8} {'NA=0.1':<12} {'NA=0.9':<12} {'Theory':<12} {'Ratio (0.1)':<12} {'Ratio (0.9)':<12}")
    print("-" * 68)

    dof_circular_01 = results[0.1]['dof_total'][0]
    dof_circular_09 = results[0.9]['dof_total'][0]

    for i, eps in enumerate(epsilons):
        theory = dof_theory_circular / (1 - eps**2 + 1e-10)
        ratio_01 = results[0.1]['dof_total'][i] / dof_circular_01
        ratio_09 = results[0.9]['dof_total'][i] / dof_circular_09
        theory_ratio = 1 / (1 - eps**2 + 1e-10)

        print(f"{eps:<8.2f} {results[0.1]['dof_total'][i]:<12.3f} {results[0.9]['dof_total'][i]:<12.3f} "
              f"{theory:<12.3f} {ratio_01:<12.2f} {ratio_09:<12.2f}")

    print("\nTheory ratio formula: 1/(1-ε²)")
    print(f"Baseline DOF (circular, theory): {dof_theory_circular:.4f}")
    print(f"Baseline DOF (circular, NA=0.1 sim): {dof_circular_01:.4f}")
    print(f"Baseline DOF (circular, NA=0.9 sim): {dof_circular_09:.4f}")


if __name__ == "__main__":
    main()
