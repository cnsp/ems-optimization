"""Baseline (non-optimised) allocation policies.

These do *not* require a solver and serve as reference benchmarks.

Nomenclature (standardised v2.0):
    P0  — Spatially-stratified uniform allocation (``spatially_stratified_allocation``).
           This is the **canonical baseline** used in all Production V2 results and the
           final technical report.  Firehouses are selected via latitude-based spatial
           stratification to ensure even geographic coverage across Manhattan.
    P1  — Demand-proportional allocation (``demand_proportional_allocation``).
    P2  — Demand-weighted MIP-optimised allocation (see ``models.py``).

The legacy ``uniform_allocation`` function (round-robin across *all* 48 firehouses
without geographic awareness) is retained for backward-compatibility but is **deprecated**
as a baseline comparator.  It was the original P0 in Production V1; that role has been
superseded by ``spatially_stratified_allocation`` in Production V2.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import warnings
from pathlib import Path
from typing import Optional, Literal
from itertools import combinations


def uniform_allocation(
    firehouses: pd.Index,
    K: int,
    capacity: int = 5,
) -> pd.Series:
    """Legacy uniform allocation (DEPRECATED — use ``spatially_stratified_allocation`` for P0).

    Distributes K units as evenly as possible across *all* firehouses via
    round-robin.  This was the original P0 in Production V1 but is
    **deprecated** as a baseline because it lacks geographic awareness and
    produces CBD-biased placement when firehouses are ordered by database
    index.  Retained for backward-compatibility and historical comparisons.

    .. deprecated:: 2.0
        Use :func:`spatially_stratified_allocation` (the canonical P0 baseline)
        instead.

    Parameters
    ----------
    firehouses : pd.Index
        Firehouse identifiers.
    K : int
        Total number of units.
    capacity : int
        Maximum units per firehouse.

    Returns
    -------
    pd.Series
        Firehouse -> number of units.
    """
    warnings.warn(
        "uniform_allocation() is deprecated as the P0 baseline. "
        "Use spatially_stratified_allocation() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    n = len(firehouses)
    base = min(K // n, capacity)
    remainder = K - base * n

    alloc = np.full(n, base, dtype=int)
    # distribute remainder one-by-one respecting capacity
    idx = 0
    while remainder > 0 and idx < n:
        if alloc[idx] < capacity:
            alloc[idx] += 1
            remainder -= 1
        idx += 1

    return pd.Series(alloc, index=firehouses, name="units_allocated")


def demand_proportional_allocation(
    travel_time: pd.DataFrame,
    demand: pd.Series,
    K: int,
    capacity: int = 5,
) -> pd.Series:
    """P1 – Demand-proportional allocation.

    Each firehouse receives units proportional to the total demand it is
    *nearest* to (i.e., for each precinct, credit goes to the closest
    firehouse).  The raw proportions are then scaled to sum to K and
    rounded to integers, respecting capacity constraints.

    Parameters
    ----------
    travel_time : pd.DataFrame
        Travel-time matrix (rows = firehouses, columns = precincts).
    demand : pd.Series
        Demand per precinct.
    K : int
        Total number of units.
    capacity : int
        Maximum units per firehouse.

    Returns
    -------
    pd.Series
        Firehouse -> number of units.
    """
    firehouses = travel_time.index
    precincts = [p for p in travel_time.columns if p in demand.index]

    # Credit demand to nearest firehouse
    credit = pd.Series(0.0, index=firehouses)
    for j in precincts:
        nearest = travel_time[j].idxmin()
        credit[nearest] += demand[j]

    # Proportional scaling
    total_credit = credit.sum()
    if total_credit == 0:
        return uniform_allocation(firehouses, K, capacity)

    raw = (credit / total_credit) * K

    # Integer rounding with capacity enforcement
    alloc = np.floor(raw).astype(int)
    alloc = np.minimum(alloc, capacity)
    remainder = K - alloc.sum()

    # Distribute remainder by largest fractional part
    fracs = raw - alloc
    order = fracs.sort_values(ascending=False).index
    for fh in order:
        if remainder <= 0:
            break
        if alloc[fh] < capacity:
            alloc[fh] += 1
            remainder -= 1

    return pd.Series(alloc, index=firehouses, name="units_allocated")


# ---------------------------------------------------------------------------
#  Spatially-stratified baseline allocation
# ---------------------------------------------------------------------------

def _load_firehouses(data_dir: Optional[str | Path] = None) -> pd.DataFrame:
    """Load the firehouse CSV with lat/lon and in_cbd columns.

    Parameters
    ----------
    data_dir : str or Path, optional
        Path to the processed data directory.  If *None*, defaults to
        ``<project_root>/data/processed``.

    Returns
    -------
    pd.DataFrame
        Indexed by FacilityName, with Latitude, Longitude, in_cbd columns.
    """
    if data_dir is None:
        data_dir = Path(__file__).resolve().parents[3] / "data" / "processed"
    else:
        data_dir = Path(data_dir)
    df = pd.read_csv(data_dir / "firehouses_manhattan.csv")
    # Normalise in_cbd to bool
    df["in_cbd"] = df["in_cbd"].astype(str).str.strip().str.lower() == "true"
    df = df.set_index("FacilityName")
    return df


def _haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Haversine distance in miles between two points."""
    R = 3958.8  # Earth radius in miles
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = (np.sin(dlat / 2) ** 2
         + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2))
         * np.sin(dlon / 2) ** 2)
    return R * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))


