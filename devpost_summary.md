# The Ash Borer Effect: Does an Invasive Beetle Improve Your Golf Game?

The emerald ash borer has killed hundreds of millions of ash trees across 37+ states since arriving in Detroit in 2002. Ash trees line fairways on golf courses throughout the Midwest and East Coast. Fewer trees mean wider fairways — so does an ecological disaster actually make golfers better?

## What We Built

A dual-track pipeline combining causal inference with ecological modeling:

**Track A (R):** Difference-in-differences on 23,444 PGA Tour scores (2009-2022) across 84 courses, with player, course, and year fixed effects. Five courses fell in counties where EAB arrived during the study window — a natural experiment.

**Track B (Python):** A spatial spread model trained on 861 confirmed EAB counties predicts arrival dates nationwide (CV MAE: 2.32 years). We calibrated an extinction projection using 40,959 multi-year USDA Forest Inventory records.

## What We Found

**The beetle helps your golf game.** Courses see -0.76 strokes per tournament after EAB arrives (p=0.002). Tournaments are often decided by a single stroke.

**Ash trees are in serious trouble.** EAB advances ~53 km/year. Observed decline data shows 3.8% annual ash mortality post-EAB. At current rates, half of North America's 8 billion ash trees will be gone by 2035.

## Why It Matters

The absurd question is a doorway into a real one. The data-calibrated extinction timeline grounds alarming "8 billion trees at risk" headlines in observed decline rates — turning a catastrophe people scroll past into something they can actually picture.

*Built end-to-end in Zerve, with Python and R running side by side on the same canvas. Data: USDA APHIS, USDA Forest Service FIA, PGA Tour.*
