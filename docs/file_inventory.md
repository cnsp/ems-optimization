# File Inventory — EMS Readiness Optimization Project

> Generated: 2026-03-12 | Total tracked files in remote: **191** | Total local files: **195**

---

## Phase Deliverable Checklist

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 1 | Data Processing & EDA | ✅ Complete |
| Phase 2 | Demand & Service Modeling (NHPP) | ✅ Complete |
| Phase 3 | Optimization Models (P0, P1, P2) | ✅ Complete |
| Phase 4 | DES Simulation with V&V (39 tests) | ✅ Complete |
| Phase 5 | Experimental Design & Production Runs (1,440 sims) | ✅ Complete |
| Phase 6 | Comprehensive Statistical Analysis | ✅ Complete |
| Phase 7 | Final Report & Documentation | ✅ Complete |

---

## Directory Structure & File Inventory

### `configs/` — Configuration Files
| File | Size | Description |
|------|------|-------------|
| `demand.yaml` | 856 B | NHPP demand model parameters |
| `optimization.yaml` | 960 B | MIP solver and unit-count settings |
| `service.yaml` | 1.5 KB | Travel time and service time config |
| `simulation.yaml` | 1.1 KB | DES engine and batch runner settings |

### `data/raw/` — Raw Input Data
| File | Size | Tracked | Description |
|------|------|---------|-------------|
| `FDNY_Firehouse_Listing_20260223.csv` | 34 KB | ✅ | 219 FDNY firehouses |
| `FDNY_Firehouse_Listing_Data_Dictionary.xlsx` | 66 KB | ✅ | Firehouse field definitions |
| `Motor_Vehicle_Collisions_-_Crashes_20260223.csv` | 536 MB | ❌ | 2.24M crash records (too large) |
| `Motor_Vehicle_Collisions_Data_Dictionary.xlsx` | 96 KB | ✅ | Crash field definitions |
| `Police_Precincts_20260223.csv` | 3.6 MB | ❌ | 78 precinct boundaries (large) |
| `Police_Precincts_Data_Dictionary.xlsx` | 62 KB | ✅ | Precinct field definitions |
| `manhattan_boundary.geojson` | 247 KB | ✅ | Manhattan polygon boundary |
| `cbd_boundary.geojson` | 101 KB | ✅ | CBD/Congestion Relief Zone boundary |
| `nyc_borough_boundaries.geojson` | 3.1 MB | ✅ | All 5 NYC borough boundaries |

### `data/processed/` — Processed Data
| File | Size | Tracked | Description |
|------|------|---------|-------------|
| `crashes_manhattan.csv` | 99 MB | ❌ | Filtered Manhattan crashes (large) |
| `crashes_manhattan.parquet` | 15 MB | ❌ | Parquet version of above |
| `demand_lambda_hourly.csv` | 1.9 KB | ✅ | Hourly λ factors (24 hours) |
| `demand_lambda_dow.csv` | 653 B | ✅ | Day-of-week λ factors |
| `demand_lambda_precinct.csv` | 1.7 KB | ✅ | Precinct-level λ rates |
| `demand_model_summary.json` | 696 B | ✅ | Demand model summary stats |
| `distance_matrix_firehouse_precinct.csv` | 27 KB | ✅ | 48×30 distance matrix |
| `firehouses_clean.csv` | 32 KB | ✅ | All cleaned firehouses |
| `firehouses_manhattan.csv` | 7.1 KB | ✅ | 48 Manhattan firehouses |
| `precincts_manhattan.geojson` | 640 KB | ✅ | 30 Manhattan precincts |

### `src/ems_readiness/` — Source Code (7,134 lines total)
| Module | Files | Description |
|--------|-------|-------------|
| `demand/` | `__init__.py`, `arrival_generator.py` | NHPP arrival generation (thinning algorithm) |
| `service/` | `__init__.py`, `travel_time.py`, `service_time.py` | Travel proxy & LogNormal service time |
| `optimization/` | `__init__.py`, `models.py`, `policies.py`, `allocator.py` | MIP formulations & baseline policies |
| `simulation/` | `__init__.py`, `engine.py`, `entities.py`, `resources.py`, `dispatcher.py`, `metrics.py`, `runner.py` | SimPy DES engine with batch runner |
| `utils/` | `__init__.py`, `distance.py` | Haversine distance calculations |

