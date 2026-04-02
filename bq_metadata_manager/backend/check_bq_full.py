import os
from services.bq_service import get_bq_client

client = get_bq_client()
table_id = "re-data-prod.virtual_assistant_metrics.bot_retention"
query = f"SELECT COUNT(*) as cnt FROM `{table_id}`"
res = client.query(query).to_dataframe()
print(f"Total rows in BigQuery for {table_id}: {res.cnt[0]}")

# Also check for Feb 2026 specifically
query_feb = f"""
SELECT COUNT(*) as cnt 
FROM `{table_id}` 
WHERE EXTRACT(YEAR FROM conversation_start_datetime) = 2026 
AND EXTRACT(MONTH FROM conversation_start_datetime) = 2
"""
res_feb = client.query(query_feb).to_dataframe()
print(f"Rows in Feb 2026: {res_feb.cnt[0]}")
