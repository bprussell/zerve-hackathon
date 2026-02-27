"""
Calibrate ash mortality rate from observed FIA multi-year data
and produce refined extinction projections.

Compares ash tree estimates across FIA eval years for counties
with known EAB arrival dates to measure actual decline rates,
then re-runs the extinction projection with calibrated parameters.

Input:
  - data/raw/fia_ash_multiyear.csv (multi-year FIA pulls)
  - data/raw/eab_detections_by_county.csv
  - data/processed/eab_predicted_spread.csv (from spread model)

Output:
  - data/processed/ash_extinction_calibrated.csv (refined timeline)
  - data/processed/mortality_by_species.csv (observed decline rates)
"""

import csv
import os
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROC_DIR = os.path.join(DATA_DIR, "processed")

# Functional extinction threshold
EXTINCTION_THRESHOLD_PCT = 1.0


def load_data():
    """Load multi-year FIA, EAB detections, and spread predictions."""
    print("-- Loading data --")

    fia = pd.read_csv(
        os.path.join(RAW_DIR, "fia_ash_multiyear.csv"),
        dtype={"state_fips": str, "county_fips": str},
    )
    print(f"  Multi-year FIA: {len(fia)} records")

    eab = pd.read_csv(
        os.path.join(RAW_DIR, "eab_detections_by_county.csv"),
        dtype={"fips": str},
    )
    eab["fips"] = eab["fips"].str.zfill(5)
    print(f"  EAB detections: {len(eab)} counties")

    spread = pd.read_csv(
        os.path.join(PROC_DIR, "eab_predicted_spread.csv"),
        dtype={"fips": str},
    )
    print(f"  Spread predictions: {len(spread)} counties")

    return fia, eab, spread


def compute_state_level_trends(fia, eab):
    """Compute ash population trends at the state level over time."""
    print("\n-- State-level ash trends --")

    # Aggregate: total ash per state per eval year
    state_year = (
        fia.groupby(["state_fips", "state", "eval_year"])["estimate"]
        .sum()
        .reset_index()
    )

    # Merge EAB detection year (earliest in state)
    eab_state = (
        eab.groupby("state_fips")["year_detected"]
        .min()
        .reset_index()
        .rename(columns={"year_detected": "eab_first_year", "state_fips": "state_fips_eab"})
    )
    # State FIPS from county FIPS
    eab["state_fips_eab"] = eab["fips"].str[:2]
    eab_state = (
        eab.groupby("state_fips_eab")["year_detected"]
        .min()
        .reset_index()
        .rename(columns={"year_detected": "eab_first_year"})
    )

    state_year = state_year.merge(
        eab_state,
        left_on="state_fips",
        right_on="state_fips_eab",
        how="left",
    )
    state_year["years_since_eab"] = state_year["eval_year"] - state_year["eab_first_year"]

    # For each state, compute peak ash estimate and relative decline
    for state in sorted(state_year["state"].unique()):
        s = state_year[state_year["state"] == state].sort_values("eval_year")
        eab_yr = s["eab_first_year"].iloc[0]
        peak = s["estimate"].max()
        latest = s["estimate"].iloc[-1]
        pct_decline = (1 - latest / peak) * 100 if peak > 0 else 0
        n_years = s["eval_year"].max() - s["eval_year"].min()
        print(f"  {state}: peak {peak:,.0f} -> latest {latest:,.0f} "
              f"({pct_decline:.1f}% decline over {n_years} years, EAB since {eab_yr:.0f})")

    return state_year


