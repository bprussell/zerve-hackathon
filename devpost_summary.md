# The Ash Borer Effect: Does an Invasive Beetle Improve Your Golf Game?

The emerald ash borer (EAB) has killed hundreds of millions of ash trees across 37+ states since its 2002 detection in Michigan. Ash trees line fairways on golf courses throughout the Midwest and East Coast. Fewer trees mean wider fairways — so does an ecological disaster actually make golfers better?

## What We Built

A dual-track pipeline combining causal inference with ecological modeling:

**Track A (R):** Difference-in-differences analysis on 23,444 PGA Tour scores (2009-2022) across 72 US courses, with player, course, and year fixed effects. Five courses fell in counties where EAB arrived during our study window, creating a natural experiment.

**Track B (Python):** A spatial spread model trained on 861 confirmed EAB counties predicts arrival dates for all 3,109 contiguous US counties (CV MAE: 2.32 years). We calibrated an extinction projection using 40,959 multi-year USDA Forest Inventory records across 16 states.

## What We Found

**The beetle helps your golf game.** Courses in EAB-affected counties show a significant improvement of **0.76 strokes per tournament** after EAB arrival (p=0.005). Tournaments are often decided by a single stroke.

**Ash trees are in serious trouble.** EAB advances at ~53 km/year, reaching all of the contiguous US by ~2037. County-level FIA data reveals 3.8% annual ash mortality post-EAB, with white ash declining 21%. At current rates, half of North America's 8.15 billion ash trees will be gone by 2035.

## Why It Matters

This project turns an absurd question into a lens for understanding a genuine ecological catastrophe unfolding across America's forests, parks, and golf courses. The data-calibrated extinction timeline grounds the alarming "8 billion trees at risk" headlines in observed decline rates.

*Built with Zerve (SQL + R + Python), using USDA APHIS, USDA Forest Service FIA, and PGA Tour data.*
