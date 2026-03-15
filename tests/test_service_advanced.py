"""Advanced tests for service models (travel time, service time, distance).

Covers:
- Haversine and Manhattan distance functions
- Distance matrix construction
- Travel time calculations with time-of-day factors
- Service time distribution sampling
- Edge cases and input validation
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from ems_readiness.service.service_time import ServiceTimeModel
from ems_readiness.service.travel_time import (
    build_travel_time_matrix,
    travel_time_from_coords,
    travel_time_minutes,
)
from ems_readiness.utils.distance import (
    EARTH_RADIUS_MILES,
    build_distance_matrix,
    haversine,
    manhattan_distance,
)


# ── Haversine Distance Tests ─────────────────────────────────────


class TestHaversine:
    """Verify the Haversine (great-circle) distance function."""

    def test_zero_distance_same_point(self):
        """Distance from a point to itself is zero."""
        assert haversine(40.7, -74.0, 40.7, -74.0) == pytest.approx(0.0, abs=1e-6)

    def test_known_distance(self):
        """Rough check: Midtown to Downtown Manhattan ~ 3-5 miles."""
        d = haversine(40.758, -73.985, 40.710, -73.995)
        assert 2.0 < d < 6.0

    def test_symmetry(self):
        """Haversine should be symmetric."""
        d1 = haversine(40.75, -73.99, 40.71, -74.01)
        d2 = haversine(40.71, -74.01, 40.75, -73.99)
        assert d1 == pytest.approx(d2, rel=1e-10)

    def test_positive_distance(self):
        """Distance between distinct points should be positive."""
        d = haversine(40.0, -74.0, 41.0, -73.0)
        assert d > 0

    def test_antipodal_large(self):
        """Roughly antipodal points should give large distance."""
        d = haversine(0.0, 0.0, 0.0, 180.0)
        # Should be close to half Earth circumference in miles
        assert d > 10000


class TestManhattanDistance:
    """Verify the Manhattan (L1) distance function."""

    def test_zero_distance(self):
        """Same point gives zero."""
        assert manhattan_distance(40.7, -74.0, 40.7, -74.0) == pytest.approx(0.0, abs=1e-6)

    def test_greater_than_haversine(self):
        """Manhattan distance >= Haversine (triangle inequality in L1)."""
        lat1, lon1, lat2, lon2 = 40.758, -73.985, 40.710, -73.995
        d_man = manhattan_distance(lat1, lon1, lat2, lon2)
        d_hav = haversine(lat1, lon1, lat2, lon2)
        assert d_man >= d_hav - 1e-6

    def test_positive_distance(self):
        """Distance between distinct points should be positive."""
        d = manhattan_distance(40.0, -74.0, 40.1, -73.9)
        assert d > 0


# ── Distance Matrix Tests ────────────────────────────────────────


class TestDistanceMatrix:
    """Verify distance matrix construction."""

    def test_shape(self):
        """Matrix should be origins x destinations."""
        origins = pd.DataFrame({
            "Latitude": [40.7, 40.8], "Longitude": [-74.0, -73.9],
            "FacilityName": ["A", "B"],
        })
        dests = pd.DataFrame({
            "centroid_lat": [40.75, 40.85, 40.65],
            "centroid_lon": [-73.95, -73.85, -74.05],
            "Precinct": ["1", "2", "3"],
        })
        dm = build_distance_matrix(origins, dests, metric="haversine")
        assert dm.shape == (2, 3)

    def test_diagonal_zero_for_same_points(self):
        """If origins == destinations, diagonal should be zero."""
        pts = pd.DataFrame({
            "Latitude": [40.7, 40.8], "Longitude": [-74.0, -73.9],
            "FacilityName": ["A", "B"],
            "centroid_lat": [40.7, 40.8], "centroid_lon": [-74.0, -73.9],
            "Precinct": ["A", "B"],
        })
        dm = build_distance_matrix(
            pts, pts,
            origin_lat="Latitude", origin_lon="Longitude", origin_id="FacilityName",
            dest_lat="centroid_lat", dest_lon="centroid_lon", dest_id="Precinct",
        )
        assert dm.loc["A", "A"] == pytest.approx(0.0, abs=1e-6)
        assert dm.loc["B", "B"] == pytest.approx(0.0, abs=1e-6)

    def test_all_positive_off_diagonal(self):
        """Off-diagonal distances should be positive."""
        pts = pd.DataFrame({
            "Latitude": [40.7, 40.8, 40.9], "Longitude": [-74.0, -73.9, -73.8],
            "FacilityName": ["A", "B", "C"],
            "centroid_lat": [40.7, 40.8, 40.9], "centroid_lon": [-74.0, -73.9, -73.8],
            "Precinct": ["A", "B", "C"],
        })
        dm = build_distance_matrix(
            pts, pts,
            origin_lat="Latitude", origin_lon="Longitude", origin_id="FacilityName",
            dest_lat="centroid_lat", dest_lon="centroid_lon", dest_id="Precinct",
        )
        for i in dm.index:
            for j in dm.columns:
                if i != j:
                    assert dm.loc[i, j] > 0

    def test_manhattan_metric(self):
        """Manhattan metric should produce a valid matrix."""
        origins = pd.DataFrame({
            "Latitude": [40.7, 40.8], "Longitude": [-74.0, -73.9],
            "FacilityName": ["A", "B"],
        })
        dests = pd.DataFrame({
            "centroid_lat": [40.75], "centroid_lon": [-73.95], "Precinct": ["1"],
        })
        dm = build_distance_matrix(origins, dests, metric="manhattan")
        assert dm.shape == (2, 1)
        assert (dm.values >= 0).all()


# ── Travel Time Tests ─────────────────────────────────────────────


class TestTravelTime:
    """Verify travel time proxy calculations."""

    def test_basic_calculation(self):
        """1 mile at 20 mph = 3 minutes."""
        assert travel_time_minutes(1.0, 20.0) == pytest.approx(3.0)

    def test_zero_distance(self):
        """Zero distance should yield zero travel time."""
        assert travel_time_minutes(0.0, 20.0) == pytest.approx(0.0)

    def test_from_coords(self):
        """End-to-end travel time from coordinates should be positive."""
        tt = travel_time_from_coords(40.758, -73.985, 40.710, -73.995, speed_mph=20.0)
        assert tt > 0

    def test_travel_time_matrix(self):
        """Travel time matrix should have same shape as distance matrix."""
        dm = pd.DataFrame({"1": [1.0, 2.0], "2": [3.0, 1.5]}, index=["A", "B"])
        ttm = build_travel_time_matrix(dm, speed_mph=20.0)
        assert ttm.shape == dm.shape
        # All travel times should be positive for positive distances
        assert (ttm.values > 0).all()

    def test_speed_inversely_proportional(self):
        """Doubling speed should halve travel time."""
        tt_slow = travel_time_minutes(10.0, 20.0)
        tt_fast = travel_time_minutes(10.0, 40.0)
        assert tt_slow == pytest.approx(2 * tt_fast)


# ── Service Time Tests ────────────────────────────────────────────


class TestServiceTimeModel:
    """Verify service time distribution sampling."""

    def test_lognormal_positive(self):
        """Lognormal samples should all be positive."""
        model = ServiceTimeModel(mean_minutes=25.0, std_minutes=10.0, distribution="lognormal")
        samples = model.sample(1000, rng=42)
        assert (samples > 0).all()

    def test_exponential_positive(self):
        """Exponential samples should all be positive."""
        model = ServiceTimeModel(mean_minutes=25.0, distribution="exponential")
        samples = model.sample(1000, rng=42)
        assert (samples > 0).all()

    def test_lognormal_mean_close(self):
        """Sample mean should be within 10% of target for large n."""
        model = ServiceTimeModel(mean_minutes=25.0, std_minutes=10.0, distribution="lognormal")
        samples = model.sample(10000, rng=42)
        assert abs(samples.mean() - 25.0) < 2.5  # within 10%

    def test_exponential_mean_close(self):
        """Exponential sample mean should be near target."""
        model = ServiceTimeModel(mean_minutes=25.0, distribution="exponential")
        samples = model.sample(10000, rng=42)
        assert abs(samples.mean() - 25.0) < 2.5

    def test_reproducibility(self):
        """Same seed should give identical samples."""
        model = ServiceTimeModel(mean_minutes=25.0, std_minutes=10.0)
        s1 = model.sample(100, rng=42)
        s2 = model.sample(100, rng=42)
        np.testing.assert_array_equal(s1, s2)

    def test_different_seeds_differ(self):
        """Different seeds should give different samples."""
        model = ServiceTimeModel(mean_minutes=25.0, std_minutes=10.0)
        s1 = model.sample(100, rng=1)
        s2 = model.sample(100, rng=2)
        assert not np.array_equal(s1, s2)

    def test_sample_size(self):
        """Returned array should match requested size."""
        model = ServiceTimeModel()
        assert len(model.sample(50, rng=42)) == 50
        assert len(model.sample(1, rng=42)) == 1

    def test_invalid_distribution_raises(self):
        """Unsupported distribution should raise."""
        with pytest.raises(ValueError):
            ServiceTimeModel(distribution="gamma")
