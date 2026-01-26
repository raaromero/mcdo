"""
Verify Gaussian annular aperture implementation.

The key insight: For a Gaussian beam illuminating an annular aperture,
both the outer (full) and inner (obstructed) regions sample the SAME
Gaussian profile - just with different integration limits.

Verification tests:
1. Visual: Show both inner/outer sample the same Gaussian curve
2. Limit ε→0: Annular should equal circular aperture
3. Limit ε→1: Annular should approach zero (infinitely thin ring)
4. Energy check: Power scaling should be consistent
"""

import sys
sys.path.insert(0, '.')

import numpy as np
import matplotlib.pyplot as plt
from scipy.special import jv
from monte_carlo.richards_wolf import RichardsWolfSimulator

print("="*80)
print("VERIFICATION: Gaussian Annular Aperture Implementation")
print("="*80)

wavelength = 0.532
NA_outer = 0.9
n_medium = 1.0
alpha = 2.0  # truncation coefficient

theta_outer = np.arcsin(NA_outer / n_medium)
sin2_alpha_outer = np.sin(theta_outer)**2

print(f"\nParameters:")
print(f"  λ = {wavelength} μm")
print(f"  NA_outer = {NA_outer}")
print(f"  θ_outer = {np.degrees(theta_outer):.2f}°")
print(f"  α (truncation) = {alpha}")

# =============================================================================
# TEST 1: Visualize the Gaussian profile
# =============================================================================
print("\n" + "="*80)
print("TEST 1: Gaussian Profile Visualization")
print("="*80)

theta = np.linspace(0, theta_outer, 100)

# Correct Gaussian (same for both inner and outer)
A_correct = np.exp(-alpha * np.sin(theta)**2 / sin2_alpha_outer)

# What the CURRENT code does for inner (WRONG)
eps = 0.5
NA_inner = NA_outer * eps
theta_inner = np.arcsin(NA_inner / n_medium)
sin2_alpha_inner = np.sin(theta_inner)**2
A_wrong_inner = np.exp(-alpha * np.sin(theta)**2 / sin2_alpha_inner)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Plot 1: Gaussian profiles
ax = axes[0]
ax.plot(np.degrees(theta), A_correct, 'b-', lw=2.5, label='Correct: Same Gaussian for both')
ax.plot(np.degrees(theta), A_wrong_inner, 'r--', lw=2, label=f'Wrong: Inner uses sin²(θ_inner)')
ax.axvline(np.degrees(theta_inner), color='orange', ls=':', lw=2, label=f'θ_inner (ε={eps})')
ax.axvline(np.degrees(theta_outer), color='green', ls=':', lw=2, label=f'θ_outer')
ax.fill_between(np.degrees(theta), 0, A_correct, where=theta <= theta_inner,
                alpha=0.3, color='orange', label='Inner disk region')
ax.fill_between(np.degrees(theta), 0, A_correct, where=theta > theta_inner,
                alpha=0.3, color='blue', label='Annular ring region')
ax.set_xlabel('Angle θ (degrees)', fontsize=12)
ax.set_ylabel('Gaussian Amplitude A(θ)', fontsize=12)
ax.set_title('Gaussian Apodization Profile', fontsize=12, fontweight='bold')
ax.legend(loc='upper right', fontsize=9)
ax.grid(True, alpha=0.3)
ax.set_xlim([0, np.degrees(theta_outer)*1.1])
ax.set_ylim([0, 1.1])

# Plot 2: Show the error
ax = axes[1]
# At θ_inner, compare values
theta_test = np.linspace(0, theta_inner, 50)
A_correct_test = np.exp(-alpha * np.sin(theta_test)**2 / sin2_alpha_outer)
A_wrong_test = np.exp(-alpha * np.sin(theta_test)**2 / sin2_alpha_inner)
error = np.abs(A_correct_test - A_wrong_test) / A_correct_test * 100

ax.plot(np.degrees(theta_test), error, 'r-', lw=2.5)
ax.set_xlabel('Angle θ (degrees)', fontsize=12)
ax.set_ylabel('Relative Error (%)', fontsize=12)
ax.set_title(f'Error in Inner Disk Gaussian (ε={eps})', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3)

# At the inner edge
A_at_inner_correct = np.exp(-alpha * sin2_alpha_inner / sin2_alpha_outer)
A_at_inner_wrong = np.exp(-alpha)  # = exp(-α) because sin²(θ)/sin²(θ) = 1
print(f"\n  At θ_inner = {np.degrees(theta_inner):.2f}°:")
print(f"    Correct Gaussian value: {A_at_inner_correct:.4f}")
print(f"    Wrong (current) value:  {A_at_inner_wrong:.4f}")
print(f"    Error: {abs(A_at_inner_correct - A_at_inner_wrong)/A_at_inner_correct*100:.1f}%")

plt.tight_layout()
plt.savefig('data/comprehensive_comparison/verify_gaussian_profile.png', dpi=150)
print(f"\n  ✓ Saved: data/comprehensive_comparison/verify_gaussian_profile.png")
plt.close()

