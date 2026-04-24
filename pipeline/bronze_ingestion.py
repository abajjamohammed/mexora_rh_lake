import json
import os
from datetime import datetime
from pathlib import Path

def ingerer_bronze(filepath_source: str, data_lake_root: Path) -> dict:
    """
    Charge les données brutes dans data_lake/bronze/
    """
    if not os.path.exists(filepath_source):
        print(f"❌ Erreur : Le fichier {filepath_source} est introuvable.")
        return {}

    with open(filepath_source, 'r', encoding='utf-8') as f:
        data = json.load(f)

    offres = data.get('offres', [])
    stats = {'total': len(offres), 'par_source': {}}

    partitions = {}
    for offre in offres:
        source = offre.get('source', 'inconnu').lower().replace(' ', '_')
        date_pub = offre.get('date_publication', '')

        try:
            mois_partition = datetime.strptime(date_pub[:7], '%Y-%m').strftime('%Y_%m')
        except (ValueError, TypeError):
            mois_partition = 'date_inconnue'

        cle = f"{source}/{mois_partition}"
        if cle not in partitions:
            partitions[cle] = []
        partitions[cle].append(offre)

    # --- C'est ici qu'on cible le dossier data_lake/bronze ---
    for partition, offres_partition in partitions.items():
        chemin_dir = data_lake_root / 'bronze' / partition
        chemin_dir.mkdir(parents=True, exist_ok=True)

        chemin_fichier = chemin_dir / 'offres_raw.json'
        
        with open(chemin_fichier, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'source_fichier': filepath_source,
                    'date_ingestion': datetime.now().isoformat(),
                    'partition': partition,
                    'nb_offres': len(offres_partition)
                },
                'offres': offres_partition
            }, f, ensure_ascii=False, indent=2)

        source_nom = partition.split('/')[0]
        stats['par_source'][source_nom] = stats['par_source'].get(source_nom, 0) + len(offres_partition)

    print(f"✅ [BRONZE] {stats['total']} offres ingérées dans data_lake/bronze/")
    return stats

if __name__ == "__main__":
    # On définit les chemins
    BASE_DIR = Path(__file__).resolve().parent.parent
    SOURCE_JSON = BASE_DIR / "offres_emploi_it_maroc.json"
    
    # ON CIBLE LE DOSSIER data_lake
    DATA_LAKE_FOLDER = BASE_DIR / "data_lake" 

    ingerer_bronze(str(SOURCE_JSON), DATA_LAKE_FOLDER)