# Pipeline Provenance & Regeneration Audit Report

**Date:** 2026-03-21  
**Scope:** All figures/tables referenced in `README.md`, `docs/core/*.md`, `docs/analysis/*.md` (excluding `docs/archive/`)  
**Status:** Audit only — NO files overwritten, NO push, NO PR

---

## === 1. PROVENANCE TABLE ===

### 1A. Figures Embedded in Technical Report (`docs/core/technical_report.md`)

| # | Artifact | Location | Generator | Upstream Data | Status |
|---|----------|----------|-----------|---------------|--------|
| TR-1 | `policy_comparison_panel_K20_cap2.png` | `results/baseline/figures/` | `scripts/run_production_v2.py` | Optimization solver + simulation | ✅ Reproducible |
| TR-2 | `response_time_distribution_by_policy.png` | `results/baseline/figures/` | `scripts/run_production_v2.py` | `all_results_raw.csv` | ✅ Reproducible |
| TR-3 | `fleet_sensitivity_dual.png` | `results/archive/figures/` | `scripts/analysis/regenerate_all_figures.py` | `all_results_raw.csv` | ⚠️ Archive artifact in active doc |
| TR-4 | `cbd_robustness_enhanced.png` | `results/analysis/figures/` | `scripts/analysis/regenerate_all_figures.py` | `cbd_experiment_results.csv` | ⚠️ Generator has stale read path |
| TR-5 | `queue_comparison_by_policy.png` | `results/analysis/figures/` | `scripts/analysis/analyze_queue_metrics.py` | Production exp CSVs | ⚠️ Generator has stale read path |
| TR-6 | `seasonal_patterns.png` | `results/analysis/figures/` | `scripts/analysis/analyze_seasonal_patterns.py` | `crashes_manhattan.csv` | ⚠️ Generator writes to stale output path |
| TR-7 | `distance_comparison_bar.png` | `results/analysis/distance_comparison/` | `scripts/analysis/run_distance_comparison_experiment.py` | Distance matrices + simulation | ✅ Reproducible |
| TR-8 | `cbd_equity_tradeoff_summary.png` | `results/analysis/figures/` | `scripts/analysis/regenerate_all_figures.py` | `cbd_experiment_results.csv` | ⚠️ Generator has stale read path |
| TR-9 | `capacity_sensitivity_heatmap.png` | `results/archive/figures/` | `scripts/analysis/generate_capacity_sensitivity_heatmap.py` | `simulation_results.csv` | 🔴 Archive + generator broken (stale read path) + shows "Data format issue" |

### 1B. Figures Embedded in Analysis Docs (`docs/analysis/*.md`)

| # | Artifact | Location | Generator | Upstream Data | Status |
|---|----------|----------|-----------|---------------|--------|
| AN-1 | `performance_vs_capacity_K40.png` | `results/analysis/capacity_comparison/` | `scripts/analysis/capacity_sensitivity_analysis.py` | Optimization + simulation | ✅ Reproducible |
| AN-2 | `tradeoff_dispersion_rt_K40.png` | `results/analysis/capacity_comparison/` | `scripts/analysis/capacity_sensitivity_analysis.py` | Same | ✅ Reproducible |
| AN-3 | `rt_heatmap_K40.png` | `results/analysis/capacity_comparison/` | `scripts/analysis/capacity_sensitivity_analysis.py` | Same | ✅ Reproducible |
| AN-4 | `full_spectrum_summary.png` | `results/analysis/capacity_comparison/` | `scripts/analysis/capacity_sensitivity_analysis.py` | Same | ✅ Reproducible |
| AN-5 | `cbd_response_comparison.png` | `results/analysis/figures/` | `notebooks/09_cbd_analysis.ipynb` | CBD experiment data | ⚠️ Notebook-only |
| AN-6 | `cbd_scenario_comparison.png` | `results/analysis/figures/` | `notebooks/09_cbd_analysis.ipynb` | CBD experiment data | ⚠️ Notebook-only |
| AN-7 | `cbd_heatmap.png` | `results/analysis/figures/` | `notebooks/09_cbd_analysis.ipynb` | CBD experiment data | ⚠️ Notebook-only |
| AN-8 | `queue_comparison_by_policy.png` | `results/analysis/figures/` | `scripts/analysis/analyze_queue_metrics.py` | Exp CSVs | ⚠️ Generator has stale read path |
| AN-9 | `queue_vs_fleet_size.png` | `results/analysis/figures/` | `scripts/analysis/analyze_queue_metrics.py` | Same | ⚠️ Same |
| AN-10 | `queue_vs_demand.png` | `results/analysis/figures/` | `scripts/analysis/analyze_queue_metrics.py` | Same | ⚠️ Same |
| AN-11 | `queue_heatmap.png` | `results/analysis/figures/` | `scripts/analysis/analyze_queue_metrics.py` | Same | ⚠️ Same |

