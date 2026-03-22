---
status: ✅ CURRENT
last_updated: "2026-03-22"
verified: "Cross-checked against technical_report.md §10–11, README.md, and figure_trace_guide.md"
---
# Figure & Table Traceability

> **Purpose**: Provide a single-lookup traceability matrix for every figure and
> table referenced in the **technical report** or **README**. Each row traces
> the full chain: **script → input data → output artifact → document section**.

---

## 1. Traceability Rule

Every canonical figure or table must satisfy this chain:

```
Generator Script  →  Input Data File(s)  →  Output Artifact  →  Document Reference
```

- **Generator Script**: The Python script (or notebook) that produces the artifact.
- **Input Data**: The `data/processed/` or `results/` file(s) consumed.
- **Output Artifact**: The `.png`, `.csv`, or `.tex` file produced.
- **Document Reference**: The section in `technical_report.md`, `README.md`, or `executive_summary.md` where it appears.

If any link in the chain is broken, the artifact has **unclear provenance** and must be flagged.

---

## 2. Key Figures — Full Traceability

### 2a. Technical Report Inline Figures (Figures 1–9)

These are the numbered figures that appear inline in `docs/core/technical_report.md`.

| Fig # | Description | Generator | Input Data | Output Path | TR Section |
|-------|-------------|-----------|------------|-------------|------------|
| 1 | Policy comparison panel (P0, P1, P2 staging at K=20 cap=2) | `scripts/run_production_v2.py` | `results/baseline/allocations/allocations_K20.csv`, `data/processed/firehouses_manhattan.csv` | `results/baseline/figures/policy_comparison_panel_K20_cap2.png` | §5.4 |
| 2 | Response time distribution by policy and fleet size | `scripts/run_production_v2.py` | `results/baseline/simulation/exp1_*.csv`, `exp2_*.csv` | `results/baseline/figures/response_time_distribution_by_policy.png` | §5.5 |
| 3 | Fleet sensitivity dual-axis (RT + coverage vs K) | `scripts/run_production_v2.py` | `results/baseline/simulation/exp2_fleet_sensitivity.csv` | `results/baseline/figures/fleet_sensitivity_v2_dual.png` | §5.6 |
| 4 | CBD robustness (RT and coverage under stress) | Production analysis pipeline | `results/analysis/simulation/cbd_experiment/cbd_experiment_results.csv` | `results/analysis/figures/cbd_robustness_enhanced.png` | §5.10 |
| 5 | Queue metrics by policy (confirms zero queueing) | `scripts/analysis/analyze_queue_metrics.py` | Simulation queue logs | `results/analysis/figures/queue_comparison_by_policy.png` | §5.8 |
| 6 | Seasonal variation (monthly demand factors) | `scripts/analysis/analyze_seasonal_patterns.py` | `data/processed/crashes_manhattan.csv` | `results/analysis/figures/seasonal_patterns.png` | §5.9 |
| 7 | Distance metric comparison (Haversine vs Manhattan) | `scripts/analysis/run_distance_comparison_experiment.py` | Distance matrices, simulation results | `results/analysis/distance_comparison/distance_comparison_bar.png` | §5.10 |
| 8 | CBD equity-efficiency tradeoff | `scripts/analysis/run_cbd_focused_optimization.py` | CBD simulation results | `results/analysis/figures/cbd_equity_tradeoff_summary.png` | §5.11 |
| 9 | Capacity sensitivity heatmap (K=20, 30, 40) | `scripts/analysis/generate_capacity_sensitivity_heatmap.py` | `results/analysis/capacity_comparison/simulation_results.csv` | `results/analysis/figures/capacity_sensitivity_heatmap.png` | §5.12 |

### 2b. Publication-Quality Figures (pub_fig series)

| ID | Description | Generator | Input Data | Output Path | TR Section |
|----|-------------|-----------|------------|-------------|------------|
| pub_fig1 | Policy comparison | `scripts/analysis/generate_publication_figures.py` | `results/baseline/simulation/exp1_*.csv` | `results/figures/pub_fig1_policy_comparison.png` | §5.5 |
| pub_fig2 | Fleet sensitivity | `scripts/analysis/generate_publication_figures.py` | `results/baseline/simulation/exp2_*.csv` | `results/figures/pub_fig2_fleet_sensitivity.png` | §5.6 |
| pub_fig3 | Demand robustness | `scripts/analysis/generate_publication_figures.py` | `results/baseline/simulation/exp3_*.csv` | `results/figures/pub_fig3_demand_robustness.png` | §5.7 |
| pub_fig4 | Service sensitivity | `scripts/analysis/generate_publication_figures.py` | `results/baseline/simulation/exp4_*.csv` | `results/figures/pub_fig4_service_sensitivity.png` | §5.7 |
| pub_fig5 | Performance heatmap | `scripts/analysis/generate_publication_figures.py` | `results/baseline/tables/descriptive_statistics.csv` | `results/figures/pub_fig5_performance_heatmap.png` | §5.5 |

### 2c. Demand & EDA Figures (referenced in tech report)

