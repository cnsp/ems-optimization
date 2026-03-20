#!/usr/bin/env python3
"""Run validation pilot runs and save results.

Pilots:
1. Baseline P0 (spatially-stratified) vs P2 (demand-weighted MIP): K=20, 1 week, 30 reps
2. Sensitivity to K: P2 with K=[10, 20, 30, 40]
3. Sensitivity to demand: P2 K=20 with demand scaled [0.5x, 1x, 2x]

Policy nomenclature (v2.0):
  P0 = spatially_stratified_allocation (latitude-based baseline)
  P1 = demand_proportional_allocation
  P2 = demand-weighted MIP (build_demand_weighted)
"""

import json
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from ems_readiness.simulation.engine import EMSSimulation
from ems_readiness.simulation.runner import BatchRunner

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

OUT_DIR = PROJECT_ROOT / "results" / "simulation" / "validation_pilot"
OUT_DIR.mkdir(parents=True, exist_ok=True)

dm = pd.read_csv(PROJECT_ROOT / "data/processed/distance_matrix_firehouse_precinct.csv", index_col=0)
dm.columns = dm.columns.astype(str)
all_fhs = dm.index.tolist()


def make_p0_allocation(K):
    """P0: Spatially-stratified uniform allocation (canonical baseline)."""
    from ems_readiness.optimization.policies import spatially_stratified_allocation
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        return spatially_stratified_allocation(K=K, method="latitude", capacity=2)


def make_p2_allocation(K, capacity=2):
    """P2: Demand-weighted MIP optimized allocation."""
    from ems_readiness.optimization.allocator import EMSAllocator
    allocator = EMSAllocator.from_project(PROJECT_ROOT)
    result = allocator.solve(K=K, model="demand_weighted", capacity=capacity)
    return result.allocation


def make_p1_allocation(K, capacity=2):
    """P1: Demand-proportional allocation."""
    from ems_readiness.optimization.policies import demand_proportional_allocation
    from ems_readiness.service.travel_time import build_travel_time_matrix
    tt = build_travel_time_matrix(dm)
    precinct_rates = pd.read_csv(
        PROJECT_ROOT / "data/processed/demand_lambda_precinct.csv"
    )
    rate_col = "crash_rate_per_hour" if "crash_rate_per_hour" in precinct_rates.columns else "lambda_per_hour"
    demand = precinct_rates.set_index("precinct")[rate_col]
    demand.index = demand.index.astype(str)
    return demand_proportional_allocation(tt, demand, K=K, capacity=capacity)


def save_pilot_result(name, data):
    """Save pilot result as JSON."""
    path = OUT_DIR / f"{name}.json"
    # Make JSON-serializable
    serializable = {}
    for k, v in data.items():
        if isinstance(v, dict):
            serializable[k] = {}
            for k2, v2 in v.items():
                if isinstance(v2, dict):
                    serializable[k][k2] = {
                        k3: (float(v3) if isinstance(v3, (np.floating, np.integer)) else v3)
                        for k3, v3 in v2.items()
                    }
                elif isinstance(v2, (np.floating, np.integer)):
                    serializable[k][k2] = float(v2)
                else:
                    serializable[k][k2] = v2
        elif isinstance(v, list):
            serializable[k] = v
        elif isinstance(v, (np.floating, np.integer)):
            serializable[k] = float(v)
        else:
            serializable[k] = v
    with open(path, "w") as f:
        json.dump(serializable, f, indent=2, default=str)
    logger.info(f"Saved {path}")


# ── Pilot 1: Baseline P0 vs P2 ──────────────────────────────────

