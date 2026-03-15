"""EMS Readiness – Optimization sub-package.

Modules
-------
models     – LP / MIP formulations (demand-weighted, p-median, maximal-coverage,
             CBD-focused demand-weighted, CBD-focused coverage)
allocator  – High-level interface that loads data, builds models, and solves
policies   – Baseline (non-optimized) allocation policies
"""

from .allocator import EMSAllocator          # noqa: F401
from .policies import (                     # noqa: F401
    uniform_allocation,
    demand_proportional_allocation,
    spatially_stratified_allocation,
    spatial_stratification_analysis,
)
from .models import (                        # noqa: F401
    build_cbd_focused_demand_weighted,
    build_cbd_focused_coverage,
)
