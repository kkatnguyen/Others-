"""Turn Epoch AI's data center CSVs into two Tableau-ready files.

Usage:  pip install pandas zipcodes
        python scripts/prepare_data.py [AS_OF_DATE]

Reads data/raw/data_centers.csv and data/raw/data_center_timelines.csv and writes:
  data/data_centers_clean.csv   one row per data center, with map coordinates
  data/capacity_by_month.csv    one row per data center per month, ready to sum
"""
import re
import sys
from pathlib import Path

import pandas as pd
import zipcodes

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data"
AS_OF = pd.Timestamp(sys.argv[1] if len(sys.argv) > 1 else "2026-10-26")

# US sites whose address has no usable ZIP code: (city, state) to look up.
US_CITY = {
    "Google Mesa": ("Mesa", "AZ"),
    "Amazon Madison Mega Site": ("Canton", "MS"),
    "Google Kansas City East": ("Kansas City", "MO"),
    "AWS New Albany": ("New Albany", "OH"),
    "Google The Dalles": ("The Dalles", "OR"),
    "Amazon Ridgeland": ("Ridgeland", "MS"),
    "Meta Huntsville": ("Toney", "AL"),
    "Google Storey County": ("Sparks", "NV"),
    "CoreWeave Chester VA": ("Chester", "VA"),
    "Microsoft-Nebius New Jersey": ("Vineland", "NJ"),
    "Stream Phoenix": ("Goodyear", "AZ"),
    "CoreWeave Lancaster Greenfield site": ("Lancaster", "PA"),
    "OpenAI Stargate Michigan": ("Saline", "MI"),
    "OpenAI Stargate Milam": ("Cameron", "TX"),
    "OpenAI Stargate New Mexico": ("Santa Teresa", "NM"),
    "OpenAI Stargate Wisconsin": ("Port Washington", "WI"),
}

# Non-US sites: approximate city coordinates (lat, long).
WORLD_CITY = {
    "DayOne Nusajaya": ("Iskandar Puteri", 1.42, 103.63),
    "DayOne Kempas": ("Johor Bahru", 1.54, 103.71),
    "Bridge Data Centres MY06": ("Sedenak", 1.70, 103.55),
    "Google Waltham Cross": ("Cheshunt", 51.70, -0.03),
    "VNET Bayin Ulanqab": ("Ulanqab", 41.00, 113.10),
    "Huawei Horinger": ("Horinger", 40.38, 111.82),
    "Oracle Batam": ("Batam", 1.08, 104.03),
    "Huawei Wuhu": ("Wuhu", 31.35, 118.38),
    "CoreWeave Norway": ("Øvrebø", 58.27, 7.90),
    "Nebius Mantsala": ("Mäntsälä", 60.63, 25.32),
    "Southgate Melbourne": ("Melbourne", -37.81, 144.96),
    "Alibaba Zhangbei": ("Zhangbei", 41.16, 114.72),
    "Start Campus Sines Data Campus": ("Sines", 37.96, -8.87),
    "Nscale Keflavik": ("Reykjanesbær", 63.99, -22.56),
    "EcoDataCenter 2": ("Borlänge", 60.48, 15.43),
    "Envision Galaxy Ulanqab": ("Ulanqab", 41.00, 113.10),
    "Microsoft Narvik Norway": ("Narvik", 68.44, 17.43),
    "OpenAI Stargate UAE": ("Abu Dhabi", 24.45, 54.38),
}


def strip_tags(s):
    """'Anthropic #confident, Cursor #likely' -> 'Anthropic, Cursor'."""
    if pd.isna(s):
        return None
    return re.sub(r"\s*#\w+", "", s).strip()


def zip_from_address(addr):
    """Last valid 5-digit US ZIP in the address, skipping a leading street number."""
    if pd.isna(addr):
        return None
    for m in reversed(list(re.finditer(r"\b(\d{5})\b", addr))):
        if m.start() > 0 and zipcodes.is_real(m.group(1)):
            return m.group(1)
    return None


