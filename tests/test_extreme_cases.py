"""Extreme / boundary condition tests.

Covers:
- Zero demand (no arrivals)
- Single unit (K=1)
- High demand (stress test)
- Zero service time (simplified case)
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import simpy

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from ems_readiness.simulation.engine import EMSSimulation
from ems_readiness.simulation.entities import Incident
from ems_readiness.simulation.metrics import MetricsCollector
from ems_readiness.simulation.resources import UnitPool


# ── Zero Demand Tests ────────────────────────────────────────────

class TestZeroDemand:
    """No arrivals should produce no incidents and no activity."""

    def test_zero_demand_no_incidents(self, project_root):
        """With a custom zero-rate arrival generator, no incidents should occur."""
        dm = pd.read_csv(
            PROJECT_ROOT / "data" / "processed" / "distance_matrix_firehouse_precinct.csv",
            index_col=0,
        )
        dm.columns = dm.columns.astype(str)

        # Allocate units across first 10 firehouses
        fhs = dm.index[:10].tolist()
        alloc = pd.Series({fh: 1 for fh in fhs})

        sim = EMSSimulation(
            policy_allocation=alloc,
            seed=42,
            project_root=str(project_root),
        )

        # Override arrival generator to produce zero arrivals
        class ZeroGenerator:
            def generate_arrivals(self, **kwargs):
                return pd.DataFrame(columns=["time_hours", "hour", "precinct"])

        sim.arrival_gen = ZeroGenerator()
        sim.run(horizon_hours=24)
        results = sim.get_results()

        assert results["summary"]["total_incidents"] == 0
        assert results["summary"]["coverage_fraction"] == 0.0
        assert results["summary"]["response_time_mean"] == 0.0

    def test_zero_demand_units_idle(self, project_root):
        """All units should remain available with zero demand."""
        dm = pd.read_csv(
            PROJECT_ROOT / "data" / "processed" / "distance_matrix_firehouse_precinct.csv",
            index_col=0,
        )
        dm.columns = dm.columns.astype(str)

        fhs = dm.index[:5].tolist()
        alloc = pd.Series({fh: 2 for fh in fhs})

        sim = EMSSimulation(
            policy_allocation=alloc,
            seed=42,
            project_root=str(project_root),
        )

        class ZeroGenerator:
            def generate_arrivals(self, **kwargs):
                return pd.DataFrame(columns=["time_hours", "hour", "precinct"])

        sim.arrival_gen = ZeroGenerator()
        sim.run(horizon_hours=24)

        # All units should be available
        assert sim.unit_pool.count_available() == sim.unit_pool.total_units
        # All utilizations should be 0
        utils = sim.unit_pool.get_utilizations(24)
        assert all(v == 0.0 for v in utils.values())


# ── Single Unit Tests ────────────────────────────────────────────

class TestSingleUnit:
    """K=1 should force queueing under moderate demand."""

    def test_single_unit_queue_builds(self, project_root):
        """With 1 unit and normal demand, queue should grow."""
        dm = pd.read_csv(
            PROJECT_ROOT / "data" / "processed" / "distance_matrix_firehouse_precinct.csv",
            index_col=0,
        )
        dm.columns = dm.columns.astype(str)
        first_fh = dm.index[0]
        alloc = pd.Series({first_fh: 1})

        sim = EMSSimulation(
            policy_allocation=alloc,
            seed=42,
            project_root=str(project_root),
        )
        sim.run(horizon_hours=24)
        results = sim.get_results()

        # With ~84 incidents/day and 1 unit, nearly all should queue
        assert results["summary"]["total_incidents"] > 10
        assert results["summary"]["queue_fraction"] > 0.5
        assert results["summary"]["queue_length_max"] > 1

    def test_single_unit_high_utilization(self, project_root):
        """Single unit should have very high utilization."""
        dm = pd.read_csv(
            PROJECT_ROOT / "data" / "processed" / "distance_matrix_firehouse_precinct.csv",
            index_col=0,
        )
        dm.columns = dm.columns.astype(str)
        first_fh = dm.index[0]
        alloc = pd.Series({first_fh: 1})

        sim = EMSSimulation(
            policy_allocation=alloc,
            seed=42,
            project_root=str(project_root),
        )
        horizon = 24.0
        sim.run(horizon_hours=horizon)
        # Compute utilization with actual horizon, not config default
        unit = list(sim.unit_pool._all_units.values())[0]
        actual_util = unit.total_busy_time / horizon
        # Single unit should be busy most of the time
        assert actual_util > 0.5, f"Single unit utilization={actual_util:.3f} too low"


# ── High Demand Tests ────────────────────────────────────────────

class TestHighDemand:
    """Stress test with high arrival rate."""

    def test_high_demand_stability(self, project_root):
        """Simulation should complete without errors under high demand."""
        dm = pd.read_csv(
            PROJECT_ROOT / "data" / "processed" / "distance_matrix_firehouse_precinct.csv",
            index_col=0,
        )
        dm.columns = dm.columns.astype(str)

        # 5 units across 5 firehouses
        fhs = dm.index[:5].tolist()
        alloc = pd.Series({fh: 1 for fh in fhs})

        sim = EMSSimulation(
            policy_allocation=alloc,
            seed=42,
            project_root=str(project_root),
        )

        # Override with high-rate generator
        class HighRateGenerator:
            """Generate arrivals at 20x normal rate."""
            def __init__(self, original):
                self.original = original

            def generate_arrivals(self, n_hours=24, start_hour=0, dow=0, rng=42):
                # Generate normal arrivals
                df = self.original.generate_arrivals(
                    n_hours=n_hours, start_hour=start_hour, dow=dow, rng=rng
                )
                if df.empty:
                    return df
                # Duplicate and compress times to increase rate ~5x
                dfs = []
                for offset in range(5):
                    d = df.copy()
                    d["time_hours"] = d["time_hours"] + offset * 0.01
                    dfs.append(d)
                result = pd.concat(dfs, ignore_index=True)
                result = result.sort_values("time_hours").reset_index(drop=True)
                result = result[result["time_hours"] < n_hours]
                return result

        sim.arrival_gen = HighRateGenerator(sim.arrival_gen)
        sim.run(horizon_hours=6)
        results = sim.get_results()

        # Should complete with many incidents and significant queueing
        assert results["summary"]["total_incidents"] > 30
        assert results["summary"]["queue_fraction"] > 0  # Should have queueing
        # Key: no crashes or infinite loops
        assert sim._completed is True

    def test_high_demand_metrics_consistent(self, project_root):
        """Under high demand, metrics should still be internally consistent."""
        dm = pd.read_csv(
            PROJECT_ROOT / "data" / "processed" / "distance_matrix_firehouse_precinct.csv",
            index_col=0,
        )
        dm.columns = dm.columns.astype(str)

        fhs = dm.index[:5].tolist()
        alloc = pd.Series({fh: 1 for fh in fhs})

        sim = EMSSimulation(
            policy_allocation=alloc,
            seed=99,
            project_root=str(project_root),
        )
        sim.run(horizon_hours=12)
        results = sim.get_results()
        s = results["summary"]

        # Mean response time >= mean travel time (response includes dispatch delay)
        if s["total_incidents"] > 0:
            assert s["response_time_mean"] >= s["travel_time_mean"]
            # Coverage fraction in [0, 1]
            assert 0.0 <= s["coverage_fraction"] <= 1.0
            # Queue fraction in [0, 1]
            assert 0.0 <= s["queue_fraction"] <= 1.0


# ── Zero Service Time Tests ─────────────────────────────────────

class TestZeroServiceTime:
    """Simplified case where service time is minimal."""

    def test_near_zero_service_time(self, project_root):
        """With near-zero service time, response ≈ dispatch_delay + travel."""
        dm = pd.read_csv(
            PROJECT_ROOT / "data" / "processed" / "distance_matrix_firehouse_precinct.csv",
            index_col=0,
        )
        dm.columns = dm.columns.astype(str)

        fhs = dm.index[:10].tolist()
        alloc = pd.Series({fh: 2 for fh in fhs})

        sim = EMSSimulation(
            policy_allocation=alloc,
            seed=42,
            project_root=str(project_root),
        )

        # Override service model with near-zero service times
        from ems_readiness.service.service_time import ServiceTimeModel

        class NearZeroServiceModel:
            def sample(self, size=1, rng=None):
                return np.full(size, 0.01)  # 0.01 minutes

        sim.service_model = NearZeroServiceModel()
        sim.run(horizon_hours=6)
        results = sim.get_results()
        log = results["incident_log"]

        if not log.empty:
            # Service times should all be ~0.01
            assert log["service_time_minutes"].max() < 0.1
            # Total time should be mostly dispatch + travel
            # Very little queueing expected with 20 units and fast service
            assert results["summary"]["queue_fraction"] < 0.1

    def test_zero_service_fast_turnover(self, project_root):
        """Near-zero service = units return immediately, less queueing."""
        dm = pd.read_csv(
            PROJECT_ROOT / "data" / "processed" / "distance_matrix_firehouse_precinct.csv",
            index_col=0,
        )
        dm.columns = dm.columns.astype(str)

        fhs = dm.index[:5].tolist()
        alloc = pd.Series({fh: 1 for fh in fhs})

        sim = EMSSimulation(
            policy_allocation=alloc,
            seed=42,
            project_root=str(project_root),
        )

        class NearZeroServiceModel:
            def sample(self, size=1, rng=None):
                return np.full(size, 0.001)

        sim.service_model = NearZeroServiceModel()
        sim.run(horizon_hours=6)
        results_fast = sim.get_results()

        # Compare with normal service time
        sim2 = EMSSimulation(
            policy_allocation=alloc,
            seed=42,
            project_root=str(project_root),
        )
        sim2.run(horizon_hours=6)
        results_normal = sim2.get_results()

        # Fast service should have less queueing than normal
        assert (
            results_fast["summary"]["queue_fraction"]
            <= results_normal["summary"]["queue_fraction"] + 0.01
        )
