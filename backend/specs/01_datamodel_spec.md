# SPECIFICATION 01: DATA MODEL (CORE)
**Validé par :** Arch & QA
**Date :** 10/02/2026

## 1. Entité: PointDeVente (PDV)
Représente un magasin à livrer.

| Champ | Type | Contrainte | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PK | Identifiant unique interne |
| `code_interne` | String | Unique, Index | Code magasin (ex: FR0123) |
| `nom` | String | | Nom commercial |
| `adresse_...` | String | | Adr, CP, Ville, Pays |
| `geo_lat` | Float | -90 à +90 | Latitude |
| `geo_lon` | Float | -180 à +180 | Longitude |
| `livraison_sas_frais` | Bool | Default False | Possède un SAS Frais |
| `livraison_quai_frais` | Bool | Default False | Possède un Quai Frais |
| `contrainte_acces` | Enum | [STD, PORT, ELEC] | Type camion obligatoire |
| `horaire_livraison_min`| Int | 0-1440 | Minutes depuis minuit (ex: 360 = 6h00) |
| `horaire_livraison_max`| Int | 0-1440 | Minutes depuis minuit |

**Règles de Validation (QA Logic):**
- Si `livraison_sas_frais` et `livraison_quai_frais` sont FALSE => Nécessite Véhicule avec HAYON.
- `horaire_livraison_max` doit être > `horaire_livraison_min`.

## 2. Entité: BaseLogistique
Le point de départ des camions.

| Champ | Type | Description |
| :--- | :--- | :--- |
| `id` | UUID | PK |
| `nom` | String | |
| `geo_lat/lon` | Float | Coordonnées |
| `capacite_chargement`| Int | Nb palettes / heure max |
| `temps_service` | Int | Temps moyen de chargement (min) |

## 3. Entité: Flotte & Contrats
Complexité : Liaison entre Transporteur, Véhicules et Coûts.

### 3.1 Transporteur
- Nom, Contact.

### 3.2 VehiculeType (Category)
- `nom` (ex: "Semi-Frigo 33pal")
- `capacite_poids` (kg)
- `capacite_volume` (m3)
- `capacite_palettes` (int)
- `option_hayon` (Bool)
- `emission_co2_km` (Float)

### 3.3 GrilleTarifaire (Contrat)
Lien entre un Transporteur et un Type de Véhicule.
- `cout_fixe_tournee` (Decimal) : Coût d'engagement (Terme fixe).
- `cout_km` (Decimal) : Prix au kilomètre.
- `cout_horaire` (Decimal) : Optionnel (si attente).
