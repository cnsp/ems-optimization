---
status: 🔄 HISTORICAL
last_updated: "2026-03-20"
note: "Preserved for project history. Contains old metrics/references in historical context. Do not use as current reference."
---
# Historical Data Preservation Policy

> **Document purpose:** Explains how old (pre-migration) information is handled
> throughout the repository — what was removed, what was preserved, and how
> preserved content is clearly marked so it cannot be accidentally cited as
> current.

---

## 1. Background

During Phases 8–10 the project underwent a major **nomenclature migration**
(see [`nomenclature_migration.md`](nomenclature_migration.md), DEC-011/DEC-012):

| Item | Old (v1) | Current (v2) |
|------|----------|---------------|
| P0 baseline | Index-based round-robin (`uniform_allocation`) | Spatially-stratified latitude selection (`spatially_stratified_allocation`) |
| P0 mean RT (K = 20) | ~18.5 min (optimisation), ~8.08 min (simulation) | ~4.75 min (optimisation), ~3.17 min (simulation) |
| Firehouse capacity default | 5 units | 2 units |
| P0 8-min coverage (K = 20) | ~64 % | ~99.7 % |

The migration touched **38 files** across configs, source code, results,
notebooks, and documentation (see `docs/project_wide_audit_report.md`).

---

## 2. Strategy: Remove vs. Preserve

### 2.1 Content that was **REMOVED** (stale / incorrect)

These artefacts were deleted or overwritten because they would mislead if
encountered without context:

| Category | Action | Example |
|----------|--------|---------|
| **Stale notebook outputs** | Cleared cell outputs | `07_production_results.ipynb` — 16 cells showed old P0 = 8.08 min |
| **Incorrect metric labels** | Replaced in-place | `policy_comparison.csv` — P0 label changed from "Uniform" → "Spatially-Stratified Uniform" |
| **Wrong config defaults** | Updated | `configs/optimization.yaml` — `firehouse_capacity: 5` → `2` |
| **Old P0 RT values in authoritative docs** | Replaced | `technical_report.md`, `executive_summary.md`, `optimization_results.md` |
| **Dead code paths** | Not removed, but deprecated with runtime warning | `uniform_allocation()` now emits `DeprecationWarning` |

### 2.2 Content that was **PRESERVED** (with clear markers)

Some old information has legitimate historical value — it documents *why*
decisions were made and provides an audit trail:

| Document | Old content retained | How it is marked |
|----------|---------------------|-----------------|
| `docs/policy_tradeoff_analysis.md` | Full analysis using original index-based P0 | **⚠️ Historical Context Note** banner at top of file |
| `docs/nomenclature_migration.md` | Complete before/after comparison of old vs new P0 | Entire document is the migration record |
| `docs/decisions_log.md` (DEC-011, DEC-012) | Rationale for replacing old P0 | Entries clearly dated and labelled "NEW" |
| `docs/assumptions_log.md` (A14, A15) | Reference to deprecated original P0 | Labelled "(Internal Reference)" and links to migration docs |
| `docs/conceptual_model_selection.md` | Mentions "original P0" RT of 8.08 min | In narrative context explaining the migration rationale |
| `docs/final_summary.md` | "8.08 → 3.17 min" improvement narrative | Presented as a before→after comparison |
| `docs/notebook_audit_report.md` | Audit log documenting what was changed | Meta-document describing the audit itself |
| `docs/project_workflow_wbs.md` | Task entry for P0 spatial analysis | Historical task log |
| `src/ems_readiness/optimization/policies.py` | `uniform_allocation()` function body | `DeprecationWarning` emitted at runtime; docstring says DEPRECATED |
| `src/ems_readiness/optimization/allocator.py` | `baseline_uniform()` method | Status = "Baseline (deprecated)"; docstring recommends `baseline_p0()` |

### 2.3 Result files with mixed historical data

| File | Contains old data? | Status |
|------|-------------------|--------|
| `results/baseline/simulation/all_results_raw.csv` | Yes — contains K = 10 rows where P0 RT > 4 min | **Expected** — small fleet sizes legitimately have higher RT |
| `results/tables/posthoc_comparisons.csv` | References to old statistical tests | Legacy from v1 production run; superseded by `results/baseline/tables/` |
| `results/archive/optimization/policy_comparison.csv` | No old data | ✓ Clean — all P0 labels are "Spatially-Stratified Uniform" |

---

## 3. Marking Conventions

### 3.1 Documentation banners

Historical documents that retain old data carry a blockquote banner:

```markdown
> **⚠️ Historical Context Note:** This analysis uses the **original
> index-based uniform P0** (deprecated), not the current spatially-stratified
> P0 baseline. See [`docs/nomenclature_migration.md`](nomenclature_migration.md)
> for the full nomenclature history.
```

### 3.2 Code deprecation

```python
warnings.warn(
    "uniform_allocation() is deprecated as the P0 baseline. "
    "Use spatially_stratified_allocation() instead.",
    DeprecationWarning, stacklevel=2,
)
```

### 3.3 Config comments

```yaml
# Capacity sensitivity analysis (docs/capacity_sensitivity_analysis.md)
# shows cap=2 matches or improves upon cap=5 at K≤40.
firehouse_capacity: 2
```

---

## 4. Safeguards Against Accidental Use

| Safeguard | Location | Mechanism |
|-----------|----------|-----------|
| Runtime deprecation warning | `policies.py` | `DeprecationWarning` on `uniform_allocation()` |
| Docstring flags | `policies.py`, `allocator.py` | "DEPRECATED" in first line of docstring |
| Verification script | `scripts/verify_project_consistency.py` | Automated 41-check scan for stale metrics, labels, and config values |
| Deprecated function registry | Verification script §5 | Lists all deprecated functions and their replacements |
| JSON verification report | `results/consistency_verification_report.json` | Machine-readable audit trail |
| Historical banner requirement | This document §3.1 | All docs with old data must carry ⚠️ banner |
| Nomenclature migration guide | `docs/nomenclature_migration.md` | Canonical mapping of old → new names |

---

## 5. Deprecated Functions — DO NOT USE

| Function | File | Replacement |
|----------|------|-------------|
| `uniform_allocation()` | `src/ems_readiness/optimization/policies.py` | `spatially_stratified_allocation()` |
| `baseline_uniform()` | `src/ems_readiness/optimization/allocator.py` | `baseline_p0()` |

These functions remain in the codebase for backward-compatibility and
historical traceability only. They emit `DeprecationWarning` at runtime and
are excluded from all production scripts and notebooks.

---

## 6. Verification Checklist

Before any submission or packaging, run:

```bash
python scripts/verify_project_consistency.py
```

The script checks:
- [ ] All configs have correct parameters (capacity = 2, correct policy names)
- [ ] All result files have correct metrics (P0 ~3–5 min, not 8+)
- [ ] All scripts use correct functions (no stale `uniform_allocation` calls)
- [ ] All authoritative docs have correct nomenclature
- [ ] No stale data references in production results
- [ ] All historical docs have warning banners

**Exit code 0** = all critical checks pass.

---

*Last updated: 2026-03-20*
