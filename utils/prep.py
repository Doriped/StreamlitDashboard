from pathlib import Path

import pandas as pd

# Dossier des fichiers bruts : <racine du projet>/data/raw
RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"

# Traduction des codes en libellés (documentation, pages 4 et 5).
AGGLOMERATION = {
    1: "Hors agglomération",
    2: "En agglomération",
}
LUMIERE = {
    1: "Plein jour",
    2: "Crépuscule ou aube",
    3: "Nuit sans éclairage",
    4: "Nuit, éclairage éteint",
    5: "Nuit avec éclairage",
}
METEO = {
    1: "Normale",
    2: "Pluie légère",
    3: "Pluie forte",
    4: "Neige ou grêle",
    5: "Brouillard ou fumée",
    6: "Vent fort ou tempête",
    7: "Temps éblouissant",
    8: "Temps couvert",
    9: "Autre",
}
TYPE_ROUTE = {
    1: "Autoroute",
    2: "Route nationale",
    3: "Route départementale",
    4: "Voie communale",
    5: "Hors réseau public",
    6: "Parking",
    7: "Route de métropole urbaine",
    9: "Autre",
}
ETAT_ROUTE = {
    1: "Normale",
    2: "Mouillée",
    3: "Flaques",
    4: "Inondée",
    5: "Enneigée",
    6: "Boue",
    7: "Verglacée",
    8: "Corps gras, huile",
    9: "Autre",
}
# Regroupement des catégories de véhicule (documentation, page 8).
# Les codes 4, 5, 6, 8, 9, 11, 12, 18 et 19 ne sont utilisés qu'avant 2006.
# Les codes 0 (indéterminable) et -1 (non renseigné) ne sont pas listés : ils deviennent des valeurs manquantes.
CATEGORIE_VEHICULE = {
    1: "Vélo",                    # bicyclette
    80: "Vélo",                   # vélo à assistance électrique
    50: "Trottinette / EDP",      # engin de déplacement personnel à moteur
    60: "Trottinette / EDP",      # engin de déplacement personnel sans moteur
    2: "Deux-roues motorisé",     # cyclomoteur < 50 cm3
    4: "Deux-roues motorisé",     # scooter immatriculé (avant 2006)
    5: "Deux-roues motorisé",     # motocyclette (avant 2006)
    6: "Deux-roues motorisé",     # side-car (avant 2006)
    30: "Deux-roues motorisé",    # scooter < 50 cm3
    31: "Deux-roues motorisé",    # moto 50 à 125 cm3
    32: "Deux-roues motorisé",    # scooter 50 à 125 cm3
    33: "Deux-roues motorisé",    # moto > 125 cm3
    34: "Deux-roues motorisé",    # scooter > 125 cm3
    41: "Deux-roues motorisé",    # 3 roues <= 50 cm3
    42: "Deux-roues motorisé",    # 3 roues 50 à 125 cm3
    43: "Deux-roues motorisé",    # 3 roues > 125 cm3
    3: "Voiture",                 # voiturette
    7: "Voiture",                 # véhicule léger
    8: "Voiture",                 # véhicule léger + caravane (avant 2006)
    9: "Voiture",                 # véhicule léger + remorque (avant 2006)
    10: "Utilitaire",             # véhicule utilitaire 1,5 à 3,5 t
    11: "Utilitaire",             # utilitaire + caravane (avant 2006)
    12: "Utilitaire",             # utilitaire + remorque (avant 2006)
    13: "Poids lourd",            # poids lourd 3,5 à 7,5 t
    14: "Poids lourd",            # poids lourd > 7,5 t
    15: "Poids lourd",            # poids lourd + remorque
    16: "Poids lourd",            # tracteur routier seul
    17: "Poids lourd",            # tracteur routier + semi-remorque
    18: "Bus, car, tram, train",  # transport en commun (avant 2006)
    19: "Bus, car, tram, train",  # tramway (avant 2006)
    37: "Bus, car, tram, train",  # autobus
    38: "Bus, car, tram, train",  # autocar
    39: "Bus, car, tram, train",  # train
    40: "Bus, car, tram, train",  # tramway
    20: "Autre",                  # engin spécial
    21: "Autre",                  # tracteur agricole
    35: "Autre",                  # quad léger
    36: "Autre",                  # quad lourd
    99: "Autre",                  # autre véhicule
}
GRAVITE = {
    1: "Indemne",
    2: "Tué",
    3: "Blessé hospitalisé",
    4: "Blessé léger",
}
CATEGORIE_USAGER = {
    1: "Conducteur",
    2: "Passager",
    3: "Piéton",
    4: "Piéton",  # piéton en roller ou en trottinette (code utilisé jusqu'en 2017)
}
SEXE = {
    1: "Homme",
    2: "Femme",
}
JOURS = {
    0: "Lundi",
    1: "Mardi",
    2: "Mercredi",
    3: "Jeudi",
    4: "Vendredi",
    5: "Samedi",
    6: "Dimanche",
}


