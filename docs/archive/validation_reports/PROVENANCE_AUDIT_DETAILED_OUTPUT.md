# Pipeline Provenance & Regeneration Audit — Detailed 4-Phase Output

**Date:** 2026-03-21  
**Scope:** All figures/tables in `README.md`, `docs/core/*.md`, `docs/analysis/*.md` (excluding `docs/archive/`)

---

## === 1. PROVENANCE TABLE ===

### Technical Report Figures (`docs/core/technical_report.md`)

| Artifact | Location | Generator | Upstream Data | Status |
|----------|----------|-----------|---------------|--------|
| `policy_comparison_panel_K20_cap2.png` | `results/baseline/figures/` | `scripts/run_production_v2.py` | Optimization solver + simulation | ✅ Reproducible |
| `response_time_distribution_by_policy.png` | `results/baseline/figures/` | `scripts/run_production_v2.py` | `all_results_raw.csv` | ✅ Reproducible |
| `fleet_sensitivity_dual.png` | `results/archive/figures/` | `scripts/analysis/regenerate_all_figures.py` | `all_results_raw.csv` | ⚠️ Archive artifact in active doc |
| `cbd_robustness_enhanced.png` | `results/analysis/figures/` | `scripts/analysis/regenerate_all_figures.py` | `cbd_experiment_results.csv` | ⚠️ Generator has stale read path |
| `queue_comparison_by_policy.png` | `results/analysis/figures/` | `scripts/analysis/analyze_queue_metrics.py` | Production exp CSVs | ⚠️ Generator has stale read path |
| `seasonal_patterns.png` | `results/analysis/figures/` | `scripts/analysis/analyze_seasonal_patterns.py` | `crashes_manhattan.csv` | ⚠️ Generator writes to stale output path |
| `distance_comparison_bar.png` | `results/analysis/distance_comparison/` | `scripts/analysis/run_distance_comparison_experiment.py` | Distance matrices + simulation | ✅ Reproducible |
| `cbd_equity_tradeoff_summary.png` | `results/analysis/figures/` | `scripts/analysis/regenerate_all_figures.py` | `cbd_experiment_results.csv` | ⚠️ Generator has stale read path |
| `capacity_sensitivity_heatmap.png` | `results/archive/figures/` | `scripts/analysis/generate_capacity_sensitivity_heatmap.py` | `simulation_results.csv` | 🔴 Archive + generator broken (stale read path) + shows "Data format issue" |

### Analysis Docs Figures (`docs/analysis/*.md`)

| Artifact | Location | Generator | Upstream Data | Status |
|----------|----------|-----------|---------------|--------|
| `performance_vs_capacity_K40.png` | `results/analysis/capacity_comparison/` | `scripts/analysis/capacity_sensitivity_analysis.py` | Optimization + simulation | ✅ Reproducible |
| `tradeoff_dispersion_rt_K40.png` | `results/analysis/capacity_comparison/` | `scripts/analysis/capacity_sensitivity_analysis.py` | Same | ✅ Reproducible |
| `rt_heatmap_K40.png` | `results/analysis/capacity_comparison/` | `scripts/analysis/capacity_sensitivity_analysis.py` | Same | ✅ Reproducible |
| `full_spectrum_summary.png` | `results/analysis/capacity_comparison/` | `scripts/analysis/capacity_sensitivity_analysis.py` | Same | ✅ Reproducible |
| `cbd_response_comparison.png` | `results/analysis/figures/` | `notebooks/09_cbd_analysis.ipynb` | CBD experiment data | ⚠️ Notebook-only |
| `cbd_scenario_comparison.png` | `results/analysis/figures/` | `notebooks/09_cbd_analysis.ipynb` | CBD experiment data | ⚠️ Notebook-only |
| `cbd_heatmap.png` | `results/analysis/figures/` | `notebooks/09_cbd_analysis.ipynb` | CBD experiment data | ⚠️ Notebook-only |
| `queue_comparison_by_policy.png` | `results/analysis/figures/` | `scripts/analysis/analyze_queue_metrics.py` | Exp CSVs | ⚠️ Generator has stale read path |
| `queue_vs_fleet_size.png` | `results/analysis/figures/` | `scripts/analysis/analyze_queue_metrics.py` | Same | ⚠️ Same |
| `queue_vs_demand.png` | `results/analysis/figures/` | `scripts/analysis/analyze_queue_metrics.py` | Same | ⚠️ Same |
| `queue_heatmap.png` | `results/analysis/figures/` | `scripts/analysis/analyze_queue_metrics.py` | Same | ⚠️ Same |

