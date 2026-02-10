from faker import Faker
import random
from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.app.core.database import SessionLocal, engine, Base
from backend.app.models.tms import PointDeVente, BaseLogistique, Transporteur, VehiculeType, Contrat, AccessConstraint

fake = Faker('fr_FR')

def create_base_logistique(db: Session):
    """Création d'une base logistique centrale"""
    # Vérifie si existe déjà
    existing = db.execute(select(BaseLogistique)).scalars().first()
    if existing:
        print(f"Base Logistique déjà existante : {existing.nom}")
        return existing

    base = BaseLogistique(
        nom="Base Centrale - Orléans",
        geo_lat=47.9029,
        geo_lon=1.909,
        capacite_chargement=50, # 50 palettes/heure
        temps_service=30 # 30 min de chargement
    )
    db.add(base)
    db.commit()
    db.refresh(base)
    print(f"Base Logistique créée : {base.nom}")
    return base

def create_flotte(db: Session):
    """Création Transporteurs, Véhicules et Contrats"""
    # 1. Transporteurs
    t1 = Transporteur(nom="TransEco", contact_info="contact@transeco.fr")
    t2 = Transporteur(nom="FastLog", contact_info="dispatch@fastlog.com")
    db.add_all([t1, t2])
    db.commit()

    # 2. Types Véhicules
    v_semi = VehiculeType(
        nom="Semi-Remorque 33pal",
        capacite_poids=24000, capacite_volume=80, capacite_palettes=33,
        option_hayon=False, emission_co2_km=0.9
    )
    v_porteur = VehiculeType(
        nom="Porteur 18pal Hayon",
        capacite_poids=12000, capacite_volume=45, capacite_palettes=18,
        option_hayon=True, emission_co2_km=0.6
    )
    v_frigo = VehiculeType(
        nom="Semi-Frigo 33pal",
        capacite_poids=22000, capacite_volume=80, capacite_palettes=33,
        option_hayon=False, emission_co2_km=1.1
    )
    db.add_all([v_semi, v_porteur, v_frigo])
    db.commit()

    # 3. Contrats (Tarifs)
    # TransEco - Semi (Moins cher au KM)
    c1 = Contrat(
        transporteur_id=t1.id, vehicule_type_id=v_semi.id,
        cout_fixe_tournee=150.0, cout_km=1.2, cout_horaire=45.0
    )
    # FastLog - Porteur Hayon (Plus cher mais polyvalent)
    c2 = Contrat(
        transporteur_id=t2.id, vehicule_type_id=v_porteur.id,
        cout_fixe_tournee=120.0, cout_km=1.5, cout_horaire=50.0
    )
    # TransEco - Frigo
    c3 = Contrat(
        transporteur_id=t1.id, vehicule_type_id=v_frigo.id,
        cout_fixe_tournee=180.0, cout_km=1.4, cout_horaire=55.0
    )

    db.add_all([c1, c2, c3])
    db.commit()
    print("Flotte et Contrats créés.")

def create_pdvs(db: Session, base: BaseLogistique, count=50):
    """Création de N points de vente autour de la base"""
    print(f"Génération de {count} PDV...")
    
    for _ in range(count):
        # Génération coord aléatoire autour de la base (+/- 2 degres ~ 220km)
        lat = base.geo_lat + random.uniform(-2.0, 2.0)
        lon = base.geo_lon + random.uniform(-2.0, 2.0)
        
        # Contraintes aléatoires
        has_sas = random.choice([True, False])
        has_quai = random.choice([True, False])
        
        # Horaires
        h_min = random.choice([300, 360, 420]) # 5h, 6h, 7h
        h_max = h_min + random.choice([240, 480, 720]) # Fenêtre de 4h, 8h ou 12h

        access = AccessConstraint.STD
        if not has_sas and not has_quai:
             # Si pas d'équipement, parfois on force petit camion (simulé par contrainte)
             if random.random() < 0.3:
                 access = AccessConstraint.PORT

        pdv = PointDeVente(
            code_interne=fake.unique.bothify(text='??-####'),
            nom=fake.company(),
            adresse_complete=fake.address().replace('\n', ', '),
            geo_lat=lat,
            geo_lon=lon,
            livraison_sas_frais=has_sas,
            livraison_quai_frais=has_quai,
            contrainte_acces=access,
            horaire_livraison_min=h_min,
            horaire_livraison_max=h_max
        )
        db.add(pdv)
    
    db.commit()
    print(f"{count} PDV insérés.")

def seed():
    db = SessionLocal()
    try:
        # Nettoyage (Optionnel, ici on ajoute juste)
        # db.query(PointDeVente).delete() ...
        
        base = create_base_logistique(db)
        
        # Vérifie si flotte existe déjà
        if not db.execute(select(Transporteur)).scalars().first():
            create_flotte(db)
        
        # Vérifie nombre PDV
        pdv_count = len(db.execute(select(PointDeVente.id)).all())
        if pdv_count < 50:
            create_pdvs(db, base, count=50 - pdv_count)
        else:
            print(f"Déjà {pdv_count} PDV en base.")

    except Exception as e:
        print(f"Erreur seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
