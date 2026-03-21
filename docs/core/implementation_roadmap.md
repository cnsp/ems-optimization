---
status: ✅ CURRENT
last_updated: "2026-03-20"
verified: "All metrics, code references, and nomenclature are current as of March 2026"
---
# Implementation Roadmap
## EMS Readiness Optimization — Manhattan Deployment Plan

**Version:** 1.0 | **Date:** March 12, 2026 | **Status:** Proposed

---

## Overview

This roadmap describes the phased deployment of the demand-weighted optimized ambulance allocation policy (P2) across Manhattan's 48 FDNY firehouses. The plan is designed to be low-risk, evidence-based, and incrementally validated.

**Capacity assumption:** All deployment scenarios use capacity=2 units per firehouse (the operationally optimal default established by capacity sensitivity analysis). This means no single firehouse stages more than 2 ambulances. See `docs/analysis/capacity_sensitivity_analysis.md` for supporting evidence.

---

## Phase 1: Pilot Deployment (Months 1–3)

### Objective
Validate P2 allocation at 5 high-impact firehouses and confirm simulation predictions with real-world data.

### Scope
- **Firehouses**: 5 highest-impact locations (selected based on P2 allocation recommendations for precincts with highest demand)
- **Units**: 5–8 ambulances repositioned according to P2 staging plan
- **Duration**: 90 days

### Activities
| Week | Activity | Owner |
|------|----------|-------|
| 1–2 | Briefing for pilot firehouse captains and dispatch supervisors | Operations |
| 1–2 | Install KPI monitoring dashboard (mean RT, 6-min coverage (NYC law), 8-min coverage (NFPA standard), utilization) | IT/Analytics |
| 3 | Begin P2 staging at pilot firehouses | Operations |
| 3–12 | Continuous monitoring and weekly performance reviews | Analytics |
| 8 | Mid-pilot assessment and adjustment | Leadership |
| 12 | Pilot completion report with go/no-go for Phase 2 | Research Team |

### Success Criteria
- ≥15% improvement in mean response time in pilot precincts
- ≥10 percentage point improvement in 8-min coverage (NFPA standard) in pilot area
- ≥5 percentage point improvement in 6-min coverage (NYC law) in pilot area
- No degradation in non-pilot area response times >5%
- Positive feedback from dispatch supervisors and crews

### Resources Required
- 0 additional ambulances (repositioning only)
- 1 analytics dashboard (estimated 2 weeks development)
- Training: 2-hour briefing per pilot firehouse
- Monitoring: 4 hours/week analytics staff time

### Risk Mitigation
| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Crew resistance to new staging | Medium | Medium | Early engagement, explain rationale with data |
| Unexpected demand pattern shift | Low | Medium | Weekly monitoring, pre-defined rollback criteria |
| Adjacent area performance degradation | Low | High | Monitor non-pilot areas; rollback if >5% degradation |

---

## Phase 2: Gradual Rollout (Months 3–6)

### Objective
Expand P2 allocation to 15–20 firehouses based on pilot learnings, and calibrate the model with real dispatch data.

### Scope
- **Firehouses**: 15–20 (pilot 5 + 10–15 additional)
- **Units**: 12–16 ambulances under P2 staging
- **Duration**: 90 days

### Activities
| Month | Activity | Owner |
|-------|----------|-------|
| 3 | Analyze pilot results; calibrate travel time model with real data | Research |
| 3 | Select Phase 2 firehouses based on expected impact | Research + Ops |
| 4 | Training sessions for Phase 2 firehouse crews | Operations |
| 4–6 | Staged rollout (5 new firehouses per 2 weeks) | Operations |
| 4–6 | Continuous monitoring with expanded dashboard | Analytics |
| 5 | Integrate road-network travel times (OSRM) | IT/Research |
| 6 | Phase 2 completion report | Research Team |

### Model Calibration
- Compare predicted vs actual response times from pilot data
- Adjust speed parameters based on real dispatch records
- Re-optimize P2 allocation if significant calibration changes

### Success Criteria
- Consistent ≥30% improvement in mean RT across expanded area
- ≥90% 8-min coverage (NFPA standard) across P2-served precincts
- ≥85% 6-min coverage (NYC law) across P2-served precincts
- Model predictions within ±15% of observed response times
- No reported operational issues from dispatch

---

## Phase 3: Full Deployment (Months 6–12)

### Objective
Deploy P2 allocation across all 48 Manhattan firehouses with shift-specific optimization.

### Scope
- **Firehouses**: All 48 Manhattan firehouses
- **Units**: Full fleet under P2 staging
- **Duration**: 6 months (ongoing operations thereafter)

### Activities
| Month | Activity | Owner |
|-------|----------|-------|
| 6–7 | Complete rollout to remaining firehouses | Operations |
| 7–8 | Develop shift-specific allocations (day/evening/overnight) | Research |
| 8–9 | Implement time-of-day P2 variants | Operations |
| 9–10 | Final model validation with 6 months of operational data | Research |
| 10–12 | Documentation and handoff to operations team | Research |
| 12 | Final deployment report and future recommendations | Research |

### Advanced Features
1. **Shift-specific staging**: Different P2 allocations for day (8AM–4PM), evening (4PM–12AM), and overnight (12AM–8AM) shifts
2. **Weekly adjustment**: Incorporate day-of-week demand patterns
3. **Seasonal calibration**: Quarterly model re-calibration

