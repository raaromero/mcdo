r"""Peak, position and width of the pulsed 2CE and 2PE profiles against the delay of pulse 2, for the sets and NAs of
the NA sweep (cambaliza2000_pulses_na_sweep.py, same grids and settings), with the fields from the tables
(cambaliza2000_fast_field.py).

Each delay gives three profiles along the cut:
    total  Σ_ij |A¹¹_ij + X_ij + A²²_ij|²   phase-locked pulses, all photon pairs (as in the NA sweep)
    crest  Σ_ij (|A¹¹_ij| + |X_ij| + |A²²_ij|)²
    cross  Σ_ij |X_ij|²                      the 350-nm pairs for 2CE (λ₁ + λ₂), the cross term of the two beams for 2PE
The cross profile is the 2CE signal of Lim & Saloma (2003), whose fluorescence probes are chosen against two-photon
excitation by λ₁ or λ₂ alone; for τ ≥ 30 fs the three agree.

    GRID = coarse   delays 0 to 2τ in steps of 0.1τ, τ = 5, 10, 20, 30, 50, 100 fs
    GRID = fine     delays 0 to 2τ in steps of 0.1 fs, τ = 5, 10, 20 fs (11 points per 1.17-fs fringe of the total)

    MODEL=rw MEDIUM=air NAS=0.3,0.5 GRID=coarse python scripts/cambaliza2000_pulses_delay.py
    -> output/08_two_color/cambaliza2000/pulses/delay_sweep/<set>/na<NA>_<grid>.parquet   one row per case and delay
       output/08_two_color/cambaliza2000/pulses/delay_sweep/<set>/na<NA>_<grid>.npz       profiles at a few delays

Rows hold the delay (fs and τ) and, for q = total, crest, cross: peak_q (the maximum), rel_q (over the maximum at no
delay), pos_q (its position, µm) and fwhm_q (µm). The npz holds <sig>_<θ>_<cut>_s (points), and for each τ
<sig>_<θ>_<cut>_<τ>_d (delays in fs) and <sig>_<θ>_<cut>_<τ>_p (float32, (3, delays, points): total, crest, cross over
their peaks at no delay), at 0, 0.5τ, τ, 1.5τ, 2τ (coarse) or 0 to 2.5 fs, one fringe (fine). load() reads a set back.
"""
import glob
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np
import pandas as pd
from multiprocessing import Pool

import cambaliza2000_pulses_na_sweep as S
from cambaliza2000_pulses_na_sweep_fast import focus
from cambaliza2000_pulses_sweep import fwhm
from mcdo.pulsed2ce import spectrum, C_UM_FS

GRID = os.environ.get('GRID', 'coarse')
ROOT = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'cambaliza2000', 'pulses', 'delay_sweep')
OUT = os.path.join(ROOT, os.path.basename(S.OUT))
QS = ('total', 'crest', 'cross')


def delays(tau):
    """Delays in fs of the grid, and the indices whose profiles are kept."""
    if GRID == 'coarse':
        d = np.round(np.arange(0, 21) * 0.1, 10) * tau
        return d, [0, 5, 10, 15, 20]
    d = np.round(np.arange(0, int(round(20 * tau)) + 1) * 0.1, 10)
    return d, list(range(26))


def fast_fields(na, w, th, x, z):
    return focus(na).fields(w, th, x, z)


def long_fields(na, w, th, x, z):
    return np.stack([S.field(wm, na, th, x, z, w=True) for wm in w])


def pulsed(na, tau, theta, s, cut, sig, delay=0.0, fields=fast_fields):
    """S.pulsed (same time grid and sums), returning the cross profile Σ|X|² as well."""
    l1, l2 = S.LAMS[sig]
    w1, w2 = 2 * np.pi * C_UM_FS / l1, 2 * np.pi * C_UM_FS / l2
    reach = S.N * np.max(np.abs(s)) / C_UM_FS + abs(delay)
    dt = min(tau / 20, 0.4)
    t = np.arange(-(3 * tau + reach), 3 * tau + reach + dt / 2, dt)
    window = 2 * (4 * tau + reach)
    out = np.empty((3, len(s)))
    specs = [spectrum(l, tau, t_window=window) for l in (l1, l2)]
    for b0 in range(0, len(s), S.BLOCK):
        sb = s[b0:b0 + S.BLOCK]
        x, z = (0 * sb, sb) if cut == 'z' else (sb, 0 * sb)
        env = []
        for (w, a, d), th, dl in zip(specs, (0.0, theta), (0.0, delay)):
            E = fields(na, w, th, x, z)                                                # (n_ω, comp, pts)
            c = a * d * np.exp(-1j * np.outer(t - dl, w - w.mean())) * np.exp(1j * w.mean() * dl)
            env.append(np.tensordot(c, E, axes=(1, 0)))
        e1, e2 = env
        ph = lambda dw: np.exp(1j * dw * t) * dt
        A12 = np.einsum('t,tip,tjp->ijp', ph(S.WE - w1 - w2), e1, e2)
        X = A12 + A12.transpose(1, 0, 2)        # symmetric in the components, as (E₁ + E₂)_i (E₁ + E₂)_j is; for one
                                                 # component (polarization s) this is 2A¹² for 2CE, as in S.pulsed
        A11 = np.einsum('t,tip,tjp->ijp', ph(S.WE - 2 * w1), e1, e1)
        A22 = np.einsum('t,tip,tjp->ijp', ph(S.WE - 2 * w2), e2, e2)
        out[0, b0:b0 + S.BLOCK] = (np.abs(A11 + X + A22) ** 2).sum(axis=(0, 1))
        out[1, b0:b0 + S.BLOCK] = ((np.abs(A11) + np.abs(X) + np.abs(A22)) ** 2).sum(axis=(0, 1))
        out[2, b0:b0 + S.BLOCK] = (np.abs(X) ** 2).sum(axis=(0, 1))
    return out


