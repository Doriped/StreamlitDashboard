import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# Couleurs pour le thème clair et le thème sombre de Streamlit.
# Palette de référence validée : contraste suffisant sur le fond, et couleurs distinguables par les daltoniens.
COULEURS = {
    "light": {
        "serie": "#2a78d6", "serie2": "#eb6834", "texte": "#52514e", "reference": "#898781",
        "contour": "#fcfcfb", "selection": "#0b0b0b",
        # dégradé d'une seule teinte, du plus faible (clair) au plus fort (foncé)
        "degrade": ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"],
    },
    "dark": {
        "serie": "#3987e5", "serie2": "#d95926", "texte": "#c3c2b7", "reference": "#898781",
        "contour": "#1a1a19", "selection": "#f0efec",
        # sur fond sombre, le plus faible se fond dans le fond (foncé) et le plus fort ressort (clair)
        "degrade": ["#0d366b", "#184f95", "#256abf", "#3987e5", "#6da7ec", "#9ec5f4", "#cde2fb"],
    },
}


# Renvoie les couleurs du thème (clair ou sombre) choisi par l'utilisateur
def couleurs():
    theme = st.context.theme.type or "light"
    return COULEURS[theme]


# Écrit un nombre au format français : nombre(3193) → « 3 193 », nombre(6.25, 1) → « 6,3 »
def nombre(valeur, decimales = 0):
    texte = f"{valeur:,.{decimales}f}"                       # format anglais : 3,193.0
    return texte.replace(",", " ").replace(".", ",")         # format français : 3 193,0


# Style commun à tous les graphiques : nombres au format français, axes titrés, marges réduites
def styliser(fig, titre_x, titre_y, hauteur = 380):
    fig.update_layout(
        height = hauteur,
        margin = dict(l = 10, r = 10, t = 30, b = 10),
        separators = ", ",  # virgule décimale et espace pour les milliers : 6,3 et 3 193
        showlegend = False,
        hovermode = "x",
    )
    fig.update_xaxes(title = titre_x, showgrid = False)
    fig.update_yaxes(title = titre_y, rangemode = "tozero")
    return fig


# Courbe d'une valeur par année, avec des annotations sur les années clés
# et, si demandé, une ligne de référence horizontale au niveau d'une année donnée.
def courbe_annuelle(valeurs, titre_y, unite, annotations, annee_reference = None):
    c = couleurs()
    fig = go.Figure(go.Scatter(
        x = valeurs.index,
        y = valeurs.values,
        mode = "lines+markers",
        line = dict(color = c["serie"], width = 2),
        marker = dict(size = 8),
        hovertemplate = "%{x} : <b>%{y:,}</b> " + unite + "<extra></extra>",
    ))

    if annee_reference in valeurs.index:
        fig.add_hline(
            y = valeurs[annee_reference],
            line = dict(color = c["reference"], width = 1, dash = "dash"),
            annotation_text = f"Niveau de {annee_reference}",
            annotation_position = "top left",
            annotation_font_color = c["texte"],
        )

    for annee, (texte, decalage) in annotations.items():
        if annee in valeurs.index:
            fig.add_annotation(
                x = annee, y = valeurs[annee], text = texte,
                showarrow = True, arrowhead = 0, ax = 0, ay = decalage,
                arrowcolor = c["reference"], font = dict(color = c["texte"], size = 12),
            )

    fig = styliser(fig, "Année", titre_y)
    fig.update_xaxes(range = [valeurs.index.min() - 0.5, valeurs.index.max() + 0.5], dtick = 2)
    return fig


# Barres horizontales groupées : pour chaque catégorie, la part des accidents et la part des tués (en %).
def barres_parts(tableau, hauteur = 300):
    c = couleurs()
    tableau = tableau.sort_values("part_tues")  # Plotly dessine de bas en haut : la plus grande part en haut
    fig = go.Figure()
    series = [
        ("Part des accidents", "part_accidents", "accidents", "accidents", c["serie"]),
        ("Part des tués", "part_tues", "tues", "tués", c["serie2"]),
    ]
    for nom, colonne_part, colonne_nombre, unite, couleur in series:
        fig.add_trace(go.Bar(
            name = nom,
            y = tableau.index,
            x = tableau[colonne_part],
            orientation = "h",
            marker = dict(color = couleur, cornerradius = 4),
            text = tableau[colonne_part].map(lambda v: nombre(v) + " %"),
            textposition = "outside",
            customdata = tableau[colonne_nombre],
            hovertemplate = "%{y} : <b>%{x:.0f} %</b> des " + unite + " (%{customdata:,} " + unite + ")<extra></extra>",
        ))
    fig = styliser(fig, "Part du total (%)", None, hauteur)
    fig.update_layout(
        barmode = "group", bargap = 0.25, bargroupgap = 0.1, hovermode = "closest",
        showlegend = True, legend = dict(orientation = "h", y = 1.12, x = 0, traceorder = "reversed"),
    )
    fig.update_xaxes(range = [0, tableau[["part_accidents", "part_tues"]].max().max() * 1.2], showgrid = True)
    fig.update_yaxes(rangemode = "normal")
    return fig


