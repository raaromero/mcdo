"""Reproducible slide-deck builder for the mcdo results.

The deck is a *package artifact*, not an ad-hoc script: every slide is declared
in :data:`DECK` below, every figure is one produced by a canonical script in
``scripts/`` (never recomputed here), and the whole deck rebuilds with

    python -m mcdo.deck                 # -> output/deck/mcdo_results_deck.pptx
    python -m mcdo.deck --out FILE.pptx

Section structure and terminology follow the progress report
(``parallel_progress_report.pdf``); figures follow ``run_all.py`` and the
verification scripts. If a declared figure is missing, the build reports which
script regenerates it instead of silently drawing a placeholder.

Conventions (see docs/STANDARDS): one message per slide, bullets not bold,
no underscores in visible text, LaTeX in the slide notes, references last.
"""

from __future__ import annotations

import argparse
import os

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "output")

NAVY = RGBColor(0x0A, 0x3A, 0x66)
TITLE_BLUE = RGBColor(0x12, 0x60, 0x9F)
INK = RGBColor(0x1A, 0x1A, 0x1A)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
FONT = "Helvetica Neue"

# ---------------------------------------------------------------- figures ---
# figure key -> (path relative to output/, script that regenerates it)
FIGURES = {
    # Romallosa reproduction (canonical scripts, see run_all.py)
    "fig1_cw":  ("01_romallosa/panels/fig1_contours_p1.png", "scripts/fig1_contours.py"),
    "fig1_pls": ("01_romallosa/panels/fig1_contours_p2.png", "scripts/fig1_contours.py"),
    "fig2a":       ("01_romallosa/panels/fig2_profiles_p1.png",          "scripts/fig2_profiles.py"),
    "fig2b":       ("01_romallosa/panels/fig2_profiles_p2.png",          "scripts/fig2_profiles.py"),
    "fig3":        ("01_romallosa/fig3_energy.png",                      "scripts/fig3_energy.py"),
    "fig4a":       ("01_romallosa/panels/fig4_linfoot_p1.png",           "scripts/fig4_linfoot.py"),
    "fig4b":       ("01_romallosa/panels/fig4_linfoot_p2.png",           "scripts/fig4_linfoot.py"),
    "fig5":        ("01_romallosa/fig5_linfoot_2p.png",                  "scripts/fig5_linfoot_2p.py"),
    # Gaussian illumination
    "atlas_pa_e5_cw": ("atlas/pulsed_annular/eps0p5_cw.png", "scripts/config_atlas.py"),
    "atlas_pa_e5_2fs": ("atlas/pulsed_annular/eps0p5_2fs.png", "scripts/config_atlas.py"),
    "atlas_pa_e5_1fs": ("atlas/pulsed_annular/eps0p5_1fs.png", "scripts/config_atlas.py"),
    "atlas_pa_e9_cw": ("atlas/pulsed_annular/eps0p9_cw.png", "scripts/config_atlas.py"),
    "atlas_pa_e9_2fs": ("atlas/pulsed_annular/eps0p9_2fs.png", "scripts/config_atlas.py"),
    "atlas_pa_e9_1fs": ("atlas/pulsed_annular/eps0p9_1fs.png", "scripts/config_atlas.py"),
    "fpg_axial_lo": ("02_na_apodization/panels/fig_focal_plane_gaussian_p2.png", "scripts/fig_focal_plane_gaussian.py"),
    "fpg_axial_hi": ("02_na_apodization/panels/fig_focal_plane_gaussian_p5.png", "scripts/fig_focal_plane_gaussian.py"),
    "pulse_bw":  ("05_pulsed_pupils/panels/fig_pulse_characteristics_p3.png", "scripts/fig_pulse_characteristics.py"),
    "pulse_coh": ("05_pulsed_pupils/panels/fig_pulse_characteristics_p4.png", "scripts/fig_pulse_characteristics.py"),
    "nac_lo":     ("02_na_apodization/panels/verify_na_convergence_p1.png", "scripts/verify_na_convergence.py"),
    "nac_hi":     ("02_na_apodization/panels/verify_na_convergence_p2.png", "scripts/verify_na_convergence.py"),
    "naprof_uni": ("02_na_apodization/panels/fig_na_profiles_p1.png", "scripts/fig_na_profiles.py"),
    "naprof_gau": ("02_na_apodization/panels/fig_na_profiles_p2.png", "scripts/fig_na_profiles.py"),
    "mc_launch":  ("06_monte_carlo/verify_launcher.png",           "scripts/verify_launcher.py"),
    "mc_launch_i":("06_monte_carlo/verify_launcher_intensity.png",  "scripts/verify_launcher.py"),
    "mc_vector":  ("06_monte_carlo/verify_mc_vector.png",           "scripts/verify_mc_vector.py"),
    "mc_clear":   ("06_monte_carlo/verify_mc_clear.png",            "scripts/verify_mc_clear.py"),
    "mc_conv":    ("06_monte_carlo/profiles_vs_N.png",              "scripts/verify_mc_clear.py"),
    "mc_var":     ("06_monte_carlo/mc_variance.png",                "scripts/verify_mc_clear.py"),
    "apod_alpha":  ("02_na_apodization/panels/fig_apodization_inputs_p3.png", "scripts/fig_apodization_inputs.py"),
    "apod_maps":   ("02_na_apodization/fig_apodization_maps.png",             "scripts/fig_apodization_inputs.py"),
    "apod_in":     ("02_na_apodization/panels/fig_apodization_inputs_p1.png", "scripts/fig_apodization_inputs.py"),
    "apod_out":    ("02_na_apodization/panels/fig_apodization_inputs_p2.png", "scripts/fig_apodization_inputs.py"),
    "parax_a":     ("02_na_apodization/panels/verify_tanaka_paraxial_p1.png", "scripts/verify_tanaka_paraxial.py"),
    "parax_b":     ("02_na_apodization/panels/verify_tanaka_paraxial_p2.png", "scripts/verify_tanaka_paraxial.py"),
    # NA convergence
    "nac3":        ("02_na_apodization/panels/verify_na_convergence_p3.png",  "scripts/verify_na_convergence.py"),
    "apt1":        ("02_na_apodization/panels/verify_apod_thresholds_p1.png", "scripts/verify_apod_thresholds.py"),
    "apt3":        ("02_na_apodization/panels/verify_apod_thresholds_p2.png", "scripts/verify_apod_thresholds.py"),
    # Annular apertures
    "ann1":        ("03_annular/panels/verify_annular_p1.png",           "scripts/verify_annular.py"),
    "ann2":        ("03_annular/panels/verify_annular_p2.png",           "scripts/verify_annular.py"),
    "ann3":        ("03_annular/panels/verify_annular_p3.png",           "scripts/verify_annular.py"),
    "ann4":        ("03_annular/panels/verify_annular_p4.png",           "scripts/verify_annular.py"),
    "anne1":       ("03_annular/panels/verify_annular_energy_p1.png",    "scripts/verify_annular_energy.py"),
    "anne2":       ("03_annular/panels/verify_annular_energy_p2.png",    "scripts/verify_annular_energy.py"),
    "shep1":       ("03_annular/panels/verify_sheppard_p1.png",          "scripts/verify_sheppard.py"),
    # Configuration atlas (one card per configuration: 2-D map + cross-sections)
    "atlas_na_0p1": ("atlas/NA/NA_0.1.png", "scripts/config_atlas.py"),
    "atlas_na_0p3": ("atlas/NA/NA_0.3.png", "scripts/config_atlas.py"),
    "atlas_na_0p5": ("atlas/NA/NA_0.5.png", "scripts/config_atlas.py"),
    "atlas_na_0p8": ("atlas/NA/NA_0.8.png", "scripts/config_atlas.py"),
    "atlas_na_1p0": ("atlas/NA/NA_1.0.png", "scripts/config_atlas.py"),
    "atlas_na_1p2": ("atlas/NA/NA_1.2.png", "scripts/config_atlas.py"),
    "atlas_g_at0": ("atlas/gaussian/at0.png", "scripts/config_atlas.py"),
    "atlas_g_at0p5": ("atlas/gaussian/at0p5.png", "scripts/config_atlas.py"),
    "atlas_g_at1": ("atlas/gaussian/at1.png", "scripts/config_atlas.py"),
    "atlas_g_at2": ("atlas/gaussian/at2.png", "scripts/config_atlas.py"),
    "atlas_g_at4": ("atlas/gaussian/at4.png", "scripts/config_atlas.py"),
    "atlas_e_0p0": ("atlas/annular/eps0.0.png", "scripts/config_atlas.py"),
    "atlas_e_0p3": ("atlas/annular/eps0.3.png", "scripts/config_atlas.py"),
    "atlas_e_0p5": ("atlas/annular/eps0.5.png", "scripts/config_atlas.py"),
    "atlas_e_0p7": ("atlas/annular/eps0.7.png", "scripts/config_atlas.py"),
    "atlas_e_0p9": ("atlas/annular/eps0.9.png", "scripts/config_atlas.py"),
    "atlas_e_0p99": ("atlas/annular/eps0.99.png", "scripts/config_atlas.py"),
    "atlas_p_5fs": ("atlas/pulsed/5fs.png", "scripts/config_atlas.py"),
    "atlas_p_3fs": ("atlas/pulsed/3fs.png", "scripts/config_atlas.py"),
    "atlas_p_2fs": ("atlas/pulsed/2fs.png", "scripts/config_atlas.py"),
    "atlas_p_1p5fs": ("atlas/pulsed/1p5fs.png", "scripts/config_atlas.py"),
    "atlas_p_1fs": ("atlas/pulsed/1fs.png", "scripts/config_atlas.py"),
    "cmp_full_NA_0p1": ("atlas_components/full/NA/0p1.png", "scripts/vector_atlas.py"),
    "cmp_full_NA_0p8": ("atlas_components/full/NA/0p8.png", "scripts/vector_atlas.py"),
    "cmp_full_NA_1p2": ("atlas_components/full/NA/1p2.png", "scripts/vector_atlas.py"),
    "cmp_full_gaussian_4p0": ("atlas_components/full/gaussian/4p0.png", "scripts/vector_atlas.py"),
    "cmp_full_annular_0p9": ("atlas_components/full/annular/0p9.png", "scripts/vector_atlas.py"),
    # New studies filling the flow gaps
    "pupil_geom":  ("03_annular/panels/fig_pupil_geometry_p1.png",      "scripts/fig_pupil_geometry.py"),
    "pupil_input": ("03_annular/panels/fig_pupil_geometry_p2.png",      "scripts/fig_pupil_geometry.py"),
    "annsca_rmse": ("03_annular/panels/verify_annular_scalar_p1.png",   "scripts/verify_annular_scalar.py"),
    "annsca_fwhm": ("03_annular/panels/verify_annular_scalar_p2.png",   "scripts/verify_annular_scalar.py"),
    "wl_rmse":     ("02_na_apodization/panels/verify_wavelength_p1.png","scripts/verify_wavelength.py"),
    "wl_width":    ("02_na_apodization/panels/verify_wavelength_p2.png","scripts/verify_wavelength.py"),
    # Few-cycle pulse characteristics
    "pulse_lam":   ("05_pulsed_pupils/panels/fig_pulse_characteristics_p1.png", "scripts/fig_pulse_characteristics.py"),
    "pulse_freq":  ("05_pulsed_pupils/panels/fig_pulse_characteristics_p2.png", "scripts/fig_pulse_characteristics.py"),
    # When does Gaussian illumination behave like uniform
    "naprof_comp": ("02_na_apodization/panels/fig_na_profiles_p3.png", "scripts/fig_na_profiles.py"),
    "fpg_prof_lo": ("02_na_apodization/panels/fig_focal_plane_gaussian_p1.png", "scripts/fig_focal_plane_gaussian.py"),
    "fpg_cont_lo": ("02_na_apodization/panels/fig_focal_plane_gaussian_p3.png", "scripts/fig_focal_plane_gaussian.py"),
    "fpg_prof_hi": ("02_na_apodization/panels/fig_focal_plane_gaussian_p4.png", "scripts/fig_focal_plane_gaussian.py"),
    "fpg_cont_hi": ("02_na_apodization/panels/fig_focal_plane_gaussian_p6.png", "scripts/fig_focal_plane_gaussian.py"),
    "metric_choice": ("02_na_apodization/panels/fig_metric_choice_p1.png", "scripts/fig_metric_choice.py"),
    "illum_row":  ("02_na_apodization/panels/fig_aperture_illumination_row.png", "scripts/fig_aperture_illumination.py"),
    "illum_edge": ("02_na_apodization/panels/fig_aperture_illumination_p5.png", "scripts/fig_aperture_illumination.py"),
    # Pulsed sources with annular apertures
    "pag_ratio": ("05_pulsed_pupils/panels/verify_pulsed_annular_gaussian_p1.png", "scripts/verify_pulsed_annular_gaussian.py"),
    "pag_pulse": ("05_pulsed_pupils/panels/verify_pulsed_annular_gaussian_p2.png", "scripts/verify_pulsed_annular_gaussian.py"),
    "pa_axial":  ("05_pulsed_pupils/panels/verify_pulsed_annular_p3.png", "scripts/verify_pulsed_annular.py"),
    "pa_dof":    ("05_pulsed_pupils/panels/verify_pulsed_annular_p4.png", "scripts/verify_pulsed_annular.py"),
    "pa_trans":  ("05_pulsed_pupils/panels/verify_pulsed_annular_p1.png", "scripts/verify_pulsed_annular.py"),
    "pa_linfoot":("05_pulsed_pupils/panels/verify_pulsed_annular_p2.png", "scripts/verify_pulsed_annular.py"),
    "shep2":       ("03_annular/panels/verify_sheppard_p2.png",          "scripts/verify_sheppard.py"),
}