def one_case(args):
    na, sig, tk, th, cut, tau = args
    t0 = time.time()
    s = S.grid(na, cut)
    d, keep = delays(tau)
    rows, prof = [], np.empty((3, len(keep), len(s)), np.float32)
    p0 = None
    for i, dl in enumerate(d):
        p = pulsed(na, tau, th, s, cut, sig, dl)
        pk = p.max(axis=1)
        if i == 0:
            p0 = pk
        row = dict(sig=sig, theta=tk, cut=cut, tau=tau, delay_fs=dl, delay_tau=dl / tau)
        for q, y, m, m0 in zip(QS, p, pk, p0):
            row.update({f'peak_{q}': m, f'rel_{q}': m / m0, f'pos_{q}': s[np.argmax(y)], f'fwhm_{q}': fwhm(s, y)})
        rows.append(row)
        if i in keep:
            prof[:, keep.index(i)] = p / p0[:, None]
    print(f'{S.MODEL} {S.MEDIUM} eps {S.EPS:g} apod {S.APOD:g} NA {na:g} {sig} {tk} {cut} {tau:g} fs {GRID}: '
          f'{len(d)} delays, {time.time() - t0:.0f} s', flush=True)
    base = f'{sig}_{tk}_{cut}'
    return na, rows, {f'{base}_s': s, f'{base}_{tau:g}_d': d[keep], f'{base}_{tau:g}_p': prof}


def main():
    os.makedirs(OUT, exist_ok=True)
    taus = (5, 10, 20, 30, 50, 100) if GRID == 'coarse' else (5, 10, 20)
    cases = [(na, sig, tk, th, cut, tau) for na in S.NAS for sig in ('2ce', '2pe') for tk, th in S.THETAS
             for cut in ('z', 'x') for tau in taus if not (tk == 'pi2' and na > S.N * np.sin(np.pi / 4) + 1e-9)]
    cases.sort(key=lambda c: -len(S.grid(c[0], c[4])) * len(delays(c[5])[0]) * (c[5] + 20))     # longest first
    left = {na: sum(1 for c in cases if c[0] == na) for na in S.NAS}
    rows, arrays = {na: [] for na in S.NAS}, {na: {} for na in S.NAS}
    with Pool(int(os.environ.get('WORKERS', 7))) as pool:
        for na, r, a in pool.imap_unordered(one_case, cases):
            rows[na] += r
            arrays[na].update(a)
            left[na] -= 1
            if left[na] == 0:                                           # all cases of this NA are in
                f = os.path.join(OUT, f'na{na:g}_{GRID}')
                df = pd.DataFrame(rows[na])
                for k, v in (('pol', S.POL), ('model', S.MODEL), ('medium', S.MEDIUM), ('n', S.N), ('eps', S.EPS), ('apod', S.APOD),
                             ('set', os.path.basename(S.OUT)), ('na', na), ('grid', GRID)):
                    df.insert(0, k, v)
                df.to_parquet(f + '.parquet', index=False)
                np.savez_compressed(f + '.npz', **arrays[na])
                print(f'saved NA {na:g}', flush=True)
                rows[na], arrays[na] = [], {}


def load(sets='*', grid='*'):
    """All rows of the delay runs as one table, e.g. load('rw_air', 'coarse').query("sig == '2ce' and theta == 'pi'")."""
    files = sorted(glob.glob(os.path.join(ROOT, sets, f'na*_{grid}.parquet')))
    return pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)


if __name__ == '__main__':
    main()
