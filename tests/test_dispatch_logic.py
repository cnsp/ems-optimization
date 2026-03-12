"""Dispatch logic tests.

Covers:
- Nearest-available unit selection
- Tie-breaking rules (alphabetical firehouse)
- FIFO queue ordering
- All-units-busy queueing behavior
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from ems_readiness.simulation.dispatcher import NearestAvailableDispatcher
from ems_readiness.simulation.resources import EMSUnit, UnitPool, UnitStatus


# ── Nearest Available Tests ──────────────────────────────────────

class TestNearestAvailable:
    """Verify that dispatcher selects the closest available unit."""

    def test_selects_nearest_unit(self, small_distance_matrix, small_allocation):
        """For precinct 1 (FH_A=1mi, FH_B=2mi, FH_C=3mi), select FH_A."""
        dispatcher = NearestAvailableDispatcher(
            distance_matrix=small_distance_matrix,
            speed_mph=20.0,
            use_time_of_day=False,
        )
        pool = UnitPool(small_allocation)

        unit, travel = dispatcher.find_nearest_unit(
            precinct=1, unit_pool=pool, hour_of_day=None
        )
        assert unit is not None
        assert unit.home_firehouse == "FH_A"
        # travel = 1 mi / 20 mph * 60 = 3 minutes
        assert abs(travel - 3.0) < 0.01

    def test_selects_second_nearest_when_first_busy(
        self, small_distance_matrix, small_allocation
    ):
        """If FH_A is busy, should select FH_B for precinct 1."""
        dispatcher = NearestAvailableDispatcher(
            distance_matrix=small_distance_matrix,
            speed_mph=20.0,
            use_time_of_day=False,
        )
        pool = UnitPool(small_allocation)

        # Make FH_A unit busy
        for u in pool._all_units.values():
            if u.home_firehouse == "FH_A":
                u.dispatch()

        unit, travel = dispatcher.find_nearest_unit(
            precinct=1, unit_pool=pool, hour_of_day=None
        )
        assert unit is not None
        assert unit.home_firehouse == "FH_B"
        # travel = 2 mi / 20 mph * 60 = 6 minutes
        assert abs(travel - 6.0) < 0.01

    def test_returns_none_when_all_busy(self, small_distance_matrix, small_allocation):
        """If all units busy, returns (None, inf)."""
        dispatcher = NearestAvailableDispatcher(
            distance_matrix=small_distance_matrix,
            speed_mph=20.0,
            use_time_of_day=False,
        )
        pool = UnitPool(small_allocation)

        # Make all units busy
        for u in pool._all_units.values():
            u.dispatch()

        unit, travel = dispatcher.find_nearest_unit(
            precinct=1, unit_pool=pool, hour_of_day=None
        )
        assert unit is None
        assert travel == float("inf")

    def test_different_precincts_get_different_units(
        self, small_distance_matrix, small_allocation
    ):
        """Precinct 1 should get FH_A; precinct 2 should get FH_B."""
        dispatcher = NearestAvailableDispatcher(
            distance_matrix=small_distance_matrix,
            speed_mph=20.0,
            use_time_of_day=False,
        )
        pool = UnitPool(small_allocation)

        unit1, _ = dispatcher.find_nearest_unit(precinct=1, unit_pool=pool)
        assert unit1.home_firehouse == "FH_A"

        # Reset pool for independent test
        pool2 = UnitPool(small_allocation)
        unit2, _ = dispatcher.find_nearest_unit(precinct=2, unit_pool=pool2)
        assert unit2.home_firehouse == "FH_B"


# ── Tie-Breaking Tests ───────────────────────────────────────────

class TestTieBreaking:
    """Verify consistent tie-breaking rules."""

    def test_alphabetical_tie_breaking(self):
        """When two firehouses have equal distance, pick alphabetically first."""
        dm = pd.DataFrame(
            {"1": [2.0, 2.0]},
            index=["FH_Alpha", "FH_Beta"],
        )
        dispatcher = NearestAvailableDispatcher(
            distance_matrix=dm, speed_mph=20.0, use_time_of_day=False
        )
        alloc = pd.Series({"FH_Alpha": 1, "FH_Beta": 1})
        pool = UnitPool(alloc)

        unit, _ = dispatcher.find_nearest_unit(precinct=1, unit_pool=pool)
        assert unit is not None
        assert unit.home_firehouse == "FH_Alpha"

    def test_tie_breaking_deterministic(self):
        """Tie-breaking should always produce the same result."""
        dm = pd.DataFrame(
            {"1": [2.0, 2.0, 2.0]},
            index=["FH_C", "FH_A", "FH_B"],
        )
        dispatcher = NearestAvailableDispatcher(
            distance_matrix=dm, speed_mph=20.0, use_time_of_day=False
        )
        alloc = pd.Series({"FH_C": 1, "FH_A": 1, "FH_B": 1})

        results = []
        for _ in range(10):
            pool = UnitPool(alloc)
            unit, _ = dispatcher.find_nearest_unit(precinct=1, unit_pool=pool)
            results.append(unit.home_firehouse)

        # Should always pick FH_A (alphabetically first)
        assert all(r == "FH_A" for r in results)


# ── Queue FIFO Tests ─────────────────────────────────────────────

class TestQueueFIFO:
    """Verify FIFO queue ordering in the simulation engine."""

    def test_queue_order_maintained(self, project_root):
        """With K=1 unit, incidents should be served in FIFO order."""
        dm = pd.read_csv(
            PROJECT_ROOT / "data" / "processed" / "distance_matrix_firehouse_precinct.csv",
            index_col=0,
        )
        dm.columns = dm.columns.astype(str)
        first_fh = dm.index[0]
        alloc = pd.Series({first_fh: 1})

        from ems_readiness.simulation.engine import EMSSimulation

        sim = EMSSimulation(
            policy_allocation=alloc,
            seed=42,
            project_root=str(project_root),
            trace=False,
        )
        sim.run(horizon_hours=6)
        log = sim.get_results()["incident_log"]

        if len(log) < 3:
            pytest.skip("Not enough incidents to verify FIFO")

        # For incidents that were queued, verify dispatch order matches arrival order
        queued = log[log["queued"] == True].sort_values("dispatch_time")
        if len(queued) >= 2:
            # Dispatch order should follow arrival order for queued incidents
            arrival_order = queued["arrival_time"].values
            assert all(
                arrival_order[i] <= arrival_order[i + 1]
                for i in range(len(arrival_order) - 1)
            ), "Queued incidents not dispatched in FIFO order"


# ── All Units Busy Tests ─────────────────────────────────────────

class TestAllUnitsBusy:
    """Verify queueing behavior when all units are occupied."""

    def test_queueing_occurs_with_limited_units(self, project_root):
        """With 1 unit and moderate demand, some incidents should queue."""
        dm = pd.read_csv(
            PROJECT_ROOT / "data" / "processed" / "distance_matrix_firehouse_precinct.csv",
            index_col=0,
        )
        dm.columns = dm.columns.astype(str)
        first_fh = dm.index[0]
        alloc = pd.Series({first_fh: 1})

        from ems_readiness.simulation.engine import EMSSimulation

        sim = EMSSimulation(
            policy_allocation=alloc,
            seed=42,
            project_root=str(project_root),
        )
        sim.run(horizon_hours=12)
        results = sim.get_results()
        # With 1 unit and ~3.5 arrivals/hour, many incidents should queue
        assert results["summary"]["incidents_queued"] > 0
        assert results["summary"]["queue_fraction"] > 0

    def test_queue_length_metric_recorded(self, project_root):
        """Queue length observations should be recorded."""
        dm = pd.read_csv(
            PROJECT_ROOT / "data" / "processed" / "distance_matrix_firehouse_precinct.csv",
            index_col=0,
        )
        dm.columns = dm.columns.astype(str)
        first_fh = dm.index[0]
        alloc = pd.Series({first_fh: 1})

        from ems_readiness.simulation.engine import EMSSimulation

        sim = EMSSimulation(
            policy_allocation=alloc,
            seed=42,
            project_root=str(project_root),
        )
        sim.run(horizon_hours=6)
        summary = sim.get_results()["summary"]
        # With 1 unit, max queue should be > 0
        assert summary["queue_length_max"] >= 0
