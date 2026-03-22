# Full Canonical Regeneration Plan

**Created:** 2026-03-22  
**Status:** PLANNING ONLY — Do NOT execute without explicit approval  
**Scope:** `scripts/run_production_v2.py`, active analysis generators, `results/baseline/`, `results/analysis/`, `results/figures/`

---

## === 1. REGENERATION EXECUTION PLAN ===

### Phase 1: Baseline Production (~2–3 minutes)

| Step | Command | Outputs | Est. Time |
|------|---------|---------|-----------|
| 1a | `python scripts/run_production_v2.py --reps 30` | All `results/baseline/` artifacts | ~100s |

**Outputs regenerated (complete list):**
- `results/baseline/allocations/allocations_K{10,15,20,25,30,35,40,45,48}.csv` (9 files)
- `results/baseline/simulation/results_K{10..48}.csv` (9 files)
- `results/baseline/simulation/all_results_raw.csv` (1 file — 810 rows: 3 policies × 9 K × 30 reps)
- `results/baseline/tables/` — 18 statistical tables (descriptive, ANOVA, posthoc, effect sizes, CIs, queue, exp pivots, publication tables 1–4 in CSV+TeX)
- `results/baseline/figures/` — 44 figures (experiment panels, allocation maps, RT distributions, fleet sensitivity, validation, V&V, pub_fig1–5)
- `results/baseline/comparison_with_v1.csv`
- `results/baseline/experiment_log.txt`

**What this script does internally (6 steps):**
1. Generate allocations for P0/P1/P2 × K={10..48}
2. Run 810 simulation replications (30 reps × 27 scenarios)
3. Perform ANOVA + Tukey HSD + effect sizes
4. Generate all baseline figures
5. Create v1 comparison table
6. Write experiment log

**Prerequisites:**
- `data/processed/` must be fully populated (distance matrix, demand lambda tables, firehouses, precincts)
- PuLP solver available for P2 MIP
- All `src/ems_readiness/` modules import clean

---

### Phase 2: Verification & Validation (~15s)

| Step | Command | Outputs | Est. Time |
|------|---------|---------|-----------|
| 2a | `python scripts/run_verification.py` | `results/baseline/simulation/verification/0{1..4}_*.json` | ~5s |
| 2b | `python scripts/run_validation_pilots.py` | `results/baseline/simulation/validation_pilot/*.json + *.csv` | ~10s |

**Outputs:**
- Verification: `01_toy_example.json`, `02_zero_demand.json`, `03_single_unit.json`, `04_extreme_demand.json`
- Validation: `pilot1_p0_vs_p2.json`, `pilot1_comparison_table.csv`, `pilot2_sensitivity_K.json`, `pilot2_sensitivity_K_table.csv`, `pilot3_sensitivity_demand.json`

---

### Phase 3: Analysis Artifacts (~5–10 minutes)