# ---------------------------------------------------------------- equations --
#: Review stages. The package is built and merged one stage at a time: a stage
#: is reviewed on its own deck, and only once it is accepted does its code move
#: to main. ``sections`` names the DECK sections that belong to the stage and
#: ``outputs`` the output subdirectory the stage writes into.
STAGES = {
    "1": {
        "key": "romallosa",
        "title": "Stage 1 - Romallosa (2003) replication",
        "sections": ["Romallosa (2003) replication"],
    },
    "2": {
        "key": "gaussian",
        "title": "Stage 2 - Gaussian input",
        "sections": ["Gaussian input"],
    },
    "3": {
        "key": "scalar_limit",
        "title": "Stage 3 - Numerical aperture: uniform against Gaussian input",
        "sections": ["Numerical aperture: uniform against Gaussian input"],
    },
    "4": {
        "key": "annular",
        "title": "Stage 4 - Annular apertures",
        "sections": ["Annular apertures"],
    },
    "6": {
        "key": "monte_carlo",
        "title": "Stage 6 - Monte Carlo in the clear limit",
        "sections": ["Monte Carlo in the clear limit"],
    },
    "5": {
        "key": "pulsed_annular",
        "title": "Stage 5 - Pulsed sources with annular apertures",
        "sections": ["Pulsed sources with annular apertures"],
    },
}


def stage_outputs(stage_id):
    """Figures and scripts a stage actually uses, read from its own slides.

    Derived from the slides rather than from a directory name, so the listing
    can never drift out of step with what the stage presents.
    """
    st = STAGES[stage_id]
    keep, keys = False, []
    for item in DECK:
        if item[0] == "section":
            keep = item[1] in st["sections"]
        elif keep and item[0] == "slide" and item[3]:
            keys.append(item[3])
    figs = {k: FIGURES[k] for k in dict.fromkeys(keys) if k in FIGURES}
    scripts = sorted({script for _, script in figs.values()})
    dirs = sorted({os.path.dirname(rel) for rel, _ in figs.values()})
    return figs, scripts, dirs


def stage_deck(stage_id):
    """The DECK entries for one stage, plus its title and outputs slides."""
    st = STAGES[stage_id]
    figs, scripts, dirs = stage_outputs(stage_id)
    items = [("title", st["title"])]
    keep = False
    for item in DECK:
        if item[0] == "section":
            keep = item[1] in st["sections"]
        if keep:
            items.append(item)
    bullets = [
        (0, "Everything in this stage is produced by the package, with no manual steps"),
        (0, f"Scripts: {len(scripts)}, each run by 'python run_all.py'"),
    ]
    bullets += [(1, os.path.basename(sc)) for sc in scripts]
    bullets += [
        (0, f"Figures: {len(figs)}, written to " + ", ".join("output/" + d for d in dirs)),
        (0, "Rebuild this stage: python run_all.py --only "
            + " ".join(os.path.basename(sc) for sc in scripts)),
        (0, f"Rebuild this deck: python -m mcdo.deck --stage {stage_id}"),
    ]
    items.append(("section", "Outputs for this stage"))
    items.append(("slide", "What this stage produces", bullets, None, None))
    return items


