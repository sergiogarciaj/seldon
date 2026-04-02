import os
import google.generativeai as genai
from dotenv import load_dotenv
import json

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash-lite')

def generate_table_description(table_name: str, schema: list):
    prompt = f"""
    Eres un arquitecto de datos experto.
    Analiza el siguiente esquema de la tabla de BigQuery '{table_name}' y genera una descripción concisa y profesional del propósito de la tabla y lo que representan sus datos.
    
    Esquema:
    {json.dumps(schema, indent=2)}
    
    Respuesta en español.
    """
    response = model.generate_content(prompt)
    return response.text.strip()

def generate_sql_query(user_request: str, catalog: list):
    """
    Generates SQL for BigQuery based on catalog metadata.
    catalog is a list of dicts with {full_id, short_name, schema_json, description}
    """
    catalog_context = "\n".join([
        f"Tabla: `{t['full_id']}` (Referencia corta: {t['short_name']})\nDescripción: {t['description']}\nEsquema: {json.dumps(t['schema_json'])}"
        for t in catalog
    ])
    
    prompt = f"""
    Eres un experto en SQL para Google BigQuery.
    Dada la siguiente solicitud del usuario y el catálogo de tablas disponibles en BigQuery, redacta una query SQL válida para BigQuery.
    
    REGLAS CRÍTICAS:
    - Solo devuelve la query SQL, nada más. No incluyas explicaciones ni bloques de código markdown extraños.
    - Usa SIEMPRE los IDs completos de las tablas entre comillas invertidas (backticks), por ejemplo: `proyecto.dataset.tabla`.
    - No uses dialectos de PostgreSQL; usa funciones y sintaxis estándar de BigQuery (ej: TIMESTAMP, EXTRACT, etc).
    
    Catálogo:
    {catalog_context}
    
    Solicitud del usuario:
    {user_request}
    """
    response = model.generate_content(prompt)
    # Clean possible markdown artifacts
    sql = response.text.strip().replace("```sql", "").replace("```", "")
    return sql
