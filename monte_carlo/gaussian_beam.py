"""
Monte Carlo simulation of a focused Gaussian beam.

This module implements Gaussian beam propagation for Monte Carlo simulations,
adapted from gbp-mc repository. Focuses on propagation without scattering.
"""

import numpy as np
from typing import Optional, Tuple, Dict


class GaussianBeamSimulator:
    """
    Monte Carlo simulator for focused Gaussian beam propagation.

    This class simulates photon propagation through a focused Gaussian beam,
    sampling from a Gaussian intensity distribution at the lens plane.

    Parameters
    ----------
    n_photons : int
        Number of photons to simulate
    wavelength : float
        Wavelength of light in microns
    numerical_aperture : float
        Numerical aperture of the system
    focal_length : float
        Focal length in microns
    n_medium : float
        Index of refraction of medium (default: 1.0 for air)
    z_focus : float
        Z-coordinate of the focal point (default: 0)
    truncation_coeff : float
        Truncation coefficient for the beam (>4 means untruncated, default: 4)
    random_seed : Optional[int]
        Seed for random number generator
    """

    def __init__(
        self,
        n_photons: int = 10000,
        wavelength: float = 0.532,  # microns
        numerical_aperture: float = 0.1,
        focal_length: float = 10000.0,  # microns (10mm)
        n_medium: float = 1.0,
        z_focus: float = 0.0,
        truncation_coeff: float = 4.0,
        random_seed: Optional[int] = None
    ):
        """Initialize the Gaussian beam simulator."""
        self.n_photons = n_photons
        self.wavelength = wavelength
        self.NA = numerical_aperture
        self.n = n_medium
        self.f = focal_length
        self.z_f = z_focus
        self.z_lens = z_focus - focal_length
        self.trunc_coeff = truncation_coeff
        self.random_seed = random_seed

        if random_seed is not None:
            np.random.seed(random_seed)

        # Calculate aperture radius from NA and focal length
        theta = np.arcsin(self.NA / self.n)
        self.aperture_radius = self.f * np.tan(theta)
        self.aperture = 2 * self.aperture_radius

        # Wave number
        self.k = 2 * np.pi / self.wavelength

        # Beam waist at focus (for Gaussian beam through aperture)
        if trunc_coeff >= 4:
            # Untruncated beam
            self.w_incident = (self.aperture / 2) / np.sqrt(trunc_coeff)
            Nw = self.w_incident**2 / (self.wavelength * self.f)
            self.w0 = self.w_incident / np.sqrt(1 + (np.pi * Nw)**2)
        else:
            # Truncated beam
            self.w0 = (2 / np.pi) * (self.wavelength * self.f / self.aperture)

        # Rayleigh range
        self.z_R = np.pi * self.w0**2 / self.wavelength
        self.focal_tolerance = 2 * self.z_R

    def beam_radius(self, z: np.ndarray) -> np.ndarray:
        """
        Calculate beam radius at position z.

        Parameters
        ----------
        z : np.ndarray
            Axial position(s)

        Returns
        -------
        np.ndarray
            Beam radius at each position
        """
        return self.w0 * np.sqrt(1 + ((z - self.z_f) / self.z_R)**2)

    def init_collimated_gaussian(self) -> np.ndarray:
        """
        Initialize photon positions at the lens with Gaussian distribution.

        Returns
        -------
        np.ndarray
            Array of shape (3, n_photons) with (x, y, z) coordinates at lens
        """
        # Standard deviation at lens for Gaussian distribution
        # D4σ beam width: w = 2*radius = 4*stdev, so stdev = radius/2
        stdev_at_lens = self.beam_radius(self.z_lens) / 2

        # Initialize position array
        r_coll = np.zeros((3, self.n_photons))

        # Sample from Gaussian distribution
        r_coll[0] = np.random.normal(scale=stdev_at_lens, size=self.n_photons)
        r_coll[1] = np.random.normal(scale=stdev_at_lens, size=self.n_photons)
        r_coll[2] = np.full(self.n_photons, self.z_lens)

        # Apply aperture constraint - reject photons outside aperture
        rLens_squared = r_coll[0]**2 + r_coll[1]**2
        blocked = rLens_squared > self.aperture_radius**2
        n_blocked = np.sum(blocked)

        # Regenerate blocked photons until they pass through aperture
        while n_blocked > 0:
            x_new = np.random.normal(scale=stdev_at_lens, size=n_blocked)
            y_new = np.random.normal(scale=stdev_at_lens, size=n_blocked)
            r_new_squared = x_new**2 + y_new**2

            # Only update photons that now pass through aperture
            passed = r_new_squared <= self.aperture_radius**2

            # Find indices of blocked photons
            blocked_indices = np.where(blocked)[0]
            passed_indices = blocked_indices[passed]

            # Update positions
            r_coll[0, passed_indices] = x_new[passed]
            r_coll[1, passed_indices] = y_new[passed]

            # Update blocked mask
            blocked[passed_indices] = False
            n_blocked = np.sum(blocked)

        return r_coll

    def focus_rays(self, r_coll: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate ray directions to focus at focal point.

        Parameters
        ----------
        r_coll : np.ndarray
            Array of shape (3, n_photons) with positions at lens

        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            - focal_target: (x, y) coordinates where each ray should focus
            - directions: normalized direction vectors (3, n_photons)
        """
        # Sample target positions at focal plane from Gaussian distribution
        stdev_at_focus = self.w0 / 2  # w0 is radius at focus

        focal_x = np.random.normal(scale=stdev_at_focus, size=self.n_photons)
        focal_y = np.random.normal(scale=stdev_at_focus, size=self.n_photons)

        # Calculate direction vectors from lens to focal point
        mu = np.zeros((3, self.n_photons))
        mu[0] = focal_x - r_coll[0]
        mu[1] = focal_y - r_coll[1]
        mu[2] = self.z_f - r_coll[2]

        # Normalize direction vectors
        norm = np.sqrt(mu[0]**2 + mu[1]**2 + mu[2]**2)
        mu[0] /= norm
        mu[1] /= norm
        mu[2] /= norm

        return (focal_x, focal_y), mu

    def propagate_to_plane(
        self,
        r_start: np.ndarray,
        directions: np.ndarray,
        z_target: float
    ) -> np.ndarray:
        """
        Propagate rays to a target z-plane.

        Parameters
        ----------
        r_start : np.ndarray
            Starting positions (3, n_photons)
        directions : np.ndarray
            Normalized direction vectors (3, n_photons)
        z_target : float
            Target z-coordinate

        Returns
        -------
        np.ndarray
            Positions at target plane (3, n_photons)
        """
        # Calculate propagation distance along ray
        # z_start + t * dz = z_target
        # t = (z_target - z_start) / dz
        t = (z_target - r_start[2]) / directions[2]

        # Calculate final positions
        r_final = np.zeros((3, self.n_photons))
        r_final[0] = r_start[0] + t * directions[0]
        r_final[1] = r_start[1] + t * directions[1]
        r_final[2] = z_target

        return r_final

    def simulate(self, z_target: Optional[float] = None) -> Dict:
        """
        Run full simulation: initialize photons and propagate to target plane.

        Parameters
        ----------
        z_target : Optional[float]
            Target z-plane for final positions. If None, uses focal plane.

        Returns
        -------
        Dict
            Dictionary containing:
            - 'lens_positions': positions at lens (3, n_photons)
            - 'focal_targets': target positions at focal plane (2, n_photons)
            - 'directions': normalized direction vectors (3, n_photons)
            - 'final_positions': positions at target plane (3, n_photons)
        """
        if z_target is None:
            z_target = self.z_f

        # Initialize photons at lens with Gaussian distribution
        lens_positions = self.init_collimated_gaussian()

        # Calculate focusing directions
        focal_targets, directions = self.focus_rays(lens_positions)

        # Propagate to target plane
        final_positions = self.propagate_to_plane(lens_positions, directions, z_target)

        return {
            'lens_positions': lens_positions,
            'focal_targets': np.array(focal_targets),
            'directions': directions,
            'final_positions': final_positions
        }
