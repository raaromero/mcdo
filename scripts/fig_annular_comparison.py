"""Profiles across configurations, on axes that make them comparable.

Absolute microns hide the comparison: at numerical aperture 0.1 the focus is
hundreds of microns long and at 1.2 it is under a micron, so plotting both
against z in microns says more about the aperture than about the ring. Here
every axial profile is drawn against z divided by that configuration's own
unobstructed depth of focus, so the curve for obstruction ratio 0.9 literally
runs five times wider than the ratio-0 curve beside it and the extension can be
read straight off the axis. Transverse profiles are drawn against r divided by
the Airy radius for the same reason.

Two figures, one per input, each three rows (aperture) by two columns
(transverse, axial). The unobstructed disk is drawn in grey behind every panel
as the reference the other curves are measured against.

Reads the profiles saved by verify_annular_baseline.py. Recomputes nothing.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mcdo.style import apply as _apply_style
_apply_style()

from mcdo.figio import save_panels

LAM = 0.750
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', '03_annular')
DATA = os.path.join(OUT, 'annular_baseline.npz')

NA_CASES = [0.1, 0.8, 1.2]
EPS_SHOW = [0.0, 0.5, 0.9, 0.99]
INPUTS = [('uniform', 'uniform'),
          ('Gaussian, alpha = 4', 'gaussian')]
COLOR = {0.0: '#999999', 0.5: '#1f77b4', 0.9: '#d62728', 0.99: '#2ca02c'}


def main():
    if not os.path.exists(DATA):
        raise SystemExit(f"{DATA} not found — run verify_annular_baseline.py first")
    d = np.load(DATA, allow_pickle=True)

    na_col = d['na']
    in_col = np.array([str(v) for v in d['input']])
    eps_col = d['eps']

    def summary(xna, label, eps, field):
        m = (na_col == xna) & (in_col == label) & (np.abs(eps_col - eps) < 1e-9)
        return float(d[field][m][0]) if m.any() else float('nan')

    for label, slug in INPUTS:
        fig, axes = plt.subplots(3, 2, figsize=(20.5, 19.5))
        for row, xna in enumerate(NA_CASES):
            airy = 0.61 * LAM / xna
            dof0 = summary(xna, label, 0.0, 'depth_um')

            for eps in EPS_SHOW:
                key = f"{xna}|{label}|{eps}"
                if key + '|r' not in d:
                    continue
                pr, pz = d[key + '|r'], d[key + '|z']
                lab = ('no obstruction' if eps == 0 else f'ratio {eps:g}')
                gain = summary(xna, label, eps, 'gain')
                if eps != 0:
                    lab += f' ({gain:.1f}x)'
                width = 2.6 if eps == 0 else 2.0

                ax = axes[row, 0]
                ax.plot(pr[0] / airy, pr[1], '-', color=COLOR[eps], lw=width,
                        label=lab)
                ax = axes[row, 1]
                ax.plot(pz[0] / dof0, pz[1], '-', color=COLOR[eps], lw=width,
                        label=lab)

            for col, (xlab, xmax) in enumerate(
                    [('Radial position, in Airy radii', 4.0),
                     ('Axial position, in unobstructed depths of focus', 8.0)]):
                ax = axes[row, col]
                ax.axhline(0.5, color='#bbb', ls='--', lw=1.2)
                ax.set_xlim(0, xmax)
                ax.set_ylim(0, 1.05)
                ax.set_xlabel(xlab)
                ax.set_ylabel('Normalized intensity')
                short = 'uniform' if slug == 'uniform' else 'Gaussian, alpha = 4'
                ax.set_title(f'Numerical aperture {xna:g}, {short} input, 750 nm',
                             fontsize=12)
                ax.grid(alpha=0.25)
                ax.legend(fontsize=10)

        plt.tight_layout()
        save_panels(fig, fig.axes, os.path.join(OUT, 'panels'),
                    f'fig_annular_comparison_{slug}')
        out = os.path.join(OUT, f'fig_annular_comparison_{slug}.png')
        fig.savefig(out, dpi=300, bbox_inches='tight')
        plt.close(fig)
        print(f"Saved → {out}")

    print("\nAxial extension read off the normalized axis (should equal the gain):")
    for xna in NA_CASES:
        for label, _ in INPUTS:
            gains = "  ".join(f"ratio {e:g}: {summary(xna, label, e, 'gain'):5.2f}x"
                              for e in EPS_SHOW if e != 0)
            short = 'uniform' if label == 'uniform' else 'Gaussian'
            print(f"  NA {xna:<4} {short:<9} {gains}")


if __name__ == '__main__':
    main()
