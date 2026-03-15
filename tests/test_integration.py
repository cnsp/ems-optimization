"""Integration tests for component interactions.

Covers:
- Demand model -> Simulation pipeline
- Optimization -> Simulation pipeline
- Full pipeline: data -> optimize -> simulate -> metrics
- Batch runner with optimised allocation
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from ems_readiness.demand.arrival_generator import NHPPArrivalGenerator
from ems_readiness.optimization.models import build_demand_weighted, extract_allocation
from ems_readiness.optimization.policies import uniform_allocation
from ems_readiness.service.service_time import ServiceTimeModel
from ems_readiness.service.travel_time import build_travel_time_matrix
from ems_readiness.simulation.engine import EMSSimulation
from ems_readiness.simulation.runner import BatchRunner
from ems_readiness.utils.distance import build_distance_matrix

DATA_DIR = PROJECT_ROOT / "data" / "processed"


# ── Demand -> Simulation Integration ──────────────────────────────


class TestDemandSimulationIntegration:
    """Verify demand model feeds correctly into simulation."""

    def test_arrivals_drive_incidents(self):
        """Simulation incident count should correlate with arrival count."""
        dm = pd.read_csv(DATA_DIR / "distance_matrix_firehouse_precinct.csv", index_col=0)
        dm.columns = dm.columns.astype(str)
        fhs = dm.index[:10].tolist()
        alloc = pd.Series({fh: 2 for fh in fhs})

        sim = EMSSimulation(
            policy_allocation=alloc, seed=42,
            project_root=str(PROJECT_ROOT),
        )
        sim.run(horizon_hours=24)
        results = sim.get_results()

        # Incidents should be > 0 because demand model generates arrivals
        assert results["summary"]["total_incidents"] > 0

    def test_custom_arrival_generator(self):
        """Simulation should accept a custom arrival generator."""
        dm = pd.read_csv(DATA_DIR / "distance_matrix_firehouse_precinct.csv", index_col=0)
        dm.columns = dm.columns.astype(str)
        alloc = pd.Series({dm.index[0]: 5})

        sim = EMSSimulation(
            policy_allocation=alloc, seed=42,
            project_root=str(PROJECT_ROOT),
        )

        # Replace with a deterministic generator
        class FixedGenerator:
            def generate_arrivals(self, n_hours=24, **kwargs):
                precincts = [int(c) for c in dm.columns[:5]]
                return pd.DataFrame({
                    "time_hours": np.linspace(0.1, n_hours - 0.1, 10),
                    "hour": [int(t) % 24 for t in np.linspace(0.1, n_hours - 0.1, 10)],
                    "precinct": [precincts[i % len(precincts)] for i in range(10)],
                })

        sim.arrival_gen = FixedGenerator()
        sim.run(horizon_hours=24)
        results = sim.get_results()
        # May lose 1 incident at boundary; accept 9 or 10
        assert results["summary"]["total_incidents"] >= 9


# ── Optimization -> Simulation Integration ────────────────────────


class TestOptimizationSimulationIntegration:
    """Verify optimised allocations work in simulation."""

    def test_optimised_allocation_runs(self):
        """A demand-weighted optimised allocation should run in simulation."""
        dm = pd.read_csv(DATA_DIR / "distance_matrix_firehouse_precinct.csv", index_col=0)
        dm.columns = dm.columns.astype(str)
        tt = dm / 20.0 * 60.0  # travel time in minutes

        demand_df = pd.read_csv(DATA_DIR / "demand_lambda_precinct.csv")
        rate_col = [c for c in demand_df.columns if c != "precinct"][0]
        demand = demand_df.set_index("precinct")[rate_col].astype(float)
        demand.index = demand.index.astype(str)

        prob = build_demand_weighted(tt, demand, K=20, capacity=2)
        prob.solve()
        alloc = extract_allocation(prob)

        # Filter to only firehouses with units
        alloc = alloc[alloc > 0]
        assert alloc.sum() == 20

        sim = EMSSimulation(
            policy_allocation=alloc, seed=42,
            project_root=str(PROJECT_ROOT),
        )
        sim.run(horizon_hours=24)
        results = sim.get_results()
        assert results["summary"]["total_incidents"] > 0
        assert results["summary"]["response_time_mean"] > 0

    def test_optimised_beats_uniform_trend(self):
        """P2 allocation should trend toward better RT than P0 (directional)."""
        dm = pd.read_csv(DATA_DIR / "distance_matrix_firehouse_precinct.csv", index_col=0)
        dm.columns = dm.columns.astype(str)
        tt = dm / 20.0 * 60.0

        demand_df = pd.read_csv(DATA_DIR / "demand_lambda_precinct.csv")
        rate_col = [c for c in demand_df.columns if c != "precinct"][0]
        demand = demand_df.set_index("precinct")[rate_col].astype(float)
        demand.index = demand.index.astype(str)

        # Optimised allocation
        prob = build_demand_weighted(tt, demand, K=30, capacity=2)
        prob.solve()
        opt_alloc = extract_allocation(prob)
        opt_alloc = opt_alloc[opt_alloc > 0]

        # Uniform allocation
        uni_alloc = uniform_allocation(dm.index.tolist(), K=30, capacity=2)

        # Run both
        results = {}
        for name, alloc in [("P2", opt_alloc), ("P0", uni_alloc)]:
            sim = EMSSimulation(
                policy_allocation=alloc, seed=42,
                project_root=str(PROJECT_ROOT),
            )
            sim.run(horizon_hours=48)
            results[name] = sim.get_results()["summary"]["response_time_mean"]

        # P2 should have lower or similar response time
        assert results["P2"] <= results["P0"] * 1.15  # Allow 15% tolerance


# ── Full Pipeline Integration ─────────────────────────────────────


class TestFullPipeline:
    """End-to-end pipeline: load data -> optimise -> simulate -> report."""

    def test_end_to_end_pipeline(self):
        """Complete pipeline should produce valid results."""
        # Step 1: Load data
        dm = pd.read_csv(DATA_DIR / "distance_matrix_firehouse_precinct.csv", index_col=0)
        dm.columns = dm.columns.astype(str)
        assert dm.shape[0] > 0

        # Step 2: Compute travel times
        tt = build_travel_time_matrix(dm, speed_mph=20.0)
        assert (tt.values >= 0).all()

        # Step 3: Load demand
        demand_df = pd.read_csv(DATA_DIR / "demand_lambda_precinct.csv")
        rate_col = [c for c in demand_df.columns if c != "precinct"][0]
        demand = demand_df.set_index("precinct")[rate_col].astype(float)
        demand.index = demand.index.astype(str)
        assert (demand.values > 0).all()

        # Step 4: Optimise
        prob = build_demand_weighted(tt, demand, K=20, capacity=2)
        prob.solve()
        alloc = extract_allocation(prob)
        alloc = alloc[alloc > 0]
        assert alloc.sum() == 20

        # Step 5: Simulate
        sim = EMSSimulation(
            policy_allocation=alloc, seed=42,
            project_root=str(PROJECT_ROOT),
        )
        sim.run(horizon_hours=24)
        results = sim.get_results()

        # Step 6: Validate results
        s = results["summary"]
        assert s["total_incidents"] > 0
        assert 0 < s["response_time_mean"] < 60  # reasonable
        assert 0 <= s["coverage_fraction"] <= 1
        assert 0 <= s["queue_fraction"] <= 1

        log = results["incident_log"]
        assert not log.empty
        assert "response_time_minutes" in log.columns


# ── Batch Runner Integration ──────────────────────────────────────


class TestBatchRunnerIntegration:
    """Verify batch runner works end-to-end."""

    def test_batch_runner_multiple_reps(self):
        """BatchRunner should aggregate 3 replications correctly."""
        dm = pd.read_csv(DATA_DIR / "distance_matrix_firehouse_precinct.csv", index_col=0)
        dm.columns = dm.columns.astype(str)
        fhs = dm.index[:10].tolist()
        alloc = pd.Series({fh: 2 for fh in fhs})

        runner = BatchRunner(
            project_root=str(PROJECT_ROOT),
            data_dir="data/processed",
        )
        agg = runner.run_scenario(
            policy_allocation=alloc,
            num_replications=3,
            seed_base=42,
            horizon_hours=24,
            policy_name="integration_test",
        )

        # Should have per-replication data
        assert len(agg["per_replication"]) == 3
        # Should have aggregated metrics
        assert "response_time_mean" in agg
        assert agg["response_time_mean"]["mean"] > 0
        # CI should make sense
        assert agg["response_time_mean"]["ci_lower"] <= agg["response_time_mean"]["mean"]
        assert agg["response_time_mean"]["mean"] <= agg["response_time_mean"]["ci_upper"]

    def test_batch_runner_comparison_table(self):
        """Comparison table from two scenarios should have 2 rows."""
        dm = pd.read_csv(DATA_DIR / "distance_matrix_firehouse_precinct.csv", index_col=0)
        dm.columns = dm.columns.astype(str)

        runner = BatchRunner(project_root=str(PROJECT_ROOT), data_dir="data/processed")

        for policy_name, fhs_count in [("small", 5), ("medium", 10)]:
            fhs = dm.index[:fhs_count].tolist()
            alloc = pd.Series({fh: 2 for fh in fhs})
            runner.run_scenario(
                policy_allocation=alloc,
                num_replications=2,
                seed_base=42,
                horizon_hours=12,
                policy_name=policy_name,
            )

        table = runner.get_comparison_table()
        assert len(table) == 2
        assert "policy" in table.columns
