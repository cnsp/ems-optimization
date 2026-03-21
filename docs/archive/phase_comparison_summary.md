---
status: 🔄 HISTORICAL
last_updated: "2026-03-20"
note: "Preserved for project history. Contains old metrics/references in historical context. Do not use as current reference."
---
# EMS Optimization — Phase Comparison Summary

## TL;DR: **12 phases originally planned, 7 phases implemented**

The original project outline defined **12 sequential sections/phases**. The implementation consolidated these into **7 execution phases** that fully cover all 12 original sections (verified at 100% alignment).

---

## Original Phases Planned (from `EMS_Project_Outline_Hybrid_Final_Submission.docx`)

The outline document defines 12 numbered sections, each with explicit "Main tasks" and a "Completion output":

| # | Original Phase | Description |
|---|---------------|-------------|
| 1 | **Project Purpose & Decision Problem** | Define the operational decision, confirm baseline vs. alternative policies, frame as decision-support study |
| 2 | **Research Questions & Measures of Effectiveness** | Finalize research questions, choose primary/secondary MOEs, define service-level thresholds, specify decision rules |
| 3 | **Study Scope & System Boundary** | Lock geography (Manhattan + CBD), define spatial units, list included/excluded model components |
| 4 | **Data Strategy & Engineering Plan** | Acquire crash records, build zone-by-time panel, create site-to-zone distance matrix, document data pipeline |
| 5 | **GIS & Spatial Analysis Plan** | Select spatial units, produce hotspot/density maps, validate firehouse-to-zone matrices |
| 6 | **Input Modeling & Crash-Demand Estimation** | EDA of crash counts, estimate arrival process (NHPP), export simulation-ready lambda tables |
| 7 | **Allocation Policy Design & Scenario Library** | Define baseline + alternative policies, formulate MIP allocation, generate scenario library |
| 8 | **Conceptual Simulation Model** | Define entities, resources, queues, events, state variables, logic flow; create conceptual diagram |
| 9 | **Simulation Implementation Plan** | Build SimPy DES engine (data loaders, dispatch, queue handling, output logging) |
| 10 | **Verification & Validation Plan** | Code verification (toy examples, unit tests), validation (baseline comparison, sensitivity checks) |
| 11 | **Experimental Design & Output Analysis** | Factorial design, production runs, ANOVA, confidence intervals, CBD robustness comparison |
| 12 | **Recommendation, Documentation & Final Reporting** | Final report, presentation, reproducible code package, policy recommendation |

---

## Phases Implemented (from `final_summary.md` and `project_archive.md`)

The project was executed in **7 phases**, each completed over approximately one week:

| Phase | Description | Status | Key Deliverables | Original Sections Covered |
|-------|-------------|--------|-------------------|--------------------------|
| **Phase 1** | Data Processing & EDA | Complete | 628K Manhattan crashes, 48 firehouses, 10 EDA figures | Sections 1–5 (problem definition, scope, data, GIS) |
| **Phase 2** | Demand & Service Modeling | Complete | NHPP model (λ₀=3.48/hr), lambda tables, distance matrix | Section 6 (input modeling) |
| **Phase 3** | Optimization Models | Complete | 3 MIP formulations (Demand-Weighted, P-Median, Maximal Coverage), policy library | Section 7 (allocation policy design) |
| **Phase 4** | DES Simulation + V&V | Complete | SimPy engine (7 modules), 39 unit tests, verification log | Sections 8–10 (conceptual model, implementation, V&V) |
| **Phase 5** | Production Experiments | Complete | 1,770 runs across 5 experiments (incl. CBD robustness) | Section 11 (experimental design) |
| **Phase 6** | Statistical Analysis | Complete | ANOVA, Tukey HSD, Cohen's d, 5 pub-quality figures, 4 tables | Section 11 (output analysis) |
| **Phase 7** | Final Report & Docs | Complete | Technical report, executive presentation, implementation roadmap, archive | Section 12 (reporting & documentation) |

---

## Mapping: Original 12 Sections → Implemented 7 Phases

```
Original Outline Implementation
───────────────── ──────────────
 1. Project Purpose & Decision Problem ─┐
 2. Research Questions & MOEs ─┤
 3. Study Scope & System Boundary ─┼─► Phase 1: Data Processing & EDA
 4. Data Strategy & Engineering Plan ─┤
 5. GIS & Spatial Analysis Plan ─┘
 6. Input Modeling & Demand Estimation ───► Phase 2: Demand & Service Modeling
 7. Allocation Policy Design ───► Phase 3: Optimization Models
 8. Conceptual Simulation Model ─┐
 9. Simulation Implementation ─┼─► Phase 4: DES Simulation + V&V
10. Verification & Validation ─┘
11. Experimental Design & Output ─┬─► Phase 5: Production Experiments
 └─► Phase 6: Statistical Analysis
12. Recommendation & Reporting ───► Phase 7: Final Report & Docs
```

---

## Discrepancies & Observations

### Consolidation (not omission)
- **No original sections were dropped.** The `project_alignment_verification.md` confirms 100% coverage across all 12 outline sections.
- The 12 outline sections were **consolidated into 7 execution phases** for practical workflow efficiency.

### Key consolidations:
1. **Sections 1–5 → Phase 1**: Problem framing, scope, data acquisition, and spatial analysis were executed together as a single data-processing sprint.
2. **Sections 8–10 → Phase 4**: Conceptual modeling, implementation, and V&V were treated as one integrated simulation-development phase.
3. **Section 11 → Phases 5 + 6**: The outline's single "Experimental Design & Output Analysis" section was **split into two phases** — production runs (Phase 5) and statistical analysis (Phase 6) — giving more rigor to each.

### Additions beyond the original outline:
- **CBD Robustness Experiment** (Exp 5): 330 additional runs specifically for CBD-focused analysis — the outline mentioned CBD as a robustness check but the implementation gave it a full dedicated experiment.
- **Queue Analysis** (`queue_analysis.md`): Dedicated queueing-theory analysis not explicitly called out as a standalone deliverable in the outline.
- **Implementation Roadmap** (`implementation_roadmap.md`): A 3-phase real-world deployment plan that goes beyond the academic scope of the original outline.
- **Gap Closure Report** and **Gap Remediation Plan**: Quality-assurance documents ensuring all outline requirements were met.

---

## Final Answer

> **12 phases originally planned, 7 phases implemented** — with all 12 original sections fully covered (100% alignment verified). The reduction from 12 to 7 reflects consolidation of related activities, not omission. One original section (Experimental Design & Output Analysis) was actually expanded into two separate phases for greater rigor.
