from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, database
from services import bq_service, ai_service, db_service
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Seldon API")

# Create tables on startup
models.Base.metadata.create_all(bind=database.engine)

class TableRegister(BaseModel):
    full_table_id: str
    short_name: str

class TableSave(BaseModel):
    full_table_id: str
    short_name: str
    description: str
    schema: List[dict]
    tags: List[str] = []

class TableUpdate(BaseModel):
    short_name: str
    description: str
    tags: List[str] = []

class QueryRequest(BaseModel):
    prompt: str

@app.get("/tables")
def list_tables(db: Session = Depends(database.get_db)):
    return db.query(models.TableMetadata).all()

@app.post("/tables/analyze")
def analyze_table(req: TableRegister):
    try:
        schema = bq_service.get_table_schema(req.full_table_id)
        suggested_description = ai_service.generate_table_description(req.short_name, schema)
        return {
            "schema": schema,
            "suggested_description": suggested_description
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tables/save")
def save_table(req: TableSave, db: Session = Depends(database.get_db)):
    # 1. Ingest sample data to local Postgres
    try:
        df = bq_service.ingest_table_data(req.full_table_id)
        db_service.create_local_table_from_results(req.short_name, df, schema=req.schema)
        
        # 2. Save metadata
        ids = req.full_table_id.split(".")
        new_meta = models.TableMetadata(
            short_name=req.short_name,
            project_id=ids[0],
            dataset_id=ids[1],
            table_id=ids[2],
            description=req.description,
            schema_json=req.schema,
            tags=req.tags
        )
        db.add(new_meta)
        db.commit()
        return {"status": "success", "rows_ingested": len(df)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/tables/{table_id}")
def update_table(table_id: int, req: TableUpdate, db: Session = Depends(database.get_db)):
    table = db.query(models.TableMetadata).filter(models.TableMetadata.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    
    try:
        if table.short_name != req.short_name:
            db_service.rename_local_table(table.short_name, req.short_name)
            table.short_name = req.short_name
            
        table.description = req.description
        table.tags = req.tags
        db.commit()
        db.refresh(table)
        return {"status": "success", "message": "Tabla actualizada correctamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error renaming local table or saving: {str(e)}")

@app.delete("/tables/{table_id}")
def delete_table(table_id: int, db: Session = Depends(database.get_db)):
    table = db.query(models.TableMetadata).filter(models.TableMetadata.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    
    try:
        # 1. Drop physical table
        db_service.drop_local_table(table.short_name)
        
        # 2. Delete metadata
        db.delete(table)
        db.commit()
        return {"status": "success", "message": f"Tabla '{table.short_name}' eliminada correctamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting table: {str(e)}")

@app.post("/queries/generate")
def generate_query(req: QueryRequest, db: Session = Depends(database.get_db)):
    catalog = db.query(models.TableMetadata).all()
    catalog_list = [
        {
            "short_name": t.short_name, 
            "description": t.description, 
            "schema_json": t.schema_json,
            "full_id": f"{t.project_id}.{t.dataset_id}.{t.table_id}"
        }
        for t in catalog
    ]
    sql = ai_service.generate_sql_query(req.prompt, catalog_list)
    return {"sql": sql}

@app.post("/queries/execute")
def execute_ai_query(sql: str, target_table: str):
    try:
        # EXECUTE IN BIGQUERY DIRECTLY
        df = bq_service.run_bigquery_query(sql)
        # Still save results locally for quick view in Streamlit (sample/results)
        row_count = db_service.create_local_table_from_results(target_table, df)
        
        return {
            "total_records": row_count,
            "first_5": df.head(5).to_dict(orient="records"),
            "last_5": df.tail(5).to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
