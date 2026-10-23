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


# Lit les 3 tables propres. Grâce à @st.cache_data, les fichiers ne sont lus qu'une seule fois :
# les fois suivantes, Streamlit renvoie directement le résultat gardé en mémoire
@st.cache_data(show_spinner = "Chargement des données…")
def charger_donnees():
    accidents = pd.read_parquet(PROCESSED_DIR / "accidents.parquet")
    personnes = pd.read_parquet(PROCESSED_DIR / "personnes.parquet")
    qualite = pd.read_parquet(PROCESSED_DIR / "qualite.parquet")
    return accidents, personnes, qualite


# Lit les contours des départements (pour la carte) et renvoie aussi le nom de chaque département
@st.cache_data
def charger_departements():
    with open(CONTOURS, encoding = "utf-8") as fichier:
        contours = json.load(fichier)
    noms = {f["properties"]["code"]: f["properties"]["nom"] for f in contours["features"]}
    return contours, noms
