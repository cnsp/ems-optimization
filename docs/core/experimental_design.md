---
status: ✅ CURRENT
last_updated: "2026-03-20"
verified: "All metrics, code references, and nomenclature are current as of March 2026"
---
# Experimental Design – EMS Readiness Simulation Study

## 1. Research Questions and Hypotheses

### Primary Research Questions

| ID | Research Question |
|----|-------------------|
| RQ1 | How do the three allocation policies (P0: Spatially-Stratified Uniform, P1: Demand-Proportional, P2: Demand-Weighted Optimized) compare in terms of mean response time, P90 (90th percentile) response time, 6-minute coverage (NYC law), and 8-minute coverage (NFPA standard)? |
| RQ2 | How sensitive is each policy's performance to fleet size (K)? |
| RQ3 | How robust is each policy to changes in demand intensity? |
| RQ4 | How do service time variations affect policy performance? |

### Hypotheses

| ID | Hypothesis | Rationale |
|----|-----------|-----------|
| H1 | P2 achieves lower mean response time than P1, which outperforms P0 | Optimization-based allocation better matches supply to demand |
| H2 | P2's advantage over P0 diminishes as K increases | With excess capacity, allocation quality matters less |
| H3 | All policies degrade under high demand, but P0 degrades fastest | Spatially-stratified uniform allocation wastes units in low-demand areas |
| H4 | P2 is more robust to service time variation than P0 | Optimized placement compensates for longer on-scene times |

---

## 2. Experimental Factors and Levels

### Factor Summary

| Factor | Symbol | Levels | Values |
|--------|--------|--------|--------|
| Allocation Policy | π | 3 | P0 (Spatially-Stratified Uniform), P1 (Demand-Proportional), P2 (Demand-Weighted) |
| Fleet Size | K | 6 | 15, 20, 25, 30, 35, 40 *(Exp2 subset; full canonical design: K = 10–48)* |
| Demand Multiplier | δ | 6 | 0.5, 0.75, 1.0, 1.25, 1.5, 2.0 |
| Service Time Mean | μ_s | 3 | 20 min (−20%), 25 min (baseline), 30 min (+20%) |

### Capacity Constraint

The **firehouse capacity** parameter (C) defines the maximum number of EMS units that can be staged at any single firehouse. The operational default is **C = 2 units per firehouse**, established by the Capacity Sensitivity experiment (see `docs/analysis/capacity_sensitivity_analysis.md`).

At fleet sizes K ≤ 30, the capacity constraint does not bind—results are identical whether C = 2 or C = 5. This was confirmed by the full-spectrum capacity sensitivity analysis testing cap = 1 through 5.

> **Historical note:** The experiments in Section 4 below (Exp1–Exp4) were originally designed with C = 5. All production results reported in the technical report (§5) use C = 2, which produces numerically identical outcomes at the fleet sizes tested. See the technical report §4.5.1 for the consolidated experimental design table.

### Factor Details

#### Allocation Policies
- **P0 (Spatially-Stratified Uniform)**: Latitude-based spatial selection of K evenly-spaced firehouses, providing even geographic coverage (see `spatially_stratified_allocation` in `src/ems_readiness/optimization/policies.py`)
- **P1 (Demand-Proportional)**: Units proportional to nearest-firehouse demand credit
- **P2 (Demand-Weighted Optimized)**: MIP minimizing expected demand-weighted response time

#### Fleet Size (K)
Pre-computed allocations at K ∈ {20, 30, 40, 48}. For intermediate values (15, 25, 35), allocations are generated dynamically using the optimization and baseline policy functions.

#### Demand Scaling
Applied by multiplying the NHPP base arrival rate (3.48 crashes/hour) by δ. All temporal patterns (hourly, day-of-week) and spatial patterns (precinct probabilities) remain unchanged.

#### Service Time Scenarios
The baseline lognormal service time (μ = 25 min, σ = 10 min) is varied by adjusting the mean:
- Low: μ = 20 min (−20%)
- Baseline: μ = 25 min
- High: μ = 30 min (+20%)

Standard deviation is held proportional (σ/μ ratio constant).

---

## 3. Response Variables

| Metric | Symbol | Description |
|--------|--------|-------------|
| Mean Response Time | E[RT] | Average time from incident arrival to unit arrival on scene |
| P90 (90th %ile) RT | RT_90 | 90th percentile response time — exceeded by only 10% of incidents |
| 95th Percentile RT | RT_95 | Response time exceeded by only 5% of incidents |
| 8-min Coverage | C_8 | Fraction of incidents with response time ≤ 8 min |
| 10-min Coverage | C_10 | Fraction of incidents with response time ≤ 10 min |
| Mean Utilization | ρ̄ | Average unit utilization across fleet |
| Max Utilization | ρ_max | Maximum single-unit utilization |
| Mean Queue Length | L̄ | Time-weighted average queue length |
| Max Queue Length | L_max | Peak queue length observed |
| Queue Fraction | Q_frac | Fraction of incidents that waited in queue |
| Total Incidents | N | Total incidents generated |
| Incidents Queued | N_q | Number of incidents that entered queue |

---

## 4. Experiment Sets

### Experiment 1: Baseline Policy Comparison
- **Objective**: Compare P0, P1, P2 at baseline conditions
- **Factors**: π ∈ {P0, P1, P2}, K = 20, δ = 1.0, μ_s = 25, **C = 5**
- **Runs**: 3 policies × 30 replications = **90 runs**
- **Output**: `results/analysis/simulation/production/exp1_policy_comparison.csv`

