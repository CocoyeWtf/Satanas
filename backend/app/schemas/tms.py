from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from uuid import UUID

class PDVResponse(BaseModel):
    id: UUID
    code_interne: str
    nom: str
    geo_lat: float
    geo_lon: float
    livraison_sas_frais: bool
    livraison_quai_frais: bool
    contrainte_acces: str
    
    class Config:
        from_attributes = True # ORM Mode

class OptimizationRequest(BaseModel):
    date_tournee: date
    vehicle_ids: Optional[List[UUID]] = None

class VolumeImportResult(BaseModel):
    total_rows_processed: int
    updated_pdvs: int
    errors: list[str] = []
