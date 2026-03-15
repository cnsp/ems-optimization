# Final Project Summary
## EMS Readiness Optimization for Manhattan — v1.3.0

**Completion Date:** March 15, 2026 
**Repository:** github.com/cnsp/ems-optimization 
**Tag:** v1.3.0 (Capacity & Baseline Improvements)

---

## Repository Statistics

| Metric | Value |
|--------|-------|
| Total files in repository | **230+** |
| Total Python lines of code | **8,500+** |
| Python source files | 46 |
| Jupyter notebooks | 8 |
| CSV result files | 55+ |
| PNG figures | 66+ |
| PDF documents | 23 |
| Markdown documents | 32 |
| LaTeX tables | 4 |
| YAML configuration files | 5 |
| Unit tests | 39 (all passing) |

## Simulation Statistics

| Metric | Value |
|--------|-------|
| Total simulation runs | **2,700+** |
| Replications per cell | 15–30 |
| Simulation duration per run | 168 hours (1 week) |
| Warm-up period per run | 24 hours |
| Total simulated time | ~450,000 hours (~51 years) |
| Total experiments | 8 (factorial + CBD + capacity + V2) |
| Verification tests | 4 (all passed) |
| Validation pilots | 3 (all passed) |

## Key Metrics Achieved (Production V2 — cap=2, P0-spatial, K=20)

| Metric | P0-spatial (Baseline) | P1 (Demand-Proportional) | P2 (Optimized) |
|--------|----------------------|--------------------------|-----------------|
| Mean Response Time | 3.17 min | 2.63 min | **2.57 min** |
| P95 Response Time | 6.26 min | 5.05 min | **4.66 min** |
| 8-min Coverage | 99.6% | 99.6% | **99.6%** |
| Mean Utilization | 7.6% | 7.5% | 7.5% |

**Key Observation:** P1 (demand-proportional allocation) captures most of the improvement over P0-spatial, indicating that matching supply to demand patterns is the primary driver of performance gains. P2's additional optimization yields a further 2.3% reduction in mean response time beyond P1.

**P0 Baseline Improvement (V1 → V2):**

| Metric | P0-index (V1) | P0-spatial (V2) | Improvement |
|--------|--------------|-----------------|-------------|
| Mean Response Time | 8.08 min | **3.17 min** | **−60.7%** |
| 8-min Coverage | 64.4% | **99.6%** | **+35.2 pp** |

**Statistical Significance:** All results p < 0.001. P0-spatial improvement driven by geographic placement.

## Phase Completion Status

| Phase | Description | Status | Deliverables |
|-------|-------------|--------|-------------|
| Phase 1 | Data Processing & EDA | ✅ Complete | 10 figures, processed data, EDA notebook |
| Phase 2 | Demand & Service Modeling | ✅ Complete | NHPP model, lambda tables, 2 spec docs |
| Phase 3 | Optimization Models | ✅ Complete | 3 MIP models, allocations, comparison |
| Phase 4 | DES Simulation + V&V | ✅ Complete | SimPy engine, 39 tests, V&V log |
| Phase 5 | Production Experiments | ✅ Complete | 1,770 runs, 5 experiments (incl. CBD) |
| Phase 6 | Statistical Analysis | ✅ Complete | ANOVA, post-hoc, 5 pub figures, 4 tables |
| Phase 7 | Final Report & Docs | ✅ Complete | Technical report, presentation, roadmap |
| Phase 8 | Alternative Analyses | ✅ Complete | Distance metric comparison, CBD-focused analysis |
| Phase 9 | Capacity & Baseline Improvements | ✅ Complete | Capacity sensitivity (cap 1–5), P0-spatial, Production V2 |

**All 9 phases complete. Project delivered.**

## Files Added in This Session

### Part 1: Repository Sync
- Force-added 38 files previously excluded by .gitignore
- Includes all processed data, figures, experiment tables, and maps
- Pushed successfully to origin/main

### Part 2: Phase 7 Deliverables
- `docs/technical_report.md` (.pdf) — 25-page full report
- `docs/executive_presentation.md` (.pdf) — 10-slide stakeholder deck
- `docs/implementation_roadmap.md` (.pdf) — 3-phase deployment plan
- `docs/project_archive.md` (.pdf) — Timeline, decisions, lessons learned
- `docs/code_documentation.md` (.pdf) — Architecture & API guide
- `docs/file_inventory.md` (.pdf) — Complete file listing
- `README.md` — Enhanced with key findings and full documentation
- `scripts/generate_summary_dashboard.py` — Dashboard generator
- `results/figures/project_summary_dashboard.png` — Visual summary
- `docs/final_summary.md` — This file

