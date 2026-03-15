#!/usr/bin/env python3
"""Analyse and visualise spatially-stratified P0 baseline policies.

Produces:
  results/figures/p0_spatial_map.png          – map of selected firehouses
  results/figures/p0_spatial_metrics.png       – bar chart comparison
  results/figures/p0_spatial_north_south.png   – north-south spacing profile
"""
import sys
from pathlib import Path

# Project imports
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from ems_readiness.optimization.policies import (
    spatial_stratification_analysis,
    _load_firehouses,
    _haversine_miles,
)

K = 20
FIGDIR = ROOT / "results" / "figures"
FIGDIR.mkdir(parents=True, exist_ok=True)

# ── Load data & run analysis ──────────────────────────────────────────
df = _load_firehouses()
results = spatial_stratification_analysis(K=K)

METHODS = ["latitude", "grid", "maximin"]
LABELS = {"latitude": "Latitude-Based", "grid": "Grid-Based", "maximin": "Maximin Distance"}
COLORS = {"latitude": "#1f77b4", "grid": "#2ca02c", "maximin": "#d62728"}

# ── Figure 1: Maps of selected firehouses ─────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(18, 10), sharey=True, sharex=True)
for ax, method in zip(axes, METHODS):
    selected = results[method]["selected"]
    sel_mask = df.index.isin(selected)

    # All firehouses (grey)
    ax.scatter(df.loc[~sel_mask, "Longitude"], df.loc[~sel_mask, "Latitude"],
               c="lightgrey", s=30, zorder=2, edgecolors="grey", linewidths=0.5,
               label="Not selected")
    # Selected (colour-coded by CBD)
    sel_df = df.loc[sel_mask]
    cbd_mask = sel_df["in_cbd"]
    ax.scatter(sel_df.loc[cbd_mask, "Longitude"], sel_df.loc[cbd_mask, "Latitude"],
               c=COLORS[method], s=100, zorder=3, edgecolors="black", linewidths=0.8,
               marker="s", label=f"Selected (CBD)")
    ax.scatter(sel_df.loc[~cbd_mask, "Longitude"], sel_df.loc[~cbd_mask, "Latitude"],
               c=COLORS[method], s=100, zorder=3, edgecolors="black", linewidths=0.8,
               marker="^", label=f"Selected (non-CBD)")

    ax.set_title(f"{LABELS[method]}\n({results[method]['n_cbd']} CBD / "
                 f"{results[method]['n_non_cbd']} non-CBD)", fontsize=12, fontweight="bold")
    ax.set_xlabel("Longitude")
    ax.legend(fontsize=8, loc="lower left")

axes[0].set_ylabel("Latitude")
fig.suptitle(f"P0 Spatial Stratification – K={K} Selected Firehouses", fontsize=15, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig(FIGDIR / "p0_spatial_map.png", dpi=150, bbox_inches="tight")
print(f"✓ Saved {FIGDIR / 'p0_spatial_map.png'}")

# ── Figure 2: Metric comparison bars ──────────────────────────────────
metrics = {
    "Mean NN Dist\n(miles)": [results[m]["mean_nn_dist"] for m in METHODS],
    "Lat Spacing Std\n(degrees)": [results[m]["coverage_std"] for m in METHODS],
    "% CBD": [results[m]["pct_cbd"] for m in METHODS],
}

fig, axes = plt.subplots(1, 3, figsize=(14, 5))
for ax, (metric_name, values) in zip(axes, metrics.items()):
    bars = ax.bar([LABELS[m] for m in METHODS], values,
                  color=[COLORS[m] for m in METHODS], edgecolor="black", linewidth=0.6)
    ax.set_title(metric_name, fontsize=12, fontweight="bold")
    ax.set_ylabel(metric_name.split("\n")[0])
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01 * max(values),
                f"{val:.3f}" if "Std" in metric_name else f"{val:.2f}",
                ha="center", va="bottom", fontsize=9)
    ax.tick_params(axis="x", rotation=25)

fig.suptitle(f"Spatial Distribution Metrics Comparison – K={K}", fontsize=14, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.93])
fig.savefig(FIGDIR / "p0_spatial_metrics.png", dpi=150, bbox_inches="tight")
print(f"✓ Saved {FIGDIR / 'p0_spatial_metrics.png'}")

# ── Figure 3: North-south latitude profile ────────────────────────────
fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
for ax, method in zip(axes, METHODS):
    selected = results[method]["selected"]
    sel_lats = np.sort(df.loc[selected, "Latitude"].values)
    all_lats = np.sort(df["Latitude"].values)

    # All firehouses as ticks
    ax.scatter(all_lats, np.zeros_like(all_lats), c="lightgrey", s=20,
               marker="|", zorder=1, label="All firehouses")
    # Selected
    ax.scatter(sel_lats, np.ones(len(sel_lats)) * 0.5, c=COLORS[method],
               s=80, marker="D", zorder=3, edgecolors="black", linewidths=0.5,
               label=f"Selected ({method})")

    # Show spacing arrows
    for i in range(len(sel_lats) - 1):
        ax.annotate("", xy=(sel_lats[i + 1], 0.3), xytext=(sel_lats[i], 0.3),
                     arrowprops=dict(arrowstyle="<->", color=COLORS[method], lw=1.2))

    ax.set_yticks([])
    ax.set_title(f"{LABELS[method]}", fontsize=11, fontweight="bold")
    ax.legend(fontsize=8, loc="upper left")
    ax.set_xlim(df["Latitude"].min() - 0.005, df["Latitude"].max() + 0.005)

axes[-1].set_xlabel("Latitude (South → North)", fontsize=11)
fig.suptitle(f"North-South Spacing Profile – K={K}", fontsize=14, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig(FIGDIR / "p0_spatial_north_south.png", dpi=150, bbox_inches="tight")
print(f"✓ Saved {FIGDIR / 'p0_spatial_north_south.png'}")

# ── Print summary table ───────────────────────────────────────────────
print("\n" + "=" * 70)
print(f"SPATIAL STRATIFICATION COMPARISON  (K = {K})")
print("=" * 70)
header = f"{'Method':<20} {'#Sel':>4} {'CBD':>4} {'Non-CBD':>7} {'%CBD':>6} {'MeanNN':>8} {'LatStd':>10}"
print(header)
print("-" * 70)
for m in METHODS:
    r = results[m]
    print(f"{LABELS[m]:<20} {r['n_selected']:>4} {r['n_cbd']:>4} {r['n_non_cbd']:>7} "
          f"{r['pct_cbd']:>5.1f}% {r['mean_nn_dist']:>8.4f} {r['coverage_std']:>10.6f}")
print("-" * 70)
print("\nMeanNN  = Mean nearest-neighbor distance (miles) — higher = better dispersion")
print("LatStd  = Std of latitude spacings (degrees) — lower = more uniform spacing")

# Total CBD in population
total_cbd = df["in_cbd"].sum()
print(f"\nPopulation: {len(df)} firehouses, {total_cbd} in CBD ({100*total_cbd/len(df):.1f}%)")
print("Done!")
