"""Advanced simulation engine tests.

Covers:
- Metrics collector correctness
- UnitPool resource management
- Incident entity lifecycle
- Multi-firehouse allocation behaviour
- Utilisation accounting
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from ems_readiness.simulation.entities import Incident
from ems_readiness.simulation.metrics import MetricsCollector
from ems_readiness.simulation.resources import EMSUnit, UnitPool, UnitStatus


# ── MetricsCollector Tests ────────────────────────────────────────


class TestMetricsCollector:
    """Verify that the metrics collector computes correct statistics."""

    def test_empty_collector(self):
        """Empty collector should return zero summary."""
        mc = MetricsCollector(response_threshold_minutes=8.0)
        s = mc.get_summary_statistics()
        assert s["total_incidents"] == 0
        assert s["response_time_mean"] == 0.0
        assert s["coverage_fraction"] == 0.0

    def test_single_incident(self):
        """Recording one incident should update all relevant stats."""
        mc = MetricsCollector(response_threshold_minutes=8.0)
        inc = Incident(
            id=1, arrival_time=0.0, precinct=1,
            dispatch_time=0.01, service_start_time=0.05,
            completion_time=0.5,
            travel_time_minutes=2.4, service_time_minutes=25.0,
            dispatch_delay_minutes=0.6,
        )
        mc.record_incident(inc)
        s = mc.get_summary_statistics()
        assert s["total_incidents"] == 1
        assert s["travel_time_mean"] == pytest.approx(2.4)
        assert s["service_time_mean"] == pytest.approx(25.0)

    def test_coverage_fraction(self):
        """Coverage should reflect incidents within threshold."""
        mc = MetricsCollector(response_threshold_minutes=8.0)
        for i, rt in enumerate([5.0, 6.0, 10.0, 12.0]):
            inc = Incident(
                id=i, arrival_time=float(i), precinct=1,
                dispatch_time=float(i) + 0.01,
                service_start_time=float(i) + rt / 60.0,
                completion_time=float(i) + 1.0,
                travel_time_minutes=rt - 1.0,
                service_time_minutes=20.0,
                dispatch_delay_minutes=1.0,
            )
            mc.record_incident(inc)
        s = mc.get_summary_statistics()
        # 5 and 6 are within 8, so 2 out of 4
        assert s["coverage_fraction"] == pytest.approx(0.5)

    def test_queue_fraction(self):
        """Queue fraction should count queued incidents."""
        mc = MetricsCollector()
        for i in range(10):
            inc = Incident(
                id=i, arrival_time=float(i), precinct=1,
                dispatch_time=float(i) + 0.1,
                service_start_time=float(i) + 0.2,
                completion_time=float(i) + 1.0,
                travel_time_minutes=5.0,
                service_time_minutes=20.0,
                dispatch_delay_minutes=1.0,
                queued=(i < 3),  # 3 out of 10 queued
            )
            mc.record_incident(inc)
        s = mc.get_summary_statistics()
        assert s["queue_fraction"] == pytest.approx(0.3)

    def test_incident_log_dataframe(self):
        """Incident log should be a proper DataFrame."""
        mc = MetricsCollector()
        for i in range(5):
            inc = Incident(id=i, arrival_time=float(i), precinct=1)
            mc.record_incident(inc)
        log = mc.get_incident_log()
        assert isinstance(log, pd.DataFrame)
        assert len(log) == 5
        assert "id" in log.columns

    def test_reset(self):
        """Reset should clear all state."""
        mc = MetricsCollector()
        inc = Incident(id=1, arrival_time=0.0, precinct=1,
                      travel_time_minutes=5.0, dispatch_delay_minutes=1.0)
        mc.record_incident(inc)
        mc.reset()
        assert mc.get_summary_statistics()["total_incidents"] == 0

    def test_queue_length_tracking(self):
        """Queue length observations should be recorded."""
        mc = MetricsCollector()
        mc.record_queue_length(0.0, 0)
        mc.record_queue_length(1.0, 3)
        mc.record_queue_length(2.0, 1)
        mc.record_queue_length(3.0, 0)
        s = mc.get_summary_statistics()
        assert s["queue_length_max"] == 3


# ── UnitPool Tests ────────────────────────────────────────────────


class TestUnitPool:
    """Verify unit pool management."""

    def test_creation(self):
        alloc = pd.Series({"FH_A": 2, "FH_B": 1})
        pool = UnitPool(alloc)
        assert pool.total_units == 3
        assert pool.count_available() == 3

    def test_dispatch_reduces_available(self):
        alloc = pd.Series({"FH_A": 2, "FH_B": 1})
        pool = UnitPool(alloc)
        units = pool.get_available_units()
        units[0].dispatch()
        assert pool.count_available() == 2

    def test_return_restores_available(self):
        alloc = pd.Series({"FH_A": 1})
        pool = UnitPool(alloc)
        unit = pool.get_available_units()[0]
        unit.dispatch()
        assert pool.count_available() == 0
        unit.return_available(busy_duration_hours=0.5)
        assert pool.count_available() == 1
        assert unit.incidents_served == 1
        assert unit.total_busy_time == pytest.approx(0.5)

    def test_available_by_firehouse(self):
        alloc = pd.Series({"FH_A": 2, "FH_B": 1})
        pool = UnitPool(alloc)
        by_fh = pool.get_available_by_firehouse()
        assert len(by_fh["FH_A"]) == 2
        assert len(by_fh["FH_B"]) == 1

    def test_utilisation(self):
        alloc = pd.Series({"FH_A": 1})
        pool = UnitPool(alloc)
        unit = pool.get_available_units()[0]
        unit.dispatch()
        unit.return_available(busy_duration_hours=5.0)
        utils = pool.get_utilizations(10.0)
        assert list(utils.values())[0] == pytest.approx(0.5)

    def test_zero_allocation_ignored(self):
        """Firehouses with 0 units should be skipped."""
        alloc = pd.Series({"FH_A": 2, "FH_B": 0, "FH_C": 1})
        pool = UnitPool(alloc)
        assert pool.total_units == 3
        assert "FH_B" not in pool.get_available_by_firehouse()


# ── EMSUnit Tests ─────────────────────────────────────────────────


class TestEMSUnit:
    """Verify single unit state transitions."""

    def test_initial_state(self):
        unit = EMSUnit(id="U1", home_firehouse="FH_A")
        assert unit.is_available
        assert unit.incidents_served == 0
        assert unit.total_busy_time == 0.0

    def test_dispatch_transition(self):
        unit = EMSUnit(id="U1", home_firehouse="FH_A")
        unit.dispatch()
        assert unit.status == UnitStatus.DISPATCHED
        assert not unit.is_available

    def test_on_scene_transition(self):
        unit = EMSUnit(id="U1", home_firehouse="FH_A")
        unit.dispatch()
        unit.arrive_on_scene()
        assert unit.status == UnitStatus.ON_SCENE

    def test_return_transition(self):
        unit = EMSUnit(id="U1", home_firehouse="FH_A")
        unit.dispatch()
        unit.arrive_on_scene()
        unit.return_available(busy_duration_hours=0.3)
        assert unit.is_available
        assert unit.incidents_served == 1
        assert unit.total_busy_time == pytest.approx(0.3)

    def test_multiple_incidents(self):
        unit = EMSUnit(id="U1", home_firehouse="FH_A")
        for _ in range(5):
            unit.dispatch()
            unit.return_available(busy_duration_hours=0.2)
        assert unit.incidents_served == 5
        assert unit.total_busy_time == pytest.approx(1.0)


# ── Incident Entity Tests ────────────────────────────────────────


class TestIncidentEntity:
    """Verify Incident data class properties."""

    def test_response_time_calculation(self):
        inc = Incident(
            id=1, arrival_time=1.0, precinct=1,
            service_start_time=1.1,
        )
        assert inc.response_time_minutes == pytest.approx(6.0)  # 0.1 hours * 60

    def test_total_time_calculation(self):
        inc = Incident(
            id=1, arrival_time=1.0, precinct=1,
            completion_time=2.0,
        )
        assert inc.total_time_minutes == pytest.approx(60.0)

    def test_none_times(self):
        inc = Incident(id=1, arrival_time=1.0, precinct=1)
        assert inc.response_time_minutes is None
        assert inc.total_time_minutes is None
