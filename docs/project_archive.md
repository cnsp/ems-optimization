---
status: 📋 REFERENCE
last_updated: "2026-03-20"
verified: "Specialized analysis document. Cross-reference with current production results."
---
# Project Archive
## EMS Readiness Optimization — Complete Project Timeline & Record

**Project Duration:** February 2026 — March 2026 
**Version:** 1.0.0 
**Status:** Complete

---

## Project Timeline

### Phase 1: Data Processing & Exploratory Data Analysis
**Duration:** Week 1 
**Deliverables:**
- Raw data acquisition from NYC Open Data (2.24M crash records, 219 firehouses, 78 precincts)
- Data cleaning pipeline (`scripts/data_audit.py`, `audit_step1-4`)
- Spatial filtering: 628,811 Manhattan crashes, 48 firehouses, 30 precincts
- EDA notebook (`notebooks/02_eda_spatiotemporal.ipynb`)
- 10 EDA figures (crash heatmap, temporal trends, precinct density, etc.)
- Source manifest and data dictionaries

**Key Decisions:**
- DEC-001: Manhattan as primary study area, CBD for robustness
- DEC-002: FDNY firehouses as candidate staging locations
- DEC-005: Use all available crash data for demand estimation

### Phase 2: Demand & Service Modeling
**Duration:** Week 2 
**Deliverables:**
- NHPP demand model (λ₀ = 3.48/hr, hourly + DOW factors)
- Lambda tables: `demand_lambda_hourly.csv`, `demand_lambda_dow.csv`, `demand_lambda_precinct.csv`
- Travel time proxy (Haversine/20mph with TOD factors)
- Service time distribution (LogNormal, μ=25min, σ=10min)
- Distance matrix (48×30 firehouses × precincts)
- Model specification documents
- Demo notebook (`notebooks/03_input_modeling.ipynb`, `04_service_travel_proxy.ipynb`)

**Key Decisions:**
- DEC-003: Discrete-Event Simulation using SimPy
- LogNormal over Exponential for service times
- 20 mph average speed for urban EMS

### Phase 3: Optimization Models
**Duration:** Week 3 
**Deliverables:**
- Three MIP formulations: Demand-Weighted, P-Median, Maximal Coverage
- Baseline policies: Uniform (P0), Demand-Proportional (P1)
- EMSAllocator class for end-to-end optimization
- Allocations for K=20,30,40,48 scenarios
- Policy comparison table and sensitivity analysis
- Optimization notebook (`notebooks/05_optimization.ipynb`)

**Key Decisions:**
- DEC-004: Linear Programming using PuLP
- CBC solver with 300s time limit
- Capacity limit of 5 units per firehouse
- 8-minute coverage threshold

### Phase 4: Discrete-Event Simulation with V&V
**Duration:** Week 4 
**Deliverables:**
- SimPy DES engine (7 modules: engine, entities, resources, dispatcher, metrics, runner)
- NearestAvailableDispatcher with TOD-adjusted travel times
- BatchRunner with CRN support
- 4 verification tests (toy example, zero demand, single unit, extreme demand)
- 3 validation pilots (P0 vs P2, fleet sensitivity, demand sensitivity)
- 39 unit tests across 4 test modules
- Verification log and conceptual model documents

**Key Decisions:**
- Nearest-available dispatch policy
- 24-hour warm-up period
- 168-hour (1-week) simulation duration
- Common Random Numbers for variance reduction

### Phase 5: Experimental Design & Production Runs
**Duration:** Week 5 
**Deliverables:**
- Factorial experimental design (4 experiments, 1,440 total runs)
- Exp1: 3 policies × 30 reps = 90 runs
- Exp2: 3 policies × 6 K levels × 30 reps = 540 runs
- Exp3: 3 policies × 6 demand levels × 30 reps = 540 runs
- Exp4: 3 policies × 3 service levels × 30 reps = 270 runs
- Production result CSVs and experiment logs
- Production results notebook (`notebooks/07_production_results.ipynb`)

**Key Decisions:**
- 30 replications per cell (sufficient for CLT)
- K range: 15–40 units
- Demand multiplier range: 0.5×–2.0×
- Service time range: 20–30 min mean

