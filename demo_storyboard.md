# Demo Video Storyboard (3 minutes max)

## 0:00-0:15 — The Hook
- Screen: Title card "The Ash Borer Effect"
- Voiceover: "Does an invasive beetle improve your golf game? We used PGA Tour data, USDA forest surveys, and causal inference to find out."
- Visual: Side-by-side image of EAB beetle and a golf fairway lined with dead/dying ash trees

## 0:15-0:40 — The Setup
- Voiceover: "The emerald ash borer has killed hundreds of millions of ash trees across 37 states since 2002, spreading county by county from Detroit. Ash trees line fairways on courses across the Midwest. Fewer trees means wider fairways — and maybe fewer penalty shots."
- Visual: EAB spread map animation (county detections by year, 2002-2022)
- Visual: Quick flash of validation — news articles about golf courses removing ash trees

## 0:40-1:10 — The Zerve Pipeline
- Voiceover: "We built a multi-language pipeline in Zerve: SQL for data ingestion, R for causal inference, Python for spatial modeling."
- Visual: Show the Zerve DAG — two branches diverging and merging
- Call out: SQL blocks ingesting three data sources (EAB detections, PGA scores, FIA tree data)
- Call out: Track A (R) and Track B (Python) running in parallel

## 1:10-1:50 — Track A Results
- Voiceover: "Track A: Difference-in-differences analysis on 23,000 PGA Tour scores across 72 courses, 2009-2022. Five courses fell in counties where EAB arrived during our study window."
- Visual: Show the R code / fixest regression output in Zerve
- Voiceover: "The result? A statistically significant improvement of 0.76 strokes per tournament after EAB arrival. P-value: 0.005. The beetle helps your game."
- Visual: Coefficient table or simple bar chart showing the treatment effect

## 1:50-2:30 — Track B Results
- Voiceover: "Track B: We trained a spatial spread model on 861 detected counties to predict when EAB reaches the rest of the US."
- Visual: Predicted spread map — color-coded by arrival year
- Voiceover: "Then we pulled 41,000 multi-year forest inventory records to calibrate ash mortality from observed data."
- Visual: State-level decline chart (Michigan, Ohio, Pennsylvania curves)
- Voiceover: "At current rates, half of North America's 8 billion ash trees will be gone by 2035. White ash — the most common species — has already declined 21% across surveyed states."
- Visual: Extinction timeline chart (% remaining vs. year)

## 2:30-2:50 — The App
- Voiceover: "We deployed a dual-panel dashboard via Zerve App Builder."
- Visual: Show the live app — Panel 1 (spread map / "when is EAB coming to my county?"), Panel 2 (extinction timeline)
- Quick demo: type in a county, show predicted arrival year

## 2:50-3:00 — The Close
- Voiceover: "An absurd question. A real catastrophe. All built end-to-end in Zerve."
- Visual: Title card with project link, team name, ZerveHack branding