LX = {
    "components": r"E_x(P)=-i(I_0+I_2\cos 2\phi),\quad E_y(P)=-iI_2\sin 2\phi,\quad E_z(P)=-2iI_1\cos\phi",
    "integrals": (r"I_m(u,v)=\int_0^{\alpha}\sqrt{\cos\theta}\,g_m(\theta)\,"
                  r"J_m\!\left(\frac{v\sin\theta}{\sin\alpha}\right)"
                  r"\exp\!\left(\frac{iu\cos\theta}{\sin^2\alpha}\right)d\theta"
                  "\n\n"
                  r"g_0=\sin\theta(1+\cos\theta),\quad g_1=\sin^2\theta,\quad g_2=\sin\theta(1-\cos\theta)"),
    "coords": (r"u=\frac{2\pi}{\lambda}\sin^2\!\alpha\cdot z,\quad "
               r"v=\frac{2\pi}{\lambda}\sin\alpha\cdot r,\quad "
               r"\alpha=\arcsin\!\left(\frac{\mathrm{NA}}{n}\right)"),
    "apod": (r"A(\theta)=\exp\!\left(-\alpha\frac{\sin^2\theta}{\sin^2\alpha_{\max}}\right),"
             r"\qquad \alpha=\left(\frac{r_{\mathrm{aperture}}}{w_{\mathrm{beam}}}\right)^2"),
    "metrics": (r"\Delta\mathrm{FWHM}=\frac{\mathrm{FWHM}_{\mathrm{vector}}-\mathrm{FWHM}_{\mathrm{scalar}}}{\mathrm{FWHM}_{\mathrm{scalar}}}\times 100\%"
                "\n\n"
                r"\mathrm{RMSE}=\sqrt{\frac{1}{N}\sum_i\left(I_{\mathrm{vector}}(r_i)-I_{\mathrm{scalar}}(r_i)\right)^2}"),
    "babinet": (r"E_{\mathrm{annular}}(\epsilon)=E_{\mathrm{disk}}(\mathrm{NA}_{\mathrm{outer}})"
                r"-E_{\mathrm{disk}}(\mathrm{NA}_{\mathrm{inner}}),\qquad "
                r"\epsilon=\frac{r_{\mathrm{inner}}}{r_{\mathrm{outer}}}"
                "\n\n"
                r"\mathrm{DOF}(\epsilon)=\frac{\mathrm{DOF}_0}{1-\epsilon^2}"),
    "scalar": (r"U(u,v)=\int_0^{\alpha}A(\theta)\sqrt{\cos\theta}\,\sin\theta\,"
               r"J_0\!\left(\frac{v\sin\theta}{\sin\alpha}\right)"
               r"\exp\!\left(\frac{iu\cos\theta}{\sin^2\alpha}\right)d\theta,\qquad I=|U|^2"
               "\n\n"
               r"\text{no }(1\pm\cos\theta)\text{ kernel: polarization is absent}"
               "\n\n"
               r"I(v)=\left[\frac{2J_1(v)}{v}\right]^2\quad\text{(Airy, paraxial limit)}"),
    "pulse": (r"|E(\omega)|^2\propto\exp\!\left[-\frac{(\omega-\omega_c)^2}{2a}\right],\qquad a=\frac{2\ln 2}{\tau^2}"
              "\n\n"
              r"|E(P)|^2=\int|E(\omega)|^2\,|E(P;\omega)|^2\,d\omega"
              "\n\n"
              r"\tau_{\mathrm{crit}}=\frac{\lambda_c}{2c}\quad\text{(coherence length equals the Nyquist interval)}"),
    "sheppard": (r"\text{focal plane:}\quad I(v)=J_0^2(v)\,e^{-a^2v^2}"
                 "\n\n"
                 r"\text{on axis:}\quad I(u)=\frac{1}{1+u^2a^4}\exp\!\left(\frac{-u^2a^2}{1+u^2a^4}\right)"
                 "\n\n"
                 r"a\ \text{sets the ring width};\ a\to 0\ \text{is an infinitely thin ring}"),
    "linfoot": (r"F=1-\frac{\langle(r-a)^2\rangle}{\langle r^2\rangle},\quad "
                r"S=\frac{\langle a^2\rangle}{\langle r^2\rangle},\quad "
                r"Q=\frac{\langle|a||r|\rangle}{\langle r^2\rangle},\quad 2Q-S=F"),
}


# Plain-language caption rendered above each equation, so no formula appears
# on a slide without saying what it is and what its symbols mean.
LX_CAPTION = {
    "scalar": "Scalar Debye integral: the focal field with polarization ignored. "
              "u and v are the axial and radial optical coordinates, alpha the aperture "
              "half-angle, A the pupil amplitude.",
    "components": "The three focal field components for an x-polarized input. "
                  "phi is the azimuth; the axial component is absent from scalar theory.",
    "integrals": "The three Richards-Wolf diffraction integrals. theta runs over the "
                 "focusing cone, the Bessel functions carry the radial dependence, and "
                 "the angular weights distinguish the three components.",
    "coords": "Optical coordinates: dimensionless axial and radial positions that make "
              "the result scale with wavelength and numerical aperture.",
    "apod": "Gaussian pupil apodization. The truncation coefficient alpha is the squared "
            "ratio of aperture radius to beam waist, and sets the amplitude at the rim.",
    "pulse": "Pulse spectrum and the time-integrated focal intensity: a Gaussian in "
             "frequency of width set by the duration tau, summed incoherently over the band.",
    "metrics": "The two comparison metrics: the fractional error in predicted spot size, "
               "and the point-by-point error between normalized profiles.",
    "babinet": "Annular field by Babinet subtraction, and the paraxial depth-of-focus law. "
               "epsilon is the inner over outer pupil radius.",
    "sheppard": "Sheppard and Wilson closed forms for a Gaussian annulus, from a "
                "Laguerre-Gaussian mode sum. The single parameter a sets the ring width.",
    "linfoot": "Linfoot criteria comparing a test profile a against reference r: "
               "fidelity, structural content and correlation quality.",
}

