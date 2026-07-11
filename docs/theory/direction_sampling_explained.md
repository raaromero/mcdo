# How we initialize photon directions — and why we don't need the focal intensity

*A plain-language companion to `docs/theory/06_monte_carlo.md` §2–§3. Verify the
claims against `output/06_monte_carlo/verify_launcher.png`.*

## The short answer

**Yes — we initialize the directions correctly without ever knowing the focal
intensity.** That is not a trick; it is the whole reason the Monte Carlo is a
*solver* and not circular. We sample the **input** (the pupil), and the focal
intensity is the **output** we are trying to compute. If we needed the output to
build the input, the method would be useless. We don't.

## What we actually sample

A photon is one plane-wave component of the converging beam. To launch it we need
its direction (θ, φ) on the focusing cone. We draw it from the **pupil angular
density**

$$p(\theta) \propto |A(\theta)|\,\sqrt{\cos\theta}\,\sin\theta, \qquad
\varphi \sim \text{Uniform}[0,2\pi),$$

by **inverse-transform sampling** (`_direction_cdf` in `montecarlo.py`): tabulate
the cumulative integral of `p(θ)` on `[0, α]`, draw a uniform number `u∈[0,1]`,
and read off the θ whose CDF equals `u`. Repeat for every photon. φ is just a
uniform spin.

Every ingredient of `p(θ)` is known **before** any field is computed:

| factor | where it comes from | known? |
|---|---|---|
| cone limit `θ ≤ α`, `sinα = NA/n` | the objective's numerical aperture | yes, a number |
| `√cosθ` | aplanatic (Abbe sine) projection — energy conservation as the ray bends onto the converging sphere | yes, geometry |
| `A(θ)` | the input illumination you choose (uniform, Gaussian, annular, axicon) | yes, you set it |
| `sinθ` | the solid-angle element `sinθ dθ dφ` | yes, geometry |

None of these is the focal field. So the launch distribution is fully fixed by
the lens and the beam you shine in — not by where the light ends up.

## Why this is not circular (the "amazing if true" part)

The focal intensity is `I(P) = |Σ_j w_j e^{i k\hat{k}_j·P}|²`. It is the
**consequence** of launching correctly-distributed photons and letting them
interfere — it is computed, never assumed. Compare two things that sound similar
but are completely different:

- **Sampling a known distribution** (what a histogram-fitter does): you must
  already possess the distribution to draw from it.
- **Sampling the source of a transform, then evaluating the transform** (what we
  do): you possess the *input* distribution; the *output* is produced by the
  physics. The Debye–Wolf integral is that transform, and it is a *fixed map* —
  pupil in, focal field out. We never invert it.

A clean analogy: ray-tracing a lens. You launch rays from the source with known
positions and angles; you do **not** need the image to decide how to launch them
— the image is what forms downstream. Same here, with plane waves instead of
rays and interference instead of a geometric crossing.

## What the proof figure shows

`output/06_monte_carlo/verify_launcher.png`:
- **panel (1)** — the sampled θ histogram lands exactly on `p(θ)` (KS ≈ 1/√N).
  *This is the direction distribution, measured.*
- **panels (2,4)** — dividing out the geometry recovers the input `A(θ)` and the
  input intensity `|A|²` (flat disk for uniform, Gaussian for Gaussian).
- **panel (3)** — φ is uniform.
- And only **then**, in `verify_launcher_intensity.png`, the coherent sum of
  those launched photons reproduces the deterministic focal field (RMS ≈ 7×10⁻⁴).
  The output matches *because* the input was right — confirmation, not input.

## The one caveat

"Correct directions without the focal intensity" is exact in a **clear** medium,
because the input→output map (Debye–Wolf) is fixed and known. In a **scattering**
medium the same launch is still correct at the entrance; scattering then removes
or redirects photons from that already-correct ensemble (it never needs the focal
intensity either). See `docs/theory/06_monte_carlo.md` §3, §7.

## Validity — high NA, axicons, and what *would* break it

The launcher samples the angular spectrum of the **Debye–Wolf** representation.
That representation rests on a few assumptions; here is each, and whether it
holds for us.

| assumption | holds? | if violated |
|---|---|---|
| **Debye approximation** (high Fresnel number `N_F = a²/(λf) ≫ 1`) | yes — real objectives have `N_F ~ 10³–10⁶` | low `N_F`: focal shift, fore–aft axial asymmetry. Not our regime. |
| **propagating waves only** (cone `θ≤α`, no evanescent) | yes — focusing in a homogeneous medium | matters only sub-wavelength / near-field (not aplanatic focusing) |
| **aplanatic / Abbe sine** `ρ = f sinθ` | yes — well-corrected objective | put the *measured* pupil `A(θ)` in; framework unchanged |
| **scalar field** | only at low NA | at high NA use the **vector** launcher (below) |

**High NA — valid and consistent, with the vector launcher.** Richards–Wolf *is*
the high-NA theory (that is what it was built for), so nothing breaks at high NA
*as a matter of principle*. The thing that breaks is the **scalar** shortcut: it
misses `E_z` and polarization. We handle that with `sample_photons_vector`, which
carries the refracted 3-vector and reproduces **both** RW cuts at NA=0.8 to
RMS ≈ 6×10⁻⁴ (`verify_mc_vector.png`). The scalar–vector gap at high NA is the
documented *anisotropic-threshold* result (Phase 2), an expected physical effect,
not a launcher fault. Consistency across NA holds: low-NA → scalar = vector =
Airy; high-NA → the vector deformation appears, and the clear-limit gate
(MC = deterministic) passes at every NA tested.

**Axicons — valid.** A conical pupil is just a complex `A(θ) = exp(jβ sinθ/sinα)`;
the launcher samples θ ∝ √cosθ·sinθ (since `|A|=1`) and carries the conical phase
in the weight. The MC reproduces the deterministic Debye field for the axicon to
RMS ≈ 1.8×10⁻³ (`verify_mc_configs.png`). Two caveats, **neither a breakdown of
the launcher**:
1. The 4–8% axicon "miss" is the *analytic Durnin J₀²* prediction (a
   stationary-phase model) being approximate — the **simulation** is exact; see
   `FLAGS.md` and review 04.
2. The rapidly varying axicon phase makes the coherent sum partly cancel, so it
   needs *more* photons (N≈10⁴ vs 3×10³) and θ-nodes to converge. That is a
   *variance / sampling cost*, not bias — the estimator is still unbiased.

**Bottom line.** Nothing fundamental is violated. The only genuine limits are:
use the vector launcher at high NA (scalar is an approximation, as designed), and
budget more photons for strongly oscillatory pupils (axicons). Both are quantified
and tested, not hand-waved.
