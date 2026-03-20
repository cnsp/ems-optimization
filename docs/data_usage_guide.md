# Data Usage Guide — EMS Readiness Optimization

> **Last updated**: 2026-03-20  
> **Purpose**: Tell you exactly which files are current, which are legacy, and which to use for any given analysis task.

---

## Quick Rules

| Rule | Details |
|------|---------|
| **Source of truth for simulation** | `results/production_v2/` — cap=2, spatially-stratified P0, 30 replications |
| **Source of truth for optimization** | `results/optimization/` — cap=5 (Phase 3 historical), but metrics are correct |
| **Source of truth for publication tables** | `results/tables/table1_*` through `table4_*` |
| **Default capacity assumption** | **cap=2** (see DEC-010). Files with cap=5 are either legacy or part of capacity sweeps |
| **P0 means** | Spatially-stratified uniform (latitude-based). Files with `P0` without `_spatial` suffix in `capacity_comparison/` or `heatmaps/` refer to the **deprecated** index-based P0 |
| **Legacy indicator** | Any file with `_legacy` in the name, or `P0` without `_spatial` in capacity/heatmap sweeps |

---

## Folder-by-Folder File Inventory

### `results/production_v2/` — ✅ PRIMARY SOURCE OF TRUTH

This is the canonical simulation output. All files use **cap=2**, **spatially-stratified P0**, and **30 Monte Carlo replications**.

| Path | Status | Description |
|------|--------|-------------|
| `allocations/allocations_K{10..48}.csv` | ✅ CURRENT | Unit allocations for P0/P1/P2 at each K |
| `simulation/results_K{10..48}.csv` | ✅ CURRENT | Raw simulation output per K |
| `simulation/all_results_raw.csv` | ✅ CURRENT | Combined raw results across all K |
| `tables/descriptive_statistics.csv` | ✅ CURRENT | Mean RT, CI, coverage, utilization per (K, policy) |
| `tables/anova_results.csv` | ✅ CURRENT | ANOVA test results |
| `tables/posthoc_comparisons.csv` | ✅ CURRENT | Tukey HSD pairwise comparisons |
| `tables/effect_sizes.csv` | ✅ CURRENT | Cohen's d effect sizes |
| `tables/confidence_intervals.csv` | ✅ CURRENT | 95% confidence intervals |
| `tables/queue_statistics.csv` | ✅ CURRENT | Queue/utilization metrics |
| `figures/*.png` | ✅ CURRENT | All production figures (allocation maps, RT distributions, sensitivity curves) |
| `comparison_with_v1.csv` | 📊 COMPARISON | Shows how v2 (cap=2) compares to v1 (cap=5) |
| `experiment_log.txt` | ✅ CURRENT | Run metadata and parameters |

---

### `results/optimization/` — ⚠️ PHASE 3 HISTORICAL (cap=5)

These are the original Phase 3 optimization-only results. They use **cap=5** (the old default before DEC-010). The optimization metrics (objective values, coverage) are mathematically correct for cap=5 but **do not reflect the current cap=2 default**. Use `production_v2/` for cap=2 results.

| Path | Status | Description |
|------|--------|-------------|
| `allocations_K{15..48}.csv` | ⚠️ LEGACY | Allocations at cap=5 |
| `policy_comparison.csv` | ⚠️ LEGACY | Full metrics at cap=5 — correct for cap=5, not current default |
| `sensitivity_analysis.csv` | ⚠️ LEGACY | RT & coverage by K at cap=5 |
| `findings_summary.json` | ⚠️ LEGACY | Best-policy summary at cap=5 |
| `PHASE3_SUMMARY.md` / `.pdf` | ⚠️ LEGACY | Phase 3 write-up (cap=5 era). Conclusions still directionally valid |

> **Why keep these?** They document the Phase 3 milestone and remain useful for comparing cap=5 vs cap=2 outcomes.

---

### `results/tables/` — Mixed Current & Legacy

