# # SATANAS V1.0 - MASTER TECHNICAL SPECIFICATION

**Version:** 1.0 | **Date:** 10/02/2026
**Ref:** Based on User CDC 09/02/2026
**Tech Stack Mandated:** Python, Google OR-Tools, Modern Web Stack

## 1. VISION DU PROJET
Développement d'un logiciel professionnel d'optimisation de tournées de livraison (TMS - Transport Management System) pour la grande distribution (Frais, Sec, Gel).
**Objectif critique :** Optimisation des coûts (Km + Terme fixe) sous contraintes horaires strictes.
**Philosophie :** "Local First" pour la phase 1, évolutif vers architecture Web/Cloud.

## 2. STACK TECHNIQUE & ARCHITECTURE
L'architecture est choisie pour sa robustesse, sa capacité de calcul et sa facilité de déploiement (Docker ready).

* **Backend (API & Logic) :** Python 3.11+
    * *Framework :* **FastAPI** (Performance, typage strict, documentation auto).
    * *Algorithmique :* **Google OR-Tools** (Module Constraint Programming & Routing).
    * *Data Processing :* Pandas (Manipulation des volumes et exports Excel).
* **Frontend (UI) :**
    * *Framework :* **React** (TypeScript) + Vite.
    * *UI Library :* ShadCN/UI ou Material UI (Customisé).
    * *Design System :* Dark Mode Force (Noir, Gris, Orange, Blanc, Rouge). Pas de bleu.
* **Base de Données :**
    * *Phase 1 (Local) :* **SQLite** (fichiers locaux, rapide pour setup) ou **PostgreSQL** via Docker (recommandé dès le début pour la compatibilité JSON et géo).
    * *ORM :* SQLAlchemy ou Prisma.
* **Infrastructure :** Conteneurisation Docker recommandée pour isoler l'environnement de calcul.

## 3. DOMAINE MÉTIER & DATA MODEL (ENTITÉS)

### 3.1. Points de Vente (PDV)
* **Attributs :** ID, Nom, Adresse, Lat/Lon, Type (Hyper, Super, etc.), Pays/Région.
* **Contraintes Logistiques (Le "Contrat d'Interface") :**
    * SAS (Frais/Sec/Gel) : Booléen + Capacité (nb palettes/combis).
    * Quai (Frais/Sec/Gel) : Booléen (implique besoin Hayon si Faux).
    * Accessibilité : Camion électrique, Surbaissé, Porteur uniquement.
    * Horaires :
        * Avec SAS : Livraison avant 06:00.
        * Sans SAS : Livraison avant 09:00.
        * Exceptions (Arrêtés, travaux).

### 3.2. Bases Logistiques (Hubs)
* **Attributs :** ID, Lat/Lon, Horaires ouverture.
* **Capacités :** Capacité chargement/heure, Capacité rétention quais.

### 3.3. Flotte & Contrats Transporteurs
* **Véhicules :**
    * Types : Tracteur+Semi (25-27t, 33 EQP), Porteur (9-26t), Porteur+Remorque.
    * Spécificités : Fourgon, Frigo (Mono/Bi-temp), City.
* **Modèle de Coût (Objective Function) :**
    * Type A : Prix au km.
    * Type B : Terme fixe (par tournée) + Prix au km.
    * *Règle métier critique :* Si un camion fait plusieurs tours, le terme fixe peut être unique ou multiple selon contrat (à paramétrer).

### 3.4. Commandes & Volumes (Flux)
* Types de flux : Suivi (Fond de rayon) vs MEA (Promo).
* Unité : Support (Palette ou Combi).
* *Variable d'ajustement :* La MEA est utilisée pour saturer les camions (remplissage 100%).

## 4. LOGIQUE ALGORITHMIQUE (LE CŒUR OR-TOOLS)

L'algorithme doit résoudre un **CVRPTW** (Capacitated Vehicle Routing Problem with Time Windows) enrichi.

### 4.1. Paramètres de l'Solver
* **Time Limit :** 5 minutes max.
* **Priorités (Hard Constraints) :**
    1.  Respect des Time Windows (Horaires PDV).
    2.  Respect des capacités Véhicules (Poids/Volume/EQP).
    3.  Compatibilité Véhicule/PDV (Accès, Hayon).
* **Fonction Objectif (Soft Constraints / Minimization) :**
    1.  Minimiser le Coût Total (Somme des Termes Fixes + Coûts Kilométriques).
    2.  Maximiser le Remplissage (Utilisation MEA).

### 4.2. Workflow de Calcul
1.  **Ingest :** Import des volumes (Excel/JSON) + Disponibilité Flotte.
2.  **Pre-Process :** Calcul/Récupération Matrice de distances (Distancier local ou API).
3.  **Core Optimization (OR-Tools) :**
    * Passe 1 : Placement des impératifs (Suivi).
    * Passe 2 : Comblement avec MEA (Variable d'ajustement).
4.  **Post-Process :** Génération des feuilles de route, Chiffrage prévisionnel.

## 5. FONCTIONNALITÉS UTILISATEUR (UI)

### 5.1. Écrans Principaux
* **Dashboard KPI :** Coût/Tour, Km/Tour, Remplissage %, Nb Colis/Tour.
* **Gestion des Données (CRUD) :** PDV, Bases, Transporteurs (Contrats), Flotte.
* **Planification (L'Optimiseur) :**
    * Import fichiers volumes.
    * Lancement calcul.
    * Vue Gantt / Carte des tournées.
    * Ajustement manuel (Drag & Drop) par l'exploitant.
* **Suivi Opérationnel :** Statut (Préparé, Chargé, Parti).
* **Facturation :** Synthèse pré-facturation transporteur.

### 5.2. Sécurité & UX
* **Auth :** RBAC (Rôles : Admin, Exploitant, Viewer).
* **Design :** Mode sombre strict. Ergonomie "Pro" (dense, informatif).

## 6. ROADMAP & PHASING

### Phase 1 (MVP - Le périmètre actuel)
* Base de données complète & Interface de gestion.
* Moteur d'optimisation OR-Tools fonctionnel (Local).
* Gestion des coûts complexes (Fixe + Variable).
* Export Excel des feuilles de route.
* Calcul de pré-facturation.

### Phase 2 (Évolutions futures)
* Enlèvements fournisseurs (Backhaul).
* Application Mobile Chauffeur (Preuve de livraison, Géoloc).
* API Distancier externe.



--- AEGIS METADATA ---
ID: 0b969572-5e98-4629-a616-ac90c1bd2635
TYPE: NOTE
STATUS: ACTIVE
TAGS: 