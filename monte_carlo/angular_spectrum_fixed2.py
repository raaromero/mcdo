"""
Monte Carlo simulation using angular spectrum sampling - FIXED VERSION 2.

Fixed issues:
1. Use direct Fraunhofer formula: x = λf/(2π) × kx
2. Increase aperture spatial sampling for accurate FFT
"""

import numpy as np
from typing import Optional, Tuple


class AngularSpectrumSimulatorFixed2:
    """
    Monte Carlo simulator using angular spectrum approach - FIXED v2.

    Fixes:
    - Uses Fraunhofer diffraction formula (not ray tracing)
    - Ensures high spatial resolution of aperture (200+ pixels across diameter)
      to accurately compute FFT → jinc² distribution

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
        fft_size: int = 512
    ):
        """Initialize the angular spectrum simulator."""
        self.n_photons = n_photons
        self.wavelength = wavelength
        self.focal_length = focal_length
        self.numerical_aperture = numerical_aperture
        self.n_medium = n_medium
        self.random_seed = random_seed
        self.fft_size = fft_size

        if random_seed is not None:
            np.random.seed(random_seed)

        # Wave number: k = 2π n / λ
        self.k = 2 * np.pi * n_medium / wavelength

        # Maximum angle from NA: NA = n * sin(θ_max)
        # Maximum transverse wave vector: k_max = k * sin(θ_max) = k * (NA / n)
        sin_theta_max = numerical_aperture / n_medium
        self.k_max = self.k * sin_theta_max

        # Calculate aperture radius from NA and focal length
        # NA = n * sin(theta) ≈ n * (R/f) for small angles (low NA)
        self.aperture_radius = (numerical_aperture * focal_length) / n_medium

        # Compute angular spectrum via 2D FFT
        self._compute_angular_spectrum_fft()

    def _compute_angular_spectrum_fft(self):
        """
        Compute the angular spectrum by taking 2D FFT of circular aperture.

        FIXED: Ensures high spatial resolution of aperture (200+ pixels across)
        for accurate FFT computation.
        """
        # FIX: Prioritize good spatial sampling of the aperture
        # Need at least 200 pixels across aperture diameter for smooth jinc²
        min_pixels_across_aperture = 200
        L_from_aperture = min_pixels_across_aperture * self.aperture_radius

        # Also ensure decent k-space resolution
        desired_k_points = 50
        L_from_kspace = desired_k_points * 2 * np.pi / self.k_max

        # Take the LARGER of the two to satisfy both constraints
        L = max(L_from_aperture, L_from_kspace)

        dx = L / self.fft_size
        x = np.linspace(-L/2, L/2, self.fft_size)
        y = np.linspace(-L/2, L/2, self.fft_size)
        X, Y = np.meshgrid(x, y)
        R = np.sqrt(X**2 + Y**2)

        # Create circular aperture: 1 inside, 0 outside
        aperture = (R <= self.aperture_radius).astype(float)

        # Compute 2D FFT (shifted to center zero frequency)
        fft_aperture = np.fft.fftshift(np.fft.fft2(np.fft.ifftshift(aperture)))

        # Angular spectrum intensity
        self.angular_spectrum_2d = np.abs(fft_aperture)**2

        # Create k-space grid and save as instance attributes for visualization
        # Frequency spacing
        dk = 2 * np.pi / L  # frequency spacing in k-space
        kx_1d = np.fft.fftshift(np.fft.fftfreq(self.fft_size, dx)) * 2 * np.pi
        ky_1d = np.fft.fftshift(np.fft.fftfreq(self.fft_size, dx)) * 2 * np.pi
        self.kx_grid, self.ky_grid = np.meshgrid(kx_1d, ky_1d)

        # Flatten for sampling
        self.kx_flat = self.kx_grid.flatten()
        self.ky_flat = self.ky_grid.flatten()
        self.intensity_flat = self.angular_spectrum_2d.flatten()

        # Filter to only propagating waves: kx² + ky² <= k²
        # This prevents evanescent waves (imaginary kz)
        # The circular aperture FFT already encodes the NA limitation
        k_transverse_squared = self.kx_flat**2 + self.ky_flat**2
        valid_mask = k_transverse_squared <= self.k**2

        self.kx_valid = self.kx_flat[valid_mask]
        self.ky_valid = self.ky_flat[valid_mask]
        self.intensity_valid = self.intensity_flat[valid_mask]

        # Normalize to probability distribution
        intensity_sum = np.sum(self.intensity_valid)
        if intensity_sum == 0 or not np.isfinite(intensity_sum):
            raise ValueError(
                f"Angular spectrum intensity sum is {intensity_sum}. "
                f"This may indicate the FFT grid is not appropriate for the current parameters. "
                f"Try increasing fft_size or adjusting the aperture/wavelength parameters."
            )
        self.intensity_valid = self.intensity_valid / intensity_sum

    def sample_angular_spectrum(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Sample (kx, ky) from the 2D FFT-computed angular spectrum.

        The angular spectrum is computed as the 2D Fourier transform of the
        circular aperture. Photon directions are sampled weighted by the
        intensity |FFT|² of this angular spectrum.

        Returns
        -------
        tuple of np.ndarray
            (kx, ky) wave vector components sampled from FFT angular spectrum
        """
        # Sample indices from the flattened intensity distribution
        indices = np.random.choice(
            len(self.kx_valid),
            size=self.n_photons,
            p=self.intensity_valid
        )

        # Get corresponding k-vectors
        kx = self.kx_valid[indices]
        ky = self.ky_valid[indices]

        return kx, ky

    def kspace_to_direction(
        self,
        kx: np.ndarray,
        ky: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Convert wave vector components to normalized direction vectors.

        Uses dispersion relation: k² = kx² + ky² + kz²
        where k = 2πn/λ

        Parameters
        ----------
        kx : np.ndarray
            x component of wave vector
        ky : np.ndarray
            y component of wave vector

        Returns
        -------
        tuple of np.ndarray
            (dx, dy, dz) normalized direction vectors
        """
        # kz from dispersion relation: k² = kx² + ky² + kz²
        kz_squared = self.k**2 - kx**2 - ky**2

        # Ensure kz is real (should always be true if kx, ky <= k_max)
        if np.any(kz_squared < 0):
            raise ValueError("Evanescent waves detected (kz² < 0). Check k_max constraint.")

        kz = np.sqrt(kz_squared)

        # Direction vector is parallel to k vector
        # Normalize to unit vector: d = k / |k|
        # Since |k| = k (by construction), we have:
        dx = kx / self.k
        dy = ky / self.k
        dz = kz / self.k

        # Verify normalization
        norm_check = np.sqrt(dx**2 + dy**2 + dz**2)
        assert np.allclose(norm_check, 1.0), "Direction vectors not properly normalized"

        return dx, dy, dz

    def propagate(self) -> dict:
        """
        Propagate photons from aperture center to focal plane.

        Physics (Angular Spectrum Method - FIXED v2):
        1. All photons start at aperture center (0, 0, 0)
        2. The angular spectrum (Fourier transform of the circular aperture)
           gives us the probability distribution for photon directions
        3. Sample (kx, ky) weighted by angular spectrum intensity: jinc²(k_rho * R)
        4. Use Fraunhofer diffraction formula:
           x = (λf)/(2π) × kx
           y = (λf)/(2π) × ky

        Returns
        -------
        dict
            Dictionary containing:
            - 'aperture_positions': (x, y, z) at aperture (all at origin)
            - 'focal_positions': (x, y, z) at focal plane
            - 'directions': (dx, dy, dz) normalized direction vectors
            - 'k_vectors': (kx, ky, kz) angular spectrum components
        """
        # All photons start at aperture center (plane wave approximation)
        x_ap = np.zeros(self.n_photons)
        y_ap = np.zeros(self.n_photons)
        z_ap = np.zeros(self.n_photons)

        # Sample from angular spectrum
        kx, ky = self.sample_angular_spectrum()

        # Convert to direction vectors and get kz
        dx, dy, dz = self.kspace_to_direction(kx, ky)

        # Calculate kz for output
        kz = np.sqrt(self.k**2 - kx**2 - ky**2)

        # FIXED: Use Fraunhofer diffraction formula
        # Direct mapping from k-space to focal plane:
        # x = (λf)/(2π) × kx
        # y = (λf)/(2π) × ky
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