### Phase 6: Full Statistical Analysis
**Duration:** Week 6 
**Deliverables:**
- Descriptive statistics for all experiments
- One-way and two-way ANOVA
- Tukey HSD post-hoc comparisons with Bonferroni correction
- Cohen's d effect sizes
- 95% confidence intervals
- 5 publication-quality figures
- 4 LaTeX-formatted tables
- Statistical analysis notebook (`notebooks/08_statistical_analysis.ipynb`)
- Output analysis report

### Phase 7: Final Report & Documentation
**Duration:** Week 7 
**Deliverables:**
- Full technical report
- Executive presentation (10 slides)
- Implementation roadmap (3-phase deployment plan)
- Enhanced README with full project documentation
- Code documentation and architecture guide
- Project archive (this document)
- File inventory
- Summary dashboard visualization
- Final git repository with all deliverables

---

## Key Decisions Summary

| ID | Decision | Rationale | Date |
|----|----------|-----------|------|
| DEC-001 | Manhattan study area | Highest density, most data | Week 1 |
| DEC-002 | FDNY firehouses as candidates | Existing infrastructure | Week 1 |
| DEC-003 | SimPy for DES | Mature, process-based, Python | Week 2 |
| DEC-004 | PuLP for optimization | Free, CBC solver, Python | Week 3 |
| DEC-005 | All historical crash data | Maximum statistical power | Week 1 |
| DEC-006 | LogNormal service times | Better empirical fit than Exponential | Week 2 |
| DEC-007 | 20 mph average EMS speed | Literature-supported urban speed | Week 2 |
| DEC-008 | 8-minute coverage threshold | NFPA Standard 1710 | Week 3 |
| DEC-009 | 30 replications per cell | Sufficient for CLT, manageable compute | Week 5 |
| DEC-010 | CRN for variance reduction | Enables precise pairwise comparisons | Week 4 |

---

## Lessons Learned

1. **Spatial mismatch dominates**: The largest source of response time inefficiency is spatial mismatch (where ambulances are vs where calls are), not fleet size. Optimization of location has 3× the impact of fleet expansion.

2. **Simple models can be powerful**: Haversine distance with a calibrated speed factor provides sufficient accuracy for policy comparison, even without detailed road network routing.

3. **Simulation validates optimization**: Static optimization models predict the right direction, but simulation captures stochastic dynamics (queuing, utilization, variance) that analytical models miss.

4. **CRN is essential**: Common Random Numbers reduced the variance of pairwise comparisons by >90%, enabling detection of the small P1 vs P2 difference (0.064 min) with just 30 replications.

5. **Robustness matters more than precision**: The finding that policy rankings are invariant to ±100% demand changes is more valuable than exact response time predictions.

---

## Future Work Recommendations

1. **Dynamic repositioning**: Real-time ambulance relocation based on current system state
2. **Road network integration**: OSRM/Google routing for accurate travel times
3. **Multi-incident demand**: Include medical, fire, and hazmat calls
4. **Multi-borough scaling**: Extend to all 5 NYC boroughs
5. **Stochastic optimization**: Account for demand uncertainty in the MIP
6. **CAD integration**: Embed recommendations in dispatch software
7. **Machine learning demand forecasting**: Use recent trends for adaptive allocation

---

## Maintenance & Update Procedures

### Quarterly Model Recalibration
1. Download latest crash data from NYC Open Data
2. Re-run `scripts/demand_modeling.py` to update lambda tables
3. Re-run `scripts/run_optimization_comparison.py` for updated P2 allocation
4. Compare new allocation with current deployment

### Annual Full Re-validation
1. Run complete production experiment suite (1,440 simulations)
2. Compare simulation predictions with actual operational data
3. Adjust model parameters based on validation results
4. Update technical report with new findings

### Code Updates
- All source code in `src/ems_readiness/` with 39 unit tests
- Run `pytest tests/ -v` before any deployment
- Follow PEP 8 style conventions
- Update `docs/code_documentation.md` for API changes

---

*Project archived on March 12, 2026. All files available at github.com/cnsp/ems-optimization.*
