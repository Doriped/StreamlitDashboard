from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"

# Code → label tables, from the official documentation (docs/description-des-bases-de-donnees-annuelles.pdf)
AREA = {
    1: "Outside built-up area",
    2: "Built-up area",
}
LIGHT = {
    1: "Daylight",
    2: "Dusk or dawn",
    3: "Night, no street lighting",
    4: "Night, street lighting off",
    5: "Night, street lighting on",
}
WEATHER = {
    1: "Normal",
    2: "Light rain",
    3: "Heavy rain",
    4: "Snow or hail",
    5: "Fog or smoke",
    6: "Strong wind or storm",
    7: "Dazzling sun",
    8: "Overcast",
    9: "Other",
}
ROAD_TYPE = {
    1: "Motorway",
    2: "National road",
    3: "Departmental road",
    4: "Municipal road",
    5: "Off public network",
    6: "Car park",
    7: "Urban metropolitan road",
    9: "Other",
}
SURFACE = {
    1: "Normal",
    2: "Wet",
    3: "Puddles",
    4: "Flooded",
    5: "Snow-covered",
    6: "Mud",
    7: "Icy",
    8: "Oil or grease",
    9: "Other",
}
# Vehicle categories (catv) grouped into travel modes. Codes 4, 5, 6, 8, 9, 11, 12, 18 and 19 were only used
# before 2006. Codes 0 (undetermined) and -1 (not filled in) are left out and become missing values.
VEHICLE = {
    1: "Bicycle",
    80: "Bicycle",                       # e-bike
    50: "E-scooter / PMD",               # motorised personal mobility device
    60: "E-scooter / PMD",               # non-motorised personal mobility device
    2: "Motorised two-wheeler",          # moped < 50 cc
    4: "Motorised two-wheeler",          # registered scooter (before 2006)
    5: "Motorised two-wheeler",          # motorcycle (before 2006)
    6: "Motorised two-wheeler",          # sidecar (before 2006)
    30: "Motorised two-wheeler",         # scooter < 50 cc
    31: "Motorised two-wheeler",         # motorcycle 50-125 cc
    32: "Motorised two-wheeler",         # scooter 50-125 cc
    33: "Motorised two-wheeler",         # motorcycle > 125 cc
    34: "Motorised two-wheeler",         # scooter > 125 cc
    41: "Motorised two-wheeler",         # three-wheeler <= 50 cc
    42: "Motorised two-wheeler",         # three-wheeler 50-125 cc
    43: "Motorised two-wheeler",         # three-wheeler > 125 cc
    3: "Car",                            # microcar
    7: "Car",
    8: "Car",                            # car + caravan (before 2006)
    9: "Car",                            # car + trailer (before 2006)
    10: "Van",                           # light commercial vehicle 1.5-3.5 t
    11: "Van",                           # van + caravan (before 2006)
    12: "Van",                           # van + trailer (before 2006)
    13: "Heavy goods vehicle",           # 3.5-7.5 t
    14: "Heavy goods vehicle",           # > 7.5 t
    15: "Heavy goods vehicle",           # with trailer
    16: "Heavy goods vehicle",           # road tractor
    17: "Heavy goods vehicle",           # road tractor + semi-trailer
    18: "Bus, coach, tram, train",       # public transport (before 2006)
    19: "Bus, coach, tram, train",       # tram (before 2006)
    37: "Bus, coach, tram, train",       # bus
    38: "Bus, coach, tram, train",       # coach
    39: "Bus, coach, tram, train",       # train
    40: "Bus, coach, tram, train",       # tram
    20: "Other",                         # special vehicle
    21: "Other",                         # farm tractor
    35: "Other",                         # light quad
    36: "Other",                         # heavy quad
    99: "Other",
}
SEVERITY = {
    1: "Unharmed",
    2: "Killed",
    3: "Hospitalized",
    4: "Slightly injured",
}
USER_TYPE = {
    1: "Driver",
    2: "Passenger",
    3: "Pedestrian",
    4: "Pedestrian",  # pedestrian on rollers or kick scooter (code used until 2017)
}
SEX = {
    1: "Male",
    2: "Female",
}
WEEKDAYS = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}


# Reads a raw file. The separator and the encoding change across years, so both are detected.
def read_table(year, table):
    path = RAW_DIR / str(year) / f"{table}.csv"

    with open(path, encoding = "latin-1") as file:
        header = file.readline()
    if ";" in header:
        sep, decimal = ";", ","   # 2019 onwards: "47,56"
    elif "\t" in header:
        sep, decimal = "\t", "."  # characteristics 2009
    else:
        sep, decimal = ",", "."   # 2005-2018

    try:
        raw = pd.read_csv(path, sep = sep, decimal = decimal, encoding = "utf-8", low_memory = False)
    except UnicodeDecodeError:  # files before 2019 are in Latin-1
        raw = pd.read_csv(path, sep = sep, decimal = decimal, encoding = "latin-1", low_memory = False)

    # In 2022 the accident id is called "Accident_Id" instead of "Num_Acc"
    return raw.rename(columns = {"Accident_Id": "Num_Acc"})


# Returns INSEE department codes: "59", "2A", "971"
def normalize_department(dep, year):
    dep = dep.astype(str)
    if year >= 2019:
        return dep.str.zfill(2)  # 2019 lost the leading zeros ("8" for "08")

    # Before 2019: 3 digits ("590" for 59, "201"/"202" for Corsica, "971" for Guadeloupe).
    # 2009 lost the leading zeros ("10" for "010"), hence the zfill.
    dep = dep.str.zfill(3)
    result = dep.str[:2]
    result.loc[dep.str.startswith("97")] = dep
    result.loc[dep == "201"] = "2A"
    result.loc[dep == "202"] = "2B"
    return result


