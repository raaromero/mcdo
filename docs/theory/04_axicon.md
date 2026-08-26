# Axicon / Bessel beams via a conical pupil phase
*(Phase 4 — focal segment, position-dependent Bessel scale, axicon↔annulus)*

## 1. Construction

A true axicon is a cone: phase ∝ pupil radius ρ. With the sine condition
ρ ∝ sinθ this is a conical pupil phase behind the aplanatic lens,
$$A(\theta)=\exp\!\big(+j\,\beta\,\sin\theta/\sin\alpha\big),$$
$\beta$ = phase depth (rad) at the pupil edge (`mcdo/apodization.py::axicon`).
On the on-axis integral the total phase is
$\Psi(\theta)=u\cos\theta/\sin^2\alpha+\beta\sin\theta/\sin\alpha$; stationary
phase gives the segment mapping
$$u(\theta^\*) = \beta\,\sin\alpha\,\cot\theta^\* \quad(>0),$$
so each axial position $u$ is fed by a cone angle $\theta^\*(u)$ and the local
transverse profile is the Bessel beam $J_0^2(v\,\sin\theta^\*/\sin\alpha)$
[Dur87; Her91]. Steep rays ($\theta\to\alpha$) feed the segment onset
$u\approx\beta\cos\alpha$; paraxial rays feed large $u$.

## 2. Verified results (`output/04_axicon/verify_axicon.png`, linear-x y-cut)

- **β=0 regression** ≡ plain disk: max diff 0 (exact).
- **Focal segment** forms at positive $u$; bright (>½-max) length grows with
  β: 10.9 (β=10), 14.2 (β=20), 17.9 (β=40) vs the plain-focus FWHM 9.9 at
  $X_{NA}=0.8$ — onset at $u\approx\beta\cos\alpha$.
- **Position-dependent Bessel scale (Durnin checkpoint):** at $\theta^\*$ =
  0.55α, 0.70α, 0.85α the transverse profile at the predicted $u$ matches
  $J_0^2(v\sin\theta^\*/\sin\alpha)$ to max dev **0.04–0.08**, at both
  $X_{NA}=0.13$ and $0.8$.
- **Axicon ≡ annulus**: the axicon's local profile at $\theta^\*$ overlies a
  thin annulus centred on the same θ and the $J_0^2$ prediction — two roads
  to one Bessel core.

## 3. Flag — the deviation is SPA-limited, not vector

The 0.04–0.08 deviation from $J_0^2$ is **comparable at low and high NA**, so
it is the stationary-phase-approximation error (finite segment + the
$\sqrt{\cos\theta}\,(1+\cos\theta)\sin\theta$ amplitude taper across the
contributing zone), **not** a polarization effect. This is the opposite of
the thin annulus (Phase 3), which isolates a single θ and therefore exposes a
genuine high-NA vector deformation of the Bessel beam (dev 0.163 at
sinα=0.9 vs 0.004 at low NA). Takeaway: **the annulus is the clean
vector-Bessel probe; the axicon integrates over θ and is SPA-limited.**

The axicon's DOF gain (≈1.4–1.8× here) is modest next to the annulus
(≈44× at ε=0.99); its value is the position-tunable Bessel scale, not raw DOF.
