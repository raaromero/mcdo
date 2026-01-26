"""
Find the correction needed to make Richards-Wolf (Gaussian) match Debye (Gaussian).

The goal is to identify what's causing the systematic FWHM difference and correct it.
"""

import sys
sys.path.insert(0, '.')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.special import jv
from scipy import integrate
from monte_carlo.richards_wolf import RichardsWolfSimulator
from monte_carlo.gaussian_beam_theory import FocusedGaussianBeamTheory

# Parameters - use low NA where they should agree
wavelength = 0.532
n_medium = 1.0
NA = 0.1
aperture_default = 1500.0
truncation_coeff = 2.0

theta_max = np.arcsin(NA / n_medium)
focal_length = (aperture_default / 2) / np.tan(theta_max)

print("="*70)
print("FINDING RICHARDS-WOLF CORRECTION")
print("="*70)
print(f"NA = {NA}, λ = {wavelength} μm, α = {truncation_coeff}")
print(f"θ_max = {np.degrees(theta_max):.4f}°")
print()

# Initialize both models
debye = FocusedGaussianBeamTheory(
    numerical_aperture=NA,
    wavelength=wavelength,
    n_medium=n_medium,
    focal_length=focal_length,
    z_focus=0.0,
    truncation_coeff=truncation_coeff
)

rw = RichardsWolfSimulator(
    wavelength=wavelength,
    numerical_aperture=NA,
    n_medium=n_medium,
    polarization='x',
    input_field='gaussian',
    truncation_coeff=truncation_coeff
)

print("="*70)
print("COMPARING MATHEMATICAL FORMULATIONS")
print("="*70)

print("""
DEBYE (Tanaka et al.):
  Integration variable: r0 ∈ [0, 1] (normalized aperture radius)
  Gaussian: exp(-α * r0²)  [simplified, ignoring small ε terms]

RICHARDS-WOLF:
  Integration variable: θ ∈ [0, θ_max]
  Relation: r0 = sin(θ)/sin(θ_max)
  Gaussian: exp(-α * sin²(θ)/sin²(θ_max)) = exp(-α * r0²)

  Additional factors in RW:
  - sqrt(cos(θ)) : aplanatic/energy conservation factor
  - sin(θ) : Jacobian from integration
  - (1 + cos(θ)) or (1 - cos(θ)) : geometric factors

At low NA (θ_max << 1):
  - cos(θ) ≈ 1, so sqrt(cos(θ)) ≈ 1
  - sin(θ) ≈ θ

The sqrt(cos(θ)) factor might be causing the difference!
""")

# Let's compute the focal plane intensity manually with and without sqrt(cos(θ))
print("="*70)
print("TESTING: Effect of sqrt(cos(θ)) apodization factor")
print("="*70)

k = 2 * np.pi / wavelength
sin_alpha = np.sin(theta_max)
sin2_alpha = sin_alpha ** 2

def compute_I0_integral(v, include_sqrt_cos=True, gaussian_alpha=truncation_coeff):
    """Compute I0 integral at focal plane (u=0) for x-polarization."""
    def integrand(theta):
        if abs(np.sin(theta)) < 1e-15:
            return 0.0
        cos_t = np.cos(theta)
        sin_t = np.sin(theta)

        # Aplanatic factor
        if include_sqrt_cos:
            apod = np.sqrt(cos_t)
        else:
            apod = 1.0

        # Geometric factor for I0
        geo = sin_t * (1 + cos_t)

        # Bessel function
        bessel = jv(0, v * sin_t / sin_alpha)

        # Gaussian apodization
        field_apod = np.exp(-gaussian_alpha * sin_t**2 / sin2_alpha)

        return apod * geo * bessel * field_apod

    result, _ = integrate.quad(integrand, 0, theta_max, limit=100)
    return result

# Radial grid
airy_r = 0.61 * wavelength / NA
r = np.linspace(0, 4 * airy_r, 100)
v = k * sin_alpha * r

print("\nComputing intensity profiles...")

# With sqrt(cos(θ)) - standard RW
I_with_sqrt = np.zeros_like(r)
for i, v_val in enumerate(v):
    I0 = compute_I0_integral(v_val, include_sqrt_cos=True)
    I_with_sqrt[i] = np.abs(I0)**2

# Without sqrt(cos(θ))
I_without_sqrt = np.zeros_like(r)
for i, v_val in enumerate(v):
    I0 = compute_I0_integral(v_val, include_sqrt_cos=False)
    I_without_sqrt[i] = np.abs(I0)**2

# Debye
I_debye = debye.focal_plane_intensity(r, z=0.0)

