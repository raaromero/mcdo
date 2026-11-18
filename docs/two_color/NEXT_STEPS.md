# Two-color excitation with pulses: what is next, and how to run it

Written 2026-11-12 so that a new session, of any model, can continue without the earlier conversation. Read this
file, then `docs/review/07_two_color_pulses/review_07.pdf` (what was checked) and
`docs/two_color/pulse_derivations.pdf` (the derivations). Do the steps in order. Each step has a command, a check
with a number that must be met, and what to do if it is not met.

## 0. Rules that hold for every step

1. Do not install anything (pip, npm, brew) without the user's explicit permission.
2. Do not change `pulse_results.pptx` or the main deck. New slides go in `pulse_delay.pptx` or a new backup deck.
3. Do not deploy the dashboard and do not push to the remote without the user's go-ahead. The remote is public.
4. Use the tables of the fields (`cambaliza2000_fast_field.py`) for sweeps, and recompute samples the long way
   after every sweep (step H3 below). A sweep without a passing sample check is not a result.
5. Paraxial scalar results are drawn for NA ≤ 0.5.
6. Writing, in chat, slides and documents: full sentences; "I", not "we"; pairs named by wavelength (350-nm pairs
   = 750 + 656, 375-nm pairs = 750 + 750, 328-nm pairs = 656 + 656); none of "only", "far", "every", "fails";
   own results are labelled "Current work"; no "Label: fragment" bullets and no arrows.
7. Figures: 600 DPI; fonts 32 (title), 28 (axis labels), 24 (ticks); line width ≥ 2; about 11 × 10 in per panel;
   at most two panels across; legends never over the data.
8. Do what was asked and no more. Flag a physics or math problem before working around it.

Python is `/opt/homebrew/Caskroom/miniforge/base/envs/dev/bin/python` (below: `$P`). Run from
`/Users/raaromero/mcdo_2ce`. `output/` is a link to `/Users/raaromero/mcdo_dev/output` and is not in git.

## 1. The harnesses

Run these before trusting any new number. All must pass.

| Id | Command | Passes when |
|----|---------|-------------|
| H1 | `$P -m pytest tests -q -x` | all tests pass (1074 on 2026-11-11, about 3 min) |
| H2 | `$P -m pytest tests/test_twobeam.py -q -k divergence` | passes: ∇·E = 0 for the vector field (E_z = −2 I₁ cos φ) |
| H3 | `$P scripts/cambaliza2000_delay_sample_check.py` | last line reads `SAMPLES … (pass)`: peaks within 1e-8 of the long way, stored profiles within 1e-6 |
| H3p | `SAMPLES=polp $P scripts/cambaliza2000_delay_sample_check.py` | the same, for the runs with polarization p |
| H6 | `$P scripts/cambaliza2000_delay_allpairs_check.py` (about 15 min) | last line reads `ALL PAIRS … (pass)`: the total with all pairs, recomputed as a sum over pairs of frequencies with no time grid, within 5e-3 of the stored profiles (1.1e-4 on 2026-11-12, 32 cases) |
| H4 | closed form against stored data (below) | collinear lenses, 100 fs: peak at Δt = τ is 0.2500 ± 0.0001; facing lenses, NA 0.2, 100 fs: 0.513 ± 0.01 |
| H5 | peak at the edge of the line (below) | no row that is drawn in a figure has `|pos| > 0.98 ×` the half-length of its line |

H4 and H5 in one command:

```bash
$P - <<'EOF'
import sys; sys.path.insert(0, 'scripts'); sys.path.insert(0, '.')
import cambaliza2000_pulses_delay as P
t = P.load('rw_air', 'coarse').query("sig == '2ce' and tau == 100 and delay_tau == 1")
print('H4 collinear', t.query("theta == '0' and cut == 'z'").rel_cross.agg(['min', 'max']).round(4).tolist(), '(0.2500)')
print('H4 facing NA 0.2', round(float(t.query("theta == 'pi' and cut == 'z' and na == 0.2").rel_cross.iloc[0]), 3), '(0.513)')
EOF
```

The formulas behind H4 are Eqs. for the temporal overlap, F(Δt)/F(0) = exp(−2 ln2 Δt²/τ²), and for facing lenses,
peak = exp[−4 ln2 z_m²/(D² + G²)] with z_m = cΔt/2n, G = cτ/(√2 n) and D the continuous-beam depth of focus of 2CE
(3.56 µm at NA 0.5, growing as 1/NA²). They are derived in `pulse_derivations.pdf`, Sections 6 and 7.

