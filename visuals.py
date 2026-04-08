import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as mcolors
from bisect import bisect_left

METRIC_CONFIG = {
    "Total Run Value": {
        "col": "weighted_relative_re_sum",
        "fmt": "{:+.2f}",
        "label": "Total Runs Added",
        "diverging": True,
    },
    "Average Run Value": {
        "col": "weighted_relative_re_mean",
        "fmt": "{:+.2f}",
        "label": "Average Runs Added",
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
    """Return 0–1 percentile rank of value within a sorted list.
    0.0 = minimum (darkest blue), 1.0 = maximum (darkest red).
    """
    n = len(sorted_vals)
    if n <= 1:
        return 0.5
    idx = bisect_left(sorted_vals, value)
    return idx / (n - 1)


def plot_zone_dashboard(player_df, zone_percentiles, hitter_count_toggle="<2k", metric="Total Run Value", is_qualified=True):

    cfg = METRIC_CONFIG[metric]
    col = cfg["col"]

    # filter to the selected count state; Overall uses the full player_df
    if hitter_count_toggle == "Overall":
        df = player_df.copy()
    else:
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
    norm = mcolors.Normalize(vmin=0, vmax=1)

    for zone in ["Waste", "Chase", "Shadow", "Heart"]:
        x1, x2, y1, y2 = bounds[zone]
        raw_value = zone_values.get(zone, None)

        if raw_value is None:
            color = "lightgrey"
        else:
            # key is just PlateZone for Overall, (PlateZone, hitter_count) otherwise
            if hitter_count_toggle == "Overall":
                lookup_key = zone
            else:
                lookup_key = (zone, hitter_count_toggle)

            sorted_vals = zone_percentiles.get(lookup_key, [])
            pct = _percentile_rank(sorted_vals, raw_value)
            # 0.0 → darkest blue (RdBu_r left), 1.0 → darkest red (RdBu_r right)
            color = cmap(norm(pct))

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

    qualifier_note = "" if is_qualified else " *"
    ax.set_title(f"{cfg['label']} ({hitter_count_toggle}){qualifier_note}", weight="bold")

    if not is_qualified:
        ax.text(
            0, -0.5,
            "* Below minimum PA threshold — percentile colors are relative to qualified batters",
            ha="center", va="bottom", fontsize=9, style="italic", color="gray"
        )

    ax.set_aspect("equal", adjustable="box")
    ax.legend(loc="upper right", framealpha=1)

    ax.text(2, 0.15, "Color = percentile rank within zone\n(qualified batters, same count)",
            ha="right", va="bottom", fontsize=10)

    return fig