"""Travel-time proxy for EMS response.

Assumptions
-----------
* Travel time = Haversine distance / average speed.
* Default average speed: 20 mph (urban EMS with lights & sirens).
* Optional time-of-day speed multiplier to capture peak / off-peak variation.

Limitations
-----------
* Does not model road-network routing or real-time congestion.
* Haversine underestimates true road distance (typical Manhattan detour
  factor ≈ 1.3–1.4 for grid streets, but we keep the simpler proxy per
  the project charter).

References
----------
- Goldberg (2004), "Operations Research Models for the Deployment of
  Emergency Services Vehicles".
- NYC DOT average traffic speed ≈ 12–25 mph in Manhattan.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ems_readiness.utils.distance import haversine

# ── Default configuration ────────────────────────────────────────────
DEFAULT_SPEED_MPH = 20.0  # urban EMS average with lights & sirens

# Time-of-day speed multipliers (hour → factor applied to base speed).
# Values > 1 mean faster travel; < 1 mean slower.
# Derived from NYC DOT speed reports; used only when time_of_day is supplied.
TOD_SPEED_FACTORS: dict[int, float] = {
    # Overnight (00–06): less traffic → faster
    **{h: 1.30 for h in range(0, 6)},
    # AM peak (06–10): commuter traffic → slower
    **{h: 0.75 for h in range(6, 10)},
    # Midday (10–16): moderate
    **{h: 0.90 for h in range(10, 16)},
    # PM peak (16–20): commuter traffic → slower
    **{h: 0.70 for h in range(16, 20)},
    # Evening (20–24): lighter traffic
    **{h: 1.10 for h in range(20, 24)},
}


def travel_time_minutes(
    distance_miles: float | np.ndarray,
    speed_mph: float = DEFAULT_SPEED_MPH,
    hour_of_day: int | None = None,
) -> float | np.ndarray:
    """Convert distance to travel time in **minutes**.

    Parameters
    ----------
    distance_miles : float or array-like
        Haversine distance(s) in miles.
    speed_mph : float
        Base average speed in miles per hour.
    hour_of_day : int or None
        If supplied (0–23), a time-of-day speed factor is applied.

    Returns
    -------
    float or np.ndarray
        Estimated travel time(s) in minutes.
    """
    effective_speed = speed_mph
    if hour_of_day is not None:
        factor = TOD_SPEED_FACTORS.get(int(hour_of_day) % 24, 1.0)
        effective_speed = speed_mph * factor
    return (distance_miles / effective_speed) * 60.0


def travel_time_from_coords(
    lat1: float, lon1: float,
    lat2: float, lon2: float,
    speed_mph: float = DEFAULT_SPEED_MPH,
    hour_of_day: int | None = None,
) -> float:
    """End-to-end: coordinates → Haversine distance → travel time (min)."""
    dist = haversine(lat1, lon1, lat2, lon2)
    return travel_time_minutes(dist, speed_mph=speed_mph, hour_of_day=hour_of_day)


def build_travel_time_matrix(
    distance_matrix: pd.DataFrame,
    speed_mph: float = DEFAULT_SPEED_MPH,
    hour_of_day: int | None = None,
) -> pd.DataFrame:
    """Convert a distance matrix (miles) into a travel-time matrix (minutes)."""
    tt = travel_time_minutes(
        distance_matrix.values, speed_mph=speed_mph, hour_of_day=hour_of_day
    )
    return pd.DataFrame(tt, index=distance_matrix.index, columns=distance_matrix.columns)
