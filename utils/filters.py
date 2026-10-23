ALL_FRANCE = "Metropolitan France"
ALL_MODES = "All modes"


def apply_filters(accidents, people, period, department, mode):
    start, end = period
    accidents = accidents[accidents["year"].between(start, end)]
    people = people[people["year"].between(start, end)]

    if department == ALL_FRANCE:
        accidents = accidents[accidents["zone"] == ALL_FRANCE]
        people = people[people["zone"] == ALL_FRANCE]
    else:
        accidents = accidents[accidents["dep"] == department]
        people = people[people["dep"] == department]

    # Keeps the people of this mode, and the accidents involving at least one of them
    if mode != ALL_MODES:
        people = people[people["mode"] == mode]
        accidents = accidents[accidents["accident_id"].isin(people["accident_id"])]

    return accidents, people
