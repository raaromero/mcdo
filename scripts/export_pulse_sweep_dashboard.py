r"""Pulse-length sweep (cambaliza2000_pulses_sweep.py) to the dashboard: one row of metrics per signal, θ, cut and τ, and
the profiles after the pulses.

Metrics (cut = along the axis z, or across x): FWHM of the continuous-beam profile, of the 350-nm pairs across the two
pulses alone (|2A₁₂|²), of all pairs (central fringe, fringe crests, fringes averaged), and of the time-integrated rate
(a dye that loses phase fast: ∫I₁I₂ dt for 2CE, ∫|E₁ + E₂|⁴ dt for 2PE); peak of all pairs over the cross pairs; peak of
the pairs within one pulse over the cross pairs; fringe depth; spectral FWHM Δν = 441/τ THz.

    python scripts/export_pulse_sweep_dashboard.py -> dashboard/cambaliza/public/data/pulse_sweep.json
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import numpy as np

from cambaliza2000_pulses_sweep import fwhm, depth, OUT

R = np.load(os.path.join(OUT, 'sweep.npz'))
DEST = os.path.join(os.path.dirname(__file__), '..', 'dashboard', 'cambaliza', 'public', 'data', 'pulse_sweep.json')
TH = {'0': 0, 'pi2': 90, 'pi': 180}
r4 = lambda a: [round(float(v), 4) for v in a]
rows, prof = [], {}
for sig, pre in (('2CE', ''), ('2PE', 'pe_')):
    for tk, deg in TH.items():
        for cut in ('z', 'x'):
            s = R['zs'] if cut == 'z' else R['xs']
            step = 2                                                    # half the samples for the profiles
            cw = R[f'{pre}{tk}_{cut}_cw']
            prof[f'{sig}|{deg}|{cut}|cw'] = r4(cw[::step])
            for tau in R['taus']:
                g = lambda q: R[f'{pre}{tk}_{cut}_{tau:g}_fin_{q}']
                one, allp, crest, mean, single, rate = (g(q) for q in ('one', 'all', 'crest', 'mean', 'single', 'rate'))
                f = lambda y: None if not np.isfinite(w := fwhm(s, y)) else round(float(w), 4)
                rows.append(dict(sig=sig, th=deg, cut=cut, tau=float(tau), dnu=round(441 / tau, 2),
                                 cw=f(cw), one=f(one), all=f(allp), crest=f(crest), mean=f(mean), rate=f(rate),
                                 gain=round(float(allp.max() / one.max()), 5), same=round(float(single.max() / one.max()), 7),
                                 depth=round(float(depth(one, crest)), 4)))
                k = f'{sig}|{deg}|{cut}|{tau:g}'
                for q, y in (('one', one), ('all', allp), ('rate', rate)):
                    prof[f'{k}|{q}'] = r4((y / y.max())[::step])
out = dict(taus=[float(t) for t in R['taus']], z=r4(R['zs'][::2]), x=r4(R['xs'][::2]), rows=rows, prof=prof)
json.dump(out, open(DEST, 'w'), separators=(',', ':'))
print(f'{len(rows)} rows, {len(prof)} profiles -> {DEST} ({os.path.getsize(DEST) / 1e6:.2f} MB)')