def fit_mortality_curve_county(fia, eab):
    """Fit exponential decay model at county level post-EAB.

    For each county with EAB detection:
    - Track ash estimates across eval years
    - Align to years_since_eab
    - Normalize to baseline (estimate at or just before EAB arrival)
    - Fit: surviving_fraction = exp(-lambda * years_since_eab)

    County-level fitting avoids the dilution problem of state-level
    analysis where unaffected counties mask the decline signal.
    """
    print("\n-- Fitting mortality curve (county-level) --")

    # Merge EAB year onto FIA data
    eab_by_county = eab.set_index("fips")["year_detected"].to_dict()
    fia = fia.copy()
    fia["county_fips"] = fia["county_fips"].str.zfill(5)
    fia["eab_year"] = fia["county_fips"].map(eab_by_county)

    # Only counties with known EAB arrival
    fia_eab = fia[fia["eab_year"].notna()].copy()
    fia_eab["years_since_eab"] = fia_eab["eval_year"] - fia_eab["eab_year"]

    # Aggregate total ash per county per eval year
    county_year = (
        fia_eab.groupby(["county_fips", "eval_year", "years_since_eab"])["estimate"]
        .sum()
        .reset_index()
    )

    # Normalize each county relative to its baseline (nearest pre-EAB or at-EAB estimate)
    normalized = []
    counties_used = 0
    for county in county_year["county_fips"].unique():
        c = county_year[county_year["county_fips"] == county].sort_values("eval_year")
        if len(c) < 3:
            continue

        # Baseline: estimate closest to EAB arrival (years_since_eab closest to 0, prefer <= 0)
        pre_eab = c[c["years_since_eab"] <= 2]  # allow up to 2 years post for baseline
        if pre_eab.empty:
            continue
        baseline_idx = pre_eab["years_since_eab"].sub(0).abs().idxmin()
        baseline = pre_eab.loc[baseline_idx, "estimate"]
        if baseline <= 0:
            continue

        c = c.copy()
        c["fraction"] = c["estimate"] / baseline
        # Only keep post-EAB observations
        post = c[c["years_since_eab"] >= 0]
        if len(post) >= 2:
            normalized.append(post)
            counties_used += 1

    if not normalized:
        print("  WARNING: No county-level post-EAB data for curve fitting")
        return -np.log(0.01) / 6  # fall back to literature

    all_norm = pd.concat(normalized)
    print(f"  Counties used for calibration: {counties_used}")

    # Fit exponential decay: fraction = exp(-lambda * t)
    def decay_model(t, lam):
        return np.exp(-lam * t)

    t = all_norm["years_since_eab"].values.astype(float)
    y = all_norm["fraction"].values.astype(float)

    # Filter out bad data points
    valid = (t >= 0) & (y > 0) & (y <= 1.5) & np.isfinite(t) & np.isfinite(y)
    t = t[valid]
    y = y[valid]

    if len(t) < 10:
        print("  WARNING: Insufficient data for curve fitting")
        lit_lam = -np.log(0.01) / 6
        return lit_lam, np.exp(-lit_lam)

    try:
        popt, pcov = curve_fit(decay_model, t, y, p0=[0.1], bounds=(0, 2))
        lam = popt[0]
        perr = np.sqrt(np.diag(pcov))[0]

        # Convert to mortality parameters
        annual_survival = np.exp(-lam)
        annual_mortality = 1 - annual_survival

        # How many years for 99% mortality?
        years_to_99 = -np.log(0.01) / lam if lam > 0 else float("inf")
        # How many years for 50% mortality?
        years_to_50 = -np.log(0.50) / lam if lam > 0 else float("inf")

        print(f"  Fitted lambda: {lam:.4f} +/- {perr:.4f}")
        print(f"  Annual survival rate: {annual_survival:.4f}")
        print(f"  Annual mortality rate: {annual_mortality:.4f}")
        print(f"  Years to 50% mortality: {years_to_50:.1f}")
        print(f"  Years to 99% mortality: {years_to_99:.1f}")
        print(f"  Data points used: {len(t)}")

        # Compare with literature (99% in 6 years)
        lit_lam = -np.log(0.01) / 6
        print(f"  Literature lambda: {lit_lam:.4f} (99% in 6 years)")
        if lam < lit_lam:
            print(f"  -> Observed decline is SLOWER than literature")
        else:
            print(f"  -> Observed decline is FASTER than literature")

        return lam, annual_survival

    except (RuntimeError, ValueError) as e:
        print(f"  Curve fitting failed: {e}")
        return 0.99, 6


