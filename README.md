# EMS Readiness Optimization for Manhattan

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**A simulation-based approach to optimizing ambulance staging locations in Manhattan, reducing EMS response times by 68% through demand-weighted allocation.**

---

## Key Findings

| Metric | P0 (Current) | P2 (Optimized) | Improvement |
|--------|-------------|-----------------|-------------|
| Mean Response Time | 8.08 min | **2.57 min** | **−68.2%** |
| P90 Response Time | 19.47 min | **3.76 min** | **−80.7%** |
| 8-min Coverage | 64.4% | **99.6%** | **+35.2 pp** |

Results based on 1,770 simulation experiments with 30 replications each (p < 0.001, Cohen's d > 28).

---

## Project Overview

This project evaluates three ambulance allocation policies for Manhattan's 48 FDNY firehouses:

- **P0 (Uniform)**: Current practice — equal distribution across all firehouses
- **P1 (Demand-Proportional)**: Units allocated based on nearby demand
- **P2 (Demand-Weighted Optimized)**: MIP-optimized allocation minimizing expected response time

The analysis combines:
1. **NHPP Demand Modeling** — Calibrated from 2.24M historical motor vehicle collision records
2. **Mixed-Integer Programming** — Three optimization formulations (PuLP/CBC solver)
3. **Discrete-Event Simulation** — SimPy-based DES with 1,770 production runs (incl. CBD robustness)
4. **Statistical Analysis** — ANOVA, Tukey HSD, confidence intervals, effect sizes

## Repository Structure

```
ems-optimization/
├── configs/                    # YAML configuration files
│   ├── demand.yaml             # NHPP demand model parameters
│   ├── optimization.yaml       # MIP solver settings
│   ├── service.yaml            # Travel & service time config
│   ├── simulation.yaml         # DES engine settings
│   └── cbd_scenario.yaml       # CBD robustness experiment config
├── data/
│   ├── raw/                    # Original data files (NYC Open Data)
│   ├── processed/              # Cleaned & transformed data
│   └── manifests/              # Data audit records
├── docs/                       # Project documentation
│   ├── technical_report.md     # Comprehensive final report
│   ├── executive_presentation.md # Stakeholder slide deck
│   ├── implementation_roadmap.md # Deployment plan
│   ├── conceptual_model.md     # DES model specification
│   ├── optimization_formulation.md # MIP formulations
│   ├── experimental_design.md  # Factorial experiment design
│   ├── output_analysis.md      # Statistical analysis report
│   └── ...                     # Additional documentation
├── notebooks/                  # Jupyter analysis notebooks
│   ├── 02_eda_spatiotemporal.ipynb
│   ├── 03_input_modeling.ipynb
│   ├── 04_service_travel_proxy.ipynb
│   ├── 05_optimization.ipynb
│   ├── 06_simulation_debug.ipynb
│   ├── 07_production_results.ipynb
│   ├── 08_statistical_analysis.ipynb
│   └── 09_cbd_analysis.ipynb
├── results/
│   ├── figures/                # 47 visualization PNGs
│   ├── tables/                 # Statistical tables (CSV + LaTeX)
│   ├── simulation/             # Simulation output data
│   ├── optimization/           # Optimization results
│   └── maps/                   # Allocation map visualizations
├── scripts/                    # Automation & analysis scripts
├── src/ems_readiness/          # Core Python package
│   ├── demand/                 # NHPP arrival generator
│   ├── service/                # Travel time & service time models
│   ├── optimization/           # MIP formulations & allocator
│   ├── simulation/             # SimPy DES engine
│   └── utils/                  # Distance calculations
├── tests/                      # 39 unit tests (pytest)
├── requirements.txt            # Python dependencies
├── Makefile                    # Build automation
└── LICENSE                     # MIT License
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

The large raw data files are not tracked in Git. To reproduce from scratch:

1. Download from [NYC Open Data](https://data.cityofnewyork.us/):
   - Motor Vehicle Collisions — Crashes → `data/raw/Motor_Vehicle_Collisions_-_Crashes_20260223.csv`
   - Police Precincts → `data/raw/Police_Precincts_20260223.csv`

2. Process the data:
```bash
make data
# Or: python src/ems_readiness/data_processing.py
```

> **Note**: All processed data files needed for simulation and analysis are tracked in Git, so you can skip data download if you only want to run simulations.

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
```

### Run Specific Experiments

```python
from ems_readiness.simulation import EMSSimulation, BatchRunner
from ems_readiness.optimization import EMSAllocator

# Initialize allocator
allocator = EMSAllocator.from_project(".")

# Get P2 allocation for K=20 units
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
| [Technical Report](docs/technical_report.md) | Comprehensive final report with all findings |
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

## Research Questions

1. **RQ1**: How does demand for EMS services vary spatially and temporally across Manhattan?
2. **RQ2**: What is the optimal allocation of K ambulances to minimize expected response time?
3. **RQ3**: How do optimized allocations compare to the uniform baseline under realistic conditions?
4. **RQ4**: How sensitive are policy rankings to fleet size, demand intensity, and service time?
5. **RQ5**: What fleet size achieves ≥95% coverage within 8 minutes?

## Citation

```bibtex
@misc{ems_optimization_2026,
  title={EMS Readiness Optimization for Manhattan: A Simulation-Based Approach to Ambulance Staging},
  author={EMS Optimization Research Team},
  year={2026},
  howpublished={\url{https://github.com/cnsp/ems-optimization}},
  note={Version 1.1.0}
}
```

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

## Contact

- **Repository**: [github.com/cnsp/ems-optimization](https://github.com/cnsp/ems-optimization)
- **Issues**: [GitHub Issues](https://github.com/cnsp/ems-optimization/issues)

---

*Built with Python, SimPy, PuLP, pandas, and matplotlib. 7,500+ lines of code across 14 modules, validated with 39 tests and 1,770 simulation experiments. 100% alignment with project outline (v1.1.0).*
