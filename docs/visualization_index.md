---
status: ✅ CURRENT
last_updated: "2026-03-20"
verified: "All metrics, code references, and nomenclature are current as of March 2026"
---
# Visualization Index

> Complete catalog of every generated figure in the project, organised by
> analysis stage.  For detailed data-flow traces and downstream usage see
> [`figure_trace_guide.md`](figure_trace_guide.md).

---

## Quick Reference

| Category | Count | Location | Key Script / Notebook |
|----------|------:|----------|-----------------------|
| Demand & EDA | 13 | `results/figures/` | `demand_modeling.py`, `02_eda_spatiotemporal.ipynb` |
| Service & Travel Models | 5 | `results/figures/` | `04_service_travel_proxy.ipynb` |
| Optimization | 7 | `results/figures/`, `results/figures/optimization/` | `run_optimization_comparison.py` |
| Simulation Experiments | 4 | `results/figures/` | `07_production_results.ipynb` |
| Verification & Validation | 4 | `results/figures/` | `06_simulation_debug.py` |
| Extended Fleet Analysis | 7 | `results/figures/` | `scripts/run_production_v2.py` |
| Extended Fleet Analysis (V2) | 12 | `results/baseline/production_v2/figures/` | `scripts/run_production_v2.py` |
| CBD Analysis | 5 | `results/figures/` | `09_cbd_analysis.ipynb` |
| CBD Focused Comparison | 3 | `results/analysis/cbd_focused_comparison/` | `run_cbd_focused_optimization.py` |
| Queue Analysis | 5 | `results/figures/` | `analyze_queue_metrics.py` |
| Seasonal Analysis | 3 | `results/figures/` | `analyze_seasonal_patterns.py` |
| Capacity Sensitivity | 2 | `results/figures/` | `capacity_sensitivity_analysis.py`, `generate_capacity_sensitivity_heatmap.py` |
| Capacity Comparison | 21 | `results/analysis/capacity_comparison/` | `capacity_sensitivity_analysis.py` |
| Distance Comparison | 4 | `results/analysis/distance_comparison/` | `run_distance_comparison_experiment.py` |
| P0 Spatial Baseline | 4 | `results/figures/` | `p0_spatial_analysis.py` |
| Publication Quality | 5 | `results/figures/` | `generate_publication_figures.py` |
| Dashboard | 1 | `results/figures/` | `generate_summary_dashboard.py` |
| Response Time Trade-off | 3 | `results/figures/` | `generate_publication_figures.py` |
| Allocation Maps | 3 | `results/analysis/maps/` | Production pipeline |
| Statistical | 1 | `results/figures/` | Production pipeline |
| Heatmaps (parametric grid) | ~160 | `results/analysis/heatmaps/` | `generate_capacity_sensitivity_heatmap.py` |
| **Total** | **~280** | | |

---

## 1  Demand & EDA

| Figure | Path | Description | Script / Notebook |
|--------|------|-------------|-------------------|
| `fig_hourly_demand.png` | `results/figures/` | 24-hour crash demand profile | `notebooks/02_eda_spatiotemporal.ipynb` |
| `fig_daily_demand.png` | `results/figures/` | Day-of-week crash volume | `notebooks/02_eda_spatiotemporal.ipynb` |
| `fig_temporal_trends.png` | `results/figures/` | Long-term crash trends 2012-2026 | `notebooks/02_eda_spatiotemporal.ipynb` |
| `fig_crash_heatmap.png` | `results/figures/` | Spatial heatmap of crash incidents | `notebooks/02_eda_spatiotemporal.ipynb` |
| `fig_precinct_density.png` | `results/figures/` | Precinct demand density choropleth | `notebooks/02_eda_spatiotemporal.ipynb` |
| `fig_firehouses_map.png` | `results/figures/` | Map of 48 Manhattan firehouses | `notebooks/02_eda_spatiotemporal.ipynb` |
| `fig_cbd_comparison.png` | `results/figures/` | CBD robustness comparison | `notebooks/02_eda_spatiotemporal.ipynb` |
| `fig_precinct_demand.png` | `results/figures/` | Precinct demand bar chart (original) | `scripts/demand_modeling.py` |
| `precinct_demand_rates.png` | `results/figures/` | Basic precinct demand rates bar chart | `scripts/generate_precinct_demand_visualizations.py` |
| `precinct_demand_rates_improved.png` | `results/figures/` | Improved bar chart with legend, annotations | `scripts/generate_precinct_demand_visualizations.py` |
| `precinct_demand_heatmap.png` | `results/figures/` | Spatial heatmap of precinct demand | `scripts/generate_precinct_demand_visualizations.py` |
| `fig_demand_model_fit.png` | `results/figures/` | NHPP model fit diagnostics | `scripts/demand_modeling.py` |
| `fig_hourly_rates.png` | `results/figures/` | CBD vs non-CBD lambda factors | `scripts/demand_modeling.py` |
| `temporal_demand_patterns.png` | `results/figures/` | Temporal demand pattern overview | Production pipeline |

