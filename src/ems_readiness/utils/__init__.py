"""Utility functions for EMS readiness optimization.

Provides distance calculations, reproducibility helpers, and
other shared utilities.
"""

from ems_readiness.utils.distance import (
    build_distance_matrix,
    haversine,
    manhattan_distance,
)
from ems_readiness.utils.reproducibility import SeedManager
