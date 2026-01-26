"""
Step 1: Gaussian Beam Apodization Profiles
Individual standalone plots for presentation
"""

import sys
sys.path.insert(0, '.')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

output_dir = 'data/presentation_slides/step1_gaussian_profiles'
os.makedirs(output_dir, exist_ok=True)

print("="*60)
print("STEP 1: Gaussian Beam Apodization Profiles")
print("="*60)

# Normalized radial coordinate
rho = np.linspace(0, 1.3, 300)

# =============================================================================
# Plot 1a: Single Gaussian profile (α=2) showing truncation concept
# =============================================================================
fig, ax = plt.subplots(figsize=(8, 6))
alpha = 2.0
A = np.exp(-alpha * rho**2)

ax.plot(rho, A, 'b-', lw=3, label=f'Gaussian (α = {alpha})')
ax.axvline(1.0, color='red', ls='--', lw=2, label='Aperture edge')
ax.axhline(np.exp(-alpha), color='gray', ls=':', lw=1.5,
           label=f'Value at edge = {np.exp(-alpha):.3f}')
ax.fill_between(rho, 0, A, where=rho <= 1, alpha=0.2, color='blue')

ax.set_xlabel('Normalized radius ρ = r / r_aperture', fontsize=14)
ax.set_ylabel('Amplitude A(ρ)', fontsize=14)
ax.set_title(f'Gaussian Beam Truncation (α = {alpha})', fontsize=14, fontweight='bold')
ax.legend(fontsize=11, loc='upper right')
ax.set_xlim([0, 1.3])
ax.set_ylim([0, 1.1])
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(f'{output_dir}/gaussian_single_alpha2.png', dpi=200)
plt.close()
print(f"  ✓ gaussian_single_alpha2.png")

