"""
Find the exact correction to make Richards-Wolf (Gaussian) match Debye (Gaussian).

The Bessel argument differs:
- Debye: k * r * r0 * tan(θ_max)
- RW:    k * r * r0 * sin(θ_max)

Correction: multiply RW Bessel argument by 1/cos(θ_max)
"""

import sys
sys.path.insert(0, '.')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.special import jv
from scipy import integrate
from monte_carlo.gaussian_beam_theory import FocusedGaussianBeamTheory

wavelength = 0.532
n_medium = 1.0
aperture_default = 1500.0
truncation_coeff = 2.0
k = 2 * np.pi / wavelength

def compute_fwhm(r, I):
    half_max = 0.5
    above_half = I > half_max
    if above_half.any():
        r_half = r[above_half]
        if len(r_half) > 0:
            return 2 * r_half[-1]
    return np.nan

def compute_rw_intensity(r_array, NA, trunc_coeff, bessel_correction=1.0):
    """
    Compute RW focal plane intensity with optional Bessel argument correction.

    bessel_correction: multiply Bessel argument by this factor
    """
    theta_max = np.arcsin(NA / n_medium)
    sin_alpha = np.sin(theta_max)
    sin2_alpha = sin_alpha ** 2

    intensity = np.zeros_like(r_array)

    for i, r in enumerate(r_array):
        v = k * sin_alpha * r  # Standard optical coordinate

        def I0_integrand(theta):
            if abs(np.sin(theta)) < 1e-15:
                return 0.0
            cos_t = np.cos(theta)
            sin_t = np.sin(theta)

            apod = np.sqrt(cos_t)
            geo = sin_t * (1 + cos_t)

            # Bessel argument with correction factor
            bessel_arg = v * sin_t / sin_alpha * bessel_correction
            bessel = jv(0, bessel_arg)

            field_apod = np.exp(-trunc_coeff * sin_t**2 / sin2_alpha)

            return apod * geo * bessel * field_apod

        I0, _ = integrate.quad(I0_integrand, 0, theta_max, limit=100)
        intensity[i] = np.abs(I0)**2

    return intensity / intensity.max()

print("="*70)
print("TESTING BESSEL ARGUMENT CORRECTION: multiply by 1/cos(θ_max)")
print("="*70)

NA_values = [0.1, 0.3, 0.5]
alpha_values = [1.1, 2.0, 4.0]

print(f"\n{'NA':>6} {'α':>6} {'FWHM_Debye':>12} {'FWHM_RW':>12} {'FWHM_RW_corr':>12} {'MSE':>10} {'MSE_corr':>10}")
print("-"*76)

for NA in NA_values:
    theta_max = np.arcsin(NA / n_medium)
    focal_length = (aperture_default / 2) / np.tan(theta_max)
    cos_alpha = np.cos(theta_max)
    correction_factor = 1.0 / cos_alpha

    airy_r = 0.61 * wavelength / NA
    r = np.linspace(0, 3 * airy_r, 80)

    for alpha in alpha_values:
        debye = FocusedGaussianBeamTheory(
            numerical_aperture=NA,
            wavelength=wavelength,
            n_medium=n_medium,
            focal_length=focal_length,
            z_focus=0.0,
            truncation_coeff=alpha
        )

        I_debye = debye.focal_plane_intensity(r, z=0.0)
        I_debye = I_debye / I_debye.max()

        I_rw = compute_rw_intensity(r, NA, alpha, bessel_correction=1.0)
        I_rw_corr = compute_rw_intensity(r, NA, alpha, bessel_correction=correction_factor)

        fwhm_d = compute_fwhm(r, I_debye)
        fwhm_rw = compute_fwhm(r, I_rw)
        fwhm_rw_c = compute_fwhm(r, I_rw_corr)

        mse = np.mean((I_debye - I_rw)**2)
        mse_c = np.mean((I_debye - I_rw_corr)**2)

        print(f"{NA:6.2f} {alpha:6.2f} {fwhm_d:12.4f} {fwhm_rw:12.4f} {fwhm_rw_c:12.4f} {mse:10.6f} {mse_c:10.6f}")

