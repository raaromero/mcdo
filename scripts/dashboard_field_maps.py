"""Annular pupils with pulsed sources: a small web application.

Each parameter gets its own control, so one can be stepped while the others are
held fixed. That is how every comparison in this work is made, and a single
dropdown over all configurations cannot express it.

The page shows the two-dimensional field, the transverse and axial profiles
against the unobstructed reference at the same aperture, the measured
quantities for the selected configuration, and the equations the whole study
rests on.

Fields come from the atlas. Nothing is recomputed here.

    python scripts/dashboard_field_maps.py
    -> output/03_annular/field_map_dashboard.html
"""

import base64
import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np

ROOT = os.path.join(os.path.dirname(__file__), '..')
SRC = os.path.join(ROOT, 'output', 'atlas', 'annular_grid')
BASE = os.path.join(ROOT, 'output', '03_annular', 'annular_baseline.npz')
OUT = os.path.join(ROOT, 'output', '03_annular', 'field_map_dashboard.html')

NA_VALS = [0.1, 0.8, 1.2]
IN_VALS = [('uniform', 'Uniform'), ('gaussian', 'Gaussian, α = 4')]
ALPHA_VALS = [('0.0', 'Uniform'), ('1.0', 'α = 1'), ('2.0', 'α = 2'),
              ('4.0', 'α = 4'), ('8.0', 'α = 8')]
TRUNC = os.path.join(ROOT, 'output', 'atlas', 'truncation_grid')
EPS_VALS = [0.0, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99]
TAU_VALS = [('cw', 'Continuous wave'), ('2fs', '2 fs'), ('1fs', '1 fs')]
PULSED = os.path.join(ROOT, 'output', 'atlas', 'pulsed_annular')
PULSED_IL = os.path.join(ROOT, 'output', 'atlas', 'pulsed_illumination')
PULSED_GRID = os.path.join(ROOT, 'output', 'atlas', 'pulsed_grid')
PULSED_SWEEP = os.path.join(ROOT, 'output', '05_pulsed_pupils',
                            'pulsed_annular_grid.npz')
APERTURE_SWEEP = os.path.join(ROOT, 'output', '05_pulsed_pupils',
                              'pulsed_annular_apertures.npz')
TRUNC_SWEEP = os.path.join(ROOT, 'output', '02_na_apodization',
                           'truncation_sweep.npz')
STRIDE = 4          # the browser does not need the full grid
FLOOR = 1e-4



def _pack(Is):
    """Map as base64 bytes: one byte per point, in fiftieths of a decade.

    The maps are 97% of this page. Written as JSON numbers they cost about six
    bytes a point; the values span only -4 to 0 decades, so a single byte at
    1/50 of a decade holds them exactly as quantized, and base64 brings the
    page from 17 MB to under 5 MB with no loss of resolution.
    """
    q = np.clip(np.rint(50.0 * np.log10(np.maximum(Is, FLOOR))), -200, 0)
    b = (q + 200).astype(np.uint8).tobytes()
    return dict(b=base64.b64encode(b).decode('ascii'),
                r=int(Is.shape[0]), c=int(Is.shape[1]))


def _key(na, inp, eps, tau='cw'):
    return f"{na}|{inp}|{eps}|{tau}"


