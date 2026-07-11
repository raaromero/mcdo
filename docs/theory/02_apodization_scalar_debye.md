# Pupil apodization and the scalar-Debye / Airy validation chain
*(Phase 2 — Gaussian illumination; convergence to Debye/Airy at low NA;
NA thresholds for vector diffraction)*

## 1. Illumination function A(θ) for an aplanatic lens

An aplanatic objective obeys the **sine condition**: pupil radius
$r = f\sin\theta$. A collimated Gaussian beam with $1/e^2$ intensity radius
$w$ at a pupil of radius $r_{ap}$ therefore produces the angular *amplitude*

$$A(\theta) = \exp\!\Big(-\alpha_t\,\frac{\sin^2\theta}{\sin^2\alpha}\Big),
 \qquad \alpha_t = \Big(\frac{r_{ap}}{w}\Big)^2 \quad\text{[H\&B03 Eq. 1]}$$

- $\alpha_t \to 0$: uniform (overfilled) illumination
- $\alpha_t = 1$: beam waist at pupil edge (amplitude $e^{-1}$ there)
- $\alpha_t \ge 4$: effectively untruncated Gaussian (<2% at edge)

$A(\theta)$ multiplies the integrands of $I_0, I_1, I_2$ (and the scalar
integral). The $\sqrt{\cos\theta}$ aplanatic energy-conservation factor is
separate and always present. **Annular/Babinet note:** inner and outer disks
must reference the *outer* aperture's $\sin^2\alpha$ so both sample the same
physical beam. **MC note:** $\lvert A(\theta)\rvert^2$ is the photon-launch
density at the pupil in the Monte Carlo phase — same object, two pipelines.

## 2. The three-level theory chain

| level | what it keeps | integrand |
|---|---|---|
| vector RW | everything | kernels $(1\pm\cos\theta)J_{0,2}$, $\sin\theta\,J_1$ |
| scalar Debye | wide-angle geometry, drops polarization | $A\sqrt{\cos\theta}\,\sin\theta\,J_0(\tfrac{v\sin\theta}{\sin\alpha})\,e^{ju\cos\theta/\sin^2\alpha}$ |
| paraxial | drops wide-angle too ($\alpha\to 0$) | analytic |

Paraxial limits (uniform illumination):

$$I(v) = \Big[\frac{2J_1(v)}{v}\Big]^2 \;(\text{Airy, FWHM}_v = 3.2326),
\qquad I(u) = \Big[\frac{\sin(u/4)}{u/4}\Big]^2$$

So **RW − scalar isolates polarization (vector) effects**, and
**scalar − Airy isolates wide-angle geometry**. This separation is the
logic behind the NA-threshold question.

## 3. Verification results (`scripts/verify_na_convergence.py`, λ=750 nm, n=1.3)

**A. Low-NA convergence** ($X_{NA}=0.1$): max deviation from Airy over
$v\in[0,10]$ — RW y-cut $2\times10^{-4}$, RW x-cut $10^{-3}$, scalar
$10^{-4}$. All theories coincide; both the vector machinery and the scalar
module are validated against the analytic limit.

**B. High-NA divergence** ($X_{NA}=1.2$): max deviation from Airy — x-cut
0.21 (zeros filled by $E_z$), y-cut 0.056, scalar 0.031. The focal spot
elongates *along* the polarization axis.

**C. FWHM (v units) vs NA** — deviation of the vector x-cut from scalar:

| threshold | exceeded at |
|---|---|
| 1% | $X_{NA} \approx 0.30$ |
| 5% | $X_{NA} \approx 0.60$ |

At $X_{NA}=1.2$: FWHM$_x$ +31% vs Airy, FWHM$_y$ −6%, scalar −3.6%.
The y-cut *narrows* slightly while the x-cut broadens strongly — vector
effects are anisotropic, so "the" NA threshold depends on which cut an
experiment measures. Scalar theory stays within ~1% up to $X_{NA}\approx0.8$;
the polarization splitting is the dominant correction.

**D. Axial first minimum** (paraxial limit: true zero at $u=4\pi=12.566$):

| $X_{NA}$ | RW $u_0$ | depth |
|---|---|---|
| 0.1 | 12.55 | $3\times10^{-7}$ |
| 0.4 | 12.28 | $6\times10^{-5}$ |
| 0.8 | 11.28 | $1.3\times10^{-3}$ |
| 1.2 | 8.98 | $1.6\times10^{-2}$ |

The axial zeros migrate focus-ward and *fill in* at high NA — the apodized
axial "sinc" loses its exact zeros (relevant later for optical sectioning).

**E. Gaussian apodization** ($X_{NA}=0.8$, RW y-cut): regression
$\alpha_t\to 0$ equals uniform to $8\times10^{-14}$;
FWHM$_v$: 3.169 (uniform) → 3.491 ($\alpha_t$=1) → 3.882 ($\alpha_t$=2) →
4.800 ($\alpha_t$=4). Underfilling lowers the effective NA and suppresses
the Airy rings (smooth pupil → no hard-edge diffraction), visible in panel
(d) of `output/02_na_apodization/verify_na_convergence.png`.

## 4. Status

- A(θ) implemented in `mcdo/apodization.py`; `compute_integrals`
  accepts `apodization=` (default None = uniform, regression-tested).
- Scalar Debye + Airy/sinc² in `mcdo/debye.py`, validated both ways
  (low-NA convergence, controlled high-NA divergence).
- Next checkpoints for this phase: Tanaka 1985 / Horváth & Bor 2003
  analytic profiles for truncated Gaussians (port from mcdo's
  `gaussian_beam_theory.py` and verify); then notebook 02.
