#!/usr/bin/env python3
"""
Phase 6 – Publication-Quality Figures
======================================

Reads production experiment CSVs and generates five publication figures (300 DPI).
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
PROJECT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT / "results" / "simulation" / "production"
FIG_DIR = PROJECT / "results" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

DPI = 300
CAPACITY = 5  # v1 production experiments used capacity=5 (implicit default)
PALETTE = {"P0": "#d62728", "P1": "#1f77b4", "P2": "#2ca02c"}
POLICY_LABELS = {"P0": "P0 (Spatially-Stratified)", "P1": "P1 (Demand-Prop.)", "P2": "P2 (Max Coverage)"}
sns.set_theme(style="whitegrid", font_scale=1.1, rc={"figure.dpi": DPI})


def load(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / f"{name}.csv")


# ===================================================================
# Figure 1 – Policy Comparison (multi-panel)
# ===================================================================
def fig1_policy_comparison():
    print("  Figure 1: Policy Comparison …")
    df = load("exp1_policy_comparison")

    fig, axes = plt.subplots(1, 4, figsize=(18, 5))

    # Panel A – Response Time Box Plot
    ax = axes[0]
    order = ["P0", "P1", "P2"]
    sns.boxplot(data=df, x="policy", y="mean_response_time", order=order,
                palette=PALETTE, ax=ax, width=0.5, fliersize=3)
    ax.set_xlabel("Policy")
    ax.set_ylabel("Mean Response Time (min)")
    ax.set_title("A. Response Time")
    ax.set_xticklabels([POLICY_LABELS[p] for p in order], rotation=15, ha="right")

    # Add significance brackets
    y_max = df["mean_response_time"].max()
    bracket_y = y_max * 1.05
    for i, (pA, pB) in enumerate([(0, 2), (0, 1), (1, 2)]):
        a = df[df["policy"] == order[pA]]["mean_response_time"]
        b = df[df["policy"] == order[pB]]["mean_response_time"]
        _, p = stats.ttest_ind(a, b)
        stars = "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else "ns"))
        y = bracket_y + i * y_max * 0.08
        ax.plot([pA, pA, pB, pB], [y, y + y_max*0.02, y + y_max*0.02, y], lw=1, c="k")
        ax.text((pA + pB) / 2, y + y_max*0.02, stars, ha="center", va="bottom", fontsize=9)

    # Panel B – 6-min Coverage (NYC) Bar Chart
    ax = axes[1]
    x_pos = np.arange(3)
    if "coverage_6min" in df.columns:
        means_6 = df.groupby("policy")["coverage_6min"].mean().reindex(order)
        sems_6 = df.groupby("policy")["coverage_6min"].sem().reindex(order)
        ax.bar(x_pos, means_6 * 100, yerr=sems_6 * 100 * 1.96, capsize=4,
               color=[PALETTE[p] for p in order], edgecolor="black", linewidth=0.5)
    ax.set_xticks(x_pos)
    ax.set_xticklabels([POLICY_LABELS[p] for p in order], rotation=15, ha="right")
    ax.set_ylabel("6-min Coverage (%)")
    ax.set_title("B. 6-min Coverage (NYC)")
    ax.set_ylim(0, 105)
    ax.axhline(90, ls="--", color="grey", lw=0.8, label="90% target")
    ax.legend(fontsize=8)

    # Panel C – 8-min Coverage (NFPA) Bar Chart
    ax = axes[2]
    means = df.groupby("policy")["coverage_8min"].mean().reindex(order)
    sems = df.groupby("policy")["coverage_8min"].sem().reindex(order)
    ax.bar(x_pos, means * 100, yerr=sems * 100 * 1.96, capsize=4,
           color=[PALETTE[p] for p in order], edgecolor="black", linewidth=0.5)
    ax.set_xticks(x_pos)
    ax.set_xticklabels([POLICY_LABELS[p] for p in order], rotation=15, ha="right")
    ax.set_ylabel("8-min Coverage (NFPA) (%)")
    ax.set_title("C. 8-min Coverage (NFPA)")
    ax.set_ylim(0, 105)
    ax.axhline(90, ls="--", color="grey", lw=0.8, label="90% target")
    ax.legend(fontsize=8)

    # Panel D – Utilization
    ax = axes[3]
    means_u = df.groupby("policy")["mean_utilization"].mean().reindex(order)
    sems_u = df.groupby("policy")["mean_utilization"].sem().reindex(order)
    ax.bar(x_pos, means_u, yerr=sems_u * 1.96, capsize=4,
           color=[PALETTE[p] for p in order], edgecolor="black", linewidth=0.5)
    ax.set_xticks(x_pos)
    ax.set_xticklabels([POLICY_LABELS[p] for p in order], rotation=15, ha="right")
    ax.set_ylabel("Mean Utilization")
    ax.set_title("D. Utilization")

    fig.suptitle(f"Figure 1: Baseline Policy Comparison (K=20, cap={CAPACITY}, 30 replications)", fontsize=13, y=1.02)
    fig.tight_layout()
    path = FIG_DIR / "pub_fig1_policy_comparison.png"
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"    → {path}")


# ===================================================================
# Figure 2 – Fleet Sensitivity (line + CI ribbon)
# ===================================================================
def fig2_fleet_sensitivity():
    print("  Figure 2: Fleet Sensitivity …")
    df = load("exp2_fleet_sensitivity")

    fig, ax = plt.subplots(figsize=(8, 5))
    for pol in ["P0", "P1", "P2"]:
        sub = df[df["policy"] == pol]
        grouped = sub.groupby("K")["mean_response_time"]
        means = grouped.mean()
        sems = grouped.sem()
        ci = 1.96 * sems
        ax.plot(means.index, means.values, "o-", color=PALETTE[pol], label=POLICY_LABELS[pol], markersize=5)
        ax.fill_between(means.index, (means - ci).values, (means + ci).values,
                        alpha=0.18, color=PALETTE[pol])

    ax.set_xlabel("Fleet Size (K)")
    ax.set_ylabel("Mean Response Time (min)")
    ax.set_title(f"Figure 2: Fleet Size Sensitivity with 95% CI (cap={CAPACITY})")
    ax.legend()
    ax.axhline(8, ls="--", color="grey", lw=0.8, label="8-min NFPA target")
    ax.axhline(6, ls="--", color="red", lw=0.8, alpha=0.6, label="6-min NYC target")
    fig.tight_layout()
    path = FIG_DIR / "pub_fig2_fleet_sensitivity.png"
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"    → {path}")


# ===================================================================
# Figure 3 – Demand Robustness
# ===================================================================
def fig3_demand_robustness():
    print("  Figure 3: Demand Robustness …")
    df = load("exp3_demand_sensitivity")

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # Panel A – Response Time
    ax = axes[0]
    for pol in ["P0", "P1", "P2"]:
        sub = df[df["policy"] == pol]
        g = sub.groupby("demand_multiplier")["mean_response_time"]
        means, sems = g.mean(), g.sem()
        ax.plot(means.index, means.values, "o-", color=PALETTE[pol], label=POLICY_LABELS[pol])
        ax.fill_between(means.index, (means - 1.96*sems).values, (means + 1.96*sems).values,
                        alpha=0.15, color=PALETTE[pol])
    ax.set_xlabel("Demand Multiplier")
    ax.set_ylabel("Mean Response Time (min)")
    ax.set_title("A. Response Time vs Demand")
    ax.legend(fontsize=8)
    ax.axhline(8, ls="--", color="grey", lw=0.8)

    # Panel B – 6-min Coverage (NYC)
    ax = axes[1]
    has_6min = "coverage_6min" in df.columns
    for pol in ["P0", "P1", "P2"]:
        sub = df[df["policy"] == pol]
        if has_6min:
            g = sub.groupby("demand_multiplier")["coverage_6min"]
            means, sems = g.mean(), g.sem()
            ax.plot(means.index, means.values * 100, "D-", color=PALETTE[pol], label=POLICY_LABELS[pol])
            ax.fill_between(means.index, (means - 1.96*sems).values * 100, (means + 1.96*sems).values * 100,
                            alpha=0.15, color=PALETTE[pol])
    ax.set_xlabel("Demand Multiplier")
    ax.set_ylabel("6-min Coverage (NYC) (%)")
    ax.set_title("B. 6-min Coverage vs Demand")
    ax.legend(fontsize=8)
    ax.axhline(90, ls="--", color="grey", lw=0.8)

    # Panel C – 8-min Coverage (NFPA)
    ax = axes[2]
    for pol in ["P0", "P1", "P2"]:
        sub = df[df["policy"] == pol]
        g = sub.groupby("demand_multiplier")["coverage_8min"]
        means, sems = g.mean(), g.sem()
        ax.plot(means.index, means.values * 100, "o-", color=PALETTE[pol], label=POLICY_LABELS[pol])
        ax.fill_between(means.index, (means - 1.96*sems).values * 100, (means + 1.96*sems).values * 100,
                        alpha=0.15, color=PALETTE[pol])
    ax.set_xlabel("Demand Multiplier")
    ax.set_ylabel("8-min Coverage (NFPA) (%)")
    ax.set_title("C. 8-min Coverage (NFPA) vs Demand")
    ax.legend(fontsize=8)
    ax.axhline(90, ls="--", color="grey", lw=0.8)

    fig.suptitle(f"Figure 3: Demand Robustness (K=20, cap={CAPACITY})", fontsize=13, y=1.02)
    fig.tight_layout()
    path = FIG_DIR / "pub_fig3_demand_robustness.png"
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"    → {path}")


# ===================================================================
# Figure 4 – Service Time Sensitivity (grouped bar)
# ===================================================================
def fig4_service_sensitivity():
    print("  Figure 4: Service Time Sensitivity …")
    df = load("exp4_service_robustness")

    fig, ax = plt.subplots(figsize=(9, 5))
    st_levels = sorted(df["service_time_mean"].unique())
    policies = ["P0", "P1", "P2"]
    x = np.arange(len(st_levels))
    w = 0.25

    for i, pol in enumerate(policies):
        means, errs = [], []
        for st in st_levels:
            sub = df[(df["policy"] == pol) & (df["service_time_mean"] == st)]
            means.append(sub["mean_response_time"].mean())
            errs.append(1.96 * sub["mean_response_time"].sem())
        ax.bar(x + i * w, means, w, yerr=errs, capsize=3,
               label=POLICY_LABELS[pol], color=PALETTE[pol], edgecolor="black", linewidth=0.5)

    ax.set_xticks(x + w)
    ax.set_xticklabels([f"{int(s)} min" for s in st_levels])
    ax.set_xlabel("Mean Service Time")
    ax.set_ylabel("Mean Response Time (min)")
    ax.set_title(f"Figure 4: Service Time Sensitivity (K=20, cap={CAPACITY})")
    ax.legend()
    ax.axhline(8, ls="--", color="grey", lw=0.8)
    fig.tight_layout()
    path = FIG_DIR / "pub_fig4_service_sensitivity.png"
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"    → {path}")


# ===================================================================
# Figure 5 – Performance Heatmap
# ===================================================================
def fig5_heatmap():
    print("  Figure 5: Performance Heatmap …")
    frames = []
    for name in ["exp1_policy_comparison", "exp2_fleet_sensitivity",
                  "exp3_demand_sensitivity", "exp4_service_robustness"]:
        frames.append(load(name))
    all_data = pd.concat(frames, ignore_index=True)

    # Build scenario labels
    all_data["scenario"] = all_data["scenario_id"]
    pivot = all_data.groupby(["policy", "scenario_id"])["mean_response_time"].mean().reset_index()
    heatmap_data = pivot.pivot(index="scenario_id", columns="policy", values="mean_response_time")

    # Normalize by row (best policy = 1.0)
    norm = heatmap_data.div(heatmap_data.min(axis=1), axis=0)

    # Take a representative subset (one per experiment)
    keep_scenarios = []
    for exp_prefix in ["P0_K20", "P1_K20", "P2_K20",
                       "P0_K15", "P1_K25", "P2_K40",
                       "P0_K20_d0.5", "P1_K20_d1.5", "P2_K20_d2.0",
                       "P0_K20_s20", "P1_K20_s30", "P2_K20_s25"]:
        if exp_prefix in norm.index:
            keep_scenarios.append(exp_prefix)
    if not keep_scenarios:
        keep_scenarios = list(norm.index[:15])
    norm_sub = norm.loc[keep_scenarios]

    fig, ax = plt.subplots(figsize=(7, max(5, len(norm_sub) * 0.4)))
    sns.heatmap(norm_sub, annot=True, fmt=".2f", cmap="RdYlGn_r",
                linewidths=0.5, ax=ax, vmin=1.0, vmax=norm_sub.max().max(),
                cbar_kws={"label": "Relative Response Time\n(1.0 = best)"})
    ax.set_title(f"Figure 5: Relative Performance Heatmap (cap={CAPACITY})")
    ax.set_ylabel("Scenario")
    ax.set_xlabel("Policy")
    fig.tight_layout()
    path = FIG_DIR / "pub_fig5_performance_heatmap.png"
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"    → {path}")


# ===================================================================
# Main
# ===================================================================
def main():
    print("=" * 60)
    print("Generating publication-quality figures …")
    print("=" * 60)
    fig1_policy_comparison()
    fig2_fleet_sensitivity()
    fig3_demand_robustness()
    fig4_service_sensitivity()
    fig5_heatmap()
    print("\nAll figures saved to results/figures/")


if __name__ == "__main__":
    main()