| ID | Description | Generator | Input Data | Output Path | TR Section |
|----|-------------|-----------|------------|-------------|------------|
| precinct_rates | Precinct demand bar chart (improved) | `scripts/analysis/generate_precinct_demand_visualizations.py` | `data/processed/demand_lambda_precinct.csv` | `results/figures/precinct_demand_rates_improved.png` | §5.2 |
| precinct_heatmap | Precinct demand choropleth | `scripts/analysis/generate_precinct_demand_visualizations.py` | `data/processed/demand_lambda_precinct.csv`, precinct boundaries, CBD boundary | `results/figures/precinct_demand_heatmap.png` | §5.2 |
| demand_fit | NHPP model fit diagnostics | `scripts/demand_modeling.py` | `data/processed/demand_lambda_*.csv`, `data/processed/crashes_manhattan.csv` | `results/figures/fig_demand_model_fit.png` | §5.2 |

### 2d. Verification & Validation Figures

| ID | Description | Generator | Input Data | Output Path | TR Section |
|----|-------------|-----------|------------|-------------|------------|
| v_toy | Toy example timeline | `notebooks/06_simulation_debug.py` | Synthetic data | `results/figures/verification_toy_timeline.png` | §4.4.3 |
| v_p0p2 | Pilot 1: P0 vs P2 | `notebooks/06_simulation_debug.py` | `results/baseline/simulation/validation_pilot/pilot1_*.json` | `results/figures/validation_p0_vs_p2.png` | §4.4.3 |
| v_K | Pilot 2: RT vs K | `notebooks/06_simulation_debug.py` | `results/baseline/simulation/validation_pilot/pilot2_*.json` | `results/figures/validation_sensitivity_K.png` | §4.4.3 |
| v_demand | Pilot 3: RT vs demand | `notebooks/06_simulation_debug.py` | `results/baseline/simulation/validation_pilot/pilot3_*.json` | `results/figures/validation_sensitivity_demand.png` | §4.4.3 |

---

## 3. Key Tables — Full Traceability

### 3a. Publication Tables (Tables 1–4)

| Table # | Description | Generator | Input Data | Output Path(s) | TR Section |
|---------|-------------|-----------|------------|-----------------|------------|
| 1 | Baseline policy comparison | `scripts/analysis/analyze_production_results.py` | `results/baseline/simulation/exp1_*.csv` | `results/baseline/tables/table1_baseline_comparison.csv` (+ `.tex`) | §5.5 |
| 2 | ANOVA summary | `scripts/analysis/analyze_production_results.py` | Production simulation CSVs | `results/baseline/tables/table2_anova_summary.csv` (+ `.tex`) | §5.5 |
| 3 | Pairwise comparisons | `scripts/analysis/analyze_production_results.py` | Production simulation CSVs | `results/baseline/tables/table3_pairwise_comparisons.csv` (+ `.tex`) | §5.5 |
| 4 | Sensitivity summary | `scripts/analysis/analyze_production_results.py` | Production simulation CSVs | `results/baseline/tables/table4_sensitivity_summary.csv` (+ `.tex`) | §5.7 |

### 3b. Statistical Analysis Tables

| ID | Description | Generator | Output Path | TR Section |
|----|-------------|-----------|-------------|------------|
| anova | Full ANOVA results | `scripts/analysis/analyze_production_results.py` | `results/baseline/tables/anova_results.csv` | §5.5 |
| ci | 95% confidence intervals | `scripts/analysis/analyze_production_results.py` | `results/baseline/tables/confidence_intervals.csv` | §5.5 |
| effect | Cohen's d effect sizes | `scripts/analysis/analyze_production_results.py` | `results/baseline/tables/effect_sizes.csv` | §5.5 |
| desc | Descriptive statistics | `scripts/analysis/analyze_production_results.py` | `results/baseline/tables/descriptive_statistics.csv` | §5.5 |
| posthoc | Tukey HSD comparisons | `scripts/analysis/analyze_production_results.py` | `results/baseline/tables/posthoc_comparisons.csv` | §5.5 |
| sens | Sensitivity summary | `scripts/analysis/analyze_production_results.py` | `results/baseline/tables/sensitivity_summary.csv` | §5.7 |
| queue | Queue statistics | `scripts/analysis/analyze_queue_metrics.py` | `results/baseline/tables/queue_statistics.csv` | §5.8 |
| seasonal | Seasonal analysis | `scripts/analysis/analyze_seasonal_patterns.py` | `results/baseline/tables/seasonal_analysis.csv` | §5.9 |

### 3c. Experiment Pivot Tables

| ID | Description | Generator | Output Path | TR Section |
|----|-------------|-----------|-------------|------------|
| exp1 | Exp1 summary at K=20 | `scripts/analysis/analyze_production_results.py` | `results/baseline/tables/exp1_summary.csv` | §5.5 |
| exp2 | Fleet sensitivity pivot | `scripts/analysis/analyze_production_results.py` | `results/baseline/tables/exp2_pivot_rt.csv` | §5.6 |
| exp3 | Demand sensitivity pivot | `scripts/analysis/analyze_production_results.py` | `results/baseline/tables/exp3_pivot_rt.csv` | §5.7 |
| exp4 | Service robustness pivot | `scripts/analysis/analyze_production_results.py` | `results/baseline/tables/exp4_pivot_rt.csv` | §5.7 |

