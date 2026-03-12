"""Simulation entities – data classes for incidents and events.

Each incident flows through the following lifecycle:
    arrival → queue → dispatch → travel → on-scene → complete
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Incident:
    """Represents a single EMS incident (call for service).

    Attributes
    ----------
    id : int
        Unique incident identifier.
    arrival_time : float
        Simulation time (hours) when the call arrives.
    precinct : int
        Precinct where the incident occurs.
    assigned_unit : str or None
        ID of the EMS unit dispatched (set at dispatch).
    assigned_firehouse : str or None
        Home firehouse of the assigned unit.
    dispatch_time : float or None
        Simulation time when a unit is dispatched.
    service_start_time : float or None
        Simulation time when on-scene service begins (after travel).
    completion_time : float or None
        Simulation time when the unit becomes available again.
    travel_time_minutes : float or None
        Travel time from firehouse to incident (minutes).
    service_time_minutes : float or None
        On-scene service duration (minutes).
    dispatch_delay_minutes : float or None
        Time spent waiting in queue + fixed dispatch delay (minutes).
    queued : bool
        Whether this incident had to wait for a unit.
    """

    id: int
    arrival_time: float
    precinct: int
    assigned_unit: Optional[str] = None
    assigned_firehouse: Optional[str] = None
    dispatch_time: Optional[float] = None
    service_start_time: Optional[float] = None
    completion_time: Optional[float] = None
    travel_time_minutes: Optional[float] = None
    service_time_minutes: Optional[float] = None
    dispatch_delay_minutes: Optional[float] = None
    queued: bool = False

    @property
    def response_time_minutes(self) -> Optional[float]:
        """Total response time from arrival to on-scene (minutes)."""
        if self.service_start_time is not None and self.arrival_time is not None:
            return (self.service_start_time - self.arrival_time) * 60.0
        return None

    @property
    def total_time_minutes(self) -> Optional[float]:
        """Total time from arrival to completion (minutes)."""
        if self.completion_time is not None and self.arrival_time is not None:
            return (self.completion_time - self.arrival_time) * 60.0
        return None
