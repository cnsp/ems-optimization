# EMS Readiness Optimization for Manhattan

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**A simulation-based approach to optimizing ambulance staging locations in Manhattan, reducing EMS response times by 19% over a spatially-stratified baseline through demand-weighted allocation with capacity=2 constraints.**

---

## Key Findings

| Metric | P0 (Baseline) | P2 (Optimized) | Improvement |
|--------|----------------------|-----------------|-------------|
| Mean Response Time | 3.17 min | **2.57 min** | **−18.9%** |
| P95 Response Time | 6.26 min | **4.66 min** | **−25.6%** |
| 8-min Coverage | 99.7% | **99.7%** | +0.0 pp |
| Mean Utilization | 7.6% | 7.4% | −0.2 pp |

Results based on 2,700+ simulation experiments with 30 replications each (p < 0.001).
Capacity sensitivity analysis (cap 1–5) confirms cap=2 as operationally optimal default.
Alternative analyses confirm stability under distance metric choice and geographic focus.

---

## Project Overview

This project evaluates three ambulance allocation policies for Manhattan's 48 FDNY firehouses:

- **P0 (Spatially-Stratified Uniform)**: Latitude-based geographic stratification providing even north–south coverage
- **P1 (Demand-Proportional)**: Units allocated based on nearby demand
- **P2 (Demand-Weighted Optimized)**: MIP-optimized allocation minimizing expected response time

The analysis combines:
1. **NHPP Demand Modeling** — Calibrated from 2.24M historical motor vehicle collision records
2. **Mixed-Integer Programming** — Three optimization formulations with capacity=2 constraint (PuLP/CBC solver)
3. **Discrete-Event Simulation** — SimPy-based DES with 2,700+ production runs across 9 experiment sets
4. **Statistical Analysis** — ANOVA, Tukey HSD, confidence intervals, effect sizes
5. **Capacity Sensitivity Analysis** — Full spectrum (cap 1–5) across 9 fleet sizes
6. **Alternative Analyses** — Manhattan distance metric comparison + CBD-focused optimization evaluation

## Start Here

If you're new to the project:

1. Read the [Technical Report](docs/core/technical_report.md)
2. Run the baseline pipeline:
   ```bash
   python scripts/run_production_v2.py
   ```
3. View canonical outputs in: `results/baseline/`

For supporting analyses, see:
- `results/analysis/`
- `docs/analysis/`

## Repository Architecture

The repository is organized to eliminate ambiguity:

**Results:**
- **Baseline** → canonical results (`results/baseline/`)
- **Analysis** → robustness & sensitivity (`results/analysis/`)
- **Archive** → historical artifacts (`results/archive/`)

