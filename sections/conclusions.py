import streamlit as st

from utils.viz import nombre

HEURES_DE_NUIT = [22, 23, 0, 1, 2, 3, 4, 5]
USAGERS_VULNERABLES = ["Piéton", "Vélo", "Trottinette / EDP", "Deux-roues motorisé"]


def afficher(accidents, personnes, territoire, periode):
    st.header("6. Conclusions et pistes d'action")
    tues = personnes[personnes["gravite"] == "Tué"]
    if len(tues) == 0:
        st.warning("Aucun tué ne correspond aux filtres choisis.")
        return

    # Les chiffres clés de la sélection actuelle
    debut, fin = periode
    heures = accidents[["num_acc", "heure"]]
    tues_nuit = tues.merge(heures, on = "num_acc")["heure"].isin(HEURES_DE_NUIT).mean() * 100
    accidents_nuit = accidents["heure"].isin(HEURES_DE_NUIT).mean() * 100
    hors_agglomeration = (tues["agglomeration"] == "Hors agglomération").mean() * 100
    departementales = (tues["type_route"] == "Route départementale").mean() * 100
    vulnerables = {annee: tues.loc[tues["annee"] == annee, "mode"].isin(USAGERS_VULNERABLES).mean() * 100 for annee in [debut, fin]}

    st.markdown(f"**Ce qui ressort** ({territoire}, {debut}-{fin}) :")
    colonne1, colonne2, colonne3 = st.columns(3)
    with colonne1.container(border = True):
        st.markdown(
            f"**1. Le danger est hors des villes.**\n\n"
            f"{nombre(hors_agglomeration)} % des tués meurent hors agglomération, "
            f"et {nombre(departementales)} % sur les routes départementales."
        )
    with colonne2.container(border = True):
        st.markdown(
            f"**2. La nuit pèse lourd.**\n\n"
            f"{nombre(tues_nuit)} % des tués meurent entre 22 h et 6 h, "
            f"alors que seulement {nombre(accidents_nuit)} % des accidents ont lieu à ces heures-là."
        )
    texte_vulnerables = (
        f"En {fin}, {nombre(vulnerables[fin])} % des tués étaient à pied, à vélo, en trottinette ou en deux-roues motorisé"
    )
    if debut < fin and tues["annee"].eq(debut).any():
        texte_vulnerables += f", contre {nombre(vulnerables[debut])} % en {debut}"
    with colonne3.container(border = True):
        st.markdown(f"**3. Les usagers vulnérables restent exposés.**\n\n{texte_vulnerables}.")

    # Pistes d'action, une par constat
    st.subheader("Pistes d'action pour un décideur local")
    st.markdown(
        "Ces données montrent **où et quand** la route tue, pas **pourquoi** : les pistes ci-dessous sont à étudier "
        "au cas par cas, pas des solutions dont l'efficacité serait prouvée ici."
    )
    st.markdown(
        "- **Routes départementales** : repérer les tronçons où se concentrent les accidents mortels, puis étudier "
        "les aménagements (séparation des voies, traitement des obstacles en bord de route, carrefours) et les contrôles de vitesse.\n"
        "- **Nuit et week-end** : cibler les contrôles (vitesse, alcool, stupéfiants) et la prévention sur ces créneaux, "
        "et étudier l'éclairage des carrefours les plus accidentés.\n"
        "- **Usagers vulnérables** : développer des aménagements cyclables séparés de la circulation, sécuriser les traversées "
        "piétonnes et apaiser la vitesse en ville ; accompagner la mobilité des seniors."
    )

    # Ce que les données ne disent pas encore
    st.subheader("Pour aller plus loin")
    st.markdown(
        "- **Rapporter à la population** (INSEE) pour mesurer le risque par habitant, et pas seulement par accident.\n"
        "- **Rapporter au trafic** (kilomètres parcourus) pour savoir si la hausse des cyclistes tués vient d'un risque "
        "plus élevé ou simplement de plus de cyclistes.\n"
        "- **Évaluer les mesures locales**, par exemple comparer avant et après le passage à 80 km/h, ou le retour à 90 km/h "
        "décidé par certains départements."
    )
    st.success(
        "En résumé, en France métropolitaine : après une forte baisse entre 2005 et 2013, la mortalité routière stagne. "
        "Les marges de progrès se trouvent sur les routes de campagne, la nuit, et auprès des usagers vulnérables."
    )
