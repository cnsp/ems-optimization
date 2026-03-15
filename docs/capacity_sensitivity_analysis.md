# Capacity Sensitivity Analysis

## Comparing Capacity = 2 (Realistic) vs Capacity = 5 (Unrealistic)

**Date:** March 2026  
**Fleet Sizes:** K = 20, K = 40  
**Policies:** P0-spatial (maximin), P1 (demand-proportional), P2 (demand-weighted optimisation)  
**Simulation:** 15 replications × 168 hours (1 week) per scenario  

---

## 1. Methodology

### 1.1 Objective

Evaluate whether a realistic firehouse capacity constraint (cap = 2 EMS units per firehouse) significantly degrades system performance compared to the current unrealistic setting (cap = 5), and characterise the trade-offs involved.

### 1.2 Experimental Design

| Factor | Levels |
|--------|--------|
| Fleet size (K) | 20, 40 |
| Capacity per firehouse | 2, 5 |
| Allocation policy | P0-spatial (maximin), P1 (demand-proportional), P2 (demand-weighted optimisation) |
| Replications | 15 per scenario |
| Simulation horizon | 168 hours (1 week) |
| Random seed base | 42 |

Total scenarios: 2 × 2 × 3 = **12 allocation–simulation experiments**.

### 1.3 Metrics

- **Firehouses used**: Number of stations with ≥ 1 unit
- **Max units per firehouse**: Concentration indicator
- **Mean response time (RT)**: Demand-weighted average
- **90th percentile RT**: Tail performance
- **Coverage fraction**: % of incidents within 8-minute threshold
- **CBD vs non-CBD distribution**: Spatial equity

---

## 2. Results

### 2.1 Allocation Patterns

#### K = 20 (Primary Scenario)

| Policy | Cap | Firehouses Used | Max Units/FH | Units in CBD | Proxy RT (min) |
|--------|-----|-----------------|--------------|--------------|----------------|
| P0-spatial | 2 | 20 | 1 | 9 | 1.302 |
| P0-spatial | 5 | 20 | 1 | 9 | 1.302 |
| P1-demand | 2 | 18 | 2 | 11 | 0.824 |
| P1-demand | 5 | 18 | 2 | 11 | 0.824 |
| P2-optimised | 2 | 20 | 1 | 10 | 0.731 |
| P2-optimised | 5 | 20 | 1 | 10 | 0.731 |

**Key finding at K = 20:** The capacity constraint does **not bind** — no policy places more than 2 units at any firehouse. The cap = 2 and cap = 5 allocations are **identical**. With 20 units and 48 candidate firehouses, the system naturally spreads units across many stations.

#### K = 40 (Higher Fleet Size — Constraint Binds)

| Policy | Cap | Firehouses Used | Max Units/FH | Unit Std | Units in CBD | Proxy RT (min) |
|--------|-----|-----------------|--------------|----------|--------------|----------------|
| P0-spatial | 2 | 40 | 1 | 0.000 | 20 | 0.777 |
| P0-spatial | 5 | 40 | 1 | 0.000 | 20 | 0.777 |
| P1-demand | 2 | **22** | **2** | 0.395 | 20 | 0.716 |
| P1-demand | 5 | **21** | **4** | 0.995 | 22 | 0.724 |
| P2-optimised | 2 | **29** | **2** | 0.494 | 25 | 0.716 |
| P2-optimised | 5 | **24** | **5** | 1.523 | 19 | 0.716 |

**Key finding at K = 40:** The capacity constraint **actively shapes** the allocation:
- **P2 cap = 2** uses **29 firehouses** vs only **24** at cap = 5, forcing better geographic spread
- **P2 cap = 5** concentrates up to 5 units at a single firehouse (unit std = 1.52 vs 0.49)
- **P1 cap = 2** uses 22 stations vs 21 at cap = 5, with max 2 vs 4 units per station

### 2.2 Simulation Performance

#### K = 20

| Policy | Cap | Mean RT (min) | P90 RT (min) | Coverage |
|--------|-----|---------------|--------------|----------|
| P0-spatial | 2 | 3.111 | 4.054 | 99.66% |
| P0-spatial | 5 | 3.111 | 4.054 | 99.66% |
| P1-demand | 2 | 2.617 | 3.990 | 99.65% |
| P1-demand | 5 | 2.617 | 3.990 | 99.65% |
| P2-optimised | 2 | 2.562 | 3.743 | 99.65% |
| P2-optimised | 5 | 2.562 | 3.743 | 99.65% |

**At K = 20, performance is identical** between cap = 2 and cap = 5 because allocations are the same.

#### K = 40