## 2  Service & Travel Models

| Figure | Path | Description | Script / Notebook |
|--------|------|-------------|-------------------|
| `distance_matrix_heatmap.png` | `results/figures/` | Haversine distance matrix heatmap | `notebooks/04_service_travel_proxy.ipynb` |
| `distance_matrix_coverage.png` | `results/figures/` | Distance matrix coverage visualization | `notebooks/04_service_travel_proxy.ipynb` |
| `travel_time_by_tod.png` | `results/figures/` | Travel time by time-of-day band | `notebooks/04_service_travel_proxy.ipynb` |
| `tod_speed_factors.png` | `results/figures/` | 24-hour speed factor profile | `notebooks/04_service_travel_proxy.ipynb` |
| `service_time_distribution.png` | `results/figures/` | LogNormal service time distribution | `notebooks/04_service_travel_proxy.ipynb` |
| `nhpp_arrivals_demo.png` | `results/figures/` | NHPP arrival generation demo | `notebooks/04_service_travel_proxy.ipynb` |

## 3  Optimization

| Figure | Path | Description | Script / Notebook |
|--------|------|-------------|-------------------|
| `fig_policy_comparison.png` | `results/figures/` | Policy comparison (P0, P1, P2) | `scripts/run_optimization_comparison.py` |
| `fig_tradeoff_curve.png` | `results/figures/` | RT vs coverage trade-off | `scripts/run_optimization_comparison.py` |
| `opt_allocation_comparison.png` | `results/figures/` | Allocation maps by model | `scripts/run_optimization_comparison.py` |
| `opt_inputs.png` | `results/figures/` | Optimization inputs visualization | `scripts/run_optimization_comparison.py` |
| `opt_sensitivity.png` | `results/figures/` | Objective vs fleet size | `scripts/run_optimization_comparison.py` |
| `policy_comparison.png` | `results/figures/` | Alternative policy comparison chart | Production pipeline |
| `allocation_heatmaps.png` | `results/figures/optimization/` | Optimization allocation heatmaps | `scripts/run_optimization_comparison.py` |
| `policy_comparison.png` | `results/figures/optimization/` | Optimization-specific policy comparison | `scripts/run_optimization_comparison.py` |

## 4  Simulation Experiments

| Figure | Path | Description | Script / Notebook |
|--------|------|-------------|-------------------|
| `exp1_policy_comparison.png` | `results/figures/` | Experiment 1: Policy box plots | `notebooks/07_production_results.ipynb` |
| `exp2_fleet_sensitivity.png` | `results/figures/` | Experiment 2: RT vs fleet size | `notebooks/07_production_results.ipynb` |
| `exp3_demand_sensitivity.png` | `results/figures/` | Experiment 3: RT vs demand multiplier | `notebooks/07_production_results.ipynb` |
| `exp4_service_robustness.png` | `results/figures/` | Experiment 4: RT vs service time | `notebooks/07_production_results.ipynb` |

## 5  Verification & Validation

