# What Leads to an Offensive Rebound?

Offensive rebounding is one of basketball's most valuable—and comparatively understudied—sources of extra possessions. This project uses NBA play-by-play data to understand which players generate second-chance opportunities and which shot and game contexts make an offensive rebound more likely.

## What the analysis covers

- 539,265 play-by-play events from the 2019–20 NBA season
- 121,284 recorded rebound events, including 36,639 offensive rebounds
- Player-level offensive-rebound production
- Offensive rebounds normalized by each player's shot volume
- Rebound probability after misses at different shot distances
- Tracking-data locations showing how rebound position changes with shot side

## Selected results

![Offensive rebounds relative to player shot volume](results/figures/offensive_rebounds_per_100_shot_attempts.svg)

This view adjusts for how often each player shoots, showing offensive rebounds per 100 field-goal attempts among players with at least 500 attempts. It is an activity-normalized comparison—not a literal conversion rate—because a player can rebound a teammate's miss.

![Offensive rebound probability by shot distance](results/figures/rebound_probability_by_shot_distance.svg)

Misses near the basket produced offensive rebounds more frequently than most mid-range and three-point misses. Mid-range attempts are sneaky costly: they return only two points when made, while misses in these distance bands also produced some of the lowest offensive-rebound probabilities in the sample. Shot value and the chance of recovering a miss therefore point in the same direction.

<img width="1164" alt="Shot origins and directional rebound-location density" src="https://github.com/user-attachments/assets/a15f17b1-e1aa-4a6c-82f7-6987b08625ac" />

The red dots make the shot origin explicit, while the heat density shows the location of the player nearest the rim when the ball reaches it. For missed threes from below the centerline, 71.4% of those nearest-rim positions were above it. For shots from above the centerline, 72.1% were below it. In other words, the likely recovery position shifts to the opposite side of the lane.

This is a player-position proxy for where a rebound can be secured—not a literal map of the ball's flight and not a claim that the nearest player was always credited with the rebound.

Together, the analyses separate two parts of generating a second chance: the shot context that changes whether an offensive rebound occurs, and the floor position from which the rebound is recovered. The underlying model also considers shooter location, spacing near the rim, which team has the closest player, player movement between release and rim contact, and historical rebounding performance.

## Repository structure

```text
analysis/
  prepare_rebounds.py             play-by-play linking and figure generation
  directional_rebound_heatmap.py tracking-data density visualization
data/
  README.md                    source-data notes
notebooks/
  offensive_rebounding.ipynb exploratory play-by-play work
results/
  figures/                   publication-ready charts
  tables/                    summary data behind each chart
```

## Methods

Missed field goals are linked to the following rebound event within the same game segment. The play-by-play analysis compares offensive-rebound rates across shot-distance bands and normalizes player totals by each player's field-goal-attempt volume. A separate tracking sample identifies the shooter's location at release and the player closest to the rim at rim contact for 55,631 side-location missed threes. Raw tracking data are not included in the repository.

## Tools

Python · pandas · NumPy · SciPy · Matplotlib · Jupyter
