# Demo Video Storyboard (3 minutes max)

## 0:00-0:05 — Title Card
- Screen: Title slide "The Ash Borer Effect"
- Brief pause, then advance

## 0:05-0:50 — Personal Intro (image progression)
- Voiceover: "I'm a golfer, and about ten years ago I started noticing ash trees on my courses marked with a white X."
- Visual: Slide 2 — photo of ash tree with white X spray-painted on it
- Voiceover: "That's because of this — the Emerald Ash Borer, an invasive beetle that arrived in Detroit in 2002."
- Visual: Slide 3 — close-up photo of EAB beetle
- Voiceover: "It burrows under the bark, leaving these S-shaped trails, and has wiped out hundreds of millions of ash trees."
- Visual: Slide 4 — photo of EAB larval galleries / trails in wood
- Voiceover: "Entire forests have been devastated."
- Visual: Slide 5 — photo of dead ash canopy / forest with standing dead trees
- Voiceover: "But I noticed something — as these trees were removed from my golf courses, I started scoring better. Fewer trees in the fairway means fewer penalty shots."
- Visual: Slide 6 — photo of tree-lined golf fairway

## 0:50-1:00 — The Question
- Voiceover: "For this hackathon, I wanted to answer the question: does an ecological disaster actually make golfers better?"
- Visual: Slide 7 — "Fewer trees mean wider fairways. Does an ecological disaster actually make golfers better?"

## 1:00-1:20 — The Zerve Pipeline
- Voiceover: "I built a multi-language pipeline in Zerve — Python for data ingestion and spatial modeling, R for causal inference — running side by side on the same canvas."
- Visual: Slide 8 — Zerve canvas DAG screenshot
- Call out: Three data sources, Track A (R) and Track B (Python) branching from the same ingestion block

## 1:20-1:50 — Track A: The Beetle Helps Your Game
- Voiceover: "Track A uses difference-in-differences — a causal inference method — on 23,000 PGA Tour scores across 84 courses, 2009 to 2022. Five courses fell in counties where EAB arrived during the study window."
- Visual: Slide 9 — big "-0.76 strokes" stat
- Voiceover: "The result: a statistically significant improvement of 0.76 strokes per tournament. The beetle helps your game."
- Note: Can show parallel trends and coefficient plots from Zerve canvas during narration if time allows

## 1:50-2:20 — Track B: Ash Extinction
- Voiceover: "Track B models the ecological side. I trained a spatial spread model on 861 detected counties, then calibrated ash mortality using 41,000 multi-year USDA forest inventory records."
- Visual: Slide 10 — extinction timeline with "2035" stat
- Voiceover: "At current observed rates, half of America's 8 billion ash trees will be gone by 2035."

## 2:20-2:45 — The App (animated spread map)
- Voiceover: "I deployed an interactive explorer via Zerve App Builder. Pick a year and watch the beetle march across the country."
- Visual: Slide 11 — live demo of the published app, sliding through years 2002 to 2022
- Show the map updating with each year, green ash habitat overtaken by orange EAB detections

## 2:45-3:00 — The Close
- Voiceover: "An absurd question. A real answer. A real catastrophe. All built end-to-end in Zerve."
- Visual: Slide 12 — closing card with app link
