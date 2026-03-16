# Visualization Index

> Complete catalog of every generated figure in the project, organised by
> analysis stage.  For detailed data-flow traces and downstream usage see
> [`figure_trace_guide.md`](figure_trace_guide.md).

---

## Quick Reference

| Category | Count | Key Script / Notebook |
|----------|------:|-----------------------|
| Demand & EDA | 10 | `demand_modeling.py`, `02_eda_spatiotemporal.ipynb` |
| Service & Travel Models | 4 | `04_service_travel_proxy.ipynb` |
| Optimization | 5 | `run_optimization_comparison.py` |
| Simulation Experiments | 4 | `07_production_results.ipynb` |
| Verification & Validation | 4 | `06_simulation_debug.py` |
| Extended Fleet Analysis & Fleet | 3 | `run_production_v2.py` |
| CBD Analysis | 6 | `09_cbd_analysis.ipynb`, `run_cbd_focused_optimization.py` |
| Queue Analysis | 4 | `analyze_queue_metrics.py` |
| Seasonal Analysis | 3 | `analyze_seasonal_patterns.py` |
| Capacity Sensitivity | 2 | `capacity_sensitivity_analysis.py`, `generate_capacity_sensitivity_heatmap.py` |
| Distance Comparison | 4 | `run_distance_comparison_experiment.py` |
| P0 Spatial Baseline | 3 | `p0_spatial_analysis.py` |
| Publication Quality | 5 | `generate_publication_figures.py` |
| Dashboard | 1 | `generate_summary_dashboard.py` |
| **Total** | **~60** | |

---

## 1  Demand & EDA

| Figure | Description | Script / Notebook |
|--------|-------------|-------------------|
| `fig_hourly_demand.png` | 24-hour crash demand profile | `notebooks/02_eda_spatiotemporal.ipynb` |
| `fig_daily_demand.png` | Day-of-week crash volume | `notebooks/02_eda_spatiotemporal.ipynb` |
| `fig_temporal_trends.png` | Long-term crash trends 2012-2026 | `notebooks/02_eda_spatiotemporal.ipynb` |
| `fig_crash_heatmap.png` | Spatial heatmap of crash incidents | `notebooks/02_eda_spatiotemporal.ipynb` |
| `fig_precinct_density.png` | Precinct demand density choropleth | `notebooks/02_eda_spatiotemporal.ipynb` |
| `fig_firehouses_map.png` | Map of 48 Manhattan firehouses | `notebooks/02_eda_spatiotemporal.ipynb` |
| `fig_cbd_comparison.png` | CBD robustness comparison | `notebooks/02_eda_spatiotemporal.ipynb` |
| `fig_precinct_demand.png` | Precinct demand bar chart (original) | `scripts/demand_modeling.py` |
| **`precinct_demand_rates_improved.png`** | **Improved bar chart** with legend, annotations | `scripts/generate_precinct_demand_visualizations.py` |
| **`precinct_demand_heatmap.png`** | **Spatial heatmap** of precinct demand | `scripts/generate_precinct_demand_visualizations.py` |
| `fig_demand_model_fit.png` | NHPP model fit diagnostics | `scripts/demand_modeling.py` |
| `fig_hourly_rates.png` | CBD vs non-CBD lambda factors | `scripts/demand_modeling.py` |

## 2  Service & Travel Models

| Figure | Description | Script / Notebook |
|--------|-------------|-------------------|
| `distance_matrix_heatmap.png` | Haversine distance matrix heatmap | `notebooks/04_service_travel_proxy.ipynb` |
| `travel_time_by_tod.png` | Travel time by time-of-day band | `notebooks/04_service_travel_proxy.ipynb` |
| `tod_speed_factors.png` | 24-hour speed factor profile | `notebooks/04_service_travel_proxy.ipynb` |
| `service_time_distribution.png` | LogNormal service time distribution | `notebooks/04_service_travel_proxy.ipynb` |
| `nhpp_arrivals_demo.png` | NHPP arrival generation demo | `notebooks/04_service_travel_proxy.ipynb` |

## 3  Optimization

| Figure | Description | Script / Notebook |
|--------|-------------|-------------------|
| `fig_policy_comparison.png` | Policy comparison (P0, P1, P2) | `scripts/run_optimization_comparison.py` |
| `fig_tradeoff_curve.png` | RT vs coverage trade-off | `scripts/run_optimization_comparison.py` |
| `opt_allocation_comparison.png` | Allocation maps by model | `scripts/run_optimization_comparison.py` |
| `opt_inputs.png` | Optimization inputs visualization | `scripts/run_optimization_comparison.py` |
| `opt_sensitivity.png` | Objective vs fleet size | `scripts/run_optimization_comparison.py` |

## 4  Simulation Experiments

| Figure | Description | Script / Notebook |
|--------|-------------|-------------------|
| `exp1_policy_comparison.png` | Experiment 1: Policy box plots | `notebooks/07_production_results.ipynb` |
| `exp2_fleet_sensitivity.png` | Experiment 2: RT vs fleet size | `notebooks/07_production_results.ipynb` |
| `exp3_demand_sensitivity.png` | Experiment 3: RT vs demand multiplier | `notebooks/07_production_results.ipynb` |
| `exp4_service_robustness.png` | Experiment 4: RT vs service time | `notebooks/07_production_results.ipynb` |

## 5  Verification & Validation

