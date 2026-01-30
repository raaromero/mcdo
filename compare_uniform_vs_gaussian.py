"""
Compare uniform illumination vs Gaussian with small alpha values.
Verify when Gaussian approaches uniform behavior.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from monte_carlo.richards_wolf import RichardsWolfSimulator

OUTPUT_DIR = Path("data/alpha_sweep")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def compute_profile(na, input_field, alpha=None, n_points=200, r_max_airy=5):
    """Compute radial focal plane profile."""
    if input_field == 'uniform':
        sim = RichardsWolfSimulator(
            wavelength=0.532,
            numerical_aperture=na,
            input_field='uniform'
        )
    else:
        sim = RichardsWolfSimulator(
            wavelength=0.532,
            numerical_aperture=na,
            input_field='gaussian',
            truncation_coeff=alpha
        )

    r_airy = np.linspace(0, r_max_airy, n_points)
    r_um = r_airy * sim.airy_radius
    z = np.zeros_like(r_um)

    Ex, Ey, Ez = sim.compute_field(r_um, z)
    intensity = np.abs(Ex)**2

    # Normalize
    intensity = intensity / np.max(intensity)

    return r_airy, intensity


def compute_rms_diff(profile1, profile2):
    """Compute RMS difference between two profiles."""
    return np.sqrt(np.mean((profile1 - profile2)**2))


def main():
    alphas_to_test = [0.001, 0.01, 0.1, 0.25, 0.5]
    nas = [0.1, 0.9]

    # Store results for convergence plot
    all_results = {}

    # Figure 1: Profile comparisons (2x2)
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    colors = ['C0', 'C1', 'C2', 'C3', 'C4']

    for row, na in enumerate(nas):
        print(f"\nNA = {na}")
        print("-" * 40)

        # Compute uniform baseline
        r_airy, uniform_profile = compute_profile(na, 'uniform')
        print(f"  Uniform: computed")

        all_results[na] = {'alphas': [], 'rms': []}

        # Left plot: profiles
        ax = axes[row, 0]
        ax.plot(r_airy, uniform_profile, 'k-', lw=2.5, label='Uniform (input_field="uniform")')

        for i, alpha in enumerate(alphas_to_test):
            _, gaussian_profile = compute_profile(na, 'gaussian', alpha)
            rms = compute_rms_diff(uniform_profile, gaussian_profile)
            pct = rms * 100
            print(f"  α={alpha}: RMS diff = {rms:.6f} ({pct:.4f}%)")

            all_results[na]['alphas'].append(alpha)
            all_results[na]['rms'].append(rms)

            ax.plot(r_airy, gaussian_profile, colors[i] + '--', lw=1.5,
                    label=f'α={alpha} (diff={pct:.3f}%)')

        ax.set_xlabel('r / r_Airy', fontsize=11)
        ax.set_ylabel('Normalized Intensity (Ex)', fontsize=11)
        ax.set_title(f'NA = {na}', fontsize=12, fontweight='bold')
        ax.set_xlim(0, 4)
        ax.set_ylim(0, 1.05)
        ax.legend(fontsize=8, loc='upper right')
        ax.grid(True, alpha=0.3)
        ax.axhline(0.5, color='gray', ls=':', alpha=0.5)

        # Right plot: difference from uniform
        ax = axes[row, 1]
        for i, alpha in enumerate(alphas_to_test):
            _, gaussian_profile = compute_profile(na, 'gaussian', alpha)
            diff = np.abs(gaussian_profile - uniform_profile)
            ax.semilogy(r_airy, diff + 1e-10, colors[i] + '-', lw=1.5, label=f'α={alpha}')

        ax.set_xlabel('r / r_Airy', fontsize=11)
        ax.set_ylabel('|Gaussian - Uniform|', fontsize=11)
        ax.set_title(f'Difference from Uniform (NA={na})', fontsize=12)
        ax.set_xlim(0, 4)
        ax.set_ylim(1e-6, 1)
        ax.axhline(0.01, color='r', ls='--', alpha=0.7, label='1% threshold')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3, which='both')

    plt.suptitle('Uniform vs Gaussian Illumination Comparison', fontsize=14, y=1.01)
    plt.tight_layout()

    save_path = OUTPUT_DIR / "uniform_vs_gaussian_comparison.png"
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\nSaved: {save_path}")

    # Figure 2: RMS Convergence plot
    fig, ax = plt.subplots(figsize=(8, 6))

    for na in nas:
        alphas = all_results[na]['alphas']
        rms_vals = all_results[na]['rms']
        ax.loglog(alphas, rms_vals, 'o-', markersize=8, lw=2, label=f'NA = {na}')

    ax.axhline(0.01, color='r', ls='--', alpha=0.7, lw=1.5, label='1% threshold')
    ax.axhline(0.001, color='orange', ls=':', alpha=0.7, lw=1.5, label='0.1% threshold')

    ax.set_xlabel('α (truncation coefficient)', fontsize=12)
    ax.set_ylabel('RMS difference from Uniform', fontsize=12)
    ax.set_title('Convergence to Uniform Illumination', fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, which='both')
    ax.set_xlim(0.0005, 1)
    ax.set_ylim(1e-5, 0.1)

    plt.tight_layout()
    save_path = OUTPUT_DIR / "rms_convergence_vs_alpha.png"
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


if __name__ == "__main__":
    main()
