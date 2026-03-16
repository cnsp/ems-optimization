# Decisions Log

This document logs key decisions made during the EMS Readiness Optimization project.

## Decision Template

```markdown
### [DEC-XXX] Decision Title

**Date**: YYYY-MM-DD
**Decision Maker**: [Name/Role]
**Status**: Proposed / Accepted / Superseded

**Context**:
[What situation prompted this decision?]

**Options Considered**:
1. Option A: [Description]
2. Option B: [Description]
3. Option C: [Description]

**Decision**:
[Which option was chosen and why]

**Consequences**:
[What are the implications of this decision?]
```

---

## Decisions

### [DEC-001] Study Area Selection

**Date**: 2026-03-12
**Decision Maker**: Project Lead
**Status**: Accepted

**Context**:
Need to select primary and secondary study areas for the EMS optimization analysis.

**Options Considered**:
1. All of NYC: Comprehensive but computationally expensive
2. Manhattan only: Focused, manageable scope
3. Manhattan + CBD robustness check: Balanced approach

**Decision**:
Option 3 - Manhattan as primary study area with CBD (MTA Congestion Relief Zone) as secondary area for robustness testing.

**Consequences**:
- Allows focused analysis with reasonable computational requirements
- CBD provides natural robustness check for high-demand area
- Results may not generalize to outer boroughs

---

### [DEC-002] Staging Location Candidates

**Date**: 2026-03-12
**Decision Maker**: Project Lead
**Status**: Accepted

**Context**:
Need to define candidate locations for EMS staging.

**Options Considered**:
1. Grid-based locations: Uniform coverage
2. Hospital locations: Practical operational sites
3. FDNY firehouses: Existing infrastructure
4. Combined approach: Multiple location types

**Decision**:
Option 3 - Use FDNY firehouses as staging candidates.

**Consequences**:
- Uses existing infrastructure
- Realistic operational scenario
- Limited to current firehouse locations (may not be optimal in absolute terms)

---

### [DEC-003] Simulation Framework

**Date**: 2026-03-12
**Decision Maker**: Project Lead
**Status**: Accepted

**Context**:
Need to select simulation methodology for EMS system modeling.

**Options Considered**:
1. Agent-based simulation: Detailed but complex
2. Discrete-event simulation (DES): Standard for queueing systems
3. System dynamics: Too aggregated for this application

**Decision**:
Option 2 - Discrete-event simulation using SimPy.

**Consequences**:
- Well-suited for modeling arrival, dispatch, service processes
- Efficient computation
- Python ecosystem enables integration with optimization

---

### [DEC-004] Optimization Approach

**Date**: 2026-03-12
**Decision Maker**: Project Lead
**Status**: Accepted

**Context**:
Need to select optimization method for ambulance staging.

**Options Considered**:
1. Heuristic approaches: Fast but no optimality guarantee
2. Mixed-integer programming: Optimal but potentially slow
3. Linear programming (relaxed): Fast, near-optimal for many problems
4. Metaheuristics: Flexible but tuning required

**Decision**:
Option 3 - Linear programming using PuLP, with integer constraints if needed.

**Consequences**:
- Fast solution times
- Optimality guarantees (for LP formulation)
- May need to round/adjust for integer ambulance counts

---

### [DEC-005] Data Temporal Scope

**Date**: 2026-03-12
**Decision Maker**: Project Lead
**Status**: Accepted

**Context**:
Need to determine which years of crash data to use.

**Options Considered**:
1. Most recent year only: Current patterns
2. Last 3 years: Balances recency and stability
3. All available data: Maximum sample size

**Decision**:
Option 3 - Use all available data for demand pattern estimation, with options to filter by date range.

**Consequences**:
- Maximum statistical power for pattern estimation
- May include outdated patterns (e.g., pre/post COVID)
- Can subset for sensitivity analysis

---

---

### [DEC-008] Alternative Distance Metric — Manhattan (Taxicab) Distance

**Date**: 2026-03-12
**Decision Maker**: Technical Lead
**Status**: Accepted

**Context**:
Haversine (great-circle) distance underestimates true road distances in a grid-based street network like Manhattan. Need to evaluate whether a Manhattan (taxicab) distance metric produces materially different optimization and simulation results.

**Options Considered**:
1. Haversine only (status quo)
2. Manhattan (taxicab) distance replacing Haversine
3. Both metrics compared side-by-side with simulation evaluation
4. Road network distance (OSRM / Google routing)

**Decision**:
Option 3 — Implement Manhattan distance as an alternative metric, run P2 optimization with both, and compare via simulation.

