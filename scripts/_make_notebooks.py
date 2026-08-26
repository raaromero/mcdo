"""Generate review notebooks 02–05 (display saved figures + narrative).

These are reading/review notebooks: each cell displays a figure produced by
the named script (the scripts in scripts/ remain the source of truth and are
re-runnable from the CLI). Run this generator, then execute the notebooks
(fast — they only display PNGs).
"""
import os
import nbformat as nbf

ROOT = os.path.join(os.path.dirname(__file__), '..')
NB = os.path.join(ROOT, 'notebooks')
md = nbf.v4.new_markdown_cell
code = nbf.v4.new_code_cell

HEADER = code(
    "import os\nfrom IPython.display import Image, display\n"
    "OUT = os.path.join('..', 'output')")


def fig(rel, caption):
    return [md(caption), code(f"display(Image(os.path.join(OUT, {rel!r})))")]


def build(path, title, intro, script_note, blocks):
    nb = nbf.v4.new_notebook()
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python", "version": "3.11"}}
    cells = [md(title + "\n\n" + intro), md(script_note), HEADER]
    for rel, cap in blocks:
        cells += fig(rel, cap)
    nb.cells = cells
    nbf.write(nb, path)
    print("wrote", path)


# ── 02 ─────────────────────────────────────────────────────────────────────
build(
    os.path.join(NB, '02_na_apodization.ipynb'),
    "# 02 — NA convergence & apodization",
    "Gaussian pupil illumination A(θ)=exp(−α_t sin²θ/sin²α), scalar Debye, and "
    "the analytic Airy/sinc² limits. Chain logic: **RW−scalar isolates "
    "polarization; scalar−Airy isolates wide-angle geometry.** Headline: vector "
    "thresholds are anisotropic (x-cut 0.30/0.60, y-cut 0.85/–, circular "
    "0.45/0.90, axial 1.15/– in X_NA); Gaussian illumination *extends* scalar "
    "validity. Full text: `docs/theory/02_apodization_scalar_debye.md`.",
    "Figures from `scripts/verify_na_convergence.py`, `visual_na_checks.py`, "
    "`visual_axial_checks.py`, `visual_polarization_checks.py`, "
    "`verify_apod_thresholds.py`, `verify_tanaka_paraxial.py`.",
    [("02_na_apodization/check1_lowNA_convergence.png",
      "### Check 1 — low-NA correctness\nAll theories coincide with Airy to 1e-4 at X_NA=0.1."),
     ("02_na_apodization/check2_highNA_vector.png",
      "### Check 2 — high-NA behavior (NA line-families)\nx-cut zeros fill (E_z) & lobe broadens; y-cut keeps zeros; scalar barely moves."),
     ("02_na_apodization/check3_fwhm_thresholds.png",
      "### Check 3 — FWHM thresholds (uniform)\nx-cut vs scalar: 1% @ 0.30, 5% @ 0.60; y-cut stays ≲2% to ~0.9."),
     ("02_na_apodization/check7_axial_vs_na.png",
      "### Check 7 — axial direction\nOn-axis scalar holds far longer (uniform 1% only @ ~1.15); only the (1+cosθ) kernel acts, no anisotropy."),
     ("02_na_apodization/check6_anisotropy.png",
      "### Check 6 — anisotropy = longitudinal field\nElliptical spot at X_NA=1.2; FWHM_x/FWHM_y→1.4 tracks the E_z energy fraction."),
     ("02_na_apodization/check8_polarization.png",
      "### Check 8 — input polarization\nCircular input (|I₀|²+|I₂|²+2|I₁|²) thresholds 0.45/0.90 — recovers the old report's lenient numbers under its own convention."),
     ("02_na_apodization/check5_apodization.png",
      "### Check 5 — Gaussian apodization\nα_t→0 ≡ uniform to 1e-13; FWHM_v 3.17→4.80 for α_t 0→4, Airy rings suppressed."),
     ("02_na_apodization/verify_tanaka_paraxial.png",
      "### Closer — Tanaka/H&B paraxial checkpoint\nScalar *and* RW y-cut match the independent truncated-Gaussian integral to ~1e-4."),
     ("02_na_apodization/verify_apod_thresholds.png",
      "### Corrected NA-threshold study\nWith a consistent scalar reference, Gaussian α_t=4 sits below uniform everywhere — Gaussian extends scalar validity (reverses the old report)."),
     ])