| Step | Script | Outputs | Est. Time | Data Source |
|------|--------|---------|-----------|-------------|
| 3a | `scripts/analysis/regenerate_all_figures.py` | `results/figures/` (21 canonical figures) | ~30s | `results/baseline/simulation/all_results_raw.csv` (V2 data) |
| 3b | `scripts/analysis/analyze_production_results.py` | `results/analysis/tables/` (8 tables) | ~10s | ⚠️ `results/analysis/simulation/production/` (V1 data, CAP=5) |
| 3c | `scripts/analysis/generate_publication_figures.py` | `results/analysis/figures/pub_fig*` (5 figs) | ~15s | ⚠️ `results/analysis/simulation/production/` (V1 data, CAP=5) |
| 3d | `scripts/analysis/generate_precinct_demand_visualizations.py` | `results/figures/precinct_demand_*.png` (2 figs) | ~10s | `data/processed/` |
| 3e | `scripts/analysis/analyze_queue_metrics.py` | `results/figures/queue_*.png`, `results/tables/queue_*.csv` | ~10s | ⚠️ V1-DATA refs |
| 3f | `scripts/analysis/analyze_seasonal_patterns.py` | `results/figures/seasonal_*.png`, `results/tables/seasonal_*.csv` | ~15s | `data/processed/crashes_manhattan.csv` |
| 3g | `scripts/analysis/generate_summary_dashboard.py` | `results/figures/project_summary_dashboard.png` | ~5s | ⚠️ V1-DATA refs, CAP=5 |
| 3h | `scripts/analysis/capacity_sensitivity_full_spectrum.py` | `results/analysis/capacity_comparison/` (full cap sweep) | ~3 min | Runs own simulations |
| 3i | `scripts/analysis/generate_capacity_sensitivity_heatmap.py` | `results/figures/capacity_sensitivity_heatmap.png` | ~5s | `results/analysis/capacity_comparison/` |
| 3j | `scripts/analysis/generate_all_heatmaps.py` | `results/analysis/heatmaps/` (108+ maps) | ~2 min | Runs own allocations |
| 3k | `scripts/analysis/run_cbd_experiment.py` | `results/analysis/simulation/cbd_experiment/` | ~30s | Runs own simulations |
| 3l | `scripts/analysis/run_cbd_focused_optimization.py` | `results/analysis/cbd_focused_comparison/` | ~30s | ⚠️ CAP=5 |
| 3m | `scripts/analysis/run_distance_comparison_experiment.py` | `results/analysis/distance_comparison/` | ~30s | ⚠️ CAP=5 |
| 3n | `scripts/analysis/p0_spatial_analysis.py` | `results/analysis/figures/p0_spatial_*.png` | ~10s | `data/processed/` |
| 3o | `scripts/analysis/generate_tradeoff_improved.py` | `results/figures/response_time_coverage_tradeoff*.png` | ~5s | ⚠️ CAP=5 |

**⚠️ CRITICAL: V1-vs-V2 Data Source Conflict**

Several analysis scripts (3b, 3c, 3e, 3g, 3l, 3m, 3o) still read from `results/analysis/simulation/production/` which contains **V1 data (cap=5)**. These scripts need to be either:
1. **Redirected** to read from `results/baseline/simulation/all_results_raw.csv` (V2, cap=2), OR
2. **Marked as V1-legacy** and excluded from canonical regeneration

---

### Phase 4: Unit Tests (~30s)

| Step | Command | Outputs | Est. Time |
|------|---------|---------|-----------|
| 4a | `python -m pytest tests/ -v` | Console output (39 tests across 4 modules) | ~30s |

---

### Phase 5: Documentation Reconciliation (~manual, 30–60 min)

After all artifacts are regenerated, update docs to reference correct files and metrics. See Section 3 below.

---

## === 2. CANONICAL ARTIFACT LIST ===

### Baseline Simulation (Source of Truth)

| Artifact | Path | Generated By |
|----------|------|-------------|
| Raw simulation data (810 rows) | `results/baseline/simulation/all_results_raw.csv` | `run_production_v2.py` |
| Per-K simulation results (9 files) | `results/baseline/simulation/results_K{N}.csv` | `run_production_v2.py` |
| Verification JSONs (4 files) | `results/baseline/simulation/verification/0{1..4}_*.json` | `run_verification.py` |
| Validation pilot JSONs (3 files) | `results/baseline/simulation/validation_pilot/pilot{1..3}_*.json` | `run_validation_pilots.py` |
| Validation comparison tables (2 files) | `results/baseline/simulation/validation_pilot/pilot{1,2}_*_table.csv` | `run_validation_pilots.py` |

### Baseline Tables (18 files)