| Figure | Path | Description | Script / Notebook |
|--------|------|-------------|-------------------|
| `verification_toy_timeline.png` | `results/figures/` | Toy example timeline | `notebooks/06_simulation_debug.py` |
| `validation_p0_vs_p2.png` | `results/figures/` | Pilot 1: P0 vs P2 | `notebooks/06_simulation_debug.py` |
| `validation_sensitivity_K.png` | `results/figures/` | Pilot 2: RT vs K | `notebooks/06_simulation_debug.py` |
| `validation_sensitivity_demand.png` | `results/figures/` | Pilot 3: RT vs demand | `notebooks/06_simulation_debug.py` |

## 6  Extended Fleet Analysis

### 6a  Summary figures (`results/figures/`)

| Figure | Path | Description | Script / Notebook |
|--------|------|-------------|-------------------|
| `fleet_sensitivity_dual.png` | `results/figures/` | Dual-panel fleet sensitivity | `scripts/run_production_v2.py` |
| `fleet_sensitivity_curve.png` | `results/figures/` | Fleet sensitivity single curve | `scripts/run_production_v2.py` |
| `fleet_sensitivity_v2_dual.png` | `results/figures/` | V2 dual-panel fleet sensitivity | `scripts/run_production_v2.py` |
| `production_fleet_sensitivity.png` | `results/figures/` | Production fleet sensitivity chart | `scripts/run_production_v2.py` |
| `demand_sensitivity_curve.png` | `results/figures/` | Demand sensitivity curve | Production pipeline |
| `response_time_distribution_by_policy.png` | `results/figures/` | RT distribution by policy | Production pipeline |
| `policy_comparison_panel_K20_cap2.png` | `results/figures/` | Staging map panel (P0/P1/P2) | Production pipeline |
| `allocation_comparison_K20.png` | `results/figures/` | Allocation comparison for K=20 | Production pipeline |

### 6b  Extended fleet detail (`results/baseline/production_v2/figures/`)

| Figure | Path | Description | Script / Notebook |
|--------|------|-------------|-------------------|
| `allocation_map_K20.png` | `results/baseline/production_v2/figures/` | Allocation map at K=20 | `scripts/run_production_v2.py` |
| `allocation_map_K30.png` | `results/baseline/production_v2/figures/` | Allocation map at K=30 | `scripts/run_production_v2.py` |
| `allocation_map_K40.png` | `results/baseline/production_v2/figures/` | Allocation map at K=40 | `scripts/run_production_v2.py` |
| `coverage_vs_K.png` | `results/baseline/production_v2/figures/` | Coverage vs fleet size | `scripts/run_production_v2.py` |
| `effect_sizes.png` | `results/baseline/production_v2/figures/` | Statistical effect sizes | `scripts/run_production_v2.py` |
| `mean_rt_vs_K.png` | `results/baseline/production_v2/figures/` | Mean response time vs fleet size | `scripts/run_production_v2.py` |
| `p95_rt_vs_K.png` | `results/baseline/production_v2/figures/` | P95 response time vs fleet size | `scripts/run_production_v2.py` |
| `queue_metrics_vs_K.png` | `results/baseline/production_v2/figures/` | Queue metrics vs fleet size | `scripts/run_production_v2.py` |
| `rt_distribution_K20.png` | `results/baseline/production_v2/figures/` | RT distribution at K=20 | `scripts/run_production_v2.py` |
| `rt_distribution_K30.png` | `results/baseline/production_v2/figures/` | RT distribution at K=30 | `scripts/run_production_v2.py` |
| `rt_distribution_K40.png` | `results/baseline/production_v2/figures/` | RT distribution at K=40 | `scripts/run_production_v2.py` |
| `utilization_vs_K.png` | `results/baseline/production_v2/figures/` | Unit utilization vs fleet size | `scripts/run_production_v2.py` |

## 7  CBD Analysis

### 7a  Main CBD figures (`results/figures/`)

