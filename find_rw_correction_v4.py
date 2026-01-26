"""
Deep comparison of Debye and RW integrands to find all differences.
"""

import sys
sys.path.insert(0, '.')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.special import jv
from scipy import integrate
from scipy.special import expit
from monte_carlo.gaussian_beam_theory import FocusedGaussianBeamTheory

wavelength = 0.532
n_medium = 1.0
aperture_default = 1500.0
k = 2 * np.pi / wavelength

def compute_fwhm(r, I):
    half_max = 0.5
    above_half = I > half_max
    if above_half.any():
        r_half = r[above_half]
        if len(r_half) > 0:
            return 2 * r_half[-1]
    return np.nan

# Work at NA = 0.1 where there's still mismatch
NA = 0.1
truncation_coeff = 2.0

theta_max = np.arcsin(NA / n_medium)
focal_length = (aperture_default / 2) / np.tan(theta_max)

debye = FocusedGaussianBeamTheory(
    numerical_aperture=NA,
    wavelength=wavelength,
    n_medium=n_medium,
    focal_length=focal_length,
    z_focus=0.0,
    truncation_coeff=truncation_coeff
)

# Get Debye parameters
ws = debye.beam_radius(z=debye.z_lens)
alpha_debye = (debye.aperture / 2) / ws
eps = debye.epsilon(z=debye.z_lens)
P = k * ws**2 / debye.f
Z = 1.0  # at focal plane

s1 = (P * alpha_debye**2 * (1 - Z) / (2 * Z)) + (alpha_debye**2 * eps / (1 + eps**2))
s2 = -alpha_debye**2 / (1 + eps**2)

print("="*70)
print("DEBYE PARAMETERS")
print("="*70)
print(f"NA = {NA}, α = {truncation_coeff}")
print(f"ws = {ws:.4f}")
print(f"alpha_debye = {alpha_debye:.6f}")
print(f"alpha_debye² = {alpha_debye**2:.6f}")
print(f"epsilon = {eps:.6f}")
print(f"P = {P:.4f}")
print(f"s1 = {s1:.6f}")
print(f"s2 = {s2:.6f}")

# The Debye integral for focal plane intensity is (from Tanaka et al.):
# I(r) = factor * (firstterm² + secondterm²)
# where:
#   firstterm = ∫₀¹ r0 * J0(P*α*R/Z*r0) * exp(s2*r0²) * cos(s1*r0²) dr0
#   secondterm = ∫₀¹ r0 * J0(P*α*R/Z*r0) * exp(s2*r0²) * sin(s1*r0²) dr0

# Note: The Debye code uses expit which is actually just exp for negative arguments
# expit(x) = 1/(1+exp(-x)), but for numerical purposes with large negative x,
# it's approximately exp(x)

# Actually wait - looking at the code more carefully:
# expit is scipy.special.expit = 1/(1+e^-x), the logistic function
# But they're using it with s2 which is negative...

print(f"\nChecking expit usage:")
print(f"s2 = {s2:.6f}")
print(f"expit(s2) = {expit(s2):.6f}")
print(f"exp(s2) = {np.exp(s2):.6f}")

# Ah! expit(s2) ≠ exp(s2)!
# expit(-2) = 1/(1+e^2) ≈ 0.119
# exp(-2) = e^-2 ≈ 0.135
# This could be a bug in the Debye code or intentional

# Let me read the Debye code again...
print("\n" + "="*70)
print("RE-IMPLEMENTING DEBYE INTEGRAL CORRECTLY")
print("="*70)

def debye_intensity_manual(r_array, use_expit=True):
    """Manually compute Debye intensity following the code."""
    intensity = np.zeros_like(r_array)

    for i, r in enumerate(r_array):
        R = r / ws

        def f1_integrand(r0):
            bessel_arg = P * alpha_debye * R / Z * r0
            if use_expit:
                gauss = expit(-alpha_debye**2 * r0**2 / (1 + eps**2))
            else:
                gauss = np.exp(-alpha_debye**2 * r0**2 / (1 + eps**2))
            return r0 * jv(0, bessel_arg) * gauss * np.cos(s1 * r0**2)

        def f2_integrand(r0):
            bessel_arg = P * alpha_debye * R / Z * r0
            if use_expit:
                gauss = expit(-alpha_debye**2 * r0**2 / (1 + eps**2))
            else:
                gauss = np.exp(-alpha_debye**2 * r0**2 / (1 + eps**2))
            return r0 * jv(0, bessel_arg) * gauss * np.sin(s1 * r0**2)

        factor = P**2 * alpha_debye**4 / (4 * Z**2 * (s1**2 + s2**2))

        firstterm, _ = integrate.quad(f1_integrand, 0, 1, limit=100)
        secondterm, _ = integrate.quad(f2_integrand, 0, 1, limit=100)

        intensity[i] = factor * (firstterm**2 + secondterm**2)

    return intensity / intensity.max()

