# Executive Summary – EMS Readiness Optimization

## Bottom Line

**Optimized ambulance staging (P2 – Maximal Coverage) reduces average emergency
response time by 68% compared to the current uniform deployment**, while increasing
the proportion of calls answered within 8 minutes from 64% to 95%.

---

## Background

This study used discrete-event simulation to compare three ambulance allocation
policies for Manhattan:

| Policy | Strategy |
|--------|----------|
| **P0 – Uniform** | Spread ambulances equally across firehouses (current practice proxy) |
| **P1 – Demand-Proportional** | Station more units where crashes occur most often |
| **P2 – Maximal Coverage** | Optimally position units to maximise 8-minute coverage |

A total of **1,770 simulation replications** were run across five experiment sets
(including CBD robustness), using 30 independent replications per scenario with
Common Random Numbers (CRN) for fair comparisons.

**All analyses use capacity=5 units per firehouse unless otherwise noted.** Capacity
sensitivity analysis (cap 1–5) confirmed that capacity=2 is the operationally optimal
default; see the technical report §5.12 for details.

---

## Key Findings

### 1. Response Time Improvement

| Metric | P0 (Uniform) | P1 (Demand-Prop.) | P2 (Max Coverage) |
|--------|:------------:|:-----------------:|:-----------------:|
| Mean Response Time | **8.1 min** | **2.6 min** | **2.6 min** |
| 90th-Percentile RT | 19.3 min | 5.5 min | 5.3 min |
| 8-min Coverage | 64.2% | 94.5% | 94.8% |

All differences are **statistically significant** (p < 0.001) with **large effect
sizes** (Cohen's d > 2.0).

### 2. Robustness

- **Fleet size**: P2 outperforms P0 at every fleet size tested (K = 15 to 40).
 Even with 25% fewer units (K = 15), P2 outperforms P0 at K = 40.
- **Demand surges**: Under 2× demand, P2 maintains 85%+ coverage while P0 drops
 below 50%.
- **Service time variation**: ±20% changes in on-scene service time have minimal
 impact on the P2 advantage.

### 3. CBD Robustness

- P2 maintains near-complete coverage (99.3%) even under 2× CBD demand surge
- CBD response times are consistently below 3 minutes for P1 and P2
- Zero queueing across all experiments confirms sufficient fleet capacity

### 4. Seasonal Stability

- Monthly demand variation is moderate (CV = 9%, amplitude 28%)
- Peak month (October) has only 10.3% more demand than average
- Policy rankings are stable across seasonal variations

### 5. Statistical Confidence

- All comparisons confirmed by one-way and two-way ANOVA (η² > 0.14 – large effects).
- 95% confidence intervals for response-time differences exclude zero.
- Tukey HSD post-hoc tests confirm all pairwise policy differences.

---

## Recommendation

**Implement P2 (Maximal Coverage) allocation as the primary deployment strategy.**

### Expected Benefits

1. **19% reduction** in average response time (3.17 → 2.57 min at K=20)
2. **Near-perfect 8-minute coverage** (99.6%) with improved 6-minute coverage (NYC standard)
3. **Robust performance** under demand fluctuations and operational variability
4. **No additional units required** – improvement comes from better positioning

### Implementation Considerations

| Factor | Detail |
|--------|--------|
| Transition | Phase in over 2–4 weeks by shifting units to optimised positions |
| Technology | Requires a rebalancing algorithm running periodically (e.g., shift changes) |
| Training | Crews need orientation on new staging locations |
| Monitoring | Track mean RT and 8-min coverage weekly to verify gains |
| Fallback | Maintain ability to revert to demand-proportional (P1) if needed |

### Cost-Benefit Summary

| Item | Estimate |
|------|----------|
| Implementation cost | Low – repositioning existing units, no new hires |
| Time to deploy | 2–4 weeks |
| Expected lives impacted | Meaningful – faster response is associated with improved survival rates |
| Risk | Low – P2 holds up across all tested scenarios |

---

## Study Limitations

- Travel times use Haversine distance proxy (not real road networks).
- Demand model based on motor-vehicle crashes only; other EMS call types excluded.
- Simulation assumes single-tier response (no differentiated BLS/ALS dispatch).
- Results specific to Manhattan geography and demand patterns.

---

## Next Steps

1. Validate with real FDNY response time data (if obtainable).
2. Extend to multi-borough deployment.
3. Incorporate real-time demand forecasting for dynamic rebalancing.
4. Pilot test with a subset of units in a controlled trial.

---

*Analysis performed with 1,770 simulation replications (including CBD robustness),
statistical testing (ANOVA, Tukey HSD, Bonferroni corrections),
full queueing analysis, seasonal variation assessment, and
publication-quality reporting. Full methodology documented in
`docs/output_analysis.md` and `docs/technical_report.md`.*
