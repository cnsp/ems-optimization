#!/usr/bin/env python3
"""Production V2 experiment runner – capacity=2, spatially-stratified P0.

Re-runs the full production experiment suite with:
  - Capacity = 2 (proven optimal from sensitivity analysis)
  - New P0-spatial baseline (latitude-based stratification)
  - P1 demand-proportional (with capacity=2)
  - P2 optimized demand-weighted (with capacity=2)

K values: 10, 15, 20, 25, 30, 35, 40, 45, 48
30 replications per scenario, base seed = 42

Usage:
    python scripts/run_production_v2.py
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from scipy import stats

# ── Project setup ────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from ems_readiness.simulation.engine import EMSSimulation
from ems_readiness.optimization.allocator import EMSAllocator
from ems_readiness.optimization.policies import (
    spatially_stratified_allocation,
    demand_proportional_allocation,
)

# ── Output directories ──────────────────────────────────────────────
OUT_ROOT = PROJECT_ROOT / "results" / "production_v2"
ALLOC_DIR = OUT_ROOT / "allocations"
SIM_DIR = OUT_ROOT / "simulation"
TABLE_DIR = OUT_ROOT / "tables"
FIG_DIR = OUT_ROOT / "figures"
for d in [ALLOC_DIR, SIM_DIR, TABLE_DIR, FIG_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── Logging ──────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(OUT_ROOT / "experiment_log.txt", mode="a"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────
SEED_BASE = 42
HORIZON_HOURS = 168
CAPACITY = 2
K_VALUES = [10, 15, 20, 25, 30, 35, 40, 45, 48]
POLICIES = ["P0-spatial", "P1", "P2"]
NUM_REPLICATIONS = 30
RESPONSE_THRESHOLD = 8.0


# =====================================================================
#  STEP 1: Generate allocations
# =====================================================================

def generate_all_allocations(allocator: EMSAllocator) -> Dict[str, Dict[int, pd.Series]]:
    """Generate allocations for all policies and K values.

    Returns dict: policy -> {K -> allocation Series}
    """
    logger.info("=" * 60)
    logger.info("STEP 1: Generating allocations for all K values and policies")
    logger.info(f"  Capacity = {CAPACITY}")
    logger.info(f"  K values = {K_VALUES}")
    logger.info(f"  Policies = {POLICIES}")
    logger.info("=" * 60)

    allocations = {"P0-spatial": {}, "P1": {}, "P2": {}}

    for K in K_VALUES:
        logger.info(f"\n--- K = {K} ---")

        # P0-spatial: latitude-based stratified allocation
        alloc_p0 = spatially_stratified_allocation(
            K=K, method="latitude", capacity=CAPACITY,
            data_dir=str(PROJECT_ROOT / "data" / "processed"),
        )
        allocations["P0-spatial"][K] = alloc_p0
        n_active_p0 = (alloc_p0 > 0).sum()
        logger.info(f"  P0-spatial: {n_active_p0} active firehouses, {alloc_p0.sum()} units")

        # P1: demand-proportional allocation
        alloc_p1 = demand_proportional_allocation(
            travel_time=allocator.travel_time,
            demand=allocator.demand,
            K=K,
            capacity=CAPACITY,
        )
        allocations["P1"][K] = alloc_p1
        n_active_p1 = (alloc_p1 > 0).sum()
        logger.info(f"  P1: {n_active_p1} active firehouses, {alloc_p1.sum()} units")

        # P2: optimized demand-weighted allocation
        result_p2 = allocator.solve(
            model="demand_weighted", K=K, capacity=CAPACITY,
        )
        alloc_p2 = result_p2.allocation
        allocations["P2"][K] = alloc_p2
        n_active_p2 = (alloc_p2 > 0).sum()
        logger.info(f"  P2: {n_active_p2} active firehouses, {alloc_p2.sum()} units "
                     f"(obj={result_p2.objective_value:.4f}, status={result_p2.status})")

        # Save combined allocation CSV for this K
        alloc_df = pd.DataFrame({
            "P0-spatial": alloc_p0,
            "P1": alloc_p1,
            "P2": alloc_p2,
        })
        alloc_df.to_csv(ALLOC_DIR / f"allocations_K{K}.csv")

    logger.info(f"\nAll allocations saved to {ALLOC_DIR}")
    return allocations


# =====================================================================
#  STEP 2: Run simulations
# =====================================================================

def run_single_replication(
    allocation: pd.Series,
    seed: int,
    horizon_hours: float = HORIZON_HOURS,
) -> Dict[str, Any]:
    """Run one simulation replication and return summary metrics."""
    config = {
        "horizon_hours": horizon_hours,
        "warmup_hours": 0,
        "response_threshold_minutes": RESPONSE_THRESHOLD,
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
    sim.run(horizon_hours=horizon_hours)
    results = sim.get_results()
    summary = results["summary"]

    # Utilization metrics
    util_data = results["unit_utilizations"]
    if isinstance(util_data, dict) and "per_unit" in util_data:
        unit_utils = list(util_data["per_unit"].values())
    elif isinstance(util_data, dict):
        unit_utils = list(util_data.values())
    else:
        unit_utils = []
    mean_util = float(np.mean(unit_utils)) if unit_utils else 0.0
    max_util = float(np.max(unit_utils)) if unit_utils else 0.0

    # 10-min coverage from incident log
    log = results.get("incident_log")
    if log is not None and not log.empty and "response_time_minutes" in log.columns:
        coverage_10 = float((log["response_time_minutes"] <= 10.0).mean())
        p95_rt = float(log["response_time_minutes"].quantile(0.95))
    else:
        coverage_10 = summary.get("coverage_fraction", np.nan)
        p95_rt = summary.get("response_time_p90", np.nan)

    return {
        "mean_response_time": summary.get("response_time_mean", np.nan),
        "median_response_time": summary.get("response_time_median", np.nan),
        "p90_response_time": summary.get("response_time_p90", np.nan),
        "p95_response_time": p95_rt,
        "coverage_8min": summary.get("coverage_fraction", np.nan),
        "coverage_10min": coverage_10,
        "mean_utilization": mean_util,
        "max_utilization": max_util,
        "mean_queue_length": summary.get("queue_length_tw_avg", 0.0),
        "max_queue_length": summary.get("queue_length_max", 0),
        "queue_fraction": summary.get("queue_fraction", 0.0),
        "total_incidents": summary.get("total_incidents", 0),
        "incidents_queued": summary.get("incidents_queued", 0),
        "random_seed": seed,
    }


def run_full_simulation_suite(
    allocations: Dict[str, Dict[int, pd.Series]],
    num_reps: int = NUM_REPLICATIONS,
) -> pd.DataFrame:
    """Run all scenarios: 3 policies × 9 K values × 30 replications."""
    total_scenarios = len(POLICIES) * len(K_VALUES)
    total_runs = total_scenarios * num_reps
    logger.info("\n" + "=" * 60)
    logger.info("STEP 2: Running full production simulation suite")
    logger.info(f"  Policies: {POLICIES}")
    logger.info(f"  K values: {K_VALUES}")
    logger.info(f"  Replications: {num_reps}")
    logger.info(f"  Total scenarios: {total_scenarios}")
    logger.info(f"  Total simulation runs: {total_runs}")
    logger.info("=" * 60)

    rows = []
    run_count = 0
    errors = []
    t0 = time.time()

    for policy in POLICIES:
        for K in K_VALUES:
            allocation = allocations[policy][K]
            scenario_id = f"{policy}_K{K}"

            for rep in range(num_reps):
                seed = SEED_BASE + rep
                run_count += 1

                try:
                    row = run_single_replication(allocation, seed)
                    row.update({
                        "policy": policy,
                        "K": K,
                        "scenario_id": scenario_id,
                        "replication": rep,
                        "capacity": CAPACITY,
                    })
                    rows.append(row)
                except Exception as e:
                    err_msg = f"ERROR {scenario_id} rep={rep}: {e}"
                    logger.error(err_msg)
                    errors.append(err_msg)
                    traceback.print_exc()

                # Progress
                if run_count % 30 == 0 or run_count == total_runs:
                    elapsed = time.time() - t0
                    rate = run_count / elapsed if elapsed > 0 else 0
                    eta = (total_runs - run_count) / rate if rate > 0 else 0
                    logger.info(
                        f"  [{run_count}/{total_runs}] "
                        f"({100*run_count/total_runs:.0f}%) "
                        f"| {scenario_id} rep {rep} "
                        f"| Elapsed: {elapsed:.0f}s | ETA: {eta:.0f}s"
                    )

    elapsed = time.time() - t0
    logger.info(f"\nSimulation suite complete: {len(rows)} runs in {elapsed:.0f}s "
                f"({len(errors)} errors)")

    df = pd.DataFrame(rows)
    col_order = [
        "policy", "K", "scenario_id", "replication", "capacity",
        "mean_response_time", "median_response_time",
        "p90_response_time", "p95_response_time",
        "coverage_8min", "coverage_10min",
        "mean_utilization", "max_utilization",
        "mean_queue_length", "max_queue_length", "queue_fraction",
        "total_incidents", "incidents_queued", "random_seed",
    ]
    df = df[[c for c in col_order if c in df.columns]]

    # Save raw simulation results
    df.to_csv(SIM_DIR / "all_results_raw.csv", index=False)

    # Also save per-K files for convenience
    for K in K_VALUES:
        kdf = df[df["K"] == K]
        kdf.to_csv(SIM_DIR / f"results_K{K}.csv", index=False)

    logger.info(f"Raw results saved to {SIM_DIR}")
    return df


# =====================================================================
#  STEP 3: Statistical analysis
# =====================================================================

def perform_statistical_analysis(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """ANOVA, Tukey HSD, effect sizes across all K values."""
    logger.info("\n" + "=" * 60)
    logger.info("STEP 3: Statistical analysis")
    logger.info("=" * 60)

    tables = {}

    # --- 3a. Descriptive statistics ---
    desc_rows = []
    for K in K_VALUES:
        kdf = df[df["K"] == K]
        for policy in POLICIES:
            pdf = kdf[kdf["policy"] == policy]
            if pdf.empty:
                continue
            desc_rows.append({
                "K": K,
                "policy": policy,
                "n": len(pdf),
                "mean_RT": pdf["mean_response_time"].mean(),
                "std_RT": pdf["mean_response_time"].std(),
                "ci95_lower": pdf["mean_response_time"].mean() - 1.96 * pdf["mean_response_time"].std() / np.sqrt(len(pdf)),
                "ci95_upper": pdf["mean_response_time"].mean() + 1.96 * pdf["mean_response_time"].std() / np.sqrt(len(pdf)),
                "median_RT": pdf["median_response_time"].mean() if "median_response_time" in pdf.columns else np.nan,
                "p95_RT": pdf["p95_response_time"].mean(),
                "coverage_8min": pdf["coverage_8min"].mean(),
                "coverage_10min": pdf["coverage_10min"].mean(),
                "mean_util": pdf["mean_utilization"].mean(),
                "max_util": pdf["max_utilization"].mean(),
                "queue_fraction": pdf["queue_fraction"].mean(),
                "mean_queue_length": pdf["mean_queue_length"].mean(),
            })
    desc_df = pd.DataFrame(desc_rows)
    desc_df.to_csv(TABLE_DIR / "descriptive_statistics.csv", index=False)
    tables["descriptive"] = desc_df
    logger.info(f"  Descriptive statistics: {len(desc_df)} rows")

    # --- 3b. ANOVA at each K ---
    anova_rows = []
    for K in K_VALUES:
        kdf = df[df["K"] == K]
        groups = [kdf[kdf["policy"] == p]["mean_response_time"].dropna().values for p in POLICIES]
        groups = [g for g in groups if len(g) > 0]
        if len(groups) >= 2:
            f_stat, p_val = stats.f_oneway(*groups)
        else:
            f_stat, p_val = np.nan, np.nan
        anova_rows.append({
            "K": K,
            "F_statistic": f_stat,
            "p_value": p_val,
            "significant_005": p_val < 0.05 if not np.isnan(p_val) else False,
            "significant_001": p_val < 0.001 if not np.isnan(p_val) else False,
        })
    anova_df = pd.DataFrame(anova_rows)
    anova_df.to_csv(TABLE_DIR / "anova_results.csv", index=False)
    tables["anova"] = anova_df
    logger.info(f"  ANOVA results: {len(anova_df)} K values tested")

    # --- 3c. Pairwise Tukey HSD ---
    from scipy.stats import tukey_hsd as _tukey_stub
    posthoc_rows = []
    for K in K_VALUES:
        kdf = df[df["K"] == K]
        policy_data = {}
        for p in POLICIES:
            vals = kdf[kdf["policy"] == p]["mean_response_time"].dropna().values
            if len(vals) > 0:
                policy_data[p] = vals

        policy_names = list(policy_data.keys())
        if len(policy_names) < 2:
            continue

        # Tukey HSD
        try:
            result = stats.tukey_hsd(*[policy_data[p] for p in policy_names])
            for i in range(len(policy_names)):
                for j in range(i + 1, len(policy_names)):
                    p1, p2 = policy_names[i], policy_names[j]
                    diff = policy_data[p1].mean() - policy_data[p2].mean()
                    pval = result.pvalue[i][j]
                    posthoc_rows.append({
                        "K": K,
                        "comparison": f"{p1} vs {p2}",
                        "mean_diff": diff,
                        "p_value": pval,
                        "significant": pval < 0.05,
                    })
        except Exception as e:
            logger.warning(f"Tukey HSD failed at K={K}: {e}")
            # Fallback: pairwise t-tests with Bonferroni
            for i in range(len(policy_names)):
                for j in range(i + 1, len(policy_names)):
                    p1, p2 = policy_names[i], policy_names[j]
                    t_stat, pval = stats.ttest_ind(policy_data[p1], policy_data[p2])
                    pval_adj = min(pval * 3, 1.0)  # Bonferroni for 3 comparisons
                    diff = policy_data[p1].mean() - policy_data[p2].mean()
                    posthoc_rows.append({
                        "K": K,
                        "comparison": f"{p1} vs {p2}",
                        "mean_diff": diff,
                        "p_value": pval_adj,
                        "significant": pval_adj < 0.05,
                    })

    posthoc_df = pd.DataFrame(posthoc_rows)
    posthoc_df.to_csv(TABLE_DIR / "posthoc_comparisons.csv", index=False)
    tables["posthoc"] = posthoc_df
    logger.info(f"  Post-hoc comparisons: {len(posthoc_df)} pairs")

    # --- 3d. Effect sizes (Cohen's d) ---
    effect_rows = []
    for K in K_VALUES:
        kdf = df[df["K"] == K]
        policy_data = {}
        for p in POLICIES:
            vals = kdf[kdf["policy"] == p]["mean_response_time"].dropna().values
            if len(vals) > 0:
                policy_data[p] = vals

        policy_names = list(policy_data.keys())
        for i in range(len(policy_names)):
            for j in range(i + 1, len(policy_names)):
                p1, p2 = policy_names[i], policy_names[j]
                d1, d2 = policy_data[p1], policy_data[p2]
                pooled_std = np.sqrt(((len(d1)-1)*d1.std()**2 + (len(d2)-1)*d2.std()**2) /
                                     (len(d1) + len(d2) - 2))
                cohens_d = (d1.mean() - d2.mean()) / pooled_std if pooled_std > 0 else 0
                magnitude = (
                    "negligible" if abs(cohens_d) < 0.2 else
                    "small" if abs(cohens_d) < 0.5 else
                    "medium" if abs(cohens_d) < 0.8 else
                    "large"
                )
                effect_rows.append({
                    "K": K,
                    "comparison": f"{p1} vs {p2}",
                    "cohens_d": cohens_d,
                    "magnitude": magnitude,
                })

    effect_df = pd.DataFrame(effect_rows)
    effect_df.to_csv(TABLE_DIR / "effect_sizes.csv", index=False)
    tables["effect_sizes"] = effect_df
    logger.info(f"  Effect sizes: {len(effect_df)} pairs")

    # --- 3e. Confidence intervals ---
    ci_rows = []
    for K in K_VALUES:
        kdf = df[df["K"] == K]
        for policy in POLICIES:
            vals = kdf[kdf["policy"] == policy]["mean_response_time"].dropna()
            if len(vals) < 2:
                continue
            ci = stats.t.interval(0.95, len(vals)-1, loc=vals.mean(), scale=vals.std()/np.sqrt(len(vals)))
            ci_rows.append({
                "K": K,
                "policy": policy,
                "mean": vals.mean(),
                "ci_lower": ci[0],
                "ci_upper": ci[1],
                "margin_of_error": (ci[1] - ci[0]) / 2,
            })
    ci_df = pd.DataFrame(ci_rows)
    ci_df.to_csv(TABLE_DIR / "confidence_intervals.csv", index=False)
    tables["ci"] = ci_df

    # --- 3f. Queue statistics ---
    queue_rows = []
    for K in K_VALUES:
        kdf = df[df["K"] == K]
        for policy in POLICIES:
            pdf = kdf[kdf["policy"] == policy]
            if pdf.empty:
                continue
            queue_rows.append({
                "K": K,
                "policy": policy,
                "mean_queue_fraction": pdf["queue_fraction"].mean(),
                "mean_queue_length": pdf["mean_queue_length"].mean(),
                "max_queue_length": pdf["max_queue_length"].max(),
                "mean_incidents_queued": pdf["incidents_queued"].mean(),
            })
    queue_df = pd.DataFrame(queue_rows)
    queue_df.to_csv(TABLE_DIR / "queue_statistics.csv", index=False)
    tables["queue"] = queue_df

    logger.info(f"\nAll statistical tables saved to {TABLE_DIR}")
    return tables


# =====================================================================
#  STEP 4: Visualizations
# =====================================================================

def generate_visualizations(df: pd.DataFrame, tables: Dict[str, pd.DataFrame]):
    """Generate all production v2 figures."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
    plt.rcParams.update({"figure.dpi": 150, "savefig.dpi": 150,
                         "font.size": 10, "figure.figsize": (10, 6)})

    logger.info("\n" + "=" * 60)
    logger.info("STEP 4: Generating visualizations")
    logger.info("=" * 60)

    desc = tables["descriptive"]
    colors = {"P0-spatial": "#2196F3", "P1": "#FF9800", "P2": "#4CAF50"}

    # --- 4a. Mean Response Time vs K ---
    fig, ax = plt.subplots(figsize=(10, 6))
    for policy in POLICIES:
        pdf = desc[desc["policy"] == policy].sort_values("K")
        ax.errorbar(pdf["K"], pdf["mean_RT"],
                     yerr=1.96 * pdf["std_RT"] / np.sqrt(30),
                     marker="o", label=policy, color=colors[policy],
                     capsize=4, linewidth=2, markersize=6)
    ax.set_xlabel("Number of EMS Units (K)")
    ax.set_ylabel("Mean Response Time (minutes)")
    ax.set_title("Policy Comparison: Mean Response Time vs Fleet Size\n(Production V2 – Capacity=2, P0-spatial baseline)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xticks(K_VALUES)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "mean_rt_vs_K.png")
    plt.close()
    logger.info("  Saved mean_rt_vs_K.png")

    # --- 4b. Coverage vs K ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    for policy in POLICIES:
        pdf = desc[desc["policy"] == policy].sort_values("K")
        ax1.plot(pdf["K"], pdf["coverage_8min"], marker="o",
                 label=policy, color=colors[policy], linewidth=2, markersize=6)
        ax2.plot(pdf["K"], pdf["coverage_10min"], marker="s",
                 label=policy, color=colors[policy], linewidth=2, markersize=6)
    ax1.set_title("8-Minute Coverage vs K")
    ax1.set_xlabel("K"); ax1.set_ylabel("Coverage Fraction")
    ax1.legend(); ax1.grid(True, alpha=0.3); ax1.set_xticks(K_VALUES)
    ax1.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    ax2.set_title("10-Minute Coverage vs K")
    ax2.set_xlabel("K"); ax2.set_ylabel("Coverage Fraction")
    ax2.legend(); ax2.grid(True, alpha=0.3); ax2.set_xticks(K_VALUES)
    ax2.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    fig.suptitle("Coverage vs Fleet Size (Production V2)", fontsize=13, y=1.02)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "coverage_vs_K.png", bbox_inches="tight")
    plt.close()
    logger.info("  Saved coverage_vs_K.png")

    # --- 4c. P95 Response Time vs K ---
    fig, ax = plt.subplots(figsize=(10, 6))
    for policy in POLICIES:
        pdf = desc[desc["policy"] == policy].sort_values("K")
        ax.plot(pdf["K"], pdf["p95_RT"], marker="^",
                label=policy, color=colors[policy], linewidth=2, markersize=6)
    ax.set_xlabel("K"); ax.set_ylabel("95th Percentile Response Time (min)")
    ax.set_title("95th Percentile Response Time vs Fleet Size")
    ax.legend(); ax.grid(True, alpha=0.3); ax.set_xticks(K_VALUES)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "p95_rt_vs_K.png")
    plt.close()
    logger.info("  Saved p95_rt_vs_K.png")

    # --- 4d. Response time distributions for select K values ---
    for K in [20, 30, 40]:
        kdf = df[df["K"] == K]
        fig, ax = plt.subplots(figsize=(10, 5))
        data_for_box = []
        labels_for_box = []
        for policy in POLICIES:
            vals = kdf[kdf["policy"] == policy]["mean_response_time"].dropna()
            if len(vals) > 0:
                data_for_box.append(vals.values)
                labels_for_box.append(policy)
        bp = ax.boxplot(data_for_box, labels=labels_for_box, patch_artist=True)
        for patch, policy in zip(bp["boxes"], labels_for_box):
            patch.set_facecolor(colors.get(policy, "#999"))
            patch.set_alpha(0.6)
        ax.set_ylabel("Mean Response Time (minutes)")
        ax.set_title(f"Response Time Distribution at K={K} (30 replications)")
        ax.grid(True, alpha=0.3, axis="y")
        fig.tight_layout()
        fig.savefig(FIG_DIR / f"rt_distribution_K{K}.png")
        plt.close()
    logger.info("  Saved rt_distribution_K{20,30,40}.png")

    # --- 4e. Queue metrics vs K ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    for policy in POLICIES:
        qdf = tables["queue"]
        pdf = qdf[qdf["policy"] == policy].sort_values("K")
        ax1.plot(pdf["K"], pdf["mean_queue_fraction"], marker="o",
                 label=policy, color=colors[policy], linewidth=2)
        ax2.plot(pdf["K"], pdf["mean_queue_length"], marker="s",
                 label=policy, color=colors[policy], linewidth=2)
    ax1.set_title("Queue Fraction vs K")
    ax1.set_xlabel("K"); ax1.set_ylabel("Fraction of Incidents Queued")
    ax1.legend(); ax1.grid(True, alpha=0.3); ax1.set_xticks(K_VALUES)
    ax2.set_title("Mean Queue Length vs K")
    ax2.set_xlabel("K"); ax2.set_ylabel("Mean Queue Length")
    ax2.legend(); ax2.grid(True, alpha=0.3); ax2.set_xticks(K_VALUES)
    fig.suptitle("Queue Metrics (Production V2)", fontsize=13, y=1.02)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "queue_metrics_vs_K.png", bbox_inches="tight")
    plt.close()
    logger.info("  Saved queue_metrics_vs_K.png")

    # --- 4f. Utilization vs K ---
    fig, ax = plt.subplots(figsize=(10, 6))
    for policy in POLICIES:
        pdf = desc[desc["policy"] == policy].sort_values("K")
        ax.plot(pdf["K"], pdf["mean_util"], marker="o",
                label=f"{policy} (mean)", color=colors[policy], linewidth=2)
        ax.plot(pdf["K"], pdf["max_util"], marker="^",
                label=f"{policy} (max)", color=colors[policy],
                linewidth=1.5, linestyle="--", alpha=0.7)
    ax.set_xlabel("K"); ax.set_ylabel("Utilization")
    ax.set_title("Unit Utilization vs Fleet Size")
    ax.legend(ncol=2); ax.grid(True, alpha=0.3); ax.set_xticks(K_VALUES)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "utilization_vs_K.png")
    plt.close()
    logger.info("  Saved utilization_vs_K.png")

    # --- 4g. Allocation maps for K = 20, 30, 40 ---
    _generate_allocation_maps()

    # --- 4h. Effect size heatmap ---
    effect = tables["effect_sizes"]
    if not effect.empty:
        fig, ax = plt.subplots(figsize=(12, 6))
        comparisons = effect["comparison"].unique()
        for ci, comp in enumerate(comparisons):
            edf = effect[effect["comparison"] == comp].sort_values("K")
            ax.bar([k + ci*0.25 - 0.25 for k in edf["K"]], edf["cohens_d"].abs(),
                   width=0.25, label=comp, alpha=0.8)
        ax.axhline(0.2, color="gray", linestyle=":", alpha=0.5, label="Small effect (0.2)")
        ax.axhline(0.5, color="gray", linestyle="--", alpha=0.5, label="Medium effect (0.5)")
        ax.axhline(0.8, color="gray", linestyle="-", alpha=0.5, label="Large effect (0.8)")
        ax.set_xlabel("K"); ax.set_ylabel("|Cohen's d|")
        ax.set_title("Effect Sizes: Pairwise Policy Comparisons")
        ax.legend(fontsize=8); ax.grid(True, alpha=0.3, axis="y")
        ax.set_xticks(K_VALUES)
        fig.tight_layout()
        fig.savefig(FIG_DIR / "effect_sizes.png")
        plt.close()
        logger.info("  Saved effect_sizes.png")

    logger.info(f"\nAll figures saved to {FIG_DIR}")


