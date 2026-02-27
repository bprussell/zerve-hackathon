import pandas as pd
import re

# ── Load raw data ──
eab = pd.read_csv("eab_detections_by_county.csv", dtype={"fips": str})
eab["fips"] = eab["fips"].str.zfill(5)

courses = pd.read_csv("pga_courses_geocoded.csv", dtype={"fips": str, "state_fips": str})

pga_modern = pd.read_csv("ASA All PGA Raw Data - Tourn Level.csv")

hist_leaders = pd.read_csv("Full_Leaderboard_Table.csv")
hist_tourneys = pd.read_csv("Full_Tournament_Table.csv")

fia_snapshot = pd.read_csv("fia_ash_by_county.csv", dtype={"county_fips": str})
fia_snapshot["county_fips"] = fia_snapshot["county_fips"].str.zfill(5)

fia_multiyear = pd.read_csv("fia_ash_multiyear.csv", dtype={"state_fips": str, "county_fips": str})

centroids = pd.read_csv("census_county_centroids.csv", dtype={"fips": str})

print(f"EAB detections: {len(eab)}")
print(f"Courses: {len(courses)}")
print(f"PGA modern: {len(pga_modern)}")
print(f"Historical leaders: {len(hist_leaders)}")
print(f"Historical tourneys: {len(hist_tourneys)}")
print(f"FIA snapshot: {len(fia_snapshot)}")
print(f"FIA multiyear: {len(fia_multiyear)}")
print(f"Centroids: {len(centroids)}")
