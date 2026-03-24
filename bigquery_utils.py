from google.cloud import bigquery
from google.oauth2 import service_account
import streamlit as st

credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(project="master-trackman-project", credentials=credentials)

def import_data(dataset, table_name):
    query = f"""
    SELECT GameID, Inning, Top_Bottom, PAofInning, PitchofPA, Batter, PlateLocSide, PlateLocHeight, PitchCall, Balls, Strikes, delta_run_exp
    FROM `master-trackman-project.{dataset}.{table_name}`
    ORDER BY GameID ASC, Inning ASC, Top_Bottom DESC, PAofInning ASC, PitchofPA ASC
    """
    df = client.query(query).to_dataframe()
    return df