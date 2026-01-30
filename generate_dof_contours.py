"""
Generate 2D r-z contour plots for DOF study.
One plot per configuration for better readability.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from monte_carlo.richards_wolf import RichardsWolfSimulator

OUTPUT_DIR = Path("data/annular_dof/contours")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

wavelength = 0.532
n_medium = 1.0


def compute_annular_field_2d(NA, epsilon, r_array, z_array, input_field='gaussian', alpha=4.0):
    """Compute field on 2D r-z grid."""
    rw_outer = RichardsWolfSimulator(
        wavelength=wavelength, numerical_aperture=NA, n_medium=n_medium,
        polarization='x', input_field=input_field, truncation_coeff=alpha
    )

    r_flat = r_array.flatten()
    z_flat = z_array.flatten()

    Ex_out, Ey_out, Ez_out = rw_outer.compute_field(np.abs(r_flat), z_flat)

    if epsilon > 0.001:
        NA_inner = NA * epsilon
        rw_inner = RichardsWolfSimulator(
            wavelength=wavelength, numerical_aperture=NA_inner, n_medium=n_medium,
            polarization='x', input_field=input_field, truncation_coeff=alpha,
            gaussian_reference_na=NA if input_field == 'gaussian' else None
        )
        Ex_in, Ey_in, Ez_in = rw_inner.compute_field(np.abs(r_flat), z_flat)
        Ex = Ex_out - Ex_in
        Ey = Ey_out - Ey_in
        Ez = Ez_out - Ez_in
    else:
        Ex, Ey, Ez = Ex_out, Ey_out, Ez_out

    I_ex = np.abs(Ex.reshape(r_array.shape))**2
    return I_ex


def measure_dof(z_1d, I_axial, threshold=0.5):
    """Measure DOF from axial profile."""
    above = I_axial >= threshold
    if not np.any(above):
        return np.nan
    indices = np.where(above)[0]
    if len(indices) < 2:
        return np.nan
    return z_1d[indices[-1]] - z_1d[indices[0]]


def generate_single_contour(NA, epsilon, input_field, alpha):
    """Generate single contour plot."""
    airy_r = 0.61 * wavelength / NA
    dof_scale = wavelength / (NA**2)

    # Grid in physical units
    r_max = 2.5 * airy_r
    z_max = 5.0 * dof_scale

    n_r = 100
    n_z = 120

    r_1d = np.linspace(-r_max, r_max, n_r)
    z_1d = np.linspace(-z_max, z_max, n_z)
    R, Z = np.meshgrid(r_1d, z_1d)

    print(f"  Computing NA={NA}, ε={epsilon}, {input_field}...")
    I_ex = compute_annular_field_2d(NA, epsilon, R, Z, input_field, alpha)
    I_ex_norm = I_ex / np.max(I_ex)

    # Compute DOF from on-axis profile
    center_idx = n_r // 2
    I_axial = I_ex_norm[:, center_idx]
    dof_um = measure_dof(z_1d, I_axial, 0.5)
    dof_normalized = dof_um / dof_scale if not np.isnan(dof_um) else np.nan

    # Large single figure
    fig, ax = plt.subplots(figsize=(10, 8))

    # Contour levels - all black except 0.5
    levels_black = [0.01, 0.05, 0.10, 0.20, 0.30, 0.40, 0.60, 0.70, 0.80, 0.90]
    levels_highlight = [0.50]

    cs_black = ax.contour(R, Z, I_ex_norm, levels=levels_black, colors='k', linewidths=1.0)
    ax.clabel(cs_black, inline=True, fontsize=10, fmt='%.2f')

    # Highlight 0.5 contour in orange
    cs_orange = ax.contour(R, Z, I_ex_norm, levels=levels_highlight, colors='tab:orange', linewidths=2.5)
    ax.clabel(cs_orange, inline=True, fontsize=12, fmt='%.2f', colors='tab:orange')

    # Airy radius markers
    ax.axvline(-airy_r, color='red', ls='--', lw=2, alpha=0.8)
    ax.axvline(airy_r, color='red', ls='--', lw=2, alpha=0.8)

    ax.set_xlabel('r (μm)', fontsize=14)
    ax.set_ylabel('z (μm)', fontsize=14)
    ax.tick_params(labelsize=12)

    # Title with DOF
    if input_field == 'uniform':
        field_str = 'Uniform'
    else:
        field_str = f'Gaussian α={alpha}'

    eps_str = 'Circular' if epsilon == 0 else f'ε={epsilon}'
    dof_str = f'DOF = {dof_um:.3f} μm ({dof_normalized:.2f} × λ/NA²)' if not np.isnan(dof_um) else 'DOF: N/A'
    ax.set_title(f'{field_str}, NA={NA}, {eps_str} - Ex\nAiry r = {airy_r:.3f} μm, {dof_str}', fontsize=14)

    ax.set_xlim(-r_max, r_max)
    ax.set_ylim(-z_max, z_max)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    # Filename
    field_tag = 'uniform' if input_field == 'uniform' else f'gaussian_a{alpha}'
    eps_tag = 'circular' if epsilon == 0 else f'eps{epsilon}'
    filename = f'contour_NA{NA}_{field_tag}_{eps_tag}.png'

    save_path = OUTPUT_DIR / filename
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {save_path}")


def main():
    configs = [
        # (NA, epsilon, input_field, alpha)
        # High NA, Gaussian
        (0.9, 0.0, 'gaussian', 4.0),
        (0.9, 0.5, 'gaussian', 4.0),
        (0.9, 0.99, 'gaussian', 4.0),
        # High NA, Uniform
        (0.9, 0.0, 'uniform', 1.0),
        (0.9, 0.5, 'uniform', 1.0),
        (0.9, 0.99, 'uniform', 1.0),
        # Low NA, Gaussian
        (0.1, 0.0, 'gaussian', 4.0),
        (0.1, 0.5, 'gaussian', 4.0),
        (0.1, 0.99, 'gaussian', 4.0),
        # Low NA, Uniform
        (0.1, 0.0, 'uniform', 1.0),
        (0.1, 0.5, 'uniform', 1.0),
        (0.1, 0.99, 'uniform', 1.0),
    ]

    print(f"Generating {len(configs)} contour plots...")
    for NA, eps, input_field, alpha in configs:
        generate_single_contour(NA, eps, input_field, alpha)

    print("\nDone!")


if __name__ == "__main__":
    main()
