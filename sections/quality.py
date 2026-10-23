import streamlit as st

from utils.viz import fmt, lines, yearly_line

# ONISR official figure for 2024 ("Chiffres clés 2024", final results, 28 May 2025)
ONISR_2024_DEATHS = 3193
ONISR_2024_URL = (
    "https://www.onisr.securite-routiere.gouv.fr/etat-de-linsecurite-routiere/"
    "bilans-annuels-de-la-securite-routiere/bilan-2024-de-la-securite-routiere"
)


# Not affected by the filters: data quality concerns the whole database
def show(checks):
    st.header("5. Data quality and limitations")
    st.markdown(
        "The data comes from the **injury accident reports (BAAC)** filled in by the police for every crash "
        "with at least one casualty. It is a raw database: here are the checks, the fixes and the limitations to keep in mind."
    )

    checks = checks.set_index("year")
    deaths_2024 = checks.loc[2024, "killed_metro"]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Duplicate crashes", fmt(checks["duplicate_accidents"].sum()),
                help = "Crash ids appearing twice in the same file, over the 20 years.")
    col2.metric("Orphan people or vehicles", fmt(checks["users_without_accident"].sum() + checks["vehicles_without_accident"].sum()),
                help = "People or vehicles linked to a crash that does not exist: a consistency check between the tables.")
    col3.metric("Duplicate vehicles (fixed)", fmt(checks["duplicate_vehicles"].sum()),
                help = "Two vehicles of the same crash with the same letter: only the first one is kept.")
    col4.metric("2024 deaths: gap with ONISR", fmt(deaths_2024 - ONISR_2024_DEATHS),
                help = f"Our data: {fmt(deaths_2024)} deaths in metropolitan France in 2024. ONISR official figure: {fmt(ONISR_2024_DEATHS)}.")
    st.markdown(
        f"**Validation:** our data gives {fmt(deaths_2024)} deaths in metropolitan France in 2024, exactly the "
        f"[ONISR official figure]({ONISR_2024_URL}). The breakdowns by travel mode and by sex also match the published figures."
    )

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Share of geolocated crashes")
        gps = (100 - checks["gps_missing_pct"]).round(1)
        st.plotly_chart(yearly_line(gps, "Geolocated crashes (%)", "%", {2009: ("2009: 0%", -60)}), width = "stretch")
        st.caption(
            "Line: share of crashes in metropolitan France with valid GPS coordinates (none in 2009). "
            "A map of individual crashes is only possible from 2018; the department is known for all of them."
        )
    with col2:
        st.subheader("The 2018 break in injury figures")
        injured = checks[["hospitalized_metro", "slightly_injured_metro"]]
        injured.columns = ["Hospitalized", "Slightly injured"]
        st.plotly_chart(lines(injured, "Injured people", "injured", marked_year = 2018, mark_text = "Method change"), width = "stretch")
        st.caption(
            "Lines: hospitalized and slightly injured people per year. In 2018 the first fall by 23% while the second rise: "
            "this is a change in how police record injuries, not an improvement. That is why this dashboard compares years using deaths."
        )

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Fixes applied")
        st.markdown(
            "- **Different file formats before 2019**: separator, character encoding, year without century (`5` for 2005), "
            "hour as a number (`740`), 3-digit department codes (`590`), GPS coordinates multiplied by 100,000.\n"
            "- **Lost leading zeros in department codes** in 2009 (`10` for `010`, Ain) and 2019 (`8` for `08`, Ardennes): "
            "without the fix, thousands of crashes moved to the wrong department.\n"
            "- **Impossible GPS coordinates** (outside mainland France) removed.\n"
            "- **Absurd speed limits** (0, 500, 900 km/h) set to unknown.\n"
            "- **Several locations for one crash** (since 2023): only the main one is kept.\n"
            "- **40 vehicle categories** grouped into 8 travel modes, checked against ONISR figures."
        )
    with col2:
        st.subheader("Limitations")
        st.markdown(
            "- **No exposure data**: without traffic, distances travelled or population, we compare counts and severity rates, "
            "not a risk per kilometre or per inhabitant.\n"
            "- **Correlation is not causation**: night crashes are more severe, but night is not necessarily the cause.\n"
            "- **Unreported crashes**: the police are not always called for minor crashes; death counts are reliable, crash counts less so.\n"
            "- **Categories added over time**: e-scooters (2019), urban metropolitan roads, speed limit (2019).\n"
            "- **Age accurate to one year**: only the year of birth is known.\n"
            "- **Hit-and-run drivers** (since 2021): about 2% of people involved, with unknown sex and age.\n"
            "- **Privacy**: only aggregated figures are shown; ONISR publishes vehicle makes and models separately, with no possible link."
        )
