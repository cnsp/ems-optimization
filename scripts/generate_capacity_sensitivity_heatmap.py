#!/usr/bin/env python3
"""
Generate capacity sensitivity heatmap for the technical report.

Creates a side-by-side heatmap showing mean response time by policy
and per-firehouse capacity limit at K=20 and K=40.

Output: results/figures/capacity_sensitivity_heatmap.png
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "results" / "capacity_comparison"
FIGURES_DIR = PROJECT_ROOT / "results" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Policy display names — map all known variants to canonical labels
POLICY_LABELS = {
    "P0": "P0",
    "P0_spatial": "P0",
    "P1": "P1",
    "P1_demand": "P1",
    "P2": "P2",
    "P2_optimised": "P2",
}


def load_simulation_data():
    """Load and combine simulation results from all K files."""
    frames = []

    # Main file (K=20 and K=40)
    main_file = RESULTS_DIR / "simulation_results.csv"
    if main_file.exists():
        df = pd.read_csv(main_file)
        print(f"Loaded {len(df)} rows from simulation_results.csv")
        print(f"  Columns: {list(df.columns)}")
        print(f"  Policies: {df['policy'].unique()}")
        print(f"  K values: {sorted(df['K'].unique())}")
        print(f"  Capacity values: {sorted(df['capacity'].unique())}")
        frames.append(df)

    # K=30 file
    k30_file = RESULTS_DIR / "simulation_results_K30.csv"
    if k30_file.exists():
        df30 = pd.read_csv(k30_file)
        print(f"Loaded {len(df30)} rows from simulation_results_K30.csv")
        frames.append(df30)

    if not frames:
        raise FileNotFoundError("No simulation results found!")

    combined = pd.concat(frames, ignore_index=True)
    print(f"\nCombined: {len(combined)} rows")
    print(f"  All K values: {sorted(combined['K'].unique())}")
    print(f"  All capacity values: {sorted(combined['capacity'].unique())}")
    return combined


def create_heatmap(df, k_values=(20, 40)):
    """Create side-by-side heatmaps for specified K values."""
    fig, axes = plt.subplots(1, len(k_values), figsize=(6 * len(k_values), 4.5),
                             sharey=True)
    if len(k_values) == 1:
        axes = [axes]

    fig.suptitle("Capacity Sensitivity: Mean Response Time by Policy and Capacity Limit",
                 fontsize=14, fontweight="bold", y=1.02)

    for ax, K in zip(axes, k_values):
        subset = df[df["K"] == K].copy()
        if subset.empty:
            ax.text(0.5, 0.5, f"K={K}\nNo data available",
                    ha="center", va="center", transform=ax.transAxes, fontsize=12)
            ax.set_title(f"K = {K}")
            continue

        # Map policy names to display labels
        subset["Policy"] = subset["policy"].map(POLICY_LABELS)
        subset = subset.dropna(subset=["Policy"])
        subset = subset.drop_duplicates(subset=["Policy", "capacity"])

        # Pivot to get policies (rows) × capacity (columns)
        pivot = subset.pivot_table(
            index="Policy",
            columns="capacity",
            values="response_time_mean",
            aggfunc="mean"
        )

        # Sort policies in order P0, P1, P2 (deduplicated)
        policy_order = list(dict.fromkeys(v for v in POLICY_LABELS.values() if v in pivot.index))
        pivot = pivot.reindex(policy_order)

        # Sort columns numerically
        pivot = pivot[sorted(pivot.columns)]

        print(f"\nHeatmap data for K={K}:")
        print(pivot.round(3))

        # Plot heatmap
        sns.heatmap(
            pivot,
            annot=True,
            fmt=".2f",
            cmap="YlOrRd",
            ax=ax,
            cbar_kws={"label": "Mean RT (min)"},
            linewidths=0.5,
            linecolor="white",
            vmin=pivot.values.min() - 0.1,
            vmax=pivot.values.max() + 0.1,
        )

        ax.set_title(f"K = {K}", fontsize=13, fontweight="bold")
        ax.set_xlabel("Capacity Limit (units/firehouse)", fontsize=11)
        if ax == axes[0]:
            ax.set_ylabel("Policy", fontsize=11)
        else:
            ax.set_ylabel("")

        # Rename capacity columns for clarity
        cap_labels = [f"cap={int(c)}" for c in sorted(pivot.columns)]
        ax.set_xticklabels(cap_labels, rotation=0)

    plt.tight_layout()

    output_path = FIGURES_DIR / "capacity_sensitivity_heatmap.png"
    fig.savefig(output_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"\nSaved: {output_path}")
    return output_path


def main():
    print("=" * 60)
    print("Generating Capacity Sensitivity Heatmap")
    print("=" * 60)

    df = load_simulation_data()
    output = create_heatmap(df, k_values=(20, 40))
    print(f"\nDone! Output: {output}")


if __name__ == "__main__":
    main()