"""Tests for the SeedManager reproducibility utility.

Covers:
- Seed derivation from master seed
- Component isolation
- Global seed setting
- Config loading
- Metadata output
- RNG caching and independence
"""

import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from ems_readiness.utils.reproducibility import (
    COMPONENT_NAMES,
    DEFAULT_MASTER_SEED,
    SeedManager,
)


class TestSeedDerivation:
    """Verify that seeds are derived deterministically."""

    def test_default_master_seed(self):
        sm = SeedManager(log_seeds=False)
        assert sm.master_seed == DEFAULT_MASTER_SEED

    def test_custom_master_seed(self):
        sm = SeedManager(master_seed=123, log_seeds=False)
        assert sm.master_seed == 123

    def test_deterministic_derivation(self):
        """Same master seed always gives same component seeds."""
        sm1 = SeedManager(master_seed=42, log_seeds=False)
        sm2 = SeedManager(master_seed=42, log_seeds=False)
        for comp in COMPONENT_NAMES:
            assert sm1.get_seed(comp) == sm2.get_seed(comp)

    def test_different_master_gives_different_seeds(self):
        sm1 = SeedManager(master_seed=42, log_seeds=False)
        sm2 = SeedManager(master_seed=99, log_seeds=False)
        # At least one component should differ (practically all will)
        diffs = sum(
            sm1.get_seed(c) != sm2.get_seed(c) for c in COMPONENT_NAMES
        )
        assert diffs == len(COMPONENT_NAMES)

    def test_all_components_unique(self):
        """Each component should get a distinct seed."""
        sm = SeedManager(master_seed=42, log_seeds=False)
        seeds = [sm.get_seed(c) for c in COMPONENT_NAMES]
        assert len(set(seeds)) == len(seeds)

    def test_unknown_component_derived(self):
        """Unknown component names should be derived on the fly."""
        sm = SeedManager(master_seed=42, log_seeds=False)
        s1 = sm.get_seed("custom_component")
        s2 = sm.get_seed("custom_component")
        assert s1 == s2  # same component gives same seed
        assert isinstance(s1, int)


class TestComponentOverrides:
    """Verify explicit per-component seed overrides."""

    def test_override_takes_precedence(self):
        sm = SeedManager(
            master_seed=42,
            component_overrides={"demand": 999},
            log_seeds=False,
        )
        assert sm.get_seed("demand") == 999

    def test_non_overridden_still_derived(self):
        sm_with = SeedManager(
            master_seed=42,
            component_overrides={"demand": 999},
            log_seeds=False,
        )
        sm_without = SeedManager(master_seed=42, log_seeds=False)
        # simulation seed should be the same (not overridden)
        assert sm_with.get_seed("simulation") == sm_without.get_seed("simulation")


class TestRNGManagement:
    """Verify Generator creation and caching."""

    def test_rng_returns_generator(self):
        sm = SeedManager(master_seed=42, log_seeds=False)
        rng = sm.get_rng("demand")
        assert isinstance(rng, np.random.Generator)

    def test_rng_cached(self):
        """Multiple calls for same component return same object."""
        sm = SeedManager(master_seed=42, log_seeds=False)
        rng1 = sm.get_rng("simulation")
        rng2 = sm.get_rng("simulation")
        assert rng1 is rng2

    def test_different_component_rngs_independent(self):
        """Different components should produce different random streams."""
        sm = SeedManager(master_seed=42, log_seeds=False)
        rng_d = sm.get_rng("demand")
        rng_s = sm.get_rng("simulation")
        # Draw from each and verify they differ
        v1 = rng_d.random()
        v2 = rng_s.random()
        assert v1 != v2

    def test_rng_reproducible(self):
        """Generators from same master seed produce same sequence."""
        sm1 = SeedManager(master_seed=42, log_seeds=False)
        sm2 = SeedManager(master_seed=42, log_seeds=False)
        vals1 = [sm1.get_rng("demand").random() for _ in range(10)]
        vals2 = [sm2.get_rng("demand").random() for _ in range(10)]
        assert vals1 == vals2


class TestGlobalSeeds:
    """Verify set_global_seeds affects module-level PRNGs."""

    def test_global_seeds_reproducible(self):
        sm = SeedManager(master_seed=42, log_seeds=False)
        sm.set_global_seeds()
        v1 = np.random.random()

        sm2 = SeedManager(master_seed=42, log_seeds=False)
        sm2.set_global_seeds()
        v2 = np.random.random()

        assert v1 == v2


class TestMetadataAndSummary:
    """Verify summary/metadata output."""

    def test_summary_structure(self):
        sm = SeedManager(master_seed=42, log_seeds=False)
        s = sm.summary()
        assert "master_seed" in s
        assert "component_seeds" in s
        assert s["master_seed"] == 42

    def test_to_metadata(self):
        sm = SeedManager(master_seed=42, log_seeds=False)
        meta = sm.to_metadata()
        assert "reproducibility" in meta
        assert meta["reproducibility"]["master_seed"] == 42

    def test_log_seeds_returns_summary(self):
        sm = SeedManager(master_seed=42, log_seeds=False)
        info = sm.log_seeds()
        assert isinstance(info, dict)
        assert "master_seed" in info


class TestConfigLoading:
    """Verify loading from reproducibility.yaml."""

    def test_from_config_loads(self):
        """Should load config from project root."""
        sm = SeedManager.from_config(str(PROJECT_ROOT))
        assert sm.master_seed == 42  # default in config

    def test_from_config_fallback(self, tmp_path):
        """Missing config should fall back to defaults."""
        sm = SeedManager.from_config(str(tmp_path))
        assert sm.master_seed == DEFAULT_MASTER_SEED