### Experiment 2: Fleet Size Sensitivity
- **Objective**: Evaluate performance across fleet sizes
- **Factors**: π ∈ {P0, P1, P2}, K ∈ {15, 20, 25, 30, 35, 40} *(Exp2 subset; full production design: K = 10–48)*, δ = 1.0, μ_s = 25, **C = 5**
- **Runs**: 3 × 6 × 30 = **540 runs**
- **Output**: `results/analysis/simulation/production/exp2_fleet_sensitivity.csv`

### Experiment 3: Demand Scaling Sensitivity
- **Objective**: Assess robustness to demand changes
- **Factors**: π ∈ {P0, P1, P2}, K = 20, δ ∈ {0.5, 0.75, 1.0, 1.25, 1.5, 2.0}, μ_s = 25, **C = 5**
- **Runs**: 3 × 6 × 30 = **540 runs**
- **Output**: `results/analysis/simulation/production/exp3_demand_sensitivity.csv`

### Experiment 4: Service Time Robustness
- **Objective**: Test sensitivity to on-scene service duration
- **Factors**: π ∈ {P0, P1, P2}, K = 20, δ = 1.0, μ_s ∈ {20, 25, 30}, **C = 5**
- **Runs**: 3 × 3 × 30 = **270 runs**
- **Output**: `results/analysis/simulation/production/exp4_service_robustness.csv`

### Total Experimental Runs (Exp 1–4)
| Experiment | Runs |
|-----------|------|
| Exp 1: Policy Comparison | 90 |
| Exp 2: Fleet Sensitivity | 540 |
| Exp 3: Demand Sensitivity | 540 |
| Exp 4: Service Robustness | 270 |
| **Subtotal (Exp 1–4)** | **1,440** |

> **Note:** The full production design (documented in `docs/core/technical_report.md` §4.5.1) expands to **2,760 total runs** across five experiment sets by adding CBD Robustness (330 runs) and Capacity Sensitivity (450 runs, cap 1–5). The Policy & Fleet Analysis experiment uses the full canonical K range (10, 15, 20, 25, 30, 35, 40, 45, 48), totalling 810 runs. Exp 2 above documents the original 6-level K subset. All production results use **capacity=2**.
>
> **Run-count reconciliation:** The five table-level components in §4.5.1 (810 + 540 + 270 + 330 + 450) sum to 2,400, not 2,760. The 2,760 figure counts **all individual replication rows** across every output file. The 360-run difference arises because (a) the production pipeline stored its own experiment files (`exp1`–`exp4`) separately from the baseline sweep (`all_results_raw.csv`, 810 rows), adding 1,620 production rows (90 + 720 + 540 + 270), and (b) Exp 2's actual output includes 180 `P0_legacy` (uniform allocation) runs for backward-compatibility comparison, expanding it from 540 to 720. The Capacity Sensitivity experiment (450 runs) was executed but stored in aggregated form only (54 summary rows); its per-replication rows are not part of the 2,760 tally. See `technical_report.md` §4.5.1 for the full reconciliation table. A "run" = one 168-hour simulation replication for a single policy–parameter combination.

---

## 5. Replication Strategy

### Common Random Numbers (CRN)
To reduce variance across policy comparisons, all policies within the same experiment/scenario share the same random number seeds per replication:
- Replication `i` uses seed `seed_base + i` where `seed_base = 42`
- Seeds: 42, 43, 44, ..., 71 (for 30 replications)
- This ensures the same incident arrival pattern for all policies at the same replication number

### Replication Count Justification
- **30 replications** per scenario provides approximately ±5% half-width for 95% confidence intervals on mean response time
- Validated in Phase 4 pilot runs showing stable CI widths

### Simulation Horizon
- **168 hours** (1 week) per replication
- No warm-up period (terminating simulation)
- Captures full weekly demand cycle (hourly + day-of-week patterns)

---

## 6. Output Data Structure

Each experiment CSV contains one row per replication with columns:

```
experiment_id - Experiment identifier (exp1, exp2, exp3, exp4)
scenario_id - Unique scenario label
replication - Replication number (0-29)
policy - Policy name (P0, P1, P2)
K - Fleet size
demand_multiplier - Demand scaling factor
service_time_mean - Service time mean (minutes)
mean_response_time - Mean response time (minutes)
p90_response_time - P90 (90th percentile) response time (minutes)
coverage_6min - fraction of calls with response time ≤ 6 minutes (NYC law)
p95_response_time - 95th percentile response time (minutes)
coverage_8min - Fraction with RT ≤ 8 min
coverage_10min - Fraction with RT ≤ 10 min
mean_utilization - Mean fleet utilization
max_utilization - Maximum unit utilization
mean_queue_length - Time-weighted average queue length
max_queue_length - Peak queue length
queue_fraction - Fraction of incidents queued
total_incidents - Total incidents in replication
incidents_queued - Number queued
random_seed - Random seed used
```

---

## 7. Analysis Plan

### Statistical Methods
1. **Paired t-tests** (using CRN) for pairwise policy comparison
2. **ANOVA** for multi-factor analysis across fleet sizes
3. **95% confidence intervals** for all point estimates
4. **Effect size** (Cohen's d) for practical significance

### Visualizations
1. Box plots: response time distributions by policy
2. Line plots: performance metrics vs. fleet size (sensitivity curves)
3. Heatmaps: policy × demand multiplier performance
4. Confidence interval plots for key comparisons

---

---

## 8. Cross-References

- **Full experimental design table** (all 5 experiment sets, 2,760 runs): `docs/core/technical_report.md` §4.5.1
- **Output analysis methodology**: `docs/core/output_analysis.md`
- **CBD robustness analysis**: `docs/analysis/cbd_analysis.md`
- **Capacity sensitivity analysis**: `docs/analysis/capacity_sensitivity_analysis.md`

---

*Document created: Phase 5 – Experimental Design*
*Last updated: 2026-03-22*