| Artifact | Path |
|----------|------|
| Descriptive statistics | `results/baseline/tables/descriptive_statistics.csv` |
| ANOVA results | `results/baseline/tables/anova_results.csv` |
| Post-hoc comparisons | `results/baseline/tables/posthoc_comparisons.csv` |
| Confidence intervals | `results/baseline/tables/confidence_intervals.csv` |
| Effect sizes | `results/baseline/tables/effect_sizes.csv` |
| Queue statistics | `results/baseline/tables/queue_statistics.csv` |
| Queue ANOVA | `results/baseline/tables/queue_anova.csv` |
| Sensitivity summary | `results/baseline/tables/sensitivity_summary.csv` |
| Exp1 summary | `results/baseline/tables/exp1_summary.csv` |
| Exp2–4 pivot tables | `results/baseline/tables/exp{2,3,4}_pivot_rt.csv` |
| Production results | `results/baseline/tables/production_results.csv` |
| Seasonal analysis | `results/baseline/tables/seasonal_analysis.csv` |
| Statistical analysis | `results/baseline/tables/statistical_analysis.csv` |
| Publication Tables 1–4 | `results/baseline/tables/table{1..4}_*.csv` + `.tex` |
| Validation results | `results/baseline/tables/validation_results.csv` |

### Baseline Figures (44 files)

**EDA/Demand (10):** `fig_hourly_demand.png`, `fig_daily_demand.png`, `fig_temporal_trends.png`, `fig_crash_heatmap.png`, `fig_precinct_density.png`, `fig_precinct_demand.png`, `fig_demand_model_fit.png`, `fig_hourly_rates.png`, `fig_cbd_comparison.png`, `fig_firehouses_map.png`

**Optimization (5):** `fig_policy_comparison.png`, `fig_tradeoff_curve.png`, `policy_comparison.png`, `policy_comparison_panel_K20_cap2.png`, `p0_vs_p2_response_time.png`

**Experiment panels (4):** `exp1_policy_comparison.png`, `exp2_fleet_sensitivity.png`, `exp3_demand_sensitivity.png`, `exp4_service_robustness.png`

**Fleet/capacity (7):** `fleet_sensitivity_v2_dual.png`, `production_fleet_sensitivity.png`, `mean_rt_vs_K.png`, `p95_rt_vs_K.png`, `coverage_vs_K.png`, `utilization_vs_K.png`, `queue_metrics_vs_K.png`

**V&V (4):** `verification_toy_timeline.png`, `validation_p0_vs_p2.png`, `validation_sensitivity_K.png`, `validation_sensitivity_demand.png`

**Publication (5):** `pub_fig1_policy_comparison.png`, `pub_fig2_fleet_sensitivity.png`, `pub_fig3_demand_robustness.png`, `pub_fig4_service_sensitivity.png`, `pub_fig5_performance_heatmap.png`

**Allocation maps (3):** `allocation_map_K{20,30,40}.png`

**RT distributions (3):** `rt_distribution_K{20,30,40}.png`

**Other (3):** `response_time_distribution_by_policy.png`, `statistical_effect_sizes.png`, `effect_sizes.png`, `project_summary_dashboard.png`

### Baseline Allocations (9 files)

`results/baseline/allocations/allocations_K{10,15,20,25,30,35,40,45,48}.csv`

### Canonical Top-Level Figures (`results/figures/`, 21 files)

These are generated by `regenerate_all_figures.py` and individual analysis scripts:

| Figure | Generator | Status |
|--------|-----------|--------|
| `pub_fig1_policy_comparison.png` | `regenerate_all_figures.py` | ✅ V2 data |
| `pub_fig2_fleet_sensitivity.png` | `regenerate_all_figures.py` | ✅ V2 data |
| `pub_fig3_demand_robustness.png` | `regenerate_all_figures.py` | ✅ V2 data |
| `pub_fig4_service_sensitivity.png` | `regenerate_all_figures.py` | ✅ V2 data |
| `pub_fig5_performance_heatmap.png` | `regenerate_all_figures.py` | ✅ V2 data |
| `response_time_distribution_by_policy.png` | `regenerate_all_figures.py` | ✅ V2 data |
| `fleet_sensitivity_dual.png` | `regenerate_all_figures.py` | ✅ V2 data |
| `capacity_sensitivity_heatmap.png` | `generate_capacity_sensitivity_heatmap.py` | ⚠️ KNOWN BROKEN (data format issue) |
| `cbd_equity_tradeoff_summary.png` | `regenerate_all_figures.py` | ✅ V2 data |
| `cbd_robustness_enhanced.png` | `regenerate_all_figures.py` | ✅ V2 data |
| `precinct_demand_heatmap.png` | `generate_precinct_demand_visualizations.py` | ✅ from processed data |
| `precinct_demand_rates_improved.png` | `generate_precinct_demand_visualizations.py` | ✅ from processed data |
| `project_summary_dashboard.png` | `generate_summary_dashboard.py` | ⚠️ V1 data refs, CAP=5 |
| `queue_comparison_by_policy.png` | `analyze_queue_metrics.py` | ⚠️ V1 data refs |
| `queue_heatmap.png` | `analyze_queue_metrics.py` | ⚠️ V1 data refs |
| `queue_vs_demand.png` | `analyze_queue_metrics.py` | ⚠️ V1 data refs |
| `queue_vs_fleet_size.png` | `analyze_queue_metrics.py` | ⚠️ V1 data refs |
| `response_time_coverage_tradeoff.png` | `generate_tradeoff_improved.py` | ⚠️ CAP=5 |
| `seasonal_decomposition.png` | `analyze_seasonal_patterns.py` | ✅ from raw crash data |
| `seasonal_heatmap.png` | `analyze_seasonal_patterns.py` | ✅ from raw crash data |
| `seasonal_patterns.png` | `analyze_seasonal_patterns.py` | ✅ from raw crash data |

### Analysis Figures/Tables (`results/analysis/`)

| Subdirectory | Content | Generator |
|-------------|---------|-----------|
| `analysis/capacity_comparison/` | Full cap sweep (cap 1–5, K=20/40), 90+ CSV+PNG | `capacity_sensitivity_full_spectrum.py` |
| `analysis/cbd_focused_comparison/` | CBD vs Manhattan-wide comparison | `run_cbd_focused_optimization.py` ⚠️ CAP=5 |
| `analysis/distance_comparison/` | Haversine vs Manhattan distance | `run_distance_comparison_experiment.py` ⚠️ CAP=5 |
| `analysis/heatmaps/` | 108 allocation heatmap PNGs + allocations | `generate_all_heatmaps.py` |
| `analysis/maps/` | K=40 allocation maps (P0/P1/P2) | `p0_spatial_analysis.py` |
| `analysis/simulation/production/` | V1 experiment CSVs (cap=5) | ⚠️ LEGACY — `run_production_experiments.py` (archived) |
| `analysis/simulation/cbd_experiment/` | CBD experiment results | `run_cbd_experiment.py` |
| `analysis/figures/` | ~40 analysis figures | Various analysis scripts |
| `analysis/tables/` | ~20 analysis tables | `analyze_production_results.py` ⚠️ V1 |

---

## === 3. DOCS RECONCILIATION TARGET LIST ===

### README.md
- Verify all paths point to `results/baseline/` as source of truth
- Confirm capacity=2, spatial P0 messaging

### docs/core/ (30 files — check all, high-priority subset below)

| Document | Priority | What to check |
|----------|----------|---------------|
| `technical_report.md` | 🔴 HIGH | All metric values, figure references, table references, K=20 baseline numbers |
| `executive_summary.md` | 🔴 HIGH | Headline metrics (RT=2.57min, coverage=99.6%) match regenerated data |
| `executive_presentation.md` | 🔴 HIGH | Same as executive summary |
| `figure_trace_guide.md` | 🔴 HIGH | All 40+ figure entries match regenerated filenames and generators |
| `visualization_index.md` | 🟡 MED | Cross-check with regenerated figure set |
| `output_analysis.md` | 🟡 MED | Metrics match baseline tables |
| `experimental_design.md` | 🟡 MED | Parameters match (cap=2, reps=30, K values) |
| `verification_log.md` | 🟡 MED | V&V results match regenerated JSONs |
| `reproducibility_guide.md` | 🟡 MED | Commands still work |
| `decisions_log.md` | 🟢 LOW | Historical, unlikely to need changes |
| `assumptions_log.md` | 🟢 LOW | Historical |
| `conceptual_model.md` | 🟢 LOW | Model description, unlikely to need changes |
| `demand_model_spec.md` | 🟢 LOW | Spec, not metrics |
| `service_model_spec.md` | 🟢 LOW | Spec, not metrics |
| `optimization_formulation.md` | 🟢 LOW | Check capacity=2 is documented |
| `code_documentation.md` | 🟢 LOW | API descriptions |
| `testing_guide.md` | 🟢 LOW | Test count may change |
| `notebook_guide.md` | 🟢 LOW | Notebook descriptions |
| `data_usage_guide.md` | 🟢 LOW | Data paths |
| `ARCHITECTURAL_MAP.md` | 🟢 LOW | Structure description |
| `DOCUMENTATION_INDEX.md` | 🟢 LOW | Index of all docs |
| `source_manifest.md` | 🟢 LOW | File inventory |
| Other core docs | 🟢 LOW | Historical/reference |

