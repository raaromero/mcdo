"""
Richards-Wolf vector diffraction theory for high-NA focusing.

Computes the intensity distribution near the focus of a high numerical
aperture objective using vectorial diffraction theory.
"""

import numpy as np
from typing import Tuple
from scipy.special import jv
from scipy import integrate


class RichardsWolfSimulator:
    """
    Richards-Wolf vector diffraction simulator.

    Calculates intensity patterns near the focus using Richards-Wolf
    vectorial diffraction integrals. Useful for high-NA systems where
    scalar diffraction (Airy pattern) is insufficient.

    Parameters
    ----------
    wavelength : float
        Wavelength in microns
    numerical_aperture : float
        Numerical aperture of the objective
    n_medium : float
        Refractive index of the medium (default: 1.0 for air)
    polarization : str
        'x', 'y', or 'circular' (default: 'x')
    """

    def __init__(
        self,
        wavelength: float = 0.532,
        numerical_aperture: float = 0.9,
        n_medium: float = 1.0,
        polarization: str = 'x'
    ):
        self.wavelength = wavelength
        self.numerical_aperture = numerical_aperture
        self.n_medium = n_medium
        self.polarization = polarization

        # Wave number k = 2π/λ
        self.k = 2 * np.pi / wavelength

        # Angular aperture: sin(α) = NA/n
        self.angular_aperture = np.arcsin(numerical_aperture / n_medium)
        self.sin_alpha = np.sin(self.angular_aperture)
        self.sin2_alpha = self.sin_alpha ** 2

        # Airy radius for reference
        self.airy_radius = 0.61 * wavelength / numerical_aperture

    def _compute_integrals(
        self,
        u: float,
        v: float
    ) -> Tuple[complex, complex, complex]:
        """
        Compute Richards-Wolf integrals I₀, I₁, I₂ for a single point.

        Parameters
        ----------
        u : float
            Axial optical coordinate: u = k sin²(α) z
        v : float
            Radial optical coordinate: v = k sin(α) r

        Returns
        -------
        I0, I1, I2 : complex
            The three fundamental integrals
        """
        def I0_integrand(theta):
            if abs(np.sin(theta)) < 1e-15:
                return 0.0 + 0.0j
            cos_t = np.cos(theta)
            sin_t = np.sin(theta)
            apod = np.sqrt(cos_t)
            geo = sin_t * (1 + cos_t)
            bessel = jv(0, v * sin_t / self.sin_alpha)
            phase = np.exp(1j * u * cos_t / self.sin2_alpha)
            return apod * geo * bessel * phase

        def I1_integrand(theta):
            if abs(np.sin(theta)) < 1e-15:
                return 0.0 + 0.0j
            cos_t = np.cos(theta)
            sin_t = np.sin(theta)
            apod = np.sqrt(cos_t)
            geo = sin_t ** 2
            bessel = jv(1, v * sin_t / self.sin_alpha)
            phase = np.exp(1j * u * cos_t / self.sin2_alpha)
            return apod * geo * bessel * phase

        def I2_integrand(theta):
            if abs(np.sin(theta)) < 1e-15:
                return 0.0 + 0.0j
            cos_t = np.cos(theta)
            sin_t = np.sin(theta)
            apod = np.sqrt(cos_t)
            geo = sin_t * (1 - cos_t)
            bessel = jv(2, v * sin_t / self.sin_alpha)
            phase = np.exp(1j * u * cos_t / self.sin2_alpha)
            return apod * geo * bessel * phase

        # Integrate
        I0, _ = integrate.quad(I0_integrand, 0, self.angular_aperture,
                               complex_func=True, limit=100)
        I1, _ = integrate.quad(I1_integrand, 0, self.angular_aperture,
                               complex_func=True, limit=100)
        I2, _ = integrate.quad(I2_integrand, 0, self.angular_aperture,
                               complex_func=True, limit=100)

        return I0, I1, I2

    def compute_field(
        self,
        r: np.ndarray,
        z: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Compute electric field components Ex, Ey, Ez.

        Parameters
        ----------
        r : np.ndarray
            Radial coordinates in microns (distance from optical axis)
        z : np.ndarray
            Axial coordinates in microns (z=0 at focus)

        Returns
        -------
        Ex, Ey, Ez : np.ndarray (complex)
            Electric field components
        """
        # Convert to optical coordinates
        u = self.k * self.sin2_alpha * z
        v = self.k * self.sin_alpha * np.abs(r)

        # Flatten for computation
        u_flat = np.atleast_1d(u).flatten()
        v_flat = np.atleast_1d(v).flatten()

        Ex_flat = np.zeros_like(u_flat, dtype=complex)
        Ey_flat = np.zeros_like(u_flat, dtype=complex)
        Ez_flat = np.zeros_like(u_flat, dtype=complex)

        # Compute for each point
        for i, (u_val, v_val) in enumerate(zip(u_flat, v_flat)):
            I0, I1, I2 = self._compute_integrals(u_val, v_val)

            if self.polarization == 'x':
                Ex_flat[i] = -1j * (I0 - I2)
                Ey_flat[i] = 0
                Ez_flat[i] = -2 * I1
            elif self.polarization == 'y':
                Ex_flat[i] = 0
                Ey_flat[i] = -1j * (I0 + I2)
                Ez_flat[i] = 0
            else:  # circular
                Ex_flat[i] = -1j * (I0 - I2) / np.sqrt(2)
                Ey_flat[i] = -1j * (I0 + I2) / np.sqrt(2)
                Ez_flat[i] = -2 * I1 / np.sqrt(2)

        # Reshape to match input
        Ex = Ex_flat.reshape(np.atleast_1d(u).shape)
        Ey = Ey_flat.reshape(np.atleast_1d(u).shape)
        Ez = Ez_flat.reshape(np.atleast_1d(u).shape)

        return Ex, Ey, Ez

    def focal_plane_intensity_pattern(
        self,
        x_focal: np.ndarray,
        y_focal: np.ndarray
    ) -> np.ndarray:
        """
        Calculate intensity pattern at focal plane (z=0).

        Compatible with ApertureSimulator.focal_plane_intensity_pattern interface.

        Parameters
        ----------
        x_focal : np.ndarray
            x coordinates at focal plane in microns
        y_focal : np.ndarray
            y coordinates at focal plane in microns

        Returns
        -------
        intensity : np.ndarray
            Total intensity |Ex|² + |Ey|² + |Ez|²
        """
        r = np.sqrt(x_focal**2 + y_focal**2)
        z = np.zeros_like(r)

        Ex, Ey, Ez = self.compute_field(r, z)
        intensity = np.abs(Ex)**2 + np.abs(Ey)**2 + np.abs(Ez)**2

        # Normalize to peak intensity
        intensity = intensity / np.max(intensity)

        return intensity
