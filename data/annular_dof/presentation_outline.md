# Progress Report: Gaussian Truncation Parameter & Depth of Field

---

## Slide 1: Title

**Richards-Wolf Diffraction: Gaussian Beam Truncation & Depth of Field**

- Progress report on vectorial diffraction simulations
- Two topics: α truncation parameter, DOF for annular apertures

---

## Slide 2: Summary

**Alpha Sweep Study:**
- Goal: Find when Gaussian illumination ≈ uniform
- α = (r_aperture / w_beam)² controls truncation
- Result: **α ≤ 0.25 gives <1% difference from uniform**

**Depth of Field Study:**
- DOF = axial FWHM of focused intensity
- Annular apertures extend DOF by 1/(1−ε²)
- High NA (>0.5) requires vectorial treatment (−37% vs paraxial)
- Validation: Uniform + Low NA matches theory within 3%

---

## Slide 3: Alpha Sweep Study - Background

**Question:** When does Gaussian illumination behave like uniform?

**Why it matters:**
- Theory often assumes uniform illumination
- Experiments often use Gaussian beams
- Need to know when they're equivalent

**Truncation coefficient α** ():

Definition:
```latex
\alpha = \left( \frac{r_{\text{aperture}}}{w_{\text{beam}}} \right)^2
```

Gaussian amplitude across aperture (ρ = r/r_aperture):
```latex
A(\rho) = \exp(-\alpha \rho^2)
```

Edge amplitude (at aperture edge, ρ = 1):
```latex
A_{\text{edge}} = \exp(-\alpha)
```

**Variable definitions:**
- α: truncation coefficient
- r_aperture: aperture radius
- w_beam: Gaussian beam waist (1/e² radius)
- ρ = r / r_aperture: normalized radial position

**Physical meaning:**
- α → 0: beam much wider than aperture → uniform illumination
- α = 1: beam waist equals aperture radius → 37% at edge
- α ≥ 4: beam narrower than aperture → "untruncated" Gaussian (2% at edge)

**Figure:** `alpha_sweep/edge_amplitude_vs_alpha_annotated.png`
- x-axis: α (0 to 8), y-axis: edge amplitude exp(−α)
- Green region: α ≤ 0.25 (≈ uniform)
- Red region: α ≥ 4 ("untruncated" Gaussian)

---

## Slide 4: Alpha Sweep Results

**Method:** Compare focal intensity profiles via RMS difference

**Results:**
| α | RMS difference |
|---|----------------|
| 0.001 | 0.002% |
| 0.01 | 0.02% |
| 0.1 | 0.22% |
| 0.25 | 0.56% |
| 0.5 | 1.15% |

**Conclusion: α ≤ 0.25 is effectively uniform (<1%)**

**Figure:** `alpha_sweep/rms_convergence_vs_alpha.png`

---

## Slide 5: Alpha Sweep - Focal Profile Comparison

**Key Points:**
- Direct comparison: `input_field='uniform'` vs `input_field='gaussian'`
- At α = 0.1: profiles nearly identical
- At α = 4.0: Gaussian has broader profile, +47-109% larger DOF

**Figure:** `alpha_sweep/uniform_vs_gaussian_comparison.png`

---

## Slide 6: What is Depth of Field (DOF)?

**Key Points:**
- DOF = axial range where intensity ≥ 50% of peak
- Measures how "long" the focal region extends
- Trade-off: larger DOF → lower peak intensity

**Figure:** `contours/contour_NA0.9_gaussian_a4.0_circular.png`
- Point to z-extent of 0.50 contour

---

## Slide 7: How DOF is Computed

**Simulation (Richards-Wolf):**
- Compute on-axis intensity I(r=0, z)
- Annular apertures: Babinet's principle
```latex
E_{\text{annular}} = E_{\text{outer}} - E_{\text{inner}}
```
- Measure FWHM where I ≥ 0.5 × I_max

**Theory (Paraxial):**

