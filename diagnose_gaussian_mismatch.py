"""
Diagnose the Gaussian parameterization mismatch between Debye and Richards-Wolf.
"""

import sys
sys.path.insert(0, '.')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from monte_carlo.richards_wolf import RichardsWolfSimulator
from monte_carlo.gaussian_beam_theory import FocusedGaussianBeamTheory

# Fixed parameters
wavelength = 0.532
n_medium = 1.0
NA = 0.1  # Low NA where they should agree
aperture_default = 1500.0

theta_max = np.arcsin(NA / n_medium)
focal_length = (aperture_default / 2) / np.tan(theta_max)

print("="*70)
print("DIAGNOSING GAUSSIAN PARAMETERIZATION MISMATCH")
print("="*70)
print(f"NA = {NA}, wavelength = {wavelength} μm")
print(f"Aperture = {aperture_default} μm, focal_length = {focal_length:.2f} μm")
print(f"theta_max = {np.degrees(theta_max):.4f}°")
print()

# Test truncation coefficients
truncation_coeffs = [1.1, 2.0, 2.778, 4.0, 6.25]

print("="*70)
print("RICHARDS-WOLF: Aperture-plane Gaussian profile")
print("  A(θ) = exp(-α * sin²(θ)/sin²(θ_max))")
print("  At edge (θ=θ_max): A = exp(-α)")
print("="*70)

for alpha in truncation_coeffs:
    edge_amplitude_rw = np.exp(-alpha)
    print(f"  α = {alpha:.3f}: edge amplitude = {edge_amplitude_rw:.6f}")

print()
print("="*70)
print("DEBYE (FocusedGaussianBeamTheory): Internal parameters")
print("="*70)

for alpha in truncation_coeffs:
    debye = FocusedGaussianBeamTheory(
        numerical_aperture=NA,
        wavelength=wavelength,
        n_medium=n_medium,
        focal_length=focal_length,
        z_focus=0.0,
        truncation_coeff=alpha
    )

    params = debye.get_parameters()

    # Compute what alpha is actually used in the integral
    ws = debye.beam_radius(z=debye.z_lens)
    alpha_internal = (debye.aperture / 2) / ws
    eps = debye.epsilon(z=debye.z_lens)

    # The Gaussian in the integrand is: exp(-alpha_internal² * r0² / (1 + eps²))
    # At r0 = 1 (aperture edge): exp(-alpha_internal² / (1 + eps²))
    edge_amplitude_debye = np.exp(-alpha_internal**2 / (1 + eps**2))

    print(f"\n  α (input) = {alpha:.3f}:")
    print(f"    w_incident = {params['w_incident']:.4f} μm")
    print(f"    w0 = {params['w0']:.4f} μm")
    print(f"    z_R = {params['z_R']:.4f} μm")
    print(f"    ws (at lens) = {ws:.4f} μm")
    print(f"    alpha_internal = {alpha_internal:.4f}")
    print(f"    epsilon = {eps:.6f}")
    print(f"    edge amplitude = {edge_amplitude_debye:.6f}")
    print(f"    alpha_internal² / (1+eps²) = {alpha_internal**2 / (1 + eps**2):.4f}")

print()
print("="*70)
print("COMPARISON: What α_RW gives same edge amplitude as Debye?")
print("="*70)

print(f"\n{'α_input':>8} {'α_RW_equiv':>12} {'edge_Debye':>12} {'edge_RW':>12} {'match?':>8}")
print("-"*56)

for alpha in truncation_coeffs:
    debye = FocusedGaussianBeamTheory(
        numerical_aperture=NA,
        wavelength=wavelength,
        n_medium=n_medium,
        focal_length=focal_length,
        z_focus=0.0,
        truncation_coeff=alpha
    )

    ws = debye.beam_radius(z=debye.z_lens)
    alpha_internal = (debye.aperture / 2) / ws
    eps = debye.epsilon(z=debye.z_lens)

    # Debye edge amplitude
    edge_debye = np.exp(-alpha_internal**2 / (1 + eps**2))

    # What α_RW would give same edge amplitude?
    # exp(-α_RW) = edge_debye
    # α_RW = -ln(edge_debye)
    alpha_rw_equiv = -np.log(edge_debye)

    # RW edge amplitude with input alpha
    edge_rw = np.exp(-alpha)

    match = "✓" if abs(alpha - alpha_rw_equiv) < 0.01 else "✗"

    print(f"{alpha:8.3f} {alpha_rw_equiv:12.4f} {edge_debye:12.6f} {edge_rw:12.6f} {match:>8}")

