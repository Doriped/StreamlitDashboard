import re
from pathlib import Path

import requests

# data.gouv.fr API page of the dataset
API_URL = (
    "https://www.data.gouv.fr/api/1/datasets/"
    "bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-"
    "annees-de-2005-a-2024/"
)

YEARS = list(range(2005, 2025))  # 2005 to 2024

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"

# Department boundaries for the map (data.gouv.fr "Contours administratifs", ODbL), simplified to 1,000 m
GEOJSON_URL = "https://etalab-datasets.geo.data.gouv.fr/contours-administratifs/2025/geojson/departements-1000m.geojson"
GEOJSON_PATH = Path(__file__).resolve().parents[1] / "data" / "geo" / "departments.geojson"

# The 4 yearly tables, recognised by the start of the (French) file title.
# File names are inconsistent across years: caracteristiques_2005, carcteristiques-2021, Caract_2024...
TABLES = {
    "car": "characteristics",
    "lieux": "locations",
    "vehicules": "vehicles",
    "usagers": "users",
}


# Returns (table, year) for a file title, or None if the file is not needed
def identify_file(title):
    title = title.lower()
    if not title.endswith(".csv") or "immatricul" in title:
        return None
    year = re.search(r"20\d{2}", title)
    if year is None:
        return None
    for prefix, table in TABLES.items():
        if title.startswith(prefix):
            return table, int(year.group())
    return None


# Returns {(table, year): url} for every file of the dataset
def list_files():
    response = requests.get(API_URL, timeout = 30)
    response.raise_for_status()
    files = {}
    for resource in response.json()["resources"]:
        key = identify_file(resource["title"])
        if key is not None:
            files[key] = resource["url"]
    return files


def download(url, destination):
    response = requests.get(url, timeout = 120)
    response.raise_for_status()
    destination.parent.mkdir(parents = True, exist_ok = True)
    destination.write_bytes(response.content)


def main():
    files = list_files()

    for year in YEARS:
        for table in TABLES.values():
            destination = RAW_DIR / str(year) / f"{table}.csv"
            if destination.exists():
                print("already there:", year, table)
            else:
                print("downloading:", year, table)
                download(files[(table, year)], destination)

    if GEOJSON_PATH.exists():
        print("already there: department boundaries")
    else:
        print("downloading: department boundaries")
        download(GEOJSON_URL, GEOJSON_PATH)

    print("Done.")


if __name__ == "__main__":
    main()
