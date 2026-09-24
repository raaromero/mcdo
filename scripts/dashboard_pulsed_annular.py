"""Interactive view of the pulsed annular grid.

Reads the profiles saved by ``verify_pulsed_annular_grid.py`` and writes a
self-contained HTML page: pick the numerical aperture, the input and the
obstruction ratio, and compare pulse durations against each other on both the
transverse and axial profile, with the depth-of-focus gain reported alongside.

Nothing is recomputed here. The physics happens in the sweep; this only draws
what the sweep saved, so the page can be rebuilt in a second.

    python scripts/dashboard_pulsed_annular.py
    -> output/05_pulsed_pupils/pulsed_annular_dashboard.html
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '05_pulsed_pupils')
DATA = os.path.join(OUT, 'pulsed_annular_grid.npz')

COLOR = {'continuous wave': '#1f77b4', '2 fs': '#d62728', '1 fs': '#2ca02c'}


def main():
    if not os.path.exists(DATA):
        raise SystemExit(f"{DATA} not found — run verify_pulsed_annular_grid.py first")
    d = np.load(DATA, allow_pickle=True)

    na = d['na']
    inputs = [str(v) for v in d['input']]
    taus = [str(v) for v in d['tau']]
    eps = d['eps']
    gain = d['gain']

    na_vals = sorted(set(na.tolist()))
    in_vals = sorted(set(inputs))
    eps_vals = sorted(set(eps.tolist()))
    tau_vals = ['continuous wave', '2 fs', '1 fs']

    # one trace per (cell, pulse duration, axis); visibility switches with the menu
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Transverse profile', 'Axial profile'),
        horizontal_spacing=0.10)

    combos = [(a, b, e) for a in na_vals for b in in_vals for e in eps_vals]
    trace_owner = []

    for (a, b, e) in combos:
        for t in tau_vals:
            key = f"{a}|{b}|{e}|{t}"
            for col, axis in ((1, 'r'), (2, 'z')):
                arr = d.get(key + '|' + axis) if hasattr(d, 'get') else None
                if arr is None:
                    try:
                        arr = d[key + '|' + axis]
                    except KeyError:
                        continue
                x, y = arr[0], arr[1]
                if axis == 'r':
                    x = x * 1000.0                      # nanometres read better here
                fig.add_trace(
                    go.Scatter(x=x, y=y, mode='lines', name=t,
                               line=dict(color=COLOR[t], width=2.4),
                               legendgroup=t, showlegend=(col == 1),
                               visible=False),
                    row=1, col=col)
                trace_owner.append((a, b, e))

    def visibility(sel):
        return [owner == sel for owner in trace_owner]

    buttons = []
    for (a, b, e) in combos:
        g = [gain[i] for i in range(len(na))
             if na[i] == a and inputs[i] == b and eps[i] == e]
        g_txt = f"{np.nanmean(g):.2f}" if g else "n/a"
        short = 'uniform' if b == 'uniform' else 'Gaussian, alpha = 4'
        buttons.append(dict(
            label=f"NA {a:g} · {short} · ratio {e:g}",
            method='update',
            args=[{'visible': visibility((a, b, e))},
                  {'title': (f"Numerical aperture {a:g}, {short} input, "
                             f"obstruction ratio {e:g}, 750 nm "
                             f"— depth-of-focus gain {g_txt}")}]))

    first = combos[0]
    for i, v in enumerate(visibility(first)):
        fig.data[i].visible = v

    fig.update_xaxes(title_text='Radial position r (nm)', row=1, col=1)
    fig.update_xaxes(title_text='Axial position z (μm)', row=1, col=2)
    fig.update_yaxes(title_text='Normalized intensity', row=1, col=1)
    fig.update_yaxes(title_text='Normalized intensity', row=1, col=2)
    fig.add_hline(y=0.5, line=dict(color='#888', dash='dash', width=1.2))

    fig.update_layout(
        updatemenus=[dict(buttons=buttons, direction='down', showactive=True,
                          x=0.0, xanchor='left', y=1.18, yanchor='top')],
        title=(f"Numerical aperture {first[0]:g}, "
               f"{'uniform' if first[1] == 'uniform' else 'Gaussian, alpha = 4'}"
               f" input, obstruction ratio {first[2]:g}, 750 nm"),
        template='simple_white', height=620, width=1400,
        legend=dict(orientation='h', y=-0.18),
        font=dict(size=15))

    # --- second figure: trends against obstruction ratio -------------------
    fig2 = make_subplots(rows=1, cols=3, subplot_titles=(
        'Depth-of-focus extension', 'Transverse width (nm)', 'Depth of focus (um)'),
        horizontal_spacing=0.08)
    combos2 = [(a, b) for a in na_vals for b in in_vals]
    owner2 = []
    for (a, b) in combos2:
        for t in tau_vals:
            m = [i for i in range(len(na)) if na[i] == a and inputs[i] == b
                 and taus[i] == t]
            m.sort(key=lambda i: eps[i])
            xs = [eps[i] for i in m]
            for col, series in ((1, [gain[i] for i in m]),
                                (2, [d['width_nm'][i] for i in m]),
                                (3, [d['depth_um'][i] for i in m])):
                fig2.add_trace(
                    go.Scatter(x=xs, y=series, mode='lines+markers', name=t,
                               line=dict(color=COLOR[t], width=2.4),
                               legendgroup=t, showlegend=(col == 1),
                               visible=False),
                    row=1, col=col)
                owner2.append((a, b))
    buttons2 = []
    for (a, b) in combos2:
        short = 'uniform' if b == 'uniform' else 'Gaussian, alpha = 4'
        buttons2.append(dict(
            label=f"NA {a:g} - {short}", method='update',
            args=[{'visible': [o == (a, b) for o in owner2]},
                  {'title': f"Numerical aperture {a:g}, {short} input, 750 nm"}]))
    for i, vis in enumerate([o == combos2[0] for o in owner2]):
        fig2.data[i].visible = vis
    fig2.update_yaxes(type='log', row=1, col=1)
    for c, lab in ((1, 'Extension factor'), (2, 'Width (nm)'), (3, 'Depth of focus (um)')):
        fig2.update_xaxes(title_text='Obstruction ratio', row=1, col=c)
        fig2.update_yaxes(title_text=lab, row=1, col=c)
    fig2.update_layout(
        updatemenus=[dict(buttons=buttons2, direction='down', showactive=True,
                          x=0.0, xanchor='left', y=1.18, yanchor='top')],
        title=(f"Numerical aperture {combos2[0][0]:g}, "
               f"{'uniform' if combos2[0][1] == 'uniform' else 'Gaussian, alpha = 4'}"
               f" input, 750 nm"),
        template='simple_white', height=560, width=1400,
        legend=dict(orientation='h', y=-0.22), font=dict(size=15))
    out2 = os.path.join(OUT, 'pulsed_annular_trends.html')
    fig2.write_html(out2, include_plotlyjs='cdn')
    print(f"Saved → {out2}")

    out = os.path.join(OUT, 'pulsed_annular_dashboard.html')
    fig.write_html(out, include_plotlyjs='cdn')
    print(f"{len(combos)} configurations, {len(fig.data)} traces")
    print(f"Saved → {out}")


if __name__ == '__main__':
    main()
