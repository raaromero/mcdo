# Rebuild roadmap — the presented progress report, step by step

*Reference = `~/Downloads/parallel_progress_report.pdf` (Progress Report, Team
One Parallel, Romero, 2026-02-09; 16 slides). We rebuild this arc, verified,
in the clean format. Don't match exactly; ADD the missing result figures that
back each claim. MC launcher / scattering results stay OUT (deck lists MC only
as a future "Next Step").*

## Slide format
- ONE figure, centered · bullets = main points only, terse · details → concise SPEAKER NOTES.

## Presented arc (rebuild in order)
- [ ] **1 — Framing** · goal (MC of high-NA pulses, extended-DOF annular, in scattering media) · core problem · gap · (concept, no figure)
- [ ] **2 — Reference papers** · Romallosa 2003 (PRA 68 033812); Arjonillo–Saloma MC · (concept)
- [ ] **3 — Applications** · mouse-embryo imaging, IC inspection, attosecond x-ray · (concept)
- [ ] **4 — Current approaches: Scalar DT** · reliable NA≤0.5, efficient, no polarization · (+ADD: scalar-limit = Airy figure) · `verify_tanaka_paraxial`
- [ ] **5 — Current approaches: Richards–Wolf** · high-NA vector, Ex/Ey/Ez, I_m integral · (+ADD: vector focal-field figure) · `verify_mc_vector`/`fig2_profiles`
- [ ] **6 — Current approaches: Monte Carlo** · gold standard tissue optics, HG scattering diagram · (concept, borrowed diagram)
- [ ] **7 — RW field components** · Ex=−i(I₀+I₂cos2φ), Ey=−iI₂sin2φ, Ez=−2iI₁cosφ · (theory)
- [ ] **8 — RW diffraction integrals** · I₀ (Airy), I₁ (longitudinal Ez), I₂ (cross-pol) · (+ADD: I₀/I₁/I₂ profile figure) · `fig2_profiles`
- [ ] **9 — Optical coordinates** · u=(2π/λ)sin²α·z, v=(2π/λ)sinα·r, α=arcsin(NA/n) · (theory)
- [ ] **10 — Few-cycle pulse characteristics** · τ<1.2fs threshold; coherence 359.7 nm < Nyquist 375 nm · FIGURE: 1-fs spectral distribution at 750 nm · (verify coherence-length number)
- [ ] **11 — Gaussian apodization** · A(θ)=exp(−α sin²θ/sin²α_max); α→0 uniform, α≥4 untruncated · FIGURE: A(ρ) truncation curves (Horvath & Bor 2003) · `verify_apod_thresholds`

> ───── END OF PRESENTED ───── below = NOT shown, hold
- [ ] N1 — Annular DOF results (claimed as current work but no result figure shown)
- [ ] N2 — Pulsed-focus results / bandwidth-invariant DOF
- [ ] N3 — MC launcher / scattering (future next-step only)
