---
status: 📋 REFERENCE
last_updated: "2026-03-20"
verified: "Specialized analysis document. Cross-reference with current production results."
---
# File Inventory — EMS Readiness Optimization Project

> Generated: 2026-03-15 | Version: 1.3.0 | Total tracked files in remote: **230+** | Total local files: **240+**

---

## Phase Deliverable Checklist

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 1 | Data Processing & EDA | Complete |
| Phase 2 | Demand & Service Modeling (NHPP) | Complete |
| Phase 3 | Optimization Models (P0, P1, P2) | Complete |
| Phase 4 | DES Simulation with V&V (39 tests) | Complete |
| Phase 5 | Experimental Design & Production Runs (1,440 sims) | Complete |
| Phase 6 | Comprehensive Statistical Analysis | Complete |
| Phase 7 | Final Report & Documentation | Complete |
| Phase 8 | Alternative Analyses & Extensions | Complete |
| Phase 9 | Capacity & Baseline Improvements | Complete |

---

## Directory Structure & File Inventory

### `configs/` — Configuration Files
| File | Size | Description |
|------|------|-------------|
| `demand.yaml` | 856 B | NHPP demand model parameters |
| `optimization.yaml` | 960 B | MIP solver and unit-count settings (capacity=2 default) |
| `service.yaml` | 1.5 KB | Travel time and service time config |
| `simulation.yaml` | 1.1 KB | DES engine and batch runner settings |
| `cbd_scenario.yaml` | ~500 B | CBD robustness experiment config |

### `data/raw/` — Raw Input Data
| File | Size | Tracked | Description |
|------|------|---------|-------------|
| `FDNY_Firehouse_Listing_20260223.csv` | 34 KB | | 219 FDNY firehouses |
| `FDNY_Firehouse_Listing_Data_Dictionary.xlsx` | 66 KB | | Firehouse field definitions |
| `Motor_Vehicle_Collisions_-_Crashes_20260223.csv` | 536 MB | No — | 2.24M crash records (too large) |
| `Motor_Vehicle_Collisions_Data_Dictionary.xlsx` | 96 KB | | Crash field definitions |
| `Police_Precincts_20260223.csv` | 3.6 MB | No — | 78 precinct boundaries (large) |
| `Police_Precincts_Data_Dictionary.xlsx` | 62 KB | | Precinct field definitions |
| `manhattan_boundary.geojson` | 247 KB | | Manhattan polygon boundary |
| `cbd_boundary.geojson` | 101 KB | | CBD/Congestion Relief Zone boundary |
| `nyc_borough_boundaries.geojson` | 3.1 MB | | All 5 NYC borough boundaries |

### `data/processed/` — Processed Data
| File | Size | Tracked | Description |
|------|------|---------|-------------|
| `crashes_manhattan.csv` | 99 MB | No — | Filtered Manhattan crashes (large) |
| `crashes_manhattan.parquet` | 15 MB | No — | Parquet version of above |
| `demand_lambda_hourly.csv` | 1.9 KB | | Hourly λ factors (24 hours) |
| `demand_lambda_dow.csv` | 653 B | | Day-of-week λ factors |
| `demand_lambda_precinct.csv` | 1.7 KB | | Precinct-level λ rates |
| `demand_model_summary.json` | 696 B | | Demand model summary stats |
| `distance_matrix_firehouse_precinct.csv` | 27 KB | | 48×30 Haversine distance matrix |
| `distance_matrix_firehouse_precinct_manhattan.csv` | 27 KB | | 48×30 Manhattan distance matrix |
| `firehouses_clean.csv` | 32 KB | | All cleaned firehouses |
| `firehouses_manhattan.csv` | 7.1 KB | | 48 Manhattan firehouses |
| `precincts_manhattan.geojson` | 640 KB | | 30 Manhattan precincts |

### `src/ems_readiness/` — Source Code (8,500+ lines total)
| Module | Files | Description |
|--------|-------|-------------|
| `__init__.py` | 1 | Package metadata (v0.6.0) |
| `demand/` | `__init__.py`, `arrival_generator.py` | NHPP arrival generation (thinning algorithm) |
| `service/` | `__init__.py`, `travel_time.py`, `service_time.py` | Travel proxy & LogNormal service time |
| `optimization/` | `__init__.py`, `models.py`, `policies.py`, `allocator.py` | MIP formulations (incl. CBD-focused, capacity-aware) & baseline policies (incl. spatially-stratified) |
| `simulation/` | `__init__.py`, `engine.py`, `entities.py`, `resources.py`, `dispatcher.py`, `metrics.py`, `runner.py` | SimPy DES engine with batch runner |
| `utils/` | `__init__.py`, `distance.py` | Haversine & Manhattan distance calculations |

