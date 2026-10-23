import pandas as pd
import streamlit as st

from utils.viz import comparison_bars, fmt, small_multiples

# Modes shown as small multiples, from deadliest to least deadly (the others are too rare)
MODES = ["Car", "Motorised two-wheeler", "Pedestrian", "Bicycle", "Van", "E-scooter / PMD"]

# Vans: 56 deaths in 2005 then 120 in 2006, probably due to the 2006 change in vehicle codes.
# Their trend is not shown when the period starts in 2005.
BREAK_IN_2005 = ["Van"]

# ONISR age groups, to allow comparison with its reports
AGE_BINS = [0, 14, 18, 25, 35, 65, 75, 120]
AGE_GROUPS = ["0-13", "14-17", "18-24", "25-34", "35-64", "65-74", "75+"]


def show(accidents, people, period):
    st.header("4. Who? Car occupants gained the most; cyclists and older people were left behind")
    start, end = period
    killed = people[people["severity"] == "Killed"]
    if len(killed) == 0:
        st.warning("No deaths match the selected filters.")
        return

    by_mode = killed.pivot_table(index = "year", columns = "mode", values = "accident_id", aggfunc = "count", fill_value = 0)
    modes = [mode for mode in MODES if mode in by_mode.columns]
    if not modes:  # a rare mode is selected (HGV, bus...): show that one
        modes = list(by_mode.columns)
    by_mode = by_mode.reindex(index = range(start, end + 1), columns = modes, fill_value = 0)

    killed = killed.assign(age_group = pd.cut(killed["age"], bins = AGE_BINS, labels = AGE_GROUPS, right = False))
    years = sorted({start, end})
    by_age = pd.crosstab(killed["age_group"], killed["year"]).reindex(index = AGE_GROUPS, columns = years, fill_value = 0)

    sentences = []
    comparable = [mode for mode in ["Car", "Bicycle"] if mode in by_mode.columns and by_mode[mode].iloc[0] > 0]
    if start < end and comparable:
        trends = [f"{mode.lower()} **{signed(trend(by_mode[mode]))}**" for mode in comparable]
        sentences.append(f"Change in deaths between {start} and {end}: " + ", ".join(trends) + ".")
    over_65 = by_age.loc[["65-74", "75+"]].sum() / by_age.sum() * 100
    if start < end and (by_age.sum() > 0).all():  # needs deaths with a known age in both years
        sentences.append(f"People aged 65 and over make up **{fmt(over_65[end])}% of deaths in {end}**, against {fmt(over_65[start])}% in {start}.")
    men = (killed["sex"] == "Male").sum() / killed["sex"].notna().sum() * 100
    sentences.append(f"**{fmt(men)}% of those killed are men.**")
    st.markdown(" ".join(sentences))

    st.subheader("Deaths by travel mode")
    titles = {mode: mode_title(mode, by_mode[mode]) for mode in by_mode.columns}
    st.plotly_chart(small_multiples(by_mode, titles, "deaths"), width = "stretch")
    st.caption(
        "Small multiples: one chart per travel mode, each with its own vertical scale, to compare trends. "
        "The \"E-scooter / PMD\" (personal mobility device) category only exists since 2019; before that, "
        "these users were counted as pedestrians. Vans: 56 deaths in 2005 then 120 in 2006, probably due to the "
        "2006 change in vehicle codes, so the trend since 2005 is not reliable. Without data on distances travelled, "
        "more deaths do not prove that each trip is riskier (there may simply be more cyclists)."
    )

    st.subheader("Deaths by age group")
    st.plotly_chart(comparison_bars(by_age, "Age group", "Deaths", "deaths"), width = "stretch")
    st.caption(
        "Bars: deaths by age group in the first and last year of the period. Age is accurate to one year "
        "(only the year of birth is known). The population is ageing, which partly explains the higher share of older people."
    )


# Change in % between the first and last values
def trend(series):
    return (series.iloc[-1] / series.iloc[0] - 1) * 100


# 24 → "+24%", -50 → "-50%"
def signed(percent):
    text = fmt(percent) + "%"
    return text if percent < 0 else "+" + text


def mode_title(mode, series):
    if len(series) < 2 or series.iloc[0] == 0:
        return mode
    if mode in BREAK_IN_2005 and series.index[0] == 2005:
        return mode + " (see note)"
    return f"{mode} ({signed(trend(series))})"
