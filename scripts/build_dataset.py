import sys
from pathlib import Path

import pandas as pd

# Lets this script import utils/ when run from the scripts/ folder
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from utils.prep import clean_year
from utils.quality import check_year

YEARS = list(range(2005, 2025))  # must have been downloaded with download_data.py

PROCESSED_DIR = ROOT / "data" / "processed"


def main():
    all_accidents, all_people, all_checks = [], [], []

    for year in YEARS:
        print("cleaning:", year)
        accidents, people = clean_year(year)
        all_accidents.append(accidents)
        all_people.append(people)
        all_checks.append(check_year(year, accidents, people))

    accidents = pd.concat(all_accidents, ignore_index = True)
    people = pd.concat(all_people, ignore_index = True)
    checks = pd.DataFrame(all_checks)

    # Text columns have few distinct values: the category type uses much less memory and filters faster
    for table in [accidents, people]:
        for column in table.select_dtypes(include = "str").columns:
            table[column] = table[column].astype("category")

    PROCESSED_DIR.mkdir(parents = True, exist_ok = True)
    accidents.to_parquet(PROCESSED_DIR / "accidents.parquet", index = False)
    people.to_parquet(PROCESSED_DIR / "people.parquet", index = False)
    checks.to_parquet(PROCESSED_DIR / "quality.parquet", index = False)

    print("accidents:", len(accidents), "rows")
    print("people:", len(people), "rows")
    print("Done.")


if __name__ == "__main__":
    main()
