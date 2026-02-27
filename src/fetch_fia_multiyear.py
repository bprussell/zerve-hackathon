"""
Fetch multi-year FIA ash data for EAB-impacted states.

Queries the FIADB API across multiple evaluation years per state
to capture ash population decline over time. Used to calibrate
mortality curves for the extinction projection model.

Focus states: those with longest EAB exposure (MI since 2002).
Year range: 2005-2023 (covering pre/post EAB for many states).

Output: data/raw/fia_ash_multiyear.csv
"""

import csv
import json
import time
import requests

API_URL = "https://apps.fs.usda.gov/fiadb-api/fullreport"
OUTPUT_PATH = "data/raw/fia_ash_multiyear.csv"

# Ash species codes
ASH_SPCDS = {"0541", "0543", "0544", "0545", "0546", "0547"}
ASH_NAMES = {
    "0541": "white ash",
    "0543": "black ash",
    "0544": "green ash",
    "0545": "pumpkin ash",
    "0546": "blue ash",
    "0547": "velvet ash",
}

# States with significant EAB history (earliest detection year)
# Focus on states where EAB has been present 10+ years for measurable decline
STATES = {
    "26": ("Michigan", 2002),
    "39": ("Ohio", 2003),
    "18": ("Indiana", 2004),
    "17": ("Illinois", 2006),
    "24": ("Maryland", 2006),
    "42": ("Pennsylvania", 2007),
    "55": ("Wisconsin", 2008),
    "51": ("Virginia", 2008),
    "36": ("New York", 2009),
    "21": ("Kentucky", 2009),
    "27": ("Minnesota", 2009),
    "47": ("Tennessee", 2010),
    "25": ("Massachusetts", 2012),
    "09": ("Connecticut", 2012),
    "19": ("Iowa", 2010),
    "29": ("Missouri", 2008),
}

# Query these eval years for each state
EVAL_YEARS = list(range(2005, 2024))


def fetch_state_year(state_fips, state_name, year):
    """Fetch ash data for one state and one eval year."""
    wc = f"{state_fips}{year}"
    params = {
        "reptype": "State",
        "snum": "4",  # Number of live trees
        "wc": wc,
        "rselected": "County code and name",
        "cselected": "Species",
        "outputFormat": "NJSON",
        "pselected": "None",
    }
    try:
        resp = requests.get(API_URL, params=params, timeout=120)
        if resp.status_code != 200:
            return []
        data = resp.json()
        estimates = data.get("estimates", [])
        if not estimates:
            return []

        ash_rows = []
        for est in estimates:
            grp2 = est.get("GRP2", "")
            spcd = grp2.split(" ")[0].replace("`", "")
            if spcd not in ASH_SPCDS:
                continue

            grp1 = est.get("GRP1", "")
            parts = grp1.replace("`", "").split(" ", 2)
            county_fips = parts[0] if parts else ""
            county_name = ""
            if len(parts) >= 3:
                remainder = parts[2]
                name_parts = remainder.split(" ", 1)
                county_name = name_parts[1] if len(name_parts) > 1 else ""

            ash_rows.append({
                "state_fips": state_fips,
                "state": state_name,
                "county_fips": county_fips,
                "county": county_name,
                "eval_year": year,
                "spcd": spcd,
                "species": ASH_NAMES.get(spcd, "unknown ash"),
                "estimate": est.get("ESTIMATE", 0),
                "se": est.get("SE", 0),
                "se_percent": est.get("SE_PERCENT", 0),
                "plot_count": est.get("PLOT_COUNT", 0),
            })

        return ash_rows

    except requests.exceptions.RequestException:
        return []


def main():
    all_rows = []
    total_states = len(STATES)
    years_with_data = set()

    for si, (fips, (name, eab_year)) in enumerate(sorted(STATES.items()), 1):
        state_years_found = []
        for year in EVAL_YEARS:
            print(f"[{si}/{total_states}] {name} eval {year}...", end=" ", flush=True)
            rows = fetch_state_year(fips, name, year)
            if rows:
                all_rows.extend(rows)
                state_years_found.append(year)
                years_with_data.add((fips, year))
                print(f"{len(rows)} records")
            else:
                print("no data")
            time.sleep(0.5)

        if state_years_found:
            print(f"  {name}: data for eval years {state_years_found}")
        else:
            print(f"  {name}: NO DATA across any year")
        print()

    # Write CSV
    fieldnames = [
        "state_fips", "state", "county_fips", "county", "eval_year",
        "spcd", "species", "estimate", "se", "se_percent", "plot_count",
    ]
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\nDone! {len(all_rows)} total records")
    print(f"State-year combinations with data: {len(years_with_data)}")
    print(f"Output: {OUTPUT_PATH}")

    # Summary: total ash by state and year
    from collections import defaultdict
    totals = defaultdict(lambda: defaultdict(float))
    for r in all_rows:
        totals[r["state"]][r["eval_year"]] += r["estimate"]

    print("\nTotal ash trees by state and eval year:")
    for state in sorted(totals.keys()):
        years = sorted(totals[state].keys())
        vals = [f"{y}: {totals[state][y]:,.0f}" for y in years]
        print(f"  {state}: {' | '.join(vals)}")


if __name__ == "__main__":
    main()
