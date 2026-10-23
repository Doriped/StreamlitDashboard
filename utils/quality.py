from utils.prep import read_table


# Quality checks for one year. Duplicates are counted on the raw files, since cleaning removes them.
def check_year(year, accidents, people):
    characteristics = read_table(year, "characteristics")
    locations = read_table(year, "locations")
    vehicles = read_table(year, "vehicles")
    users = read_table(year, "users")
    metro = accidents[accidents["zone"] == "Metropolitan France"]

    checks = {"year": year}

    checks["duplicate_accidents"] = characteristics["Num_Acc"].duplicated().sum()
    checks["multiple_locations"] = locations["Num_Acc"].duplicated().sum()
    checks["duplicate_vehicles"] = vehicles.duplicated(subset = ["Num_Acc", "num_veh"]).sum()

    # Every user and vehicle must belong to an existing accident
    checks["users_without_accident"] = (~users["Num_Acc"].isin(characteristics["Num_Acc"])).sum()
    checks["vehicles_without_accident"] = (~vehicles["Num_Acc"].isin(characteristics["Num_Acc"])).sum()

    # Missing values, in %
    checks["gps_missing_pct"] = metro["lat"].isna().mean() * 100
    checks["speed_limit_missing_pct"] = accidents["speed_limit"].isna().mean() * 100
    checks["vehicle_unknown_pct"] = people["vehicle"].isna().mean() * 100
    checks["sex_unknown_pct"] = people["sex"].isna().mean() * 100
    checks["age_unknown_pct"] = people["age"].isna().mean() * 100

    # Totals shown in the dashboard's quality section
    checks["accidents"] = len(accidents)
    checks["killed_metro"] = metro["killed"].sum()
    checks["hospitalized_metro"] = metro["hospitalized"].sum()
    checks["slightly_injured_metro"] = metro["slightly_injured"].sum()
    return checks
