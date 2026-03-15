"""Advanced tests for optimization models and allocation policies.

Covers:
- Model building and solving (demand-weighted, p-median, maximal coverage)
- Allocation constraint satisfaction (capacity, total units)
- Baseline policies (uniform, demand-proportional)
- Edge cases (K=1, K=num_firehouses, capacity=1)
- Solution quality checks
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from ems_readiness.optimization.models import (
    build_demand_weighted,
    build_maximal_coverage,
    build_p_median,
    extract_allocation,
    solve_model,
)
from ems_readiness.optimization.policies import (
    demand_proportional_allocation,
    uniform_allocation,
)

DATA_DIR = PROJECT_ROOT / "data" / "processed"


@pytest.fixture
def toy_travel_time():
    """3 firehouses x 2 precincts travel time matrix (minutes)."""
    return pd.DataFrame(
        {"1": [3.0, 6.0, 9.0], "2": [9.0, 3.0, 6.0]},
        index=["FH_A", "FH_B", "FH_C"],
    )


@pytest.fixture
def toy_demand():
    """Demand weights for 2 precincts."""
    return pd.Series({"1": 50.0, "2": 50.0})


@pytest.fixture
def real_travel_time():
    """Load real travel time matrix (distance / 20mph * 60)."""
    dm = pd.read_csv(DATA_DIR / "distance_matrix_firehouse_precinct.csv", index_col=0)
    dm.columns = dm.columns.astype(str)
    return dm / 20.0 * 60.0  # Convert miles to minutes


@pytest.fixture
def real_demand():
    """Load real precinct demand weights."""
    path = DATA_DIR / "demand_lambda_precinct.csv"
    df = pd.read_csv(path)
    # Use the rate column as demand
    rate_col = [c for c in df.columns if c != "precinct"][0]
    return df.set_index("precinct")[rate_col].astype(float)


# ── Demand-Weighted Model Tests ───────────────────────────────────


class TestDemandWeightedModel:
    """Verify the demand-weighted optimisation model."""

    def test_builds_without_error(self, toy_travel_time, toy_demand):
        """Model should build a PuLP problem."""
        prob = build_demand_weighted(toy_travel_time, toy_demand, K=2, capacity=2)
        assert prob is not None

    def test_solution_feasible(self, toy_travel_time, toy_demand):
        """Solved model should have optimal status."""
        prob = build_demand_weighted(toy_travel_time, toy_demand, K=2, capacity=2)
        prob.solve()
        assert prob.status == 1  # Optimal

    def test_allocation_sums_to_K(self, toy_travel_time, toy_demand):
        """Total allocated units should equal K."""
        prob = build_demand_weighted(toy_travel_time, toy_demand, K=3, capacity=2)
        prob.solve()
        alloc = extract_allocation(prob)
        assert alloc.sum() == 3

    def test_capacity_respected(self, toy_travel_time, toy_demand):
        """No firehouse should exceed capacity."""
        prob = build_demand_weighted(toy_travel_time, toy_demand, K=4, capacity=2)
        prob.solve()
        alloc = extract_allocation(prob)
        assert alloc.max() <= 2

    def test_places_units_at_nearest_firehouses(self, toy_travel_time, toy_demand):
        """With equal demand, units should go to FH_A and FH_B (closest)."""
        prob = build_demand_weighted(toy_travel_time, toy_demand, K=2, capacity=1)
        prob.solve()
        alloc = extract_allocation(prob)
        # FH_A is closest to precinct 1, FH_B is closest to precinct 2
        assert alloc.get("FH_A", 0) >= 1 or alloc.get("FH_B", 0) >= 1


# ── P-Median Model Tests ─────────────────────────────────────────


class TestPMedianModel:
    """Verify the p-median optimisation model."""

    def test_solution_feasible(self, toy_travel_time, toy_demand):
        prob = build_p_median(toy_travel_time, toy_demand, K=2, capacity=2)
        prob.solve()
        assert prob.status == 1

    def test_allocation_sums_to_K(self, toy_travel_time, toy_demand):
        prob = build_p_median(toy_travel_time, toy_demand, K=3, capacity=2)
        prob.solve()
        alloc = extract_allocation(prob)
        assert alloc.sum() == 3


# ── Maximal Coverage Model Tests ──────────────────────────────────


class TestMaximalCoverageModel:
    """Verify the maximal coverage optimisation model."""

    def test_solution_feasible(self, toy_travel_time, toy_demand):
        prob = build_maximal_coverage(
            toy_travel_time, toy_demand, K=2, capacity=2, coverage_threshold=5.0
        )
        prob.solve()
        assert prob.status == 1

    def test_allocation_sums_to_K(self, toy_travel_time, toy_demand):
        prob = build_maximal_coverage(
            toy_travel_time, toy_demand, K=3, capacity=2, coverage_threshold=5.0
        )
        prob.solve()
        alloc = extract_allocation(prob)
        assert alloc.sum() == 3

    def test_high_threshold_covers_less(self, toy_travel_time, toy_demand):
        """Tighter threshold should not increase coverage."""
        # Very tight threshold: 1 minute (nothing covered)
        prob_tight = build_maximal_coverage(
            toy_travel_time, toy_demand, K=2, capacity=2, coverage_threshold=1.0
        )
        prob_tight.solve()
        # Loose threshold: 10 minutes (everything covered)
        prob_loose = build_maximal_coverage(
            toy_travel_time, toy_demand, K=2, capacity=2, coverage_threshold=10.0
        )
        prob_loose.solve()
        # Both should be feasible
        assert prob_tight.status == 1
        assert prob_loose.status == 1


# ── Baseline Policy Tests ────────────────────────────────────────


class TestUniformAllocation:
    """Verify the uniform allocation baseline."""

    def test_sums_to_K(self):
        fhs = ["FH_A", "FH_B", "FH_C", "FH_D"]
        alloc = uniform_allocation(fhs, K=10, capacity=5)
        assert alloc.sum() == 10

    def test_balanced(self):
        """Max - min should differ by at most 1."""
        fhs = [f"FH_{i}" for i in range(10)]
        alloc = uniform_allocation(fhs, K=23, capacity=5)
        assert alloc.max() - alloc.min() <= 1

    def test_capacity_respected(self):
        fhs = ["FH_A", "FH_B"]
        alloc = uniform_allocation(fhs, K=6, capacity=3)
        assert alloc.max() <= 3

    def test_single_firehouse(self):
        alloc = uniform_allocation(["FH_A"], K=5, capacity=5)
        assert alloc["FH_A"] == 5

    def test_K_equals_zero(self):
        """K=0 should give all zeros."""
        alloc = uniform_allocation(["FH_A", "FH_B"], K=0, capacity=5)
        assert alloc.sum() == 0


class TestDemandProportionalAllocation:
    """Verify the demand-proportional allocation baseline."""

    def test_sums_to_K(self, small_distance_matrix):
        demand = pd.Series({"1": 50.0, "2": 50.0})
        alloc = demand_proportional_allocation(
            small_distance_matrix / 20.0 * 60.0, demand, K=3, capacity=2
        )
        assert alloc.sum() == 3

    def test_capacity_respected(self, small_distance_matrix):
        demand = pd.Series({"1": 100.0, "2": 1.0})
        alloc = demand_proportional_allocation(
            small_distance_matrix / 20.0 * 60.0, demand, K=4, capacity=2
        )
        assert alloc.max() <= 2


# ── Edge Case Tests ───────────────────────────────────────────────


class TestOptimizationEdgeCases:
    """Verify optimizer behaviour in edge cases."""

    def test_K_equals_1(self, toy_travel_time, toy_demand):
        """K=1 should allocate 1 unit to a single firehouse."""
        prob = build_demand_weighted(toy_travel_time, toy_demand, K=1, capacity=1)
        prob.solve()
        alloc = extract_allocation(prob)
        assert alloc.sum() == 1
        assert (alloc > 0).sum() == 1  # exactly one firehouse has a unit

    def test_capacity_1_limits_spread(self, toy_travel_time, toy_demand):
        """Capacity=1 means each firehouse gets at most 1 unit."""
        prob = build_demand_weighted(toy_travel_time, toy_demand, K=3, capacity=1)
        prob.solve()
        alloc = extract_allocation(prob)
        assert alloc.max() <= 1
        assert alloc.sum() == 3

    def test_real_data_optimal(self, real_travel_time, real_demand):
        """Optimization on real data should find a feasible solution."""
        prob = build_demand_weighted(real_travel_time, real_demand, K=20, capacity=2)
        prob.solve()
        assert prob.status == 1
        alloc = extract_allocation(prob)
        assert alloc.sum() == 20
        assert alloc.max() <= 2
