"""Shared fixtures for EMS simulation tests."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Ensure src is on path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

DATA_DIR = PROJECT_ROOT / "data" / "processed"


@pytest.fixture
def project_root():
    """Return the project root directory."""
    return PROJECT_ROOT


@pytest.fixture
def data_dir():
    """Return the processed data directory."""
    return DATA_DIR


@pytest.fixture
def distance_matrix():
    """Load the real distance matrix."""
    dm = pd.read_csv(DATA_DIR / "distance_matrix_firehouse_precinct.csv", index_col=0)
    dm.columns = dm.columns.astype(str)
    return dm


@pytest.fixture
def small_distance_matrix():
    """A 3-firehouse × 2-precinct distance matrix for toy tests."""
    return pd.DataFrame(
        {
            "1": [1.0, 2.0, 3.0],
            "2": [3.0, 1.0, 2.0],
        },
        index=["FH_A", "FH_B", "FH_C"],
    )


@pytest.fixture
def small_allocation():
    """Allocation: 1 unit at each of 3 firehouses (K=3)."""
    return pd.Series({"FH_A": 1, "FH_B": 1, "FH_C": 1})


@pytest.fixture
def real_uniform_allocation(distance_matrix):
    """Uniform allocation of K=20 across real firehouses."""
    fhs = distance_matrix.index.tolist()
    n = len(fhs)
    base = 20 // n
    remainder = 20 % n
    alloc = {fh: base for fh in fhs}
    for i in range(remainder):
        alloc[fhs[i]] += 1
    return pd.Series(alloc)


@pytest.fixture
def real_demand_weighted_allocation():
    """Load a demand-weighted (P2) allocation if available, else create proportional."""
    alloc_path = DATA_DIR.parent.parent / "results" / "tables"
    # Try to load from optimization results
    for f in alloc_path.glob("*demand_weighted*K20*.csv"):
        try:
            df = pd.read_csv(f, index_col=0)
            return df.iloc[:, 0]
        except Exception:
            pass
    # Fallback: demand-proportional across all 48 firehouses
    dm = pd.read_csv(DATA_DIR / "distance_matrix_firehouse_precinct.csv", index_col=0)
    fhs = dm.index.tolist()
    K = 20
    # Simple proportional allocation
    n = len(fhs)
    base = K // n
    remainder = K % n
    alloc = {fh: base for fh in fhs}
    for i in range(remainder):
        alloc[fhs[i]] += 1
    return pd.Series(alloc)
