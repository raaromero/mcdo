# Review stages

The package is built and reviewed one stage at a time. A stage is a self-contained
piece of physics with its own deck, its own figures and its own scripts. Work on a
stage is only merged to `main` after that stage's deck has been reviewed and accepted.

## Workflow per stage

```bash
python -m mcdo.deck --list-stages      # what the stages are and what each produces
python run_all.py --stage 1            # regenerate only that stage's figures
python -m mcdo.deck --stage 1          # build that stage's review deck
```

The deck lands in `output/deck/stage<N>_<key>.pptx` and ends with an
**Outputs for this stage** section listing the scripts it runs, the figures it
writes and the exact commands to reproduce both.

## Branches

- `rebuild` — where the work happens. Everything under review lives here.
- `locked` — accepted stages only. A stage lands here after you have reviewed
  its deck and folder and said so. Nothing is added to `locked` on the model's
  own judgement.

Once a stage is accepted:

```bash
git checkout locked
git merge rebuild --no-ff -m "Lock stage N - <name>"
git checkout rebuild
```

`locked` is local and is not pushed. Publishing to the public remote goes to
`refactor` and only on an explicit instruction; never to `main`.

## Accepted so far

| Stage | Accepted | Commit |
|---|---|---|
| 1 Romallosa (2003) replication | 2026-08-26 | `cb492fc` |
| 2-6 | not yet reviewed | |

## Stages

| # | Stage | Physics |
|---|-------|---------|
| 1 | Romallosa (2003) replication | Reproduce the published figures 1-5 for a few-cycle pulse at high numerical aperture |
| 2 | Gaussian input | Replace uniform illumination with a truncated Gaussian and quantify the effect of the truncation coefficient |
| 3 | Numerical aperture: uniform against Gaussian input | Locate the numerical aperture where scalar diffraction theory stops predicting the vector result, for each input |
| 4 | Annular apertures | Extend the depth of focus with a central obstruction and measure what it costs |
| 5 | Pulsed sources with annular apertures | Combine the two and test whether the depth-of-focus gain survives a few-cycle bandwidth |

## What a stage's outputs listing is derived from

`mcdo.deck.stage_outputs` reads the stage's own slides and reports the figures
those slides use, the scripts that generate them and the directories they land in.
Nothing is hardcoded, so the listing cannot drift out of step with the deck.

## Definition of done for a stage

- Every figure is produced by a script under `scripts/`, listed in `mcdo.deck.FIGURES`.
- `python run_all.py --stage <N>` reproduces every figure from scratch.
- `python -m pytest tests/` passes, including the presentation standards in
  `tests/test_standards.py`.
- The physics is checked by `python scripts/sanity_check.py`.
- The reviewer has seen the stage deck and accepted it.