**Rationale**:
- Manhattan distance is ~27% longer on average than Haversine for Manhattan geography, better approximating grid-based street travel
- Side-by-side comparison quantifies sensitivity to metric choice
- Road network routing (Option 4) out of scope — requires external APIs and adds complexity without changing relative policy rankings
- Simulation dispatcher always uses Haversine internally, so this isolates the effect on allocation decisions

**Consequences**:
- Added `manhattan_distance()` function to `distance.py` and `metric` parameter to `build_distance_matrix()`
- Manhattan matrix generated: mean 5.48 mi vs. Haversine 4.29 mi
- Experiment showed near-identical simulation results (mean RT 2.55 min for both), confirming P2 allocation is robust to distance metric choice
- Only 2 of 48 firehouses differ between allocations
- Validates that Haversine is a sufficient approximation for this study

---

### [DEC-009] CBD-Focused vs. Manhattan-Wide Optimization

**Date**: 2026-03-12
**Decision Maker**: Technical Lead
**Status**: Accepted

**Context**:
The CBD (precincts 1, 5, 6, 7, 9, 10, 13, 14, 17, 18) accounts for ~56% of total demand. Need to evaluate whether a CBD-focused optimization strategy (up-weighting CBD demand) improves CBD response times and is preferable to the Manhattan-wide P2 model.

**Options Considered**:
1. Manhattan-wide P2 only (status quo)
2. CBD-only model (ignore non-CBD precincts)
3. CBD-focused model with 3× demand weight on CBD precincts
4. Multi-objective (Pareto) CBD/non-CBD optimization

**Decision**:
Option 3 — Implement CBD-focused demand-weighted model (3× CBD weight) and compare against Manhattan-wide P2 via simulation.

**Rationale**:
- CBD-focused (3× weight) tests whether concentrating resources improves CBD performance
- Comparison with Manhattan-wide P2 quantifies equity trade-offs
- CBD-only model (Option 2) is impractical — abandons non-CBD coverage
- Multi-objective Pareto (Option 4) deferred to future work

**Consequences**:
- Added `build_cbd_focused_demand_weighted()` and `build_cbd_focused_coverage()` to `models.py`
- CBD-focused P2 does NOT improve CBD RT (2.50 vs. 2.47 min, +1.2%) but sharply worsens non-CBD RT (6.88 vs. 2.66 min, +159%)
- Non-CBD 8-min coverage drops from 100% to 73.6%
- Validates that Manhattan-wide P2 already serves the CBD well without sacrificing equity
- Recommends against CBD-focused optimization for operational deployment

---

### [DEC-010] Firehouse Capacity Constraint — cap=2 Default

**Date**: 2026-03-15
**Decision Maker**: Technical Lead
**Status**: Accepted

**Context**:
The original formulation used cap=5 (DEC-005). Full capacity sensitivity analysis across cap ∈ {1, 2, 3, 5, unlimited} and K ∈ {10, 15, 20, 25, 30, 35, 40, 45, 48} was conducted to determine a realistic default.

**Options Considered**:
1. Keep cap=5 (original default)
2. Set cap=2 (tighter constraint)
3. Set cap=1 (strictest — one unit per firehouse)
4. Remove capacity constraint entirely

**Decision**:
Set default firehouse capacity to 2 (`firehouse_capacity: 2` in `configs/optimization.yaml`).

**Rationale**:
- At K ≤ 30, capacity never binds for any policy (max allocation ≤ 1 unit/FH), so cap=2 and cap=5 yield identical results
- At K=40, cap=2 forces wider geographic dispersion (29 vs. 24 firehouses for P2) with negligible performance loss (<0.15 min mean RT)
- cap=2 better reflects typical FDNY firehouse physical infrastructure than cap=5
- cap=1 is overly restrictive (requires 40 firehouses at K=40, some with suboptimal locations)
- Full sensitivity analysis (450 runs) confirms robustness across all capacity levels

**Consequences**:
- All Production V2 results use cap=2 as default
- V1→V2 P0 improvement is entirely due to P0-spatial baseline change (not capacity)
- P1 and P2 results unchanged between V1 and V2 (capacity does not bind at typical K)
- Future work can incorporate per-firehouse capacity data from FDNY

---

### [DEC-011] Spatially-Stratified P0 Baseline (P0-spatial)

**Date**: 2026-03-15
**Decision Maker**: Technical Lead
**Status**: Accepted

**Context**:
The original P0 (uniform allocation) assigned units to firehouses in database index order, which produced geographically clustered allocations biased toward lower Manhattan. This made P0 an artificially weak baseline.

