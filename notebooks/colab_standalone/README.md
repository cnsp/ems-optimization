# Google Colab Standalone Notebooks

Standalone, reproducible notebook suite for the EMS Readiness Optimization project. These notebooks can be run independently in Google Colab to verify and reproduce the entire analysis.

### Quick Start — Google Colab

1. Open any notebook in Google Colab
2. Run the first setup cell (installs dependencies and clones the repository)
3. Execute cells sequentially

### Quick Start — Local Jupyter

The **same notebooks** work in both Google Colab and local Jupyter with no modifications needed. The first cell automatically detects the environment and adjusts paths, imports, and setup accordingly.

**Prerequisites:**
- Python 3.8+
- Jupyter Notebook or JupyterLab

**Steps:**
```bash
# 1. Clone the repository (if you haven't already)
git clone https://github.com/cnsp/ems-optimization.git
cd ems-optimization

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch Jupyter
jupyter notebook notebooks/colab_standalone/individual/
# — or for the all-in-one pipeline —
jupyter notebook notebooks/colab_standalone/EMS_Optimization_Complete_Pipeline.ipynb
```

When running locally the setup cell will:
- Skip `pip install` and `git clone` (assumes you already have the repo and packages)
- Auto-detect the project root by walking up the directory tree
- Set all data/config/results paths relative to the detected project root
- Skip Google Drive mounting and Colab file-download calls

> **Tip:** You can launch notebooks from *any* working directory — the path detection walks up from `os.getcwd()` looking for `requirements.txt` + `src/ems_readiness/`, so it always finds the project root.

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

### Colab vs Local — Key Differences

| Feature | Google Colab | Local Jupyter |
|---------|-------------|---------------|
| Package installation | Automatic (`!pip install`) | Manual (`pip install -r requirements.txt`) |
| Repository access | Auto-cloned from GitHub | Already on disk |
| Path detection | Hardcoded `/content/ems-optimization` | Auto-detected by walking up directory tree |
| File downloads | `google.colab.files.download()` | Saved to `results/` directory |
| Google Drive | Optional mount & save | Skipped (not available) |
| `DOWNLOAD_OUTPUTS` flag | Triggers browser download | Saves to `results/` only (no browser prompt) |
| `SAVE_TO_DRIVE` flag | Mounts Drive and copies files | Ignored |

### Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | **Colab:** Re-run the setup cell. **Local:** Run `pip install -r requirements.txt` |
| `FileNotFoundError` for processed data | Run notebook 00 first to verify data files |
| `PROJECT_ROOT` is wrong | Check that `requirements.txt` and `src/ems_readiness/` exist in the project root. The auto-detection walks up from the current directory. |
| Colab disconnects during simulation | Use Colab Pro; reduce `NUM_REPS` or `K_VALUES` |
| Out of memory | Restart runtime; reduce batch sizes |
| Slow optimization | CBC solver has 120s timeout; results may be suboptimal for large K |
| `!pip` / `!git` commands shown as errors locally | These only run inside the `if IN_COLAB:` block — they should never execute locally. If they do, check that `google.colab` is not accidentally importable in your environment. |

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
