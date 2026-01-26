"""
Find the exact correction to make Richards-Wolf (Gaussian) match Debye (Gaussian).

Key finding: The Bessel argument scaling differs by cos(θ_max):
- Debye uses tan(θ_max) ∝ aperture/f (Cartesian/paraxial)
- RW uses sin(θ_max) (spherical reference surface)

Ratio: sin(θ)/tan(θ) = cos(θ)
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

# Parameters
wavelength = 0.532
n_medium = 1.0
NA = 0.1
aperture_default = 1500.0
truncation_coeff = 2.0

theta_max = np.arcsin(NA / n_medium)
focal_length = (aperture_default / 2) / np.tan(theta_max)
k = 2 * np.pi / wavelength

print("="*70)
print("CORRECTING RICHARDS-WOLF TO MATCH DEBYE")
print("="*70)
print(f"NA = {NA}, θ_max = {np.degrees(theta_max):.4f}°")
print(f"cos(θ_max) = {np.cos(theta_max):.6f}")
print(f"sin(θ_max)/tan(θ_max) = {np.sin(theta_max)/np.tan(theta_max):.6f}")
print()

# Initialize Debye
debye = FocusedGaussianBeamTheory(
    numerical_aperture=NA,
    wavelength=wavelength,
    n_medium=n_medium,
    focal_length=focal_length,
    z_focus=0.0,
    truncation_coeff=truncation_coeff
)

sin_alpha = np.sin(theta_max)
cos_alpha = np.cos(theta_max)
tan_alpha = np.tan(theta_max)
sin2_alpha = sin_alpha ** 2

def compute_rw_intensity(r_array, use_tan_scaling=False):
    """
    Compute RW focal plane intensity.

    If use_tan_scaling=True, use tan(θ_max) instead of sin(θ_max) in Bessel argument.
    This should make it match Debye.
    """
    intensity = np.zeros_like(r_array)

    for i, r in enumerate(r_array):
        # Optical coordinate v
        if use_tan_scaling:
            # Corrected: use tan(θ_max) like Debye
            v = k * tan_alpha * r
        else:
            # Standard RW: use sin(θ_max)
            v = k * sin_alpha * r

        def I0_integrand(theta):
            if abs(np.sin(theta)) < 1e-15:
                return 0.0
            cos_t = np.cos(theta)
            sin_t = np.sin(theta)

            # Standard RW factors
            apod = np.sqrt(cos_t)
            geo = sin_t * (1 + cos_t)

            # Bessel argument - note: sin(θ)/sin(θ_max) = r0
            if use_tan_scaling:
                # Corrected scaling
                bessel = jv(0, v * sin_t / tan_alpha)
            else:
                # Standard RW
                bessel = jv(0, v * sin_t / sin_alpha)

            # Gaussian apodization
            field_apod = np.exp(-truncation_coeff * sin_t**2 / sin2_alpha)

            return apod * geo * bessel * field_apod

        I0, _ = integrate.quad(I0_integrand, 0, theta_max, limit=100)
        intensity[i] = np.abs(I0)**2

    return intensity / intensity.max()

def compute_fwhm(r, I):
    half_max = 0.5
    above_half = I > half_max
    if above_half.any():
        r_half = r[above_half]
        if len(r_half) > 0:
            return 2 * r_half[-1]
    return np.nan

# Radial grid
airy_r = 0.61 * wavelength / NA
r = np.linspace(0, 4 * airy_r, 100)

print("Computing intensity profiles...")

# Debye
I_debye = debye.focal_plane_intensity(r, z=0.0)
I_debye = I_debye / I_debye.max()

# Standard RW (sin scaling)
I_rw_sin = compute_rw_intensity(r, use_tan_scaling=False)

# Corrected RW (tan scaling)
I_rw_tan = compute_rw_intensity(r, use_tan_scaling=True)

fwhm_debye = compute_fwhm(r, I_debye)
fwhm_rw_sin = compute_fwhm(r, I_rw_sin)
fwhm_rw_tan = compute_fwhm(r, I_rw_tan)

print(f"\nFWHM Results:")
print(f"  Debye (Gaussian):        {fwhm_debye:.4f} μm")
print(f"  RW sin(θ) scaling:       {fwhm_rw_sin:.4f} μm (standard)")
print(f"  RW tan(θ) scaling:       {fwhm_rw_tan:.4f} μm (corrected)")

mse_sin = np.mean((I_debye - I_rw_sin)**2)
mse_tan = np.mean((I_debye - I_rw_tan)**2)
corr_sin = np.corrcoef(I_debye, I_rw_sin)[0,1]
corr_tan = np.corrcoef(I_debye, I_rw_tan)[0,1]

print(f"\nMSE vs Debye:")
print(f"  RW sin(θ) scaling:       {mse_sin:.6f}")
print(f"  RW tan(θ) scaling:       {mse_tan:.6f}")

print(f"\nCorrelation vs Debye:")
print(f"  RW sin(θ) scaling:       {corr_sin:.6f}")
print(f"  RW tan(θ) scaling:       {corr_tan:.6f}")

# Test at multiple NA values
print("\n" + "="*70)
print("TESTING CORRECTION ACROSS DIFFERENT NA VALUES")
print("="*70)

NA_test = [0.1, 0.3, 0.5, 0.7]

print(f"\n{'NA':>6} {'FWHM_Debye':>12} {'FWHM_RW_sin':>12} {'FWHM_RW_tan':>12} {'MSE_sin':>10} {'MSE_tan':>10}")
print("-"*70)

for NA in NA_test:
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

    # Update global variables for compute function
    sin_alpha = np.sin(theta_max)
    cos_alpha = np.cos(theta_max)
    tan_alpha = np.tan(theta_max)
    sin2_alpha = sin_alpha ** 2

    airy_r = 0.61 * wavelength / NA
    r = np.linspace(0, 3 * airy_r, 80)

    I_debye = debye.focal_plane_intensity(r, z=0.0)
    I_debye = I_debye / I_debye.max()

    # Need to redefine with current theta_max
    def compute_rw_local(r_array, use_tan):
        intensity = np.zeros_like(r_array)
        for i, r_val in enumerate(r_array):
            if use_tan:
                v = k * tan_alpha * r_val
            else:
                v = k * sin_alpha * r_val

            def integrand(theta):
                if abs(np.sin(theta)) < 1e-15:
                    return 0.0
                cos_t = np.cos(theta)
                sin_t = np.sin(theta)
                apod = np.sqrt(cos_t)
                geo = sin_t * (1 + cos_t)
                if use_tan:
                    bessel = jv(0, v * sin_t / tan_alpha)
                else:
                    bessel = jv(0, v * sin_t / sin_alpha)
                field_apod = np.exp(-truncation_coeff * sin_t**2 / sin2_alpha)
                return apod * geo * bessel * field_apod

            I0, _ = integrate.quad(integrand, 0, theta_max, limit=100)
            intensity[i] = np.abs(I0)**2
        return intensity / intensity.max()

    I_rw_sin = compute_rw_local(r, False)
    I_rw_tan = compute_rw_local(r, True)

    fwhm_d = compute_fwhm(r, I_debye)
    fwhm_sin = compute_fwhm(r, I_rw_sin)
    fwhm_tan = compute_fwhm(r, I_rw_tan)

    mse_sin = np.mean((I_debye - I_rw_sin)**2)
    mse_tan = np.mean((I_debye - I_rw_tan)**2)

    print(f"{NA:6.2f} {fwhm_d:12.4f} {fwhm_sin:12.4f} {fwhm_tan:12.4f} {mse_sin:10.6f} {mse_tan:10.6f}")

# Plot for NA = 0.1
print("\n" + "="*70)
print("Generating comparison plot...")

NA = 0.1
theta_max = np.arcsin(NA / n_medium)
focal_length = (aperture_default / 2) / np.tan(theta_max)
sin_alpha = np.sin(theta_max)
tan_alpha = np.tan(theta_max)
sin2_alpha = sin_alpha ** 2

debye = FocusedGaussianBeamTheory(
    numerical_aperture=NA, wavelength=wavelength, n_medium=n_medium,
    focal_length=focal_length, z_focus=0.0, truncation_coeff=truncation_coeff
)

airy_r = 0.61 * wavelength / NA
r = np.linspace(0, 4 * airy_r, 100)

I_debye = debye.focal_plane_intensity(r, z=0.0)
I_debye = I_debye / I_debye.max()

def compute_final(r_array, use_tan):
    intensity = np.zeros_like(r_array)
    for i, r_val in enumerate(r_array):
        v = k * (tan_alpha if use_tan else sin_alpha) * r_val
        def integrand(theta):
            if abs(np.sin(theta)) < 1e-15:
                return 0.0
            cos_t = np.cos(theta)
            sin_t = np.sin(theta)
            apod = np.sqrt(cos_t)
            geo = sin_t * (1 + cos_t)
            bessel = jv(0, v * sin_t / (tan_alpha if use_tan else sin_alpha))
            field_apod = np.exp(-truncation_coeff * sin_t**2 / sin2_alpha)
            return apod * geo * bessel * field_apod
        I0, _ = integrate.quad(integrand, 0, theta_max, limit=100)
        intensity[i] = np.abs(I0)**2
    return intensity / intensity.max()

I_rw_sin = compute_final(r, False)
I_rw_tan = compute_final(r, True)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

ax = axes[0]
ax.plot(r, I_debye, 'b-', lw=2.5, label='Debye (Gaussian)')
ax.plot(r, I_rw_sin, 'r--', lw=2, label='RW sin(θ) scaling (standard)')
ax.plot(r, I_rw_tan, 'g:', lw=2.5, label='RW tan(θ) scaling (corrected)')
ax.set_xlabel('r (μm)')
ax.set_ylabel('Normalized Intensity')
ax.set_title(f'Bessel Argument Scaling Correction (NA={NA}, α={truncation_coeff})')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_xlim([0, r.max()])

ax = axes[1]
ax.plot(r, I_debye - I_rw_sin, 'r-', lw=2, label='Debye - RW (sin)')
ax.plot(r, I_debye - I_rw_tan, 'g-', lw=2, label='Debye - RW (tan)')
ax.axhline(0, color='k', ls='--', lw=1)
ax.set_xlabel('r (μm)')
ax.set_ylabel('Intensity Difference')
ax.set_title('Residuals')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_xlim([0, r.max()])

plt.tight_layout()
plt.savefig('data/comprehensive_comparison/rw_correction_bessel.png', dpi=200)
print(f"✓ Saved: data/comprehensive_comparison/rw_correction_bessel.png")

print("\n" + "="*70)
print("CONCLUSION")
print("="*70)
print("""
The correction needed in Richards-Wolf to match Debye:

In the Bessel function argument, replace sin(θ_max) with tan(θ_max):

CURRENT (richards_wolf.py):
  v = k * sin(α) * r
  bessel = J0(v * sin(θ) / sin(α))

CORRECTED:
  v = k * tan(α) * r
  bessel = J0(v * sin(θ) / tan(α))

Or equivalently, multiply the Bessel argument by 1/cos(θ_max).

This accounts for the difference between:
- Debye: Cartesian aperture coordinates (r = f * tan(θ))
- RW: Spherical reference surface (r relates to f * sin(θ))
""")