# One row per accident: when, where and in which conditions
def clean_characteristics(raw, year):
    clean = pd.DataFrame()
    clean["accident_id"] = raw["Num_Acc"]

    # Before 2019 the year has no century ("5" for 2005): the file's year is used instead
    clean["date"] = pd.to_datetime(pd.DataFrame({"year": year, "month": raw["mois"], "day": raw["jour"]}))
    clean["year"] = clean["date"].dt.year
    clean["weekday"] = clean["date"].dt.dayofweek.map(WEEKDAYS)

    # "07:40" from 2019, the number 740 before
    hhmm = raw["hrmn"].astype(str).str.replace(":", "").str.zfill(4)
    clean["hour"] = hhmm.str[:2].astype(int)

    clean["dep"] = normalize_department(raw["dep"], year)
    clean["zone"] = "Metropolitan France"
    clean.loc[clean["dep"].str.len() == 3, "zone"] = "Overseas"

    # Before 2019, coordinates are degrees × 100,000 and 0 means missing. "-" values (2009) become NaN.
    lat = pd.to_numeric(raw["lat"], errors = "coerce")
    lon = pd.to_numeric(raw["long"], errors = "coerce")
    if year < 2019:
        lat = lat.where(lat != 0) / 100000
        lon = lon.where(lon != 0) / 100000
    clean["lat"] = lat
    clean["lon"] = lon

    # Coordinates outside mainland France are wrong (all of them in 2009)
    in_france = clean["lat"].between(41, 51.5) & clean["lon"].between(-5.5, 10)
    clean.loc[(clean["zone"] == "Metropolitan France") & ~in_france, ["lat", "lon"]] = None

    # Unknown codes (including -1, "not filled in") become missing values
    clean["area"] = raw["agg"].map(AREA)
    clean["light"] = raw["lum"].map(LIGHT)
    clean["weather"] = raw["atm"].map(WEATHER)
    return clean


# One row per accident: the road where it happened
def clean_locations(raw):
    # An accident at a crossroads has one row per road: the first one is the main location
    raw = raw.drop_duplicates(subset = "Num_Acc", keep = "first")

    clean = pd.DataFrame()
    clean["accident_id"] = raw["Num_Acc"]
    clean["road_type"] = raw["catr"].map(ROAD_TYPE)
    clean["surface"] = raw["surf"].map(SURFACE)

    # Speed limit: only available from 2019; values outside 10-130 km/h are input errors
    if "vma" in raw.columns:
        clean["speed_limit"] = raw["vma"].where(raw["vma"].between(10, 130))
    else:
        clean["speed_limit"] = float("nan")
    return clean


# One row per vehicle
def clean_vehicles(raw):
    raw = raw.drop_duplicates(subset = ["Num_Acc", "num_veh"], keep = "first")

    clean = pd.DataFrame()
    clean["accident_id"] = raw["Num_Acc"]
    clean["vehicle_ref"] = raw["num_veh"]
    clean["vehicle"] = raw["catv"].map(VEHICLE)
    return clean


# One row per person involved
def clean_users(raw, year):
    clean = pd.DataFrame()
    clean["accident_id"] = raw["Num_Acc"]
    clean["vehicle_ref"] = raw["num_veh"]  # for a pedestrian: the vehicle that hit them
    clean["user_type"] = raw["catu"].map(USER_TYPE)
    clean["severity"] = raw["grav"].map(SEVERITY)
    clean["sex"] = raw["sexe"].map(SEX)
    clean["age"] = year - raw["an_nais"]
    return clean


# Adds each person's vehicle and travel mode
def link_users_vehicles(users, vehicles):
    result = users.merge(vehicles, on = ["accident_id", "vehicle_ref"], how = "left")
    result["mode"] = result["vehicle"]
    result.loc[result["user_type"] == "Pedestrian", "mode"] = "Pedestrian"
    return result


# One row per accident: characteristics, road, and casualty counts
def build_accidents(characteristics, locations, users):
    accidents = characteristics.merge(locations, on = "accident_id", how = "left")

    # People are counted by severity first, so that each accident stays on a single row
    counts = pd.crosstab(users["accident_id"], users["severity"])
    counts = counts.rename(columns = {
        "Killed": "killed",
        "Hospitalized": "hospitalized",
        "Slightly injured": "slightly_injured",
        "Unharmed": "unharmed",
    })
    return accidents.merge(counts.reset_index(), on = "accident_id", how = "left")


# One row per person, with the context of their accident (used by the dashboard filters)
def build_people(users_vehicles, accidents):
    context = accidents[["accident_id", "year", "dep", "zone", "area", "road_type"]]
    return users_vehicles.merge(context, on = "accident_id", how = "left")


# Cleans and joins the 4 tables of one year
def clean_year(year):
    characteristics = clean_characteristics(read_table(year, "characteristics"), year)
    locations = clean_locations(read_table(year, "locations"))
    vehicles = clean_vehicles(read_table(year, "vehicles"))
    users = clean_users(read_table(year, "users"), year)

    users_vehicles = link_users_vehicles(users, vehicles)
    accidents = build_accidents(characteristics, locations, users_vehicles)
    people = build_people(users_vehicles, accidents)
    return accidents, people
