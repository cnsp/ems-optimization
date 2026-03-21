#!/usr/bin/env python3
"""CBD-Focused vs Manhattan-Wide Optimization Comparison.

Compares two optimization strategies:
  1. Manhattan-wide P2: minimises response time across ALL precincts (current)
  2. CBD-focused P2: minimises response time for CBD precincts ONLY

For each allocation, simulations are run and results are disaggregated into:
  - CBD precincts response time
  - Non-CBD precincts response time
  - Overall response time

This reveals the equity vs efficiency tradeoff.

Output:
    results/analysis/cbd_focused_comparison/

Usage:
    python scripts/run_cbd_focused_optimization.py [--reps 10]
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
import pulp

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from ems_readiness.optimization.models import (
    build_demand_weighted,
    build_cbd_focused_demand_weighted,
    extract_allocation,
    extract_assignments,
)
from ems_readiness.service.travel_time import build_travel_time_matrix
from ems_readiness.simulation.engine import EMSSimulation

# ── Config ───────────────────────────────────────────────────────────
OUTPUT_DIR = PROJECT_ROOT / "results" / "cbd_focused_comparison"
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
CBD_SET = set(CBD_PRECINCTS)


def load_data():
    """Load distance matrix and demand."""
    dm = pd.read_csv(PROCESSED_DIR / "distance_matrix_firehouse_precinct.csv", index_col=0)
    dm.columns = dm.columns.astype(str)

    demand_df = pd.read_csv(PROCESSED_DIR / "demand_lambda_precinct.csv")
    demand = demand_df.set_index("precinct")["crash_rate_per_hour"]
    demand.index = demand.index.astype(str)

    return dm, demand


def solve_allocations(tt, demand):
    """Solve Manhattan-wide and CBD-focused P2."""
    # Manhattan-wide P2
    logger.info("Solving Manhattan-wide P2 (demand_weighted)...")
    prob_mw = build_demand_weighted(tt, demand, K=K, capacity=5)
    prob_mw.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=120))
    alloc_mw = extract_allocation(prob_mw)
    logger.info(f"  Manhattan-wide: {int(alloc_mw.sum())} units, {(alloc_mw>0).sum()} firehouses")

    # CBD-focused P2
    logger.info("Solving CBD-focused P2...")
    prob_cbd = build_cbd_focused_demand_weighted(tt, demand, K=K, cbd_precincts=CBD_PRECINCTS, capacity=5)
    prob_cbd.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=120))
    alloc_cbd = extract_allocation(prob_cbd)
    logger.info(f"  CBD-focused: {int(alloc_cbd.sum())} units, {(alloc_cbd>0).sum()} firehouses")

    return alloc_mw, alloc_cbd


def run_simulation_with_logging(alloc, policy_name, seed, trace=True):
    """Run single simulation and return incident log."""
    sim = EMSSimulation(
        policy_allocation=alloc,
        seed=seed,
        data_dir=str(PROCESSED_DIR),
        project_root=str(PROJECT_ROOT),
        trace=trace,
    )
    sim.run()
    return sim.get_results()


def disaggregate_results(results_list, policy_name):
    """Compute CBD vs non-CBD response times from incident logs."""
    cbd_rts = []
    non_cbd_rts = []
    overall_rts = []
    coverages_cbd = []
    coverages_noncbd = []
    coverages_cbd_6 = []
    coverages_noncbd_6 = []

    for result in results_list:
        summary = result["summary"]
        incident_log = result.get("incident_log", pd.DataFrame())

        overall_rts.append(summary.get("response_time_mean", np.nan))

        if not incident_log.empty and "precinct" in incident_log.columns:
            incident_log["precinct_str"] = incident_log["precinct"].astype(str)
            cbd_mask = incident_log["precinct_str"].isin(CBD_SET)

            cbd_incidents = incident_log[cbd_mask]
            non_cbd_incidents = incident_log[~cbd_mask]

            if len(cbd_incidents) > 0 and "response_time_minutes" in cbd_incidents.columns:
                cbd_rt = cbd_incidents["response_time_minutes"].dropna()
                cbd_rts.append(cbd_rt.mean())
                coverages_cbd.append((cbd_rt <= 8.0).mean())
                coverages_cbd_6.append((cbd_rt <= 6.0).mean())
            else:
                cbd_rts.append(np.nan)
                coverages_cbd.append(np.nan)
                coverages_cbd_6.append(np.nan)

            if len(non_cbd_incidents) > 0 and "response_time_minutes" in non_cbd_incidents.columns:
                non_cbd_rt = non_cbd_incidents["response_time_minutes"].dropna()
                non_cbd_rts.append(non_cbd_rt.mean())
                coverages_noncbd.append((non_cbd_rt <= 8.0).mean())
                coverages_noncbd_6.append((non_cbd_rt <= 6.0).mean())
            else:
                non_cbd_rts.append(np.nan)
                coverages_noncbd.append(np.nan)
                coverages_noncbd_6.append(np.nan)
        else:
            cbd_rts.append(np.nan)
            non_cbd_rts.append(np.nan)
            coverages_cbd.append(np.nan)
            coverages_noncbd.append(np.nan)
            coverages_cbd_6.append(np.nan)
            coverages_noncbd_6.append(np.nan)

    return {
        "policy": policy_name,
        "overall_rt_mean": np.nanmean(overall_rts),
        "cbd_rt_mean": np.nanmean(cbd_rts),
        "non_cbd_rt_mean": np.nanmean(non_cbd_rts),
        "cbd_coverage_8min": np.nanmean(coverages_cbd),
        "non_cbd_coverage_8min": np.nanmean(coverages_noncbd),
        "cbd_coverage_6min": np.nanmean(coverages_cbd_6),
        "non_cbd_coverage_6min": np.nanmean(coverages_noncbd_6),
        "overall_rt_std": np.nanstd(overall_rts),
        "cbd_rt_std": np.nanstd(cbd_rts),
        "non_cbd_rt_std": np.nanstd(non_cbd_rts),
    }


def plot_comparison(comp_df):
    """Create comparison visualisation."""
    sns.set_theme(style="whitegrid", font_scale=1.1)

    # Grouped bar chart of RT by region
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # 1. Response time comparison
    ax = axes[0]
    x = np.arange(len(comp_df))
    width = 0.25
    ax.bar(x - width, comp_df["cbd_rt_mean"], width, label="CBD RT", color="#D32F2F")
    ax.bar(x, comp_df["non_cbd_rt_mean"], width, label="Non-CBD RT", color="#1976D2")
    ax.bar(x + width, comp_df["overall_rt_mean"], width, label="Overall RT", color="#388E3C")
    ax.set_xticks(x)
    ax.set_xticklabels(comp_df["policy"], rotation=15, ha="right")
    ax.set_ylabel("Mean Response Time (min)")
    ax.set_title("Response Time by Region")
    ax.legend()

    # Add value labels
    for offset, col in zip([-width, 0, width],
                            ["cbd_rt_mean", "non_cbd_rt_mean", "overall_rt_mean"]):
        for i, val in enumerate(comp_df[col]):
            ax.text(i + offset, val + 0.02, f"{val:.2f}", ha="center", va="bottom", fontsize=8)

    # 2. Coverage comparison
    ax = axes[1]
    ax.bar(x - width/2, comp_df["cbd_coverage_8min"] * 100, width, label="CBD Coverage", color="#D32F2F")
    ax.bar(x + width/2, comp_df["non_cbd_coverage_8min"] * 100, width, label="Non-CBD Coverage", color="#1976D2")
    ax.set_xticks(x)
    ax.set_xticklabels(comp_df["policy"], rotation=15, ha="right")
    ax.set_ylabel("Coverage ≤ 8 min (%)")
    ax.set_title("Coverage by Region")
    ax.legend()

    fig.suptitle(f"Manhattan-Wide vs CBD-Focused Optimization (K={K})", fontsize=14)
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "cbd_focused_comparison.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved: cbd_focused_comparison.png")

    # 3. Allocation heatmap comparison
    return fig


def plot_allocation_comparison(alloc_mw, alloc_cbd, fh_df):
    """Compare where units are placed."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 8))

    for ax, alloc, title in zip(axes,
                                 [alloc_mw, alloc_cbd],
                                 ["Manhattan-Wide P2", "CBD-Focused P2"]):
        active = alloc[alloc > 0].sort_values(ascending=True)
        colors = []
        for fh in active.index:
            row = fh_df[fh_df["FacilityName"] == fh]
            if not row.empty and str(row.iloc[0].get("in_cbd", "")).lower() == "true":
                colors.append("#D32F2F")
            else:
                colors.append("#1976D2")
        ax.barh(range(len(active)), active.values, color=colors)
        ax.set_yticks(range(len(active)))
        ax.set_yticklabels(active.index, fontsize=7)
        ax.set_xlabel("Units Allocated")
        ax.set_title(title)

    # Custom legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor="#D32F2F", label="CBD Firehouse"),
                       Patch(facecolor="#1976D2", label="Non-CBD Firehouse")]
    axes[0].legend(handles=legend_elements, loc="lower right")

    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "allocation_comparison.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved: allocation_comparison.png")


