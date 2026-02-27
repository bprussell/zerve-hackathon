# The Ash Borer Effect — ZerveHack Entry

## What This Is
Hackathon entry for ZerveHack (Devpost). Dual-track analysis: (A) do golf scores improve after EAB kills ash trees on courses, (B) model EAB spread and project ash extinction timeline. See `ash-borer-plan.md` for the full roadmap.

## Current Phase
**Phase 1: Data Acquisition & Exploration** (Weeks 1–2, target end ~Mar 13)

## Key Decisions
- Track A: R + difference-in-differences causal inference
- Track B: Python + spatial spread / population decline modeling
- SQL for data wrangling in Zerve
- All dev work done locally with Claude; Zerve used only for execution/deployment (credit conservation)
- Extended PGA data back to 2009 (historical dataset) to unlock 6 treatment courses for DiD
- FIA data pulled via FIADB REST API; current snapshot is single eval year per state — need multi-year pulls for Track B extinction modeling (see issue #8)

## Data Status
- `data/raw/eab_detections_by_county.csv` — 867 US counties, FIPS + detection year (2002-2022)
- `data/raw/ASA All PGA Raw Data - Tourn Level.csv` — 36,864 rows, 2015-2022, strokes gained
- `data/raw/pga_historical/` — 61,283 leaderboard rows + 505 tournaments, 2009-2022
- `data/raw/fia_ash_by_county.csv` — 3,159 records, ash tree estimates by county (single snapshot)
- `data/processed/pga_courses_geocoded.csv` — 72 US courses with FIPS county codes

## Repo Structure
```
ash-borer-plan.md   # Full project roadmap and deliverables checklist
ideas.md            # Original brainstorm notes
CLAUDE.md           # This file — session context
data/raw/           # Source datasets
data/processed/     # Derived datasets
src/                # Fetch scripts and analysis code
```

## Conventions
- Track issues via GitHub Issues with milestones matching the 4 phases
- Update this file at the end of each working session
- Commit working code frequently; don't let local work drift

## User Context
- Comfortable with Python and SQL
- Less familiar with R and causal inference — Claude assists heavily on those
- Located in Indiana (US)
