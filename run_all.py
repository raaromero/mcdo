"""Regenerate every figure the slide deck depends on, then rebuild the deck.

Usage:
    python run_all.py                 # everything, then assemble the deck
    python run_all.py --only fig1_contours.py verify_annular.py
    python run_all.py --skip fig1_contours.py fig3_energy.py   # skip the slow ones
    python run_all.py --list          # show what would run, in order
    python run_all.py --stale         # only scripts whose figures are out of date
    python run_all.py --no-deck       # figures only

The work list is derived from :data:`mcdo.deck.FIGURES`, so it can never drift
from what the deck actually needs: declare a figure in the deck and it is
regenerated here automatically.
"""

import argparse
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from mcdo.deck import FIGURES, OUT  # noqa: E402

# Scripts that take minutes rather than seconds — reported so a run is predictable.
SLOW = {"fig1_contours.py", "fig3_energy.py", "config_atlas.py", "vector_atlas.py"}


def work_list():
    """Unique generating scripts, in a stable order, with the figures each owns."""
    owns: dict[str, list[str]] = {}
    for _key, (rel, script) in FIGURES.items():
        owns.setdefault(os.path.basename(script), []).append(rel)
    return sorted(owns.items())


def is_stale(figures):
    """True if any figure is missing or older than the script that makes it."""
    for rel in figures:
        path = os.path.join(OUT, rel)
        if not os.path.exists(path):
            return True
    return False


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", nargs="+", metavar="SCRIPT", help="run just these scripts")
    ap.add_argument("--skip", nargs="+", metavar="SCRIPT", default=[], help="skip these scripts")
    ap.add_argument("--list", action="store_true", help="show the work list and exit")
    ap.add_argument("--stale", action="store_true", help="only scripts with missing figures")
    ap.add_argument("--no-deck", action="store_true", help="skip the deck rebuild")
    ap.add_argument("--stage", default=None,
                    help="run only the scripts a review stage needs")
    args = ap.parse_args(argv)

    if args.stage:
        from mcdo.deck import stage_outputs
        _, stage_scripts, _ = stage_outputs(args.stage)
        args.only = [os.path.basename(sc) for sc in stage_scripts]

    items = work_list()
    if args.only:
        wanted = set(args.only)
        items = [(s, f) for s, f in items if s in wanted]
    items = [(s, f) for s, f in items if s not in set(args.skip)]
    if args.stale:
        items = [(s, f) for s, f in items if is_stale(f)]

    if args.list:
        for script, figs in items:
            mark = "  (slow)" if script in SLOW else ""
            print(f"{script}{mark}  ->  {len(figs)} figure(s)")
        print(f"\n{len(items)} script(s), {sum(len(f) for f in dict(items).values())} figure(s)")
        return 0

    if not items:
        print("Nothing to do.")
    failures = []
    for i, (script, figs) in enumerate(items, start=1):
        mark = "  (slow)" if script in SLOW else ""
        print(f"\n{'=' * 64}\n[{i}/{len(items)}] {script}{mark} — {len(figs)} figure(s)\n{'=' * 64}")
        started = time.time()
        result = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", script)], check=False)
        elapsed = time.time() - started
        if result.returncode != 0:
            failures.append(script)
            print(f"  ERROR in {script} (exit {result.returncode})")
        else:
            print(f"  done in {elapsed:.0f}s")

    if failures:
        print("\nFailed: " + ", ".join(failures))

    if not args.no_deck:
        print(f"\n{'=' * 64}\nAssembling the deck\n{'=' * 64}")
        subprocess.run([sys.executable, "-m", "mcdo.deck"], cwd=ROOT, check=False)

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
