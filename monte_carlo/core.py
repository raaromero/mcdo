"""
Core Monte Carlo simulation for optical propagation without scattering.
"""

import numpy as np
from typing import Optional, Tuple


class ApertureSimulator:
    """
    Monte Carlo simulator for photon propagation from aperture to focal plane.

    Simulates photons sampled from an aperture (x, y, z) that propagate to
    a focal plane. Direction is determined by the expected intensity pattern
    at the focal plane (assuming low NA).

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
        random_seed: Optional[int] = None
    ):
        """Initialize the aperture simulator."""
        self.n_photons = n_photons
        self.wavelength = wavelength
        self.focal_length = focal_length
        self.numerical_aperture = numerical_aperture
        self.n_medium = n_medium
        self.random_seed = random_seed

        if random_seed is not None:
            np.random.seed(random_seed)

        # Calculate aperture radius from NA and focal length
        # NA = n * sin(theta) ≈ n * (R/f) for small angles (low NA)
        self.aperture_radius = (numerical_aperture * focal_length) / n_medium

    def sample_aperture(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Sample photon starting positions from aperture.

        Returns
        -------
        tuple of np.ndarray
            (x, y, z) coordinates of photons at aperture
            Assumes aperture is at z=0
        """
        # Uniform sampling over circular aperture
        # Use sqrt for uniform distribution in area
        r = self.aperture_radius * np.sqrt(np.random.random(self.n_photons))
        theta = 2 * np.pi * np.random.random(self.n_photons)

        x_aperture = r * np.cos(theta)
        y_aperture = r * np.sin(theta)
        z_aperture = np.zeros(self.n_photons)

        return x_aperture, y_aperture, z_aperture

    def focal_plane_intensity_pattern(
        self,
        x_focal: np.ndarray,
        y_focal: np.ndarray
    ) -> np.ndarray:
        """
        Calculate expected intensity pattern at focal plane (low NA approximation).

        For low NA, the Airy pattern intensity is:
        I(r) = I0 * (2*J1(kr)/(kr))^2
        where k = 2*pi*NA/wavelength and r = sqrt(x^2 + y^2)

        Parameters
        ----------
        x_focal : np.ndarray
            x coordinates at focal plane
        y_focal : np.ndarray
            y coordinates at focal plane

        Returns
        -------
        np.ndarray
            Normalized intensity at each point
        """
        r = np.sqrt(x_focal**2 + y_focal**2)

        # Airy disk parameter
        k = 2 * np.pi * self.numerical_aperture / self.wavelength

        # Handle r=0 case
        kr = k * r
        intensity = np.ones_like(kr)

        # For kr != 0, use Airy pattern
        nonzero = kr != 0
        if np.any(nonzero):
            from scipy.special import j1
            intensity[nonzero] = (2 * j1(kr[nonzero]) / kr[nonzero])**2

        return intensity

    def sample_focal_plane_position(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Sample photon positions at focal plane based on intensity pattern.

        Returns
        -------
        tuple of np.ndarray
            (x, y) coordinates at focal plane (z = focal_length)
        """
        # For now, use rejection sampling
        # Sample from a region larger than the main Airy disk
        # First Airy zero at r = 1.22 * wavelength / NA
        sampling_radius = 5 * 1.22 * self.wavelength / self.numerical_aperture

        accepted_x = []
        accepted_y = []

        while len(accepted_x) < self.n_photons:
            # Generate candidate points
            n_candidates = self.n_photons * 2
            r_candidate = sampling_radius * np.sqrt(np.random.random(n_candidates))
            theta_candidate = 2 * np.pi * np.random.random(n_candidates)

            x_candidate = r_candidate * np.cos(theta_candidate)
            y_candidate = r_candidate * np.sin(theta_candidate)

            # Calculate intensity at these points
            intensity = self.focal_plane_intensity_pattern(x_candidate, y_candidate)

            # Rejection sampling
            accept_prob = np.random.random(n_candidates)
            accepted_mask = accept_prob < intensity

            accepted_x.extend(x_candidate[accepted_mask])
            accepted_y.extend(y_candidate[accepted_mask])

        # Return exactly n_photons
        x_focal = np.array(accepted_x[:self.n_photons])
        y_focal = np.array(accepted_y[:self.n_photons])

        return x_focal, y_focal

    def propagate(self) -> dict:
        """
        Propagate photons from aperture to focal plane.

        Returns
        -------
        dict
            Dictionary containing:
            - 'aperture_positions': (x, y, z) at aperture
            - 'focal_positions': (x, y, z) at focal plane
            - 'directions': (dx, dy, dz) normalized direction vectors
        """
        # Sample starting positions at aperture
        x_ap, y_ap, z_ap = self.sample_aperture()

        # Sample ending positions at focal plane
        x_focal, y_focal = self.sample_focal_plane_position()
        z_focal = np.full(self.n_photons, self.focal_length)

        # Calculate direction vectors
        dx = x_focal - x_ap
        dy = y_focal - y_ap
        dz = z_focal - z_ap

        # Normalize
        norm = np.sqrt(dx**2 + dy**2 + dz**2)
        dx /= norm
        dy /= norm
        dz /= norm

        return {
            'aperture_positions': (x_ap, y_ap, z_ap),
            'focal_positions': (x_focal, y_focal, z_focal),
            'directions': (dx, dy, dz)
        }
