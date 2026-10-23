import streamlit as st

from utils.viz import fmt

NIGHT_HOURS = [22, 23, 0, 1, 2, 3, 4, 5]
VULNERABLE_USERS = ["Pedestrian", "Bicycle", "E-scooter / PMD", "Motorised two-wheeler"]


def show(accidents, people, territory, period):
    st.header("6. Conclusions and possible actions")
    killed = people[people["severity"] == "Killed"]
    if len(killed) == 0:
        st.warning("No deaths match the selected filters.")
        return

    start, end = period
    hours = accidents[["accident_id", "hour"]]
    night_deaths = killed.merge(hours, on = "accident_id")["hour"].isin(NIGHT_HOURS).mean() * 100
    night_crashes = accidents["hour"].isin(NIGHT_HOURS).mean() * 100
    outside_towns = (killed["area"] == "Outside built-up area").mean() * 100
    departmental = (killed["road_type"] == "Departmental road").mean() * 100
    vulnerable = {year: killed.loc[killed["year"] == year, "mode"].isin(VULNERABLE_USERS).mean() * 100 for year in [start, end]}

    st.markdown(f"**Key findings** ({territory}, {start}-{end}):")
    col1, col2, col3 = st.columns(3)
    with col1.container(border = True):
        st.markdown(
            f"**1. The danger is outside towns.**\n\n"
            f"{fmt(outside_towns)}% of deaths happen outside built-up areas, and {fmt(departmental)}% on departmental roads."
        )
    with col2.container(border = True):
        st.markdown(
            f"**2. Nights weigh heavily.**\n\n"
            f"{fmt(night_deaths)}% of deaths happen between 10 pm and 6 am, while only {fmt(night_crashes)}% of crashes do."
        )
    if killed["year"].eq(end).any():
        vulnerable_text = f"In {end}, {fmt(vulnerable[end])}% of those killed were on foot, on a bicycle, an e-scooter or a motorised two-wheeler"
        if start < end and killed["year"].eq(start).any():
            vulnerable_text += f", against {fmt(vulnerable[start])}% in {start}"
    else:
        vulnerable_text = f"No deaths in {end} in this selection"
    with col3.container(border = True):
        st.markdown(f"**3. Vulnerable road users remain exposed.**\n\n{vulnerable_text}.")

    st.subheader("Possible actions for local decision-makers")
    st.markdown(
        "This data shows **where and when** people die on the roads, not **why**: the actions below are leads to study "
        "case by case, not solutions proven by this analysis."
    )
    st.markdown(
        "- **Departmental roads**: identify the sections where fatal crashes concentrate, then study road layout changes "
        "(separating traffic, treating roadside obstacles, junctions) and speed enforcement.\n"
        "- **Nights and weekends**: target checks (speed, alcohol, drugs) and prevention at these times, "
        "and study lighting at the junctions with the most crashes.\n"
        "- **Vulnerable users**: build cycle lanes separated from traffic, make pedestrian crossings safer and lower speeds "
        "in towns; support older people's mobility."
    )

    st.subheader("Going further")
    st.markdown(
        "- **Relate to population** (INSEE) to measure the risk per inhabitant, not just per crash.\n"
        "- **Relate to traffic** (kilometres travelled) to know whether the rise in cyclist deaths comes from a higher risk "
        "or simply from more cyclists.\n"
        "- **Evaluate local measures**, for example before and after the switch to 80 km/h, or the return to 90 km/h "
        "decided by some departments."
    )
    st.success(
        "In short, in metropolitan France: after a sharp fall between 2005 and 2013, road deaths have stalled. "
        "The room for improvement lies on rural roads, at night, and among vulnerable road users."
    )
