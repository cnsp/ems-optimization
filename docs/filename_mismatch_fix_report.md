---
status: 🔄 HISTORICAL
last_updated: "2026-03-20"
note: "Preserved for project history. Contains old metrics/references in historical context. Do not use as current reference."
---
# Filename Mismatch Fix Report

## Summary

**Root Cause:** 30 PNG files in `results/figures/` existed locally but were **not tracked in Git** due to a `.gitignore` rule (`results/figures/*.png`). The original 43 figures had been force-added previously (commit `c9c0f07`), but 30 additional figures generated in later phases were never force-added. This caused **broken image links** when viewing documentation on GitHub.

**Fix Applied:** Force-added all 30 untracked PNG files to Git tracking (commit `c9406c2`).

---

## Detailed Findings

### 1. Mismatches Found

**No actual filename mismatches exist** between documentation references and file names. The earlier concern about `fleet_sensitivity_dual.png` vs `fleet_sensitivity_v2_dual.png` was a false alarm — both files exist as separate figures, and docs correctly reference `fleet_sensitivity_dual.png`.

The real issue was that **30 PNG files were untracked in Git** despite being referenced in documentation.

### 2. Broken Embedded Images on GitHub (9 files)

These files were referenced via `![alt](path)` syntax and would render as broken images on GitHub:

| File | Referenced In |
|------|--------------|
| `fleet_sensitivity_dual.png` | `technical_report.md:472`, `fleet_sensitivity_dual_investigation.md:17` |
| `cbd_scenario_comparison.png` | `technical_report.md:528`, `cbd_robustness_analysis.md:81` |
| `cbd_response_comparison.png` | `cbd_robustness_analysis.md:78` |
| `cbd_heatmap.png` | `cbd_robustness_analysis.md:84` |
| `queue_comparison_by_policy.png` | `queue_analysis.md:100`, `technical_report.md:554` |
| `queue_vs_fleet_size.png` | `queue_analysis.md:103` |
| `queue_vs_demand.png` | `queue_analysis.md:106` |
| `queue_heatmap.png` | `queue_analysis.md:109` |
| `seasonal_patterns.png` | `technical_report.md:575` |

### 3. Additional Untracked Files (21 files)

Referenced in `visualization_index.md`, `figure_trace_guide.md`, and other docs via backtick notation:

- `allocation_comparison_K20.png`
- `capacity_sensitivity_heatmap_notebook.png`
- `cbd_robustness.png`
- `demand_sensitivity_curve.png`
- `distance_matrix_coverage.png`
- `fleet_sensitivity_curve.png`
- `p0_spatial_map.png`
- `p0_spatial_metrics.png`
- `p0_spatial_north_south.png`
- `p0_vs_p2_response_time.png`
- `policy_comparison.png`
- `precinct_demand_heatmap.png`
- `precinct_demand_rates.png`
- `precinct_demand_rates_improved.png`
- `production_fleet_sensitivity.png`
- `queue_metrics.png`
- `response_time_coverage_tradeoff.png`
- `seasonal_decomposition.png`
- `seasonal_heatmap.png`
- `statistical_effect_sizes.png`
- `temporal_demand_patterns.png`

### 4. Action Taken

- **No files renamed** — all filenames already matched their documentation references
- **No documentation updated** — all references were correct
- **30 files force-added to Git** — bypassing `.gitignore` rule, consistent with the original force-add approach in commit `c9c0f07`

### 5. Post-Fix Verification

- **73 PNG files** now tracked in `results/figures/` (43 original + 30 newly added)
- **All embedded image references** (`![](...)`) resolve to tracked files
- **All specific backtick references** resolve to tracked files
- **0 broken links** remaining

### 6. Note on `.gitignore`

The `.gitignore` rule `results/figures/*.png` remains in place. This is intentional — it prevents accidental commits of new generated figures. Critical figures must be explicitly force-added with `git add -f`. This is consistent with the project's approach of only tracking essential deliverables.