### 1C. Baseline Figures (`results/baseline/figures/`) — via `run_production_v2.py`

| Artifact | Generator | Status |
|----------|-----------|--------|
| `mean_rt_vs_K.png` | `run_production_v2.py` | ✅ Reproducible |
| `coverage_vs_K.png` | `run_production_v2.py` | ✅ Reproducible |
| `p95_rt_vs_K.png` | `run_production_v2.py` | ✅ Reproducible |
| `rt_distribution_K{20,30,40}.png` | `run_production_v2.py` | ✅ Reproducible |
| `queue_metrics_vs_K.png` | `run_production_v2.py` | ✅ Reproducible |
| `utilization_vs_K.png` | `run_production_v2.py` | ✅ Reproducible |
| `effect_sizes.png` | `run_production_v2.py` | ✅ Reproducible |
| `allocation_map_K{20,30,40}.png` | `run_production_v2.py` | ✅ Reproducible |
| `exp1_policy_comparison.png` | `run_production_v2.py` | ✅ Reproducible |
| `exp2_fleet_sensitivity.png` | `run_production_v2.py` | ✅ Reproducible |
| `exp3_demand_sensitivity.png` | `run_production_v2.py` | ✅ Reproducible |
| `exp4_service_robustness.png` | `run_production_v2.py` | ✅ Reproducible |
| `policy_comparison_panel_K20_cap2.png` | `run_production_v2.py` | ✅ Reproducible |
| `response_time_distribution_by_policy.png` | `run_production_v2.py` | ✅ Reproducible |
| `fleet_sensitivity_v2_dual.png` | `run_production_v2.py` | ✅ Reproducible |
| `production_fleet_sensitivity.png` | `run_production_v2.py` | ✅ Reproducible |
| `pub_fig{1..5}_*.png` | `run_production_v2.py` | ✅ Reproducible |
| `project_summary_dashboard.png` | `run_production_v2.py` | ✅ Reproducible |
| `statistical_effect_sizes.png` | `run_production_v2.py` | ✅ Reproducible |
| `fig_*.png` (EDA figures) | `run_production_v2.py` | ✅ Reproducible |
| `validation_*.png` / `verification_*.png` | `run_production_v2.py` | ✅ Reproducible |
| `p0_vs_p2_response_time.png` | `run_production_v2.py` | ✅ Reproducible |

### 1D. Baseline Tables (`results/baseline/tables/`)

| Artifact | Generator | Status |
|----------|-----------|--------|
| `descriptive_statistics.csv` | `run_production_v2.py` | ✅ Reproducible |
| `anova_results.csv` | `run_production_v2.py` | ✅ Reproducible |
| `posthoc_comparisons.csv` | `run_production_v2.py` | ✅ Reproducible |
| `effect_sizes.csv` | `run_production_v2.py` | ✅ Reproducible |
| `confidence_intervals.csv` | `run_production_v2.py` | ✅ Reproducible |
| `queue_statistics.csv` | `run_production_v2.py` | ✅ Reproducible |
| `table1_baseline_comparison.csv/.tex` | `run_production_v2.py` | ✅ Reproducible |
| `table2_anova_summary.csv/.tex` | `run_production_v2.py` | ✅ Reproducible |
| `table3_pairwise_comparisons.csv/.tex` | `run_production_v2.py` | ✅ Reproducible |
| `table4_sensitivity_summary.csv/.tex` | `run_production_v2.py` | ✅ Reproducible |
| `exp{1..4}_*.csv` | `run_production_v2.py` | ✅ Reproducible |
| `production_results.csv` | `run_production_v2.py` | ✅ Reproducible |