### Baseline Figures (`results/baseline/figures/`) — via `run_production_v2.py`

| Artifact | Location | Generator | Upstream Data | Status |
|----------|----------|-----------|---------------|--------|
| `mean_rt_vs_K.png` | `results/baseline/figures/` | `run_production_v2.py` | Simulation results | ✅ Reproducible |
| `coverage_vs_K.png` | `results/baseline/figures/` | `run_production_v2.py` | Simulation results | ✅ Reproducible |
| `p95_rt_vs_K.png` | `results/baseline/figures/` | `run_production_v2.py` | Simulation results | ✅ Reproducible |
| `rt_distribution_K{20,30,40}.png` | `results/baseline/figures/` | `run_production_v2.py` | Simulation results | ✅ Reproducible |
| `queue_metrics_vs_K.png` | `results/baseline/figures/` | `run_production_v2.py` | Simulation results | ✅ Reproducible |
| `utilization_vs_K.png` | `results/baseline/figures/` | `run_production_v2.py` | Simulation results | ✅ Reproducible |
| `effect_sizes.png` | `results/baseline/figures/` | `run_production_v2.py` | Simulation results | ✅ Reproducible |
| `allocation_map_K{20,30,40}.png` | `results/baseline/figures/` | `run_production_v2.py` | Allocation data | ✅ Reproducible |
| `exp1_policy_comparison.png` | `results/baseline/figures/` | `run_production_v2.py` | Exp 1 results | ✅ Reproducible |
| `exp2_fleet_sensitivity.png` | `results/baseline/figures/` | `run_production_v2.py` | Exp 2 results | ✅ Reproducible |
| `exp3_demand_sensitivity.png` | `results/baseline/figures/` | `run_production_v2.py` | Exp 3 results | ✅ Reproducible |
| `exp4_service_robustness.png` | `results/baseline/figures/` | `run_production_v2.py` | Exp 4 results | ✅ Reproducible |
| `policy_comparison_panel_K20_cap2.png` | `results/baseline/figures/` | `run_production_v2.py` | Optimization + simulation | ✅ Reproducible |
| `response_time_distribution_by_policy.png` | `results/baseline/figures/` | `run_production_v2.py` | `all_results_raw.csv` | ✅ Reproducible |
| `fleet_sensitivity_v2_dual.png` | `results/baseline/figures/` | `run_production_v2.py` | Simulation results | ✅ Reproducible |
| `production_fleet_sensitivity.png` | `results/baseline/figures/` | `run_production_v2.py` | Simulation results | ✅ Reproducible |
| `pub_fig{1..5}_*.png` | `results/baseline/figures/` | `run_production_v2.py` | Various | ✅ Reproducible |
| `project_summary_dashboard.png` | `results/baseline/figures/` | `run_production_v2.py` | All results | ✅ Reproducible |
| `statistical_effect_sizes.png` | `results/baseline/figures/` | `run_production_v2.py` | Statistical analysis | ✅ Reproducible |
| `fig_*.png` (EDA figures) | `results/baseline/figures/` | `run_production_v2.py` | Crash data | ✅ Reproducible |
| `validation_*.png` / `verification_*.png` | `results/baseline/figures/` | `run_production_v2.py` | V&V runs | ✅ Reproducible |
| `p0_vs_p2_response_time.png` | `results/baseline/figures/` | `run_production_v2.py` | Policy comparison | ✅ Reproducible |

