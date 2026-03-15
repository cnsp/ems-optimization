"""Tier 2a: Filter firehouses to Manhattan subset.

Inputs:
    data/raw/FDNY_Firehouse_Listing_20260223.csv
    data/processed/cache/manhattan_geom.pkl
    data/processed/cache/cbd_geom.pkl

Outputs:
    data/processed/firehouses_clean.csv
    data/processed/firehouses_manhattan.csv
"""
from __future__ import annotations

from pathlib import Path


def process_firehouses(project_root: str | Path, force: bool = False) -> dict:
    """Filter FDNY firehouses to Manhattan and tag CBD membership."""
    import pandas as pd
    import geopandas as gpd
    from shapely.geometry import Point

    from scripts.data_processing.tier1_boundaries import load_geometries

    project_root = Path(project_root)
    processed = project_root / "data" / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    raw = project_root / "data" / "raw"

    out_clean = processed / "firehouses_clean.csv"
    out_manhattan = processed / "firehouses_manhattan.csv"

    if not force and out_clean.exists() and out_manhattan.exists():
        print("  [skip] Firehouse CSVs already exist.")
        return {"firehouses_clean": str(out_clean), "firehouses_manhattan": str(out_manhattan), "skipped": True}

    manhattan_geom, cbd_geom = load_geometries(project_root)

    # Locate raw file (glob for date-stamped name)
    raw_files = list(raw.glob("FDNY_Firehouse_Listing_*.csv"))
    if not raw_files:
        raise FileNotFoundError("Missing FDNY_Firehouse_Listing_*.csv in data/raw/")
    df = pd.read_csv(raw_files[0])
    print(f"  Loaded {len(df)} firehouses from {raw_files[0].name}")

    # Identify coordinate columns
    lat_col = next((c for c in df.columns if "lat" in c.lower()), None)
    lon_col = next((c for c in df.columns if "lon" in c.lower()), None)
    if lat_col is None or lon_col is None:
        raise ValueError("Cannot find lat/lon columns in firehouse data.")

    NYC_LAT = (40.5, 41.0)
    NYC_LON = (-74.3, -73.7)

    valid = (
        df[lat_col].notna() & df[lon_col].notna()
        & df[lat_col].between(*NYC_LAT)
        & df[lon_col].between(*NYC_LON)
    )
    df_valid = df[valid].copy()
    geometry = [Point(xy) for xy in zip(df_valid[lon_col], df_valid[lat_col])]
    gdf = gpd.GeoDataFrame(df_valid, geometry=geometry, crs="EPSG:4326")

    gdf["in_manhattan"] = gdf.within(manhattan_geom)
    gdf["in_cbd"] = gdf.within(cbd_geom)

    # Save clean (all valid NYC firehouses)
    clean_df = gdf.drop(columns=["geometry"])
    clean_df.to_csv(out_clean, index=False)
    print(f"  Saved firehouses_clean.csv ({len(clean_df)} records)")

    # Manhattan subset
    manhattan_fh = gdf[gdf["in_manhattan"]].drop(columns=["geometry"])
    manhattan_fh.to_csv(out_manhattan, index=False)
    print(f"  Saved firehouses_manhattan.csv ({len(manhattan_fh)} records)")

    return {
        "firehouses_clean": str(out_clean),
        "firehouses_manhattan": str(out_manhattan),
        "n_total": len(clean_df),
        "n_manhattan": len(manhattan_fh),
        "skipped": False,
    }
