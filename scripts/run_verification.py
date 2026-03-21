#!/usr/bin/env python3
"""Run verification scenarios and save results.

Scenarios:
1. Toy Example: K=2, 2 firehouses, 5 incidents, trace all events
2. Zero Demand: K=10, no arrivals, verify no activity
3. Single Unit: K=1, moderate demand, verify queue builds
4. Extreme Demand: K=5, very high arrival rate, verify stability
"""

import json
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from ems_readiness.simulation.engine import EMSSimulation

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

OUT_DIR = PROJECT_ROOT / "results" / "baseline" / "simulation" / "verification"
OUT_DIR.mkdir(parents=True, exist_ok=True)

dm = pd.read_csv(PROJECT_ROOT / "data/processed/distance_matrix_firehouse_precinct.csv", index_col=0)
dm.columns = dm.columns.astype(str)
all_fhs = dm.index.tolist()


def save_result(name, data):
    """Save verification result to JSON."""
    path = OUT_DIR / f"{name}.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    logger.info(f"Saved {path}")


# ── Scenario 1: Toy Example ─────────────────────────────────────

def run_toy_example():
    """K=2, 2 firehouses, ~5 incidents, trace all events."""
    logger.info("\n" + "=" * 60)
    logger.info("SCENARIO 1: Toy Example (K=2, 2 firehouses, trace mode)")
    logger.info("=" * 60)

    fh1, fh2 = all_fhs[0], all_fhs[1]
    alloc = pd.Series({fh1: 1, fh2: 1})

    sim = EMSSimulation(
        policy_allocation=alloc,
        seed=42,
        project_root=str(PROJECT_ROOT),
        trace=True,
    )

    # Use a controlled arrival generator for exactly ~5 incidents
    class ControlledGenerator:
        def generate_arrivals(self, n_hours=1, start_hour=0, dow=0, rng=42):
            # Generate exactly 5 arrivals at known times in known precincts
            return pd.DataFrame({
                "time_hours": [0.5, 1.0, 1.5, 2.0, 2.5],
                "hour": [0, 1, 1, 2, 2],
                "precinct": [1, 5, 1, 5, 1],
            })

    sim.arrival_gen = ControlledGenerator()

    # Enable detailed logging
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    logging.getLogger("ems_readiness.simulation.engine").addHandler(handler)
    logging.getLogger("ems_readiness.simulation.engine").setLevel(logging.INFO)

    sim.run(horizon_hours=4)
    results = sim.get_results()
    log = results["incident_log"]

    trace_data = {
        "scenario": "toy_example",
        "K": 2,
        "firehouses": [fh1, fh2],
        "total_incidents": results["summary"]["total_incidents"],
        "incidents_queued": results["summary"]["incidents_queued"],
        "event_trace": [],
    }

    for _, row in log.iterrows():
        trace_data["event_trace"].append({
            "incident_id": int(row["id"]),
            "arrival_time_h": round(row["arrival_time"], 4),
            "precinct": int(row["precinct"]),
            "assigned_unit": row["assigned_unit"],
            "assigned_firehouse": row["assigned_firehouse"],
            "dispatch_time_h": round(row["dispatch_time"], 4) if pd.notna(row["dispatch_time"]) else None,
            "service_start_h": round(row["service_start_time"], 4) if pd.notna(row["service_start_time"]) else None,
            "completion_h": round(row["completion_time"], 4) if pd.notna(row["completion_time"]) else None,
            "travel_time_min": round(row["travel_time_minutes"], 2) if pd.notna(row["travel_time_minutes"]) else None,
            "service_time_min": round(row["service_time_minutes"], 2) if pd.notna(row["service_time_minutes"]) else None,
            "response_time_min": round(row["response_time_minutes"], 2) if pd.notna(row["response_time_minutes"]) else None,
            "queued": bool(row["queued"]),
        })

    # Verify event ordering
    ordering_ok = True
    for evt in trace_data["event_trace"]:
        if evt["dispatch_time_h"] is not None:
            if evt["dispatch_time_h"] < evt["arrival_time_h"]:
                ordering_ok = False
        if evt["service_start_h"] is not None and evt["dispatch_time_h"] is not None:
            if evt["service_start_h"] < evt["dispatch_time_h"]:
                ordering_ok = False
        if evt["completion_h"] is not None and evt["service_start_h"] is not None:
            if evt["completion_h"] < evt["service_start_h"]:
                ordering_ok = False

    trace_data["event_ordering_valid"] = ordering_ok

    logger.info(f"\nToy Example Results:")
    logger.info(f"  Incidents: {trace_data['total_incidents']}")
    logger.info(f"  Queued: {trace_data['incidents_queued']}")
    logger.info(f"  Event ordering valid: {ordering_ok}")
    for evt in trace_data["event_trace"]:
        logger.info(f"  Incident #{evt['incident_id']}: "
                     f"arr={evt['arrival_time_h']:.3f}h, "
                     f"disp={evt['dispatch_time_h']}h, "
                     f"resp={evt['response_time_min']}min, "
                     f"queued={evt['queued']}")

    save_result("01_toy_example", trace_data)
    return trace_data


# ── Scenario 2: Zero Demand ─────────────────────────────────────

