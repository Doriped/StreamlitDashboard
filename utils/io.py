import json
from pathlib import Path

import pandas as pd
import streamlit as st

PROCESSED_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"
GEOJSON_PATH = Path(__file__).resolve().parents[1] / "data" / "geo" / "departments.geojson"

SOURCE = (
    "Source: annual databases of road traffic injury accidents 2005-2024 "
    "(Bases de données annuelles des accidents corporels de la circulation routière) · "
    "ONISR / French Ministry of the Interior · data.gouv.fr · Licence Ouverte 2.0. "
    "Department boundaries: data.gouv.fr \"Contours administratifs\" · ODbL"
)

# Only the columns used by the dashboard are loaded
ACCIDENT_COLUMNS = ["accident_id", "year", "weekday", "hour", "dep", "zone", "area", "light", "road_type"]
PEOPLE_COLUMNS = ["accident_id", "year", "dep", "zone", "area", "road_type", "severity", "mode", "sex", "age"]

# The dashboard only covers metropolitan France
METRO_ONLY = [("zone", "==", "Metropolitan France")]


# cache_resource keeps a single shared copy; cache_data would return a new copy on every rerun,
# which is too much memory for tables this size. The dashboard never modifies them.
@st.cache_resource(show_spinner = "Loading data…")
def load_data():
    accidents = pd.read_parquet(PROCESSED_DIR / "accidents.parquet", columns = ACCIDENT_COLUMNS, filters = METRO_ONLY)
    people = pd.read_parquet(PROCESSED_DIR / "people.parquet", columns = PEOPLE_COLUMNS, filters = METRO_ONLY)
    return accidents, people


@st.cache_data
def load_checks():
    return pd.read_parquet(PROCESSED_DIR / "quality.parquet")


# Returns the GeoJSON boundaries and a {code: name} dictionary
@st.cache_data
def load_departments():
    with open(GEOJSON_PATH, encoding = "utf-8") as file:
        geojson = json.load(file)
    names = {f["properties"]["code"]: f["properties"]["nom"] for f in geojson["features"]}
    return geojson, names