def plot_equity_tradeoff(comp_df):
    """Scatter plot showing equity tradeoff."""
    fig, ax = plt.subplots(figsize=(8, 6))
    for _, row in comp_df.iterrows():
        ax.scatter(row["cbd_rt_mean"], row["non_cbd_rt_mean"], s=200, zorder=5)
        ax.annotate(row["policy"], (row["cbd_rt_mean"], row["non_cbd_rt_mean"]),
                    textcoords="offset points", xytext=(10, 5), fontsize=10)

    ax.set_xlabel("CBD Mean Response Time (min)")
    ax.set_ylabel("Non-CBD Mean Response Time (min)")
    ax.set_title("Equity–Efficiency Tradeoff: CBD vs Non-CBD Response Time")

    # Add reference lines
    ax.axhline(y=comp_df["non_cbd_rt_mean"].mean(), color="gray", linestyle="--", alpha=0.5)
    ax.axvline(x=comp_df["cbd_rt_mean"].mean(), color="gray", linestyle="--", alpha=0.5)

    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "equity_tradeoff.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved: equity_tradeoff.png")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reps", type=int, default=10, help="Replications per scenario")
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("CBD-Focused vs Manhattan-Wide Optimization Experiment")
    logger.info(f"K={K}, replications={args.reps}")
    logger.info("=" * 60)

    t0 = time.time()

    dm, demand = load_data()
    tt = build_travel_time_matrix(dm, speed_mph=SPEED_MPH)

    # Solve
    alloc_mw, alloc_cbd = solve_allocations(tt, demand)

    # Save allocations
    alloc_comp = pd.DataFrame({"Manhattan_Wide_P2": alloc_mw, "CBD_Focused_P2": alloc_cbd}).fillna(0)
    alloc_comp.to_csv(OUTPUT_DIR / "allocations.csv")

    # Run simulations with trace to get incident-level data
    scenarios = {
        "Manhattan-Wide P2": alloc_mw,
        "CBD-Focused P2": alloc_cbd,
    }

    all_results = {}
    # Suppress trace logging during simulation
    logging.getLogger("ems_readiness").setLevel(logging.WARNING)

    for label, alloc in scenarios.items():
        logger.info(f"\nRunning {label} simulations ({args.reps} reps)...")
        rep_results = []
        for rep in range(args.reps):
            seed = 42 + rep
            result = run_simulation_with_logging(alloc, label, seed, trace=True)
            rep_results.append(result)
        all_results[label] = rep_results

    logging.getLogger("ems_readiness").setLevel(logging.INFO)

    # Disaggregate results
    disagg_rows = []
    for label, rep_results in all_results.items():
        row = disaggregate_results(rep_results, label)
        disagg_rows.append(row)
        logger.info(f"\n{label}:")
        logger.info(f"  Overall RT: {row['overall_rt_mean']:.2f} ± {row['overall_rt_std']:.2f} min")
        logger.info(f"  CBD RT:     {row['cbd_rt_mean']:.2f} ± {row['cbd_rt_std']:.2f} min")
        logger.info(f"  Non-CBD RT: {row['non_cbd_rt_mean']:.2f} ± {row['non_cbd_rt_std']:.2f} min")
        logger.info(f"  CBD Coverage (8min): {row['cbd_coverage_8min']:.1%}")
        logger.info(f"  Non-CBD Coverage (8min): {row['non_cbd_coverage_8min']:.1%}")
        logger.info(f"  CBD Coverage (6min): {row['cbd_coverage_6min']:.1%}")
        logger.info(f"  Non-CBD Coverage (6min): {row['non_cbd_coverage_6min']:.1%}")

    comp_df = pd.DataFrame(disagg_rows)
    comp_df.to_csv(OUTPUT_DIR / "comparison_table.csv", index=False)
    logger.info(f"\nSaved comparison table to {OUTPUT_DIR / 'comparison_table.csv'}")

    # Visualise
    fh_df = pd.read_csv(PROCESSED_DIR / "firehouses_manhattan.csv")
    plot_comparison(comp_df)
    plot_allocation_comparison(alloc_mw, alloc_cbd, fh_df)
    plot_equity_tradeoff(comp_df)

    elapsed = time.time() - t0
    logger.info(f"\nExperiment completed in {elapsed:.1f}s ({elapsed/60:.1f} min)")
    logger.info(f"Results saved to: {OUTPUT_DIR}")

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("KEY FINDINGS")
    logger.info("=" * 60)
    for _, row in comp_df.iterrows():
        logger.info(f"  {row['policy']:25s}: CBD={row['cbd_rt_mean']:.2f}, "
                     f"Non-CBD={row['non_cbd_rt_mean']:.2f}, "
                     f"Overall={row['overall_rt_mean']:.2f} min")

    print("\nDone.")


if __name__ == "__main__":
    main()