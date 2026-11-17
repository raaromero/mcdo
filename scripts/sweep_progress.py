r"""Progress page of the pulse NA sweep (run_all.sh, run_queue.sh, then run_queue2.sh): every step, its NAs, what is done and running.

Reads the logs of cambaliza2000_pulses_na_sweep.py ("... NA <na> <sig> <θ> <cut>: <s> s" per finished cut, "saved NA <na>"
per finished NA) and writes a page that reloads itself every 30 s.

    python scripts/sweep_progress.py [--loop]    -> output/08_two_color/cambaliza2000/pulses/na_sweep/progress.html
"""
import html
import os
import re
import sys
import time
from datetime import datetime

D = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'cambaliza2000', 'pulses', 'na_sweep')
N = {'air': 1.0, 'water': 1.33, 'oil': 1.515}
AIR = '0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9'
WATER = '0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2'
EXTRA, DL = '4,70,150,300,1000', '0.25,0.5,0.75,1,1.5,2,3'
ALL_TAUS = '4–1000 fs (15 widths)'
LONG, DT = '2000, 3000, 5000 fs', '5, 10, 20, 30, 50, 100 fs'
HALF = '0.15,0.25,0.35,0.45,0.55,0.65,0.75,0.85'
DL2 = ','.join(f'{0.1 * i:g}' for i in range(1, 31))
# (log, what it computes, model, medium, NAs, pulse widths, delays, ε, α)
PLAN = [
    ('log_rw_air.txt', 'High NA, vector model in air', 'rw', 'air', AIR, '5–500 fs (10 widths)', '', 0, 0),
    ('log_rw_water.txt', 'High NA, vector model in water', 'rw', 'water', WATER, ALL_TAUS, '', 0, 0),
    ('log_paraxial_water.txt', 'Scalar model in water', 'paraxial', 'water', WATER, ALL_TAUS, '', 0, 0),
    ('log_paraxial_air_na0.1.txt', 'Scalar model in air at NA 0.1', 'paraxial', 'air', '0.1', ALL_TAUS, '', 0, 0),
    ('log_q01.txt', 'Extra pulse widths, vector model in air', 'rw', 'air', AIR, EXTRA + ' fs', '', 0, 0),
    ('log_q02.txt', 'Extra pulse widths, scalar model in air', 'paraxial', 'air', AIR[4:], EXTRA + ' fs', '', 0, 0),
    ('log_q03.txt', 'NA 0.95 in air, vector model', 'rw', 'air', '0.95', ALL_TAUS, '', 0, 0),
    ('log_q04.txt', 'NA 0.95 in air, scalar model', 'paraxial', 'air', '0.95', ALL_TAUS, '', 0, 0),
    ('log_q05.txt', 'NA 1.25 in water, vector model', 'rw', 'water', '1.25', ALL_TAUS, '', 0, 0),
    ('log_q06.txt', 'NA 1.25 in water, scalar model', 'paraxial', 'water', '1.25', ALL_TAUS, '', 0, 0),
    ('log_q07.txt', 'Oil immersion, vector model', 'rw', 'oil', '0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.45', ALL_TAUS, '', 0, 0),
    ('log_q08.txt', 'Oil immersion, scalar model', 'paraxial', 'oil', '0.5,0.7,0.9,1.1,1.3,1.4', ALL_TAUS, '', 0, 0),
    ('log_q09.txt', 'Delay, vector model in air', 'rw', 'air', '0.3,0.5,0.7,0.9', '10, 20, 50, 100 fs', DL, 0, 0),
    ('log_q10.txt', 'Delay, scalar model in air', 'paraxial', 'air', '0.3,0.5', '10, 20, 50, 100 fs', DL, 0, 0),
    ('log_q11.txt', 'Delay, vector model in water', 'rw', 'water', '0.9,1.2', '10, 20, 50, 100 fs', DL, 0, 0),
    ('log_q12.txt', 'Gaussian input (α = 4), vector model in air', 'rw', 'air', '0.3,0.5,0.7,0.9,0.95', ALL_TAUS, '', 0, 4),
    ('log_q13.txt', 'Gaussian input (α = 4), vector model in water', 'rw', 'water', '0.7,0.9,1.1,1.2', ALL_TAUS, '', 0, 4),
    ('log_q14.txt', 'Gaussian input (α = 4), vector model in oil', 'rw', 'oil', '1.0,1.2,1.4', ALL_TAUS, '', 0, 4),
    ('log_q15.txt', 'Gaussian input (α = 4), scalar model in air', 'paraxial', 'air', '0.3,0.5', ALL_TAUS, '', 0, 4),
    ('log_q16.txt', 'Annular pupil ε = 0.5, vector model in air', 'rw', 'air', '0.3,0.5,0.7,0.9', ALL_TAUS, '', 0.5, 0),
    ('log_q17.txt', 'Annular pupil ε = 0.9, vector model in air', 'rw', 'air', '0.3,0.5,0.7,0.9', ALL_TAUS, '', 0.9, 0),
    ('log_q18.txt', 'Annular pupil ε = 0.5, scalar model in air', 'paraxial', 'air', '0.5', ALL_TAUS, '', 0.5, 0),
    ('log_q19.txt', 'Annular pupil ε = 0.9, scalar model in air', 'paraxial', 'air', '0.5', ALL_TAUS, '', 0.9, 0),
    ('log_q20.txt', 'Annular pupil ε = 0.99, scalar model in air', 'paraxial', 'air', '0.5', ALL_TAUS, '', 0.99, 0),
    ('log_q21.txt', 'Annular pupil ε = 0.99, vector model in air', 'rw', 'air', '0.5,0.9', ALL_TAUS, '', 0.99, 0),
    ('log_plot.txt', 'Figures and dashboard data', '', '', '', '', '', 0, 0),
    # second queue (run_queue2.sh)
    ('log_r01.txt', 'Pulses of 2000 to 5000 fs, vector model in air', 'rw', 'air', '0.1,0.2', LONG, '', 0, 0),
    ('log_r02.txt', 'Pulses of 2000 to 5000 fs, scalar model in air', 'paraxial', 'air', '0.1,0.2', LONG, '', 0, 0),
    ('log_r03.txt', 'NA in steps of 0.05, vector model in air', 'rw', 'air', HALF, ALL_TAUS, '', 0, 0),
    ('log_r04.txt', 'NA in steps of 0.05, scalar model in air', 'paraxial', 'air', HALF, ALL_TAUS, '', 0, 0),
    ('log_r05.txt', 'More NAs, Gaussian input, vector model in air', 'rw', 'air', '0.1,0.2,0.4,0.6,0.8', ALL_TAUS, '', 0, 4),
    ('log_r06.txt', 'More NAs, Gaussian input, scalar model in air', 'paraxial', 'air', '0.1,0.2,0.4,0.6,0.7,0.8,0.9,0.95', ALL_TAUS, '', 0, 4),
    ('log_r07.txt', 'More NAs, Gaussian input, vector model in water', 'rw', 'water', '0.5,0.6,0.8,1.0,1.25', ALL_TAUS, '', 0, 4),
    ('log_r08.txt', 'More NAs, Gaussian input, vector model in oil', 'rw', 'oil', '0.5,0.6,0.7,0.8,0.9,1.1,1.3,1.45', ALL_TAUS, '', 0, 4),
    ('log_r09.txt', 'More NAs, ε = 0.5, vector model in air', 'rw', 'air', '0.2,0.4,0.6,0.8,0.95', ALL_TAUS, '', 0.5, 0),
    ('log_r10.txt', 'More NAs, ε = 0.9, vector model in air', 'rw', 'air', '0.2,0.4,0.6,0.8,0.95', ALL_TAUS, '', 0.9, 0),
    ('log_r11.txt', 'More NAs, ε = 0.5, scalar model in air', 'paraxial', 'air', '0.2,0.3,0.4,0.6,0.7,0.8,0.9,0.95', ALL_TAUS, '', 0.5, 0),
    ('log_r12.txt', 'More NAs, ε = 0.9, scalar model in air', 'paraxial', 'air', '0.2,0.3,0.4,0.6,0.7,0.8,0.9,0.95', ALL_TAUS, '', 0.9, 0),
    ('log_r13.txt', 'More NAs, ε = 0.99, vector model in air', 'rw', 'air', '0.6,0.7,0.8,0.95', ALL_TAUS, '', 0.99, 0),
    ('log_r14.txt', 'More NAs, ε = 0.99, scalar model in air', 'paraxial', 'air', '0.6,0.7,0.8,0.9,0.95', ALL_TAUS, '', 0.99, 0),
    ('log_r15.txt', 'Delay in steps of 0.1τ, vector model in air', 'rw', 'air', '0.3,0.5,0.7,0.9', DT, DL2, 0, 0),
    ('log_r16.txt', 'Delay in steps of 0.1τ, scalar model in air', 'paraxial', 'air', '0.3,0.5', DT, DL2, 0, 0),
    ('log_r17.txt', 'Delay in steps of 0.1τ, vector model in water', 'rw', 'water', '0.9,1.2', DT, DL2, 0, 0),
    ('log_r18.txt', 'Delay in steps of 0.1τ, Gaussian input', 'rw', 'air', '0.5,0.9', DT, DL2, 0, 4),
    ('log_r19.txt', 'Delay in steps of 0.1τ, ε = 0.5', 'rw', 'air', '0.5,0.9', DT, DL2, 0.5, 0),
    ('log_r20.txt', 'Delay in steps of 0.1τ, ε = 0.9', 'rw', 'air', '0.5,0.9', DT, DL2, 0.9, 0),
    ('log_samples.txt', 'Samples recomputed the long way', '', '', '', '', '', 0, 0),
    ('log_plot2.txt', 'Figures and dashboard data', '', '', '', '', '', 0, 0),
]
CUTS = [(s, t, c) for s in ('2ce', '2pe') for t in ('0', 'pi2', 'pi') for c in ('z', 'x')]
WORKERS = 7


