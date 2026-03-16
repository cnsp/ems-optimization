#!/usr/bin/env python3
"""
Generate Precinct Demand Visualizations
========================================

Produces two complementary figures for the EMS Readiness Optimization project:

1. **Improved bar chart** (`precinct_demand_rates_improved.png`)
   - Horizontal bars coloured by demand tier (High / Medium / Low)
   - Explicit legend, threshold annotations, and prominent median line

2. **Spatial heatmap** (`precinct_demand_heatmap.png`)
   - Manhattan precinct polygons shaded by daily crash rate
   - Precinct labels, colour bar, and geographic context

Colour‐tier definitions
-----------------------
* **High (red)**   — top 25 % of precincts by daily crash rate  (≥ Q75)
* **Medium (blue)** — middle 50 %                                (Q25–Q75)
* **Low (green)**  — bottom 25 %                                 (< Q25)

Usage
-----
    python scripts/generate_precinct_demand_visualizations.py

Outputs are saved to ``results/figures/``.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as patheffects
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATA_RAW = PROJECT_ROOT / "data" / "raw"
FIGURES_DIR = PROJECT_ROOT / "results" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Colours
# ---------------------------------------------------------------------------
RED = "#C0392B"
BLUE = "#5B8DBE"
GREEN = "#27AE60"
MEDIAN_COLOUR = "#E67E22"

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

def load_demand() -> pd.DataFrame:
    """Load precinct demand data and compute daily crash rate."""
    df = pd.read_csv(DATA_PROCESSED / "demand_lambda_precinct.csv")
    df["crashes_per_day"] = df["crash_rate_per_hour"] * 24
    return df.sort_values("crashes_per_day", ascending=True).reset_index(drop=True)


def classify_tiers(df: pd.DataFrame) -> pd.DataFrame:
    """Add a 'tier' column based on quartile thresholds."""
    q75 = df["crashes_per_day"].quantile(0.75)
    q25 = df["crashes_per_day"].quantile(0.25)
    df["tier"] = "Medium"
    df.loc[df["crashes_per_day"] >= q75, "tier"] = "High"
    df.loc[df["crashes_per_day"] < q25, "tier"] = "Low"
    df["q75"] = q75
    df["q25"] = q25
    return df


TIER_COLOURS = {"High": RED, "Medium": BLUE, "Low": GREEN}

# ---------------------------------------------------------------------------
# Figure 1: Improved bar chart
# ---------------------------------------------------------------------------

def generate_bar_chart(df: pd.DataFrame) -> Path:
    """Create an improved horizontal bar chart with legend and annotations."""
    fig, ax = plt.subplots(figsize=(14, 8))

    q75 = df["q75"].iloc[0]
    q25 = df["q25"].iloc[0]
    median_val = df["crashes_per_day"].median()

    y_pos = np.arange(len(df))
    colours = [TIER_COLOURS[t] for t in df["tier"]]

    bars = ax.barh(y_pos, df["crashes_per_day"].values, color=colours, alpha=0.85,
                   edgecolor="white", linewidth=0.5)

    # Precinct labels
    ax.set_yticks(y_pos)
    ax.set_yticklabels([f"Pct {int(p)}" for p in df["precinct"].values], fontsize=9)

    # Median line
    ax.axvline(x=median_val, color=MEDIAN_COLOUR, linestyle="--", linewidth=2.5,
               label=f"Median: {median_val:.1f} crashes/day", zorder=5)

    # Q75 threshold line
    ax.axvline(x=q75, color=RED, linestyle=":", linewidth=1.5, alpha=0.6)
    ax.annotate(f"Q75 = {q75:.1f}", xy=(q75, len(df) - 1), xytext=(q75 + 0.3, len(df) - 0.5),
                fontsize=8, color=RED, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=RED, lw=0.8))

    # Q25 threshold line
    ax.axvline(x=q25, color=GREEN, linestyle=":", linewidth=1.5, alpha=0.6)
    ax.annotate(f"Q25 = {q25:.1f}", xy=(q25, 1), xytext=(q25 + 0.5, 2.5),
                fontsize=8, color=GREEN, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=GREEN, lw=0.8))

    # Value labels on bars
    for i, v in enumerate(df["crashes_per_day"].values):
        ax.text(v + 0.08, i, f"{v:.1f}", va="center", fontsize=7.5, color="#333")

    # Legend
    legend_patches = [
        mpatches.Patch(facecolor=RED, edgecolor="white", label=f"High demand (≥ Q75 = {q75:.1f}/day)  —  top 25%"),
        mpatches.Patch(facecolor=BLUE, edgecolor="white", label=f"Medium demand (Q25–Q75)  —  middle 50%"),
        mpatches.Patch(facecolor=GREEN, edgecolor="white", label=f"Low demand (< Q25 = {q25:.1f}/day)  —  bottom 25%"),
        plt.Line2D([0], [0], color=MEDIAN_COLOUR, linewidth=2.5, linestyle="--",
                   label=f"Median: {median_val:.1f} crashes/day"),
    ]
    ax.legend(handles=legend_patches, loc="lower right", fontsize=9, framealpha=0.95,
              title="Demand Tier (by quartile)", title_fontsize=10)

    ax.set_xlabel("Crashes per Day", fontsize=12)
    ax.set_title("Precinct-Level Demand Rates — Manhattan (2012–2026)",
                 fontsize=14, fontweight="bold", pad=12)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.grid(axis="x", alpha=0.25)
    ax.set_xlim(0, df["crashes_per_day"].max() * 1.15)

    fig.tight_layout()
    out_path = FIGURES_DIR / "precinct_demand_rates_improved.png"
    fig.savefig(out_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {out_path}")
    return out_path


# ---------------------------------------------------------------------------
# Figure 2: Spatial heatmap
# ---------------------------------------------------------------------------

def generate_spatial_heatmap(df: pd.DataFrame) -> Path:
    """Create a choropleth heatmap of precinct demand over Manhattan."""
    try:
        import geopandas as gpd
        from shapely import wkt
    except ImportError:
        print("ERROR: geopandas and shapely are required for the spatial heatmap.")
        sys.exit(1)

    # Load precinct polygons
    precincts_raw = pd.read_csv(DATA_RAW / "Police_Precincts_20260223.csv")
    precincts_raw["geometry"] = precincts_raw["the_geom"].apply(wkt.loads)
    precincts_gdf = gpd.GeoDataFrame(precincts_raw, geometry="geometry", crs="EPSG:4326")

    # Load Manhattan boundary for clipping
    manhattan = gpd.read_file(DATA_RAW / "manhattan_boundary.geojson")

    # Spatial join to keep only Manhattan precincts
    manhattan_precincts = gpd.sjoin(precincts_gdf, manhattan, predicate="intersects")
    manhattan_precincts = manhattan_precincts.drop_duplicates(subset=["Precinct"])

    # Merge demand data
    merged = manhattan_precincts.merge(
        df[["precinct", "crashes_per_day", "tier"]],
        left_on="Precinct", right_on="precinct", how="left"
    )
    # Fill missing (precincts with no demand data) with 0
    merged["crashes_per_day"] = merged["crashes_per_day"].fillna(0)
    merged["tier"] = merged["tier"].fillna("Low")

    # Clip geometries to Manhattan boundary for clean edges
    merged_clipped = gpd.overlay(merged, manhattan, how="intersection")

    # Plot
    fig, ax = plt.subplots(figsize=(10, 14))

    # Manhattan outline for context
    manhattan.boundary.plot(ax=ax, linewidth=1.5, color="#333", zorder=1)

    # Choropleth
    merged_clipped.plot(
        column="crashes_per_day",
        cmap="RdYlGn_r",
        linewidth=0.8,
        edgecolor="#555",
        ax=ax,
        legend=False,
        zorder=2,
    )

    # Colour bar
    vmin = 0
    vmax = merged_clipped["crashes_per_day"].max()
    sm = plt.cm.ScalarMappable(
        cmap="RdYlGn_r",
        norm=plt.Normalize(vmin=vmin, vmax=vmax),
    )
    sm._A = []
    cbar = fig.colorbar(sm, ax=ax, fraction=0.025, pad=0.02, shrink=0.6)
    cbar.set_label("Crashes per Day", fontsize=11)

    # Add Q75 and Q25 markers on colour bar
    q75 = df["q75"].iloc[0]
    q25 = df["q25"].iloc[0]
    for val, label, color in [(q75, "Q75", RED), (q25, "Q25", GREEN)]:
        cbar.ax.axhline(y=val, color=color, linewidth=2, linestyle="--")
        cbar.ax.text(1.3, val, f" {label}={val:.1f}", va="center", fontsize=8,
                     color=color, fontweight="bold", transform=cbar.ax.get_yaxis_transform())

    # Precinct labels — use unclipped centroids for label placement
    for _, row in merged.iterrows():
        centroid = row.geometry.centroid
        pct = int(row["Precinct"])
        rate = row["crashes_per_day"]
        ax.annotate(
            f"{pct}",
            xy=(centroid.x, centroid.y),
            ha="center", va="center",
            fontsize=7, fontweight="bold",
            color="white",
            path_effects=[
                patheffects.withStroke(linewidth=2.5, foreground="black")
            ],
            zorder=4,
        )

    # Load and display CBD boundary for context
    try:
        cbd = gpd.read_file(DATA_RAW / "cbd_boundary.geojson")
        cbd.boundary.plot(ax=ax, linewidth=2, color="#E67E22", linestyle="--",
                          label="CBD boundary", zorder=3)
        ax.legend(loc="upper left", fontsize=9, framealpha=0.9)
    except Exception:
        pass  # CBD boundary is optional context

    ax.set_title("Precinct Demand Heatmap — Manhattan\nCrashes per Day by Precinct (2012–2026)",
                 fontsize=14, fontweight="bold", pad=12)
    ax.set_axis_off()

    fig.tight_layout()
    out_path = FIGURES_DIR / "precinct_demand_heatmap.png"
    fig.savefig(out_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {out_path}")
    return out_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("Generating Precinct Demand Visualizations")
    print("=" * 60)

    df = load_demand()
    df = classify_tiers(df)

    print(f"\nLoaded {len(df)} precincts")
    print(f"  Q25 threshold: {df['q25'].iloc[0]:.2f} crashes/day")
    print(f"  Q75 threshold: {df['q75'].iloc[0]:.2f} crashes/day")
    print(f"  Median:        {df['crashes_per_day'].median():.2f} crashes/day")
    print(f"  High-demand precincts:   {(df['tier'] == 'High').sum()}")
    print(f"  Medium-demand precincts: {(df['tier'] == 'Medium').sum()}")
    print(f"  Low-demand precincts:    {(df['tier'] == 'Low').sum()}")

    print("\n--- Bar Chart ---")
    generate_bar_chart(df)

    print("\n--- Spatial Heatmap ---")
    generate_spatial_heatmap(df)

    print("\nDone.")


if __name__ == "__main__":
    main()
