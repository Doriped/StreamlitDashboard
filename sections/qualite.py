import streamlit as st

from utils.viz import courbe_annuelle, courbes, nombre

# Bilan officiel de l'ONISR pour 2024 (« Chiffres clés 2024 », résultats définitifs, 28 mai 2025)
BILAN_ONISR_2024 = 3193
LIEN_ONISR_2024 = (
    "https://www.onisr.securite-routiere.gouv.fr/etat-de-linsecurite-routiere/"
    "bilans-annuels-de-la-securite-routiere/bilan-2024-de-la-securite-routiere"
)

# Cette section ne suit pas les filtres : la qualité des données concerne la base entière
def afficher(controles):
    st.header("5. Qualité des données et limites")
    st.markdown(
        "Les données viennent des **bulletins d'analyse des accidents corporels (BAAC)**, remplis par la police "
        "et la gendarmerie pour chaque accident ayant fait au moins une victime. Il s'agit d'une base brute : "
        "voici les contrôles réalisés, les corrections apportées et les limites à garder en tête."
    )

    # Les contrôles en un coup d'œil
    controles = controles.set_index("annee")
    tues_2024 = controles.loc[2024, "tues_metropole"]
    colonne1, colonne2, colonne3, colonne4 = st.columns(4)
    colonne1.metric("Accidents en double", nombre(controles["accidents_en_double"].sum()),
                    help = "Identifiants d'accident présents deux fois dans un même fichier, sur les 20 années.")
    colonne2.metric("Usagers ou véhicules orphelins",
                    nombre(controles["usagers_sans_accident"].sum() + controles["vehicules_sans_accident"].sum()),
                    help = "Usagers ou véhicules rattachés à un accident qui n'existe pas : contrôle de cohérence entre les tables.")
    colonne3.metric("Véhicules en double (corrigés)", nombre(controles["vehicules_en_double"].sum()),
                    help = "Deux véhicules d'un même accident portant la même lettre : seul le premier est gardé.")
    colonne4.metric("Tués 2024 : écart avec l'ONISR", nombre(tues_2024 - BILAN_ONISR_2024),
                    help = f"Nos données : {nombre(tues_2024)} tués en métropole en 2024. Bilan officiel de l'ONISR : {nombre(BILAN_ONISR_2024)}.")
    st.markdown(
        f"**Validation :** nos données donnent {nombre(tues_2024)} tués en métropole en 2024, "
        f"exactement le [bilan officiel de l'ONISR]({LIEN_ONISR_2024}). La répartition par mode de déplacement et par sexe "
        "correspond aussi aux chiffres publiés."
    )

    colonne1, colonne2 = st.columns(2)

    # Géolocalisation par année
    with colonne1:
        st.subheader("Part des accidents géolocalisés")
        gps = (100 - controles["gps_manquant_pct"]).round(1)
        st.plotly_chart(
            courbe_annuelle(gps, "Accidents géolocalisés (%)", "%", {2009: ("2009 : 0 %", -60)}),
            width = "stretch",
        )
        st.caption(
            "Courbe : part des accidents de métropole avec des coordonnées GPS valables (en 2009, aucune ne l'est). "
            "Une carte par point d'accident n'est possible qu'à partir de 2018 ; le département, lui, est connu pour tous."
        )

    # Rupture de 2018 sur les blessés hospitalisés
    with colonne2:
        st.subheader("La rupture de 2018 sur les blessés")
        blesses = controles[["blesses_hospitalises_metropole", "blesses_legers_metropole"]]
        blesses.columns = ["Blessés hospitalisés", "Blessés légers"]
        st.plotly_chart(
            courbes(blesses, "Nombre de blessés", "blessés", annee_marquee = 2018, texte_marque = "Changement de méthode"),
            width = "stretch",
        )
        st.caption(
            "Courbes : blessés hospitalisés et blessés légers par année. En 2018, les premiers chutent de 23 % "
            "pendant que les seconds augmentent : c'est un changement de méthode de saisie, pas une amélioration. "
            "C'est pourquoi ce dashboard compare les années avec le nombre de tués."
        )

    # Corrections et limites
    colonne1, colonne2 = st.columns(2)
    with colonne1:
        st.subheader("Corrections apportées")
        st.markdown(
            "- **Formats différents avant 2019** : séparateur, encodage des accents, année sans siècle (`5` pour 2005), "
            "heure en nombre (`740`), départements sur 3 chiffres (`590`), coordonnées GPS multipliées par 100 000.\n"
            "- **Zéros perdus dans les codes départements** en 2009 (`10` au lieu de `010` pour l'Ain) et en 2019 "
            "(`8` au lieu de `08` pour les Ardennes) : sans correction, des milliers d'accidents changeaient de département.\n"
            "- **Coordonnées GPS impossibles** (hors de la France métropolitaine) effacées.\n"
            "- **Vitesses autorisées aberrantes** (0, 500, 900 km/h) remplacées par « inconnue ».\n"
            "- **Lieux multiples** pour un même accident (depuis 2023) : seul le lieu principal est gardé.\n"
            "- **40 catégories de véhicules** regroupées en 8 modes de déplacement, validés avec les chiffres de l'ONISR."
        )
    with colonne2:
        st.subheader("Limites à garder en tête")
        st.markdown(
            "- **Pas de données d'exposition** : sans le trafic, les distances parcourues ou la population, on compare "
            "des nombres et des taux de gravité, pas un risque par kilomètre ou par habitant.\n"
            "- **Corrélation n'est pas causalité** : un accident de nuit est plus grave, mais la nuit n'en est pas forcément la cause.\n"
            "- **Accidents non déclarés** : la police n'est pas toujours appelée pour les accidents légers ; "
            "le nombre de tués est fiable, le nombre d'accidents moins.\n"
            "- **Catégories apparues en cours de route** : trottinettes (2019), routes de métropole urbaine, "
            "vitesse autorisée (2019).\n"
            "- **Âge à un an près** : seule l'année de naissance est connue.\n"
            "- **Conducteurs en fuite** (depuis 2021) : environ 2 % des usagers, de sexe et d'âge inconnus.\n"
            "- **Vie privée** : les données sont agrégées ; l'ONISR publie à part, sans lien possible, la marque et le modèle des véhicules."
        )