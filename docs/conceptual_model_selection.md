---
status: ✅ CURRENT
last_updated: "2026-03-20"
verified: "All metrics, code references, and nomenclature are current as of March 2026"
---
# Conceptual Model Selection Analysis — EMS Readiness Optimization

> **⚠️ Note:** This document references historical P0 metrics (e.g., 8.08 min) in narrative context to explain the rationale for the nomenclature migration (DEC-011/DEC-012). The **current** P0 baseline is spatially-stratified (mean RT ≈ 3.17 min at K=20). See [`nomenclature_migration.md`](nomenclature_migration.md) for details.

> **Date:** March 15, 2026
> **Purpose:** Comprehensive review of the conceptual model landscape, what was implemented, and the rationale behind selection decisions.

---

## 1. Full Conceptual Landscape

The project addresses a **facility location / resource allocation** problem: given K ambulance units and 48 candidate FDNY firehouses in Manhattan, determine the allocation that minimises response time and maximises coverage. The conceptual model document (`docs/conceptual_model.md`) and decisions log identify the following approaches that were **considered** during the project design:

### 1.1 Optimization Models Considered

| # | Approach | Category | Status |
|---|----------|----------|--------|
| 1 | **Demand-Weighted Allocation (P2)** | MIP — minimise demand-weighted response time | Yes Implemented & primary recommendation |
| 2 | **P-Median (P2-alt / P2b)** | MIP — minimise total (demand-weighted) distance | Yes Implemented |
| 3 | **Maximal Coverage (P2-cov / P2c)** | MIP — maximise demand covered within τ-minute threshold | Yes Implemented |
| 4 | **Set Covering** | MIP — cover all demand with minimum units | No Not implemented (subsumed by models 1–3) |
| 5 | **Multi-Objective / Pareto Optimization** | Bi-objective: response time vs. equity | No Deferred to future work |
| 6 | **Time-Varying Optimization (P3)** | Hour-specific λ tables, dynamic reallocation | No Deferred to future work |
| 7 | **CBD-Focused Demand-Weighted** | MIP — minimise response time for CBD precincts only | Yes Implemented (robustness check) |
| 8 | **CBD-Focused Maximal Coverage** | MIP — maximise CBD coverage within threshold | Yes Implemented (robustness check) |
| 9 | **Metaheuristics (GA, SA, etc.)** | Flexible but tuning required | No Not implemented (MIP solves fast enough) |
| 10 | **Heuristic approaches** | Fast but no optimality guarantee | No Not implemented as optimization (but baselines serve this role) |

### 1.2 Baseline Policies Considered

| # | Approach | Category | Status |
|---|----------|----------|--------|
| 11 | **Uniform Allocation (P0)** | Non-optimized — equal distribution | Yes Implemented |
| 12 | **Demand-Proportional Allocation (P1)** | Non-optimized — units proportional to nearest demand | Yes Implemented |
| 13 | **Spatially-Stratified P0 (P0 (spatially-stratified), latitude)** | Non-optimized — even geographic coverage | Yes Implemented (replaced original P0 in current version) |
| 14 | **Spatially-Stratified P0 (grid)** | Non-optimized — grid-based firehouse selection | Yes Implemented |
| 15 | **Spatially-Stratified P0 (maximin)** | Non-optimized — greedy farthest-point heuristic | Yes Implemented |
| 16 | **Random allocation** | Non-optimized — random with seed | No Not implemented (non-reproducibility concerns) |

### 1.3 Simulation Approaches Considered

| # | Approach | Status |
|---|----------|--------|
| 17 | **Discrete-Event Simulation (DES) via SimPy** | Yes Implemented |
| 18 | **Agent-Based Simulation** | No Rejected (too complex for this application) |
| 19 | **System Dynamics** | No Rejected (too aggregated) |
| 20 | **Analytical Queueing Models** | No Rejected (spatial component not representable) |

### 1.4 Distance Metrics Considered

| # | Metric | Status |
|---|--------|--------|
| 21 | **Haversine (great-circle)** | Yes Implemented (primary) |
| 22 | **Manhattan (taxicab) distance** | Yes Implemented (robustness check) |
| 23 | **Road network distance (OSRM/Google)** | No Not implemented (out of scope) |

---

## 2. Models Selected for Implementation

### 2.1 Core Optimization Models (in `models.py`)

| Function | Policy Code | Objective |
|----------|-------------|-----------|
| `build_demand_weighted()` | P2 | Minimise demand-weighted response time |
| `build_p_median()` | P2-alt | Minimise total demand-weighted distance (capacity-aware variant) |
| `build_maximal_coverage()` | P2-cov | Maximise demand-weighted coverage within 8-min threshold |
| `build_cbd_focused_demand_weighted()` | — | Minimise CBD-only demand-weighted response time |
| `build_cbd_focused_coverage()` | — | Maximise CBD-only coverage |

