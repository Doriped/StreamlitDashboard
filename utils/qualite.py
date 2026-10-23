from utils.prep import lire_table


# Contrôles qualité d'une année : doublons, cohérence entre les tables, valeurs manquantes.
# Les doublons se mesurent sur les fichiers bruts, car le nettoyage les fait disparaître.
def controler_annee(annee, accidents, personnes):
    caracteristiques = lire_table(annee, "caracteristiques")
    lieux = lire_table(annee, "lieux")
    vehicules = lire_table(annee, "vehicules")
    usagers = lire_table(annee, "usagers")
    metropole = accidents[accidents["zone"] == "Métropole"]

    controles = {"annee": annee}

    # Doublons
    controles["accidents_en_double"] = caracteristiques["Num_Acc"].duplicated().sum()
    controles["lieux_multiples"] = lieux["Num_Acc"].duplicated().sum()
    controles["vehicules_en_double"] = vehicules.duplicated(subset = ["Num_Acc", "num_veh"]).sum()

    # Cohérence entre les tables : chaque usager et chaque véhicule doit appartenir à un accident existant
    controles["usagers_sans_accident"] = (~usagers["Num_Acc"].isin(caracteristiques["Num_Acc"])).sum()
    controles["vehicules_sans_accident"] = (~vehicules["Num_Acc"].isin(caracteristiques["Num_Acc"])).sum()

    # Valeurs manquantes, en % (le GPS n'est contrôlé que pour la métropole)
    controles["gps_manquant_pct"] = metropole["lat"].isna().mean() * 100
    controles["vma_manquante_pct"] = accidents["vma"].isna().mean() * 100
    controles["vehicule_inconnu_pct"] = personnes["vehicule"].isna().mean() * 100
    controles["sexe_inconnu_pct"] = personnes["sexe"].isna().mean() * 100
    controles["age_inconnu_pct"] = personnes["age"].isna().mean() * 100

    # Validation : chiffres à comparer avec les bilans officiels de l'ONISR
    controles["accidents"] = len(accidents)
    controles["tues_metropole"] = metropole["tues"].sum()

    # Blessés de métropole, pour montrer la rupture de méthode de 2018 (calculés ici une fois pour toutes,
    # plutôt qu'à chaque clic dans le dashboard)
    controles["blesses_hospitalises_metropole"] = metropole["blesses_hospitalises"].sum()
    controles["blesses_legers_metropole"] = metropole["blesses_legers"].sum()
    return controles
