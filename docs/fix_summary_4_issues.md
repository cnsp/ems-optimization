# Fix Summary: 4 Critical Issues Resolved

## Issue 1: Pilot 1 — P2 Showed Worse RT Than P0 (CRITICAL)

**Problem:** `results/simulation/validation_pilot/pilot1_p0_vs_p2.json` showed P2 with 5.44 min mean RT, *worse* than P0 at 3.17 min — contradicting the entire optimization thesis.

**Root cause:** The validation pilot script used `EMSAllocator(project_root=...)` which was an invalid constructor call, causing it to silently fall back to a broken P2 allocation.

**Before:**
| Policy | Mean RT (min) | Coverage |
|--------|--------------|----------|
| P0     | 3.17         | 99.6%    |
| P2     | **5.44**     | **81.3%** |

**After (regenerated):**
| Policy | Mean RT (min) | Coverage |
|--------|--------------|----------|
| P0     | 3.20         | 99.5%    |
| P2     | **2.58**     | **99.6%** |

**Fix:** Corrected `make_p2_allocation()` to use `EMSAllocator.from_project()` and `result.allocation`. P2 now correctly dominates P0 by ~19%.

---

## Issue 2: policy_comparison.csv — max_units=5 Instead of capacity=2

**Problem:** `results/optimization/policy_comparison.csv` showed `max_units_at_firehouse=5` for K≥30, contradicting the capacity=2 decision (DEC-010).

**Root cause:** `scripts/run_optimization_comparison.py` hardcoded `CAPACITY = 5` instead of reading from config.

**Before:** (K=30 rows)
```
K=30, P2,  max_units_at_firehouse=5
K=30, P2b, max_units_at_firehouse=5
K=40, P2,  max_units_at_firehouse=5
K=48, P2,  max_units_at_firehouse=5
```

**After:** (all rows)
```
K=30, P2,  max_units_at_firehouse=2
K=30, P2b, max_units_at_firehouse=2
K=40, P2,  max_units_at_firehouse=2
K=48, P2,  max_units_at_firehouse=2
```

**Fix:** Changed `CAPACITY = 5` → `CAPACITY = 2` in the script and regenerated.

---

## Issue 3: exp2_pivot_rt.csv — Erratic P0 Without Legacy Label

**Problem:** `results/tables/exp2_pivot_rt.csv` had P0 values jumping erratically:
```
K=15: P0=9.48  (very high)
K=20: P0=3.17
K=25: P0=5.79  (jumps back up!)
K=30: P0=2.81
K=35: P0=3.27  (jumps again)
K=40: P0=2.45
```
This is the legacy index-based P0 (round-robin by firehouse list position), not the spatially-stratified P0. No label distinguished them.

**Root cause:** Production experiments used the legacy uniform allocation for P0 before the nomenclature migration (DEC-012).

**Before:**
```csv
K,P0,P1,P2
15,9.476,2.943,2.825
20,3.165,2.619,2.567
25,5.795,2.467,2.496
```

**After:**
```csv
K,P0,P1,P2
15,3.698,2.943,2.825
20,3.173,2.619,2.567
25,2.816,2.467,2.496
```

P0 now uses spatially-stratified allocation and decreases monotonically with K. Legacy P0 data retained as `P0_legacy` in `exp2_fleet_sensitivity.csv` and in a separate `exp2_pivot_rt_with_legacy.csv`.

---

## Issue 4: models.py — Function Defaults capacity=5

**Problem:** All optimization model functions in `src/ems_readiness/optimization/models.py` had `capacity: int = 5` as the default parameter, contradicting DEC-010 and `optimization.yaml` (which specifies `firehouse_capacity: 2`).

**Files changed:**
- `src/ems_readiness/optimization/models.py` — 6 functions: `build_demand_weighted`, `build_p_median`, `build_maximal_coverage`, `build_cbd_focused_demand_weighted`, `build_cbd_focused_coverage`, `solve_model`
- `src/ems_readiness/optimization/allocator.py` — `solve()`, `baseline_uniform()`, `baseline_demand_proportional()`, `compare_models()` + fallback default
- `src/ems_readiness/optimization/policies.py` — `uniform_allocation()`, `demand_proportional_allocation()`, `spatially_stratified_allocation()`
- `scripts/run_optimization_comparison.py` — `CAPACITY` constant

**Before:** `capacity: int = 5` (in all signatures)
**After:** `capacity: int = 2` (in all signatures, with `# Changed from 5 → 2 per DEC-010` comment)

---

## Files Modified
1. `src/ems_readiness/optimization/models.py` — capacity defaults
2. `src/ems_readiness/optimization/allocator.py` — capacity defaults + column name fix
3. `src/ems_readiness/optimization/policies.py` — capacity defaults
4. `scripts/run_optimization_comparison.py` — CAPACITY constant
5. `scripts/run_validation_pilots.py` — constructor + column name fixes
6. `results/simulation/validation_pilot/pilot1_p0_vs_p2.json` — regenerated
7. `results/optimization/policy_comparison.csv` — regenerated
8. `results/simulation/production/exp2_fleet_sensitivity.csv` — legacy relabeled + new P0 added
9. `results/tables/exp2_pivot_rt.csv` — regenerated with correct P0
10. `results/tables/exp2_pivot_rt_with_legacy.csv` — new reference file
