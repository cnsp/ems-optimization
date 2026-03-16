#!/usr/bin/env python3
"""Capacity Sensitivity Analysis: Compare capacity=2 vs capacity=5 at K=20.

This script runs a full comparative analysis of EMS unit allocation
under two capacity constraints (realistic cap=2 vs. unrealistic cap=5)
across all three policy families:
  - P0 (spatially-stratified baseline, maximin method)
  - P1 (demand-proportional)
  - P2 (demand-weighted optimisation)

For each (capacity, policy) combination it:
  1. Generates the allocation vector
  2. Runs simulation experiments (multiple replications)
  3. Collects performance metrics (mean RT, p95 RT, coverage, etc.)
  4. Saves allocation files and comparison artefacts

Outputs go to  results/capacity_comparison/
"""

from __future__ import annotations

import json
import logging
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
import pulp
import yaml

# ── Project path setup ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from ems_readiness.optimization import models, policies
from ems_readiness.optimization.allocator import EMSAllocator
from ems_readiness.service.travel_time import build_travel_time_matrix
from ems_readiness.simulation.runner import BatchRunner

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("capacity_sensitivity")

# ── Configuration ────────────────────────────────────────────────────
K_VALUES = [20, 40]              # test both fleet sizes
CAPACITY_VALUES = [2, 5]
NUM_REPLICATIONS = 15          # balance runtime vs statistical power
HORIZON_HOURS = 168            # 1 week
SEED_BASE = 42
OUTPUT_DIR = PROJECT_ROOT / "results" / "capacity_comparison"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Load shared data ────────────────────────────────────────────────

def load_data():
    """Load distance matrix, demand, travel-time matrix, and firehouse info."""
    dm = pd.read_csv(
        PROJECT_ROOT / "data" / "processed" / "distance_matrix_firehouse_precinct.csv",
        index_col=0,
    )
    dm.columns = dm.columns.astype(str)

    dl = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "demand_lambda_precinct.csv")
    demand = dl.set_index(dl["precinct"].astype(str))["lambda_per_hour"]
    demand.index.name = None
    demand.name = "demand"

    # Service config
    svc_path = PROJECT_ROOT / "configs" / "service.yaml"
    speed = 20.0
    if svc_path.exists():
        with open(svc_path) as f:
            svc = yaml.safe_load(f)
        speed = svc.get("travel_time", {}).get("average_speed_mph", 20.0)

    tt = build_travel_time_matrix(dm, speed_mph=speed)

    # Firehouse info for CBD analysis
    fh_df = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "firehouses_manhattan.csv")
    fh_df["in_cbd"] = fh_df["in_cbd"].astype(str).str.strip().str.lower() == "true"
    fh_df = fh_df.set_index("FacilityName")

    return dm, demand, tt, speed, fh_df


# ── Allocation generation ───────────────────────────────────────────

def generate_allocations(tt, demand, K, capacity, fh_df):
    """Generate allocations for all policies at the given K and capacity."""
    results = {}

    # P0 – spatially-stratified baseline (maximin method)
    log.info(f"  P0 (spatially-stratified, maximin) K={K}, capacity={capacity}")
    alloc_p0 = policies.spatially_stratified_allocation(
        K=K, method="maximin", capacity=capacity,
        data_dir=PROJECT_ROOT / "data" / "processed",
    )
    results["P0"] = alloc_p0

    # P1 – demand-proportional
    log.info(f"  P1 (demand-proportional) K={K}, capacity={capacity}")
    alloc_p1 = policies.demand_proportional_allocation(
        travel_time=tt, demand=demand, K=K, capacity=capacity,
    )
    results["P1_demand"] = alloc_p1

    # P2 – demand-weighted optimisation
    log.info(f"  P2 (demand-weighted opt) K={K}, capacity={capacity}")
    prob = models.solve_model(
        "demand_weighted", tt, demand, K=K, capacity=capacity,
    )
    status = pulp.LpStatus[prob.status]
    log.info(f"    Solver status: {status}")
    alloc_p2 = models.extract_allocation(prob)
    results["P2_optimised"] = alloc_p2

    return results