def _select_latitude(df: pd.DataFrame, K: int) -> list[str]:
    """Select K firehouses at regular latitude intervals (north→south)."""
    sorted_df = df.sort_values("Latitude")
    n = len(sorted_df)
    if K >= n:
        return sorted_df.index.tolist()
    # Evenly-spaced indices in [0, n-1]
    indices = np.round(np.linspace(0, n - 1, K)).astype(int)
    return sorted_df.index[indices].tolist()


def _select_grid(df: pd.DataFrame, K: int) -> list[str]:
    """Select K firehouses via grid-based stratification.

    Divides Manhattan's bounding box into a grid and selects one firehouse
    per grid cell (the one closest to the cell centroid).  Grid dimensions
    are chosen so the total number of cells ≈ K, with aspect ratio matching
    Manhattan's elongated shape.
    """
    lat_range = df["Latitude"].max() - df["Latitude"].min()
    lon_range = df["Longitude"].max() - df["Longitude"].min()

    # Manhattan is roughly 3× taller than wide
    aspect = lat_range / max(lon_range, 1e-9)
    n_cols = max(1, int(np.round(np.sqrt(K / aspect))))
    n_rows = max(1, int(np.round(K / n_cols)))

    # Adjust so n_rows * n_cols >= K
    while n_rows * n_cols < K:
        n_rows += 1

    lat_bins = np.linspace(df["Latitude"].min(), df["Latitude"].max(), n_rows + 1)
    lon_bins = np.linspace(df["Longitude"].min(), df["Longitude"].max(), n_cols + 1)

    selected: list[str] = []
    for r in range(n_rows):
        for c in range(n_cols):
            cell_mask = (
                (df["Latitude"] >= lat_bins[r])
                & (df["Latitude"] < lat_bins[r + 1] + 1e-9)
                & (df["Longitude"] >= lon_bins[c])
                & (df["Longitude"] < lon_bins[c + 1] + 1e-9)
            )
            cell = df[cell_mask]
            if cell.empty:
                continue
            # Pick firehouse closest to cell centroid
            clat = (lat_bins[r] + lat_bins[r + 1]) / 2
            clon = (lon_bins[c] + lon_bins[c + 1]) / 2
            dists = cell.apply(
                lambda row: _haversine_miles(row["Latitude"], row["Longitude"], clat, clon),
                axis=1,
            )
            selected.append(dists.idxmin())

    # Deduplicate (a firehouse could be nearest to multiple centroids)
    seen: set[str] = set()
    unique: list[str] = []
    for s in selected:
        if s not in seen:
            unique.append(s)
            seen.add(s)

    # If we have more than K, trim from the densest cells; if fewer, add nearest unselected
    if len(unique) > K:
        unique = unique[:K]
    elif len(unique) < K:
        remaining = [fh for fh in df.index if fh not in seen]
        # Add remaining by proximity to already-selected centroids (farthest-first)
        for fh in remaining:
            if len(unique) >= K:
                break
            unique.append(fh)
            seen.add(fh)

    return unique


def _select_maximin(df: pd.DataFrame, K: int) -> list[str]:
    """Select K firehouses that maximize the minimum pairwise distance.

    Uses a greedy farthest-point heuristic:
    1. Start with the southernmost firehouse
    2. Iteratively add the firehouse farthest from the current selection
    """
    n = len(df)
    if K >= n:
        return df.index.tolist()

    lats = df["Latitude"].values
    lons = df["Longitude"].values

    # Pre-compute pairwise distance matrix
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            d = _haversine_miles(lats[i], lons[i], lats[j], lons[j])
            dist_matrix[i, j] = d
            dist_matrix[j, i] = d

    # Start with southernmost
    start_idx = int(np.argmin(lats))
    selected_indices = [start_idx]

    for _ in range(K - 1):
        # For each unselected, find its min distance to any selected
        min_dists = np.full(n, np.inf)
        for s in selected_indices:
            min_dists = np.minimum(min_dists, dist_matrix[s])
        # Zero out already selected
        for s in selected_indices:
            min_dists[s] = -1.0
        # Pick the one with the largest min-distance
        next_idx = int(np.argmax(min_dists))
        selected_indices.append(next_idx)

    return df.index[selected_indices].tolist()


