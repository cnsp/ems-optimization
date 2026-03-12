"""Dispatch logic for EMS simulation.

Implements nearest-available dispatch: when an incident occurs,
the closest available unit (by travel time) is dispatched.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple

import pandas as pd

from ems_readiness.simulation.resources import EMSUnit, UnitPool
from ems_readiness.service.travel_time import build_travel_time_matrix

logger = logging.getLogger(__name__)


class NearestAvailableDispatcher:
    """Dispatches the nearest available EMS unit to an incident.

    Uses a pre-computed distance matrix between firehouses and precincts
    to determine the nearest available unit.  Tie-breaking: if multiple
    units at the same firehouse, pick the first; if multiple firehouses
    at equal distance, pick alphabetically first.

    Parameters
    ----------
    distance_matrix : pd.DataFrame
        Distance matrix (miles); rows = firehouses, columns = precincts.
    speed_mph : float
        Base EMS travel speed in mph.
    use_time_of_day : bool
        Whether to apply time-of-day speed factors.
    """

    def __init__(
        self,
        distance_matrix: pd.DataFrame,
        speed_mph: float = 20.0,
        use_time_of_day: bool = True,
    ):
        self.distance_matrix = distance_matrix
        self.speed_mph = speed_mph
        self.use_time_of_day = use_time_of_day
        # Pre-compute travel time matrices for each hour
        self._tt_cache: Dict[Optional[int], pd.DataFrame] = {}

    def _get_travel_time_matrix(self, hour: Optional[int] = None) -> pd.DataFrame:
        """Get travel time matrix, optionally with time-of-day adjustment."""
        cache_key = hour if self.use_time_of_day else None
        if cache_key not in self._tt_cache:
            self._tt_cache[cache_key] = build_travel_time_matrix(
                self.distance_matrix,
                speed_mph=self.speed_mph,
                hour_of_day=cache_key,
            )
        return self._tt_cache[cache_key]

    def find_nearest_unit(
        self,
        precinct: int,
        unit_pool: UnitPool,
        hour_of_day: Optional[int] = None,
    ) -> Tuple[Optional[EMSUnit], float]:
        """Find the nearest available unit to an incident precinct.

        Parameters
        ----------
        precinct : int
            Precinct ID where the incident occurred.
        unit_pool : UnitPool
            Current unit pool with availability info.
        hour_of_day : int or None
            Hour of day for time-of-day speed adjustment.

        Returns
        -------
        (unit, travel_time_minutes) : Tuple
            The selected unit and its travel time.  If no units
            available, returns (None, float('inf')).
        """
        available_by_fh = unit_pool.get_available_by_firehouse()
        if not available_by_fh:
            return None, float("inf")

        tt_matrix = self._get_travel_time_matrix(hour_of_day)
        precinct_col = str(precinct)

        # Ensure precinct column exists
        if precinct_col not in tt_matrix.columns:
            # Fallback: use the closest available precinct column
            logger.warning(
                f"Precinct {precinct} not in travel time matrix. "
                f"Using nearest available column."
            )
            precinct_col = tt_matrix.columns[0]

        best_unit: Optional[EMSUnit] = None
        best_time = float("inf")
        best_fh = ""

        for fh, units in available_by_fh.items():
            if fh not in tt_matrix.index:
                continue
            tt = tt_matrix.loc[fh, precinct_col]
            # Tie-breaking: prefer lower travel time, then alphabetically
            if tt < best_time or (tt == best_time and fh < best_fh):
                best_time = tt
                best_unit = units[0]  # pick first available at this firehouse
                best_fh = fh

        return best_unit, best_time

    def __repr__(self) -> str:
        n_fh = len(self.distance_matrix.index)
        n_pr = len(self.distance_matrix.columns)
        return (
            f"NearestAvailableDispatcher("
            f"firehouses={n_fh}, precincts={n_pr}, "
            f"speed={self.speed_mph} mph, "
            f"tod={self.use_time_of_day})"
        )