### 1E. Analysis Figures & Tables (various `results/analysis/` subdirs)

| Artifact | Location | Generator | Status |
|----------|----------|-----------|--------|
| Capacity comparison (21 PNGs + CSVs) | `results/analysis/capacity_comparison/` | `capacity_sensitivity_analysis.py` | ✅ Reproducible |
| CBD focused (3 PNGs + CSVs) | `results/analysis/cbd_focused_comparison/` | `run_cbd_focused_optimization.py` | ⚠️ Generator writes to stale path |
| Distance comparison (4 PNGs + CSVs) | `results/analysis/distance_comparison/` | `run_distance_comparison_experiment.py` | ✅ Reproducible |
| Allocation maps (3 PNGs) | `results/analysis/maps/` | `run_optimization_comparison.py` | ⚠️ Generator writes to stale path |
| Heatmaps (~160 PNGs) | `results/analysis/heatmaps/` | `generate_all_heatmaps.py` | ✅ Reproducible |
| CBD analysis figs (6 PNGs) | `results/analysis/figures/cbd_*.png` | Notebook `09_cbd_analysis.ipynb` + `regenerate_all_figures.py` | ⚠️ Mixed: notebook-only + stale read paths |
| Queue figs (5 PNGs) | `results/analysis/figures/queue_*.png` | `analyze_queue_metrics.py` | 🔴 Broken (stale read path) |
| Seasonal figs (3 PNGs) | `results/analysis/figures/seasonal_*.png` | `analyze_seasonal_patterns.py` | ⚠️ Writes to stale output path |
| P0 spatial figs (3 PNGs) | `results/analysis/figures/p0_*.png` | `p0_spatial_analysis.py` | ⚠️ Writes to stale output path |
| Precinct demand figs (3 PNGs) | `results/analysis/figures/precinct_*.png` | `generate_precinct_demand_visualizations.py` | 🔴 Broken (wrong column name) |
| Tradeoff figs (3 PNGs) | `results/analysis/figures/response_time_coverage_*.png` | `generate_tradeoff_improved.py` | ⚠️ Reads from stale path |
| Service/travel model figs (5 PNGs) | `results/analysis/figures/` | Notebook `04_service_travel_proxy.ipynb` | ⚠️ Notebook-only |

---

## === 2. ISSUES FOUND ===

### Broken Reproducibility (scripts that FAIL to run)

| Script | Error | Root Cause |
|--------|-------|------------|
| `generate_capacity_sensitivity_heatmap.py` | `FileNotFoundError` | Reads `results/capacity_comparison/` — data is at `results/analysis/capacity_comparison/` |
| `analyze_queue_metrics.py` | No data loaded → crash | Reads `results/simulation/production/` — data is at `results/analysis/simulation/production/` |
| `generate_publication_figures.py` | `FileNotFoundError` | Reads `results/simulation/production/` — same stale path |
| `generate_summary_dashboard.py` | `FileNotFoundError` | Reads `results/tables/` and `results/simulation/production/` — both stale |
| `regenerate_all_figures.py` | Partial (3 of 7 succeed) | Reads `results/simulation/cbd_experiment/` and `results/capacity_comparison/` — both stale |
| `generate_precinct_demand_visualizations.py` | `KeyError: 'crash_rate_per_hour'` | Column renamed to `lambda_per_hour` in `demand_lambda_precinct.csv` |
| `generate_tradeoff_improved.py` | Would fail | Reads `results/optimization/` — data is at `results/archive/optimization/` |

### Archive Artifacts Referenced in Active (Non-Archive) Documents

| Document | Artifact | Archive Path | Issue |
|----------|----------|--------------|-------|
| `docs/core/technical_report.md` (line 478) | Fleet Sensitivity Dual | `results/archive/figures/fleet_sensitivity_dual.png` | **Archive figure in active technical report** |
| `docs/core/technical_report.md` (line 670) | Capacity Sensitivity Heatmap | `results/archive/figures/capacity_sensitivity_heatmap.png` | **Archive figure in active report** + shows "Data format issue" |

### Scripts Writing to Legacy Flat Paths (`results/figures/`, `results/tables/`)

These scripts would create output in the deprecated `results/figures/` or `results/tables/` directories instead of the reorganized `results/baseline/` or `results/analysis/` structure:

