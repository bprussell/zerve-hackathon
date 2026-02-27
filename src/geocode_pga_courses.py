"""
Geocode PGA Tour courses to FIPS county codes.
Uses Nominatim (OpenStreetMap) for lat/lon, then FCC API for FIPS lookup.
Outputs: data/processed/pga_courses_geocoded.csv
"""

import csv
import json
import os
import time
import requests

PGA_PATH = "data/raw/ASA All PGA Raw Data - Tourn Level.csv"
OUTPUT_PATH = "data/processed/pga_courses_geocoded.csv"

US_STATES = {
    'AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN',
    'IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV',
    'NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN',
    'TX','UT','VT','VA','WA','WV','WI','WY','DC',
}

STATE_ABBREV_TO_FULL = {
    'AL':'Alabama','AK':'Alaska','AZ':'Arizona','AR':'Arkansas','CA':'California',
    'CO':'Colorado','CT':'Connecticut','DE':'Delaware','DC':'District of Columbia',
    'FL':'Florida','GA':'Georgia','HI':'Hawaii','ID':'Idaho','IL':'Illinois',
    'IN':'Indiana','IA':'Iowa','KS':'Kansas','KY':'Kentucky','LA':'Louisiana',
    'ME':'Maine','MD':'Maryland','MA':'Massachusetts','MI':'Michigan','MN':'Minnesota',
    'MS':'Mississippi','MO':'Missouri','MT':'Montana','NE':'Nebraska','NV':'Nevada',
    'NH':'New Hampshire','NJ':'New Jersey','NM':'New Mexico','NY':'New York',
    'NC':'North Carolina','ND':'North Dakota','OH':'Ohio','OK':'Oklahoma',
    'OR':'Oregon','PA':'Pennsylvania','RI':'Rhode Island','SC':'South Carolina',
    'SD':'South Dakota','TN':'Tennessee','TX':'Texas','UT':'Utah','VT':'Vermont',
    'VA':'Virginia','WA':'Washington','WV':'West Virginia','WI':'Wisconsin','WY':'Wyoming',
}

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
FCC_URL = "https://geo.fcc.gov/api/census/area"
HEADERS = {"User-Agent": "ash-borer-project/1.0 (hackathon research)"}


def extract_us_courses(pga_path: str) -> list[dict]:
    """Parse unique US courses from PGA data."""
    with open(pga_path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    seen = set()
    courses = []
    for r in rows:
        course_raw = r.get("course", "")
        if course_raw in seen or " - " not in course_raw:
            continue
        seen.add(course_raw)

        name, location = course_raw.rsplit(" - ", 1)
        parts = location.split(", ")
        state_abbr = parts[-1].strip()
        city = ", ".join(parts[:-1]).strip()

        if state_abbr in US_STATES:
            courses.append({
                "course_raw": course_raw,
                "course_name": name.strip(),
                "city": city,
                "state_abbr": state_abbr,
                "state": STATE_ABBREV_TO_FULL.get(state_abbr, state_abbr),
            })
    return courses


def geocode_nominatim(city: str, state: str) -> tuple[float, float] | None:
    """Get lat/lon for a city, state using Nominatim."""
    query = f"{city}, {state}, USA"
    try:
        resp = requests.get(NOMINATIM_URL, params={
            "q": query, "format": "json", "limit": 1,
        }, headers=HEADERS, timeout=15)
        results = resp.json()
        if results:
            return float(results[0]["lat"]), float(results[0]["lon"])
    except Exception as e:
        print(f"    Nominatim error for '{query}': {e}")
    return None


def fips_from_latlon(lat: float, lon: float) -> dict | None:
    """Get FIPS county from lat/lon using FCC API."""
    try:
        resp = requests.get(FCC_URL, params={
            "lat": lat, "lon": lon, "format": "json",
        }, timeout=15)
        data = resp.json()
        if data.get("results"):
            r = data["results"][0]
            return {
                "fips": r.get("county_fips", ""),
                "county_name": r.get("county_name", ""),
                "state_fips": r.get("state_fips", ""),
            }
    except Exception as e:
        print(f"    FCC error for ({lat}, {lon}): {e}")
    return None


def main():
    os.makedirs("data/processed", exist_ok=True)

    courses = extract_us_courses(PGA_PATH)
    print(f"Found {len(courses)} unique US courses to geocode\n")

    results = []
    failed = []

    for i, c in enumerate(courses, 1):
        label = f"{c['city']}, {c['state_abbr']}"
        print(f"[{i}/{len(courses)}] {c['course_name']} ({label})")

        # Step 1: Get lat/lon
        coords = geocode_nominatim(c["city"], c["state"])
        if not coords:
            print(f"  FAILED: no coordinates")
            failed.append(c)
            time.sleep(1.1)  # Nominatim rate limit: 1 req/sec
            continue

        lat, lon = coords
        time.sleep(1.1)  # Nominatim rate limit

        # Step 2: Get FIPS
        fips_info = fips_from_latlon(lat, lon)
        if not fips_info:
            print(f"  FAILED: no FIPS for ({lat}, {lon})")
            failed.append(c)
            continue

        print(f"  -> {fips_info['county_name']} (FIPS {fips_info['fips']})")
        results.append({
            "course_raw": c["course_raw"],
            "course_name": c["course_name"],
            "city": c["city"],
            "state_abbr": c["state_abbr"],
            "state": c["state"],
            "lat": lat,
            "lon": lon,
            "fips": fips_info["fips"],
            "county_name": fips_info["county_name"],
            "state_fips": fips_info["state_fips"],
        })

    # Write results
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "course_raw", "course_name", "city", "state_abbr", "state",
            "lat", "lon", "fips", "county_name", "state_fips",
        ])
        writer.writeheader()
        writer.writerows(results)

    print(f"\nDone! {len(results)} courses geocoded, {len(failed)} failed")
    print(f"Output: {OUTPUT_PATH}")

    if failed:
        print(f"\nFailed courses:")
        for c in failed:
            print(f"  {c['course_name']} - {c['city']}, {c['state_abbr']}")


if __name__ == "__main__":
    main()
