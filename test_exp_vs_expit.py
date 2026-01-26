"""
Empirical test: exp vs expit in Debye formula.

Compare both versions against:
1. Richards-Wolf (well-established vector diffraction theory)
2. Known theoretical limits (Airy pattern for uniform illumination)
"""

import sys
sys.path.insert(0, '.')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.special import jv, expit
from scipy import integrate

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

def debye_intensity(r_array, NA, trunc_coeff, use_exp=True):
    """Debye/Tanaka intensity with exp or expit."""
    theta_max = np.arcsin(NA / n_medium)
    f = (aperture_default / 2) / np.tan(theta_max)

    # Beam parameters (using corrected formula)
    w_incident = (aperture_default / 2) / np.sqrt(trunc_coeff)
    Nw = w_incident**2 / (wavelength * f)
    w0 = w_incident / np.sqrt(1 + (np.pi * Nw)**2)
    z_R = np.pi * w0**2 / wavelength

    z_lens = -f
    z_f = 0
    ws = w0 * np.sqrt(1 + ((z_lens - z_f) / z_R)**2)

    alpha = (aperture_default / 2) / ws
    eps = 2 * (z_lens - z_f) / (k * ws**2)
    P = k * ws**2 / f
    Z = 1.0  # focal plane

    s1 = (P * alpha**2 * (1 - Z) / (2 * Z)) + (alpha**2 * eps / (1 + eps**2))
    s2 = -alpha**2 / (1 + eps**2)

    intensity = np.zeros_like(r_array)

    for i, r in enumerate(r_array):
        R = r / ws

        def f1_integrand(r0):
            bessel_arg = P * alpha * R / Z * r0
            if use_exp:
                gauss = np.exp(-alpha**2 * r0**2 / (1 + eps**2))
            else:
                gauss = expit(-alpha**2 * r0**2 / (1 + eps**2))
            return r0 * jv(0, bessel_arg) * gauss * np.cos(s1 * r0**2)

        def f2_integrand(r0):
            bessel_arg = P * alpha * R / Z * r0
            if use_exp:
                gauss = np.exp(-alpha**2 * r0**2 / (1 + eps**2))
            else:
                gauss = expit(-alpha**2 * r0**2 / (1 + eps**2))
            return r0 * jv(0, bessel_arg) * gauss * np.sin(s1 * r0**2)

        firstterm, _ = integrate.quad(f1_integrand, 0, 1, limit=100)
        secondterm, _ = integrate.quad(f2_integrand, 0, 1, limit=100)

        intensity[i] = firstterm**2 + secondterm**2

    return intensity / intensity.max()

def rw_intensity(r_array, NA, trunc_coeff):
    """Richards-Wolf vector diffraction."""
    theta_max = np.arcsin(NA / n_medium)
    sin_alpha = np.sin(theta_max)
    sin2_alpha = sin_alpha ** 2

    intensity = np.zeros_like(r_array)

    for i, r in enumerate(r_array):
        v = k * sin_alpha * r

        def I0_integrand(theta):
            if abs(np.sin(theta)) < 1e-15:
                return 0.0
            cos_t = np.cos(theta)
            sin_t = np.sin(theta)
            apod = np.sqrt(cos_t)
            geo = sin_t * (1 + cos_t)
            bessel = jv(0, v * sin_t / sin_alpha)
            field_apod = np.exp(-trunc_coeff * sin_t**2 / sin2_alpha)
            return apod * geo * bessel * field_apod

        I0, _ = integrate.quad(I0_integrand, 0, theta_max, limit=100)
        intensity[i] = np.abs(I0)**2

    return intensity / intensity.max()

def airy_pattern(r_array, NA):
    """Theoretical Airy pattern for uniform illumination."""
    airy_r = 0.61 * wavelength / NA
    x = r_array / airy_r * 1.22 * np.pi  # Scale to first zero at r = airy_r

    intensity = np.ones_like(r_array)
    nonzero = x > 0
    intensity[nonzero] = (2 * jv(1, x[nonzero]) / x[nonzero])**2
    return intensity

print("="*70)
print("EMPIRICAL TEST: exp vs expit")
print("="*70)

# Test 1: Compare FWHM across NA values for Gaussian beam (α=2)
print("\nTest 1: FWHM comparison (Gaussian beam, α=2)")
print("-"*70)
print(f"{'NA':>6} {'Debye(exp)':>12} {'Debye(expit)':>12} {'RW':>12} {'exp-RW':>10} {'expit-RW':>10}")
print("-"*70)