# Lit un fichier brut, en détectant son séparateur et son encodage (ils changent selon les années)
def lire_table(annee, table):
    chemin = RAW_DIR / str(annee) / f"{table}.csv"

    # Séparateur : on regarde quel caractère sépare les noms de colonnes sur la première ligne
    with open(chemin, encoding = "latin-1") as fichier:
        premiere_ligne = fichier.readline()
    if ";" in premiere_ligne:
        sep = ";"
        decimal = ","  # depuis 2019, les nombres sont écrits avec une virgule
    elif "\t" in premiere_ligne:
        sep = "\t"     # tabulation (caractéristiques 2009)
        decimal = "."
    else:
        sep = ","      # 2005-2018
        decimal = "."

    # Encodage : UTF-8 depuis 2019, Latin-1 avant (les accents sont codés différemment)
    try:
        brut = pd.read_csv(chemin, sep = sep, decimal = decimal, encoding = "utf-8", low_memory = False)
    except UnicodeDecodeError:
        brut = pd.read_csv(chemin, sep = sep, decimal = decimal, encoding = "latin-1", low_memory = False)

    # En 2022, l'identifiant de l'accident s'appelle « Accident_Id » dans la table caractéristiques
    brut = brut.rename(columns = {"Accident_Id": "Num_Acc"})
    return brut


# Code département au format INSEE : « 59 », « 2A », « 971 »
def normaliser_departement(dep, annee):
    dep = dep.astype(str)
    if annee >= 2019:
        # En 2019, les zéros du début ont été perdus (« 8 » au lieu de « 08 » pour les Ardennes) : on les remet
        return dep.str.zfill(2)

    # Avant 2019 : 3 chiffres (« 590 » pour le Nord, « 201 » / « 202 » pour la Corse, « 971 » pour la Guadeloupe)
    # En 2009, les zéros du début ont été perdus (« 10 » au lieu de « 010 » pour l'Ain) : on les remet
    dep = dep.str.zfill(3)
    resultat = dep.str[:2]
    resultat.loc[dep.str.startswith("97")] = dep
    resultat.loc[dep == "201"] = "2A"
    resultat.loc[dep == "202"] = "2B"
    return resultat


# Une ligne par accident : quand, où, dans quelles conditions
def nettoyer_caracteristiques(brut, annee):
    propre = pd.DataFrame()
    propre["num_acc"] = brut["Num_Acc"]

    # Date : avant 2019, l'année est écrite sans le siècle (5 pour 2005), on utilise donc l'année du fichier
    propre["date"] = pd.to_datetime(pd.DataFrame({"year": annee, "month": brut["mois"], "day": brut["jour"]}))
    propre["annee"] = propre["date"].dt.year
    propre["jour_semaine"] = propre["date"].dt.dayofweek.map(JOURS)

    # Heure : « 07:40 » depuis 2019, le nombre 740 avant. On ramène tout à « 0740 » et on garde les 2 premiers chiffres
    hrmn = brut["hrmn"].astype(str).str.replace(":", "").str.zfill(4)
    propre["heure"] = hrmn.str[:2].astype(int)

    # Lieu : un code département à 3 caractères (971, 974…) désigne l'outre-mer
    propre["dep"] = normaliser_departement(brut["dep"], annee)
    propre["zone"] = "Métropole"
    propre.loc[propre["dep"].str.len() == 3, "zone"] = "Outre-mer"

    # GPS : en 2009, la longitude contient des « - » isolés, que to_numeric transforme en valeurs manquantes
    lat = pd.to_numeric(brut["lat"], errors = "coerce")
    lon = pd.to_numeric(brut["long"], errors = "coerce")
    if annee < 2019:
        # Avant 2019 : degrés multipliés par 100 000 (5051500 = 50,515°), et 0 veut dire « non renseigné »
        lat = lat.where(lat != 0) / 100000
        lon = lon.where(lon != 0) / 100000
    propre["lat"] = lat
    propre["lon"] = lon

    # Contrôle : un accident en métropole doit être situé dans le rectangle de la France métropolitaine,
    # sinon ses coordonnées sont fausses (en 2009, par exemple, elles le sont toutes) et on les efface
    dans_la_france = propre["lat"].between(41, 51.5) & propre["lon"].between(-5.5, 10)
    propre.loc[(propre["zone"] == "Métropole") & ~dans_la_france, ["lat", "lon"]] = None

    # Conditions : les codes inconnus (dont -1 « non renseigné ») deviennent des valeurs manquantes
    propre["agglomeration"] = brut["agg"].map(AGGLOMERATION)
    propre["lumiere"] = brut["lum"].map(LUMIERE)
    propre["meteo"] = brut["atm"].map(METEO)
    return propre


