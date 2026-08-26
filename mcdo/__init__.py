"""
mcdo — vector-diffraction + pulsed + structured-pupil focal-field toolkit.

Built bottom-up and validated phase by phase (see docs/theory): Richards-Wolf
vector focusing, Gaussian apodization, scalar-Debye/Airy limits, annular
apertures (Babinet), axicon/Bessel beams, and pulsed spectral integration.
Designed so the same pupil/illumination objects become the Monte-Carlo photon
launchers in the scattering phase.

Modules
-------
config        : SimConfig dataclass (all tunable parameters + spectral grid)
rw_integrals  : vectorized Richards-Wolf integrals I₀, I₁, I₂ (optional A(θ))
intensity     : CW and pulsed (Eq. 10) intensity on (r, z) grids
apodization   : pupil illumination A(θ) — uniform, gaussian, gaussian_ring, axicon
debye         : scalar Debye integral + paraxial Airy / sinc² analytics
annular       : annular apertures via field-level Babinet
polarization  : focal intensity for linear-x cuts and circular input
linfoot       : Fidelity F, Structural Content S, Correlation Quality Q
"""

from .config import SimConfig
from .rw_integrals import compute_integrals, integrals_to_intensity
from .intensity import cw_intensity, pulsed_intensity, transverse_profile, axial_profile
from .linfoot import fidelity, structural_content, correlation_quality, linfoot_profile
from . import apodization, debye, annular, polarization

__all__ = [
    "SimConfig",
    "compute_integrals",
    "integrals_to_intensity",
    "cw_intensity",
    "pulsed_intensity",
    "transverse_profile",
    "axial_profile",
    "fidelity",
    "structural_content",
    "correlation_quality",
    "linfoot_profile",
    "apodization",
    "debye",
    "annular",
    "polarization",
]
