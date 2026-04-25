import pandas as pd
import re
import json
from pathlib import Path

def extraire_competences(df: pd.DataFrame, referentiel_path: Path) -> pd.DataFrame:
    """
    Scanne les descriptions et les compétences brutes pour extraire 
    les mots-clés IT basés sur le référentiel JSON.
    """
    # 1. Charger le référentiel
    with open(referentiel_path, 'r', encoding='utf-8') as f:
        referentiel = json.load(f)

    # 2. Transformer le référentiel en dictionnaire à plat : alias -> (nom_normalisé, famille)
    dict_competences = {}
    for famille, competences in referentiel['familles'].items():
        for nom_normalise, aliases in competences.items():
            for alias in aliases:
                dict_competences[alias.lower()] = {
                    'competence': nom_normalise,
                    'famille': famille
                }

    # Trier les alias par longueur décroissante (pour éviter que 'c' match avant 'c#')
    aliases_tries = sorted(dict_competences.keys(), key=len, reverse=True)

    resultats = []

    print("[SILVER NLP] Extraction des compétences en cours...")

    for _, offre in df.iterrows():
        # On fusionne le titre, les compétences brutes et la description pour tout scanner
        texte_complet = ' '.join(filter(None, [
            str(offre.get('titre_poste', '')),
            str(offre.get('competences_brut', '')),
            str(offre.get('description', ''))
        ])).lower()

        competences_trouvees = set()

        for alias in aliases_tries:
            # Recherche du mot exact avec des "word boundaries" (\b)
            # pour éviter que 'js' match dans le mot 'toujours'
            pattern = r'\b' + re.escape(alias) + r'\b'
            if re.search(pattern, texte_complet):
                info = dict_competences[alias]
                nom_c = info['competence']
                
                if nom_c not in competences_trouvees:
                    competences_trouvees.add(nom_c)
                    resultats.append({
                        'id_offre': offre['id_offre'],
                        'profil': offre['profil_normalise'],
                        'ville': offre['ville_std'],
                        'competence': nom_c,
                        'famille': info['famille'],
                        'date_pub': offre['date_publication']
                    })

        # Si aucune compétence n'est trouvée
        if not competences_trouvees:
            resultats.append({
                'id_offre': offre['id_offre'],
                'profil': offre['profil_normalise'],
                'ville': offre['ville_std'],
                'competence': 'non_détecté',
                'famille': 'inconnu',
                'date_pub': offre['date_publication']
            })

    df_comp = pd.DataFrame(resultats)
    return df_comp

def executer_nlp(data_lake_root: Path):
    # 1. Charger les données nettoyées à l'étape précédente
    silver_path = data_lake_root / 'silver' / 'offres_clean' / 'offres_clean.parquet'
    if not silver_path.exists():
        print("❌ Erreur : offres_clean.parquet introuvable. Lance silver_transform.py d'abord.")
        return

    df_offres = pd.read_parquet(silver_path)
    
    # 2. Charger le référentiel (situé à la racine du projet)
    ref_path = data_lake_root.parent / 'referentiel_competences_it.json'
    
    # 3. Extraire
    df_competences = extraire_competences(df_offres, ref_path)
    
    # 4. Sauvegarder
    output_dir = data_lake_root / 'silver' / 'competences_extraites'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / 'competences.parquet'
    df_competences.to_parquet(output_file, index=False)
    
    print(f"✅ [SILVER NLP] {len(df_competences)} lignes de compétences extraites.")
    print(f"✅ [SILVER NLP] Sauvegardé dans : {output_file}")

if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_LAKE_ROOT = BASE_DIR / "data_lake"
    executer_nlp(DATA_LAKE_ROOT)