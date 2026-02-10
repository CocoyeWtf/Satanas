import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.app.models.tms import PointDeVente
from backend.app.schemas.tms import VolumeImportResult
from typing import BinaryIO

def process_excel_volumes(file_content: bytes, db: Session) -> VolumeImportResult:
    """
    Traite le fichier Excel des volumes.
    - Header en ligne 4 (index 3).
    - Col A: Code PDV.
    - Col C: EQC.
    - Conversion : Palettes = EQC / 1.64.
    """
    try:
        # Lecture Excel (BytesIO)
        # engine="openpyxl" requis pour .xlsx
        df = pd.read_excel(file_content, header=3, engine="openpyxl")
        
        result = VolumeImportResult(total_rows_processed=0, updated_pdvs=0)
        
        seen_codes = set()
        
        # Itération simple (optimisable en batch plus tard)
        for index, row in df.iterrows():
            result.total_rows_processed += 1
            
            # Extraction SAFE
            code_pdv = str(row.iloc[0]).strip() # Col A
            eqc_val = row.iloc[2] # Col C
            
            if pd.isna(code_pdv) or code_pdv == 'nan':
                continue
                
            if pd.isna(eqc_val):
                eqc_val = 0.0
            
            # Calcul Logique métier
            try:
                palettes = float(eqc_val) / 1.64
            except ValueError:
                result.errors.append(f"Row {index+4}: Invalid EQC value '{eqc_val}'")
                continue

            # Simulation update DB (TODO: champ 'demande_palettes' dans le modèle)
            pdv = db.execute(select(PointDeVente).where(PointDeVente.code_interne == code_pdv)).scalars().first()
            if pdv:
                # Ici on simule une mise à jour. 
                # Dans le vrai modèle, on aurait un champ 'daily_demand' ou une table liée.
                # print(f"Update PDV {code_pdv}: {palettes:.2f} palettes")
                result.updated_pdvs += 1
                seen_codes.add(code_pdv)
            else:
                # print(f"PDV not found: {code_pdv}")
                pass
                
        return result

    except Exception as e:
        return VolumeImportResult(total_rows_processed=0, updated_pdvs=0, errors=[str(e)])
