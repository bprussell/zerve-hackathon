import pandas as pd
import numpy as np
import math
from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score
from scipy.optimize import curve_fit

# ── Constants ──
ORIGIN_FIPS = "26163"  # Wayne County, MI
MORTALITY_RATE = 0.99
MORTALITY_YEARS = 6

# ── Utility functions ──

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def bearing_deg(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1)*math.sin(lat2) - math.sin(lat1)*math.cos(lat2)*math.cos(dlon)
    return math.degrees(math.atan2(x, y)) % 360

# ── Step 1: Build county dataset ──
print("-- Building county dataset --")

# Aggregate ash by county
ash_by_county = (
    fia_snapshot.groupby("county_fips")["estimate"]
    .sum().reset_index()
    .rename(columns={"county_fips": "fips", "estimate": "ash_estimate"})
)

df = centroids.merge(eab[["fips", "year_detected"]], on="fips", how="left")
df = df.merge(ash_by_county, on="fips", how="left")
df["ash_estimate"] = df["ash_estimate"].fillna(0)
df["has_eab"] = df["year_detected"].notna().astype(int)

# Filter to contiguous US
exclude = {"AK", "HI", "PR", "VI", "GU", "AS", "MP"}
df = df[~df["USPS"].isin(exclude)].copy()

# Origin coords
origin = df[df["fips"] == ORIGIN_FIPS].iloc[0]
olat, olon = origin["lat"], origin["lon"]
print(f"  Origin: {origin['county_name']}, {origin['USPS']}")

# Features
df["dist_from_origin_km"] = df.apply(lambda r: haversine_km(olat, olon, r["lat"], r["lon"]), axis=1)
df["bearing_from_origin"] = df.apply(lambda r: bearing_deg(olat, olon, r["lat"], r["lon"]), axis=1)
df["bearing_sin"] = np.sin(np.radians(df["bearing_from_origin"]))
df["bearing_cos"] = np.cos(np.radians(df["bearing_from_origin"]))
df["log_ash"] = np.log1p(df["ash_estimate"])

print(f"  Counties: {len(df)} (EAB: {df['has_eab'].sum()}, no EAB: {(~df['has_eab'].astype(bool)).sum()})")

# ── Step 2: Fit spread model ──
print("\n-- Fitting spread model --")

FEATURES = ["dist_from_origin_km", "bearing_sin", "bearing_cos", "lat", "lon", "log_ash"]
train = df[df["has_eab"] == 1].copy()
X_train = train[FEATURES].values
y_train = train["year_detected"].values

model = Pipeline([
    ("scaler", StandardScaler()),
    ("poly", PolynomialFeatures(degree=2, interaction_only=False, include_bias=False)),
    ("ridge", Ridge(alpha=10.0)),
])

cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring="neg_mean_absolute_error")
print(f"  CV MAE: {-cv_scores.mean():.2f} +/- {cv_scores.std():.2f} years")

r2_scores = cross_val_score(model, X_train, y_train, cv=5, scoring="r2")
print(f"  CV R2: {r2_scores.mean():.3f} +/- {r2_scores.std():.3f}")

model.fit(X_train, y_train)

# ── Step 3: Predict arrival years ──
print("\n-- Predicting arrival years --")

X_all = df[FEATURES].values
df["predicted_year"] = model.predict(X_all)
df["arrival_year"] = df.apply(
    lambda r: int(r["year_detected"]) if r["has_eab"] == 1 else round(r["predicted_year"]),
    axis=1,
).astype(int)
df.loc[(df["has_eab"] == 1) & (df["arrival_year"] < 2002), "arrival_year"] = 2002
df.loc[(df["has_eab"] == 0) & (df["arrival_year"] < 2023), "arrival_year"] = 2023
df.loc[df["arrival_year"] > 2075, "arrival_year"] = 2075

unknown = df[df["has_eab"] == 0]
print(f"  Predicted {len(unknown)} counties: {unknown['arrival_year'].min()}-{unknown['arrival_year'].max()}")

# ── Step 4: Calibrate mortality from multi-year FIA ──
print("\n-- Calibrating mortality from FIA data --")

