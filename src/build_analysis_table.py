"""
Build unified analysis table for Track A DiD.
Merges ASA (2015-2022) and historical (2009-2014) PGA data,
joins with EAB detection dates and course geocoding.
Outputs: data/processed/track_a_analysis.csv
"""

import csv
import os
import re


def load_csv(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def parse_course_location(course_str):
    """Extract course name, city, state from 'Name - City, ST' or 'Name (detail) - City, ST.'"""
    course_str = course_str.strip().rstrip(".")
    if " - " not in course_str:
        return course_str, "", ""
    name, location = course_str.rsplit(" - ", 1)
    parts = location.split(", ")
    state = parts[-1].strip() if len(parts) >= 2 else ""
    city = ", ".join(parts[:-1]).strip()
    return name.strip(), city, state


def normalize_course_name(name):
    """Normalize course name for matching between datasets."""
    name = name.lower().strip()
    # Remove parenthetical details like "(Stadium Course)", "(Plantation Course)"
    name = re.sub(r"\s*\(.*?\)\s*", " ", name)
    # Remove common suffixes
    for suffix in ["golf club", "country club", "golf course", "cc", "gc", "golf links",
                   "golf resort", "resort", "golf trail"]:
        name = re.sub(rf"\s+{suffix}\s*$", "", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


def main():
    os.makedirs("data/processed", exist_ok=True)

    # Load source data
    asa = load_csv("data/raw/ASA All PGA Raw Data - Tourn Level.csv")
    hist_lb = load_csv("data/raw/pga_historical/Full_Leaderboard_Table.csv")
    hist_tourn = load_csv("data/raw/pga_historical/Full_Tournament_Table.csv")
    courses_geo = load_csv("data/processed/pga_courses_geocoded.csv")
    eab = load_csv("data/raw/eab_detections_by_county.csv")

    # Build EAB lookup: FIPS -> year_detected
    eab_by_fips = {r["fips"]: int(r["year_detected"]) for r in eab}

    # Build course geocoding lookup: normalized name -> geo info
    geo_lookup = {}
    for c in courses_geo:
        key = normalize_course_name(c["course_name"])
        geo_lookup[key] = c
        # Also index by raw course string
        geo_lookup[c["course_raw"].lower().strip()] = c

    # Build tournament lookup for historical data
    tourn_lookup = {}
    for t in hist_tourn:
        tid = t.get("", "")
        tourn_lookup[tid] = t

    # --- Process ASA data (2015-2022) ---
    rows = []
    asa_matched = 0
    asa_unmatched = set()

    for r in asa:
        course_raw = r.get("course", "")
        name, city, state = parse_course_location(course_raw)
        norm = normalize_course_name(name)

        # Look up geocoding
        geo = geo_lookup.get(course_raw.lower().strip()) or geo_lookup.get(norm)
        if not geo:
            asa_unmatched.add(course_raw)
            continue
        asa_matched += 1

        fips = geo["fips"]
        eab_year = eab_by_fips.get(fips)

        season = int(r.get("season", 0))
        strokes = r.get("strokes", "")
        par = r.get("hole_par", "")

        if not strokes or not par:
            continue

        try:
            score_vs_par = int(strokes) - int(par)
        except ValueError:
            continue

        treated = 1 if (eab_year and season >= eab_year) else 0
        post = 1 if (eab_year and season >= eab_year) else 0
        eab_county = 1 if eab_year else 0

        rows.append({
            "source": "asa",
            "player": r.get("player", ""),
            "course_name": name,
            "course_raw": course_raw,
            "city": city,
            "state": state,
            "fips": fips,
            "county": geo.get("county_name", ""),
            "year": season,
            "strokes": strokes,
            "par": par,
            "score_vs_par": score_vs_par,
            "n_rounds": r.get("n_rounds", ""),
            "sg_total": r.get("sg_total", ""),
            "sg_ott": r.get("sg_ott", ""),
            "sg_app": r.get("sg_app", ""),
            "sg_arg": r.get("sg_arg", ""),
            "sg_putt": r.get("sg_putt", ""),
            "eab_county": eab_county,
            "eab_year": eab_year or "",
            "post_eab": post,
            "treatment": treated,
        })

    print(f"ASA: {asa_matched} rows matched, {len(asa_unmatched)} courses unmatched")
    if asa_unmatched:
        print(f"  Unmatched: {sorted(asa_unmatched)[:10]}")

    # --- Process historical data (2009-2014 only, avoid overlap with ASA) ---
    hist_matched = 0
    hist_unmatched = set()

    for r in hist_lb:
        tid = r.get("tournamentID", "")
        tourn = tourn_lookup.get(tid)
        if not tourn:
            continue

        year = int(tourn.get("year", 0))
        if year >= 2015:  # Skip overlap with ASA data
            continue

        course_raw = tourn.get("course", "").strip().rstrip(".")
        # Some tournaments have multiple courses (e.g., "Course A. Course B.")
        # Take the first one
        first_course = course_raw.split(".")[0].strip()
        name, city, state = parse_course_location(first_course)
        norm = normalize_course_name(name)

        geo = geo_lookup.get(first_course.lower().strip()) or geo_lookup.get(norm)
        if not geo:
            hist_unmatched.add(first_course)
            continue
        hist_matched += 1

        fips = geo["fips"]
        eab_year = eab_by_fips.get(fips)

        tot = r.get("TOT", "")
        score_str = r.get("SCORE", "")

        if not tot:
            continue
        try:
            tot_int = int(tot)
        except ValueError:
            continue

        # Estimate par from TOT and SCORE
        # SCORE is relative to par (e.g., "-24" means 24 under par)
        try:
            score_vs_par = int(score_str)
            par = tot_int - score_vs_par
        except (ValueError, TypeError):
            # If SCORE isn't parseable, skip
            continue

        # Count rounds played
        n_rounds = sum(1 for rd in ["R1", "R2", "R3", "R4"] if r.get(rd, "").strip())

        treated = 1 if (eab_year and year >= eab_year) else 0
        post = 1 if (eab_year and year >= eab_year) else 0
        eab_county = 1 if eab_year else 0

        rows.append({
            "source": "historical",
            "player": r.get("PLAYER", ""),
            "course_name": name,
            "course_raw": first_course,
            "city": city,
            "state": state,
            "fips": fips,
            "county": geo.get("county_name", ""),
            "year": year,
            "strokes": tot,
            "par": par,
            "score_vs_par": score_vs_par,
            "n_rounds": n_rounds,
            "sg_total": "",
            "sg_ott": "",
            "sg_app": "",
            "sg_arg": "",
            "sg_putt": "",
            "eab_county": eab_county,
            "eab_year": eab_year or "",
            "post_eab": post,
            "treatment": treated,
        })

    print(f"Historical: {hist_matched} rows matched, {len(hist_unmatched)} courses unmatched")
    if hist_unmatched:
        print(f"  Unmatched: {sorted(hist_unmatched)[:10]}")

    # Sort and write
    rows.sort(key=lambda r: (r["year"], r["course_name"], r["player"]))

    with open("data/processed/track_a_analysis.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "source", "player", "course_name", "course_raw", "city", "state",
            "fips", "county", "year", "strokes", "par", "score_vs_par", "n_rounds",
            "sg_total", "sg_ott", "sg_app", "sg_arg", "sg_putt",
            "eab_county", "eab_year", "post_eab", "treatment",
        ])
        writer.writeheader()
        writer.writerows(rows)

    # Summary stats
    treatment_rows = [r for r in rows if r["treatment"] == 1]
    control_rows = [r for r in rows if r["treatment"] == 0]
    eab_pre = [r for r in rows if r["eab_county"] == 1 and r["post_eab"] == 0]
    eab_post = [r for r in rows if r["eab_county"] == 1 and r["post_eab"] == 1]
    non_eab = [r for r in rows if r["eab_county"] == 0]

    print(f"\n--- Analysis Table Summary ---")
    print(f"Total rows: {len(rows)}")
    print(f"  EAB counties, pre-arrival:  {len(eab_pre)}")
    print(f"  EAB counties, post-arrival: {len(eab_post)} (treatment=1)")
    print(f"  Non-EAB counties:           {len(non_eab)}")
    print(f"Years: {min(r['year'] for r in rows)}-{max(r['year'] for r in rows)}")
    print(f"Unique courses: {len(set(r['course_name'] for r in rows))}")
    print(f"Unique players: {len(set(r['player'] for r in rows))}")
    print(f"Output: data/processed/track_a_analysis.csv")


if __name__ == "__main__":
    main()
