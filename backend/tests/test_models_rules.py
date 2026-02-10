import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from backend.app.core.database import Base
from backend.app.models.tms import PointDeVente, AccessConstraint

# --- FIXTURE DB (SQLite Memory) ---

@pytest.fixture(scope="module")
def db_session():
    # Création d'une DB en mémoire pour les tests
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine) # Création des tables
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

# --- TESTS D'INTÉGRATION (Modèles Réels) ---

def test_validation_sas_quai():
    """Test 1 (Spec): Si ni SAS ni Quai => Hayon requis"""
    # Cas 1: Pas de SAS, Pas de Quai -> Hayon requis
    pdv_difficile = PointDeVente(
        code_interne="TEST01", nom="Petit Magasin", 
        geo_lat=48.8, geo_lon=2.3,
        livraison_sas_frais=False, livraison_quai_frais=False,
        horaire_livraison_min=0, horaire_livraison_max=1440
    )
    opts = pdv_difficile.get_required_vehicle_options()
    assert opts["hayon"] is True, "Un magasin sans SAS ni Quai DOIT nécessiter un Hayon"

    # Cas 2: Avec Quai -> Pas besoin de Hayon (implicite)
    pdv_facile = PointDeVente(
        code_interne="TEST02", nom="Grand Magasin",
        geo_lat=48.8, geo_lon=2.3,
        livraison_sas_frais=False, livraison_quai_frais=True,
        horaire_livraison_min=0, horaire_livraison_max=1440
    )
    opts = pdv_facile.get_required_vehicle_options()
    assert opts["hayon"] is False, "Un magasin avec Quai ne devrait pas imposer un Hayon"

def test_validation_horaire(db_session):
    """Test 2 (Spec): horaire_min <= horaire_max (Check Constraint DB)"""
    # Cas valide
    pdv = PointDeVente(
        code_interne="TEST03", nom="Valid Hours",
        geo_lat=48.8, geo_lon=2.3,
        horaire_livraison_min=360, # 6h00
        horaire_livraison_max=720  # 12h00
    )
    db_session.add(pdv)
    db_session.commit() # Devrait passer sans erreur

    # Cas invalide
    pdv_invalid = PointDeVente(
        code_interne="TEST04", nom="Invalid Hours",
        geo_lat=48.8, geo_lon=2.3,
        horaire_livraison_min=800,
        horaire_livraison_max=600 # Min > Max !
    )
    db_session.add(pdv_invalid)
    
    # SQLite lève l'erreur au moment du commit pour les Check Constraints
    with pytest.raises(IntegrityError) as excinfo:
        db_session.commit()
    
    db_session.rollback() # Important pour nettoyer la session après l'erreur

def test_validation_coordinates(db_session):
    """Test 3 (Spec): Latitude doit être entre -90 et +90 (Check Constraint DB)"""
    # Cas invalide : Latitude trop grande
    pdv_out = PointDeVente(
        code_interne="TEST05", nom="Space Shop",
        geo_lat=95.0, # Hors limite
        geo_lon=2.3,
        horaire_livraison_min=0, horaire_livraison_max=1440
    )
    db_session.add(pdv_out)

    with pytest.raises(IntegrityError):
        db_session.commit()
    
    db_session.rollback()
