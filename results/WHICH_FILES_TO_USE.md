# Which Files Should I Use?

> Quick reference card. For full details, see [`docs/data_usage_guide.md`](../docs/data_usage_guide.md).

---

## I want to... → Use this file

| I want to... | Use this file |
|--------------|---------------|
| **Compare P0 vs P1 vs P2** | `baseline/tables/descriptive_statistics.csv` |
| **Get publication-ready comparison table** | `baseline/tables/table1_baseline_comparison.csv` |
| **See how RT changes with fleet size** | `baseline/tables/exp2_pivot_rt.csv` |
| **Check statistical significance** | `baseline/tables/anova_results.csv` + `posthoc_comparisons.csv` |
| **Get effect sizes** | `baseline/tables/effect_sizes.csv` |
| **Analyze capacity sensitivity** | `analysis/capacity_comparison/full_comparison.csv` |
| **View allocation heatmaps** | `analysis/heatmaps/heatmap_K*_policyP0_spatial_cap*.png` (use `P0_spatial`!) |
| **Check CBD analysis** | `analysis/cbd_focused_comparison/comparison_table.csv` |
| **Verify simulator correctness** | `baseline/simulation/verification/*.json` |
| **See validation pilots** | `baseline/simulation/validation_pilot/*.json` |
| **Get raw simulation data** | `baseline/simulation/all_results_raw.csv` |
| **Use publication figures** | `baseline/figures/pub_fig*.png` |
| **See allocation maps** | `baseline/figures/allocation_map_K*.png` |
| **Compare distance metrics** | `analysis/distance_comparison/comparison_table.csv` |

---

## Status Legend

| Symbol | Meaning |
|--------|---------|
| ✅ CURRENT | Safe to use for analysis and reporting |
| ⚠️ LEGACY | Historical reference only — do not cite as current |
| 📊 COMPARISON | Contains both current and legacy data for comparison |

---

## Folder Status at a Glance

| Folder | Status | Notes |
|--------|--------|-------|
| `baseline/` | ✅ **SOURCE OF TRUTH** | cap=2, spatial P0, 30 reps |
| `baseline/simulation/` | ✅ Current | V&V pilots |
| `baseline/tables/` | ✅ Current | Publication & experiment tables |
| `baseline/figures/` | ✅ Current | `pub_fig*` for publications |
| `analysis/capacity_comparison/` | ✅ Current | Full cap sweep |
| `analysis/heatmaps/` | ✅ Current | Use `P0_spatial` for canonical P0 |
| `analysis/cbd_focused_comparison/` | ✅ Current | CBD experiment |
| `analysis/distance_comparison/` | ✅ Current | Manhattan vs Haversine |
| `analysis/maps/` | ✅ Current | K=40 allocation maps |
| `analysis/simulation/` | ✅ Current | Production experiments & CBD experiment |
| `archive/optimization/` | ⚠️ **Legacy (cap=5)** | Phase 3 historical |
| `archive/` | ⚠️ Legacy | Audit reports, old figures/tables |

---

## Common Pitfalls

1. **Don't use `archive/optimization/` as current results** — it uses cap=5. Use `baseline/` instead.
2. **In `analysis/heatmaps/` and `analysis/capacity_comparison/`**, files with `P0` (no `_spatial`) are the deprecated index-based P0. Use `P0_spatial` for the canonical baseline.
3. **`capacity_sensitivity_heatmap.png`** in `archive/figures/` has a data format issue — use `analysis/figures/capacity_sensitivity_heatmap_notebook.png` instead.
4. **Files ending in `_notebook.csv`** in `archive/tables/` are from older notebook runs, not the production pipeline.
