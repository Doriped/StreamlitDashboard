# Routes de France : pourquoi la route ne tue pas moins depuis 10 ans

Dashboard Streamlit de *data storytelling* sur les accidents corporels de la circulation routière en France, de 2005 à 2024.

Après une forte baisse entre 2005 et 2013, la mortalité routière stagne autour de 3 200 tués par an en métropole. Le dashboard montre **où, quand et pour qui la route tue encore** : sur les routes de campagne, la nuit, et parmi les usagers vulnérables (cyclistes, seniors).

- **Application en ligne** : [routes-de-france.streamlit.app](https://routes-de-france.streamlit.app/)
- **Code source** : [github.com/Doriped/StreamlitDashboard](https://github.com/Doriped/StreamlitDashboard)
- **Vidéo de démonstration** : *(à compléter)*
- **Storyboard** : [STORYBOARD.md](STORYBOARD.md)
- **Auteur** : *(Prénom NOM, groupe)* — EFREI Paris, projet individuel de Data Visualization 2026

## Le projet en bref

| | |
|---|---|
| **Public visé** | Décideurs locaux : élus et services des conseils départementaux, préfectures, communes |
| **Question** | La mortalité routière stagne depuis 2013 : où, quand et pour qui la route tue-t-elle encore ? |
| **Message** | Le danger se concentre hors des villes (70 % des tués), la nuit (22 % des tués pour 12 % des accidents) et chez les usagers vulnérables (45 % des tués en 2024) |
| **Indicateurs** | Le nombre de **tués** (seul indicateur de gravité comparable sur 20 ans) et la **létalité** (tués pour 100 accidents) |

## Les données

| Données | Source | Licence |
|---|---|---|
| Accidents corporels 2005-2024 : 4 fichiers par an (caractéristiques, lieux, véhicules, usagers) | [Bases de données annuelles des accidents corporels de la circulation routière](https://www.data.gouv.fr/datasets/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2024) — ONISR / Ministère de l'Intérieur, data.gouv.fr | Licence Ouverte 2.0 |
| Contours des départements (pour la carte) | [Contours administratifs](https://www.data.gouv.fr/datasets/contours-administratifs) — data.gouv.fr, version simplifiée à 1 000 m | ODbL |

La documentation officielle des variables est fournie dans [docs/description-des-bases-de-donnees-annuelles.pdf](docs/description-des-bases-de-donnees-annuelles.pdf).

Les fichiers bruts (80 CSV, 440 Mo) ne sont pas inclus : ils sont téléchargés par un script. Les **tables propres** (`data/processed/`, 40 Mo) et les contours (`data/geo/`) sont inclus, pour que le dashboard démarre sans attendre.

## Installation et lancement

Prérequis : **Python 3.11** (testé avec Python 3.11.9 sous Windows).

```powershell
# 1. Créer l'environnement virtuel et installer les librairies (versions figées)
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt

# 2. Lancer le dashboard (il s'ouvre dans le navigateur, sur http://localhost:8501)
.venv\Scripts\python -m streamlit run app.py
```

Sous macOS ou Linux, remplacer `.venv\Scripts\python` par `.venv/bin/python`.

### Reconstruire les données depuis zéro (facultatif)

Les tables propres sont déjà fournies. Pour les reconstruire à partir des fichiers officiels :

```powershell
# Télécharge les 80 fichiers bruts et les contours (environ 1 min 30) ; les fichiers déjà présents ne sont pas retéléchargés
.venv\Scripts\python scripts\download_data.py

# Nettoie, assemble et contrôle les 20 années, puis écrit data/processed/ (environ 2 min)
.venv\Scripts\python scripts\build_dataset.py
```

## Structure du projet

```
app.py                      point d'entrée : filtres de la barre latérale, puis les 6 sections dans l'ordre de l'histoire
sections/
├── accroche.py             1. indicateurs clés et courbe des tués 2005-2024
├── ou.py                   2. en / hors agglomération, types de route, carte des départements
├── quand.py                3. carte de chaleur heure × jour, éclairage
├── qui.py                  4. petits multiples par mode de déplacement, classes d'âge
├── qualite.py              5. contrôles, corrections et limites des données
└── conclusions.py          6. constats clés et pistes d'action
utils/
├── io.py                   chargement des données (avec st.cache_data) et citation des sources
├── filtres.py              application des filtres
├── prep.py                 lecture et nettoyage des fichiers bruts, jointures
├── qualite.py              contrôles qualité de chaque année
└── viz.py                  fonctions de graphiques au style commun (couleurs, format des nombres)
scripts/
├── download_data.py        téléchargement des données (API data.gouv.fr, avec cache)
└── build_dataset.py        construction des tables propres
data/
├── raw/                    fichiers bruts téléchargés (non inclus)
├── processed/              tables propres : accidents.parquet, personnes.parquet, qualite.parquet
└── geo/                    contours des départements
docs/                       documentation officielle des variables (ONISR)
STORYBOARD.md               cadrage, public, déroulé de l'histoire
```

## Méthode

### Préparation des données

Les 80 fichiers sont lus, nettoyés et assemblés en **deux tables** de niveaux différents :

- **`accidents`** (1 286 097 lignes, une par accident) : date, heure, département, conditions, type de route, et le bilan humain (tués, blessés) ;
- **`personnes`** (2 887 353 lignes, une par personne impliquée) : gravité, âge, sexe, mode de déplacement, et le contexte de l'accident.

Deux tables sont nécessaires : un accident implique plusieurs personnes, et les mettre dans une seule table ferait compter plusieurs fois le même accident. Le bilan humain est donc **résumé par accident** (`pd.crosstab`) avant d'être joint à la table des accidents.

Les colonnes de codes sont traduites en libellés à l'aide de la documentation officielle, et les 40 catégories de véhicules sont regroupées en 8 modes de déplacement.

### Corrections apportées

- **Deux formats de fichiers** (2005-2018 et 2019-2024) : séparateur (`,`, tabulation ou `;`), encodage (Latin-1 ou UTF-8), année sans siècle, heure en nombre, codes départements sur 3 chiffres, coordonnées GPS multipliées par 100 000. Le séparateur et l'encodage sont détectés automatiquement.
- **Colonne renommée** en 2022 (`Accident_Id` au lieu de `Num_Acc`).
- **Zéros perdus dans les codes départements** en 2009 et en 2019 (`8` au lieu de `08`), qui faisaient changer des milliers d'accidents de département.
- **Coordonnées GPS impossibles** effacées (toutes celles de 2009), **vitesses autorisées aberrantes** remplacées par « inconnue », **lieux multiples** pour un même accident réduits au lieu principal, **véhicules en double** supprimés.
- **Ancien code « piéton en roller ou trottinette »** (jusqu'en 2017) rattaché aux piétons, comme le fait l'ONISR.

### Contrôles et validation

Pour chaque année : doublons, cohérence entre les tables (aucun usager ni véhicule rattaché à un accident inexistant) et valeurs manquantes. Les résultats sont enregistrés dans `qualite.parquet` et affichés dans la section 5 du dashboard.

**Validation externe** : pour 2024, nos données donnent exactement les chiffres du [bilan officiel de l'ONISR](https://www.onisr.securite-routiere.gouv.fr/etat-de-linsecurite-routiere/bilans-annuels-de-la-securite-routiere/bilan-2024-de-la-securite-routiere) : 3 193 tués en métropole, la répartition par mode de déplacement, 2 465 hommes et 728 femmes, 45 % d'usagers vulnérables.

### Performance et tests

- Les données sont chargées une seule fois grâce à `st.cache_data`, et stockées au format **Parquet** avec des colonnes de type `category` : 208 Mo en mémoire au lieu de 860 Mo, et un changement de filtre en 0,4 à 1,6 seconde.
- Les chiffres qui ne dépendent pas des filtres (contrôles qualité) sont calculés une fois, lors de la construction des données.
- Le dashboard a été testé automatiquement (`streamlit.testing`) sur **120 combinaisons de filtres** (départements, modes de déplacement, périodes), sans erreur.

## Limites

- **Pas de données d'exposition** : sans le trafic, les distances parcourues ou la population, on compare des nombres et des taux de gravité, pas un risque par kilomètre ou par habitant. Une hausse des cyclistes tués peut venir d'un nombre plus élevé de cyclistes.
- **Corrélation n'est pas causalité** : un accident de nuit ou sur une route limitée à 80 km/h est plus grave, mais ces données ne disent pas pourquoi.
- **Accidents non déclarés** : les forces de l'ordre ne sont pas toujours appelées pour les accidents légers ; le nombre de tués est fiable, le nombre d'accidents moins.
- **Ruptures de méthode** : blessés hospitalisés non comparables avant et après 2018 (avertissement de l'ONISR) ; catégorie « trottinette / EDP » et vitesse autorisée disponibles seulement depuis 2019 ; géolocalisation incomplète avant 2018 (et inexistante en 2009).
- **Âge à un an près** (seule l'année de naissance est connue) et **conducteurs en fuite** de sexe et d'âge inconnus depuis 2021 (environ 2 % des usagers).
- **Vie privée** : le dashboard n'affiche que des données agrégées. L'ONISR publie à part, sans lien possible avec les accidents, la marque et le modèle des véhicules.
