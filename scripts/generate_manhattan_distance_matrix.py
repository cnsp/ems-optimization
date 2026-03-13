#!/usr/bin/env python3
"""Generate Manhattan (taxicab) distance matrix between firehouses and precincts.

Produces ``data/processed/distance_matrix_firehouse_precinct_manhattan.csv``
using the L1 (Manhattan / taxicab) distance metric instead of Haversine.

This is more realistic for grid-based street networks like Manhattan,
where travel follows north–south / east–west streets rather than
great-circle arcs.

Usage:
    python scripts/generate_manhattan_distance_matrix.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from shapely import wkt

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from ems_readiness.utils.distance import (
    build_distance_matrix,
    haversine,
    manhattan_distance,
)

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
RAW_DIR = PROJECT_ROOT / "data" / "raw"


def load_firehouses() -> pd.DataFrame:
    """Load Manhattan firehouses with lat/lon."""
    fh = pd.read_csv(PROCESSED_DIR / "firehouses_manhattan.csv")
    print(f"Loaded {len(fh)} Manhattan firehouses")
    return fh


def load_precinct_centroids() -> pd.DataFrame:
    """Load precinct geometries and compute centroids for Manhattan precincts."""
    # Determine which precincts are in the existing (Haversine) distance matrix
    dm = pd.read_csv(
        PROCESSED_DIR / "distance_matrix_firehouse_precinct.csv", index_col=0
    )
    manhattan_precincts = [int(p) for p in dm.columns]

    # Load precinct geometries
    prec = pd.read_csv(RAW_DIR / "Police_Precincts_20260223.csv")
    prec["geometry"] = prec["the_geom"].apply(wkt.loads)

    import geopandas as gpd

    gdf = gpd.GeoDataFrame(prec, geometry="geometry", crs="EPSG:4326")
    gdf = gdf[gdf["Precinct"].isin(manhattan_precincts)].copy()

    # Compute centroids (geographic CRS is fine for this purpose)
    gdf["centroid_lat"] = gdf.geometry.centroid.y
    gdf["centroid_lon"] = gdf.geometry.centroid.x
    gdf["Precinct"] = gdf["Precinct"].astype(str)

    print(f"Computed centroids for {len(gdf)} Manhattan precincts")
    return gdf[["Precinct", "centroid_lat", "centroid_lon"]]


def main():
    print("=" * 60)
    print("Generating Manhattan Distance Matrix")
    print("=" * 60)

    firehouses = load_firehouses()
    precincts = load_precinct_centroids()

    # Build Manhattan distance matrix
    dm_manhattan = build_distance_matrix(
        origins=firehouses,
        destinations=precincts,
        origin_lat="Latitude",
        origin_lon="Longitude",
        origin_id="FacilityName",
        dest_lat="centroid_lat",
        dest_lon="centroid_lon",
        dest_id="Precinct",
        metric="manhattan",
    )

    out_path = PROCESSED_DIR / "distance_matrix_firehouse_precinct_manhattan.csv"
    dm_manhattan.to_csv(out_path)
    print(f"\nSaved Manhattan distance matrix: {out_path}")
    print(f"  Shape: {dm_manhattan.shape}")
    print(f"  Range: {dm_manhattan.min().min():.3f} – {dm_manhattan.max().max():.3f} miles")
    print(f"  Mean : {dm_manhattan.values.mean():.3f} miles")

    # Compare with Haversine
    dm_haversine = pd.read_csv(
        PROCESSED_DIR / "distance_matrix_firehouse_precinct.csv", index_col=0
    )
    dm_haversine.columns = dm_haversine.columns.astype(str)
    dm_manhattan.columns = dm_manhattan.columns.astype(str)

    # Align columns
    common_cols = sorted(set(dm_haversine.columns) & set(dm_manhattan.columns))
    h = dm_haversine[common_cols].values.flatten()
    m = dm_manhattan[common_cols].values.flatten()

    ratio = m / np.where(h > 0, h, 1e-10)
    print(f"\n--- Comparison ---")
    print(f"  Haversine mean : {h.mean():.3f} miles")
    print(f"  Manhattan mean : {m.mean():.3f} miles")
    print(f"  Ratio (M/H)    : {ratio.mean():.3f} ± {ratio.std():.3f}")
    print(f"  Manhattan is on average {(ratio.mean()-1)*100:.1f}% longer than Haversine")

    print("\nDone.")


if __name__ == "__main__":
    main()
