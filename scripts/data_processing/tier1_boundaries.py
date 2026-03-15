"""Tier 1: Process geographic boundaries into pickle files.

Inputs:
    data/raw/manhattan_boundary.geojson
    data/raw/cbd_boundary.geojson

Outputs:
    data/processed/cache/manhattan_geom.pkl
    data/processed/cache/cbd_geom.pkl
"""
from __future__ import annotations

import pickle
from pathlib import Path


def process_boundaries(project_root: str | Path, force: bool = False) -> dict:
    """Load GeoJSON boundaries and save as pickle for fast reuse.

    Parameters
    ----------
    project_root : Path
        Project root directory.
    force : bool
        If True, regenerate even if outputs exist.

    Returns
    -------
    dict   Summary with keys 'manhattan_geom', 'cbd_geom', 'skipped'.
    """
    import geopandas as gpd

    project_root = Path(project_root)
    raw_dir = project_root / "data" / "raw"
    cache_dir = project_root / "data" / "processed" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Also keep copies in raw/ for backward compat with existing scripts
    manhattan_pkl = cache_dir / "manhattan_geom.pkl"
    cbd_pkl = cache_dir / "cbd_geom.pkl"
    manhattan_pkl_raw = raw_dir / "manhattan_geom.pkl"
    cbd_pkl_raw = raw_dir / "cbd_geom.pkl"

    if not force and manhattan_pkl.exists() and cbd_pkl.exists():
        print("  [skip] Boundary pickles already exist.")
        return {"manhattan_geom": str(manhattan_pkl), "cbd_geom": str(cbd_pkl), "skipped": True}

    # --- Manhattan ---
    src = raw_dir / "manhattan_boundary.geojson"
    if not src.exists():
        raise FileNotFoundError(f"Missing raw file: {src}")
    manhattan_gdf = gpd.read_file(src)
    manhattan_geom = manhattan_gdf.unary_union
    for p in (manhattan_pkl, manhattan_pkl_raw):
        with open(p, "wb") as f:
            pickle.dump(manhattan_geom, f)
    print(f"  Saved manhattan_geom.pkl  (bounds: {manhattan_gdf.total_bounds})")

    # --- CBD ---
    src = raw_dir / "cbd_boundary.geojson"
    if not src.exists():
        raise FileNotFoundError(f"Missing raw file: {src}")
    cbd_gdf = gpd.read_file(src)
    cbd_geom = cbd_gdf.unary_union
    for p in (cbd_pkl, cbd_pkl_raw):
        with open(p, "wb") as f:
            pickle.dump(cbd_geom, f)
    print(f"  Saved cbd_geom.pkl  (bounds: {cbd_gdf.total_bounds})")

    return {"manhattan_geom": str(manhattan_pkl), "cbd_geom": str(cbd_pkl), "skipped": False}


def load_geometries(project_root: str | Path) -> tuple:
    """Load cached geometry pickles. Regenerates if missing."""
    project_root = Path(project_root)
    cache_dir = project_root / "data" / "processed" / "cache"
    manhattan_pkl = cache_dir / "manhattan_geom.pkl"
    cbd_pkl = cache_dir / "cbd_geom.pkl"

    # Fall back to raw/ for backward compat
    if not manhattan_pkl.exists():
        manhattan_pkl = project_root / "data" / "raw" / "manhattan_geom.pkl"
    if not cbd_pkl.exists():
        cbd_pkl = project_root / "data" / "raw" / "cbd_geom.pkl"

    if not manhattan_pkl.exists() or not cbd_pkl.exists():
        print("  Geometry pickles missing -- regenerating...")
        process_boundaries(project_root, force=True)
        manhattan_pkl = cache_dir / "manhattan_geom.pkl"
        cbd_pkl = cache_dir / "cbd_geom.pkl"

    with open(manhattan_pkl, "rb") as f:
        manhattan_geom = pickle.load(f)
    with open(cbd_pkl, "rb") as f:
        cbd_geom = pickle.load(f)

    return manhattan_geom, cbd_geom
