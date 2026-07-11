# What Leads to an Offensive Rebound?

Offensive rebounding is one of basketball's most valuable—and comparatively understudied—sources of extra possessions. This project uses NBA play-by-play data to understand which players generate second-chance opportunities and which shot and game contexts make an offensive rebound more likely.

## What the analysis covers

- 539,265 play-by-play events from the 2019–20 NBA season
- 121,284 recorded rebound events, including 36,639 offensive rebounds
- Player-level offensive-rebound production
- Offensive rebounds normalized by each player's shot volume
- Rebound probability after misses at different shot distances
- Tracking-data locations showing where missed threes are recovered

## Selected results

![Offensive rebounds relative to player shot volume](results/figures/offensive_rebounds_per_100_shot_attempts.svg)

This view adjusts for how often each player shoots, showing offensive rebounds per 100 field-goal attempts among players with at least 500 attempts. It is an activity-normalized comparison—not a literal conversion rate—because a player can rebound a teammate's miss.

![Offensive rebound probability by shot distance](results/figures/rebound_probability_by_shot_distance.svg)

Misses near the basket produced offensive rebounds more frequently than most mid-range and three-point misses. Mid-range attempts are sneaky costly: they return only two points when made, while misses in these distance bands also produced some of the lowest offensive-rebound probabilities in the sample. Shot value and the chance of recovering a miss therefore point in the same direction.

![Rebound-location density after missed three-point attempts](results/figures/rebound_location_heatmap.png)

The tracking-data view adds the spatial side of the question. Hotter areas show where credited rebounders were positioned near rim contact after missed three-point attempts. The concentration around the paint makes the recovery zone visible, while the spread across the lane shows that long shots do not produce one deterministic rebound path. This is a map of rebounder locations—not the ball's literal flight path.

Together, the analyses separate two parts of generating a second chance: the shot context that changes whether an offensive rebound occurs, and the floor position from which the rebound is recovered. The underlying model also considers shooter location, spacing near the rim, which team has the closest player, player movement between release and rim contact, and historical rebounding performance.

## Repository structure

```text
analysis/
  prepare_rebounds.py          play-by-play linking and figure generation
  rebound_location_heatmap.R  tracking-data density visualization
data/
  README.md                    source-data notes
notebooks/
  offensive_rebounding.ipynb exploratory play-by-play work
results/
  figures/                   publication-ready charts
  tables/                    summary data behind each chart
```

## Methods

Missed field goals are linked to the following rebound event within the same game segment. The play-by-play analysis compares offensive-rebound rates across shot-distance bands and normalizes player totals by each player's field-goal-attempt volume. A separate player-tracking sample maps the credited rebounder's coordinates near rim contact after missed three-point attempts. Raw tracking data are not included in the repository.

## Tools

Python · R · pandas · NumPy · Matplotlib · ggplot2 · Jupyter