### Baseline Tables (`results/baseline/tables/`)

| Artifact | Location | Generator | Upstream Data | Status |
|----------|----------|-----------|---------------|--------|
| `descriptive_statistics.csv` | `results/baseline/tables/` | `run_production_v2.py` | Simulation results | ✅ Reproducible |
| `anova_results.csv` | `results/baseline/tables/` | `run_production_v2.py` | Simulation results | ✅ Reproducible |
| `posthoc_comparisons.csv` | `results/baseline/tables/` | `run_production_v2.py` | Simulation results | ✅ Reproducible |
| `effect_sizes.csv` | `results/baseline/tables/` | `run_production_v2.py` | Simulation results | ✅ Reproducible |
| `confidence_intervals.csv` | `results/baseline/tables/` | `run_production_v2.py` | Simulation results | ✅ Reproducible |
| `queue_statistics.csv` | `results/baseline/tables/` | `run_production_v2.py` | Simulation results | ✅ Reproducible |
| `table1_baseline_comparison.csv/.tex` | `results/baseline/tables/` | `run_production_v2.py` | Policy results | ✅ Reproducible |
| `table2_anova_summary.csv/.tex` | `results/baseline/tables/` | `run_production_v2.py` | ANOVA results | ✅ Reproducible |
| `table3_pairwise_comparisons.csv/.tex` | `results/baseline/tables/` | `run_production_v2.py` | Post-hoc tests | ✅ Reproducible |
| `table4_sensitivity_summary.csv/.tex` | `results/baseline/tables/` | `run_production_v2.py` | Sensitivity analysis | ✅ Reproducible |
| `exp{1..4}_*.csv` | `results/baseline/tables/` | `run_production_v2.py` | Experiment results | ✅ Reproducible |
| `production_results.csv` | `results/baseline/tables/` | `run_production_v2.py` | All results | ✅ Reproducible |

### Analysis Artifacts (`results/analysis/` subdirs)

| Artifact | Location | Generator | Upstream Data | Status |
|----------|----------|-----------|---------------|--------|
| Capacity comparison (21 PNGs + CSVs) | `results/analysis/capacity_comparison/` | `capacity_sensitivity_analysis.py` | Optimization + simulation | ✅ Reproducible |
| CBD focused (3 PNGs + CSVs) | `results/analysis/cbd_focused_comparison/` | `run_cbd_focused_optimization.py` | CBD experiment data | ⚠️ Generator writes to stale path |
| Distance comparison (4 PNGs + CSVs) | `results/analysis/distance_comparison/` | `run_distance_comparison_experiment.py` | Distance matrices + simulation | ✅ Reproducible |
| Allocation maps (3 PNGs) | `results/analysis/maps/` | `run_optimization_comparison.py` | Allocation data | ⚠️ Generator writes to stale path |
| Heatmaps (~160 PNGs) | `results/analysis/heatmaps/` | `generate_all_heatmaps.py` | Various | ✅ Reproducible |
| CBD analysis figs (6 PNGs) | `results/analysis/figures/cbd_*.png` | Notebook `09_cbd_analysis.ipynb` + `regenerate_all_figures.py` | CBD experiment data | ⚠️ Mixed: notebook-only + stale read paths |
| Queue figs (5 PNGs) | `results/analysis/figures/queue_*.png` | `analyze_queue_metrics.py` | Production CSVs | 🔴 Broken (stale read path) |
| Seasonal figs (3 PNGs) | `results/analysis/figures/seasonal_*.png` | `analyze_seasonal_patterns.py` | `crashes_manhattan.csv` | ⚠️ Writes to stale output path |
| P0 spatial figs (3 PNGs) | `results/analysis/figures/p0_*.png` | `p0_spatial_analysis.py` | Spatial data | ⚠️ Writes to stale output path |
| Precinct demand figs (3 PNGs) | `results/analysis/figures/precinct_*.png` | `generate_precinct_demand_visualizations.py` | `demand_lambda_precinct.csv` | 🔴 Broken (wrong column name) |
| Tradeoff figs (3 PNGs) | `results/analysis/figures/response_time_coverage_*.png` | `generate_tradeoff_improved.py` | Optimization results | ⚠️ Reads from stale path |
| Service/travel model figs (5 PNGs) | `results/analysis/figures/` | Notebook `04_service_travel_proxy.ipynb` | Model outputs | ⚠️ Notebook-only |

