r"""Linfoot's criteria of the paraxial scalar profile against the vector (Richards-Wolf) one, for every case computed.

Same definitions and data as the dashboard (scripts/dashboard_cambaliza_extra.py -> metrics.json): each profile
normalized to unit energy over its window, vector r = reference, scalar a,
    F = 1 − Σ (a − r)² / Σ r²,   C = Σ a² / Σ r²,   Q = Σ a r / Σ r².
One figure per signal (2PE, 2CE), pupil (circular, annular ε = 0.99) and input (uniform, Gaussian α = 4):
rows F, C, Q; columns across (z = 0) and along (x = 0) the axis; θ = 0, π/2, π in colour; air solid (filled),
water dashed (open). Every NA computed: 0.2–0.95 in air, 0.2–1.25 in water (θ = π/2 only where crossed lenses fit).
2CE: θ = 0 and π are the same profile; 2PE across the axis: θ = π equals θ = 0 (drawn once).

    python scripts/cambaliza2000_linfoot_all.py
    -> output/08_two_color/cambaliza2000/high_na/linfoot/linfoot_<2pe|2ce>_<circ|ann>_<uni|gau>.png, linfoot_all.txt
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo.style import apply as _apply_style
from mcdo.cutinset import cut_inset, fig_legend

_apply_style()
matplotlib.rcParams.update({'font.size': 28, 'axes.titlesize': 32, 'axes.labelsize': 32, 'xtick.labelsize': 28,
                            'ytick.labelsize': 28, 'legend.fontsize': 28})   # ≥ 11 pt on the slide with the inset beside the plots

ROOT = os.path.join(os.path.dirname(__file__), '..')
M = json.load(open(os.path.join(ROOT, 'dashboard', 'cambaliza', 'public', 'data', 'metrics.json')))
OUT = os.path.join(ROOT, 'output', '08_two_color', 'cambaliza2000', 'high_na', 'linfoot')
os.makedirs(OUT, exist_ok=True)
COL = {'0': '#ff7f0e', 'pi2': '#d62728', 'pi': '#1f77b4'}
TH = {'0': 'θ = 0', 'pi2': 'θ = π/2', 'pi': 'θ = π'}
KEYS = (('F', 2, 'Fidelity F'), ('C', 3, 'Structural content C'), ('Q', 4, 'Correlation quality Q'))
PUP = {'circ': 'circular pupils', 'ann': 'annular pupils, ε = 0.99'}
INP = {'uni': 'uniform input', 'gau': 'Gaussian input'}

lines = []
for sig in ('2PE', '2CE'):
    for pupil in ('circ', 'ann'):
        for inp in ('uni', 'gau'):
            fig, axes = plt.subplots(3, 2, figsize=(18.5, 17.0), sharex=True)
            for col, axis in enumerate(('x', 'z')):
                for th in ('0', 'pi2', 'pi'):
                    if (sig == '2CE' and th == 'pi') or (sig == '2PE' and axis == 'x' and th == 'pi'):
                        continue                               # the same profile as θ = 0
                    lab = 'θ = 0 and π' if sig == '2CE' and th == '0' else TH[th]   # 2PE across: θ = π is the θ = 0 curve
                    for med, ls, mk in (('air', '-', 'o'), ('water', '--', 's')):
                        rows = M.get(f'{sig}|{axis}|{th}|{pupil}|{inp}|{med}', [])
                        if not rows:
                            continue
                        na = np.array([r[0] for r in rows])
                        for row, (key, i, name) in enumerate(KEYS):
                            v = np.array([np.nan if r[i] is None else r[i] for r in rows])
                            axes[row, col].plot(na, v, ls + mk, color=COL[th], lw=3, ms=8,
                                                mfc=COL[th] if med == 'air' else 'white', label=f'{lab}, {med}')
                        for target in (0.5, 0.9):
                            r = next((r for r in rows if abs(r[0] - target) < 1e-9), None)
                            if r:
                                lines.append(f'{sig} {axis} {lab:12s} {PUP[pupil]:26s} {INP[inp]:15s} {med:5s} NA {target}: '
                                             f'F {r[2]:.4f}  C {r[3]:.4f}  Q {r[4]:.4f}')
                axes[0, col].set_title(('Across the axis' if axis == 'x' else 'Along the axis'))
                axes[2, col].set_xlabel('NA')
                cut_inset(axes[0, col], axis, sig=sig, theta=0.0, eps=0.99 if pupil == 'ann' else 0.0, size=2.6,
                          where='lower left')               # every curve starts near 1 at low NA: this corner is empty
            for row, (key, i, name) in enumerate(KEYS):
                axes[row, 0].set_ylabel(name)
                for col in (0, 1):
                    axes[row, col].axhline(1, color='#888888', lw=1.5)
            fig.suptitle(f'{sig}, scalar against vector: {PUP[pupil]}, {INP[inp]}'
                         + ('\n(across the axis, θ = π is the θ = 0 curve)' if sig == '2PE' else ''), fontsize=30, y=1.02)
            h, l = axes[0, 1].get_legend_handles_labels()
            h0, l0 = axes[0, 0].get_legend_handles_labels()
            for hh, ll in zip(h0, l0):
                if ll not in l:
                    h.append(hh); l.append(ll)
            fig_legend(fig, h, l)
            name = f'linfoot_{sig.lower()}_{pupil}_{inp}.png'
            fig.savefig(os.path.join(OUT, name), dpi=300, bbox_inches='tight'); plt.close(fig)
            print('Saved ->', name)
open(os.path.join(OUT, 'linfoot_all.txt'), 'w').write('\n'.join(lines) + '\n')
print(f'{len(lines)} rows -> linfoot_all.txt')

# ── deck section: one slide per signal and angle, as the width slides (circular pupils, uniform input):
#    across | along; F, C, Q in colour; air solid (filled), water dashed (open) ──
LC = {'F': ('#1f77b4', 'Fidelity F', 2), 'C': ('#2ca02c', 'Structural content C', 3), 'Q': ('#9467bd', 'Correlation quality Q', 4)}
for sig, th, lab, theta in (('2CE', '0', 'θ = 0 and π', 0.0), ('2CE', 'pi2', 'θ = π/2', np.pi / 2), ('2PE', '0', 'θ = 0', 0.0),
                            ('2PE', 'pi2', 'θ = π/2', np.pi / 2), ('2PE', 'pi', 'θ = π', np.pi)):
    fig, axes = plt.subplots(1, 2, figsize=(18.5, 7.0), sharey=False)
    for ax, axis in zip(axes, ('x', 'z')):
        ax.axhline(1, color='#888888', lw=1.5)
        for key, (c, name, i) in LC.items():
            for med, ls, mk in (('air', '-', 'o'), ('water', '--', 's')):
                rows = M.get(f'{sig}|{axis}|{th}|circ|uni|{med}', [])
                ax.plot([r[0] for r in rows], [r[i] for r in rows], ls + mk, color=c, lw=3, ms=8,
                        mfc=c if med == 'air' else 'white', label=f'{key}, {med}')      # F, C, Q defined on the slides
        ax.set_xlabel('NA'); ax.set_xlim(0.15, 1.3)
        ax.set_title('Across the axis' if axis == 'x' else 'Along the axis')         # signal and θ: in the slide title
        cut_inset(ax, axis, sig=sig, theta=theta)
    axes[0].set_ylabel('Scalar against vector')
    h, l = axes[0].get_legend_handles_labels()
    fig_legend(fig, h, l)
    name = f'linfoot_na_{sig.lower()}_{th}.png'
    fig.savefig(os.path.join(OUT, name), dpi=300, bbox_inches='tight'); plt.close(fig)
    print('Saved ->', name)
