"""
Fetch EAB county-level detection data from ArcGIS feature service.
Outputs: data/raw/eab_detections_by_county.csv
"""

import csv
import json
import urllib.request
import urllib.parse

SERVICE_URL = (
    "https://services1.arcgis.com/eZaevkfA0RPFQmA8/arcgis/rest/services/"
    "US_CA_wEAB_2017/FeatureServer/0/query"
)
OUT_FIELDS = "FIPS,STATE_NAME,COUNTY_NAM,STATE_FIPS,CNTY_FIPS,YearDetec2,PRNAME"
PAGE_SIZE = 1000
OUTPUT_PATH = "data/raw/eab_detections_by_county.csv"


def fetch_page(offset: int) -> list[dict]:
    params = urllib.parse.urlencode({
        "where": "1=1",
        "outFields": OUT_FIELDS,
        "returnGeometry": "false",
        "resultOffset": offset,
        "resultRecordCount": PAGE_SIZE,
        "f": "json",
    })
    url = f"{SERVICE_URL}?{params}"
    with urllib.request.urlopen(url) as resp:
        data = json.loads(resp.read())
    return [f["attributes"] for f in data.get("features", [])]


def main():
    all_records = []
    offset = 0
    while True:
        page = fetch_page(offset)
        if not page:
            break
        all_records.extend(page)
        print(f"  Fetched {len(all_records)} records so far...")
        offset += PAGE_SIZE

    # Separate US and Canada records
    us_records = []
    ca_records = []
    for r in all_records:
        # Canadian records have PRNAME set (province name), US ones are blank/space
        if r.get("PRNAME", "").strip():
            ca_records.append(r)
        else:
            us_records.append(r)

    # Write US records (have FIPS codes)
    us_records.sort(key=lambda r: (r.get("YearDetec2") or 9999, r.get("FIPS") or ""))
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["fips", "state_fips", "county_fips", "state", "county", "year_detected"])
        for r in us_records:
            writer.writerow([
                r.get("FIPS", ""),
                r.get("STATE_FIPS", ""),
                r.get("CNTY_FIPS", ""),
                r.get("STATE_NAME", "").strip(),
                r.get("COUNTY_NAM", "").strip(),
                r.get("YearDetec2", ""),
            ])

    # Write Canada records separately
    ca_output = OUTPUT_PATH.replace(".csv", "_canada.csv")
    ca_records.sort(key=lambda r: (r.get("YearDetec2") or 9999, r.get("PRNAME") or ""))
    with open(ca_output, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["province", "county", "year_detected"])
        for r in ca_records:
            writer.writerow([
                r.get("PRNAME", "").strip(),
                r.get("COUNTY_NAM", "").strip(),
                r.get("YearDetec2", ""),
            ])

    print(f"\nDone! {len(us_records)} US counties -> {OUTPUT_PATH}")
    print(f"      {len(ca_records)} Canada regions -> {ca_output}")


if __name__ == "__main__":
    main()
