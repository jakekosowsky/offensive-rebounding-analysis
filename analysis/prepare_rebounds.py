from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


SOURCE = Path("/Users/JakeKosowsky/NBA Model/2019-20_pbp.csv")
OUTPUT = Path("outputs/github-portfolio/offensive-rebounding-analysis")
FIGURES = OUTPUT / "results" / "figures"
TABLES = OUTPUT / "results" / "tables"
FIGURES.mkdir(parents=True, exist_ok=True)
TABLES.mkdir(parents=True, exist_ok=True)

columns = [
    "URL", "Quarter", "SecLeft", "AwayTeam", "HomeTeam", "Shooter",
    "ShotOutcome", "ShotDist", "Rebounder", "ReboundType"
]
pbp = pd.read_csv(SOURCE, usecols=columns)

rebounds = pbp[pbp["ReboundType"].isin(["offensive", "defensive"])].copy()
offensive = rebounds[rebounds["ReboundType"] == "offensive"].copy()

player_totals = (
    offensive.dropna(subset=["Rebounder"])
    .query("Rebounder != 'Team'")
    .groupby("Rebounder")
    .size()
    .sort_values(ascending=False)
    .head(15)
    .rename("offensive_rebounds")
    .reset_index()
)
player_totals.to_csv(TABLES / "top_offensive_rebounders.csv", index=False)

fig, ax = plt.subplots(figsize=(9, 6))
plot_players = player_totals.sort_values("offensive_rebounds")
ax.barh(plot_players["Rebounder"], plot_players["offensive_rebounds"], color="#2563eb")
ax.set_title("Players generating the most second-chance opportunities")
ax.set_xlabel("Offensive rebounds")
ax.set_ylabel("")
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(FIGURES / "top_offensive_rebounders.png", dpi=180)
fig.savefig(FIGURES / "top_offensive_rebounders.svg")
plt.close(fig)

# A missed shot is paired with the immediately following rebound event when the
# game and quarter remain unchanged.
misses = pbp[pbp["ShotOutcome"] == "miss"].copy()
miss_indices = misses.index
next_rows = pbp.reindex(miss_indices + 1)
valid = (
    next_rows["ReboundType"].isin(["offensive", "defensive"]).to_numpy()
    & (next_rows["URL"].to_numpy() == misses["URL"].to_numpy())
    & (next_rows["Quarter"].to_numpy() == misses["Quarter"].to_numpy())
)
misses = misses.loc[valid].copy()
misses["next_rebound_type"] = next_rows.loc[next_rows.index[valid], "ReboundType"].to_numpy()
misses["offensive_rebound"] = (misses["next_rebound_type"] == "offensive").astype(int)

distance_bins = [-0.1, 3, 8, 14, 20, 24, 30]
distance_labels = ["0–3", "4–8", "9–14", "15–20", "21–24", "25–30"]
misses["shot_distance_band"] = pd.cut(
    misses["ShotDist"], bins=distance_bins, labels=distance_labels
)
distance_rates = (
    misses.dropna(subset=["shot_distance_band"])
    .groupby("shot_distance_band", observed=True)["offensive_rebound"]
    .agg(["mean", "count"])
    .reset_index()
)
distance_rates["offensive_rebound_rate"] = distance_rates.pop("mean")
distance_rates.to_csv(TABLES / "rebound_rate_by_shot_distance.csv", index=False)

fig, ax = plt.subplots(figsize=(9, 5.5))
ax.plot(
    distance_rates["shot_distance_band"].astype(str),
    100 * distance_rates["offensive_rebound_rate"],
    marker="o",
    linewidth=2.5,
    color="#2563eb",
)
ax.set_title("Offensive-rebound probability changes with shot distance")
ax.set_xlabel("Shot distance (feet)")
ax.set_ylabel("Offensive rebounds after misses (%)")
ax.grid(axis="y", alpha=0.25)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(FIGURES / "rebound_probability_by_shot_distance.png", dpi=180)
fig.savefig(FIGURES / "rebound_probability_by_shot_distance.svg")
plt.close(fig)

quarter_rates = (
    misses[misses["Quarter"].between(1, 4)]
    .groupby("Quarter")["offensive_rebound"]
    .agg(["mean", "count"])
    .query("count >= 100")
    .reset_index()
)
quarter_rates["offensive_rebound_rate"] = quarter_rates.pop("mean")
quarter_rates.to_csv(TABLES / "rebound_rate_by_quarter.csv", index=False)

fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(
    quarter_rates["Quarter"].astype(str),
    100 * quarter_rates["offensive_rebound_rate"],
    color="#0f766e",
)
ax.set_title("Offensive-rebound probability by quarter")
ax.set_xlabel("Quarter")
ax.set_ylabel("Offensive rebounds after misses (%)")
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(FIGURES / "rebound_probability_by_quarter.png", dpi=180)
fig.savefig(FIGURES / "rebound_probability_by_quarter.svg")
plt.close(fig)

summary = pd.DataFrame(
    {
        "metric": ["rebound_events", "offensive_rebounds", "linked_missed_shots"],
        "value": [len(rebounds), len(offensive), len(misses)],
    }
)
summary.to_csv(TABLES / "analysis_summary.csv", index=False)
