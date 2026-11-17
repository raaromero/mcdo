r"""The total with all photon pairs of the delay sweep, recomputed in frequency with no time grid.

The sweep (cambaliza2000_pulses_delay.py) builds each pulse in time and integrates E_a E_b e^{iω_e t} over t. Here
the same amplitudes are sums over the pairs of frequencies that add to ω_e,

    A^{ab}(P) = ∫ Ẽ_a(P, ω) Ẽ_b(P, ω_e − ω) dω,     Ẽ_b(P, ω) = a_b(ω) (ω/ω_b) E_ω(P) e^{iωΔt_b},

on a frequency grid symmetric about ω_e/2, with the fields from beam_field at each frequency, and
F = |A¹¹ + 2A¹² + A²²|². The stored profiles of the fine grid (delays 0 to 2.5 fs) are compared at every fifth point of the long lines and at all points of the short ones.

    python scripts/cambaliza2000_delay_allpairs_check.py  ->  delay_sweep/allpairs_check.txt
"""
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np

from mcdo.twobeam import beam_field

C = 0.299792458
D = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'cambaliza2000', 'pulses', 'delay_sweep')
WE = 2 * np.pi * C / 0.350
LAMS = {'2ce': (0.750, 0.656), '2pe': (0.700, 0.700)}
TH = {'0': 0.0, 'pi2': np.pi / 2, 'pi': np.pi}
CASES = [(m, na, sig, tk, cut, tau) for m in ('paraxial', 'rw') for na, tk, cut in ((0.5, '0', 'z'), (0.5, 'pi2', 'x'),
         (0.5, 'pi', 'z'), (0.7, 'pi2', 'z'), (0.9, 'pi', 'z')) for sig in ('2ce', '2pe') for tau in (5, 10)
         if not (m == 'paraxial' and na > 0.5)]


def total(model, na, sig, theta, x, z, tau, delays, dw=0.003):
    l1, l2 = LAMS[sig]
    w1, w2 = 2 * np.pi * C / l1, 2 * np.pi * C / l2
    s = 2 * np.sqrt(np.log(2)) / tau
    half = abs(w2 - w1) / 2 + 6 * s
    n = 2 * int(np.ceil(half / dw)) + 1
    w = WE / 2 + np.linspace(-half, half, n)
    w = w[w > 0.3] if w[0] <= 0.3 else w                                # the spectrum is negligible there
    if len(w) != n:                                                     # keep the grid symmetric about ω_e/2
        k = n - len(w); w = (WE / 2 + np.linspace(-half, half, n))[k:n - k]
    dw = w[1] - w[0]

    def spec(w0, th):
        kw = dict(model='rw', psi=np.pi / 2) if model == 'rw' else {}
        E = np.stack([np.atleast_2d(beam_field(x, z, 2 * np.pi * C / wk, na, theta=th, **kw))[1 if model == 'rw' else 0]
                      for wk in w])                                     # the y component (the others are zero here)
        return np.exp(-(w - w0) ** 2 * tau ** 2 / (8 * np.log(2)))[:, None] * (w / w0)[:, None] * E

    e1, e2 = spec(w1, 0.0), spec(w2, theta)
    out = []
    for dl in delays:
        f2 = e2 * np.exp(1j * w * dl)[:, None]
        A = ((e1 + f2) * (e1 + f2)[::-1]).sum(axis=0) * dw              # ∫ Ẽ(ω) Ẽ(ω_e − ω) dω with Ẽ = Ẽ₁ + Ẽ₂
        out.append(np.abs(A) ** 2)
    return np.array(out)


if __name__ == '__main__':
    lines, worst = [], 0.0
    for model, na, sig, tk, cut, tau in CASES:
        a = np.load(os.path.join(D, f'{model}_air', f'na{na:g}_fine.npz'))
        s, d, prof = a[f'{sig}_{tk}_{cut}_s'], a[f'{sig}_{tk}_{cut}_{tau}_d'], a[f'{sig}_{tk}_{cut}_{tau}_p'][0]
        i0 = int(np.argmax(prof[0]))                                    # the stored peak at no delay, kept in the sample
        keep = np.unique(np.r_[np.arange(0, len(s), 5 if len(s) > 400 else 1), i0])
        s, prof = s[keep], prof[:, keep]
        x, z = (0 * s, s) if cut == 'z' else (s, 0 * s)
        t0 = time.time()
        F = total(model, na, sig, TH[tk], x, z, float(tau), d)
        err = np.abs(F / F[0].max() - prof).max()
        worst = max(worst, err)
        lines.append(f'{model} NA {na:g} {sig} {tk} {cut} {tau} fs, {len(d)} delays from 0 to {d[-1]:g} fs, {len(s)} points: '
                     f'largest difference of the total from the pairs summed in frequency {err:.1e} of the peak '
                     f'(stored range {prof.min():.3f} to {prof.max():.3f}; {time.time() - t0:.0f} s)')
        print(lines[-1], flush=True)
    lines.append(f'ALL PAIRS largest difference over {len(CASES)} cases: {worst:.1e} ({"pass" if worst < 5e-3 else "FAIL"})')
    print(lines[-1])
    with open(os.path.join(D, 'allpairs_check.txt'), 'w') as f:
        f.write('\n'.join(lines) + '\n')
