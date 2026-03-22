# === PHASE 1: CANONICAL TRUTH VALIDATION ===

**Date:** 2026-03-22
**Scope:** Active materials only (README.md, docs/core/\*, docs/analysis/\*, results/baseline/, results/analysis/)
**Canonical sources:** `results/baseline/simulation/all_results_raw.csv`, `results/baseline/tables/*.csv`

---

## === 1. INCONSISTENCIES FOUND ===

### K-value Issues
**No K≠20 usage issues in active baseline.** K=20 is consistently used as the canonical baseline across all active docs. Fleet sensitivity analyses correctly use K∈{10,15,20,25,30,35,40,45,48}.

### Capacity Issues

| # | File | Issue | Severity |
|---|------|-------|----------|
| C1 | `docs/analysis/optimization_results.md` | **Marked ✅ CURRENT but contains cap=5 optimization data.** Table 2.1 shows Max Units=5 for P2 at K≥30, P2c with Max Units=5 at K=20. Header says "max 2 units" but all data is from cap=5 solver runs. The 46.5% improvement claim and all response time values (e.g., P0=4.75 at K=20) are optimization-only metrics from the cap=5 era — NOT simulation results. | **CRITICAL** |
| C2 | `docs/analysis/firehouse_capacity_analysis.md` | Shows `capacity=5` in code blocks. Correctly marked as 🔄 HISTORICAL with warning banner. | Minor (acceptable) |

### Numeric Inconsistencies

#### Technical Report (`docs/core/technical_report.md`) vs Canonical CSV

| # | Metric | Tech Report Value | CSV Canonical Value | Location in Report | Severity |
|---|--------|-------------------|--------------------|--------------------|----------|
| N1 | **P0 P90 RT** | **5.62 min** | **5.33 min** | Lines 65, 421, 427, 714, 816, 900 | **CRITICAL** |
| N2 | **P90 improvement (P2 vs P0)** | **−33.1%** | **−29.7%** | Lines 65, 427, 714, 816, 900 | **CRITICAL** (cascades from N1) |
| N3 | P0 95% CI | [3.10, 3.24] | [3.14, 3.19] | Line 421 | Stale |
| N4 | P1 P90 RT | 4.03 | 3.99 | Line 422 | Minor |
| N5 | P0 Utilization | 7.8% | 7.6% | Lines 68, 421, 718 | Stale |
| N6 | P1 Utilization | 7.5% | 7.4% | Lines 68, 422 | Minor |
| N7 | P2 Utilization | 7.5% | 7.4% | Lines 68, 423 | Minor |
| N8 | P0 8-min Coverage | 99.6% | 99.7% | Lines 18, 67, 421, 428, 714, 734, 766, 816 | Stale |
| N9 | P2 8-min Coverage | 99.6% | 99.7% | Lines 18, 67, 423, 428, 714, 734, 766, 816 | Stale |
| N10 | P1 Mean RT | 2.63 | 2.62 | Lines 64, 422 | Minor (rounding) |
| N11 | P0 K=15 Mean RT | 3.70 | 3.68 | Line 464 | Minor |
| N12 | P0 K=30 Mean RT | 2.78 | 2.81 | Line 466 | Minor |
| N13 | P0 K=40 Mean RT | 2.58 | 2.45 | Line 467 | **Stale** |
| N14 | P0 K=15 Coverage | 99.0% | 99.1% | Line 464 | Minor |
| N15 | P0 K=30 Coverage | 99.9% | 99.8% | Line 466 | Minor |
| N16 | P0 K=40 Coverage | 99.9% | 99.8% | Line 467 | Minor |
| N17 | Utilization range | "7.5% to 7.8%" | 7.4% to 7.6% | Line 718 | Stale |
| N18 | "η² values above 0.99" | η²=0.959 at K=20 | CSV: F=1019, η²=0.959 | Line 714 | **Stale** (overstated) |

#### README.md vs Canonical CSV

