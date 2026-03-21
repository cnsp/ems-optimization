#!/usr/bin/env python3
"""Production experiment runner for EMS Simulation Study – Phase 5.

Implements four experiment sets:
  Exp 1: Baseline policy comparison (P0, P1, P2 at K=20)
  Exp 2: Fleet size sensitivity (K ∈ {15, 20, 25, 30, 35, 40})
  Exp 3: Demand scaling sensitivity (δ ∈ {0.5, 0.75, 1.0, 1.25, 1.5, 2.0})
  Exp 4: Service time robustness (μ_s ∈ {20, 25, 30} minutes)

Uses common random numbers (CRN) across policies for variance reduction.

Usage:
    python scripts/run_production_experiments.py [--exp 1] [--reps 30]
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

# ── Project imports ──────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from ems_readiness.simulation.engine import EMSSimulation
from ems_readiness.optimization.allocator import EMSAllocator

# ── Logging ──────────────────────────────────────────────────────────
LOG_DIR = PROJECT_ROOT / "results" / "simulation" / "production"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "experiment_log.txt", mode="a"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────
SEED_BASE = 42
HORIZON_HOURS = 168
DEFAULT_K = 20
DEFAULT_DEMAND_MULT = 1.0
DEFAULT_SERVICE_MEAN = 25.0
DEFAULT_SERVICE_STD = 10.0
POLICIES = ["P0", "P1", "P2"]  # P0 = spatially-stratified uniform


# ── Allocation helpers ───────────────────────────────────────────────

def get_allocator() -> EMSAllocator:
    """Load the EMSAllocator with project data."""
    return EMSAllocator.from_project(str(PROJECT_ROOT))


def get_allocation(allocator: EMSAllocator, policy: str, K: int) -> pd.Series:
    """Get allocation for a given policy and fleet size.

    Tries to load from pre-computed CSV first; falls back to solving.
    """
    csv_path = PROJECT_ROOT / "results" / "optimization" / f"allocations_K{K}.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path, index_col=0)
        if policy in df.columns:
            return df[policy]

    # Generate dynamically
    if policy == "P0":
        result = allocator.baseline_p0(K=K)
    elif policy == "P1":
        result = allocator.baseline_demand_proportional(K=K)
    elif policy == "P2":
        result = allocator.solve("demand_weighted", K=K)
    else:
        raise ValueError(f"Unknown policy: {policy}")
    return result.allocation


# ── Single replication runner ────────────────────────────────────────

def run_single_replication(
    allocation: pd.Series,
    seed: int,
    demand_multiplier: float = 1.0,
    service_mean: float = 25.0,
    service_std: float = 10.0,
    horizon_hours: float = 168.0,
) -> Dict[str, Any]:
    """Run a single simulation replication and return summary metrics.

    Parameters
    ----------
    allocation : pd.Series
        Firehouse → unit count.
    seed : int
        Random seed for reproducibility.
    demand_multiplier : float
        Multiplier for base arrival rate.
    service_mean : float
        Mean service time (minutes).
    service_std : float
        Std dev of service time (minutes).
    horizon_hours : float
        Simulation horizon.

    Returns
    -------
    dict
        Summary statistics for this replication.
    """
    # Build custom config to inject demand multiplier + service time
    config = {
        "horizon_hours": horizon_hours,
        "warmup_hours": 0,
        "response_threshold_minutes": 8.0,
        "additional_thresholds": [6.0],
        "trace_mode": False,
    }

    sim = EMSSimulation(
        policy_allocation=allocation,
        config=config,
        seed=seed,
        data_dir="data/processed",
        project_root=str(PROJECT_ROOT),
        trace=False,
    )

    # Override demand multiplier by scaling base rate
    sim.arrival_gen.base_rate *= demand_multiplier

    # Override service time model
    if service_mean != 25.0 or service_std != 10.0:
        from ems_readiness.service.service_time import ServiceTimeModel
        sim.service_model = ServiceTimeModel(
            mean_minutes=service_mean,
            std_minutes=service_std,
            distribution="lognormal",
        )

    sim.run(horizon_hours=horizon_hours)
    results = sim.get_results()
    summary = results["summary"]

    # Extract utilization metrics from unit-level data
    util_data = results["unit_utilizations"]
    if isinstance(util_data, dict) and "per_unit" in util_data:
        unit_utils = list(util_data["per_unit"].values())
        mean_util = np.mean(unit_utils) if unit_utils else 0.0
        max_util = np.max(unit_utils) if unit_utils else 0.0
    elif isinstance(util_data, dict):
        unit_utils = list(util_data.values())
        mean_util = np.mean(unit_utils) if unit_utils else 0.0
        max_util = np.max(unit_utils) if unit_utils else 0.0
    else:
        mean_util = 0.0
        max_util = 0.0

    # Build response row
    row = {
        "mean_response_time": summary.get("response_time_mean", np.nan),
        "p90_response_time": summary.get("response_time_p90", np.nan),
        "p95_response_time": summary.get("response_time_p95",
                                          summary.get("response_time_p90", np.nan)),
        "coverage_6min": summary.get("coverage_6min", np.nan),
        "coverage_8min": summary.get("coverage_fraction", np.nan),
        "coverage_10min": _compute_coverage_10(results),
        "mean_utilization": mean_util,
        "max_utilization": max_util,
        "mean_queue_length": summary.get("queue_length_tw_avg", 0.0),
        "max_queue_length": summary.get("queue_length_max", 0),
        "queue_fraction": summary.get("queue_fraction", 0.0),
        "total_incidents": summary.get("total_incidents", 0),
        "incidents_queued": summary.get("incidents_queued", 0),
        "random_seed": seed,
    }
    return row


def _compute_coverage_10(results: Dict) -> float:
    """Compute 10-minute coverage from incident log."""
    log = results.get("incident_log")
    if log is not None and not log.empty and "response_time_minutes" in log.columns:
        return float((log["response_time_minutes"] <= 10.0).mean())
    # Fallback: use 8-min coverage as lower bound
    return results["summary"].get("coverage_fraction", np.nan)


# ── Experiment runners ───────────────────────────────────────────────

def run_experiment(
    experiment_id: str,
    scenarios: List[Dict[str, Any]],
    num_replications: int = 30,
    output_path: Optional[Path] = None,
) -> pd.DataFrame:
    """Run a full experiment set and return results DataFrame.

    Parameters
    ----------
    experiment_id : str
        Experiment identifier.
    scenarios : list of dict
        Each dict has keys: policy, allocation, K, demand_multiplier, service_time_mean.
    num_replications : int
        Replications per scenario.
    output_path : Path or None
        Where to save CSV.

    Returns
    -------
    pd.DataFrame
        All replication results.
    """
    total_runs = len(scenarios) * num_replications
    logger.info(f"\n{'='*60}")
    logger.info(f"EXPERIMENT: {experiment_id}")
    logger.info(f"Scenarios: {len(scenarios)}, Replications: {num_replications}, Total runs: {total_runs}")
    logger.info(f"{'='*60}")

    rows = []
    run_count = 0
    start_time = time.time()
    errors = []

    for si, scenario in enumerate(scenarios):
        policy = scenario["policy"]
        allocation = scenario["allocation"]
        K = scenario["K"]
        demand_mult = scenario.get("demand_multiplier", DEFAULT_DEMAND_MULT)
        svc_mean = scenario.get("service_time_mean", DEFAULT_SERVICE_MEAN)
        svc_std = scenario.get("service_time_std", DEFAULT_SERVICE_STD)
        scenario_id = scenario.get("scenario_id", f"{policy}_K{K}_d{demand_mult}_s{svc_mean}")

        for rep in range(num_replications):
            seed = SEED_BASE + rep
            run_count += 1

            try:
                row = run_single_replication(
                    allocation=allocation,
                    seed=seed,
                    demand_multiplier=demand_mult,
                    service_mean=svc_mean,
                    service_std=svc_std,
                    horizon_hours=HORIZON_HOURS,
                )
                row.update({
                    "experiment_id": experiment_id,
                    "scenario_id": scenario_id,
                    "replication": rep,
                    "policy": policy,
                    "K": K,
                    "demand_multiplier": demand_mult,
                    "service_time_mean": svc_mean,
                })
                rows.append(row)

            except Exception as e:
                err_msg = f"ERROR in {scenario_id} rep={rep}: {e}"
                logger.error(err_msg)
                errors.append(err_msg)
                traceback.print_exc()

            # Progress reporting
            if run_count % 50 == 0 or run_count == total_runs:
                elapsed = time.time() - start_time
                rate = run_count / elapsed if elapsed > 0 else 0
                remaining = (total_runs - run_count) / rate if rate > 0 else 0
                logger.info(
                    f"  Progress: {run_count}/{total_runs} "
                    f"({100*run_count/total_runs:.0f}%) "
                    f"| Elapsed: {elapsed:.1f}s "
                    f"| ETA: {remaining:.1f}s"
                )

    elapsed = time.time() - start_time
    df = pd.DataFrame(rows)

    # Reorder columns
    col_order = [
        "experiment_id", "scenario_id", "replication", "policy", "K",
        "demand_multiplier", "service_time_mean",
        "mean_response_time", "p90_response_time", "p95_response_time",
        "coverage_6min", "coverage_8min", "coverage_10min",
        "mean_utilization", "max_utilization",
        "mean_queue_length", "max_queue_length", "queue_fraction",
        "total_incidents", "incidents_queued", "random_seed",
    ]
    df = df[[c for c in col_order if c in df.columns]]

    if output_path:
        df.to_csv(output_path, index=False)
        logger.info(f"Saved {len(df)} rows to {output_path}")

    logger.info(f"Experiment {experiment_id} complete: {len(df)} rows, {elapsed:.1f}s, {len(errors)} errors")

    if errors:
        logger.warning(f"Errors encountered:\n" + "\n".join(errors))

    return df


# ── Experiment definitions ───────────────────────────────────────────

def build_exp1_scenarios(allocator: EMSAllocator) -> List[Dict]:
    """Experiment 1: Baseline Policy Comparison (K=20)."""
    scenarios = []
    for policy in POLICIES:
        alloc = get_allocation(allocator, policy, K=DEFAULT_K)
        scenarios.append({
            "policy": policy,
            "allocation": alloc,
            "K": DEFAULT_K,
            "scenario_id": f"{policy}_K{DEFAULT_K}",
        })
    return scenarios


def build_exp2_scenarios(allocator: EMSAllocator) -> List[Dict]:
    """Experiment 2: Fleet Size Sensitivity."""
    fleet_sizes = [15, 20, 25, 30, 35, 40]
    scenarios = []
    for K in fleet_sizes:
        for policy in POLICIES:
            alloc = get_allocation(allocator, policy, K=K)
            scenarios.append({
                "policy": policy,
                "allocation": alloc,
                "K": K,
                "scenario_id": f"{policy}_K{K}",
            })
    return scenarios


def build_exp3_scenarios(allocator: EMSAllocator) -> List[Dict]:
    """Experiment 3: Demand Scaling Sensitivity."""
    demand_multipliers = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
    scenarios = []
    for dm in demand_multipliers:
        for policy in POLICIES:
            alloc = get_allocation(allocator, policy, K=DEFAULT_K)
            scenarios.append({
                "policy": policy,
                "allocation": alloc,
                "K": DEFAULT_K,
                "demand_multiplier": dm,
                "scenario_id": f"{policy}_K{DEFAULT_K}_d{dm}",
            })
    return scenarios


def build_exp4_scenarios(allocator: EMSAllocator) -> List[Dict]:
    """Experiment 4: Service Time Robustness."""
    service_means = [20.0, 25.0, 30.0]
    scenarios = []
    for sm in service_means:
        # Keep coefficient of variation constant (std/mean = 10/25 = 0.4)
        ss = sm * (DEFAULT_SERVICE_STD / DEFAULT_SERVICE_MEAN)
        for policy in POLICIES:
            alloc = get_allocation(allocator, policy, K=DEFAULT_K)
            scenarios.append({
                "policy": policy,
                "allocation": alloc,
                "K": DEFAULT_K,
                "service_time_mean": sm,
                "service_time_std": ss,
                "scenario_id": f"{policy}_K{DEFAULT_K}_s{sm:.0f}",
            })
    return scenarios


# ── Summary report ───────────────────────────────────────────────────

def generate_summary_report(results: Dict[str, pd.DataFrame]):
    """Print and save a summary of all experiment results."""
    logger.info("\n" + "=" * 70)
    logger.info("PRODUCTION EXPERIMENT SUMMARY")
    logger.info("=" * 70)

    for exp_id, df in results.items():
        logger.info(f"\n--- {exp_id} ---")
        logger.info(f"  Total rows: {len(df)}")
        logger.info(f"  Scenarios: {df['scenario_id'].nunique()}")

        # Group by policy and summarize
        grp = df.groupby("policy")["mean_response_time"]
        for policy, vals in grp:
            logger.info(
                f"  {policy}: mean_RT={vals.mean():.2f} ± {vals.std():.2f} min, "
                f"coverage_8min={df[df['policy']==policy]['coverage_8min'].mean():.3f}"
            )

    # Save combined summary
    summary_rows = []
    for exp_id, df in results.items():
        for scenario_id, sdf in df.groupby("scenario_id"):
            summary_rows.append({
                "experiment": exp_id,
                "scenario": scenario_id,
                "policy": sdf["policy"].iloc[0],
                "K": sdf["K"].iloc[0],
                "demand_mult": sdf["demand_multiplier"].iloc[0],
                "svc_mean": sdf["service_time_mean"].iloc[0],
                "n_reps": len(sdf),
                "mean_RT": sdf["mean_response_time"].mean(),
                "std_RT": sdf["mean_response_time"].std(),
                "mean_coverage_8": sdf["coverage_8min"].mean(),
                "mean_p90_RT": sdf["p90_response_time"].mean(),
                "mean_utilization": sdf["mean_utilization"].mean(),
                "mean_queue_frac": sdf["queue_fraction"].mean(),
            })

    summary_df = pd.DataFrame(summary_rows)
    summary_path = LOG_DIR / "experiment_summary.csv"
    summary_df.to_csv(summary_path, index=False)
    logger.info(f"\nSaved experiment summary to {summary_path}")


# ── Main ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Run EMS production experiments")
    parser.add_argument("--exp", type=int, nargs="*", default=None,
                        help="Experiment(s) to run (1-4). Default: all")
    parser.add_argument("--reps", type=int, default=30,
                        help="Number of replications per scenario (default: 30)")
    args = parser.parse_args()

    experiments_to_run = args.exp or [1, 2, 3, 4]
    num_reps = args.reps

    logger.info(f"\n{'#'*70}")
    logger.info(f"EMS Production Experiments – {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Experiments: {experiments_to_run}, Replications: {num_reps}")
    logger.info(f"{'#'*70}")

    # Load allocator
    logger.info("Loading EMSAllocator...")
    allocator = get_allocator()

    all_results: Dict[str, pd.DataFrame] = {}
    total_start = time.time()

    # Experiment 1
    if 1 in experiments_to_run:
        scenarios = build_exp1_scenarios(allocator)
        df = run_experiment(
            "exp1_policy_comparison",
            scenarios,
            num_replications=num_reps,
            output_path=LOG_DIR / "exp1_policy_comparison.csv",
        )
        all_results["exp1"] = df

    # Experiment 2
    if 2 in experiments_to_run:
        scenarios = build_exp2_scenarios(allocator)
        df = run_experiment(
            "exp2_fleet_sensitivity",
            scenarios,
            num_replications=num_reps,
            output_path=LOG_DIR / "exp2_fleet_sensitivity.csv",
        )
        all_results["exp2"] = df

    # Experiment 3
    if 3 in experiments_to_run:
        scenarios = build_exp3_scenarios(allocator)
        df = run_experiment(
            "exp3_demand_sensitivity",
            scenarios,
            num_replications=num_reps,
            output_path=LOG_DIR / "exp3_demand_sensitivity.csv",
        )
        all_results["exp3"] = df

    # Experiment 4
    if 4 in experiments_to_run:
        scenarios = build_exp4_scenarios(allocator)
        df = run_experiment(
            "exp4_service_robustness",
            scenarios,
            num_replications=num_reps,
            output_path=LOG_DIR / "exp4_service_robustness.csv",
        )
        all_results["exp4"] = df

    # Summary
    total_elapsed = time.time() - total_start
    generate_summary_report(all_results)

    total_runs = sum(len(df) for df in all_results.values())
    logger.info(f"\nALL EXPERIMENTS COMPLETE")
    logger.info(f"Total runs: {total_runs}")
    logger.info(f"Total time: {total_elapsed:.1f}s ({total_elapsed/60:.1f} min)")
    logger.info(f"Avg time per run: {total_elapsed/total_runs:.3f}s" if total_runs else "No runs")


if __name__ == "__main__":
    main()