### `scripts/` — Automation Scripts (24 scripts)
| File | Phase | Description |
|------|-------|-------------|
| `data_audit.py` | 2 | Data quality audit pipeline |
| `audit_step1_boundaries.py` | 2 | Boundary file validation |
| `audit_step2_firehouses.py` | 2 | Firehouse data validation |
| `audit_step3_precincts.py` | 2 | Precinct data validation |
| `audit_step4_crashes.py` | 2 | Crash data validation |
| `demand_modeling.py` | 2 | NHPP demand model fitting |
| `run_optimization_comparison.py` | 3 | Multi-model optimization comparison |
| `run_verification.py` | 5 | Simulation verification tests |
| `run_validation_pilots.py` | 5 | Validation pilot experiments |
| `run_production_experiments.py` | 6 | Full 1,440-run production experiments |
| `analyze_production_results.py` | 6 | Production result analysis |
| `generate_publication_figures.py` | 6 | Publication-quality figure generation |
| `generate_summary_dashboard.py` | 6 | Project summary dashboard |
| `run_cbd_experiment.py` | 6 | CBD robustness experiment (330 runs) |
| `analyze_queue_metrics.py` | 6 | Queue metrics analysis |
| `analyze_seasonal_patterns.py` | 6 | Seasonal variation analysis |
| `generate_manhattan_distance_matrix.py` | 8 | Manhattan (taxicab) distance matrix generation |
| `run_distance_comparison_experiment.py` | 8 | Haversine vs. Manhattan metric comparison |
| `run_cbd_focused_optimization.py` | 8 | CBD-focused vs. Manhattan-wide optimization |
| `capacity_sensitivity_analysis.py` | 9 | Initial cap=2 vs cap=5 comparison |
| `capacity_sensitivity_full_spectrum.py` | 9 | Full-spectrum cap 1–5 sensitivity (450 runs) |
| `p0_spatial_analysis.py` | 9 | P0 spatial stratification analysis and visualization |
| `run_production_v2.py` | 9 | Extended Fleet Analysis experiment runner (810 runs) |
| `generate_all_heatmaps.py` | 9 | Generates 108 staging location heat maps (9K × 3 policies × 4 capacities) |

### `tests/` — Test Suite (39 tests)
| File | Tests | Description |
|------|-------|-------------|
| `conftest.py` | — | Shared fixtures |
| `test_simulation_core.py` | 15 | Core DES engine tests |
| `test_dispatch_logic.py` | 10 | Dispatcher & resource tests |
| `test_extreme_cases.py` | 8 | Edge case & stress tests |
| `test_reproducibility.py` | 6 | Seeded reproducibility tests |

### `notebooks/` — Analysis Notebooks (8 notebooks)
| File | Description |
|------|-------------|
| `02_eda_spatiotemporal.ipynb` | Exploratory data analysis |
| `03_input_modeling.ipynb` | NHPP demand model fitting |
| `04_service_travel_proxy.ipynb` | Service & travel time validation |
| `05_optimization.ipynb` | Optimization model comparison |
| `06_simulation_debug.ipynb` | Simulation debugging & V&V |
| `07_production_results.ipynb` | Production experiment results |
| `08_statistical_analysis.ipynb` | Comprehensive statistical analysis |
| `09_cbd_analysis.ipynb` | CBD robustness analysis |

### `results/figures/` — Visualizations (66+ PNG files)
| Category | Files | Description |
|----------|-------|-------------|
| EDA | 10 | Crash heatmap, temporal trends, firehouses map, etc. |
| Optimization | 4 | Inputs, sensitivity, allocation comparison |
| Simulation V&V | 4 | Verification timeline, validation comparisons |
| Experiments | 4 | Exp1–Exp4 result plots |
| Publication | 5 | pub_fig1–pub_fig5 (high quality) |
| Model | 6 | Distance heatmap, travel time, service time, NHPP |
| CBD | 3 | CBD robustness figures |
| Queue | 4 | Queue analysis figures |
| Seasonal | 3 | Seasonal analysis figures |
| Distance Comparison | 4 | Haversine vs Manhattan figures |
| CBD-Focused Comparison | 3 | CBD-focused vs Manhattan-wide figures |
| Capacity Sensitivity | 10+ | Cap 1–5 sensitivity figures |
| Extended Fleet Analysis | 10+ | analysis result figures |

