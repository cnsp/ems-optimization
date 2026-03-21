---
status: 🔄 HISTORICAL
last_updated: "2026-03-20"
note: "Preserved for project history. Contains old metrics/references in historical context. Do not use as current reference."
---
# EMS Optimization: End-to-End Notebook Output Comparison Report

**Generated:** 2026-03-15  
**Purpose:** Audit what the end-to-end notebook (`01_end_to_end_workflow.ipynb`) produces vs. what exists across the full project.

---

## Section A: What the End-to-End Notebook Currently Produces

### Visualizations (8 inline plots, 0 saved to disk)

| # | Section | Visualization | Type |
|---|---------|--------------|------|
| 1 | 3.2 Temporal demand patterns | Hourly Crash Rate + Day-of-Week Pattern (2-panel) | Bar charts |
| 2 | 3.3 Spatial demand distribution | Precinct-Level Demand Rates | Horizontal bar chart |
| 3 | 3.4 Distance matrix & coverage | Distance Matrix heatmap | Heatmap |
| 4 | 3.4 Distance matrix & coverage | Nearest-Firehouse Distance per Precinct | Bar chart |
| 5 | 4.2 Policy comparison | Response Time vs Fleet Size + Coverage vs Fleet Size (2-panel) | Line charts |
| 6 | 4.3 Trade-off | Response Time vs Coverage Trade-off | Scatter plot |
| 7 | 6.1 Simulation results | P0 vs P2 Response Time (boxplot) | Box plot |
| 8 | 6.2 Fleet sensitivity | Fleet Size Sensitivity — P2 Policy | Line chart |
| 9 | 6.3 Demand sensitivity | Demand Intensity Sensitivity — P2 Policy | Line chart |

**Note:** No figures are saved to `results/figures/` — all are `plt.show()` only.

### Tables / Summary Statistics (6 printed outputs)

| # | Section | Output | Format |
|---|---------|--------|--------|
| 1 | 1. Setup | Configuration summary (K values, capacity, tau, horizon, reps, seed) | Printed text |
| 2 | 3.1 Dataset overview | Key Statistics (total crashes, date range, duration, rates, counts) | Printed text |
| 3 | 4.1 Optimization results | Expected Response Time pivot table (policy × K) | Printed DataFrame |
| 4 | 4.1 Optimization results | Demand Coverage pivot table (policy × K) | Printed DataFrame |
| 5 | 5.3 Validation summary | Verification (4 tests) + Validation (3 pilots) pass/fail summary | Printed text |
| 6 | 7. Summary | Full results table (K, policy, RT, coverage, stations_used) + best policy per K + key findings | Printed text |

### Verification & Validation Tests (7 tests, all inline)

- 4 verification tests (toy example, zero demand, single-unit saturation, extreme demand stress)
- 3 validation pilots (P0 vs P2, fleet sensitivity, demand sensitivity)

---

## Section B: What Exists in the Full Project

### Figures in `results/figures/` (60 PNG files)

#### EDA & Demand Visualization (14 figures)
- `fig_crash_heatmap.png` — Crash density heatmap
- `fig_daily_demand.png` — Daily demand time series
- `fig_hourly_demand.png` — Hourly demand distribution
- `fig_hourly_rates.png` — Hourly arrival rates
- `fig_temporal_trends.png` — Temporal trend decomposition
- `fig_firehouses_map.png` — Firehouse locations map
- `fig_precinct_demand.png` — Precinct demand chart
- `fig_precinct_density.png` — Precinct density visualization
- `fig_demand_model_fit.png` — Input model goodness-of-fit
- `precinct_demand_heatmap.png` — Precinct-level demand heatmap
- `precinct_demand_rates_improved.png` — Improved precinct demand rates chart
- `seasonal_decomposition.png` — Seasonal decomposition plot
- `seasonal_heatmap.png` — Seasonal heatmap
- `seasonal_patterns.png` — Seasonal patterns overview

#### Service & Travel Model (4 figures)
- `distance_matrix_heatmap.png` — Distance matrix heatmap
- `service_time_distribution.png` — Service time distribution
- `tod_speed_factors.png` — Time-of-day speed factors
- `travel_time_by_tod.png` — Travel time by time of day
- `nhpp_arrivals_demo.png` — NHPP arrival process demo

#### Optimization Results (8 figures)
- `fig_policy_comparison.png` — Policy comparison summary
- `fig_tradeoff_curve.png` — Response time vs coverage trade-off
- `opt_allocation_comparison.png` — Allocation comparison across policies
- `opt_inputs.png` — Optimization input visualization
- `opt_sensitivity.png` — Optimization sensitivity analysis
- `policy_comparison_panel_K20_cap2.png` — Policy comparison panel at K=20, cap=2
- `optimization/allocation_heatmaps.png` — Allocation heatmaps by policy
- `optimization/policy_comparison.png` — Policy comparison detail

