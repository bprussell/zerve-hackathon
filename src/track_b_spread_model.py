"""
Track B: EAB Spatial Spread Model

Predicts emerald ash borer arrival year for unaffected US counties
and projects ash tree extinction timeline.

Input:
  - data/raw/eab_detections_by_county.csv (867 counties, 2002-2022)
  - data/raw/fia_ash_by_county.csv (3,159 records, ash estimates)
  - Census Gazetteer county centroids (downloaded at runtime)

Output:
  - data/processed/eab_predicted_spread.csv
  - data/processed/ash_extinction_timeline.csv
"""

import csv
import math
import os
import time
import urllib.request
import urllib.parse
import io
import json

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score

# --Constants ──────────────────────────────────────────────────────────

# EAB origin: Wayne County, MI (FIPS 26163) — first US detection in 2002
ORIGIN_FIPS = "26163"

# Literature: ~99% ash mortality within 6 years of EAB arrival
# Knight et al. (2013), Herms & McCullough (2014)
MORTALITY_RATE = 0.99
MORTALITY_YEARS = 6

# Functional extinction threshold: 1% of original population
EXTINCTION_THRESHOLD = 0.01

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROC_DIR = os.path.join(DATA_DIR, "processed")

TIGERWEB_URL = (
    "https://tigerweb.geo.census.gov/arcgis/rest/services/"
    "TIGERweb/tigerWMS_Current/MapServer/86/query"
)
CENTROIDS_CACHE = os.path.join(RAW_DIR, "census_county_centroids.csv")


# --Utility Functions --


def haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance between two points in km."""
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def bearing_deg(lat1, lon1, lat2, lon2):
    """Bearing from point 1 to point 2 in degrees [0, 360)."""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    bearing = math.degrees(math.atan2(x, y))
    return bearing % 360


def load_csv(path):
    """Load a CSV file as a list of dicts."""
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


# --Step 1: Get County Centroids --


TIGERWEB_LAYER = 82  # Counties layer

# State FIPS to USPS abbreviation
STATE_FIPS_TO_USPS = {
    "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA",
    "08": "CO", "09": "CT", "10": "DE", "11": "DC", "12": "FL",
    "13": "GA", "15": "HI", "16": "ID", "17": "IL", "18": "IN",
    "19": "IA", "20": "KS", "21": "KY", "22": "LA", "23": "ME",
    "24": "MD", "25": "MA", "26": "MI", "27": "MN", "28": "MS",
    "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH",
    "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND",
    "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI",
    "45": "SC", "46": "SD", "47": "TN", "48": "TX", "49": "UT",
    "50": "VT", "51": "VA", "53": "WA", "54": "WV", "55": "WI",
    "56": "WY", "60": "AS", "66": "GU", "69": "MP", "72": "PR",
    "78": "VI",
}


def fetch_tigerweb_page(offset=0, page_size=1000):
    """Fetch one page of county centroids from TIGERweb ArcGIS REST API."""
    base = TIGERWEB_URL.replace("/86/", f"/{TIGERWEB_LAYER}/")
    params = urllib.parse.urlencode({
        "where": "1=1",
        "outFields": "GEOID,BASENAME,STATE,INTPTLAT,INTPTLON",
        "returnGeometry": "false",
        "resultOffset": offset,
        "resultRecordCount": page_size,
        "f": "json",
    })
    url = f"{base}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data.get("features", [])


def fetch_county_centroids():
    """Fetch county centroids from TIGERweb API (or use cache)."""
    if os.path.exists(CENTROIDS_CACHE):
        print(f"  Using cached centroids: {CENTROIDS_CACHE}")
        df = pd.read_csv(CENTROIDS_CACHE, dtype={"fips": str})
        print(f"  Loaded {len(df)} county centroids")
        return df

    print("  Fetching county centroids from TIGERweb API...")
    all_records = []
    offset = 0
    page_size = 1000

    while True:
        features = fetch_tigerweb_page(offset, page_size)
        if not features:
            break
        for feat in features:
            attrs = feat.get("attributes", {})
            geoid = str(attrs.get("GEOID", "")).zfill(5)
            state_fips = geoid[:2]
            lat_str = attrs.get("INTPTLAT", "")
            lon_str = attrs.get("INTPTLON", "")
            if not lat_str or not lon_str:
                continue
            all_records.append({
                "fips": geoid,
                "county_name": attrs.get("BASENAME", ""),
                "USPS": STATE_FIPS_TO_USPS.get(state_fips, ""),
                "lat": float(lat_str),
                "lon": float(lon_str),
            })
        print(f"    Fetched {len(all_records)} counties...")
        if len(features) < page_size:
            break
        offset += page_size
        time.sleep(0.3)

    df = pd.DataFrame(all_records)
    df.to_csv(CENTROIDS_CACHE, index=False)
    print(f"  Saved {len(df)} centroids to {CENTROIDS_CACHE}")
    return df


# --Step 2: Merge Data Sources ─────────────────────────────────────────


def build_county_dataset():
    """Merge county centroids + EAB detections + FIA ash data."""
    print("\n-- Loading data --")

    # County centroids
    centroids = fetch_county_centroids()

    # EAB detections
    eab = pd.read_csv(
        os.path.join(RAW_DIR, "eab_detections_by_county.csv"),
        dtype={"fips": str},
    )
    eab["fips"] = eab["fips"].str.zfill(5)
    print(f"  EAB detections: {len(eab)} counties")

    # FIA ash data — aggregate total ash estimate per county (all species)
    fia = pd.read_csv(
        os.path.join(RAW_DIR, "fia_ash_by_county.csv"),
        dtype={"county_fips": str},
    )
    fia["county_fips"] = fia["county_fips"].str.zfill(5)
    ash_by_county = (
        fia.groupby("county_fips")["estimate"]
        .sum()
        .reset_index()
        .rename(columns={"county_fips": "fips", "estimate": "ash_estimate"})
    )
    print(f"  FIA ash data: {len(ash_by_county)} counties with ash trees")

    # Merge onto centroids
    df = centroids.merge(eab[["fips", "year_detected"]], on="fips", how="left")
    df = df.merge(ash_by_county, on="fips", how="left")
    df["ash_estimate"] = df["ash_estimate"].fillna(0)
    df["has_eab"] = df["year_detected"].notna().astype(int)

    # Filter to contiguous US + DC (exclude AK, HI, territories)
    exclude_states = {"AK", "HI", "PR", "VI", "GU", "AS", "MP"}
    df = df[~df["USPS"].isin(exclude_states)].copy()

    # Get origin coordinates
    origin = df[df["fips"] == ORIGIN_FIPS].iloc[0]
    origin_lat, origin_lon = origin["lat"], origin["lon"]
    print(f"  Origin: {origin['county_name']}, {origin['USPS']} "
          f"({origin_lat:.4f}, {origin_lon:.4f})")

    # Feature engineering
    df["dist_from_origin_km"] = df.apply(
        lambda r: haversine_km(origin_lat, origin_lon, r["lat"], r["lon"]),
        axis=1,
    )
    df["bearing_from_origin"] = df.apply(
        lambda r: bearing_deg(origin_lat, origin_lon, r["lat"], r["lon"]),
        axis=1,
    )
    # Decompose bearing into sin/cos components (cyclical feature)
    df["bearing_sin"] = np.sin(np.radians(df["bearing_from_origin"]))
    df["bearing_cos"] = np.cos(np.radians(df["bearing_from_origin"]))

    # Log-transform ash estimate (skewed)
    df["log_ash"] = np.log1p(df["ash_estimate"])

    print(f"  Final dataset: {len(df)} contiguous US counties")
    print(f"    With EAB: {df['has_eab'].sum()}")
    print(f"    Without EAB: {(~df['has_eab'].astype(bool)).sum()}")
    print(f"    With ash trees: {(df['ash_estimate'] > 0).sum()}")

    return df


# --Step 3: Fit Spatial Spread Model ───────────────────────────────────


FEATURES = [
    "dist_from_origin_km",
    "bearing_sin",
    "bearing_cos",
    "lat",
    "lon",
    "log_ash",
]


def fit_spread_model(df):
    """Fit polynomial ridge regression to predict EAB arrival year.

    Uses a linear model (with polynomial features) rather than tree-based
    models so predictions extrapolate naturally beyond the training range
    for distant, not-yet-infected counties.
    """
    print("\n-- Fitting spread model --")

    # Training data: counties with known EAB detection
    train = df[df["has_eab"] == 1].copy()
    X_train = train[FEATURES].values
    y_train = train["year_detected"].values

    print(f"  Training samples: {len(train)}")
    print(f"  Detection year range: {y_train.min():.0f}-{y_train.max():.0f}")
    print(f"  Distance range: {train['dist_from_origin_km'].min():.0f}-"
          f"{train['dist_from_origin_km'].max():.0f} km")

    # Polynomial ridge regression — extrapolates beyond training range
    model = Pipeline([
        ("scaler", StandardScaler()),
        ("poly", PolynomialFeatures(degree=2, interaction_only=False, include_bias=False)),
        ("ridge", Ridge(alpha=10.0)),
    ])

    # Cross-validation (5-fold)
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring="neg_mean_absolute_error")
    mae = -cv_scores.mean()
    mae_std = cv_scores.std()
    print(f"  5-fold CV MAE: {mae:.2f} +/- {mae_std:.2f} years")

    r2_scores = cross_val_score(model, X_train, y_train, cv=5, scoring="r2")
    print(f"  5-fold CV R2: {r2_scores.mean():.3f} +/- {r2_scores.std():.3f}")

    # Fit on all training data
    model.fit(X_train, y_train)

    # Estimate average spread speed
    mask = (train["dist_from_origin_km"] > 50) & (train["year_detected"] > 2002)
    if mask.sum() > 10:
        years_elapsed = train.loc[mask, "year_detected"].values - 2002
        speed = train.loc[mask, "dist_from_origin_km"].values / years_elapsed
        print(f"  Estimated spread speed: {np.median(speed):.0f} km/year (median)")

    # Training performance
    y_pred_train = model.predict(X_train)
    train_mae = np.mean(np.abs(y_train - y_pred_train))
    print(f"  Training MAE: {train_mae:.2f} years")

    # Feature names after polynomial expansion
    poly_names = model.named_steps["poly"].get_feature_names_out(FEATURES)
    coefs = model.named_steps["ridge"].coef_
    # Show top 10 features by absolute coefficient
    top_idx = np.argsort(np.abs(coefs))[-10:][::-1]
    print("  Top coefficients:")
    for i in top_idx:
        print(f"    {poly_names[i]}: {coefs[i]:.4f}")

    return model


# --Step 4: Predict Arrival Years ──────────────────────────────────────


def predict_arrival(df, model):
    """Predict EAB arrival year for all counties (known + unknown)."""
    print("\n--Predicting arrival years --")

    X_all = df[FEATURES].values
    df = df.copy()
    df["predicted_year"] = model.predict(X_all)

    # For known detections, keep actual year; for unknowns, use prediction
    df["arrival_year"] = df.apply(
        lambda r: int(r["year_detected"]) if r["has_eab"] == 1 else round(r["predicted_year"]),
        axis=1,
    )
    df["arrival_year"] = df["arrival_year"].astype(int)

    # Clamp predictions: no earlier than 2002, cap at reasonable future
    df.loc[df["arrival_year"] < 2002, "arrival_year"] = 2002
    df.loc[df["arrival_year"] > 2075, "arrival_year"] = 2075

    # Summary
    unknown = df[df["has_eab"] == 0]
    print(f"  Predicted arrival for {len(unknown)} undetected counties")
    print(f"  Predicted year range: {unknown['arrival_year'].min():.0f}–"
          f"{unknown['arrival_year'].max():.0f}")

    # Distribution by decade
    bins = list(range(2020, 2080, 10))
    labels = [f"{b}s" for b in bins[:-1]]
    unknown_decades = pd.cut(unknown["arrival_year"], bins=bins, labels=labels, right=False)
    print("  Predicted arrivals by decade:")
    for label, count in unknown_decades.value_counts().sort_index().items():
        print(f"    {label}: {count} counties")

    return df


# --Step 5: Ash Extinction Projection ─────────────────────────────────


def project_extinction(df):
    """Project ash tree population decline over time."""
    print("\n--Projecting ash extinction --")

    # Only counties with ash trees
    ash_counties = df[df["ash_estimate"] > 0].copy()
    print(f"  Counties with ash: {len(ash_counties)}")
    total_ash = ash_counties["ash_estimate"].sum()
    print(f"  Total baseline ash estimate: {total_ash:,.0f} trees")

    # Annual mortality curve: exponential decay over MORTALITY_YEARS
    # After arrival, trees die following: surviving = (1 - rate)^(years/period)
    # We use: annual_survival = (1 - MORTALITY_RATE)^(1/MORTALITY_YEARS)
    annual_survival = (1 - MORTALITY_RATE) ** (1 / MORTALITY_YEARS)
    print(f"  Annual survival rate post-EAB: {annual_survival:.4f}")
    print(f"  (= {MORTALITY_RATE*100:.0f}% mortality over {MORTALITY_YEARS} years)")

    # Build timeline: for each year, sum surviving ash across all counties
    years = list(range(2002, 2076))
    timeline = []

    for year in years:
        surviving = 0
        for _, row in ash_counties.iterrows():
            arrival = row["arrival_year"]
            baseline = row["ash_estimate"]
            if year < arrival:
                # EAB hasn't arrived yet
                surviving += baseline
            else:
                # Years since EAB arrival
                years_since = year - arrival
                surviving += baseline * (annual_survival ** years_since)

        pct_remaining = (surviving / total_ash) * 100 if total_ash > 0 else 0
        timeline.append({
            "year": year,
            "surviving_trees": round(surviving),
            "pct_remaining": round(pct_remaining, 2),
            "trees_lost": round(total_ash - surviving),
        })

    timeline_df = pd.DataFrame(timeline)

    # Find key milestones
    for threshold_pct in [75, 50, 25, 10, 5, 1]:
        hit = timeline_df[timeline_df["pct_remaining"] <= threshold_pct]
        if len(hit) > 0:
            yr = hit.iloc[0]["year"]
            print(f"  {threshold_pct}% remaining by: {yr}")

    return timeline_df


# --Step 6: Write Outputs ──────────────────────────────────────────────


def write_outputs(df, timeline_df):
    """Save results to CSV."""
    os.makedirs(PROC_DIR, exist_ok=True)

    # Spread predictions
    spread_path = os.path.join(PROC_DIR, "eab_predicted_spread.csv")
    spread_cols = [
        "fips", "county_name", "USPS", "lat", "lon",
        "has_eab", "year_detected", "arrival_year", "predicted_year",
        "dist_from_origin_km", "bearing_from_origin",
        "ash_estimate", "log_ash",
    ]
    out = df[spread_cols].sort_values("arrival_year")
    out.to_csv(spread_path, index=False, float_format="%.4f")
    print(f"\n  Spread predictions: {spread_path} ({len(out)} rows)")

    # Extinction timeline
    timeline_path = os.path.join(PROC_DIR, "ash_extinction_timeline.csv")
    timeline_df.to_csv(timeline_path, index=False)
    print(f"  Extinction timeline: {timeline_path} ({len(timeline_df)} rows)")


# --Main ───────────────────────────────────────────────────────────────


def main():
    print("=" * 60)
    print("Track B: EAB Spatial Spread Model")
    print("=" * 60)

    df = build_county_dataset()
    model = fit_spread_model(df)
    df = predict_arrival(df, model)
    timeline_df = project_extinction(df)
    write_outputs(df, timeline_df)

    print("\n" + "=" * 60)
    print("Done.")
    print("=" * 60)


if __name__ == "__main__":
    main()