TAU_LISTS = {'long': (2000, 3000, 5000), 'delay2': (5, 10, 20, 30, 50, 100), '10': (5, 7, 10, 15, 20, 30, 50, 100, 200, 500), 'extra': (4, 70, 150, 300, 1000), 'delay': (10, 20, 50, 100),
             'all': (4, 5, 7, 10, 15, 20, 30, 50, 70, 100, 150, 200, 300, 500, 1000)}


def tau_list(taus):
    return TAU_LISTS['long' if taus == LONG else 'delay2' if taus == DT else 'delay' if taus.startswith('10, 20') else 'extra' if taus.startswith(EXTRA) else
                     '10' if '10 widths' in taus else 'all']


def size(step, na, cut):
    """Points along the cut and number of pulse runs (each delay is one more run)."""
    log, what, model, medium, nas, taus, dl, eps, apod = step
    zspan = 5 * N[medium] * (0.5 / na) ** 2 / ((1 - eps ** 2) if eps else 1)
    pts = 2 * int(50 * zspan) + 1 if cut == 'z' else 301
    return pts, len(tau_list(taus)) * ((len(dl.split(',')) + 1) if dl else 1)


FIT = {}
SPEEDUP = 8                     # current code over tables, median of the sweep checks in fast_check.txt (5 to 25)