def _collect():
    """Field, profiles and measured quantities for every configuration."""
    data, meas = {}, {}
    if os.path.exists(BASE):
        b = np.load(BASE, allow_pickle=True)
        names = {'uniform': 'uniform',
                 'gaussian': 'Gaussian, alpha = 4'}
        for i in range(len(b['eps'])):
            for short, full in names.items():
                if str(b['input'][i]) == full:
                    meas[_key(float(b['na'][i]), short, float(b['eps'][i]))] = dict(
                        width=float(b['width_nm'][i]), depth=float(b['depth_um'][i]),
                        gain=float(b['gain'][i]), peak=float(b['peak'][i]),
                        transmission=float(b['transmission'][i]))

    # the alpha sweep, whose cells had maps but no numbers beside them
    if os.path.exists(TRUNC_SWEEP):
        t = np.load(TRUNC_SWEEP, allow_pickle=True)
        for i in range(len(t['eps'])):
            meas[_key(0.8, f"alpha{float(t['alpha_t'][i]):g}.0"
                      if float(t['alpha_t'][i]) == int(t['alpha_t'][i])
                      else f"alpha{float(t['alpha_t'][i])}",
                      float(t['eps'][i]))] = dict(
                width=float(t['width'][i]), depth=float(t['depth'][i]),
                gain=float(t['gain'][i]),
                transmission=float(t['transmission'][i]),
                peak=float('nan'))

    # measured quantities for the pulsed configurations, from the sweeps that
    # produced them. Transmission is geometric - it depends on the pupil, not
    # on the pulse - so the continuous-wave value carries over unchanged.
    for path, na_of in ((PULSED_SWEEP, None), (APERTURE_SWEEP, None)):
        if not os.path.exists(path):
            continue
        b = np.load(path, allow_pickle=True)
        names = [str(v) for v in b['input']]
        taus = [str(v) for v in b['tau']]
        tag = {'continuous wave': 'cw', '2 fs': '2fs', '1 fs': '1fs'}
        for i in range(len(b['eps'])):
            short = 'uniform' if names[i] == 'uniform' else 'gaussian'
            na = float(b['na'][i]) if 'na' in b.files else 0.8
            k = _key(na, short, float(b['eps'][i]), tag.get(taus[i], taus[i]))
            if k in meas:
                continue
            cw = meas.get(_key(na, short, float(b['eps'][i])))
            meas[k] = dict(
                width=float(b['width_nm'][i]), depth=float(b['depth_um'][i]),
                gain=float(b['gain'][i]), peak=float(b['peak'][i]),
                transmission=(cw or {}).get('transmission', float('nan')))

    for na in NA_VALS:
        for inp, _lab in IN_VALS:
            for eps in EPS_VALS:
                stem = (f"na{str(na).replace('.', 'p')}_{inp}"
                        f"_eps{str(eps).replace('.', 'p')}")
                f = os.path.join(SRC, f'field_{stem}.npz')
                if not os.path.exists(f):
                    continue
                d = np.load(f)
                I = d['intensity'] / d['intensity'].max()
                h, v = d['h'][::STRIDE], d['v'][::STRIDE]
                Is = I[::STRIDE, ::STRIDE]
                iz, ir = int(np.argmin(np.abs(v))), int(np.argmin(np.abs(h)))
                tr, ax = Is[iz, :], Is[:, ir]
                entry = dict(
                    h=[round(x, 4) for x in h.tolist()],
                    v=[round(x, 4) for x in v.tolist()],
                    z=_pack(Is),
                    tr=[round(float(q), 5) for q in (tr / tr.max())],
                    ax=[round(float(q), 5) for q in (ax / ax.max())])
                data[_key(na, inp, eps)] = entry

    # alpha swept at numerical aperture 0.8, continuous wave
    for at, _lab in ALPHA_VALS:
        for eps in EPS_VALS:
            f = os.path.join(TRUNC, f"field_at{at.replace('.', 'p')}"
                                    f"_eps{str(eps).replace('.', 'p')}.npz")
            if not os.path.exists(f):
                continue
            d = np.load(f)
            I = d['intensity'] / d['intensity'].max()
            h, v = d['h'][::STRIDE], d['v'][::STRIDE]
            Is = I[::STRIDE, ::STRIDE]
            iz, ir = int(np.argmin(np.abs(v))), int(np.argmin(np.abs(h)))
            tr, ax = Is[iz, :], Is[:, ir]
            data[_key(0.8, f'alpha{at}', eps)] = dict(
                h=[round(x, 4) for x in h.tolist()],
                v=[round(x, 4) for x in v.tolist()],
                z=_pack(Is),
                tr=[round(float(q), 5) for q in (tr / tr.max())],
                ax=[round(float(q), 5) for q in (ax / ax.max())])

    # both illuminations, every ratio, continuous wave and 1 fs
    for inp in ('uniform', 'gaussian'):
        for eps in EPS_VALS:
            for tau in ('cw', '1fs'):
                f = os.path.join(
                    PULSED_IL,
                    f"field_{inp}_eps{str(eps).replace('.', 'p')}_{tau}.npz")
                if not os.path.exists(f):
                    continue
                d = np.load(f)
                I = d['intensity'] / d['intensity'].max()
                h, v = d['h'][::STRIDE], d['v'][::STRIDE]
                Is = I[::STRIDE, ::STRIDE]
                iz, ir = int(np.argmin(np.abs(v))), int(np.argmin(np.abs(h)))
                tr, ax = Is[iz, :], Is[:, ir]
                data[_key(0.8, inp, eps, tau)] = dict(
                    h=[round(x, 4) for x in h.tolist()],
                    v=[round(x, 4) for x in v.tolist()],
                    z=_pack(Is),
                    tr=[round(float(q), 5) for q in (tr / tr.max())],
                    ax=[round(float(q), 5) for q in (ax / ax.max())])

    # the gap-filling pass: 2 fs at aperture 0.8, and both pulse durations at
    # apertures 0.1 and 1.2, for both illuminations and every ratio
    for na in NA_VALS:
        for inp in ('uniform', 'gaussian'):
            for eps in EPS_VALS:
                for tau in ('2fs', '1fs'):
                    f = os.path.join(
                        PULSED_GRID,
                        f"field_na{str(na).replace('.', 'p')}_{inp}"
                        f"_eps{str(eps).replace('.', 'p')}_{tau}.npz")
                    if not os.path.exists(f):
                        continue
                    d = np.load(f)
                    I = d['intensity'] / d['intensity'].max()
                    h, v = d['h'][::STRIDE], d['v'][::STRIDE]
                    Is = I[::STRIDE, ::STRIDE]
                    iz, ir = int(np.argmin(np.abs(v))), int(np.argmin(np.abs(h)))
                    tr, ax = Is[iz, :], Is[:, ir]
                    data[_key(na, inp, eps, tau)] = dict(
                        h=[round(x, 4) for x in h.tolist()],
                        v=[round(x, 4) for x in v.tolist()],
                        z=_pack(Is),
                        tr=[round(float(q), 5) for q in (tr / tr.max())],
                        ax=[round(float(q), 5) for q in (ax / ax.max())])

    # pulsed fields exist only at numerical aperture 0.8, uniform, at two ratios
    for eps in (0.5, 0.9):
        for tau, _lab in TAU_VALS:
            f = os.path.join(
                PULSED, f"field_eps{str(eps).replace('.', 'p')}_{tau}.npz")
            if not os.path.exists(f):
                continue
            d = np.load(f)
            I = d['intensity'] / d['intensity'].max()
            h, v = d['h'][::STRIDE], d['v'][::STRIDE]
            Is = I[::STRIDE, ::STRIDE]
            iz, ir = int(np.argmin(np.abs(v))), int(np.argmin(np.abs(h)))
            tr, ax = Is[iz, :], Is[:, ir]
            data[_key(0.8, 'uniform', eps, tau)] = dict(
                h=[round(x, 4) for x in h.tolist()],
                v=[round(x, 4) for x in v.tolist()],
                z=_pack(Is),
                tr=[round(float(q), 5) for q in (tr / tr.max())],
                ax=[round(float(q), 5) for q in (ax / ax.max())])
    return data, meas