### docs/analysis/ (14 files)

| Document | Priority | What to check |
|----------|----------|---------------|
| `capacity_sensitivity_analysis.md` | 🟡 MED | Metrics match regenerated capacity sweep |
| `cbd_focused_optimization_analysis.md` | 🟡 MED | Check if still references cap=5 data |
| `cbd_robustness_analysis.md` | 🟡 MED | Same |
| `queue_analysis.md` | 🟡 MED | Queue metrics match |
| `optimization_results.md` | 🟡 MED | Policy comparison metrics |
| `policy_tradeoff_analysis.md` | 🟡 MED | Tradeoff curve figures |
| `research_questions_assessment.md` | 🟡 MED | Answers reference correct metrics |
| `distance_metric_comparison.md` | 🟢 LOW | Distance analysis |
| `fleet_sensitivity_dual_investigation.md` | 🟢 LOW | Fleet sensitivity discussion |
| `firehouse_capacity_analysis.md` | 🟢 LOW | Capacity discussion |
| `eda_and_data_split_summary.md` | 🟢 LOW | Data description |
| `analysis_precinct_demand_trace.md` | 🟢 LOW | Demand trace |
| `cbd_comparison_and_validity_report.md` | 🟢 LOW | CBD validity |
| `alternative_analyses_summary.md` | 🟢 LOW | Summary of alternatives |

### `results/WHICH_FILES_TO_USE.md`
- 🟡 MED: Verify all paths and status markers are still correct after regeneration

---

## === 4. RISKS AND PREREQUISITES ===

### Prerequisites

| # | Prerequisite | How to Verify |
|---|-------------|---------------|
| P1 | `data/processed/` fully populated (13 files) | `ls data/processed/*.csv data/processed/*.geojson` |
| P2 | Python environment with all deps | `pip install -r requirements.txt` |
| P3 | PuLP solver available | `python -c "import pulp; pulp.LpSolverDefault"` |
| P4 | SimPy installed | `python -c "import simpy"` |
| P5 | ~2GB RAM available for 810 simulation runs | `free -m` |
| P6 | `src/ems_readiness/` imports clean | `python -c "from ems_readiness.simulation.engine import EMSSimulation"` |
| P7 | Git LFS files pulled (raw crash data not needed for simulation) | LFS only needed for data processing, not production runs |

### Risks

