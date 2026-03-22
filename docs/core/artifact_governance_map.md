---
status: ✅ CURRENT
last_updated: "2026-03-22"
verified: "Cross-checked against repository structure, README.md, technical_report.md, and executive_summary.md"
---
# Artifact Governance Map

> **Purpose**: Define the canonical/supporting/historical tier system, map every
> script to its output artifacts, and provide a single authoritative reference
> for what is current, what is supporting, and what is legacy.

---

## 1. Tier Definitions (Canonical Rules)

Every file in `results/`, `docs/`, and `scripts/` belongs to exactly one tier:

| Tier | Label | Folder Convention | Meaning |
|------|-------|-------------------|---------|
| **Canonical** | ✅ Current | `results/baseline/`, `docs/core/` | Source-of-truth outputs used in the technical report and README. These are the authoritative results. |
| **Supporting** | 🔬 Analysis | `results/analysis/`, `docs/analysis/` | Robustness, sensitivity, and alternative analyses that strengthen but do not replace canonical findings. |
| **Historical** | ⚠️ Archive | `results/archive/`, `docs/archive/`, `scripts/archive/` | Superseded artifacts from earlier project phases (e.g., cap=5 era, old nomenclature). Retained for audit trail only. |

### Upgrade / Downgrade Rules

- An artifact moves from Supporting → Canonical only if it is cited in the technical report main body (not just appendix).
- An artifact moves from Canonical → Historical when a newer version with the same scope is produced and verified.
- Historical artifacts are **never deleted** — they serve as the audit trail.

---

## 2. Generator Registry — Canonical Scripts

These scripts produce the artifacts cited in `README.md`, `docs/core/technical_report.md`, or `docs/core/executive_summary.md`.

| # | Script | Tier | Outputs | Experiment / Purpose |
|---|--------|------|---------|----------------------|
| G1 | `scripts/generate_all_data.py` | Canonical | `data/processed/` (demand lambdas, distance matrices, firehouses, precincts GeoJSON) | Data pipeline entry point |
| G2 | `scripts/run_production_v2.py` | Canonical | `results/baseline/simulation/`, `results/baseline/tables/`, `results/baseline/figures/`, `results/baseline/allocations/` | Production experiments (Exp1–4, fleet analysis): 810 runs, 3 policies × 9 K-values × 30 reps |
| G3 | `scripts/run_verification.py` | Canonical | `results/baseline/simulation/verification/01–04_*.json` | 4 verification tests (toy, zero-demand, single-unit, extreme) |
| G4 | `scripts/run_validation_pilots.py` | Canonical | `results/baseline/simulation/validation_pilot/pilot1–3_*.json` | 3 validation pilots (P0 vs P2, fleet sensitivity, demand sensitivity) |
| G5 | `scripts/run_optimization_comparison.py` | Canonical | `results/figures/fig_policy_comparison.png`, `results/figures/fig_tradeoff_curve.png`, allocation CSVs | Static optimization comparison across K-values |
| G6 | `scripts/demand_modeling.py` | Canonical | `data/processed/demand_lambda_*.csv`, `results/figures/fig_precinct_demand.png`, `results/figures/fig_demand_model_fit.png` | NHPP demand calibration |
| G7 | `scripts/analysis/analyze_production_results.py` | Canonical | `results/baseline/tables/` (ANOVA, CIs, effect sizes, descriptive stats) | Statistical analysis of production results |
| G8 | `scripts/analysis/generate_publication_figures.py` | Canonical | `results/figures/pub_fig1–5_*.png` | Publication-quality figures for technical report |

### Generator Registry — Supporting Scripts

These scripts produce artifacts in `results/analysis/` or `docs/analysis/`, cited in appendices or supporting documents.

