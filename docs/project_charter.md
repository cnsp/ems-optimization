---
status: ✅ CURRENT
last_updated: "2026-03-20"
verified: "All metrics, code references, and nomenclature are current as of March 2026"
---
# Project Charter: EMS Readiness Optimization

## Project Title

EMS Readiness Optimization: Strategic Firehouse-Based EMS Staging Under Stochastic Crash Demand in Manhattan

## Problem Statement

Emergency Medical Services (EMS) response times are critical for patient outcomes in motor vehicle collisions. Current EMS staging strategies may not optimally position ambulances to minimize response times given the spatial and temporal variability of crash incidents in Manhattan. This project investigates whether optimized firehouse-based EMS staging can improve system readiness compared to baseline allocation policies.

## Objectives

### Primary Objectives

1. **Develop a discrete-event simulation model** that accurately represents EMS dispatch, travel, and service processes in Manhattan
2. **Compare optimized vs. baseline staging policies** to quantify potential improvements in system readiness metrics
3. **Evaluate time-varying vs. fixed staging** to determine if dynamic allocation provides significant benefits

### Secondary Objectives

1. Test robustness of conclusions within the Central Business District (CBD)
2. Conduct sensitivity analysis on key parameters (unit count, demand levels, travel times)
3. Provide practical recommendations for EMS operational planning

## Scope

### In Scope

- **Geographic Area**: Manhattan (primary), CBD/MTA Congestion Relief Zone (robustness)
- **Incident Type**: Motor vehicle collision crashes requiring EMS response
- **Staging Locations**: FDNY firehouses as candidate staging points
- **Analysis Period**: Historical crash data patterns (2013-2026)
- **Methods**: Discrete-event simulation, linear programming optimization

### Out of Scope

- Real-time operational implementation
- Other incident types (medical emergencies, fires)
- Detailed routing algorithms (simplified travel time assumptions)
- Budget/cost optimization
- Multi-borough analysis

## Research Questions

1. **RQ1**: Can optimized firehouse-based EMS staging improve system readiness versus baseline allocation?

2. **RQ2**: Does time-varying staging outperform fixed staging policies?

3. **RQ3**: Are the conclusions robust when the analysis is restricted to the Central Business District?

4. **RQ4**: How sensitive are the results to changes in:
 - Number of available EMS units
 - Demand intensity levels
 - Service time and travel time assumptions

5. **RQ5**: What are the key managerial trade-offs in implementing optimized staging?

## Deliverables

### Technical Deliverables

1. **Simulation Model**
 - Discrete-event simulation implemented in Python (SimPy)
 - Configurable parameters for scenario analysis
 - Documentation of model assumptions and validation

2. **Optimization Model**
 - Linear program for ambulance staging (PuLP)
 - Time-varying allocation framework
 - Baseline policy implementations

3. **Analysis Pipeline**
 - Data preprocessing scripts
 - Experiment execution framework
 - Results aggregation and visualization

### Documentation Deliverables

1. Final report with methodology, results, and recommendations
2. Technical documentation for reproducibility
3. Presentation slides summarizing key findings

### Data Deliverables

1. Processed datasets for Manhattan crashes
2. Firehouse location analysis
3. Demand pattern characterization

## Timeline (Estimated)

| Phase | Description | Duration |
|-------|-------------|----------|
| Phase 1 | Data acquisition and exploration | 1 week |
| Phase 2 | Data processing and demand modeling | 1 week |
| Phase 3 | Simulation model development | 2 weeks |
| Phase 4 | Optimization integration | 1 week |
| Phase 5 | Experiment execution | 1 week |
| Phase 6 | Analysis and documentation | 1 week |

## Stakeholders

- Project Lead / Researcher
- Academic Advisor (if applicable)
- Potential: NYC EMS operations (for real-world validation)

## Success Criteria

1. Simulation model produces statistically valid outputs
2. Clear evidence of improvement (or lack thereof) from optimization
3. Robust conclusions across multiple scenarios
4. Reproducible analysis pipeline
5. Documented assumptions and limitations

## Assumptions

See [assumptions_log.md](assumptions_log.md) for detailed assumptions.

## Risks

1. **Data Quality**: Crash location data may have inaccuracies
2. **Model Validity**: Simplified travel times may not reflect reality
3. **Computational**: Large-scale simulation may require significant compute time

## Approval

- Charter Created: March 2026
- Status: Active
