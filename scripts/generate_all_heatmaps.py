#!/usr/bin/env python3
"""Generate 108 Manhattan heat maps showing staging locations.

Combinations: 9 K values × 3 policies × 4 capacity levels = 108 maps.

K values: 5, 10, 15, 20, 25, 30, 35, 40, 45
Policies: P0-spatial, P1 (demand-proportional), P2 (demand-weighted optimisation)
Capacities: 1, 2, 3, 5

For each combination, generates the allocation if not already cached,
then produces a Manhattan heat map with staging location positions.

Output: results/heatmaps/heatmap_K{k}_policy{policy}_cap{capacity}.png
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import pulp
import yaml

# ── Project path setup ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from ems_readiness.optimization import models, policies
from ems_readiness.service.travel_time import build_travel_time_matrix

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("heatmaps")

# ── Configuration ────────────────────────────────────────────────────
K_VALUES = [5, 10, 15, 20, 25, 30, 35, 40, 45]
CAPACITY_VALUES = [1, 2, 3, 5]
POLICY_NAMES = ["P0-spatial", "P1", "P2"]  # display names
POLICY_INTERNAL = {
    "P0-spatial": "P0_spatial",
    "P1": "P1_demand",
    "P2": "P2_optimised",
}

ALLOC_DIR = PROJECT_ROOT / "results" / "heatmaps" / "allocations"
HEATMAP_DIR = PROJECT_ROOT / "results" / "heatmaps"
ALLOC_DIR.mkdir(parents=True, exist_ok=True)
HEATMAP_DIR.mkdir(parents=True, exist_ok=True)

# ── Load shared data ────────────────────────────────────────────────

def load_data():
    """Load distance matrix, demand, travel-time matrix, firehouse info, and Manhattan boundary."""
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

    # Firehouse info
    fh_df = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "firehouses_manhattan.csv")
    fh_df["in_cbd"] = fh_df["in_cbd"].astype(str).str.strip().str.lower() == "true"
    fh_df = fh_df.set_index("FacilityName")

    # Manhattan boundary
    manhattan_gdf = gpd.read_file(PROJECT_ROOT / "data" / "raw" / "manhattan_boundary.geojson")

    return dm, demand, tt, speed, fh_df, manhattan_gdf


def generate_allocation(policy_display: str, K: int, capacity: int,
                         tt, demand, fh_df) -> pd.Series:
    """Generate allocation for a given policy, K, and capacity."""
    internal = POLICY_INTERNAL[policy_display]

    if internal == "P0_spatial":
        alloc = policies.spatially_stratified_allocation(
            K=K, method="maximin", capacity=capacity,
            data_dir=PROJECT_ROOT / "data" / "processed",
        )
    elif internal == "P1_demand":
        alloc = policies.demand_proportional_allocation(
            travel_time=tt, demand=demand, K=K, capacity=capacity,
        )
    elif internal == "P2_optimised":
        prob = models.solve_model(
            "demand_weighted", tt, demand, K=K, capacity=capacity,
        )
        alloc = models.extract_allocation(prob)
    else:
        raise ValueError(f"Unknown policy: {internal}")

    return alloc


def try_load_existing_allocation(policy_display: str, K: int, capacity: int) -> pd.Series | None:
    """Try loading allocation from existing result files."""
    internal = POLICY_INTERNAL[policy_display]

    # Check capacity_comparison directory
    cap_file = PROJECT_ROOT / "results" / "capacity_comparison" / f"allocation_{internal}_K{K}_cap{capacity}.csv"
    if cap_file.exists():
        df = pd.read_csv(cap_file, index_col=0)
        return df.iloc[:, 0]

    # Check production_v2 (only cap=2)
    if capacity == 2:
        prod_file = PROJECT_ROOT / "results" / "production_v2" / "allocations" / f"allocations_K{K}.csv"
        if prod_file.exists():
            df = pd.read_csv(prod_file, index_col=0)
            col_map = {"P0-spatial": "P0-spatial", "P1": "P1", "P2": "P2"}
            col = col_map.get(policy_display)
            if col and col in df.columns:
                return df[col]

    return None


def get_allocation(policy_display: str, K: int, capacity: int,
                   tt, demand, fh_df) -> pd.Series:
    """Get allocation: load existing or generate new."""
    alloc = try_load_existing_allocation(policy_display, K, capacity)
    if alloc is not None:
        log.info(f"  Loaded existing: K={K}, {policy_display}, cap={capacity}")
        return alloc

    log.info(f"  Generating new:  K={K}, {policy_display}, cap={capacity}")
    alloc = generate_allocation(policy_display, K, capacity, tt, demand, fh_df)

    # Save for future use
    internal = POLICY_INTERNAL[policy_display]
    out_file = ALLOC_DIR / f"allocation_{internal}_K{K}_cap{capacity}.csv"
    alloc.to_frame("units_allocated").to_csv(out_file)

    return alloc


def create_heatmap(alloc: pd.Series, fh_df: pd.DataFrame, manhattan_gdf: gpd.GeoDataFrame,
                   K: int, policy_display: str, capacity: int, output_path: Path):
    """Create a Manhattan heat map showing staging location positions."""
    fig, ax = plt.subplots(1, 1, figsize=(8, 12))

    # Plot Manhattan boundary
    manhattan_gdf.plot(ax=ax, color="#f0f0f0", edgecolor="#333333", linewidth=1.2)

    # Prepare firehouse data with allocations
    active = alloc[alloc > 0]
    if len(active) == 0:
        ax.set_title(f"No active stations\nK={K}, {policy_display}, cap={capacity}", fontsize=13)
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return

    # Get coords for all firehouses
    fh_coords = fh_df[["Latitude", "Longitude"]].copy()

    # Inactive firehouses (small grey dots)
    inactive_fhs = [fh for fh in fh_coords.index if fh not in active.index]
    if inactive_fhs:
        inactive_df = fh_coords.loc[inactive_fhs]
        ax.scatter(
            inactive_df["Longitude"], inactive_df["Latitude"],
            s=12, c="#cccccc", marker="o", alpha=0.5, zorder=2,
            label="Inactive firehouses"
        )

    # Active firehouses - size proportional to units allocated
    active_df = fh_coords.loc[active.index].copy()
    active_df["units"] = active.values

    # Color by units: use a colormap
    max_units = int(active_df["units"].max())
    if max_units == 1:
        colors = ["#e74c3c"] * len(active_df)
    else:
        cmap = plt.cm.YlOrRd
        norm = plt.Normalize(vmin=1, vmax=max_units)
        colors = [cmap(norm(u)) for u in active_df["units"]]

    sizes = 30 + active_df["units"] * 50  # scale dot size by units

    scatter = ax.scatter(
        active_df["Longitude"], active_df["Latitude"],
        s=sizes, c=colors, edgecolors="black", linewidth=0.7,
        marker="o", zorder=3,
    )

    # Add colorbar if multiple unit levels
    if max_units > 1:
        sm = plt.cm.ScalarMappable(cmap=plt.cm.YlOrRd, norm=plt.Normalize(vmin=1, vmax=max_units))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, shrink=0.4, aspect=20, pad=0.02)
        cbar.set_label("Units allocated", fontsize=10)
        cbar.set_ticks(range(1, max_units + 1))

    # Title and labels
    n_active = len(active)
    total_units = int(active.sum())
    ax.set_title(
        f"EMS Staging Locations — K={K}, {policy_display}, Capacity={capacity}\n"
        f"{n_active} active stations, {total_units} total units",
        fontsize=13, fontweight="bold", pad=12
    )
    ax.set_xlabel("Longitude", fontsize=10)
    ax.set_ylabel("Latitude", fontsize=10)

    # Legend
    legend_elements = [
        mpatches.Patch(facecolor="#cccccc", edgecolor="#999", label="Inactive firehouses"),
        mpatches.Patch(facecolor="#e74c3c", edgecolor="black", label="Active staging locations"),
    ]
    ax.legend(handles=legend_elements, loc="lower left", fontsize=9, framealpha=0.9)

    # Set bounds with padding
    bounds = manhattan_gdf.total_bounds  # minx, miny, maxx, maxy
    pad_x = (bounds[2] - bounds[0]) * 0.05
    pad_y = (bounds[3] - bounds[1]) * 0.05
    ax.set_xlim(bounds[0] - pad_x, bounds[2] + pad_x)
    ax.set_ylim(bounds[1] - pad_y, bounds[3] + pad_y)

    ax.set_aspect("equal")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def main():
    log.info("Loading data...")
    dm, demand, tt, speed, fh_df, manhattan_gdf = load_data()

    total = len(K_VALUES) * len(POLICY_NAMES) * len(CAPACITY_VALUES)
    log.info(f"Generating {total} heat maps...")

    count = 0
    missing_log = []

    for K in K_VALUES:
        for policy in POLICY_NAMES:
            for cap in CAPACITY_VALUES:
                count += 1
                tag = f"[{count}/{total}] K={K}, {policy}, cap={cap}"
                log.info(tag)

                try:
                    alloc = get_allocation(policy, K, cap, tt, demand, fh_df)

                    # Map policy display name to filename-safe version
                    policy_file = policy.replace("-", "_")
                    fname = f"heatmap_K{K}_policy{policy_file}_cap{cap}.png"
                    output_path = HEATMAP_DIR / fname

                    create_heatmap(alloc, fh_df, manhattan_gdf, K, policy, cap, output_path)
                    log.info(f"  Saved: {fname}")

                except Exception as e:
                    log.error(f"  FAILED: {tag} — {e}")
                    missing_log.append({"K": K, "policy": policy, "capacity": cap, "error": str(e)})

    log.info(f"\nCompleted: {count - len(missing_log)}/{total} heat maps generated.")
    if missing_log:
        log.warning(f"Failed: {len(missing_log)} combinations:")
        for m in missing_log:
            log.warning(f"  K={m['K']}, {m['policy']}, cap={m['capacity']}: {m['error']}")
        # Save missing log
        pd.DataFrame(missing_log).to_csv(HEATMAP_DIR / "missing_combinations.csv", index=False)

    # Generate summary
    summary = {
        "total_expected": total,
        "total_generated": count - len(missing_log),
        "total_failed": len(missing_log),
        "K_values": K_VALUES,
        "policies": POLICY_NAMES,
        "capacity_values": CAPACITY_VALUES,
    }
    import json
    with open(HEATMAP_DIR / "generation_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    log.info(f"Summary saved to {HEATMAP_DIR / 'generation_summary.json'}")


if __name__ == "__main__":
    main()