def spatially_stratified_allocation(
    K: int,
    method: Literal["latitude", "grid", "maximin"] = "latitude",
    capacity: int = 5,
    data_dir: Optional[str | Path] = None,
) -> pd.Series:
    """P0 — Spatially-stratified uniform allocation (canonical baseline).

    Selects firehouses at roughly regular spatial intervals across
    Manhattan's geography, then distributes K units evenly among them.
    This ensures geographic coverage and avoids the CBD bias of the legacy
    index-based round-robin (``uniform_allocation``).

    Parameters
    ----------
    K : int
        Total number of units to allocate.
    method : {'latitude', 'grid', 'maximin'}
        Spatial selection strategy:

        - **latitude** – Sort by latitude (south→north), pick every Nth
          firehouse for even north-south spacing.
        - **grid** – Divide the bounding box into a grid, pick one
          firehouse per cell (closest to centroid).
        - **maximin** – Greedy farthest-point selection that maximises the
          minimum pairwise distance (optimal spatial dispersion).
    capacity : int, default 5
        Maximum units per firehouse.
    data_dir : str or Path, optional
        Path to ``data/processed/`` directory containing
        ``firehouses_manhattan.csv``.

    Returns
    -------
    pd.Series
        Firehouse -> number of units allocated.
        Index contains *all* 48 firehouses; unselected ones have 0.
    """
    df = _load_firehouses(data_dir)

    # Select which firehouses get units
    n_stations = min(K, len(df))  # At most K stations (1 unit each minimum)
    if method == "latitude":
        selected = _select_latitude(df, n_stations)
    elif method == "grid":
        selected = _select_grid(df, n_stations)
    elif method == "maximin":
        selected = _select_maximin(df, n_stations)
    else:
        raise ValueError(f"Unknown method: {method!r}. Choose from latitude, grid, maximin.")

    # Allocate units evenly among selected firehouses
    n_sel = len(selected)
    base = min(K // n_sel, capacity)
    remainder = K - base * n_sel

    alloc = pd.Series(0, index=df.index, name="units_allocated")
    for fh in selected:
        alloc[fh] = base
    # Distribute remainder round-robin among selected
    for fh in selected:
        if remainder <= 0:
            break
        if alloc[fh] < capacity:
            alloc[fh] += 1
            remainder -= 1

    return alloc


def spatial_stratification_analysis(
    K: int = 20,
    data_dir: Optional[str | Path] = None,
) -> dict:
    """Run all 3 stratification methods and return a comparison dict.

    Returns
    -------
    dict
        Keys: 'latitude', 'grid', 'maximin'.
        Each value is a dict with:
        - 'selected' : list of firehouse names
        - 'allocation' : pd.Series
        - 'n_cbd' / 'n_non_cbd' : int
        - 'pct_cbd' : float
        - 'mean_nn_dist' : float (mean nearest-neighbor distance in miles)
        - 'coverage_std' : float (std of latitude spacing – uniformity)
    """
    df = _load_firehouses(data_dir)
    results = {}

    for method in ("latitude", "grid", "maximin"):
        alloc = spatially_stratified_allocation(K, method=method, data_dir=data_dir)
        selected = alloc[alloc > 0].index.tolist()
        sel_df = df.loc[selected]

        # CBD distribution
        n_cbd = int(sel_df["in_cbd"].sum())
        n_non = len(selected) - n_cbd

        # Mean nearest-neighbor distance
        lats = sel_df["Latitude"].values
        lons = sel_df["Longitude"].values
        nn_dists = []
        for i in range(len(lats)):
            dists = [
                _haversine_miles(lats[i], lons[i], lats[j], lons[j])
                for j in range(len(lats))
                if i != j
            ]
            nn_dists.append(min(dists) if dists else 0.0)
        mean_nn = float(np.mean(nn_dists))

        # Latitude spacing uniformity
        sorted_lats = np.sort(lats)
        spacings = np.diff(sorted_lats)
        coverage_std = float(np.std(spacings)) if len(spacings) > 0 else 0.0

        results[method] = {
            "selected": selected,
            "allocation": alloc,
            "n_selected": len(selected),
            "n_cbd": n_cbd,
            "n_non_cbd": n_non,
            "pct_cbd": round(100 * n_cbd / len(selected), 1) if selected else 0,
            "mean_nn_dist": round(mean_nn, 4),
            "coverage_std": round(coverage_std, 6),
        }

    return results