# RW implementation
sin_alpha = np.sin(theta_max)
sin2_alpha = sin_alpha ** 2

def rw_intensity(r_array, remove_sqrt_cos=False, remove_geo_factor=False):
    """RW focal plane intensity with options to disable factors."""
    intensity = np.zeros_like(r_array)

    for i, r in enumerate(r_array):
        v = k * sin_alpha * r

        def I0_integrand(theta):
            if abs(np.sin(theta)) < 1e-15:
                return 0.0
            cos_t = np.cos(theta)
            sin_t = np.sin(theta)

            # Aplanatic factor
            if remove_sqrt_cos:
                apod = 1.0
            else:
                apod = np.sqrt(cos_t)

            # Geometric factor
            if remove_geo_factor:
                geo = sin_t  # Just Jacobian
            else:
                geo = sin_t * (1 + cos_t)

            bessel = jv(0, v * sin_t / sin_alpha)
            field_apod = np.exp(-truncation_coeff * sin_t**2 / sin2_alpha)

            return apod * geo * bessel * field_apod

        I0, _ = integrate.quad(I0_integrand, 0, theta_max, limit=100)
        intensity[i] = np.abs(I0)**2

    return intensity / intensity.max()

# Test different configurations
airy_r = 0.61 * wavelength / NA
r = np.linspace(0, 4 * airy_r, 100)

print("\nComputing intensity profiles...")

I_debye_orig = debye.focal_plane_intensity(r, z=0.0)
I_debye_orig = I_debye_orig / I_debye_orig.max()

I_debye_expit = debye_intensity_manual(r, use_expit=True)
I_debye_exp = debye_intensity_manual(r, use_expit=False)

I_rw_standard = rw_intensity(r, remove_sqrt_cos=False, remove_geo_factor=False)
I_rw_no_sqrt = rw_intensity(r, remove_sqrt_cos=True, remove_geo_factor=False)
I_rw_no_geo = rw_intensity(r, remove_sqrt_cos=True, remove_geo_factor=True)

print(f"\nFWHM comparison:")
print(f"  Debye (original):      {compute_fwhm(r, I_debye_orig):.4f} μm")
print(f"  Debye (expit):         {compute_fwhm(r, I_debye_expit):.4f} μm")
print(f"  Debye (exp):           {compute_fwhm(r, I_debye_exp):.4f} μm")
print(f"  RW (standard):         {compute_fwhm(r, I_rw_standard):.4f} μm")
print(f"  RW (no sqrt(cos)):     {compute_fwhm(r, I_rw_no_sqrt):.4f} μm")
print(f"  RW (no sqrt, no geo):  {compute_fwhm(r, I_rw_no_geo):.4f} μm")

# Check if expit is the issue
print(f"\nMSE vs Debye (original):")
print(f"  Debye (expit):         {np.mean((I_debye_orig - I_debye_expit)**2):.8f}")
print(f"  Debye (exp):           {np.mean((I_debye_orig - I_debye_exp)**2):.8f}")
print(f"  RW (standard):         {np.mean((I_debye_orig - I_rw_standard)**2):.6f}")

# The key difference might be the phase term cos(s1*r0²) + i*sin(s1*r0²)
# At focal plane, s1 is very small but not zero

print(f"\n" + "="*70)
print("TESTING: Effect of phase term s1")
print("="*70)

# At focal plane, the phase factor is exp(i*s1*r0²) = cos(s1*r0²) + i*sin(s1*r0²)
# s1 is small but nonzero due to epsilon term
print(f"s1 = {s1:.8f}")
print(f"At r0=1: cos(s1) = {np.cos(s1):.8f}, sin(s1) = {np.sin(s1):.8f}")

# The intensity is (firstterm² + secondterm²) which is |∫... exp(i*s1*r0²)|²
# If we ignore the phase: |(∫... * 1)|² = firstterm² (with cos=1, sin=0)

def debye_no_phase(r_array):
    """Debye without the phase oscillation term."""
    intensity = np.zeros_like(r_array)

    for i, r in enumerate(r_array):
        R = r / ws

        def integrand(r0):
            bessel_arg = P * alpha_debye * R / Z * r0
            gauss = np.exp(-alpha_debye**2 * r0**2 / (1 + eps**2))
            # No phase term - equivalent to cos(0) = 1, sin(0) = 0
            return r0 * jv(0, bessel_arg) * gauss

        result, _ = integrate.quad(integrand, 0, 1, limit=100)
        # Just the squared magnitude of the integral
        intensity[i] = result**2

    return intensity / intensity.max()

I_debye_no_phase = debye_no_phase(r)
print(f"\nFWHM Debye (no phase term): {compute_fwhm(r, I_debye_no_phase):.4f} μm")
print(f"MSE vs Debye (original):    {np.mean((I_debye_orig - I_debye_no_phase)**2):.8f}")

# Now let's make RW match Debye by transforming to the same variables
print("\n" + "="*70)
print("MATCHING RW TO DEBYE BY COORDINATE TRANSFORM")
print("="*70)