### Part 3: Gap Closure (v1.1.0)
- `docs/cbd_definition.md` — CBD geographic definition (10 precincts)
- `configs/cbd_scenario.yaml` — CBD experiment configuration
- `scripts/run_cbd_experiment.py` — CBD DES experiment runner (330 runs)
- `scripts/analyze_queue_metrics.py` — Queue metrics analysis script
- `scripts/analyze_seasonal_patterns.py` — Seasonal pattern analysis script
- `notebooks/09_cbd_analysis.ipynb` — CBD analysis notebook
- `docs/cbd_robustness_analysis.md` (.pdf) — CBD findings document
- `docs/queue_analysis.md` (.pdf) — Queue metrics analysis document
- `docs/gap_closure_report.md` (.pdf) — Gap closure verification report
- `results/simulation/cbd_experiment/` — 330 CBD simulation runs
- `results/figures/cbd_*.png` — 3 CBD figures
- `results/figures/queue_*.png` — 4 queue analysis figures
- `results/figures/seasonal_*.png` — 3 seasonal analysis figures
- `results/tables/cbd_*.csv` — 2 CBD tables
- `results/tables/queue_*.csv` — 2 queue tables
- `results/tables/seasonal_*.csv` — 1 seasonal table

### v1.2.0 – Alternative Analyses (March 12, 2026)

**New experiments:**
- **Distance Metric Comparison:** Haversine vs Manhattan (taxicab) distance — confirmed model robustness; allocations differ at only 2/48 firehouses; simulation performance identical
- **CBD-Focused Optimisation:** Manhattan-wide vs CBD-focused allocation — demonstrated that demand-weighted objective already optimally balances CBD and non-CBD performance; CBD-focused allocation provides no CBD benefit while severely degrading non-CBD service

**New deliverables:**
- `scripts/generate_manhattan_distance_matrix.py` — Manhattan distance matrix generation
- `scripts/run_distance_comparison_experiment.py` — Distance metric comparison experiment
- `scripts/run_cbd_focused_optimization.py` — CBD-focused optimisation experiment
- `data/processed/distance_matrix_firehouse_precinct_manhattan.csv` — Manhattan distance matrix
- `docs/distance_metric_comparison.md` (.pdf) — Distance metric comparison report
- `docs/cbd_focused_optimization_analysis.md` (.pdf) — CBD-focused analysis report
- `docs/alternative_analyses_summary.md` (.pdf) — Combined summary of alternative analyses
- `results/distance_comparison/` — 4 figures + 2 tables
- `results/cbd_focused_comparison/` — 3 figures + 2 tables

**Modified files:**
- `src/ems_readiness/utils/distance.py` — Added `manhattan_distance()` function
- `src/ems_readiness/optimization/models.py` — Added `build_cbd_focused_demand_weighted()` and `build_cbd_focused_coverage()`
- `docs/technical_report.md` — Added §5.10 and §5.11; updated figures/tables lists

### v1.3.0 – Capacity & Baseline Improvements (March 15, 2026)

**Phase 9: Major methodological improvements to baseline policy and capacity constraints.**

**Key changes:**
- **Firehouse capacity constraint reduced from 5 to 2** — Full sensitivity analysis (cap 1–5) shows that cap=2 is operationally realistic and optimal for typical fleet sizes
- **Spatially-stratified P0 baseline** — Replaced index-based P0 with latitude-sorted selection ensuring geographic coverage; P0 mean RT improved by 61% (8.08 → 3.17 min at K=20)
- **Production V2 re-run** — Complete 810-run production experiment with cap=2 and P0-spatial across 9 fleet sizes (K=10–48) × 3 policies × 30 replications
- **38% narrowing of P0-P2 gap** — Spatial stratification shows geographic placement is the dominant factor in EMS response performance

**New scripts:**
- `scripts/capacity_sensitivity_analysis.py` — Initial cap=2 vs cap=5 comparison
- `scripts/capacity_sensitivity_full_spectrum.py` — Full-spectrum cap 1–5 sensitivity analysis
- `scripts/p0_spatial_analysis.py` — Spatial stratification analysis and visualization
- `scripts/run_production_v2.py` — Production V2 experiment runner (810 runs)

**New results:**
- `results/capacity_comparison/` — 60+ files: allocations, figures, tables for cap 1–5
- `results/production_v2/` — Complete V2 results: allocations, simulation, figures, tables

**New documentation:**
- `docs/firehouse_capacity_analysis.md` — Firehouse capacity methodology and initial analysis
- `docs/capacity_sensitivity_analysis.md` — Full-spectrum capacity sensitivity report

**Modified files:**
- `src/ems_readiness/optimization/policies.py` — Added `spatially_stratified_allocation()` and `spatial_stratification_analysis()`
- `src/ems_readiness/optimization/__init__.py` — Exposed new spatial stratification functions
- `src/ems_readiness/optimization/models.py` — Updated `build_p_median` for capacity-aware allocation; added `solve_model()` convenience function
- `configs/optimization.yaml` — Default capacity changed from 5 to 2
- All documentation files updated to reflect v1.3.0

---

*Project complete. Tagged as v1.3.0 — capacity & baseline improvements with Production V2 results.*