fia_multiyear["county_fips"] = fia_multiyear["county_fips"].str.zfill(5)
eab_by_county_dict = eab.set_index("fips")["year_detected"].to_dict()
fia_cal = fia_multiyear.copy()
fia_cal["eab_year"] = fia_cal["county_fips"].map(eab_by_county_dict)
fia_eab = fia_cal[fia_cal["eab_year"].notna()].copy()
fia_eab["years_since_eab"] = fia_eab["eval_year"] - fia_eab["eab_year"]

county_year = (
    fia_eab.groupby(["county_fips", "eval_year", "years_since_eab"])["estimate"]
    .sum().reset_index()
)

normalized = []
for county in county_year["county_fips"].unique():
    c = county_year[county_year["county_fips"] == county].sort_values("eval_year")
    if len(c) < 3:
        continue
    pre = c[c["years_since_eab"] <= 2]
    if pre.empty:
        continue
    bl_idx = pre["years_since_eab"].sub(0).abs().idxmin()
    baseline = pre.loc[bl_idx, "estimate"]
    if baseline <= 0:
        continue
    c = c.copy()
    c["fraction"] = c["estimate"] / baseline
    post = c[c["years_since_eab"] >= 0]
    if len(post) >= 2:
        normalized.append(post)

all_norm = pd.concat(normalized)
t_vals = all_norm["years_since_eab"].values.astype(float)
y_vals = all_norm["fraction"].values.astype(float)
valid = (t_vals >= 0) & (y_vals > 0) & (y_vals <= 1.5)
t_vals, y_vals = t_vals[valid], y_vals[valid]

popt, _ = curve_fit(lambda t, lam: np.exp(-lam * t), t_vals, y_vals, p0=[0.1], bounds=(0, 2))
lam = popt[0]
annual_survival_cal = np.exp(-lam)
print(f"  Calibrated annual survival: {annual_survival_cal:.4f} (lambda={lam:.4f})")
print(f"  Years to 50% mortality: {-np.log(0.5)/lam:.1f}")

# ── Step 5: Extinction projections (literature + calibrated) ──
print("\n-- Projecting extinction --")

ash_counties = df[df["ash_estimate"] > 0].copy()
total_ash = ash_counties["ash_estimate"].sum()
print(f"  Baseline: {total_ash:,.0f} ash trees across {len(ash_counties)} counties")

annual_survival_lit = (1 - MORTALITY_RATE) ** (1 / MORTALITY_YEARS)

years = list(range(2002, 2076))
timeline_rows = []
for year in years:
    surv_lit = 0
    surv_cal = 0
    for _, row in ash_counties.iterrows():
        arr = row["arrival_year"]
        base = row["ash_estimate"]
        if year < arr:
            surv_lit += base
            surv_cal += base
        else:
            yrs = year - arr
            surv_lit += base * (annual_survival_lit ** yrs)
            surv_cal += base * (annual_survival_cal ** yrs)
    timeline_rows.append({
        "year": year,
        "pct_lit": round(surv_lit / total_ash * 100, 2),
        "pct_cal": round(surv_cal / total_ash * 100, 2),
        "surviving_lit": round(surv_lit),
        "surviving_cal": round(surv_cal),
    })

extinction_df = pd.DataFrame(timeline_rows)

# Spread output
spread_df = df[["fips", "county_name", "USPS", "lat", "lon", "has_eab",
                "year_detected", "arrival_year", "predicted_year",
                "dist_from_origin_km", "bearing_from_origin",
                "ash_estimate"]].copy()

# Key milestones
print("\n  Literature-based (99% in 6yr):")
for pct in [75, 50, 25, 10, 1]:
    hit = extinction_df[extinction_df["pct_lit"] <= pct]
    if len(hit): print(f"    {pct}% remaining by {hit.iloc[0]['year']}")

print("  Calibrated (FIA observed):")
for pct in [75, 50, 25, 10, 1]:
    hit = extinction_df[extinction_df["pct_cal"] <= pct]
    if len(hit): print(f"    {pct}% remaining by {hit.iloc[0]['year']}")

print(f"\nDone. spread_df: {len(spread_df)} rows, extinction_df: {len(extinction_df)} rows")
