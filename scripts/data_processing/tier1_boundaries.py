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

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable=None, *args, **kwargs):
        return iterable


def process_boundaries(project_root: str | Path, force: bool = False, cache_mgr=None) -> dict:
    """Load GeoJSON boundaries and save as pickle for fast reuse.

    Parameters
    ----------
    project_root : Path
        Project root directory.
    force : bool
        If True, regenerate even if outputs exist.
    cache_mgr : CacheManager, optional
        If provided, check/update cache validity.

    Returns
    -------
    dict   Summary with keys 'manhattan_geom', 'cbd_geom', 'skipped'.
    """
    import geopandas as gpd

    project_root = Path(project_root)
    raw_dir = project_root / "data" / "raw"
    cache_dir = project_root / "data" / "processed" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    manhattan_pkl = cache_dir / "manhattan_geom.pkl"
    cbd_pkl = cache_dir / "cbd_geom.pkl"
    manhattan_pkl_raw = raw_dir / "manhattan_geom.pkl"
    cbd_pkl_raw = raw_dir / "cbd_geom.pkl"

    # Cache check
    if not force and cache_mgr and cache_mgr.is_valid("tier1_boundaries"):
        print("  [cache] Boundary pickles unchanged -- using cached data.")
        return {"manhattan_geom": str(manhattan_pkl), "cbd_geom": str(cbd_pkl), "skipped": True}

    if not force and manhattan_pkl.exists() and cbd_pkl.exists():
        print("  [skip] Boundary pickles already exist.")
        return {"manhattan_geom": str(manhattan_pkl), "cbd_geom": str(cbd_pkl), "skipped": True}

    boundaries = [
        ("manhattan_boundary.geojson", manhattan_pkl, manhattan_pkl_raw, "manhattan_geom.pkl"),
        ("cbd_boundary.geojson", cbd_pkl, cbd_pkl_raw, "cbd_geom.pkl"),
    ]

    for src_name, pkl_path, pkl_raw, label in tqdm(boundaries, desc="  Boundaries", leave=False):
        src = raw_dir / src_name
        if not src.exists():
            raise FileNotFoundError(f"Missing raw file: {src}")
        gdf = gpd.read_file(src)
        geom = gdf.unary_union
        for p in (pkl_path, pkl_raw):
            with open(p, "wb") as f:
                pickle.dump(geom, f)
        print(f"  Saved {label}  (bounds: {gdf.total_bounds})")

    if cache_mgr:
        cache_mgr.update("tier1_boundaries")

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
