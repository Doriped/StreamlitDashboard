import pandas as pd
import streamlit as st

from utils.filters import ALL_FRANCE
from utils.viz import department_map, fmt, share_bars

# Road types too rare to be readable on their own
SMALL_ROAD_TYPES = {"Car park": "Others", "Off public network": "Others", "Other": "Others"}

MAP_INDICATORS = {
    "Deaths per 100 crashes": "lethality",
    "Number of deaths": "killed",
}


def show(accidents, people, accidents_france, people_france, department, geojson, names):
    st.header("2. Where? A third of crashes, two thirds of deaths")
    killed = people[people["severity"] == "Killed"]

    area = shares(accidents, killed, "area")
    roads = shares(
        accidents.assign(road_type = group_roads(accidents["road_type"])),
        killed.assign(road_type = group_roads(killed["road_type"])),
        "road_type",
    )

    if len(killed) == 0:
        st.info("No deaths in this selection: the share of deaths cannot be computed.")
    elif {"Outside built-up area", "Built-up area"} <= set(area.index):
        outside, inside = area.loc["Outside built-up area"], area.loc["Built-up area"]
        sentence = (
            f"Outside built-up areas: **{fmt(outside['share_accidents'])}% of crashes, "
            f"but {fmt(outside['share_killed'])}% of deaths**."
        )
        if inside["lethality"] > 0:
            sentence += f" A crash there is on average **{fmt(outside['lethality'] / inside['lethality'], 1)} times deadlier** than in town."
        st.markdown(sentence)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Inside or outside built-up areas")
        st.plotly_chart(share_bars(area, height = 260), width = "stretch")
    with col2:
        st.subheader("By road type")
        st.plotly_chart(share_bars(roads, height = 400), width = "stretch")
    st.caption(
        "Charts: share of crashes (blue) and share of deaths (orange) for each category. "
        "When the orange bar is longer than the blue one, crashes there are deadlier than average."
    )

    # The map always shows every department, so the selected one can be compared with the others
    st.subheader("Map of departments")
    choice = st.radio("Color the map by:", list(MAP_INDICATORS), horizontal = True)

    killed_france = people_france[people_france["severity"] == "Killed"]
    by_department = shares(accidents_france, killed_france, "dep")
    by_department["name"] = by_department.index.map(names)

    st.plotly_chart(department_map(by_department, MAP_INDICATORS[choice], choice, geojson, department), width = "stretch")

    # Only departments with enough crashes are compared: 1 death in 3 crashes would mean "33 deaths per 100 crashes"
    ranking = by_department.sort_values("lethality", ascending = False)
    comparable = ranking[(ranking["accidents"] >= 50) & (ranking["killed"] > 0)]
    sentence = ""
    if len(comparable) >= 2:
        top, bottom = comparable.iloc[0], comparable.iloc[-1]
        sentence = (
            f"A crash is **{fmt(top['lethality'] / bottom['lethality'])} times deadlier** in the worst-hit department, "
            f"**{top['name']}** ({fmt(top['lethality'], 1)} deaths per 100 crashes), "
            f"than in the least affected, **{bottom['name']}** ({fmt(bottom['lethality'], 1)})."
        )
    if department != ALL_FRANCE and department in ranking.index:
        rank = list(ranking.index).index(department) + 1
        average = len(killed_france) / len(accidents_france) * 100
        sentence += (
            f" **{names[department]}**: {fmt(by_department.loc[department, 'lethality'], 1)} deaths per 100 crashes, "
            f"against {fmt(average, 1)} on average ({ordinal(rank)} deadliest of {len(ranking)} departments)."
        )
    st.markdown(sentence)
    st.caption(
        "Map: each department is colored by the selected indicator (see the color scale on the right). "
        "Hover over a department to see its figures. Over a short period or for a rare mode, "
        "small departments have few crashes and their figures vary a lot."
    )


# On a category column, .map only transforms the list of categories, not every row
def group_roads(road_types):
    return road_types.map(lambda road_type: SMALL_ROAD_TYPES.get(road_type, road_type))


# For each category: crashes, deaths, their share of the total (%) and the lethality
def shares(accidents, killed, column):
    table = pd.DataFrame({
        "accidents": accidents.groupby(column).size(),
        "killed": killed.groupby(column).size(),
    }).fillna(0)
    table["share_accidents"] = table["accidents"] / table["accidents"].sum() * 100
    table["share_killed"] = (table["killed"] / table["killed"].sum() * 100).fillna(0)  # 0 when there are no deaths
    table["lethality"] = table["killed"] / table["accidents"] * 100
    return table


# 1 → "1st", 2 → "2nd", 11 → "11th", 23 → "23rd"
def ordinal(n):
    suffix = "th" if 11 <= n % 100 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"
