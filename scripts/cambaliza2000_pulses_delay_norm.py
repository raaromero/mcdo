r"""Pulsed 2CE and 2PE against the delay between the pulses, the delay given as a path difference in wavelengths.

Beam 2's pulse reaches the focus Δt after beam 1's; the delay is written as the path difference cΔt in units of
λ₀ = 700 nm (the 2PE wavelength; one unit is 2.335 fs), N = cΔt/λ₀. With facing lenses the pulses then meet at
z = cΔt/2n = Nλ₀/2n, half a wavelength per unit of N. Same model as cambaliza2000_pulses_sweep.py (all photon pairs,
narrow 350-nm level, phase-locked, paraxial NA 0.5, air), along the axis (x = 0). For each θ, τ and N: the profile
after the pulses, its peak, centroid and FWHM (fringe crests), and the dye rate (the 'now' rate added up).

    python scripts/cambaliza2000_pulses_delay_norm.py
    -> output/08_two_color/cambaliza2000/pulses/delay_norm/{delay_norm.npz, delay_norm.txt}
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import numpy as np

from cambaliza2000_pulses_sweep import run, fwhm, ZS, C_UM_FS, OUT as SWEEP

OUT = os.path.join(SWEEP, '..', 'delay_norm')
os.makedirs(OUT, exist_ok=True)
L0 = 0.700                                                          # µm: unit of path difference
NS = np.arange(-20, 20.5, 1.0)                                      # path difference in wavelengths
TAUS = (10.0, 20.0, 100.0)
THETAS = (('0', 0.0), ('pi2', np.pi / 2), ('pi', np.pi))


def one(sig, tk):
    """All τ and N for one signal and θ -> part_<sig>_<θ>.npz."""
    th, res = dict(THETAS)[tk], {}
    for tau in TAUS:
        out = {q: [] for q in ('all', 'rate', 'one')}
        for n in NS:
            _, fin, _ = run(tau, th, 'z', sig, delay=n * L0 / C_UM_FS)
            for q in out:
                out[q].append(fin['crest' if q == 'all' else q])
        for q, v in out.items():
            res[f'{sig}_{tk}_{tau:g}_{q}'] = np.array(v)
        print(sig, tk, tau, 'done', flush=True)
    np.savez_compressed(os.path.join(OUT, f'part_{sig}_{tk}.npz'), **res)


def main():
    """Six processes (signal × θ), then one file."""
    from multiprocessing import Pool
    jobs = [(sig, tk) for sig in ('2ce', '2pe') for tk, _ in THETAS]
    with Pool(6) as p:
        p.starmap(one, jobs)
    res, lines = {}, []
    for sig, tk in jobs:
        res.update(np.load(os.path.join(OUT, f'part_{sig}_{tk}.npz')))
    for key in sorted({k.rsplit('_', 1)[0] for k in res}):
        A = res[f'{key}_all']
        pk, cen = A.max(1), (A * ZS).sum(1) / A.sum(1)
        w = [fwhm(ZS, a) for a in A]
        lines.append(f'{key}: N ' + ' '.join(f'{n:+.0f}:{p / pk.max():.3f}/{c:+.2f}/{x:.2f}' for n, p, c, x in zip(NS, pk, cen, w)))
    np.savez_compressed(os.path.join(OUT, 'delay_norm.npz'), ns=NS, zs=ZS, taus=np.array(TAUS), **res)
    open(os.path.join(OUT, 'delay_norm.txt'), 'w').write('peak (of max) / centroid (um) / FWHM crest (um)\n' + '\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
