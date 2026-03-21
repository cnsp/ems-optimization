# capacity_comparison/ — ✅ CURRENT (Capacity Sweep)

Full capacity sensitivity analysis across cap={1,2,3,4,5} × K={20,30,40} × {P0, P0_spatial, P1, P2}.

## Key Files
- `simulation_results.csv` — Full results for K=20 sweep
- `simulation_results_K30.csv` — Full results for K=30 sweep
- `full_comparison.csv` — Combined comparison
- `optimal_configurations.csv` — Best configs identified

## Naming Convention for Allocations
- `allocation_P0_spatial_K*_cap*.csv` — ✅ Canonical spatially-stratified P0
- `allocation_P0_K*_cap*.csv` — 📊 Legacy index-based P0 (included for comparison only)
- `allocation_P1_demand_K*_cap*.csv` — ✅ P1 demand-proportional
- `allocation_P2_optimised_K*_cap*.csv` — ✅ P2 optimized

> **Note**: `P0` without `_spatial` = deprecated index-based P0. For the canonical baseline, use `P0_spatial` files.
