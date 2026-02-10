# ACTION PLAN - SATANAS V1.0 INITIALIZATION
**Phase:** 0 - Setup & Foundation

## OBJECTIF IMMÉDIAT
Mettre en place l'environnement de développement "Vibe Coding" (VSCode + IA) et structurer la base de données.

## ÉTAPES

### 1. Initialisation de l'Environnement (Tech Setup)
- [ ] Créer le dossier projet `SATANAS_TMS`.
- [ ] Initialiser Git (`git init`).
- [ ] Créer l'environnement virtuel Python (`python -m venv venv`).
- [ ] Créer la structure de dossiers :
    - `/backend` (FastAPI)
    - `/frontend` (React/Vite)
    - `/data` (Pour les fichiers Excel sources et la DB SQLite/Postgres)
    - `/docs` (Pour stocker le CDC et les specs)

### 2. Définition du Modèle de Données (Backend)
- [ ] Installer FastAPI et SQLAlchemy.
- [ ] Créer les modèles Python (`models.py`) correspondant au CDC :
    - `PDV`, `BaseLogistique`, `Transporteur`, `Vehicule`, `Contrat`.
- [ ] Créer un script de "Seed" (données factices) pour tester rapidement (5 PDV, 1 Base, 2 Camions).

### 3. Prototype Moteur OR-Tools (Core)
- [ ] Installer `ortools` et `pandas`.
- [ ] Créer un script Python isolé `optimizer_poc.py`.
- [ ] Coder un scénario simple : 1 Dépôt -> 5 PDV avec fenêtres horaires.
- [ ] Valider que OR-Tools sort une solution en < 5 secondes.

### 4. Interface Utilisateur (Skeleton)
- [ ] Initialiser le projet React (Vite + TypeScript).
- [ ] Installer Tailwind CSS + ShadCN (pour le Dark Mode "Pro").
- [ ] Créer la page d'accueil (Dashboard vide).

---
**Note pour l'utilisateur :** Ne pas essayer de tout faire en même temps. On commence par le **Point 1 et 2**.



--- AEGIS METADATA ---
ID: 18b625d5-c3c7-4cc4-86b9-53eb1e788842
TYPE: NOTE
STATUS: ACTIVE
TAGS: 