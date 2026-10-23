import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# Light and dark theme colors (colorblind-safe palette, readable contrast on both backgrounds)
COLORS = {
    "light": {
        "series": "#2a78d6", "series2": "#eb6834", "text": "#52514e", "reference": "#898781",
        "border": "#fcfcfb", "selection": "#0b0b0b",
        "scale": ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"],
    },
    "dark": {
        "series": "#3987e5", "series2": "#d95926", "text": "#c3c2b7", "reference": "#898781",
        "border": "#1a1a19", "selection": "#f0efec",
        # on a dark background, low values blend into the background and high values stand out
        "scale": ["#0d366b", "#184f95", "#256abf", "#3987e5", "#6da7ec", "#9ec5f4", "#cde2fb"],
    },
}


def colors():
    return COLORS[st.context.theme.type or "light"]


# fmt(3193) → "3,193", fmt(6.25, 1) → "6.3"
def fmt(value, decimals = 0):
    return f"{value:,.{decimals}f}"


# Layout shared by all charts
def style(fig, x_title, y_title, height = 380):
    fig.update_layout(height = height, margin = dict(l = 10, r = 10, t = 30, b = 10), showlegend = False, hovermode = "x")
    fig.update_xaxes(title = x_title, showgrid = False)
    fig.update_yaxes(title = y_title, rangemode = "tozero")
    return fig


# One value per year. annotations = {year: (text, vertical offset in px)}, negative = above the point.
def yearly_line(values, y_title, unit, annotations, reference_year = None):
    c = colors()
    fig = go.Figure(go.Scatter(
        x = values.index, y = values.values, mode = "lines+markers",
        line = dict(color = c["series"], width = 2), marker = dict(size = 8),
        hovertemplate = "%{x}: <b>%{y:,}</b> " + unit + "<extra></extra>",
    ))

    if reference_year in values.index:
        fig.add_hline(
            y = values[reference_year],
            line = dict(color = c["reference"], width = 1, dash = "dash"),
            annotation_text = f"{reference_year} level", annotation_position = "top left",
            annotation_font_color = c["text"],
        )

    for year, (text, offset) in annotations.items():
        if year in values.index:
            fig.add_annotation(
                x = year, y = values[year], text = text,
                showarrow = True, arrowhead = 0, ax = 0, ay = offset,
                arrowcolor = c["reference"], font = dict(color = c["text"], size = 12),
            )

    fig = style(fig, "Year", y_title)
    fig.update_xaxes(range = [values.index.min() - 0.5, values.index.max() + 0.5], dtick = 2)
    return fig


# Grouped horizontal bars: share of crashes and share of deaths for each category.
# table needs the columns accidents, killed, share_accidents, share_killed.
def share_bars(table, height = 300):
    c = colors()
    table = table.sort_values("share_killed")  # Plotly draws bottom-up: largest share on top
    fig = go.Figure()
    series = [
        ("Share of crashes", "share_accidents", "accidents", "crashes", c["series"]),
        ("Share of deaths", "share_killed", "killed", "deaths", c["series2"]),
    ]
    for name, share_column, count_column, unit, color in series:
        fig.add_trace(go.Bar(
            name = name, y = table.index, x = table[share_column], orientation = "h",
            marker = dict(color = color, cornerradius = 4),
            text = table[share_column].map(lambda v: fmt(v) + "%"), textposition = "outside",
            customdata = table[count_column],
            hovertemplate = "%{y}: <b>%{x:.0f}%</b> of " + unit + " (%{customdata:,} " + unit + ")<extra></extra>",
        ))
    fig = style(fig, "Share of total (%)", None, height)
    fig.update_layout(
        barmode = "group", bargap = 0.25, bargroupgap = 0.1, hovermode = "closest",
        showlegend = True, legend = dict(orientation = "h", y = 1.12, x = 0, traceorder = "reversed"),
    )
    fig.update_xaxes(range = [0, table[["share_accidents", "share_killed"]].max().max() * 1.2], showgrid = True)
    fig.update_yaxes(rangemode = "normal")
    return fig


# Choropleth of departments. data is indexed by department code, with the columns name, accidents, killed, lethality.
def department_map(data, column, color_title, geojson, selected = None):
    c = colors()
    fig = go.Figure(go.Choropleth(
        geojson = geojson, featureidkey = "properties.code", locations = data.index, z = data[column],
        colorscale = c["scale"],
        zmin = 0, zmax = data[column].quantile(0.95),  # one extreme department shouldn't flatten the others
        marker = dict(line = dict(color = c["border"], width = 0.5)),
        colorbar = dict(title = dict(text = color_title, side = "right"), thickness = 12),
        customdata = data[["name", "accidents", "killed", "lethality"]],
        hovertemplate = (
            "<b>%{location} – %{customdata[0]}</b><br>"
            "%{customdata[1]:,} crashes · %{customdata[2]:,} deaths<br>"
            "%{customdata[3]:.1f} deaths per 100 crashes<extra></extra>"
        ),
    ))

    # Thick outline around the selected department
    if selected in data.index:
        fig.add_trace(go.Choropleth(
            geojson = geojson, featureidkey = "properties.code", locations = [selected], z = [0],
            colorscale = [[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]], showscale = False,
            marker = dict(line = dict(color = c["selection"], width = 3)), hoverinfo = "skip",
        ))

    fig.update_geos(fitbounds = "locations", visible = False, bgcolor = "rgba(0,0,0,0)")
    fig.update_layout(height = 560, margin = dict(l = 0, r = 0, t = 10, b = 0))
    return fig


