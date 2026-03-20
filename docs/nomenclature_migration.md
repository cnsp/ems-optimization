---
status: 🔄 HISTORICAL
last_updated: "2026-03-20"
note: "Preserved for project history. Contains old metrics/references in historical context. Do not use as current reference."
---
# P0 Nomenclature Migration Guide

**Status**: Internal Reference Document  
**Last Updated**: March 15, 2026  
**Purpose**: Explains the evolution of the P0 baseline policy definition for team members interpreting older project artifacts.

---

## Current Standard (v3.0)

| Policy | Name | Definition | Code Entry Point |
|--------|------|-----------|-----------------|
| **P0** | Spatially-Stratified Uniform Allocation | Firehouses sorted by latitude; K evenly-spaced stations selected; units distributed round-robin | `EMSAllocator.baseline_p0()` → `policies.spatially_stratified_allocation()` |
| **P1** | Demand-Proportional Allocation | Units allocated proportional to nearby demand | `EMSAllocator.baseline_demand_proportional()` → `policies.demand_proportional_allocation()` |
| **P2** | Demand-Weighted MIP Optimization | Mixed-Integer Program minimizing demand-weighted expected response time | `EMSAllocator.solve(model="demand_weighted")` → `models.build_demand_weighted()` |

---

## Historical Evolution

### Phase 1: Original P0 ("V1")

- **Implementation**: `policies.uniform_allocation()` — round-robin allocation across all 48 firehouses in database (CSV) order
- **Problem**: Firehouse CSV ordering clustered downtown/CBD firehouses first, creating an inadvertent geographic bias
- **Performance**: Mean RT = 8.08 min at K=20, 64.4% 8-minute coverage
- **Period**: Project inception through Phase 8

### Phase 2: Spatially-Stratified P0 ("V2")

- **Implementation**: `policies.spatially_stratified_allocation()` — latitude-based spatial stratification
- **Improvement**: Mean RT = 3.17 min at K=20, 99.6% 8-minute coverage (61% improvement)
- **Rationale**: Fair geographic baseline that eliminates CSV-ordering bias
- **Decision Reference**: DEC-011 in `docs/decisions_log.md`
- **Period**: Phase 9 onwards

### Phase 3: Nomenclature Standardization ("V3")

- **Change**: Removed all V1/V2 terminology from public-facing documents
- **P0 now always means**: spatially-stratified allocation
- **Original uniform allocation**: Retained in code with `DeprecationWarning`, not referenced in technical report
- **Decision Reference**: DEC-012 in `docs/decisions_log.md`
- **Period**: Phase 11 (current)

---

## How to Interpret Older Documents

If you encounter older project artifacts (notebooks, early draft reports, commit messages), use this mapping:

| Old Term | Current Equivalent | Notes |
|----------|-------------------|-------|
| P0 (before Phase 9) | `uniform_allocation()` (deprecated) | Index-based round-robin; **not** the current P0 |
| P0 (V1) | `uniform_allocation()` (deprecated) | Same as above |
| P0 (V2) | P0 (current) | Spatially-stratified; this is now just "P0" |
| P0-legacy | `uniform_allocation()` (deprecated) | Another name for the old index-based method |
| P0-spatial | P0 (current) | Interim name; now just "P0" |
| P0_baseline | P0 (current) | Code variable name used in some scripts |
| Production V1 | Early experiments using old P0 | Results with 8.08 min mean RT |
| Production V2 | Current experiments using current P0 | Results with 3.17 min mean RT for P0 |

---

## Code Compatibility

The deprecated `uniform_allocation()` function remains available but issues a `DeprecationWarning`:

```python
# Deprecated — do not use in new code
from ems_readiness.optimization.policies import uniform_allocation
alloc = uniform_allocation(firehouses, K=20)  # DeprecationWarning issued

# Correct — use this instead
from ems_readiness.optimization.policies import spatially_stratified_allocation
alloc = spatially_stratified_allocation(K=20, method='latitude')

# Or via EMSAllocator
allocator = EMSAllocator(...)
result = allocator.baseline_p0(K=20)  # Calls spatially_stratified_allocation internally
```

---

## Performance Comparison (for reference)

| Metric | Old P0 (index-based, deprecated) | Current P0 (spatially-stratified) | P2 (optimized) |
|--------|----------------------------------|-----------------------------------|----------------|
| Mean RT (K=20) | 8.08 min | 3.17 min | 2.57 min |
| P90 RT (K=20) | 19.47 min | 5.62 min | 3.76 min |
| 8-min Coverage (K=20) | 64.4% | 99.6% | 99.6% |
| Firehouses Used | 20 (arbitrary) | 20 (geographically spread) | 20 (demand-optimized) |

The 61% improvement from the old to current P0 confirms that **geographic placement** is the dominant factor in EMS response time performance.

---

*This document is for internal team reference only. The technical report (`docs/technical_report.md`) presents only the current methodology without historical evolution.*