# ── 03 ─────────────────────────────────────────────────────────────────────
build(
    os.path.join(NB, '03_annular.ipynb'),
    "# 03 — Annular apertures (field-level Babinet)",
    "Annulus ε=r_in/r_out as the field-level difference of two disks at the "
    "same (r,z,k). DOF extension 1/(1−ε²) (3 digits at low NA, ~40% short at "
    "sinα=0.9); thin annulus → Durnin J₀² (and a genuine high-NA vector "
    "deformation, dev 0.163 vs 0.004). Strehl cost (1−ε²)². Validated against "
    "Sheppard & Wilson 1978. Full text: `docs/theory/03_annular_babinet.md`.",
    "Figures from `scripts/verify_annular.py`, `verify_annular_energy.py`, "
    "`verify_sheppard.py`.",
    [("03_annular/verify_annular.png",
      "### Profiles, DOF, illumination\n(a) transverse→J₀²; (b) axial extends; (c) DOF ratio vs theory low/high NA; (d) uniform≈Gaussian for thin annulus."),
     ("03_annular/annular_energy_cost.png",
      "### The cost side\nStrehl tracks (1−ε²)² at both NAs; central-lobe energy collapses 0.76→0.055 as ε→1."),
     ("03_annular/verify_sheppard.png",
      "### Literature anchor — Sheppard & Wilson 1978\nFit a=0.200 from the focal envelope; the **predicted** axial profile (Eq. 33, not fitted) matches to 0.8%."),
     ])

# ── 04 ─────────────────────────────────────────────────────────────────────
build(
    os.path.join(NB, '04_axicon.ipynb'),
    "# 04 — Axicon / Bessel beams",
    "Conical pupil phase A(θ)=exp(+jβ sinθ/sinα) → focal segment with "
    "position-dependent Bessel scale, u(θ*)=β sinα cotθ*. Durnin checkpoint: "
    "transverse @ predicted u = J₀²(v sinθ*/sinα) to 4–8%. **Flag:** that "
    "deviation is stationary-phase error (low≈high NA), not vector — the "
    "annulus is the clean vector-Bessel probe. See `docs/theory/04_axicon.md` "
    "and `docs/theory/FLAGS.md`.",
    "Figure from `scripts/verify_axicon.py`.",
    [("04_axicon/verify_axicon.png",
      "### Focal segment + Durnin checks\n(a) axial segment vs β; (b) low-NA Durnin (axicon vs J₀²); (c) axicon ≡ annulus ≡ J₀² at θ*=0.70α."),
     ])

# ── 05 ─────────────────────────────────────────────────────────────────────
build(
    os.path.join(NB, '05_pulsed_pupils.ipynb'),
    "# 05 — Pulsed × annular (new science)",
    "Eq.-10 spectral sum over annular fields. **Headline: the annular DOF "
    "extension is immune to few-cycle bandwidth** (44.35→44.33 cw→1 fs at "
    "ε=0.99); the transverse ring contrast erodes (Linfoot S→1.058 at 1 fs). "
    "ε=0 gives S(1fs)=1.056 = Phase-1 cross-check. **Flag:** S(τ) is "
    "non-monotonic at high ε (ring-washing). See "
    "`docs/theory/05_pulsed_pupils.md` and `FLAGS.md`.",
    "Figures from `scripts/verify_pulsed_annular.py`, `verify_pulsed_ring_decomp.py`.",
    [("05_pulsed_pupils/verify_pulsed_annular.png",
      "### Pulsed × annular grid\n(a) ε=0.99 rings fill as τ↓; (b) full disk ref; (c) axial focus persists at 1 fs; (d) DOF(ε)/DOF(0) pulse-invariant."),
     ("05_pulsed_pupils/ring_decomposition.png",
      "### Flag 2 confirmed — ring-washing\nS_ring dips below 1 (rings smooth) while S_central rises above 1 (broadening); the ring weight makes total S non-monotonic."),
     ])
print("done")