def run_p0_vs_p2():
    """Compare P0 (spatially-stratified) vs P2 (demand-weighted MIP) allocations."""
    logger.info("\n" + "=" * 60)
    logger.info("PILOT 1: P0 (Spatially-Stratified) vs P2 (Demand-Weighted MIP), K=20")
    logger.info("=" * 60)

    K = 20
    N_REPS = 30
    HORIZON = 168  # 1 week

    alloc_p0 = make_p0_allocation(K)
    alloc_p2 = make_p2_allocation(K)

    logger.info(f"P0 active firehouses: {(alloc_p0 > 0).sum()}")
    logger.info(f"P2 active firehouses: {(alloc_p2 > 0).sum()}")
    logger.info(f"P2 top allocations:\n{alloc_p2[alloc_p2 > 0].sort_values(ascending=False).head(10)}")

    runner = BatchRunner(project_root=str(PROJECT_ROOT), data_dir="data/processed")

    logger.info(f"\nRunning P0 ({N_REPS} replications, {HORIZON}h)...")
    agg_p0 = runner.run_scenario(
        policy_allocation=alloc_p0, K=K,
        num_replications=N_REPS, seed_base=100,
        horizon_hours=HORIZON, policy_name="P0",
    )

    logger.info(f"\nRunning P2 ({N_REPS} replications, {HORIZON}h)...")
    agg_p2 = runner.run_scenario(
        policy_allocation=alloc_p2, K=K,
        num_replications=N_REPS, seed_base=100,
        horizon_hours=HORIZON, policy_name="P2",
    )

    comparison = {
        "scenario": "P0_vs_P2",
        "K": K,
        "horizon_hours": HORIZON,
        "num_replications": N_REPS,
    }

    for name, agg in [("P0", agg_p0), ("P2", agg_p2)]:
        metrics = {}
        for metric in ["response_time_mean", "coverage_fraction", "queue_fraction",
                       "total_incidents", "dispatch_delay_mean", "response_time_p90"]:
            if metric in agg:
                metrics[metric] = agg[metric]
        comparison[name] = metrics

    # Log comparison
    logger.info("\n--- P0 vs P2 Comparison ---")
    for metric in ["response_time_mean", "coverage_fraction", "queue_fraction"]:
        p0_val = comparison["P0"].get(metric, {}).get("mean", "N/A")
        p2_val = comparison["P2"].get(metric, {}).get("mean", "N/A")
        logger.info(f"  {metric}: P0={p0_val:.4f}, P2={p2_val:.4f}")

    save_pilot_result("pilot1_p0_vs_p2", comparison)

    # Save comparison table
    comp_table = runner.get_comparison_table()
    comp_table.to_csv(OUT_DIR / "pilot1_comparison_table.csv", index=False)

    return comparison


# ── Pilot 2: Sensitivity to K ───────────────────────────────────

def run_sensitivity_K():
    """Test P2 with K=[10, 20, 30, 40]."""
    logger.info("\n" + "=" * 60)
    logger.info("PILOT 2: Sensitivity to K (P2 allocation)")
    logger.info("=" * 60)

    K_values = [10, 20, 30, 40]
    N_REPS = 15  # Fewer reps for speed
    HORIZON = 168

    runner = BatchRunner(project_root=str(PROJECT_ROOT), data_dir="data/processed")
    results = {}

    for K in K_values:
        logger.info(f"\n  K={K}...")
        alloc = make_p2_allocation(K)
        agg = runner.run_scenario(
            policy_allocation=alloc, K=K,
            num_replications=N_REPS, seed_base=200,
            horizon_hours=HORIZON, policy_name=f"P2_K{K}",
        )
        metrics = {}
        for metric in ["response_time_mean", "coverage_fraction", "queue_fraction",
                       "total_incidents"]:
            if metric in agg:
                metrics[metric] = agg[metric]
        results[f"K={K}"] = metrics

    data = {
        "scenario": "sensitivity_K",
        "K_values": K_values,
        "horizon_hours": HORIZON,
        "num_replications": N_REPS,
        "results": results,
    }

    # Verify monotonicity: more units → better performance
    rt_means = []
    cov_means = []
    for K in K_values:
        rt_means.append(results[f"K={K}"]["response_time_mean"]["mean"])
        cov_means.append(results[f"K={K}"]["coverage_fraction"]["mean"])

    data["response_time_decreasing"] = all(
        rt_means[i] >= rt_means[i + 1] - 0.5  # small tolerance
        for i in range(len(rt_means) - 1)
    )
    data["coverage_increasing"] = all(
        cov_means[i] <= cov_means[i + 1] + 0.02
        for i in range(len(cov_means) - 1)
    )

    logger.info("\n--- Sensitivity to K ---")
    for K in K_values:
        rt = results[f"K={K}"]["response_time_mean"]["mean"]
        cov = results[f"K={K}"]["coverage_fraction"]["mean"]
        qf = results[f"K={K}"]["queue_fraction"]["mean"]
        logger.info(f"  K={K:3d}: RT={rt:.2f} min, Cov={cov:.3f}, QueueFrac={qf:.3f}")

    logger.info(f"  Response time decreasing: {data['response_time_decreasing']}")
    logger.info(f"  Coverage increasing: {data['coverage_increasing']}")

    save_pilot_result("pilot2_sensitivity_K", data)

    # Save table
    comp = runner.get_comparison_table()
    comp.to_csv(OUT_DIR / "pilot2_sensitivity_K_table.csv", index=False)

    return data


