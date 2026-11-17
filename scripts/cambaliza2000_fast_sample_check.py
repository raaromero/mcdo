r"""Samples of the second queue (run_queue2.sh, computed with the tables) recomputed the long way, with beam_field at
every frequency as in cambaliza2000_pulses_na_sweep.py, on the stored points.

For each sample: the largest difference of the normalized total and crest profiles, and for a delay the difference
of the peak over the peak without delay (the stored _rel). Pass: all below 1e-8.

    python scripts/cambaliza2000_fast_sample_check.py   ->  na_sweep/fast_check.txt (appended)
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np

D = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'cambaliza2000', 'pulses', 'na_sweep')
LOG = os.path.join(D, 'fast_check.txt')
PASS = 1e-8
TH = {'0': 0.0, 'pi2': np.pi / 2, 'pi': np.pi}

# (set, NA, signal, angle, cut, τ in fs, delay in units of τ), a few per batch of run_queue2.sh
SAMPLES = [
    ('rw_air', 0.1, '2ce', 'pi', 'z', 5000, 0), ('paraxial_air', 0.2, '2pe', 'pi2', 'z', 3000, 0),
    ('rw_air', 0.1, '2ce', 'pi2', 'x', 2000, 0),
    ('rw_air', 0.15, '2ce', 'pi2', 'z', 4, 0), ('paraxial_air', 0.65, '2pe', '0', 'z', 70, 0),
    ('rw_air', 0.85, '2ce', 'pi', 'x', 10, 0),
    ('rw_air_gauss4', 0.4, '2ce', 'pi', 'z', 20, 0), ('rw_oil_gauss4', 0.6, '2ce', 'pi', 'z', 15, 0),
    ('rw_air_eps0.9', 0.6, '2pe', 'pi2', 'z', 7, 0), ('paraxial_air_eps0.5', 0.8, '2ce', '0', 'x', 50, 0),
    ('rw_air_eps0.99', 0.7, '2ce', 'pi', 'z', 4, 0), ('paraxial_air_eps0.99', 0.95, '2pe', 'pi', 'z', 1000, 0),
    ('rw_air', 0.5, '2ce', 'pi', 'z', 10, 1.3), ('rw_air', 0.3, '2ce', 'pi2', 'z', 30, 2.7),
    ('rw_water', 1.2, '2pe', 'pi', 'x', 5, 0.1), ('rw_air_gauss4', 0.9, '2ce', '0', 'z', 50, 1.9),
    ('rw_air_eps0.9', 0.5, '2ce', 'pi', 'z', 20, 0.6), ('paraxial_air', 0.5, '2pe', 'pi2', 'x', 100, 3),
]


def settings(folder):
    parts = folder.split('_')
    env = dict(MODEL=parts[0], MEDIUM=parts[1], EPS='0', APOD='0')
    for p in parts[2:]:
        if p.startswith('eps'):
            env['EPS'] = p[3:]
        elif p.startswith('gauss'):
            env['APOD'] = p[5:]
    return env


def one(sample):
    folder, na, sig, tk, cut, tau, dl = sample
    os.environ.update(settings(folder))
    import cambaliza2000_pulses_na_sweep as S                       # a new process per sample reads its settings
    from cambaliza2000_fast_field_check import _old_pulsed
    d = np.load(os.path.join(D, folder, f'na{na:g}.npz'))
    s = d[f'{sig}_{tk}_{cut}_s']
    key = f'{sig}_{tk}_{cut}_{tau:g}' + (f'_d{dl:g}' if dl else '')
    t0 = time.time()
    p, c = _old_pulsed(S, na, float(tau), TH[tk], s, cut, sig, dl * tau)
    diff = max(np.abs(p / p.max() - d[key]).max(), np.abs(c / c.max() - d[key + '_crest']).max())
    extra = ''
    if dl:
        p0 = _old_pulsed(S, na, float(tau), TH[tk], s, cut, sig)[0]
        r = abs(p.max() / p0.max() - float(d[key + '_rel']))
        diff = max(diff, r)
        extra = f', peak over the peak without delay {float(d[key + "_rel"]):.6f}'
    return (f'sample {folder} NA {na:g} {sig} {tk} {cut} {tau:g} fs' + (f' delay {dl:g}τ' if dl else '') +
            f': largest difference from the long way {diff:.1e}{extra} ({len(s)} points, {time.time() - t0:.0f} s)'), diff


if __name__ == '__main__':
    from multiprocessing import Pool
    with open(LOG, 'a') as f:
        f.write(f'--- {time.strftime("%Y-%m-%d %H:%M")} samples of run_queue2.sh, long way\n')
    worst = 0.0
    with Pool(int(os.environ.get('WORKERS', 6)), maxtasksperchild=1) as pool:
        for msg, w in pool.imap_unordered(one, SAMPLES):
            worst = max(worst, w)
            print(msg, flush=True)
            with open(LOG, 'a') as f:
                f.write(msg + '\n')
    msg = f'SAMPLES largest difference over {len(SAMPLES)} samples: {worst:.1e} ({"pass" if worst < PASS else "FAIL"})'
    print(msg, flush=True)
    with open(LOG, 'a') as f:
        f.write(msg + '\n')
