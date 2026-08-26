# Consistency audit — does the flow serve the goal?

**Goal:** Monte-Carlo simulation of high-NA focused *optical pulses* through
*structured pupils* (annular / axicon) in *scattering media*.

**Verdict:** the chain is physically and mathematically consistent and aligned
with the goal. The one-time gap (the MC was scalar while the deterministic chain
is vector) is now **closed** — the vector MC carries the refracted 3-vector per
photon and reproduces both Richards–Wolf cuts to RMS 6×10⁻⁴
(`verify_mc_vector.png`, `test_montecarlo`). For the full quantitative accuracy
audit across all phases, see [`../ACCURACY.md`](../ACCURACY.md).

## The chain, layer by layer

| layer | role toward the goal | consistency |
|---|---|---|
| RW vector field (I₀,I₁,I₂) | exact high-NA focus = the *source* | ✓ matches Romallosa |
| Pulse = ∫|E(ω)|²·I_cw(ω)dω (Eq.10) | the *pulsed* source | ✓ frequencies incoherent (intensities add) — correct |
| Apodization A(θ) | realistic beams; pupil engineering | ✓ aplanatic, sine condition |
| Annular (field-level Babinet) | DOF control | ✓ same ω ⇒ coherent field subtraction |
| Axicon (conical phase) | Bessel/needle beams | ✓ |
| Pulsed × annular | the new science | ✓ reuses both validated primitives |
| MC angular-spectrum, clear limit | the *engine*, μ_s→0 = RW | ✓ (scalar — see gap) |

The logic is sound: build the exact source field, validate it, add the pulse
spectrally, add pupil engineering, then re-express the field as photons whose
clear-limit coherent sum *is* the diffraction integral — so scattering can be
added as a perturbation that preserves the clear limit by construction.

## Mathematical conventions — all consistent

- k = 2πn/λ, optical coords u=k sin²α z, v=k sinα r, used identically in
  `rw_integrals`, `debye`, `annular`, `montecarlo`.
- Pulse spectrum |E(ω)|²=exp[−(ω−ω_c)²/2a], a=2ln2/τ², FWHM 4ln2/τ.
- Incoherent across ω (pulse), coherent within ω (annular subtraction, MC
  angular-spectrum) — the coherent/incoherent bookkeeping is correct everywhere.

## Which "intensity" each deliverable shows (state it to avoid confusion)

The focal intensity is azimuthally dependent for a linearly polarized input,
so every figure picks a convention:

- **Main figures / atlas**: `|I₀−I₂|²` — the |Ex|² along the y-axis (φ=π/2),
  where Ey=Ez=0. Chosen because it has *true zeros* and matches Romallosa's
  published Fig 1–2.
- **Component atlas** (`output/atlas_components/`): azimuthal averages
  ⟨|Ex|²⟩=|I₀|²+½|I₂|², ⟨|E|²⟩=|I₀|²+|I₂|²+2|I₁|² — rotationally symmetric, so
  a single r–z map is well defined, and the Ex-only vs full split is explicit.
- **Monte Carlo (6a)**: currently the *scalar* Debye field (the I₀ integrand
  without the (1±cosθ) vector kernels) — validated against `scalar_debye`.

These are different physical quantities; each is correct for its purpose. The
one thing to make consistent for the high-NA goal is the next item.

## The scalar→vector gap — CLOSED

The MC originally reproduced only the **scalar** field; the goal is high-NA where
vector effects matter. This is now closed: each photon carries a 3-vector
amplitude — the refracted polarization of an x-input ray at (θ,φ),
Novotny–Hecht Eq. 3.66 — and the components are summed separately. The
clear-limit total |Ex|²+|Ey|²+|Ez|² reproduces both vector Richards–Wolf cuts
to **RMS 6×10⁻⁴** (`sample_photons_vector` / `coherent_intensity_vector`,
`test_montecarlo`). The `atlas_components/full/` maps are the reference it
matches; `Ex_only/` is the scalar-like approximation.

**On-axis consistency check (built in):** at r=0, I₁=I₂=0 ⇒ Ex-only ≡ full ⇒ the
axial profiles in `Ex_only/` and `full/` coincide. The vector contribution
(Ey,Ez) is purely off-axis and grows with NA — exactly the Phase-2 anisotropy
result. This is the same physics, now made explicit as two folders.
