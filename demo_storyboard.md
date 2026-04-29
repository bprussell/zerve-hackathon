# Demo Video Storyboard (3 minutes max)

## 0:00-0:05 — Title Card
- Screen: Title slide "The Ash Borer Effect"
- Brief pause, then advance

## 0:05-0:50 — Personal Intro (image progression)
- Voiceover: "I'm a golfer, and about ten years ago I started noticing ash trees on my courses marked with a white X."
- Voiceover: "That's because of this — the Emerald Ash Borer, an invasive beetle that arrived in Detroit in 2002."
- Voiceover: "It burrows under the bark, leaving these S-shaped trails, and has wiped out hundreds of millions of ash trees."
- Voiceover: "Entire forests have been devastated."
- Voiceover: "But I noticed something — as these trees were removed from my golf courses, I started scoring better. Fewer trees in the fairway means fewer penalty shots."

## 0:50-1:00 — The Question
- Voiceover: "For this hackathon, I wanted to see if I could show that when the Emerald Ash Borer shows up, it causes golf scores in that area to go down."

## 1:00-1:20 — The Zerve Pipeline
- Voiceover: "I built a multi-language pipeline in Zerve, running side by side on the same canvas. I used data from the PGA tour and the USDA forest inventory to do this analysis. I ingest and wrangle the data, then analyze it with two methods, then I have some blocks here for visualizations, and these blocks at the end are used by the app builder to gather the user's input and show the result. This track, written in R, uses the difference-in-differences method to analyze how many strokes are gained off the tee in affected courses. This track, written in Python, predicts how much time we have left with our ash trees before they are wiped out by the Emerald Ash Borer."

## 1:20-1:50 — Track A: The Beetle Helps Your Game
- Voiceover: "The R analysis shows a statistically significant improvement of 0.76 strokes per tournament on affected courses compared to courses where the beetle has not shown up yet."

## 1:50-2:20 — Track B: Ash Extinction
- Voiceover: "The Python track models the ecological side. I trained a spatial spread model to calibrate the mortality of ash trees. There are publications showing that 50% of mature ash trees were gone in 2024, but young saplings aren't affected as much by the beetle. My model shows a longer timeline that accounts for this. By 2039, I predict that half of ALL ash trees in the US will be gone."

## 2:20-2:45 — The App (animated spread map)
- Voiceover: "Finally, I used Zerve's app builder to deploy an interactive data explorer. Pick a year and watch the beetle march across the country."

## 2:45-3:00 — The Close
- Voiceover: "An absurd question. A real answer. A real catastrophe. All built end-to-end in Zerve."
- Visual: Slide 12 — closing card with app link
