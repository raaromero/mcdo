# Monte Carlo Implementation Comparison: mcdo vs gbp-mc

## Key Architectural Differences

### **mcdo** (monte_carlo/core.py - ApertureSimulator)
**Approach:** "Endpoint-focused" Monte Carlo
- **Philosophy:** Sample photons directly at start and end points
- **What it does:**
  1. Sample photons uniformly from circular aperture (z=0)
  2. Sample photons at focal plane using **rejection sampling** based on Airy pattern intensity
  3. Connect the dots: calculate direction vectors from aperture → focal plane
  4. Result: positions and directions at two planes

**Key characteristics:**
- ✅ Simple, fast for single-plane analysis
- ✅ Accurate for low NA (Airy disk approximation)
- ❌ No intermediate ray tracking
- ❌ No scattering simulation
- ❌ Uniform field only (originally)

### **gbp-mc** (gaussian_beam_propagation.py - FocusedGaussianBeamMC)
**Approach:** "Ray tracing" Monte Carlo
- **Philosophy:** Track full photon trajectories through space
- **What it does:**
  1. Sample photons from Gaussian distribution at lens (or collimated beam)
  2. Calculate direction vectors pointing to focal targets
  3. **Propagate step-by-step** through multiple z-planes (num_steps parameter)
  4. Optional: account for wavefront curvature at each step
  5. Optional: handle scattering events with scattering medium
  6. Result: full 3D trajectories (x, y, z at each step)

**Key characteristics:**
- ✅ Full ray tracing with intermediate positions
- ✅ Gaussian beam physics (beam waist w0, Rayleigh range z_R)
- ✅ Wavefront curvature correction option
- ✅ Can integrate scattering (Henyey-Greenstein, Mie scattering)
- ✅ Supports both Gaussian and uniform fields
- ⚠️ More computationally expensive (tracks all steps)

---

## Detailed Feature Comparison

| Feature | mcdo (ApertureSimulator) | gbp-mc (FocusedGaussianBeamMC) |
|---------|--------------------------|--------------------------------|
| **Initial field** | Uniform circular aperture | Gaussian or uniform at lens |
| **Focal plane** | Airy pattern (low NA) | Gaussian beam focus |
| **Propagation** | Direct aperture→focal | Multi-step ray tracing |
| **Ray tracking** | Start + end only | Full trajectory (num_steps) |
| **Wavefront curvature** | ❌ Not modeled | ✅ Optional (curvature_correction) |
| **Scattering** | ❌ Not implemented | ✅ Via scatterer.py & ray_scatter.py |
| **Physics model** | Paraxial/low NA | Full Gaussian beam (w(z), R(z), z_R) |
| **Output** | Positions at 2 planes | Full 3D trajectory arrays |
| **Speed** | Fast | Slower (more steps) |
| **Use case** | Quick focal plane analysis | Detailed beam propagation + scattering |

---

## Code Structure Comparison

### mcdo: Simplified flow
```python
# 1. Sample aperture (uniform)
x_ap, y_ap, z_ap = sample_aperture()  # Uniform in circle

# 2. Sample focal plane (rejection sampling from Airy)
x_focal, y_focal = sample_focal_plane_position()  # Airy pattern

# 3. Calculate directions
dx = x_focal - x_ap
dy = y_focal - y_ap
dz = z_focal - z_ap
# normalize...

# Result: two sets of positions
```

### gbp-mc: Full ray tracing
```python
# 1. Sample lens (Gaussian or uniform)
r[:,:,0] = init_collimated(some_photons)  # Gaussian distribution

# 2. Sample focal targets (Gaussian)
at_focus_x = np.random.normal(scale=w0/2, size=some_photons)
at_focus_y = np.random.normal(scale=w0/2, size=some_photons)

# 3. Multi-step propagation loop
for step in range(0, num_steps-1):
    # Calculate direction to focus
    mu[:,:,step], s = update_in_free_space(r[:,:,step], at_focus_x, at_focus_y)

    # Optional: apply curvature correction
    if curvature_correction:
        ddr = ddR(r)  # Gradient of beam phase
        s = adaptive_step_size(ddr)

    # Move photons
    r[:,:,step+1] = move(r[:,:,step], mu[:,:,step], s)

    # Optional: check for scattering events
    # scattering logic here...

# Result: full trajectory r[3, n_photons, num_steps]
```

---

## Gaussian Beam Physics (gbp-mc only)

**gbp-mc implements full Gaussian beam equations:**

1. **Beam waist:** w₀ = (2/π) × (λf/D) for truncated beam
2. **Rayleigh range:** z_R = π w₀²/λ
3. **Beam radius:** w(z) = w₀ √(1 + ((z-z_f)/z_R)²)
4. **Radius of curvature:** R(z) = -(z-z_f) × (1 + (z_R/(z-z_f))²)
5. **Wavefront curvature factor:** T(z) = 1/R(z)

**Curvature correction:**
- Calculates ddR (phase gradient) at each step
- Adjusts step size based on local beam curvature
- More accurate for high NA or near focus

---

## Scattering Capabilities (gbp-mc only)

**gbp-mc/src/core/ includes:**
- **ray_scatter.py:** Henyey-Greenstein phase function for scattering angles
- **scatterer.py:** ScatteringMedium class with Mie scattering
  - Particle distribution in 3D volume
  - Mie phase function for particle scattering
  - Intersection detection with particles
  - Anisotropy factor g

**mcdo:** No scattering currently implemented

---

## Summary: What to Use When?

### Use **mcdo** when:
- You only need focal plane intensity distribution
- Low NA systems (Airy disk valid)
- Fast prototyping
- Uniform illumination

### Use **gbp-mc** when:
- You need full ray trajectories
- High NA or Gaussian beams
- Scattering simulations (tissue, turbid media)
- Wavefront curvature matters
- Multi-step propagation analysis

### Hybrid approach (current integration):
- Start with **gbp-mc** Gaussian field initialization
- Add **mcdo** simplicity for non-scattering cases
- Build up to full **gbp-mc** capabilities as needed