# ── Allocation analysis ─────────────────────────────────────────────

def analyse_allocation(alloc: pd.Series, fh_df: pd.DataFrame, tt: pd.DataFrame, demand: pd.Series) -> dict:
    """Compute descriptive statistics for one allocation."""
    active = alloc[alloc > 0]
    n_active = len(active)
    max_units = int(active.max()) if n_active > 0 else 0

    # CBD breakdown
    cbd_fhs = fh_df.index[fh_df["in_cbd"]].tolist()
    units_in_cbd = int(alloc.reindex(cbd_fhs, fill_value=0).sum())
    units_outside_cbd = int(alloc.sum()) - units_in_cbd
    fh_in_cbd = int(sum(1 for fh in active.index if fh in cbd_fhs))
    fh_outside_cbd = n_active - fh_in_cbd

    # Concentration (Gini-like): std of units across active firehouses
    unit_std = float(active.std()) if n_active > 1 else 0.0

    # Demand-weighted RT proxy (nearest-active-firehouse approach)
    if n_active > 0:
        precincts = [p for p in tt.columns if p in demand.index]
        tt_sub = tt.loc[active.index, precincts]
        min_tt = tt_sub.min(axis=0)
        weighted_rt = float((min_tt * demand[precincts]).sum() / demand[precincts].sum())
    else:
        weighted_rt = float("inf")

    return {
        "total_units": int(alloc.sum()),
        "firehouses_used": n_active,
        "max_units_per_fh": max_units,
        "unit_std": round(unit_std, 3),
        "units_in_cbd": units_in_cbd,
        "units_outside_cbd": units_outside_cbd,
        "fh_in_cbd": fh_in_cbd,
        "fh_outside_cbd": fh_outside_cbd,
        "proxy_weighted_rt_min": round(weighted_rt, 3),
    }


# ── Simulation ──────────────────────────────────────────────────────

def run_simulation(alloc: pd.Series, policy_name: str, capacity: int, K: int = 20) -> dict:
    """Run BatchRunner simulation for one allocation."""
    runner = BatchRunner(
        project_root=str(PROJECT_ROOT),
        data_dir="data/processed",
    )
    label = f"{policy_name}_K{K}_cap{capacity}"
    result = runner.run_scenario(
        policy_allocation=alloc,
        K=K,
        num_replications=NUM_REPLICATIONS,
        seed_base=SEED_BASE,
        horizon_hours=HORIZON_HOURS,
        policy_name=label,
        trace=False,
    )
    return result


def extract_sim_metrics(sim_result: dict) -> dict:
    """Pull key metrics from BatchRunner result dict."""
    out = {}
    for metric in [
        "response_time_mean", "response_time_median", "response_time_p90",
        "coverage_fraction", "queue_fraction", "total_incidents",
        "dispatch_delay_mean", "travel_time_mean",
    ]:
        if metric in sim_result:
            out[metric] = sim_result[metric]["mean"]
            out[f"{metric}_ci_lo"] = sim_result[metric]["ci_lower"]
            out[f"{metric}_ci_hi"] = sim_result[metric]["ci_upper"]

    # Compute p95 from per-replication data if available
    per_rep = sim_result.get("per_replication", [])
    if per_rep:
        rt_means = [r.get("response_time_mean", np.nan) for r in per_rep]
        rt_p90s = [r.get("response_time_p90", np.nan) for r in per_rep]
        out["response_time_p95_approx"] = float(np.nanpercentile(rt_p90s, 95)) if rt_p90s else np.nan
    return out


# ── Visualisations ──────────────────────────────────────────────────

