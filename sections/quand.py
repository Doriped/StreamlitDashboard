import streamlit as st

from utils.viz import barres_simples, carte_chaleur, nombre

JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
HEURES_DE_NUIT = [22, 23, 0, 1, 2, 3, 4, 5]

INDICATEURS_CHALEUR = {
    "Tués pour 100 accidents": "letalite",
    "Nombre d'accidents": "accidents",
}


def afficher(accidents, personnes):
    st.header("3. Quand ? La nuit et le week-end, chaque accident pèse plus lourd")
    if len(accidents) == 0:
        st.warning("Aucun accident ne correspond aux filtres choisis.")
        return

    # Chaque tué reçoit l'heure, le jour et l'éclairage de son accident
    moments = accidents[["num_acc", "heure", "jour_semaine", "lumiere"]]
    tues = personnes[personnes["gravite"] == "Tué"].merge(moments, on = "num_acc")

    # Phrase de conclusion : la nuit et le week-end
    nuit_accidents = accidents["heure"].isin(HEURES_DE_NUIT).mean() * 100
    nuit_tues = tues["heure"].isin(HEURES_DE_NUIT).mean() * 100
    weekend_accidents = accidents["jour_semaine"].isin(["Samedi", "Dimanche"]).mean() * 100
    weekend_tues = tues["jour_semaine"].isin(["Samedi", "Dimanche"]).mean() * 100
    st.markdown(
        f"La nuit (22 h - 6 h) : **{nombre(nuit_accidents)} % des accidents, mais {nombre(nuit_tues)} % des tués**. "
        f"Le week-end : {nombre(weekend_accidents)} % des accidents, mais {nombre(weekend_tues)} % des tués."
    )

    # Carte de chaleur heure × jour
    st.subheader("Heure et jour de la semaine")
    choix = st.radio("Colorer selon :", list(INDICATEURS_CHALEUR), horizontal = True)
    nb_accidents = accidents.pivot_table(index = "jour_semaine", columns = "heure", values = "num_acc", aggfunc = "count", fill_value = 0)
    nb_tues = tues.pivot_table(index = "jour_semaine", columns = "heure", values = "num_acc", aggfunc = "count", fill_value = 0)
    nb_accidents = nb_accidents.reindex(index = JOURS, columns = range(24), fill_value = 0)
    nb_tues = nb_tues.reindex(index = JOURS, columns = range(24), fill_value = 0)
    tableaux = {"accidents": nb_accidents, "letalite": nb_tues / nb_accidents.where(nb_accidents > 0) * 100}

    st.plotly_chart(
        carte_chaleur(tableaux[INDICATEURS_CHALEUR[choix]], nb_accidents, nb_tues, "Heure de l'accident", None, choix, " h"),
        width = "stretch",
    )
    st.caption(
        "Carte de chaleur : chaque case correspond à une heure d'un jour de la semaine (l'échelle de couleur, à droite, donne les valeurs). "
        "Les accidents sont les plus nombreux en fin d'après-midi en semaine, mais les plus meurtriers la nuit, "
        "surtout les nuits du week-end."
    )

    # Éclairage
    st.subheader("Conditions d'éclairage")
    eclairage = (tues.groupby("lumiere").size() / accidents.groupby("lumiere").size() * 100).dropna()
    moyenne = len(tues) / len(accidents) * 100
    st.plotly_chart(
        barres_simples(eclairage, "Tués pour 100 accidents", "tués pour 100 accidents",
                       reference = moyenne, texte_reference = f"Moyenne : {nombre(moyenne, 1)}"),
        width = "stretch",
    )
    st.caption(
        "Barres : nombre de tués pour 100 accidents selon l'éclairage ; la ligne pointillée marque la moyenne. "
        "Prudence : les routes sans éclairage public sont surtout hors agglomération, où l'on roule plus vite. "
        "L'éclairage n'est donc pas la seule explication."
    )
