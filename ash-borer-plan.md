# The Ash Borer Effect

**Does an Invasive Beetle Improve Your Golf Game?**

ZerveHack Hackathon Entry | Deadline: April 29, 2026, 2:00 PM EDT

---

## Thesis

The emerald ash borer (*Agrilus planipennis*) has killed hundreds of millions of ash trees across 37+ states since its 2002 detection in southeast Michigan, spreading county by county in a trackable wave. Ash trees line fairways on golf courses across the Midwest and East Coast. Fewer trees = wider fairways = fewer penalty shots?

This project crosses EAB county detection dates with PGA Tour scoring data by course location and tests a beautifully absurd hypothesis: does an ecological disaster make golfers better? Then it flips to the serious side — modeling the spread rate, projecting which counties are next, and estimating when North American ash species hit functional extinction.

## Dual-Track Concept

| | Track A: Golf Impact | Track B: Extinction Modeling |
|---|---|---|
| **Hook** | Absurd & memorable | Serious & credible |
| **Question** | Do golf scores improve at courses after EAB arrives? | When will North American ash species hit functional extinction? |
| **Method** | Difference-in-differences causal inference | Spatial spread + population decline modeling |
| **Language** | R | Python |
| **Judges see** | Creativity & Ambition (15%) | Analytical Depth (35%) |

The two tracks branch in the Zerve DAG, then merge into a final dual-panel dashboard — showcasing End-to-End Workflow (30%) and Storytelling (20%).

A null result on Track A is still a valid finding ("EAB doesn't help your game").

---

## Data Sources

All free. All sources are US government public domain (USDA/APHIS/USFS), Canadian open data (Open Government Licence), or permissively licensed (Kaggle). No third-party authorization needed.

### Primary

| # | Source | URL | Content |
|---|--------|-----|---------|
| 1 | USDA APHIS EAB Infestation Map | https://www.aphis.usda.gov/plant-pests-diseases/eab/eab-infestation-map | County-level detection by year since 2002 (updated monthly) |
| 2 | emeraldashborer.info Timeline | https://www.emeraldashborer.info/timeline/by_county/index.html | Full county-by-county spread timeline (Purdue / USFS) |
| 3 | Canada EAB Surveillance Data | https://open.canada.ca/data/en/dataset/69f4ecd8-9761-4d40-b0f9-e186f2fcce5b | EAB surveillance 2002–2020 (CSV/XLSX, CFIA) |
| 4 | PGA Tour Golf Data (Kaggle) | https://www.kaggle.com/datasets/robikscube/pga-tour-golf-data-20152022 | 2010–2022 course-level scoring data |
| 5 | USDA Forest Inventory & Analysis (FIA) | https://www.fia.fs.usda.gov/tools-data/default.asp | County-level ash tree density, biomass, volume by species |

### Supplementary / Narrative

| Source | URL | Use |
|--------|-----|-----|
| USDA APHIS EAB Story Map | https://www.aphis.usda.gov/plant-pests-diseases/eab/eab-story-map | Interactive spread visualization |
| USGA "The Ash Tree Two-Step" | https://www.usga.org/content/usga/home-page/course-care/regional-updates/central-region/2018/the-ash-tree-two-step.html | Validates golf course tree removal hypothesis |
| USDA Ash Range Map (PDF) | https://www.aphis.usda.gov/sites/default/files/eab-ash-range-map.pdf | Native ash range reference |
| Cary Institute — 8 Billion Trees at Risk | https://www.caryinstitute.org/news-insights/feature/8-billion-north-american-ash-trees-risk-emerald-ash-borer | Ecological stakes framing |
| Club+Resort Business — Racine Tree Loss | https://clubandresortbusiness.com/racine-wis-courses-latest-face-tree-loss-emerald-ash-borer/ | Real-world golf course impact |

### Validation Data Points (Golf Course Impact)

- Rockford, IL: 109 trees removed across 4 courses (Elliot 11, Ingersoll 12, Sandy Hollow 73, Sinnissippi 13)
- Browns Lake GC (WI): fairways defined by rows of ash, several removed
- Como & Phalen GC: ash trees scheduled for contractor removal in 2024

---

## Analysis Approach

### Track A — Golf Score Impact (R, Causal Inference)

1. **Geocode PGA Tour courses** to FIPS county codes
2. **Join** with EAB county detection dates — flag each course-year as pre/post EAB
3. **Difference-in-differences (DiD) analysis:**
   - Treatment group: courses in EAB-affected counties, post-arrival years
   - Control group: courses in unaffected counties (or same courses pre-arrival)
4. **Controls:** player skill (FedEx rankings), course difficulty (par, yardage), weather, non-EAB course modifications
5. **Statistical significance testing** and confidence intervals

> Claude + Zerve agent will assist heavily here — user is less familiar with R and causal inference methods.

### Track B — Extinction Modeling (Python, Spatial/ML)

1. **Pull FIA data** for ash tree density by county over time
2. **Spatial spread model:** predict EAB arrival date for currently unaffected counties based on historical spread patterns
3. **Population decline model:** estimate ash tree survival rate post-EAB arrival per county
4. **Project timeline** to functional extinction thresholds for North American ash species (all 16 species susceptible: green, black, white, blue ash, etc.)

---

## Zerve Pipeline Design

