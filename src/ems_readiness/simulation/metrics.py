"""Performance metrics collection for EMS simulation.

Tracks dispatch delays, response times, queue lengths,
unit utilizations, and coverage statistics.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from ems_readiness.simulation.entities import Incident

logger = logging.getLogger(__name__)


@dataclass
class MetricsCollector:
    """Collects and summarises simulation performance metrics.

    Attributes
    ----------
    response_threshold_minutes : float
        Primary target response time for coverage metric (default 8 min).
    additional_thresholds : tuple of float
        Additional coverage thresholds to compute (default includes 6 min
        per NYC's 6-minute EMS response requirement).
    """

    response_threshold_minutes: float = 8.0
    additional_thresholds: tuple = (6.0,)

    # Internal storage
    _incidents: List[Incident] = field(default_factory=list)
    _dispatch_delays: List[float] = field(default_factory=list)
    _response_times: List[float] = field(default_factory=list)
    _travel_times: List[float] = field(default_factory=list)
    _service_times: List[float] = field(default_factory=list)
    _queue_lengths: List[Tuple[float, int]] = field(default_factory=list)
    _incidents_queued: int = 0
    _total_incidents: int = 0

    def record_incident(self, incident: Incident) -> None:
        """Record a completed incident's metrics."""
        self._incidents.append(incident)
        self._total_incidents += 1

        if incident.dispatch_delay_minutes is not None:
            self._dispatch_delays.append(incident.dispatch_delay_minutes)

        if incident.response_time_minutes is not None:
            self._response_times.append(incident.response_time_minutes)

        if incident.travel_time_minutes is not None:
            self._travel_times.append(incident.travel_time_minutes)

        if incident.service_time_minutes is not None:
            self._service_times.append(incident.service_time_minutes)

        if incident.queued:
            self._incidents_queued += 1

    def record_queue_length(self, time: float, length: int) -> None:
        """Record a queue-length observation at a given simulation time."""
        self._queue_lengths.append((time, length))

    def get_summary_statistics(self) -> Dict:
        """Compute summary statistics from collected metrics.

        Returns
        -------
        dict
            Comprehensive metrics dictionary.
        """
        stats = {
            "total_incidents": self._total_incidents,
            "incidents_queued": self._incidents_queued,
            "queue_fraction": (
                self._incidents_queued / self._total_incidents
                if self._total_incidents > 0
                else 0.0
            ),
        }

        # Dispatch delay stats
        if self._dispatch_delays:
            dd = np.array(self._dispatch_delays)
            stats["dispatch_delay_mean"] = float(np.mean(dd))
            stats["dispatch_delay_median"] = float(np.median(dd))
            stats["dispatch_delay_p90"] = float(np.percentile(dd, 90))
            stats["dispatch_delay_max"] = float(np.max(dd))
        else:
            stats["dispatch_delay_mean"] = 0.0
            stats["dispatch_delay_median"] = 0.0
            stats["dispatch_delay_p90"] = 0.0
            stats["dispatch_delay_max"] = 0.0

        # Response time stats
        if self._response_times:
            rt = np.array(self._response_times)
            stats["response_time_mean"] = float(np.mean(rt))
            stats["response_time_median"] = float(np.median(rt))
            stats["response_time_p90"] = float(np.percentile(rt, 90))
            stats["response_time_max"] = float(np.max(rt))
            stats["response_time_std"] = float(np.std(rt))
            # Coverage: fraction within primary threshold
            within = np.sum(rt <= self.response_threshold_minutes)
            stats["coverage_fraction"] = float(within / len(rt))
            stats["incidents_within_threshold"] = int(within)
            # Additional coverage thresholds (e.g., 6-min NYC requirement)
            for thresh in self.additional_thresholds:
                key = f"coverage_{int(thresh)}min"
                within_t = np.sum(rt <= thresh)
                stats[key] = float(within_t / len(rt))
        else:
            stats["response_time_mean"] = 0.0
            stats["response_time_median"] = 0.0
            stats["response_time_p90"] = 0.0
            stats["response_time_max"] = 0.0
            stats["response_time_std"] = 0.0
            stats["coverage_fraction"] = 0.0
            stats["incidents_within_threshold"] = 0
            for thresh in self.additional_thresholds:
                key = f"coverage_{int(thresh)}min"
                stats[key] = 0.0

        # Travel time stats
        if self._travel_times:
            tt = np.array(self._travel_times)
            stats["travel_time_mean"] = float(np.mean(tt))
            stats["travel_time_median"] = float(np.median(tt))
        else:
            stats["travel_time_mean"] = 0.0
            stats["travel_time_median"] = 0.0

        # Service time stats
        if self._service_times:
            st = np.array(self._service_times)
            stats["service_time_mean"] = float(np.mean(st))
            stats["service_time_median"] = float(np.median(st))
        else:
            stats["service_time_mean"] = 0.0
            stats["service_time_median"] = 0.0

        # Queue length stats (time-weighted average)
        if self._queue_lengths:
            stats["queue_length_max"] = max(ql for _, ql in self._queue_lengths)
            stats["queue_length_tw_avg"] = self._time_weighted_avg_queue()
        else:
            stats["queue_length_max"] = 0
            stats["queue_length_tw_avg"] = 0.0

        return stats

    def _time_weighted_avg_queue(self) -> float:
        """Compute time-weighted average queue length."""
        if len(self._queue_lengths) < 2:
            return 0.0
        total_area = 0.0
        for i in range(len(self._queue_lengths) - 1):
            t1, q1 = self._queue_lengths[i]
            t2, _ = self._queue_lengths[i + 1]
            total_area += q1 * (t2 - t1)
        total_time = self._queue_lengths[-1][0] - self._queue_lengths[0][0]
        if total_time <= 0:
            return 0.0
        return total_area / total_time

    def get_incident_log(self) -> pd.DataFrame:
        """Return all recorded incidents as a DataFrame."""
        if not self._incidents:
            return pd.DataFrame()
        records = []
        for inc in self._incidents:
            records.append({
                "id": inc.id,
                "arrival_time": inc.arrival_time,
                "precinct": inc.precinct,
                "assigned_unit": inc.assigned_unit,
                "assigned_firehouse": inc.assigned_firehouse,
                "dispatch_time": inc.dispatch_time,
                "service_start_time": inc.service_start_time,
                "completion_time": inc.completion_time,
                "dispatch_delay_minutes": inc.dispatch_delay_minutes,
                "travel_time_minutes": inc.travel_time_minutes,
                "service_time_minutes": inc.service_time_minutes,
                "response_time_minutes": inc.response_time_minutes,
                "total_time_minutes": inc.total_time_minutes,
                "queued": inc.queued,
            })
        return pd.DataFrame(records)

    def reset(self) -> None:
        """Clear all collected metrics."""
        self._incidents.clear()
        self._dispatch_delays.clear()
        self._response_times.clear()
        self._travel_times.clear()
        self._service_times.clear()
        self._queue_lengths.clear()
        self._incidents_queued = 0
        self._total_incidents = 0

    def __repr__(self) -> str:
        return (
            f"MetricsCollector(incidents={self._total_incidents}, "
            f"threshold={self.response_threshold_minutes} min)"
        )