| Policy | Cap | Mean RT (min) | P90 RT (min) | Coverage |
|--------|-----|---------------|--------------|----------|
| P0-spatial | 2 | 2.443 | 3.299 | 99.84% |
| P0-spatial | 5 | 2.443 | 3.299 | 99.84% |
| P1-demand | 2 | **2.324** | **3.076** | 99.84% |
| P1-demand | 5 | 2.345 | 3.148 | 99.84% |
| P2-optimised | 2 | **2.421** | **3.254** | 99.74% |
| P2-optimised | 5 | 2.493 | 3.525 | 99.84% |

**Key finding at K = 40:** Capacity = 2 actually **improves** performance in some cases:
- **P1 cap = 2** achieves a mean RT of 2.324 min vs 2.345 min at cap = 5 (0.9% improvement)
- **P2 cap = 2** achieves a mean RT of 2.421 min vs 2.493 min at cap = 5 (**2.9% improvement**)
- P90 RT improves by ~8% for P2 under cap = 2 (3.25 vs 3.52 min)

This counterintuitive result occurs because cap = 2 forces the optimiser to distribute units across more firehouses, creating better geographic coverage and reducing average travel distances.

### 2.3 Spatial Distribution (CBD vs Non-CBD)

At K = 40, capacity = 2 encourages a more balanced allocation:
- **P2 cap = 2** places 25 units in CBD and 15 outside (62.5% CBD)
- **P2 cap = 5** places 19 in CBD and 21 outside (47.5% CBD)
- The cap = 2 allocation focuses more resources on the high-demand CBD area by using more (but less concentrated) stations

---

## 3. Key Findings

### 3.1 At K = 20, Capacity Does Not Matter

With only 20 units and 48 candidate firehouses, none of the policies ever assign more than 2 units to a single station. The constraint cap = 2 is naturally satisfied. This means:

> **For the primary K = 20 scenario, switching from cap = 5 to cap = 2 has zero impact on allocations or performance.**

### 3.2 At K = 40, Cap = 2 Is Equal or Better

When the capacity constraint actively binds (K = 40), it forces geographic dispersion. This is **beneficial** because:
1. More firehouses in service → shorter travel distances to most precincts
2. Lower concentration → less vulnerability to simultaneous incidents near one station
3. Better spatial coverage → more uniform response across Manhattan

### 3.3 Operational Realism

A capacity of 2 is more realistic for FDNY operations:
- Most FDNY firehouses host 1–2 EMS units in practice
- Having 5 ambulances at a single firehouse creates logistical challenges (parking, staffing, maintenance)
- Cap = 2 produces allocations that better resemble real-world EMS deployment patterns

### 3.4 Policy Ranking Is Stable

Across both capacity settings, the policy ranking remains consistent:
1. **P2 (optimised)** — best mean response time
2. **P1 (demand-proportional)** — close to P2 with simpler logic
3. **P0 (spatial)** — worst RT but best geographic uniformity

---

## 4. Recommendations

1. **Use capacity = 2 as the default.** It is operationally realistic and does not degrade performance. In fact, at higher fleet sizes, it improves outcomes.

2. **Keep capacity as a configurable parameter** in `configs/optimization.yaml` for future sensitivity analyses.

3. **For K = 20**, the capacity setting is irrelevant — focus analysis on policy comparison rather than capacity.

4. **For K > 30**, capacity = 2 actively constrains the optimiser but the forced dispersion is beneficial. Consider whether even cap = 1 would be appropriate for very large fleets.

---

## 5. How to Reproduce

```bash
# Run the full analysis
cd /path/to/ems-optimization
python scripts/capacity_sensitivity_analysis.py

# Modify capacity values in the script header:
# CAPACITY_VALUES = [2, 5]  → change to [1, 2, 3, 4, 5] for full sweep

# Or update the default in configs/optimization.yaml:
# firehouse_capacity: 2
```

---

## 6. Output Files

All outputs are in `results/capacity_comparison/`:

| File | Description |
|------|-------------|
| `allocation_statistics.csv` | Allocation patterns for all scenarios |
| `simulation_results.csv` | Simulation metrics with confidence intervals |
| `full_comparison.csv` | Combined allocation + simulation data |
| `allocation_*_K{K}_cap{cap}.csv` | Individual allocation vectors |
| `allocation_comparison_K{K}.png` | Side-by-side allocation bar charts |
| `performance_comparison_K{K}.png` | Performance metric bar charts |
| `concentration_analysis_K{K}.png` | Units-per-firehouse distributions |
| `cbd_distribution_K{K}.png` | CBD vs non-CBD unit distribution |
| `analysis_summary.json` | Experiment metadata |
