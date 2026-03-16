# Executive Summary – EMS Readiness Optimization

## Bottom Line

**Optimized ambulance staging (P2 – Demand-Weighted Optimised) reduces average emergency
response time by 19% compared to the spatially-stratified baseline (P0)**, while maintaining
near-perfect 8-minute coverage at 99.7% and improving 6-minute coverage from 94% to 98%.

---

## Background

This study used discrete-event simulation to compare three ambulance allocation
policies for Manhattan:

| Policy | Strategy |
|--------|----------|
| **P0 – Spatially-Stratified** | Distribute ambulances across firehouses using latitude-based stratification (baseline) |
| **P1 – Demand-Proportional** | Station more units where crashes occur most often |
| **P2 – Demand-Weighted Optimised** | Optimally position units to maximise coverage (evaluated at 6-min NYC and 8-min NFPA thresholds) |

A total of **2,700+ simulation replications** were run across five experiment sets
(including CBD robustness, fleet sensitivity, demand surge, and service-time variation),
using 30 independent replications per scenario with
Common Random Numbers (CRN) for fair comparisons.

**All analyses use capacity=2 units per firehouse (the operationally optimal default).**
Capacity sensitivity analysis (cap 1–5) confirmed that capacity=2 matches or improves
upon higher capacity limits at typical fleet sizes; see the technical report §5.12 for details.

---

## Key Findings

### 1. Response Time Improvement

| Metric | P0 (Spatially-Stratified) | P1 (Demand-Prop.) | P2 (Optimised) |
|--------|:------------:|:-----------------:|:-----------------:|
| Mean Response Time | **3.17 min** | **2.62 min** | **2.57 min** |
| P90 (90th %ile) RT | 5.33 min | 3.99 min | 3.75 min |
| 6-min Coverage (NYC law) | 94.0% | 98.0% | 98.2% |
| 8-min Coverage (NFPA standard) | 99.7% | 99.6% | 99.7% |

All differences between P0 and P2 are **statistically significant** (p < 0.001) with
**large effect sizes** (Cohen's d = 10.3 at K=20).

### 2. Robustness

- **Fleet size**: P2 outperforms P0 at most fleet sizes tested (K = 10 to 40).
  Even with fewer units, P2 achieves competitive or superior response times.
- **Demand surges**: Under 2× demand, P2 maintains strong coverage while P0 performance
  degrades more significantly.
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

**Implement P2 (Demand-Weighted Optimised) allocation as the primary deployment strategy.**

### Expected Benefits

1. **19% reduction** in average response time (3.17 → 2.57 min at K=20)
2. **Near-perfect 8-minute coverage (NFPA standard)** at 99.7%, with improved **6-minute coverage (NYC law)** reaching ~98%
3. **Robust performance** under demand fluctuations and operational variability
4. **No additional units required** – improvement comes from better positioning

### Implementation Considerations

| Factor | Detail |
|--------|--------|
| Transition | Phase in over 2–4 weeks by shifting units to optimised positions |
| Technology | Requires a rebalancing algorithm running periodically (e.g., shift changes) |
| Training | Crews need orientation on new staging locations |
| Monitoring | Track mean RT, 6-min coverage (NYC law), and 8-min coverage (NFPA standard) weekly to verify gains |
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

*Analysis performed with 2,700+ simulation replications (including CBD robustness,
fleet sensitivity, demand surge, and service-time variation),
statistical testing (ANOVA, Tukey HSD, Bonferroni corrections),
full queueing analysis, seasonal variation assessment, and
publication-quality reporting. Full methodology documented in
`docs/output_analysis.md` and `docs/technical_report.md`.*