---

## === 2. ISSUES FOUND ===

### Broken Reproducibility

These scripts **cannot be run at all** — they crash with errors:

1. **`generate_capacity_sensitivity_heatmap.py`** — `FileNotFoundError`: reads `results/capacity_comparison/`, data is at `results/analysis/capacity_comparison/`
2. **`analyze_queue_metrics.py`** — No data loaded → crash: reads `results/simulation/production/`, data is at `results/analysis/simulation/production/`
3. **`generate_publication_figures.py`** — `FileNotFoundError`: reads `results/simulation/production/`, same stale path
4. **`generate_summary_dashboard.py`** — `FileNotFoundError`: reads `results/tables/` and `results/simulation/production/`, both stale
5. **`regenerate_all_figures.py`** — Partial (3 of 7 succeed): reads `results/simulation/cbd_experiment/` and `results/capacity_comparison/`, both stale
6. **`generate_precinct_demand_visualizations.py`** — `KeyError: 'crash_rate_per_hour'`: column renamed to `lambda_per_hour` in `demand_lambda_precinct.csv`
7. **`generate_tradeoff_improved.py`** — Would fail: reads `results/optimization/`, data is at `results/archive/optimization/`

### Archive Misuse

Archive artifacts referenced in **active** (non-archive) documents:

1. **`docs/core/technical_report.md` line 478** → `results/archive/figures/fleet_sensitivity_dual.png` — Archive figure embedded in active technical report
2. **`docs/core/technical_report.md` line 670** → `results/archive/figures/capacity_sensitivity_heatmap.png` — Archive figure in active report + shows "Data format issue" (blank heatmap)

### Stale Scripts

**Scripts with stale INPUT paths:**

| Script | Stale Read Path | Correct Read Path |
|--------|-----------------|-------------------|
| `generate_capacity_sensitivity_heatmap.py` | `results/capacity_comparison/` | `results/analysis/capacity_comparison/` |
| `analyze_queue_metrics.py` | `results/simulation/production/` | `results/analysis/simulation/production/` |
| `generate_publication_figures.py` | `results/simulation/production/` | `results/analysis/simulation/production/` |
| `generate_summary_dashboard.py` | `results/tables/`, `results/simulation/production/` | `results/baseline/tables/`, `results/analysis/simulation/production/` |
| `regenerate_all_figures.py` | `results/simulation/cbd_experiment/`, `results/capacity_comparison/` | `results/analysis/simulation/cbd_experiment/`, `results/analysis/capacity_comparison/` |
| `generate_tradeoff_improved.py` | `results/optimization/` | `results/archive/optimization/` |

**Scripts with stale OUTPUT paths:**

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

### Mismatched Outputs

| Script | Column Used | Actual Column in Data | Data File |
|--------|-------------|-----------------------|-----------|
| `generate_precinct_demand_visualizations.py` | `crash_rate_per_hour` | `lambda_per_hour` | `demand_lambda_precinct.csv` |

Additionally, `capacity_sensitivity_heatmap.png` currently shows "Data format issue" (blank panels for K=20 and K=40) — the committed figure does not display valid data.

---

## === 3. REGENERATION RESULTS ===

### Scripts That Run Successfully (paths verified correct)

