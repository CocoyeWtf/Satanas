# ÉTAT MAJOR - PROJET SATANAS
**Dernière mise à jour :** 10/02/2026
**Phase Actuelle :** 1. Fondations & Data Modeling
**Mode Opératoire :** Protocol "Sovereign Pipeline" (Spec -> Test -> Code -> Audit)

## 1. VISION ARCHITECTE (ARCH)
- **Objectif :** MVP Optimiseur de tournée (Local First).
- **Architecture :** Backend FastAPI (Python) + Frontend React.
- **Data :** SQLite (Dev) -> PostgreSQL (Prod).
- **Core Logic :** Google OR-Tools.

## 2. ÉTAT DU DÉVELOPPEMENT (DEV)
- [x] Initialisation Git & Repo.
- [x] Structure des dossiers créée.
- [x] Environnement virtuel (venv) & Requirements installés.
- [ ] Création des Modèles de Données (SQLAlchemy).
- [ ] Tests Unitaires des Modèles.
- [ ] API CRUD de base.

## 3. POINTS DE VIGILANCE (QA)
- **Attention :** Les contraintes horaires (Time Windows) sont critiques. Le modèle de données doit gérer le format HH:MM avec précision.
- **Attention :** La distinction "Terme Fixe" unique vs multiple dans les contrats transporteurs doit être gérée dès le modèle de données.
- **Sécurité :** Pas de données sensibles en dur dans le code.

## 4. DIRECTIVES PERMANENTES
- Pas de code sans Spec Markdown préalable.
- Pas d'implémentation sans Tests définis (TDP).
- Revue critique automatique avant livraison.