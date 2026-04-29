-- NOTE : ces requetes sont à exécuter dans le fichier analyse_marche_it_maroc.ipynb sous l'environnement DuckDB après avoir chargé les données transformées dans les fichiers Parquet situés dans les dossiers GOLD et SILVER.

-- ----------------------------------------------------------------------------
-- Q1 : QUELLES SONT LES COMPÉTENCES LES PLUS DEMANDÉES (TOP 15 PROFILS DATA) ?
-- ----------------------------------------------------------------------------
SELECT competence, nb_offres_mentionnent, famille
    FROM read_parquet('{GOLD_PATH}/top_competences.parquet')
    WHERE profil = 'Data Engineer' OR profil = 'Data Analyst' OR profil = 'Data Scientist'
    ORDER BY nb_offres_mentionnent DESC
    LIMIT 15;


-- ----------------------------------------------------------------------------
-- Q2 : TANGER VS CASABLANCA VS RABAT (VOLUME ET TÉLÉTRAVAIL)
-- ----------------------------------------------------------------------------
   SELECT ville, SUM(nb_offres) as total_offres, 
           ROUND(AVG(nb_offres_remote * 100.0 / nb_offres), 1) as avg_pct_remote
    FROM read_parquet('{GOLD_PATH}/offres_par_ville.parquet')
    WHERE ville IN ('Casablanca', 'Rabat', 'Tanger')
    GROUP BY ville
    ORDER BY total_offres DESC;


-- ----------------------------------------------------------------------------
-- Q3 : QUEL EST LE SALAIRE MÉDIAN PAR PROFIL IT AU MAROC ?
-- ----------------------------------------------------------------------------
    SELECT profil, salaire_median
    FROM read_parquet('{GOLD_PATH}/salaires_par_profil.parquet')
    GROUP BY profil, salaire_median
    ORDER BY salaire_median DESC;


-- ----------------------------------------------------------------------------
-- Q4 : CORRÉLATION ENTRE EXPÉRIENCE MINIMALE ET SALAIRE PROPOSÉ
-- ----------------------------------------------------------------------------
-- Cette requête calcule la corrélation de Pearson nativement dans DuckDB
    SELECT experience_min, salaire_median_mad
    FROM read_parquet('{SILVER_PATH}/offres_clean/offres_clean.parquet')
    WHERE salaire_connu = True AND experience_min IS NOT NULL;


-- ----------------------------------------------------------------------------
-- Q5 : ANALYSE DE LA CONCURRENCE (TOP 10 DES RECRUTEURS)
-- ----------------------------------------------------------------------------
    SELECT entreprise, nb_offres_publiees, salaire_moyen_propose
    FROM read_parquet('{GOLD_PATH}/entreprises_recruteurs.parquet')
    ORDER BY nb_offres_publiees DESC
    LIMIT 10;


