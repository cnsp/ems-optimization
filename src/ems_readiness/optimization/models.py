"""Optimization formulations for EMS unit allocation.

All formulations use PuLP and return a solved `pulp.LpProblem`.
Each public function has the signature:

    build_<name>(travel_time, demand, K, **kwargs) -> pulp.LpProblem

Parameters
----------
travel_time : pd.DataFrame
    Travel-time matrix (minutes).  Rows = firehouses, columns = precincts.
demand : pd.Series
    Demand weight per precinct (index = precinct id, values = lambda or crash count).
K : int
    Total number of EMS units to allocate.
capacity : int
    Maximum units any single firehouse can host.
"""
from __future__ import annotations

import pulp
import numpy as np
import pandas as pd
from typing import Dict, Optional


# ---------------------------------------------------------------------------
# A) Demand-Weighted Allocation  (minimise expected response time)
# ---------------------------------------------------------------------------
def build_demand_weighted(
    travel_time: pd.DataFrame,
    demand: pd.Series,
    K: int,
    capacity: int = 5,
    solver_time_limit: int = 300,
) -> pulp.LpProblem:
    """Minimise demand-weighted expected response time.

    Decision variables
    ------------------
    x_i  : integer, number of units at firehouse i
    y_ij : binary, 1 if precinct j is served by firehouse i

    Objective
    ---------
    min  sum_j  demand_j * sum_i  travel_time_ij * y_ij

    Constraints
    -----------
    sum_i x_i = K
    0 <= x_i <= capacity  (integer)
    sum_i y_ij = 1          for all j  (each precinct served by exactly one firehouse)
    y_ij <= x_i             (can only assign to an open firehouse)
    """
    firehouses = list(travel_time.index)
    precincts = [p for p in travel_time.columns if p in demand.index]

    prob = pulp.LpProblem("DemandWeighted_EMS_Allocation", pulp.LpMinimize)

    # Decision variables
    x = pulp.LpVariable.dicts("x", firehouses, lowBound=0, upBound=capacity, cat="Integer")
    y = pulp.LpVariable.dicts("y", ((i, j) for i in firehouses for j in precincts),
                              cat="Binary")

    # Objective
    prob += pulp.lpSum(
        demand[j] * travel_time.loc[i, j] * y[(i, j)]
        for j in precincts for i in firehouses
    ), "TotalDemandWeightedResponseTime"

    # Total units constraint
    prob += pulp.lpSum(x[i] for i in firehouses) == K, "TotalUnits"

    # Each precinct served by exactly one firehouse
    for j in precincts:
        prob += pulp.lpSum(y[(i, j)] for i in firehouses) == 1, f"Serve_{j}"

    # Linking: can only assign to a firehouse that has units
    for i in firehouses:
        for j in precincts:
            prob += y[(i, j)] <= x[i], f"Link_{i}_{j}"

    # Attach metadata for easy extraction
    prob._ems_meta = dict(firehouses=firehouses, precincts=precincts,
                          x=x, y=y, K=K, capacity=capacity)
    return prob


# ---------------------------------------------------------------------------
# B) P-Median Model
# ---------------------------------------------------------------------------
def build_p_median(
    travel_time: pd.DataFrame,
    demand: pd.Series,
    K: int,
    capacity: int = 5,
    solver_time_limit: int = 300,
) -> pulp.LpProblem:
    """Classic p-median: select K firehouses and assign precincts.

    Decision variables
    ------------------
    x_i  : binary, 1 if firehouse i is opened
    y_ij : binary, 1 if precinct j is served by firehouse i

    Objective
    ---------
    min  sum_j sum_i  demand_j * travel_time_ij * y_ij

    Constraints
    -----------
    sum_i x_i = K            (open exactly K firehouses)
    sum_i y_ij = 1           for all j
    y_ij <= x_i
    """
    firehouses = list(travel_time.index)
    precincts = [p for p in travel_time.columns if p in demand.index]

    prob = pulp.LpProblem("PMedian_EMS_Allocation", pulp.LpMinimize)

    x = pulp.LpVariable.dicts("x", firehouses, cat="Binary")
    y = pulp.LpVariable.dicts("y", ((i, j) for i in firehouses for j in precincts),
                              cat="Binary")

    prob += pulp.lpSum(
        demand[j] * travel_time.loc[i, j] * y[(i, j)]
        for j in precincts for i in firehouses
    ), "TotalDemandWeightedDistance"

    prob += pulp.lpSum(x[i] for i in firehouses) == K, "OpenKFirehouses"

    for j in precincts:
        prob += pulp.lpSum(y[(i, j)] for i in firehouses) == 1, f"Serve_{j}"

    for i in firehouses:
        for j in precincts:
            prob += y[(i, j)] <= x[i], f"Link_{i}_{j}"

    prob._ems_meta = dict(firehouses=firehouses, precincts=precincts,
                          x=x, y=y, K=K)
    return prob


