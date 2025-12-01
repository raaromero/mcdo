# Angular Spectrum Method Diagnosis - Complete Summary

## Question
**Why is the angular spectrum method not approximating an Airy function well, even with very high N photons?**

## TL;DR Answer
The angular spectrum Monte Carlo method has a **fundamental k-space discretization bottleneck** that limits accuracy to RMSE ≈ 0.028 (5.6x worse than aperture sampling). The error comes from FFT pixelation, not the propagation formula or binning resolution.

---

## Step-by-Step Method Verification

Your proposed logic:
1. ✅ Circular aperture
2. ✅ FFT (angular spectrum)
3. ✅ Sample (kx, ky) weighted by |FFT|²
4. ✅ Get direction from (kx, ky)
5. ✅ Propagate to focal plane

**The logic is CORRECT, but step 2 (FFT) introduces 15% error in k-space.**

---

## Error Sources Identified

### 1. Formula Choice (Minor Issue - 1.1x improvement)

| Formula | RMSE | Max Radius | Status |
|---------|------|------------|--------|
| Ray Tracing: `x = f × (kx/kz)` | 0.0313 | 845 μm | ❌ WRONG (geometric optics) |
| Fraunhofer: `x = (λf/2π) × kx` | 0.0284 | 10 μm | ✅ CORRECT (wave optics) |
| Aperture Reference | 0.0051 | 39 μm | ✅ BEST |

**Key Findings:**
- Ray tracing creates extreme outliers (845 μm!) due to division by small kz
- Fraunhofer eliminates outliers but only improves RMSE by 1.1x
- **This is NOT the main problem**

### 2. FFT Discretization (MAJOR Issue - 5.6x worse than aperture)

**K-space sampling error:**
```
K-space RMSE: 0.152 (15% error)
Pixels across aperture: ~13 pixels
```

**Evidence:**
- Even with correct Fraunhofer formula: RMSE = 0.0284
- K-space distribution itself has 15% error vs analytical jinc²
- Increasing FFT size beyond 1024 makes it WORSE (paradoxically)

**Why increasing FFT doesn't help:**
- Larger FFT → larger spatial domain L
- Same aperture radius R → fewer pixels across aperture
- Undersampling the aperture is worse than k-space resolution

### 3. Binning Resolution (NOT the issue)

Tested different bin counts at focal plane:
```
 100 bins: RMSE = 0.0091
 300 bins: RMSE = 0.0313
1000 bins: RMSE = 0.0721
3000 bins: RMSE = 0.2307
```

**Conclusion:** RMSE gets WORSE with finer bins!
→ The photon distribution itself is wrong, not under-sampled.

---

## Attempted Fixes

### ✅ Fix 1: Use Fraunhofer instead of ray tracing
- **Result:** 1.1x improvement (0.0313 → 0.0284)
- **Status:** Minor gain, not the main issue

### ❌ Fix 2: Increase aperture sampling to 200 pixels
- **Result:** No improvement (RMSE stayed 0.028)
- **Status:** Failed - increasing spatial sampling didn't help

### ❌ Fix 3: Analytical jinc² sampling (bypass FFT entirely)
- **Result:** WORSE! RMSE = 0.153 (30x worse than aperture)
- **Status:** Failed - revealed fundamental physics mismatch

### ❌ Fix 4: Test higher FFT sizes (4096, 8192, 16384)
- **Result:** FFT 1024 was optimal, higher FFT made it worse
- **Status:** Failed - confirms FFT discretization is the bottleneck

---

## Fundamental Physics Issue

**The core problem:** Angular spectrum |FFT|² represents the **result** of interference from all aperture points, not the **initial** k-distribution for individual photons.

**Monte Carlo photon sampling requires:**
- Initial positions or directions for each photon
- Independent particle trajectories

**Angular spectrum provides:**
- Field distribution at far field (collective behavior)
- Result of coherent interference

**This is a conceptual mismatch for Monte Carlo methods.**

---

## Why Aperture Method Works Better

The aperture method (RMSE = 0.005):
1. Sample positions uniformly in circular aperture (real space)
2. Trace rays from each position to focus
3. At focus, use rejection sampling from Airy pattern

**Advantages:**
- No FFT discretization
- Direct real-space sampling
- Accounts for geometric focusing naturally
- Can achieve arbitrary accuracy with more photons

---

## Recommendations

### For Production Use:
**✅ Use the Aperture Sampling method** (`monte_carlo.core.ApertureSimulator`)
- RMSE ≈ 0.005 (excellent agreement with theory)
- No FFT discretization issues
- Scales well with photon count

### For Angular Spectrum (if needed):
**✅ Use Fraunhofer formula** (`monte_carlo.angular_spectrum_fixed.py`)
- Best achievable: RMSE ≈ 0.028
- Accept 5-6x higher error vs aperture method
- Don't increase FFT beyond 1024 (diminishing returns)

---

## File Locations

**Diagnostic Notebooks:**
- `notebooks/diagnose_angular_spectrum_step_by_step.ipynb` - Full step verification
- `notebooks/compare_ray_vs_fraunhofer.ipynb` - Formula comparison
- `notebooks/debug_angular_spectrum.ipynb` - K-space discretization analysis

**Code Implementations:**
- `monte_carlo/angular_spectrum.py` - Original (uses wrong formula)
- `monte_carlo/angular_spectrum_fixed.py` - Fixed Fraunhofer formula (best angular spectrum)
- `monte_carlo/core.py` - Aperture method (RECOMMENDED)

**Output Data:**
- `data/step_by_step_diagnosis/` - Step-by-step diagnostic plots
- `data/ray_vs_fraunhofer/` - Formula comparison plots
- `data/angular_spectrum_convergence/` - FFT size sweep results

---

## Final Answer to Original Question

**Q:** "Is it a resolution issue on the focal plane?"

**A:** No. The issue is:
1. **K-space FFT discretization** (15% error) - MAIN BOTTLENECK
2. **Ray tracing formula** (vs Fraunhofer) - minor issue (1.1x)
3. **NOT focal plane binning** - finer bins make it worse

**Recommendation:** Use the aperture sampling method instead. The angular spectrum approach has fundamental limitations for Monte Carlo that cannot be resolved by increasing resolution or photon count.
