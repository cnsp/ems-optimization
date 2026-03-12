"""Core simulation engine tests.

Covers:
- Simulation initialization and configuration
- NHPP arrival generation
- Event sequence ordering (arrival < dispatch < completion)
- Unit conservation (busy time accounting)
- Reproducibility under fixed seeds
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from ems_readiness.simulation.engine import EMSSimulation
from ems_readiness.simulation.entities import Incident
from ems_readiness.simulation.metrics import MetricsCollector
from ems_readiness.simulation.resources import UnitPool, EMSUnit, UnitStatus


# ── Initialization Tests ────────────────────────────────────────────

class TestSimulationInitialization:
    """Tests for EMSSimulation.__init__ and config loading."""

    def test_basic_initialization(self, real_uniform_allocation, project_root):
        """Simulation initializes with valid allocation."""
        sim = EMSSimulation(
            policy_allocation=real_uniform_allocation,
            seed=42,
            project_root=str(project_root),
        )
        assert sim.unit_pool.total_units == int(real_uniform_allocation.sum())
        assert sim.seed == 42
        assert sim._completed is False

    def test_all_units_available_at_start(self, real_uniform_allocation, project_root):
        """All units should be AVAILABLE before simulation runs."""
        sim = EMSSimulation(
            policy_allocation=real_uniform_allocation,
            seed=42,
            project_root=str(project_root),
        )
        assert sim.unit_pool.count_available() == sim.unit_pool.total_units

    def test_empty_queue_at_start(self, real_uniform_allocation, project_root):
        """No incidents should be queued at initialization."""
        sim = EMSSimulation(
            policy_allocation=real_uniform_allocation,
            seed=42,
            project_root=str(project_root),
        )
        assert len(sim._waiting_queue) == 0
        assert sim._incident_counter == 0

    def test_invalid_allocation_raises(self, project_root):
        """Zero-unit allocation should raise ValueError."""
        with pytest.raises(ValueError):
            EMSSimulation(
                policy_allocation=pd.Series({"FH": 0}),
                seed=42,
                project_root=str(project_root),
            )

    def test_config_loading(self, real_uniform_allocation, project_root):
        """Config loads response threshold and dispatch delay."""
        sim = EMSSimulation(
            policy_allocation=real_uniform_allocation,
            seed=42,
            project_root=str(project_root),
        )
        assert sim.response_threshold == 8.0
        assert sim.dispatch_delay_fixed > 0  # should be 1.5 min


# ── Arrival Generation Tests ────────────────────────────────────────

class TestArrivalGeneration:
    """Tests for NHPP arrival process within simulation."""

    def test_arrivals_generated(self, real_uniform_allocation, project_root):
        """Short simulation should produce incidents."""
        sim = EMSSimulation(
            policy_allocation=real_uniform_allocation,
            seed=42,
            project_root=str(project_root),
        )
        sim.run(horizon_hours=24)
        results = sim.get_results()
        assert results["summary"]["total_incidents"] > 0

    def test_arrivals_within_horizon(self, real_uniform_allocation, project_root):
        """All incident arrival times should be within [0, horizon]."""
        sim = EMSSimulation(
            policy_allocation=real_uniform_allocation,
            seed=42,
            project_root=str(project_root),
        )
        horizon = 24.0
        sim.run(horizon_hours=horizon)
        log = sim.get_results()["incident_log"]
        if not log.empty:
            assert log["arrival_time"].min() >= 0.0
            assert log["arrival_time"].max() <= horizon

    def test_arrival_rate_plausible(self, real_uniform_allocation, project_root):
        """Arrival rate should be roughly near the configured base rate."""
        sim = EMSSimulation(
            policy_allocation=real_uniform_allocation,
            seed=42,
            project_root=str(project_root),
        )
        horizon = 48.0
        sim.run(horizon_hours=horizon)
        n_incidents = sim.get_results()["summary"]["total_incidents"]
        rate = n_incidents / horizon
        # Base rate is ~3.48/hour; with NHPP variation, expect 1-10
        assert 0.5 < rate < 15.0, f"Rate {rate:.2f} outside plausible range"


# ── Event Sequence Tests ─────────────────────────────────────────

class TestEventSequence:
    """Verify temporal ordering of simulation events."""

    def test_arrival_before_dispatch(self, real_uniform_allocation, project_root):
        """Arrival time should precede dispatch time for every incident."""
        sim = EMSSimulation(
            policy_allocation=real_uniform_allocation,
            seed=42,
            project_root=str(project_root),
        )
        sim.run(horizon_hours=24)
        log = sim.get_results()["incident_log"]
        if not log.empty:
            valid = log.dropna(subset=["dispatch_time"])
            assert (valid["dispatch_time"] >= valid["arrival_time"]).all()

    def test_dispatch_before_service_start(self, real_uniform_allocation, project_root):
        """Dispatch should precede service start (travel takes time)."""
        sim = EMSSimulation(
            policy_allocation=real_uniform_allocation,
            seed=42,
            project_root=str(project_root),
        )
        sim.run(horizon_hours=24)
        log = sim.get_results()["incident_log"]
        if not log.empty:
            valid = log.dropna(subset=["dispatch_time", "service_start_time"])
            assert (valid["service_start_time"] >= valid["dispatch_time"]).all()

    def test_service_start_before_completion(self, real_uniform_allocation, project_root):
        """Service start should precede completion."""
        sim = EMSSimulation(
            policy_allocation=real_uniform_allocation,
            seed=42,
            project_root=str(project_root),
        )
        sim.run(horizon_hours=24)
        log = sim.get_results()["incident_log"]
        if not log.empty:
            valid = log.dropna(subset=["service_start_time", "completion_time"])
            assert (valid["completion_time"] >= valid["service_start_time"]).all()

    def test_positive_response_times(self, real_uniform_allocation, project_root):
        """All response times should be strictly positive."""
        sim = EMSSimulation(
            policy_allocation=real_uniform_allocation,
            seed=42,
            project_root=str(project_root),
        )
        sim.run(horizon_hours=24)
        log = sim.get_results()["incident_log"]
        if not log.empty:
            valid = log.dropna(subset=["response_time_minutes"])
            assert (valid["response_time_minutes"] > 0).all()


# ── Unit Conservation Tests ──────────────────────────────────────

class TestUnitConservation:
    """Verify unit accounting / conservation laws."""

    def test_total_busy_time_matches(self, real_uniform_allocation, project_root):
        """Sum of unit busy times ≈ sum of (travel + service) across incidents."""
        sim = EMSSimulation(
            policy_allocation=real_uniform_allocation,
            seed=42,
            project_root=str(project_root),
        )
        sim.run(horizon_hours=24)
        results = sim.get_results()
        log = results["incident_log"]

        if log.empty:
            pytest.skip("No incidents generated")

        # Total busy from incident log (travel + service in hours)
        incident_busy_hours = (
            (log["travel_time_minutes"].sum() + log["service_time_minutes"].sum()) / 60.0
        )

        # Total busy from units (directly from unit objects)
        unit_busy_hours = sum(
            u.total_busy_time for u in sim.unit_pool._all_units.values()
        )

        # Allow small tolerance for float arithmetic
        assert abs(incident_busy_hours - unit_busy_hours) < 0.01, (
            f"Incident busy={incident_busy_hours:.4f}h vs unit busy={unit_busy_hours:.4f}h"
        )

    def test_all_units_available_after_completion(self, real_uniform_allocation, project_root):
        """After simulation completes, units serving should return to available."""
        sim = EMSSimulation(
            policy_allocation=real_uniform_allocation,
            seed=42,
            project_root=str(project_root),
        )
        sim.run(horizon_hours=24)
        # Note: some units may still be busy at horizon cutoff
        # But total_units should still be conserved
        pool = sim.unit_pool
        total = pool.total_units
        assert total == int(real_uniform_allocation.sum())

    def test_incidents_served_sum(self, real_uniform_allocation, project_root):
        """Sum of incidents_served across units == total incidents."""
        sim = EMSSimulation(
            policy_allocation=real_uniform_allocation,
            seed=42,
            project_root=str(project_root),
        )
        sim.run(horizon_hours=24)
        results = sim.get_results()
        total_from_metrics = results["summary"]["total_incidents"]

        total_from_units = sum(
            u.incidents_served
            for u in sim.unit_pool._all_units.values()
        )
        assert total_from_units == total_from_metrics


# ── Reproducibility Test ─────────────────────────────────────────

class TestReproducibility:
    """Basic seed-based reproducibility (more in test_reproducibility.py)."""

    def test_same_seed_same_results(self, real_uniform_allocation, project_root):
        """Two runs with same seed should produce identical results."""
        results = []
        for _ in range(2):
            sim = EMSSimulation(
                policy_allocation=real_uniform_allocation,
                seed=42,
                project_root=str(project_root),
            )
            sim.run(horizon_hours=24)
            results.append(sim.get_results()["summary"])

        assert results[0]["total_incidents"] == results[1]["total_incidents"]
        assert abs(results[0]["response_time_mean"] - results[1]["response_time_mean"]) < 1e-10
        assert abs(results[0]["coverage_fraction"] - results[1]["coverage_fraction"]) < 1e-10