| # | Risk | Impact | Mitigation |
|---|------|--------|------------|
| R1 | **V1/V2 data source mismatch** — 7 analysis scripts still read V1 data (cap=5) from `results/analysis/simulation/production/` | ⚠️ HIGH: Analysis tables/figures won't match baseline | **Fix scripts before regeneration** to read from `results/baseline/simulation/all_results_raw.csv`, or explicitly mark as V1-legacy |
| R2 | **Broken capacity heatmap** — `generate_capacity_sensitivity_heatmap.py` produces blank panels (known "Data format issue") | 🟡 MED: One figure is known-broken | Debug the data format issue in the heatmap script before regeneration |
| R3 | **~20 possibly-broken figures** — White fraction >92% in many baseline and top-level figures | 🟡 MED: May indicate matplotlib rendering issues or sparse data | Visual inspection after regeneration; many are line/scatter plots with inherently white backgrounds |
| R4 | **Stochastic drift** — New random seeds could produce slightly different metrics than what docs quote | 🟢 LOW: Seeds are fixed (base=42), results should be deterministic | Verify key metrics (RT=2.57, coverage=99.6%) match within CI |
| R5 | **Long-running heatmap generation** — `generate_all_heatmaps.py` generates 108+ maps | 🟢 LOW: ~2 min | Run in background if needed |
| R6 | **Capacity sweep re-simulation** — `capacity_sensitivity_full_spectrum.py` runs its own simulations | 🟡 MED: Additional ~3 min, generates own data | Must run after baseline so comparative data is consistent |
| R7 | **CBD experiment uses dynamic parameters** — `run_cbd_experiment.py` may use different capacity defaults | 🟢 LOW | Verify capacity=2 is used |

### Validation Steps (Post-Regeneration)

| # | Validation | Command/Check |
|---|-----------|---------------|
| V1 | All 39 unit tests pass | `python -m pytest tests/ -v` |
| V2 | Baseline has 810 simulation rows | `wc -l results/baseline/simulation/all_results_raw.csv` (should be 811 incl header) |
| V3 | 9 allocation files exist | `ls results/baseline/allocations/` |
| V4 | 4 verification JSONs populated | `python -c "import json; [json.load(open(f'results/baseline/simulation/verification/0{i}_{n}.json')) for i,n in [(1,'toy_example'),(2,'zero_demand'),(3,'single_unit'),(4,'extreme_demand')]]"` |
| V5 | 3 validation pilots populated | Check `results/baseline/simulation/validation_pilot/` |
| V6 | Key metric check: K=20 P2 mean RT ≈ 2.57 min | `python -c "import pandas as pd; df=pd.read_csv('results/baseline/simulation/all_results_raw.csv'); print(df[(df.K==20)&(df.policy=='P2')].mean_response_time.mean())"` |
| V7 | No broken figures (visual spot-check) | Open `results/baseline/figures/pub_fig1_policy_comparison.png` etc. in browser |
| V8 | Capacity heatmap has actual data | Open `results/figures/capacity_sensitivity_heatmap.png` — should NOT show "Data format issue" |

---

## === 5. RECOMMENDED BRANCH/PR STRATEGY ===

### Strategy: Single Feature Branch with Staged Commits

```
main
 └── feature/canonical-regeneration
      ├── commit 1: "fix: redirect V1-referencing scripts to V2 baseline data"
      │             (fix 7 scripts that reference cap=5/V1 data)
      ├── commit 2: "fix: resolve capacity heatmap data format issue"
      │             (debug and fix generate_capacity_sensitivity_heatmap.py)
      ├── commit 3: "chore: regenerate baseline production outputs"
      │             (run_production_v2.py + verification + validation)
      ├── commit 4: "chore: regenerate analysis artifacts"
      │             (all analysis scripts in dependency order)
      ├── commit 5: "docs: reconcile documentation with regenerated outputs"
      │             (update all metrics, paths, figure references)
      └── commit 6: "test: verify all tests pass with regenerated data"
```

### Branch Naming
- `feature/canonical-regeneration` or `chore/full-refresh-v2`

### PR Description Template
```
## Full Canonical Regeneration

### What changed
- Fixed 7 analysis scripts to use V2 baseline data (cap=2) instead of V1 (cap=5)
- Fixed capacity sensitivity heatmap data format issue
- Regenerated all baseline simulation outputs (810 runs)
- Regenerated all analysis figures and tables
- Reconciled all documentation with fresh outputs

### Verification
- [ ] 39 unit tests pass
- [ ] 810 simulation rows in all_results_raw.csv
- [ ] Key metrics match: K=20 P2 RT ≈ 2.57 min, coverage ≈ 99.6%
- [ ] Capacity heatmap renders correctly
- [ ] All 3 validation pilots pass directional checks
- [ ] Visual spot-check of 5 publication figures
```