| # | Script | Tier | Outputs | Experiment / Purpose |
|---|--------|------|---------|----------------------|
| S1 | `scripts/analysis/capacity_sensitivity_full_spectrum.py` | Supporting | `results/analysis/capacity_comparison/` | Capacity sweep: cap={1,2,3,4,5} × K={20,40} |
| S2 | `scripts/analysis/capacity_sensitivity_analysis.py` | Supporting | `results/analysis/capacity_comparison/` (K=20 detail) | Capacity sensitivity at K=20 |
| S3 | `scripts/analysis/run_cbd_experiment.py` | Supporting | `results/analysis/simulation/cbd_experiment/` | CBD robustness: 330 DES runs |
| S4 | `scripts/analysis/run_cbd_focused_optimization.py` | Supporting | `results/analysis/cbd_focused_comparison/` | CBD-focused vs Manhattan-wide optimization |
| S5 | `scripts/analysis/run_distance_comparison_experiment.py` | Supporting | `results/analysis/distance_comparison/` | Haversine vs Manhattan distance metric |
| S6 | `scripts/analysis/generate_capacity_sensitivity_heatmap.py` | Supporting | `results/figures/capacity_sensitivity_heatmap.png` | Capacity sensitivity visualization |
| S7 | `scripts/analysis/generate_all_heatmaps.py` | Supporting | `results/analysis/heatmaps/` (~160 PNGs) | Parametric allocation heatmaps |
| S8 | `scripts/analysis/analyze_queue_metrics.py` | Supporting | `results/figures/queue_*.png`, `results/tables/queue_*.csv` | Queue analysis |
| S9 | `scripts/analysis/analyze_seasonal_patterns.py` | Supporting | `results/figures/seasonal_*.png`, `results/tables/seasonal_analysis.csv` | Seasonal pattern analysis |
| S10 | `scripts/analysis/generate_precinct_demand_visualizations.py` | Supporting | `results/figures/precinct_demand_rates_improved.png`, `results/figures/precinct_demand_heatmap.png` | Improved precinct demand charts |
| S11 | `scripts/analysis/generate_tradeoff_improved.py` | Supporting | `results/figures/response_time_coverage_tradeoff_improved.png` | Improved trade-off visualization |
| S12 | `scripts/analysis/generate_summary_dashboard.py` | Supporting | `results/figures/project_summary_dashboard.png` | Executive dashboard |
| S13 | `scripts/analysis/p0_spatial_analysis.py` | Supporting | `results/figures/p0_spatial_*.png` | P0 spatial stratification analysis |
| S14 | `scripts/analysis/generate_manhattan_distance_matrix.py` | Supporting | `data/processed/distance_matrix_firehouse_precinct_manhattan.csv` | Manhattan distance matrix generation |

### Historical / Utility Scripts (not producing active artifacts)

| Script | Status | Notes |
|--------|--------|-------|
| `scripts/archive/run_production_experiments.py` | ⚠️ Historical | Superseded by `run_production_v2.py` |
| `scripts/archive/audit_step1–4_*.py` | ⚠️ Historical | One-time data audit scripts |
| `scripts/archive/data_audit.py` | ⚠️ Historical | One-time audit |
| `scripts/fix_notebook_nomenclature.py` | Utility | One-time nomenclature migration |
| `scripts/build_enhanced_notebook.py` | Utility | Colab notebook builder |
| `scripts/verify_project_consistency.py` | Utility | Project-wide consistency check |

---

## 3. Active Artifact Registry

Artifacts actively referenced in `README.md`, `docs/core/technical_report.md`, or `docs/core/executive_summary.md`.

### 3a. Canonical Results (`results/baseline/`)

| Artifact | Path | Generator | Tech Report Section |
|----------|------|-----------|---------------------|
| Policy comparison (Exp1) | `results/baseline/simulation/exp1_policy_comparison.csv` | G2 | §5.5 |
| Fleet sensitivity (Exp2) | `results/baseline/simulation/exp2_fleet_sensitivity.csv` | G2 | §5.6 |
| Demand sensitivity (Exp3) | `results/baseline/simulation/exp3_demand_sensitivity.csv` | G2 | §5.7 |
| Service robustness (Exp4) | `results/baseline/simulation/exp4_service_robustness.csv` | G2 | §5.7 |
| Descriptive statistics | `results/baseline/tables/descriptive_statistics.csv` | G7 | §5.5 |
| ANOVA results | `results/baseline/tables/anova_results.csv` | G7 | §5.5 |
| Confidence intervals | `results/baseline/tables/confidence_intervals.csv` | G7 | §5.5 |
| Effect sizes | `results/baseline/tables/effect_sizes.csv` | G7 | §5.5 |
| Pairwise comparisons | `results/baseline/tables/posthoc_comparisons.csv` | G7 | §5.5 |
| Sensitivity summary | `results/baseline/tables/sensitivity_summary.csv` | G7 | §5.7 |
| Allocations (K=10–48) | `results/baseline/allocations/allocations_K*.csv` | G2 | §5.4 |
| Verification JSONs | `results/baseline/simulation/verification/01–04_*.json` | G3 | §4.4.3 |
| Validation pilot JSONs | `results/baseline/simulation/validation_pilot/pilot1–3_*.json` | G4 | §4.4.3 |

