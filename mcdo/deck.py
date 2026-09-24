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
from pptx.enum.text import PP_ALIGN

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
    "k_dof2d":   ("03_annular/dof_visual.png",                        "scripts/fig_dof_visual.py"),
    "k_rel":     ("03_annular/master_grid_na0p8_relative.png",        "scripts/fig_master_grid.py"),
    "q_law":     ("03_annular/panels/exact_extension_law_p1.png",      "scripts/fig_exact_extension_law.py"),
    "q_window":  ("03_annular/panels/flat_window_model_p3.png",        "scripts/fig_flat_window_model.py"),
    "q_bessel":  ("03_annular/panels/bessel_limit_p3.png",             "scripts/fig_bessel_limit.py"),
    "q_resp":    ("05_pulsed_pupils/panels/bandwidth_response_p1.png", "scripts/fig_bandwidth_response.py"),
    "m_answer":  ("02_na_apodization/panels/rmse_usefulness_p4.png",   "scripts/fig_rmse_usefulness.py"),
    "m_norm":    ("02_na_apodization/normalization_difference.png",    "scripts/fig_rmse_usefulness.py"),
    "m_pair":    ("02_na_apodization/normalization_pair.png",          "scripts/fig_rmse_usefulness.py"),
    # Single panels for the expanded stage-7 block
    "q_costs":   ("03_annular/panels/what_it_costs_p1.png",            "scripts/fig_what_it_costs.py"),
    "q_bought":  ("03_annular/panels/scatter_tradeoffs_p1.png",        "scripts/fig_scatter_tradeoffs.py"),
    "q_parity":  ("03_annular/panels/scatter_tradeoffs_p4.png",        "scripts/fig_scatter_tradeoffs.py"),
    "q_prof":    ("05_pulsed_pupils/panels/bandwidth_invariance_p1.png", "scripts/fig_bandwidth_invariance.py"),
    "q_aper":    ("05_pulsed_pupils/panels/erosion_vs_aperture_p4.png", "scripts/fig_erosion_vs_aperture.py"),
    "q_trunc":   ("02_na_apodization/panels/truncation_pulsed_p2.png", "scripts/fig_truncation_pulsed.py"),
    "q_lambda":  ("03_annular/panels/wavelength_p4.png",               "scripts/fig_wavelength.py"),
    "q_rings":   ("05_pulsed_pupils/panels/ring_erasure_p3.png",       "scripts/fig_ring_erasure.py"),
    "q_spectrum":("05_pulsed_pupils/panels/spectrum_p1.png",           "scripts/fig_spectrum.py"),
    # Single panels, one per slide
    "s_grid08":   ("03_annular/panels/master_grid_na0p8_p2.png",      "scripts/fig_master_grid.py"),
    "s_grid01":   ("03_annular/panels/master_grid_na0p1_p2.png",      "scripts/fig_master_grid.py"),
    "s_grid12":   ("03_annular/panels/master_grid_na1p2_p2.png",      "scripts/fig_master_grid.py"),
    "s_law":      ("03_annular/panels/exact_extension_law_p1.png",    "scripts/fig_exact_extension_law.py"),
    "s_truncden": ("02_na_apodization/panels/truncation_pulsed_p4.png", "scripts/fig_truncation_pulsed.py"),
    "s_fld_a0":   ("03_annular/fields_alpha0.png",                    "scripts/fig_alpha_fields.py"),
    "s_fld_a2":   ("03_annular/fields_alpha2.png",                    "scripts/fig_alpha_fields.py"),
    "s_fld_a4":   ("03_annular/fields_alpha4.png",                    "scripts/fig_alpha_fields.py"),
    # Field maps at every ratio, for picking from during the talk
    "pk_u_0p0_cw":  ("atlas/pulsed_illumination/uniform_eps0p0_cw.png",  "scripts/config_atlas.py"),
    "pk_u_0p0_1f":  ("atlas/pulsed_illumination/uniform_eps0p0_1fs.png", "scripts/config_atlas.py"),
    "pk_u_0p5_cw":  ("atlas/pulsed_illumination/uniform_eps0p5_cw.png",  "scripts/config_atlas.py"),
    "pk_u_0p5_1f":  ("atlas/pulsed_illumination/uniform_eps0p5_1fs.png", "scripts/config_atlas.py"),
    "pk_u_0p9_cw":  ("atlas/pulsed_illumination/uniform_eps0p9_cw.png",  "scripts/config_atlas.py"),
    "pk_u_0p9_1f":  ("atlas/pulsed_illumination/uniform_eps0p9_1fs.png", "scripts/config_atlas.py"),
    "pk_u_0p99_cw": ("atlas/pulsed_illumination/uniform_eps0p99_cw.png", "scripts/config_atlas.py"),
    "pk_u_0p99_1f": ("atlas/pulsed_illumination/uniform_eps0p99_1fs.png","scripts/config_atlas.py"),
    "pk_g_0p9_cw":  ("atlas/pulsed_illumination/gaussian_eps0p9_cw.png", "scripts/config_atlas.py"),
    "pk_g_0p9_1f":  ("atlas/pulsed_illumination/gaussian_eps0p9_1fs.png","scripts/config_atlas.py"),
    # Continuous wave against pulsed: the comparison stage 8 is built from
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
    "pag_lo_uni": ("05_pulsed_pupils/panels/pulsed_annular_apertures_p1.png", "scripts/verify_pulsed_apertures.py"),
    "pag_lo_gau": ("05_pulsed_pupils/panels/pulsed_annular_apertures_p2.png", "scripts/verify_pulsed_apertures.py"),
    "pag_hi_uni": ("05_pulsed_pupils/panels/pulsed_annular_apertures_p3.png", "scripts/verify_pulsed_apertures.py"),
    "pag_hi_gau": ("05_pulsed_pupils/panels/pulsed_annular_apertures_p4.png", "scripts/verify_pulsed_apertures.py"),
    "ab_0p8_gain": ("03_annular/panels/annular_baseline_p5.png", "scripts/verify_annular_baseline.py"),
    "ak_cmp":  ("03_annular/panels/fig_aperture_parameter_p4.png", "scripts/fig_aperture_parameter.py"),
    "cmp_eps_0p0": ("atlas/annular_grid/na0p8_uniform_eps0p0.png", "scripts/config_atlas.py"),
    "cmp_eps_0p5": ("atlas/annular_grid/na0p8_uniform_eps0p5.png", "scripts/config_atlas.py"),
    "cmp_eps_0p9": ("atlas/annular_grid/na0p8_uniform_eps0p9.png", "scripts/config_atlas.py"),
    "cmp_eps_0p99": ("atlas/annular_grid/na0p8_uniform_eps0p99.png", "scripts/config_atlas.py"),
    "cmp_na_0p1": ("atlas/annular_grid/na0p1_uniform_eps0p9.png", "scripts/config_atlas.py"),
    "cmp_na_0p8": ("atlas/annular_grid/na0p8_uniform_eps0p9.png", "scripts/config_atlas.py"),
    "cmp_na_1p2": ("atlas/annular_grid/na1p2_uniform_eps0p9.png", "scripts/config_atlas.py"),
    "cmp_in_uni": ("atlas/annular_grid/na0p8_uniform_eps0p5.png", "scripts/config_atlas.py"),
    "cmp_in_gau": ("atlas/annular_grid/na0p8_gaussian_eps0p5.png", "scripts/config_atlas.py"),
    "ts_gain":  ("02_na_apodization/panels/fig_truncation_sweep_p1.png", "scripts/fig_truncation_sweep.py"),
    "ts_trans": ("02_na_apodization/panels/fig_truncation_sweep_p2.png", "scripts/fig_truncation_sweep.py"),
    "ts_width": ("02_na_apodization/panels/fig_truncation_sweep_p3.png", "scripts/fig_truncation_sweep.py"),
    "ext_cw":  ("05_pulsed_pupils/panels/fig_extension_cw_pulsed_p3.png", "scripts/fig_extension_cw_pulsed.py"),
    "ext_1fs": ("05_pulsed_pupils/panels/fig_extension_cw_pulsed_p4.png", "scripts/fig_extension_cw_pulsed.py"),
    "ext_cmp_uni": ("05_pulsed_pupils/panels/fig_extension_cw_pulsed_p1.png", "scripts/fig_extension_cw_pulsed.py"),
    "ext_cmp_gau": ("05_pulsed_pupils/panels/fig_extension_cw_pulsed_p2.png", "scripts/fig_extension_cw_pulsed.py"),
    "cw_uni_0p0": ("atlas/truncation_grid/at0p0_eps0p0.png", "scripts/config_atlas.py"),
    "cw_gau_0p0": ("atlas/truncation_grid/at4p0_eps0p0.png", "scripts/config_atlas.py"),
    "cw_uni_0p5": ("atlas/truncation_grid/at0p0_eps0p5.png", "scripts/config_atlas.py"),
    "cw_gau_0p5": ("atlas/truncation_grid/at4p0_eps0p5.png", "scripts/config_atlas.py"),
    "cw_uni_0p9": ("atlas/truncation_grid/at0p0_eps0p9.png", "scripts/config_atlas.py"),
    "cw_gau_0p9": ("atlas/truncation_grid/at4p0_eps0p9.png", "scripts/config_atlas.py"),
    "cw_uni_0p99": ("atlas/truncation_grid/at0p0_eps0p99.png", "scripts/config_atlas.py"),
    "cw_gau_0p99": ("atlas/truncation_grid/at4p0_eps0p99.png", "scripts/config_atlas.py"),
    "pi_uni_0p9_cw": ("atlas/pulsed_illumination/uniform_eps0p9_cw.png", "scripts/config_atlas.py"),
    "pi_uni_0p9_1fs": ("atlas/pulsed_illumination/uniform_eps0p9_1fs.png", "scripts/config_atlas.py"),
    "pi_gau_0p9_cw": ("atlas/pulsed_illumination/gaussian_eps0p9_cw.png", "scripts/config_atlas.py"),
    "pi_gau_0p9_1fs": ("atlas/pulsed_illumination/gaussian_eps0p9_1fs.png", "scripts/config_atlas.py"),
    "gain_abs": ("03_annular/panels/fig_gain_reference_p1.png", "scripts/fig_gain_reference.py"),
    "gain_norm": ("03_annular/panels/fig_gain_reference_p2.png", "scripts/fig_gain_reference.py"),
    "pupil_geo_a": ("03_annular/panels/fig_pupil_geometry_p1.png", "scripts/fig_pupil_geometry.py"),
    "pupil_geo_b": ("03_annular/panels/fig_pupil_geometry_p2.png", "scripts/fig_pupil_geometry.py"),
    "pupil_geo_c": ("03_annular/panels/fig_pupil_geometry_p3.png", "scripts/fig_pupil_geometry.py"),
    "eb_pupil": ("03_annular/panels/fig_power_distribution_p1.png", "scripts/fig_power_distribution.py"),
    "eb_core":  ("03_annular/panels/fig_power_distribution_p2.png", "scripts/fig_power_distribution.py"),
    "eb_land":  ("03_annular/panels/fig_power_distribution_p3.png", "scripts/fig_power_distribution.py"),
    "mn_peak":   ("02_na_apodization/panels/verify_metric_normalization_p1.png", "scripts/verify_metric_normalization.py"),
    "mn_energy": ("02_na_apodization/panels/verify_metric_normalization_p2.png", "scripts/verify_metric_normalization.py"),
    "mn_curves": ("02_na_apodization/panels/verify_metric_normalization_p3.png", "scripts/verify_metric_normalization.py"),
    "ab_0p8_width": ("03_annular/panels/annular_baseline_p4.png", "scripts/verify_annular_baseline.py"),
    "ab_0p8_peak": ("03_annular/panels/annular_baseline_p6.png", "scripts/verify_annular_baseline.py"),
    "ab_1p2_gain": ("03_annular/panels/annular_baseline_p8.png", "scripts/verify_annular_baseline.py"),
    "ac_uni_0p8_ax": ("03_annular/panels/fig_annular_comparison_uniform_p4.png", "scripts/fig_annular_comparison.py"),
    "ag_0p8_uni_0p9": ("atlas/annular_grid/na0p8_uniform_eps0p9.png", "scripts/config_atlas.py"),
    "ag_0p8_uni_0p99": ("atlas/annular_grid/na0p8_uniform_eps0p99.png", "scripts/config_atlas.py"),
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
    "9": {
        "key": "pulse_report",
        "title": "Progress Report",
        "sections": ["Optical Pulses",
                     "Depth of focus, continuous wave and 1 fs",
                     "Continuous wave against a 1 fs pulse",
                     "Choosing the metric",
                     "Focal field maps"],
    },
    "7": {
        "key": "annular_working",
        "title": "Annular apertures: truncation and obstruction",
        "sections": ["Annular apertures: truncation and obstruction",
                     "Continuous wave, uniform illumination",
                     "Continuous wave, truncated Gaussian",
                     "Pulsed against continuous wave",
                     "Annular apertures: continuous wave against a pulse",
                     "What is measured",
                     "Continuous wave: the ring extends the focus",
                     "A pulse against continuous wave",
                     "Does the comparison hold elsewhere",
                     "Why it comes out this way"],
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
            keys.extend([item[3]] if isinstance(item[3], str) else item[3])
    figs = {k: FIGURES[k] for k in dict.fromkeys(keys) if k in FIGURES}
    scripts = sorted({script for _, script in figs.values()})
    dirs = sorted({os.path.dirname(rel) for rel, _ in figs.values()})
    return figs, scripts, dirs


SHOW_FIGURE_PATH = True     # print the source file on each figure slide


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
    return items


LX = {
    "components": r"E_x(P)=-i(I_0+I_2\cos 2\phi),\quad E_y(P)=-iI_2\sin 2\phi,\quad E_z(P)=-2iI_1\cos\phi",
    "integrals": (r"I_m(u,v)=\int_0^{\alpha}\sqrt{\cos\theta}\,g_m(\theta)\,"
                  r"J_m\!\left(\frac{v\sin\theta}{\sin\alpha}\right)"
                  r"\exp\!\left(\frac{iu\cos\theta}{\sin^2\alpha}\right)d\theta"
                  "\n\n"
                  r"g_0=\sin\theta(1+\cos\theta),\quad g_1=\sin^2\theta,\quad g_2=\sin\theta(1-\cos\theta)"),
    "coords": (r"u=\frac{2\pi n}{\lambda}\sin^2\!\alpha\cdot z,\quad "
               r"v=\frac{2\pi n}{\lambda}\sin\alpha\cdot r,\quad "
               r"\alpha=\arcsin\!\left(\frac{\mathrm{NA}}{n}\right)"),
    "apod": (r"A(\theta)=\exp\!\left(-\alpha\frac{\sin^2\theta}{\sin^2\alpha_{\max}}\right),"
             r"\qquad \alpha=\left(\frac{r_{\mathrm{aperture}}}{w_{\mathrm{beam}}}\right)^2"),
    "metrics": (r"\Delta\mathrm{FWHM}=\frac{\mathrm{FWHM}_{\mathrm{vector}}-\mathrm{FWHM}_{\mathrm{scalar}}}{\mathrm{FWHM}_{\mathrm{scalar}}}\times 100\%"
                "\n\n"
                r"\mathrm{RMSE}=\sqrt{\frac{1}{N}\sum_i\left(I_{\mathrm{vector}}(r_i)-I_{\mathrm{scalar}}(r_i)\right)^2}"),
    "aperture": (r"\alpha=\arcsin\!\left(\frac{\mathrm{NA}}{n}\right),\qquad "
                 r"\theta_{\mathrm{inner}}=\arcsin(\epsilon\sin\alpha)"
                 "\n\n"
                 r"\mathrm{DOF}\propto\frac{\lambda}{n\sin^2\alpha}"),
    "quantities": (r"\mathrm{DOF}=2z_{1/2},\quad I(0,z_{1/2})=\frac{1}{2} I(0,0)"
                   "\n\n"
                   r"\mathrm{FWHM}=2r_{1/2},\quad I(r_{1/2},0)=\frac{1}{2} I(0,0)"
                   "\n\n"
                   r"T(\epsilon)=\frac{\int_{\theta_{\mathrm{in}}}^{\alpha}|A|^{2}"
                   r"\sin\theta\cos\theta\,d\theta}"
                   r"{\int_{0}^{\alpha}|A|^{2}\sin\theta\cos\theta\,d\theta}"),
    "measured_dof": (r"\mathrm{DOF}=2z_{1/2},\qquad "
                     r"I(0,z_{1/2})=\frac{1}{2}I(0,0)"
                     "\n\n"
                     r"\frac{\mathrm{DOF}(\epsilon)}{\mathrm{DOF}(0)}"
                     r"\quad\text{at the same }\mathrm{NA},\,A(\theta),\,\tau"),
    "measured_power": (r"T(\epsilon)=\frac{\int_{\theta_{\mathrm{in}}}^{\alpha}"
                       r"|A(\theta)|^{2}\sin\theta\cos\theta\,d\theta}"
                       r"{\int_{0}^{\alpha}|A(\theta)|^{2}\sin\theta\cos\theta\,d\theta}"
                       "\n\n"
                       r"P(\epsilon)=\frac{I_{\epsilon}(0,0)}{I_{0}(0,0)},\qquad "
                       r"\theta_{\mathrm{in}}=\arcsin(\epsilon\sin\alpha)"),
    "normalization": (r"\text{peak:}\quad \hat{I}(r)=\frac{I(r)}{\max_r I(r)}"
                      "\n\n"
                      r"\text{energy:}\quad \hat{I}(r)=\frac{I(r)}{\int_0^{\infty} I(r')\,2\pi r'\,dr'}"
                      "\n\n"
                      r"\mathrm{RMSE}=\sqrt{\frac{1}{N}\sum_i\left(\hat{I}_{\mathrm{vector}}(r_i)-\hat{I}_{\mathrm{scalar}}(r_i)\right)^2}"),
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
    "apod": "Gaussian pupil apodization. The alpha is the squared "
            "ratio of aperture radius to beam waist, and sets the amplitude at the rim.",
    "pulse": "Pulse spectrum and the time-integrated focal intensity: a Gaussian in "
             "frequency of width set by the duration tau, summed incoherently over the band.",
    "metrics": "The two comparison metrics: the fractional error in predicted spot size, "
               "and the point-by-point error between normalized profiles.",
    "aperture": "Cone half-angle from numerical aperture and refractive index, "
                "the inner angle an obstruction ratio blocks, and the scaling of "
                "depth of focus with that angle.",
    "quantities": "The three measured quantities: depth of focus, transverse "
                  "full width at half maximum, and transmitted power.",
    "measured_dof": "Depth of focus is the full width at half maximum of the "
                    "axial profile through the focus. The extension is its ratio "
                    "to the same configuration with no obstruction.",
    "measured_power": "Transmitted power is the fraction of the incident power "
                      "passing the annulus, with the aplanatic area element "
                      "sin theta cos theta. Peak intensity is the on-axis value "
                      "relative to the unobstructed pupil.",
    "normalization": "Two ways to normalize before differencing two profiles. "
                     "Peak division sets both maxima to one. Energy division sets "
                     "the transmitted power to one, with the radial weight 2 pi r "
                     "being the area element of the focal plane.",
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
        (1, "Scalar theory fails earlier as the obstruction ratio increases, and the Gaussian advantage disappears"),
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
        (0, "Scalar Debye integral: the focal field with polarization ignored, no obliquity factor."),
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
        (0, "The three components for an x-polarized input."),
        (0, "numerical aperture 1.2, uniform, continuous wave at 750 nm"),
        (0, "Continuous wave at 750 nm"),
    ], None, "components"),
    ("slide", "Diffraction integrals", [
        (0, "I0 is the main focusing term and gives the Airy pattern"),
        (0, "I1 carries the longitudinal field, which appears at high numerical aperture"),
        (0, "I2 is the cross-polarization correction, which breaks circular symmetry"),
        (0, "The three Richards-Wolf diffraction integrals over the focusing cone, with u and v the axial and radial optical coordinates."),
    ], None, "integrals"),
    ("slide", "Optical coordinates", [
        (0, "Normalized coordinates make the result scale with wavelength and numerical aperture"),
        (0, "The origin is the geometric focus, so one calculation serves any wavelength and numerical aperture"),
        (0, "Optical coordinates: dimensionless axial and radial position."),
    ], None, "coords"),
    ("section", "Optical pulses"),
    ("slide", "Few-cycle pulse characteristics", [
        (0, "Pulse durations below 1 fs, in the few-cycle regime"),
        (0, "Spectral width grows as the inverse of the duration, so a 1 fs pulse spans several hundred terahertz"),
        (0, "Beyond that point the carrier cannot be represented and the focus deteriorates rapidly"),
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
        (0, "Focal width 500 nm, depth of focus 2.40 µm, against 475 nm and 2.40 µm for continuous wave"),
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
        (0, "Below about 2 fs the spectrum spans more than a factor of two in frequency around the 750 nm center wavelength"),
    ], "pulse_bw", None),
    ("slide", "Coherence length against pulse duration", [
        (0, "The coherence length sets how finely the frequency axis has to be sampled"),
        (0, "At 1.2 fs it falls to 360 nm, just inside the 375 nm Nyquist limit for a 750 nm center wavelength"),
    ], "pulse_coh", None),
    # ── Stage 7, expanded: continuous wave against a pulse ───────────────
    # ── Stage 9: the weekly pulse report ─────────────────────────────────
    ("section", "Optical Pulses"),
    ("slide", "Summary", [
        (0, "Previously: Generated focal intensity distributions for annular apertures"),
        (1, "Blocking the inner pupil extended depth of focus up to 44x as obstruction ratio increased from 0 to 0.99"),
        (0, "Generated focal intensity distributions for optical pulses"),
        (1, "Under uniform illumination, 1 fs DOF is consistently 0.91% longer than CW depth; consistent even if obstruction ratio is varied"),
        (1, "For untruncated Gaussian input, DOF is 9.1% longer with no obstruction, but extension falls at increasing obstruction ratios"),
    ], None, None),
    ("slide", "Optical Pulse Spectrum", [
        (0, "Spectral broadening: Bandwidth increases as the inverse of the pulse width"),
        (0, "Center wavelength 750 nm"),
    ], "q_spectrum", "pulse"),
    ("slide", "Settings", [
        (0, "Numerical aperture 0.8, center wavelength 750 nm, refractive index 1.3"),
        (0, "Obstruction ratio 0 through 0.99; truncation parameter 0 is uniform, 4 is the truncated Gaussian"),
        (0, "Continuous wave against a 1 fs pulse"),
    ], None, None),

    ("section", "Depth of focus, continuous wave and 1 fs"),
    ("slide", "Depth of Focus", [
        (0, "The depth of focus is the full width at half maximum of the on-axis profile"),
        (0, "Two profiles are drawn with their half-maximum crossings (orange) and depth of focus (white dashed lines) marked, at obstruction ratio 0 and 0.9"),
        (0, "Numerical aperture 0.8, 750 nm, continuous wave"),
    ], "k_dof2d", None),
    ("slide", "Depth of focus against obstruction ratio", [
        (0, "DOF rises from 2.42 to 107 um as the obstruction ratio goes 0 to 0.99"),
        (1, "At obstruction ratio = 0.99 all four truncations converge to 107.24-107.27 um"),
        (0, "Under truncation it is not consistent: at alpha = 4 the increase runs from 9.1% with no obstruction down to 0.9% at ratio 0.99"),
        (0, "Numerical aperture 0.8, 750 nm"),
    ], "s_grid08", None),
    ("slide", "Depth of focus against obstruction ratio, relative", [
        (0, "Relative to each pupil's own unobstructed focus, the extension at ratio 0.99 falls with truncation: 44x, 43x, 39x and 28x for alpha = 0, 1, 2 and 4"),
        (0, "Uniform: the 1 fs and continuous-wave curves coincide, differing by at most 0.03%"),
    ], "k_rel", None),
    ("slide", "Extension against obstruction ratio, computed and closed form", [
        (0, "The annulus transmits the angular band from arcsin(eps sin alpha) to alpha; the phase spread across that band sets the depth"),
        (1, "The resulting closed form contains no wavelength, so every color in the pulse receives the same extension"),
        (0, "The law predicts the 1 fs data as accurately as the continuous-wave data, 0.25% against 0.23%"),
    ], "s_law", "coords"),
    ("slide", "Depth of focus at 1 fs relative to continuous wave", [
        (0, "The 1 fs pulse lengthens the depth of focus at every obstruction ratio"),
        (1, "Uniform: 0.91% longer, the same at every obstruction ratio"),
        (1, "alpha = 4: 9.1% longer with no obstruction, falling to 0.9% at ratio 0.99"),
        (0, "The extension is the ratio of two depths, so it falls only where the two differ: 0.03%, 0.75%, 2.5% and 7.5% for alpha = 0, 1, 2 and 4"),
        (0, "Numerical aperture 0.8, 750 nm"),
    ], "s_truncden", None),
    ("slide", "Summary", [
        (0, "Under uniform illumination the 1 fs DOF is 0.91% longer at every obstruction ratio, so the extension changes by at most 0.03%"),
        (1, "The closed form contains no wavelength, so this is a property of the geometry"),
        (0, "For untruncated Gaussian input at alpha = 4 the extension falls 7.5%, because the pulse lengthens the unobstructed focus by 9.1% and the obstructed one by 0.9%"),
        (0, "At obstruction ratio 0.99 all four truncations give the same DOF, 107.24-107.27 um"),
    ], None, None),

    ("section", "Choosing the metric"),
    ("slide", "The two normalizations", [
        (0, "Peak division sets both maxima to one; energy division sets the transmitted power to one"),
        (0, "Numerical aperture 1.2, 750 nm"),
    ], "m_norm", "normalization"),
    ("slide", "Vector against scalar, by numerical aperture", [
        (0, "Peak normalization hides the peak difference; energy normalization keeps it"),
        (0, "Uniform illumination, 750 nm"),
    ], "m_pair", None),
    ("slide", "Which criterion fires first", [
        (0, "Focal width 0.42, root-mean-square 0.46 energy normalized and 0.66 peak normalized"),
        (0, "Energy normalization helps, but the focal width is still the more reliable criterion"),
        (0, "Threshold 0.01; uniform illumination, 750 nm"),
    ], "m_answer", None),

    ("section", "Focal field maps"),
    ("slide", "Optical Fields for Uniform Illumination", [
        (0, "Uniform (alpha = 0), numerical aperture 0.8, 750 nm; top row continuous wave, bottom row 1 fs pulse"),
        (0, "DOF rises from 2.42 to 11.51 um as the obstruction ratio goes 0 to 0.9"),
    ], "s_fld_a0", None),
    ("slide", "Optical Fields for Truncated Gaussian Illumination", [
        (0, "alpha = 2, numerical aperture 0.8, 750 nm; top row continuous wave, bottom row 1 fs pulse"),
        (0, "DOF rises from 2.78 to 11.58 um as the obstruction ratio goes 0 to 0.9"),
    ], "s_fld_a2", None),
    ("slide", "Optical Fields for Untruncated Gaussian Illumination", [
        (0, "alpha = 4, numerical aperture 0.8, 750 nm; top row continuous wave, bottom row 1 fs pulse"),
        (0, "DOF rises from 3.85 to 11.74 um as the obstruction ratio goes 0 to 0.9"),
        (1, "With no obstruction the focus is 59% longer than uniform; at ratio 0.9 the three illuminations agree within 2%"),
    ], "s_fld_a4", None),
    ("slide", "Uniform, no obstruction", [
        (0, "Continuous wave, numerical aperture 0.8, 750 nm"),
    ], "pk_u_0p0_cw", None),
    ("slide", "Uniform, no obstruction, 1 fs", [
        (0, "1 fs pulse, numerical aperture 0.8, 750 nm"),
    ], "pk_u_0p0_1f", None),
    ("slide", "Uniform, obstruction ratio 0.5", [
        (0, "Continuous wave, numerical aperture 0.8, 750 nm"),
    ], "pk_u_0p5_cw", None),
    ("slide", "Uniform, obstruction ratio 0.5, 1 fs", [
        (0, "1 fs pulse, numerical aperture 0.8, 750 nm"),
    ], "pk_u_0p5_1f", None),
    ("slide", "Uniform, obstruction ratio 0.9", [
        (0, "Continuous wave, numerical aperture 0.8, 750 nm"),
    ], "pk_u_0p9_cw", None),
    ("slide", "Uniform, obstruction ratio 0.9, 1 fs", [
        (0, "1 fs pulse, numerical aperture 0.8, 750 nm"),
    ], "pk_u_0p9_1f", None),
    ("slide", "Uniform, obstruction ratio 0.99", [
        (0, "Continuous wave, numerical aperture 0.8, 750 nm"),
    ], "pk_u_0p99_cw", None),
    ("slide", "Uniform, obstruction ratio 0.99, 1 fs", [
        (0, "1 fs pulse, numerical aperture 0.8, 750 nm"),
    ], "pk_u_0p99_1f", None),
    ("slide", "Truncated Gaussian, obstruction ratio 0.9", [
        (0, "Continuous wave, numerical aperture 0.8, 750 nm"),
    ], "pk_g_0p9_cw", None),
    ("slide", "Truncated Gaussian, obstruction ratio 0.9, 1 fs", [
        (0, "1 fs pulse, numerical aperture 0.8, 750 nm"),
    ], "pk_g_0p9_1f", None),
    ("slide", "Depth of focus against obstruction ratio, numerical aperture 0.1", [
        (0, "Depth of focus against obstruction, by truncation, 750 nm"),
    ], "s_grid01", None),
    ("slide", "Depth of focus against obstruction ratio, numerical aperture 1.2", [
        (0, "Depth of focus against obstruction, by truncation, 750 nm"),
    ], "s_grid12", None),

    ("section", "Annular apertures: continuous wave against a pulse"),
    ("slide", "What was varied, and what came out", [
        (0, "An annular pupil is compared with itself unobstructed, at continuous wave and with a 1 fs pulse"),
        (0, "Raising the obstruction ratio extends the depth of focus, by 44 times at ratio 0.99"),
        (0, "Under uniform illumination the extension is unchanged by the pulse"),
        (0, "Under a truncated Gaussian it erodes, and the erosion grows with the truncation"),
        (0, "The result holds at three numerical apertures and across seven center wavelengths"),
    ], None, None),
    ("slide", "Settings", [
        (0, "Numerical aperture 0.8, center wavelength 750 nm, refractive index 1.3"),
        (0, "Obstruction ratio: 0 through 0.99, the inner over outer pupil radius"),
        (0, "Truncation parameter alpha: 0 is uniform, 4 is the truncated Gaussian; larger is more truncated"),
        (0, "Continuous wave, and a 1 fs pulse of bandwidth 441 THz, 1.10 times the carrier"),
        (0, "Intensity is the azimuthal average of all three field components"),
        (0, "On the field maps: orange is the half maximum, red dashed the Airy radius"),
    ], None, None),

    ("section", "What is measured"),
    ("slide", "Both profiles in absolute units, ratio 4.76", [
        (0, "Depth of focus is the full width at half maximum of the on-axis profile"),
        (0, "Physically: the distance along the beam over which the focus stays at least half as bright"),
        (0, "Extension is that depth divided by the same pupil's depth with no obstruction"),
        (0, "Uniform illumination, numerical aperture 0.8, 750 nm, continuous wave"),
    ], "gain_abs", None),
    ("slide", "What an annulus transmits", [
        (0, "The stop removes the rays that converge at shallow angles, leaving the band from arcsin(eps sin alpha) to alpha"),
        (0, "Every result follows from that band being narrower"),
        (0, "Numerical aperture 0.8, 750 nm"),
    ], "pupil_geom", None),
    ("slide", "Everything measured, and what it costs", [
        (0, "Depth of focus rises 44 times; the transverse spot narrows slightly, from 497 to 364 nm"),
        (0, "Peak intensity falls by 2500 times and transmitted power by 51 times"),
        (0, "An independent axial measure, the extent holding 80% of the energy, tracks the depth of focus"),
        (0, "Numerical aperture 0.8, 750 nm, continuous wave against a 1 fs pulse"),
    ], "q_costs", None),

    ("section", "Continuous wave: the ring extends the focus"),
    ("slide", "Focal field against obstruction ratio", [
        (0, "Uniform illumination, obstruction ratio 0"),
        (0, "Continuous wave, numerical aperture 0.8, 750 nm"),
        (0, "Baseline: depth of focus 2.42 um, all light transmitted"),
    ], "cw_uni_0p0", None),
    ("slide", "Focal field against obstruction ratio", [
        (0, "Uniform illumination, obstruction ratio 0.5"),
        (0, "Continuous wave, numerical aperture 0.8, 750 nm"),
        (0, "Depth of focus 3.14 um, extension 1.30"),
    ], "cw_uni_0p5", None),
    ("slide", "Focal field against obstruction ratio", [
        (0, "Uniform illumination, obstruction ratio 0.9"),
        (0, "Continuous wave, numerical aperture 0.8, 750 nm"),
        (0, "Depth of focus 11.5 um, extension 4.76"),
    ], "cw_uni_0p9", None),
    ("slide", "Focal field against obstruction ratio", [
        (0, "Uniform illumination, obstruction ratio 0.99"),
        (0, "Continuous wave, numerical aperture 0.8, 750 nm"),
        (0, "Depth of focus 107 um, extension 44.3"),
    ], "cw_uni_0p99", None),
    ("slide", "What the ring is bought with", [
        (0, "Extension against transmitted power and against peak intensity, every configuration run"),
        (0, "A truncated Gaussian at ratio 0.99 passes six parts in a hundred thousand, for a smaller extension than uniform"),
        (0, "Three numerical apertures, 750 nm, continuous wave"),
    ], "q_bought", None),

    ("section", "A pulse against continuous wave"),
    ("slide", "Focal field, continuous wave", [
        (0, "Uniform illumination, obstruction ratio 0.9, continuous wave"),
        (0, "Numerical aperture 0.8, 750 nm"),
        (0, "Reference for the pulsed case that follows"),
    ], "pi_uni_0p9_cw", None),
    ("slide", "Focal field, 1 fs pulse", [
        (0, "Uniform illumination, obstruction ratio 0.9, 1 fs pulse"),
        (0, "Numerical aperture 0.8, 750 nm"),
        (0, "Extension 4.76 at continuous wave and at 1 fs. The rings fill in, the axial extent does not change"),
    ], "pi_uni_0p9_1fs", None),
    ("slide", "Focal field, continuous wave", [
        (0, "Gaussian, alpha = 4 illumination, obstruction ratio 0.9, continuous wave"),
        (0, "Numerical aperture 0.8, 750 nm"),
        (0, "Reference for the pulsed case that follows"),
    ], "pi_gau_0p9_cw", None),
    ("slide", "Focal field, 1 fs pulse", [
        (0, "Gaussian, alpha = 4 illumination, obstruction ratio 0.9, 1 fs pulse"),
        (0, "Numerical aperture 0.8, 750 nm"),
        (0, "Extension 3.05 at continuous wave against 2.83 at 1 fs"),
    ], "pi_gau_0p9_1fs", None),
    ("slide", "The profiles behind those maps", [
        (0, "Under uniform illumination the three pulse durations lie on one curve at every obstruction ratio"),
        (0, "Under truncation the curves separate, and the pulsed focus is the longer of the two"),
        (0, "Numerical aperture 0.8, 750 nm, continuous wave against 2 fs and 1 fs"),
    ], "q_prof", None),
    ("slide", "Depth-of-focus extension against obstruction ratio", [
        (0, "Continuous wave against 2 fs and 1 fs, both illuminations"),
        (0, "Uniform is unchanged to 0.03%; truncation loses 7.5% by ratio 0.99"),
        (0, "Numerical aperture 0.8, 750 nm"),
    ], "ext_cmp_uni", None),
    ("slide", "Every configuration at once", [
        (0, "Depth of focus at 1 fs against depth of focus at continuous wave"),
        (0, "Every configuration run sits on the line of equal depth: bandwidth barely moves the depth itself"),
    ], "q_parity", None),

    ("section", "Does the comparison hold elsewhere"),
    ("slide", "Across numerical aperture", [
        (0, "Uniform stays invariant at 0.1, 0.8 and 1.2, to within 0.35%"),
        (0, "The truncated erosion grows with aperture: 6.5%, 7.5% and 9.1% at ratio 0.99"),
        (0, "750 nm, continuous wave against a 1 fs pulse"),
    ], "q_aper", None),
    ("slide", "Across the truncation parameter", [
        (0, "The erosion grows steadily with truncation: 0.03%, 0.75%, 2.5% and 7.5% for alpha 0, 1, 2 and 4"),
        (0, "At alpha 8 the rim amplitude is three parts in ten thousand and the trend breaks down; that regime is not quoted"),
        (0, "Numerical aperture 0.8, 750 nm, continuous wave against a 1 fs pulse"),
    ], "q_trunc", None),
    ("slide", "Extension lost at 1 fs against center wavelength — obstruction ratio 0.99", [
        (0, "At continuous wave the extension is identical at every color from 400 to 1300 nm, to six decimal places"),
        (0, "A pulse breaks that: bandwidth is set by duration, so the same 441 THz is a larger fraction of a smaller carrier"),
        (0, "The truncated erosion runs from 2.8% at 400 nm to 11.2% at 1300 nm"),
    ], "q_lambda", None),
    ("slide", "Transverse profile at obstruction ratio 0.9", [
        (0, "At continuous wave every configuration shows a first minimum; at 1 fs none does"),
        (0, "2 fs is the threshold, and the obstruction decides it: a thin ring keeps its structure where the full disk has lost it"),
    ], "q_rings", None),

    ("section", "Why it comes out this way"),
    ("slide", "The extension in closed form", [
        (0, "On axis the pupil contributes a window in cos theta of width cos(theta_in) minus cos(alpha)"),
        (0, "The depth of focus goes as its reciprocal, giving extension = (1 - cos alpha) / (cos theta_in - cos alpha)"),
        (0, "Nothing in that expression depends on wavelength, which is why a uniform annulus is bandwidth invariant"),
        (0, "The crosses are a 1 fs pulse falling on the same curve"),
    ], "q_law", "coords"),
    ("slide", "Where the closed form fails, and why", [
        (0, "The law treats the window as flat, ignoring the aplanatic weighting across it"),
        (0, "Its error is that weighting's variation: 2.9% at a wide open cone, and zero once a ring narrows the band"),
        (0, "Three numerical apertures, 750 nm, continuous wave"),
    ], "q_window", None),
    ("slide", "The thin ring approaches a nondiffracting beam", [
        (0, "A ring transmits a single cone angle, so its focal pattern tends to the J0 squared profile of a Bessel beam"),
        (0, "It reaches that limit only where the field is effectively scalar: to 0.003 at numerical aperture 0.1, not at 1.2"),
        (0, "Three numerical apertures, 750 nm, continuous wave"),
    ], "q_bessel", None),
    ("slide", "What the pulse actually changes", [
        (0, "A 1 fs pulse lengthens the uniform focus by 0.9% at every obstruction ratio, so the extension cancels"),
        (0, "For a truncated pupil it lengthens the unobstructed focus by 9.1% and the ring by 1.2%, and the erosion is that gap"),
        (0, "Numerical aperture 0.8, 750 nm"),
    ], "q_resp", None),
    ("slide", "Summary", [
        (0, "An annular pupil extends the depth of focus 44 times at obstruction ratio 0.99, and narrows the spot slightly"),
        (0, "It pays 2500 times in peak intensity and 51 times in transmitted power"),
        (0, "Under uniform illumination the extension is unchanged by a 1 fs pulse, at every aperture and every color"),
        (0, "Under truncation it erodes, growing with the truncation, the aperture and the center wavelength"),
        (0, "The extension follows a closed form with no wavelength in it, which is why the uniform case is invariant"),
    ], None, None),

    ("section", "Romallosa (2003) replication"),
    ("slide", "Focal intensity distribution, continuous wave", [
        (0, "Contours are percent of peak; the orange contour is the half maximum"),
        (0, "Numerical aperture 0.8, center wavelength 750 nm, refractive index 1.3"),
        (0, "The dark ring is a true zero because this cut lies along the y-axis, where the other two field components vanish"),
    ], "fig1_cw", None),
    ("slide", "Focal intensity distribution, 1 fs pulse", [
        (0, "The same map for a 1 fs pulse at numerical aperture 0.8, on the same scale"),
        (0, "The dark ring fills in: each frequency puts its zero at a different radius, so the ensemble never reaches zero anywhere"),
        (0, "That filled-in pedestal is the loss of focal quality a few-cycle pulse brings"),
    ], "fig1_pls", None),
    ("slide", "Transverse intensity profile", [
        (0, "The cut the paper plots, where only the transverse component survives"),
        (0, "Pulsing fills the zeros and slows the decay away from focus"),
        (0, "Structural content 1.060 against the published 1.062"),
        (0, "Linfoot fidelity, structural content and correlation quality."),
        (0, "numerical aperture 0.8, 750 nm, continuous wave against 1 fs"),
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
        (0, "tau = 1 fs, center wavelength 750 nm"),
    ], "fig4a", None),
    ("slide", "Fidelity and structural content versus pulse width", [
        (0, "Numerical aperture 0.8, center wavelength 750 nm"),
        (0, "Both criteria return to unity for long pulses and depart only below about 2 fs"),
        (0, "Solid lines are the reference curves quoted in the paper, which the calculation follows"),
        (0, "The departure sets in at the critical duration derived earlier, 1.25 fs"),
    ], "fig4b", None),
    ("slide", "Two-photon excitation microscope", [
        (0, "The two-photon response is the squared intensity, so it weights the focal core more heavily"),
        (0, "Departures from unity are roughly a third of the single-photon case at the same duration"),
        (0, "Spectral broadening therefore degrades two-photon excitation more weakly, as the paper concludes"),
        (0, "numerical aperture 0.8, center wavelength 750 nm"),
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
        (0, "The alpha sets how hard the aperture clips the beam"),
        (0, "Gaussian pupil amplitude. The alpha is the squared ratio of aperture radius to beam waist."),
    ], None, "apod"),
    ("slide", "How the input changes with the alpha", [
        (0, "Dashed: uniform illumination, which fills the pupil evenly"),
        (0, "Colored: increasing alpha, concentrating the light toward the center"),
        (0, "A coefficient near zero recovers uniform illumination and four or more is effectively untruncated"),
        (0, "numerical aperture 0.8, continuous wave at 750 nm"),
    ], "apod_in", None),
    ("slide", "The focus that results from each input", [
        (0, "Numerical aperture 0.8, center wavelength 750 nm"),
        (0, "Each curve is the focus produced by the input of the same color"),
        (0, "Stronger truncation uses less of the aperture, so the focus is wider"),
        (0, "Uniform illumination gives the tightest focus and the strongest side lobes"),
    ], "apod_out", None),
    ("slide", "When does Gaussian illumination behave like uniform?", [
        (0, "The pupil face for increasing alpha, with the amplitude surviving at the aperture edge"),
        (0, "A coefficient near zero fills the aperture evenly; a coefficient of one leaves 37% at the edge; four or more leaves about 2%"),
        (0, "numerical aperture 0.8, continuous wave at 750 nm"),
    ], "illum_row", None),
    ("slide", "Edge amplitude decides when the two are interchangeable", [
        (0, "Edge amplitude falls as the exponential of minus the alpha"),
        (0, "Below about 0.01 the edge is within 1% of uniform, so the two calculations are interchangeable"),
        (0, "Above four the beam is narrower than the aperture and the truncation stops mattering"),
        (0, "Continuous wave at 750 nm"),
    ], "illum_edge", None),
    ("slide", "Axial profile at low numerical aperture", [
        (0, "Along the axis at numerical aperture 0.1, vector and scalar theory agree and Gaussian input only lengthens the focus"),
        (0, "The half-maximum line marks the depth of focus"),
        (0, "numerical aperture 0.1, continuous wave at 750 nm"),
    ], "fpg_axial_lo", None),
    ("slide", "Axial profile at high numerical aperture", [
        (0, "At numerical aperture 0.9 the scalar prediction no longer tracks the vector result along the axis"),
        (0, "Gaussian input keeps the two closer together than uniform input does"),
        (0, "numerical aperture 0.9, continuous wave at 750 nm"),
    ], "fpg_axial_hi", None),
    ("slide", "Focal width against the alpha", [
        (0, "Numerical aperture 0.8, center wavelength 750 nm"),
        (0, "The focal width grows steadily as the alpha rises, from 473 nm at uniform illumination"),
        (0, "Stronger truncation uses less of the aperture, which is what broadens the focus"),
    ], "apod_alpha", None),
    ("slide", "Field maps for uniform and Gaussian input, side by side", [
        (0, "Iso-intensity contours in the r-z plane, same scale"),
        (0, "The Gaussian focus is wider and longer"),
        (0, "Continuous wave at 750 nm"),
    ], "apod_maps", None),
    ("slide", "Focal plane intensity at numerical aperture 0.1", [
        (0, "Solid: vector; dashed: scalar Debye, same input"),
        (0, "The two lie on top of one another, so the apodized implementation matches the analytic result"),
        (0, "Dotted: uniform illumination, narrower because it uses the full aperture"),
        (0, "numerical aperture 0.1, continuous wave at 750 nm"),
    ], "fpg_prof_lo", None),
    ("slide", "Iso-intensity contours at numerical aperture 0.1", [
        (0, "Contours of the same field in the r-z plane, dashed lines at the Airy radius of 4.575 µm"),
        (0, "The focus is long and smooth, with no structure beyond the central lobe"),
        (0, "numerical aperture 0.1, continuous wave at 750 nm"),
    ], "fpg_cont_lo", None),
    ("slide", "Focal plane intensity at numerical aperture 0.9", [
        (0, "The same three curves at high numerical aperture"),
        (0, "The vector and scalar curves now separate, by about 3% in integrated profile area"),
        (0, "The Gaussian vector field is broader because the longitudinal component has appeared"),
        (0, "numerical aperture 0.9, continuous wave at 750 nm"),
    ], "fpg_prof_hi", None),
    ("slide", "Iso-intensity contours at numerical aperture 0.9", [
        (0, "Contours of the same field, dashed lines at the Airy radius of 0.508 µm"),
        (0, "The focus is an order of magnitude shorter in z than at numerical aperture 0.1"),
        (0, "numerical aperture 0.9, continuous wave at 750 nm"),
    ], "fpg_cont_hi", None),

    ("slide", "Gaussian input at low numerical aperture against the known scalar result", [
        (0, "Thick faint curves: the paraxial truncated-Gaussian reference"),
        (0, "Thin curves: the vector calculation, which overlaps the reference for every alpha"),
        (0, "Continuous wave at 750 nm"),
    ], "parax_a", None),
    ("slide", "Deviation from the known low-numerical-aperture result", [
        (0, "Each curve is one alpha"),
        (0, "All of them sit near the numerical floor, so the apodized implementation is validated before high numerical aperture"),
        (0, "Continuous wave at 750 nm"),
    ], "parax_b", None),
    ("slide", "Focal field for alpha = 0", [
        (0, "Two-dimensional map with cross-sections for alpha = 0 at numerical aperture 0.8"),
        (0, "Focal width 475 nm, depth of focus 2.40 µm, 1.00 times the uniform depth"),
    ], "atlas_g_at0", None),
    ("slide", "Focal field for alpha = 0.5", [
        (0, "Two-dimensional map with cross-sections for alpha = 0.5 at numerical aperture 0.8"),
        (0, "Focal width 500 nm, depth of focus 2.40 µm, 1.00 times the uniform depth"),
    ], "atlas_g_at0p5", None),
    ("slide", "Focal field for alpha = 1", [
        (0, "Two-dimensional map with cross-sections for alpha = 1 at numerical aperture 0.8"),
        (0, "Focal width 525 nm, depth of focus 2.49 µm, 1.04 times the uniform depth"),
    ], "atlas_g_at1", None),
    ("slide", "Focal field for alpha = 2", [
        (0, "Two-dimensional map with cross-sections for alpha = 2 at numerical aperture 0.8"),
        (0, "Focal width 600 nm, depth of focus 2.77 µm, 1.15 times the uniform depth"),
    ], "atlas_g_at2", None),
    ("slide", "Focal field for alpha = 4", [
        (0, "Two-dimensional map with cross-sections for alpha = 4 at numerical aperture 0.8"),
        (0, "Focal width 725 nm, depth of focus 3.78 µm, 1.58 times the uniform depth"),
    ], "atlas_g_at4", None),
    ("slide", "All three components at alpha = 4", [
        (0, "Total intensity including the longitudinal and cross-polarization terms"),
        (0, "numerical aperture 0.8, continuous wave at 750 nm"),
    ], "cmp_full_gaussian_4p0", None),
    ("section", "Numerical aperture: uniform against Gaussian input"),
    ("slide", "When does scalar theory diverge from vector theory?", [
        (0, "Scalar theory is fast but approximate, vector theory is accurate but slower"),
        (0, "The question is where the approximation stops being acceptable, for each input"),
        (0, "Key result: Gaussian illumination tolerates the scalar approximation to higher numerical aperture than uniform, because it suppresses the steep rays that generate the longitudinal field"),
    ], None, None),
    ("slide", "Focal profiles at low numerical aperture", [
        (0, "At numerical aperture 0.1 the vector and scalar profiles lie on top of the analytic Airy pattern"),
        (0, "Continuous wave at 750 nm"),
    ], "nac_lo", None),
    ("slide", "Focal profiles at high numerical aperture", [
        (0, "At numerical aperture 1.2 the total vector intensity is measurably broader than the scalar prediction"),
        (0, "The extra width is the longitudinal field, which scalar theory has no way to represent"),
        (0, "Continuous wave at 750 nm"),
    ], "nac_hi", None),
    ("slide", "Focal profiles against numerical aperture, uniform input", [
        (0, "Uniform illumination, center wavelength 750 nm, numerical aperture rising through the series"),
        (0, "The vector profile pulls away from the scalar one as the marginal rays gain weight"),
    ], "naprof_uni", None),
    ("slide", "Focal profiles against numerical aperture, Gaussian input", [
        (0, "Gaussian input with alpha = 4, center wavelength 750 nm"),
        (0, "The same series stays closer to scalar theory because the pupil edge carries little light"),
    ], "naprof_gau", None),
    ("slide", "Choosing the metric: why focal width", [
        (0, "All three compare the same pair of profiles"),
        (0, "Width registers the departure first, near aperture 0.4"),
        (0, "Error follows later; correlation never crosses 1%"),
        (0, "Fractional size error, and root-mean-square difference."),
        (0, "Continuous wave at 750 nm"),
    ], "metric_choice", "metrics"),
    ("slide", "Why the scalar prediction fails: the longitudinal component", [
        (0, "Total intensity separated into its three components, aperture 1.2"),
        (0, "The longitudinal component carries 22% of the focal energy"),
        (0, "It fills the scalar profile's zero, widening the focus"),
        (0, "The three focal field components for an x-polarized input, at azimuth phi."),
        (0, "Continuous wave at 750 nm"),
    ], "naprof_comp", "components"),
    ("slide", "Focal width against numerical aperture", [
        (0, "The width of the total intensity moves away from the scalar prediction as numerical aperture increases"),
        (0, "The grey line is the Airy width, the limit both start from at low numerical aperture"),
        (0, "The separation is the spot-size error the scalar approximation would introduce"),
        (0, "Continuous wave at 750 nm"),
    ], "nac3", None),
    ("slide", "Focal-width deviation of the total intensity from scalar theory", [
        (0, "The deviation passes 1% near numerical aperture 0.45 for uniform and 0.55 for Gaussian with alpha = 4, and 5% near 0.90 and 1.15"),
        (0, "Gaussian illumination departs later because it suppresses the marginal rays that generate the longitudinal field"),
        (0, "Continuous wave at 750 nm"),
    ], "apt1", None),
    ("slide", "Error against the scalar prediction", [
        (0, "Point-by-point error of the total intensity against the scalar profile"),
        (0, "Uniform crosses the 1% level near numerical aperture 0.63"),
        (0, "Gaussian with alpha = 4 crosses it only near 0.81"),
        (0, "Continuous wave at 750 nm"),
    ], "apt3", None),
    ("slide", "Wavelength does not move the threshold", [
        (0, "One color per wavelength, solid for uniform and dashed for Gaussian"),
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
        (0, "Continuous wave at 750 nm, uniform illumination"),
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
        (0, "Continuous wave at 750 nm"),
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
        (0, "Total intensity including the longitudinal and cross-polarization terms"),
        (0, "On axis the two coincide, so the difference is entirely off-axis"),
        (0, "Continuous wave at 750 nm"),
    ], "cmp_full_NA_1p2", None),
    ("section", "Annular apertures"),
    ("slide", "What the obstruction ratio means", [
        (0, "The obstruction ratio is the inner radius divided by the outer radius of the pupil"),
        (0, "Zero is the full disk and a value approaching one is a high obstruction ratio"),
        (0, "Annular field by subtraction at the level of the field, and the paraxial extension. Epsilon is the inner over outer pupil radius."),
        (0, "Continuous wave at 750 nm"),
    ], "pupil_geom", "babinet"),
    ("slide", "What the ring transmits of the input", [
        (0, "The same obstruction removes very different amounts of light depending on the input"),
        (0, "At obstruction 0.5 a uniform pupil keeps 75% of the power, a Gaussian with alpha = 4 only 13%"),
        (0, "Continuous wave at 750 nm"),
    ], "pupil_input", None),
    ("slide", "Transverse profile against obstruction ratio", [
        (0, "Each color is one obstruction ratio"),
        (0, "A larger obstruction narrows the central lobe"),
        (0, "The side lobes rise at the same time, which is the cost of that narrowing"),
        (0, "Continuous wave at 750 nm"),
    ], "ann1", None),
    ("slide", "Axial profile against obstruction ratio", [
        (0, "Each color is one obstruction ratio"),
        (0, "The axial profile broadens steadily as the center of the pupil is blocked"),
        (0, "Continuous wave at 750 nm"),
    ], "ann2", None),
    ("slide", "How depth of focus is measured", [
        (0, "The axial profile is taken through the focus at r = 0 and normalized to its own maximum"),
        (0, "Depth of focus is the full width at half maximum of that profile, obtained by interpolating the half-maximum crossing"),
        (0, "The extension is the ratio of that width to the same configuration with no obstruction, at the same aperture, illumination and pulse duration"),
        (0, "Past obstruction ratio 0.95 the profile no longer has a single lobe, and an extent containing 80% of the on-axis energy is reported alongside it"),
    ], None, "measured_dof"),
    ("slide", "How transmitted power and peak intensity are measured", [
        (0, "Transmitted power is the fraction of the incident power that passes the annulus, integrated over the pupil with the aplanatic area element"),
        (0, "For uniform illumination this reduces to one minus the obstruction ratio squared; for a truncated Gaussian it falls faster, since the amplitude is concentrated within the blocked region"),
        (0, "Peak intensity is the on-axis focal value relative to the unobstructed pupil at the same aperture and illumination"),
        (0, "The two differ because power that passes the pupil is redistributed over a longer focus and into the side lobes"),
    ], None, "measured_power"),
    ("slide", "What the extension is measured against", [
        (0, "Axial profile with no central stop, beside the profile at obstruction ratio 0.9 (numerical aperture 0.8, uniform, 750 nm)"),
        (0, "Depth of focus is 2.42 um with no obstruction and 11.52 um at ratio 0.9, a ratio of 4.76"),
        (0, "Every extension quoted in this section is the ratio of these two depths, taken at half maximum"),
    ], ["gain_abs", "gain_norm"], None),
    ("slide", "Depth of focus against obstruction ratio", [
        (0, "Depth of focus grows with obstruction and follows the paraxial law at low numerical aperture"),
        (0, "At high numerical aperture the vector result falls short of the paraxial prediction"),
        (0, "At obstruction 0.9 the paraxial law gives 5.26 times; the computed gain is 5.25 at numerical aperture 0.13, 4.76 at 0.8 and 3.67 at 1.17"),
        (0, "Continuous wave at 750 nm"),
    ], "ann3", None),
    ("slide", "Uniform and Gaussian illumination compared", [
        (0, "Solid: uniform illumination, dashed: truncated Gaussian"),
        (0, "Both follow the same depth-of-focus trend, so the extension does not depend on the input"),
        (0, "Dotted: the paraxial law, which the high-numerical-aperture result falls short of"),
        (0, "Continuous wave at 750 nm"),
    ], "ann4", None),
    ("slide", "Peak-intensity cost of the obstruction", [
        (0, "Each curve is one numerical aperture"),
        (0, "The peak intensity falls steadily as the obstruction grows, which is the price of the longer focus"),
        (0, "Continuous wave at 750 nm"),
    ], "anne1", None),
    ("slide", "Encircled-energy cost of the obstruction", [
        (0, "Energy in the central lobe drops as the obstruction ratio increases"),
        (0, "It is moved into the side lobes, not lost"),
        (0, "Continuous wave at 750 nm"),
    ], "anne2", None),
    ("slide", "Departure from scalar theory for an annular pupil", [
        (0, "Solid: uniform; dashed: Gaussian"),
        (0, "A larger obstruction moves every curve left: uniform falls 0.63 to 0.48"),
        (0, "At ratio 0.9 both reach 0.48, since only marginal rays remain"),
        (0, "Continuous wave at 750 nm"),
    ], "annsca_rmse", None),
    ("slide", "Focal-width departure for an annular pupil", [
        (0, "Solid: uniform; dashed: Gaussian"),
        (0, "The width departs from scalar theory sooner as the obstruction ratio increases"),
        (0, "Continuous wave at 750 nm"),
    ], "annsca_fwhm", None),
    ("slide", "Thin annulus against the published closed form", [
        (0, "Solid: our calculation for a thin Gaussian ring at low numerical aperture; dashed: their focal-plane form, which it follows"),
        (0, "Dotted: the infinitely thin ring, the non-diffracting limit whose side lobes decay far more slowly"),
        (0, "Sheppard and Wilson closed forms for a Gaussian annulus."),
        (0, "Continuous wave at 750 nm"),
    ], "shep1", "sheppard"),
    ("slide", "The axial profile is predicted, not fitted", [
        (0, "The prediction matches the independently computed profile, so the agreement is not a free-parameter fit"),
        (0, "Continuous wave at 750 nm"),
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
        (0, "Continuous wave at 750 nm"),
    ], "cmp_full_annular_0p9", None),
    ("slide", "Focal field for obstruction ratio 0.99", [
        (0, "Two-dimensional map with cross-sections for obstruction ratio 0.99 at numerical aperture 0.8"),
        (0, "Focal width 350 nm, depth of focus 12.00 µm, 5.00 times the unobstructed depth"),
    ], "atlas_e_0p99", None),
    ("section", "Pulsed sources with annular apertures"),
    ("slide", "The question", [
        (0, "Annular apertures extend the depth of focus, and few-cycle pulses degrade the focus"),
        (0, "Whether the two interact: does spectral broadening reduce the extension obtained from a central obstruction?"),
        (0, "Each wavelength in the pulse forms its own annular focus, so the extension could in principle wash out"),
        (0, "Pulse spectrum and the time-integrated focal intensity: a Gaussian in frequency of width set by the duration."),
    ], None, "pulse"),
    ("slide", "Axial profiles for pulsed annular illumination", [
        (0, "Obstruction ratio 0.99, numerical aperture 0.8, center wavelength 750 nm"),
        (0, "On-axis intensity for each obstruction ratio, from continuous wave down to 1 fs"),
        (0, "The pulsed curves lie almost exactly on the continuous-wave ones at every obstruction"),
    ], "pa_axial", None),
    ("slide", "The depth-of-focus extension is bandwidth invariant", [
        (0, "Depth of focus relative to the unobstructed case, for each pulse duration"),
        (0, "At obstruction 0.9 the extension is 4.76 times, identical from continuous wave to 1 fs"),
        (0, "At obstruction 0.99 it is 44.35 against 44.33, four parts in ten thousand"),
        (0, "Annular field by subtraction at the level of the field, and the paraxial extension. Epsilon is the inner over outer pupil radius."),
    ], "pa_dof", "babinet"),
    ("slide", "Pulsing lengthens the focus by a fixed 1%", [
        (0, "Obstruction ratio 0.99, numerical aperture 0.8, 750 nm"),
        (0, "The 1 fs focus is 1.010 times longer than continuous wave"),
        (0, "The same factor at every obstruction ratio"),
    ], "pa_trans", None),
    ("slide", "The same comparison without a ring", [
        (0, "Transverse profile, full disk, each pulse duration"),
        (0, "About 1.06 at 1 fs, full pupil or thin ring alike"),
        (0, "Contrast is lost at the same rate regardless of obstruction"),
        (0, "Linfoot criteria for a test profile a against reference r: fidelity, structural content, correlation quality."),
    ], "pa_linfoot", "linfoot"),

    ("slide", "The same question for a Gaussian input", [
        (0, "A truncated Gaussian puts less light on the marginal rays the ring keeps, so its extension is weaker to begin with"),
        (0, "At obstruction 0.9 the extension is 3.05 times for a Gaussian against 4.76 for uniform"),
        (0, "The question is whether spectral broadening now interacts with it"),
        (0, "Continuous wave at 750 nm"),
    ], "pag_ratio", None),
    ("slide", "Bandwidth invariance is exact for uniform, approximate for Gaussian", [
        (0, "For uniform illumination the extension is unchanged from continuous wave to 1 fs"),
        (0, "For a Gaussian it erodes from 3.05 to 2.83 at obstruction 0.9, about seven %"),
        (0, "Pulsing lengthens the unobstructed Gaussian focus more, which dilutes the ratio"),
    ], "pag_pulse", None),

    ("slide", "Obstruction ratio 0.5, continuous wave", [
        (0, "Baseline for the ring: continuous-wave illumination through an obstruction ratio of 0.5"),
        (0, "Numerical aperture 0.8, total intensity of all three components, physical coordinates"),
        (0, "Continuous wave at 750 nm"),
    ], "atlas_pa_e5_cw", None),
    ("slide", "Obstruction ratio 0.5, 2 fs pulse", [
        (0, "The same ring driven by a 2 fs pulse, center wavelength 750 nm"),
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
    ("slide", "Does the ring survive bandwidth at low numerical aperture?", [
        (0, "Depth-of-focus gain against pulse duration at numerical aperture 0.1 with uniform input, 750 nm"),
        (0, "Obstruction ratios 0, 0.5 and 0.99, each measured against its own unobstructed reference"),
        (0, "The gain is flat across the bandwidth, so the ring gives the same extension to a 1 fs pulse as to continuous light"),
    ], "pag_lo_uni", None),
    ("slide", "The same question for Gaussian input at low numerical aperture", [
        (0, "Numerical aperture 0.1, Gaussian input with alpha = 4, 750 nm"),
        (0, "At obstruction 0.5 the gain erodes by about 2% from continuous wave to 1 fs"),
        (0, "Truncating the pupil removes the edge rays the ring relies on, so the two effects compete"),
    ], "pag_lo_gau", None),
    ("slide", "The ring at high numerical aperture, uniform input", [
        (0, "Numerical aperture 1.2, uniform input, 750 nm"),
        (0, "The gain is still bandwidth invariant, but its size falls well below the paraxial prediction"),
    ], "pag_hi_uni", None),
    ("slide", "The ring at high numerical aperture, Gaussian input", [
        (0, "Numerical aperture 1.2, Gaussian input with alpha = 4, 750 nm"),
        (0, "At obstruction 0.5 the gain drops below one: the obstruction shortens the focus instead of extending it"),
        (0, "Gaussian truncation has already starved the pupil edge, so blocking the center removes what little weight was left"),
    ], "pag_hi_gau", None),
    ("section", "Annular apertures: truncation and obstruction"),
    ("slide", "What was varied, and what came out", [
        (0, "Varied Gaussian truncation parameter and the obstruction ratio, each for continuous wave and with a pulsed source"),
        (0, "Raising the obstruction ratio extends the depth of focus, by a large factor as the ring thins"),
        (0, "Truncating the illumination reduces DOF extension"),
        (0, "Pulsed waves leaves the extension unchanged under uniform illumination"),
        (0, "For Gaussian illumination truncation, reduces it further"),
        (0, "Seven obstruction ratios from 0 to 0.99, numerical aperture 0.8"),
    ], None, None),
    ("slide", "Settings", [
        (0, "Numerical aperture 0.8, center wavelength 750 nm, refractive index 1.3"),
        (0, "Truncation parameter alpha: 0 for uniform, 4 for the truncated Gaussian"),
        (0, "Obstruction ratio: 0 through 0.99, the inner over outer pupil radius"),
        (0, "Continuous wave, and a 1 fs pulse of bandwidth 441 THz, 1.10 times the carrier"),
        (0, "On the field maps: orange is the half maximum, red dashed the Airy radius"),
    ], None, "babinet"),

    ("section", "Continuous wave, uniform illumination"),
    ("slide", "Observations", [
        (0, "Uniform illumination, continuous wave"),
        (0, "Depth of focus rises from 2.42 to 107 um as the obstruction ratio goes from 0 to 0.99"),
        (0, "The extension follows from removing the rays that converge at shallow angles"),
        (0, "The slides that follow show the focal field at each ratio"),
    ], None, None),
    ("slide", "Focal field against obstruction ratio", [
        (0, "Uniform illumination, obstruction ratio 0"),
        (0, "Continuous wave, numerical aperture 0.8, 750 nm"),
        (0, "Baseline: depth of focus 2.42 um, all light transmitted"),
    ], "cw_uni_0p0", None),
    ("slide", "Focal field against obstruction ratio", [
        (0, "Uniform illumination, obstruction ratio 0.5"),
        (0, "Continuous wave, numerical aperture 0.8, 750 nm"),
        (0, "Depth of focus 3.14 um, extension 1.30"),
    ], "cw_uni_0p5", None),
    ("slide", "Focal field against obstruction ratio", [
        (0, "Uniform illumination, obstruction ratio 0.9"),
        (0, "Continuous wave, numerical aperture 0.8, 750 nm"),
        (0, "Depth of focus 11.5 um, extension 4.76"),
    ], "cw_uni_0p9", None),
    ("slide", "Focal field against obstruction ratio", [
        (0, "Uniform illumination, obstruction ratio 0.99"),
        (0, "Continuous wave, numerical aperture 0.8, 750 nm"),
        (0, "Depth of focus 107 um, extension 44.3"),
    ], "cw_uni_0p99", None),
    ("slide", "Depth-of-focus extension against obstruction ratio", [
        (0, "Uniform illumination, continuous wave against 2 fs and 1 fs"),
        (0, "The three curves lie on top of one another at every obstruction ratio: the extension does not depend on the bandwidth"),
        (0, "Numerical aperture 0.8, 750 nm"),
    ], "ext_cmp_uni", None),

    ("section", "Continuous wave, truncated Gaussian"),
    ("slide", "Observations", [
        (0, "Gaussian illumination at alpha = 4, continuous wave"),
        (0, "In absolute terms the focus is longer than uniform at every ratio, starting at 3.85 um against 2.42 um with no obstruction, since the beam fills only the inner pupil"),
        (0, "The extension is nonetheless smaller at every ratio, because it is measured against that longer starting point"),
        (0, "By ratio 0.99 both illuminations give the same focus, since only rays near the pupil edge are transmitted"),
    ], None, None),
    ("slide", "Focal field against obstruction ratio", [
        (0, "Gaussian illumination, alpha = 4, obstruction ratio 0"),
        (0, "Continuous wave, numerical aperture 0.8, 750 nm"),
        (0, "Baseline: depth of focus 3.85 um, already longer than uniform"),
    ], "cw_gau_0p0", None),
    ("slide", "Focal field against obstruction ratio", [
        (0, "Gaussian illumination, alpha = 4, obstruction ratio 0.5"),
        (0, "Continuous wave, numerical aperture 0.8, 750 nm"),
        (0, "Depth of focus 4.14 um, extension 1.07"),
    ], "cw_gau_0p5", None),
    ("slide", "Focal field against obstruction ratio", [
        (0, "Gaussian illumination, alpha = 4, obstruction ratio 0.9"),
        (0, "Continuous wave, numerical aperture 0.8, 750 nm"),
        (0, "Depth of focus 11.7 um, extension 3.05"),
    ], "cw_gau_0p9", None),
    ("slide", "Focal field against obstruction ratio", [
        (0, "Gaussian illumination, alpha = 4, obstruction ratio 0.99"),
        (0, "Continuous wave, numerical aperture 0.8, 750 nm"),
        (0, "Depth of focus 107 um, extension 27.8"),
    ], "cw_gau_0p99", None),
    ("slide", "Depth-of-focus extension against obstruction ratio", [
        (0, "Uniform against Gaussian at alpha = 4, continuous wave"),
        (0, "The Gaussian curve lies below at every ratio. This is the extension, each illumination against its own unobstructed focus; in absolute depth the Gaussian focus is the longer of the two"),
        (0, "Numerical aperture 0.8, 750 nm"),
    ], "ext_cw", None),

    ("section", "Pulsed against continuous wave"),
    ("slide", "Observations", [
        (0, "A 1 fs pulse against continuous wave, both illuminations"),
        (0, "Under uniform illumination the extension is unchanged at all seven obstruction ratios, to within 0.0%"),
        (0, "Under truncation it decreases monotonically with the ratio: 0.8% at 0.3, 2.6% at 0.5, 7.2% at 0.9 and 7.5% at 0.99"),
        (0, "The rings fill in under the pulse because each frequency places its zeros at a different radius"),
    ], None, None),
    ("slide", "Focal field, continuous wave", [
        (0, "Uniform illumination, obstruction ratio 0.9, continuous wave"),
        (0, "Numerical aperture 0.8, 750 nm"),
        (0, "Reference for the pulsed case that follows"),
    ], "pi_uni_0p9_cw", None),
    ("slide", "Focal field, 1 fs pulse", [
        (0, "Uniform illumination, obstruction ratio 0.9, 1 fs pulse"),
        (0, "Numerical aperture 0.8, 750 nm"),
        (0, "Extension 4.76 at continuous wave and at 1 fs. The rings fill in, the axial extent does not change"),
    ], "pi_uni_0p9_1fs", None),
    ("slide", "Focal field, continuous wave", [
        (0, "Gaussian, alpha = 4 illumination, obstruction ratio 0.9, continuous wave"),
        (0, "Numerical aperture 0.8, 750 nm"),
        (0, "Reference for the pulsed case that follows"),
    ], "pi_gau_0p9_cw", None),
    ("slide", "Focal field, 1 fs pulse", [
        (0, "Gaussian, alpha = 4 illumination, obstruction ratio 0.9, 1 fs pulse"),
        (0, "Numerical aperture 0.8, 750 nm"),
        (0, "Extension 3.05 at continuous wave against 2.83 at 1 fs"),
    ], "pi_gau_0p9_1fs", None),
    ("slide", "Depth-of-focus extension against obstruction ratio", [
        (0, "Gaussian at alpha = 4, continuous wave against 2 fs and 1 fs"),
        (0, "The pulsed curves fall below the continuous-wave curve, and the gap widens with the obstruction ratio"),
        (0, "Numerical aperture 0.8, 750 nm"),
    ], "ext_cmp_gau", None),
    ("slide", "Depth-of-focus extension against obstruction ratio", [
        (0, "Uniform against Gaussian at alpha = 4, 1 fs pulse"),
        (0, "The gap between the two illuminations is wider than at continuous wave"),
        (0, "Numerical aperture 0.8, 750 nm"),
    ], "ext_1fs", None),

    ("section", "Annular apertures with pulsed sources"),
    ("slide", "What was done", [
        (0, "Computed the focal field for an annular pupil over the following parameter values"),
        (1, "Numerical aperture: 0.1, 0.8, 1.2"),
        (1, "Illumination: uniform, and Gaussian with alpha = 4"),
        (1, "Obstruction ratio: 0, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99"),
        (1, "Pulse duration: continuous wave, 2 fs, 1 fs"),
        (0, "Each configuration is referred to two references: the same pupil without an obstruction, and the same pupil at continuous wave"),
        (0, "Measured transverse full width at half maximum, depth of focus, transmitted power, on-axis peak intensity and side-lobe ratio"),
        (0, "Recomputed the root-mean-square error between vector and scalar profiles under two profile normalizations, peak and transmitted power, each with and without weighting the radial average by the area element"),
        (0, "Center wavelength 750 nm, refractive index 1.3"),
    ], None, None),
    ("slide", "Key results", [
        (0, "Annular pupil: depth of focus increases with obstruction ratio and transmitted power decreases over the same range"),
        (0, "Illumination: a truncated Gaussian gives a smaller extension than uniform illumination at every obstruction ratio"),
        (0, "Obstruction ratio: the extension is obtained by discarding light. At ratio 0.9 the annulus lets through 19% of the incident light, and the intensity at the focal point falls to 3.6% of its unobstructed value"),
        (0, "Numerical aperture: the paraxial expression overstates the extension by a third at numerical aperture 1.2. The exact form derived from the axial phase reproduces the computed values to 2% at every aperture, and should be used in its place"),
        (0, "Pulse duration: the extension is insensitive to bandwidth under uniform illumination and decreases under Gaussian truncation"),
        (0, "Normalization: the root-mean-square error threshold depends on both the profile normalization and on whether the radial average is weighted by area; it does not agree with the width criterion under any combination"),
    ], None, None),

    ("slide", "The three quantities measured", [
        (0, "Depth of focus: full width at half maximum of the axial profile at r = 0"),
        (0, "Extension: that width divided by the same configuration with no obstruction"),
        (0, "Focal width: full width at half maximum of the radial profile at z = 0"),
        (0, "Transmitted power: fraction of the incident light passing the pupil"),
        (0, "Peak intensity: on-axis focal value relative to the unobstructed pupil"),
    ], None, "quantities"),
    ("slide", "Mechanism", [
        (0, "Central stop removes the shallow-angle rays, keeps those near the pupil edge"),
        (0, "Narrower range of convergence angles -> rays stay in phase over a longer axial distance -> DOF extends"),
        (0, "Higher obstruction ratio -> longer focus, narrower central peak, stronger side lobes, less light transmitted"),
        (0, "The extension comes from discarding rays, not from adding them, so every gain is paid for in transmitted light"),
    ], None, "babinet"),
    ("section", "Varying the annular pupil"),
    ("slide", "What is changed", [
        (0, "The inner region of the pupil is removed, leaving an annulus"),
        (0, "The field is the difference of two disks taken at the level of the field, so the coherent cross terms are retained"),
        (0, "Epsilon is the ratio of inner to outer pupil radius (numerical aperture 0.8, 750 nm)"),
    ], ["pupil_geo_a", "pupil_geo_b", "pupil_geo_c"], "babinet"),
    ("slide", "Depth of focus against obstruction ratio", [
        (0, "Depth of focus increases from 2.42 to 107 um over 0 <= eps <= 0.99 (numerical aperture 0.8, uniform, 750 nm)"),
        (0, "The paraxial expression is plotted alongside the computed values"),
    ], "ab_0p8_gain", None),
    ("slide", "Focal field at obstruction ratio 0.9", [
        (0, "Two-dimensional map with the transverse and axial profiles"),
        (0, "Dotted curve: the unobstructed disk at the same aperture"),
        (0, "The axial profile is extended and the side lobes are raised"),
        (0, "Numerical aperture 0.8, uniform, continuous wave at 750 nm"),
    ], "ag_0p8_uni_0p9", None),

    ("slide", "Observations: the annular pupil", [
        (0, "Depth of focus increases monotonically with obstruction ratio, from 2.42 to 107 um over 0 <= eps <= 0.99 at numerical aperture 0.8"),
        (0, "The increase follows from removing the rays that converge at shallow angles, so it is obtained by discarding power rather than by adding it"),
        (0, "Two quantities record what is discarded: the fraction of the incident light that gets past the annulus, and the intensity at the focal point relative to the unobstructed pupil"),
    ], None, None),

    ("section", "Varying the illumination"),
    ("slide", "What is changed", [
        (0, "The incident amplitude across the pupil, from flat to a truncated Gaussian"),
        (0, "The alpha is the squared ratio of aperture radius to beam waist: the edge amplitude is 1.00 for uniform and 0.02 at alpha = 4"),
        (0, "Continuous wave at 750 nm"),
    ], "illum_row", "apod"),
    ("slide", "Focal field for each illumination", [
        (0, "Left: uniform. Right: Gaussian with alpha = 4. Both at obstruction ratio 0.5 (numerical aperture 0.8, continuous wave at 750 nm)"),
        (0, "The Gaussian focus is wider, and its transmitted power is 0.135 against 0.750 for uniform"),
    ], ["cmp_in_uni", "cmp_in_gau"], None),
    ("slide", "Transmitted power for each illumination", [
        (0, "Uniform illumination transmits 0.750 of the incident power at eps = 0.5; a Gaussian at alpha = 4 transmits 0.135 (numerical aperture 0.8, 750 nm)"),
        (0, "The truncated Gaussian carries its amplitude in the region the obstruction removes, so the two are not separable"),
    ], "eb_pupil", None),
    ("slide", "Axial profiles for each illumination", [
        (0, "Axial position in units of the unobstructed depth of focus (numerical aperture 0.8, uniform, 750 nm)"),
        (0, "Each Gaussian curve is shorter than the uniform curve at the same obstruction ratio"),
        (0, "At numerical aperture 0.8 the unobstructed depth of focus is 2.42 um for uniform and 3.85 um for Gaussian with alpha = 4"),
    ], "ac_uni_0p8_ax", None),

    ("slide", "Extension against obstruction ratio, for each alpha", [
        (0, "One curve per alpha, uniform through alpha = 8, with the paraxial expression for reference"),
        (0, "At obstruction ratio 0.9 the extension is 4.76 for uniform, 3.05 at alpha = 4, 1.63 at alpha = 8"),
        (0, "At alpha = 8 the extension falls below unity at obstruction ratio 0.5, giving 0.95"),
        (0, "numerical aperture 0.8, continuous wave at 750 nm"),
    ], "ts_gain", None),
    ("slide", "Transmitted power against obstruction ratio, for each alpha", [
        (0, "The transmitted power falls faster the more strongly the pupil is truncated, since the incident amplitude and the obstruction occupy the same region"),
        (0, "At obstruction ratio 0.5 the transmitted power is 0.750 for uniform, 0.135 at alpha = 4 and 0.018 at alpha = 8"),
        (0, "numerical aperture 0.8, continuous wave at 750 nm"),
    ], "ts_trans", None),
    ("slide", "Focal width against obstruction ratio, for each alpha", [
        (0, "The unobstructed width grows with the alpha, from 497 nm for uniform to 1000 nm at alpha = 8"),
        (0, "All curves converge near 380 nm as the obstruction ratio approaches unity, since only rays near the pupil edge are transmitted"),
        (0, "numerical aperture 0.8, continuous wave at 750 nm"),
    ], "ts_width", None),
    ("slide", "Observations: the illumination", [
        (0, "A truncated Gaussian gives a smaller extension than uniform illumination at every obstruction ratio, by roughly a third"),
        (0, "At alpha = 4 the incident amplitude is concentrated within the inner pupil, which is the region the obstruction removes, so the two are not independent"),
        (0, "At numerical aperture 0.8, eps = 0.5 the transmitted power is 0.750 for uniform and 0.135 for Gaussian"),
        (0, "As eps approaches unity all illuminations give the same focus, since only rays near the pupil edge are transmitted"),
        (0, "Sweeping the alpha, the extension at eps = 0.9 falls from 4.76 for uniform to 3.05 at alpha = 4 and 1.63 at alpha = 8"),
    ], None, None),

    ("section", "Varying the obstruction ratio"),
    ("slide", "What is changed", [
        (0, "Epsilon is raised from 0 to 0.99 with the aperture and the illumination held fixed"),
        (0, "Values examined: 0, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99"),
        (0, "The shaded region is removed by the central stop; the remainder reaches the lens (numerical aperture 0.8, 750 nm)"),
    ], ["pupil_geo_a", "pupil_geo_b", "pupil_geo_c"], None),
    ("slide", "Focal field at each obstruction ratio", [
        (0, "Left to right: eps = 0, 0.5, 0.9, 0.99 (numerical aperture 0.8, uniform, continuous wave at 750 nm)"),
        (0, "The axial extent grows while the transverse lobe changes little; the side lobes rise with eps"),
    ], ["cmp_eps_0p0", "cmp_eps_0p5", "cmp_eps_0p9", "cmp_eps_0p99"], None),
    ("slide", "Transverse full width at half maximum against obstruction ratio", [
        (0, "The width decreases from 497 to 364 nm over 0 <= eps <= 0.99, while depth of focus increases by a factor of 44.3 (numerical aperture 0.8, uniform, 750 nm)"),
        (0, "The two illuminations converge as eps approaches unity, since only rays near the pupil edge are transmitted"),
    ], "ab_0p8_width", None),
    ("slide", "On-axis peak intensity against obstruction ratio", [
        (0, "Peak intensity relative to the unobstructed pupil: 0.563 at eps = 0.5 and 0.036 at eps = 0.9 (numerical aperture 0.8, uniform, 750 nm)"),
        (0, "The peak falls faster than the transmitted power, since the transmitted power is spread over a longer focus"),
    ], "ab_0p8_peak", None),
    ("slide", "Fraction of transmitted power in the central lobe", [
        (0, "The central lobe holds 0.84 of the transmitted power at eps = 0 and 0.10 at eps = 0.9 (numerical aperture 0.8, 750 nm)"),
        (0, "The remainder is in the side lobes; it is redistributed within the focal plane rather than removed"),
    ], "eb_core", None),
    ("slide", "Energy against radius, for each obstruction ratio", [
        (0, "Intensity weighted by the area element, so the height is energy per unit radius rather than brightness (numerical aperture 0.8, uniform, 750 nm)"),
        (0, "The central peak falls and the outer rings rise, at constant transmitted power"),
    ], "eb_land", None),
    ("slide", "Focal field at obstruction ratio 0.99", [
        (0, "The focus is no longer a single lobe (numerical aperture 0.8, uniform, 750 nm)"),
        (0, "An energy-fraction extent is measured alongside the width, which is no longer a fair description"),
    ], "ag_0p8_uni_0p99", None),

    ("slide", "Observations: the obstruction ratio", [
        (0, "At ratio 0.9 the annulus lets through 19% of the incident light; at 0.99, 2%"),
        (0, "The intensity at the focal point falls further still, to 3.6% and then to zero, because the light that does get through is spread over a longer focus"),
        (0, "The focal spot size barely responds, changing only from 497 to 364 nm over the full range, so nothing is gained in resolution"),
        (0, "On-axis peak intensity falls faster than the transmitted light, since the power that passes is redistributed over a longer focus and into the side lobes"),
        (0, "The central lobe holds 0.84 of the transmitted power at eps = 0 and 0.10 at eps = 0.9"),
        (0, "Past eps = 0.95 at high aperture the longitudinal field fills the first minimum, and the focus is no longer a single lobe"),
    ], None, None),

    ("section", "Varying the numerical aperture"),
    ("slide", "What is changed", [
        (0, "The cone half-angle at which the rays converge: 4.4 degrees at numerical aperture 0.1, 38.0 at 0.8, 67.4 at 1.2 (refractive index 1.3)"),
        (0, "The pupil pattern is unchanged; only the convergence angle differs"),
        (0, "At eps = 0.9 the transmitted rays span 0.4, 4.3 and 11.2 degrees respectively (continuous wave, 750 nm)"),
    ], "ak_cmp", "aperture"),
    ("slide", "Focal field at each numerical aperture", [
        (0, "Left to right: numerical aperture 0.1, 0.8, 1.2, all at obstruction ratio 0.9 (uniform, continuous wave at 750 nm)"),
        (0, "Depth of focus goes from 172.5 to 906.8 um at numerical aperture 0.1, from 2.42 to 11.51 um at 0.8, and from 0.86 to 2.98 um at 1.2"),
        (0, "The corresponding extensions are 5.26, 4.76 and 3.49; each map is drawn on its own scale, since the absolute size differs by more than two orders of magnitude across the three"),
    ], ["cmp_na_0p1", "cmp_na_0p8", "cmp_na_1p2"], None),
    ("slide", "Departure of the computed extension from the paraxial expression", [
        (0, "At eps = 0.9 the paraxial expression gives 5.26; the computed values are 5.26, 4.76 and 3.49 at numerical aperture 0.1, 0.8 and 1.2"),
        (0, "At eps = 0.99 it gives 50.25; the computed values are 50.18, 44.33 and 27.85"),
        (0, "With Gaussian illumination at numerical aperture 1.2 the extension falls below unity from eps = 0.3 onward: 0.97, 0.95, 1.05 at eps = 0.3, 0.5, 0.7 (continuous wave, 750 nm)"),
    ], "ab_1p2_gain", None),


    ("slide", "Observations: the numerical aperture", [
        (0, "The paraxial expression gives 5.26 at eps = 0.9 against a computed 3.49 at numerical aperture 1.2, an overstatement of a third"),
        (0, "The exact form follows from the axial phase, which varies as cos theta rather than quadratically, and reproduces the computed values to about 2% at every aperture examined"),
        (0, "Since this work is at high aperture throughout, the exact form is the one to use; the paraxial expression is retained only as the reference it is usually quoted as"),
        (0, "With Gaussian illumination at numerical aperture 1.2 the extension falls below unity from eps = 0.3, so the obstruction shortens the focus"),
    ], None, None),

    ("section", "Normalization of the comparison metrics"),
    ("slide", "What is changed", [
        (0, "The quantity held fixed when two profiles are differenced: the peak, or the transmitted power"),
        (0, "Peak normalization sets both maxima to one, which forces the profiles to agree at r = 0"),
        (0, "Energy normalization sets the transmitted power to one, leaving the peaks free to differ"),
    ], None, "normalization"),
    ("slide", "The two normalizations on the same profiles", [
        (0, "Vector against scalar Debye (numerical aperture 1.2, uniform, continuous wave at 750 nm)"),
        (0, "Under energy normalization the vector peak is 0.766 of the scalar peak; peak normalization removes that difference"),
    ], "mn_peak", None),
    ("slide", "What each normalization leaves for the metric to measure", [
        (0, "Vector minus scalar under each normalization (numerical aperture 1.2, uniform, continuous wave at 750 nm)"),
        (0, "Peak normalized, the difference vanishes at r = 0 and only the wings contribute"),
        (0, "Energy normalized, the difference is largest at the center"),
    ], "mn_energy", None),
    ("slide", "Numerical aperture at which each criterion is first met", [
        (0, "Both normalizations, with and without area weighting (uniform, continuous wave at 750 nm)"),
        (0, "Unweighted: numerical aperture 0.70 peak normalized, 0.50 energy normalized"),
        (0, "Weighted by area: 0.80 under either normalization"),
        (0, "Fractional change in width, 1% criterion: 0.45"),
        (0, "Width remains the discriminator; the error tracks it under none of the four"),
    ], "mn_curves", None),

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

        # A slide may name one figure or several. Several are placed in a row,
        # which keeps panels that belong together on the same slide without
        # forcing them into one image at export time.
        keys = [figkey] if isinstance(figkey, str) else list(figkey or [])
        paths = []
        for k in keys:
            rel, script = FIGURES[k]
            cand = os.path.join(OUT, rel)
            if os.path.exists(cand):
                paths.append(cand)
            else:
                missing.append(f"{rel}  ->  regenerate with: python {script}")
        path = paths[0] if len(paths) == 1 else None
        if len(paths) > 1:
            from PIL import Image
            row_top, row_h = 2.60, 4.30
            gap, left = 0.25, 0.55
            widths = []
            for q in paths:
                with Image.open(q) as im:
                    widths.append(im.width / im.height)
            total = sum(widths)
            avail = 12.20 - gap * (len(paths) - 1)
            scale = min(row_h, avail / total)
            x = left + (12.20 - (scale * total + gap * (len(paths) - 1))) / 2
            for q, ar in zip(paths, widths):
                w = scale * ar
                s.shapes.add_picture(q, Inches(x), Inches(row_top + (row_h - scale) / 2),
                                     width=Inches(w), height=Inches(scale))
                x += w + gap

        # A wide figure cannot sit beside the bullets without running off the
        # slide, so the aspect ratio decides the layout: tall-ish figures go to
        # the right of the text, wide ones go underneath it at full width.
        aspect = None
        if path:
            from PIL import Image
            with Image.open(path) as im:
                aspect = im.width / im.height
        # Text in a narrow column on the left, figure filling the right. A wide
        # figure is placed here too rather than stacked underneath, so every
        # slide reads the same way.
        # A sparse slide gets the narrow column and a large figure; a slide
        # with more text widens the column rather than overrunning it.
        _tw = 3.55
        for _try in (3.55, 4.4, 5.3, 6.2):
            if _text_height_in(bullets, _try - 0.25, 16) <= 5.30:
                _tw = _try
                break
            _tw = _try
        SIDE_BOX = (_tw + 0.80, 1.45, 12.85 - _tw - 0.80, 5.35)
        stacked = False          # text left, figure right, always
        # the bullets decide where a stacked figure can start
        stacked_text_h = _text_height_in(bullets, 12.20, 16) if stacked else 0.0
        fig_top = min(4.30, max(3.00, 1.55 + stacked_text_h + 0.20))
        BELOW_BOX = (0.55, fig_top, 12.20, 7.25 - fig_top)

        if path and not stacked:
            text_w, text_h = Inches(_tw), Inches(5.35)
        elif stacked:
            # the figure sits underneath, so the text may only use the band above it
            text_w, text_h = Inches(12.2), Inches(max(1.0, fig_top - 1.70))
        else:
            text_w, text_h = Inches(12.2), Inches(5.50)
        # an equation is dropped in below the text, so leave room for it — but a
        # stacked figure already occupies that band, so there the equation stays
        # in the notes only
        show_equation = bool(latexkey) and not path   # no room beside a figure
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
            left = bl + (bw - w) / 2                  # centerd in its box
            top = bt + (bh - h) / 2
            s.shapes.add_picture(path, Inches(left), Inches(top),
                                 width=Inches(w), height=Inches(h))
            if SHOW_FIGURE_PATH:
                # the source file, so a deck rebuilt in another tool can be
                # traced back to the figure it came from
                cap = s.shapes.add_textbox(Inches(left), Inches(top + h + 0.04),
                                           Inches(w), Inches(0.26))
                tf = cap.text_frame
                tf.word_wrap = True
                run = tf.paragraphs[0].add_run()
                run.text = os.path.relpath(path, OUT)
                run.font.size = Pt(9)
                run.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
                tf.paragraphs[0].alignment = PP_ALIGN.CENTER

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
                else:                         # full width, centerd under the text
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
