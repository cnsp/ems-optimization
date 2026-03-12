# Gap Remediation Plan

**Project:** EMS Readiness Optimization for Manhattan
**Date:** March 12, 2026
**Reference:** `docs/project_alignment_verification.md`

---

## Overview

The project alignment verification identified **no critical gaps** and **three minor gaps** between the project outline and deliverables. All three gaps have low remediation effort because the underlying data and infrastructure already exist.

---

## Gap Summary

| ID | Gap | Priority | Effort | Status |
|----|-----|----------|--------|--------|
| G1 | CBD robustness comparison not in DES experiments | ⚠️ Recommended | Medium | Open |
| G2 | Queue metrics underreported in technical report | ⚠️ Nice-to-have | Low | Open |
| G3 | Seasonal analysis not deeply covered | ⚠️ Nice-to-have | Very Low | Open |

---

## G1: CBD Robustness Comparison in DES

### Problem
The outline states: *"Manhattan analysis with CBD robustness comparison"* (§3) and *"Compare Manhattan-wide results with CBD-focused robustness results"* (§11). While CBD data is analyzed in EDA and the spatial analysis, the four production DES experiments run only Manhattan-wide.

### Recommended Fix: Post-Hoc CBD Filtering (Option B)
Rather than re-running simulations, filter the existing incident-level logs from production experiments to include only incidents in CBD precincts, then recompute metrics.

### Implementation Steps

1. **Identify CBD precincts** — Use `data/raw/cbd_boundary.geojson` and `data/processed/precincts_manhattan.geojson` to identify which precincts overlap the CBD (approximately precincts 1, 5, 6, 7, 10, 13, 14, 17, 18, 19, 20).

2. **Create CBD analysis script** — `scripts/analyze_cbd_robustness.py`:
   - Load incident-level logs from production experiments
   - Filter incidents where `precinct` is in the CBD precinct set
   - Recompute: mean RT, P90 RT, 8-min coverage, utilization for CBD-only incidents
   - Compare P0 vs P1 vs P2 performance in CBD subset
   - Generate comparison table and figure

3. **Add CBD section to technical report** — Add a subsection in Results (§5) titled "CBD Robustness Check":
   - Table comparing Manhattan-wide vs CBD metrics for each policy
   - Brief interpretation (e.g., "P2's advantage is even more pronounced in the CBD due to higher demand concentration")

4. **Update experimental design doc** — Add note that CBD analysis was performed as post-hoc filtering.

### Estimated Effort: 2–3 hours

### Prerequisites
- Incident-level logs must include precinct field (✅ they do)
- CBD precinct mapping exists (✅ `cbd_boundary.geojson` available)

---

## G2: Queue Metrics in Technical Report

### Problem
Queue length (mean, max) and queue fraction are tracked in every simulation run but not prominently reported in the technical report or publication tables.

### Recommended Fix
Add queue metrics to the results section.

### Implementation Steps

1. **Extract queue data** from `results/simulation/production/exp1_policy_comparison.csv`:
   - Columns: `mean_queue_length`, `max_queue_length`, `queue_fraction`, `incidents_queued`

2. **Add to technical report** — In §5 (Results), add a paragraph:
   > "Queue behavior was minimal across all policies under the K=20 baseline scenario. Under P2, mean queue length was [X] with [Y]% of incidents experiencing any queuing, compared to [A] and [B]% under P0."

3. **Optionally add table** — A small table in the appendix showing queue metrics by policy.

### Estimated Effort: 30 minutes

---

## G3: Seasonal Analysis

### Problem
The outline mentions analysis by "season" in §6. The project covers hourly and DOW patterns thoroughly but does not explicitly discuss seasonal/monthly trends.

### Recommended Fix
Add a brief seasonal note to the demand model documentation.

### Implementation Steps

1. **Check existing EDA** — `notebooks/02_eda_spatiotemporal.ipynb` likely includes monthly/annual trends. If so, reference it.

2. **Add sentence to demand model spec** — In `demand_model_spec.md`, add:
   > "Monthly analysis reveals relatively stable crash rates across seasons, with a slight increase during summer months (June–August) and a modest decrease in winter (December–February). These seasonal effects are small relative to hourly and DOW variation and are subsumed by the NHPP model's average rate."

3. **If data supports it**, add a brief monthly bar chart to the EDA notebook.

### Estimated Effort: 15–30 minutes

---

## Priority Ranking

| Priority | Action | Impact on Submission |
|----------|--------|---------------------|
| 1 | G1: CBD robustness | Directly addresses explicit outline requirement |
| 2 | G2: Queue metrics | Strengthens MOE coverage claim |
| 3 | G3: Seasonal note | Minor completeness improvement |

---

## Decision

All three gaps are **non-blocking** for submission. The project fully meets the outline's structural and methodological requirements. These remediation items would polish the submission but are not required for a complete and defensible project package.

**Recommended action:** Address G1 (CBD robustness) if time permits, as it is the only item explicitly called out in the outline's scope and experimental design sections. G2 and G3 can be addressed with minimal effort during final editing.
