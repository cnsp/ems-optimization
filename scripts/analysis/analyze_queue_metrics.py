#!/usr/bin/env python3
"""Queue Metrics Analysis for EMS Optimization Study.

Extracts, analyzes, and visualizes queue-related metrics from all
production experiment results and CBD experiments.

Generates:
  - results/figures/queue_comparison_by_policy.png
  - results/figures/queue_vs_fleet_size.png
  - results/figures/queue_vs_demand.png
  - results/figures/queue_heatmap.png
  - results/tables/queue_statistics.csv

Usage:
    python scripts/analysis/analyze_queue_metrics.py
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

FIGURES_DIR = PROJECT_ROOT / "results" / "figures"
TABLES_DIR = PROJECT_ROOT / "results" / "tables"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)

# Publication style
plt.rcParams.update({
    "figure.dpi": 300, "savefig.dpi": 300, "savefig.bbox": "tight",
    "font.size": 11, "axes.titlesize": 13, "axes.labelsize": 12,
})
POLICY_COLORS = {"P0": "#e74c3c", "P1": "#f39c12", "P2": "#27ae60"}


def load_all_production_results() -> dict:
    """Load all production experiment CSVs."""
    prod_dir = PROJECT_ROOT / "results" / "analysis" / "simulation" / "production"
    data = {}
    for f in sorted(prod_dir.glob("exp*.csv")):
        name = f.stem
        if name == "experiment_summary":
            continue  # Skip summary file
        df = pd.read_csv(f)
        if "replication" in df.columns:
            data[name] = df
            logger.info(f"Loaded {name}: {len(df)} rows")
    return data


def load_cbd_results() -> pd.DataFrame:
    """Load CBD experiment results if available."""
    cbd_path = PROJECT_ROOT / "results" / "analysis" / "simulation" / "cbd_experiment" / "cbd_experiment_results.csv"
    if cbd_path.exists():
        df = pd.read_csv(cbd_path)
        logger.info(f"Loaded CBD results: {len(df)} rows")
        return df
    return pd.DataFrame()


def extract_queue_metrics(data: dict) -> pd.DataFrame:
    """Extract queue metrics from all experiments into a unified table."""
    rows = []
    for exp_name, df in data.items():
        queue_cols = ["mean_queue_length", "max_queue_length", "queue_fraction",
                      "incidents_queued", "total_incidents"]
        for _, row in df.iterrows():
            rows.append({
                "experiment": exp_name,
                "scenario_id": row.get("scenario_id", ""),
                "policy": row["policy"],
                "K": row["K"],
                "demand_multiplier": row.get("demand_multiplier", 1.0),
                "service_time_mean": row.get("service_time_mean", 25.0),
                "replication": row["replication"],
                "mean_queue_length": row.get("mean_queue_length", 0),
                "max_queue_length": row.get("max_queue_length", 0),
                "queue_fraction": row.get("queue_fraction", 0),
                "incidents_queued": row.get("incidents_queued", 0),
                "total_incidents": row.get("total_incidents", 0),
                "mean_response_time": row.get("mean_response_time", np.nan),
                "coverage_8min": row.get("coverage_8min", np.nan),
            })
    return pd.DataFrame(rows)


def compute_queue_statistics(qdf: pd.DataFrame) -> pd.DataFrame:
    """Compute comprehensive queue statistics by policy and scenario."""
    groups = qdf.groupby(["experiment", "policy", "K", "demand_multiplier"])

    stats_rows = []
    for (exp, pol, k, dm), grp in groups:
        stats_rows.append({
            "experiment": exp,
            "policy": pol,
            "K": k,
            "demand_multiplier": dm,
            "n_replications": len(grp),
            "mean_queue_length_avg": grp["mean_queue_length"].mean(),
            "mean_queue_length_std": grp["mean_queue_length"].std(),
            "max_queue_length_avg": grp["max_queue_length"].mean(),
            "max_queue_length_max": grp["max_queue_length"].max(),
            "queue_fraction_avg": grp["queue_fraction"].mean(),
            "queue_fraction_std": grp["queue_fraction"].std(),
            "pct_reps_with_queuing": (grp["incidents_queued"] > 0).mean() * 100,
            "mean_incidents_queued": grp["incidents_queued"].mean(),
            "mean_total_incidents": grp["total_incidents"].mean(),
            "mean_response_time": grp["mean_response_time"].mean(),
            "coverage_8min": grp["coverage_8min"].mean(),
        })
    return pd.DataFrame(stats_rows)


def plot_queue_comparison_by_policy(qdf: pd.DataFrame, save_path: Path):
    """Box plots of queue metrics by policy (Experiment 1 baseline)."""
    exp1 = qdf[qdf["experiment"] == "exp1_policy_comparison"]

    fig, axes = plt.subplots(1, 3, figsize=(14, 5))

    metrics = [
        ("mean_queue_length", "Mean Queue Length"),
        ("max_queue_length", "Max Queue Length"),
        ("queue_fraction", "Queue Fraction (%)"),
    ]

    for ax, (col, title) in zip(axes, metrics):
        plot_data = exp1.copy()
        if col == "queue_fraction":
            plot_data[col] = plot_data[col] * 100

        for policy in ["P0", "P1", "P2"]:
            vals = plot_data[plot_data["policy"] == policy][col]
            bp = ax.boxplot([vals], positions=[["P0", "P1", "P2"].index(policy)],
                           widths=0.6, patch_artist=True)
            bp["boxes"][0].set_facecolor(POLICY_COLORS.get(policy, "gray"))
            bp["boxes"][0].set_alpha(0.7)

        ax.set_xticks(range(3))
        ax.set_xticklabels(["P0\n(Spatial)", "P1\n(Proportional)", "P2\n(Optimized)"])
        ax.set_title(title, fontweight="bold")
        ax.set_ylabel(title)
        ax.grid(axis="y", alpha=0.3)

    fig.suptitle("Queue Metrics by Policy (K=20, Baseline Demand)", fontweight="bold", fontsize=14)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    logger.info(f"Saved {save_path}")


def plot_queue_vs_fleet_size(qdf: pd.DataFrame, save_path: Path):
    """Queue behavior vs fleet size K."""
    exp2 = qdf[qdf["experiment"] == "exp2_fleet_sensitivity"]
    if exp2.empty:
        logger.warning("No exp2 data for queue vs fleet size")
        return

    summary = exp2.groupby(["K", "policy"]).agg({
        "mean_queue_length": "mean",
        "queue_fraction": "mean",
        "max_queue_length": "mean",
    }).reset_index()

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    for col, title, ax in zip(
        ["mean_queue_length", "queue_fraction", "max_queue_length"],
        ["Mean Queue Length", "Queue Fraction", "Max Queue Length"],
        axes
    ):
        for policy in ["P0", "P1", "P2"]:
            pdata = summary[summary["policy"] == policy]
            ax.plot(pdata["K"], pdata[col], "o-",
                   color=POLICY_COLORS.get(policy, "gray"),
                   label=policy, linewidth=2, markersize=6)
        ax.set_xlabel("Fleet Size (K)")
        ax.set_ylabel(title)
        ax.set_title(title, fontweight="bold")
        ax.legend()
        ax.grid(alpha=0.3)

    fig.suptitle("Queue Metrics vs Fleet Size", fontweight="bold", fontsize=14)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    logger.info(f"Saved {save_path}")


def plot_queue_vs_demand(qdf: pd.DataFrame, save_path: Path):
    """Queue behavior vs demand multiplier."""
    exp3 = qdf[qdf["experiment"] == "exp3_demand_sensitivity"]
    if exp3.empty:
        logger.warning("No exp3 data for queue vs demand")
        return

    summary = exp3.groupby(["demand_multiplier", "policy"]).agg({
        "mean_queue_length": "mean",
        "queue_fraction": "mean",
        "max_queue_length": "mean",
        "incidents_queued": "mean",
    }).reset_index()

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    for col, title, ax in zip(
        ["mean_queue_length", "queue_fraction", "incidents_queued"],
        ["Mean Queue Length", "Queue Fraction", "Mean Incidents Queued"],
        axes
    ):
        for policy in ["P0", "P1", "P2"]:
            pdata = summary[summary["policy"] == policy]
            ax.plot(pdata["demand_multiplier"], pdata[col], "o-",
                   color=POLICY_COLORS.get(policy, "gray"),
                   label=policy, linewidth=2, markersize=6)
        ax.set_xlabel("Demand Multiplier")
        ax.set_ylabel(title)
        ax.set_title(title, fontweight="bold")
        ax.legend()
        ax.grid(alpha=0.3)

    fig.suptitle("Queue Metrics vs Demand Level", fontweight="bold", fontsize=14)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    logger.info(f"Saved {save_path}")


def plot_queue_heatmap(stats_df: pd.DataFrame, save_path: Path):
    """Heatmap of queue metrics across all scenarios."""
    # Create a pivot for queue fraction
    pivot_data = stats_df[stats_df["experiment"].isin(
        ["exp1_policy_comparison", "exp2_fleet_sensitivity", "exp3_demand_sensitivity"]
    )].copy()

    # Build a meaningful label
    pivot_data["label"] = pivot_data.apply(
        lambda r: f"{r['experiment'].split('_')[0]} K={int(r['K'])} d={r['demand_multiplier']}", axis=1
    )

    if pivot_data.empty:
        logger.warning("No data for heatmap")
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 8))

    for ax, (metric, title) in zip(axes, [
        ("queue_fraction_avg", "Mean Queue Fraction"),
        ("mean_queue_length_avg", "Mean Queue Length"),
    ]):
        try:
            pivot = pivot_data.pivot_table(values=metric, index="label", columns="policy", aggfunc="mean")
            pivot = pivot.reindex(columns=["P0", "P1", "P2"])
            sns.heatmap(pivot, annot=True, fmt=".4f", cmap="YlOrRd", ax=ax,
                       linewidths=0.5, cbar_kws={"label": title})
            ax.set_title(title, fontweight="bold")
            ax.set_ylabel("Scenario")
        except Exception as e:
            logger.warning(f"Could not create heatmap for {metric}: {e}")

    fig.suptitle("Queue Metrics Across All Scenarios", fontweight="bold", fontsize=14)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    logger.info(f"Saved {save_path}")


def perform_queue_anova(qdf: pd.DataFrame) -> pd.DataFrame:
    """Perform ANOVA on queue metrics across policies."""
    results = []

    for exp_name in qdf["experiment"].unique():
        exp_data = qdf[qdf["experiment"] == exp_name]

        for metric in ["mean_queue_length", "max_queue_length", "queue_fraction"]:
            groups = [grp[metric].values for _, grp in exp_data.groupby("policy")]
            if len(groups) < 2:
                continue

            # Check if all values are the same (no variation)
            all_vals = np.concatenate(groups)
            if np.std(all_vals) == 0:
                results.append({
                    "experiment": exp_name,
                    "metric": metric,
                    "F_statistic": 0.0,
                    "p_value": 1.0,
                    "significant": False,
                    "note": "No variation in data (all values identical)",
                })
                continue

            try:
                f_stat, p_val = stats.f_oneway(*groups)
                results.append({
                    "experiment": exp_name,
                    "metric": metric,
                    "F_statistic": f_stat if not np.isnan(f_stat) else 0.0,
                    "p_value": p_val if not np.isnan(p_val) else 1.0,
                    "significant": p_val < 0.05 if not np.isnan(p_val) else False,
                    "note": "",
                })
            except Exception as e:
                results.append({
                    "experiment": exp_name,
                    "metric": metric,
                    "F_statistic": 0.0,
                    "p_value": 1.0,
                    "significant": False,
                    "note": str(e),
                })

    return pd.DataFrame(results)


def main():
    logger.info("=" * 60)
    logger.info("QUEUE METRICS ANALYSIS")
    logger.info("=" * 60)

    # Load data
    data = load_all_production_results()
    cbd_data = load_cbd_results()

    if cbd_data is not None and not cbd_data.empty:
        data["cbd_experiment"] = cbd_data

    # Extract queue metrics
    qdf = extract_queue_metrics(data)
    logger.info(f"Total queue metric records: {len(qdf)}")

    # Compute statistics
    stats_df = compute_queue_statistics(qdf)
    stats_df.to_csv(TABLES_DIR / "queue_statistics.csv", index=False)
    logger.info(f"Saved queue statistics: {len(stats_df)} rows")

    # ANOVA
    anova_df = perform_queue_anova(qdf)
    anova_df.to_csv(TABLES_DIR / "queue_anova.csv", index=False)
    logger.info(f"Saved queue ANOVA results")

    # Generate visualizations
    plot_queue_comparison_by_policy(qdf, FIGURES_DIR / "queue_comparison_by_policy.png")
    plot_queue_vs_fleet_size(qdf, FIGURES_DIR / "queue_vs_fleet_size.png")
    plot_queue_vs_demand(qdf, FIGURES_DIR / "queue_vs_demand.png")
    plot_queue_heatmap(stats_df, FIGURES_DIR / "queue_heatmap.png")

    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("QUEUE METRICS SUMMARY")
    logger.info("=" * 60)
    for exp_name in sorted(stats_df["experiment"].unique()):
        exp_stats = stats_df[stats_df["experiment"] == exp_name]
        logger.info(f"\n--- {exp_name} ---")
        for _, row in exp_stats.iterrows():
            logger.info(
                f"  {row['policy']} K={int(row['K'])}: "
                f"queue_frac={row['queue_fraction_avg']:.4f}, "
                f"mean_ql={row['mean_queue_length_avg']:.4f}, "
                f"max_ql={row['max_queue_length_max']:.0f}, "
                f"pct_reps_queued={row['pct_reps_with_queuing']:.1f}%"
            )

    logger.info("\nQueue analysis complete!")


if __name__ == "__main__":
    main()
