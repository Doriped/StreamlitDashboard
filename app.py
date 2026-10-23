import streamlit as st

from sections import accroche, conclusions, ou, qualite, quand, qui
from utils.filtres import TOUS_LES_MODES, TOUTE_LA_FRANCE, filtrer
from utils.io import SOURCE, charger_controles, charger_departements, charger_donnees

st.set_page_config(page_title = "Routes de France", page_icon = "🚗", layout = "wide")

accidents, personnes = charger_donnees()
controles = charger_controles()
contours, noms_departements = charger_departements()


# Texte affiché dans la liste des départements : « 39 – Jura » au lieu de « 39 »
def nom_complet(code):
    if code == TOUTE_LA_FRANCE:
        return code
    return f"{code} – {noms_departements[code]}"

# Barre latérale : les filtres, qui s'appliquent à toutes les sections
with st.sidebar:
    st.header("Filtres")
    periode = st.slider("Période", min_value = 2005, max_value = 2024, value = (2005, 2024))

    departements = sorted(accidents.loc[accidents["zone"] == "Métropole", "dep"].unique())
    departement = st.selectbox("Département", [TOUTE_LA_FRANCE] + departements, format_func = nom_complet)

    modes = sorted(personnes["mode"].dropna().unique())
    mode = st.selectbox("Mode de déplacement", [TOUS_LES_MODES] + modes)

accidents_filtres, personnes_filtrees = filtrer(accidents, personnes, periode, departement, mode)

# Pour la carte, il faut tous les départements, même quand un seul est sélectionné
# (si toute la France est déjà sélectionnée, inutile de refaire le même filtre)
if departement == TOUTE_LA_FRANCE:
    accidents_france, personnes_france = accidents_filtres, personnes_filtrees
else:
    accidents_france, personnes_france = filtrer(accidents, personnes, periode, TOUTE_LA_FRANCE, mode)

# Titre et source
st.title("Routes de France : pourquoi la route ne tue pas moins depuis 10 ans")
st.caption(SOURCE)

# Si les filtres ne laissent aucun accident, un seul message plutôt qu'un par section
if len(accidents_filtres) == 0:
    st.warning("Aucun accident ne correspond aux filtres choisis : élargissez la période, le département ou le mode.")
    st.stop()

# L'histoire, section par section
accroche.afficher(accidents_filtres, personnes_filtrees, periode)
ou.afficher(accidents_filtres, personnes_filtrees, accidents_france, personnes_france, departement, contours, noms_departements)
quand.afficher(accidents_filtres, personnes_filtrees)
qui.afficher(accidents_filtres, personnes_filtrees, periode)
qualite.afficher(controles)
conclusions.afficher(accidents_filtres, personnes_filtrees, nom_complet(departement), periode)