**Scripts:**
- **Scripts (root)** → production entry points
- **scripts/analysis/** → supporting analyses
- **scripts/archive/** → legacy utilities

**Documentation:**
- **docs/core/** → primary documentation
- **docs/analysis/** → supporting analyses
- **docs/archive/** → historical records

## Repository Structure

```
ems-optimization/
├── configs/ # YAML configuration files
│ ├── demand.yaml # NHPP demand model parameters
│ ├── optimization.yaml # MIP solver settings (capacity=2 default)
│ ├── service.yaml # Travel & service time config
│ ├── simulation.yaml # DES engine settings
│ └── cbd_scenario.yaml # CBD robustness experiment config
├── data/
│ ├── raw/ # Original data files (NYC Open Data)
│ ├── processed/ # Generated data (not in Git — run `make data`)
│ └── manifests/ # Data audit records
├── docs/ # Project documentation (62+ .md files, see docs/core/DOCUMENTATION_INDEX.md)
│ ├── core/ # Key deliverables, specs, guides
│ │ ├── technical_report.md # Full final report (v2.1.0)
│ │ ├── executive_presentation.md # Stakeholder slide deck
│ │ └── ... # Additional core docs
│ ├── analysis/ # Robustness & sensitivity analyses
│ │ ├── capacity_sensitivity_analysis.md
│ │ └── ... # Additional analysis docs
│ └── archive/ # Historical/superseded docs
├── notebooks/ # Jupyter analysis notebooks
│ ├── 02_eda_spatiotemporal.ipynb
│ ├── 03_input_modeling.ipynb
│ ├── 04_service_travel_proxy.ipynb
│ ├── 05_optimization.ipynb
│ ├── 06_simulation_debug.ipynb
│ ├── 07_production_results.ipynb
│ ├── 08_statistical_analysis.ipynb
│ ├── 09_cbd_analysis.ipynb
│ └── colab_standalone/ # Google Colab standalone notebooks
│     ├── individual/ # 8 phase notebooks (00–07)
│     ├── EMS_Optimization_Complete_Pipeline.ipynb
│     └── README.md
├── results/
│ ├── baseline/ # Canonical production results (cap=2)
│ │ ├── allocations/ # Policy allocation CSVs
│ │ ├── figures/ # Publication-ready figures
│ │ ├── simulation/ # Verification & validation output
│ │ └── tables/ # Statistical summary tables
│ ├── analysis/ # Supporting robustness & sensitivity
│ │ ├── capacity_comparison/ # Capacity sensitivity (cap 1–5) results
│ │ ├── cbd_focused_comparison/ # CBD-focused vs Manhattan-wide results
│ │ ├── distance_comparison/ # Haversine vs Manhattan metric results
│ │ ├── heatmaps/ # Allocation heatmaps (K × cap × policy)
│ │ ├── maps/ # Allocation map visualizations
│ │ ├── simulation/ # CBD & production DES output
│ │ └── tables/ # Analysis summary tables
│ ├── archive/ # Legacy/historical artifacts (cap=5 era)
│ │ ├── figures/ # Superseded figures
│ │ ├── optimization/ # Phase 3 historical optimization results
│ │ └── tables/ # Superseded tables
│ ├── figures/ # Top-level visualization PNGs
│ ├── tables/ # Top-level statistical tables (CSV + LaTeX)
│ └── simulation/ # Top-level simulation output data
├── scripts/ # Automation & analysis scripts (23+)
├── src/ems_readiness/ # Core Python package (v0.6.0)
│ ├── demand/ # NHPP arrival generator
│ ├── service/ # Travel time & service time models
│ ├── optimization/ # MIP formulations, policies & allocator
│ ├── simulation/ # SimPy DES engine
│ └── utils/ # Distance calculations
├── tests/ # 176 unit tests (pytest)
├── requirements.txt # Python dependencies
├── Makefile # Build automation
└── LICENSE # MIT License
```

## Installation & Setup

### Prerequisites
- Python 3.11+
- pip

### Quick Start

```bash
# Clone the repository
git clone https://github.com/cnsp/ems-optimization.git
cd ems-optimization

# Create virtual environment and install dependencies
make setup
# Or manually:
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install project package in development mode
pip install -e .
```

### Data Setup

Large raw data files are tracked via **Git LFS**. Ensure Git LFS is installed before cloning:

```bash
git lfs install   # one-time setup
git clone https://github.com/cnsp/ems-optimization.git
```

The following files are pulled automatically via LFS on clone:
- `data/raw/Motor_Vehicle_Collisions_-_Crashes_20260223.csv` (536 MB)
- `data/raw/Police_Precincts_20260223.csv` (3.6 MB)

All other raw files (boundary GeoJSONs, firehouse listings, data dictionaries) and key processed
files (distance matrices, demand lambdas, firehouse lists) are tracked directly in Git.

If LFS files were not pulled (e.g., shallow clone), run:
```bash
git lfs pull
```

See [`data/raw/README.md`](data/raw/README.md) for original NYC Open Data download links.

> **Note:** The Colab notebooks (`notebooks/colab_standalone/`) include self-contained data
> processing cells that generate `crashes_manhattan.csv` from the raw crash CSV on first run.
> All other processed files are tracked in Git and require no extra setup.

Generate all processed data (single command):
```bash
make data
# Or: python scripts/generate_all_data.py
```

3. Verify data:
```bash
make verify-data
```

#### Pipeline CLI Options

The data pipeline (`scripts/generate_all_data.py`) supports several options:

| Flag | Description |
|------|-------------|
| `--force` | Regenerate all files even if they exist |
| `--no-validate` | Skip raw data validation checks |
| `--no-cache` | Disable smart caching |
| `--jobs N` / `-j N` | Parallel workers (0 = auto-detect CPU count) |
| `--tier {1,2,3}` | Run only a specific tier |
| `--version` | Show current data version info |
| `--seed N` | Master seed for reproducibility (default: 42) |
| `--verify` | Check data existence without generating |

```bash
# Force-regenerate with 4 parallel workers
python scripts/generate_all_data.py --force --jobs 4

# Show data version/lineage info
python scripts/generate_all_data.py --version

# Skip validation (faster startup)
python scripts/generate_all_data.py --no-validate
```

> **Note**: Notebooks auto-detect and regenerate missing processed data on first run, so you can also just open any notebook and it will trigger the pipeline if needed.

## How to Reproduce Results

### Run the Full Pipeline

```bash
# 1. Process data (if raw data available)
make data

# 2. Run optimization comparison
python scripts/run_optimization_comparison.py

# 3. Run simulation verification
python scripts/run_verification.py

# 4. Run validation pilots
python scripts/run_validation_pilots.py

# 5. Run production experiments (1,440 simulations — takes ~2-4 hours)
python scripts/run_production_v2.py

# 6. Analyze results and generate figures
python scripts/analyze_production_results.py
python scripts/generate_publication_figures.py

# 7. Run CBD robustness experiment (330 simulations)
python scripts/run_cbd_experiment.py --reps 30

# 8. Run gap closure analyses
python scripts/analyze_queue_metrics.py
python scripts/analyze_seasonal_patterns.py

# 9. Run alternative analyses (Phase 8)
python scripts/generate_manhattan_distance_matrix.py
python scripts/run_distance_comparison_experiment.py --reps 10
python scripts/run_cbd_focused_optimization.py --reps 10

# 10. Run capacity sensitivity analysis (Phase 9)
python scripts/capacity_sensitivity_full_spectrum.py

# 11. Run P0 spatial stratification analysis
python scripts/p0_spatial_analysis.py

# 12. Run extended fleet analysis experiments (810 simulations — cap=2)
python scripts/run_production_v2.py
```

### Run Specific Experiments

```python
from ems_readiness.simulation import EMSSimulation, BatchRunner
from ems_readiness.optimization import EMSAllocator

# Initialize allocator
allocator = EMSAllocator.from_project(".")

# Get P2 allocation for K=20 units (capacity=2 default)
result = allocator.solve(model="demand_weighted", K=20)
print(result.allocation)

# Run simulation
sim = EMSSimulation.from_config("configs/simulation.yaml", allocation=result.allocation)
metrics = sim.run(duration_hours=168)
print(f"Mean RT: {metrics['mean_response_time']:.2f} min")
```

## How to Run Tests

```bash
# Run all 176 tests
pytest tests/ -v

# Run specific test modules
pytest tests/test_simulation_core.py -v
pytest tests/test_dispatch_logic.py -v
pytest tests/test_extreme_cases.py -v
pytest tests/test_reproducibility.py -v
```

## Documentation Index

> 📖 **Full index:** [`docs/core/DOCUMENTATION_INDEX.md`](docs/core/DOCUMENTATION_INDEX.md) — master list of all 62 docs with status badges (✅ Current / 🔄 Historical / 📋 Reference)

### Key Documents

| Document | Description |
|----------|-------------|
| [Technical Report](docs/core/technical_report.md) | Full final report (v2.1.0) with all findings |
| [Executive Summary](docs/core/executive_summary.md) | One-page executive summary |
| [Executive Presentation](docs/core/executive_presentation.md) | 10-slide stakeholder presentation |
| [Data Usage Guide](docs/core/data_usage_guide.md) | Which data/results files to use and why |
| [Reproducibility Guide](docs/core/reproducibility_guide.md) | How to reproduce all results |

### Model & Methods

| Document | Description |
|----------|-------------|
| [Conceptual Model](docs/core/conceptual_model.md) | DES model specification |
| [Optimization Formulation](docs/core/optimization_formulation.md) | MIP mathematical formulations |
| [Experimental Design](docs/core/experimental_design.md) | Factorial experiment specification |
| [Optimization Results](docs/analysis/optimization_results.md) | Current optimization results (cap=2) |

### Analysis & Robustness

| Document | Description |
|----------|-------------|
| [Capacity Sensitivity](docs/analysis/capacity_sensitivity_analysis.md) | Full-spectrum capacity (cap 1–5) analysis |
| [CBD Robustness](docs/analysis/cbd_robustness_analysis.md) | CBD-specific DES experiment findings |
| [Distance Metric Comparison](docs/analysis/distance_metric_comparison.md) | Haversine vs. Manhattan distance analysis |
| [Research Questions](docs/analysis/research_questions_assessment.md) | Evaluation of all 5 research questions |

### Guides

| Document | Description |
|----------|-------------|
| [Code Documentation](docs/core/code_documentation.md) | Architecture and API guide |
| [Notebook Guide](docs/core/notebook_guide.md) | Notebook descriptions and execution order |
| [Testing Guide](docs/core/testing_guide.md) | Testing framework and how to run tests |
| [Figure Trace Guide](docs/core/figure_trace_guide.md) | Figure-to-source traceability |
| [Visualization Index](docs/core/visualization_index.md) | Complete catalog of all generated figures |

## Navigating Results

The `results/` folder contains output from multiple project phases. Each subfolder has its own `README.md` explaining what's there and whether it's current or legacy.

| Folder | Label | Status | What's Inside |
|--------|-------|--------|---------------|
| `results/baseline/` | Canonical | ✅ Current | Production allocations, figures, simulation verification/validation, tables |
| `results/baseline/simulation/` | Canonical | ✅ Current | Verification tests, validation pilots |
| `results/analysis/` | Supporting | ✅ Current | All robustness & sensitivity analyses |
| `results/analysis/capacity_comparison/` | Supporting | ✅ Current | Full capacity sweep (cap 1–5) |
| `results/analysis/cbd_focused_comparison/` | Supporting | ✅ Current | CBD-focused optimization experiment |
| `results/analysis/distance_comparison/` | Supporting | ✅ Current | Manhattan vs Haversine comparison |
| `results/analysis/heatmaps/` | Supporting | ✅ Current | Allocation heatmaps across K × cap × policy |
| `results/analysis/maps/` | Supporting | ✅ Current | Allocation maps at K=40 |
| `results/archive/` | Legacy | ⚠️ Historical | Phase 3 historical artifacts (cap=5 era) |
| `results/archive/optimization/` | Legacy | ⚠️ Historical | Superseded optimization results |
| `results/figures/` | — | ✅ Mostly Current | Publication figures (`pub_fig*`) + technical plots |
| `results/tables/` | — | ✅ Mostly Current | Publication tables + experiment pivots ([see README](results/tables/README.md)) |
| `results/simulation/` | — | ✅ Current | Top-level simulation output data |

**Quick reference**: [`results/WHICH_FILES_TO_USE.md`](results/WHICH_FILES_TO_USE.md)  
**Full guide**: [`docs/core/data_usage_guide.md`](docs/core/data_usage_guide.md)

## Google Colab Notebooks

For external verification and reproduction, standalone Google Colab notebooks are available in `notebooks/colab_standalone/`. These require no local setup — just open in Colab and run.

| Notebook | Phase | Runtime |
|----------|-------|---------|
| `00_colab_setup_and_data` | Environment setup, data verification | ~2 min |
| `01_colab_eda_spatiotemporal` | Exploratory data analysis | ~5 min |
| `02_colab_demand_modeling` | NHPP demand model | ~5 min |
| `03_colab_service_modeling` | Travel/service time models | ~3 min |
| `04_colab_optimization` | P0/P1/P2 allocation policies | ~5 min |
| `05_colab_simulation` | SimPy DES (demo or full-scale) | 5 min – 8 hr |
| `06_colab_statistical_analysis` | ANOVA, effect sizes, CIs | ~3 min |
| `07_colab_visualization_reporting` | Publication figures, summary report | ~3 min |
| **All-in-One Pipeline** | Complete end-to-end analysis | 5–10 hr |

See [`notebooks/colab_standalone/README.md`](notebooks/colab_standalone/README.md) for detailed instructions.

## Research Questions

1. **RQ1**: How does demand for EMS services vary spatially and temporally across Manhattan?
2. **RQ2**: What is the optimal allocation of K ambulances to minimize expected response time?
3. **RQ3**: How do optimized allocations compare to the spatially-stratified uniform baseline under realistic conditions?
4. **RQ4**: How sensitive are policy rankings to fleet size, demand intensity, service time, and firehouse capacity?
5. **RQ5**: What fleet size achieves ≥95% coverage within 8 minutes?

## Citation

```bibtex
@misc{ems_optimization_2026,
 title={EMS Readiness Optimization for Manhattan: A Simulation-Based Approach to Ambulance Staging},
 author={EMS Optimization Research Team},
 year={2026},
 howpublished={\url{https://github.com/cnsp/ems-optimization}},
 note={Version 1.3.0}
}
```

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

## Contact

- **Repository**: [github.com/cnsp/ems-optimization](https://github.com/cnsp/ems-optimization)
- **Issues**: [GitHub Issues](https://github.com/cnsp/ems-optimization/issues)

---

*Built with Python, SimPy, PuLP, pandas, and matplotlib. 8,500+ lines of code across 14 modules, tested with 176 unit tests and 2,700+ simulation experiments. Covers capacity sensitivity (cap 1–5), spatially-stratified P0 baseline, and alternative distance metric and CBD-focused optimization analyses.*