| Path | Status | Description |
|------|--------|-------------|
| `table1_baseline_comparison.csv` / `.tex` | ✅ CURRENT | Publication Table 1 — P0 vs P1 vs P2 at K=20,30,40 |
| `table2_anova_summary.csv` / `.tex` | ✅ CURRENT | Publication Table 2 — ANOVA results |
| `table3_pairwise_comparisons.csv` / `.tex` | ✅ CURRENT | Publication Table 3 — Tukey HSD |
| `table4_sensitivity_summary.csv` / `.tex` | ✅ CURRENT | Publication Table 4 — Fleet/demand sensitivity |
| `exp1_summary.csv` | ✅ CURRENT | Experiment 1 policy comparison summary |
| `exp2_pivot_rt.csv` | ✅ CURRENT | Experiment 2 fleet sensitivity pivot (current P0 only) |
| `exp3_pivot_rt.csv` | ✅ CURRENT | Experiment 3 demand sensitivity pivot |
| `exp4_pivot_rt.csv` | ✅ CURRENT | Experiment 4 service robustness pivot |
| `exp2_pivot_rt_with_legacy.csv` | 📊 COMPARISON | Fleet sensitivity with both current P0 and legacy P0 columns |
| `production_results.csv` | ✅ CURRENT | Combined production simulation results |
| `optimization_comparison.csv` | ⚠️ LEGACY | Optimization-only comparison (cap=5 era) |
| `optimization_results.csv` | ⚠️ LEGACY | Optimization-only results (cap=5 era) |
| `sensitivity_summary.csv` | ✅ CURRENT | Sensitivity analysis summary |
| `statistical_analysis.csv` | ✅ CURRENT | Statistical test results |
| `cbd_comparison.csv` | ✅ CURRENT | CBD vs non-CBD comparison |
| `cbd_robustness.csv` | ✅ CURRENT | CBD robustness analysis |
| `cbd_summary_all.csv` | ✅ CURRENT | CBD comprehensive summary |
| `queue_metrics.csv` | ✅ CURRENT | Queue performance metrics |
| `queue_anova.csv` | ✅ CURRENT | Queue ANOVA analysis |
| `queue_statistics.csv` | ✅ CURRENT | Queue descriptive stats |
| `seasonal_analysis.csv` | ✅ CURRENT | Seasonal demand patterns |
| `validation_results.csv` | ✅ CURRENT | V&V validation results |
| `anova_results.csv` | ✅ CURRENT | ANOVA (duplicate of production_v2 copy) |
| `confidence_intervals.csv` | ✅ CURRENT | CIs (from production run) |
| `confidence_intervals_notebook.csv` | ⚠️ LEGACY | CIs from older notebook run |
| `descriptive_statistics.csv` | ✅ CURRENT | Descriptive stats |
| `effect_sizes.csv` | ✅ CURRENT | Effect sizes |
| `posthoc_comparisons.csv` | ✅ CURRENT | Posthoc tests |
| `posthoc_comparisons_notebook.csv` | ⚠️ LEGACY | Posthoc from older notebook run |

---

### `results/figures/` — ✅ Mostly Current

All figures were regenerated or verified during the Phase 10 audit. Publication-quality figures use the `pub_fig*` prefix.

| Path Pattern | Status | Description |
|------|--------|-------------|
| `pub_fig1_policy_comparison.png` | ✅ CURRENT | Publication Figure 1 |
| `pub_fig2_fleet_sensitivity.png` | ✅ CURRENT | Publication Figure 2 |
| `pub_fig3_demand_robustness.png` | ✅ CURRENT | Publication Figure 3 |
| `pub_fig4_service_sensitivity.png` | ✅ CURRENT | Publication Figure 4 |
| `pub_fig5_performance_heatmap.png` | ✅ CURRENT | Publication Figure 5 |
| `fig_*` prefix files | ✅ CURRENT | Technical report figures (crash heatmap, demand, firehouses, etc.) |
| `exp1_*` through `exp4_*` | ✅ CURRENT | Experiment result plots |
| `validation_*` / `verification_*` | ✅ CURRENT | V&V output plots |
| `capacity_sensitivity_heatmap.png` | ⚠️ KNOWN ISSUE | Shows "Data format issue" — placeholder, not usable |
| `capacity_sensitivity_heatmap_notebook.png` | ✅ CURRENT | Working version from notebook |
| `fleet_sensitivity_v2_dual.png` | ✅ CURRENT | Fleet sensitivity (v2, cap=2) |
| `fleet_sensitivity_dual.png` | ⚠️ LEGACY | Older fleet sensitivity plot |
| `fleet_sensitivity_curve.png` | ⚠️ LEGACY | Older single-axis fleet sensitivity |
| `policy_comparison.png` | ✅ CURRENT | General policy comparison |
| `policy_comparison_panel_K20_cap2.png` | ✅ CURRENT | Panel figure at K=20, cap=2 |
| `optimization/*.png` | ⚠️ LEGACY | Phase 3 optimization visualizations (cap=5) |
| `cbd_*` | ✅ CURRENT | CBD analysis figures |
| `queue_*` | ✅ CURRENT | Queue analysis figures |
| `seasonal_*` | ✅ CURRENT | Seasonal pattern figures |
| `p0_spatial_*` | ✅ CURRENT | Spatial P0 analysis |
| `production_fleet_sensitivity.png` | ✅ CURRENT | Production fleet sensitivity |
| `project_summary_dashboard.png` | ✅ CURRENT | Overview dashboard |

