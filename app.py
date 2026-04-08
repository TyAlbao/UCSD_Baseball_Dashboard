import streamlit as st
import pandas as pd
import visuals
from bigquery_utils import import_data

st.set_page_config(layout="wide")
st.title("UCSD Hitting Decision Dashboard")

@st.cache_data
def load_data_hitter_count():
    return import_data('dashboard_dataset', 'swing_results_hitter_count')

@st.cache_data
def load_data_overall():
    return import_data('dashboard_dataset', 'swing_results_overall')

df_hitter_count = load_data_hitter_count()
df_overall = load_data_overall()

if st.sidebar.button("Refresh Data"):
    load_data_hitter_count.clear()
    load_data_overall.clear()
    st.rerun()

# --- AB qualifier: based on total pitch count across hitter_count table ---
mean_abs = df_hitter_count.groupby('Batter')['count'].sum().mean()
qualified_batters = df_hitter_count.groupby('Batter')['count'].sum()
qualified_batters = qualified_batters[qualified_batters >= mean_abs].index

players = sorted(df_hitter_count["Batter"].unique())
player = st.sidebar.selectbox("Select Player", players)
is_qualified = player in qualified_batters

count_bucket = st.sidebar.radio("Count State", ["<2k", "2k", "Overall"])
metric = st.sidebar.radio("Metric", list(visuals.METRIC_CONFIG.keys()))

cfg = visuals.METRIC_CONFIG[metric]
col = cfg["col"]

if count_bucket == "Overall":
    df = df_overall
    df_qualified = df_overall[df_overall["Batter"].isin(qualified_batters)]
    # percentile lookup keyed by PlateZone only
    zone_percentiles = (
        df_qualified.groupby("PlateZone")[col]
        .apply(sorted)
        .to_dict()
    )
else:
    df = df_hitter_count
    df_qualified = df_hitter_count[df_hitter_count["Batter"].isin(qualified_batters)]
    # percentile lookup keyed by (PlateZone, hitter_count)
    zone_percentiles = (
        df_qualified.groupby(["PlateZone", "hitter_count"])[col]
        .apply(sorted)
        .to_dict()
    )

player_df = df[df["Batter"] == player]

fig = visuals.plot_zone_dashboard(player_df, zone_percentiles, count_bucket, metric, is_qualified)
left_col, _ = st.columns([2, 1])
with left_col:
    st.pyplot(fig)