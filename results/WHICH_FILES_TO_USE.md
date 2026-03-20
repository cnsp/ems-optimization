# Which Files Should I Use?

> Quick reference card. For full details, see [`docs/data_usage_guide.md`](../docs/data_usage_guide.md).

---

## I want to... → Use this file

| I want to... | Use this file |
|--------------|---------------|
| **Compare P0 vs P1 vs P2** | `production_v2/tables/descriptive_statistics.csv` |
| **Get publication-ready comparison table** | `tables/table1_baseline_comparison.csv` |
| **See how RT changes with fleet size** | `tables/exp2_pivot_rt.csv` |
| **Check statistical significance** | `production_v2/tables/anova_results.csv` + `posthoc_comparisons.csv` |
| **Get effect sizes** | `production_v2/tables/effect_sizes.csv` |
| **Analyze capacity sensitivity** | `capacity_comparison/full_comparison.csv` |
| **View allocation heatmaps** | `heatmaps/heatmap_K*_policyP0_spatial_cap*.png` (use `P0_spatial`!) |
| **Check CBD analysis** | `cbd_focused_comparison/comparison_table.csv` |
| **Verify simulator correctness** | `simulation/verification/*.json` |
| **See validation pilots** | `simulation/validation_pilot/*.json` |
| **Get raw simulation data** | `production_v2/simulation/all_results_raw.csv` |
| **Use publication figures** | `figures/pub_fig*.png` |
| **See allocation maps** | `production_v2/figures/allocation_map_K*.png` |
| **Compare distance metrics** | `distance_comparison/comparison_table.csv` |

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
| `production_v2/` | ✅ **SOURCE OF TRUTH** | cap=2, spatial P0, 30 reps |
| `simulation/` | ✅ Current | V&V + production experiments |
| `tables/` | ✅ Mostly current | See README for legacy files |
| `figures/` | ✅ Mostly current | `pub_fig*` for publications |
| `capacity_comparison/` | ✅ Current | Full cap sweep |
| `heatmaps/` | ✅ Current | Use `P0_spatial` for canonical P0 |
| `cbd_focused_comparison/` | ✅ Current | CBD experiment |
| `distance_comparison/` | ✅ Current | Manhattan vs Haversine |
| `maps/` | ✅ Current | K=40 allocation maps |
| `optimization/` | ⚠️ **Legacy (cap=5)** | Phase 3 historical |

---

## Common Pitfalls

1. **Don't use `optimization/` as current results** — it uses cap=5. Use `production_v2/` instead.
2. **In `heatmaps/` and `capacity_comparison/`**, files with `P0` (no `_spatial`) are the deprecated index-based P0. Use `P0_spatial` for the canonical baseline.
3. **`capacity_sensitivity_heatmap.png`** in `figures/` has a data format issue — use `capacity_sensitivity_heatmap_notebook.png` instead.
4. **Files ending in `_notebook.csv`** in `tables/` are from older notebook runs, not the production pipeline.
