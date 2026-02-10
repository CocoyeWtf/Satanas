from typing import Optional, List
from sqlalchemy import String, Float, Boolean, Integer, ForeignKey, Enum as SQLEnum, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid
import uuid
import enum

from backend.app.core.database import Base

# Enums
class AccessConstraint(str, enum.Enum):
    STD = "STD"
    PORT = "PORT"
    ELEC = "ELEC"

# 1. PointDeVente (PDV)
class PointDeVente(Base):
    __tablename__ = "point_de_vente"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code_interne: Mapped[str] = mapped_column(String, unique=True, index=True)
    nom: Mapped[str] = mapped_column(String)
    adresse_complete: Mapped[Optional[str]] = mapped_column(String) # Simplifié pour l'instant
    geo_lat: Mapped[float] = mapped_column(Float)
    geo_lon: Mapped[float] = mapped_column(Float)
    
    livraison_sas_frais: Mapped[bool] = mapped_column(Boolean, default=False)
    livraison_quai_frais: Mapped[bool] = mapped_column(Boolean, default=False)
    
    contrainte_acces: Mapped[AccessConstraint] = mapped_column(SQLEnum(AccessConstraint), default=AccessConstraint.STD)
    
    horaire_livraison_min: Mapped[int] = mapped_column(Integer) # Minutes depuis minuit
    horaire_livraison_max: Mapped[int] = mapped_column(Integer) # Minutes depuis minuit

    # Contraintes Check (SQLite supporte CHECK)
    __table_args__ = (
        CheckConstraint('geo_lat >= -90 AND geo_lat <= 90', name='check_lat'),
        CheckConstraint('geo_lon >= -180 AND geo_lon <= 180', name='check_lon'),
        CheckConstraint('horaire_livraison_max > horaire_livraison_min', name='check_horaire_coherence'),
    )

    def get_required_vehicle_options(self):
        """Détermine les options véhicule requises"""
        # Règle 3 : Validation SAS/Quai => Hayon
        if not self.livraison_sas_frais and not self.livraison_quai_frais:
            return {"hayon": True}
        return {"hayon": False}

# 2. BaseLogistique
class BaseLogistique(Base):
    __tablename__ = "base_logistique"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom: Mapped[str] = mapped_column(String)
    geo_lat: Mapped[float] = mapped_column(Float)
    geo_lon: Mapped[float] = mapped_column(Float)
    capacite_chargement: Mapped[int] = mapped_column(Integer) # Palettes/heure
    temps_service: Mapped[int] = mapped_column(Integer) # Minutes

# 3. Flotte & Contrats

class Transporteur(Base):
    __tablename__ = "transporteur"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom: Mapped[str] = mapped_column(String)
    contact_info: Mapped[Optional[str]] = mapped_column(String)

    # Relations
    contrats: Mapped[List["Contrat"]] = relationship(back_populates="transporteur")

class VehiculeType(Base):
    __tablename__ = "vehicule_type"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom: Mapped[str] = mapped_column(String) # ex: Semi-Frigo 33pal
    capacite_poids: Mapped[float] = mapped_column(Float) # kg
    capacite_volume: Mapped[float] = mapped_column(Float) # m3
    capacite_palettes: Mapped[int] = mapped_column(Integer)
    option_hayon: Mapped[bool] = mapped_column(Boolean, default=False)
    emission_co2_km: Mapped[float] = mapped_column(Float)

    # Relations
    contrats: Mapped[List["Contrat"]] = relationship(back_populates="vehicule_type")

class Contrat(Base):
    """Grille Tarifaire : Lien Transporteur <-> Véhicule"""
    __tablename__ = "contrat"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    transporteur_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("transporteur.id"))
    vehicule_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("vehicule_type.id"))
    
    cout_fixe_tournee: Mapped[float] = mapped_column(Float) # Decimal en prod, Float en SQLite/Dev
    cout_km: Mapped[float] = mapped_column(Float)
    cout_horaire: Mapped[Optional[float]] = mapped_column(Float)

    # Relations
    transporteur: Mapped["Transporteur"] = relationship(back_populates="contrats")
    vehicule_type: Mapped["VehiculeType"] = relationship(back_populates="contrats")
