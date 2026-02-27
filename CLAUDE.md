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

## Repo Structure
```
ash-borer-plan.md   # Full project roadmap and deliverables checklist
ideas.md            # Original brainstorm notes
data/               # Raw and processed datasets (gitignored if large)
src/                # Analysis code (Python, R, SQL)
```

## Conventions
- Track issues via GitHub Issues with milestones matching the 4 phases
- Update this file at the end of each working session
- Commit working code frequently; don't let local work drift

## User Context
- Comfortable with Python and SQL
- Less familiar with R and causal inference — Claude assists heavily on those
- Located in Indiana (US)
