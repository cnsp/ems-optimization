"""Tier 3a: Build NHPP lambda tables from Manhattan crash data.

Inputs:
    data/processed/crashes_manhattan.parquet
    data/processed/precincts_manhattan.geojson

Outputs:
    data/processed/demand_lambda_hourly.csv
    data/processed/demand_lambda_dow.csv
    data/processed/demand_lambda_precinct.csv
    data/processed/demand_model_summary.json
"""
from __future__ import annotations

import json
from pathlib import Path


def build_lambda_tables(project_root: str | Path, force: bool = False) -> dict:
    """Compute hourly, DOW, and precinct arrival-rate factors."""
    import pandas as pd
    import numpy as np
    import geopandas as gpd
    from shapely.geometry import Point

    project_root = Path(project_root)
    processed = project_root / "data" / "processed"

    outputs = [
        processed / "demand_lambda_hourly.csv",
        processed / "demand_lambda_dow.csv",
        processed / "demand_lambda_precinct.csv",
        processed / "demand_model_summary.json",
    ]

    if not force and all(p.exists() for p in outputs):
        print("  [skip] Lambda tables already exist.")
        return {"files": [str(p) for p in outputs], "skipped": True}

    # --- Load data ---
    parquet = processed / "crashes_manhattan.parquet"
    if not parquet.exists():
        raise FileNotFoundError(
            f"Missing {parquet}. Run crash processing first (Tier 2c)."
        )
    df = pd.read_parquet(parquet)
    df["crash_datetime"] = pd.to_datetime(df["crash_datetime"])
    df["hour"] = df["crash_datetime"].dt.hour
    df["dow"] = df["crash_datetime"].dt.dayofweek
    df["date"] = df["crash_datetime"].dt.date
    print(f"  Loaded {len(df):,} Manhattan crashes")

    # Overall rate
    date_min = df["crash_datetime"].min()
    date_max = df["crash_datetime"].max()
    total_hours = (date_max - date_min).total_seconds() / 3600
    lambda_overall = len(df) / total_hours
    print(f"  Overall lambda: {lambda_overall:.4f} crashes/hour")

    # --- Hourly factors ---
    hourly_crash_counts = df.groupby("hour").size()
    date_hour_counts = df.groupby(["date", "hour"]).size().reset_index(name="crashes")
    hours_per_bucket = date_hour_counts.groupby("hour").size()
    lambda_hourly = hourly_crash_counts / hours_per_bucket
    lambda_hourly_normalized = lambda_hourly / lambda_hourly.mean()

    # CBD / Non-CBD split
    cbd_df = df[df.get("in_cbd", pd.Series(dtype=bool)) == True]
    non_cbd_df = df[df.get("in_cbd", pd.Series(dtype=bool)) == False]

    def _hourly_factors(sub):
        if len(sub) == 0:
            return pd.Series(np.ones(24), index=range(24))
        counts = sub.groupby("hour").size()
        dh = sub.groupby([sub["crash_datetime"].dt.date, "hour"]).size().reset_index(name="c")
        h_per = dh.groupby("hour").size()
        lam = counts / h_per
        return lam / lam.mean()

    cbd_hourly_norm = _hourly_factors(cbd_df)
    non_cbd_hourly_norm = _hourly_factors(non_cbd_df)

    hourly_output = pd.DataFrame({
        "hour": range(24),
        "lambda_per_hour": lambda_hourly.values,
        "factor": lambda_hourly_normalized.values,
        "cbd_factor": cbd_hourly_norm.values if len(cbd_df) > 0 else 1.0,
        "non_cbd_factor": non_cbd_hourly_norm.values if len(non_cbd_df) > 0 else 1.0,
    })
    hourly_output.to_csv(outputs[0], index=False)
    print(f"  Saved demand_lambda_hourly.csv")

    # --- DOW factors ---
    dow_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow_crash_counts = df.groupby("dow").size()
    date_dow_counts = df.groupby(["date", "dow"]).size().reset_index(name="crashes")
    days_per_dow = date_dow_counts.groupby("dow").size()
    lambda_dow = dow_crash_counts / days_per_dow
    lambda_dow_normalized = lambda_dow / lambda_dow.mean()

    def _dow_factors(sub):
        if len(sub) == 0:
            return pd.Series(np.ones(7), index=range(7))
        counts = sub.groupby("dow").size()
        dd = sub.groupby([sub["crash_datetime"].dt.date, "dow"]).size().reset_index(name="c")
        d_per = dd.groupby("dow").size()
        lam = counts / d_per
        return lam / lam.mean()

    cbd_dow_norm = _dow_factors(cbd_df)
    non_cbd_dow_norm = _dow_factors(non_cbd_df)

    dow_output = pd.DataFrame({
        "dow": range(7),
        "day_name": dow_names,
        "lambda_per_day": lambda_dow.values,
        "factor": lambda_dow_normalized.values,
        "cbd_factor": cbd_dow_norm.values if len(cbd_df) > 0 else 1.0,
        "non_cbd_factor": non_cbd_dow_norm.values if len(non_cbd_df) > 0 else 1.0,
    })
    dow_output.to_csv(outputs[1], index=False)
    print(f"  Saved demand_lambda_dow.csv")

    # --- Precinct rates ---
    precincts_path = processed / "precincts_manhattan.geojson"
    if precincts_path.exists():
        precincts = gpd.read_file(precincts_path)
        geometry = [Point(xy) for xy in zip(df["LONGITUDE"], df["LATITUDE"])]
        crashes_gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
        joined = gpd.sjoin(crashes_gdf, precincts[["Precinct", "geometry"]], how="left", predicate="within")
        joined = joined.rename(columns={"Precinct": "precinct"})
        precinct_counts = joined.groupby("precinct").size().reset_index(name="total_crashes")
        precinct_counts["crash_rate_per_hour"] = precinct_counts["total_crashes"] / total_hours
        precinct_counts["demand_weight"] = precinct_counts["total_crashes"] / precinct_counts["total_crashes"].sum()
        precinct_counts.to_csv(outputs[2], index=False)
        print(f"  Saved demand_lambda_precinct.csv ({len(precinct_counts)} precincts)")
    else:
        print("  [warn] precincts_manhattan.geojson not found -- skipping precinct rates")

    # --- Summary JSON ---
    summary = {
        "n_crashes": int(len(df)),
        "date_min": str(date_min),
        "date_max": str(date_max),
        "total_hours": float(total_hours),
        "lambda_overall": float(lambda_overall),
        "lambda_overall_per_day": float(lambda_overall * 24),
        "peak_hour": int(lambda_hourly.idxmax()),
        "peak_dow": dow_names[int(lambda_dow.idxmax())],
    }
    with open(outputs[3], "w") as f:
        json.dump(summary, f, indent=2)
    print(f"  Saved demand_model_summary.json")

    return {"files": [str(p) for p in outputs], "skipped": False}