def plot_allocation_comparison(all_allocs: dict, fh_df: pd.DataFrame, suffix: str = ""):
    """Side-by-side bar charts showing allocation per firehouse."""
    fig, axes = plt.subplots(len(CAPACITY_VALUES), 1, figsize=(14, 5 * len(CAPACITY_VALUES)),
                             sharex=True)
    if len(CAPACITY_VALUES) == 1:
        axes = [axes]

    policy_names = list(next(iter(all_allocs.values())).keys())
    colors = {"P0": "#4CAF50", "P1_demand": "#2196F3", "P2_optimised": "#FF5722"}
    bar_width = 0.25

    for ax_idx, cap in enumerate(CAPACITY_VALUES):
        ax = axes[ax_idx]
        allocs = all_allocs[cap]

        # Get union of active firehouses
        active_fhs = set()
        for a in allocs.values():
            active_fhs.update(a[a > 0].index.tolist())
        active_fhs = sorted(active_fhs)

        x = np.arange(len(active_fhs))
        for pidx, pname in enumerate(policy_names):
            vals = [allocs[pname].get(fh, 0) for fh in active_fhs]
            ax.bar(x + pidx * bar_width, vals, bar_width,
                   label=pname, color=colors.get(pname, "gray"), alpha=0.85)

        ax.set_title(f"Allocation (Capacity = {cap})", fontsize=13, fontweight="bold")
        ax.set_ylabel("Units Allocated")
        ax.axhline(y=cap, color="red", linestyle="--", alpha=0.5, label=f"Cap={cap}")
        ax.legend(fontsize=9)
        ax.set_xticks(x + bar_width)
        ax.set_xticklabels([fh[:20] for fh in active_fhs], rotation=60, ha="right", fontsize=7)

    plt.tight_layout()
    fname = f"allocation_comparison{suffix}.png"
    fig.savefig(OUTPUT_DIR / fname, dpi=150, bbox_inches="tight")
    plt.close(fig)
    log.info(f"Saved {fname}")


def plot_performance_comparison(comparison_df: pd.DataFrame, suffix: str = ""):
    """Bar charts comparing simulation performance metrics."""
    metrics_to_plot = [
        ("response_time_mean", "Mean Response Time (min)", False),
        ("response_time_p90", "90th Percentile RT (min)", False),
        ("coverage_fraction", "Coverage Fraction", True),
        ("queue_fraction", "Queue Fraction", False),
    ]
    available_metrics = [m for m in metrics_to_plot if m[0] in comparison_df.columns]

    fig, axes = plt.subplots(1, len(available_metrics), figsize=(5 * len(available_metrics), 5))
    if len(available_metrics) == 1:
        axes = [axes]

    colors_cap = {2: "#1976D2", 5: "#F57C00"}
    hatches_policy = {"P0": "///", "P1_demand": "...", "P2_optimised": ""}

    for ax_idx, (metric, label, is_pct) in enumerate(available_metrics):
        ax = axes[ax_idx]
        groups = comparison_df.groupby("capacity")

        bar_width = 0.12
        policy_list = comparison_df["policy"].unique()
        n_policies = len(policy_list)

        for g_idx, (cap, grp) in enumerate(groups):
            for p_idx, (_, row) in enumerate(grp.iterrows()):
                pos = p_idx + g_idx * (n_policies + 0.5) * bar_width
                val = row[metric]
                ci_lo = row.get(f"{metric}_ci_lo", val)
                ci_hi = row.get(f"{metric}_ci_hi", val)
                yerr = [[val - ci_lo], [ci_hi - val]]
                bar = ax.bar(pos, val, bar_width * 2.5, yerr=yerr,
                             color=colors_cap.get(cap, "gray"),
                             hatch=hatches_policy.get(row["policy"], ""),
                             edgecolor="black", linewidth=0.5, capsize=3, alpha=0.85)

        ax.set_title(label, fontsize=11, fontweight="bold")
        if is_pct:
            ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

        # Custom x-ticks
        tick_labels = []
        tick_pos = []
        for g_idx, (cap, grp) in enumerate(groups):
            for p_idx, (_, row) in enumerate(grp.iterrows()):
                pos = p_idx + g_idx * (n_policies + 0.5) * bar_width
                tick_pos.append(pos)
                tick_labels.append(f"{row['policy']}\ncap={cap}")
        ax.set_xticks(tick_pos)
        ax.set_xticklabels(tick_labels, fontsize=7)

    plt.tight_layout()
    fname = f"performance_comparison{suffix}.png"
    fig.savefig(OUTPUT_DIR / fname, dpi=150, bbox_inches="tight")
    plt.close(fig)
    log.info(f"Saved {fname}")