# Normalize all
I_with_sqrt = I_with_sqrt / I_with_sqrt.max()
I_without_sqrt = I_without_sqrt / I_without_sqrt.max()
I_debye = I_debye / I_debye.max()

# FWHM calculation
def compute_fwhm(r, I):
    half_max = 0.5
    above_half = I > half_max
    if above_half.any():
        r_half = r[above_half]
        if len(r_half) > 0:
            return 2 * r_half[-1]
    return np.nan

fwhm_with = compute_fwhm(r, I_with_sqrt)
fwhm_without = compute_fwhm(r, I_without_sqrt)
fwhm_debye = compute_fwhm(r, I_debye)

print(f"\nFWHM Results:")
print(f"  Debye (Gaussian):              {fwhm_debye:.4f} μm")
print(f"  RW with sqrt(cos(θ)):          {fwhm_with:.4f} μm")
print(f"  RW without sqrt(cos(θ)):       {fwhm_without:.4f} μm")

# MSE comparison
mse_with = np.mean((I_debye - I_with_sqrt)**2)
mse_without = np.mean((I_debye - I_without_sqrt)**2)
print(f"\nMSE vs Debye:")
print(f"  RW with sqrt(cos(θ)):          {mse_with:.6f}")
print(f"  RW without sqrt(cos(θ)):       {mse_without:.6f}")

# Now let's check if the issue is in the geometric factors
print("\n" + "="*70)
print("TESTING: Different geometric factor approximations")
print("="*70)

def compute_I0_modified(v, geo_approx='full'):
    """Test different geometric factor approximations."""
    def integrand(theta):
        if abs(np.sin(theta)) < 1e-15:
            return 0.0
        cos_t = np.cos(theta)
        sin_t = np.sin(theta)

        # Aplanatic factor - try without
        apod = 1.0  # np.sqrt(cos_t)

        # Geometric factor
        if geo_approx == 'full':
            geo = sin_t * (1 + cos_t)
        elif geo_approx == 'paraxial':
            # In paraxial limit: sin(θ) ≈ θ, cos(θ) ≈ 1
            # So sin(θ)(1+cos(θ)) ≈ 2*sin(θ) ≈ 2θ
            geo = 2 * sin_t
        elif geo_approx == 'simple':
            # Just sin(θ) - the Jacobian
            geo = sin_t

        bessel = jv(0, v * sin_t / sin_alpha)
        field_apod = np.exp(-truncation_coeff * sin_t**2 / sin2_alpha)

        return apod * geo * bessel * field_apod

    result, _ = integrate.quad(integrand, 0, theta_max, limit=100)
    return result

# Test different approximations
I_full = np.zeros_like(r)
I_paraxial = np.zeros_like(r)
I_simple = np.zeros_like(r)

for i, v_val in enumerate(v):
    I_full[i] = np.abs(compute_I0_modified(v_val, 'full'))**2
    I_paraxial[i] = np.abs(compute_I0_modified(v_val, 'paraxial'))**2
    I_simple[i] = np.abs(compute_I0_modified(v_val, 'simple'))**2

I_full = I_full / I_full.max()
I_paraxial = I_paraxial / I_paraxial.max()
I_simple = I_simple / I_simple.max()

print(f"\nFWHM with no sqrt(cos) and different geometric factors:")
print(f"  geo = sin(θ)(1+cos(θ)):  {compute_fwhm(r, I_full):.4f} μm")
print(f"  geo = 2*sin(θ):          {compute_fwhm(r, I_paraxial):.4f} μm")
print(f"  geo = sin(θ):            {compute_fwhm(r, I_simple):.4f} μm")
print(f"  Debye target:            {fwhm_debye:.4f} μm")

print(f"\nMSE vs Debye:")
print(f"  geo = sin(θ)(1+cos(θ)):  {np.mean((I_debye - I_full)**2):.6f}")
print(f"  geo = 2*sin(θ):          {np.mean((I_debye - I_paraxial)**2):.6f}")
print(f"  geo = sin(θ):            {np.mean((I_debye - I_simple)**2):.6f}")

# Plot comparison
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

ax = axes[0]
ax.plot(r, I_debye, 'b-', lw=2.5, label='Debye (Gaussian)')
ax.plot(r, I_with_sqrt, 'r--', lw=2, label='RW with sqrt(cos(θ))')
ax.plot(r, I_without_sqrt, 'g:', lw=2, label='RW without sqrt(cos(θ))')
ax.set_xlabel('r (μm)')
ax.set_ylabel('Normalized Intensity')
ax.set_title(f'Effect of sqrt(cos(θ)) factor (NA={NA}, α={truncation_coeff})')
ax.legend()
ax.grid(True, alpha=0.3)

