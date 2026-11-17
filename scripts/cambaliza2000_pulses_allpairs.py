r"""Pulsed 2CE counting all photon pairs from both beams (narrow 350-nm transition, phase-locked pulses).

The two-photon amplitude at P sums all pairs of photons whose frequencies add to the transition ω_e, from either
beam, before squaring (second-order perturbation theory, narrow final state):

    A(P) = ∫ E(P, t)² e^{iω_e t} dt,   E = E₁ + E₂,   E_j = env_j(P, t) e^{−iω_j t},
         = A₁₁ + 2 A₁₂ + A₂₂,   A_jk = ∫ env_j env_k e^{i(ω_e − ω_j − ω_k) t} dt,     F(P) = |A(P)|².

2A₁₂: one photon from each beam (the 2CE pairs; ω₁ + ω₂ = ω_e). A₁₁, A₂₂: both photons from one beam, possible only
where that beam's spectrum reaches ω_e/2 (700 nm), i.e. for short pulses. The pulses are phase-locked (one source),
so the three terms interfere. 'one pair' = |2A₁₂|², 'all pairs' = |A|². Paraxial scalar, NA 0.5, air, zero delay,
transform-limited Gaussian pulses (same fields as cambaliza2000_pulses_delay.py).

    python scripts/cambaliza2000_pulses_allpairs.py
    -> output/08_two_color/cambaliza2000/pulses/allpairs/{allpairs.npz, numbers.txt, axial_*.png, map_*.png}
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np

from mcdo.pulsed2ce import _fields, C_UM_FS

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'cambaliza2000', 'pulses', 'allpairs')
os.makedirs(OUT, exist_ok=True)
NA, N, L1, L2, LE = 0.5, 1.0, 0.750, 0.656, 0.350
W1, W2, WE = (2 * np.pi * C_UM_FS / l for l in (L1, L2, LE))       # rad/fs


def env_t(x, z, lam, tau, theta, t, window):
    """Field envelope (n_t, points) about the centre frequency of its pulse."""
    dw, c, E = _fields(x, z, lam, tau, window, NA, N, theta, 0.0, 0.0, 'paraxial', None, None)
    return np.tensordot(c[None, :] * np.exp(-1j * np.outer(t, dw)), E, axes=(1, 0))


def amplitudes(x, z, tau, theta):
    """A₁₁, A₁₂, A₂₂ and the intensity overlap ∫ I₁ I₂ dt at lab points (x, z)."""
    x, z = np.broadcast_arrays(np.asarray(x, float).ravel(), np.asarray(z, float).ravel())
    reach = N * np.sqrt(np.max(x ** 2 + z ** 2)) / C_UM_FS
    dt = min(tau / 20, 0.4)                                     # resolves ω₂ − ω₁ = 0.36 rad/fs
    t = np.arange(-(3 * tau + reach), 3 * tau + reach + dt / 2, dt)
    window = 2 * (4 * tau + reach)
    e1 = env_t(x, z, L1, tau, 0.0, t, window)
    e2 = env_t(x, z, L2, tau, theta, t, window)
    ph = lambda d: np.exp(1j * d * t)[:, None]
    A11 = np.sum(e1 * e1 * ph(WE - 2 * W1), axis=0) * dt
    A12 = np.sum(e1 * e2 * ph(WE - W1 - W2), axis=0) * dt
    A22 = np.sum(e2 * e2 * ph(WE - 2 * W2), axis=0) * dt
    I12 = np.sum(np.abs(e1) ** 2 * np.abs(e2) ** 2, axis=0) * dt
    return A11, A12, A22, I12


def fwhm(s, y):
    y = y / y.max()
    i0 = int(np.argmax(y))
    r, l = i0, i0
    while r < len(y) - 1 and y[r] >= 0.5:
        r += 1
    while l > 0 and y[l] >= 0.5:
        l -= 1
    return np.interp(0.5, [y[r], y[r - 1]], [s[r], s[r - 1]]) - np.interp(0.5, [y[l], y[l + 1]], [s[l], s[l + 1]])


def main():
    zs, xs = np.linspace(-5, 5, 1001), np.linspace(-1.5, 1.5, 601)
    res, lines = {}, []
    for theta, tk in ((np.pi, 'pi'), (0.0, '0'), (np.pi / 2, 'pi2')):
        for tau in (10.0, 20.0, 100.0):
            for cut, (x, z), s in (('z', (0 * zs, zs), zs), ('x', (xs, 0 * xs), xs)):
                A11, A12, A22, I12 = amplitudes(x, z, tau, theta)
                one, allp, single = np.abs(2 * A12) ** 2, np.abs(A11 + 2 * A12 + A22) ** 2, np.abs(A11) ** 2 + np.abs(A22) ** 2
                key = f'{tk}_{tau:g}_{cut}'
                res.update({key + '_one': one, key + '_all': allp, key + '_single': single, key + '_I12': I12})
                pk = one.max()
                fo, fa = fwhm(s, one), fwhm(s, allp)
                lines.append(f'theta {tk}, tau {tau:g} fs, {cut}: FWHM one pair {fo:.3f} um, all pairs {fa:.3f} um; '
                             f'max all/one {allp.max() / pk:.3f}; single-beam |A11|²+|A22|² max / one-pair max '
                             f'{single.max() / pk:.4f}; one-pair vs ∫I1I2 shape rms diff '
                             f'{np.sqrt(np.mean((one / one.max() - I12 / I12.max()) ** 2)):.4f}')
                print(lines[-1], flush=True)
    np.savez_compressed(os.path.join(OUT, 'allpairs.npz'), zs=zs, xs=xs, **res)
    open(os.path.join(OUT, 'numbers.txt'), 'w').write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