#### Production Experiment Results (4 figures)
- `exp1_policy_comparison.png` — Experiment 1: baseline policy comparison
- `exp2_fleet_sensitivity.png` — Experiment 2: fleet size sensitivity
- `exp3_demand_sensitivity.png` — Experiment 3: demand scaling sensitivity
- `exp4_service_robustness.png` — Experiment 4: service time robustness

#### Publication-Quality Figures (5 figures)
- `pub_fig1_policy_comparison.png` — Publication: Policy comparison
- `pub_fig2_fleet_sensitivity.png` — Publication: Fleet sensitivity
- `pub_fig3_demand_robustness.png` — Publication: Demand robustness
- `pub_fig4_service_sensitivity.png` — Publication: Service sensitivity
- `pub_fig5_performance_heatmap.png` — Publication: Performance heatmap

#### Verification & Validation (3 figures)
- `validation_p0_vs_p2.png` — Validation: P0 vs P2 comparison
- `validation_sensitivity_K.png` — Validation: fleet sensitivity
- `validation_sensitivity_demand.png` — Validation: demand sensitivity
- `verification_toy_timeline.png` — Verification: toy example event trace

#### Capacity Sensitivity (2 figures)
- `capacity_sensitivity_heatmap.png` — Capacity sensitivity heatmap (P0/P1/P2 × cap=1–5 at K=20 and K=40)
- `firehouse_capacity_analysis.png` — Firehouse capacity analysis

#### CBD / Robustness Analysis (6 figures)
- `cbd_equity_tradeoff_summary.png` — CBD equity trade-off
- `cbd_heatmap.png` — CBD demand heatmap
- `cbd_response_comparison.png` — CBD response time comparison
- `cbd_robustness_enhanced.png` — CBD robustness enhanced view
- `cbd_scenario_comparison.png` — CBD scenario comparison
- `fig_cbd_comparison.png` — CBD vs non-CBD comparison

#### Queue & Advanced Analysis (4 figures)
- `queue_comparison_by_policy.png` — Queue comparison by policy
- `queue_heatmap.png` — Queue heatmap
- `queue_vs_demand.png` — Queue vs demand
- `queue_vs_fleet_size.png` — Queue vs fleet size

#### P0 Spatial Analysis (3 figures)
- `p0_spatial_map.png` — P0 spatial allocation map
- `p0_spatial_metrics.png` — P0 spatial metrics
- `p0_spatial_north_south.png` — P0 north/south comparison

#### Fleet & Trade-off (3 figures)
- `fleet_sensitivity_dual.png` — Fleet sensitivity dual panel
- `response_time_coverage_tradeoff_improved.png` — Improved trade-off curve
- `response_time_coverage_tradeoff_zoomed.png` — Zoomed trade-off curve
- `response_time_distribution_by_policy.png` — RT distribution by policy

#### Summary Dashboard (1 figure)
- `project_summary_dashboard.png` — Project summary dashboard

### Tables in `results/tables/` (18 CSV files)

| File | Content |
|------|---------|
| `optimization_comparison.csv` | Policy comparison across all K values |
| `table1_baseline_comparison.csv` | Table 1: Baseline vs optimized comparison |
| `table2_anova_summary.csv` | Table 2: ANOVA results summary |
| `table3_pairwise_comparisons.csv` | Table 3: Pairwise policy comparisons |
| `table4_sensitivity_summary.csv` | Table 4: Sensitivity analysis summary |
| `descriptive_statistics.csv` | Descriptive statistics by policy & K |
| `anova_results.csv` | Full ANOVA results |
| `confidence_intervals.csv` | Confidence intervals for RT by policy |
| `effect_sizes.csv` | Cohen's d effect sizes |
| `posthoc_comparisons.csv` | Tukey HSD post-hoc comparisons |
| `exp1_summary.csv` | Experiment 1 summary |
| `exp2_pivot_rt.csv` | Experiment 2 response time pivot |
| `exp3_pivot_rt.csv` | Experiment 3 response time pivot |
| `exp4_pivot_rt.csv` | Experiment 4 response time pivot |
| `sensitivity_summary.csv` | Sensitivity summary |
| `queue_statistics.csv` | Queue statistics |
| `queue_anova.csv` | Queue ANOVA results |
| `cbd_comparison.csv` / `cbd_summary_all.csv` | CBD comparison data |
| `seasonal_analysis.csv` | Seasonal analysis results |