### `scripts/` — Automation Scripts
| File | Description |
|------|-------------|
| `data_audit.py` | Data quality audit pipeline |
| `audit_step1_boundaries.py` | Boundary file validation |
| `audit_step2_firehouses.py` | Firehouse data validation |
| `audit_step3_precincts.py` | Precinct data validation |
| `audit_step4_crashes.py` | Crash data validation |
| `demand_modeling.py` | NHPP demand model fitting |
| `run_optimization_comparison.py` | Multi-model optimization comparison |
| `run_verification.py` | Simulation verification tests |
| `run_validation_pilots.py` | Validation pilot experiments |
| `run_production_experiments.py` | Full 1,440-run production experiments |
| `analyze_production_results.py` | Production result analysis |
| `generate_publication_figures.py` | Publication-quality figure generation |
| `generate_summary_dashboard.py` | Project summary dashboard |

### `tests/` — Test Suite (39 tests)
| File | Tests | Description |
|------|-------|-------------|
| `conftest.py` | — | Shared fixtures |
| `test_simulation_core.py` | 15 | Core DES engine tests |
| `test_dispatch_logic.py` | 10 | Dispatcher & resource tests |
| `test_extreme_cases.py` | 8 | Edge case & stress tests |
| `test_reproducibility.py` | 6 | Seeded reproducibility tests |

### `notebooks/` — Analysis Notebooks (7 notebooks)
| File | Description |
|------|-------------|
| `02_eda_spatiotemporal.ipynb` | Exploratory data analysis |
| `03_input_modeling.ipynb` | NHPP demand model fitting |
| `04_service_travel_proxy.ipynb` | Service & travel time validation |
| `05_optimization.ipynb` | Optimization model comparison |
| `06_simulation_debug.ipynb` | Simulation debugging & V&V |
| `07_production_results.ipynb` | Production experiment results |
| `08_statistical_analysis.ipynb` | Comprehensive statistical analysis |

### `results/figures/` — Visualizations (33 PNG files)
| Category | Files | Description |
|----------|-------|-------------|
| EDA | 10 | Crash heatmap, temporal trends, firehouses map, etc. |
| Optimization | 4 | Inputs, sensitivity, allocation comparison |
| Simulation V&V | 4 | Verification timeline, validation comparisons |
| Experiments | 4 | Exp1–Exp4 result plots |
| Publication | 5 | pub_fig1–pub_fig5 (high quality) |
| Model | 6 | Distance heatmap, travel time, service time, NHPP |

### `results/tables/` — Statistical Tables (18 files)
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

### `results/simulation/` — Simulation Outputs
| Directory | Files | Description |
|-----------|-------|-------------|
| `production/` | 6 | 4 experiment CSVs + summary + log |
| `validation_pilot/` | 5 | 3 pilot JSONs + 2 comparison tables |
| `verification/` | 4 | 4 verification test JSONs |

### `results/optimization/` — Optimization Results
| File | Description |
|------|-------------|
| `allocations_K20–K48.csv` | Unit allocations for K=20,30,40,48 |
| `policy_comparison.csv` | 5-policy comparison results |
| `sensitivity_analysis.csv` | K-sensitivity analysis |
| `findings_summary.json` | Machine-readable summary |
| `PHASE3_SUMMARY.md/.pdf` | Phase 3 narrative summary |

### `docs/` — Documentation (25+ files)
| File | Description |
|------|-------------|
| `project_charter.md` | Project scope and objectives |
| `source_manifest.md/.pdf` | Data source inventory |
| `assumptions_log.md` | Documented assumptions |
| `decisions_log.md/.pdf` | Key decision records |
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
| `technical_report.md` | Comprehensive final report |
| `executive_presentation.md` | Slide deck for stakeholders |
| `implementation_roadmap.md` | Deployment plan |
| `project_archive.md` | Project archive & timeline |
| `code_documentation.md` | Code architecture guide |
| `file_inventory.md` | This file |

---

## Project Statistics

| Metric | Value |
|--------|-------|
| Total Python LOC | 7,134 |
| Total source modules | 14 |
| Total test cases | 39 |
| Total notebooks | 7 |
| Total figures | 33 |
| Total CSV result files | 27 |
| Total documentation files | 25+ |
| Total simulation runs | 1,440 |
| Tracked files in Git | 191+ |
| Project size (excl. raw data) | ~130 MB |