| # | Metric | README Value | CSV Canonical Value | Severity |
|---|--------|--------------|--------------------| ---------|
| R1 | P0 P95 RT | 6.26 | 6.28 | Minor |
| R2 | P2 P95 RT | 4.66 | 4.69 | Minor |
| R3 | P95 Improvement | −25.6% | −25.4% | Minor |
| R4 | Mean RT Improvement | −19.0% | −18.9% | Minor |
| R5 | P0 8-min Coverage | 99.6% | 99.7% | Minor |
| R6 | P2 Utilization | 7.5% | 7.4% | Minor |
| R7 | Unit test count | "39 unit tests (pytest)" (line 139), "39 tests" (line 303) | **176 tests across 13 modules** (pytest --co) | **Stale** |
| R8 | Footer test count | "176 unit tests" (line 427) | 176 tests ✓ | OK |
| R9 | Sim run count | "2,700+" | Tech report says 2,400; actual ~2,760 (see below) | **Stale** (all three documents disagree) |

#### Executive Presentation (`docs/core/executive_presentation.md`) vs CSV

| # | Metric | Exec Pres Value | CSV Canonical Value | Severity |
|---|--------|-----------------|--------------------| ---------|
| E1 | P0 P95 RT | 6.26 | 6.28 | Minor |
| E2 | P2 P95 RT | 4.66 | 4.69 | Minor |
| E3 | P1 P95 RT | 5.05 | 5.01 | Minor |
| E4 | P0 6-min Coverage | 93.7% (slide 2, line 30) | 94.0% | Stale |
| E5 | P0 8-min Coverage | 99.6% | 99.7% | Minor |

#### Executive Summary (`docs/core/executive_summary.md`) vs CSV
- P90 values: 5.33, 3.99, 3.75 — **matches CSV** ✅
- 8-min Coverage: 99.7%, 99.6%, 99.7% — **matches CSV** ✅
- Mean RT: 3.17, 2.62, 2.57 — **matches CSV** ✅
- Sim run count: "2,700+" — disagrees with tech report "2,400"

### Simulation Run Count Inconsistency

| Document | Claimed Count | 
|----------|---------------|
| README.md | 2,700+ |
| Executive Summary | 2,700+ |
| Executive Presentation | 2,700+ |
| Technical Report (abstract, throughout) | 2,400 |

**Actual counts (from CSVs):**
- `all_results_raw.csv`: 810 runs (3 policies × 9 K × 30 reps)
- `exp1_policy_comparison.csv`: 90 (overlap with above at K=20)
- `exp2_fleet_sensitivity.csv`: 720
- `exp3_demand_sensitivity.csv`: 540
- `exp4_service_robustness.csv`: 270
- `cbd_experiment_results.csv`: 330
- Production subtotal (exp1-4): 1,620
- Total non-duplicated: ~2,760 (baseline 810 + CBD 330 + remaining production unique ~1,620)

Neither "2,400" nor "2,700+" is precisely correct.

### Artifact Issues

| # | Issue | Severity |
|---|-------|----------|
| A1 | `results/figures/capacity_sensitivity_heatmap.png` — Shows "Data format issue" placeholder text for K=20 and K=40 panels (broken figure, no actual heatmap data rendered). Per uploaded screenshot. | **CRITICAL** |
| A2 | `results/analysis/figures/capacity_sensitivity_heatmap.png` — same issue as A1 (39KB, likely broken) | **CRITICAL** |
| A3 | Tech report Figure 9 caption says "K=20, K=30, and K=40" but the actual heatmap only has K=20 and K=40 panels (K=30 panel missing) | **Stale** |
| A4 | No rt_heatmap_K30.png exists in `results/analysis/capacity_comparison/` (only K20 and K40) | Stale |

---

## === 2. CANONICAL VALUES ===

**Source:** `results/baseline/simulation/all_results_raw.csv` (K=20, cap=2, 30 reps)

| Metric | P0 | P1 | P2 |
|--------|----|----|-----|
| Mean Response Time | **3.17 min** | **2.62 min** | **2.57 min** |
| Mean RT 95% CI | [3.14, 3.19] | [2.60, 2.64] | [2.55, 2.59] |
| P90 Response Time | **5.33 min** | **3.99 min** | **3.75 min** |
| P95 Response Time | **6.28 min** | **5.01 min** | **4.69 min** |
| 6-min Coverage | **94.0%** | **98.0%** | **98.2%** |
| 8-min Coverage | **99.7%** | **99.6%** | **99.7%** |
| Mean Utilization | **7.6%** | **7.4%** | **7.4%** |
| Queue Fraction | 0.0 | 0.0 | 0.0 |
| Total Incidents (mean) | 570.6 | 572.8 | 571.4 |

