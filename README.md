# EMS Readiness Optimization for Manhattan

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**A simulation-based approach to optimizing ambulance staging locations in Manhattan, reducing EMS response times by 19% over a spatially-stratified baseline through demand-weighted allocation with capacity=2 constraints.**

---

## Key Findings

| Metric | P0 (Baseline) | P2 (Optimized) | Improvement |
|--------|----------------------|-----------------|-------------|
| Mean Response Time | 3.17 min | **2.57 min** | **−19.0%** |
| P95 Response Time | 6.26 min | **4.66 min** | **−25.6%** |
| 8-min Coverage | 99.6% | **99.6%** | +0.0 pp |
| Mean Utilization | 7.6% | 7.5% | −0.1 pp |

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
├── docs/ # Project documentation (32+ files)
│ ├── technical_report.md # Full final report (v2.1.0)
│ ├── executive_presentation.md # Stakeholder slide deck
│ ├── implementation_roadmap.md # Deployment plan
│ ├── conceptual_model.md # DES model specification
│ ├── optimization_formulation.md # MIP formulations
│ ├── experimental_design.md # Factorial experiment design
│ ├── output_analysis.md # Statistical analysis report
│ ├── capacity_sensitivity_analysis.md # Cap 1–5 sensitivity report
│ ├── firehouse_capacity_analysis.md # Capacity methodology
│ └── ... # Additional documentation
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
│ ├── figures/ # 66+ visualization PNGs
│ ├── tables/ # Statistical tables (CSV + LaTeX)
│ ├── simulation/ # Simulation output data
│ ├── optimization/ # Optimization results
│ ├── distance_comparison/ # Haversine vs Manhattan metric results
│ ├── cbd_focused_comparison/ # CBD-focused vs Manhattan-wide results
│ ├── capacity_comparison/ # Capacity sensitivity (cap 1–5) results
│ ├── production_v2/ # Extended fleet analysis results (cap=2)
│ └── maps/ # Allocation map visualizations
├── scripts/ # Automation & analysis scripts (23+)
├── src/ems_readiness/ # Core Python package (v0.6.0)
│ ├── demand/ # NHPP arrival generator
│ ├── service/ # Travel time & service time models
│ ├── optimization/ # MIP formulations, policies & allocator
│ ├── simulation/ # SimPy DES engine
│ └── utils/ # Distance calculations
├── tests/ # 39 unit tests (pytest)
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

Raw data files and all processed/intermediate data are **not** tracked in Git. The pipeline regenerates everything from raw inputs.

1. Download large files from [NYC Open Data](https://data.cityofnewyork.us/):
   - Motor Vehicle Collisions — Crashes → `data/raw/Motor_Vehicle_Collisions_-_Crashes_20260223.csv`
   - Police Precincts → `data/raw/Police_Precincts_20260223.csv`

   **Automated download** (crash data only):
   ```bash
   python scripts/download_crash_data.py
   # Or with a row limit for testing: python scripts/download_crash_data.py --limit 500000
   ```

   See [`data/raw/README.md`](data/raw/README.md) for manual download links and verification instructions.

   > **Note:** The Colab notebooks automatically download and process crash data on first run.

2. Generate all processed data (single command):
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
python scripts/run_production_experiments.py

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
# Run all 39 tests
pytest tests/ -v

# Run specific test modules
pytest tests/test_simulation_core.py -v
pytest tests/test_dispatch_logic.py -v
pytest tests/test_extreme_cases.py -v
pytest tests/test_reproducibility.py -v
```

## Documentation Index

| Document | Description |
|----------|-------------|
| [Technical Report](docs/technical_report.md) | Full final report (v2.1.0) with all findings |
| [Executive Presentation](docs/executive_presentation.md) | 10-slide stakeholder presentation |
| [Implementation Roadmap](docs/implementation_roadmap.md) | Phased deployment plan |
| [Conceptual Model](docs/conceptual_model.md) | DES model specification |
| [Optimization Formulation](docs/optimization_formulation.md) | MIP mathematical formulations |
| [Experimental Design](docs/experimental_design.md) | Factorial experiment specification |
| [Output Analysis](docs/output_analysis.md) | Statistical analysis report |
| [Verification Log](docs/verification_log.md) | V&V test results |
| [Code Documentation](docs/code_documentation.md) | Architecture and API guide |
| [File Inventory](docs/file_inventory.md) | Complete project file listing |
| [Project Archive](docs/project_archive.md) | Timeline and lessons learned |
| [CBD Robustness Analysis](docs/cbd_robustness_analysis.md) | CBD-specific DES experiment findings |
| [Queue Analysis](docs/queue_analysis.md) | Queueing performance analysis |
| [Gap Closure Report](docs/gap_closure_report.md) | Verification of 100% alignment |
| [Distance Metric Comparison](docs/distance_metric_comparison.md) | Haversine vs. Manhattan distance analysis |
| [CBD-Focused Optimization](docs/cbd_focused_optimization_analysis.md) | CBD-focused vs. Manhattan-wide comparison |
| [Alternative Analyses Summary](docs/alternative_analyses_summary.md) | Combined Phase 8 alternative analyses |
| [Capacity Sensitivity Analysis](docs/capacity_sensitivity_analysis.md) | Full-spectrum capacity (cap 1–5) analysis |
| [Firehouse Capacity Analysis](docs/firehouse_capacity_analysis.md) | Capacity methodology and initial findings |
| [Research Questions Assessment](docs/research_questions_assessment.md) | Evaluation of all 5 research questions with simulation evidence |
| [Work Breakdown Structure](docs/project_workflow_wbs.md) | Complete WBS across all 9 phases |
| [Conceptual Model Selection](docs/conceptual_model_selection.md) | Analysis of all conceptual models considered, implemented, and deferred |
| [Figure Trace Guide](docs/figure_trace_guide.md) | Data lineage and downstream usage for every project figure |
| [Visualization Index](docs/visualization_index.md) | Complete catalog of all ~60 generated figures with generation scripts |
| [Notebook Guide](docs/notebook_guide.md) | Purpose, scope, and usage guide for Jupyter notebooks |

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