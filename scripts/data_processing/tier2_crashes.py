"""Tier 2c: Filter crash data to Manhattan.

Inputs:
    data/raw/Motor_Vehicle_Collisions_-_Crashes_*.csv
    data/processed/cache/manhattan_geom.pkl + cbd_geom.pkl

Outputs:
    data/processed/crashes_manhattan.csv
    data/processed/crashes_manhattan.parquet
"""
from __future__ import annotations

import os
from pathlib import Path

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable=None, *args, **kwargs):
        if iterable is not None:
            return iterable
        class _Dummy:
            def update(self, n=1): pass
            def close(self): pass
            def set_postfix_str(self, s): pass
        return _Dummy()


def _process_chunk(args):
    """Process a single chunk -- used by parallel and serial paths."""
    import pandas as pd
    import numpy as np
    from shapely.geometry import Point
    from shapely import prepared
    import pickle

    chunk_bytes, manhattan_pkl_path, cbd_pkl_path = args

    # Deserialize chunk
    chunk = pickle.loads(chunk_bytes)

    # Load geometries (each worker loads its own copy)
    with open(manhattan_pkl_path, "rb") as f:
        manhattan_geom = pickle.load(f)
    with open(cbd_pkl_path, "rb") as f:
        cbd_geom = pickle.load(f)

    manhattan_prep = prepared.prep(manhattan_geom)
    cbd_prep = prepared.prep(cbd_geom)

    NYC_LAT = (40.5, 41.0)
    NYC_LON = (-74.3, -73.7)

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
        return mh, len(chunk), len(mh)
    return None, len(chunk), 0


def process_crashes(
    project_root: str | Path,
    force: bool = False,
    cache_mgr=None,
    n_jobs: int = 1,
) -> dict:
    """Chunk-process crash CSV, filter to Manhattan, save CSV + Parquet."""
    import pandas as pd
    import numpy as np
    import pickle
    import warnings
    warnings.filterwarnings("ignore")

    from scripts.data_processing.tier1_boundaries import load_geometries

    project_root = Path(project_root)
    processed = project_root / "data" / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    raw = project_root / "data" / "raw"

    out_csv = processed / "crashes_manhattan.csv"
    out_parquet = processed / "crashes_manhattan.parquet"

    # Cache check
    if not force and cache_mgr and cache_mgr.is_valid("tier2_crashes"):
        print("  [cache] Crash data unchanged -- using cached data.")
        return {"crashes_csv": str(out_csv), "crashes_parquet": str(out_parquet), "skipped": True}

    if not force and out_csv.exists() and out_parquet.exists():
        print("  [skip] Manhattan crash files already exist.")
        return {"crashes_csv": str(out_csv), "crashes_parquet": str(out_parquet), "skipped": True}

    # Ensure geometries exist
    load_geometries(project_root)

    cache_dir = project_root / "data" / "processed" / "cache"
    manhattan_pkl_path = str(cache_dir / "manhattan_geom.pkl")
    cbd_pkl_path = str(cache_dir / "cbd_geom.pkl")

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

    # Count total chunks for progress bar (estimate from file size)
    file_size = raw_files[0].stat().st_size
    estimated_chunks = max(1, file_size // (CHUNK_SIZE * 200))  # rough estimate

    print(f"  Processing {raw_files[0].name} in chunks of {CHUNK_SIZE:,}...")

    if n_jobs > 1:
        # Parallel processing
        try:
            from joblib import Parallel, delayed
            print(f"  Using {n_jobs} parallel workers")

            # Read all chunks first, then process in parallel
            chunks_data = []
            for chunk in pd.read_csv(raw_files[0], chunksize=CHUNK_SIZE, low_memory=False):
                chunks_data.append(pickle.dumps(chunk))
                total_rows += len(chunk)

            pbar = tqdm(total=len(chunks_data), desc="  Filtering crashes", unit="chunk")

            results = Parallel(n_jobs=n_jobs, backend="loky")(
                delayed(_process_chunk)((chunk_bytes, manhattan_pkl_path, cbd_pkl_path))
                for chunk_bytes in chunks_data
            )

            for mh_df, n_total, n_mh in results:
                if mh_df is not None:
                    manhattan_chunks.append(mh_df)
                    manhattan_count += n_mh
                pbar.update(1)
            pbar.close()

        except ImportError:
            print("  [warn] joblib not available, falling back to serial processing")
            n_jobs = 1

    if n_jobs <= 1:
        # Serial processing with progress bar
        pbar = tqdm(desc="  Filtering crashes", unit="chunk")
        for i, chunk in enumerate(
            pd.read_csv(raw_files[0], chunksize=CHUNK_SIZE, low_memory=False)
        ):
            result = _process_chunk((pickle.dumps(chunk), manhattan_pkl_path, cbd_pkl_path))
            mh_df, n_total, n_mh = result
            total_rows += n_total
            if mh_df is not None:
                manhattan_chunks.append(mh_df)
                manhattan_count += n_mh
            pbar.update(1)
            pbar.set_postfix_str(f"{total_rows:,} rows, {manhattan_count:,} Manhattan")
        pbar.close()

    manhattan_df = pd.concat(manhattan_chunks, ignore_index=True)

    # Ensure consistent dtypes for parquet serialization
    for col in manhattan_df.columns:
        if manhattan_df[col].dtype == object:
            manhattan_df[col] = manhattan_df[col].astype(str)

    manhattan_df.to_csv(out_csv, index=False)
    manhattan_df.to_parquet(out_parquet, index=False)

    print(f"  Saved crashes_manhattan.csv  ({len(manhattan_df):,} records)")
    print(f"  Saved crashes_manhattan.parquet")

    if cache_mgr:
        cache_mgr.update("tier2_crashes")

    return {
        "crashes_csv": str(out_csv),
        "crashes_parquet": str(out_parquet),
        "n_total": total_rows,
        "n_manhattan": len(manhattan_df),
        "skipped": False,
    }