**Total: 5 optimization formulations** implemented as PuLP MIP models.

### 2.2 Baseline Policies (in `policies.py`)

| Function | Policy Code | Method |
|----------|-------------|--------|
| `uniform_allocation()` | P0 (original) | Equal distribution, round-robin remainder |
| `demand_proportional_allocation()` | P1 | Units proportional to nearest-firehouse demand credit |
| `spatially_stratified_allocation()` | P0 (spatially-stratified) | Three sub-methods: latitude, grid, maximin |

**Total: 3 baseline allocation functions** (with P0 (spatially-stratified) offering 3 sub-variants).

### 2.3 Mapping to Conceptual Framework

The conceptual model document (§1.1) defines **5 candidate policies** for simulation comparison:

| Code | Policy | Implementation |
|------|--------|----------------|
| P0 | Uniform allocation | `uniform_allocation()` → replaced by `spatially_stratified_allocation(method='latitude')` in current version |
| P1 | Demand-proportional | `demand_proportional_allocation()` |
| P2 | Demand-weighted optimisation | `build_demand_weighted()` |
| P2-alt | P-median selection | `build_p_median()` |
| P2-cov | Maximal coverage | `build_maximal_coverage()` |

The CBD-focused models and Manhattan distance variants were **additional robustness checks** beyond the core 5 policies.

---

## 3. Selection Rationale

### 3.1 Why These Three MIP Models?

The three core optimization models were chosen to represent **distinct operational objectives** (DEC-003):

1. **Demand-Weighted (P2):** Aligns with equity — weights response time by demand intensity, so high-demand areas receive proportionally better service. This is the **primary recommendation**.

2. **P-Median (P2-alt):** Answers "which K locations should we open?" — useful when the decision is about which firehouses to staff rather than how many units to place.

3. **Maximal Coverage (P2-cov):** Focuses on a binary service-level target (≤ 8 min) — useful for regulatory compliance and equity guarantees.

These three represent the **canonical facility location models** in the operations research literature (Daskin 2013; Church & ReVelle 1974; ReVelle & Swain 1970).

### 3.2 Why Were Other Models Excluded?

| Excluded Model | Reason |
|---------------|--------|
| **Set Covering** | Subsumed by Maximal Coverage — Set Covering asks "what's the minimum K to cover everything?" while Maximal Coverage asks "given K, what's the best coverage?" The latter is more relevant for fixed-budget decisions. |
| **Multi-Objective Pareto** | Adds significant complexity; deferred to future work. The single-objective models already allow comparing equity (P2 vs. P2-cov) indirectly. |
| **Time-Varying (P3)** | Requires dynamic reallocation during the simulation, which is out of scope for this **static staging** study. Listed as future work. |
| **Metaheuristics** | Unnecessary — the problem size (48 firehouses × 25–30 precincts) is small enough that CBC solves all MIPs in under 5 seconds. No need for approximate methods. |
| **Road Network Routing** | Requires external API integration (OSRM/Google) and adds complexity without changing relative policy rankings (confirmed by Manhattan distance robustness check). |

### 3.3 Why Two Baseline Policies?

- **P0 (Uniform):** A naïve lower bound — distributes units without any demand information. Answers "how much does intelligence in allocation actually matter?"
- **P1 (Demand-Proportional):** A practical heuristic requiring no solver — answers "can a simple rule-of-thumb approach the optimal?"

The **P0 (spatially-stratified)** upgrade (DEC-011) was motivated by discovering that the original P0 was artificially weak due to database-order bias, not a genuine "uniform" allocation. The latitude-based stratification corrected this, providing a fairer baseline (mean RT dropped from 8.08 → 3.17 min at K=20).

### 3.4 Why CBD-Focused Models?

The CBD accounts for ~56% of total demand. CBD-focused models (DEC-009) were implemented to test whether **geographic prioritisation** could improve performance in the highest-demand zone. The result was definitive: CBD-focused optimization **does not** improve CBD response time (+1.2%) but **sharply degrades** non-CBD service (+159% RT). This validates that the Manhattan-wide P2 already handles the CBD well.

### 3.5 Why Manhattan Distance as Robustness Check?

Manhattan distance (DEC-008) was implemented because Haversine underestimates road distances in a grid network. The side-by-side comparison showed **near-identical simulation results** (mean RT 2.55 min for both), with only 2 of 48 firehouses differing between allocations. This confirms Haversine is a sufficient approximation.

---

## 4. Experimental Coverage

### 4.1 Core Experiments (from `experimental_design.md`)

The formal experimental design uses **3 policies × 4 experiments = 1,440 total simulation runs**:

