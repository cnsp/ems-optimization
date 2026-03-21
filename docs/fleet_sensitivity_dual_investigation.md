---
status: 📋 REFERENCE
last_updated: "2026-03-20"
verified: "Specialized analysis document. Cross-reference with current production results."
---
# Investigation Report: `fleet_sensitivity_dual.png` and Related Figure Issues

## Summary

**`fleet_sensitivity_dual.png` is NOT broken.** It exists at the correct path (`results/figures/fleet_sensitivity_dual.png`), contains valid dual-panel chart content (Mean Response Time vs Fleet Size + Coverage vs Fleet Size), and is correctly referenced in all documentation files.

The **actual broken figure** was `capacity_sensitivity_heatmap.png`, which had a **policy label mapping bug** causing P0 data to be silently dropped. This has been fixed.

---

## Step 1: References to `fleet_sensitivity_dual`

Found in **5 documentation files**:

| File | Reference Type |
|------|---------------|
| `docs/technical_report.md` (line 472) | `![Fleet Sensitivity Analysis](../results/figures/fleet_sensitivity_dual.png)` |
| `docs/technical_report.md` (line 947) | Listed as Figure 3 in artifact index |
| `docs/visualization_index.md` (line 105) | Catalog entry with source script `run_production_v2.py` |
| `docs/figure_trace_guide.md` (line 91) | Trace entry #30 linking to technical report Section 5.6 |
| `docs/output_comparison_report.md` (line 124) | Listed under fleet sensitivity figures |

All references use the **correct path**: `results/figures/fleet_sensitivity_dual.png`.

## Step 2: Actual Files Found

Three fleet sensitivity files exist:

| File | Size | Content |
|------|------|---------|
| `fleet_sensitivity_dual.png` | 285 KB | ✓ Valid dual-panel chart (2777×1231 px) |
| `fleet_sensitivity_curve.png` | 65 KB | Valid single-panel curve |
| `fleet_sensitivity_v2_dual.png` | (variant) | Valid chart (not referenced in docs) |

**No mismatch found** — the referenced file exists and renders correctly.

## Step 3: Root Cause of the Reported Issue

The actual problematic figure was **`capacity_sensitivity_heatmap.png`**, which was documented in `output_comparison_report.md` as:

> `capacity_sensitivity_heatmap.png` — Capacity sensitivity heatmap (**broken — shows "Data format issue"**)

### Bug Details

In `scripts/generate_capacity_sensitivity_heatmap.py`, the policy label mapping was:

```python
POLICY_LABELS = {
    "P0_spatial": "P0",    # Expected 'P0_spatial' in data
    "P1_demand": "P1",
    "P2_optimised": "P2",
}
```

But the simulation CSV (`results/analysis/capacity_comparison/simulation_results.csv`) stores the policy as **`"P0"`**, not `"P0_spatial"`. This caused:
1. P0 rows failed the `map()` → returned `NaN`
2. `dropna(subset=["Policy"])` silently removed all P0 data
3. Heatmap rendered with only P1 and P2 (or showed "Data format issue" in earlier versions)

### Fix Applied

Updated `POLICY_LABELS` to handle all known variants:

```python
POLICY_LABELS = {
    "P0": "P0",
    "P0_spatial": "P0",
    "P1": "P1",
    "P1_demand": "P1",
    "P2": "P2",
    "P2_optimised": "P2",
}
```

Also fixed the `reindex` to deduplicate values:
```python
policy_order = list(dict.fromkeys(v for v in POLICY_LABELS.values() if v in pivot.index))
```

## Step 4: Verification

After the fix, the heatmap correctly shows all three policies:

**K=20:**
| Policy | cap=1 | cap=2 | cap=3 | cap=4 | cap=5 |
|--------|-------|-------|-------|-------|-------|
| P0 | 3.11 | 3.11 | 3.11 | 3.11 | 3.11 |
| P1 | 2.59 | 2.62 | 2.62 | 2.62 | 2.62 |
| P2 | 2.56 | 2.56 | 2.56 | 2.56 | 2.56 |

**K=40:**
| Policy | cap=1 | cap=2 | cap=3 | cap=4 | cap=5 |
|--------|-------|-------|-------|-------|-------|
| P0 | 2.44 | 2.44 | 2.44 | 2.44 | 2.44 |
| P1 | 2.39 | 2.32 | 2.34 | 2.34 | 2.34 |
| P2 | 2.38 | 2.42 | 2.46 | 2.50 | 2.49 |

## Step 5: Other Referenced Files — Path Mismatch Audit

While investigating, I found **44 images referenced in docs** that exist in subdirectories of `results/` but not in `results/figures/`. These are not broken — the docs reference them with correct relative paths to their actual locations (e.g., `results/baseline/figures/`, `results/analysis/capacity_comparison/`, etc.). No action needed for these.

**No other scripts** had the `P0_spatial` vs `P0` label mismatch.

## Files Changed

| File | Change |
|------|--------|
| `scripts/generate_capacity_sensitivity_heatmap.py` | Fixed POLICY_LABELS mapping + deduplicated reindex |
| `results/figures/capacity_sensitivity_heatmap.png` | Regenerated with all 3 policies |
| `docs/output_comparison_report.md` | Removed "broken" annotations |

**Commit:** `fix: capacity_sensitivity_heatmap missing P0 due to policy label mismatch`
