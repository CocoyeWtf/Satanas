from fastapi.testclient import TestClient
from backend.app.main import app
import pytest

client = TestClient(app)

def test_read_pdvs():
    response = client.get("/api/v1/pdvs")
    assert response.status_code == 200
    pdvs = response.json()
    assert isinstance(pdvs, list)
    # On s'attend à avoir des PDV si le seed a tourné
    if len(pdvs) > 0:
        assert "code_interne" in pdvs[0]

def test_optimize_endpoint_success():
    # Payload valide
    payload = {
        "date_tournee": "2026-02-11",
        "vehicle_ids": [] # Liste vide = default (5)
    }
    
    response = client.post("/api/v1/optimize", json=payload)
    
    # Vérification Basic
    assert response.status_code == 200, f"Erreur API: {response.text}"
    
    data = response.json()
    
    # Vérification Structure JSON
    assert "status" in data
    assert "total_distance_meters" in data
    assert "routes" in data
    
    # Vérification Contenu Routes
    routes = data["routes"]
    assert len(routes) == 5 # Default 5 véhicules
    
    # Vérification d'une route
    route_0 = routes[0]
    assert "steps" in route_0
    assert "distance_meters" in route_0
    
    # Check Steps structure
    if len(route_0["steps"]) > 0:
        step = route_0["steps"][0]
        assert step["stop_type"] == "DEPOT" # Doit commencer par Depot
