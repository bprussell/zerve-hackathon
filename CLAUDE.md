# The Ash Borer Effect — ZerveHack Entry

## What This Is
Hackathon entry for ZerveHack (Devpost). Dual-track analysis: (A) do golf scores improve after EAB kills ash trees on courses, (B) model EAB spread and project ash extinction timeline. See `ash-borer-plan.md` for the full roadmap.

## Current Phase
**Phase 3: Build in Zerve** (Weeks 5-6)
- Phase 2 complete (Issues #6, #7, #8, #12 all closed)
- **Issue #9 closed** — all 8 blocks running in Zerve (4 analysis + 4 viz), DAG wired
- Still need: #10 (Fleet), #11 (App Builder)
- Drafts ready: Devpost summary, demo storyboard, social media post

## Track A Result
DiD with player + course + year fixed effects:
- Treatment effect: **-0.759 strokes** (SE 0.245, p=0.002)
- 5 treatment courses (with both pre/post data), 84 total courses, 23,444 obs (4-round scores), 2009-2022
- Dependent variable: score_vs_par (strokes relative to par)
- The beetle helps your golf game.

## Track B Result
Polynomial ridge regression on spatial features (Python/sklearn):
- **861 training counties** (known EAB detections, 2002-2022)
- **CV MAE: 2.32 years**, R2: 0.635
- Median spread speed: **53 km/year** from Wayne County, MI origin
- County-level arrival year predictions are speculative (model extrapolates poorly for distant counties)
- Viz focuses on ash density + EAB overlay rather than predicted arrival years

## Track B Calibrated Extinction (Issue #8)
Multi-year FIA data (40,959 records, 16 states, 2005-2023) calibrates mortality:
- **Literature**: 99% mortality in 6 years (mature canopy trees in core zone)
- **Observed**: 3.82% annual mortality (all trees incl. seedlings/regeneration)
- **50% ash remaining by ~2035** (calibrated), vs. ~2019 (literature)
- 8.1 billion baseline ash trees across 1,880 counties

## Zerve Pipeline Status
All 8 blocks (4 analysis + 4 visualization) ready for Zerve:
```
[Block 1: ingest.load_data (Py)]
    ├→ [Block 2: wrangle.track_a (Py)]
    │       ├→ [Block 3: analysis.track_a_did (R)]
    │       ├→ [Block 5: viz.track_a_trend (R)]
    │       └→ [Block 6: viz.track_a_coef (R)]
    └→ [Block 4: analysis.track_b_spread (Py)]
            ├→ [Block 7: viz.spread_map (Py)]
            └→ [Block 8: viz.extinction_timeline (Py)]
```

### Zerve-Specific Notes
- **No fixest or lfe** in Zerve R runtime → Track A uses manual Frisch-Waugh-Lovell demeaning + manual clustered SEs (pure base R, mathematically identical)
- **Python→R variable passing**: Zerve serializes ALL variables via Parquet. Must `del` all non-DataFrame variables (dicts, functions, Series, loop vars) at end of Python blocks before R blocks.
- **`or` with pandas Series**: Don't use `geo_lookup.get(x) or geo_lookup.get(y)` — Series truthiness is ambiguous. Use explicit `if x is None` pattern.
- **Available R packages**: lme4, data.table, stats, ggplot2, dplyr, tidyverse (but NOT fixest, lfe, plm)
- **R ggplot rendering**: assign to a named variable (e.g. `trend_plot <- ggplot(...)`) — Zerve auto-renders it inline. No `print()`, `ggsave()`, or `png()` needed.
- **Block code files**: all saved in `zerve_blocks/` for easy copy-paste into Zerve canvas
- **matplotlib aspect ratio**: must use `set_aspect(1/np.cos(np.radians(37)))` for geographic maps, not `"equal"` (which stretches E-W)
- **State outlines**: embedded as gzipped base64 Census Bureau 20m GeoJSON in block 7 (~29KB, stdlib only: json+gzip+base64)
- **FIA data gap**: `fetch_fia_ash_data.py` only queried 30 states — AR, CO, SD, MT, etc. have zero ash records (data limitation, not reality)

## Key Decisions
- Track A: R + difference-in-differences causal inference
- Track B: Python + spatial spread / population decline modeling
- All dev work done locally with Claude; Zerve used only for execution/deployment (credit conservation)
- Extended PGA data back to 2009 (historical dataset) to unlock 5 treatment courses for DiD
- FIA data pulled via FIADB REST API; single snapshot + multi-year for calibration

## Data Status
- `data/raw/eab_detections_by_county.csv` — 867 US counties, FIPS + detection year (2002-2022)
- `data/raw/ASA All PGA Raw Data - Tourn Level.csv` — 36,864 rows, 2015-2022, strokes gained
- `data/raw/pga_historical/` — 61,283 leaderboard rows + 505 tournaments, 2009-2022
- `data/raw/fia_ash_by_county.csv` — 3,159 records, ash tree estimates by county (single snapshot, 30 states — AR, SD, CO, MT, ND, ID, WA, OR, NM, UT, WY, NV, CT, DC not covered)
- `data/raw/us_states_20m.json` — Census Bureau 20m state boundaries GeoJSON (for viz)
- `data/raw/fia_ash_multiyear.csv` — 40,959 records, 16 states x 19 eval years (2005-2023)
- `data/raw/census_county_centroids.csv` — 3,235 US county centroids (TIGERweb API)
- `data/processed/pga_courses_geocoded.csv` — 72 US courses with FIPS county codes
- `data/processed/track_a_analysis.csv` — 37,422 merged rows for DiD analysis
- `data/processed/eab_predicted_spread.csv` — 3,109 counties with actual/predicted EAB arrival year
- `data/processed/ash_extinction_timeline.csv` — year-by-year ash population projection (2002-2075)
- `data/processed/ash_extinction_calibrated.csv` — calibrated extinction timeline
- `data/processed/mortality_by_species.csv` — species-level decline rates

## Repo Structure
```
ash-borer-plan.md   # Full project roadmap and deliverables checklist
ideas.md            # Original brainstorm notes
CLAUDE.md           # This file — session context
data/raw/           # Source datasets
data/processed/     # Derived datasets
src/                # Local analysis scripts
  fetch_eab_data.py
  fetch_fia_ash_data.py
  fetch_fia_multiyear.py
  geocode_pga_courses.py
  build_analysis_table.py
  track_a_did.R
  track_b_spread_model.py
  calibrate_extinction.py
zerve_blocks/       # Code files for Zerve canvas blocks
  block1_ingest_load_data.py
  block2_wrangle_track_a.py
  block3_track_a_did.R
  block4_track_b_spread.py
  block5_viz_track_a_trend.R
  block6_viz_track_a_coef.R
  block7_viz_spread_map.py
  block8_viz_extinction_timeline.py
  block_r_probe.R
devpost_summary.md    # 300-word Devpost summary
demo_storyboard.md    # 3-min demo video storyboard
social_post_draft.md  # LinkedIn post draft
```

## Environment
- R 4.5.2 installed at `/c/Program Files/R/R-4.5.2/bin/Rscript`
- R packages in `~/R/library` (fixest, data.table)
- Use full path to Rscript, NOT export PATH
- Python 3.11 via Windows Store
- Kaggle auth: set `KAGGLE_KEY` and `KAGGLE_USERNAME='_'` env vars in Python

## Conventions
- Track issues via GitHub Issues with milestones matching the 4 phases
- Update this file at the end of each working session
- Commit working code frequently; don't let local work drift

## User Context
- Comfortable with Python and SQL
- Less familiar with R and causal inference — Claude assists heavily on those
- Located in Indiana (US)
- Prefers Claude to keep working autonomously unless blocked
