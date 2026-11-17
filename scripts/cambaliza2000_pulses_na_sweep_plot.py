r"""How long the pulses must be for the pulsed 2CE and 2PE to match the continuous-beam profiles, against NA.

Each pulsed profile is compared with the continuous-beam profile of the same model, medium and NA, along the axis
(x = 0) and across it (z = 0), with the measures of Cambaliza & Saloma (2000) and Romallosa et al. (2003):

* largest difference: the largest gap between the two profiles, each scaled to its own peak (% of the peak);
* depth of focus and transverse width: FWHM along z and along x through the fringe crests, over the continuous-beam value;
* side lobe: the largest maximum outside the central lobe of the crest envelope (% of the peak), pulsed minus continuous;
* Linfoot fidelity F, structural content S and correlation quality Q (mcdo.linfoot) on the two cuts together, with the
  continuous-beam profile as the reference: F = 1 − Σ(r − a)²/Σr², S = Σa²/Σr², Q = Σ ar/Σr².

A pulse width is within tolerance when the difference stays below 1% of the peak, both FWHM within 1% of their
continuous-beam values, the side lobe within 1 point and F, S and Q within 0.01 of 1; it is read off on a log scale of
τ. Data from cambaliza2000_pulses_na_sweep.py.

    python scripts/cambaliza2000_pulses_na_sweep_plot.py
    -> output/08_two_color/cambaliza2000/pulses/na_sweep/{diff_vs_tau_<set>.png, metrics_vs_tau_<set>_<sig>.png,
       tau_cw_vs_na.png, tau_cw_vs_na_<sig>.png, tau_cw.txt}
       and dashboard/cambaliza/public/data/pulse_na.json (the same numbers, for the pulse results tab)
    PANELS=1 python scripts/cambaliza2000_pulses_na_sweep_plot.py
    -> …/na_sweep/tau_cw_vs_na[_pupils]_<sig>_{pi,0_pi2}.png: the two τ-against-NA figures, at most two panels across
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo.style import apply as _apply_style
from mcdo.linfoot import fidelity, structural_content, correlation_quality
from cambaliza2000_pulses_sweep import fwhm

_apply_style()
matplotlib.rcParams.update({'font.size': 26, 'axes.titlesize': 26, 'axes.labelsize': 26, 'xtick.labelsize': 22,
                            'ytick.labelsize': 22, 'legend.fontsize': 20})
D = os.path.join(os.path.dirname(__file__), '..', 'output', '08_two_color', 'cambaliza2000', 'pulses', 'na_sweep')
THETAS = (('0', 'θ = 0, collinear lenses'), ('pi2', 'θ = π/2, crossed lenses'), ('pi', 'θ = π, facing lenses'))
MEDCOL = {'air': '#4e79a7', 'water': '#e15759', 'oil': '#59a14f'}


def set_label(name):
    """'rw_water_eps0.9_gauss4' -> 'Richards–Wolf, water, ε = 0.9, Gaussian input α = 4'."""
    parts = name.split('_')
    lab = ['scalar' if parts[0] == 'paraxial' else 'Richards–Wolf', parts[1]]
    for q in parts[2:]:
        lab.append(f'ε = {q[3:]}' if q.startswith('eps') else f'Gaussian input α = {q[5:]}')
    return ', '.join(lab)


SETS = {n: set_label(n) for n in sorted(os.listdir(D)) if os.path.isdir(os.path.join(D, n))}
MAIN = [n for n in SETS if n.count('_') == 1]                       # circular pupil, uniform input
STYLE = {n: (MEDCOL[n.split('_')[1]], '--' if n.startswith('paraxial') else '-') for n in SETS}
# measure: label, axis label, distance from continuous beams (in % or points), tolerance
MET = {'diff': ('Largest difference', 'Largest difference (% of the peak)', lambda v: v, 1.0),
       'dof': ('Depth of focus', 'DOF pulsed / DOF continuous (ratio)', lambda v: 100 * abs(v - 1), 1.0),
       'wx': ('Width across the axis', 'FWHM pulsed / FWHM continuous (ratio)', lambda v: 100 * abs(v - 1), 1.0),
       'side': ('Side lobe', 'Side lobe, pulsed − continuous (% of the peak)', lambda v: abs(v), 1.0),
       'F': ('Linfoot fidelity F', 'Fidelity F (1 = identical)', lambda v: 100 * (1 - v), 1.0),
       'S': ('Linfoot structural content S', 'Structural content S (1 = identical)', lambda v: 100 * abs(v - 1), 1.0),
       'Q': ('Linfoot correlation quality Q', 'Correlation quality Q (1 = identical)', lambda v: 100 * abs(v - 1), 1.0)}


def side_lobe(y):
    """Largest maximum outside the central lobe (% of the peak): beyond the first minimum on each side."""
    i0 = int(np.argmax(y)); r, l = i0, i0
    while r < len(y) - 1 and y[r + 1] <= y[r]:
        r += 1
    while l > 0 and y[l - 1] <= y[l]:
        l -= 1
    out = np.concatenate([y[r:], y[:l + 1]])
    return 100 * out.max() / y.max() if out.size else 0.0


def measures(R, sig, tk, key):
    """All measures of one pulsed profile (key = τ) against the continuous-beam one."""
    p = lambda c, k: R[f'{sig}_{tk}_{c}_{k}']
    s = lambda c: R[f'{sig}_{tk}_{c}_s']
    cw, te = np.concatenate([p('z', 'cw'), p('x', 'cw')]), np.concatenate([p('z', key), p('x', key)])
    return {'diff': 100 * max(np.abs(p(c, key) - p(c, 'cw')).max() for c in 'zx'),
            'dof': fwhm(s('z'), p('z', f'{key}_crest')) / fwhm(s('z'), p('z', 'cw_crest')),
            'wx': fwhm(s('x'), p('x', f'{key}_crest')) / fwhm(s('x'), p('x', 'cw_crest')),
            'side': max(side_lobe(p(c, f'{key}_crest')) for c in 'zx') - max(side_lobe(p(c, 'cw_crest')) for c in 'zx'),
            'F': fidelity(cw, te), 'S': structural_content(cw, te), 'Q': correlation_quality(cw, te)}


def load(name):
    """{NA: {(sig, θ): {measure: values over τ, 'taus': τ}}} for one set (runs that saved the crest envelope)."""
    out = {}
    for f in sorted(glob.glob(os.path.join(D, name, 'na*.npz'))):
        R = np.load(f)
        if not any(k.endswith('_cw_crest') for k in R.files):
            continue
        d = {}
        for sig in ('2ce', '2pe'):
            for tk, _ in THETAS:
                if f'{sig}_{tk}_z_cw' not in R:
                    continue
                rows = [measures(R, sig, tk, f'{t:g}') for t in R['taus']]
                d[(sig, tk)] = {k: np.array([r[k] for r in rows]) for k in MET} | {'taus': R['taus']}
        out[float(R['na'])] = d
    return out


def tau_within(taus, dev, tol):
    """Shortest τ beyond which the distance from continuous beams stays below tol (log interpolation); nan if never."""
    dev = np.where(np.isfinite(dev), dev, np.inf)
    ok = dev < tol
    if not ok[-1]:
        return np.nan
    i = len(ok) - 1
    while i > 0 and ok[i - 1]:
        i -= 1
    if i == 0:
        return float(taus[0])
    if not np.isfinite(dev[i - 1]):
        return float(taus[i])
    a, b = np.log(max(dev[i - 1], 1e-9)), np.log(max(dev[i], 1e-9))
    return float(np.exp(np.interp(np.log(tol), [b, a], [np.log(taus[i]), np.log(taus[i - 1])])))


def tw(d, na, sig, tk, k):
    v = d[na][(sig, tk)]
    return tau_within(v['taus'], MET[k][2](v[k]), MET[k][3])


data = {k: load(k) for k in SETS if os.path.isdir(os.path.join(D, k))}
data = {k: v for k, v in data.items() if v}
cmap = plt.get_cmap('viridis')
colour = lambda i, n: cmap(i / max(n - 1, 1))

# 3. Pulse width within tolerance against NA (drawn below; defined here for the panels of PANELS=1)
def against_na(ax, sig, tk, k, names=None, paraxial_max=None):
    """With paraxial_max, the scalar curves stop at that NA."""
    for name, d in data.items():
        if name not in (names or MAIN):
            continue
        nas = [na for na in sorted(d) if (sig, tk) in d[na]
               and not (paraxial_max and name.startswith('paraxial') and na > paraxial_max + 1e-9)]
        t = [tw(d, na, sig, tk, k) for na in nas]
        col, ls = STYLE[name]
        ax.plot(nas, t, ls, marker='o', color=col, lw=2.8, ms=8, label=SETS[name])
        far = [na for na, v in zip(nas, t) if np.isnan(v)]          # still outside tolerance at the longest pulse
        ax.plot(far, [520] * len(far), '^', color=col, ms=14, mfc='none', mew=2.5)
    ax.set_yscale('log'); ax.set_ylim(3, 700); ax.set_xlim(0.05, 1.25)
    ax.axhspan(3, 5, color='0.9', zorder=0)                            # below the shortest pulse run


PUP = [n for n in SETS if n.startswith('rw_air') and n in data]
pcol = plt.get_cmap('tab10')


def pupils_on(ax, sig, tk):
    """Pulse width with the depth of focus within 1% against NA, one line per pupil and input (Richards–Wolf, air)."""
    for i, name in enumerate(PUP):
        d = data[name]; nas = [na for na in sorted(d) if (sig, tk) in d[na]]
        ax.plot(nas, [tw(d, na, sig, tk, 'dof') for na in nas], 'o-', color=pcol(i), lw=2.6, ms=8, label=SETS[name])
    ax.set_yscale('log'); ax.set_ylim(3, 1500); ax.set_xlim(0.05, 1.0); ax.axhspan(3, 4, color='0.9', zorder=0)


if os.environ.get('PANELS'):
    # PANELS=1: tau_cw_vs_na.png and tau_cw_vs_na_pupils.png at most two panels across, for slides (fonts 32, 28, 24;
    # about 11 × 10 in per panel; 600 DPI): per signal, θ = π alone and θ = 0 with π/2. The scalar curves stop at NA 0.5.
    # Writes tau_cw_vs_na_<sig>_{pi,0_pi2}.png and tau_cw_vs_na_pupils_<sig>_{pi,0_pi2}.png and nothing else.
    matplotlib.rcParams.update({'font.size': 28, 'axes.titlesize': 32, 'axes.labelsize': 28, 'xtick.labelsize': 24,
                                'ytick.labelsize': 24, 'legend.fontsize': 24, 'figure.dpi': 100})
    L = lambda **k: plt.Line2D([], [], lw=2.8, **k)
    keys = {'': ([L(color=MEDCOL[m], marker='o', ms=8) for m in MEDCOL] + [L(color='k'), L(color='k', ls='--')],
                 list(MEDCOL) + ['Richards–Wolf', 'scalar']),
            '_pupils': ([L(color=pcol(i), marker='o', ms=8) for i in range(len(PUP))],
                        ['circular pupil' if n == 'rw_air' else f'ε = {n.split("eps")[1]}' if 'eps' in n else
                         f'Gaussian input α = {n.split("gauss")[1]}' for n in PUP])}
    ylab = {'': 'Pulse width that matches\ncontinuous beams within 1% (fs)',
            '_pupils': 'Pulse width with the depth of focus\nwithin 1% of continuous beams (fs)'}
    TT = dict(THETAS)
    for fig_name in ('', '_pupils'):
        for sig in ('2ce', '2pe'):
            for part, tks in (('pi', ('pi',)), ('0_pi2', ('0', 'pi2'))):
                fig, axes = plt.subplots(1, len(tks), figsize=(11 * len(tks), 10), squeeze=False, sharey=True)
                fig.subplots_adjust(wspace=0.1)
                for ax, tk in zip(axes[0], tks):
                    if fig_name:
                        pupils_on(ax, sig, tk)
                    else:
                        against_na(ax, sig, tk, 'diff', paraxial_max=0.5)
                    ax.set_title(f'{sig.upper()}, {TT[tk]}'); ax.set_xlabel('NA')
                axes[0, 0].set_ylabel(ylab[fig_name])
                axes[0, -1].legend(*keys[fig_name], loc='lower left' if part == 'pi' else 'upper right', frameon=False)
                fig.savefig(os.path.join(D, f'tau_cw_vs_na{fig_name}_{sig}_{part}.png'), dpi=600, bbox_inches='tight')
                plt.close(fig)
    print('Saved -> tau_cw_vs_na[_pupils]_<sig>_{pi,0_pi2}.png')
    sys.exit()


# 1. Largest difference against τ, one figure per set: rows 2CE and 2PE, columns the three lens angles, a line per NA
for name, d in data.items():
    nas = sorted(d)
    fig, axes = plt.subplots(2, 3, figsize=(30, 16), sharex=True, sharey=True)
    for r, sig in enumerate(('2ce', '2pe')):
        for c, (tk, ttl) in enumerate(THETAS):
            ax = axes[r, c]
            for i, na in enumerate(nas):
                if (sig, tk) in d[na]:
                    v = d[na][(sig, tk)]
                    ax.plot(v['taus'], np.maximum(v['diff'], 1e-3), 'o-', color=colour(i, len(nas)), lw=2.4, ms=7,
                            label=f'NA {na:g}')
            ax.axhline(MET['diff'][3], color='k', ls=':', lw=2)
            ax.set_xscale('log'); ax.set_yscale('log'); ax.set_ylim(1e-2, 150)
            ax.set_title(f'{sig.upper()}, {ttl}')
            if r == 1:
                ax.set_xlabel('Pulse width τ (fs)')
    axes[0, 0].legend(loc='upper right', ncol=2, frameon=False)
    fig.supylabel('Largest difference from the continuous-beam profile (% of the peak)', x=0.005)
    fig.tight_layout(rect=(0.015, 0, 1, 1))
    fig.savefig(os.path.join(D, f'diff_vs_tau_{name}.png'), dpi=200, bbox_inches='tight'); plt.close(fig)

# 2. The measures of Cambaliza & Saloma and Romallosa et al. against τ, one figure per set and signal
ROWS = ('dof', 'wx', 'side', 'F', 'S')
for name, d in data.items():
    nas = sorted(d)
    for sig in ('2ce', '2pe'):
        fig, axes = plt.subplots(3, len(ROWS), figsize=(9 * len(ROWS), 22), sharex=True)
        for c, k in enumerate(ROWS):
            for r, (tk, ttl) in enumerate(THETAS):
                ax = axes[r, c]
                for i, na in enumerate(nas):
                    if (sig, tk) in d[na]:
                        v = d[na][(sig, tk)]
                        ax.plot(v['taus'], v[k], 'o-', color=colour(i, len(nas)), lw=2.4, ms=7, label=f'NA {na:g}')
                ax.axhline(0 if k == 'side' else 1, color='k', ls=':', lw=2)
                ax.set_xscale('log')
                ax.set_title(f'{MET[k][0]}, {ttl}', fontsize=22)
                ax.set_ylabel(MET[k][1])
                if r == 2:
                    ax.set_xlabel('Pulse width τ (fs)')
        axes[0, 0].legend(loc='lower right', ncol=2, frameon=False)
        fig.tight_layout()
        fig.savefig(os.path.join(D, f'metrics_vs_tau_{name}_{sig}.png'), dpi=200, bbox_inches='tight'); plt.close(fig)


# 3. Pulse width within tolerance against NA: largest difference for both signals, then every measure per signal
fig, axes = plt.subplots(2, 3, figsize=(30, 16), sharex=True, sharey=True)
for r, sig in enumerate(('2ce', '2pe')):
    for c, (tk, ttl) in enumerate(THETAS):
        against_na(axes[r, c], sig, tk, 'diff')
        axes[r, c].set_title(f'{sig.upper()}, {ttl}')
        if r == 1:
            axes[r, c].set_xlabel('NA')
        if c == 0:
            axes[r, c].set_ylabel('τ within 1% of continuous beams (fs)')
axes[0, 2].legend(loc='upper right', frameon=False)
fig.tight_layout()
fig.savefig(os.path.join(D, 'tau_cw_vs_na.png'), dpi=200, bbox_inches='tight'); plt.close(fig)
KS = ('diff', 'dof', 'wx', 'side', 'F')
for sig in ('2ce', '2pe'):
    fig, axes = plt.subplots(3, len(KS), figsize=(9 * len(KS), 22), sharex=True, sharey=True)
    for c, k in enumerate(KS):
        for r, (tk, ttl) in enumerate(THETAS):
            against_na(axes[r, c], sig, tk, k)
            axes[r, c].set_title(f'{MET[k][0]}, {ttl}', fontsize=22)
            if r == 2:
                axes[r, c].set_xlabel('NA')
    axes[0, 2].legend(loc='upper right', frameon=False)
    fig.supylabel(f'τ within tolerance of continuous beams, {sig.upper()} (fs)', x=0.005)
    fig.tight_layout(rect=(0.015, 0, 1, 1))
    fig.savefig(os.path.join(D, f'tau_cw_vs_na_{sig}.png'), dpi=200, bbox_inches='tight'); plt.close(fig)

# 5. Key results for the slides: depth of focus (of continuous beams) against τ with a line per NA, and against NA with
# a line per τ, for the three lens angles; scalar model in air unless the vector model in air is in
KEY = os.environ.get('KEY', 'paraxial_air')                        # the deck's set; KEY=rw_air for the vector model
if KEY in data:
    d, nas = data[KEY], sorted(data[KEY])
    for sig in ('2ce', '2pe'):
        fig, axes = plt.subplots(1, 3, figsize=(30, 9), sharey=True)
        for c, (tk, ttl) in enumerate(THETAS):
            ax = axes[c]
            for i, na in enumerate(nas):
                if (sig, tk) in d[na]:
                    v = d[na][(sig, tk)]
                    ax.plot(v['taus'], v['dof'], 'o-', color=colour(i, len(nas)), lw=2.6, ms=7, label=f'NA {na:g}')
            ax.axhline(1, color='k', ls=':', lw=2)
            ax.set_xscale('log'); ax.set_ylim(0, 1.25); ax.set_title(ttl); ax.set_xlabel('Pulse width τ (fs)')
        axes[0].set_ylabel(f'{sig.upper()} DOF pulsed / DOF continuous (ratio)')
        fig.legend(*axes[2].get_legend_handles_labels(), loc='lower center', bbox_to_anchor=(0.5, 0.98), ncol=len(nas), frameon=False)
        fig.tight_layout()
        fig.savefig(os.path.join(D, f'key_dof_vs_tau_{sig}{"" if KEY == "paraxial_air" else "_" + KEY}.png'), dpi=200, bbox_inches='tight'); plt.close(fig)
        taus = sorted(set.intersection(*[set(d[na][(sig, 'pi')]['taus']) for na in nas]))      # widths run at every NA
        fig, axes = plt.subplots(1, 3, figsize=(30, 9), sharey=True)
        tcol = plt.get_cmap('plasma')
        for c, (tk, ttl) in enumerate(THETAS):
            ax = axes[c]
            ok = [na for na in nas if (sig, tk) in d[na]]
            for j, t in enumerate(taus):
                ax.plot(ok, [d[na][(sig, tk)]['dof'][list(d[na][(sig, tk)]['taus']).index(t)] for na in ok], 'o-', color=tcol(0.9 * j / max(len(taus) - 1, 1)),
                        lw=2.6, ms=7, label=f'{t:g} fs')
            ax.axhline(1, color='k', ls=':', lw=2)
            ax.set_ylim(0, 1.25); ax.set_xlim(0.05, 1.0); ax.set_title(ttl); ax.set_xlabel('NA')
        axes[0].set_ylabel(f'{sig.upper()} DOF pulsed / DOF continuous (ratio)')
        fig.legend(*axes[2].get_legend_handles_labels(), loc='lower center', bbox_to_anchor=(0.5, 0.98), ncol=len(taus), frameon=False)
        fig.tight_layout()
        fig.savefig(os.path.join(D, f'key_dof_vs_na_{sig}{"" if KEY == "paraxial_air" else "_" + KEY}.png'), dpi=200, bbox_inches='tight'); plt.close(fig)
    json.dump({f'{sig}|{tk}|{na:g}|{t:g}': round(float(v), 4) for na in nas for sig in ('2ce', '2pe') for tk, _ in THETAS
               if (sig, tk) in d[na] for t, v in zip(d[na][(sig, tk)]['taus'], d[na][(sig, tk)]['dof'])},
              open(os.path.join(D, 'key_dof.json' if KEY == 'paraxial_air' else f'key_dof_{KEY}.json'), 'w'))

# 6. Pupil and input, Richards–Wolf model in air: pulse width within tolerance against NA for each pupil and input
if len(PUP) > 1:
    fig, axes = plt.subplots(2, 3, figsize=(30, 16), sharex=True, sharey=True)
    for r, sig in enumerate(('2ce', '2pe')):
        for c, (tk, ttl) in enumerate(THETAS):
            ax = axes[r, c]
            pupils_on(ax, sig, tk)
            ax.set_title(f'{sig.upper()}, {ttl}')
            if r == 1:
                ax.set_xlabel('NA')
            if c == 0:
                ax.set_ylabel('τ with DOF within 1% of continuous beams (fs)')
    axes[0, 2].legend(loc='upper right', frameon=False, fontsize=18)
    fig.tight_layout()
    fig.savefig(os.path.join(D, 'tau_cw_vs_na_pupils.png'), dpi=200, bbox_inches='tight'); plt.close(fig)

# 7. The delay: peak (over the peak without delay) and centre along the axis against Δt/τ, one figure per set and signal
for name in SETS:
    files = sorted(glob.glob(os.path.join(D, name, 'na*.npz')))
    runs = {}
    for f in files:
        R = np.load(f)
        dk = [k for k in R.files if k.endswith('_rel') and '_z_' in k]
        if dk:
            runs[float(R['na'])] = R
    if not runs:
        continue
    for sig in ('2ce', '2pe'):
        taus = sorted({float(k.split('_')[3]) for R in runs.values() for k in R.files if k.startswith(f'{sig}_') and k.endswith('_rel')})
        fig, axes = plt.subplots(2, 3, figsize=(30, 16), sharex=True)
        nas = sorted(runs)
        for c, (tk, ttl) in enumerate(THETAS):
            for i, na in enumerate(nas):
                R = runs[na]
                for j, tau in enumerate(taus):
                    ds = sorted({float(k.split('_d')[1].split('_')[0]) for k in R.files if k.startswith(f'{sig}_{tk}_z_{tau:g}_d') and k.endswith('_rel')})
                    if not ds:
                        continue
                    zs = R[f'{sig}_{tk}_z_s']
                    rel = [1.0] + [float(R[f'{sig}_{tk}_z_{tau:g}_d{x:g}_rel']) for x in ds]
                    cen = [float((zs * R[f'{sig}_{tk}_z_{tau:g}']).sum() / R[f'{sig}_{tk}_z_{tau:g}'].sum())] + \
                          [float((zs * R[f'{sig}_{tk}_z_{tau:g}_d{x:g}']).sum() / R[f'{sig}_{tk}_z_{tau:g}_d{x:g}'].sum()) for x in ds]
                    ls = ('-', '--', ':', '-.')[j % 4]
                    lab = f'NA {na:g}, {tau:g} fs'
                    axes[0, c].plot([0] + ds, rel, ls, marker='o', color=colour(i, len(nas)), lw=2.2, ms=6, label=lab)
                    axes[1, c].plot([0] + ds, cen, ls, marker='o', color=colour(i, len(nas)), lw=2.2, ms=6, label=lab)
            axes[0, c].set_title(f'{sig.upper()} peak, {ttl}'); axes[1, c].set_title(f'{sig.upper()} centre along the axis, {ttl}')
            axes[1, c].set_xlabel('Delay of pulse 2, Δt/τ')
        axes[0, 0].set_ylabel('Peak, with delay / without delay (ratio)'); axes[1, 0].set_ylabel('Centre of the profile along z (µm)')
        axes[0, 2].legend(loc='upper right', frameon=False, fontsize=14, ncol=2)
        fig.tight_layout()
        fig.savefig(os.path.join(D, f'delay_{name}_{sig}.png'), dpi=200, bbox_inches='tight'); plt.close(fig)

# 4. The numbers, as text and for the dashboard
lines = []
J = {'taus': None, 'met': {k: {'label': v[0], 'unit': v[1], 'tol': v[3]} for k, v in MET.items()}, 'sets': {}}
for name, d in data.items():
    nas = sorted(d)
    J['sets'][name] = {'label': SETS[name], 'nas': nas, 'val': {}, 'tw': {}, 'taus': None}
    for sig in ('2ce', '2pe'):
        for tk, _ in THETAS:
            ok = [na for na in nas if (sig, tk) in d[na]]
            if not ok:
                continue
            J['taus'] = J['sets'][name]['taus'] = [float(t) for t in d[ok[0]][(sig, tk)]['taus']]
            key = f'{sig.upper()}|{tk}'
            J['sets'][name]['val'][key] = {k: {f'{na:g}': [round(float(x), 5) if np.isfinite(x) else None
                                                          for x in d[na][(sig, tk)][k]] for na in ok} for k in MET}
            J['sets'][name]['tw'][key] = {k: [[na, None if np.isnan(t) else round(t, 1)] for na in ok
                                              for t in [tw(d, na, sig, tk, k)]] for k in MET}
            for na in ok:
                lines.append(f'{sig} {tk} {name} NA {na:g}: within tolerance from ' +
                             ', '.join(f'{k} {tw(d, na, sig, tk, k):.1f} fs' for k in MET))
open(os.path.join(D, 'tau_cw.txt'), 'w').write('\n'.join(lines) + '\n')
DJ = os.path.join(os.path.dirname(__file__), '..', 'dashboard', 'cambaliza', 'public', 'data', 'pulse_na.json')
json.dump(J, open(DJ, 'w'))
print('Saved', len(data), 'sets:', ', '.join(data) or 'none yet')
