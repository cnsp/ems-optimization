# CBD-Focused vs Manhattan-Wide Optimization Analysis

**Date:** March 12, 2026 
**Version:** 1.0 
**Author:** EMS Optimization Team

---

## 1. Motivation

The baseline EMS optimisation (P2: demand-weighted allocation) minimises the **Manhattan-wide** expected response time, treating all 25 precincts equally in the objective function. Given that the Central Business District (CBD) accounts for ~56% of all crash demand from only 10 precincts, a natural question arises:

> **Would dedicating resources specifically to the CBD improve CBD response times, and at what cost to non-CBD precincts?**

This analysis compares two optimisation strategies to examine the **equity vs efficiency tradeoff** in EMS resource allocation.

## 2. Methodology

### 2.1 Optimisation Formulations

| Strategy | Objective | Precincts in Objective |
|----------|-----------|----------------------|
| **Manhattan-Wide P2** | min Σⱼ dⱼ Σᵢ tᵢⱼ yᵢⱼ | All 25 precincts |
| **CBD-Focused P2** | min Σⱼ∈CBD dⱼ Σᵢ tᵢⱼ yᵢⱼ | 10 CBD precincts only |

Both formulations:
- Allocate K=20 total EMS units
- Maximum 2 units per firehouse
- Assign all precincts to exactly one firehouse (feasibility)
- Use the same Haversine travel-time matrix

The CBD-focused model uses `build_cbd_focused_demand_weighted()` from `src/ems_readiness/optimization/models.py`.

### 2.2 CBD Precincts

Per `docs/cbd_definition.md`, the 10 CBD precincts are: 1, 5, 6, 7, 9, 10, 13, 14, 17, 18.

### 2.3 Experiment Design

1. Solve both optimisations for K=20
2. Run 10 replications per allocation using the DES simulation engine
3. Disaggregate results into CBD and non-CBD response times
4. Compute coverage fractions (≤ 8 min threshold) by region

## 3. Results

### 3.1 Allocation Comparison

| Metric | Manhattan-Wide P2 | CBD-Focused P2 |
|--------|-------------------|----------------|
| **Total units** | 20 | 20 |
| **Active firehouses** | 20 | 12 |
| **CBD firehouses used** | ~10 | ~12 |
| **Non-CBD firehouses used** | ~10 | ~0 |

The CBD-focused optimisation concentrates all 20 units in firehouses near the CBD, leaving non-CBD precincts without dedicated nearby units.

### 3.2 Response Time Performance

| Strategy | CBD RT (min) | Non-CBD RT (min) | Overall RT (min) |
|----------|-------------|-----------------|-----------------|
| **Manhattan-Wide P2** | 2.47 ± 0.04 | 2.66 ± 0.05 | 2.55 ± 0.03 |
| **CBD-Focused P2** | 2.50 ± 0.06 | 6.88 ± 0.24 | 4.42 ± 0.12 |

### 3.3 Coverage Performance

| Strategy | CBD Coverage (≤8 min) | Non-CBD Coverage (≤8 min) |
|----------|-----------------------|--------------------------|
| **Manhattan-Wide P2** | 100.0% | 99.2% |
| **CBD-Focused P2** | 99.9% | 73.6% |

### 3.4 Key Finding: The Equity Tradeoff

The CBD-focused allocation:
- **Does not improve** CBD response times (2.50 vs 2.47 min — marginally worse)
- **Dramatically worsens** non-CBD response times (6.88 vs 2.66 min — 159% increase)
- **Degrades** non-CBD coverage from 99.2% to 73.6%
- **Increases** overall response time from 2.55 to 4.42 min (73% worse)

## 4. Figures

| Figure | Description |
|--------|-------------|
| `results/cbd_focused_comparison/cbd_focused_comparison.png` | Grouped bar chart of CBD vs non-CBD response times and coverage |
| `results/cbd_focused_comparison/allocation_comparison.png` | Horizontal bar chart showing unit placement for each strategy |
| `results/cbd_focused_comparison/equity_tradeoff.png` | Scatter plot of CBD RT vs non-CBD RT tradeoff |

## 5. Discussion

### 5.1 Why CBD-Focused Doesn't Help the CBD

The Manhattan-wide optimisation already allocates significant resources near the CBD because:
1. The demand-weighted objective naturally concentrates units where demand is highest
2. CBD precincts generate 56% of all demand, so they already receive proportional attention
3. The additional units in the CBD-focused model provide negligible marginal benefit

### 5.2 Why CBD-Focused Hurts Non-CBD

When all units are concentrated in CBD firehouses:
- Non-CBD incidents must be served by distant units
- Travel times for northern Manhattan (precincts 30, 32, 33, 34, 50, 52) increase dramatically
- The dispatch model sends the nearest available unit, but "nearest" becomes very far for non-CBD precincts

### 5.3 Equity Implications

From a public policy perspective:
- **Equal access to emergency services** is a fundamental equity principle
- Concentrating resources in the CBD would disproportionately harm residents of:
 - Washington Heights (Pct 33, 34)
 - Harlem (Pct 25, 26, 28, 30, 32)
 - East Harlem (Pct 23, 25)
- These areas typically have lower income levels, creating an **environmental justice concern**

### 5.4 When CBD-Focused Might Make Sense

A CBD-focused strategy could be justified during:
- **Special events** (e.g., Times Square New Year's Eve) with temporary demand surges
- **Time-of-day** periods when non-CBD demand drops to near zero (very late night)
- **Multi-tier systems** where a separate non-CBD fleet exists

## 6. Recommendation

**The Manhattan-wide P2 allocation is strongly preferred** over the CBD-focused alternative because:

1. It achieves near-identical CBD performance (2.47 vs 2.50 min)
2. It maintains excellent non-CBD performance (2.66 vs 6.88 min)
3. It preserves equitable coverage across all communities
4. The demand-weighted objective naturally prioritises high-demand areas without explicit geographic targeting

The results confirm that the demand-weighted formulation is an effective "self-balancing" approach that delivers both **efficiency** (low overall RT) and **equity** (balanced regional performance).

## 7. Files Generated

| File | Description |
|------|-------------|
| `src/ems_readiness/optimization/models.py` | New functions: `build_cbd_focused_demand_weighted()`, `build_cbd_focused_coverage()` |
| `scripts/run_cbd_focused_optimization.py` | Experiment script |
| `results/cbd_focused_comparison/comparison_table.csv` | Performance comparison data |
| `results/cbd_focused_comparison/allocations.csv` | Allocation comparison |
| `results/cbd_focused_comparison/*.png` | Comparison figures |