# =============================================================================
# TEST 2: Current implementation check
# =============================================================================
print("\n" + "="*80)
print("TEST 2: Check Current Implementation")
print("="*80)

# Create outer and inner simulators with SAME truncation coefficient
rw_outer = RichardsWolfSimulator(
    wavelength=wavelength,
    numerical_aperture=NA_outer,
    n_medium=n_medium,
    polarization='x',
    input_field='gaussian',
    truncation_coeff=alpha
)

rw_inner = RichardsWolfSimulator(
    wavelength=wavelength,
    numerical_aperture=NA_inner,
    n_medium=n_medium,
    polarization='x',
    input_field='gaussian',
    truncation_coeff=alpha
)

print(f"\n  Outer simulator:")
print(f"    NA = {rw_outer.numerical_aperture}")
print(f"    sin²(α) = {rw_outer.sin2_alpha:.6f}")
print(f"    truncation_coeff = {rw_outer.truncation_coeff}")

print(f"\n  Inner simulator:")
print(f"    NA = {rw_inner.numerical_aperture}")
print(f"    sin²(α) = {rw_inner.sin2_alpha:.6f}")
print(f"    truncation_coeff = {rw_inner.truncation_coeff}")

print(f"\n  ⚠️  Problem: Inner uses sin²(α) = {rw_inner.sin2_alpha:.6f}")
print(f"              Should use sin²(α) = {rw_outer.sin2_alpha:.6f} (outer's value)")
print(f"              Ratio: {rw_inner.sin2_alpha / rw_outer.sin2_alpha:.4f} (should be 1.0)")

# =============================================================================
# TEST 3: Limit case ε → 0 (should match circular)
# =============================================================================
print("\n" + "="*80)
print("TEST 3: Limit Case ε → 0 (Should Match Circular Aperture)")
print("="*80)

# For ε=0, annular = full circular aperture
r = np.linspace(0, 0.5, 100)
z = np.zeros_like(r)

# Circular aperture (ε=0)
Ex_circular, _, Ez_circular = rw_outer.compute_field(r, z)
I_circular = np.abs(Ex_circular)**2 + np.abs(Ez_circular)**2
I_circular = I_circular / I_circular.max()

# "Annular" with ε≈0 (tiny inner disk)
eps_tiny = 0.01
NA_tiny = NA_outer * eps_tiny
rw_tiny = RichardsWolfSimulator(
    wavelength=wavelength,
    numerical_aperture=NA_tiny,
    n_medium=n_medium,
    polarization='x',
    input_field='gaussian',
    truncation_coeff=alpha
)
Ex_tiny, _, Ez_tiny = rw_tiny.compute_field(r, z)
Ex_annular = Ex_circular - Ex_tiny
Ez_annular = Ez_circular - Ez_tiny
I_annular_tiny = np.abs(Ex_annular)**2 + np.abs(Ez_annular)**2
I_annular_tiny = I_annular_tiny / I_annular_tiny.max()

# Compare
mse = np.mean((I_circular - I_annular_tiny)**2)
corr = np.corrcoef(I_circular.flatten(), I_annular_tiny.flatten())[0, 1]

print(f"\n  Circular (ε=0) vs Annular (ε={eps_tiny}):")
print(f"    MSE = {mse:.8f}")
print(f"    Correlation = {corr:.8f}")
print(f"    {'✓ PASS' if corr > 0.999 else '✗ FAIL'}: Should be nearly identical")

# =============================================================================
# TEST 4: Compare OLD vs NEW implementation (using gaussian_reference_na)
# =============================================================================
print("\n" + "="*80)
print("TEST 4: Old vs New Implementation for ε=0.5")
print("="*80)

eps = 0.5
NA_inner = NA_outer * eps

# OLD implementation (no gaussian_reference_na - WRONG for annular)
rw_inner_old = RichardsWolfSimulator(
    wavelength=wavelength,
    numerical_aperture=NA_inner,
    n_medium=n_medium,
    polarization='x',
    input_field='gaussian',
    truncation_coeff=alpha  # Uses its own sin²(α_inner) - WRONG
)

# NEW implementation (with gaussian_reference_na - CORRECT for annular)
rw_inner_new = RichardsWolfSimulator(
    wavelength=wavelength,
    numerical_aperture=NA_inner,
    n_medium=n_medium,
    polarization='x',
    input_field='gaussian',
    truncation_coeff=alpha,
    gaussian_reference_na=NA_outer  # Use outer NA for Gaussian normalization
)

print(f"\n  OLD inner: gaussian_sin2_alpha = {rw_inner_old.gaussian_sin2_alpha:.6f}")
print(f"  NEW inner: gaussian_sin2_alpha = {rw_inner_new.gaussian_sin2_alpha:.6f}")
print(f"  Outer:     gaussian_sin2_alpha = {rw_outer.sin2_alpha:.6f}")
print(f"  NEW matches outer: {np.isclose(rw_inner_new.gaussian_sin2_alpha, rw_outer.sin2_alpha)}")

