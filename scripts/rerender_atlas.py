"""Redraw atlas cards from the saved fields, without recomputing them.

config_atlas.py computes the field and draws the card in one pass, so a change
to how a card looks costs a full recomputation. Every field is already saved
beside its card as a .npz, so a presentation change needs only a redraw.

    python scripts/rerender_atlas.py              # every family
    python scripts/rerender_atlas.py annular_grid # one family
"""

import glob
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')

from mcdo.atlascard import render_card

ROOT = os.path.join(os.path.dirname(__file__), '..')
ATLAS = os.path.join(ROOT, 'output', 'atlas')
LAM = 0.750


FAMILY = {
    'annular_grid': 'Annular Aperture',
    'truncation_grid': 'Truncated Gaussian',
    'pulsed_grid': 'Pulsed Illumination',
    'pulsed_illumination': 'Pulsed Illumination',
    'na': 'Numerical Aperture',
    'gaussian': 'Gaussian Apodization',
    'annular': 'Annular Aperture',
    'axicon': 'Axicon',
    'pulsed': 'Pulsed Illumination',
}
DURATION = {'cw': 'continuous wave', '1fs': '1 fs pulse', '2fs': '2 fs pulse'}


def _num(token):
    """`0p99` reads as 0.99; a blind replace of p turns eps into e.s."""
    return token.replace('p', '.')


def _title(family, stem):
    """A readable title from the file stem.

    The first version replaced every p with a period, so `eps0p9` came out as
    `e.s0.9` and the illumination stayed lowercase. This parses the tokens.
    """
    parts = []
    for tok in stem.split('_'):
        if tok.startswith('na') and tok[2:3].isdigit():
            parts.append(f'numerical aperture {float(_num(tok[2:])):g}')
        elif tok.startswith('eps'):
            parts.append(f'ε = {float(_num(tok[3:])):g}')
        elif tok.startswith('at') and tok[2:3].isdigit():
            a = float(_num(tok[2:]))
            parts.append('uniform' if a == 0 else f'α = {a:g}')
        elif tok in DURATION:
            parts.append(DURATION[tok])
        elif tok in ('uniform', 'gaussian'):
            parts.append('uniform' if tok == 'uniform' else 'Gaussian')
        else:
            parts.append(tok)
    head = FAMILY.get(family, family.replace('_', ' ').title())
    return f"{head}: " + ', '.join(parts)


def main(argv):
    families = argv[1:] or sorted(
        d for d in os.listdir(ATLAS) if os.path.isdir(os.path.join(ATLAS, d)))
    total = 0
    for fam in families:
        fields = sorted(glob.glob(os.path.join(ATLAS, fam, 'field_*.npz')))
        for f in fields:
            stem = os.path.basename(f)[len('field_'):-len('.npz')]
            d = np.load(f)
            I = d['intensity'] / d['intensity'].max()
            # a pulsed card is drawn against the same pupil at continuous
            # wave, which is the comparison the card exists to make
            base_tr = base_ax = None
            base_label = None
            for suffix in ('_1fs', '_2fs'):
                if not stem.endswith(suffix):
                    continue
                cw_path = os.path.join(ATLAS, fam,
                                       f'field_{stem[:-len(suffix)]}_cw.npz')
                if not os.path.exists(cw_path):
                    cw_path = os.path.join(ATLAS, fam,
                                           f'field_{stem[:-len(suffix)]}.npz')
                if os.path.exists(cw_path):
                    c = np.load(cw_path)
                    if c['intensity'].shape == d['intensity'].shape:
                        B = c['intensity'] / c['intensity'].max()
                        base_tr = B[int(np.argmin(np.abs(c['v'])))]
                        base_ax = B[:, int(np.argmin(np.abs(c['h'])))]
                        base_label = 'Same pupil, continuous wave'
            render_card(d['h'], d['v'], I, _title(fam, stem),
                        os.path.join(ATLAS, fam, f'{stem}.png'),
                        base_tr, base_ax, airy_um=0.61 * LAM / 0.8,
                        base_label=base_label or 'Uniform disk, continuous wave',
                        curve_label=None)
            total += 1
        if fields:
            print(f'{fam}: {len(fields)} cards redrawn')
    print(f'{total} cards redrawn from saved fields, nothing recomputed')


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