| Figure | Path | Description | Script / Notebook |
|--------|------|-------------|-------------------|
| `cbd_heatmap.png` | `results/figures/` | CBD crash density + firehouses | `notebooks/09_cbd_analysis.ipynb` |
| `cbd_response_comparison.png` | `results/figures/` | CBD stress RT comparison | `notebooks/09_cbd_analysis.ipynb` |
| `cbd_scenario_comparison.png` | `results/figures/` | CBD vs Manhattan scenarios | `notebooks/09_cbd_analysis.ipynb` |
| `cbd_robustness.png` | `results/figures/` | CBD robustness analysis (basic) | Production pipeline |
| `cbd_robustness_enhanced.png` | `results/figures/` | Enhanced CBD robustness | Production pipeline |
| `cbd_equity_tradeoff_summary.png` | `results/figures/` | CBD equity-efficiency trade-off summary | `scripts/run_cbd_focused_optimization.py` |

### 7b  CBD focused comparison (`results/analysis/cbd_focused_comparison/`)

| Figure | Path | Description | Script / Notebook |
|--------|------|-------------|-------------------|
| `cbd_focused_comparison.png` | `results/analysis/cbd_focused_comparison/` | CBD-focused RT comparison bar chart | `scripts/run_cbd_focused_optimization.py` |
| `allocation_comparison.png` | `results/analysis/cbd_focused_comparison/` | CBD allocation distribution comparison | `scripts/run_cbd_focused_optimization.py` |
| `equity_tradeoff.png` | `results/analysis/cbd_focused_comparison/` | CBD vs non-CBD equity trade-off | `scripts/run_cbd_focused_optimization.py` |

## 8  Queue Analysis

| Figure | Path | Description | Script / Notebook |
|--------|------|-------------|-------------------|
| `queue_comparison_by_policy.png` | `results/figures/` | Queue metrics by policy | `scripts/analyze_queue_metrics.py` |
| `queue_heatmap.png` | `results/figures/` | Queue length heatmap | `scripts/analyze_queue_metrics.py` |
| `queue_metrics.png` | `results/figures/` | Queue metrics overview | `scripts/analyze_queue_metrics.py` |
| `queue_vs_demand.png` | `results/figures/` | Queue vs demand multiplier | `scripts/analyze_queue_metrics.py` |
| `queue_vs_fleet_size.png` | `results/figures/` | Queue vs fleet size | `scripts/analyze_queue_metrics.py` |

## 9  Seasonal Analysis

| Figure | Path | Description | Script / Notebook |
|--------|------|-------------|-------------------|
| `seasonal_patterns.png` | `results/figures/` | Seasonal variation analysis | `scripts/analyze_seasonal_patterns.py` |
| `seasonal_decomposition.png` | `results/figures/` | Seasonal decomposition | `scripts/analyze_seasonal_patterns.py` |
| `seasonal_heatmap.png` | `results/figures/` | Month x DoW heatmap | `scripts/analyze_seasonal_patterns.py` |

## 10  Capacity Sensitivity

### 10a  Summary figures (`results/figures/`)

| Figure | Path | Description | Script / Notebook |
|--------|------|-------------|-------------------|
| `capacity_sensitivity_heatmap.png` | `results/figures/` | RT by policy and capacity | `scripts/generate_capacity_sensitivity_heatmap.py` |
| `capacity_sensitivity_heatmap_notebook.png` | `results/figures/` | RT heatmap (notebook variant) | Notebook pipeline |
| `firehouse_capacity_analysis.png` | `results/figures/` | Capacity analysis detail | `scripts/capacity_sensitivity_analysis.py` |

### 10b  Capacity comparison detail (`results/analysis/capacity_comparison/`)

