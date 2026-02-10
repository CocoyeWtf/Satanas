# SPECIFICATION 02: CORE OPTIMIZATION ENGINE
**Validé par :** Lead Architect & Data Scientist
**Date :** 10/02/2026

## 1. Objectif du POC Solver
Résoudre un problème classique de **CVRP (Capacitated Vehicle Routing Problem)**, c'est-à-dire optimiser les tournées de véhicules ayant une capacité limitée pour livrer un ensemble de clients.

## 2. Inputs (Entrées)
Le moteur prendra en entrée :
1.  **Liste des Points de Vente (PDV)** :
    *   Coordonnées : Latitude / Longitude.
    *   Demande : Nombre de palettes à livrer.
    *   Identifiant unique.
2.  **Liste des Véhicules** :
    *   Capacité maximale : Nombre de palettes (ex: 33).
    *   Point de départ : Base Logistique (Lat/Lon).

## 3. Constraints (Contraintes)
### Hard Constraints (Obligatoires)
1.  **Capacité Véhicule** : La somme des demandes des PDV d'une tournée ne doit jamais dépasser la capacité du véhicule.
2.  **Visite Complète** : Tous les PDV doivent être visités exactement une fois.
3.  **Boucle Base** : Chaque véhicule part de la Base Logistique et y revient à la fin de la tournée.

### Soft Constraints (Objectif)
1.  **Minimiser la Distance Totale** : L'objectif principal est de réduire le kilométrage total parcouru par la flotte.

## 4. Modèle Mathématique & Distances
### Matrice de Distance
Le moteur OR-Tools nécessite une matrice de distances (ou de temps) entre tous les points.

### Formule de Haversine
Puisque nous travaillons avec des coordonnées géographiques (Latitude, Longitude), la distance euclidienne simple n'est pas précise.
Nous **DEVONS** utiliser la formule de **Haversine** pour calculer la distance "à vol d'oiseau" tenant compte de la courbure terrestre.

**Formule (approx) :**
a = sin²(Δlat/2) + cos(lat1) * cos(lat2) * sin²(Δlon/2)
c = 2 * atan2(√a, √(1-a))
d = R * c
(où R est le rayon de la Terre ~ 6371 km)

## 5. Architecture Technique (OR-Tools)
- Utilisation du `RoutingIndexManager` et `RoutingModel`.
- Utilisation de `AddDimension` pour gérer la capacité ("Capacity").
- Stratégie de recherche initiale : `PATH_CHEAPEST_ARC` (bon compromis vitesse/qualité).
- Stratégie de méta-heuristique : `GUIDED_LOCAL_SEARCH` (pour sortir des minimums locaux).