---

### `results/capacity_comparison/` — ✅ CURRENT (Capacity Sweep)

Full capacity sensitivity sweep across cap={1,2,3,4,5} × K={20,30,40} × {P0, P0_spatial, P1, P2}. All data is current and correct.

| Path Pattern | Status | Description |
|------|--------|-------------|
| `allocation_P0_spatial_K*_cap*.csv` | ✅ CURRENT | Spatially-stratified P0 allocations |
| `allocation_P0_K*_cap*.csv` | 📊 COMPARISON | Index-based (legacy) P0 allocations — included for comparison only |
| `allocation_P1_demand_K*_cap*.csv` | ✅ CURRENT | P1 allocations across capacities |
| `allocation_P2_optimised_K*_cap*.csv` | ✅ CURRENT | P2 optimized allocations |
| `simulation_results.csv` | ✅ CURRENT | Full simulation results for K=20 sweep |
| `simulation_results_K30.csv` | ✅ CURRENT | Full simulation results for K=30 sweep |
| `full_comparison.csv` | ✅ CURRENT | Combined comparison table |
| `optimal_configurations.csv` | ✅ CURRENT | Best configurations identified |
| `*.png` figures | ✅ CURRENT | Capacity comparison visualizations |

> **Note**: Files with `P0` (no `_spatial`) are the deprecated index-based P0 included for comparison purposes. Use `P0_spatial` files for the canonical baseline.

---

### `results/heatmaps/` — ✅ CURRENT (Comprehensive Sweep)

Heatmap visualizations across K={5,10,15,20,25,30,35,40,45} × cap={1,2,3,5} × {P0, P0_spatial, P1, P2}. All generated from a single consistent run.

| Path Pattern | Status | Description |
|------|--------|-------------|
| `heatmap_K*_policyP0_spatial_cap*.png` | ✅ CURRENT | Canonical P0 heatmaps |
| `heatmap_K*_policyP0_cap*.png` | 📊 COMPARISON | Legacy P0 heatmaps (index-based, for comparison) |
| `heatmap_K*_policyP1_cap*.png` | ✅ CURRENT | P1 heatmaps |
| `heatmap_K*_policyP2_cap*.png` | ✅ CURRENT | P2 heatmaps |
| `allocations/*.csv` | ✅ CURRENT | Underlying allocation data for each heatmap |
| `generation_summary.json` | ✅ CURRENT | Metadata about the heatmap generation run |

> **Same note**: `policyP0` (without `_spatial`) = deprecated index-based P0. Use `policyP0_spatial` for the canonical baseline.

---

### `results/cbd_focused_comparison/` — ✅ CURRENT

CBD-focused optimization experiment results. Demonstrates that CBD weighting does not improve CBD RT but degrades non-CBD RT.

| Path | Status | Description |
|------|--------|-------------|
| `allocations.csv` | ✅ CURRENT | CBD-focused allocations |
| `comparison_table.csv` | ✅ CURRENT | CBD vs standard comparison |
| `*.png` figures | ✅ CURRENT | CBD comparison visualizations |
| `experiment_log.txt` | ✅ CURRENT | Experiment metadata |

---

### `results/distance_comparison/` — ✅ CURRENT

Manhattan vs Haversine distance metric comparison. Shows P2 is robust to distance metric choice.

| Path | Status | Description |
|------|--------|-------------|
| `allocation_comparison.csv` | ✅ CURRENT | Haversine vs Manhattan allocations |
| `comparison_table.csv` | ✅ CURRENT | Side-by-side metrics |
| `*.png` figures | ✅ CURRENT | Distance comparison plots |
| `experiment_log.txt` | ✅ CURRENT | Experiment metadata |

---

### `results/simulation/` — ✅ CURRENT

Simulation verification, validation pilots, and production experiment results.

