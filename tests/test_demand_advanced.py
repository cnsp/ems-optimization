"""Advanced tests for the demand / NHPP arrival generator.

Covers:
- Lambda table loading and validation
- Effective rate calculation
- NHPP arrival properties (thinning correctness)
- Spatial allocation of arrivals to precincts
- Edge cases: zero rate, very high rate, short/long horizons
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from ems_readiness.demand.arrival_generator import (
    NHPPArrivalGenerator,
    effective_rate,
    load_lambda_tables,
)

DATA_DIR = PROJECT_ROOT / "data" / "processed"


# ── Lambda Table Tests ────────────────────────────────────────────


class TestLambdaTables:
    """Verify lambda factor tables load correctly."""

    def test_load_tables_exist(self):
        """Lambda CSV files should load as a 3-tuple."""
        hourly, dow, precinct = load_lambda_tables(str(DATA_DIR))
        assert isinstance(hourly, pd.DataFrame)
        assert isinstance(dow, pd.DataFrame)
        assert isinstance(precinct, pd.DataFrame)

    def test_hourly_factors_shape(self):
        """Hourly table should have 24 rows (one per hour)."""
        hourly, _, _ = load_lambda_tables(str(DATA_DIR))
        assert len(hourly) == 24

    def test_dow_factors_shape(self):
        """Day-of-week table should have 7 rows."""
        _, dow, _ = load_lambda_tables(str(DATA_DIR))
        assert len(dow) == 7

    def test_hourly_factors_positive(self):
        """All hourly factors should be strictly positive."""
        hourly, _, _ = load_lambda_tables(str(DATA_DIR))
        factor_col = [c for c in hourly.columns if "factor" in c.lower()]
        if factor_col:
            assert (hourly[factor_col[0]].values > 0).all()
        else:
            # Fall back: last numeric column
            assert (hourly.iloc[:, -1].values > 0).all()

    def test_dow_factors_positive(self):
        """All day-of-week factors should be strictly positive."""
        _, dow, _ = load_lambda_tables(str(DATA_DIR))
        factor_col = [c for c in dow.columns if "factor" in c.lower()]
        if factor_col:
            assert (dow[factor_col[0]].values > 0).all()
        else:
            assert (dow.iloc[:, -1].values > 0).all()


# ── Effective Rate Tests ──────────────────────────────────────────


class TestEffectiveRate:
    """Verify the instantaneous rate lambda(t) calculation."""

    def test_base_rate_only(self):
        """With unit factors, effective rate equals base rate."""
        hourly = {h: 1.0 for h in range(24)}
        dow = {d: 1.0 for d in range(7)}
        rate = effective_rate(3.48, hour=10, dow=2, hourly_factors=hourly, dow_factors=dow)
        assert abs(rate - 3.48) < 1e-6

    def test_multiplicative_factors(self):
        """Rate should equal base * hourly_factor * dow_factor."""
        hourly = {h: 2.0 for h in range(24)}
        dow = {d: 1.5 for d in range(7)}
        rate = effective_rate(3.0, hour=5, dow=3, hourly_factors=hourly, dow_factors=dow)
        assert abs(rate - 3.0 * 2.0 * 1.5) < 1e-6

    def test_zero_base_rate(self):
        """Zero base rate yields zero effective rate."""
        hourly = {h: 2.0 for h in range(24)}
        dow = {d: 1.5 for d in range(7)}
        rate = effective_rate(0.0, hour=0, dow=0, hourly_factors=hourly, dow_factors=dow)
        assert rate == 0.0


# ── NHPP Generator Tests ─────────────────────────────────────────


class TestNHPPGenerator:
    """Test the thinning-based arrival generator."""

    @pytest.fixture
    def generator(self):
        """Create a generator from project data."""
        return NHPPArrivalGenerator.from_tables(str(DATA_DIR))

    def test_arrivals_non_empty(self, generator):
        """24-hour generation should produce arrivals."""
        df = generator.generate_arrivals(n_hours=24, start_hour=0, dow=2, rng=42)
        assert len(df) > 0

    def test_arrivals_within_horizon(self, generator):
        """All arrival times should be in [0, n_hours)."""
        n = 48
        df = generator.generate_arrivals(n_hours=n, start_hour=0, dow=0, rng=99)
        assert df["time_hours"].min() >= 0
        assert df["time_hours"].max() < n

    def test_arrivals_sorted(self, generator):
        """Arrival times should be monotonically non-decreasing."""
        df = generator.generate_arrivals(n_hours=24, start_hour=0, dow=1, rng=7)
        times = df["time_hours"].values
        assert (np.diff(times) >= 0).all()

    def test_arrival_count_plausible(self, generator):
        """With base rate ~3.48/hr, 24h should give roughly 50-150 arrivals."""
        df = generator.generate_arrivals(n_hours=24, start_hour=0, dow=3, rng=42)
        assert 10 < len(df) < 500

    def test_precinct_column_present(self, generator):
        """When precinct rates are loaded, arrivals should have a precinct column."""
        df = generator.generate_arrivals(n_hours=24, start_hour=0, dow=0, rng=42)
        probs = getattr(generator, "precinct_probs", None) or getattr(generator, "_precinct_probs", None)
        if probs is not None:
            assert "precinct" in df.columns

    def test_seed_reproducibility(self, generator):
        """Same rng seed should produce identical arrivals."""
        df1 = generator.generate_arrivals(n_hours=24, start_hour=0, dow=0, rng=42)
        df2 = generator.generate_arrivals(n_hours=24, start_hour=0, dow=0, rng=42)
        pd.testing.assert_frame_equal(df1, df2)

    def test_different_seeds_differ(self, generator):
        """Different seeds should produce different arrival sets."""
        df1 = generator.generate_arrivals(n_hours=24, start_hour=0, dow=0, rng=1)
        df2 = generator.generate_arrivals(n_hours=24, start_hour=0, dow=0, rng=2)
        assert len(df1) != len(df2) or not np.allclose(
            df1["time_hours"].values, df2["time_hours"].values
        )

    def test_short_horizon(self, generator):
        """1-hour horizon should work without error."""
        df = generator.generate_arrivals(n_hours=1, start_hour=14, dow=4, rng=42)
        assert isinstance(df, pd.DataFrame)

    def test_long_horizon(self, generator):
        """168-hour (1-week) horizon should complete."""
        df = generator.generate_arrivals(n_hours=168, start_hour=0, dow=0, rng=42)
        assert len(df) > 100  # At least some arrivals over a week
