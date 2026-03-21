---
status: ✅ CURRENT
last_updated: "2026-03-20"
verified: "All metrics, code references, and nomenclature are current as of March 2026"
---
# CBD Comparison Data & Result Validity Report

**EMS Optimization Project** | March 12, 2026

---

## 1. Manhattan-Wide vs CBD Comparison Data

### 1.1 Primary Comparison Table (`results/tables/cbd_comparison.csv`)

This table directly compares **overall Manhattan** metrics against **CBD-specific** and **non-CBD** subregions under baseline conditions:

| Policy | Overall Mean RT | CBD Mean RT | Non-CBD Mean RT | Overall Coverage (8 min) | CBD Coverage | Non-CBD Coverage |
|--------|:-:|:-:|:-:|:-:|:-:|:-:|
| **P0** (spatially-stratified) | 3.17 min | 2.75 min | 3.69 min | 99.7% | 100.0% | 99.3% |
| **P1** (demand-proportional) | 2.62 min | 2.44 min | 2.84 min | 99.6% | 100.0% | 99.3% |
| **P2** (demand-weighted MIP) | 2.57 min | 2.48 min | 2.67 min | 99.7% | 100.0% | 99.4% |

**Key insight**: All three policies achieve excellent CBD coverage (100.0%). P0 has slightly higher non-CBD response times (3.69 min) due to its uniform geographic distribution. P2 achieves the most balanced performance across both subregions.

### 1.2 Full Scenario Comparison (`results/tables/cbd_summary_all.csv`)

This table extends the comparison across all 4 CBD stress-test scenarios:

| Scenario | Policy | Overall RT | CBD RT | Non-CBD RT | Overall Cov. | CBD Cov. | Non-CBD Cov. | Incidents |
|----------|--------|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| **baseline** | P0 | 3.17 | 2.75 | 3.69 | 99.7% | 100.0% | 99.3% | 570.6 |
| **baseline** | P1 | 2.62 | 2.44 | 2.84 | 99.6% | 100.0% | 99.3% | 572.8 |
| **baseline** | P2 | 2.57 | 2.48 | 2.67 | 99.7% | 100.0% | 99.4% | 571.4 |
| **cbd_surge** (2× demand) | P0 | 3.28 | 2.83 | 3.85 | 99.2% | 99.9% | 98.4% | 906.5 |
| **cbd_surge** | P1 | 2.78 | 2.54 | 3.06 | 99.2% | 99.9% | 98.4% | 908.6 |
| **cbd_surge** | P2 | 2.73 | 2.61 | 2.87 | 99.4% | 99.8% | 98.8% | 906.8 |
| **cbd_slow_service** (35 min) | P0 | 3.20 | 2.77 | 3.74 | 99.6% | 100.0% | 99.0% | 570.5 |
| **cbd_slow_service** | P1 | 2.67 | 2.47 | 2.91 | 99.5% | 99.9% | 99.1% | 572.7 |
| **cbd_slow_service** | P2 | 2.62 | 2.53 | 2.74 | 99.6% | 99.9% | 99.2% | 571.2 |
| **cbd_only** | CBD_ONLY | 8.32 | 2.97 | 15.06 | 63.2% | 99.8% | 17.0% | 578.0 |
| **mixed** | MIXED | 8.32 | 2.97 | 15.06 | 63.2% | 99.8% | 17.0% | 578.0 |

### 1.3 Figures Showing the Comparison

Three figures visualize the CBD vs Manhattan comparison:

- **`results/figures/fig_cbd_comparison.png`** — Side-by-side bar chart of CBD vs non-CBD response times
- **`results/figures/cbd_response_comparison.png`** — Response time distributions by subregion
- **`results/figures/cbd_scenario_comparison.png`** — Performance across all CBD stress scenarios
- **`results/figures/cbd_heatmap.png`** — Spatial heatmap of CBD performance

### 1.4 Documentation

- **`docs/cbd_robustness_analysis.pdf`** — Full written analysis with interpretation
- **`docs/cbd_definition.pdf`** — Geographic definition of the CBD (10 precincts with ≥30% overlap with MTA Congestion Relief Zone)

---

## 2. Validity of Previous Results (Phases 1–7)

### 2.1 Production Runs: UNCHANGED — PASS
The original 1,440 production simulation runs are **completely intact** in their original location:

| Experiment | File | Rows | Description |
|------------|------|:----:|-------------|
| exp1 | `production/exp1_policy_comparison.csv` | 90 | Policy comparison (P0/P1/P2 × 30 reps) |
| exp2 | `production/exp2_fleet_sensitivity.csv` | 540 | Fleet size sensitivity |
| exp3 | `production/exp3_demand_sensitivity.csv` | 540 | Demand multiplier sensitivity |
| exp4 | `production/exp4_service_robustness.csv` | 270 | Service time robustness |
| **Total** | | **1,440** | |

**Timestamp verification**: All production files were last modified at ~20:51–20:54 UTC on March 12, 2026 (the original production run time). They have **not been touched** since.

### 2.2 CBD Experiment: ADDITIVE — PASS
The CBD experiment (330 runs) is stored in a **completely separate directory**:

```
results/simulation/
├── production/ ← Original 1,440 runs (UNTOUCHED)
│ ├── exp1_policy_comparison.csv
│ ├── exp2_fleet_sensitivity.csv
│ ├── exp3_demand_sensitivity.csv
│ └── exp4_service_robustness.csv
└── cbd_experiment/ ← NEW 330 runs (ADDITIVE)
 ├── cbd_experiment_results.csv
 └── cbd_experiment_summary.csv
```

- CBD files were created at 22:10 UTC — **~1.5 hours after** the production runs
- No production files were modified during or after the CBD experiment
- Total project runs: 1,440 + 330 = **1,770 runs**

### 2.3 Queue Analysis: Based on SAME Data — PASS
The queue analysis (`results/tables/queue_statistics.csv`) references both production and CBD experiment data. It **reads** from the existing CSVs without modifying them. Key finding confirmed across all 1,770 runs: **queue_fraction = 0.0** everywhere.

### 2.4 Seasonal Analysis: Based on SAME Underlying Data — PASS
The seasonal analysis (`results/tables/seasonal_analysis.csv`) is based on the **original 416,434 crash records** — the same demand dataset used throughout the project. It performs a temporal decomposition of the input data, not the simulation outputs.

### 2.5 All Previous Deliverables: VALID — PASS
| Category | Status | Notes |
|----------|--------|-------|
| Experiment results (exp1–exp4) | Unchanged | 1,440 runs in `production/` directory |
| Statistical tables (ANOVA, CIs, effect sizes) | Valid | Based on unchanged production data |
| Publication figures (pub_fig1–5) | Valid | Generated from unchanged data |
| Optimization results | Valid | Based on unchanged simulation outputs |
| Technical documentation | Valid | Enhanced with new sections, originals preserved |

---

## 3. Summary

1. **The CBD vs Manhattan comparison data** is in `results/tables/cbd_comparison.csv` and `results/tables/cbd_summary_all.csv`, with visualizations in `results/figures/cbd_*.png` and full analysis in `docs/cbd_robustness_analysis.pdf`.

2. **All previous results remain 100% valid.** The gap resolution was purely additive — 330 new CBD runs in a separate directory, plus new analysis scripts and documentation. The original 1,440 production runs, all figures, tables, and findings are untouched and unchanged.
