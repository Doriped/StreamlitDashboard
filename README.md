# Roads of France: why road deaths have not fallen in 10 years

A Streamlit data storytelling dashboard on road traffic injury accidents in France, 2005-2024.

After a sharp fall between 2005 and 2013, road deaths in metropolitan France have stalled at around 3,200 a year. The dashboard shows **where, when and among whom people still die on the roads**: on rural roads, at night, and among vulnerable road users (cyclists, older people).

- **Live app**: [routes-de-france.streamlit.app](https://routes-de-france.streamlit.app/)
- **Source code**: [github.com/Doriped/StreamlitDashboard](https://github.com/Doriped/StreamlitDashboard)
- **Demo video**: *(to be added)*
- **Storyboard**: [STORYBOARD.md](STORYBOARD.md)
- **Author**: *Anguille Dorian* — EFREI Paris, individual Data Visualization project 2026

## The project in brief

| | |
|---|---|
| **Audience** | Local decision-makers: elected officials and staff of departmental councils, prefectures, municipalities |
| **Question** | Road deaths have stalled since 2013: where, when and among whom do people still die on the roads? |
| **Message** | The danger is concentrated outside towns (70% of deaths), at night (22% of deaths for 12% of crashes) and among vulnerable road users (45% of deaths in 2024) |
| **Indicators** | The number of **deaths** (the only severity measure comparable over 20 years) and **lethality** (deaths per 100 crashes) |

## Data

| Data | Source | Licence |
|---|---|---|
| Injury accidents 2005-2024: 4 files per year (characteristics, locations, vehicles, users) | [Bases de données annuelles des accidents corporels de la circulation routière](https://www.data.gouv.fr/datasets/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2024) — ONISR / French Ministry of the Interior, data.gouv.fr | Licence Ouverte 2.0 |
| Department boundaries (for the map) | [Contours administratifs](https://www.data.gouv.fr/datasets/contours-administratifs) — data.gouv.fr, simplified to 1,000 m | ODbL |

The official variable documentation (in French) is in [docs/description-des-bases-de-donnees-annuelles.pdf](docs/description-des-bases-de-donnees-annuelles.pdf).

The raw files (80 CSV files, 440 MB) are not included: a script downloads them. The **clean tables** (`data/processed/`, 40 MB) and the boundaries (`data/geo/`) are included, so the dashboard starts right away.

## Install and run

Requires **Python 3.11** (tested with Python 3.11.9 on Windows).

```powershell
# 1. Create the virtual environment and install the pinned dependencies
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt

# 2. Run the dashboard (it opens in the browser at http://localhost:8501)
.venv\Scripts\python -m streamlit run app.py
```

On macOS or Linux, replace `.venv\Scripts\python` with `.venv/bin/python`.

### Rebuilding the data from scratch (optional)

The clean tables are already provided. To rebuild them from the official files:

```powershell
# Downloads the 80 raw files and the boundaries (about 1.5 min); files already present are skipped
.venv\Scripts\python scripts\download_data.py

# Cleans, joins and checks the 20 years, then writes data/processed/ (about 2 min)
.venv\Scripts\python scripts\build_dataset.py
```

## Project structure

```
app.py                      entry point: sidebar filters, then the 6 sections in story order
sections/
├── hook.py                 1. key figures and road deaths 2005-2024
├── where.py                2. inside / outside built-up areas, road types, department map
├── when.py                 3. hour × weekday heatmap, light conditions
├── who.py                  4. small multiples by travel mode, age groups
├── quality.py              5. data checks, fixes and limitations
└── conclusions.py          6. key findings and possible actions
utils/
├── io.py                   data loading (cached) and source citation
├── filters.py              sidebar filters
├── prep.py                 reading and cleaning the raw files, joins
├── quality.py              yearly quality checks
└── viz.py                  chart functions with a shared style
scripts/
├── download_data.py        data download (data.gouv.fr API, skips existing files)
└── build_dataset.py        builds the clean tables
data/
├── raw/                    downloaded raw files (not included)
├── processed/              clean tables: accidents.parquet, people.parquet, quality.parquet
└── geo/                    department boundaries
docs/                       official variable documentation (ONISR)
STORYBOARD.md               framing, audience, story outline
```

## Method

### Data preparation

The 80 files are read, cleaned and joined into **two tables** at different levels:

- **`accidents`** (1,286,097 rows, one per crash): date, hour, department, conditions, road type and casualty counts;
- **`people`** (2,887,353 rows, one per person involved): severity, age, sex, travel mode and the context of the crash.

Two tables are needed because a crash involves several people: a single table would count the same crash several times. Casualties are therefore **counted per crash** (`pd.crosstab`) before being joined to the accidents table.

Coded columns are turned into labels using the official documentation, and the 40 vehicle categories are grouped into 8 travel modes.

### Fixes

- **Two file formats** (2005-2018 and 2019-2024): separator (`,`, tab or `;`), encoding (Latin-1 or UTF-8), year without century, hour as a number, 3-digit department codes, GPS coordinates multiplied by 100,000. The separator and encoding are detected automatically.
- **Renamed column** in 2022 (`Accident_Id` instead of `Num_Acc`).
- **Lost leading zeros in department codes** in 2009 and 2019 (`8` instead of `08`), which moved thousands of crashes to the wrong department.
- **Impossible GPS coordinates** removed (all of them in 2009), **absurd speed limits** set to unknown, **several locations for one crash** reduced to the main one, **duplicate vehicles** removed.
- **Old "pedestrian on rollers or kick scooter" code** (until 2017) counted as pedestrians, as ONISR does.

### Checks and validation

For each year: duplicates, consistency between tables (no person or vehicle linked to a missing crash) and missing values. The results are saved in `quality.parquet` and shown in section 5 of the dashboard.

**External validation**: for 2024, our data gives exactly the figures of the [ONISR official report](https://www.onisr.securite-routiere.gouv.fr/etat-de-linsecurite-routiere/bilans-annuels-de-la-securite-routiere/bilan-2024-de-la-securite-routiere): 3,193 deaths in metropolitan France, the breakdown by travel mode, 2,465 men and 728 women, 45% vulnerable road users.

### Performance and tests

- Tables are stored as **Parquet** files with `category` columns (each repeated text value is stored once).
- The dashboard only loads **the columns it uses** and **metropolitan France**, once, with `st.cache_resource`: a single copy is shared by every visitor, whereas `st.cache_data` would return a new copy on each rerun. The small tables (quality checks, boundaries) use `st.cache_data`.
- Result: **under 600 MB of memory** at peak (against 1.6 GB in the first version, which exceeded the Streamlit Community Cloud limit), and 0.4 to 1.6 seconds per filter change.
- Figures that do not depend on the filters (quality checks) are computed once, when the data is built.
- The dashboard was tested automatically (`streamlit.testing`) on **120 filter combinations** (departments, travel modes, periods), with no errors and no empty values in the text.

## Limitations

- **No exposure data**: without traffic, distances travelled or population, the dashboard compares counts and severity rates, not a risk per kilometre or per inhabitant. A rise in cyclist deaths may come from more cyclists.
- **Correlation is not causation**: crashes at night or on 80 km/h roads are more severe, but this data does not say why.
- **Unreported crashes**: the police are not always called for minor crashes; death counts are reliable, crash counts less so.
- **Method breaks**: hospitalized casualties are not comparable before and after 2018 (ONISR warning); the e-scooter category and the speed limit only exist since 2019; geolocation is incomplete before 2018 (and missing in 2009).
- **Age accurate to one year** (only the year of birth is known), and **hit-and-run drivers** with unknown sex and age since 2021 (about 2% of people involved).
- **Privacy**: the dashboard only shows aggregated figures. ONISR publishes vehicle makes and models separately, with no possible link to the crashes.