## 2. Where things stand (2026-11-12)

Done and checked:
- Delay sweep, 16 sets (scalar and vector; air, water, oil; circular, Gaussian input α = 4, annular ε = 0.5, 0.9,
  0.99), coarse grid (Δt = 0 to 2τ in steps of 0.1τ; τ = 5, 10, 20, 30, 50, 100 fs) and fine grid (0.1 fs; τ = 5,
  10, 20 fs). Data: `output/08_two_color/cambaliza2000/pulses/delay_sweep/<set>/na<NA>_<grid>.parquet` and `.npz`;
  read with `cambaliza2000_pulses_delay.load(set, grid)`.
- Review against the four papers, with one correction to the code (E_z factor, see review_07, Section 4).
- Figures (`scripts/cambaliza2000_pulses_delay_plot.py`) and the backup deck (`scripts/make_pulse_delay_deck.py`).
- Documents: `docs/review/07_two_color_pulses/review_07.pdf`, `docs/two_color/pulse_derivations.pdf`,
  `docs/progress/work_to_date.pdf` (Section 7 has the results by lens angle), and the derivations in three parts,
  `docs/two_color/derivations/{1_scalar_focal_field,2_vector_focal_field,3_two_beams}.pdf` (shared `preamble.tex`;
  numbers from `scripts/derivation_checks.py`). Build each with `tectonic <name>.tex` in its folder.

## 3. Steps

### Step 1. Close the E_z correction (done 2026-11-12)
The pupil study was regenerated. In `widths.csv` (5712 rows) the 208 rows with `signal = 2PE`, `theta = π/2`,
`model = p` changed, as predicted, and no other row did. In air with the circular pupil the 2PE width changed from
0.802 to 0.781 µm at NA 0.5 and from 0.721 to 0.729 µm at NA 0.7. No figure, slide or dashboard table shows that
case: the polarization figures draw 2CE, and the dashboard takes the models s and scalar. `dlambda.csv` moved by up
to 3e-6 in all models, the scalar one included, which is the script having changed since it was last run, not E_z.
What is left: run H1 and H2 before the commit of Step 3.

### Step 2. Polarization with pulses and a delay (done 2026-11-12)
Set `rw_air_polp` (vector model, air, NA 0.3, 0.5, 0.7, coarse and fine grids), each beam polarized in the plane
of the lens axes. Six samples recomputed the long way pass (peaks within 1.8e-11).
- The 350-nm pairs along the axis with collinear and facing lenses equal those of polarization s to 2e-12, as they
  must.
- Crossed lenses: the fringes against the delay are about a quarter as deep as with s (amplitude of the oscillating
  part about 0.05 against 0.21 at NA 0.5 and 5 fs). They are not absent, since E_z away from the focus mixes the
  components. The 350-nm pairs fall with the delay in the same way. The 2CE spot is wider (0.83 against 0.75 µm
  at NA 0.5).
- Facing lenses with all pairs: beam 2 polarized in the plane has the opposite sign after the rotation by π, so
  the fringes against the delay are shifted by half a period relative to s. `rel_total` is over the value at no
  delay, which is then near a minimum at the focus, so `rel_total` exceeds 1 across x at 5 and 10 fs. Use
  `peak_total`, not `rel_total`, for that case.
- To separate the fringes from the smooth part of `rel_total`, subtract a 5-fs Savitzky–Golay smooth (window 51
  points of the fine grid, order 3).
Not on a slide yet. If the user asks: one backup slide, two panels (s and p), same axes, in `pulse_delay.pptx`.

Open question for the user, do not decide it: for real molecules the two-photon absorption of two photons with
perpendicular polarizations differs from that of parallel ones by a factor that depends on the molecule. The
model does not include this factor.

### Step 3. Commit and push the branch `two-color`
Blocked on three answers from the user (asked 2026-11-11):
1. `docs/two_color/walkthrough/walkthrough.src.md` and `walkthrough.md` state the dashboard password in their
   subtitle. Remove that phrase before any commit unless the user says otherwise.
2. Whether the walkthrough screenshots (15 MB) go in the repository.
3. Commit message trailer: `HANDOFF.md` says plain messages with no automated trailers.

Then: `git add -A`; `git ls-files | grep -c gbp_mc_external` must print 0; `git status --short | grep -c "^A.*output"`
must print 0; run H1; commit; push only after the user says to.

### Step 4. Dashboard (optional, on request)
`$P scripts/export_pulse_delay_dashboard.py` writes the delay data for the dashboard. Build with
`cd dashboard/cambaliza && npm run build`. Do not deploy; the user runs
`cd dashboard/cambaliza && vercel deploy --prod --yes`.

