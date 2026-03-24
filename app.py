import streamlit as st
import pandas as pd
import pickle
import visuals
from import_data import import_data

st.set_page_config(layout="wide")

st.title("UCSD Hitting Decision Dashboard")

# Load data
@st.cache_data
def load_data():
    df = import_data('dashboard_dataset', 'swing_results')
    zone_scaling = df.groupby(['PlateZone','hitter_count'])[['weighted_re_sum']].agg(lambda x: x.abs().max()).to_dict()

    return df, zone_scaling

df, zone_scaling = load_data()

# Refresh button
if st.sidebar.button("Refresh Data"):
    load_data.clear()
    st.rerun()

# Sidebar controls
players = sorted(df["Batter"].unique())
player = st.sidebar.selectbox("Select Player", players)
count_bucket = st.sidebar.radio("Count State", ["2k", "<2k"])

player_df = df[df["Batter"] == player]

# Call your plotting function
fig = visuals.plot_zone_dashboard(player_df, zone_scaling, count_bucket)
st.pyplot(fig)