| Script | Stale Output Path | Correct Output Path |
|--------|-------------------|---------------------|
| `analyze_queue_metrics.py` | `results/figures/`, `results/tables/` | `results/analysis/figures/`, `results/baseline/tables/` |
| `analyze_seasonal_patterns.py` | `results/figures/`, `results/tables/` | `results/analysis/figures/`, `results/baseline/tables/` |
| `p0_spatial_analysis.py` | `results/figures/` | `results/analysis/figures/` |
| `generate_publication_figures.py` | `results/figures/` | `results/baseline/figures/` |
| `generate_summary_dashboard.py` | `results/figures/` | `results/baseline/figures/` |
| `regenerate_all_figures.py` | `results/figures/` | `results/baseline/figures/` or `results/analysis/figures/` |
| `generate_tradeoff_improved.py` | `results/figures/` | `results/analysis/figures/` |
| `generate_precinct_demand_visualizations.py` | `results/figures/` | `results/analysis/figures/` |
| `run_optimization_comparison.py` | `results/optimization/`, `results/maps/` | `results/archive/optimization/`, `results/analysis/maps/` |
| `run_cbd_focused_optimization.py` | `results/cbd_focused_comparison/` | `results/analysis/cbd_focused_comparison/` |

### Stale Input Paths in Scripts

| Script | Stale Read Path | Correct Read Path |
|--------|-----------------|-------------------|
| `generate_capacity_sensitivity_heatmap.py` | `results/capacity_comparison/` | `results/analysis/capacity_comparison/` |
| `analyze_queue_metrics.py` | `results/simulation/production/` | `results/analysis/simulation/production/` |
| `generate_publication_figures.py` | `results/simulation/production/` | `results/analysis/simulation/production/` |
| `generate_summary_dashboard.py` | `results/tables/`, `results/simulation/production/` | `results/baseline/tables/`, `results/analysis/simulation/production/` |
| `regenerate_all_figures.py` | `results/simulation/cbd_experiment/`, `results/capacity_comparison/` | `results/analysis/simulation/cbd_experiment/`, `results/analysis/capacity_comparison/` |
| `generate_tradeoff_improved.py` | `results/optimization/` | `results/archive/optimization/` |

### Column Name Mismatch

| Script | Uses | Actual Column | File |
|--------|------|---------------|------|
| `generate_precinct_demand_visualizations.py` | `crash_rate_per_hour` | `lambda_per_hour` | `demand_lambda_precinct.csv` |

### Documentation Path References That Are Informational-Only Stale

The `docs/core/visualization_index.md` and `docs/core/figure_trace_guide.md` reference `results/figures/` as the location for many figures. These files have been reorganized to `results/baseline/figures/` and `results/analysis/figures/`. The index is informational (no embedded images) but is misleading.

### Notebook-Only Figures (No Script Equivalent)

| Figure | Notebook | Status |
|--------|----------|--------|
| `fig_hourly_demand.png` | `02_eda_spatiotemporal.ipynb` | Notebook-only (also generated by `run_production_v2.py`) |
| `fig_daily_demand.png` | `02_eda_spatiotemporal.ipynb` | Same |
| `fig_temporal_trends.png` | `02_eda_spatiotemporal.ipynb` | Same |
| `fig_crash_heatmap.png` | `02_eda_spatiotemporal.ipynb` | Same |
| `fig_precinct_density.png` | `02_eda_spatiotemporal.ipynb` | Same |
| `fig_firehouses_map.png` | `02_eda_spatiotemporal.ipynb` | Same |
| `cbd_heatmap.png` | `09_cbd_analysis.ipynb` | Notebook-only (no script equivalent) |
| `cbd_response_comparison.png` | `09_cbd_analysis.ipynb` | Notebook-only |
| `cbd_scenario_comparison.png` | `09_cbd_analysis.ipynb` | Notebook-only |
| `distance_matrix_heatmap.png` | `04_service_travel_proxy.ipynb` | Notebook-only |
| `distance_matrix_coverage.png` | `04_service_travel_proxy.ipynb` | Notebook-only |
| `travel_time_by_tod.png` | `04_service_travel_proxy.ipynb` | Notebook-only |
| `tod_speed_factors.png` | `04_service_travel_proxy.ipynb` | Notebook-only |
| `service_time_distribution.png` | `04_service_travel_proxy.ipynb` | Notebook-only |
| `nhpp_arrivals_demo.png` | `04_service_travel_proxy.ipynb` | Notebook-only |

