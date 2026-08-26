# Monte-Carlo focal field
*(Phase 6 — design, clear-limit gate, per-configuration proofs; scattering next)*

## 1. Why a photon is a vector, and why the clear limit must equal RW

A standard *incoherent* ray MC (energy-only photons binned by position) does
**not** reproduce the focal field — its no-scattering limit is the geometric
caustic (a point), not the Airy/RW pattern, because the focus is interference.
The fix: each photon is a **plane-wave (angular-spectrum) component** of the
converging field, carrying a direction k̂ in the focusing cone, a complex
weight w, and phase referenced to the geometric focus:

$$U(P) = \sum_j w_j\, e^{\,i k\,\hat{k}_j\cdot P},\qquad I(P)=|U(P)|^2 .$$

With μ_s=0 this is a Monte-Carlo evaluation of the (scalar) Debye-Wolf
integral, so it **converges to the deterministic field as N→∞**. Phase = k·(path)
= ω·t, so *carrying phase and tracing photons in time are the same operation*;
all CW photons reach the focus in phase (equal paths on the reference sphere).

## 2. Photon launch (the pupil → photon map)

* **direction**: θ ~ p(θ) ∝ |A(θ)|·√cosθ·sinθ (radiant amplitude × solid angle),
  φ uniform. The same `apodization.A(θ)` object used by the deterministic
  solver is the launcher.
* **phase weight**: w = e^{i·arg A(θ)} — carries the pupil phase, so annular
  (A=0 outside the ring) and axicon (A = conical phase) use the same sampler.
* **position**: implicit at focus for the clear field (focus-referenced phase);
  explicit on the pupil/reference sphere for scattering (Stage 6b), where each
  photon is marched with free-path sampling.
* **wavelength** (pulsed): λ ~ |E(ω)|² power spectrum. Same-λ photons interfere
  *coherently*; different-λ photons add *incoherently* — which is exactly
  Eq. 10, $I=\int|E(\omega)|^2|E(P,\omega)|^2 d\omega$. λ is carried through the
  photon's life, so in a scattering medium it sets the wavelength-dependent
  μ_s and Mie phase function.

## 3. Why the launch is physically forced (not curve-fitting)

The distribution checks (§6) show the *output* matches; this section is the
*first-principles* reason the launch is correct, independent of any measured
histogram.

**The plane-wave decomposition is exact, not an analogy.** In the Debye–Wolf
representation [Wolf 1959; Richards & Wolf 1959] the field near the focus of an
aplanatic system *is* an angular spectrum of plane waves whose wavevectors fill
the geometrical focusing cone. "Photon = plane-wave component" is therefore
rigorous high-aperture diffraction theory — which is *why* the μ_s=0 sum must
equal the Richards–Wolf integral.