def compute_species_mortality(fia, eab):
    """Break down mortality rates by ash species."""
    print("\n-- Species-level mortality --")

    # Merge EAB year onto FIA data
    eab_by_county = eab.set_index("fips")["year_detected"].to_dict()
    fia = fia.copy()
    fia["eab_year"] = fia["county_fips"].map(eab_by_county)
    fia["years_since_eab"] = fia["eval_year"] - fia["eab_year"]

    results = []
    for species in sorted(fia["species"].unique()):
        sp = fia[fia["species"] == species]

        # Aggregate by eval year across all counties
        by_year = sp.groupby("eval_year")["estimate"].sum().reset_index()
        by_year = by_year.sort_values("eval_year")

        if len(by_year) < 3:
            continue

        peak = by_year["estimate"].max()
        latest = by_year["estimate"].iloc[-1]
        earliest = by_year["estimate"].iloc[0]
        pct_change = ((latest - earliest) / earliest * 100) if earliest > 0 else 0

        results.append({
            "species": species,
            "peak_estimate": round(peak),
            "earliest_estimate": round(earliest),
            "latest_estimate": round(latest),
            "pct_change": round(pct_change, 1),
            "n_eval_years": len(by_year),
        })

        print(f"  {species}: {earliest:,.0f} -> {latest:,.0f} ({pct_change:+.1f}%)")

    return pd.DataFrame(results)


def project_extinction_calibrated(spread, fia_snapshot, lam):
    """Re-run extinction projection with calibrated mortality rate."""
    print("\n-- Calibrated extinction projection --")

    # Get baseline ash per county from the single-snapshot FIA data
    fia_snap = pd.read_csv(
        os.path.join(RAW_DIR, "fia_ash_by_county.csv"),
        dtype={"county_fips": str},
    )
    fia_snap["county_fips"] = fia_snap["county_fips"].str.zfill(5)
    ash_by_county = (
        fia_snap.groupby("county_fips")["estimate"]
        .sum()
        .reset_index()
        .rename(columns={"county_fips": "fips", "estimate": "ash_estimate"})
    )

    # Merge arrival year from spread predictions
    county_data = ash_by_county.merge(
        spread[["fips", "arrival_year"]],
        on="fips",
        how="inner",
    )

    total_ash = county_data["ash_estimate"].sum()
    print(f"  Counties with ash + arrival year: {len(county_data)}")
    print(f"  Total baseline ash: {total_ash:,.0f}")

    annual_survival = np.exp(-lam)
    print(f"  Using calibrated annual survival: {annual_survival:.4f}")

    # Build timeline
    years = list(range(2002, 2076))
    timeline = []

    for year in years:
        surviving = 0
        for _, row in county_data.iterrows():
            arrival = row["arrival_year"]
            baseline = row["ash_estimate"]
            if year < arrival:
                surviving += baseline
            else:
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

    # Milestones
    for threshold in [75, 50, 25, 10, 5, 1]:
        hit = timeline_df[timeline_df["pct_remaining"] <= threshold]
        if len(hit) > 0:
            yr = hit.iloc[0]["year"]
            print(f"  {threshold}% remaining by: {yr}")

    return timeline_df


def write_outputs(timeline_df, species_df):
    """Save calibrated outputs."""
    os.makedirs(PROC_DIR, exist_ok=True)

    timeline_path = os.path.join(PROC_DIR, "ash_extinction_calibrated.csv")
    timeline_df.to_csv(timeline_path, index=False)
    print(f"\n  Calibrated timeline: {timeline_path}")

    species_path = os.path.join(PROC_DIR, "mortality_by_species.csv")
    species_df.to_csv(species_path, index=False)
    print(f"  Species mortality: {species_path}")


def main():
    print("=" * 60)
    print("Track B: Calibrated Extinction Projection")
    print("=" * 60)

    fia, eab, spread = load_data()
    state_year = compute_state_level_trends(fia, eab)
    lam, annual_survival = fit_mortality_curve_county(fia, eab)
    species_df = compute_species_mortality(fia, eab)
    timeline_df = project_extinction_calibrated(spread, fia, lam)
    write_outputs(timeline_df, species_df)

    print("\n" + "=" * 60)
    print("Done.")
    print("=" * 60)


if __name__ == "__main__":
    main()