| Figure | Path | Description | Script / Notebook |
|--------|------|-------------|-------------------|
| `allocation_comparison.png` | `results/analysis/capacity_comparison/` | Allocation comparison overview | `scripts/capacity_sensitivity_analysis.py` |
| `allocation_comparison_K20.png` | `results/analysis/capacity_comparison/` | Allocation comparison at K=20 | `scripts/capacity_sensitivity_analysis.py` |
| `allocation_comparison_K40.png` | `results/analysis/capacity_comparison/` | Allocation comparison at K=40 | `scripts/capacity_sensitivity_analysis.py` |
| `cbd_distribution.png` | `results/analysis/capacity_comparison/` | CBD unit distribution | `scripts/capacity_sensitivity_analysis.py` |
| `cbd_distribution_K20.png` | `results/analysis/capacity_comparison/` | CBD distribution at K=20 | `scripts/capacity_sensitivity_analysis.py` |
| `cbd_distribution_K40.png` | `results/analysis/capacity_comparison/` | CBD distribution at K=40 | `scripts/capacity_sensitivity_analysis.py` |
| `concentration_analysis.png` | `results/analysis/capacity_comparison/` | Unit concentration analysis | `scripts/capacity_sensitivity_analysis.py` |
| `concentration_analysis_K20.png` | `results/analysis/capacity_comparison/` | Concentration at K=20 | `scripts/capacity_sensitivity_analysis.py` |
| `concentration_analysis_K40.png` | `results/analysis/capacity_comparison/` | Concentration at K=40 | `scripts/capacity_sensitivity_analysis.py` |
| `full_spectrum_summary.png` | `results/analysis/capacity_comparison/` | Combined 6-panel summary figure | `scripts/capacity_sensitivity_analysis.py` |
| `max_units_vs_capacity_K20.png` | `results/analysis/capacity_comparison/` | Max units per firehouse at K=20 | `scripts/capacity_sensitivity_analysis.py` |
| `max_units_vs_capacity_K40.png` | `results/analysis/capacity_comparison/` | Max units per firehouse at K=40 | `scripts/capacity_sensitivity_analysis.py` |
| `performance_comparison.png` | `results/analysis/capacity_comparison/` | Performance comparison overview | `scripts/capacity_sensitivity_analysis.py` |
| `performance_comparison_K20.png` | `results/analysis/capacity_comparison/` | Performance at K=20 | `scripts/capacity_sensitivity_analysis.py` |
| `performance_comparison_K40.png` | `results/analysis/capacity_comparison/` | Performance at K=40 | `scripts/capacity_sensitivity_analysis.py` |
| `performance_vs_capacity_K20.png` | `results/analysis/capacity_comparison/` | Performance metric curves at K=20 | `scripts/capacity_sensitivity_analysis.py` |
| `performance_vs_capacity_K40.png` | `results/analysis/capacity_comparison/` | Performance metric curves at K=40 | `scripts/capacity_sensitivity_analysis.py` |
| `rt_heatmap_K20.png` | `results/analysis/capacity_comparison/` | Policy x capacity RT heatmap at K=20 | `scripts/capacity_sensitivity_analysis.py` |
| `rt_heatmap_K40.png` | `results/analysis/capacity_comparison/` | Policy x capacity RT heatmap at K=40 | `scripts/capacity_sensitivity_analysis.py` |
| `tradeoff_dispersion_rt_K20.png` | `results/analysis/capacity_comparison/` | Firehouses used vs mean RT at K=20 | `scripts/capacity_sensitivity_analysis.py` |
| `tradeoff_dispersion_rt_K40.png` | `results/analysis/capacity_comparison/` | Firehouses used vs mean RT at K=40 | `scripts/capacity_sensitivity_analysis.py` |

## 11  Distance Comparison

| Figure | Path | Description | Script / Notebook |
|--------|------|-------------|-------------------|
| `distance_matrices_heatmap.png` | `results/analysis/distance_comparison/` | Side-by-side distance heatmaps | `scripts/run_distance_comparison_experiment.py` |
| `distance_scatter.png` | `results/analysis/distance_comparison/` | Haversine vs Manhattan scatter | `scripts/run_distance_comparison_experiment.py` |
| `distance_comparison_bar.png` | `results/analysis/distance_comparison/` | Performance bar chart | `scripts/run_distance_comparison_experiment.py` |
| `distance_comparison_boxplot.png` | `results/analysis/distance_comparison/` | Replication box plots | `scripts/run_distance_comparison_experiment.py` |

## 12  P0 Spatial Baseline

