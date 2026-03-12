"""EMS unit resources and pool management.

Manages a pool of EMS units allocated to firehouses, tracking
their availability status for dispatch.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

import pandas as pd


class UnitStatus(Enum):
    """Possible states for an EMS unit."""
    AVAILABLE = "available"
    DISPATCHED = "dispatched"
    ON_SCENE = "on_scene"
    RETURNING = "returning"


@dataclass
class EMSUnit:
    """Represents a single EMS ambulance unit.

    Attributes
    ----------
    id : str
        Unique unit identifier (e.g., 'Engine_4_1').
    home_firehouse : str
        Firehouse name where this unit is stationed.
    status : UnitStatus
        Current operational status.
    """

    id: str
    home_firehouse: str
    status: UnitStatus = UnitStatus.AVAILABLE
    incidents_served: int = 0
    total_busy_time: float = 0.0  # hours

    def dispatch(self) -> None:
        """Mark unit as dispatched."""
        self.status = UnitStatus.DISPATCHED

    def arrive_on_scene(self) -> None:
        """Mark unit as on-scene."""
        self.status = UnitStatus.ON_SCENE

    def return_available(self, busy_duration_hours: float) -> None:
        """Mark unit as available and update statistics."""
        self.status = UnitStatus.AVAILABLE
        self.incidents_served += 1
        self.total_busy_time += busy_duration_hours

    @property
    def is_available(self) -> bool:
        return self.status == UnitStatus.AVAILABLE


class UnitPool:
    """Manages a pool of EMS units across firehouses.

    Parameters
    ----------
    allocation : pd.Series
        Firehouse name → number of units allocated.
    """

    def __init__(self, allocation: pd.Series):
        self.allocation = allocation
        self._units: Dict[str, List[EMSUnit]] = {}
        self._all_units: Dict[str, EMSUnit] = {}
        self._total_units = 0

        for firehouse, n_units in allocation.items():
            n = int(n_units)
            if n <= 0:
                continue
            self._units[firehouse] = []
            for i in range(n):
                uid = f"{firehouse}_unit_{i}"
                unit = EMSUnit(id=uid, home_firehouse=firehouse)
                self._units[firehouse].append(unit)
                self._all_units[uid] = unit
                self._total_units += 1

    @property
    def total_units(self) -> int:
        """Total number of units in the pool."""
        return self._total_units

    def get_available_units(self) -> List[EMSUnit]:
        """Return all currently available units."""
        return [u for u in self._all_units.values() if u.is_available]

    def get_available_by_firehouse(self) -> Dict[str, List[EMSUnit]]:
        """Return available units grouped by firehouse."""
        result: Dict[str, List[EMSUnit]] = {}
        for fh, units in self._units.items():
            avail = [u for u in units if u.is_available]
            if avail:
                result[fh] = avail
        return result

    def count_available(self) -> int:
        """Count of currently available units."""
        return sum(1 for u in self._all_units.values() if u.is_available)

    def get_unit(self, unit_id: str) -> Optional[EMSUnit]:
        """Look up a unit by ID."""
        return self._all_units.get(unit_id)

    def get_utilizations(self, horizon_hours: float) -> Dict[str, float]:
        """Compute utilization (fraction of time busy) for each unit."""
        if horizon_hours <= 0:
            return {}
        return {
            uid: unit.total_busy_time / horizon_hours
            for uid, unit in self._all_units.items()
        }

    def get_firehouse_utilizations(self, horizon_hours: float) -> Dict[str, float]:
        """Average utilization by firehouse."""
        if horizon_hours <= 0:
            return {}
        result = {}
        for fh, units in self._units.items():
            if units:
                avg_util = sum(u.total_busy_time for u in units) / (
                    len(units) * horizon_hours
                )
                result[fh] = avg_util
        return result

    def __repr__(self) -> str:
        return (
            f"UnitPool(total={self._total_units}, "
            f"available={self.count_available()}, "
            f"firehouses={len(self._units)})"
        )
