# Annular apertures via field-level Babinet
*(Phase 3 — DOF extension vs obstruction; thin-annulus/Bessel limit)*

## 1. Construction

In physical variables the RW integrals are
$$I_m(r,z)=\int_{\theta_{in}}^{\alpha} A(\theta)\sqrt{\cos\theta}\,
\mathrm{kern}_m(\theta)\,J_m(kr\sin\theta)\,e^{jkz\cos\theta}\,d\theta$$
so by linearity an annulus with obstruction ratio
$\varepsilon = r_{in}/r_{out} = \sin\theta_{in}/\sin\alpha$ (sine condition) is
the **difference of two disks at the same $(r,z,k)$**:
$$I_m^{ann} = I_m(\alpha) - I_m(\alpha_{in}),\qquad
\sin\alpha_{in}=\varepsilon\sin\alpha .$$
Subtraction is on the complex integrals (fields), keeping coherent cross
terms. $A(\theta)$ references the **outer** aperture. Implemented in
`mcdo/annular.py::compute_integrals_annular`; ε=0 regression vs the full disk
is exact (diff = 0).

## 2. Verified results (`output/03_annular/verify_annular.png`, linear-x y-cut)

**Transverse (X_NA=1.17, sinα=0.9):** central lobe narrows monotonically,
FWHM$_v$ 3.047 → 2.063 for ε 0 → 0.99, at the cost of strong sidelobes —
the classic annular resolution/sidelobe trade-off.

**Thin-annulus / Bessel limit:** at ε=0.99 the transverse profile approaches
Durnin's $J_0^2(v)$ —
| | max\|I − J₀²\| |
|---|---|
| X_NA = 0.13 (sinα=0.1) | 0.004 ✓ scalar limit |
| X_NA = 1.17 (sinα=0.9) | 0.163 — **vector-deformed Bessel beam** |

At high NA the $(1\pm\cos\theta)$ kernels and $E_z$ reshape the nondiffracting
beam (FWHM$_v$ 2.06 vs scalar 2.25). This vector correction to Bessel beams
feeds Phase 4 (axicon).

**DOF extension (axial FWHM ratio, theory $1/(1-\varepsilon^2)$):**

| ε | theory | X_NA=0.13 | X_NA=1.17 |
|---|---|---|---|
| 0.30 | 1.10 | 1.10 | 1.07 |
| 0.50 | 1.33 | 1.33 | 1.23 |
| 0.70 | 1.96 | 1.96 | 1.64 |
| 0.90 | 5.26 | 5.25 | 3.67 |
| 0.99 | 50.25 | 50.13 | 30.42 |

Paraxial theory is matched to 3 digits at low NA (validates the module);
at sinα=0.9 the extension falls ~40% short at large ε — consistent with the
old progress report's qualitative finding, now quantified with the validated
engine.

**Illumination:** once the annulus is thin, uniform vs Gaussian ($\alpha_t$=2)
barely differ (FWHM$_v$ 2.450 vs 2.537 at ε=0.7) — the ring transmits a
nearly constant amplitude slice of the beam.

## 3. Cost side and literature anchor

**Strehl/energy cost** (`output/03_annular/annular_energy_cost.png`): on-axis
peak follows the paraxial $(1-\varepsilon^2)^2$ at both NAs (0.417 vs 0.410 at
ε=0.6); central-lobe encircled energy collapses 0.76 → 0.055 as ε→1. The
resolution/DOF gain is paid in peak intensity and contrast.

**Sheppard & Wilson 1978 anchor** (`output/03_annular/verify_sheppard.png`).
Their Laguerre-Gaussian mode sum gives closed forms for a Gaussian annulus,
focal $I(v)=J_0^2(v)e^{-v^2a^2}$ (Eq. 27) and axial
$I(u)=e^{-u^2a^2/(1+u^2a^4)}/(1+u^2a^4)$ (Eq. 33). Realizing a Gaussian-ring
pupil (`apodization.gaussian_ring`) at low NA and fitting $a=0.200$ from the
focal envelope alone, the **predicted** axial profile (Eq. 33, not fitted)
matches ours to 0.8% (FWHM_u 8.2 vs 8.3) and the focal to 1.5% — an
independent-method confirmation of the annular machinery, complementing the
hard-edge J₀²/DOF checks above.

## 4. Remaining
Notebook 03 (done — `notebooks/03_annular.ipynb`).
