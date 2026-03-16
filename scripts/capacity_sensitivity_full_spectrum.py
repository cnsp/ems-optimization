#!/usr/bin/env python3
"""Full-Spectrum Capacity Sensitivity Analysis: capacity = {1, 2, 3, 4, 5} at K=20 and K=40.

Runs optimization + simulation for capacity values 1, 3, 4 (the missing ones),
then merges with existing cap=2 and cap=5 results to produce a unified analysis
across all five capacity levels.

Outputs go to results/capacity_comparison/
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
from ems_readiness.service.travel_time import build_travel_time_matrix
from ems_readiness.simulation.runner import BatchRunner

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("capacity_full_spectrum")

# ── Configuration ────────────────────────────────────────────────────
K_VALUES = [20, 40]
NEW_CAPACITY_VALUES = [1, 3, 4]       # the missing ones
ALL_CAPACITY_VALUES = [1, 2, 3, 4, 5] # full spectrum
NUM_REPLICATIONS = 15
HORIZON_HOURS = 168   # 1 week
SEED_BASE = 42
OUTPUT_DIR = PROJECT_ROOT / "results" / "capacity_comparison"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ── Load shared data ────────────────────────────────────────────────
def load_data():
    dm = pd.read_csv(
        PROJECT_ROOT / "data" / "processed" / "distance_matrix_firehouse_precinct.csv",
        index_col=0,
    )
    dm.columns = dm.columns.astype(str)

    dl = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "demand_lambda_precinct.csv")
    demand = dl.set_index(dl["precinct"].astype(str))["lambda_per_hour"]
    demand.index.name = None
    demand.name = "demand"

    svc_path = PROJECT_ROOT / "configs" / "service.yaml"
    speed = 20.0
    if svc_path.exists():
        with open(svc_path) as f:
            svc = yaml.safe_load(f)
        speed = svc.get("travel_time", {}).get("average_speed_mph", 20.0)

    tt = build_travel_time_matrix(dm, speed_mph=speed)

    fh_df = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "firehouses_manhattan.csv")
    fh_df["in_cbd"] = fh_df["in_cbd"].astype(str).str.strip().str.lower() == "true"
    fh_df = fh_df.set_index("FacilityName")

    return dm, demand, tt, speed, fh_df


# ── Allocation generation ───────────────────────────────────────────
def generate_allocations(tt, demand, K, capacity, fh_df):
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
def analyse_allocation(alloc, fh_df, tt, demand):
    active = alloc[alloc > 0]
    n_active = len(active)
    max_units = int(active.max()) if n_active > 0 else 0

    cbd_fhs = fh_df.index[fh_df["in_cbd"]].tolist()
    units_in_cbd = int(alloc.reindex(cbd_fhs, fill_value=0).sum())
    units_outside_cbd = int(alloc.sum()) - units_in_cbd
    fh_in_cbd = int(sum(1 for fh in active.index if fh in cbd_fhs))
    fh_outside_cbd = n_active - fh_in_cbd

    unit_std = float(active.std()) if n_active > 1 else 0.0

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
def run_simulation(alloc, policy_name, capacity, K=20):
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


def extract_sim_metrics(sim_result):
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

    per_rep = sim_result.get("per_replication", [])
    if per_rep:
        rt_p90s = [r.get("response_time_p90", np.nan) for r in per_rep]
        out["response_time_p95_approx"] = float(np.nanpercentile(rt_p90s, 95)) if rt_p90s else np.nan
    return out


# ═══════════════════════════════════════════════════════════════════
# PHASE 1: Run new experiments for capacity = 1, 3, 4
# ═══════════════════════════════════════════════════════════════════

def run_new_experiments(dm, demand, tt, speed, fh_df):
    """Run optimization + simulation for the missing capacity values."""
    new_alloc_stats = []
    new_sim_rows = []

    for K in K_VALUES:
        for cap in NEW_CAPACITY_VALUES:
            log.info(f"\n{'═' * 55}")
            log.info(f"  K={K}, capacity={cap}")
            log.info(f"{'═' * 55}")

            allocs = generate_allocations(tt, demand, K, cap, fh_df)

            for pname, alloc in allocs.items():
                # Analyse allocation
                stats = analyse_allocation(alloc, fh_df, tt, demand)
                stats["policy"] = pname
                stats["capacity"] = cap
                stats["K"] = K
                new_alloc_stats.append(stats)

                # Save allocation CSV
                fname = f"allocation_{pname}_K{K}_cap{cap}.csv"
                alloc.to_csv(OUTPUT_DIR / fname, header=True)
                log.info(f"  Saved {fname}")

                # Run simulation
                log.info(f"  Simulating {pname} K={K} cap={cap} ({NUM_REPLICATIONS} reps × {HORIZON_HOURS}h)")
                sim_result = run_simulation(alloc, pname, cap, K=K)
                metrics = extract_sim_metrics(sim_result)
                metrics["policy"] = pname
                metrics["capacity"] = cap
                metrics["K"] = K
                new_sim_rows.append(metrics)

    return pd.DataFrame(new_alloc_stats), pd.DataFrame(new_sim_rows)


# ═══════════════════════════════════════════════════════════════════
# PHASE 2: Merge with existing results
# ═══════════════════════════════════════════════════════════════════

def merge_results(new_alloc_df, new_sim_df):
    """Merge new results with existing cap=2,5 results."""
    # Load existing
    existing_sim = pd.read_csv(OUTPUT_DIR / "simulation_results.csv")
    existing_alloc = pd.read_csv(OUTPUT_DIR / "allocation_statistics.csv")

    # Combine
    all_sim = pd.concat([existing_sim, new_sim_df], ignore_index=True)
    all_alloc = pd.concat([existing_alloc, new_alloc_df], ignore_index=True)

    # Deduplicate: keep last entry for each (K, capacity, policy)
    all_sim = all_sim.drop_duplicates(subset=["K", "capacity", "policy"], keep="last")
    all_alloc = all_alloc.drop_duplicates(subset=["K", "capacity", "policy"], keep="last")

    # Sort
    all_sim = all_sim.sort_values(["K", "capacity", "policy"]).reset_index(drop=True)
    all_alloc = all_alloc.sort_values(["K", "capacity", "policy"]).reset_index(drop=True)

    # Save updated files
    all_sim.to_csv(OUTPUT_DIR / "simulation_results.csv", index=False)
    all_alloc.to_csv(OUTPUT_DIR / "allocation_statistics.csv", index=False)

    # Full comparison
    full_comp = all_alloc.merge(all_sim, on=["policy", "capacity", "K"], how="outer")
    full_comp = full_comp.sort_values(["K", "capacity", "policy"]).reset_index(drop=True)
    full_comp.to_csv(OUTPUT_DIR / "full_comparison.csv", index=False)

    log.info(f"Merged results: {len(all_sim)} simulation rows, {len(all_alloc)} allocation rows")
    return full_comp, all_alloc, all_sim


# ═══════════════════════════════════════════════════════════════════
# PHASE 3: Comprehensive Visualisations
# ═══════════════════════════════════════════════════════════════════

POLICY_COLORS = {"P0": "#4CAF50", "P1_demand": "#2196F3", "P2_optimised": "#FF5722"}
POLICY_LABELS = {"P0": "P0 (Uniform-Spatial)", "P1_demand": "P1 (Demand)", "P2_optimised": "P2 (Optimised)"}
POLICY_MARKERS = {"P0": "s", "P1_demand": "^", "P2_optimised": "o"}


def plot_performance_vs_capacity(full_df):
    """Line plots: performance metrics vs capacity for each K and policy."""
    for K in K_VALUES:
        kdf = full_df[full_df["K"] == K].copy()

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(f"Performance vs Capacity Constraint (K={K})", fontsize=15, fontweight="bold")

        metrics = [
            ("response_time_mean", "Mean Response Time (min)", axes[0, 0]),
            ("response_time_p90", "90th Percentile RT (min)", axes[0, 1]),
            ("coverage_fraction", "Coverage Fraction", axes[1, 0]),
            ("firehouses_used", "Firehouses Used", axes[1, 1]),
        ]

        for metric, ylabel, ax in metrics:
            if metric not in kdf.columns:
                ax.text(0.5, 0.5, f"{metric}\nnot available", ha="center", va="center", transform=ax.transAxes)
                continue

            for policy in ["P0", "P1_demand", "P2_optimised"]:
                pdf = kdf[kdf["policy"] == policy].sort_values("capacity")
                if pdf.empty:
                    continue

                ax.plot(pdf["capacity"], pdf[metric],
                        marker=POLICY_MARKERS[policy], color=POLICY_COLORS[policy],
                        label=POLICY_LABELS[policy], linewidth=2, markersize=8)

                # CI bands for sim metrics
                lo_col = f"{metric}_ci_lo"
                hi_col = f"{metric}_ci_hi"
                if lo_col in pdf.columns and hi_col in pdf.columns:
                    ax.fill_between(pdf["capacity"], pdf[lo_col], pdf[hi_col],
                                    color=POLICY_COLORS[policy], alpha=0.15)

            ax.set_xlabel("Capacity Constraint")
            ax.set_ylabel(ylabel)
            ax.set_xticks(ALL_CAPACITY_VALUES)
            ax.legend(fontsize=9)
            ax.grid(True, alpha=0.3)

            if metric == "coverage_fraction":
                ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        fig.savefig(OUTPUT_DIR / f"performance_vs_capacity_K{K}.png", dpi=150, bbox_inches="tight")
        plt.close(fig)
        log.info(f"Saved performance_vs_capacity_K{K}.png")


def plot_tradeoff_analysis(full_df):
    """Trade-off: firehouses used (dispersion) vs mean RT."""
    for K in K_VALUES:
        kdf = full_df[full_df["K"] == K].copy()
        if "response_time_mean" not in kdf.columns or "firehouses_used" not in kdf.columns:
            continue

        fig, ax = plt.subplots(figsize=(10, 7))
        ax.set_title(f"Trade-off: Dispersion vs Performance (K={K})", fontsize=14, fontweight="bold")

        for policy in ["P0", "P1_demand", "P2_optimised"]:
            pdf = kdf[kdf["policy"] == policy].sort_values("capacity")
            if pdf.empty:
                continue

            ax.plot(pdf["firehouses_used"], pdf["response_time_mean"],
                    marker=POLICY_MARKERS[policy], color=POLICY_COLORS[policy],
                    label=POLICY_LABELS[policy], linewidth=2, markersize=10)

            # Annotate capacity values
            for _, row in pdf.iterrows():
                ax.annotate(f"cap={int(row['capacity'])}",
                            (row["firehouses_used"], row["response_time_mean"]),
                            textcoords="offset points", xytext=(8, 5), fontsize=8,
                            color=POLICY_COLORS[policy])

        ax.set_xlabel("Firehouses Used (Dispersion)", fontsize=12)
        ax.set_ylabel("Mean Response Time (min)", fontsize=12)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.invert_xaxis()  # More firehouses = more dispersion = left
        plt.tight_layout()
        fig.savefig(OUTPUT_DIR / f"tradeoff_dispersion_rt_K{K}.png", dpi=150, bbox_inches="tight")
        plt.close(fig)
        log.info(f"Saved tradeoff_dispersion_rt_K{K}.png")


def plot_max_units_vs_capacity(alloc_df):
    """Bar chart: max units per firehouse vs capacity."""
    for K in K_VALUES:
        kdf = alloc_df[alloc_df["K"] == K].copy()

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.set_title(f"Max Units per Firehouse vs Capacity (K={K})", fontsize=14, fontweight="bold")

        bar_width = 0.25
        x = np.arange(len(ALL_CAPACITY_VALUES))

        for pidx, policy in enumerate(["P0", "P1_demand", "P2_optimised"]):
            pdf = kdf[kdf["policy"] == policy].sort_values("capacity")
            if pdf.empty:
                continue
            cap_vals = pdf.groupby("capacity")["max_units_per_fh"].first()
            vals = cap_vals.reindex(ALL_CAPACITY_VALUES).fillna(0)
            ax.bar(x + pidx * bar_width, vals, bar_width,
                   label=POLICY_LABELS[policy], color=POLICY_COLORS[policy], alpha=0.85, edgecolor="white")

        # Add diagonal reference line (cap = max_units when binding)
        ax.plot(x + bar_width, ALL_CAPACITY_VALUES, "k--", alpha=0.4, label="Capacity = Max Units")

        ax.set_xlabel("Capacity Constraint")
        ax.set_ylabel("Max Units at Any Firehouse")
        ax.set_xticks(x + bar_width)
        ax.set_xticklabels(ALL_CAPACITY_VALUES)
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3, axis="y")
        plt.tight_layout()
        fig.savefig(OUTPUT_DIR / f"max_units_vs_capacity_K{K}.png", dpi=150, bbox_inches="tight")
        plt.close(fig)
        log.info(f"Saved max_units_vs_capacity_K{K}.png")


def plot_comprehensive_heatmap(full_df):
    """Heatmap: mean RT for each (policy, capacity) at each K."""
    for K in K_VALUES:
        kdf = full_df[full_df["K"] == K].copy()
        if "response_time_mean" not in kdf.columns:
            continue

        pivot = kdf.pivot_table(index="policy", columns="capacity", values="response_time_mean")
        pivot = pivot.reindex(["P0", "P1_demand", "P2_optimised"])
        pivot = pivot.reindex(columns=ALL_CAPACITY_VALUES)

        fig, ax = plt.subplots(figsize=(10, 4))
        im = ax.imshow(pivot.values, cmap="RdYlGn_r", aspect="auto")

        ax.set_xticks(range(len(ALL_CAPACITY_VALUES)))
        ax.set_xticklabels(ALL_CAPACITY_VALUES)
        ax.set_yticks(range(len(pivot.index)))
        ax.set_yticklabels([POLICY_LABELS.get(p, p) for p in pivot.index])
        ax.set_xlabel("Capacity Constraint")
        ax.set_title(f"Mean Response Time Heatmap (K={K})", fontsize=14, fontweight="bold")

        # Annotate cells
        for i in range(pivot.shape[0]):
            for j in range(pivot.shape[1]):
                val = pivot.iloc[i, j]
                if not pd.isna(val):
                    ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=11, fontweight="bold")

        fig.colorbar(im, ax=ax, label="Mean RT (min)")
        plt.tight_layout()
        fig.savefig(OUTPUT_DIR / f"rt_heatmap_K{K}.png", dpi=150, bbox_inches="tight")
        plt.close(fig)
        log.info(f"Saved rt_heatmap_K{K}.png")


def plot_comprehensive_summary(full_df):
    """Combined multi-panel figure for the full spectrum."""
    fig, axes = plt.subplots(2, 3, figsize=(18, 11))
    fig.suptitle("Full Capacity Spectrum Analysis (K=20 and K=40)", fontsize=16, fontweight="bold")

    # Panel arrangement:
    # Row 0: K=20 (mean RT, p90 RT, firehouses)
    # Row 1: K=40 (mean RT, p90 RT, firehouses)

    for row, K in enumerate(K_VALUES):
        kdf = full_df[full_df["K"] == K].copy()

        panel_defs = [
            ("response_time_mean", "Mean RT (min)", axes[row, 0]),
            ("response_time_p90", "90th %ile RT (min)", axes[row, 1]),
            ("firehouses_used", "Firehouses Used", axes[row, 2]),
        ]

        for metric, ylabel, ax in panel_defs:
            if metric not in kdf.columns:
                continue
            for policy in ["P0", "P1_demand", "P2_optimised"]:
                pdf = kdf[kdf["policy"] == policy].sort_values("capacity")
                if pdf.empty:
                    continue
                ax.plot(pdf["capacity"], pdf[metric],
                        marker=POLICY_MARKERS[policy], color=POLICY_COLORS[policy],
                        label=POLICY_LABELS[policy], linewidth=2, markersize=7)

            ax.set_xlabel("Capacity")
            ax.set_ylabel(ylabel)
            ax.set_xticks(ALL_CAPACITY_VALUES)
            ax.set_title(f"K={K}: {ylabel}", fontsize=11)
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(OUTPUT_DIR / "full_spectrum_summary.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    log.info("Saved full_spectrum_summary.png")


# ═══════════════════════════════════════════════════════════════════
# PHASE 4: Create comprehensive comparison table
# ═══════════════════════════════════════════════════════════════════

def create_comparison_tables(full_df):
    """Create formatted comparison tables."""
    for K in K_VALUES:
        kdf = full_df[full_df["K"] == K].copy()

        # Key metrics table
        cols = ["policy", "capacity", "firehouses_used", "max_units_per_fh",
                "response_time_mean", "response_time_p90", "coverage_fraction",
                "proxy_weighted_rt_min"]
        available = [c for c in cols if c in kdf.columns]
        summary = kdf[available].sort_values(["policy", "capacity"])
        summary.to_csv(OUTPUT_DIR / f"comparison_table_K{K}.csv", index=False)
        log.info(f"Saved comparison_table_K{K}.csv")

        # Print summary
        log.info(f"\n{'=' * 70}")
        log.info(f"  COMPARISON TABLE K={K}")
        log.info(f"{'=' * 70}")
        log.info(f"\n{summary.to_string(index=False)}")

    # Cross-K comparison for best configurations
    best_rows = []
    for K in K_VALUES:
        kdf = full_df[full_df["K"] == K].copy()
        if "response_time_mean" in kdf.columns:
            best_idx = kdf["response_time_mean"].idxmin()
            best = kdf.loc[best_idx].to_dict()
            best["K"] = K
            best_rows.append(best)

    if best_rows:
        best_df = pd.DataFrame(best_rows)
        best_df.to_csv(OUTPUT_DIR / "optimal_configurations.csv", index=False)
        log.info(f"\nOptimal configurations saved.")


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    t_start = time.time()
    log.info("=" * 65)
    log.info("  Full-Spectrum Capacity Sensitivity Analysis")
    log.info(f"  K values: {K_VALUES}")
    log.info(f"  New capacity values: {NEW_CAPACITY_VALUES}")
    log.info(f"  Full spectrum: {ALL_CAPACITY_VALUES}")
    log.info("=" * 65)

    dm, demand, tt, speed, fh_df = load_data()
    log.info(f"Data loaded: {len(dm)} firehouses, {len(demand)} precincts")

    # Phase 1: Run new experiments
    log.info("\n" + "=" * 65)
    log.info("  PHASE 1: Running experiments for capacity = {1, 3, 4}")
    log.info("=" * 65)
    new_alloc_df, new_sim_df = run_new_experiments(dm, demand, tt, speed, fh_df)

    # Phase 2: Merge with existing
    log.info("\n" + "=" * 65)
    log.info("  PHASE 2: Merging with existing cap=2,5 results")
    log.info("=" * 65)
    full_df, alloc_df, sim_df = merge_results(new_alloc_df, new_sim_df)

    # Phase 3: Comprehensive visualisations
    log.info("\n" + "=" * 65)
    log.info("  PHASE 3: Generating comprehensive visualisations")
    log.info("=" * 65)
    plot_performance_vs_capacity(full_df)
    plot_tradeoff_analysis(full_df)
    plot_max_units_vs_capacity(alloc_df)
    plot_comprehensive_heatmap(full_df)
    plot_comprehensive_summary(full_df)

    # Phase 4: Comparison tables
    log.info("\n" + "=" * 65)
    log.info("  PHASE 4: Creating comparison tables")
    log.info("=" * 65)
    create_comparison_tables(full_df)

    # Phase 5: Summary JSON
    summary = {
        "K_values": K_VALUES,
        "all_capacity_values": ALL_CAPACITY_VALUES,
        "new_capacity_values": NEW_CAPACITY_VALUES,
        "num_replications": NUM_REPLICATIONS,
        "horizon_hours": HORIZON_HOURS,
        "policies": ["P0", "P1_demand", "P2_optimised"],
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "runtime_seconds": round(time.time() - t_start, 1),
        "total_scenarios": len(K_VALUES) * len(ALL_CAPACITY_VALUES) * 3,
    }
    with open(OUTPUT_DIR / "analysis_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    elapsed = time.time() - t_start
    log.info(f"\n{'=' * 65}")
    log.info(f"  Full-spectrum analysis complete in {elapsed:.0f}s")
    log.info(f"  Results: {OUTPUT_DIR}")
    log.info(f"{'=' * 65}")


if __name__ == "__main__":
    main()
