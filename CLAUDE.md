# The Ash Borer Effect — ZerveHack Entry

## What This Is
Hackathon entry for ZerveHack (Devpost). Dual-track analysis: (A) do golf scores improve after EAB kills ash trees on courses, (B) model EAB spread and project ash extinction timeline. See `ash-borer-plan.md` for the full roadmap.

## Current Phase
**Phase 2 COMPLETE. Moving to Phase 3: Build in Zerve** (Weeks 5-6)
- Issues #6, #7, #8 all complete — both tracks have full results
- Issue #12 complete — 300-word Devpost summary drafted
- Demo storyboard drafted, social media post drafted
- **Next up: Issue #9** (transfer pipeline to Zerve, wire up DAG) — requires Zerve platform
- Then #10 (Fleet), #11 (App Builder), #13 (record video), #14 (submit)

## Track A Result
DiD with player + course + year fixed effects (R/fixest):
- Treatment effect: **-0.759 strokes** (SE 0.271, p=0.005)
- 5 treatment courses, 23,444 obs (4-round scores), 2009-2022
- The beetle helps your golf game.

## Track B Result
Polynomial ridge regression on spatial features (Python/sklearn):
- **861 training counties** (known EAB detections, 2002-2022)
- **CV MAE: 2.32 years**, R2: 0.635
- Median spread speed: **53 km/year** from Wayne County, MI origin
- Predicts all contiguous US counties reached by **~2037** (Pacific NW last)
- County centroids from Census TIGERweb API (cached)
- Outputs: `data/processed/eab_predicted_spread.csv` (3,109 counties), `data/processed/ash_extinction_timeline.csv`

## Track B Calibrated Extinction (Issue #8)
Multi-year FIA data (40,959 records, 16 states, 2005-2023) calibrates mortality:
- **Literature**: 99% mortality in 6 years (mature canopy trees in core zone)
- **Observed**: 3.82% annual mortality (all trees incl. seedlings/regeneration)
- **50% ash remaining by ~2035** (calibrated), vs. ~2019 (literature)
- White ash hardest hit (-21.3%); black ash still growing (+10.7%)
- MI: -30%, OH: -45%, PA: -52% since EAB arrival
- Outputs: `data/processed/ash_extinction_calibrated.csv`, `data/processed/mortality_by_species.csv`

## Key Decisions
- Track A: R + difference-in-differences causal inference
- Track B: Python + spatial spread / population decline modeling
- SQL for data wrangling in Zerve
- All dev work done locally with Claude; Zerve used only for execution/deployment (credit conservation)
- Extended PGA data back to 2009 (historical dataset) to unlock 5 treatment courses for DiD
- FIA data pulled via FIADB REST API; single snapshot + multi-year (40,959 records) for calibration

## Data Status
- `data/raw/eab_detections_by_county.csv` — 867 US counties, FIPS + detection year (2002-2022)
- `data/raw/ASA All PGA Raw Data - Tourn Level.csv` — 36,864 rows, 2015-2022, strokes gained
- `data/raw/pga_historical/` — 61,283 leaderboard rows + 505 tournaments, 2009-2022
- `data/raw/fia_ash_by_county.csv` — 3,159 records, ash tree estimates by county (single snapshot)
- `data/processed/pga_courses_geocoded.csv` — 72 US courses with FIPS county codes
- `data/processed/track_a_analysis.csv` — 37,422 merged rows for DiD analysis
- `data/raw/census_county_centroids.csv` — 3,235 US county centroids (TIGERweb API)
- `data/processed/eab_predicted_spread.csv` — 3,109 counties with actual/predicted EAB arrival year
- `data/processed/ash_extinction_timeline.csv` — year-by-year ash population projection (2002-2075)
- `data/raw/fia_ash_multiyear.csv` — 40,959 records, 16 states x 19 eval years (2005-2023)
- `data/processed/ash_extinction_calibrated.csv` — calibrated extinction timeline
- `data/processed/mortality_by_species.csv` — species-level decline rates

## Repo Structure
```
ash-borer-plan.md   # Full project roadmap and deliverables checklist
ideas.md            # Original brainstorm notes
CLAUDE.md           # This file — session context
data/raw/           # Source datasets
data/processed/     # Derived datasets
src/                # Fetch scripts and analysis code
  fetch_eab_data.py
  fetch_fia_ash_data.py
  geocode_pga_courses.py
  build_analysis_table.py
  track_a_did.R
  track_b_spread_model.py
  fetch_fia_multiyear.py
  calibrate_extinction.py
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