alpha = 2.0
for NA in [0.1, 0.2, 0.3, 0.5, 0.7]:
    airy_r = 0.61 * wavelength / NA
    r = np.linspace(0, 3 * airy_r, 80)

    I_exp = debye_intensity(r, NA, alpha, use_exp=True)
    I_expit = debye_intensity(r, NA, alpha, use_exp=False)
    I_rw = rw_intensity(r, NA, alpha)

    fwhm_exp = compute_fwhm(r, I_exp)
    fwhm_expit = compute_fwhm(r, I_expit)
    fwhm_rw = compute_fwhm(r, I_rw)

    diff_exp = abs(fwhm_exp - fwhm_rw)
    diff_expit = abs(fwhm_expit - fwhm_rw)

    print(f"{NA:6.2f} {fwhm_exp:12.4f} {fwhm_expit:12.4f} {fwhm_rw:12.4f} {diff_exp:10.4f} {diff_expit:10.4f}")

# Test 2: Uniform illumination (α→0) should approach Airy pattern
print("\n" + "="*70)
print("Test 2: Uniform illumination limit (α=0.01, should approach Airy)")
print("-"*70)
print(f"{'NA':>6} {'Debye(exp)':>12} {'Debye(expit)':>12} {'Airy':>12} {'exp-Airy':>10} {'expit-Airy':>10}")
print("-"*70)

alpha = 0.01  # Nearly uniform
for NA in [0.1, 0.3, 0.5]:
    airy_r = 0.61 * wavelength / NA
    r = np.linspace(0, 3 * airy_r, 80)

    I_exp = debye_intensity(r, NA, alpha, use_exp=True)
    I_expit = debye_intensity(r, NA, alpha, use_exp=False)
    I_airy = airy_pattern(r, NA)

    fwhm_exp = compute_fwhm(r, I_exp)
    fwhm_expit = compute_fwhm(r, I_expit)
    fwhm_airy = compute_fwhm(r, I_airy)

    diff_exp = abs(fwhm_exp - fwhm_airy)
    diff_expit = abs(fwhm_expit - fwhm_airy)

    print(f"{NA:6.2f} {fwhm_exp:12.4f} {fwhm_expit:12.4f} {fwhm_airy:12.4f} {diff_exp:10.4f} {diff_expit:10.4f}")

# Test 3: MSE comparison
print("\n" + "="*70)
print("Test 3: MSE vs Richards-Wolf (α=2)")
print("-"*70)
print(f"{'NA':>6} {'MSE(exp)':>12} {'MSE(expit)':>12} {'Winner':>10}")
print("-"*70)

alpha = 2.0
exp_wins = 0
expit_wins = 0

for NA in [0.1, 0.2, 0.3, 0.4, 0.5]:
    airy_r = 0.61 * wavelength / NA
    r = np.linspace(0, 3 * airy_r, 80)

    I_exp = debye_intensity(r, NA, alpha, use_exp=True)
    I_expit = debye_intensity(r, NA, alpha, use_exp=False)
    I_rw = rw_intensity(r, NA, alpha)

    mse_exp = np.mean((I_exp - I_rw)**2)
    mse_expit = np.mean((I_expit - I_rw)**2)

    if mse_exp < mse_expit:
        winner = "exp"
        exp_wins += 1
    else:
        winner = "expit"
        expit_wins += 1

    print(f"{NA:6.2f} {mse_exp:12.6f} {mse_expit:12.6f} {winner:>10}")

print("-"*70)
print(f"Summary: exp wins {exp_wins}, expit wins {expit_wins}")

# Plot comparison at NA=0.1
print("\n" + "="*70)
print("Generating comparison plots...")

NA = 0.1
alpha = 2.0
airy_r = 0.61 * wavelength / NA
r = np.linspace(0, 4 * airy_r, 100)

I_exp = debye_intensity(r, NA, alpha, use_exp=True)
I_expit = debye_intensity(r, NA, alpha, use_exp=False)
I_rw = rw_intensity(r, NA, alpha)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

ax = axes[0]
ax.plot(r, I_rw, 'b-', lw=2.5, label='Richards-Wolf')
ax.plot(r, I_exp, 'g--', lw=2, label='Debye (exp)')
ax.plot(r, I_expit, 'r:', lw=2, label='Debye (expit)')
ax.set_xlabel('r (μm)')
ax.set_ylabel('Normalized Intensity')
ax.set_title(f'NA={NA}, α={alpha}')
ax.legend()
ax.grid(True, alpha=0.3)

ax = axes[1]
ax.plot(r, I_rw - I_exp, 'g-', lw=2, label='RW - Debye(exp)')
ax.plot(r, I_rw - I_expit, 'r-', lw=2, label='RW - Debye(expit)')
ax.axhline(0, color='k', ls='--', lw=1)
ax.set_xlabel('r (μm)')
ax.set_ylabel('Difference')
ax.set_title('Residuals vs Richards-Wolf')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('data/comprehensive_comparison/exp_vs_expit.png', dpi=200)
print(f"✓ Saved: data/comprehensive_comparison/exp_vs_expit.png")

print("\n" + "="*70)
print("CONCLUSION")
print("="*70)
