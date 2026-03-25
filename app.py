import streamlit as st
import pandas as pd
import visuals
from bigquery_utils import import_data

st.set_page_config(layout="wide")
st.title("UCSD Hitting Decision Dashboard")

@st.cache_data
def load_data():
    df = import_data('dashboard_dataset', 'swing_results')
    return df

df = load_data()

if st.sidebar.button("Refresh Data"):
    load_data.clear()
    st.rerun()

# --- AB qualifier: exclude players below mean total pitch count ---
mean_abs = df.groupby('Batter')['count'].sum().mean()
qualified_batters = df.groupby('Batter')['count'].sum()
qualified_batters = qualified_batters[qualified_batters >= mean_abs].index
df_qualified = df[df['Batter'].isin(qualified_batters)]

players = sorted(df["Batter"].unique())
player = st.sidebar.selectbox("Select Player", players)
count_bucket = st.sidebar.radio("Count State", ["2k", "<2k"])
metric = st.sidebar.radio("Metric", list(visuals.METRIC_CONFIG.keys()))

cfg = visuals.METRIC_CONFIG[metric]
col = cfg["col"]

# Percentile lookup built from qualified batters only
zone_percentiles = (
    df_qualified.groupby(["PlateZone", "hitter_count"])[col]
    .apply(sorted)
    .to_dict()
)

player_df = df[df["Batter"] == player]

fig = visuals.plot_zone_dashboard(player_df, zone_percentiles, count_bucket, metric)
left_col, _ = st.columns([2, 1])
with left_col:
    st.pyplot(fig)