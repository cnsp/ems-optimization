"""Baseline (non-optimised) allocation policies.

These do *not* require a solver and serve as reference benchmarks.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Optional


def uniform_allocation(
    firehouses: pd.Index,
    K: int,
    capacity: int = 5,
) -> pd.Series:
    """P0 – Uniform allocation: distribute K units as evenly as possible.

    Any remainder after integer division is distributed round-robin
    (first firehouses get one extra unit each).

    Parameters
    ----------
    firehouses : pd.Index
        Firehouse identifiers.
    K : int
        Total number of units.
    capacity : int
        Maximum units per firehouse.

    Returns
    -------
    pd.Series
        Firehouse -> number of units.
    """
    n = len(firehouses)
    base = min(K // n, capacity)
    remainder = K - base * n

    alloc = np.full(n, base, dtype=int)
    # distribute remainder one-by-one respecting capacity
    idx = 0
    while remainder > 0 and idx < n:
        if alloc[idx] < capacity:
            alloc[idx] += 1
            remainder -= 1
        idx += 1

    return pd.Series(alloc, index=firehouses, name="units_allocated")


def demand_proportional_allocation(
    travel_time: pd.DataFrame,
    demand: pd.Series,
    K: int,
    capacity: int = 5,
) -> pd.Series:
    """P1 – Demand-proportional allocation.

    Each firehouse receives units proportional to the total demand it is
    *nearest* to (i.e., for each precinct, credit goes to the closest
    firehouse).  The raw proportions are then scaled to sum to K and
    rounded to integers, respecting capacity constraints.

    Parameters
    ----------
    travel_time : pd.DataFrame
        Travel-time matrix (rows = firehouses, columns = precincts).
    demand : pd.Series
        Demand per precinct.
    K : int
        Total number of units.
    capacity : int
        Maximum units per firehouse.

    Returns
    -------
    pd.Series
        Firehouse -> number of units.
    """
    firehouses = travel_time.index
    precincts = [p for p in travel_time.columns if p in demand.index]

    # Credit demand to nearest firehouse
    credit = pd.Series(0.0, index=firehouses)
    for j in precincts:
        nearest = travel_time[j].idxmin()
        credit[nearest] += demand[j]

    # Proportional scaling
    total_credit = credit.sum()
    if total_credit == 0:
        return uniform_allocation(firehouses, K, capacity)

    raw = (credit / total_credit) * K

    # Integer rounding with capacity enforcement
    alloc = np.floor(raw).astype(int)
    alloc = np.minimum(alloc, capacity)
    remainder = K - alloc.sum()

    # Distribute remainder by largest fractional part
    fracs = raw - alloc
    order = fracs.sort_values(ascending=False).index
    for fh in order:
        if remainder <= 0:
            break
        if alloc[fh] < capacity:
            alloc[fh] += 1
            remainder -= 1

    return pd.Series(alloc, index=firehouses, name="units_allocated")
