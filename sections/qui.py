import pandas as pd
import streamlit as st

from utils.viz import barres_comparaison, nombre, petits_multiples

# Modes affichés en petits multiples, du plus au moins meurtrier (les autres sont trop rares pour être lisibles)
MODES = ["Voiture", "Deux-roues motorisé", "Piéton", "Vélo", "Utilitaire", "Trottinette / EDP"]

# Utilitaires : 56 tués en 2005 puis 120 en 2006, une rupture probablement due au changement des codes
# de véhicules en 2006. On n'affiche donc pas leur évolution quand la période commence en 2005
RUPTURE_2005 = ["Utilitaire"]

# Classes d'âge de l'ONISR, pour pouvoir comparer avec ses bilans
BORNES_AGE = [0, 14, 18, 25, 35, 65, 75, 120]
CLASSES_AGE = ["0-13 ans", "14-17 ans", "18-24 ans", "25-34 ans", "35-64 ans", "65-74 ans", "75 ans et plus"]


def afficher(accidents, personnes, periode):
    st.header("4. Qui ? Les automobilistes ont le plus gagné, cyclistes et seniors sont restés sur le bord de la route")
    debut, fin = periode
    tues = personnes[personnes["gravite"] == "Tué"]
    if len(tues) == 0:
        st.warning("Aucun tué ne correspond aux filtres choisis.")
        return

    # Tués par année et par mode de déplacement
    par_mode = tues.pivot_table(index = "annee", columns = "mode", values = "num_acc", aggfunc = "count", fill_value = 0)
    modes_presents = [mode for mode in MODES if mode in par_mode.columns]
    if not modes_presents:  # filtre sur un mode rare (poids lourd, bus…) : on affiche ce mode-là
        modes_presents = list(par_mode.columns)
    par_mode = par_mode.reindex(index = range(debut, fin + 1), columns = modes_presents, fill_value = 0)

    # Tués par classe d'âge, la première et la dernière année de la période
    tues = tues.assign(classe_age = pd.cut(tues["age"], bins = BORNES_AGE, labels = CLASSES_AGE, right = False))
    annees = sorted({debut, fin})
    par_age = pd.crosstab(tues["classe_age"], tues["annee"]).reindex(index = CLASSES_AGE, columns = annees, fill_value = 0)

    # Phrase de conclusion
    phrases = []
    comparables = [mode for mode in ["Voiture", "Vélo"] if mode in par_mode.columns and par_mode[mode].iloc[0] > 0]
    if debut < fin and comparables:
        evolutions = [f"{mode.lower()} **{variation(par_mode[mode])}**" for mode in comparables]
        phrases.append(f"Entre {debut} et {fin}, évolution du nombre de tués : " + ", ".join(evolutions) + ".")
    seniors = par_age.loc[["65-74 ans", "75 ans et plus"]].sum() / par_age.sum() * 100
    if debut < fin:
        phrases.append(
            f"Les 65 ans et plus représentent **{nombre(seniors[fin])} % des tués en {fin}**, "
            f"contre {nombre(seniors[debut])} % en {debut}."
        )
    hommes = (tues["sexe"] == "Homme").sum() / tues["sexe"].notna().sum() * 100
    phrases.append(f"**{nombre(hommes)} % des tués sont des hommes.**")
    st.markdown(" ".join(phrases))

    # Petits multiples par mode
    st.subheader("Nombre de tués par mode de déplacement")
    titres = {mode: titre_mode(mode, par_mode[mode]) for mode in par_mode.columns}
    st.plotly_chart(petits_multiples(par_mode, titres, "tués"), width = "stretch")
    st.caption(
        "Petits multiples : un graphique par mode de déplacement, chacun avec sa propre échelle verticale, "
        "pour comparer la forme des évolutions. La catégorie « Trottinette / EDP » n'existe que depuis 2019 : "
        "avant, ces usagers étaient comptés parmi les piétons. Note sur les utilitaires : 56 tués en 2005 puis 120 en 2006, "
        "une rupture probablement due au changement des codes de véhicules en 2006 ; l'évolution depuis 2005 n'est pas fiable. "
        "Sans données sur les distances parcourues, "
        "une hausse des tués ne prouve pas que chaque trajet soit plus dangereux (il peut y avoir plus de cyclistes)."
    )

    # Barres par classe d'âge
    st.subheader("Nombre de tués par classe d'âge")
    st.plotly_chart(barres_comparaison(par_age, "Classe d'âge", "Nombre de tués", "tués"), width = "stretch")
    st.caption(
        "Barres : nombre de tués par classe d'âge, la première et la dernière année de la période. "
        "L'âge est calculé à un an près (seule l'année de naissance est connue). "
        "La population vieillit : une partie de la hausse de la part des seniors est mécanique."
    )


# Évolution en % entre la première et la dernière valeur d'une série, par exemple « -50 % »
def variation(serie):
    return signe((serie.iloc[-1] / serie.iloc[0] - 1) * 100)


# Écrit un pourcentage avec son signe : 24 → « +24 % », -50 → « -50 % »
def signe(pourcentage):
    texte = nombre(pourcentage) + " %"
    return texte if pourcentage < 0 else "+" + texte


# Titre d'un mini-graphique : le mode et son évolution sur la période, si elle a un sens
def titre_mode(mode, serie):
    if len(serie) < 2 or serie.iloc[0] == 0:
        return mode
    if mode in RUPTURE_2005 and serie.index[0] == 2005:
        return mode + " (voir la note)"
    return f"{mode} ({signe((serie.iloc[-1] / serie.iloc[0] - 1) * 100)})"
