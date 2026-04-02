import os
from google.cloud import bigquery
from google.oauth2.credentials import Credentials
import google.auth
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = "data-exp-contactcenter"

def get_bq_client():
    """Obtiene el cliente de BigQuery usando credentials.json o ADC."""
    if os.path.exists('credentials.json'):
        creds = Credentials.from_authorized_user_file('credentials.json')
        # Use a project where the user has job creation permissions for billing
        return bigquery.Client(project="cus-data-dev", credentials=creds)
    
    try:
        credentials, project = google.auth.default()
        return bigquery.Client(project=project or PROJECT_ID, credentials=credentials)
    except Exception as e:
        print(f"❌ Error al crear el cliente de BigQuery: {e}")
        return None

def run_sql_file(file_path):
    """Lee un archivo SQL y lo ejecuta en BigQuery."""
    client = get_bq_client()
    if not client:
        print("❌ No se pudo inicializar el cliente. ¿Ya ejecutaste auth_setup.py?")
        return

    if not os.path.exists(file_path):
        print(f"❌ Archivo no encontrado: {file_path}")
        return

    print(f"📖 Leyendo {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        query = f.read()

    print(f"🚀 Ejecutando script en BigQuery...")
    try:
        query_job = client.query(query, location="US")
        result = query_job.result()  # Espera a que termine
        
        # Si es una consulta que devuelve filas, imprímelas
        if query_job.statement_type == 'SELECT':
            df = result.to_dataframe()
            print(f"✅ ¡Éxito! Resultados:\n")
            print(df.to_string(index=False))
        else:
            print(f"✅ ¡Éxito! El script se ejecutó correctamente.")
    except Exception as e:
        print(f"❌ Error ejecutando el script: {e}")
        import sys
        sys.exit(1)

if __name__ == "__main__":
    import sys
    sql_file = sys.argv[1] if len(sys.argv) > 1 else "new_calculated.sql"
    run_sql_file(sql_file)
