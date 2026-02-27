import pandas as pd
import re

# ── Build Track A analysis table ──
# Matches original src/build_analysis_table.py logic exactly

# Fix hist_tourneys: first column is tournamentID
hist_tourneys.columns = ["tournamentID", "year", "date", "name", "course"]

# Ensure numeric types
hist_leaders["TOT"] = pd.to_numeric(hist_leaders["TOT"], errors="coerce")
pga_modern["strokes"] = pd.to_numeric(pga_modern["strokes"], errors="coerce")
pga_modern["hole_par"] = pd.to_numeric(pga_modern["hole_par"], errors="coerce")
pga_modern["n_rounds"] = pd.to_numeric(pga_modern["n_rounds"], errors="coerce")

# Build EAB lookup
eab_by_fips = {r["fips"]: int(r["year_detected"]) for _, r in eab.iterrows()}

# --- Course name helpers (matching original logic) ---
def parse_course_location(course_str):
    """Extract course name from 'Name - City, ST' format."""
    course_str = course_str.strip().rstrip(".")
    if " - " not in course_str:
        return course_str, "", ""
    name, location = course_str.rsplit(" - ", 1)
    parts = location.split(", ")
    state = parts[-1].strip() if len(parts) >= 2 else ""
    city = ", ".join(parts[:-1]).strip()
    return name.strip(), city, state

def normalize_course_name(name):
    """Normalize course name for matching."""
    name = name.lower().strip()
    name = re.sub(r"\s*\(.*?\)\s*", " ", name)
    for suffix in ["golf club", "country club", "golf course", "cc", "gc",
                    "golf links", "golf resort", "resort", "golf trail"]:
        name = re.sub(rf"\s+{suffix}\s*$", "", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name

# Build geo lookup: normalized name -> row, AND raw course string -> row
geo_lookup = {}
for _, c in courses.iterrows():
    key = normalize_course_name(c["course_name"])
    geo_lookup[key] = c
    geo_lookup[c["course_raw"].lower().strip()] = c

# Build tournament lookup: tournamentID -> tournament row
tourn_lookup = {}
for _, t in hist_tourneys.iterrows():
    tourn_lookup[str(t["tournamentID"])] = t

# --- Process ASA/modern data (2015-2022) ---
rows = []
asa_matched = 0

for _, r in pga_modern.iterrows():
    course_raw = str(r.get("course", ""))
    name, city, state = parse_course_location(course_raw)
    norm = normalize_course_name(name)

    geo = geo_lookup.get(course_raw.lower().strip())
    if geo is None:
        geo = geo_lookup.get(norm)
    if geo is None:
        continue
    asa_matched += 1

    fips = geo["fips"]
    eab_year = eab_by_fips.get(fips)
    season = int(r["season"])
    strokes = r["strokes"]
    par = r["hole_par"]

    if pd.isna(strokes) or pd.isna(par):
        continue
    score_vs_par = int(strokes) - int(par)
    n_rounds = int(r["n_rounds"]) if not pd.isna(r["n_rounds"]) else 0

    treated = 1 if (eab_year and season >= eab_year) else 0
    eab_county = 1 if eab_year else 0

    rows.append({
        "source": "asa",
        "player": r["player"],
        "course_name": name,
        "fips": fips,
        "county": geo.get("county_name", ""),
        "year": season,
        "strokes": int(strokes),
        "par": int(par),
        "score_vs_par": score_vs_par,
        "n_rounds": n_rounds,
        "eab_county": eab_county,
        "eab_year": eab_year if eab_year else None,
        "treatment": treated,
    })

print(f"ASA: {asa_matched} rows matched")

# --- Process historical data (2009-2014 ONLY, avoid ASA overlap) ---
hist_matched = 0

for _, r in hist_leaders.iterrows():
    tid = str(r["tournamentID"])
    tourn = tourn_lookup.get(tid)
    if tourn is None:
        continue

    year = int(tourn["year"])
    if year >= 2015:
        continue  # Skip overlap with ASA data

    course_raw = str(tourn["course"]).strip().rstrip(".")
    first_course = course_raw.split(".")[0].strip()
    name, city, state = parse_course_location(first_course)
    norm = normalize_course_name(name)

    geo = geo_lookup.get(first_course.lower().strip())
    if geo is None:
        geo = geo_lookup.get(norm)
    if geo is None:
        continue
    hist_matched += 1

    fips = geo["fips"]
    eab_year = eab_by_fips.get(fips)

    tot = r["TOT"]
    if pd.isna(tot) or tot <= 0:
        continue

    # SCORE column is score relative to par (e.g., -24)
    try:
        score_vs_par = int(r["SCORE"])
        par = int(tot) - score_vs_par
    except (ValueError, TypeError):
        continue

    # Count rounds played from R1-R4
    n_rounds = sum(1 for rd in ["R1", "R2", "R3", "R4"]
                   if str(r.get(rd, "")).strip() not in ("", "nan", "None"))

    treated = 1 if (eab_year and year >= eab_year) else 0
    eab_county = 1 if eab_year else 0

    rows.append({
        "source": "historical",
        "player": r["PLAYER"],
        "course_name": name,
        "fips": fips,
        "county": geo.get("county_name", ""),
        "year": year,
        "strokes": int(tot),
        "par": par,
        "score_vs_par": score_vs_par,
        "n_rounds": n_rounds,
        "eab_county": eab_county,
        "eab_year": eab_year if eab_year else None,
        "treatment": treated,
    })

print(f"Historical: {hist_matched} rows matched")

# Build full dataframe
track_a_all = pd.DataFrame(rows)
print(f"\nAll rows: {len(track_a_all)}")

# Filter to 4-round scores (made the cut)
track_a_df = track_a_all[track_a_all["n_rounds"] == 4].copy()

print(f"After 4-round filter: {len(track_a_df)} rows")
print(f"Unique courses: {track_a_df['course_name'].nunique()}")
print(f"Unique players: {track_a_df['player'].nunique()}")
print(f"EAB treatment courses: {track_a_df[track_a_df['eab_county']==1]['course_name'].nunique()}")
print(f"Treatment obs: {track_a_df['treatment'].sum()}")
print(f"Year range: {track_a_df['year'].min()}-{track_a_df['year'].max()}")

# Clean up temp variables for R block compatibility
del rows, eab_by_fips, geo_lookup, tourn_lookup, track_a_all
del parse_course_location, normalize_course_name
del asa_matched, hist_matched
# Loop variables
del r, c, t, tid, tourn, year, course_raw, first_course
del name, city, state, norm, geo, fips, eab_year, season
del strokes, par, score_vs_par, n_rounds, treated, eab_county
del tot
