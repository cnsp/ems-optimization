"""Tier 3b: Build distance matrices (Haversine + Manhattan).

Inputs:
    data/processed/firehouses_manhattan.csv
    data/processed/precincts_manhattan.geojson  (or raw Police_Precincts_*.csv)

Outputs:
    data/processed/distance_matrix_firehouse_precinct.csv
    data/processed/distance_matrix_firehouse_precinct_manhattan.csv
"""
from __future__ import annotations

import sys
from pathlib import Path


def build_distance_matrices(project_root: str | Path, force: bool = False) -> dict:
    """Compute Haversine and Manhattan distance matrices."""
    import pandas as pd
    import numpy as np
    import geopandas as gpd
    from shapely import wkt

    project_root = Path(project_root)
    sys.path.insert(0, str(project_root / "src"))
    from ems_readiness.utils.distance import build_distance_matrix

    processed = project_root / "data" / "processed"
    raw = project_root / "data" / "raw"

    out_haversine = processed / "distance_matrix_firehouse_precinct.csv"
    out_manhattan = processed / "distance_matrix_firehouse_precinct_manhattan.csv"

    if not force and out_haversine.exists() and out_manhattan.exists():
        print("  [skip] Distance matrices already exist.")
        return {"haversine": str(out_haversine), "manhattan": str(out_manhattan), "skipped": True}

    # --- Load firehouses ---
    fh_path = processed / "firehouses_manhattan.csv"
    if not fh_path.exists():
        raise FileNotFoundError(f"Missing {fh_path}. Run firehouse processing first.")
    fh = pd.read_csv(fh_path)
    print(f"  Loaded {len(fh)} Manhattan firehouses")

    # --- Load precinct centroids ---
    prec_path = processed / "precincts_manhattan.geojson"
    if prec_path.exists():
        prec_gdf = gpd.read_file(prec_path)
    else:
        # Fallback: load from raw
        raw_files = list(raw.glob("Police_Precincts_*.csv"))
        if not raw_files:
            raise FileNotFoundError("No precinct data found.")
        prec_df = pd.read_csv(raw_files[0])
        prec_df["geometry"] = prec_df["the_geom"].apply(wkt.loads)
        prec_gdf = gpd.GeoDataFrame(prec_df, geometry="geometry", crs="EPSG:4326")

    # Compute centroids (suppress warning -- geographic CRS is acceptable here)
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        prec_gdf["centroid_lat"] = prec_gdf.geometry.centroid.y
        prec_gdf["centroid_lon"] = prec_gdf.geometry.centroid.x

    # build_distance_matrix expects specific column names
    # Origins: FacilityName, Latitude, Longitude
    # Destinations: Precinct, centroid_lat, centroid_lon
    destinations = prec_gdf[["Precinct", "centroid_lat", "centroid_lon"]].copy()

    # --- Haversine ---
    dm_hav = build_distance_matrix(fh, destinations, metric="haversine")
    dm_hav.to_csv(out_haversine)
    print(f"  Saved distance_matrix_firehouse_precinct.csv ({dm_hav.shape})")

    # --- Manhattan ---
    dm_man = build_distance_matrix(fh, destinations, metric="manhattan")
    dm_man.to_csv(out_manhattan)
    print(f"  Saved distance_matrix_firehouse_precinct_manhattan.csv ({dm_man.shape})")

    return {"haversine": str(out_haversine), "manhattan": str(out_manhattan), "skipped": False}
