---
status: 🔄 HISTORICAL
last_updated: "2026-03-20"
note: "Preserved for project history. Contains old metrics/references in historical context. Do not use as current reference."
---
# Notebook Nomenclature & Data Consistency Audit Report

> **⚠️ Note:** This audit report documents changes made during the P0 nomenclature migration. It references old metric values (e.g., 8.08 min) to describe *what was changed*. These are not current results. See [`nomenclature_migration.md`](nomenclature_migration.md).

**Date:** 2026-03-20  
**Reference:** DEC-012 (P0 Nomenclature Standardization)

## Correct Nomenclature

| Code | Name | Description |
|------|------|-------------|
| **P0** | Spatially-stratified uniform | Latitude-based spatial selection, 1 unit each (canonical baseline) |
| **P1** | Demand-proportional | Units allocated proportional to precinct demand rates |
| **P2** | Demand-weighted optimized | MIP minimizing demand-weighted expected response time |

**Data source:** `results/simulation/production/` (contains spatial P0 results, ~3.17 min at K=20)

---

## Notebooks Audited (18 total)

### Core Notebooks (9 files)

| Notebook | Changes | Details |
|----------|---------|---------|
| `01_end_to_end_workflow.ipynb` | Cleared outputs | 33 stale output cells cleared (already used correct code with `spatially_stratified_allocation` and baseline) |
| `02_eda_spatiotemporal.ipynb` | Cleared outputs | 20 output cells cleared |
| `03_input_modeling.ipynb` | No changes | Already consistent |
| `04_service_travel_proxy.ipynb` | Cleared outputs | 11 output cells cleared |
| `05_optimization.ipynb` | **Fixed nomenclature** | P0 descriptions changed from "Uniform" to "Spatial Baseline"; 5 markdown cells updated |
| `06_simulation_debug.ipynb` | **Fixed code + nomenclature** | `P0_uniform` → `P0` in JSON key references; section titles and labels updated; 6 output cells cleared |
| `07_production_results.ipynb` | **Cleared stale outputs** | 16 output cells cleared (were showing old P0 metrics: 8.08 min, 64.4% coverage) |
| `08_statistical_analysis.ipynb` | **Fixed metrics + cleared outputs** | Updated stale metric references (64.2% → ~99.7%, 68% → ~19% reduction); 14 output cells cleared |
| `09_cbd_analysis.ipynb` | No changes | Already consistent |

### Colab Notebooks (9 files)

| Notebook | Changes | Details |
|----------|---------|---------|
| `00_colab_setup_and_data.ipynb` | **Fixed imports** | `uniform_allocation` → `spatially_stratified_allocation` in import verification |
| `01_colab_eda_spatiotemporal.ipynb` | No changes | Already consistent |
| `02_colab_demand_modeling.ipynb` | No changes | Already consistent |
| `03_colab_service_modeling.ipynb` | No changes | Already consistent |
| `04_colab_optimization.ipynb` | **Fixed code + nomenclature** | `uniform_allocation` → `spatially_stratified_allocation`; P0 section header and summary updated |
| `05_colab_simulation.ipynb` | **Fixed code** | Fallback allocation generation uses `spatially_stratified_allocation` |
| `06_colab_statistical_analysis.ipynb` | No changes | Already consistent |
| `07_colab_visualization_reporting.ipynb` | No changes | Already had correct labels (`P0 (Spatial Baseline)`) |
| `EMS_Optimization_Complete_Pipeline.ipynb` | **Fixed code + labels** | `uniform_allocation` → `spatially_stratified_allocation`; P0 label updated to "Spatial Baseline" |

---

## Summary of Changes

| Category | Count |
|----------|-------|
| Code fixes (`uniform_allocation` → `spatially_stratified_allocation`) | 5 notebooks |
| JSON key fixes (`P0_uniform` → `P0`) | 1 notebook |
| Label/description fixes (Uniform → Spatial Baseline) | 3 notebooks |
| Stale metric corrections (64.2% → ~99.7%, 8.08 min → ~3.17 min) | 1 notebook |
| Output cells cleared (stale results) | 7 notebooks |
| No changes needed | 7 notebooks |

## Verification

After fixes, the following checks all pass (zero matches):
- No `uniform_allocation` calls in any notebook
- No `P0_uniform` references in any notebook
- No `P0 (Uniform)` labels in any notebook
- No stale `8.08` min metrics in any output
- No stale `64.2%` / `0.644` coverage in any output
- All P0 references use "Spatial Baseline" or "Spatially-stratified" terminology
- All code uses `spatially_stratified_allocation` for P0 policy generation