| Path | Status | Description |
|------|--------|-------------|
| `verification/01_toy_example.json` | ✅ CURRENT | Verification test 1 |
| `verification/02_zero_demand.json` | ✅ CURRENT | Verification test 2 |
| `verification/03_single_unit.json` | ✅ CURRENT | Verification test 3 |
| `verification/04_extreme_demand.json` | ✅ CURRENT | Verification test 4 |
| `validation_pilot/pilot1_*.json/.csv` | ✅ CURRENT | Pilot 1: P0 vs P2 |
| `validation_pilot/pilot2_*.json/.csv` | ✅ CURRENT | Pilot 2: Fleet sensitivity |
| `validation_pilot/pilot3_*.json` | ✅ CURRENT | Pilot 3: Demand sensitivity |
| `production/exp1_*.csv` | ✅ CURRENT | Experiment 1 results |
| `production/exp2_*.csv` | ✅ CURRENT | Experiment 2 results |
| `production/exp3_*.csv` | ✅ CURRENT | Experiment 3 results |
| `production/exp4_*.csv` | ✅ CURRENT | Experiment 4 results |
| `production/experiment_summary.csv` | ✅ CURRENT | Combined summary |
| `production/experiment_log.txt` | ✅ CURRENT | Run metadata |
| `cbd_experiment/*.csv` | ✅ CURRENT | CBD experiment results |

---

### `results/maps/` — ✅ CURRENT

Static allocation maps at K=40.

| Path | Status | Description |
|------|--------|-------------|
| `map_allocation_P0_K40.png` | ✅ CURRENT | P0 spatial allocation map |
| `map_allocation_P1_K40.png` | ✅ CURRENT | P1 allocation map |
| `map_allocation_P2_K40.png` | ✅ CURRENT | P2 allocation map |

---

### Root-Level Files in `results/`

| Path | Status | Description |
|------|--------|-------------|
| `consistency_verification_report.json` | ✅ CURRENT | Automated consistency check output |
| `subfolder_audit_report.md` / `.pdf` | ✅ CURRENT | Deep audit of all subfolders |
| `file_contents_verification.md` / `.pdf` | ✅ CURRENT | File content verification results |

---

## Decision Tree: "Which File Should I Use?"

### For baseline policy comparison (P0 vs P1 vs P2):
→ **`results/production_v2/tables/descriptive_statistics.csv`**  
→ Or publication-ready: **`results/tables/table1_baseline_comparison.csv`**

### For fleet size sensitivity (how does RT change with K?):
→ **`results/tables/exp2_pivot_rt.csv`** (current P0 only)  
→ Or with legacy comparison: **`results/tables/exp2_pivot_rt_with_legacy.csv`**

### For demand sensitivity:
→ **`results/tables/exp3_pivot_rt.csv`**

### For service time robustness:
→ **`results/tables/exp4_pivot_rt.csv`**

### For statistical significance:
→ **`results/production_v2/tables/anova_results.csv`** + **`posthoc_comparisons.csv`** + **`effect_sizes.csv`**

### For capacity sensitivity analysis:
→ **`results/capacity_comparison/full_comparison.csv`**  
→ Heatmaps: **`results/heatmaps/heatmap_K*_policyP*_spatial_cap*.png`**

### For CBD analysis:
→ **`results/cbd_focused_comparison/comparison_table.csv`**  
→ Or: **`results/tables/cbd_comparison.csv`**

### For verification & validation:
→ **`results/simulation/verification/*.json`**  
→ **`results/simulation/validation_pilot/*.json`**

### For publication figures:
→ **`results/figures/pub_fig*.png`**

### For allocation maps:
→ **`results/production_v2/figures/allocation_map_K*.png`** (cap=2)  
→ Or: **`results/maps/map_allocation_P*_K40.png`**

---

## Naming Conventions

| Pattern | Meaning |
|---------|---------|
| `_legacy` suffix | Explicitly marked as historical/deprecated data |
| `P0` in `capacity_comparison/` or `heatmaps/` (without `_spatial`) | Index-based legacy P0 — for comparison only |
| `P0_spatial` or just `P0` elsewhere | Current spatially-stratified P0 |
| `cap2` / `cap=2` | Current default capacity |
| `cap5` / `cap=5` | Historical default capacity (pre-DEC-010) |
| `_notebook` suffix | Generated from older notebook run, not production pipeline |
| `pub_fig*` | Publication-quality figures |
| `table{1-4}_*` | Publication-ready tables |
| `v2` | Current production version (cap=2, spatial P0) |

---

## Key Project Decisions Affecting Data

| Decision | Impact on Files |
|----------|----------------|
| **DEC-010**: Capacity changed from 5 → 2 | `production_v2/` uses cap=2; `optimization/` still shows cap=5 |
| **DEC-011**: P0 changed to spatially-stratified | All current P0 is spatial; old index-based P0 appears as `P0_legacy` or `P0` without `_spatial` in sweeps |
| **DEC-012**: P0 nomenclature standardized | "P0" in any public/current document = spatially-stratified |
