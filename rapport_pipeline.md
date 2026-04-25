# Rapport de Traitement — Pipeline Mexora RH Intelligence

Ce document détaille les transformations effectuées sur les données au sein du Data Lake.

## 1. Ingestion Bronze (Raw Layer)
- **Objectif :** Archiver les données brutes sans aucune modification.
- **Règle de partitionnement :** Les données sont découpées par `source` (LinkedIn, Rekrute, etc.) puis par `année_mois`.
- **Volume traité :** 5000 offres d'emploi.
- **Cas limites gérés :** 
    - Les offres sans date de publication ont été placées dans un dossier `date_inconnue` pour éviter de bloquer le pipeline.
    - Utilisation du format JSON pour préserver la structure flexible originale.

## 2. Transformation Silver (Cleaned Layer)

### A. Normalisation des données
Le script `silver_transform.py` a appliqué les règles suivantes :
- **Villes :** Utilisation d'un mapping (dictionnaire) pour regrouper les variantes (ex: "casa" -> "Casablanca", "FEZ" -> "Fès").
- **Salaires :** 
    - Extraction des montants via Expressions Régulières (Regex).
    - Conversion des salaires en Euros vers MAD (Taux fixe : 10.8).
    - Calcul de la médiane pour les fourchettes (ex: "10K-15K" -> 12500 MAD).
- **Profils :** Regroupement de plus de 20 intitulés de postes différents en 7 familles clés (Data Engineer, Data Analyst, etc.).

### B. Extraction des compétences (NLP)
Le script `silver_nlp.py` a scanné le texte libre des descriptions :
- **Technique :** Recherche par mots-clés avec frontières de mots (`\b`) pour éviter les faux positifs.
- **Référentiel :** Utilisation du dictionnaire de 300 compétences IT fourni.
- **Résultat :** Passage d'un format "une ligne par offre" à un format "une ligne par compétence par offre", permettant des analyses granulaires.

## 3. Agrégation Gold (Curated Layer)
Utilisation de **DuckDB** pour générer 5 tables analytiques optimisées au format Parquet.
- **Règle métier :** Les statistiques de salaires ne sont calculées que pour les profils ayant au moins 2 offres pour garantir un minimum de pertinence statistique.

## 4. Statistiques et Qualité
- **Lignes avant (Bronze) :** 5 000 offres.
- **Lignes après (Silver Clean) :** 5 000 offres enrichies.
- **Lignes après (Silver NLP) :** ~25 000 lignes (selon le nombre de compétences détectées).
- **Taux de détection :** Environ 95% des offres ont au moins une compétence technique identifiée.

## 5. Cas limites et erreurs rencontrées
- **Erreur de moteur Parquet :** Nécessité d'installer `pyarrow` pour supporter l'écriture compressée Snappy.
- **Dates incohérentes :** Certaines offres (5%) présentaient une date d'expiration antérieure à la date de publication ; elles ont été conservées mais marquées pour analyse.
- **Salaires "Confidentiels" :** Ces lignes ont été ignorées dans les calculs de moyennes mais conservées pour les calculs de volumes.