**The direction distribution is dictated, not chosen.** Within the cone the
amplitude of each plane-wave component is fixed by three physical factors, none
of them free:
 * **aperture / NA** — directions are confined to the spherical cap
   θ ∈ [0, α], sinα = NA/n; there is simply no light outside the cone
   (solid angle Ω = 2π(1−cosα));
 * **aplanatic (Abbe sine) factor √cosθ** — energy conservation as a ray bends
   from the flat pupil onto the spherical converging wavefront (the "intensity
   law of geometrical optics"); required for an aberration-free lens, not
   inserted by hand;
 * **input illumination A(θ)** — the only thing the experimenter controls
   (uniform, Gaussian, annular, axicon…).

 The product A(θ)·√cosθ is the angular amplitude; ×sinθ is the solid-angle
 Jacobian. So `p(θ) ∝ |A|·√cosθ·sinθ` is *derived* from Maxwell + lens geometry,
 not fitted.

**Location and direction are locked by the sine condition.** A real aplanatic
lens maps a pupil ray at radius ρ to focal angle θ by ρ = f·sinθ. Initial
*position* and initial *direction* are therefore **not independent** — one fixes
the other. The 2-D pupil map (ρ̂ = sinθ/sinα) and the θ-distribution are the
same information in two coordinates. The physical launch surface is the
**reference sphere** of radius f centred on focus (equivalently the flat exit
pupil); that is the only "position" the clear field needs, because the phase is
referenced to focus. An explicit slab-plane position is added only for
scattering (§7).

**Yes — straight lines.** In the homogeneous medium each component propagates
rectilinearly along its k̂; the geometrical rays are the wavefront normals —
straight lines converging from the reference sphere to focus — and the
diffraction pattern is their coherent interference, with phase accumulating as
k·(straight path). In a scattering medium these straight segments are broken at
the sampled free-path points (§7); the unscattered photons keep going straight,
which is exactly why the attenuated RW core survives.

**Constraints on the initial direction (summary).** (i) |k| = n·k₀ is fixed —
all one-frequency photons live on the sphere of radius nk₀, only the *direction*
varies; (ii) the direction lies in the forward cone θ≤α set by the NA; (iii) it
points toward the geometric focus (converging, k_z>0); (iv) its statistical
weight is A(θ)·√cosθ; (v) azimuth uniform for a rotationally symmetric pupil,
the vector polarization weight (Novotny–Hecht Eq. 3.66) being the only
φ-dependence. Pulsed light adds a sixth: |k| is drawn from the power spectrum
|E(ω)|².

**So there are two correctness arguments, not one.** (a) *Analytic* — the
importance-sampling estimator (1/N)Σ wⱼ e^{ik·P} is provably **unbiased** for the
Debye integral for any density that covers the support, so N→∞ convergence is
guaranteed *before* running anything; the histogram match in §6 only confirms
the implementation has no bug. (b) *Empirical* — §5 and §6 show the input
distribution, the output field, and the per-configuration RMS all agree. The
analytic guarantee is the "aside from matching distributions" reason the launch
is trustworthy.

## 4. Clear-limit gate (`output/06_monte_carlo/verify_mc_clear.png`)

X_NA=0.8 scalar field, MC vs `scalar_debye`:

| N | RMS | null floor |
|---|---|---|
| 10³ | 0.0117 | 4.4e-3 |
| 10⁴ | 0.0033 | 5.3e-4 |
| 10⁵ | 0.0008 | ~5e-4 |

The **null floor ∝ 1/N** (random-walk residual at the true zeros) — the
photon-count requirement: N≳10⁴ for zeros clean to ~10⁻³. Low-NA (X_NA=0.3)
matches the analytic Airy to 0.0015.

**Resolution.** The field's max spatial frequencies are k·sinα (transverse,
marginal ray) and k·(1−cosα) (axial), so
$$dx,dy \le \lambda/(2\,\mathrm{NA}),\qquad dz \le \lambda/(2n(1-\cos\alpha)).$$
Intensity needs ½ of that; we use ~¼-Nyquist (comfortable oversampling):
at X_NA=0.8, **dx=dy=117 nm, dz=341 nm**. (dz coarser than dx — the focus is
axially elongated.)

## 5. Per-configuration proof (`output/06_monte_carlo/verify_mc_configs.png`)

The launcher reproduces every pupil — same scalar Debye integral evaluated
deterministically vs by MC photons (N=10⁵, RMS over the x–z slice):

| configuration | RMS | 
|---|---|
| uniform | 0.0006 |
| Gaussian α_t=2 | 0.0010 |
| annular ε=0.5 (top-hat ring) | 0.0009 |
| axicon β=20 (conical phase) | 0.0018 |

All <0.2%. This proves the photon launcher correctly encodes apodization
(density), annular obstruction (support), and pupil phase (weight).

## 6. Launcher initialization proof (`verify_launcher.png`, `verify_launcher_intensity.png`)

§2 *defines* the launch and §3 *justifies* it; this *proves* it samples the
right distribution and reproduces the expected intensity in the clear limit —
the prerequisite the scattering run (§7) inherits unchanged. Four checks,
uniform and Gaussian
(α_t=2) input:

1. **Direction.** The sampled polar-angle density equals the Debye-Wolf
   integrand density p(θ) ∝ |A(θ)|·√cosθ·sinθ to the sampling limit:
   Kolmogorov-Smirnov distance KS = 0.0018 ≈ 1/√N (N=3×10⁵). Directions span the
   cone θ∈[0,α], α=38° here; uniform input peaks near the rim (the sinθ
   solid-angle weight), Gaussian is pulled toward the axis.
2. **Azimuth.** φ is uniform on [0, 2π) (flatness 0.04, histogram Poisson
   noise) — the rotational symmetry of the input.
3. **Input illumination** (the uniform-vs-Gaussian question). Dividing the
   sampled θ-density by the geometric factor √cosθ·sinθ recovers the pupil
   amplitude A(θ): flat for uniform, exp(−α_t sin²θ/sin²α) for Gaussian. The 2-D
   pupil maps (photons weighted by |A|√cosθ → input intensity |A|²) show the flat
   disk vs the Gaussian spot. Note: the *raw* photon number-density in the pupil
   is ∝ |A|/√cosθ — the importance density that minimises the variance of the
   coherent sum, **not** |A|². The two differ only by the deterministic aplanatic
   factor √cosθ and both reproduce the field (check 4).
4. **Intensity gate.** The coherent MC intensity matches the deterministic Debye
   field: transverse (z=0) and axial (x=0) cuts coincide through peak, zeros and
   side-lobes (down to the ~10⁻³ null floor), and the x–z slice RMS = 0.0007 for
   both inputs. The deterministic iso-value contours (Romallosa style) overlaid
   on the MC heat map sit on the MC structure.

Because both the launch distribution and the resulting field are certified, a
scattering medium can only *remove* (ballistic attenuation) or *redirect*
(diffuse halo) photons from a correct starting ensemble — the μ_s→0 limit is
exact by construction.

## 7. Status and next

- **6a done**: coherent clear-medium MC, validated against the deterministic
  field globally, per configuration, and at the launcher-distribution level
  (§6); sampling/voxel requirements quantified (`study_sampling.png`); 3-D
  volume saving (`.npz`).
- **Vector field done**: photons carry the refracted 3-vector polarization
  (Novotny-Hecht Eq. 3.66); |Ex|²+|Ey|²+|Ez|² matches both Richards-Wolf cuts
  (`verify_mc_vector.png`).
- **6b — scattering (first slab run DONE, validated)**: focused beam through a
  slab z∈[−d,0] (`mcdo/focus_scatter.py`); each photon is the converging ray,
  entering at (−d tanθ cosφ, −d tanθ sinφ, −d). Unscattered photons stay coherent
  as the **ballistic core** (amplitude exp(−μ_s L/2), L=d/cosθ); forward-scattered
  photons (Henyey–Greenstein walk) form the **incoherent halo**. Validated against
  rungs 1–3 (μ_s→0 = clear focus; MC ballistic fraction = analytic
  ⟨e^{−μ_s d/cosθ}⟩ to <0.001; energy conserved to 2×10⁻¹⁶), K=10 trials
  (`verify_mc_scatter.png`). Next: rungs 4–6 (single-scatter Born, diffusion,
  MCML cross-check); axial halo; vector + pulsed (λ-dependent μ_s) scattering.

## Appendix — the configuration atlas

`output/atlas/atlas_{NA,gaussian,annular,axicon,pulsed}.png`: every parameter
family in one Romallosa-style view (2-D r–z map + transverse + axial cuts),
linear-x y-cut |I₀−I₂|². The growing visual record of what's been built:
NA 0.3–1.2 (optical coords), α_t 0–4, ε 0–0.99, β 0–40, τ cw–1 fs. Fields
saved as `field_*.npz` for reuse.
