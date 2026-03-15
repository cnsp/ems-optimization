# Assumptions Log

This document records all assumptions made during the EMS Readiness Optimization project.

## Data Assumptions

### A1: Crash Data Representativeness
**Assumption**: Historical crash data (2013-2026) is representative of future crash patterns.
**Rationale**: Long time series provides stable estimates of spatial and temporal patterns.
**Risk**: Major changes in traffic patterns (e.g., congestion pricing) could alter future demand.
**Mitigation**: Include sensitivity analysis on demand levels.

### A2: Location Accuracy
**Assumption**: Crash latitude/longitude coordinates are sufficiently accurate for demand estimation.
**Rationale**: NYPD geocoding process should provide reasonable accuracy for most incidents.
**Risk**: Some records may have missing or inaccurate coordinates.
**Mitigation**: Filter records with missing coordinates; aggregate to grid cells.

### A3: Firehouse Availability
**Assumption**: All Manhattan firehouses are available as potential EMS staging locations.
**Rationale**: Study explores optimal staging locations; operational constraints addressed separately.
**Risk**: Some firehouses may not have space or infrastructure for EMS staging.
**Mitigation**: Document as limitation; can add constraints in future iterations.

## Model Assumptions

### A4: Travel Time Model
**Assumption**: Travel times can be approximated using Euclidean distance with a scaling factor or simplified network distances.
**Rationale**: Full routing adds complexity without fundamentally changing optimization insights.
**Risk**: May over/underestimate actual response times in some areas.
**Mitigation**: Sensitivity analysis on travel time multipliers.

### A5: Single Unit Response
**Assumption**: Each crash incident requires exactly one EMS unit.
**Rationale**: Simplifies simulation while capturing core dispatch dynamics.
**Risk**: Major incidents may require multiple units.
**Mitigation**: Model captures most incidents; note as limitation.

### A6: Homogeneous Service Time
**Assumption**: Service time (on-scene + transport) follows a single distribution.
**Rationale**: Data on actual service times not available; use literature estimates.
**Risk**: Service times may vary by incident severity.
**Mitigation**: Sensitivity analysis on service time parameters.

### A7: Immediate Dispatch
**Assumption**: EMS units are dispatched immediately upon incident occurrence.
**Rationale**: Focuses on travel time rather than dispatch delay.
**Risk**: Real systems have dispatch processing time.
**Mitigation**: Can add dispatch delay parameter if needed.

## Geographic Assumptions

### A8: Manhattan Boundary
**Assumption**: Incidents and firehouses are classified by whether they fall within Manhattan borough boundary.
**Rationale**: Standard geographic classification for NYC.
**Risk**: Boundary edges may have some ambiguity.
**Mitigation**: Use official borough boundary polygons.

### A9: CBD Definition
**Assumption**: CBD is defined as the MTA Congestion Relief Zone boundary.
**Rationale**: Provides consistent, official boundary for the high-density core.
**Risk**: Other CBD definitions exist; results depend on boundary choice.
**Mitigation**: Document specific boundary used; can test alternatives.

## Operational Assumptions

### A10: Firehouse Staging Capacity (Updated v1.3.0)
**Assumption**: ~~Any number of EMS units can stage at a single firehouse.~~ **Updated:** Maximum 2 EMS units per firehouse (default capacity constraint).
**Rationale**: Full capacity sensitivity analysis (cap 1–5) demonstrates that cap=2 is operationally realistic based on typical FDNY firehouse infrastructure, and matches or improves performance compared to cap=5 at K ≤ 40. At K=20, capacity never binds (all policies allocate ≤ 1 unit/firehouse). At K=40, cap=2 forces wider geographic dispersion (29 vs 24 firehouses for P2).
**Risk**: Some firehouses may accommodate more or fewer units depending on physical infrastructure.
**Mitigation**: Capacity sensitivity analysis (cap 1–5) quantifies performance impact. Results are robust across all tested capacity values.

### A11: No Pre-emption
**Assumption**: Once an EMS unit is assigned to an incident, it completes service before taking new calls.
**Rationale**: Standard EMS operational policy.
**Risk**: Pre-emption for high-priority calls does occur.
**Mitigation**: Aligns with most common practice; note limitation.

### A12: Manhattan Distance Approximation
**Assumption**: Manhattan (taxicab) distance provides an upper-bound approximation of actual road distance in a grid-based network; Haversine provides a lower bound.
**Rationale**: Manhattan's street grid is largely rectangular; true road distance falls between Haversine and Manhattan distance.
**Risk**: Diagonal avenues and non-grid areas (e.g., lower Manhattan) deviate from both approximations.
**Mitigation**: Compared both metrics side-by-side; P2 allocation is robust to metric choice (mean RT differs by <0.01 min in simulation).

### A13: CBD-Focused Demand Weighting
**Assumption**: Applying a 3× demand weight to CBD precincts in the CBD-focused model is a reasonable multiplier to test CBD prioritisation.
**Rationale**: The 3× factor substantially up-weights CBD demand (from 56% to ~77% effective weight) without completely ignoring non-CBD.
**Risk**: A different multiplier (e.g., 2× or 5×) might yield different conclusions.
**Mitigation**: Results show that even with 3× weight, CBD RT does not improve (2.50 vs. 2.47 min), while non-CBD RT degrades dramatically (+159%). This confirms that the Manhattan-wide P2 is robust and any CBD-focused up-weighting is counterproductive.

### A14: Spatially-Stratified Baseline (P0-spatial) *(Added v1.3.0)*
**Assumption**: The baseline uniform allocation policy (P0) distributes units across firehouses using latitude-based spatial stratification rather than arbitrary index-based ordering.
**Rationale**: Index-based allocation (original P0) assigned units to firehouses in database-order, producing geographically biased clusters. Latitude-based stratification divides Manhattan into equal-width latitude bands and round-robins units across bands, ensuring even north–south geographic coverage regardless of firehouse ordering in the dataset.
**Risk**: Latitude-only stratification does not account for east–west variation or local demand density.
**Mitigation**: Manhattan's elongated north–south geometry makes latitude the dominant spatial axis. P0-spatial is a *baseline* comparator; optimized policies (P1, P2) already account for demand. Simulation confirms P0-spatial reduces mean response time by ~61% vs. original P0 (3.17 vs. 8.08 min at K=20).

---

## Assumption Review Schedule

| Assumption | Review Date | Reviewer | Status |
|------------|-------------|----------|--------|
| All | Initial | Project Lead | Documented |

---

*Last Updated: March 15, 2026*
