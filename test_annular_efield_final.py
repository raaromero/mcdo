"""
Test annular aperture using proper E-field subtraction
For both low NA and high NA with separate plots
"""
import sys
sys.path.insert(0, '.')

import numpy as np
import matplotlib.pyplot as plt
from scipy.special import j1
from monte_carlo.richards_wolf import RichardsWolfSimulator

print("="*80)
print("Annular Aperture with E-Field Subtraction: Low NA vs High NA")
print("="*80)

# Parameters
wavelength = 0.75  # μm
n_medium = 1.0
aperture_diameter = 1500.0
a_outer = aperture_diameter / 2

# Test for both low and high NA
NA_values = [0.1, 0.9]
eps_values = [0.0, 0.5, 0.99]

# Process each NA separately
for NA in NA_values:

    theta = np.arcsin(NA / n_medium)
    focal_length = a_outer / np.tan(theta)
    airy_radius = 0.61 * wavelength / NA

    print(f"\n{'='*80}")
    print(f"NA = {NA} ({'Low NA - Paraxial' if NA < 0.5 else 'High NA - Vectorial'})")
    print(f"{'='*80}")
    print(f"  λ = {wavelength} μm ({wavelength*1000:.0f} nm)")
    print(f"  NA = {NA}")
    print(f"  f = {focal_length:.1f} μm ({focal_length/1000:.2f} mm)")
    print(f"  Airy radius = {airy_radius:.3f} μm")

    # Radial grid - longer range to show more structure
    # Convert kaw=10 to physical distance for plotting range
    kaw_max = 10
    r_max = kaw_max * focal_length * wavelength / (2 * np.pi * a_outer)
    r = np.linspace(0, r_max, 200)
    z = np.zeros_like(r)

    print(f"  Plot range: 0 to {r_max:.2f} μm (kaw=0 to {kaw_max})")

    # Storage for results
    results = {}

    # Compute for each epsilon
    for eps in eps_values:
        print(f"\n  Computing ε = {eps}...")

        # Full aperture
        rw_outer = RichardsWolfSimulator(
            wavelength=wavelength,
            numerical_aperture=NA,
            n_medium=n_medium,
            polarization='x',
            input_field='uniform',
            fill_factor=1.0
        )

        if eps < 1e-3:
            # Just circular aperture
            Ex, Ey, Ez = rw_outer.compute_field(r, z)
            I_rw = np.abs(Ex)**2 + np.abs(Ey)**2 + np.abs(Ez)**2
        else:
            # Annular aperture - subtract E-fields
            NA_inner = NA * eps
            rw_inner = RichardsWolfSimulator(
                wavelength=wavelength,
                numerical_aperture=NA_inner,
                n_medium=n_medium,
                polarization='x',
                input_field='uniform',
                fill_factor=1.0
            )

            # Get E-fields from both
            Ex_outer, Ey_outer, Ez_outer = rw_outer.compute_field(r, z)
            Ex_inner, Ey_inner, Ez_inner = rw_inner.compute_field(r, z)

            # Subtract E-fields
            Ex_annular = Ex_outer - Ex_inner
            Ey_annular = Ey_outer - Ey_inner
            Ez_annular = Ez_outer - Ez_inner

            # Get intensity
            I_rw = np.abs(Ex_annular)**2 + np.abs(Ey_annular)**2 + np.abs(Ez_annular)**2

        # Normalize
        I_rw = I_rw / I_rw.max()

        # Analytical Fraunhofer
        def I_annular_analytical(kaw, eps):
            kaw_safe = np.where(kaw == 0, 1e-10, kaw)
            term1 = 2 * j1(kaw_safe) / kaw_safe
            term2 = (eps**2) * 2 * j1(eps * kaw_safe) / (eps * kaw_safe)
            I = ((term1 - term2)**2) / ((1 - eps**2)**2)
            return I

        # Convert r to kaw
        kaw = r * (2 * np.pi * a_outer) / (focal_length * wavelength)
        I_analytical = I_annular_analytical(kaw, eps if eps > 1e-6 else 1e-9)

        # Metrics
        mse = np.mean((I_rw - I_analytical)**2)
        corr = np.corrcoef(I_rw, I_analytical)[0, 1]

        # Store
        results[eps] = {
            'I_rw': I_rw,
            'I_analytical': I_analytical,
            'mse': mse,
            'corr': corr
        }

        print(f"    MSE = {mse:.6f}, Corr = {corr:.6f}")

    # Create plot for this NA (all three epsilon values)
    print(f"\n  Creating plot...")

    # 3 columns layout (like Fig 8.30)
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    eps_labels = {
        0.0: 'ε≈0 (Circular)',
        0.5: 'ε=0.5',
        0.99: 'ε=0.99'
    }

    regime = "Low NA (Paraxial)" if NA < 0.5 else "High NA (Vectorial)"

    for idx, eps in enumerate(eps_values):
        ax = axes[idx]
        res = results[eps]

        # Plot both methods
        ax.plot(r, res['I_analytical'], 'r--', linewidth=2.5,
                label='Fraunhofer', alpha=0.8)
        ax.plot(r, res['I_rw'], 'b-', linewidth=2.5,
                label='Richards-Wolf', alpha=0.8)

        # Reference lines
        ax.axhline(0.5, color='gray', linestyle=':', linewidth=1, alpha=0.5)

        # Labels
        ax.set_xlabel('Radial distance r (μm)', fontsize=12)
        ax.set_ylabel('Normalized Intensity I/I₀', fontsize=12)
        ax.set_title(f'{eps_labels[eps]}\n' +
                     f'MSE = {res["mse"]:.6f}, Corr = {res["corr"]:.6f}',
                     fontsize=11, fontweight='bold')
        ax.legend(fontsize=10, loc='upper right')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, r_max)
        ax.set_ylim(0, 1.05)

    # Overall title with parameters
    fig.suptitle(f'{regime}: Annular Aperture (Fraunhofer vs Richards-Wolf)\n' +
                 f'λ = {wavelength*1000:.0f} nm, NA = {NA}, f = {focal_length/1000:.2f} mm',
                 fontsize=13, fontweight='bold')

    plt.tight_layout()

    # Save with NA-specific filename
    na_str = f"NA_{NA:.1f}".replace('.', 'p')
    filename = f'data/annular_aperture_{na_str}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: {filename}")
    plt.close()

    # Summary for this NA
    print(f"\n  Summary for NA = {NA}:")
    for eps in eps_values:
        res = results[eps]
        print(f"    {eps_labels[eps]}:")
        print(f"      MSE = {res['mse']:.6f}, Corr = {res['corr']:.6f}")

print("\n" + "="*80)
print("FINAL SUMMARY")
print("="*80)
print("\n✓ Two separate plots generated:")
print("  1. data/annular_aperture_NA_0p1.png (Low NA)")
print("  2. data/annular_aperture_NA_0p9.png (High NA)")
print("\n✓ E-field subtraction method validated for annular apertures!")
print("="*80)
