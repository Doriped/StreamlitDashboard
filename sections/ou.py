import pandas as pd
import streamlit as st

from utils.filtres import TOUTE_LA_FRANCE
from utils.viz import barres_parts, carte_departements, nombre

# Types de route trop rares pour être lisibles séparément : regroupés dans « Autres »
PETITS_TYPES_DE_ROUTE = {"Parking": "Autres", "Hors réseau public": "Autres", "Autre": "Autres"}

INDICATEURS_CARTE = {
    "Tués pour 100 accidents": "letalite",
    "Nombre de tués": "tues",
}


def afficher(accidents, personnes, accidents_france, personnes_france, departement, contours, noms):
    st.header("2. Où ? Un tiers des accidents, deux tiers des morts")
    if len(accidents) == 0:
        st.warning("Aucun accident ne correspond aux filtres choisis.")
        return
    tues = personnes[personnes["gravite"] == "Tué"]

    # En ou hors agglomération, et par type de route
    agglomeration = parts(accidents, tues, "agglomeration")
    routes = parts(
        accidents.assign(type_route = regrouper_routes(accidents["type_route"])),
        tues.assign(type_route = regrouper_routes(tues["type_route"])),
        "type_route",
    )

    if "Hors agglomération" in agglomeration.index and "En agglomération" in agglomeration.index:
        hors = agglomeration.loc["Hors agglomération"]
        ville = agglomeration.loc["En agglomération"]
        phrase = (
            f"Hors agglomération : **{nombre(hors['part_accidents'])} % des accidents, "
            f"mais {nombre(hors['part_tues'])} % des tués**."
        )
        # Le rapport n'a de sens que s'il y a eu au moins un tué en ville (sinon : division par zéro)
        if ville["letalite"] > 0:
            phrase += (
                f" Un accident y fait en moyenne **{nombre(hors['letalite'] / ville['letalite'], 1)} fois plus de morts** qu'en ville."
            )
        st.markdown(phrase)

    colonne1, colonne2 = st.columns(2)
    with colonne1:
        st.subheader("En ou hors agglomération")
        st.plotly_chart(barres_parts(agglomeration, hauteur = 260), width = "stretch")
    with colonne2:
        st.subheader("Par type de route")
        st.plotly_chart(barres_parts(routes, hauteur = 400), width = "stretch")
    st.caption(
        "Graphiques : pour chaque catégorie, part des accidents (bleu) et part des tués (orange). "
        "Quand la barre orange dépasse la bleue, les accidents y sont plus meurtriers que la moyenne."
    )

    # Carte : tous les départements, pour situer celui qui est sélectionné
    st.subheader("Carte des départements")
    choix = st.radio("Colorer la carte selon :", list(INDICATEURS_CARTE), horizontal = True)
    colonne = INDICATEURS_CARTE[choix]

    tues_france = personnes_france[personnes_france["gravite"] == "Tué"]
    par_departement = parts(accidents_france, tues_france, "dep")
    par_departement["nom"] = par_departement.index.map(noms)

    st.plotly_chart(
        carte_departements(par_departement, colonne, choix, contours, departement),
        width = "stretch",
    )

    # Phrase de conclusion sous la carte. On ne compare que les départements avec assez d'accidents et au moins
    # un tué : avec 3 accidents, 1 tué donnerait « 33 tués pour 100 accidents », un chiffre sans valeur
    classement = par_departement.sort_values("letalite", ascending = False)
    comparables = classement[(classement["accidents"] >= 50) & (classement["tues"] > 0)]
    phrase = ""
    if len(comparables) >= 2:
        plus, moins = comparables.iloc[0], comparables.iloc[-1]
        phrase = (
            f"Un accident est **{nombre(plus['letalite'] / moins['letalite'])} fois plus meurtrier** "
            f"dans le département le plus touché, **{plus['nom']}** ({nombre(plus['letalite'], 1)} tués pour 100 accidents), "
            f"que dans le moins touché, **{moins['nom']}** ({nombre(moins['letalite'], 1)})."
        )
    if departement != TOUTE_LA_FRANCE and departement in classement.index:
        rang = list(classement.index).index(departement) + 1
        rang_texte = "1er" if rang == 1 else f"{rang}e"
        moyenne = tues_france.shape[0] / accidents_france.shape[0] * 100
        phrase += (
            f" **{noms[departement]}** : {nombre(par_departement.loc[departement, 'letalite'], 1)} tués pour 100 accidents, "
            f"contre {nombre(moyenne, 1)} en moyenne en métropole ({rang_texte} département le plus meurtrier sur {len(classement)})."
        )
    st.markdown(phrase)
    st.caption(
        "Carte : chaque département est coloré selon l'indicateur choisi (l'échelle de couleur, à droite, donne les valeurs). "
        "Survolez un département pour voir ses chiffres. Sur une courte période ou pour un mode rare, "
        "les petits départements ont peu d'accidents : leurs chiffres varient beaucoup d'une année à l'autre."
    )


# Regroupe les types de route trop rares dans « Autres ». Sur une colonne de type category,
# .map ne transforme que la liste des catégories (une dizaine de valeurs), pas chaque ligne
def regrouper_routes(types_de_route):
    return types_de_route.map(lambda type_route: PETITS_TYPES_DE_ROUTE.get(type_route, type_route))


# Pour chaque catégorie d'une colonne : nombre d'accidents et de tués, leur part du total (en %), et la létalité
def parts(accidents, tues, colonne):
    tableau = pd.DataFrame({
        "accidents": accidents.groupby(colonne).size(),
        "tues": tues.groupby(colonne).size(),
    }).fillna(0)
    tableau["part_accidents"] = tableau["accidents"] / tableau["accidents"].sum() * 100
    tableau["part_tues"] = tableau["tues"] / tableau["tues"].sum() * 100
    tableau["letalite"] = tableau["tues"] / tableau["accidents"] * 100
    return tableau
