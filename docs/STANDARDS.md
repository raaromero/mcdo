# Figure and deck standards

Single source of truth for anything that ends up in a figure or a slide.
`mcdo/deck.py` and every script in `scripts/` follow this.

## Physical parameters (identical across all scripts)

| Symbol | Meaning | Value |
|---|---|---|
| λ_c | carrier wavelength | 0.750 µm |
| n | medium refractive index | 1.3 |
| NA | numerical aperture | 0.8 unless the study sweeps it |
| α | aperture half-angle | arcsin(NA / n) |

Any script that needs a different value states why in its docstring. The gate
`scripts/sanity_check.py` uses these same values.

## Reproducibility rules

1. **Never recompute a figure that a canonical script already produces.**
   Find the script, re-run it. `mcdo/deck.py` computes nothing — it assembles.
2. Every deck figure is declared in `mcdo.deck.FIGURES` as
   `key -> (path under output/, script that regenerates it)`. A missing figure
   makes the build print that command rather than degrade silently.
3. Multi-panel figures call `mcdo.figio.save_panels`, which writes each panel
   separately for one-plot-per-slide use. The same computation serves both.
4. Rebuild everything with `python run_all.py`; deck only with
   `python -m mcdo.deck`; validate with `python scripts/sanity_check.py`.

## Axis-label vocabulary (use verbatim)

| Quantity | Label |
|---|---|
| radial position | `Radial position r (μm)` |
| axial position | `Axial position z (μm)` |
| optical radial coordinate | `Optical radial coordinate v` |
| optical axial coordinate | `Optical axial coordinate u` |
| intensity | `Normalized intensity` |
| on-axis intensity | `Normalized on-axis intensity` |
| numerical aperture | `Numerical aperture` |
| obstruction ratio | `Obstruction ratio` |
| pulse duration | `Pulse width (fs)` |
| pupil radius | `Normalized pupil radius ρ` |
| pupil amplitude | `Input amplitude A(ρ)` |
| depth of focus | `Depth of focus, relative` |
| spot-size error | `FWHM deviation from scalar (%)` |
| point-by-point error | `RMSE against scalar` |

Rules: sentence case, units in parentheses, no abbreviations such as
`norm. I`, and **no underscores** anywhere a reader can see them — write
`α_t` as mathtext `$\alpha_t$`, never `alpha_t` or `X_NA`.

## Figure conventions

- Legends outside the axes: `loc="upper left", bbox_to_anchor=(1.02, 1), frameon=False`.
- No internal project vocabulary in titles (no "Phase 1/2/3" — those are
  planning labels, not physics).
- Panel letters `(a)`, `(b)` belong to the combined figure only; `save_panels`
  strips them automatically so a standalone panel reads on its own.
- 2-D fields: heat map plus contours, or labelled iso-intensity contours in the
  Romallosa style, normalized to a peak of 100.
- Every configuration card shows the 2-D map with transverse and axial
  cross-sections, and the uniform continuous-wave baseline dotted for reference
  (`scripts/config_atlas.py`).

## Slide conventions

- One message per slide; one figure per slide.
- A figure must stand alone: if it is the only thing a reader sees, the point
  must still land.
- Bullets are full phrases, not fragments, and are not bold.
- Equations live in the slide notes as LaTeX, ready to paste.
- Section dividers separate every major part; references last.
- Terminology follows the progress report, not invented phrasing.

## Figure panels and slide wiring

Multi-panel figures are saved panel-by-panel by `mcdo.figio.save_panels`, and
the deck points each slide at one panel file. Two hazards follow from that, and
both are now guarded:

1. **Re-indexing.** Changing a figure's layout (say 2x2 to 2x3) renumbers every
   panel, so a slide keeps its index but silently gets a different plot.
   `save_panels` writes `<prefix>_panels.json` recording what each index holds,
   and `test_panel_index_matches_panel_content` fails when a slide names a
   numeric setting the panel does not.
2. **Orphans.** A layout with fewer panels leaves the extra files behind, where
   review folders and decks pick them up as current. `save_panels` deletes its
   own previous panels before writing, and
   `test_declared_figures_exist_on_disk` fails if the deck declares a figure
   that is not there.

Panels a slide does not use are fine — a figure often carries a breakdown that
the deck deliberately does not show.

## What is plotted

`mcdo/components.py` holds the one definition of each focal intensity:

| Name | Expression | Use |
|---|---|---|
| `full` | `\|I0\|^2 + \|I2\|^2 + 2\|I1\|^2` | total intensity, all components — the default for all new results |
| `ex_only` | `\|I0\|^2 + \|I2\|^2/2` | transverse component only |
| `scalar` | `\|I0\|^2` | scalar Debye, no polarization |
| `y_cut` | `\|I0 - I2\|^2` | x-polarized intensity along the y-axis — reproduction of published figures only |

The Romallosa replication uses `y_cut` because the paper does. Everything after
it uses `full`, and the deck states the change where it happens.

Atlas scripts take `--component {full,ex,scalar,ycut}` and write each choice to
its own directory, so one output type never overwrites another.