### 3b. Key Figures (in tech report or README)

| Figure | Path | Generator | Tech Report Section |
|--------|------|-----------|---------------------|
| `pub_fig1_policy_comparison.png` | `results/figures/` | G8 | §5.5 |
| `pub_fig2_fleet_sensitivity.png` | `results/figures/` | G8 | §5.6 |
| `pub_fig3_demand_robustness.png` | `results/figures/` | G8 | §5.7 |
| `pub_fig4_service_sensitivity.png` | `results/figures/` | G8 | §5.7 |
| `pub_fig5_performance_heatmap.png` | `results/figures/` | G8 | §5.5 |
| `fleet_sensitivity_dual.png` | `results/figures/` | G2 | §5.6 |
| `precinct_demand_rates_improved.png` | `results/figures/` | S10 | §5.2 |
| `precinct_demand_heatmap.png` | `results/figures/` | S10 | §5.2 |
| `capacity_sensitivity_heatmap.png` | `results/figures/` | S6 | §5.12 |
| `cbd_robustness_enhanced.png` | `results/figures/` | Pipeline | §5.10 |

### 3c. Processed Data (committed to Git)

| Artifact | Path | Generator | Used By |
|----------|------|-----------|---------|
| Hourly lambda | `data/processed/demand_lambda_hourly.csv` | G6 | Simulation engine (NHPP) |
| Day-of-week lambda | `data/processed/demand_lambda_dow.csv` | G6 | Simulation engine (NHPP) |
| Precinct lambda | `data/processed/demand_lambda_precinct.csv` | G6 | Optimization (demand weights), simulation (arrival rates) |
| Distance matrix (Haversine) | `data/processed/distance_matrix_firehouse_precinct.csv` | G1 | Dispatcher, optimization models |
| Distance matrix (Manhattan) | `data/processed/distance_matrix_firehouse_precinct_manhattan.csv` | S14 | Alternative distance analysis |
| Firehouses (Manhattan) | `data/processed/firehouses_manhattan.csv` | G1 | Optimization, simulation, visualization |
| Precincts (Manhattan) | `data/processed/precincts_manhattan.geojson` | G1 | Spatial joins, visualization |

---

## 4. Experiment Mapping

Each experiment set corresponds to a specific research question and generates specific artifacts.

| Experiment | RQ | Factors Varied | K-values | Policies | Reps | Generator | Output Location |
|------------|-----|----------------|----------|----------|------|-----------|-----------------|
| **Exp1** — Policy Comparison | RQ1 | Policy (P0, P1, P2) | 20 | All 3 | 30 | G2 | `results/baseline/simulation/exp1_*` |
| **Exp2** — Fleet Sensitivity | RQ2 | K ∈ {10,15,20,25,30,35,40,45,48} | All 9 | All 3 | 30 | G2 | `results/baseline/simulation/exp2_*` |
| **Exp3** — Demand Sensitivity | RQ3 | δ ∈ {0.5, 0.75, 1.0, 1.25, 1.5, 2.0} | 20 | P0, P2 | 30 | G2 | `results/baseline/simulation/exp3_*` |
| **Exp4** — Service Robustness | RQ4 | μ_s ∈ {20, 25, 30} min | 20 | P0, P2 | 30 | G2 | `results/baseline/simulation/exp4_*` |
| **Capacity** — Cap Sensitivity | RQ4 | cap ∈ {1,2,3,4,5} | 20, 40 | P0, P1, P2 | 30 | S1, S2 | `results/analysis/capacity_comparison/` |
| **CBD** — CBD Robustness | RQ3 | CBD surge scenarios | 20, 30 | P0, P2 | 30 | S3 | `results/analysis/simulation/cbd_experiment/` |
| **CBD-Focused** — Optimization | RQ4 | CBD-specific models | 20 | P0, P2, CBD variants | 10 | S4 | `results/analysis/cbd_focused_comparison/` |
| **Distance** — Metric Comparison | RQ4 | Haversine vs Manhattan | 20 | P0, P2 | 10 | S5 | `results/analysis/distance_comparison/` |
| **Queue** — Queue Analysis | RQ1 | Derived from Exp1–4 | Multiple | All 3 | — | S8 | `results/tables/queue_*.csv` |
| **Seasonal** — Pattern Analysis | RQ1 | Monthly decomposition | — | — | — | S9 | `results/tables/seasonal_analysis.csv` |