def run_zero_demand():
    """K=10, no arrivals, verify no activity."""
    logger.info("\n" + "=" * 60)
    logger.info("SCENARIO 2: Zero Demand (K=10, no arrivals)")
    logger.info("=" * 60)

    alloc = pd.Series({fh: 1 for fh in all_fhs[:10]})

    sim = EMSSimulation(
        policy_allocation=alloc,
        seed=42,
        project_root=str(PROJECT_ROOT),
    )

    class ZeroGenerator:
        def generate_arrivals(self, **kwargs):
            return pd.DataFrame(columns=["time_hours", "hour", "precinct"])

    sim.arrival_gen = ZeroGenerator()
    sim.run(horizon_hours=24)
    results = sim.get_results()

    data = {
        "scenario": "zero_demand",
        "K": 10,
        "horizon_hours": 24,
        "total_incidents": results["summary"]["total_incidents"],
        "all_units_idle": sim.unit_pool.count_available() == 10,
        "zero_utilization": all(
            u.total_busy_time == 0 for u in sim.unit_pool._all_units.values()
        ),
        "no_queue": results["summary"]["queue_length_max"] == 0,
    }

    logger.info(f"\nZero Demand Results:")
    logger.info(f"  Total incidents: {data['total_incidents']}")
    logger.info(f"  All units idle: {data['all_units_idle']}")
    logger.info(f"  Zero utilization: {data['zero_utilization']}")
    logger.info(f"  No queue: {data['no_queue']}")

    assert data["total_incidents"] == 0
    assert data["all_units_idle"]
    assert data["zero_utilization"]

    save_result("02_zero_demand", data)
    return data


# ── Scenario 3: Single Unit ─────────────────────────────────────

def run_single_unit():
    """K=1, moderate demand, verify queue builds."""
    logger.info("\n" + "=" * 60)
    logger.info("SCENARIO 3: Single Unit (K=1, moderate demand)")
    logger.info("=" * 60)

    alloc = pd.Series({all_fhs[0]: 1})

    sim = EMSSimulation(
        policy_allocation=alloc,
        seed=42,
        project_root=str(PROJECT_ROOT),
    )
    sim.run(horizon_hours=24)
    results = sim.get_results()
    s = results["summary"]
    unit = list(sim.unit_pool._all_units.values())[0]

    data = {
        "scenario": "single_unit",
        "K": 1,
        "firehouse": all_fhs[0],
        "horizon_hours": 24,
        "total_incidents": s["total_incidents"],
        "incidents_queued": s["incidents_queued"],
        "queue_fraction": round(s["queue_fraction"], 4),
        "queue_length_max": s["queue_length_max"],
        "queue_length_tw_avg": round(s["queue_length_tw_avg"], 2),
        "response_time_mean_min": round(s["response_time_mean"], 2),
        "response_time_p90_min": round(s["response_time_p90"], 2),
        "coverage_fraction": round(s["coverage_fraction"], 4),
        "unit_utilization": round(unit.total_busy_time / 24.0, 4),
    }

    logger.info(f"\nSingle Unit Results:")
    for k, v in data.items():
        logger.info(f"  {k}: {v}")

    assert data["incidents_queued"] > 0, "Expected queueing with 1 unit"
    assert data["queue_fraction"] > 0.5, "Most incidents should queue"
    assert data["unit_utilization"] > 0.8, "Unit should be busy most of the time"

    save_result("03_single_unit", data)
    return data


# ── Scenario 4: Extreme Demand ──────────────────────────────────

def run_extreme_demand():
    """K=5, very high arrival rate, verify stability."""
    logger.info("\n" + "=" * 60)
    logger.info("SCENARIO 4: Extreme Demand (K=5, high rate)")
    logger.info("=" * 60)

    alloc = pd.Series({fh: 1 for fh in all_fhs[:5]})

    sim = EMSSimulation(
        policy_allocation=alloc,
        seed=42,
        project_root=str(PROJECT_ROOT),
    )

    # 3x demand
    class HighRateGenerator:
        def __init__(self, original):
            self.original = original
        def generate_arrivals(self, n_hours=24, start_hour=0, dow=0, rng=42):
            df = self.original.generate_arrivals(n_hours=n_hours, start_hour=start_hour, dow=dow, rng=rng)
            if df.empty:
                return df
            dfs = []
            for offset in range(3):
                d = df.copy()
                d["time_hours"] = d["time_hours"] + offset * 0.005
                dfs.append(d)
            result = pd.concat(dfs, ignore_index=True).sort_values("time_hours").reset_index(drop=True)
            return result[result["time_hours"] < n_hours]

    sim.arrival_gen = HighRateGenerator(sim.arrival_gen)
    sim.run(horizon_hours=12)
    results = sim.get_results()
    s = results["summary"]

    data = {
        "scenario": "extreme_demand",
        "K": 5,
        "demand_multiplier": 3,
        "horizon_hours": 12,
        "total_incidents": s["total_incidents"],
        "incidents_queued": s["incidents_queued"],
        "queue_fraction": round(s["queue_fraction"], 4),
        "queue_length_max": s["queue_length_max"],
        "response_time_mean_min": round(s["response_time_mean"], 2),
        "response_time_p90_min": round(s["response_time_p90"], 2),
        "coverage_fraction": round(s["coverage_fraction"], 4),
        "simulation_completed": sim._completed,
        "metrics_consistent": (
            s["response_time_mean"] >= s["travel_time_mean"]
            and 0 <= s["coverage_fraction"] <= 1
            and 0 <= s["queue_fraction"] <= 1
        ),
    }

    logger.info(f"\nExtreme Demand Results:")
    for k, v in data.items():
        logger.info(f"  {k}: {v}")

    assert data["simulation_completed"], "Simulation should complete without error"
    assert data["metrics_consistent"], "Metrics should be internally consistent"

    save_result("04_extreme_demand", data)
    return data


if __name__ == "__main__":
    results = {}
    results["toy"] = run_toy_example()
    results["zero"] = run_zero_demand()
    results["single"] = run_single_unit()
    results["extreme"] = run_extreme_demand()

    logger.info("\n" + "=" * 60)
    logger.info("ALL VERIFICATION SCENARIOS COMPLETE")
    logger.info("=" * 60)
    for name, r in results.items():
        logger.info(f"  {name}: {r['scenario']} - OK")