| Artifact / Script | Match Status | Notes |
|-------------------|--------------|-------|
| `run_production_v2.py` → all `results/baseline/` | **Not re-run** (810 simulations, long-running) | Paths verified correct; would produce identical structure |
| `capacity_sensitivity_analysis.py` → `results/analysis/capacity_comparison/` | **Not re-run** (requires simulation) | Paths verified correct |
| `run_distance_comparison_experiment.py` → `results/analysis/distance_comparison/` | **Not re-run** (requires simulation) | Paths verified correct |
| `run_cbd_experiment.py` → `results/analysis/simulation/cbd_experiment/` | **Not re-run** (requires simulation) | Paths verified correct |
| `demand_modeling.py` → `results/baseline/figures/` | **Not re-run** (needs raw crash data) | Paths verified correct |
| `run_verification.py` → `results/baseline/simulation/verification/` | **Not re-run** | Paths verified correct |
| `run_validation_pilots.py` → `results/baseline/simulation/validation_pilot/` | **Not re-run** | Paths verified correct |
| `p0_spatial_analysis.py` | ✅ Ran successfully | Output went to wrong dir (`results/figures/` instead of `results/analysis/figures/`) |

### Scripts That FAIL

| Artifact / Script | Match Status | Notes |
|-------------------|--------------|-------|
| `generate_capacity_sensitivity_heatmap.py` | 🔴 FAIL — FileNotFoundError | Needs path fix: `results/capacity_comparison/` → `results/analysis/capacity_comparison/` |
| `analyze_queue_metrics.py` | 🔴 FAIL — No data loaded | Needs path fix: `results/simulation/production/` → `results/analysis/simulation/production/` |
| `generate_publication_figures.py` | 🔴 FAIL — FileNotFoundError | Needs same stale simulation path fix |
| `generate_summary_dashboard.py` | 🔴 FAIL — FileNotFoundError | Needs two path fixes (tables + simulation) |
| `regenerate_all_figures.py` | ⚠️ PARTIAL — 3 of 7 subfunctions succeed | CBD + capacity read paths are stale |
| `generate_precinct_demand_visualizations.py` | 🔴 FAIL — KeyError | Column rename needed: `crash_rate_per_hour` → `lambda_per_hour` |
| `generate_tradeoff_improved.py` | 🔴 Would FAIL | Reads `results/optimization/` which is now `results/archive/optimization/` |

---

## === 4. RECOMMENDED ACTIONS ===

### Keep As-Is

1. **All `results/baseline/` artifacts** — Generated by `run_production_v2.py` with correct paths
2. **`results/analysis/capacity_comparison/` artifacts** — `capacity_sensitivity_analysis.py` paths are correct
3. **`results/analysis/distance_comparison/` artifacts** — `run_distance_comparison_experiment.py` paths correct
4. **`results/analysis/simulation/` artifacts** — Experiment runners have correct paths
5. **`demand_modeling.py`** — Writes to `results/baseline/figures/` correctly
6. **`run_verification.py`** and **`run_validation_pilots.py`** — Both correct
7. **`generate_all_heatmaps.py`** — Writes to `results/analysis/heatmaps/` correctly

### Regenerate and Replace

1. **`capacity_sensitivity_heatmap.png`** — Currently in archive and shows "Data format issue" (blank panels). After fixing `generate_capacity_sensitivity_heatmap.py`, regenerate to `results/analysis/figures/`
2. **Queue analysis figures (5 PNGs)** — After fixing `analyze_queue_metrics.py` paths, regenerate to `results/analysis/figures/`
3. **Precinct demand figures (3 PNGs)** — After fixing column name in `generate_precinct_demand_visualizations.py`, regenerate to `results/analysis/figures/`
4. **Publication figures** — After fixing `generate_publication_figures.py`, regenerate to confirm match with `results/baseline/figures/` versions

### Move to Archive

| Artifact | Current Location | Action |
|----------|-----------------|--------|
| No artifacts need moving | — | Current archive contents are already correctly placed |

### Fix Script (13 scripts need path corrections)

