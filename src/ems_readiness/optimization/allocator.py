"""High-level EMS Allocator – loads data, builds models, solves, reports.

Usage
-----
>>> allocator = EMSAllocator.from_project(project_root="/path/to/ems-optimization")
>>> result = allocator.solve(model="demand_weighted", K=40)
>>> print(result.allocation)
>>> print(result.objective_value)
"""
from __future__ import annotations

import pathlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

import numpy as np
import pandas as pd
import pulp
import yaml

from ems_readiness.service.travel_time import build_travel_time_matrix
from . import models, policies


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------
@dataclass
class AllocationResult:
    """Container for optimisation results."""
    model_name: str
    K: int
    status: str
    objective_value: float
    allocation: pd.Series                       # firehouse -> units
    assignments: Optional[Dict[str, str]] = None  # precinct -> firehouse (if applicable)
    coverage: Optional[pd.Series] = None         # precinct -> bool (maximal-coverage)
    solve_time_sec: float = 0.0
    meta: Dict[str, Any] = field(default_factory=dict)

    # Convenience -----------------------------------------------------------
    @property
    def active_firehouses(self) -> int:
        return int((self.allocation > 0).sum())

    @property
    def units_deployed(self) -> int:
        return int(self.allocation.sum())

    def summary(self) -> pd.DataFrame:
        """One-row summary DataFrame."""
        row = {
            "model": self.model_name,
            "K": self.K,
            "status": self.status,
            "objective": round(self.objective_value, 4),
            "active_firehouses": self.active_firehouses,
            "units_deployed": self.units_deployed,
        }
        if self.coverage is not None:
            row["precincts_covered"] = int(self.coverage.sum())
            row["precincts_total"] = len(self.coverage)
        return pd.DataFrame([row])


