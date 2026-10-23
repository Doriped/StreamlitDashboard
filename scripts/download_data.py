import re
from pathlib import Path

import requests

# Adresse de l'API data.gouv.fr décrivant le jeu de données.
API_URL = (
    "https://www.data.gouv.fr/api/1/datasets/"
    "bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-"
    "annees-de-2005-a-2024/"
)

# Années à télécharger : ajouter des années dans cette liste pour en télécharger d'autres.
ANNEES = list(range(2005, 2025))  # de 2005 à 2024 (la borne de fin est exclue)

# Dossier de destination : <racine du projet>/data/raw
RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"

# Contours des départements pour la carte (data.gouv.fr « Contours administratifs », licence ODbL),
CONTOURS_URL = "https://etalab-datasets.geo.data.gouv.fr/contours-administratifs/2025/geojson/departements-1000m.geojson"
CONTOURS_DESTINATION = Path(__file__).resolve().parents[1] / "data" / "geo" / "departements.geojson"

# Les 4 tables de chaque année, reconnues par le début du titre du fichier.
TABLES = {
    "car": "caracteristiques",  
    "lieux": "lieux",
    "vehicules": "vehicules",
    "usagers": "usagers",
}


# Renvoie (table, année) à partir du titre d'un fichier, ou None s'il ne nous intéresse pas.
def identifier_fichier(titre):
    titre = titre.lower()
    if not titre.endswith(".csv") or "immatricul" in titre:
        return None
    annee = re.search(r"20\d{2}", titre)
    if annee is None:
        return None
    for debut, table in TABLES.items():
        if titre.startswith(debut):
            return table, int(annee.group())
    return None


# Interroge l'API et renvoie un dictionnaire {(table, année): url}
def lister_fichiers():
    reponse = requests.get(API_URL, timeout = 30)
    reponse.raise_for_status()  # arrête le script si la requête a échoué
    fichiers = {}
    for ressource in reponse.json()["resources"]:
        cle = identifier_fichier(ressource["title"])
        if cle is not None:
            fichiers[cle] = ressource["url"]
    return fichiers


# Télécharge le fichier situé à `url` et l'enregistre dans `destination`
def telecharger(url, destination):
    reponse = requests.get(url, timeout = 120)
    reponse.raise_for_status()
    destination.parent.mkdir(parents = True, exist_ok = True)
    destination.write_bytes(reponse.content)


def main():
    fichiers = lister_fichiers()

    for annee in ANNEES:
        for table in TABLES.values():
            url = fichiers[(table, annee)]
            destination = RAW_DIR / str(annee) / f"{table}.csv"
            if destination.exists():
                print("déjà présent :", annee, table)
            else:
                print("téléchargement :", annee, table)
                telecharger(url, destination)

    if CONTOURS_DESTINATION.exists():
        print("déjà présent : contours des départements")
    else:
        print("téléchargement : contours des départements")
        telecharger(CONTOURS_URL, CONTOURS_DESTINATION)

    print("Terminé.")


if __name__ == "__main__":
    main()