**Options Considered**:
1. Keep index-based P0 (status quo)
2. Latitude-based spatial stratification (P0-spatial)
3. Random allocation with fixed seed
4. Grid-based stratification (latitude + longitude)

**Decision**:
Replace index-based P0 with latitude-based spatially-stratified P0 (P0-spatial) as the standard baseline.

**Rationale**:
- Index-based P0 is not a meaningful "uniform" allocation — it depends on arbitrary database ordering
- Latitude-based stratification divides Manhattan into equal-width bands and round-robins units, providing even north–south coverage
- Manhattan's elongated geometry makes latitude the dominant spatial axis; adding longitude stratification adds complexity with minimal benefit
- Random allocation is non-reproducible without seed management
- P0-spatial at K=20: mean RT = 3.17 min vs. 8.08 min for index-based P0 (−60.7%)
- P0-spatial provides a fairer baseline for evaluating P1 and P2 improvements

**Consequences**:
- P2 improvement over P0 narrows from 68% to 19% (2.57 vs. 3.17 min) — reflects that much of P0's original weakness was geographic clustering, not lack of demand-weighting
- All Production V2 results use P0-spatial
- Added `spatially_stratified_allocation()` and `spatial_stratification_analysis()` to `optimization/policies.py`
- Historical V1 results preserved in `results/production_v1/` for comparison

*Last Updated: March 15, 2026*



### [DEC-003] Optimization Policy Selection

**Date**: 2026-03-12
**Decision Maker**: Technical Lead
**Status**: Accepted

**Context**:
Multiple optimization formulations exist for EMS allocation. Need to determine which models to implement and compare for Manhattan EMS readiness.

**Options Considered**:
1. Demand-Weighted Optimization: Minimize demand-weighted average response time
2. P-Median: Minimize total response time (unweighted)
3. Maximal Coverage: Maximize demand covered within threshold
4. Set Covering: Cover all demand with minimum units
5. Hybrid: Multi-objective optimization

**Decision**:
Implement and compare options 1-3 (Demand-Weighted, P-Median, Maximal Coverage) plus two baseline policies (Uniform, Demand-Proportional).

**Rationale**:
- Demand-Weighted (P2) aligns with equity goals (weight by demand intensity)
- P-Median (P2b) provides comparison for unweighted optimization
- Maximal Coverage (P2c) represents pure coverage objective
- Baselines (P0, P1) provide non-optimized benchmarks
- Set Covering is subsumed by other models
- Multi-objective deferred to future work

**Consequences**:
- Need to implement 3 MIP solvers + 2 baseline policies
- Compare 5 policies × 4 K values = 20 scenarios
- Provides a full policy comparison for decision-makers

---

### [DEC-004] Unit Count Scenarios (K)

**Date**: 2026-03-12
**Decision Maker**: Technical Lead
**Status**: Accepted

**Context**:
Need to determine which unit counts to evaluate for optimization and sensitivity analysis.

**Options Considered**:
1. K = {20, 30, 40, 48} - Current recommendation
2. K = {10, 20, 30, 40, 50} - Wider range
3. K = {25, 30, 35, 40, 45, 50} - Finer granularity
4. K = 40 only - Current Manhattan capacity

**Decision**:
Use K = {20, 30, 40, 48}

**Rationale**:
- K=20: Resource-constrained scenario (50% of current)
- K=30: Moderate resource scenario (75% of current)
- K=40: Current Manhattan capacity (baseline)
- K=48: All firehouses staffed with 1 unit (upper bound given capacity=5)
- Provides sufficient range to observe diminishing returns
- Computationally efficient (4 scenarios × 5 policies = 20 optimizations)

**Consequences**:
- May miss optimal K if it falls outside range (e.g., K=25)
- But results show K=20 achieves near-optimal for P2, so range is sufficient
- Future work can refine with continuous K if needed

---

### [DEC-005] Firehouse Capacity Constraint

**Date**: 2026-03-12
**Decision Maker**: Technical Lead
**Status**: Accepted

**Context**:
Need to determine maximum units that can be allocated to a single firehouse.

**Options Considered**:
1. No limit (unconstrained)
2. Capacity = 3 units per firehouse
3. Capacity = 5 units per firehouse
4. Capacity = 10 units per firehouse
5. Variable capacity by firehouse size

**Decision**:
Use capacity = 5 units per firehouse (uniform across all locations)

**Rationale**:
- Based on FDNY operational guidance (typical firehouse can support 4-6 units)
- Prevents unrealistic concentration (e.g., all 40 units at one location)
- 5 units allows sufficient flexibility for optimized allocation
- Uniform capacity simplifies optimization formulation
- Conservative estimate (actual capacity varies 3-10 by location)