### Dashboard highlights
The tab Highlights (first in the nav, `#mode=hl`) shows one card per key result, grouped by lens angle and delay. A
click applies the settings of that result and opens its view; a banner above the view gives the result, a link back
to the cards and the previous and next results, and the URL keeps `hl=<id>`. Once the view has drawn, the plot named by
the card's `scroll` is brought into view.
- The highlights are defined in `dashboard/cambaliza/src/highlights.ts`, one entry each:
  `{ id, group, text, opens, preset, scroll? }`. The array order is the order of the cards and of Previous and Next.
- To add one, add an entry: `text` from `docs/progress/work_to_date.tex` (approved wording), `opens` naming the view
  and the plot, `preset` with the state keys of `S` in `src/main.ts` (keys left out take their defaults), and `scroll`
  with the id of the plot: in Pulse results each chart cell is `c-<chart key>` (`c-ntw`, `c-a180`, `c-dpk`, `c-xpk`,
  `c-xpos`, `c-xpu`, `c-xfi`, …) and the section of the delay against NA is `sec-delay-na`; in Scalar vs vector at high
  NA the profiles are `c-nax` and `c-naz`. Check that the view shows the quantity of the sentence and that each value
  is an option of its control.
- 21 cards (2026-11-18): eight for continuous beams at high NA (the scalar against vector card reads "At NA 0.9 the
  paraxial 2CE depth of focus is 36% longer than the vector one (1.10 against 0.81 µm); at NA 0.5 it is 7% longer."),
  five for pulses without delay and eight for the delay, five of which open the section "Delay between the pulses,
  against NA" (facing lenses at low NA, facing lenses at NA 0.5 and above, pupils, fringes, the two polarizations).
  Two were added on 2026-11-18 for the maps of the PSF in the x–z plane: `cw-2pe-collinear` (2PE, θ = 0, NA 0.9) and
  `cw-2ce-crossed` (2CE, θ = π/2, NA 0.7). The maps of Scalar vs vector at high NA are drawn for the first angle of
  `ths`, so a highlight of the maps of one angle sets that angle alone.
- The section "Delay between the pulses, against NA" of Pulse results reads `public/data/pulse_delay_sweep.json`
  (0.82 MB), written by `$P scripts/export_pulse_delay_sweep_dashboard.py` from the stored delay tables: rw_air, the
  Gaussian input α = 4 and the annular pupils ε = 0.5 and 0.9 on the coarse grid (all NAs and τ), and rw_air and
  rw_air_polp on the fine grid (5, 10, 20 fs). Its controls are the state keys `xth`, `xtau`, `xnas`, `xna`, `xpol`.
  The older `pulse_delay.json` (scalar model, NA 0.5) is unchanged and still feeds the delay charts above the section.
- Build and preview locally: `cd dashboard/cambaliza && npm run build && npx vite preview --port 4173`, then open
  `http://localhost:4173/#mode=hl`. Do not deploy; the user runs `cd dashboard/cambaliza && vercel deploy --prod --yes`.

### Step 5. Candidates after that, for the user to choose
- Pulses that are not transform-limited (chirp), which lengthen the pulse at the focus.
- 2CE with pulses through a scattering medium: the Monte Carlo model of `docs/review/06` with the pulse model.
- A broad absorption band in place of the narrow 350-nm level (signal ∫ I₁ I₂ dt for the 350-nm pairs).
- Unequal pulse widths τ₁ ≠ τ₂ (the overlap becomes exp[−4 ln2 Δt²/(τ₁² + τ₂²)]).

## 4. Adding a run

```bash
MODEL=rw|paraxial MEDIUM=air|water|oil EPS=<ε> APOD=<α> POL=s|p GRID=coarse|fine NAS=0.3,0.5 \
  $P scripts/cambaliza2000_pulses_delay.py
```
New runs write new files (`<model>_<medium>[_eps<ε>][_gauss<α>][_polp]/na<NA>_<grid>.*`) and do not rewrite
others. Add two or more samples of each new set to `SAMPLES` in `scripts/cambaliza2000_delay_sample_check.py`
and run H3. Annular pupils with ε = 0.99 take hours; the others take minutes.

### Decks
Each deck is rebuilt by its script; never edit a `.pptx` by hand. The two 2CE decks and their concise versions come from
one script, `scripts/make_2ce_decks.py`. Slides carried over from the meeting of 2026-10-29 take their text word for word
from `scripts/approved_slides_2ce_meeting.py`, and the delay slides come from `scripts/pulse_delay_slides.py`, which
`scripts/make_pulse_delay_deck.py` shares.

```bash
DECK=high_na $P scripts/make_2ce_decks.py          # -> output/08_two_color/decks/2ce_high_na.pptx (38 slides)
DECK=high_na MAIN=1 $P scripts/make_2ce_decks.py   # -> output/08_two_color/decks/2ce_high_na_main.pptx (16 slides)
DECK=pulses $P scripts/make_2ce_decks.py           # -> output/08_two_color/decks/2ce_pulses.pptx (39 slides; Part 2 is the delay)
DECK=pulses MAIN=1 $P scripts/make_2ce_decks.py    # -> output/08_two_color/decks/2ce_pulses_main.pptx (16 slides)
D=output/08_two_color/decks
$P scripts/pptx_resave_pdf.py $D/2ce_high_na.pptx $D/2ce_high_na_main.pptx $D/2ce_pulses.pptx $D/2ce_pulses_main.pptx
# re-saves each deck through PowerPoint, which opens on the user's screen, so that Keynote loads it, and writes the PDF
# beside it; look at the PDF pages (pdftoppm -r 100 -png) before telling the user anything
```

The figures of at most two panels are drawn by the plotting scripts with an option that writes new files and leaves the
files of the frozen decks as they are; the maps of the PSF in the x–z plane have their own script:

```bash
PANELS=1 $P scripts/cambaliza2000_pulse_time_frequency.py   # pulse_waves_{spectrum,sum}.png, pulse_gaussian_{time_frequency,wavelength}.png
PANELS=1 $P scripts/cambaliza2000_pulses_gate_plot.py       # sweep/profiles_100fs_2ce_{0_pi,pi2}.png
PANELS=1 $P scripts/cambaliza2000_pulses_na_sweep_plot.py   # na_sweep/tau_cw_vs_na[_pupils]_<sig>_{pi,0_pi2}.png (scalar to NA 0.5)
PANELS=1 $P scripts/fig_lim2002_slides.py                   # lim2002/slides/axial_2ce_paraxial_vector_na0.5_na0.9.png
$P scripts/cambaliza2000_high_na_maps.py                    # high_na/maps/psf_<2ce|2pe>_<0|pi2|pi>.png and widths.txt
```

### Guides
Each of the two decks has a dashboard guide (one card per slide of the full deck, with the title and the bullets of the
slide word for word, the link, the settings as a sentence and a screenshot) and a presenter guide (per slide, the main
point, what to say, the likely questions, and whether the slide is also in the concise deck). The concise decks have
the same titles and bullets, so the same guides serve them. The dashboard guides link to the local dashboard on port
4317 (`npm run dev` in `dashboard/cambaliza`).

```bash
cd docs/two_color/walkthrough
# screenshots: npm run build and npx vite preview --port 4173 in dashboard/cambaliza, headless Chromium with
# --remote-debugging-port=9333, then (ONLY=<id>,<id> limits the screenshots to those steps)
node shoot.mjs steps_2ce_high_na.json img_2ce_high_na
node shoot.mjs steps_2ce_pulses.json img_2ce_pulses
$P build.py 2ce_high_na   # walkthrough_2ce_high_na.src.md + steps_2ce_high_na.json -> $OUT/decks/2ce_high_na_guide.{html,pdf}
$P build.py 2ce_pulses    # walkthrough_2ce_pulses.src.md + steps_2ce_pulses.json -> $OUT/decks/2ce_pulses_guide.{html,pdf}
cd ..
# presenter guides: pandoc, then headless Chromium --print-to-pdf, as in the header of each file
CHR="$HOME/Library/Caches/ms-playwright/chromium-1140/chrome-mac/Chromium.app/Contents/MacOS/Chromium"
for d in 2ce_high_na 2ce_pulses; do
  pandoc presenter_guide_$d.md -s --embed-resources --css presenter_guide.css -o $OUT/decks/presenter_guide_$d.html
  "$CHR" --headless=new --no-pdf-header-footer --print-to-pdf=$OUT/decks/presenter_guide_$d.pdf file://$OUT/decks/presenter_guide_$d.html
done
```

`$OUT` is `/Users/raaromero/mcdo_dev/output/08_two_color`. If the wording of a slide changes, read the deck with
python-pptx, copy the new title and bullets into the card of both guides (the bullets go in the blue box of the
dashboard guide) and rebuild. The `.src.md` files and the presenter guides state no password.
