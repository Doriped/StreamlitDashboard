TOUTE_LA_FRANCE = "France métropolitaine"
TOUS_LES_MODES = "Tous les modes"


# Applique les filtres de la barre latérale aux deux tables
def filtrer(accidents, personnes, periode, departement, mode):
    debut, fin = periode
    accidents = accidents[accidents["annee"].between(debut, fin)]
    personnes = personnes[personnes["annee"].between(debut, fin)]

    # Territoire : toute la métropole, ou un seul département
    if departement == TOUTE_LA_FRANCE:
        accidents = accidents[accidents["zone"] == "Métropole"]
        personnes = personnes[personnes["zone"] == "Métropole"]
    else:
        accidents = accidents[accidents["dep"] == departement]
        personnes = personnes[personnes["dep"] == departement]

    # Mode de déplacement : on garde les personnes de ce mode, et les accidents où il y en a au moins une
    if mode != TOUS_LES_MODES:
        personnes = personnes[personnes["mode"] == mode]
        accidents = accidents[accidents["num_acc"].isin(personnes["num_acc"])]

    return accidents, personnes
