import pandas as pd
from sqlalchemy import create_engine, Table, Column, Integer, String, Float, Boolean, MetaData, text
from database import engine

def map_bq_to_pg(bq_type: str):
    mapping = {
        "STRING": "TEXT",
        "INTEGER": "BIGINT",
        "INT64": "BIGINT",
        "FLOAT": "DOUBLE PRECISION",
        "FLOAT64": "DOUBLE PRECISION",
        "BOOLEAN": "BOOLEAN",
        "BOOL": "BOOLEAN",
        "TIMESTAMP": "TIMESTAMP",
        "DATE": "DATE",
        "DATETIME": "TIMESTAMP"
    }
    return mapping.get(bq_type.upper(), "TEXT")

def create_local_table_from_results(table_name: str, df: pd.DataFrame, schema: list = None):
    """
    Saves results to a new PostgreSQL table with explicit type mapping.
    """
    dtype_map = {}
    if schema:
        from sqlalchemy.types import TEXT, BIGINT, Float, BOOLEAN, TIMESTAMP, DATE
        type_mapping = {
            "TEXT": TEXT,
            "BIGINT": BIGINT,
            "DOUBLE PRECISION": Float,
            "BOOLEAN": BOOLEAN,
            "TIMESTAMP": TIMESTAMP,
            "DATE": DATE
        }
        for field in schema:
            pg_type_name = map_bq_to_pg(field['type'])
            dtype_map[field['name']] = type_mapping.get(pg_type_name, TEXT)

    # NEW: Serialize complex types (lists, dicts, numpy arrays) to strings
    for col in df.columns:
        if df[col].dtype == 'object':
            # Check if any element is a list or numpy array
            if any(isinstance(x, (list, dict, pd.Series)) or str(type(x)).find('numpy.ndarray') != -1 for x in df[col] if x is not None):
                df[col] = df[col].apply(lambda x: str(x) if x is not None else None)

    df.to_sql(table_name, engine, if_exists='replace', index=False, dtype=dtype_map)
    return len(df)

def execute_query(sql_query: str):
    """
    Executes a query and returns a DataFrame.
    """
    return pd.read_sql(sql_query, engine)

def rename_local_table(old_name: str, new_name: str):
    """
    Renames a physical local PostgreSQL table.
    """
    with engine.begin() as conn:
        conn.execute(text(f'ALTER TABLE "{old_name}" RENAME TO "{new_name}";'))

def drop_local_table(table_name: str):
    """
    Drops a physical local PostgreSQL table.
    """
    with engine.begin() as conn:
        conn.execute(text(f'DROP TABLE IF EXISTS "{table_name}";'))
