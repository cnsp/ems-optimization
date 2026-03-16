# Notebook Guide

> Purpose, scope, and recommended usage for the Jupyter notebooks in `notebooks/`.

---

## Overview

The eight notebooks in this project are **exploratory and analytical companions** to the production pipeline, not standalone end-to-end runners. They were created during development to prototype analysis, visualize intermediate results, and document findings for each project phase. The production workflow is driven by the scripts in `scripts/` and the `src/ems_readiness` package.

**Bottom line:** Use `scripts/` to reproduce results. Use `notebooks/` to understand, explore, and present them.

---

## Notebook Inventory

| Notebook | Phase | Purpose | Standalone? |
|----------|-------|---------|-------------|
| `02_eda_spatiotemporal` | 1 — EDA | Spatiotemporal analysis of crash demand patterns; generates hourly/daily/seasonal figures | Yes (reads raw data directly) |
| `03_input_modeling` | 2 — Demand | Documents NHPP demand model fitting, lambda tables, goodness-of-fit | Partially (reads processed data) |
| `04_service_travel_proxy` | 2 — Service | Demonstrates distance matrix, travel-time proxy, service-time distribution, arrival generator | No (imports `ems_readiness` package) |
| `05_optimization` | 3 — Optimization | Documents optimization formulations and policy comparison results | Partially (reads results CSVs) |
| `06_simulation_debug` | 4 — Simulation | Verification and validation of the DES engine (toy examples, pilots) | No (imports `ems_readiness` package) |
| `07_production_results` | 5 — Results | Analyzes 1,440 production simulation runs across four experiment sets | Partially (reads results CSVs) |
| `08_statistical_analysis` | 6 — Statistics | Full statistical analysis: ANOVA, Tukey HSD, effect sizes, confidence intervals | Partially (reads results CSVs) |
| `09_cbd_analysis` | Robustness | CBD-focused optimization and distance-metric comparison | Partially (reads results CSVs) |

### "Standalone?" column explained

- **Yes**: The notebook reads raw data and can run independently given the raw data files.
- **Partially**: The notebook reads pre-computed results (CSVs from `data/processed/` or `results/`). It can run if those files exist, but does not regenerate them — that is the job of `scripts/`.
- **No**: The notebook imports `ems_readiness` as a library (via `sys.path` injection) and depends on the installed or path-accessible package.

---

## Relationship to `scripts/`

```
scripts/                          notebooks/
─────────────────────────────     ──────────────────────────────
data_audit.py                  -> 02_eda_spatiotemporal.ipynb
demand_modeling.py             -> 03_input_modeling.ipynb
(package modules)              -> 04_service_travel_proxy.ipynb
run_optimization_comparison.py -> 05_optimization.ipynb
run_verification.py            -> 06_simulation_debug.ipynb
run_validation_pilots.py
run_production_experiments.py  -> 07_production_results.ipynb
run_production_v2.py
analyze_production_results.py  -> 08_statistical_analysis.ipynb
run_cbd_experiment.py          -> 09_cbd_analysis.ipynb
run_cbd_focused_optimization.py
```

**Key points:**

- Scripts generate data and results; notebooks visualize and analyze them.
- Scripts are the authoritative, reproducible pipeline. Notebooks may contain exploratory code that was later formalized into scripts.
- Four notebooks (`05`, `06`, `07`, `08`) have paired `.py` files in `notebooks/` — these are Jupytext percent-format scripts used for version control of the notebook content.
- No notebook calls a script via `subprocess`. The `08_statistical_analysis` notebook references script paths in documentation but loads results files directly.

---

## Recommended Workflow

### To reproduce all results from scratch

```bash
# 1. Process raw data
make data

# 2. Run the full analysis pipeline
make analysis

# 3. Or run individual scripts
python scripts/run_optimization_comparison.py
python scripts/run_production_v2.py
python scripts/analyze_production_results.py
```

### To explore or present results

Open notebooks in JupyterLab after running the production scripts:

```bash
jupyter lab notebooks/
```

Notebooks assume results files already exist in `data/processed/` and `results/`.

### To modify the simulation or optimization

1. Edit source code in `src/ems_readiness/`
2. Re-run the appropriate script in `scripts/`
3. Open the corresponding notebook to visualize updated results

---

## Jupytext `.py` Files

The `.py` files in `notebooks/` (e.g., `05_optimization.py`) are **Jupytext percent-format** mirrors of the corresponding `.ipynb` files. They exist for cleaner version control (diffs on `.py` are more readable than on `.ipynb` JSON). These are not independent scripts — they are an alternative representation of the same notebook content.

---

## Maintenance Status

All notebooks reflect the final project state (current version with spatially-stratified P0, capacity=2 default, CBD robustness analysis). They are maintained as documentation and presentation artifacts. For any future model changes, update the scripts first, re-run experiments, then refresh notebook outputs.