| Figure | Path | Description | Script / Notebook |
|--------|------|-------------|-------------------|
| `p0_spatial_map.png` | `results/figures/` | P0 (spatially-stratified) firehouse selections | `scripts/p0_spatial_analysis.py` |
| `p0_spatial_metrics.png` | `results/figures/` | Stratification comparison metrics | `scripts/p0_spatial_analysis.py` |
| `p0_spatial_north_south.png` | `results/figures/` | North-south distribution | `scripts/p0_spatial_analysis.py` |
| `p0_vs_p2_response_time.png` | `results/figures/` | P0 vs P2 response time comparison | `scripts/p0_spatial_analysis.py` |

## 13  Publication-Quality Figures

| Figure | Path | Description | Script / Notebook |
|--------|------|-------------|-------------------|
| `pub_fig1_policy_comparison.png` | `results/figures/` | Publication: Policy comparison | `scripts/generate_publication_figures.py` |
| `pub_fig2_fleet_sensitivity.png` | `results/figures/` | Publication: Fleet sensitivity | `scripts/generate_publication_figures.py` |
| `pub_fig3_demand_robustness.png` | `results/figures/` | Publication: Demand robustness | `scripts/generate_publication_figures.py` |
| `pub_fig4_service_sensitivity.png` | `results/figures/` | Publication: Service sensitivity | `scripts/generate_publication_figures.py` |
| `pub_fig5_performance_heatmap.png` | `results/figures/` | Publication: Performance heatmap | `scripts/generate_publication_figures.py` |

## 14  Response Time Trade-off

| Figure | Path | Description | Script / Notebook |
|--------|------|-------------|-------------------|
| `response_time_coverage_tradeoff.png` | `results/figures/` | RT vs coverage trade-off (original) | `scripts/generate_publication_figures.py` |
| `response_time_coverage_tradeoff_improved.png` | `results/figures/` | Improved RT vs coverage with data table | `scripts/generate_publication_figures.py` |
| `response_time_coverage_tradeoff_zoomed.png` | `results/figures/` | Zoomed high-performance region | `scripts/generate_publication_figures.py` |

## 15  Statistical Analysis

| Figure | Path | Description | Script / Notebook |
|--------|------|-------------|-------------------|
| `statistical_effect_sizes.png` | `results/figures/` | Effect sizes across experiments | Production pipeline |

## 16  Allocation Maps

| Figure | Path | Description | Script / Notebook |
|--------|------|-------------|-------------------|
| `map_allocation_P0_K40.png` | `results/analysis/maps/` | P0 allocation map at K=40 | Production pipeline |
| `map_allocation_P1_K40.png` | `results/analysis/maps/` | P1 allocation map at K=40 | Production pipeline |
| `map_allocation_P2_K40.png` | `results/analysis/maps/` | P2 allocation map at K=40 | Production pipeline |

## 17  Dashboard

| Figure | Path | Description | Script / Notebook |
|--------|------|-------------|-------------------|
| `project_summary_dashboard.png` | `results/figures/` | Full project summary | `scripts/generate_summary_dashboard.py` |

## 18  Heatmaps (Parametric Grid)

Systematic allocation heatmaps covering all combinations of fleet size, policy, and capacity.

**Location:** `results/analysis/heatmaps/`

**Naming convention:** `heatmap_K{k}_policy{policy}_cap{capacity}.png`

- **Fleet sizes (K):** 5, 10, 15, 20, 25, 30, 35, 40, 45
- **Policies:** P0, P0_spatial, P1, P2
- **Capacities:** 1, 2, 3, 5

| Example | Description |
|---------|-------------|
| `heatmap_K20_policyP2_cap2.png` | Optimized allocation (P2), 20 units, capacity 2 |
| `heatmap_K10_policyP0_spatial_cap1.png` | Spatial baseline (P0), 10 units, capacity 1 |
| `heatmap_K40_policyP1_cap5.png` | Demand-proportional (P1), 40 units, capacity 5 |

Corresponding allocation CSVs are stored in `results/analysis/heatmaps/allocations/`.

---

## Regeneration

All figures can be regenerated from source data.  See
[`figure_trace_guide.md`](figure_trace_guide.md) for the full list of
regeneration commands.
