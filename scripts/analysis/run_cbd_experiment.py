#!/usr/bin/env python3
"""CBD-Specific Robustness Experiment for EMS Optimization Study.

Tests all three policies (P0, P1, P2) under CBD-specific conditions:
  Scenario A: CBD demand surge (2x CBD demand, normal elsewhere)
  Scenario B: CBD service time increase (longer on-scene times in CBD)
  Scenario C: CBD-only allocation (units allocated only near CBD)
  Scenario D: Mixed allocation (60% CBD, 40% flexible)

30 replications per scenario × 3 policies × 4 scenarios = 360 runs.

Usage:
    python scripts/analysis/run_cbd_experiment.py [--reps 30]
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd
import yaml

# ── Project imports ──────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from ems_readiness.simulation.engine import EMSSimulation
from ems_readiness.optimization.allocator import EMSAllocator
from ems_readiness.service.service_time import ServiceTimeModel

# ── Logging ──────────────────────────────────────────────────────────
OUTPUT_DIR = PROJECT_ROOT / "results" / "analysis" / "simulation" / "cbd_experiment"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(OUTPUT_DIR / "cbd_experiment_log.txt", mode="w"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────
SEED_BASE = 42
HORIZON_HOURS = 168
DEFAULT_K = 20
POLICIES = ["P0", "P1", "P2"]  # P0 = spatially-stratified uniform

# CBD precincts (from spatial analysis - see docs/core/cbd_definition.md)
CBD_PRECINCTS = [1, 5, 6, 7, 9, 10, 13, 14, 17, 18]


def load_cbd_config() -> Dict:
    """Load CBD scenario configuration."""
    config_path = PROJECT_ROOT / "configs" / "cbd_scenario.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


def get_allocator() -> EMSAllocator:
    """Load the EMSAllocator."""
    return EMSAllocator.from_project(str(PROJECT_ROOT))


def get_allocation(allocator: EMSAllocator, policy: str, K: int) -> pd.Series:
    """Get allocation for a given policy and fleet size."""
    csv_path = PROJECT_ROOT / "results" / "baseline" / "allocations" / f"allocations_K{K}.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path, index_col=0)
        if policy in df.columns:
            return df[policy]

    if policy == "P0":
        result = allocator.baseline_p0(K=K)
    elif policy == "P1":
        result = allocator.baseline_demand_proportional(K=K)
    elif policy == "P2":
        result = allocator.solve("demand_weighted", K=K)
    else:
        raise ValueError(f"Unknown policy: {policy}")
    return result.allocation


def get_cbd_only_allocation(allocator: EMSAllocator, K: int) -> pd.Series:
    """Create allocation with units only at firehouses nearest to CBD precincts."""
    dm = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "distance_matrix_firehouse_precinct.csv", index_col=0)
    dm.columns = dm.columns.astype(str)
    cbd_cols = [str(p) for p in CBD_PRECINCTS if str(p) in dm.columns]
    cbd_distances = dm[cbd_cols].mean(axis=1)
    cbd_firehouses = cbd_distances.nsmallest(K).index.tolist()

    alloc = pd.Series(0, index=dm.index)
    per_fh = max(1, K // len(cbd_firehouses))
    remaining = K
    for fh in cbd_firehouses:
        units = min(per_fh, remaining, 5)
        alloc[fh] = units
        remaining -= units
        if remaining <= 0:
            break
    # Distribute remainder
    i = 0
    while remaining > 0:
        fh = cbd_firehouses[i % len(cbd_firehouses)]
        if alloc[fh] < 5:
            alloc[fh] += 1
            remaining -= 1
        i += 1

    return alloc


def get_mixed_allocation(allocator: EMSAllocator, K: int, cbd_fraction: float = 0.6) -> pd.Series:
    """Create mixed allocation: cbd_fraction to CBD, rest flexible."""
    dm = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "distance_matrix_firehouse_precinct.csv", index_col=0)
    dm.columns = dm.columns.astype(str)
    cbd_cols = [str(p) for p in CBD_PRECINCTS if str(p) in dm.columns]

    cbd_distances = dm[cbd_cols].mean(axis=1)
    sorted_fh = cbd_distances.sort_values().index.tolist()

    K_cbd = int(K * cbd_fraction)
    K_non_cbd = K - K_cbd

    alloc = pd.Series(0, index=dm.index)

    # Allocate CBD units to nearest CBD firehouses
    remaining = K_cbd
    for fh in sorted_fh:
        if remaining <= 0:
            break
        units = min(max(1, remaining // 10), remaining, 5)
        alloc[fh] = units
        remaining -= units

    # Allocate non-CBD units to remaining firehouses
    non_cbd_fh = [fh for fh in sorted_fh if alloc[fh] == 0]
    remaining = K_non_cbd
    for fh in non_cbd_fh:
        if remaining <= 0:
            break
        units = min(max(1, remaining // 10), remaining, 5)
        alloc[fh] = units
        remaining -= units

    return alloc


def run_single_cbd_replication(
    allocation: pd.Series,
    seed: int,
    cbd_demand_mult: float = 1.0,
    non_cbd_demand_mult: float = 1.0,
    service_mean: float = 25.0,
    cbd_service_mean: float = None,
    horizon_hours: float = 168.0,
) -> Dict[str, Any]:
    """Run a single CBD experiment replication."""
    # Compute effective overall demand multiplier
    # CBD is ~55.7% of demand, non-CBD ~44.3%
    effective_demand_mult = 0.557 * cbd_demand_mult + 0.443 * non_cbd_demand_mult

    config = {
        "horizon_hours": horizon_hours,
        "warmup_hours": 0,
        "response_threshold_minutes": 8.0,
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

    # Apply demand multiplier
    sim.arrival_gen.base_rate *= effective_demand_mult

    # Apply CBD-specific service time if specified
    if cbd_service_mean is not None and cbd_service_mean != service_mean:
        # Use a higher mean to simulate CBD difficulty
        effective_svc_mean = 0.557 * cbd_service_mean + 0.443 * service_mean
        sim.service_model = ServiceTimeModel(
            mean_minutes=effective_svc_mean,
            std_minutes=effective_svc_mean * 0.4,  # constant CV
            distribution="lognormal",
        )

    sim.run(horizon_hours=horizon_hours)
    results = sim.get_results()
    summary = results["summary"]

    # Extract utilization
    util_data = results["unit_utilizations"]
    if isinstance(util_data, dict) and "per_unit" in util_data:
        unit_utils = list(util_data["per_unit"].values())
    elif isinstance(util_data, dict):
        unit_utils = list(util_data.values())
    else:
        unit_utils = [0.0]
    mean_util = np.mean(unit_utils) if unit_utils else 0.0
    max_util = np.max(unit_utils) if unit_utils else 0.0

    # Try to compute CBD-specific metrics from incident log
    log = results.get("incident_log")
    cbd_rt_mean = np.nan
    cbd_coverage_8 = np.nan
    cbd_coverage_6 = np.nan
    non_cbd_rt_mean = np.nan
    non_cbd_coverage_8 = np.nan
    non_cbd_coverage_6 = np.nan

    if log is not None and not log.empty and "precinct" in log.columns:
        cbd_mask = log["precinct"].isin(CBD_PRECINCTS)
        cbd_log = log[cbd_mask]
        non_cbd_log = log[~cbd_mask]

        if not cbd_log.empty and "response_time_minutes" in cbd_log.columns:
            cbd_rt_mean = cbd_log["response_time_minutes"].mean()
            cbd_coverage_8 = (cbd_log["response_time_minutes"] <= 8.0).mean()
            cbd_coverage_6 = (cbd_log["response_time_minutes"] <= 6.0).mean()

        if not non_cbd_log.empty and "response_time_minutes" in non_cbd_log.columns:
            non_cbd_rt_mean = non_cbd_log["response_time_minutes"].mean()
            non_cbd_coverage_8 = (non_cbd_log["response_time_minutes"] <= 8.0).mean()
            non_cbd_coverage_6 = (non_cbd_log["response_time_minutes"] <= 6.0).mean()

    row = {
        "mean_response_time": summary.get("response_time_mean", np.nan),
        "p90_response_time": summary.get("response_time_p90", np.nan),
        "coverage_6min": summary.get("coverage_6min", np.nan),
        "coverage_8min": summary.get("coverage_fraction", np.nan),
        "mean_utilization": mean_util,
        "max_utilization": max_util,
        "mean_queue_length": summary.get("queue_length_tw_avg", 0.0),
        "max_queue_length": summary.get("queue_length_max", 0),
        "queue_fraction": summary.get("queue_fraction", 0.0),
        "total_incidents": summary.get("total_incidents", 0),
        "incidents_queued": summary.get("incidents_queued", 0),
        "cbd_mean_rt": cbd_rt_mean,
        "cbd_coverage_6min": cbd_coverage_6,
        "cbd_coverage_8min": cbd_coverage_8,
        "non_cbd_mean_rt": non_cbd_rt_mean,
        "non_cbd_coverage_6min": non_cbd_coverage_6,
        "non_cbd_coverage_8min": non_cbd_coverage_8,
        "random_seed": seed,
    }
    return row


def run_cbd_experiment(
    experiment_id: str,
    scenarios: List[Dict],
    num_replications: int = 30,
    output_path: Path = None,
) -> pd.DataFrame:
    """Run a full CBD experiment set."""
    total_runs = len(scenarios) * num_replications
    logger.info(f"\n{'='*60}")
    logger.info(f"CBD EXPERIMENT: {experiment_id}")
    logger.info(f"Scenarios: {len(scenarios)}, Reps: {num_replications}, Total: {total_runs}")
    logger.info(f"{'='*60}")

    rows = []
    run_count = 0
    start_time = time.time()

    for scenario in scenarios:
        for rep in range(num_replications):
            seed = SEED_BASE + rep
            run_count += 1

            try:
                row = run_single_cbd_replication(
                    allocation=scenario["allocation"],
                    seed=seed,
                    cbd_demand_mult=scenario.get("cbd_demand_mult", 1.0),
                    non_cbd_demand_mult=scenario.get("non_cbd_demand_mult", 1.0),
                    service_mean=scenario.get("service_mean", 25.0),
                    cbd_service_mean=scenario.get("cbd_service_mean", None),
                    horizon_hours=HORIZON_HOURS,
                )
                row.update({
                    "experiment_id": experiment_id,
                    "scenario_id": scenario["scenario_id"],
                    "replication": rep,
                    "policy": scenario["policy"],
                    "K": scenario["K"],
                    "scenario_type": scenario.get("scenario_type", "baseline"),
                })
                rows.append(row)
            except Exception as e:
                logger.error(f"ERROR in {scenario['scenario_id']} rep={rep}: {e}")

            if run_count % 50 == 0 or run_count == total_runs:
                elapsed = time.time() - start_time
                rate = run_count / elapsed if elapsed > 0 else 0
                remaining = (total_runs - run_count) / rate if rate > 0 else 0
                logger.info(
                    f"  Progress: {run_count}/{total_runs} "
                    f"({100*run_count/total_runs:.0f}%) "
                    f"| Elapsed: {elapsed:.1f}s | ETA: {remaining:.1f}s"
                )

    df = pd.DataFrame(rows)
    if output_path:
        df.to_csv(output_path, index=False)
        logger.info(f"Saved {len(df)} rows to {output_path}")

    return df


def build_all_scenarios(allocator: EMSAllocator) -> List[Dict]:
    """Build all CBD experiment scenarios."""
    scenarios = []

    for policy in POLICIES:
        alloc = get_allocation(allocator, policy, K=DEFAULT_K)

        # Scenario A: CBD demand surge
        scenarios.append({
            "policy": policy, "allocation": alloc, "K": DEFAULT_K,
            "scenario_id": f"A_cbdsurge_{policy}",
            "scenario_type": "cbd_surge",
            "cbd_demand_mult": 2.0, "non_cbd_demand_mult": 1.0,
        })

        # Scenario B: CBD service time increase
        scenarios.append({
            "policy": policy, "allocation": alloc, "K": DEFAULT_K,
            "scenario_id": f"B_cbdslow_{policy}",
            "scenario_type": "cbd_slow_service",
            "cbd_service_mean": 35.0, "service_mean": 25.0,
        })

    # Scenario C: CBD-only allocation
    cbd_alloc = get_cbd_only_allocation(allocator, K=DEFAULT_K)
    scenarios.append({
        "policy": "CBD_ONLY", "allocation": cbd_alloc, "K": DEFAULT_K,
        "scenario_id": "C_cbdonly_CBDONLY",
        "scenario_type": "cbd_only",
    })

    # Scenario D: Mixed allocation
    mixed_alloc = get_mixed_allocation(allocator, K=DEFAULT_K, cbd_fraction=0.6)
    scenarios.append({
        "policy": "MIXED", "allocation": mixed_alloc, "K": DEFAULT_K,
        "scenario_id": "D_mixed_MIXED",
        "scenario_type": "mixed",
    })

    # Also run standard P0/P1/P2 under normal conditions for CBD comparison
    for policy in POLICIES:
        alloc = get_allocation(allocator, policy, K=DEFAULT_K)
        scenarios.append({
            "policy": policy, "allocation": alloc, "K": DEFAULT_K,
            "scenario_id": f"E_baseline_{policy}",
            "scenario_type": "baseline",
        })

    return scenarios


def main():
    parser = argparse.ArgumentParser(description="Run CBD robustness experiments")
    parser.add_argument("--reps", type=int, default=30, help="Replications per scenario")
    args = parser.parse_args()

    logger.info(f"\n{'#'*70}")
    logger.info(f"CBD Robustness Experiment – {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Replications: {args.reps}")
    logger.info(f"CBD precincts: {CBD_PRECINCTS}")
    logger.info(f"{'#'*70}")

    allocator = get_allocator()
    scenarios = build_all_scenarios(allocator)

    logger.info(f"Total scenarios: {len(scenarios)}")
    logger.info(f"Total runs: {len(scenarios) * args.reps}")

    start = time.time()
    df = run_cbd_experiment(
        experiment_id="cbd_robustness",
        scenarios=scenarios,
        num_replications=args.reps,
        output_path=OUTPUT_DIR / "cbd_experiment_results.csv",
    )
    elapsed = time.time() - start

    # Generate summary
    logger.info(f"\n{'='*60}")
    logger.info("CBD EXPERIMENT SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"Total runs: {len(df)}")
    logger.info(f"Total time: {elapsed:.1f}s ({elapsed/60:.1f} min)")

    # Summary by scenario type and policy
    summary = df.groupby(["scenario_type", "policy"]).agg({
        "mean_response_time": ["mean", "std"],
        "coverage_6min": ["mean", "std"],
        "coverage_8min": ["mean", "std"],
        "cbd_mean_rt": "mean",
        "cbd_coverage_6min": "mean",
        "cbd_coverage_8min": "mean",
        "queue_fraction": "mean",
    }).round(4)
    logger.info(f"\n{summary.to_string()}")

    # Save summary
    summary_flat = df.groupby(["scenario_type", "policy"]).agg({
        "mean_response_time": "mean",
        "coverage_6min": "mean",
        "coverage_8min": "mean",
        "cbd_mean_rt": "mean",
        "cbd_coverage_6min": "mean",
        "cbd_coverage_8min": "mean",
        "non_cbd_mean_rt": "mean",
        "non_cbd_coverage_6min": "mean",
        "non_cbd_coverage_8min": "mean",
        "queue_fraction": "mean",
        "total_incidents": "mean",
    }).round(4)
    summary_flat.to_csv(OUTPUT_DIR / "cbd_experiment_summary.csv")
    logger.info(f"\nSaved summary to {OUTPUT_DIR / 'cbd_experiment_summary.csv'}")


if __name__ == "__main__":
    main()