### Other Notebooks' Unique Outputs

| Notebook | Unique Outputs Not in End-to-End |
|----------|--------------------------------|
| `02_eda_spatiotemporal` | Crash density heatmap, monthly/seasonal patterns, CBD vs non-CBD breakdown, firehouse overlay map |
| `03_input_modeling` | Homogeneous Poisson fit, NHPP model diagnostics, goodness-of-fit tests, lambda table export |
| `04_service_travel_proxy` | Service time distribution, ToD speed factors, NHPP arrival demo, call timeline example |
| `05_optimization` | Allocation heatmaps by policy, diminishing returns analysis, spatial maps |
| `06_simulation_debug` | Verification event trace timeline, detailed pilot tables |
| `07_production_results` | 4-experiment panel figures (810 simulation results), combined summary table |
| `08_statistical_analysis` | ANOVA, Tukey HSD, Cohen's d, confidence intervals, assumption checks |
| `09_cbd_analysis` | CBD vs non-CBD comparison, CBD scenario analysis, spatial coverage analysis |

---

## Section C: Gap Analysis

### Critical Gaps (key results that should be in the end-to-end notebook)

| # | Missing Item | Source | Why Critical |
|---|-------------|--------|-------------|
| 1 | **Statistical analysis tables** (ANOVA, effect sizes, confidence intervals) | NB 08 | Required by project outline §11 for "statistically defensible comparison" |
| 2 | **CBD robustness comparison** (CBD vs non-CBD RT, coverage) | NB 09 | Required by project outline §3 and §11: "Manhattan-wide results with CBD-focused robustness" |
| 3 | **Production experiment results** (Exp 1-4 summaries) | NB 07 | The 810-simulation production run results are the primary evidence base |
| 4 | **Figures not saved to disk** | — | None of the 8 visualizations are saved to `results/figures/`, making them non-reproducible outside the notebook |
| 5 | **Queue/utilization metrics** | NB 07, scripts | Project outline §2 lists "queue length" and "unit utilization" as key MOEs |
| 6 | **Service-level metric** (% incidents within 8-min threshold) | NB 07 | Project outline §2 requires "percentage of incidents served within a defined threshold" |

### Important Gaps (useful but not essential)

| # | Missing Item | Source | Why Important |
|---|-------------|--------|--------------|
| 7 | **Crash density heatmap** (spatial map) | NB 02 | Visually demonstrates demand concentration; strong for presentations |
| 8 | **Firehouse locations map** | NB 02 | Shows candidate staging sites on map |
| 9 | **Input model fit diagnostics** (Poisson/NHPP) | NB 03 | Demonstrates demand model credibility |
| 10 | **Allocation comparison visualization** (which firehouses get units) | NB 05 | Shows spatial allocation differences between policies |
| 11 | **Response time distribution by policy** (histograms/violin) | NB 07 | Richer than just mean RT; shows distributional shape |
| 12 | **Seasonal/monthly patterns** | NB 02 | Shows temporal demand structure beyond hourly/DoW |
| 13 | **Capacity sensitivity analysis** | Scripts | Shows cap=2 is sufficient |

### Optional Gaps (detailed analysis, fine in specialized notebooks)

| # | Missing Item | Source | Why Optional |
|---|-------------|--------|-------------|
| 14 | Service time distribution visualization | NB 04 | Implementation detail |
| 15 | ToD speed factor visualization | NB 04 | Implementation detail |
| 16 | NHPP arrival demo | NB 04 | Implementation detail |
| 17 | Detailed ANOVA assumption checks (Q-Q, Levene) | NB 08 | Statistical detail |
| 18 | P0 spatial stratification analysis (latitude/grid/maximin) | Scripts | Design validation detail |
| 19 | Manhattan distance comparison | Scripts | Robustness check detail |
| 20 | Seasonal decomposition | NB 02 | Extended EDA |
| 21 | Queue heatmap & detailed queue analysis | Scripts | Advanced diagnostics |
| 22 | Publication-quality figure generation | Scripts | Separate publication pipeline |
| 23 | Project summary dashboard | Scripts | Standalone summary artifact |

---

## Section D: Recommendations for Enhancement

### Priority 1 — Critical (should be added)

#### D1. Add CBD Robustness Section (Section 6.4 or new Section 6.5)
- **What:** Run P0 and P2 simulations at K=20 with CBD/non-CBD RT breakdown
- **Content:** Table showing CBD RT vs non-CBD RT for each policy; bar chart comparison
- **Data source:** Can reuse existing simulation results or run lightweight CBD analysis
- **Effort:** ~30 lines of code + 1 visualization
- **Justification:** Project outline explicitly requires CBD robustness comparison