---

## Timeline Summary

```
Month: 1 2 3 4 5 6 7 8 9 10 11 12
 |----Phase 1 (Pilot)----|
 |------Phase 2 (Expansion)------|
 |------Phase 3 (Full)------|
 [Monitoring Dashboard Development]
 [Road Network Integration]
 [Shift-Specific Optimization]
 [Handoff & Documentation]
```

---

## Resource Requirements

### Personnel
| Role | FTE | Duration | Notes |
|------|-----|----------|-------|
| Data Analyst | 0.5 | 12 months | Dashboard, monitoring, calibration |
| Operations Coordinator | 0.25 | 12 months | Firehouse liaison, training |
| Research Lead | 0.25 | 12 months | Model calibration, optimization updates |
| IT Support | 0.1 | 3 months | Dashboard deployment |

### Technology
| Component | Cost Estimate | Timeline |
|-----------|--------------|----------|
| KPI Dashboard (web-based) | $15–25K development | Month 1–2 |
| OSRM routing server (optional) | $5K/year hosting | Month 4–5 |
| Data pipeline (CAD integration) | $10–20K development | Month 6–8 |

### Training
- Phase 1: 5 briefings × 2 hours = 10 hours
- Phase 2: 15 briefings × 1.5 hours = 22.5 hours
- Phase 3: 28 briefings × 1 hour = 28 hours
- Materials: Staging maps, quick-reference cards, FAQ documents

---

## Success Metrics and Monitoring

### Key Performance Indicators

Simulation baselines below are from the current P0 (spatially-stratified) at K=20. Operational deployment targets use P2 with capacity=2 units per firehouse (the recommended default from capacity sensitivity analysis).

| KPI | Baseline (P0, cap=2) | Target (P2, cap=2) | Measurement |
|-----|---------------------|-------------------|-------------|
| Mean Response Time | 3.17 min | < 3.0 min | Daily from CAD |
| 8-min Coverage (NFPA standard) | 99.6% | > 99% | Weekly calculation |
| 6-min Coverage (NYC law) | ~93.7% | > 95% | Weekly calculation |
| P90 (90th %ile) Response Time | 5.32 min | < 5 min | Weekly calculation |
| Utilization | 7.6% | 7–10% | Weekly calculation |
| Crew satisfaction | N/A | > 80% positive | Quarterly survey |

### Monitoring Cadence
- **Daily**: Mean RT, 6-min coverage (NYC law), and 8-min coverage (NFPA standard)
- **Weekly**: Full KPI dashboard review; anomaly detection
- **Monthly**: Trend analysis and model performance assessment
- **Quarterly**: Full review with leadership; model recalibration

### Rollback Criteria
- If mean RT increases by >20% in any precinct for >2 consecutive weeks
- If 8-min coverage (NFPA standard) drops below 50% in any precinct
- If dispatch supervisors report critical operational issues
- Rollback procedure: Revert to P0 staging at affected firehouses within 24 hours

---

## Technology Integration Needs

### Phase 1 (Dashboard Only)
- Web-based dashboard displaying real-time KPIs
- Data source: Manual extraction from CAD system
- Hosting: Internal server or cloud (Heroku/AWS)

### Phase 2 (Routing Integration)
- OSRM or similar open-source routing engine
- Real road-network travel time calculations
- Replaces Haversine-based proxy for improved accuracy

### Phase 3 (CAD Integration)
- Automated data feed from Computer-Aided Dispatch
- Real-time unit location tracking
- Automated P2 allocation recommendations at shift change
- Future: Dynamic repositioning suggestions

---

## Risk Register

| ID | Risk | Probability | Impact | Mitigation | Owner |
|----|------|------------|--------|------------|-------|
| R1 | Crew resistance | Medium | Medium | Early communication, data-driven rationale | Operations |
| R2 | Model prediction error | Low | Medium | Calibration with real data; gradual rollout | Research |
| R3 | Adjacent area degradation | Low | High | Monitor all precincts; rollback trigger | Analytics |
| R4 | Demand pattern change | Low | Low | Quarterly recalibration; adaptive model | Research |
| R5 | Technology delays | Medium | Low | Phase 1 requires no technology; decouple | IT |
| R6 | Leadership change | Low | Medium | Document rationale; institutional knowledge | Research |

---

## Budget Summary

| Category | Phase 1 | Phase 2 | Phase 3 | Total |
|----------|---------|---------|---------|-------|
| Personnel | $25K | $25K | $50K | $100K |
| Technology | $20K | $10K | $15K | $45K |
| Training | $2K | $3K | $5K | $10K |
| Contingency (15%) | $7K | $6K | $10.5K | $23.5K |
| **Total** | **$54K** | **$44K** | **$80.5K** | **$178.5K** |

*Note: Costs are estimates. No new ambulances are required — the investment is in analytics, training, and monitoring.*

---

## Expected Return on Investment

- **Annual time saved**: ~167,750 minutes (2,796 ambulance-hours)
- **Equivalent fleet expansion**: 3× effective capacity
- **If fleet could be reduced by even 2 units**: $200K+/year savings in operating costs
- **Payback period**: < 12 months based on conservative efficiency gains

---

*Prepared by the EMS Optimization Research Team. For questions, contact the project lead or refer to the full technical report (docs/core/technical_report.md).*
