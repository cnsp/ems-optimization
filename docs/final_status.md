---
status: 🔄 HISTORICAL
last_updated: "2026-03-20"
note: "Preserved for project history. Contains old metrics/references in historical context. Do not use as current reference."
---
# EMS Optimization Project — Final Status Report

**Date:** 2026-03-15  
**Test Status:** 176/176 passing  
**Remote:** Pushed to `origin/main`

---

## Test Failure Analysis & Resolution

### Root Cause

All 54 failures (45 FAILED + 9 ERROR) traced to a **single root cause**: a column name mismatch in `data/processed/demand_lambda_precinct.csv`.

| Location | Expected Column | Actual Column |
|---|---|---|
| `src/ems_readiness/demand/arrival_generator.py:111` | `lambda_per_hour` | `crash_rate_per_hour` |
| `src/ems_readiness/optimization/allocator.py:116` | `lambda_per_hour` | `crash_rate_per_hour` |

The data pipeline (`scripts/generate_all_data.py`) correctly generates the precinct lambda table with the column name `crash_rate_per_hour`, but two source modules still referenced the old column name `lambda_per_hour`. This caused a `KeyError` whenever:

- The NHPP arrival generator was constructed via `from_tables()` (affects all simulation & demand tests)
- The EMS allocator loaded demand data (affects optimization integration tests)

### Affected Test Modules

| Module | Failures | Errors | Type |
|---|---|---|---|
| `test_demand_advanced.py` | 0 | 9 | `KeyError` in fixture setup |
| `test_simulation_core.py` | 14 | 0 | `KeyError` during `EMSSimulation.__init__` |
| `test_dispatch_logic.py` | 3 | 0 | Same cascade |
| `test_extreme_cases.py` | 10 | 0 | Same cascade |
| `test_integration.py` | 6 | 0 | Same cascade |
| `test_performance.py` | 3 | 0 | Same cascade |
| `test_regression.py` | 3 | 0 | Same cascade |
| `test_reproducibility.py` | 6 | 0 | Same cascade |

### Fix Applied

Two one-line changes:

```python
# arrival_generator.py line 111
- zip(precinct["precinct"].astype(int), precinct["lambda_per_hour"])
+ zip(precinct["precinct"].astype(int), precinct["crash_rate_per_hour"])

# allocator.py line 116
- demand = dl.set_index(dl["precinct"].astype(str))["lambda_per_hour"]
+ demand = dl.set_index(dl["precinct"].astype(str))["crash_rate_per_hour"]
```

---

## Current Test Status

```
============================= 176 passed in 2.86s ==============================
```

All 176 tests pass across 12 test modules:

| Module | Tests | Status |
|---|---|---|
| `test_demand_advanced.py` | 9 | All pass |
| `test_dispatch_logic.py` | 3 | All pass |
| `test_extreme_cases.py` | 10 | All pass |
| `test_integration.py` | 6 | All pass |
| `test_optimization_advanced.py` | 22 | All pass |
| `test_performance.py` | 3 | All pass |
| `test_properties.py` | 22 | All pass |
| `test_regression.py` | 3 | All pass |
| `test_reproducibility.py` | 6 | All pass |
| `test_seed_manager.py` | 9 | All pass |
| `test_service_advanced.py` | 39 | All pass |
| `test_simulation_advanced.py` | 16 | All pass |
| `test_simulation_core.py` | 28 | All pass |

---

## Data Pipeline Status

`make clean-data && make data` completes successfully in ~65 seconds, generating all 11 processed files:

- `firehouses_clean.csv`, `firehouses_manhattan.csv`
- `precincts_manhattan.geojson`
- `crashes_manhattan.csv`, `crashes_manhattan.parquet`
- `demand_lambda_hourly.csv`, `demand_lambda_dow.csv`, `demand_lambda_precinct.csv`
- `demand_model_summary.json`
- `distance_matrix_firehouse_precinct.csv`, `distance_matrix_firehouse_precinct_manhattan.csv`

---

## Git Commit History (recent)

```
aed09cd fix: resolve column name mismatch (lambda_per_hour -> crash_rate_per_hour) -- all 176 tests pass
e79fefb feat: add 5 pipeline enhancements -- validation, progress bars, caching, parallel processing, versioning
aac03c9 feat: implement data dependency migration -- pipeline, auto-gen, clean Git
6ace59d docs: add data dependency analysis and migration plan
35ea7a5 feat: engineering hygiene - expanded tests, seed management, documentation
f18fd53 Remove remaining emojis from scripts and notebooks
```

## Remote Repository Status

- **Remote:** `origin` -> `github.com/cnsp/ems-optimization.git`
- **Branch:** `main`
- **Status:** Up to date (all commits pushed)

---

## Recommendations

1. **CI/CD:** Consider adding a GitHub Actions workflow to run `pytest tests/ -v` on every push/PR to catch regressions early.
2. **Column naming convention:** Standardize on either `lambda_per_hour` or `crash_rate_per_hour` project-wide. The current choice (`crash_rate_per_hour`) is more descriptive and domain-appropriate.
3. **Data contract tests:** Add a lightweight test that validates CSV column names match what the code expects, to prevent this class of bug from recurring.