# ------------------------------------------------------------------- deck ----
# ("title", str)                        -> title slide
# ("section", str)                      -> section divider
# ("slide", title, bullets, figure_key or None, latex_key or None)
#   bullets: list of (level, text)
DECK = [
    ("title", "Progress Report"),

    ("section", "Summary"),
    ("slide", "Summary: goal, problem and gap", [
        (0, "Long-term goal: Monte Carlo simulation of high-NA optical pulses with extended depth of focus (annular apertures) in scattering media"),
        (0, "Core problem"),
        (1, "Imaging through scattering media requires both tight focusing (high NA) and scattering simulation (Monte Carlo)"),
        (1, "Current Monte Carlo implementations use scalar diffraction, which breaks down at high NA"),
        (1, "Optical pulses below 2 fs exhibit spectral broadening that further complicates focusing"),
        (0, "Gap"),
        (1, "No existing tool combines high-NA vector diffraction, pulsed sources, and Monte Carlo scattering"),
    ], None, None),
    ("slide", "Summary: what was done and what is next", [
        (0, "Completed"),
        (1, "Reproduced the Romallosa (2003) figures, matching their Linfoot criteria"),
        (1, "Added Gaussian apodization, validated against the paraxial result at low numerical aperture"),
        (1, "Mapped where scalar theory fails: Gaussian tolerates higher numerical aperture than uniform"),
        (1, "Threshold is wavelength independent; the spot size is not"),
        (1, "Implemented annular apertures: depth of focus extends, at a cost in peak intensity"),
        (1, "Scalar theory fails earlier as the ring thins, and the Gaussian advantage disappears"),
        (0, "Next steps"),
        (1, "Monte Carlo photon tracing, driven by these focal fields"),
        (1, "Later: Monte Carlo photon tracing in scattering media"),
    ], None, None),
    ("section", "Background"),
    ("slide", "Research context", [
        (0, "Key applications"),
        (1, "Mouse embryo imaging in thick biological samples"),
        (1, "Integrated circuit inspection"),
        (1, "Attosecond x-ray generation"),
    ], None, None),
    ("slide", "Scalar diffraction theory", [
        (0, "Reliable for numerical apertures at or below 0.5"),
        (0, "Computationally efficient, but carries no polarization effects"),
        (0, "Scalar Debye integral: the focal field with polarization ignored. u and v are the axial and radial optical coordinates, alpha the aperture half-angle, A the pupil amplitude."),
    ], None, "scalar"),
    ("slide", "Richards-Wolf vector diffraction theory", [
        (0, "Handles tightly focused beams above numerical aperture 0.5"),
        (0, "Full vector field calculation that accounts for polarization"),
        (0, "Assumes monochromatic illumination"),
    ], None, None),
    ("slide", "Monte Carlo methods", [
        (0, "The gold standard for tissue optics and established for random media"),
        (0, "Conventionally driven by a scalar diffraction source"),
    ], None, None),
    ("slide", "Vector field components", [
        (0, "Light focused through a high-NA lens must be treated as a vector wave"),
        (0, "The axial component becomes significant at high numerical aperture"),
        (0, "The three focal field components for an x-polarized input. phi is the azimuth; the axial component is absent from scalar theory."),
    ], None, "components"),
    ("slide", "Diffraction integrals", [
        (0, "I0 is the main focusing term and gives the Airy pattern"),
        (0, "I1 carries the longitudinal field, which appears at high numerical aperture"),
        (0, "I2 is the cross-polarization correction, which breaks circular symmetry"),
        (0, "The three Richards-Wolf diffraction integrals. theta runs over the focusing cone, the Bessel functions carry the radial dependence, and the angular weights distinguish the three components."),
    ], None, "integrals"),
    ("slide", "Optical coordinates", [
        (0, "Normalized coordinates make the result scale with wavelength and numerical aperture"),
        (0, "The origin is the geometric focus, so one calculation serves any wavelength and numerical aperture"),
        (0, "Optical coordinates: dimensionless axial and radial positions that make the result scale with wavelength and numerical aperture."),
    ], None, "coords"),
    ("section", "Optical pulses"),
    ("slide", "Few-cycle pulse characteristics", [
        (0, "Pulse durations below one femtosecond, in the few-cycle regime"),
        (0, "Spectral width grows as the inverse of the duration, so a one femtosecond pulse spans several hundred terahertz"),
        (0, "Below a critical duration of a quarter wave period, 1.25 fs at 750 nm, the coherence length drops under the Nyquist interval of 375 nm"),
        (0, "Beyond that point the carrier cannot be represented and the focus deteriorates rapidly"),
        (0, "Pulse spectrum and the time-integrated focal intensity: a Gaussian in frequency of width set by the duration tau, summed incoherently over the band."),
    ], "pulse_lam", "pulse"),
    ("slide", "The same spectrum against frequency", [
        (0, "Against frequency the spectrum is a symmetric Gaussian about the carrier"),
        (0, "This is the variable the spectral integration runs over; the long-wavelength tail in the previous slide is only the change of variable"),
    ], "pulse_freq", None),

    ("slide", "Focal field for a 5 fs pulse", [
        (0, "Two-dimensional map with cross-sections for a 5 fs pulse at numerical aperture 0.8"),
        (0, "Focal width 475 nm, depth of focus 2.40 µm, against 475 nm and 2.40 µm for continuous wave"),
    ], "atlas_p_5fs", None),
    ("slide", "Focal field for a 3 fs pulse", [
        (0, "Two-dimensional map with cross-sections for a 3 fs pulse at numerical aperture 0.8"),
        (0, "Focal width 475 nm, depth of focus 2.40 µm, against 475 nm and 2.40 µm for continuous wave"),
    ], "atlas_p_3fs", None),
    ("slide", "Focal field for a 2 fs pulse", [
        (0, "Two-dimensional map with cross-sections for a 2 fs pulse at numerical aperture 0.8"),
        (0, "Focal width 500 nm, depth of focus 2.40 µm, against 475 nm and 2.40 µm for continuous wave"),
    ], "atlas_p_2fs", None),
    ("slide", "Focal field for a 1.5 fs pulse", [
        (0, "Two-dimensional map with cross-sections for a 1.5 fs pulse at numerical aperture 0.8"),
        (0, "Focal width 500 nm, depth of focus 2.40 µm, against 475 nm and 2.40 µm for continuous wave"),
    ], "atlas_p_1p5fs", None),
    ("slide", "Focal field for a 1 fs pulse", [
        (0, "Two-dimensional map with cross-sections for a 1 fs pulse at numerical aperture 0.8"),
        (0, "Focal width 500 nm, depth of focus 2.40 µm, against 475 nm and 2.40 µm for continuous wave"),
    ], "atlas_p_1fs", None),
    ("slide", "Bandwidth against pulse duration", [
        (0, "Shorter pulses carry proportionally more bandwidth, so a few-cycle pulse can no longer be treated as one wavelength"),
        (0, "Below about 2 fs the spectrum spans a full octave around the 750 nm centre wavelength"),
    ], "pulse_bw", None),
    ("slide", "Coherence length against pulse duration", [
        (0, "The coherence length sets how finely the frequency axis has to be sampled"),
        (0, "At 1.2 fs it falls to 360 nm, just inside the 375 nm Nyquist limit for a 750 nm centre wavelength"),
    ], "pulse_coh", None),
    ("section", "Romallosa (2003) replication"),
    ("slide", "Focal intensity distribution, continuous wave", [
        (0, "Contours are percent of peak; the orange contour is the half maximum"),
        (0, "Numerical aperture 0.8, centre wavelength 750 nm, refractive index 1.3"),
        (0, "The dark ring is a true zero because this cut lies along the y-axis, where the other two field components vanish"),
    ], "fig1_cw", None),
    ("slide", "Focal intensity distribution, 1 fs pulse", [
        (0, "The same map for a 1 fs pulse at numerical aperture 0.8, on the same scale"),
        (0, "The dark ring fills in: each frequency puts its zero at a different radius, so the ensemble never reaches zero anywhere"),
        (0, "That filled-in pedestal is the loss of focal quality a few-cycle pulse brings"),
    ], "fig1_pls", None),
    ("slide", "Transverse intensity profile", [
        (0, "Cut along the direction where only the transverse component survives, the same cut the paper plots"),
        (0, "Pulsing fills the zeros and slows the decay away from focus"),
        (0, "Structural content 1.060 against the published 1.062, a difference of two parts in a thousand"),
        (0, "Linfoot criteria comparing a test profile a against reference r: fidelity, structural content and correlation quality."),
    ], "fig2a", "linfoot"),
    ("slide", "Axial intensity profile", [
        (0, "The same comparison along the optical axis"),
        (0, "Structural content 1.058 against the published 1.057"),
        (0, "Continuous-wave focal width 472.8 nm, matching the published value"),
    ], "fig2b", None),
    ("slide", "Energy within the focal width", [
        (0, "Each marker set is one numerical aperture, from 0.1 to 1.2"),
        (0, "The curves collapse together, so the loss of encircled energy is not an aperture effect"),
        (0, "Energy falls linearly with duration below about 2 fs, following the published reference line"),
    ], "fig3", None),
    ("slide", "Fidelity and structural content versus numerical aperture", [
        (0, "Filled markers: structural content, which rises above unity as pulsing broadens the focus"),
        (0, "Open markers: fidelity, which falls below unity for the same reason"),
        (0, "Both are flat across numerical aperture, reproducing the insensitivity the paper reports"),
    ], "fig4a", None),
    ("slide", "Fidelity and structural content versus pulse width", [
        (0, "Numerical aperture 0.8, centre wavelength 750 nm"),
        (0, "Both criteria return to unity for long pulses and depart only below about 2 fs"),
        (0, "Solid lines are the reference curves quoted in the paper, which the calculation follows"),
        (0, "The departure sets in at the critical duration derived earlier, 1.25 fs"),
    ], "fig4b", None),
    ("slide", "Two-photon excitation microscope", [
        (0, "The two-photon response is the squared intensity, so it weights the focal core more heavily"),
        (0, "Departures from unity are roughly a third of the single-photon case at the same duration"),
        (0, "Spectral broadening therefore degrades two-photon excitation more weakly, as the paper concludes"),
    ], "fig5", None),
    ("section", "Gaussian input"),
    ("slide", "A note on what is plotted from here on", [
        (0, "The replication above follows the paper and plots the x-polarized intensity along the y-axis, where the other two components vanish"),
        (0, "Every result from here on plots the total intensity of all three components, averaged over azimuth"),
        (0, "The two agree on axis and separate off axis as numerical aperture rises, which is the effect measured in the next section"),
    ], None, None),

    ("slide", "Incorporating a Gaussian beam into Richards-Wolf", [
        (0, "Romallosa assumes uniform illumination, a flat amplitude across the aperture"),
        (0, "Real lasers are Gaussian, so an apodization factor multiplies every diffraction integral"),
        (0, "The truncation coefficient sets how hard the aperture clips the beam"),
        (0, "Gaussian pupil apodization. The truncation coefficient alpha is the squared ratio of aperture radius to beam waist, and sets the amplitude at the rim."),
    ], None, "apod"),
    ("slide", "How the input changes with the truncation coefficient", [
        (0, "Dashed: uniform illumination, which fills the pupil evenly"),
        (0, "Coloured: increasing truncation coefficient, concentrating the light toward the centre"),
        (0, "A coefficient near zero recovers uniform illumination and four or more is effectively untruncated"),
    ], "apod_in", None),
    ("slide", "The focus that results from each input", [
        (0, "Numerical aperture 0.8, centre wavelength 750 nm"),
        (0, "Each curve is the focus produced by the input of the same colour"),
        (0, "Stronger truncation uses less of the aperture, so the focus is wider"),
        (0, "Uniform illumination gives the tightest focus and the strongest side lobes"),
    ], "apod_out", None),
    ("slide", "When does Gaussian illumination behave like uniform?", [
        (0, "The pupil face for increasing truncation coefficient, with the amplitude surviving at the aperture edge"),
        (0, "A coefficient near zero fills the aperture evenly; a coefficient of one leaves 37 per cent at the edge; four or more leaves about 2 per cent"),
    ], "illum_row", None),
    ("slide", "Edge amplitude decides when the two are interchangeable", [
        (0, "Edge amplitude falls as the exponential of minus the truncation coefficient"),
        (0, "Below about 0.01 the edge is within one per cent of uniform, so the two calculations are interchangeable"),
        (0, "Above four the beam is narrower than the aperture and the truncation stops mattering"),
    ], "illum_edge", None),
    ("slide", "Axial profile at low numerical aperture", [
        (0, "Along the axis at numerical aperture 0.1, vector and scalar theory agree and Gaussian input only lengthens the focus"),
        (0, "The half-maximum line marks the depth of focus"),
    ], "fpg_axial_lo", None),
    ("slide", "Axial profile at high numerical aperture", [
        (0, "At numerical aperture 0.9 the scalar prediction no longer tracks the vector result along the axis"),
        (0, "Gaussian input keeps the two closer together than uniform input does"),
    ], "fpg_axial_hi", None),
    ("slide", "Focal width against the truncation coefficient", [
        (0, "Numerical aperture 0.8, centre wavelength 750 nm"),
        (0, "The focal width grows steadily as the truncation coefficient rises, from 473 nm at uniform illumination"),
        (0, "Stronger truncation uses less of the aperture, which is what broadens the focus"),
    ], "apod_alpha", None),
    ("slide", "Field maps for uniform and Gaussian input, side by side", [
        (0, "Iso-intensity contours of the total intensity in the r-z plane, on the same scale"),
        (0, "The Gaussian focus is wider and longer because the pupil edge carries almost no light"),
    ], "apod_maps", None),
    ("slide", "Focal plane intensity at numerical aperture 0.1", [
        (0, "Solid: Richards-Wolf with a Gaussian input; dashed: the scalar Debye result for the same input"),
        (0, "The two lie on top of one another, so the apodized implementation matches the analytic result"),
        (0, "Dotted: uniform illumination, narrower because it uses the full aperture"),
    ], "fpg_prof_lo", None),
    ("slide", "Iso-intensity contours at numerical aperture 0.1", [
        (0, "Contours of the same field in the r-z plane, dashed lines at the Airy radius of 4.575 µm"),
        (0, "The focus is long and smooth, with no structure beyond the central lobe"),
    ], "fpg_cont_lo", None),
    ("slide", "Focal plane intensity at numerical aperture 0.9", [
        (0, "The same three curves at high numerical aperture"),
        (0, "The vector and scalar curves now separate, by about 3 per cent in integrated profile area"),
        (0, "The Gaussian vector field is broader because the longitudinal component has appeared"),
    ], "fpg_prof_hi", None),
    ("slide", "Iso-intensity contours at numerical aperture 0.9", [
        (0, "Contours of the same field, dashed lines at the Airy radius of 0.508 µm"),
        (0, "The focus is an order of magnitude shorter in z than at numerical aperture 0.1"),
    ], "fpg_cont_hi", None),

    ("slide", "Gaussian input at low numerical aperture against the known scalar result", [
        (0, "Thick faint curves: the paraxial truncated-Gaussian reference"),
        (0, "Thin curves: the vector calculation, which overlaps the reference for every truncation coefficient"),
    ], "parax_a", None),
    ("slide", "Deviation from the known low-numerical-aperture result", [
        (0, "Each curve is one truncation coefficient"),
        (0, "All of them sit near the numerical floor, so the apodized implementation is validated before high numerical aperture"),
    ], "parax_b", None),
    ("slide", "Focal field for truncation coefficient 0", [
        (0, "Two-dimensional map with cross-sections for truncation coefficient 0 at numerical aperture 0.8"),
        (0, "Focal width 475 nm, depth of focus 2.40 µm, 1.00 times the uniform depth"),
    ], "atlas_g_at0", None),
    ("slide", "Focal field for truncation coefficient 0.5", [
        (0, "Two-dimensional map with cross-sections for truncation coefficient 0.5 at numerical aperture 0.8"),
        (0, "Focal width 500 nm, depth of focus 2.40 µm, 1.00 times the uniform depth"),
    ], "atlas_g_at0p5", None),
    ("slide", "Focal field for truncation coefficient 1", [
        (0, "Two-dimensional map with cross-sections for truncation coefficient 1 at numerical aperture 0.8"),
        (0, "Focal width 525 nm, depth of focus 2.49 µm, 1.04 times the uniform depth"),
    ], "atlas_g_at1", None),
    ("slide", "Focal field for truncation coefficient 2", [
        (0, "Two-dimensional map with cross-sections for truncation coefficient 2 at numerical aperture 0.8"),
        (0, "Focal width 600 nm, depth of focus 2.77 µm, 1.15 times the uniform depth"),
    ], "atlas_g_at2", None),
    ("slide", "Focal field for truncation coefficient 4", [
        (0, "Two-dimensional map with cross-sections for truncation coefficient 4 at numerical aperture 0.8"),
        (0, "Focal width 725 nm, depth of focus 3.78 µm, 1.58 times the uniform depth"),
    ], "atlas_g_at4", None),
    ("slide", "All three components at truncation coefficient 4", [
        (0, "Total intensity including the longitudinal and cross-polarization terms"),
    ], "cmp_full_gaussian_4p0", None),
    ("section", "Numerical aperture: uniform against Gaussian input"),
    ("slide", "When does scalar theory diverge from vector theory?", [
        (0, "Scalar theory is fast but approximate, vector theory is accurate but slower"),
        (0, "The question is where the approximation stops being acceptable, for each input"),
        (0, "Key result: Gaussian illumination tolerates the scalar approximation to higher numerical aperture than uniform, because it suppresses the steep rays that generate the longitudinal field"),
    ], None, None),
    ("slide", "Focal profiles at low numerical aperture", [
        (0, "At numerical aperture 0.1 the vector and scalar profiles lie on top of the analytic Airy pattern"),
        (0, "Nothing distinguishes the three theories here, which is why scalar diffraction is used at low aperture"),
    ], "nac_lo", None),
    ("slide", "Focal profiles at high numerical aperture", [
        (0, "At numerical aperture 1.2 the total vector intensity is measurably broader than the scalar prediction"),
        (0, "The extra width is the longitudinal field, which scalar theory has no way to represent"),
    ], "nac_hi", None),
    ("slide", "Focal profiles against numerical aperture, uniform input", [
        (0, "Uniform illumination, centre wavelength 750 nm, numerical aperture rising through the series"),
        (0, "The vector profile pulls away from the scalar one as the marginal rays gain weight"),
    ], "naprof_uni", None),
    ("slide", "Focal profiles against numerical aperture, Gaussian input", [
        (0, "Gaussian input with truncation coefficient 4, centre wavelength 750 nm"),
        (0, "The same series stays closer to scalar theory because the pupil edge carries little light"),
    ], "naprof_gau", None),
    ("slide", "Choosing the metric: why focal width", [
        (0, "All three measures compare the same pair of profiles as numerical aperture rises"),
        (0, "The focal-width difference registers the departure first, near numerical aperture 0.4"),
        (0, "Root-mean-square error follows only later, and Pearson correlation never crosses one per cent at all"),
        (0, "At numerical aperture 0.8 the predicted spot size is already wrong by four per cent while the correlation still reads 0.999"),
        (0, "The two comparison metrics: the fractional error in predicted spot size, and the point-by-point error between normalized profiles."),
    ], "metric_choice", "metrics"),
    ("slide", "Why the scalar prediction fails: the longitudinal component", [
        (0, "The total intensity separated into its three field components at numerical aperture 1.2"),
        (0, "The longitudinal component is absent from scalar theory yet carries 22 per cent of the focal energy here"),
        (0, "It fills the region where the scalar profile has its zero, which is what widens the focus"),
        (0, "The three focal field components for an x-polarized input. phi is the azimuth; the axial component is absent from scalar theory."),
    ], "naprof_comp", "components"),
    ("slide", "Focal width against numerical aperture", [
        (0, "The width of the total intensity moves away from the scalar prediction as numerical aperture increases"),
        (0, "The grey line is the Airy width, the limit both start from at low numerical aperture"),
        (0, "The separation is the spot-size error the scalar approximation would introduce"),
    ], "nac3", None),
    ("slide", "Focal-width deviation of the total intensity from scalar theory", [
        (0, "Each curve is one illumination, comparing the width of the total intensity against the scalar prediction with the same pupil amplitude"),
        (0, "The deviation passes one per cent near numerical aperture 0.45 for uniform and 0.55 for Gaussian with coefficient 4, and five per cent near 0.90 and 1.15"),
        (0, "Gaussian illumination departs later because it suppresses the marginal rays that generate the longitudinal field"),
    ], "apt1", None),
    ("slide", "Error against the scalar prediction", [
        (0, "Point-by-point error of the total intensity against the scalar profile"),
        (0, "Uniform crosses the one per cent level near numerical aperture 0.63"),
        (0, "Gaussian with truncation coefficient 4 crosses it only near 0.81"),
    ], "apt3", None),
    ("slide", "Wavelength does not move the threshold", [
        (0, "One colour per wavelength, solid for uniform and dashed for Gaussian"),
        (0, "The curves for the three wavelengths lie on top of one another"),
        (0, "The threshold numerical aperture is therefore the same at every wavelength"),
    ], "wl_rmse", None),
    ("slide", "The focus itself still scales with wavelength", [
        (0, "The same three wavelengths, now plotted as the physical focal width"),
        (0, "Here the curves separate: a longer wavelength gives a proportionally larger focus"),
        (0, "Only the scalar-to-vector threshold is wavelength free, not the spot size"),
    ], "wl_width", None),
    ("slide", "Focal field at numerical aperture 0.1", [
        (0, "Two-dimensional map with transverse and axial cross-sections at numerical aperture 0.1"),
        (0, "Focal width 3820 nm, depth of focus 167.59 µm"),
    ], "atlas_na_0p1", None),
    ("slide", "All three components at numerical aperture 0.1", [
        (0, "Total intensity including the longitudinal and cross-polarization terms"),
        (0, "On axis the two coincide, so the difference is entirely off-axis"),
    ], "cmp_full_NA_0p1", None),
    ("slide", "Focal field at numerical aperture 0.3", [
        (0, "Two-dimensional map with transverse and axial cross-sections at numerical aperture 0.3"),
        (0, "Focal width 1273 nm, depth of focus 18.62 µm"),
    ], "atlas_na_0p3", None),
    ("slide", "Focal field at numerical aperture 0.5", [
        (0, "Two-dimensional map with transverse and axial cross-sections at numerical aperture 0.5"),
        (0, "Focal width 764 nm, depth of focus 6.46 µm"),
    ], "atlas_na_0p5", None),
    ("slide", "Focal field at numerical aperture 0.8", [
        (0, "Two-dimensional map with transverse and axial cross-sections at numerical aperture 0.8"),
        (0, "Focal width 477 nm, depth of focus 2.33 µm"),
    ], "atlas_na_0p8", None),
    ("slide", "All three components at numerical aperture 0.8", [
        (0, "Total intensity including the longitudinal and cross-polarization terms"),
        (0, "On axis the two coincide, so the difference is entirely off-axis"),
    ], "cmp_full_NA_0p8", None),
    ("slide", "Focal field at numerical aperture 1.0", [
        (0, "Two-dimensional map with transverse and axial cross-sections at numerical aperture 1.0"),
        (0, "Focal width 406 nm, depth of focus 1.37 µm"),
    ], "atlas_na_1p0", None),
    ("slide", "Focal field at numerical aperture 1.2", [
        (0, "Two-dimensional map with transverse and axial cross-sections at numerical aperture 1.2"),
        (0, "Focal width 338 nm, depth of focus 0.82 µm"),
    ], "atlas_na_1p2", None),
    ("slide", "All three components at numerical aperture 1.2", [
        (0, "Total intensity including the longitudinal and cross-polarization terms"),
        (0, "On axis the two coincide, so the difference is entirely off-axis"),
    ], "cmp_full_NA_1p2", None),
    ("section", "Annular apertures"),
    ("slide", "What the obstruction ratio means", [
        (0, "The obstruction ratio is the inner radius divided by the outer radius of the pupil"),
        (0, "Zero is the full disk and a value approaching one is a thin ring"),
        (0, "Annular field by Babinet subtraction, and the paraxial depth-of-focus law. epsilon is the inner over outer pupil radius."),
    ], "pupil_geom", "babinet"),
    ("slide", "What the ring transmits of the input", [
        (0, "The same obstruction removes very different amounts of light depending on the input"),
        (0, "At obstruction 0.5 a uniform pupil keeps 75 per cent of the power, a Gaussian with coefficient 4 only 13 per cent"),
    ], "pupil_input", None),
    ("slide", "Transverse profile against obstruction ratio", [
        (0, "Each colour is one obstruction ratio"),
        (0, "A larger obstruction narrows the central lobe"),
        (0, "The side lobes rise at the same time, which is the cost of that narrowing"),
    ], "ann1", None),
    ("slide", "Axial profile against obstruction ratio", [
        (0, "Each colour is one obstruction ratio"),
        (0, "The axial profile broadens steadily as the centre of the pupil is blocked"),
    ], "ann2", None),
    ("slide", "Depth of focus against obstruction ratio", [
        (0, "Depth of focus grows with obstruction and follows the paraxial law at low numerical aperture"),
        (0, "At high numerical aperture the vector result falls short of the paraxial prediction"),
        (0, "At obstruction 0.9 the paraxial law gives 5.26 times; the computed gain is 5.25 at numerical aperture 0.13, 4.76 at 0.8 and 3.67 at 1.17"),
    ], "ann3", None),
    ("slide", "Uniform and Gaussian illumination compared", [
        (0, "Solid: uniform illumination, dashed: truncated Gaussian"),
        (0, "Both follow the same depth-of-focus trend, so the extension does not depend on the input"),
        (0, "Dotted: the paraxial law, which the high-numerical-aperture result falls short of"),
    ], "ann4", None),
    ("slide", "Peak-intensity cost of the obstruction", [
        (0, "Each curve is one numerical aperture"),
        (0, "The peak intensity falls steadily as the obstruction grows, which is the price of the longer focus"),
    ], "anne1", None),
    ("slide", "Encircled-energy cost of the obstruction", [
        (0, "Energy inside the central lobe drops as the ring thins"),
        (0, "That energy is not lost but moved into the side lobes"),
    ], "anne2", None),
    ("slide", "Departure from scalar theory for an annular pupil", [
        (0, "Solid: uniform illumination, dashed: Gaussian, one colour per obstruction ratio"),
        (0, "A larger obstruction moves every curve to the left: uniform falls from 0.63 to 0.48 as the ring thins"),
        (0, "At obstruction 0.9 both illuminations reach 0.48, since only marginal rays remain either way"),
    ], "annsca_rmse", None),
    ("slide", "Focal-width departure for an annular pupil", [
        (0, "Solid: uniform illumination, dashed: Gaussian, one colour per obstruction ratio"),
        (0, "The focal width departs from the scalar prediction sooner as the ring thins"),
    ], "annsca_fwhm", None),
    ("slide", "Thin annulus against the published closed form", [
        (0, "Sheppard and Wilson (1978) solved the annular focus by summing Laguerre-Gaussian modes, giving closed forms with one width parameter"),
        (0, "Solid: our calculation for a thin Gaussian ring at low numerical aperture; dashed: their focal-plane form, which it follows"),
        (0, "Dotted: the infinitely thin ring, the non-diffracting limit whose side lobes decay far more slowly"),
        (0, "Sheppard and Wilson closed forms for a Gaussian annulus, from a Laguerre-Gaussian mode sum. The single parameter a sets the ring width."),
    ], "shep1", "sheppard"),
    ("slide", "The axial profile is predicted, not fitted", [
        (0, "The width parameter is fitted once to the focal plane, then used unchanged to predict the axial profile"),
        (0, "The prediction matches the independently computed profile, so the agreement is not a free-parameter fit"),
    ], "shep2", None),
    ("slide", "Focal field for obstruction ratio 0", [
        (0, "Two-dimensional map with cross-sections for obstruction ratio 0 at numerical aperture 0.8"),
        (0, "Focal width 475 nm, depth of focus 2.40 µm, 1.00 times the unobstructed depth"),
    ], "atlas_e_0p0", None),
    ("slide", "Focal field for obstruction ratio 0.3", [
        (0, "Two-dimensional map with cross-sections for obstruction ratio 0.3 at numerical aperture 0.8"),
        (0, "Focal width 475 nm, depth of focus 2.58 µm, 1.08 times the unobstructed depth"),
    ], "atlas_e_0p3", None),
    ("slide", "Focal field for obstruction ratio 0.5", [
        (0, "Two-dimensional map with cross-sections for obstruction ratio 0.5 at numerical aperture 0.8"),
        (0, "Focal width 425 nm, depth of focus 3.05 µm, 1.27 times the unobstructed depth"),
    ], "atlas_e_0p5", None),
    ("slide", "Focal field for obstruction ratio 0.7", [
        (0, "Two-dimensional map with cross-sections for obstruction ratio 0.7 at numerical aperture 0.8"),
        (0, "Focal width 400 nm, depth of focus 4.43 µm, 1.85 times the unobstructed depth"),
    ], "atlas_e_0p7", None),
    ("slide", "Focal field for obstruction ratio 0.9", [
        (0, "Two-dimensional map with cross-sections for obstruction ratio 0.9 at numerical aperture 0.8"),
        (0, "Focal width 375 nm, depth of focus 11.45 µm, 4.77 times the unobstructed depth"),
    ], "atlas_e_0p9", None),
    ("slide", "All three components at obstruction ratio 0.9", [
        (0, "Total intensity including the longitudinal and cross-polarization terms"),
    ], "cmp_full_annular_0p9", None),
    ("slide", "Focal field for obstruction ratio 0.99", [
        (0, "Two-dimensional map with cross-sections for obstruction ratio 0.99 at numerical aperture 0.8"),
        (0, "Focal width 350 nm, depth of focus 12.00 µm, 5.00 times the unobstructed depth"),
    ], "atlas_e_0p99", None),
    ("section", "Pulsed sources with annular apertures"),
    ("slide", "The question", [
        (0, "Annular apertures extend the depth of focus, and few-cycle pulses degrade the focus"),
        (0, "Do the two interact, or does spectral broadening spoil the extension a ring provides?"),
        (0, "Each wavelength in the pulse forms its own annular focus, so the extension could in principle wash out"),
        (0, "Pulse spectrum and the time-integrated focal intensity: a Gaussian in frequency of width set by the duration tau, summed incoherently over the band."),
    ], None, "pulse"),
    ("slide", "Axial profiles for pulsed annular illumination", [
        (0, "Obstruction ratio 0.99, numerical aperture 0.8, centre wavelength 750 nm"),
        (0, "On-axis intensity for each obstruction ratio, from continuous wave down to one femtosecond"),
        (0, "The pulsed curves lie almost exactly on the continuous-wave ones at every obstruction"),
    ], "pa_axial", None),
    ("slide", "The depth-of-focus extension is bandwidth invariant", [
        (0, "Depth of focus relative to the unobstructed case, for each pulse duration"),
        (0, "At obstruction 0.9 the extension is 4.76 times, identical from continuous wave to one femtosecond"),
        (0, "At obstruction 0.99 it is 44.35 against 44.33, four parts in ten thousand"),
        (0, "Annular field by Babinet subtraction, and the paraxial depth-of-focus law. epsilon is the inner over outer pupil radius."),
    ], "pa_dof", "babinet"),
    ("slide", "Pulsing lengthens the focus by a fixed one per cent", [
        (0, "Obstruction ratio 0.99, numerical aperture 0.8, centre wavelength 750 nm"),
        (0, "In absolute terms the one femtosecond focus is 1.010 times longer than continuous wave"),
        (0, "That factor is the same at every obstruction ratio, so the two effects act independently"),
    ], "pa_trans", None),
    ("slide", "The same comparison without a ring", [
        (0, "Transverse profile through the full disk, continuous wave against each pulse duration"),
        (0, "At one femtosecond it is about 1.06 whether the pupil is full or a thin ring"),
        (0, "The ring contrast is lost to pulsing at the same rate regardless of obstruction"),
        (0, "Linfoot criteria comparing a test profile a against reference r: fidelity, structural content and correlation quality."),
    ], "pa_linfoot", "linfoot"),

    ("slide", "The same question for a Gaussian input", [
        (0, "A truncated Gaussian puts less light on the marginal rays the ring keeps, so its extension is weaker to begin with"),
        (0, "At obstruction 0.9 the extension is 3.05 times for a Gaussian against 4.76 for uniform"),
        (0, "The question is whether spectral broadening now interacts with it"),
    ], "pag_ratio", None),
    ("slide", "Bandwidth invariance is exact for uniform, approximate for Gaussian", [
        (0, "For uniform illumination the extension is unchanged from continuous wave to one femtosecond"),
        (0, "For a Gaussian it erodes from 3.05 to 2.83 at obstruction 0.9, about seven per cent"),
        (0, "Pulsing lengthens the unobstructed Gaussian focus more, which dilutes the ratio"),
    ], "pag_pulse", None),

    ("slide", "Obstruction ratio 0.5, continuous wave", [
        (0, "Baseline for the ring: continuous-wave illumination through an obstruction ratio of 0.5"),
        (0, "Numerical aperture 0.8, total intensity of all three components, physical coordinates"),
    ], "atlas_pa_e5_cw", None),
    ("slide", "Obstruction ratio 0.5, 2 fs pulse", [
        (0, "The same ring driven by a 2 fs pulse, centre wavelength 750 nm"),
        (0, "Numerical aperture 0.8, total intensity of all three components, physical coordinates"),
    ], "atlas_pa_e5_2fs", None),
    ("slide", "Obstruction ratio 0.5, 1 fs pulse", [
        (0, "At 1 fs the spectrum spans the full window and the ring structure fills in"),
        (0, "Numerical aperture 0.8, total intensity of all three components, physical coordinates"),
    ], "atlas_pa_e5_1fs", None),
    ("slide", "Obstruction ratio 0.9, continuous wave", [
        (0, "A thin annulus stretches the focus along the axis at fixed wavelength"),
        (0, "Numerical aperture 0.8, total intensity of all three components, physical coordinates"),
    ], "atlas_pa_e9_cw", None),
    ("slide", "Obstruction ratio 0.9, 2 fs pulse", [
        (0, "The stretched focus survives a 2 fs bandwidth essentially unchanged"),
        (0, "Numerical aperture 0.8, total intensity of all three components, physical coordinates"),
    ], "atlas_pa_e9_2fs", None),
    ("slide", "Obstruction ratio 0.9, 1 fs pulse", [
        (0, "Even at 1 fs the depth-of-focus gain from the ring is retained"),
        (0, "Numerical aperture 0.8, total intensity of all three components, physical coordinates"),
    ], "atlas_pa_e9_1fs", None),
    ("section", "Monte Carlo in the clear limit"),
    ("slide", "How a photon is launched", [
        (0, "Each photon is drawn on the pupil, not in the focal volume: a radius from the illumination profile and an azimuth uniform on the full circle"),
        (0, "The lens maps that pupil point to a ray direction, and the photon carries the refracted polarization vector with it"),
        (0, "Sampling the pupil this way is what makes the photon ensemble reproduce the diffraction integral"),
        (0, "Kolmogorov-Smirnov distance to the analytic direction distribution is 0.0009, and the azimuth is flat to within 2.5 per cent"),
    ], "mc_launch", None),
    ("slide", "The sampled input matches the intended illumination", [
        (0, "Radial intensity of the launched ensemble against the analytic pupil profile"),
        (0, "Uniform and Gaussian inputs are both recovered, which fixes the launcher before any scattering is added"),
    ], "mc_launch_i", None),
    ("slide", "The Monte Carlo reproduces the vector focal field", [
        (0, "Two hundred thousand photons, numerical aperture 0.8, no scattering"),
        (0, "Root-mean-square difference from the deterministic Richards-Wolf result is 0.0006 across the polarization direction and 0.0007 along it"),
        (0, "With scattering switched off the stochastic and deterministic calculations are the same calculation"),
    ], "mc_vector", None),
    ("slide", "The clear limit against analytic references", [
        (0, "The Monte Carlo recovers the Airy pattern at low numerical aperture and the null floor falls as one over the photon count"),
        (0, "Both the transverse and axial cuts agree, so the agreement is not a single-cut coincidence"),
    ], "mc_clear", None),
    ("slide", "Convergence with photon count", [
        (0, "The profile approaches the deterministic result as photons are added, with no residual bias"),
        (0, "This sets how many photons a given accuracy costs before scattering is introduced"),
    ], "mc_conv", None),
    ("slide", "Variance across independent trials", [
        (0, "Every Monte Carlo result is run as at least ten independent trials with the per-trial data saved"),
        (0, "The spread across trials is the error bar; a single run is never reported on its own"),
    ], "mc_var", None),
    ("section", "Summary and next steps"),
    ("slide", "What was accomplished", [
        (0, "Reproduced the Romallosa (2003) figures for high-NA optical pulses"),
        (0, "Introduced Gaussian apodization and validated it against the known low-numerical-aperture result"),
        (0, "Quantified where scalar theory fails for each input, finding Gaussian more forgiving than uniform, with a wavelength-independent threshold"),
        (0, "Implemented annular apertures, characterized depth-of-focus extension and its cost, and located the scalar breakdown for a ring"),
    ], None, None),
    ("slide", "Next steps", [
        (0, "Immediate: annular apertures with pulsed sources"),
        (1, "Apply spectral integration to annular fields"),
        (1, "Study how pulse duration interacts with the depth-of-focus extension"),
        (0, "Future: Monte Carlo photon transport with scattering, driven by these focal fields"),
    ], None, None),
    ("slide", "References", [
        (0, "Richards, B. and Wolf, E. (1959). Electromagnetic diffraction in optical systems II. Proc. R. Soc. London A 253, 358."),
        (0, "Romallosa, K. M., Bantang, J. and Saloma, C. (2003). Phys. Rev. A 68, 033812."),
        (0, "Tanaka, K., Saga, N. and Hauchi, K. (1985). Appl. Opt. 24, 1098."),
        (0, "Sheppard, C. J. R. and Wilson, T. (1978). Gaussian-beam theory of lenses with annular aperture. IEE J. Microwaves, Optics and Acoustics 2, 105."),
        (0, "Horvath, Z. L. and Bor, Z. (2003). Opt. Commun. 222, 51."),
        (0, "Born, M. and Wolf, E. (1999). Principles of Optics, 7th ed. Cambridge University Press."),
    ], None, None),
]




