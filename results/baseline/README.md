# baseline/ — ✅ SOURCE OF TRUTH

> **This folder contains the canonical simulation results for the project.**

## Parameters
- **Capacity**: 2 units per firehouse (DEC-010)
- **P0 Baseline**: Spatially-stratified uniform (DEC-011)
- **Replications**: 30 Monte Carlo runs per scenario
- **K values**: 10, 15, 20, 25, 30, 35, 40, 45, 48
- **Policies**: P0 (spatial), P1 (demand-proportional), P2 (demand-weighted MIP)

## Structure

```
baseline/
├── allocations/          # Unit allocations per (K, policy)
│   └── allocations_K{N}.csv
├── simulation/           # Raw simulation output
│   ├── results_K{N}.csv  # Per-K results
│   └── all_results_raw.csv  # Combined
├── tables/               # Statistical analysis
│   ├── descriptive_statistics.csv
│   ├── anova_results.csv
│   ├── posthoc_comparisons.csv
│   ├── effect_sizes.csv
│   ├── confidence_intervals.csv
│   └── queue_statistics.csv
├── figures/              # Production visualizations
│   ├── allocation_map_K{N}.png
│   ├── rt_distribution_K{N}.png
│   ├── mean_rt_vs_K.png
│   └── ... (coverage, utilization, etc.)
├── comparison_with_v1.csv  # v2 (cap=2) vs v1 (cap=5)
└── experiment_log.txt
```

## When to Use This Folder
- **Any simulation-based analysis** → start here
- **Statistical tests** → use `tables/`
- **Allocation maps** → use `figures/`
- **Raw data for custom analysis** → use `simulation/all_results_raw.csv`
