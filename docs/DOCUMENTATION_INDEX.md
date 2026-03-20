---
status: ✅ CURRENT
last_updated: "2026-03-20"
verified: "Master index of all 62 documentation files"
---
# Documentation Index — EMS Readiness Optimization

> **How to use this index:** Each document has a status badge. Use ✅ CURRENT docs for active reference. 🔄 HISTORICAL docs are preserved for project history and contain old metrics in context — don't use them as current reference. 📋 REFERENCE docs are specialized analyses that should be cross-referenced with production results.

---

## Quick Navigation

| If you need... | Read this |
|----------------|-----------|
| **Project overview** | [`technical_report.md`](technical_report.md) or [`executive_summary.md`](executive_summary.md) |
| **Which results files to use** | [`data_usage_guide.md`](data_usage_guide.md) |
| **How to reproduce results** | [`reproducibility_guide.md`](reproducibility_guide.md) |
| **Current metrics & numbers** | [`optimization_results.md`](optimization_results.md) |
| **Math formulations** | [`optimization_formulation.md`](optimization_formulation.md) |
| **Why P0 changed** | [`nomenclature_migration.md`](nomenclature_migration.md) (🔄 historical) |
| **Why capacity=2** | [`capacity_sensitivity_analysis.md`](capacity_sensitivity_analysis.md) |
| **All project decisions** | [`decisions_log.md`](decisions_log.md) |
| **Notebook execution order** | [`notebook_guide.md`](notebook_guide.md) |
| **Figure traceability** | [`figure_trace_guide.md`](figure_trace_guide.md) |
| **Run tests** | [`testing_guide.md`](testing_guide.md) |

---

## ✅ CURRENT — Safe to Reference (34 docs)

### Core Project Documentation
| Document | Description |
|----------|-------------|
| [`project_charter.md`](project_charter.md) | Project scope, objectives, and problem statement |
| [`assumptions_log.md`](assumptions_log.md) | All project assumptions with justification and risks |
| [`decisions_log.md`](decisions_log.md) | Key decision records (DEC-001 through DEC-012) |
| [`blocker_log.md`](blocker_log.md) | Obstacle tracking log |
| [`source_manifest.md`](source_manifest.md) | Data source inventory and descriptions |

### Model Specifications
| Document | Description |
|----------|-------------|
| [`conceptual_model.md`](conceptual_model.md) | Full conceptual model: entities, processes, assumptions |
| [`conceptual_model_selection.md`](conceptual_model_selection.md) | Rationale for DES + MIP hybrid approach |
| [`demand_model_spec.md`](demand_model_spec.md) | NHPP demand model specification |
| [`service_model_spec.md`](service_model_spec.md) | Travel-time proxy and service-time distribution specs |
| [`optimization_formulation.md`](optimization_formulation.md) | Mathematical formulations for P0/P1/P2 policies |

### Experimental Design & Results
| Document | Description |
|----------|-------------|
| [`experimental_design.md`](experimental_design.md) | Experimental design: 5 experiment sets, 2,400 runs |
| [`optimization_results.md`](optimization_results.md) | Optimization results summary (cap=2, current P0) |
| [`capacity_sensitivity_analysis.md`](capacity_sensitivity_analysis.md) | Full-spectrum capacity sensitivity (cap 1–5) |
| [`cbd_robustness_analysis.md`](cbd_robustness_analysis.md) | CBD robustness analysis with current metrics |
| [`cbd_comparison_and_validity_report.md`](cbd_comparison_and_validity_report.md) | CBD comparison and model validity |
| [`cbd_definition.md`](cbd_definition.md) | CBD geographic boundary definition |
| [`distance_metric_comparison.md`](distance_metric_comparison.md) | Haversine vs Manhattan distance analysis |
| [`queue_analysis.md`](queue_analysis.md) | Queue analysis confirming zero waiting |

### Reports & Summaries
| Document | Description |
|----------|-------------|
| [`technical_report.md`](technical_report.md) | Full technical report (journal-style, ~600 lines) |
| [`executive_summary.md`](executive_summary.md) | One-page executive summary |
| [`executive_presentation.md`](executive_presentation.md) | Slide-style executive presentation |
| [`final_summary.md`](final_summary.md) | Comprehensive project final summary |
| [`research_questions_assessment.md`](research_questions_assessment.md) | Assessment against original research questions |
| [`project_alignment_verification.md`](project_alignment_verification.md) | Alignment verification with project outline |

### Guides & References
| Document | Description |
|----------|-------------|
| [`data_usage_guide.md`](data_usage_guide.md) | Which data/results files to use and why |
| [`notebook_guide.md`](notebook_guide.md) | Notebook descriptions and execution order |
| [`reproducibility_guide.md`](reproducibility_guide.md) | How to reproduce all results |
| [`testing_guide.md`](testing_guide.md) | Testing framework and how to run tests |
| [`code_documentation.md`](code_documentation.md) | Code architecture and module documentation |
| [`figure_trace_guide.md`](figure_trace_guide.md) | Figure-to-source traceability guide |
| [`visualization_index.md`](visualization_index.md) | Index of all project visualizations |

