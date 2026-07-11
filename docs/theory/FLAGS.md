# Two results worth understanding

Both came out of the Phase 4–5 sprint. Neither is a bug; each is a real
physical effect that is easy to misread, so they are documented here.

---

## Flag 1 — the axicon's Bessel deviation is stationary-phase error, not vector

**Observed.** The axicon focal segment has a position-dependent transverse
profile that should equal the Bessel beam J₀²(v·sinθ\*/sinα) at the cone angle
θ\*(u) selected by stationary phase. It does — to a max deviation of **0.04–0.08**.
But that deviation is **the same at low NA (X_NA=0.13) and high NA (0.8)**.

**Why this is surprising.** The thin annulus (Phase 3) showed the opposite: its
J₀² deviation grew from 0.004 at low NA to **0.163** at sinα=0.9 — a genuine
high-NA *vector* deformation of the Bessel core (the (1±cosθ) kernels and the
longitudinal field E_z reshaping it). I expected the axicon, at the same high
NA, to show the same vector deformation. It doesn't.

**The resolution.** The two pupils probe the Bessel beam differently:

- The **annulus isolates a single cone angle** θ_ring. Its focal field is
  purely J₀²(v·sinθ_ring/sinα), so any departure is the vector kernels acting
  at that one angle — a clean, isolated vector effect that grows with NA.
- The **axicon integrates over a range of θ.** At each axial point u, a *band*
  of angles around θ\*(u) contributes (the stationary-phase point has finite
  width ∝ 1/√β). The transverse profile is therefore a θ-average, and its
  leading departure from the ideal J₀² is the **stationary-phase approximation
  error** itself — finite segment length and the
  √cosθ·(1+cosθ)·sinθ amplitude taper across the contributing band. That error
  is O(1/β), present already in scalar theory, and at the β tested it is
  *larger* than the vector correction — so it dominates and masks the vector
  effect, equally at low and high NA.

**Takeaway.** The thin annulus is the clean probe of vector deformation of a
Bessel beam; the axicon is stationary-phase-limited and its vector signature is
buried. (This is also why the figure panel is labelled "two roads to one Bessel
core" — axicon ≡ annulus at the matched θ — rather than "vector deformation".)

**Verified (β-scan, `output/04_axicon/axicon_validity.png`).** Pushing β at fixed
θ\*=0.7α (NA=0.3, scalar regime), the J₀² deviation falls **0.134 (β=5) → 0.078
(β=20) → 0.006 (β=2560)** — a decreasing ≈1/β trend, confirming the 4–8% is the
stationary-phase *model* error and vanishes as β→∞. Meanwhile MC vs the
deterministic Debye field stays ≤0.019 at every β (the *method* is bias-free; it
only needs more photons as the phase oscillates faster). Validity ceilings:
N_theta=3001 resolves the pupil phase to β>2560 (mathematical), but for a real
objective (f≈2 mm) the focal segment z\*∝β leaves the focal region (Debye) at
β≈160 — the physical limit binds first. The launcher itself never breaks; the
J₀² *formula* is the approximation.

---

## Flag 2 — the pulsed annular ring contrast is non-monotonic in τ

**Observed.** Transverse Linfoot S (pulsed vs CW, same ε) at high obstruction:

| ε | 5 fs | 2 fs | 1 fs |
|---|---|---|---|
| 0.90 | 0.988 | 0.987 | 1.058 |
| 0.99 | 0.987 | 0.986 | 1.058 |

S dips **below 1** at moderate τ before jumping **above 1** at 1 fs. The full
disk (ε=0) is monotonic by contrast: 1.001 → 1.011 → 1.056.

**The mechanism (confirmed by the central/ring decomposition,
`output/05_pulsed_pupils/ring_decomposition.png`).** S = ⟨a²⟩/⟨r²⟩ over the
window (a = pulsed, r = CW, peak-normalized). Split at the first CW zero
(v₀=2.45 at ε=0.9), the two regions move oppositely with τ:

| τ | S_total | S_central | S_ring |
|---|---|---|---|
| 5 fs | 0.988 | 1.001 | 0.823 |
| 3 fs | 0.984 | 1.003 | 0.734 |
| 2 fs | 0.987 | 1.009 | 0.717 |
| 1.5 fs | 1.004 | 1.017 | 0.833 |
| 1 fs | 1.060 | 1.036 | 1.369 |

- **S_central rises only slowly** (1.00 → 1.04): the Bessel-like central lobe
  is narrow and robust, so bandwidth barely broadens it until 1 fs.
- **S_ring dips to 0.72** (rings wash out — pulsing averages Bessel beams of
  different scales J₀²(v·k/k_c), shifting ring positions so they partially
  cancel) **then jumps to 1.37** at 1 fs, where the hugely broadened central
  skirt spills *into* the ring region and overfills it.

The subtlety the decomposition reveals: the rings carry only **7%** of the
window weight, yet S dips below 1 — because at moderate τ S_central sits so
close to 1 that even a small ring deficit (0.07·(0.72−1) ≈ −0.02) drags the
total under. At 1 fs both regions exceed 1, so S_total = 1.06. At ε=0 the
central lobe carries essentially all the weight and broadens monotonically, so
no dip.

**Not a bug.** S(cw,cw)=1 exactly; the ε=0 value S(1 fs)=1.056 matches the
independent Phase-1 single-photon Romallosa value (1.053–1.062).

**Takeaway.** "Pulsing degrades ring contrast" is too simple at high ε: moderate
pulses first *smooth* the Bessel rings (which can read as S<1) before few-cycle
central broadening dominates. The physically robust statement is that the
**axial DOF benefit survives pulsing while the transverse structure smooths**.

**Verified (`output/05_pulsed_pupils/pulsed_S_diagnostic.png`).** The
non-monotonic S(τ) is confirmed *real*, not numerical or a single-cut artifact:
(A) on a dense τ grid the dip-then-rise is **smooth** (a bug/undersampling would
be jagged); (B) S is **flat vs N_freq** (51→801) at both 2 fs and 1 fs — not
spectral undersampling; (C) the dip-then-rise is present in the y-cut |I₀−I₂|²,
the x-cut |I₀+I₂|²+4|I₁|², **and** the full azimuth-averaged |I₀|²+|I₂|²+2|I₁|²
(all of E_x,E_y,E_z) — so it is not an artifact of the y-cut. Cross-check:
S(5/2/1 fs)=0.988/0.987/1.057 reproduces the table above.
