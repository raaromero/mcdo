"""
Test annular aperture using proper E-field subtraction
"""
import sys
sys.path.insert(0, '.')

import numpy as np
import matplotlib.pyplot as plt
from scipy.special import j1
from monte_carlo.richards_wolf import RichardsWolfSimulator

print("="*80)
print("Testing Annular Aperture with E-Field Subtraction")
print("="*80)

# Parameters
wavelength = 0.75  # μm
NA = 0.1
n_medium = 1.0
aperture_diameter = 1500.0
a_outer = aperture_diameter / 2
theta = np.arcsin(NA / n_medium)
focal_length = a_outer / np.tan(theta)
airy_radius = 0.61 * wavelength / NA

print(f"\nParameters:")
print(f"  λ = {wavelength} μm")
print(f"  NA = {NA}")
print(f"  f = {focal_length:.1f} μm")
print(f"  Airy radius = {airy_radius:.3f} μm")

# Radial grid
r_max = 6.4
r = np.linspace(0, r_max, 100)
z = np.zeros_like(r)

# Test with ε = 0.5
eps = 0.5
print(f"\n{'='*80}")
print(f"Testing ε = {eps} (annular aperture)")
print(f"{'='*80}")

# Full aperture
print("\n1. Computing full aperture (outer)...")
rw_outer = RichardsWolfSimulator(
    wavelength=wavelength,
    numerical_aperture=NA,
    n_medium=n_medium,
    polarization='x',
    input_field='uniform',
    fill_factor=1.0
)

Ex_outer, Ey_outer, Ez_outer = rw_outer.compute_field(r, z)
print(f"   Ex_outer shape: {Ex_outer.shape}")
print(f"   Sample: {Ex_outer[0]}")

# Inner aperture (blocked region)
NA_inner = NA * eps
print(f"\n2. Computing blocked center (inner, NA={NA_inner})...")
rw_inner = RichardsWolfSimulator(
    wavelength=wavelength,
    numerical_aperture=NA_inner,
    n_medium=n_medium,
    polarization='x',
    input_field='uniform',
    fill_factor=1.0
)

Ex_inner, Ey_inner, Ez_inner = rw_inner.compute_field(r, z)
print(f"   Ex_inner shape: {Ex_inner.shape}")
print(f"   Sample: {Ex_inner[0]}")

# Subtract E-fields
print("\n3. Subtracting E-fields...")
Ex_annular = Ex_outer - Ex_inner
Ey_annular = Ey_outer - Ey_inner
Ez_annular = Ez_outer - Ez_inner

# Get intensity
I_rw = np.abs(Ex_annular)**2 + np.abs(Ey_annular)**2 + np.abs(Ez_annular)**2
I_rw = I_rw / I_rw.max()

print(f"   I_annular shape: {I_rw.shape}")
print(f"   I_annular max: {I_rw.max()}")
print(f"   I_annular[0]: {I_rw[0]}")

# Compare with analytical Fraunhofer
print("\n4. Computing analytical Fraunhofer...")

def I_annular_analytical(kaw, eps):
    kaw_safe = np.where(kaw == 0, 1e-10, kaw)
    term1 = 2 * j1(kaw_safe) / kaw_safe
    term2 = (eps**2) * 2 * j1(eps * kaw_safe) / (eps * kaw_safe)
    I = ((term1 - term2)**2) / ((1 - eps**2)**2)
    return I

# Convert r to kaw
kaw = r * (2 * np.pi * a_outer) / (focal_length * wavelength)
I_analytical = I_annular_analytical(kaw, eps)

# Metrics
mse = np.mean((I_rw - I_analytical)**2)
corr = np.corrcoef(I_rw, I_analytical)[0, 1]

print(f"   MSE = {mse:.6f}")
print(f"   Correlation = {corr:.6f}")

# Plot
print("\n5. Plotting...")
fig, ax = plt.subplots(1, 1, figsize=(10, 7))

ax.plot(r, I_analytical, 'r--', linewidth=2.5, label='Fraunhofer (Analytical)', alpha=0.8)
ax.plot(r, I_rw, 'b-', linewidth=2.5, label='Richards-Wolf (E-field subtraction)', alpha=0.8)
ax.axvline(airy_radius, color='cyan', linestyle=':', linewidth=1.5, alpha=0.7,
           label=f'Airy radius = {airy_radius:.3f} μm')
ax.axhline(0.5, color='gray', linestyle=':', linewidth=1, alpha=0.5)

ax.set_xlabel('Radial distance r (μm)', fontsize=13)
ax.set_ylabel('Normalized Intensity', fontsize=13)
ax.set_title(f'Annular Aperture (ε={eps})\\n' +
             f'MSE={mse:.6f}, Correlation={corr:.6f}',
             fontsize=12, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)
ax.set_xlim(0, r_max)
ax.set_ylim(0, 1.05)

plt.tight_layout()
plt.savefig('data/annular_test_eps_0.5.png', dpi=300, bbox_inches='tight')
print(f"   ✓ Saved: data/annular_test_eps_0.5.png")
plt.show()

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"\nε = {eps}:")
print(f"  MSE:         {mse:.6f}")
print(f"  Correlation: {corr:.6f}")

if mse < 0.01 and corr > 0.99:
    print(f"\n✓✓ EXCELLENT agreement! E-field subtraction method works correctly.")
elif mse < 0.1 and corr > 0.9:
    print(f"\n✓ Good agreement.")
else:
    print(f"\n⚠ Poor agreement - check implementation.")

print("="*80)