Axial intensity for circular aperture:
```latex
I(z) = \mathrm{sinc}^2 \left( \frac{\pi z}{2} \right)
```

DOF for circular aperture:
```latex
\mathrm{DOF}_{\mathrm{circular}} \approx 1.77 \times \frac{\lambda}{\mathrm{NA}^2}
```

DOF for annular aperture:
```latex
\mathrm{DOF}_{\mathrm{annular}} \approx \frac{\mathrm{DOF}_{\mathrm{circular}}}{1 - \varepsilon^2}
```

**Variable definitions:**
- z: axial position (in units of λ/NA²)
- λ: wavelength (e.g., 0.532 μm)
- NA: numerical aperture
- ε = NA_inner / NA_outer: obstruction ratio
- λ/NA² has units of length (μm); e.g., NA=0.9, λ=0.532 μm → λ/NA² = 0.66 μm

**Sources:**
- sinc² axial intensity: Born & Wolf, *Principles of Optics*, 7th ed., §8.8.1
- DOF ≈ 1.77 × λ/NA²: FWHM of sinc²; Sheppard & Török, J. Microsc. 185:366 (1997)
- DOF_annular = DOF/(1−ε²): Sheppard, Optik 48:329 (1977)

**Figure:** None (text slide)

---

## Slide 8: Validation - Uniform + Low NA Matches Theory

**Key Points:**
- Low NA (0.1): simulation = 1.71, theory = 1.77 (3% error)
- Validates Richards-Wolf implementation
- Paraxial theory works at low NA

**Figure:** `uniform_dof_test.png`

---

## Slide 9: High NA - Vectorial Effects

**Key Points:**
- High NA (0.9): simulation 37% smaller than theory
- Vectorial effects compress focal region
- Paraxial theory breaks down at NA > 0.5

**Figure:** `uniform_dof_test.png` (compare both NA panels)

---

## Slide 10: Annular Apertures Extend DOF

**Key Points:**
- Theory: DOF ratio = 1/(1−ε²)
- ε = 0.9 → 5× enhancement
- ε = 0.99 → 50× enhancement

**Figure:** `dof_vs_epsilon_comparison.png`

---

## Slide 11: Contours - High NA Uniform (ε = 0 vs 0.5 vs 0.99)

**Key Points:**
- ε = 0 (circular): compact focal spot
- ε = 0.5: moderate DOF extension
- ε = 0.99: dramatically extended along z
- Orange contour = 0.5 level (DOF boundary)

**Figures (one per sub-slide):**
- `contours/contour_NA0.9_uniform_circular.png`
- `contours/contour_NA0.9_uniform_eps0.5.png`
- `contours/contour_NA0.9_uniform_eps0.99.png`

---

## Slide 12: Contours - High NA Gaussian α=4 (ε = 0 vs 0.5 vs 0.99)

**Key Points:**
- Gaussian illumination gives larger DOF than uniform
- Same trend: annular extends DOF further
- Compare to uniform slides

**Figures (one per sub-slide):**
- `contours/contour_NA0.9_gaussian_a4.0_circular.png`
- `contours/contour_NA0.9_gaussian_a4.0_eps0.5.png`
- `contours/con1111111111111
## Slide 15: Next Steps

- Systematic DOF vs ε study across more configurations
- Address GitHub issues #3, #4, #5
- Compare with experimental data
- Investigate intermediate NA regime (0.3-0.7)

**Figure:** None

---

## Appendix: Plot Locations

| Topic | File |
|-------|------|
| Aperture profiles | `data/alpha_sweep/aperture_profiles_1d.png` |
| α RMS convergence | `data/alpha_sweep/rms_convergence_vs_alpha.png` |
| α DOF comparison | `data/annular_dof/axial_profiles_comparison.png` |
| DOF validation | `data/annular_dof/uniform_dof_test.png` |
| DOF vs ε | `data/annular_dof/dof_vs_epsilon_comparison.png` |
| 2D contours | `data/annular_dof/contours/*.png` |