### 3d. Supporting Analysis Tables

| ID | Description | Generator | Output Path | TR Section |
|----|-------------|-----------|-------------|------------|
| dist_comp | Distance metric comparison | `scripts/analysis/run_distance_comparison_experiment.py` | `results/analysis/distance_comparison/comparison_table.csv` | §5.10 |
| cbd_comp | CBD-focused comparison | `scripts/analysis/run_cbd_focused_optimization.py` | `results/analysis/cbd_focused_comparison/comparison_table.csv` | §5.11 |
| cap_full | Full capacity comparison | `scripts/analysis/capacity_sensitivity_full_spectrum.py` | `results/analysis/capacity_comparison/full_comparison.csv` | §5.12 |
| cbd_exp | CBD experiment summary | `scripts/analysis/run_cbd_experiment.py` | `results/analysis/simulation/cbd_experiment/cbd_experiment_summary.csv` | §5.10 |

---

## 4. README Key Findings Table — Data Source

The headline table in `README.md`:

| Metric | Value | Source File | Column |
|--------|-------|-------------|--------|
| P0 Mean RT: 3.17 min | `results/baseline/tables/descriptive_statistics.csv` | `mean_response_time` (P0, K=20) |
| P2 Mean RT: 2.57 min | `results/baseline/tables/descriptive_statistics.csv` | `mean_response_time` (P2, K=20) |
| P0 P95 RT: 6.26 min | `results/baseline/tables/descriptive_statistics.csv` | `p95_response_time` (P0, K=20) |
| P2 P95 RT: 4.66 min | `results/baseline/tables/descriptive_statistics.csv` | `p95_response_time` (P2, K=20) |
| 8-min Coverage: 99.7% | `results/baseline/tables/descriptive_statistics.csv` | `coverage_8min` (K=20) |
| 2,700+ experiments | `results/baseline/simulation/experiment_summary.csv` | Total count |

---

## 5. Known Exceptions

These are artifacts that do not follow the standard traceability chain or have special provenance.

| Artifact | Exception Type | Notes |
|----------|----------------|-------|
| `results/figures/project_summary_dashboard.png` | Composite | Generated by `generate_summary_dashboard.py`; aggregates data from multiple sources. Not directly cited in tech report body. |
| `results/analysis/heatmaps/*.png` (~160 files) | Parametric grid | Generated by `generate_all_heatmaps.py` for exploration; not individually cited in tech report. |
| `results/analysis/maps/*.png` | Supporting | Allocation maps at K=40; generated by production pipeline. |
| Notebook-generated figures (02, 04, 07, 08, 09) | Exploratory companions | Not canonical generators. If a notebook figure is cited in tech report, the corresponding script generator is authoritative. |
| `results/archive/` (all contents) | Historical | Cap=5 era artifacts. Retained for audit trail. Do not cite in current documents. |
| `results/figures/fig_tradeoff_curve.png` | Superseded | Original trade-off curve with overlapping labels. Replaced by `response_time_coverage_tradeoff_improved.png`. |
| Capacity sensitivity heatmap (`results/figures/capacity_sensitivity_heatmap.png`) | Known data format issue | As of last regeneration, the K=20 and K=40 subplots display "Data format issue" text. The underlying simulation data in `results/analysis/capacity_comparison/` is valid. Regeneration requires matching the expected column format in `generate_capacity_sensitivity_heatmap.py`. |

---

## 6. Regeneration Quick Reference

To regenerate all canonical figures and tables from scratch:

```bash
# Step 1: Ensure processed data exists
python scripts/generate_all_data.py --verify

# Step 2: Run production pipeline (generates Exp1–4, fleet analysis, allocations, baseline figures/tables)
python scripts/run_production_v2.py

# Step 3: Run statistical analysis (generates publication tables)
python scripts/analysis/analyze_production_results.py

# Step 4: Generate publication figures
python scripts/analysis/generate_publication_figures.py

# Step 5: Generate supporting figures
python scripts/analysis/generate_precinct_demand_visualizations.py
python scripts/analysis/analyze_queue_metrics.py
python scripts/analysis/analyze_seasonal_patterns.py
python scripts/analysis/generate_capacity_sensitivity_heatmap.py
python scripts/analysis/generate_summary_dashboard.py
```

For the full regeneration sequence including all supporting analyses, see `docs/core/reproducibility_guide.md`.

---

## 7. Cross-References

| Need | Document |
|------|----------|
| Detailed figure data-flow traces | `docs/core/figure_trace_guide.md` |
| Complete visualization catalog | `docs/core/visualization_index.md` |
| Script-to-artifact registry | `docs/core/artifact_governance_map.md` |
| Data file inventory | `docs/core/source_manifest.md` |
| Which results files to use | `results/WHICH_FILES_TO_USE.md` |
