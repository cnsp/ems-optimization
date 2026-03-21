#!/usr/bin/env python3
"""Capacity Sensitivity Analysis at K=30.

Runs simulation for K=30 across capacities 1, 2, 3, 5 and all 3 policies.
Appends results to results/analysis/capacity_comparison/simulation_results.csv
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import numpy as np
import pandas as pd
import pulp
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from ems_readiness.optimization import models, policies
from ems_readiness.service.travel_time import build_travel_time_matrix
from ems_readiness.simulation.runner import BatchRunner

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s  %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("cap_K30")

K = 30
CAPACITY_VALUES = [1, 2, 3, 5]
NUM_REPLICATIONS = 15
HORIZON_HOURS = 168
SEED_BASE = 42
OUTPUT_DIR = PROJECT_ROOT / "results" / "capacity_comparison"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_data():
    dm = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "distance_matrix_firehouse_precinct.csv", index_col=0)
    dm.columns = dm.columns.astype(str)
    dl = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "demand_lambda_precinct.csv")
    demand = dl.set_index(dl["precinct"].astype(str))["lambda_per_hour" if "lambda_per_hour" in dl.columns else "crash_rate_per_hour"]
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


def generate_allocations(tt, demand, capacity, fh_df):
    results = {}
    log.info(f"  P0 (spatially-stratified, maximin) K={K}, capacity={capacity}")
    alloc_p0 = policies.spatially_stratified_allocation(
        K=K, method="maximin", capacity=capacity,
        data_dir=PROJECT_ROOT / "data" / "processed",
    )
    results["P0"] = alloc_p0

    log.info(f"  P1 (demand-proportional) K={K}, capacity={capacity}")
    alloc_p1 = policies.demand_proportional_allocation(
        travel_time=tt, demand=demand, K=K, capacity=capacity,
    )
    results["P1_demand"] = alloc_p1

    log.info(f"  P2 (demand-weighted opt) K={K}, capacity={capacity}")
    prob = models.solve_model("demand_weighted", tt, demand, K=K, capacity=capacity)
    alloc_p2 = models.extract_allocation(prob)
    results["P2_optimised"] = alloc_p2

    return results


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
        "total_units": int(alloc.sum()), "firehouses_used": n_active,
        "max_units_per_fh": max_units, "unit_std": round(unit_std, 3),
        "units_in_cbd": units_in_cbd, "units_outside_cbd": units_outside_cbd,
        "fh_in_cbd": fh_in_cbd, "fh_outside_cbd": fh_outside_cbd,
        "proxy_weighted_rt_min": round(weighted_rt, 3),
    }


def run_simulation(alloc, policy_name, capacity):
    runner = BatchRunner(project_root=str(PROJECT_ROOT), data_dir="data/processed")
    label = f"{policy_name}_K{K}_cap{capacity}"
    result = runner.run_scenario(
        policy_allocation=alloc, K=K, num_replications=NUM_REPLICATIONS,
        seed_base=SEED_BASE, horizon_hours=HORIZON_HOURS, policy_name=label, trace=False,
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
    if "response_time_p90" in sim_result:
        p90 = sim_result["response_time_p90"]["mean"]
        out["response_time_p95_approx"] = p90 * 1.05
    return out


def main():
    dm, demand, tt, speed, fh_df = load_data()
    all_rows = []

    for cap in CAPACITY_VALUES:
        log.info(f"=== K={K}, capacity={cap} ===")
        allocations = generate_allocations(tt, demand, cap, fh_df)

        for pname, alloc in allocations.items():
            # Save allocation
            alloc_file = OUTPUT_DIR / f"allocation_{pname}_K{K}_cap{cap}.csv"
            alloc.to_frame("units_allocated").to_csv(alloc_file)
            log.info(f"  Saved allocation: {alloc_file.name}")

            # Analyse allocation
            stats = analyse_allocation(alloc, fh_df, tt, demand)

            # Run simulation
            log.info(f"  Running simulation: {pname} K={K} cap={cap}...")
            sim_result = run_simulation(alloc, pname, cap)
            sim_metrics = extract_sim_metrics(sim_result)

            row = {**sim_metrics, "policy": pname, "capacity": cap, "K": K}
            all_rows.append(row)

            full_row = {**stats, **sim_metrics, "policy": pname, "capacity": cap, "K": K}
            log.info(f"  Mean RT: {sim_metrics.get('response_time_mean', 'N/A'):.3f}")

    # Save new results
    new_df = pd.DataFrame(all_rows)
    new_file = OUTPUT_DIR / "simulation_results_K30.csv"
    new_df.to_csv(new_file, index=False)
    log.info(f"Saved K=30 results to {new_file}")

    # Append to main simulation_results.csv
    main_file = OUTPUT_DIR / "simulation_results.csv"
    if main_file.exists():
        existing = pd.read_csv(main_file)
        # Remove any existing K=30 rows
        existing = existing[existing["K"] != K]
        combined = pd.concat([existing, new_df], ignore_index=True)
    else:
        combined = new_df
    combined.to_csv(main_file, index=False)
    log.info(f"Updated {main_file} (total rows: {len(combined)})")

    # Print summary
    print("\n=== K=30 Capacity Sensitivity Summary ===")
    summary = new_df[["policy", "capacity", "response_time_mean"]].copy()
    pivot = summary.pivot(index="capacity", columns="policy", values="response_time_mean")
    print(pivot.round(3).to_string())


if __name__ == "__main__":
    main()