# =============================================================================
# Plot 1b-d: Individual Gaussian profiles for each α
# =============================================================================
for alpha in [1.0, 2.0, 4.0]:
    fig, ax = plt.subplots(figsize=(8, 6))
    A = np.exp(-alpha * rho**2)

    ax.plot(rho, A, 'b-', lw=3)
    ax.axvline(1.0, color='red', ls='--', lw=2, label='Aperture edge')
    ax.axhline(np.exp(-alpha), color='gray', ls=':', lw=1.5)
    ax.fill_between(rho, 0, A, where=rho <= 1, alpha=0.2, color='blue')

    # Annotate edge value
    edge_val = np.exp(-alpha)
    ax.annotate(f'Edge value = {edge_val:.3f}',
                xy=(1.0, edge_val), xytext=(1.1, edge_val + 0.1),
                fontsize=11, arrowprops=dict(arrowstyle='->', color='gray'))

    ax.set_xlabel('ρ = r / r_aperture', fontsize=14)
    ax.set_ylabel('Amplitude A(ρ)', fontsize=14)
    ax.set_title(f'Gaussian Profile: α = {alpha}', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.set_xlim([0, 1.3])
    ax.set_ylim([0, 1.1])
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    alpha_str = str(alpha).replace('.', 'p')
    plt.savefig(f'{output_dir}/gaussian_alpha{alpha_str}.png', dpi=200)
    plt.close()
    print(f"  ✓ gaussian_alpha{alpha_str}.png")

# =============================================================================
# Plot 1e: All three α values overlaid for comparison
# =============================================================================
fig, ax = plt.subplots(figsize=(8, 6))
colors = ['#e41a1c', '#377eb8', '#4daf4a']
alphas = [1.0, 2.0, 4.0]

for alpha, color in zip(alphas, colors):
    A = np.exp(-alpha * rho**2)
    ax.plot(rho, A, color=color, lw=2.5, label=f'α = {alpha}')

ax.axvline(1.0, color='black', ls='--', lw=2, label='Aperture edge')
ax.axhline(1/np.e, color='gray', ls=':', lw=1, alpha=0.7, label='1/e level')

ax.set_xlabel('ρ = r / r_aperture', fontsize=14)
ax.set_ylabel('Amplitude A(ρ)', fontsize=14)
ax.set_title('Gaussian Truncation: Effect of α', fontsize=14, fontweight='bold')
ax.legend(fontsize=11, loc='upper right')
ax.set_xlim([0, 1.3])
ax.set_ylim([0, 1.1])
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(f'{output_dir}/gaussian_all_alphas.png', dpi=200)
plt.close()
print(f"  ✓ gaussian_all_alphas.png")

# =============================================================================
# Plot 1f: 2D Gaussian on circular aperture (single α=2)
# =============================================================================
x = np.linspace(-1.3, 1.3, 300)
y = np.linspace(-1.3, 1.3, 300)
X, Y = np.meshgrid(x, y)
R = np.sqrt(X**2 + Y**2)

alpha = 2.0
G = np.exp(-alpha * R**2)
G_masked = np.where(R <= 1, G, 0)

fig, ax = plt.subplots(figsize=(8, 8))
im = ax.imshow(G_masked, extent=[-1.3, 1.3, -1.3, 1.3], cmap='hot',
               vmin=0, vmax=1, origin='lower')
circle = plt.Circle((0, 0), 1.0, fill=False, color='cyan', lw=2)
ax.add_patch(circle)
plt.colorbar(im, ax=ax, label='Amplitude', shrink=0.8)

ax.set_xlabel('x / r_aperture', fontsize=12)
ax.set_ylabel('y / r_aperture', fontsize=12)
ax.set_title(f'2D Gaussian on Circular Aperture (α = {alpha})', fontsize=13, fontweight='bold')
ax.set_aspect('equal')
plt.tight_layout()
plt.savefig(f'{output_dir}/gaussian_2d_circular_alpha2.png', dpi=200)
plt.close()
print(f"  ✓ gaussian_2d_circular_alpha2.png")

# =============================================================================
# Plot 1g-h: 2D Gaussian on annular aperture (ε=0.5 and ε=0.99)
# =============================================================================
alpha = 2.0
G = np.exp(-alpha * R**2)

for eps in [0.5, 0.99]:
    mask = (R >= eps) & (R <= 1)
    G_masked = np.where(mask, G, 0)

    fig, ax = plt.subplots(figsize=(8, 8))
    im = ax.imshow(G_masked, extent=[-1.3, 1.3, -1.3, 1.3], cmap='hot',
                   vmin=0, vmax=1, origin='lower')

    # Draw aperture boundaries
    circle_outer = plt.Circle((0, 0), 1.0, fill=False, color='cyan', lw=2, label='Outer')
    circle_inner = plt.Circle((0, 0), eps, fill=False, color='cyan', lw=2, ls='--', label='Inner')
    ax.add_patch(circle_outer)
    ax.add_patch(circle_inner)
    plt.colorbar(im, ax=ax, label='Amplitude', shrink=0.8)

    ax.set_xlabel('x / r_outer', fontsize=12)
    ax.set_ylabel('y / r_outer', fontsize=12)
    ax.set_title(f'2D Gaussian on Annular Aperture\nα = {alpha}, ε = {eps}',
                fontsize=13, fontweight='bold')
    ax.set_aspect('equal')
    plt.tight_layout()

    eps_str = str(eps).replace('.', 'p')
    plt.savefig(f'{output_dir}/gaussian_2d_annular_eps{eps_str}.png', dpi=200)
    plt.close()
    print(f"  ✓ gaussian_2d_annular_eps{eps_str}.png")

# =============================================================================
# Plot 1i: 1D profile showing annular regions
# =============================================================================
fig, ax = plt.subplots(figsize=(10, 6))
alpha = 2.0
A = np.exp(-alpha * rho**2)
eps = 0.5

ax.plot(rho, A, 'b-', lw=3, label=f'Gaussian (α = {alpha})')
ax.fill_between(rho, 0, A, where=rho <= eps, alpha=0.4, color='red', label=f'Blocked (ρ < ε={eps})')
ax.fill_between(rho, 0, A, where=(rho > eps) & (rho <= 1), alpha=0.4, color='green', label='Transmitted')
ax.axvline(eps, color='red', ls='--', lw=2)
ax.axvline(1.0, color='black', ls='--', lw=2, label='Outer edge')

ax.set_xlabel('ρ = r / r_outer', fontsize=14)
ax.set_ylabel('Amplitude A(ρ)', fontsize=14)
ax.set_title(f'Gaussian on Annular Aperture (ε = {eps})\nSame beam profile, inner region blocked',
            fontsize=13, fontweight='bold')
ax.legend(fontsize=11, loc='upper right')
ax.set_xlim([0, 1.3])
ax.set_ylim([0, 1.1])
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(f'{output_dir}/gaussian_1d_annular_regions.png', dpi=200)
plt.close()
print(f"  ✓ gaussian_1d_annular_regions.png")

print(f"\n{'='*60}")
print(f"DONE: All plots saved to {output_dir}/")
print(f"{'='*60}")
