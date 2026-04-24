#!/usr/bin/env python3
"""
generate_data.py
Génère les fichiers de données pour le mini-projet Data Lake.
- offres_emploi_it_maroc.json : 5000 offres d'emploi IT au Maroc (brutes, avec incohérences intentionnelles)
- referentiel_competences_it.json : dictionnaire des compétences (identique à l'énoncé)
- entreprises_it_maroc.csv : liste d'entreprises IT marocaines
"""

import json
import random
import csv
from datetime import datetime, timedelta

# ---------- Configuration ----------
NB_OFFRES = 5000
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2024, 11, 30)

# ---------- Données pour génération aléatoire ----------
SOURCES = ["rekrute", "marocannonce", "linkedin"]

TITRES = [
    "Data Engineer", "Ingénieur Big Data", "Data Eng.", "Dev Data", "Data Engineer Junior",
    "Data Analyst", "Analyste Data", "BI Developer", "Data Analyst Junior",
    "Data Scientist", "Machine Learning Engineer", "Scientifique des données",
    "Développeur Full Stack", "Fullstack React/Node.js", "Dev Full Stack",
    "Développeur Backend", "Back-end Engineer", "Devops Engineer", "Cloud Architect",
    "Admin Systèmes", "Chef de Projet IT", "Scrum Master", "Architecte Logiciel"
]

ENTREPRISES = [
    "TechMaroc SARL", "Informatique Services", "DataSmart", "CloudMaroc", "Solutions IT",
    "Banque Populaire", "Attijariwafa", "CGI Maroc", "Capgemini", "IBM Maroc",
    "Oracle Maroc", "Microsoft Maroc", "Deloitte", "PwC", "KPMG", "Accenture",
    "Wafasalaf", "Maroc Telecom", "Inwi", "Orange Maroc", "HPS", "M2M Group"
]

VILLES_INCOHERENTES = [
    "Casablanca", "casa", "CASABLANCA", "Casa", "Rabat", "RABAT", "rabat",
    "Tanger", "tanger", "TANGER", "Marrakech", "MARRAKECH", "Fès", "FEZ", "Meknès"
]

CONTRATS = ["CDI", "cdi", "Contrat à durée indéterminée", "Permanent", "CDD", "Freelance", "Stage"]

EXPERIENCES = [
    "3-5 ans", "3 à 5 ans", "min 3 ans", "Débutant accepté", "5+ ans", "Senior (7+ ans)",
    "1-2 ans", "Moins de 1 an", "", None
]

ETUDES = ["Bac+5", "Bac+4", "Bac+3", "Bac+2", "Ingénieur", "Master", "Licence", None]
SECTEURS = ["Informatique / Télécom", "Banque / Finance", "Conseil", "Santé", "Industrie", "E-commerce", "Énergie", "Transport"]
TELETRAVAIL = ["Hybride", "Oui", "Non", "Partiel", "Télétravail complet", ""]
LANGUES = [["Français"], ["Anglais"], ["Français", "Anglais"], ["Anglais", "Arabe"], []]

COMPETENCES_LIST = [
    "Python", "SQL", "JavaScript", "Java", "C#", "Scala", "R", "React", "Angular", "Vue.js",
    "Node.js", "Django", "Spring Boot", "Spark", "Kafka", "Airflow", "Hadoop", "AWS", "Azure", "GCP",
    "Docker", "Kubernetes", "Terraform", "Git", "CI/CD", "Jenkins", "Power BI", "Tableau", "Looker",
    "Machine Learning", "Deep Learning", "NLP", "TensorFlow", "PyTorch", "Pandas", "NumPy", "Scikit-learn"
]

# Référentiel normalisé (identique à l'énoncé)
REFERENTIEL = {
    "familles": {
        "langages": {
            "python": ["python", "python3", "py"],
            "javascript": ["javascript", "js", "node.js", "nodejs", "node"],
            "java": ["java", "java8", "java11", "java17", "scala"],
            "csharp": ["c#", "csharp", ".net"],
            "sql": ["sql", "mysql", "postgresql", "postgres", "oracle", "tsql"],
            "r": ["r", "rlang", "r-studio"]
        },
        "frameworks_web": {
            "react": ["react", "reactjs", "react.js"],
            "angular": ["angular", "angularjs"],
            "django": ["django", "django rest"],
            "spring": ["spring", "spring boot", "springboot"],
            "vue": ["vue", "vue.js"]
        },
        "data_engineering": {
            "spark": ["spark", "apache spark", "pyspark"],
            "kafka": ["kafka", "apache kafka"],
            "airflow": ["airflow", "apache airflow"],
            "dbt": ["dbt", "data build tool"],
            "hadoop": ["hadoop", "hdfs", "mapreduce"]
        },
        "cloud": {
            "aws": ["aws", "amazon web services", "ec2", "s3", "lambda"],
            "gcp": ["gcp", "google cloud", "bigquery", "cloud storage"],
            "azure": ["azure", "microsoft azure", "synapse"]
        },
        "bi_analytics": {
            "power_bi": ["power bi", "powerbi", "pbi"],
            "tableau": ["tableau", "tableau desktop"],
            "metabase": ["metabase"],
            "looker": ["looker", "looker studio"]
        }
    }
}

