from backend.app.core.database import engine, Base
from backend.app.models.tms import PointDeVente, BaseLogistique, Transporteur, VehiculeType, Contrat

def init_db():
    print("Création des tables dans la base de données...")
    Base.metadata.create_all(bind=engine)
    print("Tables créées avec succès !")

if __name__ == "__main__":
    init_db()