### `results/tables/` — Statistical Tables (55+ files)
| File | Description |
|------|-------------|
| `descriptive_statistics.csv` | Summary stats for all experiments |
| `anova_results.csv` | ANOVA test results |
| `posthoc_comparisons.csv` | Pairwise comparisons (Tukey HSD) |
| `confidence_intervals.csv` | 95% confidence intervals |
| `effect_sizes.csv` | Cohen's d effect sizes |
| `sensitivity_summary.csv` | Sensitivity analysis summary |
| `table1–table4_*.csv/.tex` | Publication-ready tables (CSV + LaTeX) |
| `exp1–exp4_*.csv` | Per-experiment pivot tables |
| `optimization_comparison.csv` | Policy comparison metrics |
| `cbd_*.csv` | CBD robustness tables |
| `queue_*.csv` | Queue analysis tables |
| `seasonal_*.csv` | Seasonal analysis tables |

### `results/simulation/` — Simulation Outputs
| Directory | Files | Description |
|-----------|-------|-------------|
| `production/` | 6 | 4 experiment CSVs + summary + log |
| `validation_pilot/` | 5 | 3 pilot JSONs + 2 comparison tables |
| `verification/` | 4 | 4 verification test JSONs |

### `results/archive/optimization/` — Optimization Results
| File | Description |
|------|-------------|
| `allocations_K20–K48.csv` | Unit allocations for K=20,30,40,48 |
| `policy_comparison.csv` | 5-policy comparison results |
| `sensitivity_analysis.csv` | K-sensitivity analysis |
| `findings_summary.json` | Machine-readable summary |
| `PHASE3_SUMMARY.md/.pdf` | Phase 3 narrative summary |

### `results/analysis/distance_comparison/` — Distance Metric Comparison (Phase 8)
| File | Description |
|------|-------------|
| `comparison_table.csv` | Haversine vs. Manhattan simulation metrics |
| `allocation_comparison.csv` | Side-by-side firehouse allocations |
| `distance_matrices_heatmap.png` | Dual-panel heatmap |
| `distance_scatter.png` | Manhattan vs. Haversine scatter |
| `distance_comparison_bar.png` | RT comparison bar chart |
| `distance_comparison_boxplot.png` | RT distribution boxplot |
| `experiment_log.txt` | Experiment execution log |

### `results/analysis/cbd_focused_comparison/` — CBD-Focused Optimization (Phase 8)
| File | Description |
|------|-------------|
| `comparison_table.csv` | CBD-focused vs. Manhattan-wide metrics |
| `allocations.csv` | Side-by-side allocations |
| `cbd_focused_comparison.png` | RT comparison bar chart |
| `allocation_comparison.png` | Allocation distribution comparison |
| `equity_tradeoff.png` | CBD vs. non-CBD equity trade-off |
| `experiment_log.txt` | Experiment execution log |

### `results/analysis/capacity_comparison/` — Capacity Sensitivity Analysis (Phase 9)
| File | Description |
|------|-------------|
| `cap_*_allocations_*.csv` | Allocation vectors per capacity × K |
| `capacity_sensitivity_summary.csv` | Summary table: cap 1–5 × K 10–48 |
| `capacity_*_figures.png` | Capacity sensitivity visualization figures |
| `experiment_log.txt` | Experiment execution log |

### `results/baseline/` — Extended Fleet Analysis Results (Phase 9)
| File | Description |
|------|-------------|
| `v2_allocations_*.csv` | P0 (spatially-stratified), P1, P2 allocations per K |
| `v2_simulation_results.csv` | Full Extended Fleet Analysis simulation results (810 runs) |
| `v2_summary_statistics.csv` | Extended Fleet Analysis summary statistics by policy × K |
| `comparison_with_v1.csv` | baseline comparison table |
| `*.png` | Extended Fleet Analysis result figures |

### `results/analysis/heatmaps/` — Staging Location Heat Map Collection (108 maps)

