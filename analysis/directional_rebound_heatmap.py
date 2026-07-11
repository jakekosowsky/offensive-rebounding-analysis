"""Map missed-three shot origins against the likely rebound side.

The tracking sample does not publish a credited rebounder identifier. The
rebound-location proxy is therefore the player closest to the rim when the ball
reaches it. This matches the spatial question without presenting the proxy as a
literal ball-flight path.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle, Rectangle
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde


ROOT = Path(__file__).resolve().parents[1]
PBP = ROOT / "data" / "testing_data_pbp.csv"
LOCATIONS = ROOT / "data" / "testing_data_loc.csv"
OUTPUT = ROOT / "results" / "figures" / "directional_rebound_heatmap.png"


def prepare_tracking_sample() -> pd.DataFrame:
    pbp_columns = [
        "playbyplayorder_id",
        "fg3attempted",
        "fg3made",
        "shooter_player_id",
        *[f"playerid_off_player_{i}" for i in range(1, 6)],
    ]
    pbp = pd.read_csv(PBP, usecols=pbp_columns)
    pbp = pbp.query("fg3attempted == 1 and fg3made == 0").copy()

    coordinate_columns = ["playbyplayorder_id"]
    for team in ("off", "def"):
        for i in range(1, 6):
            coordinate_columns.extend(
                [
                    f"AtShot_loc_x_{team}_player_{i}",
                    f"AtShot_loc_y_{team}_player_{i}",
                    f"AtRim_loc_x_{team}_player_{i}",
                    f"AtRim_loc_y_{team}_player_{i}",
                ]
            )

    event_ids = set(pbp["playbyplayorder_id"].dropna().astype("int64"))
    location_parts = []
    for chunk in pd.read_csv(
        LOCATIONS, usecols=coordinate_columns, chunksize=100_000
    ):
        selected = chunk[chunk["playbyplayorder_id"].isin(event_ids)]
        if not selected.empty:
            location_parts.append(selected)
    tracking = pbp.merge(
        pd.concat(location_parts, ignore_index=True),
        on="playbyplayorder_id",
        how="inner",
    )

    offensive_ids = tracking[
        [f"playerid_off_player_{i}" for i in range(1, 6)]
    ].to_numpy()
    shooter_id = tracking["shooter_player_id"].to_numpy()[:, None]
    shooter_match = offensive_ids == shooter_id
    shooter_slot = shooter_match.argmax(axis=1)
    row = np.arange(len(tracking))

    shot_x_all = tracking[
        [f"AtShot_loc_x_off_player_{i}" for i in range(1, 6)]
    ].to_numpy(dtype=float)
    shot_y_all = tracking[
        [f"AtShot_loc_y_off_player_{i}" for i in range(1, 6)]
    ].to_numpy(dtype=float)
    shot_x = shot_x_all[row, shooter_slot]
    shot_y = shot_y_all[row, shooter_slot]

    rim_x_columns = [
        f"AtRim_loc_x_{team}_player_{i}"
        for team in ("off", "def")
        for i in range(1, 6)
    ]
    rim_y_columns = [
        f"AtRim_loc_y_{team}_player_{i}"
        for team in ("off", "def")
        for i in range(1, 6)
    ]
    rim_x_all = tracking[rim_x_columns].to_numpy(dtype=float)
    rim_y_all = tracking[rim_y_columns].to_numpy(dtype=float)
    distance = np.hypot(rim_x_all + 41.75, rim_y_all)
    closest_slot = np.argmin(np.where(np.isnan(distance), np.inf, distance), axis=1)
    rebound_x = rim_x_all[row, closest_slot]
    rebound_y = rim_y_all[row, closest_slot]

    sample = pd.DataFrame(
        {
            "shot_x": shot_x,
            "shot_y": shot_y,
            "rebound_x": rebound_x,
            "rebound_y": rebound_y,
        }
    )
    valid = (
        shooter_match.any(axis=1)
        & np.isfinite(sample).all(axis=1)
        & (sample["shot_x"] < 0)
        & (sample["rebound_x"] < 0)
    )
    return sample.loc[valid].copy()


def draw_half_court(ax: plt.Axes) -> None:
    line = "#64748b"
    ax.set_facecolor("#f8fafc")
    ax.add_patch(Rectangle((-47, -25), 47, 50, fill=False, lw=1.3, ec=line))
    ax.add_patch(Rectangle((-47, -8), 19, 16, fill=False, lw=1.3, ec=line))
    ax.add_patch(Circle((-41.75, 0), 0.75, fill=False, lw=1.5, ec=line))
    ax.plot([-43, -43], [-3, 3], color=line, lw=2)
    ax.add_patch(Arc((-41.75, 0), 8, 8, theta1=-90, theta2=90, lw=1.1, ec=line))
    ax.add_patch(Arc((-41.75, 0), 47.5, 47.5, theta1=-68, theta2=68, lw=1.3, ec=line))
    ax.plot([-47, -33.1], [-22, -22], color=line, lw=1.3)
    ax.plot([-47, -33.1], [22, 22], color=line, lw=1.3)
    ax.axhline(0, color="#94a3b8", lw=1, ls=(0, (4, 4)), zorder=1)
    ax.set_xlim(-47, -13)
    ax.set_ylim(-25, 25)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def density(ax: plt.Axes, frame: pd.DataFrame) -> None:
    points = frame[["rebound_x", "rebound_y"]].sample(
        min(7_500, len(frame)), random_state=14
    )
    kde = gaussian_kde(points.to_numpy().T, bw_method=0.25)
    x = np.linspace(-47, -13, 180)
    y = np.linspace(-25, 25, 220)
    xx, yy = np.meshgrid(x, y)
    zz = kde(np.vstack([xx.ravel(), yy.ravel()])).reshape(xx.shape)
    zz /= zz.max()
    ax.contourf(
        xx,
        yy,
        zz,
        levels=[0.08, 0.16, 0.28, 0.42, 0.60, 0.80, 1.01],
        cmap="YlGnBu",
        alpha=0.88,
        antialiased=True,
        zorder=2,
    )


def plot_panel(
    ax: plt.Axes,
    frame: pd.DataFrame,
    title: str,
    opposite_condition: pd.Series,
    annotation_side: str,
) -> None:
    draw_half_court(ax)
    density(ax, frame)
    shot_sample = frame[["shot_x", "shot_y"]].sample(
        min(140, len(frame)), random_state=7
    )
    ax.scatter(
        shot_sample["shot_x"],
        shot_sample["shot_y"],
        s=15,
        c="#dc2626",
        edgecolors="white",
        linewidths=0.35,
        alpha=0.72,
        zorder=4,
        label="Shot origins",
    )
    share = 100 * opposite_condition.mean()
    ax.set_title(title, loc="left", fontsize=13, fontweight="bold", color="#0f172a")
    ax.text(
        -45.5,
        23.4 if annotation_side == "top" else -23.4,
        f"{share:.1f}% on opposite side",
        ha="left",
        va="top" if annotation_side == "top" else "bottom",
        fontsize=11,
        fontweight="bold",
        color="#0f172a",
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.9, "pad": 4},
        zorder=5,
    )


def main() -> None:
    sample = prepare_tracking_sample()
    lower = sample[sample["shot_y"] <= -8]
    upper = sample[sample["shot_y"] >= 8]

    fig, axes = plt.subplots(1, 2, figsize=(13, 6.6), facecolor="white")
    plot_panel(
        axes[0],
        lower,
        "Shots from the lower side",
        lower["rebound_y"] > 0,
        "top",
    )
    plot_panel(
        axes[1],
        upper,
        "Shots from the upper side",
        upper["rebound_y"] < 0,
        "bottom",
    )
    fig.suptitle(
        "Missed threes pull likely rebound positions across the lane",
        x=0.06,
        y=0.98,
        ha="left",
        fontsize=20,
        fontweight="bold",
        color="#0f172a",
    )
    fig.text(
        0.06,
        0.92,
        "Red dots show shot origins; heat density shows the player nearest the rim at rim contact.",
        ha="left",
        fontsize=11.5,
        color="#475569",
    )
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="lower left",
        bbox_to_anchor=(0.055, 0.015),
        frameon=False,
        fontsize=10.5,
    )
    fig.text(
        0.94,
        0.03,
        "Tracking sample: 55,631 side-location missed threes",
        ha="right",
        fontsize=9.5,
        color="#64748b",
    )
    fig.subplots_adjust(left=0.055, right=0.97, top=0.86, bottom=0.10, wspace=0.10)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main()