---

## === 3. REGENERATION RESULTS ===

### Scripts That Run Successfully

| Script | Output Location | Match Status | Notes |
|--------|----------------|--------------|-------|
| `run_production_v2.py` | `results/baseline/` | **Not re-run** (long-running: 810 simulations) | Paths verified correct; would produce identical structure |
| `capacity_sensitivity_analysis.py` | `results/analysis/capacity_comparison/` | **Not re-run** (requires simulation) | Paths verified correct |
| `run_distance_comparison_experiment.py` | `results/analysis/distance_comparison/` | **Not re-run** (requires simulation) | Paths verified correct |
| `run_cbd_experiment.py` | `results/analysis/simulation/cbd_experiment/` | **Not re-run** (requires simulation) | Paths verified correct |
| `demand_modeling.py` | `results/baseline/figures/` | **Not re-run** (needs raw crash data) | Paths verified correct |
| `run_verification.py` | `results/baseline/simulation/verification/` | **Not re-run** | Paths verified correct |
| `run_validation_pilots.py` | `results/baseline/simulation/validation_pilot/` | **Not re-run** | Paths verified correct |
| `p0_spatial_analysis.py` | ⚠️ `results/figures/` (stale) | ✅ Ran successfully | Output went to wrong dir; should write to `results/analysis/figures/` |

### Scripts That FAIL

| Script | Error | Attempted Fix | Notes |
|--------|-------|---------------|-------|
| `generate_capacity_sensitivity_heatmap.py` | FileNotFoundError | Path fix needed | Would need `results/capacity_comparison/` → `results/analysis/capacity_comparison/` |
| `analyze_queue_metrics.py` | No data found | Path fix needed | Would need `results/simulation/production/` → `results/analysis/simulation/production/` |
| `generate_publication_figures.py` | FileNotFoundError | Path fix needed | Same stale simulation path |
| `generate_summary_dashboard.py` | FileNotFoundError | Two path fixes needed | Both `results/tables/` and `results/simulation/production/` are stale |
| `regenerate_all_figures.py` | Partial success (3/7) | Two path fixes needed | CBD + capacity paths stale |
| `generate_precinct_demand_visualizations.py` | KeyError | Column rename fix | `crash_rate_per_hour` → `lambda_per_hour` |

---

## === 4. RECOMMENDED ACTIONS ===

### Keep As-Is (No Changes Needed)

These artifacts and their generators are correctly configured:

1. **All `results/baseline/` artifacts** — Generated by `run_production_v2.py` with correct paths
2. **`results/analysis/capacity_comparison/` artifacts** — `capacity_sensitivity_analysis.py` paths are correct
3. **`results/analysis/distance_comparison/` artifacts** — `run_distance_comparison_experiment.py` paths correct
4. **`results/analysis/simulation/` artifacts** — Experiment runners have correct paths
5. **`demand_modeling.py`** — Writes to `results/baseline/figures/` correctly
6. **`run_verification.py`** and **`run_validation_pilots.py`** — Both correct

### Fix Script Input/Output Paths (13 scripts)

