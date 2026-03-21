---
status: 🔄 HISTORICAL
last_updated: "2026-03-20"
note: "Preserved for project history. Contains old metrics/references in historical context. Do not use as current reference."
---
# Gap Closure Report

**EMS Optimization Project**
**Date:** March 12, 2026

---

## Overview

This report documents the resolution of all three gaps identified in the project alignment verification. All gaps have been addressed, bringing project alignment from **98% to 100%**.

---

## Gap Summary

| ID | Gap | Status | Resolution |
|----|-----|--------|------------|
| G1 | CBD-specific robustness analysis | RESOLVED | Full DES experiment with 4 CBD scenarios |
| G2 | Queue metrics prominence | RESOLVED | Comprehensive queue analysis with visualizations |
| G3 | Seasonal variation analysis | RESOLVED | Monthly pattern analysis with statistical tests |

---

## G1: CBD Robustness Analysis

### What was done
- Defined CBD region using MTA Congestion Relief Zone boundary
- Identified 10 CBD precincts (≥30% overlap criterion)
- Designed and ran 4 CBD-specific DES scenarios:
 - Scenario A: CBD demand surge (2× CBD demand)
 - Scenario B: CBD service time increase (35 min vs 25 min)
 - Scenario C: CBD-only allocation
 - Scenario D: Mixed allocation (60/40 CBD/non-CBD)
- Executed 330 simulation runs (30 replications each)
- Created CBD analysis notebook with visualizations
- Generated 3 new figures and 2 new tables

### Key findings
- P2 maintains its advantage across all CBD scenarios
- CBD response times are inherently lower due to firehouse concentration
- Even under 2× demand surge, P2 achieves 99.3% overall coverage
- No queuing observed in any CBD scenario

### Deliverables
- `docs/cbd_definition.md` — CBD geographic definition
- `configs/cbd_scenario.yaml` — Scenario configuration
- `scripts/run_cbd_experiment.py` — Experiment runner
- `notebooks/09_cbd_analysis.ipynb` — Analysis notebook
- `docs/cbd_robustness_analysis.md` — Findings document
- `results/analysis/simulation/cbd_experiment/` — Experiment data
- `results/figures/cbd_*.png` — 3 figures
- `results/tables/cbd_*.csv` — 2 tables

---

## G2: Queue Metrics Prominence

### What was done
- Created queue metrics extraction script
- Analyzed queue behavior across all production and CBD experiments
- Performed ANOVA on queue metrics
- Generated 4 queue-focused visualizations
- Created dedicated queue analysis document
- Updated technical report with queue analysis section

### Key findings
- Queue fraction = 0.0 across ALL experiments
- No incidents queued in any replication (1,770+ total runs)
- Low utilization (~10-15%) explains absence of queuing
- Response time differences between policies are purely spatial

### Deliverables
- `scripts/analyze_queue_metrics.py` — Analysis script
- `docs/queue_analysis.md` — Detailed analysis document
- `results/figures/queue_*.png` — 4 figures
- `results/tables/queue_statistics.csv` — Statistics table
- `results/tables/queue_anova.csv` — ANOVA results

---

## G3: Seasonal Variation Analysis

### What was done
- Analyzed 416,434 crash records for monthly patterns
- Computed monthly demand rates and seasonal factors
- Performed statistical tests (chi-square, ANOVA, Kruskal-Wallis)
- Created seasonal decomposition (trend, seasonal, residual)
- Generated 3 seasonal visualizations
- Updated demand model documentation

### Key findings
- Coefficient of variation: ~9% (moderate seasonal variation)
- Peak month: October (factor = 1.103)
- Trough month: February (factor = 0.822)
- Seasonal amplitude: ~28%
- Chi-square test rejects uniformity (p < 0.001)
- Annual average is a reasonable approximation for simulation
- Seasonal adjustments recommended for high-fidelity models

### Deliverables
- `scripts/analyze_seasonal_patterns.py` — Analysis script
- `results/figures/seasonal_patterns.png` — Monthly bar chart
- `results/figures/seasonal_decomposition.png` — Decomposition plot
- `results/figures/seasonal_heatmap.png` — Month × Hour heatmap
- `results/tables/seasonal_analysis.csv` — Monthly statistics

---

## Updated Project Statistics

| Metric | Before | After |
|--------|--------|-------|
| Alignment score | 98% | **100%** |
| Simulation runs | 1,440 | **1,770** |
| Figures | ~30 | **~42** |
| Tables | ~12 | **~18** |
| Documentation pages | 15 | **21** |
| Analysis scripts | 6 | **9** |
| Notebooks | 8 | **9** |

---

## Verification

All gaps have been verified as resolved:
- CBD experiments run successfully (330 runs, 39.6 seconds)
- Queue analysis complete with all visualizations
- Seasonal analysis complete with statistical tests
- All documentation updated
- Technical report enhanced with three new sections
- Git committed and tagged as v1.1.0

---

## Conclusion

The project now achieves **100% alignment** with the project outline. All three identified gaps have been addressed thoroughly with new experiments, analyses, visualizations, and documentation.