**Consequences**:
- P2 allocates up to 5 units at high-demand firehouses (Midtown, Financial District)
- May under-utilize capacity at larger firehouses
- Future work can incorporate actual capacity data per location

---

### [DEC-006] Coverage Threshold for Maximal Coverage Model

**Date**: 2026-03-12
**Decision Maker**: Technical Lead
**Status**: Accepted

**Context**:
Maximal Coverage model requires threshold τ (minutes) to define "covered" demand.

**Options Considered**:
1. τ = 5 minutes (aggressive response target)
2. τ = 8 minutes (NFPA recommendation)
3. τ = 10 minutes (relaxed target)
4. τ = 6 minutes (NYC local law)
5. Multiple thresholds for sensitivity analysis

**Decision**:
Use τ = 8 minutes (NFPA standard)

**Rationale**:
- NFPA 1710 specifies 8 minutes for 90% of emergencies
- Aligns with national standards for comparability
- NYC local law (6 min) is aspirational but not consistently achievable
- All policies achieve 100% coverage at τ=8 with K≥20
- Using τ=5 would require more units; τ=10 is too lenient

**Consequences**:
- P2c (Maximal Coverage) achieves 100% coverage but with worse response time (3.48 min)
- May want to test τ=6 in future work to align with NYC requirements
- 8-minute threshold appropriate for Manhattan context (dense, short distances)

---

### [DEC-007] Recommended Policy for Deployment

**Date**: 2026-03-12
**Decision Maker**: Technical Lead
**Status**: Proposed

**Context**:
After comparing 5 policies, need to recommend best allocation strategy for Manhattan EMS.

**Options Considered**:
1. P0 (Uniform): Equal distribution
2. P1 (Demand-Proportional): Simple heuristic
3. P2 (Demand-Weighted): Minimizes weighted response time
4. P2b (P-Median): Minimizes total response time
5. P2c (Maximal Coverage): Maximizes coverage

**Decision**:
**Primary recommendation: P2 (Demand-Weighted) with K=20-30**

**Rationale**:
- Best response time: 2.49-2.54 min (0-2% from optimal)
- 100% coverage at K≥20
- Efficient: Uses only 20-23 firehouses vs. 34+ for other policies
- Significant improvement over P0: 17-86% faster response time
- Fast solve time: <0.05 seconds
- Diminishing returns beyond K=30 (additional units provide <0.01 min benefit)

**Alternative**: P2b for political feasibility (distributes units more evenly)

**Consequences**:
- Requires MIP solver integration (PuLP + CBC)
- Concentrated allocation may face political resistance (some firehouses get 0 units)
- Recommend phased implementation: Start with P1, transition to P2
- Quarterly reallocation based on updated demand patterns

---

### [DEC-012] P0 Nomenclature Standardization

**Date**: 2026-03-15
**Decision Maker**: Technical Lead
**Status**: Approved

**Context**:
During development, the P0 baseline evolved through two implementations:
- **Original P0 (deprecated)**: Index-based round-robin allocation across all 48 firehouses in database order. This inadvertently created a CBD-biased allocation because firehouses in the CSV are clustered by geography, producing mean RT of 8.08 min at K=20 with only 64.4% 8-minute coverage.
- **Current P0**: Spatially-stratified uniform allocation using latitude-based firehouse selection, achieving 3.17 min mean RT at K=20 with 99.6% coverage — a 61% improvement.

Earlier documentation referred to these as "P0 (V1)" and "P0 (V2)" or "P0-legacy" and "P0-spatial", creating confusion in the technical report.

**Decision**:
Standardize nomenclature:
- **P0** = spatially-stratified uniform allocation (the only P0 going forward)
- The original index-based allocation is fully deprecated and removed from all public-facing documentation
- Historical context (V1 → V2 evolution) is retained only in internal documentation (this decisions log, `docs/assumptions_log.md`, and `docs/nomenclature_migration.md`)
- The technical report presents only the current methodology with no V1/V2 references

**Rationale**:
- The technical report is a publication-quality deliverable and should not contain development history
- External readers should see a clean, coherent methodology presentation
- Internal documentation provides the full audit trail for the team
- The deprecated `uniform_allocation()` function remains in code with a `DeprecationWarning` for backward compatibility

**Consequences**:
- Technical report uses "P0" exclusively to mean spatially-stratified allocation
- Code retains `uniform_allocation()` with deprecation warning for backward compatibility
- `baseline_p0()` in `EMSAllocator` calls `spatially_stratified_allocation()`
- All performance metrics in the technical report reflect the current P0 implementation
- Migration guide (`docs/nomenclature_migration.md`) available for interpreting older documents
