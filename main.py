# main.py
from pathlib import Path
from pipeline.bronze_ingestion import ingerer_bronze
from pipeline.silver_transform import executer_pipeline_silver
from pipeline.silver_nlp import executer_nlp
from pipeline.gold_aggregation import construire_gold

BASE_DIR = Path(__file__).resolve().parent
DATA_LAKE_ROOT = BASE_DIR / "data_lake"
SOURCE_JSON = BASE_DIR / "offres_emploi_it_maroc.json"

if __name__ == "__main__":
    print("🚀 Lancement du Pipeline Mexora RH...")
    
    # 1. Bronze
    ingerer_bronze(str(SOURCE_JSON), DATA_LAKE_ROOT)
    
    # 2. Silver
    executer_pipeline_silver(DATA_LAKE_ROOT)
    executer_nlp(DATA_LAKE_ROOT)
    
    # 3. Gold
    construire_gold(DATA_LAKE_ROOT)
    
    print("✨ Pipeline terminé avec succès !")