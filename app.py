import streamlit as st
import pandas as pd
import pickle
import visuals

st.set_page_config(layout="wide")

st.title("UCSD Hitting Decision Dashboard")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("data/swing_results.csv")
    with open("data/zone_scaling.pkl", "rb") as f:
        zone_scaling = pickle.load(f)
    return df, zone_scaling

df, zone_scaling = load_data()

# Sidebar controls
players = sorted(df["Batter"].unique())
player = st.sidebar.selectbox("Select Player", players)
count_bucket = st.sidebar.radio("Count State", ["2k", "<2k"])

player_df = df[df["Batter"] == player]

# Call your plotting function
visuals.plot_zone_dashboard(player_df, zone_scaling, count_bucket)