def _generate_allocation_maps():
    """Generate allocation maps for K = 20, 30, 40."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    try:
        fh_df = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "firehouses_manhattan.csv")
    except Exception:
        logger.warning("Could not load firehouses for map generation")
        return

    for K in [20, 30, 40]:
        alloc_path = ALLOC_DIR / f"allocations_K{K}.csv"
        if not alloc_path.exists():
            continue
        alloc_df = pd.read_csv(alloc_path, index_col=0)

        fig, axes = plt.subplots(1, 3, figsize=(18, 8))
        for ax, policy in zip(axes, POLICIES):
            col = policy
            if col not in alloc_df.columns:
                continue
            merged = fh_df.set_index("FacilityName").join(alloc_df[[col]])
            merged = merged.dropna(subset=[col])

            # Plot all firehouses as small gray dots
            ax.scatter(fh_df["Longitude"], fh_df["Latitude"],
                       c="lightgray", s=15, zorder=1, alpha=0.5)
            # Plot active firehouses colored by unit count
            active = merged[merged[col] > 0]
            sc = ax.scatter(active["Longitude"], active["Latitude"],
                            c=active[col], cmap="YlOrRd", s=60 + active[col]*40,
                            edgecolors="black", linewidth=0.5, zorder=2,
                            vmin=0, vmax=max(CAPACITY, active[col].max()))
            ax.set_title(f"{policy} (K={K})", fontsize=12)
            ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude")
            plt.colorbar(sc, ax=ax, label="Units", shrink=0.7)

        fig.suptitle(f"Allocation Maps – K={K}, Capacity={CAPACITY}", fontsize=14)
        fig.tight_layout()
        fig.savefig(FIG_DIR / f"allocation_map_K{K}.png", bbox_inches="tight")
        plt.close()

    logger.info("  Saved allocation_map_K{20,30,40}.png")


# =====================================================================
#  STEP 5: Comparison with original results (V1)
# =====================================================================

def create_v1_comparison(df_v2: pd.DataFrame):
    """Compare V2 results with original V1 production results."""
    logger.info("\n" + "=" * 60)
    logger.info("STEP 5: Comparison with V1 (original production results)")
    logger.info("=" * 60)

    v1_path = PROJECT_ROOT / "results" / "simulation" / "production" / "exp2_fleet_sensitivity.csv"
    if not v1_path.exists():
        logger.warning(f"V1 results not found at {v1_path}; skipping comparison")
        return

    df_v1 = pd.read_csv(v1_path)

    # Aggregate V1 by policy and K
    v1_agg = df_v1.groupby(["policy", "K"]).agg(
        v1_mean_RT=("mean_response_time", "mean"),
        v1_std_RT=("mean_response_time", "std"),
        v1_coverage_8min=("coverage_8min", "mean"),
        v1_queue_fraction=("queue_fraction", "mean"),
        v1_mean_util=("mean_utilization", "mean"),
    ).reset_index()

    # Map V1 policy names: P0 -> P0-index, P1 -> P1-v1, P2 -> P2-v1
    v1_agg["policy_v1"] = v1_agg["policy"]

    # Aggregate V2
    v2_agg = df_v2.groupby(["policy", "K"]).agg(
        v2_mean_RT=("mean_response_time", "mean"),
        v2_std_RT=("mean_response_time", "std"),
        v2_coverage_8min=("coverage_8min", "mean"),
        v2_queue_fraction=("queue_fraction", "mean"),
        v2_mean_util=("mean_utilization", "mean"),
    ).reset_index()
    v2_agg["policy_v2"] = v2_agg["policy"]

    # Build comparison: match V1-P0 with V2-P0-spatial, V1-P1 with V2-P1, V1-P2 with V2-P2
    policy_map = {"P0": "P0-spatial", "P1": "P1", "P2": "P2"}
    rows = []
    for _, v1_row in v1_agg.iterrows():
        v2_policy = policy_map.get(v1_row["policy"])
        if v2_policy is None:
            continue
        v2_match = v2_agg[(v2_agg["policy"] == v2_policy) & (v2_agg["K"] == v1_row["K"])]
        if v2_match.empty:
            continue
        v2_row = v2_match.iloc[0]
        rows.append({
            "K": v1_row["K"],
            "v1_policy": v1_row["policy"],
            "v2_policy": v2_policy,
            "v1_config": "cap=5, P0-index",
            "v2_config": "cap=2, P0-spatial",
            "v1_mean_RT": v1_row["v1_mean_RT"],
            "v2_mean_RT": v2_row["v2_mean_RT"],
            "RT_change": v2_row["v2_mean_RT"] - v1_row["v1_mean_RT"],
            "RT_change_pct": 100 * (v2_row["v2_mean_RT"] - v1_row["v1_mean_RT"]) / v1_row["v1_mean_RT"],
            "v1_coverage_8min": v1_row["v1_coverage_8min"],
            "v2_coverage_8min": v2_row["v2_coverage_8min"],
            "coverage_change": v2_row["v2_coverage_8min"] - v1_row["v1_coverage_8min"],
            "v1_queue_fraction": v1_row["v1_queue_fraction"],
            "v2_queue_fraction": v2_row["v2_queue_fraction"],
            "v1_mean_util": v1_row["v1_mean_util"],
            "v2_mean_util": v2_row["v2_mean_util"],
        })

    comp_df = pd.DataFrame(rows)
    comp_df.to_csv(OUT_ROOT / "comparison_with_v1.csv", index=False)
    logger.info(f"  V1 vs V2 comparison: {len(comp_df)} rows")
    logger.info(f"  Saved to {OUT_ROOT / 'comparison_with_v1.csv'}")

    # Print summary
    logger.info("\n  V1 vs V2 Summary:")
    for policy_v1, policy_v2 in policy_map.items():
        pcomp = comp_df[comp_df["v1_policy"] == policy_v1]
        if pcomp.empty:
            continue
        logger.info(f"    {policy_v1}→{policy_v2}:")
        logger.info(f"      Avg RT change: {pcomp['RT_change'].mean():+.3f} min "
                     f"({pcomp['RT_change_pct'].mean():+.1f}%)")
        logger.info(f"      Avg coverage change: {pcomp['coverage_change'].mean():+.4f}")

    return comp_df


# =====================================================================
#  STEP 6: Experiment log
# =====================================================================

def write_experiment_log(df: pd.DataFrame):
    """Write comprehensive experiment log."""
    log_path = OUT_ROOT / "experiment_log.txt"
    with open(log_path, "a") as f:
        f.write("\n" + "=" * 70 + "\n")
        f.write(f"PRODUCTION V2 EXPERIMENT LOG\n")
        f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 70 + "\n\n")

        f.write("CONFIGURATION:\n")
        f.write(f"  Firehouse capacity: {CAPACITY}\n")
        f.write(f"  P0 baseline: spatially-stratified (latitude method)\n")
        f.write(f"  P1: demand-proportional with cap={CAPACITY}\n")
        f.write(f"  P2: optimized demand-weighted with cap={CAPACITY}\n")
        f.write(f"  Horizon: {HORIZON_HOURS} hours (1 week)\n")
        f.write(f"  Response threshold: {RESPONSE_THRESHOLD} minutes\n")
        f.write(f"  Base seed: {SEED_BASE}\n")
        f.write(f"  Replications per scenario: {NUM_REPLICATIONS}\n")
        f.write(f"  K values: {K_VALUES}\n")
        f.write(f"  Policies: {POLICIES}\n\n")

        f.write("SEED VALUES:\n")
        for rep in range(NUM_REPLICATIONS):
            f.write(f"  Replication {rep}: seed = {SEED_BASE + rep}\n")

        total_scenarios = len(POLICIES) * len(K_VALUES)
        total_runs = total_scenarios * NUM_REPLICATIONS
        f.write(f"\nTOTAL SCENARIOS: {total_scenarios}\n")
        f.write(f"TOTAL SIMULATION RUNS: {total_runs}\n")
        f.write(f"COMPLETED RUNS: {len(df)}\n")
        f.write(f"ERRORS: {total_runs - len(df)}\n\n")

        f.write("OUTPUT FILES:\n")
        f.write(f"  Allocations: {ALLOC_DIR}\n")
        f.write(f"  Raw simulation results: {SIM_DIR}\n")
        f.write(f"  Statistical tables: {TABLE_DIR}\n")
        f.write(f"  Figures: {FIG_DIR}\n")
        f.write(f"  V1 comparison: {OUT_ROOT / 'comparison_with_v1.csv'}\n\n")

        f.write("SCENARIO SUMMARY:\n")
        for K in K_VALUES:
            for policy in POLICIES:
                kpdf = df[(df["K"] == K) & (df["policy"] == policy)]
                if not kpdf.empty:
                    f.write(f"  {policy}_K{K}: {len(kpdf)} reps, "
                            f"mean_RT={kpdf['mean_response_time'].mean():.3f} ± "
                            f"{kpdf['mean_response_time'].std():.3f} min, "
                            f"cov8={kpdf['coverage_8min'].mean():.4f}\n")

    logger.info(f"Experiment log written to {log_path}")


# =====================================================================
#  MAIN
# =====================================================================

def main():
    parser = argparse.ArgumentParser(description="Run Production V2 experiments")
    parser.add_argument("--reps", type=int, default=NUM_REPLICATIONS,
                        help=f"Replications per scenario (default: {NUM_REPLICATIONS})")
    parser.add_argument("--skip-sim", action="store_true",
                        help="Skip simulation, load existing results for analysis")
    args = parser.parse_args()

    logger.info("#" * 70)
    logger.info(f"EMS Production V2 Experiments – {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"  Capacity: {CAPACITY}")
    logger.info(f"  K values: {K_VALUES}")
    logger.info(f"  Policies: {POLICIES}")
    logger.info(f"  Replications: {args.reps}")
    logger.info("#" * 70)

    t_start = time.time()

    # Step 1: Load allocator and generate allocations
    logger.info("\nLoading EMSAllocator...")
    allocator = EMSAllocator.from_project(str(PROJECT_ROOT))

    allocations = generate_all_allocations(allocator)

    if args.skip_sim:
        raw_path = SIM_DIR / "all_results_raw.csv"
        if raw_path.exists():
            logger.info(f"\nLoading existing results from {raw_path}")
            df = pd.read_csv(raw_path)
        else:
            logger.error(f"No existing results found at {raw_path}")
            sys.exit(1)
    else:
        # Step 2: Run full simulation suite
        df = run_full_simulation_suite(allocations, num_reps=args.reps)

    # Step 3: Statistical analysis
    tables = perform_statistical_analysis(df)

    # Step 4: Visualizations
    generate_visualizations(df, tables)

    # Step 5: V1 comparison
    create_v1_comparison(df)

    # Step 6: Experiment log
    write_experiment_log(df)

    total_time = time.time() - t_start
    logger.info("\n" + "#" * 70)
    logger.info(f"PRODUCTION V2 COMPLETE")
    logger.info(f"  Total runs: {len(df)}")
    logger.info(f"  Total time: {total_time:.0f}s ({total_time/60:.1f} min)")
    logger.info("#" * 70)


if __name__ == "__main__":
    main()