| Figure | Description | Script / Notebook |
|--------|-------------|-------------------|
| `verification_toy_timeline.png` | Toy example timeline | `notebooks/06_simulation_debug.py` |
| `validation_p0_vs_p2.png` | Pilot 1: P0 vs P2 | `notebooks/06_simulation_debug.py` |
| `validation_sensitivity_K.png` | Pilot 2: RT vs K | `notebooks/06_simulation_debug.py` |
| `validation_sensitivity_demand.png` | Pilot 3: RT vs demand | `notebooks/06_simulation_debug.py` |

## 6  Extended Fleet Analysis & Fleet

| Figure | Description | Script / Notebook |
|--------|-------------|-------------------|
| `fleet_sensitivity_dual.png` | Dual-panel fleet sensitivity | `scripts/run_production_v2.py` |
| `response_time_distribution_by_policy.png` | RT distribution by policy | Production pipeline |
| `policy_comparison_panel_K20_cap2.png` | Staging map panel (P0/P1/P2) | Production pipeline |

## 7  CBD Analysis

| Figure | Description | Script / Notebook |
|--------|-------------|-------------------|
| `cbd_heatmap.png` | CBD crash density + firehouses | `notebooks/09_cbd_analysis.ipynb` |
| `cbd_response_comparison.png` | CBD stress RT comparison | `notebooks/09_cbd_analysis.ipynb` |
| `cbd_scenario_comparison.png` | CBD vs Manhattan scenarios | `notebooks/09_cbd_analysis.ipynb` |
| `cbd_robustness_enhanced.png` | Enhanced CBD robustness | Production pipeline |
| `cbd_equity_tradeoff_summary.png` | CBD equity-efficiency trade-off | `scripts/run_cbd_focused_optimization.py` |

## 8  Queue Analysis

| Figure | Description | Script / Notebook |
|--------|-------------|-------------------|
| `queue_comparison_by_policy.png` | Queue metrics by policy | `scripts/analyze_queue_metrics.py` |
| `queue_heatmap.png` | Queue length heatmap | `scripts/analyze_queue_metrics.py` |
| `queue_vs_demand.png` | Queue vs demand multiplier | `scripts/analyze_queue_metrics.py` |
| `queue_vs_fleet_size.png` | Queue vs fleet size | `scripts/analyze_queue_metrics.py` |

## 9  Seasonal Analysis

| Figure | Description | Script / Notebook |
|--------|-------------|-------------------|
| `seasonal_patterns.png` | Seasonal variation analysis | `scripts/analyze_seasonal_patterns.py` |
| `seasonal_decomposition.png` | Seasonal decomposition | `scripts/analyze_seasonal_patterns.py` |
| `seasonal_heatmap.png` | Month x DoW heatmap | `scripts/analyze_seasonal_patterns.py` |

## 10  Capacity Sensitivity

| Figure | Description | Script / Notebook |
|--------|-------------|-------------------|
| `capacity_sensitivity_heatmap.png` | RT by policy and capacity | `scripts/generate_capacity_sensitivity_heatmap.py` |
| `firehouse_capacity_analysis.png` | Capacity analysis detail | `scripts/capacity_sensitivity_analysis.py` |

## 11  Distance Comparison

| Figure | Description | Script / Notebook |
|--------|-------------|-------------------|
| `distance_comparison/distance_matrices_heatmap.png` | Side-by-side distance heatmaps | `scripts/run_distance_comparison_experiment.py` |
| `distance_comparison/distance_scatter.png` | Haversine vs Manhattan scatter | `scripts/run_distance_comparison_experiment.py` |
| `distance_comparison/distance_comparison_bar.png` | Performance bar chart | `scripts/run_distance_comparison_experiment.py` |
| `distance_comparison/distance_comparison_boxplot.png` | Replication box plots | `scripts/run_distance_comparison_experiment.py` |

## 12  P0 Spatial Baseline

| Figure | Description | Script / Notebook |
|--------|-------------|-------------------|
| `p0_spatial_map.png` | P0 (spatially-stratified) firehouse selections | `scripts/p0_spatial_analysis.py` |
| `p0_spatial_metrics.png` | Stratification comparison metrics | `scripts/p0_spatial_analysis.py` |
| `p0_spatial_north_south.png` | North-south distribution | `scripts/p0_spatial_analysis.py` |

## 13  Publication-Quality Figures

| Figure | Description | Script / Notebook |
|--------|-------------|-------------------|
| `pub_fig1_policy_comparison.png` | Final Figure 1 | `scripts/generate_publication_figures.py` |
| `pub_fig2_fleet_sensitivity.png` | Final Figure 2 | `scripts/generate_publication_figures.py` |
| `pub_fig3_demand_robustness.png` | Final Figure 3 | `scripts/generate_publication_figures.py` |
| `pub_fig4_service_sensitivity.png` | Final Figure 4 | `scripts/generate_publication_figures.py` |
| `pub_fig5_performance_heatmap.png` | Final Figure 5 | `scripts/generate_publication_figures.py` |

## 14  Dashboard

| Figure | Description | Script / Notebook |
|--------|-------------|-------------------|
| `project_summary_dashboard.png` | Full project summary | `scripts/generate_summary_dashboard.py` |

---

## Regeneration

All figures can be regenerated from source data.  See
[`figure_trace_guide.md`](figure_trace_guide.md) for the full list of
regeneration commands.
