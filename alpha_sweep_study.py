"""
Alpha sweep study: How Gaussian truncation parameter affects focal intensity.

Shows convergence toward uniform illumination as alpha -> 0.

Related to GitHub issue #6.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import pickle
from monte_carlo.richards_wolf import RichardsWolfSimulator

# Output directory
OUTPUT_DIR = Path("data/alpha_sweep")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def compute_focal_profile(na, alpha, n_points=200, r_max_airy=5):
    """Compute radial focal plane profile for given alpha."""
    sim = RichardsWolfSimulator(
        wavelength=0.532,
        numerical_aperture=na,
        input_field='gaussian',
        truncation_coeff=alpha
    )

    # Radial coordinates in Airy units
    r_airy = np.linspace(0, r_max_airy, n_points)
    r_um = r_airy * sim.airy_radius
    z = np.zeros_like(r_um)

    # Compute field
    Ex, Ey, Ez = sim.compute_field(r_um, z)
    intensity_total = np.abs(Ex)**2 + np.abs(Ey)**2 + np.abs(Ez)**2
    intensity_ex = np.abs(Ex)**2

    # Normalize
    intensity_total = intensity_total / np.max(intensity_total)
    intensity_ex = intensity_ex / np.max(intensity_ex)

    return {
        'r_airy': r_airy,
        'r_um': r_um,
        'intensity_total': intensity_total,
        'intensity_ex': intensity_ex,
        'airy_radius': sim.airy_radius
    }


def compute_uniform_baseline(na, n_points=200, r_max_airy=5):
    """Compute uniform illumination baseline."""
    sim = RichardsWolfSimulator(
        wavelength=0.532,
        numerical_aperture=na,
        input_field='uniform'
    )

    r_airy = np.linspace(0, r_max_airy, n_points)
    r_um = r_airy * sim.airy_radius
    z = np.zeros_like(r_um)

    Ex, Ey, Ez = sim.compute_field(r_um, z)
    intensity_total = np.abs(Ex)**2 + np.abs(Ey)**2 + np.abs(Ez)**2
    intensity_ex = np.abs(Ex)**2

    intensity_total = intensity_total / np.max(intensity_total)
    intensity_ex = intensity_ex / np.max(intensity_ex)

    return {
        'r_airy': r_airy,
        'r_um': r_um,
        'intensity_total': intensity_total,
        'intensity_ex': intensity_ex,
        'airy_radius': sim.airy_radius
    }


def compute_metrics(r_airy, intensity):
    """Compute FWHM and first sidelobe level."""
    # FWHM
    half_max = 0.5
    above_half = intensity >= half_max
    if np.any(above_half):
        # Find where it crosses 0.5
        for i in range(len(intensity)-1):
            if intensity[i] >= half_max and intensity[i+1] < half_max:
                # Linear interpolation
                fwhm_radius = r_airy[i] + (half_max - intensity[i]) / (intensity[i+1] - intensity[i]) * (r_airy[i+1] - r_airy[i])
                fwhm = 2 * fwhm_radius
                break
        else:
            fwhm = np.nan
    else:
        fwhm = np.nan

    # First sidelobe: find first minimum, then first maximum after that
    # Find first minimum (after main lobe)
    first_min_idx = None
    for i in range(1, len(intensity)-1):
        if intensity[i] < intensity[i-1] and intensity[i] < intensity[i+1]:
            if intensity[i] < 0.1:  # Ensure we're past main lobe
                first_min_idx = i
                break

    # Find first maximum after first minimum
    first_sidelobe = np.nan
    if first_min_idx is not None:
        for i in range(first_min_idx+1, len(intensity)-1):
            if intensity[i] > intensity[i-1] and intensity[i] > intensity[i+1]:
                first_sidelobe = intensity[i]
                break

    return {'fwhm': fwhm, 'first_sidelobe': first_sidelobe}


def run_alpha_sweep(na, alphas, n_points=200):
    """Run sweep over alpha values."""
    print(f"\nRunning alpha sweep for NA={na}")
    print(f"Alpha values: {alphas}")

    results = {
        'na': na,
        'alphas': alphas,
        'profiles': {},
        'metrics': {}
    }

    # Compute uniform baseline
    print("  Computing uniform baseline...")
    uniform = compute_uniform_baseline(na, n_points)
    results['uniform'] = uniform
    results['metrics']['uniform'] = compute_metrics(uniform['r_airy'], uniform['intensity_ex'])

    # Sweep alpha
    for alpha in alphas:
        print(f"  Computing alpha={alpha}...")
        profile = compute_focal_profile(na, alpha, n_points)
        results['profiles'][alpha] = profile
        results['metrics'][alpha] = compute_metrics(profile['r_airy'], profile['intensity_ex'])

    return results


def plot_profile_family(results, save_path):
    """Plot family of profiles for different alpha values."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Left: Linear scale
    ax = axes[0]
    uniform = results['uniform']
    ax.plot(uniform['r_airy'], uniform['intensity_ex'], 'k--', lw=2, label='Uniform', zorder=10)

    cmap = plt.cm.viridis
    alphas = sorted(results['profiles'].keys())
    for i, alpha in enumerate(alphas):
        color = cmap(i / len(alphas))
        profile = results['profiles'][alpha]
        ax.plot(profile['r_airy'], profile['intensity_ex'], color=color, label=f'α={alpha}')

    ax.set_xlabel('r / r_Airy')
    ax.set_ylabel('Normalized Intensity (Ex)')
    ax.set_title(f'Focal Plane Intensity vs Alpha (NA={results["na"]})')
    ax.legend(loc='upper right', fontsize=8)
    ax.set_xlim(0, 5)
    ax.grid(True, alpha=0.3)
    ax.axhline(0.5, color='gray', ls=':', alpha=0.5)

    # Right: Log scale to see sidelobes
    ax = axes[1]
    ax.semilogy(uniform['r_airy'], uniform['intensity_ex'], 'k--', lw=2, label='Uniform', zorder=10)

    for i, alpha in enumerate(alphas):
        color = cmap(i / len(alphas))
        profile = results['profiles'][alpha]
        ax.semilogy(profile['r_airy'], profile['intensity_ex'], color=color, label=f'α={alpha}')

    ax.set_xlabel('r / r_Airy')
    ax.set_ylabel('Normalized Intensity (Ex)')
    ax.set_title(f'Log Scale - Sidelobe Structure')
    ax.legend(loc='upper right', fontsize=8)
    ax.set_xlim(0, 5)
    ax.set_ylim(1e-4, 1.5)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def plot_metrics_vs_alpha(results, save_path):
    """Plot FWHM and sidelobe level vs alpha."""
    alphas = sorted(results['profiles'].keys())
    fwhm_values = [results['metrics'][a]['fwhm'] for a in alphas]
    sidelobe_values = [results['metrics'][a]['first_sidelobe'] for a in alphas]

    uniform_fwhm = results['metrics']['uniform']['fwhm']
    uniform_sidelobe = results['metrics']['uniform']['first_sidelobe']

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    # FWHM vs alpha
    ax = axes[0]
    ax.plot(alphas, fwhm_values, 'bo-', markersize=8, label='Gaussian')
    ax.axhline(uniform_fwhm, color='k', ls='--', label=f'Uniform ({uniform_fwhm:.3f})')
    ax.set_xlabel('Alpha (truncation coefficient)')
    ax.set_ylabel('FWHM (Airy units)')
    ax.set_title(f'FWHM vs Alpha (NA={results["na"]})')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xscale('log')

    # Sidelobe vs alpha
    ax = axes[1]
    ax.plot(alphas, sidelobe_values, 'ro-', markersize=8, label='Gaussian')
    ax.axhline(uniform_sidelobe, color='k', ls='--', label=f'Uniform ({uniform_sidelobe:.3f})')
    ax.set_xlabel('Alpha (truncation coefficient)')
    ax.set_ylabel('First Sidelobe Level')
    ax.set_title(f'Sidelobe Level vs Alpha (NA={results["na"]})')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xscale('log')

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def plot_convergence_to_uniform(results, save_path):
    """Plot RMS difference from uniform vs alpha."""
    alphas = sorted(results['profiles'].keys())
    uniform_intensity = results['uniform']['intensity_ex']

    rms_diff = []
    for alpha in alphas:
        gaussian_intensity = results['profiles'][alpha]['intensity_ex']
        diff = np.sqrt(np.mean((gaussian_intensity - uniform_intensity)**2))
        rms_diff.append(diff)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.loglog(alphas, rms_diff, 'go-', markersize=10, linewidth=2)
    ax.set_xlabel('Alpha (truncation coefficient)', fontsize=12)
    ax.set_ylabel('RMS difference from Uniform', fontsize=12)
    ax.set_title(f'Convergence to Uniform Illumination (NA={results["na"]})', fontsize=14)
    ax.grid(True, alpha=0.3, which='both')

    # Add annotation for convergence threshold
    ax.axhline(0.01, color='r', ls='--', alpha=0.7, label='1% threshold')
    ax.legend()

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def main():
    # Alpha values to sweep (log-spaced from small to large)
    alphas = [0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0]

    # Run for both low and high NA
    for na in [0.1, 0.9]:
        print(f"\n{'='*60}")
        print(f"NA = {na}")
        print('='*60)

        results = run_alpha_sweep(na, alphas, n_points=150)

        # Save intermediate data
        data_file = OUTPUT_DIR / f"alpha_sweep_NA{na}.pkl"
        with open(data_file, 'wb') as f:
            pickle.dump(results, f)
        print(f"Saved data: {data_file}")

        # Generate plots
        plot_profile_family(results, OUTPUT_DIR / f"profiles_NA{na}.png")
        plot_metrics_vs_alpha(results, OUTPUT_DIR / f"metrics_vs_alpha_NA{na}.png")
        plot_convergence_to_uniform(results, OUTPUT_DIR / f"convergence_NA{na}.png")

    print("\nDone! Results saved to:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
