import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as mcolors

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


def plot_zone_dashboard(player_df, zone_scaling_dict, hitter_count_toggle="<2k", metric="Run Value"):

    cfg = METRIC_CONFIG[metric]
    col = cfg["col"]

    # unwrap nested dict if needed (zone_scaling is only used for Run Value)
    if "weighted_re_sum" in zone_scaling_dict:
        zone_scaling = zone_scaling_dict["weighted_re_sum"]
    else:
        zone_scaling = zone_scaling_dict

    df = player_df[player_df["hitter_count"] == hitter_count_toggle].copy()
    zone_values = dict(zip(df["PlateZone"], df[col]))

    bounds = {
        "Waste":  (-2.167, 2.167, 0,     4.833),
        "Chase":  (-1.667, 1.667, 0.5,   4.333),
        "Shadow": (-1.108, 1.108, 1.167, 3.833),
        "Heart":  (-0.558, 0.558, 1.833, 3.167),
    }

    fig, ax = plt.subplots(figsize=(10, 8))

    for zone in ["Waste", "Chase", "Shadow", "Heart"]:
        x1, x2, y1, y2 = bounds[zone]
        raw_value = zone_values.get(zone, 0)

        if cfg["diverging"]:
            cmap = plt.cm.RdBu_r
            zone_max_abs = zone_scaling.get((zone, hitter_count_toggle), 1)
            norm = mcolors.Normalize(vmin=-zone_max_abs, vmax=zone_max_abs)
        else:
            cmap = plt.cm.YlGn
            # scale 0 → max across all zones for this count state
            all_vals = [zone_values.get(z, 0) for z in bounds]
            v_max = max(all_vals) if max(all_vals) > 0 else 1
            norm = mcolors.Normalize(vmin=0, vmax=v_max)

        color = cmap(norm(raw_value))

        rect = patches.Rectangle(
            (x1, y1),
            x2 - x1,
            y2 - y1,
            linewidth=1.5,
            edgecolor="black",
            facecolor=color,
        )
        ax.add_patch(rect)

        label_text = cfg["fmt"].format(raw_value)
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
        "Color scaled within each zone\nrelative to team max (per count)"
        if cfg["diverging"]
        else "Color scaled 0 → max across zones"
    )
    ax.text(2, 0.15, scale_note, ha="right", va="bottom", fontsize=10)

    return fig