def cost(step, na, cut):
    """Seconds for one cut: t = r · runs · pts^k, with r and k fitted per model to the cuts already finished."""
    pts, runs = size(step, na, cut)
    if step[0].startswith(('log_q', 'log_r')):                                 # the queue runs on the tables
        if step[2] + '_fast' in FIT:
            r, k = FIT[step[2] + '_fast']
            return r * runs * pts ** k
        r, k = FIT.get(step[2], FIT.get('rw', (1e-3, 1.5)))
        return r * runs * pts ** k / SPEEDUP
    r, k = FIT.get(step[2], FIT.get('rw', (1e-3, 1.5)))
    return r * runs * pts ** k


def rates():
    """Fit log(t / runs) = log r + k log(pts) per model on the finished cuts; the rate returned is 1 (cost is seconds)."""
    import numpy as np
    pts, t = {}, {}
    for step in PLAN:
        f = os.path.join(D, step[0])
        if not step[2] or not os.path.exists(f):
            continue
        for na, sig, tk, cut, sec in re.findall(r'NA ([\d.]+) (2ce|2pe) (0|pi2|pi) (z|x): (\d+) s', open(f).read()):
            p_, runs = size(step, float(na), cut)
            m = step[2] + ('_fast' if step[0].startswith(('log_q', 'log_r')) else '')
            pts.setdefault(m, []).append(p_); t.setdefault(m, []).append(max(int(sec), 1) / runs)
    for m in pts:
        if len(set(pts[m])) < 3:                                    # too few sizes for a slope
            continue
        k, lr = np.polyfit(np.log(pts[m]), np.log(t[m]), 1)
        FIT[m] = (float(np.exp(lr)), float(k))
    if 'rw' in FIT and 'paraxial' not in FIT:
        FIT['paraxial'] = (FIT['rw'][0] / 3, FIT['rw'][1])
    return {'rw': 1.0, 'paraxial': 1.0}


