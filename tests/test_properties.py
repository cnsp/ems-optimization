"""Property-based tests using Hypothesis.

Covers invariant properties that should hold for any valid input:
- Distance functions are non-negative and symmetric
- Allocation constraints are always satisfied
- Simulation metrics are in valid ranges
- Service time samples are always positive
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from ems_readiness.service.service_time import ServiceTimeModel
from ems_readiness.simulation.entities import Incident
from ems_readiness.simulation.metrics import MetricsCollector
from ems_readiness.simulation.resources import EMSUnit, UnitPool
from ems_readiness.utils.distance import haversine, manhattan_distance

# ── Strategies ────────────────────────────────────────────────────

# Valid latitude/longitude ranges
latitude = st.floats(min_value=-89.9, max_value=89.9, allow_nan=False, allow_infinity=False)
longitude = st.floats(min_value=-179.9, max_value=179.9, allow_nan=False, allow_infinity=False)
# Positive integers for unit counts
small_positive = st.integers(min_value=1, max_value=10)


# ── Distance Property Tests ──────────────────────────────────────


class TestDistanceProperties:
    """Invariant properties of distance functions."""

    @given(lat=latitude, lon=longitude)
    @settings(max_examples=50)
    def test_haversine_zero_self_distance(self, lat, lon):
        """Distance from a point to itself is zero."""
        d = haversine(lat, lon, lat, lon)
        assert d == pytest.approx(0.0, abs=1e-6)

    @given(lat1=latitude, lon1=longitude, lat2=latitude, lon2=longitude)
    @settings(max_examples=50)
    def test_haversine_non_negative(self, lat1, lon1, lat2, lon2):
        """Haversine distance is always non-negative."""
        d = haversine(lat1, lon1, lat2, lon2)
        assert d >= 0

    @given(lat1=latitude, lon1=longitude, lat2=latitude, lon2=longitude)
    @settings(max_examples=50)
    def test_haversine_symmetric(self, lat1, lon1, lat2, lon2):
        """Haversine is symmetric: d(A,B) == d(B,A)."""
        d1 = haversine(lat1, lon1, lat2, lon2)
        d2 = haversine(lat2, lon2, lat1, lon1)
        assert d1 == pytest.approx(d2, rel=1e-9)

    @given(lat1=latitude, lon1=longitude, lat2=latitude, lon2=longitude)
    @settings(max_examples=50)
    def test_manhattan_non_negative(self, lat1, lon1, lat2, lon2):
        """Manhattan distance is always non-negative."""
        d = manhattan_distance(lat1, lon1, lat2, lon2)
        assert d >= 0

    @given(
        lat1=st.floats(min_value=30.0, max_value=50.0, allow_nan=False),
        lon1=st.floats(min_value=-80.0, max_value=-70.0, allow_nan=False),
        dlat=st.floats(min_value=-0.5, max_value=0.5, allow_nan=False),
        dlon=st.floats(min_value=-0.5, max_value=0.5, allow_nan=False),
    )
    @settings(max_examples=50)
    def test_manhattan_and_haversine_close(self, lat1, lon1, dlat, dlon):
        """Manhattan and Haversine should be in similar ballpark for nearby points."""
        lat2 = lat1 + dlat
        lon2 = lon1 + dlon
        d_man = manhattan_distance(lat1, lon1, lat2, lon2)
        d_hav = haversine(lat1, lon1, lat2, lon2)
        # Both should be non-negative
        assert d_man >= 0
        assert d_hav >= 0
        # They should be within a reasonable factor of each other
        if d_hav > 0.01:  # avoid division by near-zero
            ratio = d_man / d_hav
            assert 0.5 < ratio < 2.0, f"ratio={ratio:.3f} out of range"


# ── Service Time Property Tests ──────────────────────────────────


class TestServiceTimeProperties:
    """Invariant properties of service time sampling."""

    @given(seed=st.integers(min_value=0, max_value=2**31 - 1))
    @settings(max_examples=30)
    def test_lognormal_always_positive(self, seed):
        """Lognormal samples are always strictly positive."""
        model = ServiceTimeModel(mean_minutes=25.0, std_minutes=10.0, distribution="lognormal")
        samples = model.sample(100, rng=seed)
        assert (samples > 0).all()

    @given(seed=st.integers(min_value=0, max_value=2**31 - 1))
    @settings(max_examples=30)
    def test_exponential_always_positive(self, seed):
        """Exponential samples are always strictly positive."""
        model = ServiceTimeModel(mean_minutes=25.0, distribution="exponential")
        samples = model.sample(100, rng=seed)
        assert (samples > 0).all()

    @given(n=st.integers(min_value=1, max_value=1000))
    @settings(max_examples=20)
    def test_sample_size_matches(self, n):
        """Returned array length always matches requested size."""
        model = ServiceTimeModel()
        assert len(model.sample(n, rng=42)) == n


# ── UnitPool Property Tests ──────────────────────────────────────


class TestUnitPoolProperties:
    """Invariant properties of unit pool management."""

    @given(n_units=st.lists(small_positive, min_size=1, max_size=5))
    @settings(max_examples=30)
    def test_total_units_equals_sum(self, n_units):
        """Total units should always equal sum of allocation."""
        fhs = [f"FH_{i}" for i in range(len(n_units))]
        alloc = pd.Series(dict(zip(fhs, n_units)))
        pool = UnitPool(alloc)
        assert pool.total_units == sum(n_units)

    @given(n_units=st.lists(small_positive, min_size=1, max_size=5))
    @settings(max_examples=30)
    def test_initial_all_available(self, n_units):
        """All units available initially."""
        fhs = [f"FH_{i}" for i in range(len(n_units))]
        alloc = pd.Series(dict(zip(fhs, n_units)))
        pool = UnitPool(alloc)
        assert pool.count_available() == pool.total_units


# ── Metrics Property Tests ────────────────────────────────────────


class TestMetricsProperties:
    """Invariant properties of the metrics collector."""

    @given(n_incidents=st.integers(min_value=1, max_value=50))
    @settings(max_examples=20)
    def test_total_incidents_correct(self, n_incidents):
        """Recorded incident count should match input count."""
        mc = MetricsCollector()
        for i in range(n_incidents):
            inc = Incident(id=i, arrival_time=float(i), precinct=1)
            mc.record_incident(inc)
        assert mc.get_summary_statistics()["total_incidents"] == n_incidents

    @given(
        threshold=st.floats(min_value=1.0, max_value=30.0, allow_nan=False),
        n=st.integers(min_value=1, max_value=20),
    )
    @settings(max_examples=20)
    def test_coverage_in_unit_interval(self, threshold, n):
        """Coverage fraction should always be in [0, 1]."""
        mc = MetricsCollector(response_threshold_minutes=threshold)
        rng = np.random.default_rng(42)
        for i in range(n):
            rt = rng.uniform(0.5, 20.0)
            inc = Incident(
                id=i, arrival_time=float(i), precinct=1,
                service_start_time=float(i) + rt / 60.0,
                travel_time_minutes=rt,
                dispatch_delay_minutes=0.0,
            )
            mc.record_incident(inc)
        cov = mc.get_summary_statistics()["coverage_fraction"]
        assert 0.0 <= cov <= 1.0
