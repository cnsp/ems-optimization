# EMS Readiness Optimization for Manhattan
## Executive Presentation

---

## Slide 1: Title

### Optimizing Ambulance Staging in Manhattan
**A Simulation-Based Approach to Reducing EMS Response Times**

- EMS Optimization Research Team
- March 2026
- Prepared for FDNY Operations Leadership

---

## Slide 2: The Problem

### Current EMS Response Performance is Unacceptable

**The current uniform allocation policy (P0):**
- Distributes ambulances **equally** across 48 firehouses
- **Ignores** where crashes actually happen
- Results in **8.08-minute average response time**
- Only **64.4%** of calls get response within 8 minutes

**Why this matters:**
- Manhattan has ~3.48 MVC calls per hour (30,500+ per year)
- Midtown generates 3–5× more calls than Upper Manhattan
- Every minute of delay increases mortality risk for critical patients

> "The difference between a 2-minute and 8-minute response can be the difference between life and death."

---

## Slide 3: Current State — P0 Performance

### Uniform Allocation: Equal ≠ Equitable

| Metric | P0 Value | Target |
|--------|----------|--------|
| Mean Response Time | **8.08 min** | < 4 min |
| P90 Response Time | **19.47 min** | < 8 min |
| 8-min Coverage | **64.4%** | > 95% |
| Utilization | 9.1% | — |

**Root Cause:** Spatial mismatch between where ambulances are staged and where crashes occur.

- Midtown precincts (highest demand) are underserved
- Upper Manhattan precincts (lowest demand) have excess capacity
- The system is not capacity-constrained—it's *location-constrained*

---

## Slide 4: Our Solution — Optimized Allocation (P2)

### Smart Staging: Put Ambulances Where They're Needed

**Approach:**
1. Analyzed **2.24 million** historical crash records
2. Built a demand model capturing hourly and geographic patterns
3. Used **mathematical optimization** to find the best allocation
4. Validated with **1,440 simulation runs**

**P2 Allocation Strategy:**
- Concentrates units in **high-demand areas** (Midtown, Lower Manhattan)
- Maintains **minimum coverage** in low-demand areas
- Uses the **same 20 ambulances** — just staged differently
- Implementable as a **simple shift-change staging plan**

---

## Slide 5: Key Results — Head-to-Head Comparison

### P2 Sharply Improves Performance

| Metric | P0 (Current) | P2 (Optimized) | Improvement |
|--------|-------------|-----------------|-------------|
| Mean Response Time | 8.08 min | **2.57 min** | **↓ 68%** |
| P90 Response Time | 19.47 min | **3.76 min** | **↓ 81%** |
| 8-min Coverage | 64.4% | **99.6%** | **↑ 35 pp** |
| Fleet Used | 20 units | 20 units | **Same fleet** |

**Statistical confidence:**
- All improvements significant at p < 0.001
- Effect sizes are "Large" (Cohen's d > 28)
- Based on 30 independent simulation replications
- 95% CI for mean RT improvement: [5.41, 5.61] minutes

---

## Slide 6: Performance Improvements Visualized

### Response Time Distribution Shift

**P0 Distribution:** Wide spread, 8.08 min mean, long tail to 21+ min
**P2 Distribution:** Tight cluster around 2.57 min, 99.6% under 8 min

### Key Visual Insights (see results/figures/):
- `pub_fig1_policy_comparison.png` — Side-by-side policy comparison
- `pub_fig2_fleet_sensitivity.png` — How fleet size affects each policy
- `pub_fig5_performance_heatmap.png` — Performance across all scenarios

**The bottom line:** P2 doesn't just shift the average — it nearly eliminates the long waits that matter most.

---

## Slide 7: Robustness Analysis

### P2 Wins Under Every Condition We Tested

**Fleet Size Sensitivity (K = 15 to 40):**
- P2 achieves >99% coverage with just K=25 units
- P0 requires K=40 to reach 99% coverage
- **P2 with 15 units outperforms P0 with 40 units**

**Demand Variation (0.5× to 2.0×):**
- P2 mean RT ranges 2.44–2.85 min (stable)
- P0 mean RT ranges 7.80–8.58 min (degrades)
- Policy rankings unchanged across all demand levels

**Service Time Sensitivity (20–30 min mean):**
- No impact on policy rankings
- Response time unaffected by service time variations
- Results hold under all operational assumptions tested

---

## Slide 8: Implementation Roadmap

### Three-Phase Deployment Plan

**Phase 1 — Pilot (Months 1–3)**
- Deploy P2 at **5 highest-impact firehouses** (Midtown)
- Monitor mean RT, 8-min coverage, and utilization daily
- Success criterion: ≥15% improvement in pilot area response times

**Phase 2 — Expansion (Months 3–6)**
- Expand to **15–20 firehouses** based on pilot results
- Calibrate model with real dispatch data
- Begin road-network travel time integration

**Phase 3 — Full Deployment (Months 6–12)**
- Roll out to **all 48 Manhattan firehouses**
- Implement shift-specific allocations
- Establish continuous optimization cycle

**Requirements:** No new equipment, no new technology. Just repositioning existing ambulances.

---

## Slide 9: Expected Benefits

### Annual Impact Estimate (K=20 units)

| Benefit | Value |
|---------|-------|
| Calls per year affected | **~30,500** MVC calls |
| Mean RT reduction per call | **5.5 minutes** |
| Total annual time saved | **167,750 minutes** (2,796 hours) |
| Additional calls within 8-min target | **~10,700** per year |
| Effective fleet multiplier | **3×** (20 units → equivalent of 60) |

### What this means in practice:
- Faster defibrillation and trauma response
- Quicker stroke and cardiac care
- Better coverage in currently underserved areas
- Same performance with fewer units, or better performance with the current fleet

---

## Slide 10: Recommendations and Next Steps

### Immediate Recommendations

1. ✅ **Approve P2 adoption** as the standard ambulance staging policy for Manhattan
2. ✅ **Launch pilot** at Midtown firehouses within 30 days
3. ✅ **Establish monitoring** dashboard with real-time KPI tracking
4. ✅ **Brief dispatch leadership** on new staging locations

### Future Opportunities
- **Dynamic repositioning**: Adjust staging in real-time based on current unit positions
- **Multi-borough expansion**: Extend optimization to Brooklyn, Queens, Bronx, Staten Island
- **All-incident integration**: Include medical emergencies, fires, and hazmat calls
- **CAD integration**: Embed optimization recommendations in dispatch software

### Questions?

**Contact:** EMS Optimization Research Team 
**Repository:** github.com/cnsp/ems-optimization 
**Full Technical Report:** docs/technical_report.md

---

*This analysis is based on 1,440 simulation experiments, 2.24 million historical crash records, and rigorous statistical validation. All results can be reproduced from the project repository.*
