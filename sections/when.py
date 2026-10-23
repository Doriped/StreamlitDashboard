import streamlit as st

from utils.viz import fmt, heatmap, simple_bars

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
NIGHT_HOURS = [22, 23, 0, 1, 2, 3, 4, 5]

HEATMAP_INDICATORS = {
    "Deaths per 100 crashes": "lethality",
    "Number of crashes": "accidents",
}


def show(accidents, people):
    st.header("3. When? At night and at weekends, every crash takes a heavier toll")

    # Each death gets the hour, weekday and light conditions of its crash
    moments = accidents[["accident_id", "hour", "weekday", "light"]]
    killed = people[people["severity"] == "Killed"].merge(moments, on = "accident_id")
    if len(killed) == 0:
        st.info("No deaths in this selection: the severity of crashes by time cannot be computed.")
        return

    night_crashes = accidents["hour"].isin(NIGHT_HOURS).mean() * 100
    night_deaths = killed["hour"].isin(NIGHT_HOURS).mean() * 100
    weekend_crashes = accidents["weekday"].isin(["Saturday", "Sunday"]).mean() * 100
    weekend_deaths = killed["weekday"].isin(["Saturday", "Sunday"]).mean() * 100
    st.markdown(
        f"At night (10 pm - 6 am): **{fmt(night_crashes)}% of crashes, but {fmt(night_deaths)}% of deaths**. "
        f"At weekends: {fmt(weekend_crashes)}% of crashes, but {fmt(weekend_deaths)}% of deaths."
    )

    st.subheader("Hour and day of the week")
    choice = st.radio("Color by:", list(HEATMAP_INDICATORS), horizontal = True)
    crashes = accidents.pivot_table(index = "weekday", columns = "hour", values = "accident_id", aggfunc = "count", fill_value = 0)
    deaths = killed.pivot_table(index = "weekday", columns = "hour", values = "accident_id", aggfunc = "count", fill_value = 0)
    crashes = crashes.reindex(index = WEEKDAYS, columns = range(24), fill_value = 0)
    deaths = deaths.reindex(index = WEEKDAYS, columns = range(24), fill_value = 0)
    tables = {"accidents": crashes, "lethality": deaths / crashes.where(crashes > 0) * 100}

    st.plotly_chart(heatmap(tables[HEATMAP_INDICATORS[choice]], crashes, deaths, "Hour of the crash", None, choice, ":00"), width = "stretch")
    st.caption(
        "Heatmap: one cell per hour of each weekday (see the color scale on the right). "
        "Crashes are most frequent on weekday late afternoons, but deadliest at night, especially on weekend nights."
    )

    st.subheader("Light conditions")
    by_light = (killed.groupby("light").size() / accidents.groupby("light").size() * 100).dropna()
    average = len(killed) / len(accidents) * 100
    st.plotly_chart(
        simple_bars(by_light, "Deaths per 100 crashes", "deaths per 100 crashes",
                    reference = average, reference_text = f"Average: {fmt(average, 1)}"),
        width = "stretch",
    )
    st.caption(
        "Bars: deaths per 100 crashes by light conditions; the dashed line is the average. "
        "Note that unlit roads are mostly outside built-up areas, where speeds are higher, "
        "so lighting is not the only explanation."
    )
