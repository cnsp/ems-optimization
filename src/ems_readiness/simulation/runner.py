"""Batch runner for multiple simulation replications.

Executes a scenario (policy × K) across N replications with
different random seeds and aggregates results with confidence intervals.

Usage
-----
>>> from ems_readiness.simulation.runner import BatchRunner
>>> runner = BatchRunner(project_root=".")
>>> results = runner.run_scenario(policy_alloc, K=40, num_replications=30)
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd
from scipy import stats

from ems_readiness.simulation.engine import EMSSimulation

logger = logging.getLogger(__name__)


class BatchRunner:
    """Execute multiple replications of an EMS simulation scenario.

    Parameters
    ----------
    project_root : str or Path
        Project root directory.
    data_dir : str or Path
        Relative path to processed data.
    config : dict or None
        Shared simulation configuration.
    """

    def __init__(
        self,
        project_root: str | Path = ".",
        data_dir: str | Path = "data/processed",
        config: Optional[Dict] = None,
    ):
        self.project_root = Path(project_root)
        self.data_dir = data_dir
        self.config = config
        self._results: List[Dict[str, Any]] = []

    def run_scenario(
        self,
        policy_allocation: pd.Series,
        K: Optional[int] = None,
        num_replications: int = 30,
        seed_base: int = 42,
        horizon_hours: Optional[float] = None,
        policy_name: str = "unnamed",
        trace: bool = False,
    ) -> Dict[str, Any]:
        """Run multiple replications of a single scenario.

        Parameters
        ----------
        policy_allocation : pd.Series
            Firehouse → unit count.
        K : int or None
            Total units (for labelling; inferred from allocation if None).
        num_replications : int
            Number of independent replications.
        seed_base : int
            Base seed; replication i uses seed_base + i.
        horizon_hours : float or None
            Simulation horizon (uses config default if None).
        policy_name : str
            Label for this policy scenario.
        trace : bool
            Enable trace logging.

        Returns
        -------
        dict
            Aggregated results with means, CIs, and per-replication data.
        """
        if K is None:
            K = int(policy_allocation.sum())

        logger.info(
            f"Running scenario: policy={policy_name}, K={K}, "
            f"replications={num_replications}, seed_base={seed_base}"
        )

        rep_summaries: List[Dict] = []
        rep_logs: List[pd.DataFrame] = []

        for rep in range(num_replications):
            seed = seed_base + rep
            logger.debug(f"  Replication {rep + 1}/{num_replications} (seed={seed})")

            sim = EMSSimulation(
                policy_allocation=policy_allocation,
                config=self.config,
                seed=seed,
                data_dir=self.data_dir,
                project_root=str(self.project_root),
                trace=trace,
            )

            sim.run(horizon_hours=horizon_hours)
            results = sim.get_results()

            summary = results["summary"]
            summary["replication"] = rep
            summary["seed"] = seed
            rep_summaries.append(summary)

            # Keep incident log only if trace mode (memory management)
            if trace:
                log = results["incident_log"]
                log["replication"] = rep
                rep_logs.append(log)

        # Aggregate
        agg = self._aggregate_results(rep_summaries)
        agg["policy_name"] = policy_name
        agg["K"] = K
        agg["num_replications"] = num_replications
        agg["seed_base"] = seed_base
        agg["per_replication"] = rep_summaries

        if rep_logs:
            agg["incident_logs"] = pd.concat(rep_logs, ignore_index=True)

        self._results.append(agg)
        return agg

    def _aggregate_results(
        self, rep_summaries: List[Dict], confidence: float = 0.95
    ) -> Dict[str, Any]:
        """Compute means and confidence intervals across replications.

        Parameters
        ----------
        rep_summaries : list of dicts
            Per-replication summary statistics.
        confidence : float
            Confidence level for intervals.

        Returns
        -------
        dict
            Aggregated statistics with mean, std, ci_lower, ci_upper.
        """
        df = pd.DataFrame(rep_summaries)
        agg = {}

        # Key metrics to aggregate
        metrics = [
            "total_incidents",
            "incidents_queued",
            "queue_fraction",
            "dispatch_delay_mean",
            "dispatch_delay_median",
            "dispatch_delay_p90",
            "response_time_mean",
            "response_time_median",
            "response_time_p90",
            "response_time_std",
            "coverage_fraction",
            "incidents_within_threshold",
            "coverage_6min",
            "coverage_8min",
            "travel_time_mean",
            "service_time_mean",
            "queue_length_max",
            "queue_length_tw_avg",
        ]
        # Dynamically add any additional coverage_*min columns from data
        if rep_summaries:
            for key in rep_summaries[0]:
                if key.startswith("coverage_") and key.endswith("min") and key not in metrics:
                    metrics.append(key)

        for metric in metrics:
            if metric in df.columns:
                values = df[metric].values
                n = len(values)
                mean = float(np.mean(values))
                std = float(np.std(values, ddof=1)) if n > 1 else 0.0

                if n > 1 and std > 0:
                    t_crit = stats.t.ppf((1 + confidence) / 2, df=n - 1)
                    margin = t_crit * std / np.sqrt(n)
                else:
                    margin = 0.0

                agg[metric] = {
                    "mean": mean,
                    "std": std,
                    "ci_lower": mean - margin,
                    "ci_upper": mean + margin,
                    "min": float(np.min(values)),
                    "max": float(np.max(values)),
                }

        return agg

    def get_all_results(self) -> List[Dict[str, Any]]:
        """Return results from all scenarios run so far."""
        return self._results

    def get_comparison_table(self) -> pd.DataFrame:
        """Build a summary comparison table across all scenarios.

        Returns
        -------
        pd.DataFrame
            One row per scenario with key metrics.
        """
        rows = []
        for r in self._results:
            row = {
                "policy": r.get("policy_name", ""),
                "K": r.get("K", 0),
                "replications": r.get("num_replications", 0),
            }
            for metric in [
                "response_time_mean",
                "coverage_fraction",
                "dispatch_delay_mean",
                "queue_fraction",
                "total_incidents",
            ]:
                if metric in r:
                    row[f"{metric}_mean"] = r[metric]["mean"]
                    row[f"{metric}_ci_lower"] = r[metric]["ci_lower"]
                    row[f"{metric}_ci_upper"] = r[metric]["ci_upper"]
            rows.append(row)
        return pd.DataFrame(rows)

    def save_results(
        self,
        output_dir: str | Path = "results/simulation",
        prefix: str = "",
    ) -> None:
        """Save all results to files.

        Parameters
        ----------
        output_dir : str or Path
            Directory to save results.
        prefix : str
            Optional filename prefix.
        """
        out = self.project_root / output_dir
        out.mkdir(parents=True, exist_ok=True)

        # Comparison table
        comp = self.get_comparison_table()
        if not comp.empty:
            fname = f"{prefix}comparison.csv" if prefix else "comparison.csv"
            comp.to_csv(out / fname, index=False)
            logger.info(f"Saved comparison table to {out / fname}")

        # Per-scenario summaries
        for r in self._results:
            pname = r.get("policy_name", "unknown")
            k = r.get("K", 0)
            fname = f"{prefix}{pname}_K{k}_summary.json"

            # Make JSON-serializable
            summary = {}
            for key, val in r.items():
                if key in ("per_replication", "incident_logs"):
                    continue
                if isinstance(val, dict):
                    summary[key] = {
                        k2: (float(v2) if isinstance(v2, (np.floating, np.integer)) else v2)
                        for k2, v2 in val.items()
                    }
                else:
                    summary[key] = val

            with open(out / fname, "w") as f:
                json.dump(summary, f, indent=2, default=str)
            logger.info(f"Saved {fname}")

    def reset(self) -> None:
        """Clear all stored results."""
        self._results.clear()

    def __repr__(self) -> str:
        return f"BatchRunner(scenarios_run={len(self._results)})"
