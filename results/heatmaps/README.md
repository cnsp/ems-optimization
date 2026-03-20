# heatmaps/ — ✅ CURRENT (Comprehensive Sweep)

Heatmap visualizations of unit allocations across K={5..45} × cap={1,2,3,5} × {P0, P0_spatial, P1, P2}.

## File Naming
```
heatmap_K{N}_policy{POLICY}_cap{C}.png
```

- `policyP0_spatial` — ✅ Canonical spatially-stratified P0
- `policyP0` (no `_spatial`) — 📊 Legacy index-based P0 (for comparison)
- `policyP1` — ✅ P1 demand-proportional
- `policyP2` — ✅ P2 demand-weighted optimized

## Allocations Subfolder
`allocations/` contains the underlying CSV data for each heatmap.

## Metadata
`generation_summary.json` — parameters and timestamp of the generation run.

> **For the canonical P0 baseline**, always use `policyP0_spatial` files.
