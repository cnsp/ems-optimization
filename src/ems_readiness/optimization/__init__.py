"""EMS Readiness – Optimization sub-package.

Modules
-------
models     – LP / MIP formulations (demand-weighted, p-median, maximal-coverage)
allocator  – High-level interface that loads data, builds models, and solves
policies   – Baseline (non-optimized) allocation policies
"""

from .allocator import EMSAllocator          # noqa: F401
from .policies import uniform_allocation, demand_proportional_allocation  # noqa: F401
