# Google Colab Standalone Notebooks

Standalone, reproducible notebook suite for the EMS Readiness Optimization project. These notebooks can be run independently in Google Colab to verify and reproduce the entire analysis.

### Quick Start

1. Open any notebook in Google Colab
2. Run the first setup cell (installs dependencies and clones the repository)
3. Execute cells sequentially

### System Requirements

| Mode | Runtime | Memory | Colab Tier |
|------|---------|--------|------------|
| Setup + EDA | ~5 min | 2 GB | Free |
| Demand + Service modeling | ~5 min | 2 GB | Free |
| Optimization | ~5 min | 4 GB | Free |
| Simulation (demo, 5 reps) | ~5 min | 4 GB | Free |
| Simulation (full, 30 reps) | 4-8 hours | 8+ GB | **Pro recommended** |
| Statistical analysis | ~3 min | 2 GB | Free |
| All-in-one (full) | 5-10 hours | 8+ GB | **Pro recommended** |

### Individual Phase Notebooks

Located in `individual/`:

| # | Notebook | Description | Runtime |
|---|----------|-------------|---------|
| 00 | `00_colab_setup_and_data.ipynb` | Environment setup, dependency installation, data verification | ~2 min |
| 01 | `01_colab_eda_spatiotemporal.ipynb` | Temporal and spatial exploratory data analysis | ~5 min |
| 02 | `02_colab_demand_modeling.ipynb` | NHPP demand model, lambda estimation, thinning algorithm | ~5 min |
| 03 | `03_colab_service_modeling.ipynb` | Travel time proxy, service time distribution, distance matrices | ~3 min |
| 04 | `04_colab_optimization.ipynb` | P0/P1/P2 allocation policies, MIP formulation, PuLP solver | ~5 min |
| 05 | `05_colab_simulation.ipynb` | SimPy DES, 30 replications per scenario, CRN | 5 min - 8 hr |
| 06 | `06_colab_statistical_analysis.ipynb` | ANOVA, effect sizes, Tukey HSD, confidence intervals | ~3 min |
| 07 | `07_colab_visualization_reporting.ipynb` | Publication figures, summary report generation | ~3 min |

### All-in-One Notebook

`EMS_Optimization_Complete_Pipeline.ipynb` combines all 8 phases into a single notebook that can run the entire project from scratch.

### Data Access

Notebooks clone the project repository from GitHub:
```
https://github.com/cnsp/ems-optimization.git
```

**Note:** The raw motor vehicle collisions CSV (~536 MB) and police precincts CSV (~3.6 MB) are not tracked in Git due to their size. The processed data files (which are sufficient for most notebooks) are included in the repository.

If you need the raw data:
1. Download from [NYC Open Data - Motor Vehicle Collisions](https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95)
2. Download from [NYC Open Data - Police Precincts](https://data.cityofnewyork.us/Public-Safety/Police-Precincts/kmub-pusk)
3. Place in `data/raw/`

### Output Options

Each notebook supports three output modes (configured in the setup cell):

1. **Display inline** (default): All figures and tables displayed in the notebook
2. **Download files** (`DOWNLOAD_OUTPUTS = True`): Triggers browser download of output files
3. **Save to Google Drive** (`SAVE_TO_DRIVE = True`): Mounts Drive and saves to `MyDrive/EMS_Optimization_Results/`

### Notebook Dependencies

Notebooks 01-04 are independent and can run in any order after running 00 (setup).

Notebooks 05-07 have sequential dependencies:
- **05 (Simulation)** requires allocations from **04 (Optimization)** - or generates them automatically
- **06 (Statistical Analysis)** requires results from **05 (Simulation)**
- **07 (Visualization)** requires results from **05 (Simulation)**

### Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Re-run the setup cell; ensure `!pip install` completed |
| `FileNotFoundError` for processed data | Run notebook 00 first to verify data files |
| Colab disconnects during simulation | Use Colab Pro; reduce `NUM_REPS` or `K_VALUES` |
| Out of memory | Restart runtime; reduce batch sizes |
| Slow optimization | CBC solver has 120s timeout; results may be suboptimal for large K |

### Verification Checklist

From the project's verification and validation framework (Section 4.4.3):

**Verification (4 tests):**
- Toy example with known analytical solution
- Zero-demand test (no arrivals implies no incidents)
- Single-unit saturation test
- Extreme demand stress test

**Validation (3 pilots):**
- Pilot 1: P0 vs P2 directional comparison (P2 dominates)
- Pilot 2: Response time decreases monotonically with fleet size
- Pilot 3: Response time increases with demand intensity

**Unit tests:** 39 tests across 4 test modules

### License

MIT License - see project root `LICENSE` file.