# Carte des départements, colorée selon une valeur (dégradé d'une seule teinte).
# donnees : une ligne par département, indexée par son code, avec les colonnes nom, accidents, tues, letalite
def carte_departements(donnees, colonne, titre_couleur, contours, departement_selectionne = None):
    c = couleurs()
    fig = go.Figure(go.Choropleth(
        geojson = contours,
        featureidkey = "properties.code",  # le code du département dans le fichier des contours
        locations = donnees.index,
        z = donnees[colonne],
        colorscale = c["degrade"],
        # L'échelle s'arrête au 95e percentile : un département extrême ne doit pas écraser les nuances des autres
        zmin = 0,
        zmax = donnees[colonne].quantile(0.95),
        marker = dict(line = dict(color = c["contour"], width = 0.5)),
        colorbar = dict(title = dict(text = titre_couleur, side = "right"), thickness = 12),
        customdata = donnees[["nom", "accidents", "tues", "letalite"]],
        hovertemplate = (
            "<b>%{location} – %{customdata[0]}</b><br>"
            "%{customdata[1]:,} accidents · %{customdata[2]:,} tués<br>"
            "%{customdata[3]:.1f} tués pour 100 accidents<extra></extra>"
        ),
    ))

    # Contour épais autour du département choisi dans le filtre
    if departement_selectionne in donnees.index:
        fig.add_trace(go.Choropleth(
            geojson = contours, featureidkey = "properties.code",
            locations = [departement_selectionne], z = [0],
            colorscale = [[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]], showscale = False,
            marker = dict(line = dict(color = c["selection"], width = 3)),
            hoverinfo = "skip",
        ))

    fig.update_geos(fitbounds = "locations", visible = False, bgcolor = "rgba(0,0,0,0)")
    fig.update_layout(height = 560, margin = dict(l = 0, r = 0, t = 10, b = 0), separators = ", ")
    return fig


# Carte de chaleur : une case par (ligne, colonne), colorée selon une valeur (dégradé d'une seule teinte).
# valeurs, accidents, tues : trois tableaux de même forme (par exemple jours × heures)
def carte_chaleur(valeurs, accidents, tues, titre_x, titre_y, titre_couleur, unite_colonne = ""):
    c = couleurs()
    fig = go.Figure(go.Heatmap(
        z = valeurs.values,
        x = [f"{colonne}{unite_colonne}" for colonne in valeurs.columns],
        y = valeurs.index,
        colorscale = c["degrade"],
        zmin = 0,
        zmax = pd.Series(valeurs.values.ravel()).quantile(0.95),  # comme la carte : un extrême n'écrase pas les nuances
        xgap = 2, ygap = 2,  # un fin espace entre les cases
        colorbar = dict(title = dict(text = titre_couleur, side = "right"), thickness = 12),
        # pour chaque case, le couple (accidents, tués), affiché dans l'infobulle
        customdata = np.dstack([accidents.values, tues.values]),
        hovertemplate = (
            "<b>%{y}, %{x}</b><br>%{customdata[0]:,} accidents · %{customdata[1]:,} tués<br>"
            "%{z:.1f} " + titre_couleur.lower() + "<extra></extra>"
        ),
    ))
    fig = styliser(fig, titre_x, titre_y, hauteur = 360)
    fig.update_layout(hovermode = "closest")
    fig.update_yaxes(autorange = "reversed", rangemode = "normal")  # lundi en haut, dimanche en bas
    return fig


# Barres horizontales d'une seule série, avec la valeur au bout de chaque barre
# et, si demandé, une ligne verticale de référence (par exemple la moyenne)
def barres_simples(valeurs, titre_x, unite, reference = None, texte_reference = "", hauteur = 300):
    c = couleurs()
    valeurs = valeurs.sort_values()  # Plotly dessine de bas en haut : la plus grande valeur en haut
    fig = go.Figure(go.Bar(
        y = valeurs.index,
        x = valeurs.values,
        orientation = "h",
        marker = dict(color = c["serie"], cornerradius = 4),
        text = valeurs.map(lambda v: nombre(v, 1)),
        textposition = "outside",
        hovertemplate = "%{y} : <b>%{x:.1f}</b> " + unite + "<extra></extra>",
    ))
    if reference is not None:
        fig.add_vline(
            x = reference,
            line = dict(color = c["reference"], width = 1, dash = "dash"),
            annotation_text = texte_reference,
            annotation_position = "top",
            annotation_font_color = c["texte"],
        )
    fig = styliser(fig, titre_x, None, hauteur)
    fig.update_layout(hovermode = "closest")
    fig.update_xaxes(range = [0, valeurs.max() * 1.2], showgrid = True)
    fig.update_yaxes(rangemode = "normal")
    return fig


