"""Tier 2b: Filter police precincts to Manhattan.

Inputs:
    data/raw/Police_Precincts_*.csv
    data/processed/cache/manhattan_geom.pkl

Outputs:
    data/processed/precincts_manhattan.geojson
"""
from __future__ import annotations

from pathlib import Path


def process_precincts(project_root: str | Path, force: bool = False) -> dict:
    """Identify precincts intersecting Manhattan and save as GeoJSON."""
    import pandas as pd
    import geopandas as gpd
    from shapely import wkt

    from scripts.data_processing.tier1_boundaries import load_geometries

    project_root = Path(project_root)
    processed = project_root / "data" / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    raw = project_root / "data" / "raw"

    out_path = processed / "precincts_manhattan.geojson"

    if not force and out_path.exists():
        print("  [skip] precincts_manhattan.geojson already exists.")
        return {"precincts_manhattan": str(out_path), "skipped": True}

    manhattan_geom, _ = load_geometries(project_root)

    raw_files = list(raw.glob("Police_Precincts_*.csv"))
    if not raw_files:
        raise FileNotFoundError("Missing Police_Precincts_*.csv in data/raw/")
    df = pd.read_csv(raw_files[0])
    print(f"  Loaded {len(df)} precincts from {raw_files[0].name}")

    geom_col = "the_geom" if "the_geom" in df.columns else next(
        (c for c in df.columns if "geom" in c.lower()), None
    )
    if geom_col is None:
        raise ValueError("Cannot find geometry column in precinct data.")

    df["geometry"] = df[geom_col].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")

    gdf["in_manhattan"] = gdf.geometry.intersects(manhattan_geom)
    manhattan_precincts = gdf[gdf["in_manhattan"]].copy()

    manhattan_precincts_save = manhattan_precincts.drop(columns=[geom_col])
    manhattan_precincts_save.to_file(out_path, driver="GeoJSON")
    print(f"  Saved precincts_manhattan.geojson ({len(manhattan_precincts_save)} precincts)")

    return {"precincts_manhattan": str(out_path), "n_precincts": len(manhattan_precincts_save), "skipped": False}
