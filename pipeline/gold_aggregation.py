import duckdb
from pathlib import Path

def construire_gold(data_lake_root: Path):
    """
    Utilise DuckDB pour créer les tables Gold à partir des fichiers Silver Parquet.
    """
    silver_offres  = data_lake_root / 'silver' / 'offres_clean' / 'offres_clean.parquet'
    silver_comp    = data_lake_root / 'silver' / 'competences_extraites' / 'competences.parquet'
    gold_path      = data_lake_root / 'gold'
    gold_path.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect()

    print("[GOLD] Début de la construction des tables analytiques...")

    # --- Table Gold 1 : Top compétences par profil ---
    print("[GOLD] 1/5 - Calcul des top compétences...")
    df_top_comp = con.execute(f"""
        SELECT 
            profil,
            famille,
            competence,
            COUNT(DISTINCT id_offre) AS nb_offres_mentionnent,
            RANK() OVER (PARTITION BY profil ORDER BY COUNT(DISTINCT id_offre) DESC) as rang
        FROM '{silver_comp}'
        WHERE competence != 'non_détecté'
        GROUP BY profil, famille, competence
    """).df()
    df_top_comp.to_parquet(gold_path / 'top_competences.parquet')

    # --- Table Gold 2 : Salaires par profil et ville ---
    print("[GOLD] 2/5 - Calcul des statistiques salariales...")
    # Correction : On utilise les noms originaux des colonnes dans le GROUP BY
    df_salaires = con.execute(f"""
        SELECT 
            profil_normalise AS profil,
            ville_std AS ville,
            COUNT(*) AS nb_offres,
            ROUND(AVG(salaire_median_mad), 0) AS salaire_moyen,
            ROUND(MEDIAN(salaire_median_mad), 0) AS salaire_median,
            MIN(salaire_min) AS salaire_min_observe,
            MAX(salaire_max) AS salaire_max_observe
        FROM '{silver_offres}'
        WHERE salaire_connu = True
        GROUP BY profil_normalise, ville_std
        HAVING nb_offres >= 2
    """).df()
    df_salaires.to_parquet(gold_path / 'salaires_par_profil.parquet')

    # --- Table Gold 3 : Volume d'offres par ville et télétravail ---
    print("[GOLD] 3/5 - Calcul des volumes par ville...")
    df_villes = con.execute(f"""
        SELECT 
            ville_std AS ville,
            profil_normalise AS profil,
            COUNT(*) AS nb_offres,
            COUNT(*) FILTER (WHERE teletravail ILIKE '%oui%' OR teletravail ILIKE '%hybride%' OR teletravail ILIKE '%télétravail%') AS nb_offres_remote
        FROM '{silver_offres}'
        GROUP BY ville_std, profil_normalise
    """).df()
    df_villes.to_parquet(gold_path / 'offres_par_ville.parquet')

    # --- Table Gold 4 : Entreprises les plus recruteurs ---
    print("[GOLD] 4/5 - Analyse des entreprises...")
    df_entreprises = con.execute(f"""
        SELECT 
            entreprise,
            COUNT(*) AS nb_offres_publiees,
            COUNT(DISTINCT profil_normalise) AS diversité_profils,
            ROUND(AVG(salaire_median_mad), 0) AS salaire_moyen_propose
        FROM '{silver_offres}'
        GROUP BY entreprise
        ORDER BY nb_offres_publiees DESC
        LIMIT 50
    """).df()
    df_entreprises.to_parquet(gold_path / 'entreprises_recruteurs.parquet')

    # --- Table Gold 5 : Tendances mensuelles ---
    print("[GOLD] 5/5 - Calcul des tendances temporelles...")
    df_tendances = con.execute(f"""
        SELECT 
            annee,
            mois,
            profil_normalise AS profil,
            COUNT(*) AS nb_offres
        FROM '{silver_offres}'
        GROUP BY annee, mois, profil_normalise
        ORDER BY annee, mois, profil_normalise
    """).df()
    df_tendances.to_parquet(gold_path / 'tendances_mensuelles.parquet')

    con.close()
    print(f"✅ [GOLD] Les 5 tables Gold ont été créées dans : {gold_path}")

if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_LAKE_ROOT = BASE_DIR / "data_lake"
    construire_gold(DATA_LAKE_ROOT)