# values, accidents and killed are tables of the same shape (e.g. weekdays × hours)
def heatmap(values, accidents, killed, x_title, y_title, color_title, column_suffix = ""):
    c = colors()
    fig = go.Figure(go.Heatmap(
        z = values.values, x = [f"{column}{column_suffix}" for column in values.columns], y = values.index,
        colorscale = c["scale"], zmin = 0, zmax = pd.Series(values.values.ravel()).quantile(0.95),
        xgap = 2, ygap = 2,
        colorbar = dict(title = dict(text = color_title, side = "right"), thickness = 12),
        customdata = np.dstack([accidents.values, killed.values]),
        hovertemplate = (
            "<b>%{y}, %{x}</b><br>%{customdata[0]:,} crashes · %{customdata[1]:,} deaths<br>"
            "%{z:.1f} " + color_title.lower() + "<extra></extra>"
        ),
    ))
    fig = style(fig, x_title, y_title, height = 360)
    fig.update_layout(hovermode = "closest")
    fig.update_yaxes(autorange = "reversed", rangemode = "normal")  # Monday on top
    return fig


# Single-series horizontal bars, with an optional vertical reference line (e.g. the average)
def simple_bars(values, x_title, unit, reference = None, reference_text = "", height = 300):
    c = colors()
    values = values.sort_values()
    fig = go.Figure(go.Bar(
        y = values.index, x = values.values, orientation = "h",
        marker = dict(color = c["series"], cornerradius = 4),
        text = values.map(lambda v: fmt(v, 1)), textposition = "outside",
        hovertemplate = "%{y}: <b>%{x:.1f}</b> " + unit + "<extra></extra>",
    ))
    if reference is not None:
        fig.add_vline(
            x = reference, line = dict(color = c["reference"], width = 1, dash = "dash"),
            annotation_text = reference_text, annotation_position = "top", annotation_font_color = c["text"],
        )
    fig = style(fig, x_title, None, height)
    fig.update_layout(hovermode = "closest")
    fig.update_xaxes(range = [0, values.max() * 1.2], showgrid = True)
    fig.update_yaxes(rangemode = "normal")
    return fig


# One small chart per column, each with its own y scale, to compare trends.
# table: one row per year, one column per series; titles: {column: chart title}
def small_multiples(table, titles, unit, n_cols = 3):
    c = colors()
    n_rows = -(-len(table.columns) // n_cols)  # ceiling division
    fig = make_subplots(
        rows = n_rows, cols = n_cols, subplot_titles = [titles[column] for column in table.columns],
        vertical_spacing = 0.18, horizontal_spacing = 0.07,
    )
    for i, column in enumerate(table.columns):
        fig.add_trace(
            go.Scatter(
                x = table.index, y = table[column], mode = "lines+markers",
                line = dict(color = c["series"], width = 2), marker = dict(size = 5),
                hovertemplate = column + ", %{x}: <b>%{y:,}</b> " + unit + "<extra></extra>",
            ),
            row = i // n_cols + 1, col = i % n_cols + 1,
        )
    fig.update_layout(height = 260 * n_rows, margin = dict(l = 10, r = 10, t = 40, b = 10), showlegend = False, hovermode = "closest")
    fig.update_yaxes(rangemode = "tozero")
    fig.update_xaxes(showgrid = False, dtick = 5, range = [table.index.min() - 0.5, table.index.max() + 0.5])
    fig.update_annotations(font = dict(size = 13, color = c["text"]))  # subplot titles
    return fig


# Grouped vertical bars comparing two columns (e.g. two years) for each category
def comparison_bars(table, x_title, y_title, unit, height = 380):
    c = colors()
    fig = go.Figure()
    for column, color in zip(table.columns, [c["series"], c["series2"]]):
        fig.add_trace(go.Bar(
            name = str(column), x = table.index, y = table[column],
            marker = dict(color = color, cornerradius = 4),
            text = table[column].map(fmt), textposition = "outside",
            hovertemplate = "%{x}, " + str(column) + ": <b>%{y:,}</b> " + unit + "<extra></extra>",
        ))
    fig = style(fig, x_title, y_title, height)
    fig.update_layout(
        barmode = "group", bargap = 0.25, bargroupgap = 0.1, hovermode = "closest",
        showlegend = True, legend = dict(orientation = "h", y = 1.1, x = 0),
    )
    fig.update_yaxes(range = [0, table.max().max() * 1.15])
    return fig


# Up to two lines of similar scale, with an optional dashed line before a given year (e.g. a method change)
def lines(table, y_title, unit, marked_year = None, mark_text = ""):
    c = colors()
    fig = go.Figure()
    for column, color in zip(table.columns, [c["series"], c["series2"]]):
        fig.add_trace(go.Scatter(
            name = column, x = table.index, y = table[column], mode = "lines+markers",
            line = dict(color = color, width = 2), marker = dict(size = 6),
            hovertemplate = column + ": <b>%{y:,}</b> " + unit + "<extra></extra>",
        ))
    if marked_year is not None:
        fig.add_vline(
            x = marked_year - 0.5, line = dict(color = c["reference"], width = 1, dash = "dash"),
            annotation_text = mark_text, annotation_position = "bottom left", annotation_font_color = c["text"],
        )
    fig = style(fig, "Year", y_title)
    fig.update_layout(
        showlegend = True, legend = dict(orientation = "h", y = 1.15, x = 0), hovermode = "x unified",
        margin = dict(l = 10, r = 10, t = 50, b = 10),
    )
    fig.update_xaxes(range = [table.index.min() - 0.5, table.index.max() + 0.5], dtick = 2)
    fig.update_yaxes(tickformat = ",d")  # "70,000" rather than "70k"
    return fig
