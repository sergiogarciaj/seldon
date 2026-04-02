import os
import pandas as pd
from google.cloud import bigquery
from google.oauth2.credentials import Credentials
import google.auth
from dotenv import load_dotenv

load_dotenv()

# Configuración (Copiada de Radar)
PROJECT_ID = "data-exp-contactcenter"
DATASET_ID = "100x100"
TABLE_ID = "third_calculated"

def get_bq_client():
    """Obtiene el cliente de BigQuery usando credentials.json o ADC."""
    try:
        # 1. Intentar cargar credenciales de usuario (generadas por auth_setup.py)
        if os.path.exists('credentials.json'):
             creds = Credentials.from_authorized_user_file('credentials.json')
             return bigquery.Client(project=PROJECT_ID, credentials=creds)
    except Exception as e:
        print(f"⚠️ No se pudo cargar credentials.json: {e}")

    # 2. Fallback a credenciales predeterminadas (GCloud ADC)
    try:
        credentials, project = google.auth.default()
        if not project:
            project = PROJECT_ID
        return bigquery.Client(project=project, credentials=credentials)
    except Exception as e:
        print(f"❌ Error al crear el cliente de BigQuery: {e}")
        return None

def run_query(query):
    """Ejecuta una consulta y devuelve un DataFrame de Pandas."""
    client = get_bq_client()
    if not client:
        print("❌ No se pudo inicializar el cliente de BigQuery. ¿Ya ejecutaste auth_setup.py?")
        return None
    
    print(f"🔄 Ejecutando consulta en el proyecto {PROJECT_ID}...")
    try:
        df = client.query(query).to_dataframe()
        print(f"✅ Consulta exitosa: {len(df)} filas obtenidas.")
        return df
    except Exception as e:
        print(f"❌ Error en la consulta: {e}")
        return None

if __name__ == "__main__":
    # Ejemplo de consulta: Obtener volumen por canal en 2025
    example_query = f"""
        SELECT 
            canal,
            COUNT(*) as total_registros,
            SUM(COALESCE(factor, 1)) as volumen_total
        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
        WHERE EXTRACT(YEAR FROM call_date) = 2025
        GROUP BY 1
        LIMIT 10
    """
    
    df = run_query(example_query)
    if df is not None:
        print("\n--- Primeras filas del resultado ---")
        print(df.head())
        
        # Aquí puedes agregar tu lógica de manipulación de datos
        # Ejemplo: df_filtrado = df[df['volumen_total'] > 100]
