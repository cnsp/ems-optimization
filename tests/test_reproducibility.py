"""Reproducibility and independent replication tests.

Covers:
- Fixed seed produces identical results
- Different seeds produce different results
- BatchRunner replication seeds are independent
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from ems_readiness.simulation.engine import EMSSimulation
from ems_readiness.simulation.runner import BatchRunner


# ── Seed Control Tests ───────────────────────────────────────────

class TestSeedControl:
    """Fixed seed should give fully reproducible output."""

    def test_identical_incident_counts(self, real_uniform_allocation, project_root):
        """Same seed → same number of incidents."""
        counts = []
        for _ in range(3):
            sim = EMSSimulation(
                policy_allocation=real_uniform_allocation,
                seed=123,
                project_root=str(project_root),
            )
            sim.run(horizon_hours=24)
            counts.append(sim.get_results()["summary"]["total_incidents"])
        assert counts[0] == counts[1] == counts[2]

    def test_identical_incident_logs(self, real_uniform_allocation, project_root):
        """Same seed → identical incident logs."""
        logs = []
        for _ in range(2):
            sim = EMSSimulation(
                policy_allocation=real_uniform_allocation,
                seed=42,
                project_root=str(project_root),
            )
            sim.run(horizon_hours=12)
            logs.append(sim.get_results()["incident_log"])

        if not logs[0].empty:
            pd.testing.assert_frame_equal(logs[0], logs[1])

    def test_identical_summary_statistics(self, real_uniform_allocation, project_root):
        """Same seed → identical summary stats (all numeric fields)."""
        summaries = []
        for _ in range(2):
            sim = EMSSimulation(
                policy_allocation=real_uniform_allocation,
                seed=77,
                project_root=str(project_root),
            )
            sim.run(horizon_hours=24)
            summaries.append(sim.get_results()["summary"])

        for key in summaries[0]:
            if isinstance(summaries[0][key], (int, float)):
                assert summaries[0][key] == summaries[1][key], (
                    f"Mismatch on {key}: {summaries[0][key]} vs {summaries[1][key]}"
                )


# ── Independent Replication Tests ────────────────────────────────

class TestIndependentReplications:
    """Different seeds should produce statistically different results."""

    def test_different_seeds_differ(self, real_uniform_allocation, project_root):
        """Two different seeds should produce different incident counts."""
        results = {}
        for seed in [42, 999]:
            sim = EMSSimulation(
                policy_allocation=real_uniform_allocation,
                seed=seed,
                project_root=str(project_root),
            )
            sim.run(horizon_hours=48)
            results[seed] = sim.get_results()["summary"]

        # Very unlikely to have identical counts with different seeds
        # (but possible; check multiple metrics)
        differs = (
            results[42]["total_incidents"] != results[999]["total_incidents"]
            or abs(results[42]["response_time_mean"] - results[999]["response_time_mean"]) > 0.001
        )
        assert differs, "Different seeds should produce different results"

    def test_batch_runner_replications_vary(self, real_uniform_allocation, project_root):
        """BatchRunner replications with consecutive seeds should vary."""
        runner = BatchRunner(
            project_root=str(project_root),
            data_dir="data/processed",
        )
        agg = runner.run_scenario(
            policy_allocation=real_uniform_allocation,
            num_replications=5,
            seed_base=100,
            horizon_hours=24,
            policy_name="test",
        )

        per_rep = agg["per_replication"]
        counts = [r["total_incidents"] for r in per_rep]

        # Not all replications should have the same count
        assert len(set(counts)) > 1, (
            f"All 5 replications had same count: {counts}"
        )

    def test_batch_runner_confidence_intervals(self, real_uniform_allocation, project_root):
        """BatchRunner should produce valid confidence intervals."""
        runner = BatchRunner(
            project_root=str(project_root),
            data_dir="data/processed",
        )
        agg = runner.run_scenario(
            policy_allocation=real_uniform_allocation,
            num_replications=5,
            seed_base=200,
            horizon_hours=24,
            policy_name="ci_test",
        )

        # Check CI structure for response_time_mean
        rt = agg.get("response_time_mean")
        if rt is not None:
            assert rt["ci_lower"] <= rt["mean"] <= rt["ci_upper"]
            assert rt["std"] >= 0
            assert rt["min"] <= rt["mean"] <= rt["max"]
