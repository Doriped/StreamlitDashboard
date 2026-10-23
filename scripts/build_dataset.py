import sys
from pathlib import Path

import pandas as pd

# Permet d'importer le dossier utils/ quand on lance ce script depuis le dossier scripts/
RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
from utils.prep import nettoyer_annee
from utils.qualite import controler_annee

# Années à nettoyer : elles doivent avoir été téléchargées avec download_data.py.
ANNEES = list(range(2005, 2025))  # de 2005 à 2024 (la borne de fin est exclue)

# Dossier des tables propres : <racine du projet>/data/processed
PROCESSED_DIR = RACINE / "data" / "processed"


def main():
    liste_accidents = []
    liste_personnes = []
    liste_controles = []

    for annee in ANNEES:
        print("nettoyage :", annee)
        accidents, personnes = nettoyer_annee(annee)
        liste_accidents.append(accidents)
        liste_personnes.append(personnes)
        liste_controles.append(controler_annee(annee, accidents, personnes))

    # On empile les années les unes sous les autres dans une seule table
    accidents = pd.concat(liste_accidents, ignore_index = True)
    personnes = pd.concat(liste_personnes, ignore_index = True)
    qualite = pd.DataFrame(liste_controles)  # une ligne par année

    # Les colonnes de texte n'ont que quelques valeurs différentes (4 gravités, 9 modes, 96 départements…) :
    # le type « category » les stocke une seule fois et remplace chaque case par un petit numéro.
    # Le dashboard filtre alors beaucoup plus vite, et prend beaucoup moins de mémoire.
    for table in [accidents, personnes]:
        for colonne in table.select_dtypes(include = "str").columns:
            table[colonne] = table[colonne].astype("category")

    PROCESSED_DIR.mkdir(parents = True, exist_ok = True)
    accidents.to_parquet(PROCESSED_DIR / "accidents.parquet", index = False)
    personnes.to_parquet(PROCESSED_DIR / "personnes.parquet", index = False)
    qualite.to_parquet(PROCESSED_DIR / "qualite.parquet", index = False)

    print("accidents :", len(accidents), "lignes")
    print("personnes :", len(personnes), "lignes")
    print("Terminé.")


if __name__ == "__main__":
    main()