# ---------- Utilitaires ----------
def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

def random_from_list(lst, allow_none=False, none_prob=0.05):
    if allow_none and random.random() < none_prob:
        return None
    return random.choice(lst)

def generer_salaire_brut():
    mode = random.choice(["fourchette_k", "fourchette_normale", "k", "null", "eur", "texte"])
    if mode == "fourchette_k":
        min_k = random.randint(8, 25)
        max_k = random.randint(min_k + 1, 35)
        return f"{min_k}K-{max_k}K MAD"
    elif mode == "fourchette_normale":
        min_mad = random.randint(8000, 25000)
        max_mad = random.randint(min_mad + 2000, 50000)
        return f"{min_mad}-{max_mad} MAD"
    elif mode == "k":
        val_k = random.randint(10, 45)
        return f"{val_k}K DH"
    elif mode == "eur":
        min_e = random.randint(2000, 5000)
        max_e = random.randint(min_e + 500, 8000)
        return f"{min_e}-{max_e} EUR"
    elif mode == "texte":
        return random.choice(["Selon profil", "Confidentiel", "", "Négociable", "À définir"])
    else:
        return None

def generer_competences_brut():
    nb_comp = random.randint(2, 8)
    comps = random.sample(COMPETENCES_LIST, nb_comp)
    separateur = random.choice([", ", " / ", " • ", "\n", "; "])
    return separateur.join(comps)

def generer_description(titre, competences_brut):
    """
    Génère une description réaliste.
    - Ajoute parfois des compétences qui ne sont PAS dans competences_brut
    - Force des mots-clés pour tester l'extraction depuis texte libre
    """
    phrases = [
        f"Nous recherchons un(e) {titre} dynamique pour rejoindre notre équipe.",
        "Vous serez en charge de développer et maintenir nos applications.",
        "Mission : participer aux projets stratégiques de l'entreprise.",
        "Environnement technique moderne et innovant.",
        "Travail en mode Agile (Scrum/Kanban)."
    ]
    # Extraire les compétences déjà présentes dans le champ brut (pour éviter de toutes les répéter)
    brut_comps = [c.strip() for c in competences_brut.replace("•", ",").replace("/", ",").replace("\n", ",").split(",") if c.strip()]
    
    # 1) Ajouter 1 à 3 compétences issues du brut (optionnel)
    if brut_comps and random.random() < 0.7:
        extra = f"Maîtrise de {', '.join(random.sample(brut_comps, min(2, len(brut_comps))))} requise."
        phrases.append(extra)
    
    # 2) Ajouter des compétences uniquement dans la description (pour tester l'extraction NLP)
    # On pioche dans COMPETENCES_LIST, mais on évite celles déjà dans brut_comps
    potential_new = [c for c in COMPETENCES_LIST if c.lower() not in [bc.lower() for bc in brut_comps]]
    if potential_new and random.random() < 0.4:  # 40% des offres auront une compétence cachée
        hidden_comp = random.choice(potential_new)
        phrases.append(f"Des connaissances en {hidden_comp} seraient un plus apprécié.")
    
    # 3) Optionnellement ajouter une compétence du référentiel sous forme d'alias différent (ex: "py" au lieu de "python")
    # pour tester la normalisation via le dictionnaire
    if random.random() < 0.3:
        # Prendre un alias depuis le référentiel
        all_aliases = []
        for famille in REFERENTIEL["familles"].values():
            for aliases in famille.values():
                all_aliases.extend(aliases)
        alias = random.choice(all_aliases)
        if alias.lower() not in ' '.join(phrases).lower():
            phrases.append(f"Environnement technique : {alias}.")
    
    random.shuffle(phrases)
    return " ".join(phrases[:random.randint(3, 6)])