# That didn't work. Let me try a different approach - look at the actual Debye integrand
print("\n" + "="*70)
print("DEEP DIVE: Comparing integrand structure")
print("="*70)

NA = 0.1
alpha = 2.0
theta_max = np.arcsin(NA / n_medium)
focal_length = (aperture_default / 2) / np.tan(theta_max)

debye = FocusedGaussianBeamTheory(
    numerical_aperture=NA,
    wavelength=wavelength,
    n_medium=n_medium,
    focal_length=focal_length,
    z_focus=0.0,
    truncation_coeff=alpha
)

# Get Debye parameters
ws = debye.beam_radius(z=debye.z_lens)
alpha_debye = (debye.aperture / 2) / ws
eps = debye.epsilon(z=debye.z_lens)
P = k * ws**2 / debye.f

print(f"\nDebye parameters:")
print(f"  ws (beam at lens) = {ws:.4f} μm")
print(f"  alpha_debye = (aperture/2)/ws = {alpha_debye:.4f}")
print(f"  epsilon = {eps:.6f}")
print(f"  P = k*ws²/f = {P:.4f}")
print(f"  truncation_coeff = {alpha}")
print(f"  alpha_debye² / (1+eps²) = {alpha_debye**2 / (1+eps**2):.4f}")

# The Debye integral at focal plane (z = z_f, Z = 1) is:
# I = factor * |∫₀¹ r0 * J0(P*α*R*r0) * exp(-α²*r0²/(1+ε²)) * [cos(s1*r0²) + i*sin(s1*r0²)] dr0|²

# Let's check what s1 is at focal plane
z = debye.z_f
Z = (z - debye.z_lens) / debye.f  # This should be ~1
s1 = (P * alpha_debye**2 * (1 - Z) / (2 * Z)) + (alpha_debye**2 * eps / (1 + eps**2))
s2 = -alpha_debye**2 / (1 + eps**2)

print(f"\nAt focal plane (z = z_f):")
print(f"  Z = (z - z_lens)/f = {Z:.6f}")
print(f"  s1 = {s1:.6f}")
print(f"  s2 = {s2:.6f}")

# For r = 0, what's the Bessel argument?
r_test = 1.0  # μm
R = r_test / ws
bessel_arg_debye = P * alpha_debye * R / Z

sin_alpha = np.sin(theta_max)
v_rw = k * sin_alpha * r_test
bessel_arg_rw = v_rw  # This is v * sin(θ)/sin(α) at r0=1, which = v

print(f"\nBessel argument at r = {r_test} μm, r0 = 1:")
print(f"  Debye: P*α*R/Z = {bessel_arg_debye:.6f}")
print(f"  RW: v = k*sin(α)*r = {bessel_arg_rw:.6f}")
print(f"  Ratio (Debye/RW) = {bessel_arg_debye/bessel_arg_rw:.6f}")

# So the Bessel arguments ARE different! Let me compute what scaling would make them match
scaling_needed = bessel_arg_debye / bessel_arg_rw
print(f"\nTo match Debye, RW needs to scale Bessel arg by: {scaling_needed:.6f}")

# Now test with this exact scaling
print("\n" + "="*70)
print(f"TESTING with exact scaling factor = {scaling_needed:.6f}")
print("="*70)

airy_r = 0.61 * wavelength / NA
r = np.linspace(0, 4 * airy_r, 100)

I_debye = debye.focal_plane_intensity(r, z=0.0)
I_debye = I_debye / I_debye.max()

I_rw = compute_rw_intensity(r, NA, alpha, bessel_correction=1.0)
I_rw_corr = compute_rw_intensity(r, NA, alpha, bessel_correction=scaling_needed)

