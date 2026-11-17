r"""Normalized-delay sweep (cambaliza2000_pulses_delay_norm.py) to the dashboard: against the path difference N (λ₀ = 700 nm),
the peak after the pulses (of its value at N = 0), the centre along the axis and the FWHM along the axis, and the profiles
along the axis (of the peak at N = 0), for all pairs (fringe crests), the cross pairs alone and the time-integrated rate.

    python scripts/export_pulse_delay_dashboard.py -> dashboard/cambaliza/public/data/pulse_delay.json
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import numpy as np

from cambaliza2000_pulses_sweep import fwhm

D = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'cambaliza2000', 'pulses', 'delay_norm')
R = np.load(os.path.join(D, 'delay_norm.npz'))
DEST = os.path.join(os.path.dirname(__file__), '..', 'dashboard', 'cambaliza', 'public', 'data', 'pulse_delay.json')
TH = {'0': 0, 'pi2': 90, 'pi': 180}
STEP = 3                                                            # every third z sample for the profiles (0.06 µm)
NS, Z = R['ns'], R['zs']
r4 = lambda a: [round(float(v), 4) for v in a]
nul = lambda v: None if not np.isfinite(v) else round(float(v), 4)
i0 = int(np.argmin(np.abs(NS)))
met, prof = {}, {}
for sig in ('2ce', '2pe'):
    for tk, deg in TH.items():
        for tau in R['taus']:
            k = f'{sig.upper()}|{deg}|{tau:g}'
            for q in ('all', 'one', 'rate'):
                A = R[f'{sig}_{tk}_{tau:g}_{q}']
                ref = A[i0].max()
                met[f'{k}|{q}'] = dict(peak=r4(A.max(1) / ref), centre=[nul(c) for c in (A * Z).sum(1) / A.sum(1)],
                                       fwhm=[nul(fwhm(Z, a)) for a in A])
                for j, n in enumerate(NS):
                    prof[f'{k}|{q}|{n:g}'] = r4(A[j, ::STEP] / ref)
out = dict(ns=r4(NS), taus=[float(t) for t in R['taus']], lam0=0.7, z=r4(Z[::STEP]), met=met, prof=prof)
json.dump(out, open(DEST, 'w'), separators=(',', ':'))
print(f'{len(met)} metric sets, {len(prof)} profiles -> {DEST} ({os.path.getsize(DEST) / 1e6:.2f} MB)')