#### D2. Add Statistical Summary Table (Section 7 enhancement)
- **What:** Include a compact ANOVA + effect size summary for the key policy comparison
- **Content:** F-statistic, p-value, Cohen's d for P0 vs P2 at K=20
- **Data source:** Can compute from the simulation replication data already generated in the notebook
- **Effort:** ~20 lines of code + 1 formatted table
- **Justification:** Required for "statistically defensible comparison"

#### D3. Add Production Experiment Summary (new Section 6.5 or enhanced Section 7)
- **What:** Load and display the production experiment results (4 experiments, 810 runs)
- **Content:** Summary table of all 4 experiments with key metrics; reference to full results
- **Data source:** Load from `results/simulation/production/experiment_summary.csv`
- **Effort:** ~15 lines of code
- **Justification:** These are the primary evidence for the recommendation

#### D4. Save All Figures to Disk
- **What:** Add `savefig()` calls for each visualization produced
- **Content:** Save to `results/figures/e2e_*.png` with consistent naming
- **Effort:** ~10 lines (one per figure)
- **Justification:** Reproducibility; figures should be available outside notebook execution

#### D5. Add Queue/Utilization Metrics
- **What:** Add queue length and utilization statistics to the simulation summary
- **Content:** Print mean queue length and unit utilization alongside response time
- **Effort:** ~10 lines (data already in simulation output)
- **Justification:** Listed as key MOEs in the project outline

### Priority 2 — Important (recommended)

#### D6. Add Crash Density Heatmap (Section 3 enhancement)
- **What:** Add a spatial heatmap of crash density across Manhattan precincts
- **Effort:** ~15 lines using existing precinct GeoDataFrame
- **Justification:** Strong visual for spatial demand understanding

#### D7. Add Allocation Comparison Visualization (Section 4 enhancement)
- **What:** Show which firehouses receive units under P0 vs P2 (side-by-side bar or map)
- **Effort:** ~20 lines
- **Justification:** Makes the optimization tangible — what actually changes

#### D8. Add Input Model Summary (Section 3 enhancement)
- **What:** Brief NHPP model summary with hourly rates plot and precinct rates
- **Effort:** ~15 lines
- **Justification:** Closes the "input modeling" gap in the end-to-end narrative

### Priority 3 — Nice to Have

#### D9. Add Response Time Distribution Plot
- **What:** Histogram or violin plot of response times by policy (not just box plot)
- **Effort:** ~10 lines

#### D10. Add Monthly/Seasonal Pattern
- **What:** Add monthly crash volume chart to EDA section
- **Effort:** ~10 lines

---

### Summary Score Card

| Category | End-to-End NB | Full Project | Coverage |
|----------|--------------|-------------|----------|
| Inline visualizations | 8-9 | 60+ figures | ~14% |
| Saved figures | 0 | 60 | 0% |
| Summary tables | 6 (printed) | 18+ CSV tables | ~33% |
| Statistical analysis | None | ANOVA, effect sizes, CIs, post-hoc | 0% |
| CBD robustness | None | Full CBD analysis | 0% |
| Queue/utilization metrics | None | Queue stats, heatmaps | 0% |
| Verification & validation | Complete (7/7 tests) | Same | 100% |
| Optimization comparison | Complete (5 policies × 4 K values) | Same + more K values | ~80% |

### Estimated Enhancement Effort

| Priority | Items | Estimated Lines of Code | Estimated Runtime Impact |
|----------|-------|------------------------|------------------------|
| Critical (P1) | D1–D5 | ~85 lines | +30–60s (CBD simulation) |
| Important (P2) | D6–D8 | ~50 lines | Negligible |
| Nice-to-have (P3) | D9–D10 | ~20 lines | Negligible |
| **Total** | **10 items** | **~155 lines** | **+30–60s** |

### Conclusion

The end-to-end notebook covers the **core workflow** well — data loading, EDA, optimization, simulation V&V, and results summary. However, it has **significant gaps** in three areas required by the project outline:

1. **No statistical analysis** (ANOVA, effect sizes, confidence intervals)
2. **No CBD robustness comparison** (explicitly required)
3. **No production experiment results** (the 810-run evidence base is not referenced)
4. **No figures saved to disk** (reproducibility concern)

The notebook currently functions as a **demonstration workflow** rather than a **comprehensive results showcase**. Adding the 5 critical items (~85 lines of code) would transform it into a truly end-to-end deliverable that matches the project outline's requirements.
