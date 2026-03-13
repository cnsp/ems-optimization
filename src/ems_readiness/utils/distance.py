"""Distance calculation utilities.

Provides Haversine (great-circle) and Manhattan (taxicab) distance between
geographic coordinates. Both are used as travel-time proxies in the EMS
simulation for comparative analysis.

References
----------
- Haversine formula: https://en.wikipedia.org/wiki/Haversine_formula
- Manhattan distance: https://en.wikipedia.org/wiki/Taxicab_geometry
- Earth radius ≈ 3958.8 miles (mean radius, WGS-84).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

EARTH_RADIUS_MILES = 3_958.8  # mean Earth radius in miles (WGS-84)
MILES_PER_DEGREE_LAT = 69.0   # approximate miles per degree of latitude
MILES_PER_DEGREE_LON_NYC = 52.3  # miles per degree of longitude at ~40.75°N


def haversine(
    lat1: float | np.ndarray,
    lon1: float | np.ndarray,
    lat2: float | np.ndarray,
    lon2: float | np.ndarray,
) -> float | np.ndarray:
    """Compute Haversine (great-circle) distance in **miles**.

    Parameters
    ----------
    lat1, lon1 : float or array-like
        Latitude / longitude of origin(s) in decimal degrees.
    lat2, lon2 : float or array-like
        Latitude / longitude of destination(s) in decimal degrees.

    Returns
    -------
    float or np.ndarray
        Distance(s) in miles.
    """
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    return 2.0 * EARTH_RADIUS_MILES * np.arcsin(np.sqrt(a))


def manhattan_distance(
    lat1: float | np.ndarray,
    lon1: float | np.ndarray,
    lat2: float | np.ndarray,
    lon2: float | np.ndarray,
    miles_per_deg_lat: float = MILES_PER_DEGREE_LAT,
    miles_per_deg_lon: float = MILES_PER_DEGREE_LON_NYC,
) -> float | np.ndarray:
    """Compute Manhattan (taxicab / L1) distance in **miles**.

    More realistic than Haversine for grid-based street networks such as
    Manhattan, where travel follows a north–south / east–west grid rather
    than a straight line.

    Parameters
    ----------
    lat1, lon1 : float or array-like
        Latitude / longitude of origin(s) in decimal degrees.
    lat2, lon2 : float or array-like
        Latitude / longitude of destination(s) in decimal degrees.
    miles_per_deg_lat : float
        Conversion factor for latitude degrees → miles (≈ 69.0).
    miles_per_deg_lon : float
        Conversion factor for longitude degrees → miles at the study
        area's latitude (≈ 52.3 at 40.75°N for Manhattan).

    Returns
    -------
    float or np.ndarray
        Distance(s) in miles.

    Notes
    -----
    ``d = |Δlat| × miles_per_deg_lat + |Δlon| × miles_per_deg_lon``

    The longitude conversion factor is pre-computed for Manhattan's average
    latitude (~40.75°N) using the formula:
        miles_per_deg_lon = cos(40.75° × π/180) × 69.0 ≈ 52.3
    """
    dlat = np.abs(np.asarray(lat2, dtype=float) - np.asarray(lat1, dtype=float))
    dlon = np.abs(np.asarray(lon2, dtype=float) - np.asarray(lon1, dtype=float))
    return dlat * miles_per_deg_lat + dlon * miles_per_deg_lon


def build_distance_matrix(
    origins: pd.DataFrame,
    destinations: pd.DataFrame,
    origin_lat: str = "Latitude",
    origin_lon: str = "Longitude",
    origin_id: str = "FacilityName",
    dest_lat: str = "centroid_lat",
    dest_lon: str = "centroid_lon",
    dest_id: str = "Precinct",
    metric: str = "haversine",
) -> pd.DataFrame:
    """Build a pairwise distance matrix (origins × destinations).

    Parameters
    ----------
    origins : pd.DataFrame
        Must contain columns for id, latitude, longitude.
    destinations : pd.DataFrame
        Must contain columns for id, latitude, longitude.
    origin_lat, origin_lon, origin_id : str
        Column names in *origins*.
    dest_lat, dest_lon, dest_id : str
        Column names in *destinations*.
    metric : str
        Distance metric to use: ``"haversine"`` (default) or ``"manhattan"``.

    Returns
    -------
    pd.DataFrame
        Shape (n_origins, n_destinations) with distances in miles.
        Index = origin ids, columns = destination ids.
    """
    o_lat = origins[origin_lat].values[:, None]
    o_lon = origins[origin_lon].values[:, None]
    d_lat = destinations[dest_lat].values[None, :]
    d_lon = destinations[dest_lon].values[None, :]

    if metric == "manhattan":
        dist = manhattan_distance(o_lat, o_lon, d_lat, d_lon)
    elif metric == "haversine":
        dist = haversine(o_lat, o_lon, d_lat, d_lon)
    else:
        raise ValueError(f"Unknown metric '{metric}'. Use 'haversine' or 'manhattan'.")

    return pd.DataFrame(
        dist,
        index=origins[origin_id].values,
        columns=destinations[dest_id].values,
    )
