"""Distance calculation utilities.

Provides Haversine (great-circle) distance between geographic coordinates.
This is the foundational metric for the travel-time proxy used throughout
the EMS simulation.

References
----------
- Haversine formula: https://en.wikipedia.org/wiki/Haversine_formula
- Earth radius ≈ 3958.8 miles (mean radius, WGS-84).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

EARTH_RADIUS_MILES = 3_958.8  # mean Earth radius in miles (WGS-84)


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


def build_distance_matrix(
    origins: pd.DataFrame,
    destinations: pd.DataFrame,
    origin_lat: str = "Latitude",
    origin_lon: str = "Longitude",
    origin_id: str = "FacilityName",
    dest_lat: str = "centroid_lat",
    dest_lon: str = "centroid_lon",
    dest_id: str = "Precinct",
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

    Returns
    -------
    pd.DataFrame
        Shape (n_origins, n_destinations) with Haversine distances in miles.
        Index = origin ids, columns = destination ids.
    """
    o_lat = origins[origin_lat].values[:, None]
    o_lon = origins[origin_lon].values[:, None]
    d_lat = destinations[dest_lat].values[None, :]
    d_lon = destinations[dest_lon].values[None, :]

    dist = haversine(o_lat, o_lon, d_lat, d_lon)

    return pd.DataFrame(
        dist,
        index=origins[origin_id].values,
        columns=destinations[dest_id].values,
    )
