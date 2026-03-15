"""Performance benchmarks and regression tests.

Ensures critical operations complete within acceptable time limits.
These are not micro-benchmarks - they guard against major performance
regressions (e.g., O(n^2) -> O(n^3) changes).

Times are generous to avoid flaky CI failures on slow machines.
"""

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from ems_readiness.demand.arrival_generator import NHPPArrivalGenerator
from ems_readiness.optimization.models import build_demand_weighted, extract_allocation
from ems_readiness.service.service_time import ServiceTimeModel
from ems_readiness.service.travel_time import build_travel_time_matrix
from ems_readiness.simulation.engine import EMSSimulation
from ems_readiness.utils.distance import build_distance_matrix, haversine

DATA_DIR = PROJECT_ROOT / "data" / "processed"


class TestDistancePerformance:
    """Benchmark distance matrix construction."""

    def test_distance_matrix_speed(self):
        """48x30 distance matrix should build in < 2 seconds."""
        rng = np.random.default_rng(0)
        fh_names = [f"FH_{i}" for i in range(48)]
        prec_names = [str(i) for i in range(30)]
        origins = pd.DataFrame({
            "Latitude": rng.uniform(40.7, 40.9, 48),
            "Longitude": rng.uniform(-74.05, -73.9, 48),
            "FacilityName": fh_names,
        })
        dests = pd.DataFrame({
            "centroid_lat": rng.uniform(40.7, 40.9, 30),
            "centroid_lon": rng.uniform(-74.05, -73.9, 30),
            "Precinct": prec_names,
        })
        start = time.perf_counter()
        dm = build_distance_matrix(origins, dests, metric="haversine")
        elapsed = time.perf_counter() - start
        assert elapsed < 2.0, f"Distance matrix took {elapsed:.2f}s (limit 2s)"
        assert dm.shape == (48, 30)


class TestArrivalPerformance:
    """Benchmark NHPP arrival generation."""

    def test_week_generation_speed(self):
        """168-hour arrival generation should complete in < 5 seconds."""
        gen = NHPPArrivalGenerator.from_tables(str(DATA_DIR))
        start = time.perf_counter()
        df = gen.generate_arrivals(n_hours=168, start_hour=0, dow=0, rng=42)
        elapsed = time.perf_counter() - start
        assert elapsed < 5.0, f"Week generation took {elapsed:.2f}s (limit 5s)"
        assert len(df) > 0


class TestOptimizationPerformance:
    """Benchmark optimization solve times."""

    def test_demand_weighted_solve_speed(self):
        """Demand-weighted K=30 cap=2 should solve in < 30 seconds."""
        dm = pd.read_csv(DATA_DIR / "distance_matrix_firehouse_precinct.csv", index_col=0)
        dm.columns = dm.columns.astype(str)
        tt = dm / 20.0 * 60.0

        demand_df = pd.read_csv(DATA_DIR / "demand_lambda_precinct.csv")
        rate_col = [c for c in demand_df.columns if c != "precinct"][0]
        demand = demand_df.set_index("precinct")[rate_col].astype(float)
        demand.index = demand.index.astype(str)

        start = time.perf_counter()
        prob = build_demand_weighted(tt, demand, K=30, capacity=2)
        prob.solve()
        elapsed = time.perf_counter() - start
        assert prob.status == 1
        assert elapsed < 30.0, f"Optimization took {elapsed:.2f}s (limit 30s)"


class TestSimulationPerformance:
    """Benchmark simulation speed."""

    def test_24h_simulation_speed(self):
        """24-hour simulation with 20 units should complete in < 10 seconds."""
        dm = pd.read_csv(DATA_DIR / "distance_matrix_firehouse_precinct.csv", index_col=0)
        dm.columns = dm.columns.astype(str)
        fhs = dm.index[:10].tolist()
        alloc = pd.Series({fh: 2 for fh in fhs})

        start = time.perf_counter()
        sim = EMSSimulation(
            policy_allocation=alloc, seed=42,
            project_root=str(PROJECT_ROOT),
        )
        sim.run(horizon_hours=24)
        elapsed = time.perf_counter() - start
        assert elapsed < 10.0, f"24h simulation took {elapsed:.2f}s (limit 10s)"

    def test_week_simulation_speed(self):
        """168-hour simulation with 20 units should complete in < 60 seconds."""
        dm = pd.read_csv(DATA_DIR / "distance_matrix_firehouse_precinct.csv", index_col=0)
        dm.columns = dm.columns.astype(str)
        fhs = dm.index[:10].tolist()
        alloc = pd.Series({fh: 2 for fh in fhs})

        start = time.perf_counter()
        sim = EMSSimulation(
            policy_allocation=alloc, seed=42,
            project_root=str(PROJECT_ROOT),
        )
        sim.run(horizon_hours=168)
        elapsed = time.perf_counter() - start
        assert elapsed < 60.0, f"168h simulation took {elapsed:.2f}s (limit 60s)"


class TestServiceTimePerformance:
    """Benchmark service time sampling."""

    def test_large_sample_speed(self):
        """Sampling 100k service times should take < 1 second."""
        model = ServiceTimeModel(mean_minutes=25.0, std_minutes=10.0)
        start = time.perf_counter()
        samples = model.sample(100_000, rng=42)
        elapsed = time.perf_counter() - start
        assert elapsed < 1.0, f"100k samples took {elapsed:.2f}s (limit 1s)"
        assert len(samples) == 100_000
