from google.cloud import bigquery

client = bigquery.Client(project="master-trackman-project")

def import_data(dataset, table_name):
    query = f"""
    SELECT GameID, Inning, Top_Bottom, PAofInning, PitchofPA, Batter, PlateLocSide, PlateLocHeight, PitchCall, Balls, Strikes, delta_run_exp
    FROM `master-trackman-project.{dataset}.{table_name}`
    ORDER BY GameID ASC, Inning ASC, Top_Bottom DESC, PAofInning ASC, PitchofPA ASC
    """
    df = client.query(query).to_dataframe()

    return df