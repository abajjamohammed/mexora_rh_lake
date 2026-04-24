import pandas as pd
import re
import json
from pathlib import Path

def charger_depuis_bronze(data_lake_root: Path) -> pd.DataFrame:
    """Charge et consolide toutes les offres depuis la zone Bronze."""
    all_offres = []
    bronze_path = data_lake_root / 'bronze'

    # On cherche tous les fichiers offres_raw.json dans les sous-dossiers
    for json_file in bronze_path.rglob('offres_raw.json'):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        all_offres.extend(data.get('offres', []))

    df = pd.DataFrame(all_offres)
    print(f"✅ [SILVER] {len(df)} offres chargées depuis Bronze")
    return df

def nettoyer_villes(df: pd.DataFrame) -> pd.DataFrame:
    """Standardise les noms de villes (ex: casa -> Casablanca)"""
    mapping_villes = {
        'casa': 'Casablanca', 'casablanca': 'Casablanca', 'casablanca ': 'Casablanca',
        'rabat': 'Rabat', 'tanger': 'Tanger', 'marrakech': 'Marrakech',
        'fez': 'Fès', 'fes': 'Fès', 'meknes': 'Meknès'
    }
    df['ville_std'] = df['ville'].str.lower().str.strip().replace(mapping_villes)
    return df

def nettoyer_titres_postes(df: pd.DataFrame) -> pd.DataFrame:
    """Standardise les intitulés de poste en familles de profils IT."""
    mapping_profils = {
        r'data\s*eng': 'Data Engineer',
        r'analyste?\s*data|data\s*anal': 'Data Analyst',
        r'data\s*sci': 'Data Scientist',
        r'full\s*stack|fullstack': 'Développeur Full Stack',
        r'devops': 'DevOps',
        r'backend': 'Développeur Backend',
        r'architect': 'Architecte IT'
    }
    df['profil_normalise'] = 'Autre IT'
    for pattern, profil in mapping_profils.items():
        masque = df['titre_poste'].str.contains(pattern, regex=True, case=False, na=False)
        df.loc[masque, 'profil_normalise'] = profil
    return df

def normaliser_salaires(df: pd.DataFrame) -> pd.DataFrame:
    """Extrait les salaires et convertit les EUR en MAD."""
    TAUX_EUR_MAD = 10.8

    def parser_salaire(valeur):
        if pd.isna(valeur) or str(valeur).lower() in ['null', 'confidentiel', 'selon profil', '']:
            return None, None, False
        
        s = str(valeur).lower().replace(' ', '')
        est_eur = 'eur' in s or '€' in s
        s = re.sub(r'eur|€|mad|dh', '', s)
        
        # Gestion des "K" (ex: 15K -> 15000)
        s = re.sub(r'(\d+)k', lambda m: str(int(m.group(1)) * 1000), s)
        
        nombres = re.findall(r'\d+', s)
        if not nombres: return None, None, False
        
        montants = [float(n) for n in nombres]
        if est_eur: montants = [m * TAUX_EUR_MAD for m in montants]
        
        sal_min = min(montants)
        sal_max = max(montants)
        return sal_min, sal_max, True

    res = df['salaire_brut'].apply(lambda x: pd.Series(parser_salaire(x)))
    df[['salaire_min', 'salaire_max', 'salaire_connu']] = res
    df['salaire_median_mad'] = (df['salaire_min'] + df['salaire_max']) / 2
    return df

def executer_pipeline_silver(data_lake_root: Path):
    # 1. Chargement
    df = charger_depuis_bronze(data_lake_root)
    
    # 2. Nettoyage
    df = nettoyer_villes(df)
    df = nettoyer_titres_postes(df)
    df = normaliser_salaires(df)
    
    # 3. Extraction de l'année et du mois pour le partitionnement Silver
    df['annee'] = df['date_publication'].str[:4]
    df['mois'] = df['date_publication'].str[5:7]

    # 4. Sauvegarde en Parquet
    silver_path = data_lake_root / 'silver' / 'offres_clean'
    silver_path.mkdir(parents=True, exist_ok=True)
    
    file_path = silver_path / 'offres_clean.parquet'
    df.to_parquet(file_path, index=False, compression='snappy')
    
    print(f"✅ [SILVER] Fichier Parquet sauvegardé : {file_path}")

if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_LAKE_ROOT = BASE_DIR / "data_lake"
    executer_pipeline_silver(DATA_LAKE_ROOT)