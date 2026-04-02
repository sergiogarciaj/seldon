import os
from google.cloud import bigquery
from google.oauth2.credentials import Credentials

# Basic setup from current app logic
PROJECT_ID = "data-exp-contactcenter"
BILLING_PROJECT_ID = "cus-data-dev"
CREDENTIALS_PATH = os.path.expanduser("~/Bigquery/bq_metadata_manager/credentials.json")

def get_bq_client():
    if os.path.exists(CREDENTIALS_PATH):
        creds = Credentials.from_authorized_user_file(CREDENTIALS_PATH)
        return bigquery.Client(project=BILLING_PROJECT_ID, credentials=creds)
    return bigquery.Client(project=BILLING_PROJECT_ID)

client = get_bq_client()
table_id = "data-exp-contactcenter.100x100.bot_retention"
query = f"SELECT COUNT(*) as cnt FROM `{table_id}`"
res = client.query(query).to_dataframe()
print(f"Total rows in BigQuery: {res.cnt[0]}")

# Also check for Feb 2026 specifically
query_feb = f"""
SELECT COUNT(*) as cnt 
FROM `{table_id}` 
WHERE EXTRACT(YEAR FROM conversation_start_datetime) = 2026 
AND EXTRACT(MONTH FROM conversation_start_datetime) = 2
"""
res_feb = client.query(query_feb).to_dataframe()
print(f"Rows in Feb 2026: {res_feb.cnt[0]}")