# ---------------------------------------------------------------------------
# Allocator class
# ---------------------------------------------------------------------------
class EMSAllocator:
    """End-to-end optimisation interface."""

    MODEL_BUILDERS = {
        "demand_weighted": models.build_demand_weighted,
        "p_median":        models.build_p_median,
        "maximal_coverage": models.build_maximal_coverage,
    }

    def __init__(
        self,
        distance_matrix: pd.DataFrame,
        demand: pd.Series,
        config: Dict[str, Any],
        travel_speed_mph: float = 20.0,
    ):
        self.distance_matrix = distance_matrix
        self.demand = demand
        self.config = config
        self.travel_speed_mph = travel_speed_mph

        # Build travel-time matrix (minutes)
        self.travel_time = build_travel_time_matrix(
            distance_matrix, speed_mph=travel_speed_mph
        )

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------
    @classmethod
    def from_project(
        cls,
        project_root: str | pathlib.Path = ".",
    ) -> "EMSAllocator":
        """Load data and config from the standard project layout."""
        root = pathlib.Path(project_root)

        # Distance matrix
        dm = pd.read_csv(
            root / "data" / "processed" / "distance_matrix_firehouse_precinct.csv",
            index_col=0,
        )
        # Ensure columns are strings for consistent indexing
        dm.columns = dm.columns.astype(str)

        # Demand
        dl = pd.read_csv(root / "data" / "processed" / "demand_lambda_precinct.csv")
        demand = dl.set_index(dl["precinct"].astype(str))["crash_rate_per_hour"]
        demand.index.name = None
        demand.name = "demand"

        # Optimisation config
        cfg_path = root / "configs" / "optimization.yaml"
        if cfg_path.exists():
            with open(cfg_path) as f:
                config = yaml.safe_load(f)
        else:
            config = {}

        # Service config (for travel speed)
        svc_path = root / "configs" / "service.yaml"
        speed = 20.0
        if svc_path.exists():
            with open(svc_path) as f:
                svc = yaml.safe_load(f)
            speed = svc.get("travel_time", {}).get("average_speed_mph", 20.0)

        return cls(dm, demand, config, travel_speed_mph=speed)

    # ------------------------------------------------------------------
    # Solve
    # ------------------------------------------------------------------
    def solve(
        self,
        model: str = "demand_weighted",
        K: Optional[int] = None,
        capacity: Optional[int] = None,
        coverage_threshold: Optional[float] = None,
        solver_time_limit: int = 300,
        solver: Optional[pulp.LpSolver] = None,
    ) -> AllocationResult:
        """Build and solve an optimisation model.

        Parameters
        ----------
        model : str
            One of 'demand_weighted', 'p_median', 'maximal_coverage'.
        K : int, optional
            Total units.  Falls back to config then 40.
        capacity : int, optional
            Per-firehouse cap.  Falls back to config then 5.
        coverage_threshold : float, optional
            Minutes threshold for maximal-coverage model.
        solver_time_limit : int
            Seconds limit for the MIP solver.
        solver : pulp.LpSolver, optional
            Custom solver instance.  Default: CBC.
        """
        import time

        if model not in self.MODEL_BUILDERS:
            raise ValueError(f"Unknown model '{model}'. Choose from {list(self.MODEL_BUILDERS)}")

        cfg = self.config
        K = K or cfg.get("default_K") or 40
        capacity = capacity or cfg.get("firehouse_capacity", 5)
        coverage_threshold = coverage_threshold or cfg.get("coverage_threshold_minutes", 8.0)

        builder = self.MODEL_BUILDERS[model]
        kwargs = dict(
            travel_time=self.travel_time,
            demand=self.demand,
            K=K,
            capacity=capacity,
            solver_time_limit=solver_time_limit,
        )
        if model == "maximal_coverage":
            kwargs["coverage_threshold"] = coverage_threshold

        prob = builder(**kwargs)

        if solver is None:
            solver = pulp.PULP_CBC_CMD(msg=0, timeLimit=solver_time_limit)

        t0 = time.time()
        prob.solve(solver)
        solve_time = time.time() - t0

        status = pulp.LpStatus[prob.status]
        obj = pulp.value(prob.objective) if prob.objective else float("nan")

        alloc = models.extract_allocation(prob)
        assignments = None
        coverage = None
        if model in ("demand_weighted", "p_median"):
            assignments = models.extract_assignments(prob)
        if model == "maximal_coverage":
            coverage = models.extract_coverage(prob)

        return AllocationResult(
            model_name=model,
            K=K,
            status=status,
            objective_value=obj,
            allocation=alloc,
            assignments=assignments,
            coverage=coverage,
            solve_time_sec=round(solve_time, 3),
        )

    # ------------------------------------------------------------------
    # Baseline policies (no solver)
    # ------------------------------------------------------------------
    def baseline_uniform(self, K: int = 40, capacity: int = 5) -> AllocationResult:
        alloc = policies.uniform_allocation(
            self.travel_time.index, K, capacity
        )
        obj = self._evaluate_response_time(alloc)
        return AllocationResult(
            model_name="uniform", K=K, status="Baseline",
            objective_value=obj, allocation=alloc,
        )

    def baseline_demand_proportional(self, K: int = 40, capacity: int = 5) -> AllocationResult:
        alloc = policies.demand_proportional_allocation(
            self.travel_time, self.demand, K, capacity
        )
        obj = self._evaluate_response_time(alloc)
        return AllocationResult(
            model_name="demand_proportional", K=K, status="Baseline",
            objective_value=obj, allocation=alloc,
        )

    # ------------------------------------------------------------------
    # Evaluation helpers
    # ------------------------------------------------------------------
    def _evaluate_response_time(self, allocation: pd.Series) -> float:
        """Compute demand-weighted average response time for an allocation.

        Each precinct is served by the nearest firehouse that has >= 1 unit.
        """
        active = allocation[allocation > 0].index
        if len(active) == 0:
            return float("inf")

        precincts = [p for p in self.travel_time.columns if p in self.demand.index]
        tt_sub = self.travel_time.loc[active, precincts]
        min_tt = tt_sub.min(axis=0)  # nearest active firehouse per precinct
        weighted = (min_tt * self.demand[precincts]).sum()
        return float(weighted)

    def evaluate_coverage(
        self, allocation: pd.Series, threshold: float = 8.0
    ) -> Dict[str, Any]:
        """Evaluate coverage statistics for a given allocation."""
        active = allocation[allocation > 0].index
        precincts = [p for p in self.travel_time.columns if p in self.demand.index]
        if len(active) == 0:
            return {"covered": 0, "total": len(precincts), "pct": 0.0}

        tt_sub = self.travel_time.loc[active, precincts]
        min_tt = tt_sub.min(axis=0)
        covered = (min_tt <= threshold).sum()
        total_demand = self.demand[precincts].sum()
        covered_demand = self.demand[precincts][min_tt <= threshold].sum()

        return {
            "covered_precincts": int(covered),
            "total_precincts": len(precincts),
            "pct_precincts": round(100 * covered / len(precincts), 1),
            "covered_demand_pct": round(100 * covered_demand / total_demand, 1) if total_demand else 0.0,
        }

    # ------------------------------------------------------------------
    # Batch comparison
    # ------------------------------------------------------------------
    def compare_models(
        self,
        K: int = 40,
        capacity: int = 5,
        coverage_threshold: float = 8.0,
        models_to_run: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """Run all models (+ baselines) for a given K and return a comparison table."""
        if models_to_run is None:
            models_to_run = ["uniform", "demand_proportional",
                             "demand_weighted", "p_median", "maximal_coverage"]

        rows = []
        for m in models_to_run:
            if m == "uniform":
                res = self.baseline_uniform(K, capacity)
            elif m == "demand_proportional":
                res = self.baseline_demand_proportional(K, capacity)
            else:
                res = self.solve(m, K, capacity, coverage_threshold)

            cov = self.evaluate_coverage(res.allocation, coverage_threshold)
            row = {
                "model": m,
                "K": K,
                "status": res.status,
                "objective": round(res.objective_value, 4),
                "active_firehouses": res.active_firehouses,
                "units_deployed": res.units_deployed,
                "solve_time_sec": res.solve_time_sec,
                **cov,
            }
            rows.append(row)

        return pd.DataFrame(rows)
