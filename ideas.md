# ZerveHack Ideas

## Hackathon Details
- **Deadline:** April 29, 2026 (2:00 PM EDT)
- **Prizes:** $5K / $3K / $2K
- **Judging:** Analytical Depth (35%), End-to-End Workflow (30%), Storytelling & Clarity (20%), Creativity & Ambition (15%)
- **Requirements:** Public Zerve project, 300-word summary, 3-min demo video, social media post
- **Bonus:** Deploying an API or interactive app gets priority consideration

---

## Idea 1: "Your Weather Tax" — The Personal Cost of Climate Change

**Elevator Pitch:** Climate change isn't abstract — it has a dollar amount, and it's different depending on where you live. By crossing NOAA's Storm Events Database (which logs property damage, crop damage, injuries, and deaths by county going back decades) with Census income data, we calculate the per-capita annual "weather tax" for every county in the US — and show how it's trending. Enter your zip code, see what extreme weather is actually costing your community, and whether it's getting worse.

**Datasets:**
- NOAA Storm Events Database (free) — property/crop damage, injuries, deaths by county, 50+ years
- US Census / American Community Survey (free) — population, income by county
- FRED (free) — inflation adjustment

**Deliverable:** API endpoint — give it a zip code, get back a climate cost profile (annual cost, trend, percentile rank, worst event types)

**Why it could win:**
- Analytical Depth (35%): Multi-decade time series, geographic regression, trend modeling
- End-to-End (30%): Clean deployable API with a clear input/output
- Storytelling (20%): Makes it personal — judges type in their own zip code
- Creativity (15%): Flips climate from global/abstract to local/personal

---

## Idea 2: "The College Bet" — Is Your Degree Worth It?

**Elevator Pitch:** The DOE's College Scorecard has data on every college in America — tuition, graduation rates, post-graduation earnings by major, debt loads. Calculate the ROI of every college-major combination in the country. Which degrees pay for themselves in 5 years? Which ones never do? How has this changed over the last decade?

**Datasets:**
- College Scorecard (free from DOE) — tuition, earnings by major, debt, graduation rates
- FRED (free) — inflation adjustment, wage benchmarks

**Deliverable:** API/app — pick a school and major, get an ROI scorecard with payback period, comparison to alternatives, and trend over time

**Zerve Showcase:**
- Fleet: ROI calculations across thousands of college-major combos in parallel
- Multi-language: SQL to join institutional data with earnings data, Python for modeling, R for confidence intervals on earnings estimates
- DAG: Massive parallel pipeline — each college-major combo as a branch

**Why it could win:**
- Analytical Depth (35%): Thousands of ROI calculations with statistical confidence intervals, controlling for selection bias
- End-to-End (30%): Clean API with personal input/output, deployed via App Builder
- Storytelling (20%): Everyone has a stake — judges will immediately look up their own school
- Creativity (15%): Turns a government dataset into a personal financial advisor

---

## Idea 3: "The Ash Borer Effect" — Does an Invasive Beetle Improve Your Golf Game?

**Elevator Pitch:** The emerald ash borer has killed hundreds of millions of ash trees across 37 states since 2002, spreading county by county in a trackable wave. Ash trees line fairways on golf courses across the Midwest and East Coast. Fewer trees = wider fairways = fewer penalty shots? We cross EAB county detection dates with PGA Tour scoring data by course location and test a beautifully absurd hypothesis: does an ecological disaster make golfers better? Then flip to the serious side: model the spread rate, project which counties are next, and estimate when (or if) North American ash species hit functional extinction.

**Datasets:**
- USDA APHIS EAB county detection data (free) — county-level detection by year since 2002
- emeraldashborer.info timeline (free) — full county-by-county spread timeline
- Canada Open Data EAB surveillance 2002-2020 (free, CSV/XLSX)
- PGA Tour scores by course (Kaggle, free) — 2010-2022, course-level scoring data

**Deliverable:** Two API endpoints — "when is EAB coming to my county?" (spread model projection) and "what's the estimated golf score impact at course X?" (causal analysis). Deployed via App Builder as a dual-panel dashboard.

**Zerve Showcase:**
- Fleet: Parallel analysis across hundreds of counties and dozens of courses
- Multi-language: SQL for joining EAB spread data with golf scores by location/year, Python for spatial spread modeling, R for difference-in-differences causal inference
- DAG: Two parallel analysis branches (golf impact + extinction modeling) merge into a final dashboard

**Why it could win:**
- Analytical Depth (35%): Two rigorous analyses — difference-in-differences causal study on golf scores (controlling for player skill, course changes) + spatial spread model with extinction projections
- End-to-End (30%): Dual API endpoints deployed as interactive app
- Storytelling (20%): Hook with the absurd golf question, then hit with the real ecological catastrophe story
- Creativity (15%): Most unexpected crossover anyone will submit — an invasive beetle × golf performance study
