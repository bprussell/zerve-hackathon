"""
Fetch FIA ash tree estimates by county from the FIADB API.
Queries number of live trees (snum=4) by county and species for EAB-affected states.
Filters for Fraxinus (ash) species: SPCD 541, 543, 544, 545, 546, 547.
Outputs: data/raw/fia_ash_by_county.csv
"""

import csv
import json
import sys
import time
import requests

API_URL = "https://apps.fs.usda.gov/fiadb-api/fullreport"
OUTPUT_PATH = "data/raw/fia_ash_by_county.csv"

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

# Eastern US states with significant ash + EAB overlap
# State FIPS codes for key states
STATES = {
    "09": "Connecticut",
    "10": "Delaware",
    "11": "District of Columbia",
    "13": "Georgia",
    "17": "Illinois",
    "18": "Indiana",
    "19": "Iowa",
    "20": "Kansas",
    "21": "Kentucky",
    "22": "Louisiana",
    "23": "Maine",
    "24": "Maryland",
    "25": "Massachusetts",
    "26": "Michigan",
    "27": "Minnesota",
    "29": "Missouri",
    "31": "Nebraska",
    "33": "New Hampshire",
    "34": "New Jersey",
    "36": "New York",
    "37": "North Carolina",
    "39": "Ohio",
    "40": "Oklahoma",
    "42": "Pennsylvania",
    "44": "Rhode Island",
    "45": "South Carolina",
    "47": "Tennessee",
    "48": "Texas",
    "50": "Vermont",
    "51": "Virginia",
    "54": "West Virginia",
    "55": "Wisconsin",
    # Non-EAB states with PGA courses (controls)
    "01": "Alabama",
    "04": "Arizona",
    "06": "California",
    "12": "Florida",
    "15": "Hawaii",
    "28": "Mississippi",
    "32": "Nevada",
    "41": "Oregon",
    "53": "Washington",
}

# Available evaluation years vary by state. Try recent years.
EVAL_YEARS = ["2023", "2022", "2021", "2020", "2019", "2018"]


def fetch_state_data(state_fips: str, state_name: str) -> list[dict]:
    """Try each eval year until we get data for this state."""
    for year in EVAL_YEARS:
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
                continue
            data = resp.json()
            estimates = data.get("estimates", [])
            if not estimates:
                continue

            # Filter for ash species
            ash_rows = []
            for est in estimates:
                grp2 = est.get("GRP2", "")
                # GRP2 format: "`0541 SPCD 0541 - white ash (Fraxinus americana)"
                spcd = grp2.split(" ")[0].replace("`", "")
                if spcd in ASH_SPCDS:
                    # Parse county from GRP1: "`26001 26001 MI Alcona"
                    grp1 = est.get("GRP1", "")
                    parts = grp1.replace("`", "").split(" ", 2)
                    county_fips = parts[0] if parts else ""
                    # Extract county name (after state abbreviation)
                    county_name = ""
                    if len(parts) >= 3:
                        remainder = parts[2]
                        # Format: "MI Alcona" or "MI Grand Traverse"
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

            if ash_rows:
                print(f"  {state_name} ({state_fips}): {len(ash_rows)} ash records from eval {year}")
                return ash_rows
            else:
                print(f"  {state_name} ({state_fips}): no ash in eval {year}, trying older...")

        except requests.exceptions.RequestException as e:
            print(f"  {state_name} ({state_fips}): error for {year}: {e}")
            continue

    print(f"  {state_name} ({state_fips}): NO DATA FOUND across all years")
    return []


def main():
    all_rows = []
    total = len(STATES)

    for i, (fips, name) in enumerate(sorted(STATES.items()), 1):
        print(f"[{i}/{total}] Fetching {name}...")
        rows = fetch_state_data(fips, name)
        all_rows.extend(rows)
        time.sleep(0.5)  # Be polite to the API

    # Write CSV
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "state_fips", "state", "county_fips", "county", "eval_year",
            "spcd", "species", "estimate", "se", "se_percent", "plot_count",
        ])
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\nDone! {len(all_rows)} total ash records across {total} states")
    print(f"Output: {OUTPUT_PATH}")

    # Quick summary
    from collections import Counter
    species_totals = Counter()
    for r in all_rows:
        species_totals[r["species"]] += r["estimate"]
    print("\nTotal estimated ash trees by species:")
    for sp, total in species_totals.most_common():
        print(f"  {sp}: {total:,.0f}")


if __name__ == "__main__":
    main()
