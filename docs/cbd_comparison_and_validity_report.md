# CBD Comparison Data & Result Validity Report

**EMS Optimization Project** | March 12, 2026

---

## 1. Manhattan-Wide vs CBD Comparison Data

### 1.1 Primary Comparison Table (`results/tables/cbd_comparison.csv`)

This table directly compares **overall Manhattan** metrics against **CBD-specific** and **non-CBD** subregions under baseline conditions:

| Policy | Overall Mean RT | CBD Mean RT | Non-CBD Mean RT | Overall Coverage (8 min) | CBD Coverage | Non-CBD Coverage |
|--------|:-:|:-:|:-:|:-:|:-:|:-:|
| **P0** (status quo) | 8.08 min | 2.73 min | 14.76 min | 64.4% | 99.9% | 20.3% |
| **P1** (nearest) | 2.63 min | 2.44 min | 2.88 min | 99.6% | 99.9% | 99.1% |
| **P2** (optimized) | 2.57 min | 2.48 min | 2.68 min | 99.6% | 99.9% | 99.2% |

**Key insight**: Under P0, the CBD enjoys excellent service (2.73 min, 99.9% coverage) while non-CBD areas suffer catastrophically (14.76 min, 20.3% coverage). P1 and P2 equalize performance across both subregions.

### 1.2 Full Scenario Comparison (`results/tables/cbd_summary_all.csv`)

This table extends the comparison across all 4 CBD stress-test scenarios:

| Scenario | Policy | Overall RT | CBD RT | Non-CBD RT | Overall Cov. | CBD Cov. | Non-CBD Cov. | Incidents |
|----------|--------|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| **baseline** | P0 | 8.08 | 2.73 | 14.76 | 64.4% | 99.9% | 20.3% | 576.9 |
| **baseline** | P1 | 2.63 | 2.44 | 2.88 | 99.6% | 99.9% | 99.1% | 574.1 |
| **baseline** | P2 | 2.57 | 2.48 | 2.68 | 99.6% | 99.9% | 99.2% | 574.7 |
| **cbd_surge** (2× demand) | P0 | 8.35 | 2.91 | 15.13 | 63.1% | 99.5% | 17.9% | 909.6 |
| **cbd_surge** | P1 | 2.75 | 2.53 | 3.02 | 99.2% | 99.8% | 98.4% | 907.8 |
| **cbd_surge** | P2 | 2.73 | 2.61 | 2.87 | 99.3% | 99.8% | 98.7% | 906.8 |
| **cbd_slow_service** (35 min) | P0 | 8.15 | 2.77 | 14.88 | 64.2% | 99.9% | 19.6% | 576.6 |
| **cbd_slow_service** | P1 | 2.68 | 2.47 | 2.94 | 99.5% | 99.9% | 98.9% | 574.0 |
| **cbd_slow_service** | P2 | 2.63 | 2.53 | 2.75 | 99.6% | 99.9% | 99.2% | 574.6 |
| **cbd_only** | CBD_ONLY | 8.35 | 2.97 | 15.05 | 63.5% | 99.9% | 18.1% | 576.9 |
| **mixed** | MIXED | 8.35 | 2.97 | 15.05 | 63.5% | 99.9% | 18.1% | 576.9 |

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

### 2.1 Production Runs: UNCHANGED ✅

The original 1,440 production simulation runs are **completely intact** in their original location:

| Experiment | File | Rows | Description |
|------------|------|:----:|-------------|
| exp1 | `production/exp1_policy_comparison.csv` | 90 | Policy comparison (P0/P1/P2 × 30 reps) |
| exp2 | `production/exp2_fleet_sensitivity.csv` | 540 | Fleet size sensitivity |
| exp3 | `production/exp3_demand_sensitivity.csv` | 540 | Demand multiplier sensitivity |
| exp4 | `production/exp4_service_robustness.csv` | 270 | Service time robustness |
| **Total** | | **1,440** | |

**Timestamp verification**: All production files were last modified at ~20:51–20:54 UTC on March 12, 2026 (the original production run time). They have **not been touched** since.

### 2.2 CBD Experiment: ADDITIVE ✅

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

### 2.3 Queue Analysis: Based on SAME Data ✅

The queue analysis (`results/tables/queue_statistics.csv`) references both production and CBD experiment data. It **reads** from the existing CSVs without modifying them. Key finding confirmed across all 1,770 runs: **queue_fraction = 0.0** everywhere.

### 2.4 Seasonal Analysis: Based on SAME Underlying Data ✅

The seasonal analysis (`results/tables/seasonal_analysis.csv`) is based on the **original 416,434 crash records** — the same demand dataset used throughout the project. It performs a temporal decomposition of the input data, not the simulation outputs.

### 2.5 All Previous Deliverables: VALID ✅

| Category | Status | Notes |
|----------|--------|-------|
| Experiment results (exp1–exp4) | ✅ Unchanged | 1,440 runs in `production/` directory |
| Statistical tables (ANOVA, CIs, effect sizes) | ✅ Valid | Based on unchanged production data |
| Publication figures (pub_fig1–5) | ✅ Valid | Generated from unchanged data |
| Optimization results | ✅ Valid | Based on unchanged simulation outputs |
| Technical documentation | ✅ Valid | Enhanced with new sections, originals preserved |

---

## 3. Summary

1. **The CBD vs Manhattan comparison data** is in `results/tables/cbd_comparison.csv` and `results/tables/cbd_summary_all.csv`, with visualizations in `results/figures/cbd_*.png` and full analysis in `docs/cbd_robustness_analysis.pdf`.

2. **All previous results remain 100% valid.** The gap resolution was purely additive — 330 new CBD runs in a separate directory, plus new analysis scripts and documentation. The original 1,440 production runs, all figures, tables, and findings are untouched and unchanged.