# Une ligne par accident : la route où il a eu lieu
def nettoyer_lieux(brut):
    # Un accident à un croisement a une ligne par route : on garde la première (le lieu principal)
    brut = brut.drop_duplicates(subset = "Num_Acc", keep = "first")

    propre = pd.DataFrame()
    propre["num_acc"] = brut["Num_Acc"]
    propre["type_route"] = brut["catr"].map(TYPE_ROUTE)
    propre["etat_route"] = brut["surf"].map(ETAT_ROUTE)

    # Vitesse maximale autorisée : hors de 10-130 km/h, c'est une erreur de saisie ou -1 (non renseigné)
    # La colonne n'existe que depuis 2019 : avant, la vitesse est inconnue (NaN = valeur manquante)
    if "vma" in brut.columns:
        propre["vma"] = brut["vma"].where(brut["vma"].between(10, 130))
    else:
        propre["vma"] = float("nan")
    return propre


# Une ligne par véhicule impliqué : sa catégorie
def nettoyer_vehicules(brut):
    # Un même identifiant (accident + lettre du véhicule) ne doit apparaître qu'une fois
    brut = brut.drop_duplicates(subset = ["Num_Acc", "num_veh"], keep = "first")

    propre = pd.DataFrame()
    propre["num_acc"] = brut["Num_Acc"]
    propre["num_veh"] = brut["num_veh"]
    propre["vehicule"] = brut["catv"].map(CATEGORIE_VEHICULE)
    return propre


# Une ligne par personne impliquée : qui, et dans quel état
def nettoyer_usagers(brut, annee):
    propre = pd.DataFrame()

    propre["num_acc"] = brut["Num_Acc"]
    propre["num_veh"] = brut["num_veh"]  
    propre["categorie_usager"] = brut["catu"].map(CATEGORIE_USAGER)
    propre["gravite"] = brut["grav"].map(GRAVITE)
    propre["sexe"] = brut["sexe"].map(SEXE)
    propre["age"] = annee - brut["an_nais"]
    return propre


# Ajoute à chaque usager son véhicule (pour un piéton : celui qui l'a heurté) et son mode de déplacement
def relier_usagers_vehicules(usagers, vehicules):
    resultat = usagers.merge(vehicules, on = ["num_acc", "num_veh"], how = "left")

    # Un piéton est rattaché au véhicule qui l'a heurté : son mode de déplacement est « Piéton »
    resultat["mode"] = resultat["vehicule"]
    resultat.loc[resultat["categorie_usager"] == "Piéton", "mode"] = "Piéton"
    return resultat


# Une ligne par accident : caractéristiques + route + bilan humain (nombre de tués, de blessés…)
def construire_accidents(caracteristiques, lieux, usagers):
    accidents = caracteristiques.merge(lieux, on = "num_acc", how = "left")

    # Bilan humain : on compte les usagers de chaque gravité, pour chaque accident
    bilan = pd.crosstab(usagers["num_acc"], usagers["gravite"])
    bilan = bilan.rename(columns = {
        "Tué": "tues",
        "Blessé hospitalisé": "blesses_hospitalises",
        "Blessé léger": "blesses_legers",
        "Indemne": "indemnes",
    })
    bilan = bilan.reset_index()  # num_acc redevient une colonne normale, pour pouvoir faire le merge

    accidents = accidents.merge(bilan, on = "num_acc", how = "left")
    return accidents


# Une ligne par personne : ajoute à chaque usager le contexte de son accident (pour filtrer dans le dashboard)
def construire_personnes(usagers_vehicules, accidents):
    contexte = accidents[["num_acc", "annee", "dep", "zone", "agglomeration", "type_route"]]
    return usagers_vehicules.merge(contexte, on = "num_acc", how = "left")


# Nettoie et assemble les 4 tables d'une année : renvoie la table des accidents et celle des personnes
def nettoyer_annee(annee):
    caracteristiques = nettoyer_caracteristiques(lire_table(annee, "caracteristiques"), annee)
    lieux = nettoyer_lieux(lire_table(annee, "lieux"))
    vehicules = nettoyer_vehicules(lire_table(annee, "vehicules"))
    usagers = nettoyer_usagers(lire_table(annee, "usagers"), annee)

    usagers_vehicules = relier_usagers_vehicules(usagers, vehicules)
    accidents = construire_accidents(caracteristiques, lieux, usagers_vehicules)
    personnes = construire_personnes(usagers_vehicules, accidents)
    return accidents, personnes