print()
print("="*70)
print("FORMULA DERIVATION")
print("="*70)
print("""
For Debye and RW to match, we need:
  Debye: exp(-alpha_internal² / (1 + eps²))
  RW:    exp(-α)

So: α = alpha_internal² / (1 + eps²)

Where:
  alpha_internal = (aperture/2) / ws
  ws = beam_radius(z_lens)
  eps = 2*(z_lens - z_f) / (k * ws²) = -2*f / (k * ws²)

For low NA (paraxial), eps → 0, so:
  α ≈ alpha_internal² = ((aperture/2) / ws)²
""")

# Now let's derive what truncation_coeff should be passed to Debye
# to get equivalent behavior to RW with a given α_RW

print()
print("="*70)
print("SOLUTION: Map RW α to Debye truncation_coeff")
print("="*70)

# The issue is that Debye computes w_incident differently for α < 4 vs α >= 4
# Let's trace through the math more carefully

for alpha_rw in truncation_coeffs:
    print(f"\nTarget: RW with α = {alpha_rw}")
    print(f"  RW edge amplitude = exp(-{alpha_rw}) = {np.exp(-alpha_rw):.6f}")

    # For RW: A(θ) = exp(-α * sin²(θ)/sin²(θ_max))
    # In normalized aperture coords (ρ = r/r_aperture = sin(θ)/sin(θ_max)):
    # A(ρ) = exp(-α * ρ²)

    # For Debye with truncation_coeff >= 4:
    #   w_incident = (aperture/2) / sqrt(truncation_coeff)
    #   Gaussian: A(r) = exp(-r²/w_incident²) = exp(-(r/(aperture/2))² * truncation_coeff)
    #   In normalized coords: A(ρ) = exp(-truncation_coeff * ρ²)
    # This matches RW if truncation_coeff = α_RW!

    # For Debye with truncation_coeff < 4:
    #   w_incident = aperture / sqrt(truncation_coeff)  -- NOTE: aperture, not aperture/2!
    #   Gaussian: A(r) = exp(-r²/w_incident²) = exp(-(r/aperture)² * truncation_coeff)
    #   In normalized coords (ρ = r/(aperture/2)):
    #     A(ρ) = exp(-((ρ*(aperture/2))/aperture)² * truncation_coeff)
    #          = exp(-(ρ/2)² * truncation_coeff)
    #          = exp(-truncation_coeff * ρ² / 4)
    # This means effective α = truncation_coeff / 4

    if alpha_rw >= 4:
        print(f"  → Use Debye truncation_coeff = {alpha_rw} (direct, >= 4 formula)")
    else:
        # For α_RW < 4, we need truncation_coeff/4 = α_RW
        # But that would require truncation_coeff = 4*α_RW >= 4, switching formulas!
        # This is the problem - the formulas are inconsistent
        needed_tc = 4 * alpha_rw
        print(f"  → Problem! Would need truncation_coeff = {needed_tc:.2f} to get α_eff = {alpha_rw}")
        print(f"     But {needed_tc:.2f} >= 4 uses different formula!")

print()
print("="*70)
print("CONCLUSION")
print("="*70)
print("""
The Debye implementation has inconsistent Gaussian parameterization:

For truncation_coeff >= 4:
  w_incident = (aperture/2) / sqrt(truncation_coeff)
  → Effective α = truncation_coeff  ✓ matches RW

For truncation_coeff < 4:
  w_incident = aperture / sqrt(truncation_coeff)
  → Effective α = truncation_coeff / 4  ✗ factor of 4 off!

FIX: Change line 85 in gaussian_beam_theory.py from:
  self.w_incident = self.aperture / np.sqrt(truncation_coeff)
to:
  self.w_incident = (self.aperture / 2) / np.sqrt(truncation_coeff)
""")