def generer_offre(idx):
    source = random.choice(SOURCES)
    titre = random.choice(TITRES)
    if random.random() < 0.2:
        titre = f"{titre} {random.choice(['Junior', 'Senior', 'Lead'])}"
    
    competences_brut = generer_competences_brut()
    description = generer_description(titre, competences_brut)
    entreprise = random.choice(ENTREPRISES)
    ville = random.choice(VILLES_INCOHERENTES)
    type_contrat = random.choice(CONTRATS)
    experience_requise = random.choice(EXPERIENCES)
    salaire_brut = generer_salaire_brut()
    niveau_etudes = random_from_list(ETUDES, allow_none=True, none_prob=0.1)
    secteur = random.choice(SECTEURS)
    date_pub = random_date(START_DATE, END_DATE).strftime("%Y-%m-%d")
    
    # Gestion des dates incohérentes (5% des cas : expiration avant publication)
    if random.random() < 0.05:
        date_exp = (datetime.strptime(date_pub, "%Y-%m-%d") - timedelta(days=random.randint(1, 10))).strftime("%Y-%m-%d")
    else:
        date_exp = (datetime.strptime(date_pub, "%Y-%m-%d") + timedelta(days=random.randint(20, 45))).strftime("%Y-%m-%d")
    
    nb_postes = random.randint(1, 5)
    teletravail = random.choice(TELETRAVAIL)
    langue_requise = random.choice(LANGUES)
    
    return {
        "id_offre": f"{source.upper()[:2]}-{date_pub[:4]}-{idx:05d}",
        "source": source,
        "titre_poste": titre,
        "description": description,
        "competences_brut": competences_brut,
        "entreprise": entreprise,
        "ville": ville,
        "type_contrat": type_contrat,
        "experience_requise": experience_requise,
        "salaire_brut": salaire_brut,
        "niveau_etudes": niveau_etudes,
        "secteur": secteur,
        "date_publication": date_pub,
        "date_expiration": date_exp,
        "nb_postes": nb_postes,
        "teletravail": teletravail,
        "langue_requise": langue_requise
    }

def generer_json_offres():
    offres = [generer_offre(i) for i in range(1, NB_OFFRES + 1)]
    with open("offres_emploi_it_maroc.json", "w", encoding="utf-8") as f:
        json.dump({"offres": offres}, f, ensure_ascii=False, indent=2)
    print(f"✅ {NB_OFFRES} offres générées dans offres_emploi_it_maroc.json")

def generer_referentiel_competences():
    with open("referentiel_competences_it.json", "w", encoding="utf-8") as f:
        json.dump(REFERENTIEL, f, ensure_ascii=False, indent=2)
    print("✅ referentiel_competences_it.json créé")

def generer_csv_entreprises():
    entreprises_data = [
        {"nom_entreprise": "TechMaroc SARL", "secteur": "IT", "taille": "PME", "ville_siege": "Casablanca", "site_web": "techmaroc.ma", "type": "SSII"},
        {"nom_entreprise": "DataSmart", "secteur": "Data", "taille": "Startup", "ville_siege": "Tanger", "site_web": "datasmart.ma", "type": "Produit"},
        {"nom_entreprise": "CloudMaroc", "secteur": "Cloud", "taille": "ETI", "ville_siege": "Rabat", "site_web": "cloudmaroc.com", "type": "Conseil"},
        {"nom_entreprise": "Solutions IT", "secteur": "Services", "taille": "PME", "ville_siege": "Casablanca", "site_web": "solutionsit.ma", "type": "SSII"},
        {"nom_entreprise": "Banque Populaire", "secteur": "Banque", "taille": "Grande Entreprise", "ville_siege": "Casablanca", "site_web": "banquepopulaire.ma", "type": "Banque"},
        {"nom_entreprise": "Maroc Telecom", "secteur": "Telecom", "taille": "Grande Entreprise", "ville_siege": "Rabat", "site_web": "iam.ma", "type": "Telecom"},
        {"nom_entreprise": "Capgemini Maroc", "secteur": "Conseil", "taille": "Grande Entreprise", "ville_siege": "Casablanca", "site_web": "capgemini.com", "type": "Conseil"},
        {"nom_entreprise": "HPS", "secteur": "Fintech", "taille": "ETI", "ville_siege": "Casablanca", "site_web": "hps-worldwide.com", "type": "Produit"},
        {"nom_entreprise": "Inwi", "secteur": "Telecom", "taille": "Grande Entreprise", "ville_siege": "Casablanca", "site_web": "inwi.ma", "type": "Telecom"},
        {"nom_entreprise": "Attijariwafa bank", "secteur": "Banque", "taille": "Grande Entreprise", "ville_siege": "Casablanca", "site_web": "attijariwafa.com", "type": "Banque"},
    ]
    for i in range(10):
        entreprises_data.append({
            "nom_entreprise": f"Entreprise IT {i+1}",
            "secteur": random.choice(["IT", "Data", "Cloud", "Cybersecurite"]),
            "taille": random.choice(["Startup", "PME", "ETI", "Grande Entreprise"]),
            "ville_siege": random.choice(["Casablanca", "Rabat", "Tanger", "Marrakech"]),
            "site_web": f"entreprise{i+1}.ma",
            "type": random.choice(["SSII", "Produit", "Conseil", "Autre"])
        })
    with open("entreprises_it_maroc.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["nom_entreprise", "secteur", "taille", "ville_siege", "site_web", "type"])
        writer.writeheader()
        writer.writerows(entreprises_data)
    print(f"✅ {len(entreprises_data)} entreprises générées dans entreprises_it_maroc.csv")

if __name__ == "__main__":
    generer_json_offres()
    generer_referentiel_competences()
    generer_csv_entreprises()
    print("\n✅ Tous les fichiers ont été générés avec succès.")