ax = axes[1]
ax.plot(r, I_debye, 'b-', lw=2.5, label='Debye (Gaussian)')
ax.plot(r, I_full, 'r--', lw=2, label='RW: sin(θ)(1+cos(θ))')
ax.plot(r, I_paraxial, 'g:', lw=2, label='RW: 2*sin(θ)')
ax.plot(r, I_simple, 'm-.', lw=2, label='RW: sin(θ)')
ax.set_xlabel('r (μm)')
ax.set_ylabel('Normalized Intensity')
ax.set_title('Effect of geometric factor approximations')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('data/comprehensive_comparison/rw_correction_test.png', dpi=200)
print(f"\n✓ Saved: data/comprehensive_comparison/rw_correction_test.png")

# Now let's look at the Debye integrand more carefully
print("\n" + "="*70)
print("COMPARING INTEGRAND STRUCTURE")
print("="*70)

print("""
DEBYE focal_plane_intensity integrand (from Tanaka et al.):
  r0 * J0(P*α*R/Z * r0) * exp(-α²*r0²/(1+ε²)) * [cos(s1*r0²) or sin(s1*r0²)]

  where:
  - r0 ∈ [0, 1] is normalized aperture radius
  - P = k*ws²/f (Fresnel number-like parameter)
  - α = (aperture/2)/ws
  - R = r/ws (normalized focal plane radius)
  - Z = (z - z_lens)/f
  - s1, s2 are phase terms

RICHARDS-WOLF I0 integrand:
  sqrt(cos(θ)) * sin(θ) * (1+cos(θ)) * J0(v*sin(θ)/sin(α)) * exp(-α*sin²(θ)/sin²(α))

Let's compare by transforming RW to r0 coordinates...
""")

# Transform RW integral to r0 coordinates
# r0 = sin(θ)/sin(θ_max), so sin(θ) = r0 * sin(θ_max)
# dθ = d(r0 * sin(θ_max)) / cos(θ) = sin(θ_max) * dr0 / sqrt(1 - r0²*sin²(θ_max))

print("In r0 coordinates, RW I0 integrand becomes:")
print("  [cos(θ)]^(1/2) * [sin(θ_max)*r0] * [1+cos(θ)] * J0(v*r0) * exp(-α*r0²)")
print("  × sin(θ_max)/cos(θ)  [from dθ transformation]")
print("")
print("  = sin²(θ_max) * r0 * (1+cos(θ)) / sqrt(cos(θ)) * J0(v*r0) * exp(-α*r0²)")
print("")
print("For small θ_max: cos(θ) ≈ 1 - θ²/2 ≈ 1 - r0²*sin²(θ_max)/2")
print("So: (1+cos(θ))/sqrt(cos(θ)) ≈ 2 for small θ")
print("")
print("This gives: 2*sin²(θ_max) * r0 * J0(v*r0) * exp(-α*r0²)")
print("")
print("DEBYE has: r0 * J0(...) * exp(-α²*r0²/(1+ε²)) * ...")
print("")
print("The key differences:")
print("1. Bessel argument: RW uses v*r0, Debye uses P*α*R/Z*r0")
print("2. Gaussian argument: RW uses α*r0², Debye uses α²*r0²/(1+ε²)")

# Let's check the actual parameter values
ws = debye.beam_radius(z=debye.z_lens)
alpha_debye = (debye.aperture / 2) / ws
eps = debye.epsilon(z=debye.z_lens)
P = k * ws**2 / debye.f
Z = 1.0  # at focal plane z = z_f, so Z = (z_f - z_lens)/f = f/f = 1

print(f"\nParameter comparison:")
print(f"  RW Gaussian exponent:    α = {truncation_coeff}")
print(f"  Debye Gaussian exponent: α²/(1+ε²) = {alpha_debye**2 / (1 + eps**2):.4f}")
print(f"  (These should match: {np.isclose(truncation_coeff, alpha_debye**2 / (1 + eps**2))})")

# The Bessel arguments
# RW: v * r0 where v = k * sin(α) * r_focal
# Debye: P * α_debye * R / Z * r0 where R = r_focal / ws
# Let's check if these are equivalent

r_test = 1.0  # 1 μm
v_rw = k * sin_alpha * r_test
R_debye = r_test / ws
bessel_arg_debye = P * alpha_debye * R_debye / Z

print(f"\nBessel argument comparison at r = {r_test} μm:")
print(f"  RW: v*r0 at r0=1:        {v_rw:.4f}")
print(f"  Debye: P*α*R/Z at r0=1:  {bessel_arg_debye:.4f}")
print(f"  Ratio: {v_rw / bessel_arg_debye:.4f}")
