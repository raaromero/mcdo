"""
CW and pulsed intensity distributions on (r, z) grids.

Implements Romallosa (2003) Eq. (10):

    |E(P)|² = ∫_{-Ω/2}^{Ω/2} |E(ω)|² · |E(P, ω)|²_CW dω

approximated as a Riemann sum over N_freq = 201 equally spaced frequencies
within the FWHM spectral bandwidth Ω = 4·ln2/τ.
"""

import numpy as np
from .rw_integrals import compute_integrals, integrals_to_intensity
from .config import SimConfig


def cw_intensity(
    r_arr: np.ndarray,
    z_arr: np.ndarray,
    cfg: SimConfig,
    normalize: bool = True,
) -> np.ndarray:
    """CW (monochromatic) intensity |E(P)|² on a (z × r) grid.

    Uses the center frequency λ_c of the config.

    Parameters
    ----------
    r_arr, z_arr : coordinate arrays (μm)
    cfg          : SimConfig instance
    normalize    : if True, divide by peak value

    Returns
    -------
    I : (N_z, N_r) real array
    """
    I0, I1, I2 = compute_integrals(r_arr, z_arr, cfg.k_c, cfg.alpha, cfg.N_theta)
    I = integrals_to_intensity(I0, I1, I2)
    if normalize and I.max() > 0:
        I = I / I.max()
    return I


def pulsed_intensity(
    r_arr: np.ndarray,
    z_arr: np.ndarray,
    cfg: SimConfig,
    normalize: bool = True,
    verbose: bool = False,
) -> np.ndarray:
    """Time-integrated pulsed intensity via spectral summation (Eq. 10).

    Sums contributions from N_freq = 201 uniformly spaced frequencies within
    the FWHM bandwidth Ω, each weighted by the Gaussian power spectrum
    |E(ω)|² ∝ exp[-(ω-ω_c)²/a].

    Parameters
    ----------
    r_arr, z_arr : coordinate arrays (μm)
    cfg          : SimConfig (tau, N_freq, N_theta set here)
    normalize    : if True, divide by peak value
    verbose      : print progress

    Returns
    -------
    I_total : (N_z, N_r) real array
    """
    omegas = cfg.omega_grid()           # (N_freq,)
    S = cfg.spectral_power(omegas)      # (N_freq,) — |E(ω)|² weights
    d_omega = omegas[1] - omegas[0]

    r_arr = np.asarray(r_arr, dtype=float)
    z_arr = np.asarray(z_arr, dtype=float)
    total = np.zeros((len(z_arr), len(r_arr)), dtype=float)

    for j, (omega, s_j) in enumerate(zip(omegas, S)):
        if verbose and j % 50 == 0:
            lam_nm = 2*np.pi*2.998e14/omega*1e3 if omega > 0 else np.inf
            print(f"  freq {j+1}/{len(omegas)}  λ={lam_nm:.1f} nm")
        k_j = cfg.k_for_omega(omega)
        I0, I1, I2 = compute_integrals(r_arr, z_arr, k_j, cfg.alpha, cfg.N_theta)
        I_cw_j = integrals_to_intensity(I0, I1, I2)
        total += s_j * I_cw_j * d_omega

    if normalize and total.max() > 0:
        total = total / total.max()
    return total


def transverse_profile(
    r_arr: np.ndarray,
    cfg: SimConfig,
    pulsed: bool = False,
    normalize: bool = True,
    verbose: bool = False,
) -> np.ndarray:
    """1-D transverse profile at z = 0.

    Returns
    -------
    I : (N_r,) array
    """
    z0 = np.array([0.0])
    if pulsed:
        I2d = pulsed_intensity(r_arr, z0, cfg, normalize=normalize, verbose=verbose)
    else:
        I2d = cw_intensity(r_arr, z0, cfg, normalize=normalize)
    return I2d[0]


def axial_profile(
    z_arr: np.ndarray,
    cfg: SimConfig,
    pulsed: bool = False,
    normalize: bool = True,
    verbose: bool = False,
) -> np.ndarray:
    """1-D axial profile at r = 0.

    Returns
    -------
    I : (N_z,) array
    """
    r0 = np.array([0.0])
    if pulsed:
        I2d = pulsed_intensity(r0, z_arr, cfg, normalize=normalize, verbose=verbose)
    else:
        I2d = cw_intensity(r0, z_arr, cfg, normalize=normalize)
    return I2d[:, 0]