def locate(row):
    """(city, state, zip, lat, long, precision) for one data center."""
    if row["Country"] != "United States":
        if row["Name"] in WORLD_CITY:
            city, lat, lon = WORLD_CITY[row["Name"]]
            return city, None, None, lat, lon, "City (approx.)"
        return None, None, None, None, None, "Unknown"
    z = zip_from_address(row["Address"])
    if z:
        info = zipcodes.matching(z)[0]
        return info["city"], info["state"], z, float(info["lat"]), float(info["long"]), "ZIP code center"
    if row["Name"] in US_CITY:
        city, state = US_CITY[row["Name"]]
        found = [r for r in zipcodes.filter_by(city=city, state=state) if r["zip_code_type"] == "STANDARD"]
        if found:
            lat = pd.Series([float(r["lat"]) for r in found]).median()
            lon = pd.Series([float(r["long"]) for r in found]).median()
            return city, state, None, lat, lon, "City (approx.)"
    return None, None, None, None, None, "Unknown"


def main():
    dc = pd.read_csv(RAW / "data_centers.csv")
    tl = pd.read_csv(RAW / "data_center_timelines.csv", parse_dates=["Date"])
    tl = tl.sort_values(["Data center", "Date"])

    # Per-site facility power: now (latest row on/before AS_OF) and at the end of the plan.
    past = tl[tl["Date"] <= AS_OF].groupby("Data center")["Power (MW)"].last()
    final = tl.groupby("Data center").agg(planned=("Power (MW)", "last"), planned_date=("Date", "last"))

    out = pd.DataFrame({
        "Name": dc["Name"],
        "Owner": dc["Owner"].map(strip_tags).fillna("Unknown"),
        "Owner confidence": dc["Owner"].str.extract(r"#(\w+)")[0].fillna("unknown"),
        "Users": dc["Users"].map(strip_tags),
        "Country": dc["Country"],
    })
    loc = dc.apply(locate, axis=1, result_type="expand")
    loc.columns = ["City", "State", "ZIP", "Latitude", "Longitude", "Location precision"]
    out = pd.concat([out, loc], axis=1)
    out["Address"] = dc["Address"]
    out["IT power (MW)"] = dc["Current power (MW)"]
    out["Facility power (MW)"] = dc["Name"].map(past).fillna(0)
    out["H100 equivalents"] = dc["Current H100 equivalents"]
    out["Capital cost (2025 USD billions)"] = dc["Current total capital cost (2025 USD billions)"]
    out["Status"] = (out["IT power (MW)"] > 0).map({True: "Operating", False: "Not yet operating"})
    out["Planned facility power (MW)"] = dc["Name"].map(final["planned"])
    out["Planned completion"] = dc["Name"].map(final["planned_date"]).dt.date
    out["Chip types"] = dc["Current chip types"]
    out["Project"] = dc["Project"].map(strip_tags)
    out.to_csv(OUT / "data_centers_clean.csv", index=False)

    # Timeline rows are each site's running state, so carry each one forward month by month.
    months = pd.date_range(tl["Date"].min().to_period("M").to_timestamp(),
                           tl["Date"].max().to_period("M").to_timestamp(), freq="MS")
    cols = ["Power (MW)", "IT power (MW)", "H100 equivalents", "Total capital cost (2025 USD billions)"]
    # Each month shows its last day, except the current month, which stops at AS_OF.
    as_of_dates = (months + pd.offsets.MonthEnd(0)).map(lambda d: min(d, AS_OF) if d.to_period("M") == AS_OF.to_period("M") else d)
    rows = []
    for name, g in tl.groupby("Data center"):
        g = g.set_index("Date")[cols]
        state = g.reindex(g.index.union(as_of_dates)).ffill().loc[as_of_dates]
        state.index = months
        state = state.dropna(how="all")
        state["Data center"] = name
        rows.append(state)
    monthly = pd.concat(rows).rename_axis("Month").reset_index()
    monthly = monthly.rename(columns={"Power (MW)": "Facility power (MW)"})
    monthly["Period"] = (monthly["Month"] <= AS_OF).map({True: "To date", False: "Planned"})
    monthly["Month"] = monthly["Month"].dt.date
    monthly = monthly[["Data center", "Month", "Period", "Facility power (MW)", "IT power (MW)",
                       "H100 equivalents", "Total capital cost (2025 USD billions)"]]
    monthly.to_csv(OUT / "capacity_by_month.csv", index=False)

    print(f"{len(out)} data centers -> data_centers_clean.csv "
          f"({out['Latitude'].notna().sum()} with coordinates)")
    print(f"{len(monthly)} rows -> capacity_by_month.csv ({months[0].date()} to {months[-1].date()})")


if __name__ == "__main__":
    main()
