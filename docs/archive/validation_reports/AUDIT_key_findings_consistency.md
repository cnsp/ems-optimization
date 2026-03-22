# Key Findings Consistency Audit

**Date:** 2026-03-21  
**Scope:** README.md vs docs/core/technical_report.md vs recomputed baseline data  
**Baseline data source:** `results/baseline/simulation/results_K20.csv` (30 replications per policy)  
**Cross-checked against:** `results/baseline/tables/table1_baseline_comparison.csv`, `results/baseline/tables/descriptive_statistics.csv`, `results/baseline/tables/exp1_summary.csv`, `results/baseline/simulation/validation_pilot/pilot1_p0_vs_p2.json`

---

## 1. COMPARISON TABLE

### P0 (Spatially-Stratified Baseline) at K=20

| Metric | README | Technical Report | Recomputed Baseline | table1_baseline | Match? |
|--------|--------|------------------|---------------------|-----------------|--------|
| Mean RT (min) | 3.17 | 3.17 | **3.165** (CI: 3.142–3.188) | 3.17 | ✅ All consistent (rounding) |
| P90 RT (min) | *(not reported)* | **5.62** | **5.334** | **5.33** | ❌ Tech report WRONG (5.62 ≠ 5.33) |
| P95 RT (min) | **6.26** | *(not reported)* | **6.280** | *(not in table1)* | ✅ README matches |
| 6-min Coverage | *(not reported)* | 94.0% | **94.0%** | *(not in table1)* | ✅ Tech report matches |
| 8-min Coverage | **99.6%** | **99.6%** | **99.7%** | **99.7%** | ⚠️ Both docs say 99.6%, baseline says 99.7% |
| Utilization | **7.6%** | **7.8%** | **7.57% (≈7.6%)** | 0.076 (7.6%) | ❌ Tech report WRONG (7.8% ≠ 7.6%) |

### P1 (Demand-Proportional) at K=20

| Metric | README | Technical Report | Recomputed Baseline | table1_baseline | Match? |
|--------|--------|------------------|---------------------|-----------------|--------|
| Mean RT (min) | *(not reported)* | 2.63 | **2.619** | 2.62 | ⚠️ Tech report rounds to 2.63, table1 to 2.62 |
| P90 RT (min) | *(not reported)* | 4.03 | **3.988** | 3.99 | ✅ Consistent (rounding) |
| 6-min Coverage | *(not reported)* | 98.0% | **98.0%** | *(not in table1)* | ✅ |
| 8-min Coverage | *(not reported)* | 99.6% | **99.6%** | 99.6% | ✅ |
| Utilization | *(not reported)* | 7.5% | **7.45% (≈7.4%)** | 0.074 (7.4%) | ⚠️ Tech report rounds up to 7.5% |

### P2 (Demand-Weighted MIP Optimized) at K=20

| Metric | README | Technical Report | Recomputed Baseline | table1_baseline | Match? |
|--------|--------|------------------|---------------------|-----------------|--------|
| Mean RT (min) | **2.57** | **2.57** | **2.567** | 2.57 | ✅ All consistent |
| P90 RT (min) | *(not reported)* | **3.76** | **3.752** | **3.75** | ✅ Consistent (rounding) |
| P95 RT (min) | **4.66** | *(not reported)* | **4.688** | *(not in table1)* | ✅ README matches (rounding) |
| 6-min Coverage | *(not reported)* | 98.2% | **98.2%** | *(not in table1)* | ✅ |
| 8-min Coverage | **99.6%** | **99.6%** | **99.7%** | **99.7%** | ⚠️ Both docs say 99.6%, baseline says 99.7% |
| Utilization | **7.5%** | **7.5%** | **7.41% (≈7.4%)** | 0.074 (7.4%) | ⚠️ Both docs round up to 7.5% |

### Improvement Metrics (P2 vs P0)

| Metric | README | Technical Report | Recomputed | Match? |
|--------|--------|------------------|------------|--------|
| Mean RT improvement | **−19.0%** | **−18.9%** | **−18.9%** | ⚠️ README rounds (18.93% → 19.0%) |
| P90 RT improvement | *(N/A)* | **−33.1%** | **−29.7%** | ❌ Tech report WRONG (uses stale P0 P90=5.62) |
| P95 RT improvement | **−25.6%** | *(N/A)* | **−25.4%** | ✅ README close (rounding) |

---

## 2. CANONICAL CORRECT VALUES (from `results_K20.csv`, n=30)