def cuts_for(na, medium):
    return [k for k in CUTS if not (k[1] == 'pi2' and na > N[medium] * 0.7071 + 1e-9)]


def status(step):
    log, what, model, medium, nas, taus, dl, eps, apod = step
    f = os.path.join(D, log)
    text = open(f).read() if os.path.exists(f) else ''
    END = {'log_plot.txt': 'QUEUE DONE', 'log_samples.txt': 'SAMPLES DONE', 'log_plot2.txt': 'QUEUE2 DONE'}
    if log in END:
        st = 'done' if END[log] in text else ('running' if text else 'waiting')
        return st, [], 0, 0, None, []
    done_na = {float(m) for m in re.findall(r'saved NA ([\d.]+)', text)}
    lines = re.findall(r'NA ([\d.]+) (2ce|2pe) (0|pi2|pi) (z|x): (\d+) s', text)
    per = {}
    for na, *_ , sec in lines:
        per.setdefault(float(na), []).append(int(sec))
    cells, tot, got = [], 0, 0
    fin = {(float(a), c) for a, _, _, c, _ in re.findall(r'NA ([\d.]+) (2ce|2pe) (0|pi2|pi) (z|x): (\d+) s', text)}
    step_left = []                                                        # costs of the cuts still to do
    for na in (float(a) for a in nas.split(',')):
        need = len(cuts_for(na, medium))
        have = need if na in done_na else len(per.get(na, []))
        if na not in done_na:
            todo = cuts_for(na, medium)
            nz = sum(1 for k in todo if k[2] == 'z') - sum(1 for a, c in fin if a == na and c == 'z')
            nx = sum(1 for k in todo if k[2] == 'x') - sum(1 for a, c in fin if a == na and c == 'x')
            step_left += [cost(step, na, 'z')] * max(nz, 0) + [cost(step, na, 'x')] * max(nx, 0)
        tot += need; got += have
        cells.append((na, have, need, 'done' if na in done_na else ('running' if have or text else 'waiting')))
    finished = 'STEP' in text or 'ALL DONE' in text or (done_na and len(done_na) == len(cells))
    st = 'done' if finished else ('running' if text else 'waiting')
    if st == 'running':                                                  # NAs not started yet in a running step
        cells = [(na, h, n, 'running' if (h and s != 'done') else s if s == 'done' else 'waiting') for na, h, n, s in cells]
    mt = os.path.getmtime(f) if text else None
    return st, cells, got, tot, mt, ([] if st == 'done' else step_left)


def wall(costs, rate):
    """Wall time of a set of cuts on WORKERS processes: the larger of the total over the workers and the longest cut."""
    return max(sum(costs) / WORKERS, max(costs, default=0)) * rate