# ---------------------------------------------------------------- builder ---
def _run(par, text, size, color, bold=False):
    r = par.add_run()
    r.text = text
    r.font.name = FONT
    r.font.size = Pt(size)
    r.font.color.rgb = color
    r.font.bold = bold
    return r


def _navy_bg(slide, prs):
    bg = slide.shapes.add_shape(1, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = NAVY
    bg.line.fill.background()
    bg.shadow.inherit = False



def _text_height_in(bullets, width_in, base_pt):
    """Estimate the rendered height of a bullet block, in inches."""
    total = 0.0
    for lvl, text in bullets:
        size = base_pt if lvl == 0 else base_pt - 3
        indent = 0.35 * lvl
        per_line = max(8, int((width_in - indent) * 72 / (size * 0.5)))
        lines = max(1, -(-len(text) // per_line))
        total += lines * size * 1.22 / 72 + 9 / 72
    return total


def build(out_path: str, author: str = "Romero, Roland Albert A.",
          items=None) -> tuple[str, list[str]]:
    """Build the deck. Returns (path, list of missing-figure messages)."""
    from mcdo.equations import render_all
    eq_paths = render_all()   # LaTeX -> PNG, so equations are visible on the slide
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    blank = prs.slide_layouts[6]
    missing: list[str] = []

    for item in (DECK if items is None else items):
        kind = item[0]
        if kind == "title":
            s = prs.slides.add_slide(blank)
            _navy_bg(s, prs)
            tb = s.shapes.add_textbox(Inches(0.8), Inches(2.7), Inches(11.7), Inches(1.6))
            _run(tb.text_frame.paragraphs[0], item[1], 46, WHITE, bold=True)
            ab = s.shapes.add_textbox(Inches(0.8), Inches(6.2), Inches(11), Inches(0.6))
            _run(ab.text_frame.paragraphs[0], author, 18, WHITE)
            continue

        if kind == "section":
            s = prs.slides.add_slide(blank)
            _navy_bg(s, prs)
            tb = s.shapes.add_textbox(Inches(0.8), Inches(3.2), Inches(11.7), Inches(1.3))
            _run(tb.text_frame.paragraphs[0], item[1], 36, WHITE, bold=True)
            continue

        _, title, bullets, figkey, latexkey = item
        s = prs.slides.add_slide(blank)

        tb = s.shapes.add_textbox(Inches(0.55), Inches(0.32), Inches(12.3), Inches(0.95))
        tb.text_frame.word_wrap = True
        _run(tb.text_frame.paragraphs[0], title, 28, TITLE_BLUE, bold=True)

        path = None
        if figkey:
            rel, script = FIGURES[figkey]
            cand = os.path.join(OUT, rel)
            if os.path.exists(cand):
                path = cand
            else:
                missing.append(f"{rel}  ->  regenerate with: python {script}")

        # A wide figure cannot sit beside the bullets without running off the
        # slide, so the aspect ratio decides the layout: tall-ish figures go to
        # the right of the text, wide ones go underneath it at full width.
        aspect = None
        if path:
            from PIL import Image
            with Image.open(path) as im:
                aspect = im.width / im.height
        SIDE_BOX = (6.45, 1.55, 6.60, 5.10)      # left, top, width, height
        stacked = bool(path) and aspect is not None and aspect > SIDE_BOX[2] / SIDE_BOX[3]
        # the bullets decide where a stacked figure can start
        stacked_text_h = _text_height_in(bullets, 12.20, 16) if stacked else 0.0
        fig_top = min(4.30, max(3.00, 1.55 + stacked_text_h + 0.20))
        BELOW_BOX = (0.55, fig_top, 12.20, 7.25 - fig_top)

        if path and not stacked:
            text_w, text_h = Inches(5.6), Inches(5.10)
        elif stacked:
            # the figure sits underneath, so the text may only use the band above it
            text_w, text_h = Inches(12.2), Inches(max(1.0, fig_top - 1.70))
        else:
            text_w, text_h = Inches(12.2), Inches(5.50)
        # an equation is dropped in below the text, so leave room for it — but a
        # stacked figure already occupies that band, so there the equation stays
        # in the notes only
        show_equation = bool(latexkey) and not stacked
        if show_equation:
            eq_top = 5.35 if path else 4.60
            text_h = Inches(max(1.0, eq_top - 0.15 - 1.55))
        bx = s.shapes.add_textbox(Inches(0.55), Inches(1.55), text_w, text_h)
        tf = bx.text_frame
        tf.word_wrap = True
        for i, (lvl, text) in enumerate(bullets):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.level = lvl
            p.space_after = Pt(9)
            base = 16 if stacked else 18
            _run(p, ("•  " if lvl == 0 else "–  ") + text, base if lvl == 0 else base - 3, INK)

        if path:
            bl, bt, bw, bh = BELOW_BOX if stacked else SIDE_BOX
            scale = min(bw / aspect, bh) / bh          # fit inside the box
            h = bh * scale
            w = h * aspect
            left = bl + (bw - w) / 2                  # centred in its box
            top = bt + (bh - h) / 2
            s.shapes.add_picture(path, Inches(left), Inches(top),
                                 width=Inches(w), height=Inches(h))

        if latexkey:
            # keep the source in the notes (copy-paste into Keynote/LaTeXiT) ...
            s.notes_slide.notes_text_frame.text = "LaTeX:\n\n" + LX[latexkey]
            # ... and show the typeset form on the slide when there is room
            eq = eq_paths.get(latexkey) if show_equation else None
            if eq and os.path.exists(eq):
                from PIL import Image
                with Image.open(eq) as im:
                    ar = im.height / im.width
                if path:                      # equation sits under the bullets
                    eq_w = Inches(5.3)
                    left, top = Inches(0.6), Inches(5.35)
                else:                         # full width, centred under the text
                    eq_w = Inches(10.4)
                    left, top = Inches(1.4), Inches(4.6)
                eq_h = Inches(eq_w.inches * ar)
                max_h = Inches(1.7)
                if eq_h > max_h:
                    eq_w = Inches(eq_w.inches * (max_h.inches / eq_h.inches))
                    eq_h = max_h
                s.shapes.add_picture(eq, left, top, width=eq_w, height=eq_h)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    prs.save(out_path)
    return out_path, missing


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build the mcdo results deck (reproducible).")
    ap.add_argument("--out", default=None)
    ap.add_argument("--stage", choices=sorted(STAGES), default=None,
                    help="build the review deck for one stage only")
    ap.add_argument("--list-stages", action="store_true")
    args = ap.parse_args(argv)

    if args.list_stages:
        for sid, st in sorted(STAGES.items()):
            figs, scripts, dirs = stage_outputs(sid)
            print(f"{sid}. {st['title']}"
                  f"  [{len(scripts)} scripts, {len(figs)} figures, "
                  + ", ".join("output/" + d for d in dirs) + "]")
        return 0

    if args.stage:
        st = STAGES[args.stage]
        out = args.out or os.path.join(OUT, "deck", f"stage{args.stage}_{st['key']}.pptx")
        path, missing = build(out, items=stage_deck(args.stage))
    else:
        out = args.out or os.path.join(OUT, "deck", "mcdo_results_deck.pptx")
        path, missing = build(out)
    n = len(prs_slides(path))
    print(f"Deck written: {path}  ({n} slides)")
    if missing:
        print("\nMissing figures (slides built without them):")
        for m in missing:
            print("  -", m)
    else:
        print("All declared figures present.")
    return 0


def prs_slides(path):
    return Presentation(path).slides


if __name__ == "__main__":
    raise SystemExit(main())