def plot_concentration_analysis(all_allocs: dict, suffix: str = ""):
    """Box/violin plot of units-per-firehouse distribution."""
    fig, axes = plt.subplots(1, len(CAPACITY_VALUES), figsize=(6 * len(CAPACITY_VALUES), 5),
                             sharey=True)
    if len(CAPACITY_VALUES) == 1:
        axes = [axes]

    policy_names = list(next(iter(all_allocs.values())).keys())
    colors = {"P0": "#4CAF50", "P1_demand": "#2196F3", "P2_optimised": "#FF5722"}

    for ax_idx, cap in enumerate(CAPACITY_VALUES):
        ax = axes[ax_idx]
        data_to_plot = []
        labels = []
        for pname in policy_names:
            active = all_allocs[cap][pname]
            active_vals = active[active > 0].values
            data_to_plot.append(active_vals)
            labels.append(pname)

        bp = ax.boxplot(data_to_plot, tick_labels=labels, patch_artist=True, widths=0.5)
        for patch, pname in zip(bp["boxes"], policy_names):
            patch.set_facecolor(colors.get(pname, "gray"))
            patch.set_alpha(0.7)

        ax.set_title(f"Units per Firehouse (Cap={cap})", fontsize=12, fontweight="bold")
        ax.set_ylabel("Units")
        ax.axhline(y=cap, color="red", linestyle="--", alpha=0.5, label=f"Cap={cap}")
        ax.legend(fontsize=9)

    plt.tight_layout()
    fname = f"concentration_analysis{suffix}.png"
    fig.savefig(OUTPUT_DIR / fname, dpi=150, bbox_inches="tight")
    plt.close(fig)
    log.info(f"Saved {fname}")


def plot_cbd_distribution(alloc_stats_df: pd.DataFrame, suffix: str = ""):
    """Stacked bar: CBD vs non-CBD units for each scenario."""
    fig, ax = plt.subplots(figsize=(10, 5))

    x_labels = [f"{row['policy']}\ncap={row['capacity']}" for _, row in alloc_stats_df.iterrows()]
    x = np.arange(len(x_labels))

    cbd = alloc_stats_df["units_in_cbd"].values
    non_cbd = alloc_stats_df["units_outside_cbd"].values

    ax.bar(x, cbd, label="CBD", color="#E53935", alpha=0.85)
    ax.bar(x, non_cbd, bottom=cbd, label="Non-CBD", color="#1E88E5", alpha=0.85)

    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, fontsize=9)
    ax.set_ylabel("Units Allocated")
    ax.set_title("Spatial Distribution: CBD vs Non-CBD", fontsize=13, fontweight="bold")
    ax.legend()
    plt.tight_layout()
    fname = f"cbd_distribution{suffix}.png"
    fig.savefig(OUTPUT_DIR / fname, dpi=150, bbox_inches="tight")
    plt.close(fig)
    log.info(f"Saved {fname}")


# ── Main ────────────────────────────────────────────────────────────