```
┌─────────────────────────────────────────────────────┐
│                    DATA INGESTION                    │
│              (SQL blocks, one per source)            │
│  EAB spread data · PGA scores · FIA tree density    │
└──────────────────┬──────────────────────────────────┘
                   │
          ┌────────┴────────┐
          ▼                 ▼
┌─────────────────┐ ┌─────────────────┐
│   TRACK A (R)   │ │  TRACK B (Py)   │
│  DiD causal     │ │  Spatial spread  │
│  inference on   │ │  + population    │
│  golf scores    │ │  decline model   │
│                 │ │                  │
│  Fleet: parallel│ │  Fleet: parallel │
│  across courses │ │  across counties │
└────────┬────────┘ └────────┬────────┘
         │                   │
         └─────────┬─────────┘
                   ▼
       ┌───────────────────────┐
       │   MERGE & DASHBOARD   │
       │   (App Builder)       │
       │                       │
       │  Panel 1: Golf impact │
       │  Panel 2: Extinction  │
       │         timeline      │
       └───────────────────────┘
```

### Platform Features Showcased

| Feature | How We Use It |
|---------|---------------|
| **Multi-language** | SQL (data wrangling) → R (causal inference) → Python (ML/spatial) |
| **DAG** | Two parallel branches merge — visually represents the dual-track concept |
| **Fleet** | Parallel county-level and course-level analyses across hundreds of units |
| **App Builder** | Deployed dual-panel dashboard with two API endpoints |

---

## Deliverables Checklist

- [ ] **Deployed App** (via App Builder) — dual-panel dashboard with two endpoints:
  - "When is EAB coming to my county?" (spread model projection)
  - "What's the golf score impact at course X?" (causal analysis results)
- [ ] **Public Zerve project URL** submitted on Devpost, runs without errors
- [ ] **300-word project summary** on Devpost: what question, what findings, why it matters
- [ ] **3-minute demo video** uploaded to YouTube/Vimeo, showcasing workflow and findings
- [ ] **Social media post** (LinkedIn or X) with: project link, hackathon mention, brief description, and @ZerveAI tag
- [ ] **Demo video storyboard** (prep artifact)

---

## 8-Week Timeline

| Weeks | Phase | Activities |
|-------|-------|------------|
| **1–2** | Data Acquisition & Exploration | Download all datasets. Explore structure, coverage, quality. Geocode PGA courses to counties. Identify data gaps early. |
| **3–4** | Analysis Pipeline (Local + Claude) | Build Track A DiD analysis in R. Build Track B spread model in Python. All dev done locally with Claude — zero credit burn. |
| **5–6** | Build in Zerve | Transfer polished code into Zerve. Wire up DAG. Test Fleet parallelism. Iterate on pipeline. |
| **7–8** | Deploy & Polish | Deploy app via App Builder. Record 3-min demo video. Write 300-word summary. Post to social media. Submit on Devpost. |

**Deadline: April 29, 2026, 2:00 PM EDT**

---

## Credit Budget Strategy

**Estimated credits available: ~200**

| Source | Credits |
|--------|---------|
| Hackathon bonus (on registration) | ~100 |
| Free tier (~50/month × 2 months) | ~100 |

**Strategy: build offline, deploy on-platform.**

1. **Design and debug locally with Claude (free)** — all heavy thinking, prototyping, code iteration costs nothing
2. **Transfer polished code into Zerve** — no trial-and-error on the platform
3. **Use lightweight datasets** during development to keep runs efficient
4. **Save credits for the final polished run** and the deployed app (which scores bonus points)

> Claude = free offline AI for all dev work. Zerve = execution and deployment only. Credits go toward deliverables, not iteration.

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Golf data lacks courses in EAB zones** | Track A underpowered | Expand to amateur/municipal course data; reduce geographic scope to Midwest corridor |
| **Null result on golf hypothesis** | Less "wow" factor | Still a valid, publishable finding — reframe as "EAB doesn't help your game" |
| **Credit overrun** | Can't finish pipeline | Pre-build everything locally; use Zerve only for execution; keep datasets lightweight |
| **FIA data too complex to wrangle** | Track B delayed | Start FIA exploration in Week 1; fall back to simpler county-level proxies if needed |
| **R/causal inference learning curve** | Track A slow | Claude + Zerve agent assist heavily; DiD is well-documented with many R packages (e.g., `did`, `fixest`) |
| **Demo video quality** | Hurts Storytelling score | Write storyboard early (Week 6); keep it simple — screen recording with voiceover |

---

## Judging Process

**Stage 1 (Pass/Fail):** Project viability — must reasonably fit theme and use the Zerve platform. Filtered before scoring.

**Stage 2 (Weighted Scoring):**

| Criterion | Weight | How We Score |
|-----------|--------|--------------|
| **Analytical Depth** | 35% | Two rigorous analyses — DiD causal study with controls + spatial spread model with extinction projections |
| **End-to-End Workflow** | 30% | Full pipeline from raw data → DAG → Fleet → deployed dual-endpoint app |
| **Storytelling & Clarity** | 20% | Hook with the absurd golf question, pivot to real ecological catastrophe |
| **Creativity & Ambition** | 15% | The most unexpected idea anyone will submit — an invasive beetle improving golf scores |

---

## Assistance Model

| Who | Does What | Cost |
|-----|-----------|------|
| **Claude** | Analysis design, code writing/debugging, storytelling/summary drafting, R/causal inference guidance | Free |
| **Zerve Agent** | On-platform code execution, DAG orchestration | Credits |
| **You** | Transfer code to Zerve, manage submissions, record demo, social post | Time |

---

*Competition: [ZerveHack on Devpost](https://zervehack.devpost.com/) · Prize pool: $10,000 ($5K / $3K / $2K)*