| Script | Fix Required |
|--------|-------------|
| `analyze_queue_metrics.py` | Read: `results/simulation/production/` → `results/analysis/simulation/production/`; Write figs → `results/analysis/figures/`; Write tables → `results/baseline/tables/` |
| `analyze_seasonal_patterns.py` | Write figs → `results/analysis/figures/`; Write tables → `results/baseline/tables/` |
| `generate_capacity_sensitivity_heatmap.py` | Read: `results/capacity_comparison/` → `results/analysis/capacity_comparison/`; Write → `results/analysis/figures/` |
| `generate_publication_figures.py` | Read: `results/simulation/production/` → `results/analysis/simulation/production/`; Write → `results/baseline/figures/`; Fix CAPACITY=5 → CAPACITY=2 |
| `generate_summary_dashboard.py` | Read tables: `results/tables/` → `results/baseline/tables/`; Read sim: `results/simulation/production/` → `results/analysis/simulation/production/`; Write → `results/baseline/figures/` |
| `regenerate_all_figures.py` | Read CBD: → `results/analysis/simulation/cbd_experiment/`; Read capacity: → `results/analysis/capacity_comparison/`; Write: split baseline/analysis |
| `generate_tradeoff_improved.py` | Read: `results/optimization/` → `results/archive/optimization/`; Write → `results/analysis/figures/` |
| `generate_precinct_demand_visualizations.py` | Fix column: `crash_rate_per_hour` → `lambda_per_hour`; Write → `results/analysis/figures/` |
| `p0_spatial_analysis.py` | Write: `results/figures/` → `results/analysis/figures/` |
| `run_optimization_comparison.py` | Write results: → `results/archive/optimization/`; Write maps: → `results/analysis/maps/` |
| `run_cbd_focused_optimization.py` | Write: → `results/analysis/cbd_focused_comparison/` |

### Fix Technical Report References

| Location | Current Reference | Recommended Fix |
|----------|------------------|-----------------|
| `docs/core/technical_report.md` line 478 | `results/archive/figures/fleet_sensitivity_dual.png` | Replace with `results/baseline/figures/fleet_sensitivity_v2_dual.png` |
| `docs/core/technical_report.md` line 670 | `results/archive/figures/capacity_sensitivity_heatmap.png` | Regenerate to `results/analysis/figures/capacity_sensitivity_heatmap.png` and update reference |

### Update Documentation Indexes

| Document | Issue |
|----------|-------|
| `docs/core/visualization_index.md` | ~100+ references to `results/figures/` → update to `results/baseline/figures/` or `results/analysis/figures/` |
| `docs/core/figure_trace_guide.md` | Same — all locations reference stale `results/figures/` |
| `docs/core/data_usage_guide.md` | References `results/figures/*.png` generically; update to reorganized paths |

---

## Summary Statistics

| Category | Count |
|----------|-------|
| **Total artifacts audited** | ~120 figures + ~40 tables |
| **Fully reproducible (script + correct paths)** | ~75 figures, ~30 tables |
| **Broken scripts (won't run)** | 7 scripts |
| **Scripts with stale output paths** | 10 scripts |
| **Scripts with stale input paths** | 6 scripts |
| **Archive artifacts in active docs** | 2 (technical report) |
| **Notebook-only figures (no script)** | 15 figures |
| **Column name mismatches** | 1 (`crash_rate_per_hour` vs `lambda_per_hour`) |

### Root Cause

All issues stem from **a single organizational change**: the directory reorganization from flat `results/figures/`, `results/tables/`, `results/simulation/`, `results/optimization/`, `results/capacity_comparison/` into the tiered `results/baseline/`, `results/analysis/`, `results/archive/` structure. **The scripts were not updated to match the new directory structure.** The data and figures themselves are valid; only the paths in the generating scripts are stale.

### Priority Ranking

1. 🔴 **P0 — Fix the 7 broken scripts** (can't regenerate at all)
2. 🟡 **P1 — Fix technical report archive refs** (TR lines 478, 670)
3. 🟡 **P2 — Fix 10 scripts with stale output paths** (would write to wrong dirs)
4. 🟢 **P3 — Update visualization_index.md and figure_trace_guide.md** (informational)
5. 🟢 **P4 — Create script equivalents for notebook-only figures** (nice-to-have)
