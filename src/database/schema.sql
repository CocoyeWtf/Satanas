-- Initialisation Schema SATANAS

-- 1. Bases Logistiques (Pré-requis pour PDV)
CREATE TABLE IF NOT EXISTS bases (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    nom VARCHAR(100) NOT NULL
);

-- 2. Points de Vente (PDV)
CREATE TABLE IF NOT EXISTS points_de_vente (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    nom VARCHAR(100) NOT NULL,
    adresse TEXT,
    code_postal VARCHAR(10),
    ville VARCHAR(100),
    contrainte_sas BOOLEAN DEFAULT FALSE,
    contrainte_acces TEXT, -- Ex: "Petit porteur uniquement"
    base_id INTEGER REFERENCES bases(id)
);

-- 3. Véhicules
CREATE TABLE IF NOT EXISTS vehicules (
    id SERIAL PRIMARY KEY,
    immatriculation VARCHAR(20) UNIQUE NOT NULL,
    type_froid VARCHAR(50) NOT NULL, -- Ex: "BI-TEMP", "FRIGO"
    capacite_eqp INTEGER NOT NULL, -- Capacité en pal
    tarif_journalier NUMERIC(10, 2),
    tarif_km NUMERIC(10, 2)
);

-- 4. Cadenciers (Grille 7 jours / 3 gammes)
CREATE TABLE IF NOT EXISTS cadenciers (
    id SERIAL PRIMARY KEY,
    pdv_id INTEGER NOT NULL REFERENCES points_de_vente(id) ON DELETE CASCADE,
    gamme VARCHAR(20) NOT NULL CHECK (gamme IN ('SEC', 'FRAIS', 'SURGELE')),
    jour_livraison INTEGER NOT NULL CHECK (jour_livraison BETWEEN 1 AND 7), -- 1=Lundi
    -- Règle A pour C (Commande = Livraison - 2 jours) 
    -- Si Livraison Lun(1) -> Commande Sam(6). Si Mer(3) -> Lun(1).
    jour_commande INTEGER NOT NULL CHECK (jour_commande BETWEEN 1 AND 7),
    UNIQUE(pdv_id, gamme, jour_livraison)
);

-- 5. Commandes (Flux)
CREATE TABLE IF NOT EXISTS commandes (
    id SERIAL PRIMARY KEY,
    numero_commande VARCHAR(50) UNIQUE NOT NULL,
    pdv_id INTEGER NOT NULL REFERENCES points_de_vente(id),
    gamme VARCHAR(20) NOT NULL,
    volume_eqp NUMERIC(5, 2) NOT NULL, -- Nombre de palettes (ex: 1.5)
    poids_kg NUMERIC(10, 2),
    
    -- Fenêtres de temps (TIMESTAMP)
    -- fenetre_debut : Moment où la commande est prête ou début de créneau (Jour B)
    -- fenetre_fin : Limite de livraison (Jour C 06h00 / 09h00)
    fenetre_debut TIMESTAMP NOT NULL,
    fenetre_fin TIMESTAMP NOT NULL,
    
    statut VARCHAR(20) DEFAULT 'A_PLANIFIER' CHECK (statut IN ('A_PLANIFIER', 'PLANIFIE', 'LIVRE', 'ANNULE')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour performance
CREATE INDEX idx_cadenciers_pdv ON cadenciers(pdv_id);
CREATE INDEX idx_commandes_fenetre ON commandes(fenetre_fin);
