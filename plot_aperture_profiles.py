"""
Plot Gaussian beam amplitude profiles across the aperture for different alpha values.
Shows how the illumination looks before focusing.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import pickle

OUTPUT_DIR = Path("data/alpha_sweep")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def gaussian_amplitude(rho, alpha):
    """
    Gaussian amplitude at normalized radius rho = r/r_aperture.

    A(rho) = exp(-alpha * rho^2)

    At aperture edge (rho=1): A = exp(-alpha)
    """
    return np.exp(-alpha * rho**2)


def plot_aperture_profiles():
    """Plot 1D cross-sections of aperture illumination."""
    alphas = [0.1, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0]

    rho = np.linspace(-1, 1, 500)  # Normalized radius across aperture

    fig, ax = plt.subplots(figsize=(10, 6))

    # Uniform illumination
    ax.plot(rho, np.ones_like(rho), 'k--', lw=2, label='Uniform (α=0)')

    # Gaussian profiles for each alpha
    cmap = plt.cm.viridis
    for i, alpha in enumerate(alphas):
        color = cmap(i / len(alphas))
        amplitude = gaussian_amplitude(np.abs(rho), alpha)
        ax.plot(rho, amplitude, color=color, lw=2, label=f'α={alpha}')

    # Aperture edges
    ax.axvline(-1, color='red', ls='--', alpha=0.5, lw=1)
    ax.axvline(1, color='red', ls='--', alpha=0.5, lw=1)
    ax.fill_betweenx([0, 1.1], -1.3, -1, color='gray', alpha=0.3)
    ax.fill_betweenx([0, 1.1], 1, 1.3, color='gray', alpha=0.3)

    ax.set_xlabel('ρ = r / r_aperture', fontsize=12)
    ax.set_ylabel('Amplitude A(ρ)', fontsize=12)
    ax.set_title('Gaussian Beam Profiles Across Aperture', fontsize=14)
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(0, 1.1)
    ax.legend(loc='lower center', ncol=4, fontsize=9)
    ax.grid(True, alpha=0.3)

    # Add annotations
    ax.annotate('Aperture\nedge', xy=(1, 0.5), xytext=(1.15, 0.5),
                fontsize=9, ha='center')
    ax.annotate('blocked', xy=(-1.15, 0.2), fontsize=8, ha='center', color='gray')
    ax.annotate('blocked', xy=(1.15, 0.2), fontsize=8, ha='center', color='gray')

    plt.tight_layout()
    save_path = OUTPUT_DIR / "aperture_profiles_1d.png"
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def plot_aperture_and_focal_2d():
    """Plot 2D aperture illumination and 1D focal profiles for select alpha values."""
    alphas_to_show = [0.1, 1.0, 4.0]

    fig, axes = plt.subplots(2, len(alphas_to_show) + 1, figsize=(14, 6),
                             gridspec_kw={'height_ratios': [1, 0.8]})

    x = np.linspace(-1.2, 1.2, 300)
    X, Y = np.meshgrid(x, x)
    R = np.sqrt(X**2 + Y**2)

    # Aperture mask
    aperture = R <= 1

    # Row 1: Aperture illumination
    # Uniform
    ax = axes[0, 0]
    img = np.ones_like(R)
    img[~aperture] = 0
    im1 = ax.imshow(img, extent=[-1.2, 1.2, -1.2, 1.2], cmap='inferno', vmin=0, vmax=1)
    circle = plt.Circle((0, 0), 1, fill=False, color='white', lw=1.5, ls='--')
    ax.add_patch(circle)
    ax.set_title('Uniform (α=0)', fontsize=11)
    ax.set_ylabel('Aperture\ny / r_aperture', fontsize=10)
    ax.set_aspect('equal')
    ax.set_xticks([])

    # Gaussian for each alpha
    for i, alpha in enumerate(alphas_to_show):
        ax = axes[0, i + 1]
        img = gaussian_amplitude(R, alpha)
        img[~aperture] = 0
        im1 = ax.imshow(img, extent=[-1.2, 1.2, -1.2, 1.2], cmap='inferno', vmin=0, vmax=1)
        circle = plt.Circle((0, 0), 1, fill=False, color='white', lw=1.5, ls='--')
        ax.add_patch(circle)
        edge_val = np.exp(-alpha)
        ax.set_title(f'α={alpha} (edge={edge_val:.2f})', fontsize=11)
        ax.set_aspect('equal')
        ax.set_xticks([])
        ax.set_yticks([])

    # Colorbar for row 1 - place it better
    cbar_ax = fig.add_axes([0.92, 0.55, 0.015, 0.35])
    cbar1 = fig.colorbar(im1, cax=cbar_ax)
    cbar1.set_label('Amplitude', fontsize=10)

    # Row 2: Focal plane profiles as 1D slices
    # Load precomputed data
    try:
        with open(OUTPUT_DIR / "alpha_sweep_NA0.1.pkl", 'rb') as f:
            data = pickle.load(f)
    except FileNotFoundError:
        print("Run alpha_sweep_study.py first to generate focal data")
        return

    r_data = data['uniform']['r_airy']
    uniform_1d = data['uniform']['intensity_ex']

    # Plot uniform slice
    ax = axes[1, 0]
    ax.plot(r_data, uniform_1d, 'k-', lw=2)
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel('Focal Intensity', fontsize=10)
    ax.set_xlabel('r / r_Airy', fontsize=10)
    ax.axhline(0.5, color='gray', ls=':', alpha=0.5)
    ax.grid(True, alpha=0.3)

    # Focal profiles for each alpha
    for i, alpha in enumerate(alphas_to_show):
        ax = axes[1, i + 1]
        if alpha in data['profiles']:
            profile_1d = data['profiles'][alpha]['intensity_ex']
            ax.plot(r_data, profile_1d, 'b-', lw=2, label=f'α={alpha}')
            ax.plot(r_data, uniform_1d, 'k--', lw=1, alpha=0.5, label='Uniform')
        ax.set_xlim(0, 4)
        ax.set_ylim(0, 1.05)
        ax.set_xlabel('r / r_Airy', fontsize=10)
        ax.axhline(0.5, color='gray', ls=':', alpha=0.5)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8, loc='upper right')
        ax.set_yticks([])

    plt.suptitle('Aperture Illumination → Focal Plane Intensity (NA=0.1)', fontsize=13)
    plt.subplots_adjust(hspace=0.25, wspace=0.1, right=0.9)

    save_path = OUTPUT_DIR / "aperture_and_focal_2d.png"
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def plot_edge_amplitude_vs_alpha():
    """Plot edge amplitude (fill factor indicator) vs alpha."""
    # More alpha points
    alphas = np.array([0.01, 0.05, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 10.0, 15.0, 20.0])

    edge_amplitude = np.exp(-alphas)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Linear scale
    ax = axes[0]
    ax.plot(alphas, edge_amplitude, 'bo-', markersize=8, linewidth=2)
    ax.axhline(1.0, color='k', ls='--', alpha=0.5, label='Uniform (edge=1)')
    ax.axhline(0.5, color='gray', ls=':', alpha=0.5)
    ax.axhline(np.exp(-4), color='r', ls='--', alpha=0.5, label=f'"Untruncated" threshold (α=4, edge={np.exp(-4):.3f})')
    ax.set_xlabel('α (truncation coefficient)', fontsize=12)
    ax.set_ylabel('Edge Amplitude A(ρ=1) = exp(-α)', fontsize=12)
    ax.set_title('Aperture Edge Illumination vs α', fontsize=13)
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # Add annotations for key points
    ax.annotate('α=1\n(37%)', xy=(1, np.exp(-1)), xytext=(2.5, 0.5),
                arrowprops=dict(arrowstyle='->', color='gray'), fontsize=9)
    ax.annotate('α=4\n(2%)', xy=(4, np.exp(-4)), xytext=(6, 0.15),
                arrowprops=dict(arrowstyle='->', color='gray'), fontsize=9)

    # Log-linear scale
    ax = axes[1]
    ax.semilogy(alphas, edge_amplitude, 'bo-', markersize=8, linewidth=2)
    ax.axhline(1.0, color='k', ls='--', alpha=0.5, label='Uniform')
    ax.axhline(np.exp(-4), color='r', ls='--', alpha=0.5, label='"Untruncated" (α=4)')
    ax.axhline(0.01, color='orange', ls=':', alpha=0.5, label='1% threshold')
    ax.set_xlabel('α (truncation coefficient)', fontsize=12)
    ax.set_ylabel('Edge Amplitude A(ρ=1) = exp(-α)', fontsize=12)
    ax.set_title('Log Scale', fontsize=13)
    ax.set_xlim(0, 20)
    ax.set_ylim(1e-9, 2)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3, which='both')

    plt.tight_layout()
    save_path = OUTPUT_DIR / "edge_amplitude_vs_alpha.png"
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


if __name__ == "__main__":
    plot_aperture_profiles()
    plot_aperture_and_focal_2d()
    plot_edge_amplitude_vs_alpha()
    print("\nDone!")
