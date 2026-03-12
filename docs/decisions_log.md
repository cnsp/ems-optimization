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
