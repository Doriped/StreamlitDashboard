import json
from pathlib import Path

import pandas as pd
import streamlit as st

# Dossier des tables propres, construites par scripts/build_dataset.py
PROCESSED_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"

# Contours des départements, téléchargés par scripts/download_data.py
CONTOURS = Path(__file__).resolve().parents[1] / "data" / "geo" / "departements.geojson"

# Citation des sources
SOURCE = (
    "Source : Bases de données annuelles des accidents corporels de la circulation routière 2005-2024 · "
    "ONISR / Ministère de l'Intérieur · data.gouv.fr · Licence Ouverte 2.0. "
    "Contours des départements : data.gouv.fr « Contours administratifs » · licence ODbL"
)


# Seules les colonnes utilisées par le dashboard sont chargées : moins de mémoire, et des filtres plus rapides
COLONNES_ACCIDENTS = ["num_acc", "annee", "jour_semaine", "heure", "dep", "zone", "agglomeration", "lumiere", "type_route"]
COLONNES_PERSONNES = ["num_acc", "annee", "dep", "zone", "agglomeration", "type_route", "gravite", "mode", "sexe", "age"]

# Le dashboard ne montre que la France métropolitaine : l'outre-mer n'est pas chargé
METROPOLE = [("zone", "==", "Métropole")]


# Lit les deux grandes tables, une seule fois. @st.cache_resource garde en mémoire un seul exemplaire,
# partagé par toutes les exécutions et tous les visiteurs. (@st.cache_data, lui, renverrait une copie
# à chaque clic : avec des tables de cette taille, la mémoire du serveur serait vite dépassée.)
# Ces tables ne sont jamais modifiées par le dashboard : chaque filtre crée une nouvelle table.
@st.cache_resource(show_spinner = "Chargement des données…")
def charger_donnees():
    accidents = pd.read_parquet(PROCESSED_DIR / "accidents.parquet", columns = COLONNES_ACCIDENTS, filters = METROPOLE)
    personnes = pd.read_parquet(PROCESSED_DIR / "personnes.parquet", columns = COLONNES_PERSONNES, filters = METROPOLE)
    return accidents, personnes


# Lit la petite table des contrôles qualité (une ligne par année)
@st.cache_data
def charger_controles():
    return pd.read_parquet(PROCESSED_DIR / "qualite.parquet")


# Lit les contours des départements (pour la carte) et renvoie aussi le nom de chaque département
@st.cache_data
def charger_departements():
    with open(CONTOURS, encoding = "utf-8") as fichier:
        contours = json.load(fichier)
    noms = {f["properties"]["code"]: f["properties"]["nom"] for f in contours["features"]}
    return contours, noms