### Important Notes
- **Do NOT force-push** to main
- **Do NOT auto-merge** — requires human review
- Keep `results/archive/` untouched (historical reference)
- The `results/analysis/simulation/production/` V1 data can be preserved in `results/archive/` if needed for historical comparison

---

## === 6. EXECUTION ORDER SUMMARY ===

```
┌─────────────────────────────────────────────────────┐
│  BEFORE REGENERATION (code fixes)                    │
│  1. Fix V1→V2 data source in 7 analysis scripts     │
│  2. Fix capacity_sensitivity_heatmap.py bug          │
│  3. Commit fixes to feature branch                   │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│  PHASE 1: BASELINE PRODUCTION (~2 min)               │
│  python scripts/run_production_v2.py --reps 30       │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│  PHASE 2: VERIFICATION & VALIDATION (~15s)           │
│  python scripts/run_verification.py                  │
│  python scripts/run_validation_pilots.py             │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│  PHASE 3: ANALYSIS (order matters!)                  │
│  3a. regenerate_all_figures.py (needs baseline data) │
│  3b. analyze_production_results.py (after V1→V2 fix)│
│  3c. generate_publication_figures.py (after fix)     │
│  3d. generate_precinct_demand_visualizations.py      │
│  3e. analyze_queue_metrics.py (after V1→V2 fix)     │
│  3f. analyze_seasonal_patterns.py                    │
│  3g. generate_summary_dashboard.py (after fix)       │
│  3h. capacity_sensitivity_full_spectrum.py           │
│  3i. generate_capacity_sensitivity_heatmap.py        │
│  3j. generate_all_heatmaps.py                        │
│  3k. run_cbd_experiment.py                           │
│  3l. run_cbd_focused_optimization.py (after fix)     │
│  3m. run_distance_comparison_experiment.py (after fix)│
│  3n. p0_spatial_analysis.py                          │
│  3o. generate_tradeoff_improved.py (after fix)       │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│  PHASE 4: UNIT TESTS (~30s)                          │
│  python -m pytest tests/ -v                          │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│  PHASE 5: DOCUMENTATION RECONCILIATION               │
│  Update docs/core/technical_report.md (HIGH)         │
│  Update docs/core/executive_summary.md (HIGH)        │
│  Update docs/core/figure_trace_guide.md (HIGH)       │
│  Update 11 analysis docs (MED)                       │
│  Update results/WHICH_FILES_TO_USE.md                │
│  Update README.md                                    │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│  FINAL: COMMIT + PR                                  │
│  Staged commits as described in Section 5            │
│  DO NOT MERGE without human review                   │
└─────────────────────────────────────────────────────┘
```

---

## === 7. SCRIPTS REQUIRING V1→V2 DATA SOURCE FIX ===

These 7 scripts currently reference `results/analysis/simulation/production/` (V1 cap=5 data) and need to be redirected to `results/baseline/simulation/all_results_raw.csv` (V2 cap=2 data):

| # | Script | Current Data Source | Fix Required |
|---|--------|-------------------|--------------|
| 1 | `analyze_production_results.py` | `results/analysis/simulation/production/exp{1..4}_*.csv` | Redirect to V2 or refactor to read `all_results_raw.csv` |
| 2 | `generate_publication_figures.py` | Same V1 path | Same fix |
| 3 | `analyze_queue_metrics.py` | V1 experiment CSVs | Same fix |
| 4 | `generate_summary_dashboard.py` | V1 path + CAP=5 | Same fix + update CAPACITY constant |
| 5 | `run_cbd_focused_optimization.py` | Uses CAP=5 internally | Change to CAP=2 |
| 6 | `run_distance_comparison_experiment.py` | Uses CAP=5 internally | Change to CAP=2 |
| 7 | `generate_tradeoff_improved.py` | Uses CAP=5 internally | Change to CAP=2 |

**Estimated fix effort:** ~1 hour of careful script editing + testing

---

*This document is a planning artifact. No regeneration has been executed.*
