"""
Run all five figures from Romallosa, Bantang & Saloma (2003).

Usage:
    /opt/homebrew/Caskroom/miniforge/base/envs/dev/bin/python run_all.py

Figures generated in output/:
    fig1_contours.png   — 2-D contour plots (CW and 1-fs pulsed)
    fig2_profiles.png   — transverse + axial profiles
    fig3_energy.png     — energy fraction vs τ
    fig4_linfoot.png    — Linfoot F, S vs NA and τ (single-photon)
    fig5_linfoot_2p.png — Linfoot F, S vs τ (two-photon)

Set RUN_FIG[n]=False to skip figure n (e.g. skip the expensive Fig 1 or 3).
"""

import subprocess, sys, os

PYTHON = sys.executable
SCRIPTS = os.path.join(os.path.dirname(__file__), 'scripts')

RUN_FIG = {1: True, 2: True, 3: True, 4: True, 5: True}

figs = [
    (1, 'fig1_contours.py',   'Fig 1 — 2D contour plots (slow ~2 min)'),
    (2, 'fig2_profiles.py',   'Fig 2 — transverse + axial profiles'),
    (3, 'fig3_energy.py',     'Fig 3 — energy fraction (slow ~5 min)'),
    (4, 'fig4_linfoot.py',    'Fig 4 — Linfoot single-photon'),
    (5, 'fig5_linfoot_2p.py', 'Fig 5 — Linfoot two-photon'),
]

for fignum, script, desc in figs:
    if not RUN_FIG.get(fignum, True):
        print(f"Skipping {desc}")
        continue
    print(f"\n{'='*60}")
    print(f"{desc}")
    print('='*60)
    result = subprocess.run(
        [PYTHON, os.path.join(SCRIPTS, script)],
        check=False
    )
    if result.returncode != 0:
        print(f"  ERROR in {script} (exit {result.returncode})")

print("\nDone. Check output/ for figures.")
