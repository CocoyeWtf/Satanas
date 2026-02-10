# SPECIFICATION 03: REST API ARCHITECTURE
**Validé par :** Lead Backend Architect
**Date :** 10/02/2026

## 1. Architecture Layered
L'API doit suivre une architecture en couches stricte pour assurer la maintenabilité et la testabilité.

`Router` -> `Controller` -> `Service` -> `Solver (Core)`

- **Router (API Layer)** : Définit les endpoints, valide les entrées (Pydantic), gère les codes HTTP.
- **Controller/Service (Business Layer)** : Orchestre la logique métier, appelle la DB, appelle le Solver.
- **Solver (Core Layer)** : Le moteur pur (OR-Tools) qui ne connaît pas le contexte HTTP.

## 2. Endpoints Requis (MVP)

### 2.1 Points de Vente (Reference Data)
- **GET** `/api/v1/pdvs`
  - **Description** : Récupère la liste de tous les magasins à livrer.
  - **Output** : JSON Array `[ {id, nom, lat, lon, ...} ]`

### 2.2 Flotte (Reference Data)
- **GET** `/api/v1/vehicles`
  - **Description** : Récupère la liste des véhicules et transporteurs disponibles.
  - **Output** : JSON Array `[ {id, type, transporteur, capacite, ...} ]`

### 2.3 Optimization (Action)
- **POST** `/api/v1/optimize`
  - **Description** : Lance le moteur d'optimisation sur les données actuelles.
  - **Input (Body)** :
    ```json
    {
      "date": "2026-02-11",
      "vehicle_ids": ["uuid-1", "uuid-2"] // Optionnel (sinon tous)
    }
    ```
  - **Output (Result)** :
    ```json
    {
      "status": "OPTIMAL",
      "total_distance_meters": 150000,
      "routes": [
        {
          "vehicle_id": "uuid-1",
          "steps": [
            {"stop_type": "DEPOT", "name": "Base Logistique"},
            {"stop_type": "DELIVERY", "name": "Magasin A", "palettes": 5},
            {"stop_type": "DEPOT", "name": "Base Logistique"}
          ],
          "distance_meters": 50000
        }
      ]
    }
    ```

## 3. Gestion des Erreurs (QA Vigilance)
- **400 Bad Request** : Si les paramètres d'entrée sont invalides.
- **422 Unprocessable Entity** : Si le solver ne trouve pas de solution possible (ex: capacité insuffisante).
- **500 Internal Server Error** : Crash inattendu du moteur.
