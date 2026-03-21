---
status: 📋 REFERENCE
last_updated: "2026-03-20"
verified: "Specialized analysis document. Cross-reference with current production results."
---
# Alternative Analyses Summary

**Date:** March 12, 2026 
**Version:** 1.0 
**Author:** EMS Optimization Team

---

## Overview

Two alternative analyses were conducted to strengthen the robustness of the EMS Readiness Optimisation study. These analyses explore (1) the sensitivity of results to the distance metric choice, and (2) the tradeoffs between Manhattan-wide and CBD-focused optimisation strategies.

---

## Analysis 1: Haversine vs Manhattan Distance Metric

### Question
Does the choice of distance metric (Haversine vs Manhattan/taxicab) significantly affect EMS allocation decisions or simulated performance?

### Method
- Implemented Manhattan (L1) distance: `d = |Δlat| × 69.0 + |Δlon| × 52.3` miles
- Generated a Manhattan distance matrix (48 firehouses × 30 precincts)
- Solved P2 under both metrics and simulated (10 replications each)

### Key Findings

| Metric | Mean RT (min) | Coverage (≤8 min) | Active Firehouses |
|--------|--------------|-------------------|-------------------|
| Haversine P0 | 3.17 | 99.6% | 20 |
| Haversine P1 | 2.63 | 99.6% | 20 |
| Haversine P2 | 2.57 | 99.6% | 20 |
| Manhattan P2 | 2.55 | 99.6% | 20 |

- Manhattan distances are ~27% longer than Haversine on average
- Allocations differ at only 2 of 48 firehouses
- **Simulation performance is effectively identical** because the scaling is uniform

### Recommendation
Haversine is adequate for this study. Both metrics preserve the same relative distance ordering. Real road-network distances would provide more meaningful improvement.

**Full report:** `docs/distance_metric_comparison.md`

---

## Analysis 2: Manhattan-Wide vs CBD-Focused Optimisation

### Question
Would optimising EMS allocation specifically for CBD precincts improve CBD response times, and at what cost to the rest of Manhattan?

### Method
- Implemented CBD-focused demand-weighted allocation (objective considers only 10 CBD precincts)
- Compared against Manhattan-wide P2 (all 25 precincts in objective)
- Ran 10 replications each and disaggregated results by region

### Key Findings

| Strategy | CBD RT (min) | Non-CBD RT (min) | Overall RT (min) | Non-CBD Coverage |
|----------|-------------|-----------------|-----------------|-----------------|
| Manhattan-Wide P2 | 2.47 | 2.66 | 2.55 | 99.2% |
| CBD-Focused P2 | 2.50 | 6.88 | 4.42 | 73.6% |

- **CBD-focused allocation does NOT improve CBD performance** (marginally worse: 2.50 vs 2.47 min)
- **Non-CBD response time increases by 159%** (from 2.66 to 6.88 min)
- **Non-CBD coverage drops from 99.2% to 73.6%**
- The demand-weighted objective already effectively prioritises CBD through its high demand weights

### Recommendation
The Manhattan-wide P2 allocation is strongly preferred. It achieves near-identical CBD performance while maintaining equitable service across all communities. The demand-weighted formulation is a self-balancing approach.

**Full report:** `docs/cbd_focused_optimization_analysis.md`

---

## Combined Conclusions

1. **Model robustness confirmed:** The baseline P2 allocation is robust to distance metric choice
2. **Equity validated:** The demand-weighted approach naturally balances efficiency and equity
3. **Geographic targeting unnecessary:** Explicit CBD targeting provides no CBD benefit while significantly harming non-CBD communities
4. **Future work:** Real road-network distances would be a more impactful enhancement than alternative distance metrics

## New Files Created

### Scripts
- `scripts/generate_manhattan_distance_matrix.py` — Manhattan distance matrix generation
- `scripts/run_distance_comparison_experiment.py` — Distance metric comparison experiment
- `scripts/run_cbd_focused_optimization.py` — CBD-focused optimisation experiment

### Data
- `data/processed/distance_matrix_firehouse_precinct_manhattan.csv` — Manhattan distance matrix

### Results
- `results/analysis/distance_comparison/` — Distance comparison figures and tables
- `results/analysis/cbd_focused_comparison/` — CBD-focused comparison figures and tables

### Documentation
- `docs/distance_metric_comparison.md` — Distance metric comparison report
- `docs/cbd_focused_optimization_analysis.md` — CBD-focused analysis report
- `docs/alternative_analyses_summary.md` — This summary document

### Modified Files
- `src/ems_readiness/utils/distance.py` — Added `manhattan_distance()` function
- `src/ems_readiness/optimization/models.py` — Added `build_cbd_focused_demand_weighted()` and `build_cbd_focused_coverage()`
