# Offensive Rebounding Analysis

An exploratory basketball analytics project examining offensive rebounds through NBA play-by-play data. The notebook reconstructs possessions, identifies rebound events, and creates a foundation for studying which players and game situations generate second-chance opportunities.

## Questions

- Who creates the most offensive-rebounding value?
- How do shot distance, lineup context, and game state relate to rebound outcomes?
- How can raw play-by-play descriptions be converted into useful possession-level features?

## Repository structure

- `notebooks/offensive_rebounding.ipynb` — exploratory event parsing and analysis
- `data/` — intentionally empty; raw NBA play-by-play data is not committed

## Tools

Python, pandas, NumPy, regular expressions, and Jupyter.

## Next steps

The current notebook is an exploratory prototype. Planned improvements include a reproducible data-download step, player opportunity metrics, lineup-adjusted comparisons, and publication-quality charts.

## Data

The original analysis used NBA play-by-play data. Add a compatible CSV to `data/` and update the notebook path locally. Large raw data files are excluded from version control.
