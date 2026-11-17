r"""Samples of the delay sweep (cambaliza2000_pulses_delay.py, fields from the tables) recomputed the long way, with
beam_field at every frequency, on the stored points.

For each sample: the largest relative difference of the three peaks (total, crest, cross) from their stored values
(float64, pass below 1e-8) and, where the profiles are kept, of the stored profiles (float32, pass below 1e-6).

    python scripts/cambaliza2000_delay_sample_check.py   ->  delay_sweep/sample_check.txt (appended)
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np

D = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'cambaliza2000', 'pulses', 'delay_sweep')
LOG = os.path.join(D, 'sample_check.txt')
PASS, PASS32 = 1e-8, 1e-6
TH = {'0': 0.0, 'pi2': np.pi / 2, 'pi': np.pi}

# (set, NA, signal, angle, cut, τ in fs, grid, delay in fs), a few per batch of run_delay.sh
SAMPLES = [
    ('rw_air', 0.1, '2ce', 'pi', 'z', 100, 'coarse', 150.0), ('rw_air', 0.25, '2pe', 'pi2', 'x', 30, 'coarse', 0.0),
    ('rw_air', 0.5, '2ce', 'pi', 'z', 10, 'fine', 1.3), ('rw_air', 0.9, '2ce', '0', 'x', 20, 'fine', 17.6),
    ('paraxial_air', 0.15, '2ce', 'pi', 'z', 50, 'coarse', 50.0), ('paraxial_air', 0.5, '2pe', 'pi', 'z', 5, 'fine', 2.4),
    ('paraxial_air_eps0.9', 0.4, '2ce', 'pi2', 'z', 20, 'coarse', 16.0),
    ('paraxial_water', 1.1, '2ce', 'pi', 'x', 5, 'coarse', 7.5), ('rw_oil', 1.45, '2ce', 'pi', 'z', 30, 'coarse', 33.0),
    ('rw_oil_gauss4', 0.7, '2pe', '0', 'z', 100, 'coarse', 200.0),
    ('rw_water', 1.2, '2ce', 'pi', 'z', 10, 'fine', 0.7), ('rw_water_gauss4', 0.8, '2ce', 'pi', 'x', 50, 'coarse', 25.0),
    ('rw_air_gauss4', 0.9, '2ce', 'pi', 'z', 20, 'fine', 2.1), ('rw_air_eps0.5', 0.9, '2pe', '0', 'z', 5, 'fine', 9.9),
    ('rw_air_eps0.99', 0.95, '2ce', 'pi', 'z', 30, 'coarse', 60.0), ('paraxial_air_gauss4', 0.1, '2ce', 'pi', 'x', 20, 'coarse', 10.0),
]


def settings(folder):
    parts = folder.split('_')
    env = dict(MODEL=parts[0], MEDIUM=parts[1], EPS='0', APOD='0', POL='s')
    for p in parts[2:]:
        if p.startswith('eps'):
            env['EPS'] = p[3:]
        elif p.startswith('gauss'):
            env['APOD'] = p[5:]
        elif p == 'polp':
            env['POL'] = 'p'
    return env


def one(sample):
    folder, na, sig, tk, cut, tau, grid, dl = sample
    os.environ.update(settings(folder), GRID=grid)
    import pandas as pd
    import cambaliza2000_pulses_delay as P                          # a new process per sample reads its settings
    f = os.path.join(D, folder, f'na{na:g}_{grid}')
    t = pd.read_parquet(f + '.parquet').query('sig == @sig and theta == @tk and cut == @cut and tau == @tau')
    a = np.load(f + '.npz')
    base = f'{sig}_{tk}_{cut}'
    s = a[f'{base}_s']
    t0 = time.time()
    p = P.pulsed(na, float(tau), TH[tk], s, cut, sig, dl, fields=P.long_fields)
    row = t.iloc[int(np.argmin(np.abs(t.delay_fs.values - dl)))]
    diff = max(abs(p[i].max() / row[f'peak_{q}'] - 1) for i, q in enumerate(P.QS))
    kept = a[f'{base}_{tau:g}_d']
    extra, dprof = '', 0.0
    if np.any(np.isclose(kept, dl)):
        p0 = P.pulsed(na, float(tau), TH[tk], s, cut, sig, 0.0, fields=P.long_fields).max(axis=1)
        prof = a[f'{base}_{tau:g}_p'][:, int(np.argmin(np.abs(kept - dl)))]
        dprof = (np.abs(p / p0[:, None] - prof).max(axis=1) / np.abs(prof).max(axis=1)).max()
        extra = f', stored profiles {dprof:.1e}'
    return (f'sample {folder} NA {na:g} {sig} {tk} {cut} {tau:g} fs {grid} delay {dl:g} fs: largest difference of the '
            f'peaks from the long way {diff:.1e}{extra} ({len(s)} points, {time.time() - t0:.0f} s)'), diff, dprof


if __name__ == '__main__':
    from multiprocessing import Pool
    if os.environ.get('SAMPLES') == 'polp':                         # the runs with polarization p
        SAMPLES = [('rw_air_polp', 0.5, '2ce', 'pi2', 'x', 5, 'fine', 1.3), ('rw_air_polp', 0.7, '2ce', 'pi2', 'z', 10, 'coarse', 10.0),
                   ('rw_air_polp', 0.3, '2pe', 'pi2', 'x', 20, 'coarse', 0.0), ('rw_air_polp', 0.5, '2ce', 'pi', 'x', 10, 'fine', 2.1),
                   ('rw_air_polp', 0.7, '2ce', '0', 'z', 100, 'coarse', 100.0), ('rw_air_polp', 0.5, '2pe', 'pi', 'z', 5, 'fine', 0.7)]
    with open(LOG, 'a') as f:
        f.write(f'--- {time.strftime("%Y-%m-%d %H:%M")} samples of run_delay.sh, long way\n')
    worst, worst32 = 0.0, 0.0
    with Pool(int(os.environ.get('WORKERS', 6)), maxtasksperchild=1) as pool:
        for msg, w, w32 in pool.imap_unordered(one, SAMPLES):
            worst, worst32 = max(worst, w), max(worst32, w32)
            print(msg, flush=True)
            with open(LOG, 'a') as f:
                f.write(msg + '\n')
    ok = worst < PASS and worst32 < PASS32
    msg = (f'SAMPLES largest difference over {len(SAMPLES)} samples: peaks {worst:.1e}, stored profiles {worst32:.1e} '
           f'({"pass" if ok else "FAIL"})')
    print(msg, flush=True)
    with open(LOG, 'a') as f:
        f.write(msg + '\n')