def page():
    rows, n_done, n_all = [], 0, len(PLAN)
    R, clock = rates(), time.time()
    for step in PLAN:
        st, cells, got, tot, mt, left = status(step)
        if st == 'running' and mt:                                         # the cuts in flight have run since the last line
            clock = max(clock, time.time())
        dur = wall(left, R.get(step[2], 0)) if left else ({'log_plot.txt': 300, 'log_plot2.txt': 300, 'log_samples.txt': 2400}.get(step[0], 0) if st != 'done' else 0)
        clock += dur
        eta = '' if st == 'done' else f'about {dur / 3600:.1f} h, done near {datetime.fromtimestamp(clock):%a %H:%M}'

        n_done += st == 'done'
        log, what, model, medium, nas, taus, dl, eps, apod = step
        bits = ''.join(f'<span class="na {s}" title="NA {na:g}: {h} of {n} cuts">{na:g}<i style="width:{100 * h / n:.0f}%"></i></span>'
                       for na, h, n, s in cells)
        detail = ', '.join(x for x in [taus, f'delays {dl} τ' if dl else '', f'ε = {eps:g}' if eps else '',
                                        f'Gaussian α = {apod:g}' if apod else ''] if x)
        frac = f'{got} of {tot} cuts' if tot else ''
        last = f'last update {datetime.fromtimestamp(mt):%H:%M}' if mt else ''
        rows.append(f'<tr class="{st}"><td><span class="dot {st}"></span>{html.escape(st)}</td>'
                    f'<td><b>{html.escape(what)}</b><div class="sub">{html.escape(detail)}</div></td>'
                    f'<td class="nas">{bits}</td><td class="sub">{frac}<br>{last}<br><b>{eta}</b></td></tr>')
    now = datetime.now()
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta http-equiv="refresh" content="30">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Pulse sweep progress</title><style>
:root {{ --bg:#fafaf8; --ink:#1d2433; --mut:#6b7280; --line:#e5e7eb; --done:#2e9d5b; --run:#e8a33d; --wait:#c7ccd4; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#14171c; --ink:#e8eaed; --mut:#9aa1ab; --line:#2a2f37; --wait:#3a404a; }} }}
body {{ margin:0; padding:24px 16px; background:var(--bg); color:var(--ink); font:15px/1.45 -apple-system, system-ui, sans-serif; }}
h1 {{ font-size:22px; margin:0 0 4px; }} .sub {{ color:var(--mut); font-size:13px; }}
.bar {{ height:10px; background:var(--wait); border-radius:5px; overflow:hidden; margin:14px 0 22px; max-width:760px; }}
.bar i {{ display:block; height:100%; background:var(--done); }}
table {{ border-collapse:collapse; width:100%; max-width:1200px; }} td {{ border-top:1px solid var(--line); padding:9px 10px; vertical-align:top; }}
tr.waiting td {{ opacity:.6; }} .dot {{ display:inline-block; width:10px; height:10px; border-radius:50%; margin-right:6px; }}
.dot.done {{ background:var(--done); }} .dot.running {{ background:var(--run); }} .dot.waiting {{ background:var(--wait); }}
.na {{ position:relative; display:inline-block; min-width:38px; text-align:center; font-size:12px; padding:2px 4px; margin:2px;
      border-radius:4px; border:1px solid var(--line); overflow:hidden; }}
.na i {{ position:absolute; left:0; bottom:0; height:3px; background:var(--run); }}
.na.done {{ background:var(--done); color:#fff; border-color:var(--done); }} .na.done i {{ display:none; }}
.na.running {{ border-color:var(--run); }}
</style></head><body>
<h1>Pulse sweep progress</h1>
<div class="sub"><b>Everything done near {datetime.fromtimestamp(clock):%a %H:%M} (estimate from the cuts finished so far, {WORKERS} workers).</b> {n_done} of {n_all} steps done. The page reloads every 30 s; updated {now:%Y-%m-%d %H:%M:%S}. Each box is
one NA: green when saved, orange outline while its cuts run (the thin bar is the share of cuts done), grey while waiting.</div>
<div class="bar"><i style="width:{100 * n_done / n_all:.0f}%"></i></div>
<table>{''.join(rows)}</table></body></html>'''


def write():
    open(os.path.join(D, 'progress.html'), 'w').write(page())


if __name__ == '__main__':
    write()
    while '--loop' in sys.argv:
        time.sleep(30)
        write()
