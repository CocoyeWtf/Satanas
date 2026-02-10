from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from backend.app.core.database import SessionLocal
from backend.app.models.tms import PointDeVente, Transporteur, VehiculeType
from backend.app.schemas.tms import PDVResponse, OptimizationRequest, VolumeImportResult
from backend.app.services.ingest import process_excel_volumes
from backend.app.services.optimization import OptimizationService

router = APIRouter()

# Dependency DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ROUTES ---

@router.get("/pdvs", response_model=List[PDVResponse])
def get_pdvs(db: Session = Depends(get_db)):
    """Liste tous les Points de Vente"""
    pdvs = db.execute(select(PointDeVente)).scalars().all()
    return pdvs

@router.post("/ingest/volumes", response_model=VolumeImportResult)
async def ingest_volumes(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload et traitement du fichier Excel des volumes"""
    if not file.filename.endswith(('.xls', '.xlsx')):
        raise HTTPException(status_code=400, detail="Format invalide (Excel only)")
    
    content = await file.read()
    result = process_excel_volumes(content, db)
    
    if result.errors and result.updated_pdvs == 0:
         raise HTTPException(status_code=422, detail=result.errors[0])
         
    return result

@router.post("/optimize")
def run_optimization(request: OptimizationRequest, db: Session = Depends(get_db)):
    """Lance le moteur d'optimisation via le Service"""
    service = OptimizationService()
    
    # Nombre de véhicules (Default 5 si non spécifié)
    v_count = 5
    if request.vehicle_ids:
        v_count = len(request.vehicle_ids)
        
    try:
        result = service.solve_tour(db, vehicules_count=v_count)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
