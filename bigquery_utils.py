from google.cloud import bigquery
from google.oauth2 import service_account
import streamlit as st


@st.cache_resource
def get_bigquery_client():
    credentials = service_account.Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"])
    )
    return bigquery.Client(
        project="master-trackman-project",
        credentials=credentials,
    )


def import_data(dataset, table_name):
    client = get_bigquery_client()

    query = f"""
    SELECT *
    FROM `master-trackman-project.{dataset}.{table_name}`
    """

    return client.query(query).to_dataframe()