def main():
    t_start = time.time()
    log.info("=" * 65)
    log.info("  Capacity Sensitivity Analysis  –  K=%s  caps=%s", K_VALUES, CAPACITY_VALUES)
    log.info("=" * 65)

    dm, demand, tt, speed, fh_df = load_data()
    log.info(f"Data loaded: {len(dm)} firehouses, {len(demand)} precincts")

    # ── Phase 1: Generate allocations ────────────────────────────────
    # Keyed by (K, cap)
    all_allocs = {}        # (K, cap) -> { policy_name -> pd.Series }
    alloc_stats_rows = []  # flat list for DataFrame

    for K in K_VALUES:
        for cap in CAPACITY_VALUES:
            log.info(f"\n{'─' * 50}")
            log.info(f"Generating allocations: K={K}, capacity={cap}")
            log.info(f"{'─' * 50}")
            allocs = generate_allocations(tt, demand, K, cap, fh_df)
            all_allocs[(K, cap)] = allocs

            for pname, alloc in allocs.items():
                stats = analyse_allocation(alloc, fh_df, tt, demand)
                stats["policy"] = pname
                stats["capacity"] = cap
                stats["K"] = K
                alloc_stats_rows.append(stats)

                # Save allocation CSV
                fname = f"allocation_{pname}_K{K}_cap{cap}.csv"
                alloc.to_csv(OUTPUT_DIR / fname, header=True)
                log.info(f"  Saved {fname}")

    alloc_stats_df = pd.DataFrame(alloc_stats_rows)
    alloc_stats_df.to_csv(OUTPUT_DIR / "allocation_statistics.csv", index=False)
    log.info("\nAllocation statistics saved.")
    log.info("\n" + alloc_stats_df.to_string(index=False))

    # ── Phase 2: Simulation experiments ──────────────────────────────
    sim_rows = []
    for K in K_VALUES:
        for cap in CAPACITY_VALUES:
            for pname, alloc in all_allocs[(K, cap)].items():
                log.info(f"\n{'─' * 50}")
                log.info(f"Simulating {pname} K={K} cap={cap}  ({NUM_REPLICATIONS} reps × {HORIZON_HOURS}h)")
                log.info(f"{'─' * 50}")
                sim_result = run_simulation(alloc, pname, cap, K=K)
                metrics = extract_sim_metrics(sim_result)
                metrics["policy"] = pname
                metrics["capacity"] = cap
                metrics["K"] = K
                sim_rows.append(metrics)

    sim_df = pd.DataFrame(sim_rows)
    sim_df.to_csv(OUTPUT_DIR / "simulation_results.csv", index=False)
    log.info("\nSimulation results saved.")

    # ── Phase 3: Combined comparison table ───────────────────────────
    comparison_df = alloc_stats_df.merge(sim_df, on=["policy", "capacity", "K"], how="outer")
    comparison_df.to_csv(OUTPUT_DIR / "full_comparison.csv", index=False)

    # ── Phase 4: Visualisations (using K=20 for primary comparison,
    #             plus K=40 where capacity actually binds)
    log.info("\nGenerating visualisations …")

    # For each K, produce plots
    for K in K_VALUES:
        k_allocs = {cap: all_allocs[(K, cap)] for cap in CAPACITY_VALUES}
        k_comp = comparison_df[comparison_df["K"] == K].copy()
        k_alloc_stats = alloc_stats_df[alloc_stats_df["K"] == K].copy()

        # Temporarily swap OUTPUT_DIR suffix for per-K files
        plot_allocation_comparison(k_allocs, fh_df, suffix=f"_K{K}")
        plot_performance_comparison(k_comp, suffix=f"_K{K}")
        plot_concentration_analysis(k_allocs, suffix=f"_K{K}")
        plot_cbd_distribution(k_alloc_stats, suffix=f"_K{K}")

    # ── Phase 5: Summary JSON ────────────────────────────────────────
    summary = {
        "K_values": K_VALUES,
        "capacity_values": CAPACITY_VALUES,
        "num_replications": NUM_REPLICATIONS,
        "horizon_hours": HORIZON_HOURS,
        "policies": list(all_allocs[(K_VALUES[0], CAPACITY_VALUES[0])].keys()),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "runtime_seconds": round(time.time() - t_start, 1),
    }
    with open(OUTPUT_DIR / "analysis_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    elapsed = time.time() - t_start
    log.info(f"\n{'=' * 65}")
    log.info(f"  Analysis complete in {elapsed:.0f} seconds")
    log.info(f"  Results saved to {OUTPUT_DIR}")
    log.info(f"{'=' * 65}")


if __name__ == "__main__":
    main()
