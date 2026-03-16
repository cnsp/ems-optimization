# Documentation Audit Report

**Date:** 2026-03-16  
**Branch:** `docs/audit-consistency-fixes`  
**PR:** [#3](https://github.com/cnsp/ems-optimization/pull/3)

---

## Audit Scope

Comprehensive review of all 60+ documentation files (.md, .yaml) in the EMS Optimization repository to identify and fix inconsistencies caused by:

1. **P0 baseline migration** — The P0 policy changed from index-based uniform allocation (~8.1 min mean RT) to spatially-stratified allocation (~3.17 min mean RT), but many documents retained the old metrics.
2. **Capacity default change** — Default firehouse capacity changed from 5 to 2 (per DEC-010), but several docs still referenced the old value.
3. **Nomenclature standardisation** — "P0-spatial" interim name should be just "P0" (per DEC-012), but appeared in many analysis documents.

---

## Issues Found and Fixed

### Category 1: Stale P0 Metrics (Critical)

The most pervasive issue. When P0 was redefined from index-based uniform to spatially-stratified, some document sections were updated while others retained old values, creating internal contradictions.

| Document | Issue | Fix |
|----------|-------|-----|
| `executive_summary.md` | 68% RT reduction, 8.1 min P0, 64.2% coverage, P2 named "Maximal Coverage", d=28.9 | Rewrote with current P0 metrics (3.17 min, 99.7%, 19% improvement) |
| `executive_presentation.md` | Slide 9: 5.5 min delta, 167,750 min annual savings, 3× fleet multiplier | Corrected to 0.60 min delta, ~18,300 min annual savings |
| `technical_report.md` §5.2 | ANOVA F=12,010, η²=0.996 | Corrected to F=1,019, η²=0.959 |
| `technical_report.md` §5.6 | Δ=−5.51 min, d=28.9 | Corrected to Δ=−0.60 min, d=10.3 |
| `technical_report.md` §7.2 | Finding 1 cited F=12,010 | Corrected to F=1,019 |
| `technical_report.md` §7.5 | Impact table: d=28.9 | Corrected to d=10.3 |
| `research_questions_assessment.md` RQ3 | −68.2% RT, d=28.9, F=12,010 | Corrected to −18.9%, d=10.3, F=1,019 |
| `research_questions_assessment.md` RQ5 | P0 8-min coverage: 57.5%–99.5% (old uniform) | Regenerated from production_v2: 99.1%–99.8% |
| `project_alignment_verification.md` | "P2 reduces mean RT by 68.2% vs P0" | Corrected to 18.9% |

### Category 2: P0-Spatial → P0 Naming

| Document | Occurrences Fixed |
|----------|-------------------|
| `capacity_sensitivity_analysis.md` | ~25 occurrences |
| `alternative_analyses_summary.md` | 1 occurrence |
| `final_summary.md` | 3 occurrences |
| `code_documentation.md` | 1 occurrence (+ clarified description) |
| `executive_presentation.md` | 2 occurrences (Slides 3, 5) |

### Category 3: Capacity Default (5 → 2)

| Document | Line | Fix |
|----------|------|-----|
| `conceptual_model.md` | §3.2 | C=5 → C=2 (with sensitivity analysis note) |
| `cbd_focused_optimization_analysis.md` | Line 28 | "Maximum 5 units" → "Maximum 2 units" |
| `project_alignment_verification.md` | Line 191 | capacity ≤ 5 → ≤ 2 |
| `technical_report.md` | §12.3 config table | capacity (5) → (2) |

### Category 4: Other Fixes

| Document | Fix |
|----------|-----|
| `executive_summary.md` | Simulation count 1,770 → 2,700+ |
| `executive_presentation.md` | Simulation count 1,440 → 2,700+ |
| `research_questions_assessment.md` | Simulation scale updated; effect size reference corrected |
| `policy_tradeoff_analysis.md` | Added prominent deprecation/context note explaining this uses the old uniform P0 |
| `implementation_roadmap.md` | Baseline label "P0, cap=5" → "P0, cap=2" |
| `capacity_sensitivity_heatmap.png` | Regenerated with 3 panels (K=20, 30, 40) instead of 2 |
| `generate_capacity_sensitivity_heatmap.py` | k_values=(20, 40) → (20, 30, 40) |

---

## Documents Reviewed but Not Modified

The following documents were reviewed and found to be accurate in context:

- `nomenclature_migration.md` — Historical reference, correctly describes the transition
- `decisions_log.md` — Historical record, mentions old metrics in correct historical context
- `assumptions_log.md` — Already updated with A14/A15 for P0 nomenclature
- `experimental_design.md` — Correctly describes v1 experiments with cap=5
- `firehouse_capacity_analysis.md` — Analysis document, cap=5 references are to the analysis subject
- `queue_analysis.md` — Uses 1,440 run count correctly (production-only scope)
- `cbd_comparison_and_validity_report.md` — Historical record of CBD addition
- `project_workflow_wbs.md` — Work breakdown with historical task descriptions
- All config files — Already correct (optimization.yaml has firehouse_capacity: 2)

---

## Verification

All corrected values were cross-referenced against:
- `results/production_v2/tables/descriptive_statistics.csv` (primary source of truth)
- `results/production_v2/tables/anova_results.csv`
- `results/production_v2/tables/effect_sizes.csv`
- `configs/optimization.yaml` (firehouse_capacity: 2)

---

## Remaining Known Issues (Low Priority)

1. Some internal/historical docs (gap_closure_report, cbd_comparison_report, project_workflow_wbs) still reference "1,770 runs" or "1,440 runs" — these are accurate for their specific scope and historical context.
2. The `research_questions_assessment.md` Experiment 1 header says "cap=5" — technically correct as the experiment was designed with cap=5, but results are identical to cap=2 since no firehouse gets >2 units at K=20.
3. `technical_report.md` §4 experiment table lists "cap=5" for Exp1–4 — historically accurate for the original experiment design.
