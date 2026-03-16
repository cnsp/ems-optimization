#!/usr/bin/env python3
"""Distance Metric Comparison Experiment.

Compares Haversine vs Manhattan (taxicab) distance metrics for EMS
optimization by running simulations with P2 allocations derived from
each metric and measuring response-time outcomes.

Experiment design:
    - Solve P2 (demand-weighted) using Haversine travel-time matrix
    - Solve P2 (demand-weighted) using Manhattan travel-time matrix
    - Run 30 replications of each allocation under both travel-time models
    - Compare mean response time, coverage, and P90

Output:
    results/distance_comparison/   (figures + tables)

Usage:
    python scripts/run_distance_comparison_experiment.py [--reps 10]
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from ems_readiness.optimization.models import build_demand_weighted, extract_allocation
from ems_readiness.service.travel_time import build_travel_time_matrix
from ems_readiness.simulation.runner import BatchRunner

# ── Config ───────────────────────────────────────────────────────────
OUTPUT_DIR = PROJECT_ROOT / "results" / "distance_comparison"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(OUTPUT_DIR / "experiment_log.txt", mode="w"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

K = 20
SPEED_MPH = 20.0
CBD_PRECINCTS = ["1", "5", "6", "7", "9", "10", "13", "14", "17", "18"]


def load_data():
    """Load distance matrices and demand."""
    dm_hav = pd.read_csv(PROCESSED_DIR / "distance_matrix_firehouse_precinct.csv", index_col=0)
    dm_hav.columns = dm_hav.columns.astype(str)

    dm_man = pd.read_csv(PROCESSED_DIR / "distance_matrix_firehouse_precinct_manhattan.csv", index_col=0)
    dm_man.columns = dm_man.columns.astype(str)

    demand_df = pd.read_csv(PROCESSED_DIR / "demand_lambda_precinct.csv")
    demand = demand_df.set_index("precinct")["crash_rate_per_hour"]
    demand.index = demand.index.astype(str)

    return dm_hav, dm_man, demand


def solve_p2(travel_time, demand, label="P2"):
    """Solve demand-weighted allocation."""
    import pulp
    prob = build_demand_weighted(travel_time, demand, K=K, capacity=5)
    prob.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=120))
    alloc = extract_allocation(prob)
    logger.info(f"  {label}: {int(alloc.sum())} units across {(alloc>0).sum()} firehouses")
    return alloc


def run_simulations(alloc, policy_name, num_reps, runner):
    """Run batch simulation and return aggregated results."""
    result = runner.run_scenario(
        policy_allocation=alloc,
        K=K,
        num_replications=num_reps,
        seed_base=42,
        policy_name=policy_name,
    )
    return result


def extract_metrics(result):
    """Extract key metrics from a batch result."""
    metrics = {}
    for key in ["response_time_mean", "response_time_median", "response_time_p90",
                 "coverage_fraction", "travel_time_mean", "incidents_queued",
                 "queue_fraction"]:
        if key in result and isinstance(result[key], dict):
            metrics[key] = result[key]["mean"]
        elif key in result:
            metrics[key] = result[key]
    return metrics


def create_comparison_table(results_dict):
    """Create comparison DataFrame."""
    rows = []
    for label, result in results_dict.items():
        m = extract_metrics(result)
        m["scenario"] = label
        rows.append(m)
    df = pd.DataFrame(rows).set_index("scenario")
    return df


def plot_comparison(comp_df):
    """Generate comparison figures."""
    sns.set_theme(style="whitegrid", font_scale=1.1)

    # 1. Bar chart of mean response times
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    metrics_to_plot = [
        ("response_time_mean", "Mean Response Time (min)"),
        ("response_time_p90", "P90 Response Time (90th percentile, min)"),
        ("coverage_fraction", "Coverage Fraction (≤8 min, NFPA)"),
    ]

    for ax, (metric, ylabel) in zip(axes, metrics_to_plot):
        vals = comp_df[metric]
        colors = ["#2196F3", "#FF5722"]
        bars = ax.bar(range(len(vals)), vals, color=colors[:len(vals)], width=0.6)
        ax.set_xticks(range(len(vals)))
        ax.set_xticklabels(vals.index, rotation=20, ha="right", fontsize=9)
        ax.set_ylabel(ylabel)
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f"{val:.2f}", ha="center", va="bottom", fontsize=9)

    fig.suptitle("Haversine vs Manhattan Distance: P2 Allocation Comparison (K=20)", fontsize=13)
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "distance_comparison_bar.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved: distance_comparison_bar.png")

    # 2. Per-replication response time distributions
    return fig


def plot_replication_distributions(results_dict):
    """Box plots of per-replication response times."""
    data = []
    for label, result in results_dict.items():
        for rep in result.get("per_replication", []):
            data.append({
                "scenario": label,
                "response_time_mean": rep.get("response_time_mean", np.nan),
                "response_time_p90": rep.get("response_time_p90", np.nan),
            })
    df = pd.DataFrame(data)
    if df.empty:
        return

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, metric, title in zip(axes,
                                  ["response_time_mean", "response_time_p90"],
                                  ["Mean Response Time", "P90 Response Time (90th pctl)"]):
        sns.boxplot(data=df, x="scenario", y=metric, ax=ax,
                    palette=["#2196F3", "#FF5722"])
        ax.set_title(title)
        ax.set_xlabel("")
        ax.set_ylabel("Minutes")

    fig.suptitle("Distribution Across Replications: Haversine vs Manhattan P2", fontsize=13)
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "distance_comparison_boxplot.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved: distance_comparison_boxplot.png")


def plot_distance_matrix_comparison(dm_hav, dm_man):
    """Side-by-side heatmaps of distance matrices."""
    fig, axes = plt.subplots(1, 2, figsize=(20, 10))

    for ax, dm, title in zip(axes, [dm_hav, dm_man],
                              ["Haversine Distance (miles)", "Manhattan Distance (miles)"]):
        sns.heatmap(dm, cmap="YlOrRd", ax=ax, cbar_kws={"label": "Miles"},
                    xticklabels=True, yticklabels=True)
        ax.set_title(title, fontsize=12)
        ax.set_xlabel("Precinct")
        ax.set_ylabel("Firehouse")
        ax.tick_params(axis='both', labelsize=6)

    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "distance_matrices_heatmap.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved: distance_matrices_heatmap.png")


def plot_scatter_comparison(dm_hav, dm_man):
    """Scatter plot of Haversine vs Manhattan distances."""
    common = sorted(set(dm_hav.columns) & set(dm_man.columns))
    h = dm_hav[common].values.flatten()
    m = dm_man[common].values.flatten()

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.scatter(h, m, alpha=0.3, s=10, color="#2196F3")
    max_val = max(h.max(), m.max()) * 1.05
    ax.plot([0, max_val], [0, max_val], "k--", alpha=0.5, label="y = x")
    # Fit line
    z = np.polyfit(h, m, 1)
    ax.plot([0, max_val], [z[1], z[1] + z[0]*max_val], "r-", alpha=0.7,
            label=f"y = {z[0]:.2f}x + {z[1]:.2f}")
    ax.set_xlabel("Haversine Distance (miles)")
    ax.set_ylabel("Manhattan Distance (miles)")
    ax.set_title("Haversine vs Manhattan Distance Comparison")
    ax.legend()
    ax.set_xlim(0, max_val)
    ax.set_ylim(0, max_val)
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "distance_scatter.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved: distance_scatter.png")


def main():
    parser = argparse.ArgumentParser(description="Distance metric comparison experiment")
    parser.add_argument("--reps", type=int, default=10, help="Replications per scenario")
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Distance Metric Comparison Experiment")
    logger.info(f"K={K}, replications={args.reps}")
    logger.info("=" * 60)

    t0 = time.time()

    # Load data
    dm_hav, dm_man, demand = load_data()

    # Generate distance comparison visualizations
    plot_distance_matrix_comparison(dm_hav, dm_man)
    plot_scatter_comparison(dm_hav, dm_man)

    # Build travel-time matrices
    tt_hav = build_travel_time_matrix(dm_hav, speed_mph=SPEED_MPH)
    tt_man = build_travel_time_matrix(dm_man, speed_mph=SPEED_MPH)

    # Solve P2 with each metric
    logger.info("\nSolving P2 with Haversine travel times...")
    alloc_hav = solve_p2(tt_hav, demand, "P2-Haversine")

    logger.info("Solving P2 with Manhattan travel times...")
    alloc_man = solve_p2(tt_man, demand, "P2-Manhattan")

    # Compare allocations
    alloc_comp = pd.DataFrame({
        "P2_Haversine": alloc_hav,
        "P2_Manhattan": alloc_man,
    }).fillna(0)
    alloc_comp["diff"] = alloc_comp["P2_Manhattan"] - alloc_comp["P2_Haversine"]
    alloc_comp.to_csv(OUTPUT_DIR / "allocation_comparison.csv")
    logger.info(f"Allocation differences: {(alloc_comp['diff'] != 0).sum()} firehouses differ")

    # Run simulations (using the standard Haversine-based simulation engine for both)
    runner = BatchRunner(project_root=str(PROJECT_ROOT))
    results = {}

    logger.info("\nRunning simulations with Haversine-optimized allocation...")
    results["P2-Haversine"] = run_simulations(alloc_hav, "P2-Haversine", args.reps, runner)

    logger.info("Running simulations with Manhattan-optimized allocation...")
    results["P2-Manhattan"] = run_simulations(alloc_man, "P2-Manhattan", args.reps, runner)

    # Create comparison table
    comp_df = create_comparison_table(results)
    comp_df.to_csv(OUTPUT_DIR / "comparison_table.csv")
    logger.info(f"\n--- Comparison Table ---\n{comp_df.to_string()}")

    # Generate figures
    plot_comparison(comp_df)
    plot_replication_distributions(results)

    elapsed = time.time() - t0
    logger.info(f"\nExperiment completed in {elapsed:.1f}s ({elapsed/60:.1f} min)")
    logger.info(f"Results saved to: {OUTPUT_DIR}")

    # Summary statistics
    logger.info("\n" + "=" * 60)
    logger.info("KEY FINDINGS")
    logger.info("=" * 60)
    for scenario in comp_df.index:
        rt = comp_df.loc[scenario, "response_time_mean"]
        cov = comp_df.loc[scenario, "coverage_fraction"]
        logger.info(f"  {scenario:20s}: RT={rt:.2f} min, Coverage={cov:.1%}")

    print("\nDone.")


if __name__ == "__main__":
    main()