# Petits multiples : un mini-graphique par colonne du tableau (par exemple un par mode de déplacement),
# chacun avec sa propre échelle verticale, pour comparer la forme des évolutions.
# tableau : une ligne par année, une colonne par série ; titres : {colonne: titre du mini-graphique}
def petits_multiples(tableau, titres, unite, nb_colonnes = 3):
    c = couleurs()
    nb_lignes = -(-len(tableau.columns) // nb_colonnes)  # division arrondie au supérieur
    fig = make_subplots(
        rows = nb_lignes, cols = nb_colonnes,
        subplot_titles = [titres[colonne] for colonne in tableau.columns],
        vertical_spacing = 0.18, horizontal_spacing = 0.07,
    )
    for i, colonne in enumerate(tableau.columns):
        fig.add_trace(
            go.Scatter(
                x = tableau.index, y = tableau[colonne], mode = "lines+markers",
                line = dict(color = c["serie"], width = 2), marker = dict(size = 5),
                hovertemplate = colonne + ", %{x} : <b>%{y:,}</b> " + unite + "<extra></extra>",
            ),
            row = i // nb_colonnes + 1, col = i % nb_colonnes + 1,
        )
    fig.update_layout(
        height = 260 * nb_lignes, margin = dict(l = 10, r = 10, t = 40, b = 10),
        separators = ", ", showlegend = False, hovermode = "closest",
    )
    fig.update_yaxes(rangemode = "tozero")
    fig.update_xaxes(showgrid = False, dtick = 5, range = [tableau.index.min() - 0.5, tableau.index.max() + 0.5])
    fig.update_annotations(font = dict(size = 13, color = c["texte"]))  # les titres des mini-graphiques
    return fig


# Barres verticales groupées : comparer deux colonnes (par exemple deux années) pour chaque catégorie
def barres_comparaison(tableau, titre_x, titre_y, unite, hauteur = 380):
    c = couleurs()
    fig = go.Figure()
    for colonne, couleur in zip(tableau.columns, [c["serie"], c["serie2"]]):
        fig.add_trace(go.Bar(
            name = str(colonne),
            x = tableau.index,
            y = tableau[colonne],
            marker = dict(color = couleur, cornerradius = 4),
            text = tableau[colonne].map(nombre),
            textposition = "outside",
            hovertemplate = "%{x}, " + str(colonne) + " : <b>%{y:,}</b> " + unite + "<extra></extra>",
        ))
    fig = styliser(fig, titre_x, titre_y, hauteur)
    fig.update_layout(
        barmode = "group", bargap = 0.25, bargroupgap = 0.1, hovermode = "closest",
        showlegend = True, legend = dict(orientation = "h", y = 1.1, x = 0),
    )
    fig.update_yaxes(range = [0, tableau.max().max() * 1.15])
    return fig


# Plusieurs courbes sur le même axe (au maximum deux, de même ordre de grandeur),
# avec une ligne verticale pour signaler une année particulière (par exemple un changement de méthode)
def courbes(tableau, titre_y, unite, annee_marquee = None, texte_marque = ""):
    c = couleurs()
    fig = go.Figure()
    for colonne, couleur in zip(tableau.columns, [c["serie"], c["serie2"]]):
        fig.add_trace(go.Scatter(
            name = colonne, x = tableau.index, y = tableau[colonne], mode = "lines+markers",
            line = dict(color = couleur, width = 2), marker = dict(size = 6),
            hovertemplate = colonne + " : <b>%{y:,}</b> " + unite + "<extra></extra>",
        ))
    if annee_marquee is not None:
        fig.add_vline(
            x = annee_marquee - 0.5,  # entre l'année précédente et l'année marquée
            line = dict(color = c["reference"], width = 1, dash = "dash"),
            annotation_text = texte_marque, annotation_position = "bottom left",
            annotation_font_color = c["texte"],
        )
    fig = styliser(fig, "Année", titre_y)
    fig.update_layout(
        showlegend = True, legend = dict(orientation = "h", y = 1.15, x = 0), hovermode = "x unified",
        margin = dict(l = 10, r = 10, t = 50, b = 10),  # de la place au-dessus pour la légende
    )
    fig.update_xaxes(range = [tableau.index.min() - 0.5, tableau.index.max() + 0.5], dtick = 2)
    fig.update_yaxes(tickformat = ",d")  # « 70 000 » plutôt que la notation anglaise « 70k »
    return fig
