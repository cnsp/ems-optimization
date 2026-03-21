---
status: 🔄 HISTORICAL
last_updated: "2026-03-20"
note: "Preserved for project history. Contains old metrics/references in historical context. Do not use as current reference."
---
# Technical Report Gap Analysis & Fix Report

**Date:** 2026-03-16  
**Scope:** Comprehensive audit of `docs/core/technical_report.md` — figures, captions, and image references  
**Status:** All issues resolved

---

## Issues Found

### Issue 1: Duplicate Images in Figure 4 Section (§5.7 CBD Robustness)

**Problem:** Two images were displayed in the Figure 4 area:
1. **Unlabeled** `![CBD Scenario Comparison](../../results/analysis/figures/cbd_scenario_comparison.png)` — a summary bar chart from EDA
2. **Labeled** `![CBD Robustness Enhanced](../../results/analysis/figures/cbd_robustness_enhanced.png)` — the actual Figure 4

The unlabeled image appeared immediately before the Figure 4 introduction paragraph, creating confusion about which image was Figure 4.

**Fix:** Removed the unlabeled `cbd_scenario_comparison.png` reference. Figure 4 now shows only `cbd_robustness_enhanced.png` with its caption.

---

### Issue 2: Duplicate Images in Figure 5 Section (§5.11 CBD-Focused vs Manhattan-Wide)

**Problem:** Two images were displayed in the Figure 5 area:
1. **Unlabeled** `![CBD-Focused Comparison](../../results/analysis/cbd_focused_comparison/cbd_focused_comparison.png)` — a raw comparison chart from the analysis subdirectory
2. **Labeled** `![CBD Equity-Efficiency Tradeoff Summary](../../results/analysis/figures/cbd_equity_tradeoff_summary.png)` — the actual Figure 5

**Fix:** Removed the unlabeled `cbd_focused_comparison.png` reference. Figure 5 now shows only `cbd_equity_tradeoff_summary.png` with its caption.

---

### Issue 3: Duplicate Images in Figure 6 Section (§5.12 Capacity Constraints)

**Problem:** Two images were displayed in the Figure 6 area:
1. **Unlabeled** `![Full Spectrum Capacity Summary](../../results/analysis/capacity_comparison/full_spectrum_summary.png)` — a multi-panel summary from the capacity comparison subdirectory
2. **Labeled** `![Capacity Sensitivity Heatmap](../../results/archive/figures/capacity_sensitivity_heatmap.png)` — the actual Figure 6

**Fix:** Removed the unlabeled `full_spectrum_summary.png` reference. Figure 6 now shows only `capacity_sensitivity_heatmap.png` with its caption.

---

### Issue 4: Figure 6 Caption Text Error — Incorrect K Value

**Problem:** The Figure 6 caption stated:
> "At K=20 **and K=30**, capacity is non-binding for all policies..."

The heatmap actually shows **K=20 and K=40** (not K=30). K=30 data exists in supplementary tables but is not displayed in this figure.

**Fix:** Updated caption to:
> "At K=20, capacity is non-binding for all policies..."

Removed the incorrect K=30 reference since the heatmap panels are K=20 and K=40 only.

---

### Issue 5: Capacity Sensitivity Heatmap — "Data Format Issue"

**Problem:** The `capacity_sensitivity_heatmap.png` displayed blank panels with "Data format issue" text instead of actual heatmap data. This was caused by a policy name mapping issue — the CSV data used labels like `P0`, `P1_demand`, and `P2_optimised`, but the plotting script's `POLICY_LABELS` dictionary wasn't mapping all variants correctly in an earlier version.

**Fix:** Regenerated the heatmap by running `scripts/generate_capacity_sensitivity_heatmap.py`. The script now correctly maps all policy label variants and produces a proper heatmap with numerical values for all 3 policies × 5 capacity levels × 2 K values.

---

## Verification Summary

### Final Figure Inventory (inline figures)

| Figure | Image File | Caption Present | Unique |
|--------|-----------|----------------|--------|
| Figure 1 | `results/baseline/figures/policy_comparison_panel_K20_cap2.png` | Yes | Yes |
| Figure 2 | `results/baseline/figures/response_time_distribution_by_policy.png` | Yes | Yes |
| Figure 3 | `results/archive/figures/fleet_sensitivity_dual.png` | Yes | Yes |
| Figure 4 | `results/analysis/figures/cbd_robustness_enhanced.png` | Yes | Yes |
| Figure 5 | `results/analysis/figures/cbd_equity_tradeoff_summary.png` | Yes | Yes |
| Figure 6 | `results/archive/figures/capacity_sensitivity_heatmap.png` | Yes | Yes |

### Supporting (unnumbered) Images

| Section | Image File | Purpose |
|---------|-----------|---------|
| §5.8 Queueing | `results/analysis/figures/queue_comparison_by_policy.png` | Supplementary |
| §5.9 Seasonal | `results/analysis/figures/seasonal_patterns.png` | Supplementary |
| §5.10 Distance | `results/analysis/distance_comparison/distance_comparison_bar.png` | Supplementary |

### Image File Existence Check

All 9 referenced images verified to exist on disk with non-zero file sizes.

---

## Changes Made

1. **Removed** 3 duplicate/unlabeled image references (lines ~528, ~609, ~660 in original)
2. **Fixed** Figure 6 caption: removed incorrect "K=30" reference
3. **Regenerated** `capacity_sensitivity_heatmap.png` with correct data rendering
4. Net line change: -6 lines (1161 → 1155)
