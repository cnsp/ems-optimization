"""Tier 2c: Filter crash data to Manhattan.

Inputs:
    data/raw/Motor_Vehicle_Collisions_-_Crashes_*.csv
    data/processed/cache/manhattan_geom.pkl + cbd_geom.pkl

Outputs:
    data/processed/crashes_manhattan.csv
    data/processed/crashes_manhattan.parquet
"""
from __future__ import annotations

from pathlib import Path


def process_crashes(project_root: str | Path, force: bool = False) -> dict:
    """Chunk-process crash CSV, filter to Manhattan, save CSV + Parquet."""
    import pandas as pd
    import numpy as np
    from shapely.geometry import Point
    from shapely import prepared
    import warnings
    warnings.filterwarnings("ignore")

    from scripts.data_processing.tier1_boundaries import load_geometries

    project_root = Path(project_root)
    processed = project_root / "data" / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    raw = project_root / "data" / "raw"

    out_csv = processed / "crashes_manhattan.csv"
    out_parquet = processed / "crashes_manhattan.parquet"

    if not force and out_csv.exists() and out_parquet.exists():
        print("  [skip] Manhattan crash files already exist.")
        return {"crashes_csv": str(out_csv), "crashes_parquet": str(out_parquet), "skipped": True}

    manhattan_geom, cbd_geom = load_geometries(project_root)
    manhattan_prep = prepared.prep(manhattan_geom)
    cbd_prep = prepared.prep(cbd_geom)

    NYC_LAT = (40.5, 41.0)
    NYC_LON = (-74.3, -73.7)

    raw_files = list(raw.glob("Motor_Vehicle_Collisions_-_Crashes_*.csv"))
    if not raw_files:
        raise FileNotFoundError(
            "Missing Motor_Vehicle_Collisions_-_Crashes_*.csv in data/raw/.\n"
            "Download from: https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95"
        )

    CHUNK_SIZE = 100_000
    manhattan_chunks = []
    total_rows = 0
    manhattan_count = 0

    print(f"  Processing {raw_files[0].name} in chunks of {CHUNK_SIZE:,}...")
    for i, chunk in enumerate(
        pd.read_csv(raw_files[0], chunksize=CHUNK_SIZE, low_memory=False)
    ):
        total_rows += len(chunk)

        chunk["crash_datetime"] = pd.to_datetime(
            chunk["CRASH DATE"] + " " + chunk["CRASH TIME"].fillna("00:00"),
            errors="coerce",
        )

        missing = chunk["LATITUDE"].isna() | chunk["LONGITUDE"].isna()
        valid = (
            ~missing
            & chunk["LATITUDE"].between(*NYC_LAT)
            & chunk["LONGITUDE"].between(*NYC_LON)
        )
        valid_chunk = chunk[valid].copy()

        def _in_manhattan(row):
            return manhattan_prep.contains(Point(row["LONGITUDE"], row["LATITUDE"]))

        def _in_cbd(row):
            return cbd_prep.contains(Point(row["LONGITUDE"], row["LATITUDE"]))

        valid_chunk["in_manhattan"] = valid_chunk.apply(_in_manhattan, axis=1)
        mh = valid_chunk[valid_chunk["in_manhattan"]].copy()
        if len(mh) > 0:
            mh["in_cbd"] = mh.apply(_in_cbd, axis=1)
            mh = mh.drop(columns=["in_manhattan"])
            manhattan_chunks.append(mh)
            manhattan_count += len(mh)

        if (i + 1) % 5 == 0 or i == 0:
            print(f"    Chunk {i+1}: {total_rows:,} rows processed, {manhattan_count:,} Manhattan")

    manhattan_df = pd.concat(manhattan_chunks, ignore_index=True)
    manhattan_df.to_csv(out_csv, index=False)
    manhattan_df.to_parquet(out_parquet, index=False)

    print(f"  Saved crashes_manhattan.csv  ({len(manhattan_df):,} records)")
    print(f"  Saved crashes_manhattan.parquet")

    return {
        "crashes_csv": str(out_csv),
        "crashes_parquet": str(out_parquet),
        "n_total": total_rows,
        "n_manhattan": len(manhattan_df),
        "skipped": False,
    }
