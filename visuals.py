import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as mcolors
import numpy as np
from bisect import bisect_left

METRIC_CONFIG = {
    "Run Value": {
        "col": "weighted_re_sum",
        "fmt": "{:+.2f}",
        "label": "Runs Added",
        "diverging": True,
    },
    "Swing %": {
        "col": "swing_percentage",
        "fmt": "{:.1%}",
        "label": "Swing %",
        "diverging": False,
    },
    "Count": {
        "col": "count",
        "fmt": "{:.0f}",
        "label": "Pitch Count",
        "diverging": False,
    },
}


def _percentile_rank(sorted_vals, value):
    """Return 0–1 percentile rank of value within a sorted list."""
    n = len(sorted_vals)
    if n == 0:
        return 0.5
    if n == 1:
        return 0.5
    # Number of values strictly below, plus 0.5 for ties → midpoint method
    idx = bisect_left(sorted_vals, value)
    return idx / (n - 1)  # 0.0 = min, 1.0 = max


def plot_zone_dashboard(player_df, zone_percentiles, hitter_count_toggle="<2k", metric="Run Value"):

    cfg = METRIC_CONFIG[metric]
    col = cfg["col"]

    df = player_df[player_df["hitter_count"] == hitter_count_toggle].copy()
    zone_values = dict(zip(df["PlateZone"], df[col]))

    bounds = {
        "Waste":  (-2.167, 2.167, 0,     4.833),
        "Chase":  (-1.667, 1.667, 0.5,   4.333),
        "Shadow": (-1.108, 1.108, 1.167, 3.833),
        "Heart":  (-0.558, 0.558, 1.833, 3.167),
    }

    fig, ax = plt.subplots(figsize=(10, 8))
    cmap = plt.cm.RdBu_r
    # Percentile is already 0–1, map directly onto colormap
    norm = mcolors.Normalize(vmin=0, vmax=1)

    for zone in ["Waste", "Chase", "Shadow", "Heart"]:
        x1, x2, y1, y2 = bounds[zone]
        raw_value = zone_values.get(zone, None)

        if raw_value is None:
            color = "lightgrey"
        elif cfg["diverging"]:
            sorted_vals = zone_percentiles.get((zone, hitter_count_toggle), [])
            pct = _percentile_rank(sorted_vals, raw_value)
            color = cmap(norm(pct))
        else:
            # For non-diverging metrics, scale within zone across count state
            sorted_vals = zone_percentiles.get((zone, hitter_count_toggle), [])
            pct = _percentile_rank(sorted_vals, raw_value)
            # Use a sequential colormap for non-diverging metrics
            color = plt.cm.Blues(norm(pct))

        rect = patches.Rectangle(
            (x1, y1),
            x2 - x1,
            y2 - y1,
            linewidth=1.5,
            edgecolor="black",
            facecolor=color,
        )
        ax.add_patch(rect)

        label_text = cfg["fmt"].format(raw_value) if raw_value is not None else "N/A"
        ax.text(
            (x1 + x2) / 2,
            y2 - 0.15,
            f"{zone}: {label_text}",
            ha="center",
            va="top",
            fontsize=11,
            weight="bold",
        )

    # ---- Rulebook strike zone ----
    rulebook = patches.Rectangle(
        (-0.833, 1.5),
        1.666,
        2.0,
        linewidth=2,
        edgecolor="black",
        facecolor="none",
        linestyle="--",
        label="Rulebook Strike Zone",
    )
    ax.add_patch(rulebook)

    ax.set_xlim(-2.5, 2.5)
    ax.set_ylim(0, 5)
    ax.set_xlabel("PlateLocSide (ft)")
    ax.set_ylabel("PlateLocHeight (ft)")
    ax.set_title(f"{cfg['label']} ({hitter_count_toggle})", weight="bold")
    ax.set_aspect("equal", adjustable="box")
    ax.legend(loc="upper right", framealpha=1)

    scale_note = (
        "Color = percentile rank within zone\n(vs. all players, same count)"
        if cfg["diverging"]
        else "Color = percentile rank within zone\n(vs. all players, same count)"
    )
    ax.text(2, 0.15, scale_note, ha="right", va="bottom", fontsize=10)

    return fig