# ---------------------------------------------------------------------------
# C) Maximal Coverage Model
# ---------------------------------------------------------------------------
def build_maximal_coverage(
    travel_time: pd.DataFrame,
    demand: pd.Series,
    K: int,
    capacity: int = 5,
    coverage_threshold: float = 8.0,
    solver_time_limit: int = 300,
) -> pulp.LpProblem:
    """Maximise demand-weighted coverage within a travel-time threshold.

    Decision variables
    ------------------
    x_i : integer, number of units at firehouse i
    z_j : binary, 1 if precinct j is covered

    Objective
    ---------
    max  sum_j  demand_j * z_j

    Constraints
    -----------
    sum_i x_i = K
    0 <= x_i <= capacity  (integer)
    z_j <= sum_i (x_i * a_ij)   where a_ij = 1 if travel_time_ij <= tau
    """
    firehouses = list(travel_time.index)
    precincts = [p for p in travel_time.columns if p in demand.index]

    # Coverage indicator matrix
    a = {}
    for i in firehouses:
        for j in precincts:
            a[(i, j)] = 1 if travel_time.loc[i, j] <= coverage_threshold else 0

    prob = pulp.LpProblem("MaxCoverage_EMS_Allocation", pulp.LpMaximize)

    x = pulp.LpVariable.dicts("x", firehouses, lowBound=0, upBound=capacity, cat="Integer")
    z = pulp.LpVariable.dicts("z", precincts, cat="Binary")

    # Objective: maximise covered demand
    prob += pulp.lpSum(demand[j] * z[j] for j in precincts), "TotalCoveredDemand"

    # Total units
    prob += pulp.lpSum(x[i] for i in firehouses) == K, "TotalUnits"

    # Coverage linking
    for j in precincts:
        prob += z[j] <= pulp.lpSum(x[i] * a[(i, j)] for i in firehouses), f"Cover_{j}"

    prob._ems_meta = dict(firehouses=firehouses, precincts=precincts,
                          x=x, z=z, a=a, K=K, capacity=capacity,
                          coverage_threshold=coverage_threshold)
    return prob


# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------
def extract_allocation(prob: pulp.LpProblem) -> pd.Series:
    """Return firehouse -> units allocation from a solved problem."""
    meta = prob._ems_meta
    x = meta["x"]
    alloc = {i: int(round(x[i].varValue or 0)) for i in meta["firehouses"]}
    return pd.Series(alloc, name="units_allocated")


def extract_assignments(prob: pulp.LpProblem) -> Dict[str, str]:
    """Return precinct -> firehouse assignment from demand-weighted / p-median."""
    meta = prob._ems_meta
    y = meta["y"]
    assignments = {}
    for j in meta["precincts"]:
        for i in meta["firehouses"]:
            if y[(i, j)].varValue and y[(i, j)].varValue > 0.5:
                assignments[j] = i
                break
    return assignments


def extract_coverage(prob: pulp.LpProblem) -> pd.Series:
    """Return precinct -> covered (bool) from a maximal-coverage solution."""
    meta = prob._ems_meta
    z = meta["z"]
    cov = {j: bool(round(z[j].varValue or 0)) for j in meta["precincts"]}
    return pd.Series(cov, name="covered")
