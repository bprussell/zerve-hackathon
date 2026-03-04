# Demo Video Storyboard (3 minutes max)

## 0:00-0:15 — The Hook
- Screen: Title card "The Ash Borer Effect"
- Voiceover: "Does an invasive beetle improve your golf game? We used PGA Tour data, USDA forest surveys, and causal inference to find out."
- Visual: Side-by-side image of EAB beetle and a golf fairway lined with dead/dying ash trees

## 0:15-0:45 — The Setup
- Voiceover: "The emerald ash borer has killed hundreds of millions of ash trees across 37 states since 2002, spreading county by county from Detroit. Ash trees line fairways on courses across the Midwest. Fewer trees means wider fairways — and maybe fewer penalty shots."
- Visual: Show the published app — use the year slider to animate the spread map from 2002 to 2022, showing EAB detections (orange) overtaking ash habitat (green)

## 0:45-1:15 — The Zerve Pipeline
- Voiceover: "We built a multi-language pipeline in Zerve: Python for data ingestion and spatial modeling, R for causal inference — running side by side on the same canvas."
- Visual: Show the Zerve DAG — zoom out to show the full pipeline
- Call out: Three data sources flowing in (EAB detections, PGA scores, FIA tree surveys)
- Call out: Track A (R) and Track B (Python) branching from the same ingestion block

## 1:15-1:55 — Track A: The Beetle Helps Your Game
- Voiceover: "Track A: A difference-in-differences analysis on 23,000 PGA Tour scores across 84 courses, 2009 to 2022. Five courses fell in counties where EAB arrived during our study window."
- Visual: Show the parallel trends plot in the canvas — EAB vs non-EAB courses tracking together pre-treatment
- Voiceover: "The result? A statistically significant improvement of 0.76 strokes per tournament. P-value: 0.002. The beetle helps your game."
- Visual: Show the coefficient plot — point estimate with 95% CI entirely below zero
- Note: Mention the Frisch-Waugh-Lovell demeaning approach — pure base R, no fixest needed

## 1:55-2:35 — Track B: Ash Extinction
- Voiceover: "Track B: We trained a spatial spread model on 861 detected counties to predict EAB's expansion, then pulled 41,000 multi-year forest inventory records to calibrate actual ash mortality."
- Visual: Show the spread map block output in the canvas — ash density with EAB overlay
- Voiceover: "At current observed rates, half of America's 8 billion ash trees will be gone by 2035."
- Visual: Show the extinction timeline in the canvas — dual curves (literature vs. FIA-calibrated), with the 50% crossing points annotated

## 2:35-2:50 — The App
- Voiceover: "We deployed an interactive explorer via Zerve App Builder. Pick a year and watch the beetle march across the country."
- Visual: Quick demo of the published app — slide through a few years, show the map updating

## 2:50-3:00 — The Close
- Voiceover: "An absurd question. A real answer. A real catastrophe. All built end-to-end in Zerve."
- Visual: Title card with project link, team name, ZerveHack branding
