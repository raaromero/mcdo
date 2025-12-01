"""
Monte Carlo simulation using analytical angular spectrum sampling.

Instead of FFT discretization, samples directly from the analytical
jinc²(k_ρ × R) distribution for a circular aperture.
"""

import numpy as np
from typing import Optional, Tuple
from scipy.special import j1


class AngularSpectrumAnalytical:
    """
    Angular spectrum simulator using analytical jinc² sampling.

    For a uniform circular aperture of radius R, the angular spectrum is:
        A(k_ρ) = jinc(k_ρ × R) = 2·J₁(k_ρ·R) / (k_ρ·R)

    We sample k_ρ weighted by |A|² = jinc²(k_ρ × R), then map to focal plane
    using the Fraunhofer formula: x = (λf)/(2π) × kx

    Parameters
    ----------
    n_photons : int
        Number of photons to simulate
    wavelength : float
        Wavelength of light (in same units as other dimensions)
    focal_length : float
        Focal length (f) where image plane is located
    numerical_aperture : float
        Numerical aperture of the system
    n_medium : float
        Index of refraction of medium (default: 1.0 for air)
    random_seed : int, optional
        Seed for random number generator for reproducibility
    """

    def __init__(
        self,
        n_photons: int = 10000,
        wavelength: float = 0.532,  # microns
        focal_length: float = 10.0,  # mm
        numerical_aperture: float = 0.1,
        n_medium: float = 1.0,
        random_seed: Optional[int] = None,
    ):
        """Initialize the analytical angular spectrum simulator."""
        self.n_photons = n_photons
        self.wavelength = wavelength
        self.focal_length = focal_length
        self.numerical_aperture = numerical_aperture
        self.n_medium = n_medium
        self.random_seed = random_seed

        if random_seed is not None:
            np.random.seed(random_seed)

        # Wave number: k = 2π n / λ
        self.k = 2 * np.pi * n_medium / wavelength

        # Maximum transverse wave vector from NA
        sin_theta_max = numerical_aperture / n_medium
        self.k_max = self.k * sin_theta_max

        # Calculate aperture radius from NA and focal length
        self.aperture_radius = (numerical_aperture * focal_length) / n_medium

    def jinc_squared(self, k_rho: np.ndarray) -> np.ndarray:
        """
        Compute jinc²(k_ρ × R) function.

        jinc(x) = 2·J₁(x) / x

        Parameters
        ----------
        k_rho : np.ndarray
            Radial wave vector magnitude

        Returns
        -------
        np.ndarray
            jinc²(k_ρ × R) values
        """
        x = k_rho * self.aperture_radius

        jinc = np.ones_like(x)
        nonzero = x != 0
        jinc[nonzero] = 2 * j1(x[nonzero]) / x[nonzero]

        return jinc**2

    def sample_k_rho_rejection(self, n_samples: int) -> np.ndarray:
        """
        Sample k_ρ from k_ρ × jinc²(k_ρ × R) using rejection sampling.

        The Jacobian for polar coordinates means we sample from:
            P(k_ρ) ∝ k_ρ × jinc²(k_ρ × R)
        not just jinc²(k_ρ × R)!

        Parameters
        ----------
        n_samples : int
            Number of samples needed

        Returns
        -------
        np.ndarray
            Sampled k_ρ values
        """
        samples = []

        # Find maximum of k_ρ × jinc²(k_ρ × R)
        # This occurs near k_ρ ≈ 1.6/R_aperture
        k_test = np.linspace(0, self.k_max, 1000)
        target_dist = k_test * self.jinc_squared(k_test)
        max_value = np.max(target_dist)

        while len(samples) < n_samples:
            # Sample candidate k_rho uniformly from [0, k_max]
            k_rho_candidates = self.k_max * np.random.random(n_samples * 2)

            # Evaluate k_ρ × jinc²(k_ρ × R)
            target_values = k_rho_candidates * self.jinc_squared(k_rho_candidates)

            # Rejection sampling
            accept_prob = np.random.random(len(k_rho_candidates))
            accepted = k_rho_candidates[accept_prob < target_values / max_value]

            samples.extend(accepted)

        return np.array(samples[:n_samples])

    def sample_angular_spectrum(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Sample (kx, ky) UNIFORMLY within NA cone.

        For lens focusing, the k-distribution is UNIFORM within k_max,
        NOT weighted by jinc²! The jinc² is the RESULT at focal plane.

        Returns
        -------
        tuple of np.ndarray
            (kx, ky) wave vector components
        """
        # Sample UNIFORMLY in circle of radius k_max
        k_rho = self.k_max * np.sqrt(np.random.random(self.n_photons))
        theta = np.random.uniform(0, 2 * np.pi, self.n_photons)

        # Convert to Cartesian
        kx = k_rho * np.cos(theta)
        ky = k_rho * np.sin(theta)

        return kx, ky

    def kspace_to_direction(
        self,
        kx: np.ndarray,
        ky: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Convert wave vector components to normalized direction vectors.

        Parameters
        ----------
        kx, ky : np.ndarray
            x and y components of wave vector

        Returns
        -------
        tuple of np.ndarray
            (dx, dy, dz) normalized direction vectors
        """
        # kz from dispersion relation: k² = kx² + ky² + kz²
        kz_squared = self.k**2 - kx**2 - ky**2

        if np.any(kz_squared < 0):
            raise ValueError("Evanescent waves detected (kz² < 0)")

        kz = np.sqrt(kz_squared)

        # Normalize to unit direction
        dx = kx / self.k
        dy = ky / self.k
        dz = kz / self.k

        return dx, dy, dz

    def propagate(self) -> dict:
        """
        Propagate photons from aperture to focal plane.

        Uses analytical jinc² sampling (no FFT discretization) and
        Fraunhofer diffraction formula for k-space to real-space mapping.

        Returns
        -------
        dict
            Dictionary containing:
            - 'aperture_positions': (x, y, z) at aperture (all at origin)
            - 'focal_positions': (x, y, z) at focal plane
            - 'directions': (dx, dy, dz) normalized direction vectors
            - 'k_vectors': (kx, ky, kz) angular spectrum components
        """
        # All photons start at aperture center
        x_ap = np.zeros(self.n_photons)
        y_ap = np.zeros(self.n_photons)
        z_ap = np.zeros(self.n_photons)

        # Sample from analytical jinc² distribution
        kx, ky = self.sample_angular_spectrum()

        # Convert to direction vectors
        dx, dy, dz = self.kspace_to_direction(kx, ky)

        # Calculate kz for output
        kz = np.sqrt(self.k**2 - kx**2 - ky**2)

        # Fraunhofer diffraction formula
        scale_factor = (self.wavelength * self.focal_length) / (2 * np.pi)
        x_focal = scale_factor * kx
        y_focal = scale_factor * ky
        z_focal = np.full(self.n_photons, self.focal_length)

        return {
            'aperture_positions': (x_ap, y_ap, z_ap),
            'focal_positions': (x_focal, y_focal, z_focal),
            'directions': (dx, dy, dz),
            'k_vectors': (kx, ky, kz)
        }
