# Phase 3: Optimization Results Summary

**Generated**: March 12, 2026

## Quick Summary

✓ **5 policies compared** across **4 unit counts** (K = 20, 30, 40, 48)
✓ **20 optimization scenarios** executed successfully
✓ **P2 (Demand-Weighted) is the winner**: 2.49-2.54 min response time, 100% coverage

## Key Results

### Best Policy
- **P2 (Demand-Weighted Optimized)** with **K=20-30 units**
- Response time: **2.54 min** (at K=20)
- Coverage: **100%** (all demand within 8 minutes)
- **86% faster** than uniform allocation at K=20

### Resource Efficiency
- Optimized allocation achieves near-optimal with **just 20 units**
- Uniform allocation requires **48 units** to match performance
- **Savings**: ~$500K-$1M annually (28 fewer units × $25-35K/unit/year)

### Diminishing Returns
**P2 gains are front-loaded**:
- K=20: 2.54 min
- K=30: 2.49 min (only 0.05 min improvement)
- K=40: 2.49 min (no improvement)
- K=48: 2.49 min (no improvement)

**P0 requires all resources to match**:
- K=20: 18.55 min
- K=30: 7.00 min
- K=40: 3.02 min
- K=48: 2.49 min ← finally matches P2

## Files Generated

### Allocations
- `allocations_K20.csv` - 20 units across 5 policies
- `allocations_K30.csv` - 30 units across 5 policies
- `allocations_K40.csv` - 40 units across 5 policies (representative)
- `allocations_K48.csv` - 48 units across 5 policies

### Analysis
- `policy_comparison.csv` - Full metrics for all 20 scenarios
- `sensitivity_analysis.csv` - Response time & coverage by K
- `findings_summary.json` - Best policies and statistics

### Visualizations
- `fig_policy_comparison.png` - 4-panel comparison chart
- `fig_tradeoff_curve.png` - Response time vs coverage
- `map_allocation_P0_K40.png` - Uniform allocation map
- `map_allocation_P1_K40.png` - Demand-proportional map
- `map_allocation_P2_K40.png` - Optimized allocation map

### Documentation
- `../docs/optimization_results.md` - Full technical report (19 pages)
- `../notebooks/05_optimization.ipynb` - Interactive analysis

## Comparison Table (K=40)

| Policy | RT (min) | Coverage | Firehouses | Comment |
|--------|----------|----------|------------|---------|
| **P2** | **2.49** | 100% | 24 | ⭐ **Best overall** |
| P2b | 2.49 | 100% | 40 | Same RT, more distributed |
| P1 | 2.52 | 100% | 21 | Simple heuristic, 1% slower |
| P0 | 3.02 | 100% | 40 | Uniform baseline, 21% slower |
| P2c | 3.48 | 100% | 10 | Coverage focus, 40% slower |

## Recommendations

### Immediate (0-3 months)
**Deploy P1 (Demand-Proportional) with current K=40**
- Simple to implement (no solver required)
- 17% improvement over current uniform allocation
- Politically acceptable (spreads units across 21 firehouses)

### Medium-term (3-12 months)
**Transition to P2 with K=20-30**
- Implement MIP solver (PuLP + CBC)
- Achieve 2.49-2.54 min response time
- Reallocate 18-20 units to other boroughs or functions
- **$500K-$1M annual savings**

### Long-term (12-24 months)
**Dynamic reallocation system**
- Quarterly updates based on crash patterns
- Time-of-day allocation (peak vs off-peak)
- Integration with real-time dispatch

## Spatial Patterns (K=40, P2)

**High allocation (5 units)**:
- Battalion 13 (Precinct 19 - Midtown East): 8.25 crashes/day
- Battalion 16 (Precinct 18 - Midtown North): 7.14 crashes/day
- Battalion 2 (Precinct 14 - Midtown South): 6.33 crashes/day
- Battalion 4 (Precinct 1 - Financial District): 5.62 crashes/day

**Zero allocation**:
- 24 firehouses in low-demand areas receive 0 units
- These areas covered by nearby high-allocation firehouses
- All areas still within 8-minute response time

## Next Steps

1. ✓ Optimization complete
2. ⏳ Discrete-event simulation validation (Phase 4)
3. ⏳ Robustness testing under uncertainty
4. ⏳ CBD-specific analysis
5. ⏳ Final report and presentation

---

*For full details, see `../docs/optimization_results.md`*
