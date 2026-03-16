# Policy Trade-off Analysis

> **⚠️ Historical Context Note:** This analysis uses the **original index-based uniform P0** (deprecated), not the current spatially-stratified P0 baseline. The original P0 distributed units round-robin by firehouse index, resulting in poor geographic coverage (mean RT ≈ 18.5 min at K=20). The current P0 uses latitude-based spatial stratification and achieves 3.17 min mean RT at K=20. See [`docs/nomenclature_migration.md`](nomenclature_migration.md) for the full nomenclature history and [`docs/decisions_log.md`](decisions_log.md) DEC-011/DEC-012 for the rationale. The plots and tables below are retained for historical reference but should not be compared directly to production results that use the current P0 baseline.

## Overview

The **Response Time vs Coverage Trade-off** plot (`fig_tradeoff_curve.png` and improved versions) is one of the key decision-support visualizations in this project. It compares all allocation policies across multiple fleet sizes on two performance dimensions simultaneously, revealing which policies are efficient and which are dominated.

---

## What the Plot Shows

### Axes

| Axis | Metric | Definition |
|------|--------|------------|
| X-axis | **Expected Response Time** (minutes) | Demand-weighted average of the minimum travel time from the nearest active firehouse to each precinct. Computed as: `sum(min_tt_j * demand_j)` where `min_tt_j` is the travel time from the closest firehouse with >= 1 unit to precinct j. Lower is better. |
| Y-axis | **% Demand Covered (<=8 min)** | Percentage of total crash demand (weighted by precinct arrival rate) that falls within 8 minutes of travel time from an active firehouse. The 8-minute threshold follows the NFPA 1710 standard. A complementary 6-minute threshold aligns with NYC local law. Higher is better. |

### Visual Encodings

- **Color** encodes fleet size: K=20 (blue), K=30 (orange), K=40 (green), K=48 (red)
- **Marker shape** encodes policy (in improved version): P0=square, P1=triangle, P2=circle, P2b=diamond, P2c=plus
- **Ideal location**: upper-left corner (low response time, high coverage)

---

## Policies Compared

| ID | Policy | Type | Description |
|----|--------|------|-------------|
| **P0** | Uniform Baseline | Non-optimized | Distributes K units as evenly as possible across **all** firehouses in the travel-time index. This is the **standard uniform allocation** (round-robin) -- not the spatially-stratified P0-spatial variant. |
| **P1** | Demand-Proportional | Non-optimized | Allocates units proportional to crash demand of nearest precincts. A simple heuristic that concentrates units in high-demand areas. |
| **P2** | Demand-Weighted Optimized | MIP (PuLP/CBC) | Minimizes demand-weighted expected response time. Primary recommended policy. |
| **P2b** | P-Median Optimized | MIP (PuLP/CBC) | Selects K firehouses and assigns precincts to minimize total demand-weighted distance. |
| **P2c** | Maximal Coverage Optimized | MIP (PuLP/CBC) | Maximizes total demand covered within the 8-minute threshold. |

### Which P0 is Used?

**P0 in this plot is the standard uniform allocation** (`policies.uniform_allocation()`), which distributes K units round-robin across all 48 Manhattan firehouses. It is **not** the spatially-stratified P0-spatial (latitude/grid/maximin) introduced later in the project for fairer baseline comparison.

This matters because:
- With K=20, uniform allocation spreads 1 unit each across 20 of 48 firehouses (round-robin by index order), which can leave large geographic gaps, hence the poor performance (RT=18.5 min, coverage=73%).
- The spatially-stratified P0 would perform better at low K because it selects firehouses with geographic spread.

---

## Key Findings from the Data

### Performance Summary

| K | P0 RT | P0 Cov | P1 RT | P1 Cov | P2 RT | P2 Cov | P2b RT | P2b Cov | P2c RT | P2c Cov |
|---|-------|--------|-------|--------|-------|--------|--------|---------|--------|---------|
| 20 | 18.55 | 73.0% | 2.87 | 100% | 2.54 | 100% | 2.54 | 100% | 3.48 | 100% |
| 30 | 7.00 | 92.0% | 2.52 | 100% | 2.49 | 100% | 2.49 | 100% | 3.48 | 100% |
| 40 | 3.02 | 100% | 2.52 | 100% | 2.49 | 100% | 2.49 | 100% | 3.48 | 100% |
| 48 | 2.49 | 100% | 2.52 | 100% | 2.49 | 100% | 2.49 | 100% | 3.48 | 100% |

### Pareto Frontier

The **Pareto frontier** (efficient frontier) consists of policies where you cannot improve one metric without worsening the other. In this dataset:

1. **P2 and P2b dominate all other policies** at every fleet size -- they achieve the lowest response time while maintaining 100% coverage at all tested K values.
2. **P2 and P2b are essentially identical** in performance (both achieve RT=2.49 min at K>=30), meaning the demand-weighted and p-median formulations converge to the same solution for this problem geometry.
3. **P1 is near-efficient** -- only ~0.4 min worse than P2 at K=20 (2.87 vs 2.54), making it a strong heuristic.
4. **P2c is consistently suboptimal** on the RT dimension (RT=3.48 at all K), because it optimizes for coverage threshold rather than minimizing response time.
5. **P0 is severely dominated at low K** (K=20: RT=18.5 min, 73% coverage) but converges to optimal at K=48 when every firehouse gets a unit.

### Why Points Overlap

Most points for K >= 30 cluster in the upper-left corner (RT ~ 2.5 min, coverage ~ 100%) because:
- Manhattan's 48 firehouses are dense enough that with 30+ units, all policies achieve near-full coverage
- The optimization models converge to similar solutions when capacity is not constraining
- The real differentiation happens at **low fleet sizes** (K=20-30), which is the operationally relevant range

---

## Downstream Usage

| Consumer | How it's used |
|----------|---------------|
| **Technical Report** (Section 5) | Primary evidence for policy recommendation |
| **Policy Recommendation** (DEC-007) | Supports "P2 with K=20-30" recommendation |
| **Fleet Sizing Decision** | Shows diminishing returns above K=30 |
| **Stakeholder Communication** | Visual summary of the cost-effectiveness trade-off |

---

## Files

| File | Description |
|------|-------------|
| `scripts/run_optimization_comparison.py` (lines 253-273) | Original generation code |
| `scripts/generate_tradeoff_improved.py` | Improved visualization script |
| `results/figures/fig_tradeoff_curve.png` | Original plot (has overlapping labels) |
| `results/figures/response_time_coverage_tradeoff_improved.png` | Improved main plot with data table |
| `results/figures/response_time_coverage_tradeoff_zoomed.png` | Zoomed view of high-performance region |
| `results/optimization/policy_comparison.csv` | Source data |

---

## Recommendations Based on Trade-off

1. **Use P2 (Demand-Weighted) as the primary policy.** It dominates or ties all alternatives at every fleet size.
2. **K=20-30 is the sweet spot.** Beyond K=30, there is minimal improvement in either RT or coverage.
3. **P1 is a reasonable fallback** if optimization infrastructure is unavailable -- it performs within 15% of optimal.
4. **P2c (Maximal Coverage) is not recommended** as the primary policy -- it consistently underperforms P2 on response time while offering no coverage advantage.
5. **P0 (Uniform) should only be used as a comparison baseline**, not for operational deployment, especially at low K.
