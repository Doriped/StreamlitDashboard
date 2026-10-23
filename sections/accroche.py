import pandas as pd
import streamlit as st

from utils.viz import courbe_annuelle, nombre

# Événements à signaler sur la courbe des tués : 
EVENEMENTS = {
    2013: ("Début du plateau", -40),
    2018: ("80 km/h sur les routes secondaires", -85),
    2020: ("Confinements", 40),
}


def afficher(accidents, personnes, periode):
    st.header("1. La route tue encore près de 9 personnes par jour")
    debut, fin = periode
    annees = range(debut, fin + 1)

    # Nombre de tués et d'accidents par année (les années sans aucun cas valent 0)
    tues = personnes[personnes["gravite"] == "Tué"].groupby("annee").size().reindex(annees, fill_value = 0)
    nb_accidents = accidents.groupby("annee").size().reindex(annees, fill_value = 0)

    if nb_accidents.sum() == 0:
        st.warning("Aucun accident ne correspond aux filtres choisis.")
        return

    # Bandeau d'indicateurs : dernière année de la période, comparée à la première
    jours = pd.Timestamp(fin, 12, 31).dayofyear  # 365, ou 366 les années bissextiles
    colonne1, colonne2, colonne3, colonne4 = st.columns(4)
    colonne1.metric(
        f"Tués en {fin}", nombre(tues[fin]),
        delta = variation(tues[debut], tues[fin], debut), delta_color = "inverse",
        help = "Personnes décédées sur le coup ou dans les 30 jours suivant l'accident.",
    )
    colonne2.metric(f"Tués par jour en {fin}", nombre(tues[fin] / jours, 1))
    colonne3.metric(
        f"Accidents en {fin}", nombre(nb_accidents[fin]),
        delta = variation(nb_accidents[debut], nb_accidents[fin], debut), delta_color = "inverse",
        help = "Accidents ayant fait au moins une victime nécessitant des soins, relevés par les forces de l'ordre.",
    )
    colonne4.metric(
        f"Tués / 100 accidents ({debut}-{fin})", nombre(tues.sum() / nb_accidents.sum() * 100, 1),
        help = "La létalité mesure la gravité des accidents : nombre de tués pour 100 accidents corporels.",
    )

    # Phrase de conclusion, calculée selon les filtres
    phrase = f"Entre {debut} et {fin}, le nombre de tués est passé de **{nombre(tues[debut])}** à **{nombre(tues[fin])}**."
    if debut < 2013 < fin:
        phrase += f" Mais depuis 2013, il n'a quasiment plus baissé : {nombre(tues[2013])} tués en 2013, {nombre(tues[fin])} en {fin}."
    st.markdown(phrase)

    # Courbe des tués, avec les événements clés et le niveau de 2013 en référence
    st.subheader("Nombre de tués par année")
    fig = courbe_annuelle(tues, "Nombre de tués", "tués", EVENEMENTS, annee_reference = 2013)
    st.plotly_chart(fig, width = "stretch")
    st.caption(
        f"Graphique : nombre de personnes tuées chaque année entre {debut} et {fin}. "
        "La ligne pointillée marque le niveau de 2013 ; 2020 est une année exceptionnelle, marquée par les confinements."
    )


# Texte de l'évolution entre deux valeurs, par exemple « -40 % depuis 2005 »
def variation(avant, apres, annee_avant):
    if avant == 0:
        return None
    return f"{nombre((apres / avant - 1) * 100)} % depuis {annee_avant}"
