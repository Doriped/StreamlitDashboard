import streamlit as st

from sections import conclusions, hook, quality, when, where, who
from utils.filters import ALL_FRANCE, ALL_MODES, apply_filters
from utils.io import SOURCE, load_checks, load_data, load_departments

st.set_page_config(page_title = "Roads of France", layout = "wide")

accidents, people = load_data()
checks = load_checks()
geojson, department_names = load_departments()


# "39 – Jura" instead of "39" in the department list
def full_name(code):
    if code == ALL_FRANCE:
        return code
    return f"{code} – {department_names[code]}"


with st.sidebar:
    st.header("Filters")
    period = st.slider("Period", min_value = 2005, max_value = 2024, value = (2005, 2024))
    departments = sorted(accidents["dep"].unique())
    department = st.selectbox("Department", [ALL_FRANCE] + departments, format_func = full_name)
    modes = sorted(people["mode"].dropna().unique())
    mode = st.selectbox("Travel mode", [ALL_MODES] + modes)

accidents_selected, people_selected = apply_filters(accidents, people, period, department, mode)

# The map needs every department, even when only one is selected
if department == ALL_FRANCE:
    accidents_france, people_france = accidents_selected, people_selected
else:
    accidents_france, people_france = apply_filters(accidents, people, period, ALL_FRANCE, mode)

st.title("Roads of France: why road deaths have not fallen in 10 years")
st.caption(SOURCE)

if len(accidents_selected) == 0:
    st.warning("No crashes match the selected filters: widen the period, the department or the travel mode.")
    st.stop()

hook.show(accidents_selected, people_selected, period)
where.show(accidents_selected, people_selected, accidents_france, people_france, department, geojson, department_names)
when.show(accidents_selected, people_selected)
who.show(accidents_selected, people_selected, period)
quality.show(checks)
conclusions.show(accidents_selected, people_selected, full_name(department), period)
