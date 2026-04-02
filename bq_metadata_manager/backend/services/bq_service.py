import os
from google.cloud import bigquery
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID", "data-exp-contactcenter")
BILLING_PROJECT_ID = os.getenv("BILLING_PROJECT_ID", "cus-data-dev")
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "..", "credentials.json")

def get_bq_client():
    if os.path.exists(CREDENTIALS_PATH):
        creds = Credentials.from_authorized_user_file(CREDENTIALS_PATH)
        return bigquery.Client(project=BILLING_PROJECT_ID, credentials=creds)
    return bigquery.Client(project=BILLING_PROJECT_ID)

def get_table_schema(full_table_id: str):
    """
    Extracts schema from BigQuery table.
    """
    # Clean possible backticks from user input
    full_table_id = full_table_id.replace("`", "")
    client = get_bq_client()
    table = client.get_table(full_table_id)
    
    schema = []
    for field in table.schema:
        schema.append({
            "name": field.name,
            "type": field.field_type,
            "mode": field.mode
        })
    return schema

def ingest_table_data(full_table_id: str, limit: int = 1000):
    """
    Fetches data from BigQuery and returns a DataFrame.
    """
    full_table_id = full_table_id.replace("`", "")
    client = get_bq_client()
    query = f"SELECT * FROM `{full_table_id}` LIMIT {limit}"
    return client.query(query).to_dataframe()

def run_bigquery_query(sql: str):
    """
    Executes a raw SQL query in BigQuery and returns a DataFrame.
    """
    client = get_bq_client()
    return client.query(sql).to_dataframe()
