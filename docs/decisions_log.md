# Decisions Log

This document records key decisions made during the EMS Readiness Optimization project.

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
- Leverages existing infrastructure
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

*Last Updated: March 12, 2026*



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
- Provides comprehensive policy comparison for decision-makers

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