---

## 5. K-Value and Capacity Rules

### Canonical K Set

The full canonical K-value set is **K ∈ {10, 15, 20, 25, 30, 35, 40, 45, 48}** (9 values).

- Defined in `configs/optimization.yaml` → `unit_counts`
- Used by `scripts/run_production_v2.py` for Exp2 (fleet sensitivity)
- Pre-computed allocations stored in `results/baseline/allocations/allocations_K*.csv`

### K Subsets by Experiment

| Context | K-values Used | Reason |
|---------|---------------|--------|
| Exp1 (Policy comparison) | 20 | Reference fleet size |
| Exp2 (Fleet sensitivity) | 10, 15, 20, 25, 30, 35, 40, 45, 48 | Full canonical range |
| Exp3 (Demand sensitivity) | 20 | Isolate demand effect |
| Exp4 (Service robustness) | 20 | Isolate service effect |
| Capacity sensitivity | 20, 40 | Low and high fleet bounds |
| CBD experiment | 20, 30 | Moderate fleet sizes |
| Heatmap generation | 5, 10, 15, 20, 25, 30, 35, 40, 45, 48 | Extended range for visualization |

### Capacity Rules

| Parameter | Value | Source | Decision |
|-----------|-------|--------|----------|
| Default capacity | **2** | `configs/optimization.yaml` → `firehouse_capacity` | DEC-010 |
| Sensitivity range | {1, 2, 3, 4, 5} | `capacity_sensitivity_full_spectrum.py` | Full-spectrum analysis |
| Cap=2 rationale | At K ≤ 30, cap=2 and cap=5 produce identical results | `docs/analysis/capacity_sensitivity_analysis.md` | Operationally realistic |
| Historical default | 5 | `results/archive/` | Superseded by DEC-010 |

---

## 6. Configuration File Map

| Config File | Controls | Key Parameters |
|-------------|----------|----------------|
| `configs/demand.yaml` | NHPP arrival model | `base_rate_per_hour: 3.48`, lambda table paths, seed: 42 |
| `configs/optimization.yaml` | MIP formulations | `unit_counts: [10–48]`, `firehouse_capacity: 2`, solver: CBC |
| `configs/service.yaml` | Travel & service time | `average_speed_mph: 20`, `mean_minutes: 25`, dispatch delay: 1.5 min |
| `configs/simulation.yaml` | DES engine | `horizon_hours: 168`, `num_replications: 30`, `seed_base: 42`, threshold: 8 min |
| `configs/cbd_scenario.yaml` | CBD robustness | CBD surge parameters |

---

## 7. Onboarding Guide

### First 5 Minutes

1. **Read** `README.md` — project overview, key findings, quick start
2. **Read** `docs/core/technical_report.md` §1 — executive summary
3. **Browse** `results/baseline/` — this is the source of truth

### Understand the Architecture

4. **Read** `docs/core/ARCHITECTURAL_MAP.md` — full execution map
5. **Read** this document (`artifact_governance_map.md`) — tier system, script registry

### Reproduce Results

6. **Run** `python scripts/generate_all_data.py --verify` — check data
7. **Run** `python scripts/run_production_v2.py` — regenerate canonical results
8. **Run** `pytest tests/ -v` — verify 176 tests pass

### Navigate Supporting Work

9. **Browse** `docs/analysis/` — robustness and sensitivity write-ups
10. **Browse** `results/analysis/` — supporting experiment outputs
11. **Consult** `docs/core/figure_trace_guide.md` — trace any figure to its generator

### Know What to Ignore

- `results/archive/` — historical cap=5 era results
- `docs/archive/` — superseded documentation
- `scripts/archive/` — legacy scripts (do not run)
- `notebooks/` — exploratory companions, not canonical generators

---

## 8. Cross-Reference Index

| If you need... | Go to... |
|----------------|----------|
| Which results file to use | `results/WHICH_FILES_TO_USE.md` |
| Full documentation index | `docs/core/DOCUMENTATION_INDEX.md` |
| Figure provenance | `docs/core/figure_trace_guide.md` |
| Figure/table traceability | `docs/core/figure_table_traceability.md` |
| Visualization catalog | `docs/core/visualization_index.md` |
| Data file inventory | `docs/core/source_manifest.md` |
| Decision rationale | `docs/core/decisions_log.md` |
| Assumptions | `docs/core/assumptions_log.md` |
| Architecture deep-dive | `docs/core/ARCHITECTURAL_MAP.md` |
