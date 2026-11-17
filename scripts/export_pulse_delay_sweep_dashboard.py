r"""Delay sweep against NA (cambaliza2000_pulses_delay.py, Richards–Wolf model in air) to the dashboard, for the section
"Delay between the pulses, against NA" of the pulse results view. 2CE only; θ = 0 and π along the axis (z), θ = π/2
across it (x).

* coarse grid (Δt = 0 to 2τ in steps of 0.1τ; τ = 5, 10, 20, 30, 50, 100 fs; every NA of the set), for the circular
  pupil, the Gaussian input α = 4 and the annular pupils ε = 0.5 and 0.9: the peak of the 350-nm pairs over its value
  at no delay (rel_cross) and its position (pos_cross, µm), against Δt/τ;
* fine grid (Δt in steps of 0.1 fs from 0 to 2τ; τ = 5, 10, 20 fs), circular pupil: all pairs and the 350-nm pairs
  against Δt. Polarization perpendicular to the plane of the lens axes (set rw_air): rel_total and rel_cross, each
  over its own value at no delay. Polarization in that plane (set rw_air_polp, NA 0.3, 0.5, 0.7): peak_total and
  peak_cross, both over peak_total at no delay, since with facing lenses the total at no delay is near a minimum.

Values are rounded to 4 significant digits.

    python scripts/export_pulse_delay_sweep_dashboard.py -> dashboard/cambaliza/public/data/pulse_delay_sweep.json
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import numpy as np

import cambaliza2000_pulses_delay as P

DEST = os.path.join(os.path.dirname(__file__), '..', 'dashboard', 'cambaliza', 'public', 'data', 'pulse_delay_sweep.json')
CUT = {'0': 'z', 'pi2': 'x', 'pi': 'z'}
COARSE = ('rw_air', 'rw_air_gauss4', 'rw_air_eps0.5', 'rw_air_eps0.9')
FINE = ('rw_air', 'rw_air_polp')
sig4 = lambda a: [float(f'{float(v):.4g}') if np.isfinite(v) else None for v in a]
key = lambda v: f'{float(v):g}'


def rows(t, th):
    return t[(t.sig == '2ce') & (t.theta == th) & (t.cut == CUT[th])]


out = {'cut': CUT, 'coarse': {}, 'fine': {}, 'nas': {}}
for name in COARSE:
    t = P.load(name, 'coarse')
    out['nas'][name] = sorted(float(v) for v in t.na.unique())
    d = out['coarse'][name] = {}
    for th in CUT:
        for (tau, na), g in rows(t, th).groupby(['tau', 'na']):
            g = g.sort_values('delay_tau')
            out.setdefault('dtau', sig4(g.delay_tau.values))
            assert len(g) == len(out['dtau'])
            d.setdefault(th, {}).setdefault(key(tau), {})[key(na)] = {'rel': sig4(g.rel_cross.values),
                                                                      'pos': sig4(g.pos_cross.values)}
out['taus'] = sorted({int(k) for th in out['coarse']['rw_air'].values() for k in th})
for name in FINE:
    t = P.load(name, 'fine')
    out['nas'][name + '_fine'] = sorted(float(v) for v in t.na.unique())
    d = out['fine'][name] = {}
    for th in CUT:
        for (tau, na), g in rows(t, th).groupby(['tau', 'na']):
            g = g.sort_values('delay_fs')
            dt = g.delay_fs.values
            assert np.allclose(np.diff(dt), 0.1) and dt[0] == 0
            if name.endswith('_polp'):
                ref = float(g.peak_total.iloc[0])
                v = {'total': sig4(g.peak_total.values / ref), 'cross': sig4(g.peak_cross.values / ref)}
            else:
                v = {'total': sig4(g.rel_total.values), 'cross': sig4(g.rel_cross.values)}
            d.setdefault(th, {}).setdefault(key(tau), {})[key(na)] = v
out['fine_step'] = 0.1                                              # fs; the fine grid starts at Δt = 0
json.dump(out, open(DEST, 'w'), separators=(',', ':'))
print(f'-> {DEST} ({os.path.getsize(DEST) / 1e6:.2f} MB)')
