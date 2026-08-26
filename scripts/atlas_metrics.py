"""Measure every configuration in the atlas, so each card carries its numbers.

Reads the fields that ``config_atlas.py`` saved and reports, for each
configuration, the transverse focal width and the axial depth of focus, both as
full widths at half maximum in micrometres, together with the ratio of the
depth of focus to that of the reference configuration in the same family.

    python scripts/atlas_metrics.py            # table to stdout
    python scripts/atlas_metrics.py --json     # machine-readable, for the deck

Nothing is recomputed here: the fields come straight from the atlas run.
"""

import argparse
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
OUT = os.path.join(os.path.dirname(__file__), '..', 'output', 'atlas')

FAMILIES = [
    ('NA', 'numerical aperture', lambda n: n.replace('field_NA', '').replace('.npz', '')),
    ('gaussian', 'truncation coefficient', lambda n: n.replace('field_at', '').replace('.npz', '')),
    ('annular', 'obstruction ratio', lambda n: n.replace('field_eps', '').replace('.npz', '')),
    ('pulsed', 'pulse duration', lambda n: n.replace('field_', '').replace('.npz', '')),
]


def fwhm(x, y):
    """Full width at half maximum of a centred profile, in the units of x."""
    y = np.asarray(y, dtype=float)
    if y.max() <= 0:
        return float('nan')
    y = y / y.max()
    above = np.where(y >= 0.5)[0]
    if above.size < 2:
        return float('nan')
    return float(x[above[-1]] - x[above[0]])


def measure(path):
    d = np.load(path)
    I, h, v = d['intensity'], d['h'], d['v']       # I is (axial, radial)
    ih = int(np.argmin(np.abs(h)))
    iz = int(np.argmax(I[:, ih]))
    return fwhm(h, I[iz]), fwhm(v, I[:, ih])


def collect():
    out = {}
    for fam, _label, key_of in FAMILIES:
        files = sorted(glob.glob(os.path.join(OUT, fam, 'field_*.npz')))
        rows = {}
        for f in files:
            width, depth = measure(f)
            rows[key_of(os.path.basename(f))] = {'width_um': width, 'depth_um': depth}
        if rows:
            base = list(rows.values())[0]['depth_um']
            for r in rows.values():
                r['depth_ratio'] = r['depth_um'] / base if base else float('nan')
        out[fam] = rows
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--json', action='store_true', help='emit JSON instead of a table')
    args = ap.parse_args(argv)

    data = collect()
    if args.json:
        print(json.dumps(data, indent=2))
        return 0

    for fam, label, _ in FAMILIES:
        rows = data.get(fam) or {}
        if not rows:
            continue
        print(f'\n{label}:')
        print(f"  {'value':>10} {'focal width (nm)':>18} {'depth of focus (µm)':>22} {'relative depth':>16}")
        for k, r in rows.items():
            print(f"  {k:>10} {r['width_um'] * 1000:>18.0f} {r['depth_um']:>22.2f} "
                  f"{r['depth_ratio']:>16.2f}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