def main():
    if not glob.glob(os.path.join(SRC, 'field_*.npz')):
        raise SystemExit(f"no fields in {SRC} - run scripts/config_atlas.py first")
    data, meas = _collect()

    seg = lambda name, items, active: "".join(
        f'<button class="seg{" on" if v == active else ""}" '
        f'data-group="{name}" data-value="{v}">{lab}</button>'
        for v, lab in items)

    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Annular pupils with pulsed sources</title>
<script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
<style>
:root {{
  --bg:#f5f5f7; --card:#ffffff; --ink:#1d1d1f; --sub:#6e6e73;
  --line:#d2d2d7; --tint:#0071e3; --radius:14px;
}}
@media (prefers-color-scheme: dark) {{
  :root {{ --bg:#000000; --card:#1c1c1e; --ink:#f5f5f7; --sub:#98989d;
           --line:#38383a; --tint:#0a84ff; }}
}}
* {{ box-sizing:border-box; }}
body {{
  margin:0; background:var(--bg); color:var(--ink);
  font:15px/1.5 -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", sans-serif;
  -webkit-font-smoothing:antialiased;
}}
header {{ padding:28px 32px 12px; }}
h1 {{ font-size:26px; font-weight:600; letter-spacing:-0.02em; margin:0; }}
.sub {{ color:var(--sub); font-size:14px; margin-top:4px; }}
main {{ padding:8px 32px 40px; display:grid; gap:18px;
        grid-template-columns:minmax(0,1.35fr) minmax(320px,1fr); }}
.card {{ background:var(--card); border-radius:var(--radius); padding:18px 20px;
         border:1px solid var(--line); }}
.controls {{ grid-column:1 / -1; display:flex; flex-wrap:wrap; gap:22px; align-items:flex-end; }}
.group {{ display:flex; flex-direction:column; gap:7px; }}
.glabel {{ font-size:12px; font-weight:600; color:var(--sub);
           text-transform:uppercase; letter-spacing:0.06em; }}
.segmented {{ display:inline-flex; background:rgba(120,120,128,0.12);
              border-radius:9px; padding:2px; }}
.seg {{ appearance:none; border:0; background:transparent; color:var(--ink);
        font:inherit; font-size:14px; padding:6px 15px; border-radius:7px;
        cursor:pointer; transition:background .15s, box-shadow .15s; white-space:nowrap; }}
.seg.on {{ background:var(--card); box-shadow:0 1px 3px rgba(0,0,0,.14); font-weight:590; }}
.seg.off {{ opacity:.3; cursor:not-allowed; }}
.seg:not(.on):hover {{ background:rgba(120,120,128,0.10); }}
.stats {{ display:grid; grid-template-columns:repeat(2,1fr); gap:12px; margin-bottom:16px; }}
.stat {{ background:rgba(120,120,128,0.10); border-radius:10px; padding:11px 13px; }}
.sv {{ font-size:21px; font-weight:600; letter-spacing:-0.02em;
       font-variant-numeric:tabular-nums; }}
.sl {{ font-size:11.5px; color:var(--sub); margin-top:2px; }}
h2 {{ font-size:15px; font-weight:600; margin:0 0 10px; letter-spacing:-0.01em; }}
@media (max-width:1080px) {{ main {{ grid-template-columns:1fr; }} }}
</style></head><body>
<header>
  <h1>Annular pupils with pulsed sources</h1>
  <div class="sub">Annular pupils, center wavelength 750 nm, refractive index 1.3, continuous wave</div>
</header>
<main>
  <div class="card controls">
    <div class="group"><div class="glabel">Numerical aperture</div>
      <div class="segmented">{seg('na', [(str(x), str(x)) for x in NA_VALS], '0.8')}</div></div>
    <div class="group"><div class="glabel">Illumination</div>
      <div class="segmented">{seg('inp', IN_VALS, 'uniform')}</div></div>
    <div class="group"><div class="glabel">Alpha sweep, numerical aperture 0.8</div>
      <div class="segmented">{seg('inp', [('alpha' + a, lab) for a, lab in ALPHA_VALS], '')}</div></div>
    <div class="group"><div class="glabel">Obstruction ratio</div>
      <div class="segmented">{seg('eps', [(str(x), str(x)) for x in EPS_VALS], '0.0')}</div></div>
    <div class="group"><div class="glabel">Pulse duration</div>
      <div class="segmented">{seg('tau', TAU_VALS, 'cw')}</div></div>
    <div class="group"><div class="glabel">Compare against</div>
      <div class="segmented">{seg('ref', [('none', 'None'), ('eps', 'No obstruction'), ('inp', 'Uniform input'), ('tau', 'Continuous wave'), ('pick', 'A chosen configuration')], 'eps')}</div></div>
  </div>
  <div class="card controls" id="bcontrols" style="display:none">
    <div class="group"><div class="glabel">Second configuration — numerical aperture</div>
      <div class="segmented">{seg('bna', [(str(x), str(x)) for x in NA_VALS], '0.8')}</div></div>
    <div class="group"><div class="glabel">Illumination</div>
      <div class="segmented">{seg('binp', IN_VALS, 'uniform')}</div></div>
    <div class="group"><div class="glabel">Obstruction ratio</div>
      <div class="segmented">{seg('beps', [(str(x), str(x)) for x in EPS_VALS], '0.9')}</div></div>
    <div class="group"><div class="glabel">Pulse duration</div>
      <div class="segmented">{seg('btau', TAU_VALS, '1fs')}</div></div>
  </div>
  <div class="card"><div id="map" style="height:560px"></div></div>
  <div class="card" id="diffcard" style="display:none; margin-top:18px">
    <h2>Difference, selected minus second</h2>
    <div id="diff" style="height:460px"></div>
    <div class="stats" id="diffstats"></div>
  </div>
  <div>
    <div class="card" style="margin-bottom:18px">
      <h2>Measured</h2>
      <div class="stats" id="stats"></div>
      <div id="prof" style="height:340px"></div>
    </div>
  </div>
</main>
<script>
const DATA = {json.dumps(data)};
const MEAS = {json.dumps(meas)};
const sel = {{na:'0.8', inp:'uniform', eps:'0.0', tau:'cw', ref:'eps',
             bna:'0.8', binp:'uniform', beps:'0.9', btau:'1fs'}};
const dark = window.matchMedia('(prefers-color-scheme: dark)').matches;
const ink = dark ? '#f5f5f7' : '#1d1d1f';
const grid = dark ? '#38383a' : '#e5e5ea';
const base = {{paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)',
  font:{{color:ink, family:'-apple-system, BlinkMacSystemFont, sans-serif', size:13}},
  margin:{{l:62,r:16,t:28,b:52}}, xaxis:{{gridcolor:grid, zeroline:false}},
  yaxis:{{gridcolor:grid, zeroline:false}}}};

function key() {{ return sel.na+'|'+sel.inp+'|'+sel.eps+'|'+sel.tau; }}

// The reference is the same configuration with the varied parameter set to its
// null value: no obstruction, or uniform illumination. Numerical aperture has
// no null value, so it is not offered as a reference.
function refKey() {{
  if (sel.ref === 'eps') return sel.na+'|'+sel.inp+'|0.0|'+sel.tau;
  if (sel.ref === 'inp') return sel.na+'|uniform|'+sel.eps+'|'+sel.tau;
  if (sel.ref === 'alpha0') return sel.na+'|alpha0.0|'+sel.eps+'|'+sel.tau;
  if (sel.ref === 'tau') return sel.na+'|'+sel.inp+'|'+sel.eps+'|cw';
  if (sel.ref === 'pick') return sel.bna+'|'+sel.binp+'|'+sel.beps+'|'+sel.btau;
  return null;
}}
function refLabel() {{
  if (sel.ref === 'eps') return 'No obstruction';
  if (sel.ref === 'inp') return 'Uniform input';
  if (sel.ref === 'tau') return 'Continuous wave';
  if (sel.ref === 'pick') return 'Second configuration';
  return null;
}}

function draw() {{
  const d = DATA[key()];
  if (!d) {{
    document.getElementById('stats').innerHTML =
      '<div class="sl">No field for this combination. Every control value the '
      + 'page offers is computed, so reaching this means a field is missing '
      + 'from the atlas.</div>';
    Plotly.purge('map'); Plotly.purge('prof');
    return;
  }}
  // maps are stored as integer fiftieths of a decade to keep the page small;
  // 1/50 of a decade is well below anything a contour or color ramp resolves
  const raw = atob(d.z.b);
  const zz = [];
  for (let i = 0; i < d.z.r; i++) {{
    const row = new Array(d.z.c);
    for (let j = 0; j < d.z.c; j++) {{
      row[j] = (raw.charCodeAt(i * d.z.c + j) - 200) / 50;
    }}
    zz.push(row);
  }}
  Plotly.newPlot('map', [
    {{type:'heatmap', x:d.h, y:d.v, z:zz, colorscale:'Inferno',
      zmin:-4, zmax:0, customdata:zz,
      colorbar:{{title:{{text:'Intensity',side:'right'}}, tickvals:[0,-1,-2,-3,-4],
        ticktext:['1','0.1','0.01','10⁻³','10⁻⁴'], thickness:14, outlinewidth:0}},
      hovertemplate:'r = %{{x:.3f}} µm<br>z = %{{y:.3f}} µm<extra></extra>'}},
    // white iso-intensity lines and an orange half maximum, matching the
    // atlas cards in the deck
    {{type:'contour', x:d.h, y:d.v, z:zz, showscale:false, hoverinfo:'skip',
      autocontour:false, contours:{{start:-4, end:0, size:0.5, coloring:'none'}},
      line:{{color:'rgba(255,255,255,0.45)', width:0.9}}}},
    {{type:'contour', x:d.h, y:d.v, z:zz, showscale:false, hoverinfo:'skip',
      autocontour:false,
      contours:{{start:Math.log10(0.5), end:Math.log10(0.5), size:1, coloring:'none'}},
      line:{{color:'#ff7f0e', width:2.6}}}}
  ], Object.assign({{}}, base, {{
      title:{{text:'Focal field, r–z plane', font:{{size:14}}}},
      xaxis:Object.assign({{}}, base.xaxis, {{title:'Radial position r (µm)'}}),
      yaxis:Object.assign({{}}, base.yaxis, {{title:'Axial position z (µm)'}})}}),
    {{responsive:true, displaylogo:false}});

  const rk = refKey(), rd = rk ? DATA[rk] : null;
  const same = rk === key();
  const traces = [];
  if (rd) {{
    traces.push({{x:rd.h, y:rd.tr, mode:'lines',
      name:refLabel() + (same ? ' (same as selected)' : ''),
      line:{{color:'#8e8e93', width:2, dash:'dot'}}, xaxis:'x', yaxis:'y'}});
    traces.push({{x:rd.v, y:rd.ax, mode:'lines', showlegend:false,
      line:{{color:'#8e8e93', width:2, dash:'dot'}}, xaxis:'x2', yaxis:'y2'}});
  }}
  traces.push({{x:d.h, y:d.tr, mode:'lines', name:'Selected',
      line:{{color:'#ff7f0e', width:2.6}}, xaxis:'x', yaxis:'y'}});
  traces.push({{x:d.v, y:d.ax, mode:'lines', showlegend:false,
      line:{{color:'#ff7f0e', width:2.6}}, xaxis:'x2', yaxis:'y2'}});
  Plotly.react('prof', traces, Object.assign({{}}, base, {{
      margin:{{l:56,r:14,t:24,b:44}},
      grid:{{rows:2, columns:1, pattern:'independent', roworder:'top to bottom'}},
      legend:{{orientation:'h', y:1.22, x:0}},
      xaxis:Object.assign({{}}, base.xaxis, {{title:'r (µm)'}}),
      yaxis:Object.assign({{}}, base.yaxis, {{title:'Transverse'}}),
      xaxis2:Object.assign({{}}, base.xaxis, {{title:'z (µm)'}}),
      yaxis2:Object.assign({{}}, base.yaxis, {{title:'Axial'}})}}),
    {{responsive:true, displaylogo:false}});

  // ── second configuration and the difference between the two ──────────
  const picking = sel.ref === 'pick';
  document.getElementById('bcontrols').style.display = picking ? '' : 'none';
  document.getElementById('diffcard').style.display = picking ? '' : 'none';
  if (picking && rd) {{
    const braw = atob(rd.z.b);
    const bz = [];
    for (let i = 0; i < rd.z.r; i++) {{
      const row = new Array(rd.z.c);
      for (let j = 0; j < rd.z.c; j++) {{
        row[j] = (braw.charCodeAt(i * rd.z.c + j) - 200) / 50;
      }}
      bz.push(row);
    }}
    // the two maps can sit on different windows; difference only where both
    // are defined, on the coarser of the two grids
    const nr = Math.min(zz.length, bz.length);
    const nc = Math.min(zz[0].length, bz[0].length);
    const diff = [];
    let worst = 0;
    for (let i = 0; i < nr; i++) {{
      const row = new Array(nc);
      for (let j = 0; j < nc; j++) {{
        row[j] = zz[i][j] - bz[i][j];
        if (Math.abs(row[j]) > worst) worst = Math.abs(row[j]);
      }}
      diff.push(row);
    }}
    const lim = Math.max(worst, 0.05);
    Plotly.react('diff', [{{
      type:'heatmap', x:d.h.slice(0, nc), y:d.v.slice(0, nr), z:diff,
      colorscale:'RdBu', reversescale:true, zmin:-lim, zmax:lim,
      colorbar:{{title:{{text:'Decades', side:'right'}}, thickness:14,
                outlinewidth:0}},
      hovertemplate:'r = %{{x:.3f}} µm<br>z = %{{y:.3f}} µm<br>' +
                    'difference %{{z:.3f}} decades<extra></extra>'}}],
      Object.assign({{}}, base, {{
        margin:{{l:62, r:16, t:10, b:52}},
        xaxis:Object.assign({{}}, base.xaxis, {{title:'r (µm)'}}),
        yaxis:Object.assign({{}}, base.yaxis, {{title:'z (µm)'}})}}),
      {{responsive:true, displaylogo:false}});

    const ma = MEAS[key()], mb = MEAS[refKey()];
    const rows = [];
    if (ma && mb) {{
      const fields = [
        ['Depth of focus', 'depth', 2, ' µm'],
        ['Width', 'width', 0, ' nm'],
        ['Extension over no obstruction', 'gain', 2, '×'],
        ['Peak intensity', 'peak', 4, ''],
        ['Fraction past the stop', 'transmission', 4, '']];
      for (const [lab, f, dp, unit] of fields) {{
        if (!isFinite(ma[f]) || !isFinite(mb[f])) continue;
        const pct = mb[f] !== 0 ? 100 * (ma[f] / mb[f] - 1) : NaN;
        rows.push('<div class="stat"><div class="sv">' +
          ma[f].toFixed(dp) + unit + ' vs ' + mb[f].toFixed(dp) + unit +
          '</div><div class="sl">' + lab +
          (isFinite(pct) ? '  (' + (pct >= 0 ? '+' : '') + pct.toFixed(2) + '%)'
                         : '') + '</div></div>');
      }}
    }}
    rows.push('<div class="stat"><div class="sv">' + worst.toFixed(3) +
      '</div><div class="sl">Largest difference anywhere on the map, in ' +
      'decades of intensity</div></div>');
    document.getElementById('diffstats').innerHTML = rows.join('');
  }}

  const m = MEAS[key()];
  document.getElementById('stats').innerHTML = m ? [
    ['Width', m.width.toFixed(0)+' nm'],
    ['Depth of focus', m.depth.toFixed(2)+' µm'],
    ['Extension over no obstruction', m.gain.toFixed(2)+'×'],
    ['Fraction of the beam past the stop',
     isFinite(m.transmission) ? m.transmission.toFixed(3) : '--'],
    ['Peak intensity', isFinite(m.peak) ? m.peak.toFixed(3) : '--'],
  ].map(([l,v]) => '<div class="stat"><div class="sv">'+v+
       '</div><div class="sl">'+l+'</div></div>').join('') :
    '<div class="sl">Not measured for this configuration</div>';
}}

// A control whose value has no computed field is shown disabled rather than
// left clickable. Selecting one used to blank the figure with no explanation,
// which reads as a broken page rather than a gap in the sweep.
function trial(group, value) {{
  const t = {{na:sel.na, inp:sel.inp, eps:sel.eps, tau:sel.tau}};
  t[group] = value;
  if (group === 'inp' && value.startsWith('alpha')) {{ t.na = '0.8'; t.tau = 'cw'; }}
  else if (group !== 'inp' && t.inp.startsWith('alpha')) {{
    if (group === 'na' && value !== '0.8') return null;
    if (group === 'tau' && value !== 'cw') return null;
  }}
  return t.na+'|'+t.inp+'|'+t.eps+'|'+t.tau;
}}
function refreshAvailability() {{
  document.querySelectorAll('.seg').forEach(o => {{
    const k = trial(o.dataset.group, o.dataset.value);
    o.classList.toggle('off', !(k && DATA[k]));
  }});
}}

document.querySelectorAll('.seg').forEach(b => b.addEventListener('click', () => {{
  if (b.classList.contains('off')) return;
  const g = b.dataset.group;
  sel[g] = b.dataset.value;
  // the alpha sweep exists only at numerical aperture 0.8, continuous wave
  if (g === 'inp' && b.dataset.value.startsWith('alpha')) {{
    sel.na = '0.8'; sel.tau = 'cw';
    document.querySelectorAll('.seg[data-group=\"na\"]').forEach(o =>
      o.classList.toggle('on', o.dataset.value === '0.8'));
    document.querySelectorAll('.seg[data-group=\"tau\"]').forEach(o =>
      o.classList.toggle('on', o.dataset.value === 'cw'));
  }}
  document.querySelectorAll('.seg[data-group="'+g+'"]').forEach(o => o.classList.remove('on'));
  b.classList.add('on');
  refreshAvailability();
  draw();
}}));
refreshAvailability();
draw();
</script></body></html>"""

    with open(OUT, 'w') as fh:
        fh.write(html)
    print(f'{len(data)} configurations')
    print(f'{os.path.getsize(OUT) / 1e6:.1f} MB')
    print(f'Saved -> {OUT}')


if __name__ == '__main__':
    main()