# In Debye: integrate over r0 ∈ [0, 1]
# In RW: integrate over θ ∈ [0, θ_max]
# Transform: r0 = sin(θ)/sin(θ_max)
# dr0 = cos(θ)/sin(θ_max) * dθ = cos(θ)/sin(θ_max) * dθ

# RW integrand in θ: sqrt(cos(θ)) * sin(θ) * (1+cos(θ)) * J0(v*sin(θ)/sin(α)) * exp(-α*sin²(θ)/sin²(α))
# Transform to r0: sqrt(cos) * (r0*sinα) * (1+cos) * J0(v*r0) * exp(-α*r0²) * (sinα/cos) dr0
#                = sinα² * r0 * (1+cos)/sqrt(cos) * J0(v*r0) * exp(-α*r0²) dr0

# At small θ: cos ≈ 1, so (1+cos)/sqrt(cos) ≈ 2
# So: 2*sinα² * r0 * J0(v*r0) * exp(-α*r0²)

# Debye: r0 * J0(P*α*R/Z*r0) * exp(-α*r0²)
# (ignoring phase, using α = alpha_debye² and small ε)

# So the structures are similar but:
# 1. Debye has P*α*R/Z as Bessel coefficient, RW has v = k*sinα*r
# 2. RW has extra factor 2*sinα²

# Let's compute what the Bessel arguments actually are
print(f"\nBessel argument comparison at r=1, r0=1:")
r_test = 1.0
R_test = r_test / ws
v_test = k * sin_alpha * r_test

bessel_debye = P * alpha_debye * R_test / Z
bessel_rw = v_test

print(f"  Debye: P*α*R/Z = {bessel_debye:.6f}")
print(f"  RW: v = k*sinα*r = {bessel_rw:.6f}")
print(f"  Ratio: {bessel_debye/bessel_rw:.6f}")

# These should be the same if the coordinate systems match
# P*α*R/Z = (k*ws²/f) * ((aperture/2)/ws) * (r/ws) / Z
#         = k * (aperture/2) * r / (f * Z)
#         = k * tan(θ_max) * r  (since aperture/2 = f*tan(θ_max))

# v = k * sin(θ_max) * r

# Ratio = tan/sin = 1/cos ≈ 1.005

# Let me try implementing RW in r0 coordinates directly
def rw_in_r0_coords(r_array):
    """RW integral transformed to r0 coordinates."""
    intensity = np.zeros_like(r_array)

    for i, r in enumerate(r_array):
        # Use same Bessel argument as Debye
        bessel_coeff = P * alpha_debye / Z * (r / ws)

        def integrand(r0):
            # Transform θ dependencies to r0
            # sin(θ) = r0 * sin(θ_max)
            # cos(θ) = sqrt(1 - r0² * sin²(θ_max))
            sin_t = r0 * sin_alpha
            cos_t = np.sqrt(1 - sin_t**2)

            # RW factors
            apod = np.sqrt(cos_t)
            geo_factor = (1 + cos_t) / cos_t  # Jacobian included

            # Gaussian with truncation_coeff (not alpha_debye²)
            gauss = np.exp(-truncation_coeff * r0**2)

            # Bessel - now with Debye-style argument
            bessel = jv(0, bessel_coeff * r0)

            return r0 * apod * geo_factor * bessel * gauss * sin_alpha**2

        result, _ = integrate.quad(integrand, 0, 1, limit=100)
        intensity[i] = result**2

    return intensity / intensity.max()

I_rw_r0 = rw_in_r0_coords(r)
print(f"\nFWHM RW (r0 coords):     {compute_fwhm(r, I_rw_r0):.4f} μm")
print(f"MSE vs Debye (original): {np.mean((I_debye_orig - I_rw_r0)**2):.6f}")

# Plot comparison
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

ax = axes[0]
ax.plot(r, I_debye_orig, 'b-', lw=2.5, label='Debye (original)')
ax.plot(r, I_rw_standard, 'r--', lw=2, label='RW (standard)')
ax.plot(r, I_rw_r0, 'g:', lw=2.5, label='RW (r0 coords, Debye Bessel)')
ax.set_xlabel('r (μm)')
ax.set_ylabel('Normalized Intensity')
ax.set_title(f'NA={NA}, α={truncation_coeff}')
ax.legend()
ax.grid(True, alpha=0.3)

ax = axes[1]
ax.plot(r, I_debye_orig - I_rw_standard, 'r-', lw=2, label='Debye - RW (standard)')
ax.plot(r, I_debye_orig - I_rw_r0, 'g-', lw=2, label='Debye - RW (r0)')
ax.axhline(0, color='k', ls='--', lw=1)
ax.set_xlabel('r (μm)')
ax.set_ylabel('Difference')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('data/comprehensive_comparison/rw_correction_v4.png', dpi=200)
print(f"\n✓ Saved: data/comprehensive_comparison/rw_correction_v4.png")