| Experiment | Policies | Factor Varied | Runs |
|-----------|----------|---------------|------|
| Exp 1: Policy Comparison | P0, P1, P2 | Baseline conditions (K=20) | 90 |
| Exp 2: Fleet Sensitivity | P0, P1, P2 | K ∈ {15, 20, 25, 30, 35, 40} | 540 |
| Exp 3: Demand Sensitivity | P0, P1, P2 | δ ∈ {0.5, 0.75, 1.0, 1.25, 1.5, 2.0} | 540 |
| Exp 4: Service Robustness | P0, P1, P2 | μ_s ∈ {20, 25, 30} min | 270 |

**Note:** The experimental design focuses on the 3 main policies (P0, P1, P2). The P2-alt and P2-cov models are evaluated in the optimization phase (Phase 3) but are **not** carried through all 4 simulation experiments — this is a deliberate scoping decision to keep the experiment tractable.

### 4.2 Additional Robustness Analyses

Beyond the core experiments, the following were conducted:

| Analysis | Models Used | Purpose |
|----------|------------|---------|
| Capacity sensitivity | P0, P1, P2 across cap ∈ {1,2,3,5,∞} | Determine default capacity (→ cap=2) |
| Manhattan vs. Haversine distance | P2 with both metrics | Validate distance metric robustness |
| CBD-focused optimization | CBD-DW, CBD-Coverage vs. P2 | Test geographic prioritisation |
| Spatial stratification comparison | P0-latitude, P0-grid, P0-maximin | Determine best P0 variant |

### 4.3 Coverage Assessment

| Dimension | Coverage |
|-----------|----------|
| Policy types | 5/5 conceptual policies implemented (P0, P1, P2, P2-alt, P2-cov) |
| Fleet sizes | 9 values tested: {10, 15, 20, 25, 30, 35, 40, 45, 48} |
| Demand variation | 6 multipliers: {0.5, 0.75, 1.0, 1.25, 1.5, 2.0} |
| Service time variation | 3 levels: {20, 25, 30} minutes |
| Distance metrics | 2: Haversine (primary) + Manhattan (robustness) |
| Capacity constraints | 5 levels: {1, 2, 3, 5, unlimited} |
| Geographic focus | 2: Manhattan-wide + CBD-focused |

**The experimental coverage is comprehensive** — all core conceptual models are implemented and tested, with extensive sensitivity analysis. The only deferred items (multi-objective Pareto, time-varying P3, road network routing) are clearly documented as future work.

---

## 5. Summary: How Model Selection Supports Research Goals

### Research Questions → Model Mapping

| Research Question | Models Used | Finding |
|-------------------|------------|---------|
| **RQ1:** How do policies compare on response time and coverage? | P0, P1, P2 (+ P2-alt, P2-cov) | P2 dominates: 2.49–2.54 min mean RT, 100% 8-min coverage |
| **RQ2:** How sensitive is performance to fleet size K? | P0, P1, P2 across K ∈ {15–40} | Diminishing returns beyond K=30; P2 advantage narrows with more units |
| **RQ3:** How robust is performance to demand changes? | P0, P1, P2 across δ ∈ {0.5–2.0} | P0 degrades fastest under high demand (H3 confirmed) |
| **RQ4:** How do service time variations affect policy performance? | P0, P1, P2 across μ_s ∈ {20–30} | P2 most robust to service time variation (H4 confirmed) |

### Key Methodological Strengths

1. **Canonical models:** The three MIP formulations (demand-weighted, p-median, maximal coverage) represent the standard operations research toolkit for facility location problems.
2. **Fair baselines:** The P0 (spatially-stratified) upgrade ensures the baseline is a genuine geographic benchmark, not an artifact of database ordering.
3. **Robustness via multiple dimensions:** Distance metric, capacity, demand intensity, service time, and geographic focus are all tested.
4. **Practical scoping:** Excluded models (metaheuristics, road network, dynamic reallocation) are justified and documented rather than silently omitted.
5. **Simulation validation:** All optimization solutions are evaluated through DES, not just static objective values — this captures queueing dynamics that MIP alone cannot.

### Conclusion

The project considered **~20+ distinct conceptual approaches** across optimization models, baseline policies, simulation methodologies, and distance metrics. Of these, **5 optimization formulations + 5 baseline policies + 1 simulation framework + 2 distance metrics** were implemented — covering the core conceptual landscape comprehensively. Selection decisions are well-documented in the decisions log, with clear rationale for both inclusions and exclusions. The experimental design provides thorough coverage of the parameter space relevant to the 4 research questions.

---

*Analysis prepared: March 15, 2026*
*Sources: `docs/conceptual_model.md`, `docs/decisions_log.md`, `docs/experimental_design.md`, `docs/optimization_formulation.md`, `docs/assumptions_log.md`, `src/ems_readiness/optimization/models.py`, `src/ems_readiness/optimization/policies.py`*
