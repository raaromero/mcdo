"""Assemble one review folder per stage.

Copies the figures a stage presents into ``output/review/stage<N>_<key>/``,
numbered in slide order and named after the slide they appear on, so the folder
can be flipped through in Finder in the same order as the deck. A README lists
the source script and output path behind every figure.

    python scripts/make_review_folder.py --stage 1
    python scripts/make_review_folder.py --all
"""

import argparse
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mcdo.deck import DECK, FIGURES, OUT, STAGES, stage_outputs

REVIEW = os.path.join(OUT, 'review')


def _slug(text):
    """A filename-safe form of a slide title, with no underscores."""
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[\s_]+', '-', text)[:70]


def build_stage(stage_id):
    st = STAGES[stage_id]
    figs, scripts, _ = stage_outputs(stage_id)
    dest = os.path.join(REVIEW, f"stage{stage_id}-{st['key'].replace('_', '-')}")
    if os.path.isdir(dest):
        shutil.rmtree(dest)          # a stale figure here would be reviewed as current
    os.makedirs(dest)

    keep, rows, index = False, [], 0
    for item in DECK:
        if item[0] == 'section':
            keep = item[1] in st['sections']
        elif keep and item[0] == 'slide' and item[3] in FIGURES:
            index += 1
            rel, script = FIGURES[item[3]]
            src = os.path.join(OUT, rel)
            name = f"{index:02d}-{_slug(item[1])}.png"
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(dest, name))
            else:
                name += "  (MISSING)"
            rows.append((name, item[1], rel, script))

    with open(os.path.join(dest, 'README.md'), 'w') as fh:
        fh.write(f"# {st['title']}\n\nFigures in the order they appear in the deck.\n\n")
        fh.write("Rebuild everything here:\n\n```bash\n"
                 f"python run_all.py --stage {stage_id}\n"
                 f"python scripts/make_review_folder.py --stage {stage_id}\n```\n\n")
        fh.write("| File | Slide | Source | Script |\n|---|---|---|---|\n")
        for name, title, rel, script in rows:
            fh.write(f"| {name} | {title} | output/{rel} | {script} |\n")
    print(f"{st['title']}: {len(rows)} figure(s) → {dest}")
    return dest


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--stage', choices=sorted(STAGES))
    ap.add_argument('--all', action='store_true')
    args = ap.parse_args(argv)
    ids = sorted(STAGES) if args.all or not args.stage else [args.stage]
    for sid in ids:
        build_stage(sid)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
