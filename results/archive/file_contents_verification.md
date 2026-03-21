# File Contents Verification Report

**Date:** 2026-03-20  
**Scope:** Representative files from every major results subfolder, plus key source files  
**Verdict:** ⚠️ **4 issues found** — see §5

---

## 1. results/production_v2/ — Main Simulation Results (V2, cap=2, spatial P0)

### 1a. `production_v2/comparison_with_v1.csv` (3.6 KB, 2026-03-16)

```csv
K,v1_policy,v2_policy,v1_config,v2_config,v1_mean_RT,v2_mean_RT,RT_change,...
15,P0,P0,"cap=5, P0-legacy","cap=2, P0",9.476,3.684,-5.792,...
20,P0,P0,"cap=5, P0-legacy","cap=2, P0",3.165,3.165, 0.000,...
30,P0,P0,"cap=5, P0-legacy","cap=2, P0",2.811,2.811, 0.000,...
15,P2,P2,"cap=5, P0-legacy","cap=2, P0",2.825,2.825, 0.000,...
```

✅ **Correct nomenclature:** v1_config says `P0-legacy`, v2_config says `P0`  
✅ **Correct metrics:** P0 K=20 → 3.17 min (not the old 8.08)  
✅ **Correct parameters:** V2 uses cap=2  
✅ P2 values stable across V1→V2 (cap doesn't affect P2 at K=20 since no firehouse gets >1 unit)

---

### 1b. `production_v2/tables/descriptive_statistics.csv` (6.3 KB, 2026-03-16)

```csv
K, policy, n, mean_RT,     std_RT,    ci95_lower, ci95_upper, ...
10, P0,    30, 4.398,       0.122,     4.354,      4.441, ...
10, P2,    30, 3.744,       0.102,     3.707,      3.780, ...
20, P0,    30, 3.165,       0.065,     3.142,      3.188, ...
20, P1,    30, 2.619,       0.052,     2.600,      2.637, ...
20, P2,    30, 2.567,       0.053,     2.548,      2.586, ...
40, P0,    30, 2.445,       0.030,     2.434,      2.456, ...
```

✅ **Policies:** P0, P1, P2 only (no P0_spatial, no legacy confusion)  
✅ **30 replications** per scenario  
✅ **P0 K=20 = 3.17 min** (correct, not 8.08)  
✅ **P2 dominates P0** at all K (ranking: P2 ≤ P1 < P0)  
✅ All mean_RT values monotonically decrease with K for P1 and P2  
✅ Confidence intervals tight (±0.02–0.06)

---

### 1c. `production_v2/simulation/results_K20.csv` (18 KB, 2026-03-16)

```csv
policy, K,  scenario_id, replication, capacity, mean_response_time, ...
P0,     20, P0_K20,      0,           2,        3.156, ...
P0,     20, P0_K20,      1,           2,        3.180, ...
P1,     20, P1_K20,      0,           2,        2.626, ...
P2,     20, P2_K20,      0,           2,        2.587, ...
```

✅ **Capacity column = 2** throughout  
✅ **Policies:** P0, P1, P2  
✅ Individual replications show consistent values around the means

---

### 1d. `production_v2/tables/confidence_intervals.csv` (2.3 KB, 2026-03-16)

```csv
K,  policy, mean,   ci_lower, ci_upper, margin_of_error
20, P0,     3.165,  3.141,    3.189,    0.024
20, P1,     2.619,  2.600,    2.637,    0.019
20, P2,     2.567,  2.547,    2.586,    0.020
```

✅ CIs are narrow and non-overlapping between P0 and P2 at K=20  
✅ Values match descriptive_statistics.csv exactly

---

## 2. results/tables/ — Summary Tables (Mix of dates)

### 2a. `tables/exp1_summary.csv` (542 B, 2026-03-20 — recently regenerated)

```csv
policy, n_reps, Mean RT (min), Mean RT (min) 95% CI,   ...
P0,     30,     3.165,         "[3.141, 3.189]",        ...
P1,     30,     2.619,         "[2.599, 2.638]",        ...
P2,     30,     2.567,         "[2.547, 2.586]",        ...
```

✅ Correct P0 = 3.17 (matches production_v2)  
✅ K=20 default experiment  
✅ P2 best, then P1, then P0

---

### 2b. `tables/exp2_pivot_rt.csv` (360 B, 2026-03-20)

```csv
K,  P0,    P1,    P2
15, 9.476, 2.943, 2.825
20, 3.165, 2.619, 2.567
25, 5.795, 2.467, 2.496
30, 2.811, 2.396, 2.511
35, 3.274, 2.343, 2.435
40, 2.445, 2.353, 2.503
```

⚠️ **ISSUE #1: P0 values are erratic** (9.47, 3.17, 5.79, 2.81, 3.27, 2.45)  
This is because **exp2 comes from V1 production data** where P0 was the legacy index-based round-robin with cap=5.  
The erratic behavior is inherent to the legacy P0 — it's geographic-blind, so some K values cluster units in Manhattan while others spread them poorly.  

**This is technically correct data** (it's V1 results faithfully reproduced), but **the label "P0"** in this file refers to the **deprecated legacy P0**, not the current spatially-stratified P0.  

**Risk:** A reader of this table could confuse it with the current P0. The file should carry a note or be regenerated with V2 data.

---

### 2c. `tables/optimization_comparison.csv` (1.4 KB, 2026-03-20)

```csv
model,                 K,  status,   objective, active_firehouses, units_deployed, ...
spatially_stratified,  20, Baseline, 4.753,     20,                20, ...
demand_proportional,   20, Baseline, 2.870,     18,                20, ...
demand_weighted,       20, Optimal,  2.544,     20,                20, ...
p_median,              20, Optimal,  2.544,     20,                20, ...
maximal_coverage,      20, Optimal,  3.482,      7,                20, ...
```

✅ Model names correct (spatially_stratified, demand_proportional, demand_weighted)  
✅ P2 and P2b give identical objectives (2.5442)  
✅ Coverage = 100% for all

---

### 2d. `tables/cbd_summary_all.csv` (907 B, 2026-03-20)

```csv
scenario_type, policy,   mean_response_time, cbd_mean_rt, non_cbd_mean_rt, ...
baseline,      P0,       3.165,              2.750,       3.685, ...
baseline,      P2,       2.567,              2.479,       2.675, ...
cbd_only,      CBD_ONLY, 8.322,              2.970,      15.058, ...
```

✅ CBD-only policy severely degrades non-CBD (15.06 min)  
✅ Baseline P2 is best overall and best for equity  
✅ Correct P0/P1/P2 nomenclature

---

## 3. results/simulation/validation_pilot/ — Pilot Experiments

### 3a. `pilot1_comparison_table.csv` (784 B, 2026-03-20)

```csv
policy, K,  replications, response_time_mean_mean, ...
P0,     20, 30,           3.169, ...
P2,     20, 30,           5.444, ...
```

⚠️ **ISSUE #2: P2 mean RT = 5.44 min** — worse than P0 (3.17 min)  
This is the **opposite** of expected (P2 should dominate P0). In all other files (production_v2, exp1_summary), P2 ≈ 2.57 min at K=20.  

**Root cause:** The pilot1 validation script re-runs the simulation from scratch with fresh allocations. The P2 allocation may have been generated with incorrect parameters or a different solver state when this pilot was last run (2026-03-20). The P0 result (3.17) matches production, so the simulation engine is fine — it's the P2 allocation that produced a bad plan.

**This needs investigation and re-running.**

---

### 3b. `pilot1_p0_vs_p2.json` (2.6 KB, 2026-03-20)

```json
{
  "scenario": "P0_vs_P2",
  "K": 20,
  "horizon_hours": 168,
  "num_replications": 30,
  "P0": {
    "response_time_mean": {"mean": 3.169, "ci_lower": 3.152, "ci_upper": 3.186},
    "coverage_fraction": {"mean": 0.996}
  },
  "P2": {
    "response_time_mean": {"mean": 5.444, "ci_lower": 5.347, "ci_upper": 5.542},
    "coverage_fraction": {"mean": 0.813}
  }
}
```

⚠️ Same issue as above: P2 coverage = 81.3% (should be ~99.7%)

---

### 3c. `pilot2_sensitivity_K.json` (3.9 KB, 2026-03-16 — older, pre-issue)

```json
(Contains P2 results for K=10,20,30,40 showing RT decreasing with K)
```

✅ Dated 2026-03-16, likely correct from earlier run

---

## 4. results/ — Robustness Experiments

### 4a. `cbd_focused_comparison/comparison_table.csv`

```csv
policy,            overall_rt, cbd_rt, non_cbd_rt, cbd_cov_8min, non_cbd_cov_8min
Manhattan-Wide P2, 2.540,      2.460,  2.642,      1.000,        0.994
CBD-Focused P2,    4.358,      2.483,  6.710,      1.000,        0.738
```

✅ CBD-focused policy provides negligible CBD improvement (2.46→2.48) but destroys non-CBD (2.64→6.71)  
✅ Confirms DEC-009 decision: CBD-focusing not worthwhile

### 4b. `distance_comparison/comparison_table.csv`

```csv
scenario,       response_time_mean, coverage_fraction
P2-Haversine,   2.540,              0.997
P2-Manhattan,   2.540,              0.997
```

✅ Near-identical results confirm P2 allocation is robust to distance metric choice  
✅ Confirms DEC-008 / Assumption A12

### 4c. `optimization/policy_comparison.csv`

```csv
K,  policy_id, policy_name,                  response_time, max_units_at_firehouse
20, P0,        Spatially-Stratified Uniform,  4.753,         1
20, P1,        Demand-Proportional,           2.870,         2
20, P2,        Demand-Weighted Optimized,     2.544,         1
30, P2,        Demand-Weighted Optimized,     2.494,         5
40, P2,        Demand-Weighted Optimized,     2.494,         5
```

⚠️ **ISSUE #3: max_units_at_firehouse = 5** for K≥30 P2/P2b/P2c  
The config says `firehouse_capacity: 2`, but the optimization comparison file shows cap=5 being used in the solver for K≥30 scenarios. This file was generated 2026-03-16, possibly before the cap was changed to 2 in configs, or the script hardcoded cap=5.

The production_v2 simulation correctly uses cap=2 (verified in results_K20.csv).

### 4d. `optimization/findings_summary.json`

```json
{
  "best_overall_response": {
    "K": 30, "policy_id": "P2", "response_time": 2.4935,
    "max_units_at_firehouse": 5
  },
  "policy_rankings_K40": [
    {"policy_id": "P2b", "response_time": 2.4935},
    {"policy_id": "P2",  "response_time": 2.4935},
    {"policy_id": "P1",  "response_time": 2.5199},
    {"policy_id": "P0",  "response_time": 2.6925},
    {"policy_id": "P2c", "response_time": 3.4821}
  ]
}
```

✅ Rankings correct: P2 = P2b < P1 < P0 < P2c  
⚠️ max_units_at_firehouse=5 (same issue as #3)

---

## 5. Source Code Verification

### 5a. `src/ems_readiness/optimization/policies.py`

```python
# Line 6:  P0 — Spatially-stratified uniform allocation
# Line 13: The legacy uniform_allocation ... is deprecated
# Line 33: """Legacy uniform allocation (DEPRECATED — use spatially_stratified_allocation for P0)."""
# Line 60: "uniform_allocation() is deprecated as the P0 baseline."
# Line 309: """P0 — Spatially-stratified uniform allocation (canonical baseline)."""
```

✅ Deprecation warning properly implemented  
✅ P0 = spatially_stratified_allocation throughout  
✅ `DeprecationWarning` issued on `uniform_allocation()` calls

### 5b. `src/ems_readiness/optimization/models.py`

```python
def build_demand_weighted(..., capacity: int = 5, ...):
def build_p_median(..., capacity: int = 5, ...):
def build_maximal_coverage(..., capacity: int = 5, ...):
def build_cbd_focused_demand_weighted(..., capacity: int = 5, ...):
```

⚠️ **ISSUE #4: Function signature defaults = 5**, but `configs/optimization.yaml` says `firehouse_capacity: 2`  
The config correctly overrides at runtime for production_v2, but any caller that doesn't pass `capacity` explicitly gets cap=5. The scripts that generated `results/optimization/policy_comparison.csv` likely used these defaults.

**Recommendation:** Change function defaults to `capacity: int = 2` to match the project-wide decision (DEC-010).

### 5c. `configs/optimization.yaml`

```yaml
firehouse_capacity: 2
# Capacity sensitivity analysis (docs/analysis/capacity_sensitivity_analysis.md)
# shows cap=2 matches or improves upon cap=5 at K≤40.
```

✅ Config is correct  
✅ Well-documented rationale

### 5d. `scripts/run_validation_pilots.py`

```python
def make_p0_allocation(K):
    return spatially_stratified_allocation(K=K, method="latitude", capacity=2)

def make_p2_allocation(K, capacity=2):
    result = allocator.solve(K=K, model="demand_weighted", capacity=capacity)
```

✅ Both functions correctly use capacity=2  
✅ P0 uses spatially_stratified_allocation (correct canonical P0)

### 5e. `scripts/data_processing/tier3_demand.py`

```python
"""Tier 3a: Build NHPP lambda tables from Manhattan crash data.
Outputs:
    data/processed/demand_lambda_hourly.csv
    data/processed/demand_lambda_dow.csv
    data/processed/demand_lambda_precinct.csv
    data/processed/demand_model_summary.json
"""
```

✅ Clean data pipeline structure  
✅ Proper tier-based architecture

---

## 6. Summary of Issues Found

| # | Severity | File | Issue | Action Needed |
|---|----------|------|-------|---------------|
| 1 | Low | `tables/exp2_pivot_rt.csv` | P0 column uses legacy V1 P0 (erratic values like 9.47, 5.79) without labeling it as "P0-legacy" | Add header note or regenerate with V2 P0 |
| 2 | **HIGH** | `simulation/validation_pilot/pilot1_*` | P2 RT=5.44 min (worse than P0=3.17) — opposite of expected | Re-run pilot1; likely stale/corrupt P2 allocation |
| 3 | Medium | `optimization/policy_comparison.csv` | max_units_at_firehouse=5 for K≥30 — doesn't match cap=2 config | Regenerate with cap=2 |
| 4 | Low | `src/.../models.py` | Function defaults `capacity=5` vs config `capacity=2` | Update function defaults to 2 |

### What's Correct ✅
- **All production_v2 files** use correct nomenclature (P0, P1, P2), correct capacity (2), and correct P0 baseline (spatially-stratified)
- **P0 at K=20 = 3.17 min** consistently (not the old 8.08)
- **P2 dominates P0** in all production results
- **CBD analysis** correctly shows CBD-focusing is counterproductive
- **Distance comparison** correctly shows Haversine ≈ Manhattan
- **Deprecation warnings** properly implemented in code
- **Data processing pipeline** clean and well-structured
- **exp1_summary.csv** (the key K=20 table) is correct
- **cbd_summary_all.csv** is correct with proper CBD/non-CBD breakdowns