**Derived:**
- Mean RT improvement (P2 vs P0): **−18.9%**
- P90 RT improvement (P2 vs P0): **−29.7%**
- P95 RT improvement (P2 vs P0): **−25.4%**
- ANOVA F-statistic (K=20): **1,019.25** (p < 0.001, η² = 0.959)

**Fleet sensitivity (P0, canonical):**

| K | Mean RT | 8-min Coverage |
|---|---------|----------------|
| 15 | 3.68 min | 99.1% |
| 20 | 3.17 min | 99.7% |
| 30 | 2.81 min | 99.8% |
| 40 | 2.45 min | 99.8% |

**Test count:** 176 tests across 13 test modules

---

## === 3. AFFECTED DOCS/ARTIFACTS ===

| File | Issues Found |
|------|-------------|
| `docs/core/technical_report.md` | N1–N18 (P90, CI, utilization, coverage, fleet sensitivity, η² claim) |
| `README.md` | R1–R9 (P95, improvement %, coverage, test count, run count) |
| `docs/core/executive_presentation.md` | E1–E5 (P95, coverage) |
| `docs/core/executive_summary.md` | Run count only (metrics are correct) |
| `docs/analysis/optimization_results.md` | C1 (entire document is cap=5 optimization data disguised as CURRENT) |
| `results/figures/capacity_sensitivity_heatmap.png` | A1 (broken figure) |
| `results/analysis/figures/capacity_sensitivity_heatmap.png` | A2 (broken figure) |

---

## === 4. SEVERITY CLASSIFICATION ===

### Critical (factual errors that change conclusions)
1. **N1+N2**: Tech report P0 P90 = 5.62 (actual: 5.33) → "33.1% P90 improvement" (actual: 29.7%). Appears in abstract, key findings table, results section, discussion, conclusions. Cascading error across 6+ locations.
2. **C1**: `docs/analysis/optimization_results.md` — marked CURRENT, contains cap=5 optimization-only data. All metrics (P0=4.75, 46% improvement, Max Units=5) are stale. This document is unreliable for anyone reading it as current.
3. **A1+A2**: `capacity_sensitivity_heatmap.png` — broken figure showing "Data format issue" placeholder. Referenced as Figure 9 in the tech report.

### Stale (outdated numbers, small magnitude, don't change conclusions)
4. **N3**: P0 CI [3.10, 3.24] → [3.14, 3.19] (narrower range)
5. **N5+N17**: P0 utilization 7.8% → 7.6%; range "7.5%–7.8%" → "7.4%–7.6%"
6. **N8+N9**: 8-min coverage 99.6% → 99.7% (appears ~15 times in tech report)
7. **N13**: P0 K=40 RT 2.58 → 2.45
8. **N18**: "η² values above 0.99" claim — actual η²=0.959 at K=20 (still large, but overstated)
9. **R7**: "39 tests across 4 modules" → 176 tests across 13 modules
10. **R9**: Simulation run count: README/exec say 2,700+, tech report says 2,400 (actual ~2,760)
11. **E4**: P0 6-min coverage 93.7% → 94.0% (one location in exec pres)
12. **A3**: Tech report Figure 9 caption says K=20,K=30,K=40 but figure only has K=20,K=40

### Minor (rounding differences ≤ 0.05, don't affect narrative)
13. **N4,N6,N7,N10,N11,N12,N14,N15,N16**: Small rounding differences (≤ 0.04 min RT, ≤ 0.1pp coverage)
14. **R1–R6**: README rounding differences (P95 off by 0.02–0.03, coverage off by 0.1pp)
15. **E1–E3,E5**: Exec presentation rounding differences

---

*END OF PHASE 1 VALIDATION REPORT — NO FIXES APPLIED*