### Engineering & Quality
| Document | Description |
|----------|-------------|
| [`engineering_hygiene_summary.md`](engineering_hygiene_summary.md) | Engineering quality practices summary |
| [`project_workflow_wbs.md`](project_workflow_wbs.md) | Work breakdown structure |
| [`implementation_roadmap.md`](implementation_roadmap.md) | 12-month implementation roadmap |

---

## 🔄 HISTORICAL — Preserved for Project History (18 docs)

> ⚠️ These documents contain old metrics (e.g., P0 = 8.08 min, capacity = 5) **in historical context**. They document what changed and why. Do **not** use them as current reference for metrics or code behavior.

### Policy & Nomenclature History
| Document | Description |
|----------|-------------|
| [`nomenclature_migration.md`](nomenclature_migration.md) | P0 nomenclature migration history (old→new P0) |
| [`historical_data_policy.md`](historical_data_policy.md) | Policy for handling historical vs current data |
| [`policy_tradeoff_analysis.md`](policy_tradeoff_analysis.md) | Trade-off analysis using ORIGINAL index-based P0 (deprecated) |
| [`firehouse_capacity_analysis.md`](firehouse_capacity_analysis.md) | Pre-DEC-010 capacity analysis (cap=5 era) |

### Audit & Migration Records
| Document | Description |
|----------|-------------|
| [`documentation_audit_report.md`](documentation_audit_report.md) | Record of documentation audit and fixes applied |
| [`notebook_audit_report.md`](notebook_audit_report.md) | Record of notebook audit and fixes applied |
| [`project_wide_audit_report.md`](project_wide_audit_report.md) | Comprehensive project-wide audit record |
| [`honest_audit_assessment.md`](honest_audit_assessment.md) | Honest assessment of project state |
| [`gap_analysis_report.md`](gap_analysis_report.md) | Gap analysis and identified issues |
| [`gap_closure_report.md`](gap_closure_report.md) | Gap closure progress report |
| [`gap_remediation_plan.md`](gap_remediation_plan.md) | Remediation plan for identified gaps |
| [`fix_summary_4_issues.md`](fix_summary_4_issues.md) | Summary of 4 critical fixes (cap=5→2, etc.) |
| [`filename_mismatch_fix_report.md`](filename_mismatch_fix_report.md) | Filename mismatch fixes |
| [`output_comparison_report.md`](output_comparison_report.md) | Before/after comparison of regenerated outputs |
| [`migration_plan.md`](migration_plan.md) | Data and results migration plan |

### Phase History
| Document | Description |
|----------|-------------|
| [`phase_comparison_summary.md`](phase_comparison_summary.md) | Phase-by-phase comparison summary |
| [`phase21_assessment.md`](phase21_assessment.md) | Phase 2.1 assessment |
| [`final_status.md`](final_status.md) | Status snapshot at a point in time |

---

## 📋 REFERENCE — Specialized Analysis (10 docs)

> These are supplementary analysis documents. They are current but specialized — cross-reference with production results in `results/production_v2/`.

### Specialized Analysis
| Document | Description |
|----------|-------------|
| [`alternative_analyses_summary.md`](alternative_analyses_summary.md) | Summary of CBD/distance alternative analyses |
| [`analysis_precinct_demand_trace.md`](analysis_precinct_demand_trace.md) | Precinct-level demand analysis trace |
| [`cbd_focused_optimization_analysis.md`](cbd_focused_optimization_analysis.md) | CBD-focused optimization deep-dive |
| [`fleet_sensitivity_dual_investigation.md`](fleet_sensitivity_dual_investigation.md) | Fleet sensitivity dual investigation |
| [`output_analysis.md`](output_analysis.md) | Output analysis methodology |
| [`eda_and_data_split_summary.md`](eda_and_data_split_summary.md) | EDA and data split summary |
| [`verification_log.md`](verification_log.md) | V&V verification log |

### Project Management
| Document | Description |
|----------|-------------|
| [`data_dependency_analysis.md`](data_dependency_analysis.md) | Data dependency and lineage analysis |
| [`file_inventory.md`](file_inventory.md) | Complete file inventory |
| [`project_archive.md`](project_archive.md) | Project archive structure |

---

## PDF Versions

Most `.md` files have corresponding `.pdf` versions (60 PDFs total). PDFs are auto-generated from Markdown and share the same status as their source `.md` file.

---

## Current Key Metrics (for reference)

| Metric | Value | Source |
|--------|-------|--------|
| P0 mean RT (K=20) | 3.17 min | Spatially-stratified baseline |
| P2 mean RT (K=20) | 2.57 min | Demand-weighted MIP |
| 8-min coverage (P2, K=20) | 99.6% | Production simulation |
| Default capacity | 2 units/firehouse | DEC-010 |
| P0 nomenclature | Spatially-stratified | DEC-011/DEC-012 |
| Total production runs | 2,400 | 5 experiment sets × 30 replications |

---

*Last audited: March 20, 2026 — 62 .md files, 60 .pdf files*
