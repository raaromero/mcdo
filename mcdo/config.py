"""Simulation parameters for Romallosa 2003 replication."""
from dataclasses import dataclass
import numpy as np

C_UM = 2.99792458e14  # speed of light (μm/s)


@dataclass
class SimConfig:
    """All physical and numerical parameters for one simulation run.

    Romallosa 2003 paper parameters:
        lam_c=0.750, X_NA=0.8, n=1.3, tau=1e-15
    """
    lam_c: float = 0.750   # center wavelength (μm)
    X_NA: float = 0.8      # numerical aperture: X_NA = n·sinα
    n: float = 1.3         # refractive index of image-side medium
    tau: float = 1e-15     # pulse FWHM (s); use np.inf for CW
    N_freq: int = 201      # spectral samples for pulsed integration
    N_theta: int = 501     # θ quadrature points (must be ODD)

    # --- derived optical quantities ---

    @property
    def sin_alpha(self) -> float:
        return self.X_NA / self.n

    @property
    def alpha(self) -> float:
        return np.arcsin(self.sin_alpha)

    @property
    def sin2_alpha(self) -> float:
        return self.sin_alpha ** 2

    @property
    def k_c(self) -> float:
        """Central wave number k_c = n·2π/λ_c  (μm⁻¹)."""
        return 2 * np.pi * self.n / self.lam_c

    @property
    def omega_c(self) -> float:
        """Central angular frequency ω_c = 2πc/λ_c  (rad/s)."""
        return 2 * np.pi * C_UM / self.lam_c

    # --- spectral bandwidth ---

    @property
    def spectral_bandwidth(self) -> float:
        """FWHM bandwidth of |E(ω)|²: Ω = 4·ln2/τ  (rad/s).

        Derived from |E(ω)|² ∝ exp[-(ω-ω_c)²/a] with a = 2·ln2/τ²:
            FWHM_ω = 4·ln2/τ  [Rom03 text after Eq. 9]
        """
        if np.isinf(self.tau):
            return 0.0
        return 4 * np.log(2) / self.tau

    def omega_grid(self) -> np.ndarray:
        """N_freq uniformly spaced ω values spanning the full spectral support.

        Half-width = min(4σ, ω_c) where σ = √a is the std of |E(ω)|².
        - 4σ covers >99.99% of the Gaussian spectral weight.
        - The ω_c cap keeps ω > 0 (no negative frequencies); for τ ≲ 1.9 fs
          the grid is therefore ω ∈ [0, 2ω_c].

        Validation against [Rom03]: integrating only the FWHM band (a literal
        reading of "201 equally sampled values within Ω") discards 24% of the
        spectral weight and gives Linfoot S_tr=1.020 vs the paper's 1.062.
        The full-support grid ω ∈ (0, 2ω_c) at τ=1 fs reproduces the paper:
        S_ax=1.058 (paper 1.057), F≈0.96 (paper 0.96), pulsed pedestal ≈0.05
        at r=1 μm (matches Fig. 2). The paper evidently integrated the full
        positive spectrum; its quoted 483 nm–1.67 μm band describes the FWHM,
        not the integration window.
        """
        a = 2 * np.log(2) / self.tau ** 2
        hw = min(4.0 * np.sqrt(a), self.omega_c)
        return np.linspace(self.omega_c - hw, self.omega_c + hw, self.N_freq)

    def spectral_power(self, omega: np.ndarray) -> np.ndarray:
        """Power spectrum |E(ω)|² of an unchirped Gaussian pulse.

            |E(ω)|² ∝ exp[-(ω-ω_c)²/(2a)],  a = 2·ln2/τ²
        FWHM = 4·ln2/τ — matches spectral_bandwidth and omega_grid edges (S=0.5).
        [Rom03 Eqs. 8–9, b=0 (unchirped)]
        """
        a = 2 * np.log(2) / self.tau ** 2
        return np.exp(-(np.asarray(omega) - self.omega_c) ** 2 / (2.0 * a))

    def k_for_omega(self, omega: float) -> float:
        """Wave number k = n·ω/c  (μm⁻¹) at angular frequency ω."""
        return self.n * float(omega) / C_UM

    def with_XNA(self, X_NA: float) -> "SimConfig":
        """Return a copy with a different numerical aperture."""
        return SimConfig(
            lam_c=self.lam_c, X_NA=X_NA, n=self.n,
            tau=self.tau, N_freq=self.N_freq, N_theta=self.N_theta,
        )

    def with_tau(self, tau: float) -> "SimConfig":
        """Return a copy with a different pulse width."""
        return SimConfig(
            lam_c=self.lam_c, X_NA=self.X_NA, n=self.n,
            tau=tau, N_freq=self.N_freq, N_theta=self.N_theta,
        )