| Metric | P0 | P1 | P2 |
|--------|-----|-----|-----|
| Mean RT (min) | 3.17 [3.14, 3.19] | 2.62 [2.60, 2.64] | 2.57 [2.55, 2.59] |
| P90 RT (min) | **5.33** | 3.99 | 3.75 |
| P95 RT (min) | **6.28** | 5.01 | 4.69 |
| 6-min Coverage | 94.0% | 98.0% | 98.2% |
| 8-min Coverage | **99.7%** | 99.6% | **99.7%** |
| Utilization | **7.6%** | 7.4% | 7.4% |

| Improvement (P2 vs P0) | Value |
|-------------------------|-------|
| Mean RT | **−18.9%** |
| P90 RT | **−29.7%** |
| P95 RT | **−25.4%** |
| 6-min Coverage | **+4.2 pp** |
| 8-min Coverage | **0 pp** |

---

## 3. WHICH DOCUMENT IS WRONG

**Technical Report has 3 material errors:**

1. **P0 P90 Response Time = 5.62 min** → Should be **5.33 min**  
   - Source of error: Appears to be stale data from an earlier pilot run. The pilot1 JSON shows P0 P90 mean = 5.50 min (also different from 5.62), suggesting the 5.62 value predates even the validation pilot and was never updated when production results were generated.
   - Impact: Cascading error — the "−33.1% P90 improvement" claim is also wrong (should be −29.7%).

2. **P0 Utilization = 7.8%** → Should be **7.6%**  
   - Source of error: Likely from pilot1 or an earlier run with slightly different parameters/seeds. The production baseline consistently shows 7.57% (rounds to 7.6%).

3. **P0 8-min Coverage = 99.6%** → Should be **99.7%**  
   - Minor rounding error. The raw mean across 30 reps is 99.67%, which rounds to 99.7%, not 99.6%.

**README has 2 minor issues:**

1. **Mean RT improvement = −19.0%** → Should be **−18.9%**  
   - Aggressive rounding (18.93% → 19.0%). The tech report correctly says 18.9%.

2. **8-min Coverage = 99.6% for both P0 and P2** → P0 and P2 should both be **99.7%**  
   - Same rounding issue as the tech report.

**Verdict: Technical Report is MORE wrong** than README. README is largely correct with minor rounding differences. Technical report has a stale P90 value (5.62) that creates a cascading error in the P90 improvement claim.

---

## 4. RECOMMENDED FIX

### Technical Report (`docs/core/technical_report.md`)

**Fix the §1 Key Findings table (line ~62-68):**
```
| P0 (Spatially-Stratified) | 3.17 | [3.14, 3.19] | 5.33 | 94.0% | 99.7% | 7.6% |
| P1 (Proportional) | 2.62 | [2.60, 2.64] | 3.99 | 98.0% | 99.6% | 7.4% |
| P2 (Optimized) | 2.57 | [2.55, 2.59] | 3.75 | 98.2% | 99.7% | 7.4% |
```

**Fix the §5.1 table (line ~419-424) — same values as above**

**Fix improvement claims (lines ~426-428):**
- "P2 reduces P90 response time by **29.7%** compared to P0 (from 5.33 to 3.75 min)"
- Keep "−18.9%" for mean RT (already correct)

**Fix P0 utilization** wherever "7.8%" appears → "7.6%"

### README.md

**Minor fixes to the Key Findings table (line ~12-17):**
- Change "−19.0%" → "−18.9%"
- Change P0 8-min Coverage "99.6%" → "99.7%"
- Change P2 8-min Coverage "99.6%" → "99.7%" (and improvement becomes "0 pp")

### Consistency with `table1_baseline_comparison.csv`
The table1 CSV is **correct and matches recomputed baseline** for all metrics it reports. It should be treated as the authoritative pre-formatted source.

---

## 5. ROOT CAUSE ANALYSIS

The tech report's stale P90 value (5.62) likely originated from an early simulation run before the production baseline was regenerated. The progression appears to be:

1. **Early pilot run** → P0 P90 ≈ 5.62 (used in tech report draft)
2. **Validation pilot (pilot1_p0_vs_p2.json)** → P0 P90 = 5.50 (improved but never synced to tech report)
3. **Production baseline (results_K20.csv)** → P0 P90 = 5.33 (final canonical value, used in table1)

The tech report was written using values from step 1 and was never fully reconciled with the production results from step 3. The README was updated more recently and uses production-era values, hence fewer discrepancies.
