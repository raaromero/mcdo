r"""How many wavelengths per pulse the photon-pair sum needs: the count beyond which the 2CE PSF stops changing.

The pulsed 2CE signal sums the photon pairs that reach the transition, ω_a + ω_b = ω_e
(mcdo.pulsed2ce.two_color_pairs), over N sampled wavelengths per pulse. Each pair carries the phase of its
arrival time, so the sum must resolve the largest arrival-time mismatch on the grid, |T_1 − T_2 − Δt|,
which is largest for facing lenses at the far end of the window with O′ offset and Δt = ±2τ.

For each pulse duration τ and both geometries it computes the signal on the window (±1 × ±5 µm, coarse
grid), for O′ aligned and offset to (±0.96, ±4.8) µm (the extreme offsets of the runs) and Δt = 0, ±τ, ±2τ,
and reports the largest change against N = 257, relative to the aligned peak. Grids are nested so the
fields are computed once per τ.

    python scripts/check_pair_count.py
    -> output/08_two_color/lim2002/pairs_convergence.csv, slides/pairs_convergence.png
"""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np

from mcdo.pulsed2ce import C_UM_FS, pair_grid, pair_signal
from mcdo.twobeam import beam_field

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'lim2002')
MODEL, NA = os.environ.get('MODEL', 'paraxial'), float(os.environ.get('NA', '0.5'))
TAUS = (10.0, 20.0, 100.0)
FAMILIES = ((5, 9, 17, 33, 65, 129, 257), (7, 13, 25, 49, 97, 193))
NREF = 257
OFFSETS = ((0.0, 0.0), (0.96, 4.8), (-0.96, -4.8))
TH = {'pi': np.pi, 'pi2': np.pi / 2}
X, Z = np.meshgrid(np.linspace(-1, 1, 21), np.linspace(-5, 5, 51))


def field(args):
    w, th, xc, zc, psi = args
    kw = dict(model='rw', psi=psi) if MODEL == 'rw' else {}
    return beam_field(X, Z, 2 * np.pi * C_UM_FS / w, NA, 1.0, theta=th, xc=xc, zc=zc, **kw).astype(np.complex128)


def fields(pool, ws, th, xc, zc, psis):
    return [np.stack(list(pool.map(field, [(w, th, xc, zc, p) for w in ws], chunksize=8))) for p in psis]


def signal(F1, F2, nmax, n, tau, delay):
    wa, wb, wt, u = pair_grid(0.750, 0.656, tau, None, n, 10.0)
    step = (nmax - 1) // (n - 1)
    c = wt * np.exp(-1j * u * delay)
    return sum(pair_signal(c, E1[::step], E2[::step], MODEL == 'rw') for E1 in F1 for E2 in F2) / (len(F1) * len(F2))


if __name__ == '__main__':
    psis = (0.0, np.pi / 2) if MODEL == 'rw' else (None,)
    rows = []
    with ProcessPoolExecutor(6) as pool:
        for tau in TAUS:
            for th in TH:
                res = {}
                for fam in FAMILIES:
                    nmax = fam[-1]
                    wa, wb, _, _ = pair_grid(0.750, 0.656, tau, None, nmax, 10.0)
                    F1 = fields(pool, wa, 0.0, 0.0, 0.0, psis)
                    for xc, zc in OFFSETS:
                        F2 = fields(pool, wb, TH[th], xc, zc, psis)
                        for n in fam:
                            for d in (-2, -1, 0, 1, 2):
                                res[(n, xc, zc, d)] = signal(F1, F2, nmax, n, tau, d * tau)
                peak = res[(NREF, 0.0, 0.0, 0)].max()
                for n in sorted({k[0] for k in res}):
                    err = max(np.abs(res[(n, xc, zc, d)] - res[(NREF, xc, zc, d)]).max()
                              for xc, zc in OFFSETS for d in (-2, -1, 0, 1, 2)) / peak
                    rows.append((tau, th, n, err))
                    print(f'{MODEL} NA {NA:g}  τ {tau:g} fs  {th}  N {n:3d}  max change {err:.2e}', flush=True)
    path = os.path.join(OUT, f'pairs_convergence_{MODEL}_na{NA:g}.csv')
    with open(path, 'w') as fh:
        fh.write('tau_fs,theta,n_wavelengths,max_change_rel_peak\n')
        for r in rows:
            fh.write(','.join(str(v) for v in r) + '\n')
    print('Saved ->', path)
