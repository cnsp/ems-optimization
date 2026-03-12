# EMS Readiness Optimization

**Strategic Firehouse-Based EMS Staging Under Stochastic Crash Demand in Manhattan**

## Overview

This project implements a discrete-event simulation study to determine whether optimized EMS staging policies can outperform baseline allocation strategies. The study focuses on Manhattan as the primary area with the Central Business District (CBD/MTA Congestion Relief Zone) used for robustness comparison.

## Research Questions

1. Can optimized firehouse-based EMS staging improve readiness vs baseline allocation?
2. Does time-varying staging outperform fixed staging?
3. Are conclusions robust when restricted to the CBD?
4. What is the sensitivity to unit count, demand levels, and service/travel assumptions?
5. What are the managerial trade-offs?

## Project Structure

```
ems-optimization/
├── configs/              # Configuration files for simulations
├── data/
│   ├── raw/              # Original, immutable data
│   ├── external/         # External reference data
│   ├── interim/          # Intermediate transformed data
│   ├── processed/        # Final datasets for modeling
│   └── manifests/        # Data manifests and documentation
├── docs/                 # Project documentation
├── notebooks/            # Jupyter notebooks for analysis
├── src/ems_readiness/    # Source code package
├── tests/                # Unit tests
└── results/
    ├── figures/          # Generated graphics and visualizations
    ├── maps/             # Geographic visualizations
    └── tables/           # Generated tables and summaries
```

## Data Sources

- **FDNY Firehouse Listing**: 219 firehouses across NYC (source: NYC Open Data)
- **Motor Vehicle Collisions**: 2.24M crash records (source: NYC Open Data)
- **Police Precincts**: 78 precincts with geographic boundaries (source: NYC Open Data)
- **Geographic Boundaries**: Manhattan, CBD (MTA Congestion Relief Zone), NYC boroughs

## Setup Instructions

### Prerequisites

- Python 3.9+
- pip package manager

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/cnsp/ems-optimization.git
   cd ems-optimization
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   Or use the Makefile:
   ```bash
   make setup
   ```

### Running the Analysis

```bash
make analysis   # Run the full analysis pipeline
make clean      # Clean generated files
```

## Study Areas

- **Manhattan**: Primary study area for simulation
- **CBD (Central Business District)**: MTA Congestion Relief Zone - used for robustness testing

## Methodology

1. **Data Preparation**: Filter and clean crash data for Manhattan, extract temporal patterns
2. **Demand Modeling**: Fit arrival rate distributions by time-of-day and day-of-week
3. **Network Construction**: Build graph representation of Manhattan street network
4. **Simulation**: Discrete-event simulation using SimPy
5. **Optimization**: Linear programming for ambulance staging (PuLP)
6. **Analysis**: Compare baseline vs optimized policies across multiple scenarios

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please read the documentation in `docs/` before submitting pull requests.

## Contact

For questions or collaboration, please open an issue in this repository.