fwhm_d = compute_fwhm(r, I_debye)
fwhm_rw = compute_fwhm(r, I_rw)
fwhm_rw_c = compute_fwhm(r, I_rw_corr)

mse = np.mean((I_debye - I_rw)**2)
mse_c = np.mean((I_debye - I_rw_corr)**2)
corr = np.corrcoef(I_debye, I_rw)[0,1]
corr_c = np.corrcoef(I_debye, I_rw_corr)[0,1]

print(f"\nResults:")
print(f"  FWHM Debye:          {fwhm_d:.4f} μm")
print(f"  FWHM RW (standard):  {fwhm_rw:.4f} μm")
print(f"  FWHM RW (corrected): {fwhm_rw_c:.4f} μm")
print(f"\n  MSE (standard):      {mse:.6f}")
print(f"  MSE (corrected):     {mse_c:.6f}")
print(f"\n  Corr (standard):     {corr:.6f}")
print(f"  Corr (corrected):    {corr_c:.6f}")

# Plot
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

ax = axes[0]
ax.plot(r, I_debye, 'b-', lw=2.5, label='Debye (Gaussian)')
ax.plot(r, I_rw, 'r--', lw=2, label='RW (standard)')
ax.plot(r, I_rw_corr, 'g:', lw=2.5, label=f'RW (scaled by {scaling_needed:.4f})')
ax.set_xlabel('r (μm)')
ax.set_ylabel('Normalized Intensity')
ax.set_title(f'NA={NA}, α={alpha}')
ax.legend()
ax.grid(True, alpha=0.3)

ax = axes[1]
ax.plot(r, I_debye - I_rw, 'r-', lw=2, label='Debye - RW (standard)')
ax.plot(r, I_debye - I_rw_corr, 'g-', lw=2, label='Debye - RW (corrected)')
ax.axhline(0, color='k', ls='--', lw=1)
ax.set_xlabel('r (μm)')
ax.set_ylabel('Difference')
ax.set_title('Residuals')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('data/comprehensive_comparison/rw_correction_v3.png', dpi=200)
print(f"\n✓ Saved: data/comprehensive_comparison/rw_correction_v3.png")

# Analyze what this scaling factor is
print("\n" + "="*70)
print("ANALYZING THE SCALING FACTOR")
print("="*70)

# scaling = P * α_debye * R / (Z * v)
#         = (k*ws²/f) * ((aperture/2)/ws) * (r/ws) / (Z * k*sin(α)*r)
#         = ws² * (aperture/2) / (f * ws * Z * sin(α) * ws)
#         = (aperture/2) / (f * Z * sin(α))
#         = tan(α) / sin(α)  [since aperture/2 = f*tan(α)]
#         = 1 / cos(α)

print(f"  scaling = {scaling_needed:.6f}")
print(f"  1/cos(θ_max) = {1/np.cos(theta_max):.6f}")
print(f"  tan(θ)/sin(θ) = {np.tan(theta_max)/np.sin(theta_max):.6f}")

# But this should be 1/cos ≈ 1.005 for NA=0.1, not the value we computed...
# Let me recalculate

print(f"\nRecalculating:")
print(f"  P = {P:.6f}")
print(f"  alpha_debye = {alpha_debye:.6f}")
print(f"  ws = {ws:.6f}")
print(f"  aperture/2 = {debye.aperture/2:.6f}")
print(f"  f = {debye.f:.6f}")
print(f"  sin(θ_max) = {sin_alpha:.6f}")
print(f"  tan(θ_max) = {np.tan(theta_max):.6f}")
print(f"  (aperture/2)/f = {(debye.aperture/2)/debye.f:.6f}")

# The issue is that ws ≠ aperture/2 due to beam propagation from z=0 to z=z_lens
print(f"\n  ws / (aperture/2) = {ws / (debye.aperture/2):.6f}")