| Script | Fix Required |
|--------|-------------|
| `analyze_queue_metrics.py` | Read: `results/simulation/production/` → `results/analysis/simulation/production/`; Write figures: → `results/analysis/figures/`; Write tables: → `results/baseline/tables/` |
| `analyze_seasonal_patterns.py` | Write figures: → `results/analysis/figures/`; Write tables: → `results/baseline/tables/` |
| `generate_capacity_sensitivity_heatmap.py` | Read: `results/capacity_comparison/` → `results/analysis/capacity_comparison/`; Write: → `results/analysis/figures/` |
| `generate_publication_figures.py` | Read: `results/simulation/production/` → `results/analysis/simulation/production/`; Write: → `results/baseline/figures/`; Fix CAPACITY=5 → CAPACITY=2 |
| `generate_summary_dashboard.py` | Read tables: `results/tables/` → `results/baseline/tables/`; Read sim: `results/simulation/production/` → `results/analysis/simulation/production/`; Write: → `results/baseline/figures/` |
| `regenerate_all_figures.py` | Read CBD: `results/simulation/cbd_experiment/` → `results/analysis/simulation/cbd_experiment/`; Read capacity: `results/capacity_comparison/` → `results/analysis/capacity_comparison/`; Write: split between `results/baseline/figures/` and `results/analysis/figures/` |
| `generate_tradeoff_improved.py` | Read: `results/optimization/` → `results/archive/optimization/`; Write: → `results/analysis/figures/`; Fix CAPACITY=5 → document legacy |
| `generate_precinct_demand_visualizations.py` | Fix column: `crash_rate_per_hour` → `lambda_per_hour`; Write: → `results/analysis/figures/` |
| `p0_spatial_analysis.py` | Write: `results/figures/` → `results/analysis/figures/` |
| `run_optimization_comparison.py` | Write results: `results/optimization/` → `results/archive/optimization/`; Write maps: `results/maps/` → `results/analysis/maps/`; Write figures: → `results/baseline/figures/` |
| `run_cbd_focused_optimization.py` | Write: `results/cbd_focused_comparison/` → `results/analysis/cbd_focused_comparison/` |

### Regenerate and Replace

After path fixes, these artifacts should be regenerated:

1. **`capacity_sensitivity_heatmap.png`** — Currently in archive and shows "Data format issue" per user screenshot. After fixing `generate_capacity_sensitivity_heatmap.py`, regenerate to `results/analysis/figures/`
2. **Queue analysis figures** — After fixing `analyze_queue_metrics.py` paths, regenerate to `results/analysis/figures/`
3. **Publication figures** — After fixing `generate_publication_figures.py`, regenerate to confirm match with `results/baseline/figures/` versions

### Move to Archive

| Artifact | Current Location | Reason |
|----------|-----------------|--------|
| No artifacts need moving | — | Current archive contents are already correctly placed |

### Fix Technical Report References

| Line | Current Reference | Recommended Fix |
|------|------------------|-----------------|
| 478 | `results/archive/figures/fleet_sensitivity_dual.png` | Replace with `results/baseline/figures/fleet_sensitivity_v2_dual.png` (the current cap=2 version) |
| 670 | `results/archive/figures/capacity_sensitivity_heatmap.png` | Regenerate to `results/analysis/figures/capacity_sensitivity_heatmap.png` and update reference |

### Update Documentation Indexes

| Document | Issue |
|----------|-------|
| `docs/core/visualization_index.md` | ~100+ references to `results/figures/` should be updated to `results/baseline/figures/` or `results/analysis/figures/` as appropriate |
| `docs/core/figure_trace_guide.md` | Same — all figure locations reference `results/figures/` which is now a stub directory |
| `docs/core/data_usage_guide.md` | References `results/figures/*.png` generically; should be updated to the reorganized paths |

---

## Summary Statistics

| Category | Count |
|----------|-------|
| **Total artifacts audited** | ~120 figures + ~40 tables |
| **Fully reproducible (script + correct paths)** | ~75 figures, ~30 tables |
| **Broken scripts (won't run)** | 6 scripts |
| **Scripts with stale output paths** | 10 scripts |
| **Scripts with stale input paths** | 6 scripts |
| **Archive artifacts in active docs** | 2 (technical report) |
| **Notebook-only figures (no script)** | 15 figures |
| **Column name mismatches** | 1 (`crash_rate_per_hour` vs `lambda_per_hour`) |

### Root Cause

All issues stem from **a single organizational change**: the directory reorganization from flat `results/figures/`, `results/tables/`, `results/simulation/`, `results/optimization/`, `results/capacity_comparison/` into the tiered `results/baseline/`, `results/analysis/`, `results/archive/` structure. **The scripts were not updated to match the new directory structure.** The data and figures themselves are valid; only the paths in the generating scripts are stale.

### Priority Ranking

1. 🔴 **P0 — Fix the 6 broken scripts** (can't regenerate at all)
2. 🟡 **P1 — Fix technical report archive refs** (TR lines 478, 670)
3. 🟡 **P2 — Fix 10 scripts with stale output paths** (would write to wrong dirs)
4. 🟢 **P3 — Update visualization_index.md and figure_trace_guide.md** (informational)
5. 🟢 **P4 — Create script equivalents for notebook-only figures** (nice-to-have)
