from sqlalchemy import Column, Integer, String, JSON, DateTime, Text
from sqlalchemy.sql import func
from database import Base

class TableMetadata(Base):
    __tablename__ = "table_metadata"

    id = Column(Integer, primary_key=True, index=True)
    short_name = Column(String, unique=True, index=True, nullable=False)
    project_id = Column(String, nullable=False)
    dataset_id = Column(String, nullable=False)
    table_id = Column(String, nullable=False)
    description = Column(String)
    schema_json = Column(JSON)  # Stores the BigQuery schema as a list of dicts
    tags = Column(JSON, default=list) # Guards a list of strings o dicts
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def full_remote_id(self):
        return f"{self.project_id}.{self.dataset_id}.{self.table_id}"


class SavedQuery(Base):
    __tablename__ = "saved_queries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    sql_query = Column(Text, nullable=False)
    tags = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