A systematic collection of **108 heat maps** visualizing ambulance staging locations on Manhattan geography for every combination of fleet size, allocation policy, and per-firehouse capacity limit. These maps are generated by `scripts/generate_all_heatmaps.py`.

**Parameter space:**

| Parameter | Values | Count |
|-----------|--------|-------|
| Fleet size (K) | 5, 10, 15, 20, 25, 30, 35, 40, 45 | 9 |
| Policy | P0 (spatially-stratified), P1, P2 | 3 |
| Capacity | 1, 2, 3, 5 | 4 |
| **Total** | **9 × 3 × 4** | **108** |

**Naming convention:** `heatmap_K{k}_policy{policy}_cap{capacity}.png`

| Example filename | Description |
|------------------|-------------|
| `heatmap_K20_policyP2_cap2.png` | Optimized allocation (P2), 20 units, capacity 2 |
| `heatmap_K10_policyP0_spatial_cap1.png` | Spatial baseline (P0), 10 units, capacity 1 |
| `heatmap_K40_policyP1_cap5.png` | Demand-proportional (P1), 40 units, capacity 5 |

Each map shows active staging locations (sized/colored by unit count) overlaid on the Manhattan borough boundary with precinct outlines and CBD boundary for reference. The companion `allocations/` subdirectory contains the underlying allocation vectors as CSV files.

These maps support scenario exploration across the full experimental space and feed into the interactive dashboard.

### `docs/` — Documentation (32+ files)
| File | Description |
|------|-------------|
| `project_charter.md` | Project scope and objectives |
| `source_manifest.md/.pdf` | Data source inventory |
| `assumptions_log.md` | Documented assumptions (14 items) |
| `decisions_log.md/.pdf` | Key decision records (DEC-001 through DEC-011) |
| `blocker_log.md` | Issue tracking |
| `demand_model_spec.md/.pdf` | NHPP demand model specification |
| `service_model_spec.md/.pdf` | Travel & service model spec |
| `optimization_formulation.md/.pdf` | MIP formulation documentation |
| `optimization_results.md/.pdf` | Optimization results narrative |
| `conceptual_model.md/.pdf` | DES conceptual model |
| `experimental_design.md/.pdf` | Factorial experimental design |
| `verification_log.md/.pdf` | V&V test results |
| `output_analysis.md/.pdf` | Statistical analysis report |
| `executive_summary.md/.pdf` | Executive summary |
| `technical_report.md` | Full final report |
| `executive_presentation.md` | Slide deck for stakeholders |
| `implementation_roadmap.md` | Deployment plan |
| `project_archive.md` | Project archive & timeline |
| `code_documentation.md` | Code architecture guide (v1.3.0) |
| `file_inventory.md` | This file |
| `cbd_robustness_analysis.md` | CBD robustness DES experiment |
| `queue_analysis.md` | Queueing performance analysis |
| `gap_closure_report.md` | Gap closure verification |
| `distance_metric_comparison.md/.pdf` | Haversine vs. Manhattan comparison (Phase 8) |
| `cbd_focused_optimization_analysis.md/.pdf` | CBD-focused optimization report (Phase 8) |
| `alternative_analyses_summary.md/.pdf` | Alternative analyses summary (Phase 8) |
| `research_questions_assessment.md` | Research questions assessment |
| `project_workflow_wbs.md/.pdf` | Work Breakdown Structure (v1.3.0) |
| `firehouse_capacity_analysis.md` | Firehouse capacity methodology (Phase 9) |
| `capacity_sensitivity_analysis.md` | Full-spectrum capacity sensitivity report (Phase 9) |
| `final_summary.md` | Final project summary (v1.3.0) |

---

## Project Statistics

| Metric | Value |
|--------|-------|
| Total Python LOC | 8,500+ |
| Total source modules | 14 |
| Total scripts | 24 |
| Total test cases | 39 |
| Total notebooks | 8 |
| Total figures | 72+ (analysis) + 108 (staging heat maps) |
| Total CSV result files | 55+ |
| Total documentation files | 32+ |
| Total simulation runs | 2,700+ (production + CBD + capacity + alternatives) |
| Tracked files in Git | 230+ |
| Project size (excl. raw data) | ~160 MB |

---

*Last updated: March 15, 2026 — Version 1.3.0*
