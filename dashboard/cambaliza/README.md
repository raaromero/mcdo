# Two-Color Excitation dashboard

Cambaliza & Saloma (2000) replicated at NA 0.5, then extended from low to high NA in air and water: circular and
annular (ε = 0.99) pupils, uniform and Gaussian (α = 4) input, paraxial scalar against vector (Richards–Wolf).
Static site (Vite + TypeScript + D3), laid out and styled after `~/nba-thread-counts/web`.

- **Home**: the main findings as tiles, each opening its Insights card.
- **Insights**: one finding per card, with a small chart and links into the dashboards.
- **Profiles**: 2PE and 2CE across (x) or along (z) the axis at one NA, θ = 0, π/2, π; hover for values.
- **Widths**: width across the axis and depth of focus against NA; click to move the NA rule.
- Options sit in the side panel; the URL keeps the view, so links are shareable. "Download image" saves a PNG.

## Data

```bash
python scripts/cambaliza2000_high_na_pupils.py     # widths.csv, dlambda.csv (about 1 h)
python scripts/dashboard_cambaliza_data.py         # -> dashboard/cambaliza/public/data, public/img (a few minutes)
```

The data and images are generated and not committed (see `.gitignore`), like `output/`.

## Run

```bash
cd dashboard/cambaliza
npm install
npm run dev          # http://localhost:5173
npm run build        # static site in dist/
```