# ── Pilot 3: Sensitivity to Demand ──────────────────────────────

def run_sensitivity_demand():
    """Test P2 K=20 with demand scaled [0.5x, 1x, 2x]."""
    logger.info("\n" + "=" * 60)
    logger.info("PILOT 3: Sensitivity to Demand (P2, K=20)")
    logger.info("=" * 60)

    K = 20
    N_REPS = 15
    HORIZON = 168
    demand_scales = [0.5, 1.0, 2.0]
    alloc = make_p2_allocation(K)
    results = {}

    for scale in demand_scales:
        logger.info(f"\n  Demand scale={scale}x...")
        runner = BatchRunner(project_root=str(PROJECT_ROOT), data_dir="data/processed")

        # For each replication, create a simulation with modified arrival rate
        rep_summaries = []
        for rep in range(N_REPS):
            seed = 300 + rep
            sim = EMSSimulation(
                policy_allocation=alloc,
                seed=seed,
                project_root=str(PROJECT_ROOT),
            )

            if scale != 1.0:
                # Modify the base rate of the arrival generator
                sim.arrival_gen.base_rate = sim.arrival_gen.base_rate * scale

            sim.run(horizon_hours=HORIZON)
            rep_summaries.append(sim.get_results()["summary"])

        # Aggregate manually
        df = pd.DataFrame(rep_summaries)
        metrics = {}
        for metric in ["response_time_mean", "coverage_fraction", "queue_fraction",
                       "total_incidents"]:
            if metric in df.columns:
                vals = df[metric].values
                metrics[metric] = {
                    "mean": float(np.mean(vals)),
                    "std": float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0,
                    "min": float(np.min(vals)),
                    "max": float(np.max(vals)),
                }
        results[f"scale_{scale}x"] = metrics

    data = {
        "scenario": "sensitivity_demand",
        "K": K,
        "demand_scales": demand_scales,
        "horizon_hours": HORIZON,
        "num_replications": N_REPS,
        "results": results,
    }

    # Verify: higher demand → worse performance
    rt_means = [
        results[f"scale_{s}x"]["response_time_mean"]["mean"]
        for s in demand_scales
    ]
    data["response_time_increases_with_demand"] = all(
        rt_means[i] <= rt_means[i + 1] + 0.5
        for i in range(len(rt_means) - 1)
    )

    logger.info("\n--- Sensitivity to Demand ---")
    for scale in demand_scales:
        rt = results[f"scale_{scale}x"]["response_time_mean"]["mean"]
        cov = results[f"scale_{scale}x"]["coverage_fraction"]["mean"]
        qf = results[f"scale_{scale}x"]["queue_fraction"]["mean"]
        n = results[f"scale_{scale}x"]["total_incidents"]["mean"]
        logger.info(f"  {scale}x: N={n:.0f}, RT={rt:.2f} min, Cov={cov:.3f}, QF={qf:.3f}")

    logger.info(f"  RT increases with demand: {data['response_time_increases_with_demand']}")

    save_pilot_result("pilot3_sensitivity_demand", data)
    return data


if __name__ == "__main__":
    pilot_results = {}

    pilot_results["p0_vs_p2"] = run_p0_vs_p2()
    pilot_results["sensitivity_K"] = run_sensitivity_K()
    pilot_results["sensitivity_demand"] = run_sensitivity_demand()

    logger.info("\n" + "=" * 60)
    logger.info("ALL VALIDATION PILOTS COMPLETE")
    logger.info("=" * 60)
