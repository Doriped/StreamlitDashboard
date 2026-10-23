import pandas as pd
import streamlit as st

from utils.viz import fmt, yearly_line

# (label, vertical offset of the label in px)
EVENTS = {
    2013: ("Start of the plateau", -40),
    2018: ("80 km/h on secondary roads", -85),
    2020: ("Lockdowns", 40),
}


def show(accidents, people, period):
    st.header("1. Road crashes still kill nearly 9 people a day")
    start, end = period
    years = range(start, end + 1)

    killed = people[people["severity"] == "Killed"].groupby("year").size().reindex(years, fill_value = 0)
    crashes = accidents.groupby("year").size().reindex(years, fill_value = 0)

    days = pd.Timestamp(end, 12, 31).dayofyear  # 365 or 366
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        f"Deaths in {end}", fmt(killed[end]),
        delta = change(killed[start], killed[end], start), delta_color = "inverse",
        help = "People killed on the spot or within 30 days of the crash.",
    )
    col2.metric(f"Deaths per day in {end}", fmt(killed[end] / days, 1))
    col3.metric(
        f"Crashes in {end}", fmt(crashes[end]),
        delta = change(crashes[start], crashes[end], start), delta_color = "inverse",
        help = "Crashes with at least one casualty needing care, recorded by the police.",
    )
    col4.metric(
        f"Deaths / 100 crashes ({start}-{end})", fmt(killed.sum() / crashes.sum() * 100, 1),
        help = "Lethality: number of deaths per 100 injury crashes. It measures how severe crashes are.",
    )

    sentence = f"Between {start} and {end}, road deaths went from **{fmt(killed[start])}** to **{fmt(killed[end])}**."
    if start < 2013 < end:
        sentence += f" But they have barely fallen since 2013: {fmt(killed[2013])} in 2013, {fmt(killed[end])} in {end}."
    st.markdown(sentence)

    st.subheader("Road deaths per year")
    st.plotly_chart(yearly_line(killed, "Deaths", "deaths", EVENTS, reference_year = 2013), width = "stretch")
    st.caption(
        f"Chart: number of people killed each year from {start} to {end}. "
        "The dashed line marks the 2013 level; 2020 is an exception due to the lockdowns."
    )


# e.g. "-40% since 2005"
def change(before, after, year_before):
    if before == 0:
        return None
    return f"{fmt((after / before - 1) * 100)}% since {year_before}"