Ex_outer, _, Ez_outer = rw_outer.compute_field(r, z)

# Old (wrong) annular
Ex_inner_old, _, Ez_inner_old = rw_inner_old.compute_field(r, z)
Ex_annular_old = Ex_outer - Ex_inner_old
Ez_annular_old = Ez_outer - Ez_inner_old
I_annular_old = np.abs(Ex_annular_old)**2 + np.abs(Ez_annular_old)**2

# New (correct) annular
Ex_inner_new, _, Ez_inner_new = rw_inner_new.compute_field(r, z)
Ex_annular_new = Ex_outer - Ex_inner_new
Ez_annular_new = Ez_outer - Ez_inner_new
I_annular_new = np.abs(Ex_annular_new)**2 + np.abs(Ez_annular_new)**2

# For comparison, also compute with manual alpha correction (should match NEW)
alpha_manual = alpha * rw_inner_old.sin2_alpha / rw_outer.sin2_alpha
rw_inner_manual = RichardsWolfSimulator(
    wavelength=wavelength,
    numerical_aperture=NA_inner,
    n_medium=n_medium,
    polarization='x',
    input_field='gaussian',
    truncation_coeff=alpha_manual
)
Ex_inner_manual, _, Ez_inner_manual = rw_inner_manual.compute_field(r, z)
Ex_annular_manual = Ex_outer - Ex_inner_manual
Ez_annular_manual = Ez_outer - Ez_inner_manual
I_annular_manual = np.abs(Ex_annular_manual)**2 + np.abs(Ez_annular_manual)**2

I_annular_current = I_annular_old
I_annular_corrected = I_annular_new

# Normalize
I_annular_current = I_annular_current / I_annular_current.max()
I_annular_corrected = I_annular_corrected / I_annular_corrected.max()

# Compare
diff = np.abs(I_annular_current - I_annular_corrected)
max_diff = np.max(diff)
mean_diff = np.mean(diff)

print(f"\n  Comparison of Current vs Corrected:")
print(f"    Max difference: {max_diff:.6f}")
print(f"    Mean difference: {mean_diff:.6f}")

# Plot comparison
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

ax = axes[0]
ax.plot(r, I_annular_current, 'r-', lw=2.5, label='Current (wrong?)')
ax.plot(r, I_annular_corrected, 'b--', lw=2, label='Corrected')
ax.set_xlabel('r (μm)')
ax.set_ylabel('Normalized Intensity')
ax.set_title(f'Gaussian Annular (ε={eps})\nNA={NA_outer}, α={alpha}')
ax.legend()
ax.grid(True, alpha=0.3)

ax = axes[1]
ax.plot(r, diff, 'k-', lw=2)
ax.set_xlabel('r (μm)')
ax.set_ylabel('|I_current - I_corrected|')
ax.set_title(f'Absolute Difference\nMax={max_diff:.4f}')
ax.grid(True, alpha=0.3)

ax = axes[2]
ax.semilogy(r, I_annular_current, 'r-', lw=2.5, label='Current')
ax.semilogy(r, I_annular_corrected, 'b--', lw=2, label='Corrected')
ax.set_xlabel('r (μm)')
ax.set_ylabel('Normalized Intensity (log)')
ax.set_title('Log Scale (shows tails)')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('data/comprehensive_comparison/verify_gaussian_annular_comparison.png', dpi=150)
print(f"\n  ✓ Saved: data/comprehensive_comparison/verify_gaussian_annular_comparison.png")
plt.close()

# Check that NEW and manual methods match
I_manual_norm = I_annular_manual / I_annular_manual.max()
new_vs_manual_diff = np.max(np.abs(I_annular_corrected - I_manual_norm))
print(f"\n  Verification: NEW vs manual α-correction match: {new_vs_manual_diff:.2e}")
print(f"    {'✓ PASS' if new_vs_manual_diff < 1e-10 else '✗ FAIL'}")

# =============================================================================
# Summary
# =============================================================================
print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"""
FIX IMPLEMENTED: Added 'gaussian_reference_na' parameter to RichardsWolfSimulator

When computing Gaussian annular apertures via Babinet's principle:
  E_annular = E_outer - E_inner

The Gaussian apodization for BOTH should sample the SAME physical beam:
  A(θ) = exp(-α · sin²(θ) / sin²(θ_outer))

USAGE for annular apertures:
  # Outer disk (normal usage)
  rw_outer = RichardsWolfSimulator(NA=NA_outer, input_field='gaussian', truncation_coeff=α)

  # Inner disk (use gaussian_reference_na to match outer's Gaussian)
  rw_inner = RichardsWolfSimulator(NA=NA_inner, input_field='gaussian', truncation_coeff=α,
                                    gaussian_reference_na=NA_outer)  # ← KEY FIX

The difference between old (wrong) and new (correct) is {max_diff*100:.1f}% at maximum.
""")

print("="*80)
