"""Run Section 1 only: Gaussian Aperture Profiles"""

import sys
sys.path.insert(0, '.')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme(style='whitegrid', font_scale=1.5)
import os

# Parameters
wavelength = 0.532  # μm

# Base output directory
base_dir = 'data/presentation_slides'
os.makedirs(base_dir, exist_ok=True)

print("="*70)
print("SECTION 1: Gaussian Aperture Profiles")
print("="*70)

sec1_dir = f'{base_dir}/sec1_gaussian_aperture'
os.makedirs(sec1_dir, exist_ok=True)

# Symmetric rho for cross-section view
rho = np.linspace(-1.3, 1.3, 600)

# Individual α profiles (symmetric)
for alpha in [1.0, 2.0, 4.0]:
    fig, ax = plt.subplots(figsize=(10, 6))
    A = np.exp(-alpha * rho**2)
    ax.plot(rho, A, 'b-', lw=3)
    ax.axvline(1.0, color='red', ls='--', lw=2, label='Aperture edge')
    ax.axvline(-1.0, color='red', ls='--', lw=2)
    ax.fill_between(rho, 0, A, where=np.abs(rho) <= 1, alpha=0.2, color='blue')
    edge_val = np.exp(-alpha)
    ax.annotate(f'Edge = {edge_val:.3f}', xy=(1.0, edge_val), xytext=(1.1, edge_val+0.15),
                arrowprops=dict(arrowstyle='->', color='gray'))
    ax.set_xlabel('ρ = r / r_aperture')
    ax.set_ylabel('Amplitude A(ρ)')
    ax.set_title(f'Gaussian Profile: α = {alpha}', fontweight='bold')
    ax.legend(loc='upper right')
    ax.set_xlim([-1.3, 1.3])
    ax.set_ylim([0, 1.1])
    plt.tight_layout()
    alpha_str = str(alpha).replace('.', 'p')
    plt.savefig(f'{sec1_dir}/gaussian_alpha{alpha_str}.png', dpi=200)
    plt.close()
    print(f"  ✓ gaussian_alpha{alpha_str}.png")

# All alphas overlaid (symmetric)
fig, ax = plt.subplots(figsize=(10, 6))
for alpha, color in zip([1.0, 2.0, 4.0], ['#e41a1c', '#377eb8', '#4daf4a']):
    A = np.exp(-alpha * rho**2)
    ax.plot(rho, A, color=color, lw=2.5, label=f'α = {alpha}')
ax.axvline(1.0, color='black', ls='--', lw=2, label='Aperture edge')
ax.axvline(-1.0, color='black', ls='--', lw=2)
ax.set_xlabel('ρ = r / r_aperture')
ax.set_ylabel('Amplitude A(ρ)')
ax.set_title('Gaussian Truncation: Effect of α', fontweight='bold')
ax.legend(loc='upper right')
ax.set_xlim([-1.3, 1.3])
ax.set_ylim([0, 1.1])
plt.tight_layout()
plt.savefig(f'{sec1_dir}/gaussian_all_alphas.png', dpi=200)
plt.close()
print(f"  ✓ gaussian_all_alphas.png")

# Annular regions visualization (symmetric)
for eps in [0.5, 0.99]:
    fig, ax = plt.subplots(figsize=(10, 6))
    alpha = 2.0
    A = np.exp(-alpha * rho**2)
    ax.plot(rho, A, 'b-', lw=3, label=f'Gaussian (α={alpha})')
    ax.fill_between(rho, 0, A, where=np.abs(rho) <= eps, alpha=0.4, color='red', label=f'Blocked (|ρ|<{eps})')
    ax.fill_between(rho, 0, A, where=(np.abs(rho) > eps) & (np.abs(rho) <= 1), alpha=0.4, color='green', label='Transmitted')
    ax.axvline(eps, color='red', ls='--', lw=2)
    ax.axvline(-eps, color='red', ls='--', lw=2)
    ax.axvline(1.0, color='black', ls='--', lw=2, label='Outer edge')
    ax.axvline(-1.0, color='black', ls='--', lw=2)
    ax.set_xlabel('ρ = r / r_outer')
    ax.set_ylabel('Amplitude A(ρ)')
    ax.set_title(f'Gaussian on Annular Aperture (ε = {eps})', fontweight='bold')
    ax.legend(loc='upper right')
    ax.set_xlim([-1.3, 1.3])
    ax.set_ylim([0, 1.1])
    plt.tight_layout()
    eps_str = str(eps).replace('.', 'p')
    plt.savefig(f'{sec1_dir}/gaussian_annular_eps{eps_str}.png', dpi=200)
    plt.close()
    print(f"  ✓ gaussian_annular_eps{eps_str}.png")

# 2D aperture visualizations
x = np.linspace(-1.3, 1.3, 300)
y = np.linspace(-1.3, 1.3, 300)
X, Y = np.meshgrid(x, y)
R = np.sqrt(X**2 + Y**2)

for alpha in [1.0, 2.0, 4.0]:
    G = np.exp(-alpha * R**2)
    G_masked = np.where(R <= 1, G, 0)

    fig, ax = plt.subplots(figsize=(8, 8))
    im = ax.imshow(G_masked, extent=[-1.3, 1.3, -1.3, 1.3], cmap='hot', vmin=0, vmax=1, origin='lower')
    circle = plt.Circle((0, 0), 1.0, fill=False, color='cyan', lw=2)
    ax.add_patch(circle)
    plt.colorbar(im, ax=ax, label='Amplitude', shrink=0.8)
    ax.set_xlabel('x / r_aperture')
    ax.set_ylabel('y / r_aperture')
    ax.set_title(f'2D Gaussian (α = {alpha}) on Circular Aperture', fontweight='bold')
    ax.set_aspect('equal')
    plt.tight_layout()
    alpha_str = str(alpha).replace('.', 'p')
    plt.savefig(f'{sec1_dir}/gaussian_2d_circular_alpha{alpha_str}.png', dpi=200)
    plt.close()
    print(f"  ✓ gaussian_2d_circular_alpha{alpha_str}.png")

for eps in [0.5, 0.99]:
    alpha = 2.0
    G = np.exp(-alpha * R**2)
    mask = (R >= eps) & (R <= 1)
    G_masked = np.where(mask, G, 0)

    fig, ax = plt.subplots(figsize=(8, 8))
    im = ax.imshow(G_masked, extent=[-1.3, 1.3, -1.3, 1.3], cmap='hot', vmin=0, vmax=1, origin='lower')
    circle_out = plt.Circle((0, 0), 1.0, fill=False, color='cyan', lw=2)
    circle_in = plt.Circle((0, 0), eps, fill=False, color='cyan', lw=2, ls='--')
    ax.add_patch(circle_out)
    ax.add_patch(circle_in)
    plt.colorbar(im, ax=ax, label='Amplitude', shrink=0.8)
    ax.set_xlabel('x / r_outer')
    ax.set_ylabel('y / r_outer')
    ax.set_title(f'2D Gaussian (α=2) on Annular (ε={eps})', fontweight='bold')
    ax.set_aspect('equal')
    plt.tight_layout()
    eps_str = str(eps).replace('.', 'p')
    plt.savefig(f'{sec1_dir}/gaussian_2d_annular_eps{eps_str}.png', dpi=200)
    plt.close()
    print(f"  ✓ gaussian_2d_annular_eps{eps_str}.png")

print("\n" + "="*70)
print("SECTION 1 COMPLETE")
print("="*70)
print(f"\nOutput directory: {sec1_dir}")
print(f"Files: {len([f for f in os.listdir(sec1_dir) if f.endswith('.png')])} PNG files")
