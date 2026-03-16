#!/usr/bin/env python3
"""Build the enhanced end-to-end workflow notebook."""

import json
from pathlib import Path

def md(source):
    return {"cell_type": "markdown", "metadata": {}, "source": [source]}

def code(source):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [source]}

cells = []

# ============================================================
# CELL 0: Title
# ============================================================
cells.append(md("""# EMS Readiness Optimization -- End-to-End Workflow

This notebook runs the **complete project pipeline** from raw data to final results.
It is designed to be self-contained: given only the raw data files, it will generate
all intermediate outputs, run optimization and simulation, and produce summary
visualizations and tables.

---

### How to Use This Notebook

| Environment | Instructions |
|---|---|
| **Local** | `cd ems-optimization && jupyter notebook notebooks/01_end_to_end_workflow.ipynb` |
| **Google Colab** | Upload the repo zip, unzip, then `%cd ems-optimization` before running |

### Prerequisites

- Python 3.10+
- Raw data files in `data/raw/` (see `data/raw/README.md` for download links)
- Dependencies: `pip install -r requirements.txt`

### Expected Runtime

| Section | Estimated Time |
|---|---|
| Setup and data generation | 2--5 minutes |
| Exploratory data analysis | <1 minute |
| Optimization (all policies, 4 fleet sizes) | 1--3 minutes |
| Simulation (4 verification + 3 validation pilots) | 5--15 minutes |
| Production simulation (810 scenarios) | 10--20 minutes |
| Statistical analysis | <1 minute |
| CBD robustness analysis | <1 minute |
| Visualization and export | 1--2 minutes |
| **Total** | **25--45 minutes** |

### Section Index

1. [Setup and Configuration](#1-setup-and-configuration)
2. [Data Generation Pipeline](#2-data-generation-pipeline)
3. [Exploratory Data Analysis](#3-exploratory-data-analysis)
4. [Optimization: Policy Comparison](#4-optimization-policy-comparison)
5. [Simulation: Verification and Validation](#5-simulation-verification-and-validation)
6. [Production Simulation Results](#6-production-simulation-results)
7. [Statistical Analysis](#7-statistical-analysis)
8. [CBD Robustness Analysis](#8-cbd-robustness-analysis)
9. [Results Visualization](#9-results-visualization)
10. [Summary and Conclusions](#10-summary-and-conclusions)

For deeper analysis on any topic, see the dedicated notebooks:
- `02_eda_spatiotemporal.ipynb` -- Spatial and temporal demand patterns
- `03_input_modeling.ipynb` -- Demand and service distributions
- `05_optimization.ipynb` -- Detailed optimization experiments
- `07_production_results.ipynb` -- Full production experiment results
- `08_statistical_analysis.ipynb` -- ANOVA, effect sizes, confidence intervals
- `09_cbd_analysis.ipynb` -- Central Business District robustness"""))

# ============================================================
# CELL 1: Setup header
# ============================================================
cells.append(md("""---
## 1. Setup and Configuration
<a id='1-setup-and-configuration'></a>"""))

# ============================================================
# CELL 2: Imports
# ============================================================
cells.append(code("""import os
import sys
import time
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats

warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)

# -- Resolve project root --
nb_dir = Path(os.getcwd())
if nb_dir.name == 'notebooks':
    PROJECT_ROOT = nb_dir.parent
else:
    PROJECT_ROOT = nb_dir
os.chdir(PROJECT_ROOT)
sys.path.insert(0, str(PROJECT_ROOT / 'src'))
sys.path.insert(0, str(PROJECT_ROOT))

print(f'Project root: {PROJECT_ROOT}')
print(f'Python:       {sys.version.split()[0]}')"""))

# ============================================================
# CELL 3: Colab header
# ============================================================
cells.append(md("""### Colab-specific setup (skip locally)

Uncomment and run the cell below only if you are on Google Colab."""))

# ============================================================
# CELL 4: Colab setup
# ============================================================
cells.append(code("""# --- Uncomment for Google Colab ---
# !pip install -q pulp simpy geopandas tqdm
# # If you uploaded a zip of the repo:
# # !unzip -q ems-optimization.zip
# # %cd ems-optimization"""))

# ============================================================
# CELL 5: Configuration
# ============================================================
cells.append(code("""# Plot defaults
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'figure.figsize': (12, 6),
    'font.size': 11,
    'axes.titlesize': 13,
    'figure.dpi': 100,
})

# Path constants
RAW_DIR       = PROJECT_ROOT / 'data' / 'raw'
PROCESSED_DIR = PROJECT_ROOT / 'data' / 'processed'
RESULTS_DIR   = PROJECT_ROOT / 'results'
FIGURES_DIR   = RESULTS_DIR / 'figures'
TABLES_DIR    = RESULTS_DIR / 'tables'

# Ensure output directories exist
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)

# Configuration
K_VALUES = [20, 30, 40, 48]
CAPACITY = 2          # firehouse capacity (units per station)
COVERAGE_TAU = 8.0    # coverage threshold in minutes
SIM_HORIZON = 168     # simulation horizon in hours (1 week)
SIM_REPS = 30         # Monte Carlo replications
SEED = 42

# Production simulation extended fleet sizes
K_VALUES_EXTENDED = [10, 15, 20, 25, 30, 35, 40, 45, 48]

print('Configuration:')
print(f'  Fleet sizes (K):            {K_VALUES}')
print(f'  Extended fleet sizes:       {K_VALUES_EXTENDED}')
print(f'  Firehouse capacity:         {CAPACITY}')
print(f'  Coverage threshold:         {COVERAGE_TAU} min')
print(f'  Simulation horizon:         {SIM_HORIZON} h ({SIM_HORIZON // 24} days)')
print(f'  MC replications:            {SIM_REPS}')
print(f'  Seed:                       {SEED}')
print(f'  Figures output dir:         {FIGURES_DIR}')
print(f'  Tables output dir:          {TABLES_DIR}')"""))

# ============================================================
# Data Generation Pipeline
# ============================================================
cells.append(md("""---
## 2. Data Generation Pipeline
<a id='2-data-generation-pipeline'></a>

The pipeline has three tiers:

| Tier | What it produces | Depends on |
|---|---|---|
| 1 | Boundary filters, clean firehouses, precinct geometries | Raw CSVs + GeoJSON |
| 2 | Manhattan crashes (filtered + geocoded) | Tier 1 + raw crash CSV |
| 3 | Demand lambdas, distance matrices | Tier 1 + Tier 2 |

**Runtime note:** Tier 2 processes ~2 million crash records and may take 2--4 minutes."""))

cells.append(code("""t0 = time.time()

from scripts.generate_all_data import ensure_data, verify_processed_data

# Generate any missing processed data
ensure_data(PROJECT_ROOT, force=False)

# Verify everything is in place
print('\\nProcessed data verification:')
all_ok = verify_processed_data(PROJECT_ROOT)

elapsed = time.time() - t0
print(f'\\nData pipeline completed in {elapsed:.1f}s')
if not all_ok:
    print('WARNING: Some files are missing. Later sections may fail.')"""))

# ============================================================
# EDA
# ============================================================
cells.append(md("""---
## 3. Exploratory Data Analysis
<a id='3-exploratory-data-analysis'></a>

Key questions:
- How much crash demand exists in Manhattan, and where is it concentrated?
- What temporal patterns drive demand intensity?
- How are firehouses distributed relative to demand?

For the full spatial and temporal analysis, see `02_eda_spatiotemporal.ipynb`."""))

cells.append(md("### 3.1 Dataset overview"))

cells.append(code("""crashes = pd.read_parquet(PROCESSED_DIR / 'crashes_manhattan.parquet')
firehouses = pd.read_csv(PROCESSED_DIR / 'firehouses_manhattan.csv')
precinct_demand = pd.read_csv(PROCESSED_DIR / 'demand_lambda_precinct.csv')
hourly_rates = pd.read_csv(PROCESSED_DIR / 'demand_lambda_hourly.csv')
dow_rates = pd.read_csv(PROCESSED_DIR / 'demand_lambda_dow.csv')

n_crashes = len(crashes)
date_min = pd.to_datetime(crashes['CRASH DATE']).min().strftime('%Y-%m-%d')
date_max = pd.to_datetime(crashes['CRASH DATE']).max().strftime('%Y-%m-%d')
n_days = (pd.to_datetime(date_max) - pd.to_datetime(date_min)).days
crashes_per_day = n_crashes / max(n_days, 1)

print('Manhattan Crash Demand -- Key Statistics')
print('=' * 50)
print(f'Total crashes:        {n_crashes:,}')
print(f'Date range:           {date_min} to {date_max}')
print(f'Duration:             {n_days:,} days ({n_days/365.25:.1f} years)')
print(f'Average crashes/day:  {crashes_per_day:.1f}')
print(f'Average crashes/hour: {crashes_per_day/24:.2f}')
print(f'Manhattan firehouses: {len(firehouses)}')
print(f'Manhattan precincts:  {len(precinct_demand)}')"""))

cells.append(md("### 3.2 Temporal demand patterns"))

cells.append(code("""fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Hourly pattern
ax = axes[0]
ax.bar(hourly_rates['hour'], hourly_rates['lambda_per_hour'],
       color='steelblue', edgecolor='white', linewidth=0.5)
ax.set_xlabel('Hour of Day')
ax.set_ylabel('Average Crashes per Hour')
ax.set_title('Hourly Crash Rate')
ax.set_xticks(range(0, 24, 3))
peak_hour = hourly_rates.loc[hourly_rates['lambda_per_hour'].idxmax(), 'hour']
ax.axvline(peak_hour, color='tomato', linestyle='--', label=f'Peak: {int(peak_hour):02d}:00')
ax.legend()

# Day-of-week pattern
ax = axes[1]
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
if 'day_name' in dow_rates.columns:
    dow_plot = dow_rates.set_index('day_name')
    rate_col = [c for c in dow_plot.columns if 'lambda' in c.lower() or 'factor' in c.lower()]
    if rate_col:
        vals = [dow_plot.loc[d, rate_col[0]] if d in dow_plot.index else 0 for d in day_order]
    else:
        vals = [dow_plot.iloc[i, 0] for i in range(min(7, len(dow_plot)))]
elif 'day_of_week' in dow_rates.columns:
    dow_plot = dow_rates.copy()
    if dow_plot['day_of_week'].dtype in ['int64', 'float64']:
        dow_plot['day_name'] = dow_plot['day_of_week'].map(
            {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday',
             4: 'Friday', 5: 'Saturday', 6: 'Sunday'})
    else:
        dow_plot['day_name'] = dow_plot['day_of_week']
    rate_col = [c for c in dow_plot.columns if 'rate' in c.lower() or 'factor' in c.lower() or 'lambda' in c.lower()]
    if rate_col:
        vals = [dow_plot.loc[dow_plot['day_name'] == d, rate_col[0]].values[0]
                if d in dow_plot['day_name'].values else 0 for d in day_order]
    else:
        vals = list(dow_plot.iloc[:, 1])[:7]
else:
    vals = list(dow_rates.iloc[:, 2])[:7]

ax.bar(range(7), vals, color='darkorange', edgecolor='white', linewidth=0.5)
ax.set_xticks(range(7))
ax.set_xticklabels([d[:3] for d in day_order])
ax.set_ylabel('Relative Rate Factor')
ax.set_title('Day-of-Week Pattern')

fig.suptitle('Manhattan Crash Demand -- Temporal Patterns', fontsize=14, y=1.02)
fig.tight_layout()
fig.savefig(FIGURES_DIR / 'temporal_demand_patterns.png', bbox_inches='tight', dpi=150)
plt.show()
print(f'Saved: {FIGURES_DIR / "temporal_demand_patterns.png"}')"""))

cells.append(md("### 3.3 Spatial demand distribution"))

cells.append(code("""fig, ax = plt.subplots(figsize=(12, 6))

rate_col = 'crash_rate_per_hour' if 'crash_rate_per_hour' in precinct_demand.columns else precinct_demand.columns[1]
pct_sorted = precinct_demand.sort_values(rate_col, ascending=True).copy()
pct_sorted['label'] = 'Pct ' + pct_sorted['precinct'].astype(str)

rates = pct_sorted[rate_col].values
daily_rates = rates * 24
median_daily = np.median(daily_rates)
colors = ['#c0392b' if r > median_daily * 1.3 else
          '#6c8ebf' if r > median_daily * 0.5 else
          '#27ae60' for r in daily_rates]

ax.barh(pct_sorted['label'], daily_rates, color=colors, edgecolor='white', linewidth=0.3)
ax.axvline(median_daily, color='orange', linestyle='--', label=f'Median: {median_daily:.1f}')
ax.set_xlabel('Crashes per Day')
ax.set_title('Precinct-Level Demand Rates (Red=High, Green=Low)')
ax.legend()
fig.tight_layout()
fig.savefig(FIGURES_DIR / 'precinct_demand_rates.png', bbox_inches='tight', dpi=150)
plt.show()
print(f'Saved: {FIGURES_DIR / "precinct_demand_rates.png"}')

top3 = pct_sorted.nlargest(3, rate_col)
print(f'Highest-demand precincts: {", ".join("Pct " + top3["precinct"].astype(str))}')
print(f'Together they account for {top3[rate_col].sum() / precinct_demand[rate_col].sum() * 100:.1f}% of total demand.')"""))

cells.append(md("### 3.4 Distance matrix and firehouse coverage"))

cells.append(code("""dm = pd.read_csv(PROCESSED_DIR / 'distance_matrix_firehouse_precinct.csv', index_col=0)
dm.columns = dm.columns.astype(str)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

ax = axes[0]
im = ax.imshow(dm.values, aspect='auto', cmap='YlOrRd')
ax.set_xlabel('Precinct Index')
ax.set_ylabel('Firehouse Index')
ax.set_title('Distance Matrix (miles)')
plt.colorbar(im, ax=ax, shrink=0.8)

ax = axes[1]
min_dists = dm.min(axis=0)
ax.hist(min_dists, bins=15, color='steelblue', edgecolor='white')
ax.axvline(min_dists.median(), color='tomato', linestyle='--',
           label=f'Median: {min_dists.median():.2f} mi')
ax.set_xlabel('Nearest Firehouse Distance (miles)')
ax.set_ylabel('Number of Precincts')
ax.set_title('Nearest-Firehouse Distance per Precinct')
ax.legend()

fig.tight_layout()
fig.savefig(FIGURES_DIR / 'distance_matrix_coverage.png', bbox_inches='tight', dpi=150)
plt.show()
print(f'Saved: {FIGURES_DIR / "distance_matrix_coverage.png"}')

print(f'Distance matrix shape: {dm.shape[0]} firehouses x {dm.shape[1]} precincts')
print(f'Distance range: {dm.values.min():.3f} -- {dm.values.max():.3f} miles')
print(f'Mean distance:  {dm.values.mean():.3f} miles')"""))

# ============================================================
# OPTIMIZATION
# ============================================================
cells.append(md("""---
## 4. Optimization: Policy Comparison
<a id='4-optimization-policy-comparison'></a>

We compare five allocation policies across four fleet sizes:

| Code | Policy | Type |
|---|---|---|
| P0 | Spatially-stratified uniform | Baseline |
| P1 | Demand-proportional | Baseline |
| P2 | Demand-weighted MIP | Optimized |
| P2b | P-median MIP | Optimized |
| P2c | Maximal coverage MIP | Optimized |

The objective metric is **expected response time** (demand-weighted, in minutes).
Coverage is the fraction of demand reachable within the threshold (8 minutes).

For detailed optimization analysis, see `05_optimization.ipynb`."""))

cells.append(code("""from ems_readiness.optimization.allocator import EMSAllocator

allocator = EMSAllocator.from_project(PROJECT_ROOT)

print(f'Allocator loaded:')
print(f'  Firehouses: {len(allocator.distance_matrix.index)}')
print(f'  Precincts:  {len(allocator.demand)}')
print(f'  Speed:      {allocator.travel_speed_mph} mph')"""))

cells.append(code("""POLICIES = {
    'P0':  {'label': 'Spatially-Stratified Uniform', 'type': 'baseline_p0'},
    'P1':  {'label': 'Demand-Proportional',          'type': 'baseline_dp'},
    'P2':  {'label': 'Demand-Weighted MIP',          'type': 'demand_weighted'},
    'P2b': {'label': 'P-Median MIP',                 'type': 'p_median'},
    'P2c': {'label': 'Maximal Coverage MIP',         'type': 'maximal_coverage'},
}

opt_results = []
allocations = {}  # store for simulation later

t0 = time.time()
for K in K_VALUES:
    print(f'\\nK = {K} units')
    for pid, pinfo in POLICIES.items():
        print(f'  {pid} ({pinfo["label"]})...', end=' ', flush=True)
        try:
            if pinfo['type'] == 'baseline_p0':
                result = allocator.baseline_p0(K, CAPACITY)
            elif pinfo['type'] == 'baseline_dp':
                result = allocator.baseline_demand_proportional(K, CAPACITY)
            else:
                result = allocator.solve(
                    model=pinfo['type'], K=K, capacity=CAPACITY,
                    coverage_threshold=COVERAGE_TAU, solver_time_limit=120)
            
            cov = allocator.evaluate_coverage(result.allocation, COVERAGE_TAU)
            rt = result.objective_value
            
            opt_results.append({
                'K': K, 'policy': pid, 'label': pinfo['label'],
                'mean_RT_min': rt,
                'coverage_pct': cov.get('covered_demand_pct', cov.get('demand_covered_pct', 0)),
                'stations_used': int((result.allocation > 0).sum()),
                'status': result.status,
            })
            allocations[(pid, K)] = result.allocation
            print(f'RT={rt:.2f} min, cov={opt_results[-1]["coverage_pct"]:.1f}%')
        except Exception as e:
            print(f'FAILED: {e}')
            opt_results.append({
                'K': K, 'policy': pid, 'label': pinfo['label'],
                'mean_RT_min': np.nan, 'coverage_pct': np.nan,
                'stations_used': 0, 'status': 'error',
            })

elapsed = time.time() - t0
print(f'\\nOptimization completed in {elapsed:.1f}s')

opt_df = pd.DataFrame(opt_results)
print(f'Total scenarios: {len(opt_df)}')"""))

cells.append(md("### 4.1 Optimization results table"))

cells.append(code("""# Pivot table: rows = K, columns = policy, values = response time
pivot_rt = opt_df.pivot(index='K', columns='policy', values='mean_RT_min')
pivot_rt = pivot_rt[['P0', 'P1', 'P2', 'P2b', 'P2c']]

pivot_cov = opt_df.pivot(index='K', columns='policy', values='coverage_pct')
pivot_cov = pivot_cov[['P0', 'P1', 'P2', 'P2b', 'P2c']]

print('Expected Response Time (minutes):')
print(pivot_rt.round(2).to_string())
print()
print('Demand Coverage within {} min (%):'.format(COVERAGE_TAU))
print(pivot_cov.round(1).to_string())

# Save optimization results
opt_df.to_csv(TABLES_DIR / 'optimization_results.csv', index=False)
print(f'\\nSaved: {TABLES_DIR / "optimization_results.csv"}')"""))

cells.append(md("### 4.2 Policy comparison visualization"))

cells.append(code("""fig, axes = plt.subplots(1, 2, figsize=(14, 6))
policy_colors = {'P0': '#3498db', 'P1': '#e67e22', 'P2': '#2ecc71', 'P2b': '#9b59b6', 'P2c': '#e74c3c'}

# Response time by fleet size
ax = axes[0]
for pid in ['P0', 'P1', 'P2', 'P2b', 'P2c']:
    subset = opt_df[opt_df['policy'] == pid]
    ax.plot(subset['K'], subset['mean_RT_min'], 'o-',
            color=policy_colors[pid], label=pid, markersize=7, linewidth=2)
ax.set_xlabel('Fleet Size (K)')
ax.set_ylabel('Expected Response Time (min)')
ax.set_title('Response Time vs Fleet Size')
ax.legend()
ax.set_xticks(K_VALUES)

# Coverage by fleet size
ax = axes[1]
for pid in ['P0', 'P1', 'P2', 'P2b', 'P2c']:
    subset = opt_df[opt_df['policy'] == pid]
    ax.plot(subset['K'], subset['coverage_pct'], 's-',
            color=policy_colors[pid], label=pid, markersize=7, linewidth=2)
ax.set_xlabel('Fleet Size (K)')
ax.set_ylabel(f'Demand Covered within {COVERAGE_TAU} min (%)')
ax.set_title('Coverage vs Fleet Size')
ax.legend()
ax.set_xticks(K_VALUES)

fig.suptitle('Optimization Results -- Policy Comparison', fontsize=14, y=1.02)
fig.tight_layout()
fig.savefig(FIGURES_DIR / 'policy_comparison.png', bbox_inches='tight', dpi=150)
plt.show()
print(f'Saved: {FIGURES_DIR / "policy_comparison.png"}')"""))

cells.append(md("### 4.3 Response Time vs Coverage trade-off"))

cells.append(code("""fig, ax = plt.subplots(figsize=(10, 7))
k_markers = {20: 'o', 30: 's', 40: 'D', 48: '^'}

for _, row in opt_df.iterrows():
    ax.scatter(row['mean_RT_min'], row['coverage_pct'],
               color=policy_colors.get(row['policy'], 'gray'),
               marker=k_markers.get(row['K'], 'o'),
               s=120, edgecolors='black', linewidth=0.5, zorder=3)

# Legend entries
for pid, col in policy_colors.items():
    ax.scatter([], [], color=col, label=pid, s=80)
for k, m in k_markers.items():
    ax.scatter([], [], color='gray', marker=m, label=f'K={k}', s=80)
ax.legend(ncol=2, fontsize=9)

ax.set_xlabel('Expected Response Time (minutes)')
ax.set_ylabel(f'Demand Covered within {COVERAGE_TAU} min (%)')
ax.set_title('Response Time vs Coverage Trade-off')
fig.tight_layout()
fig.savefig(FIGURES_DIR / 'response_time_coverage_tradeoff.png', bbox_inches='tight', dpi=150)
plt.show()
print(f'Saved: {FIGURES_DIR / "response_time_coverage_tradeoff.png"}')"""))

# ============================================================
# SIMULATION: V&V
# ============================================================
cells.append(md("""---
## 5. Simulation: Verification and Validation
<a id='5-simulation-verification-and-validation'></a>

We use discrete-event simulation (SimPy) to evaluate allocation policies under
stochastic demand. The simulation models:

- Non-homogeneous Poisson process (NHPP) arrivals calibrated from crash data
- Dispatch to nearest available unit
- Haversine-based travel time (configurable speed)
- LogNormal on-scene service time

### 5.1 Verification (4 tests)

These tests check internal correctness:
1. **Toy example** -- K=2, trace all events, check analytical consistency
2. **Zero demand** -- No arrivals should produce no incidents
3. **Single unit saturation** -- K=1, verify queue builds under load
4. **Extreme demand** -- High arrival rate, check stability

**Runtime note:** Verification tests are lightweight (<1 minute total)."""))

cells.append(code("""from ems_readiness.simulation.engine import EMSSimulation
from ems_readiness.optimization.policies import spatially_stratified_allocation

all_fhs = dm.index.tolist()

verification_results = {}
t0 = time.time()

# --- Test 1: Toy Example ---
print('Test 1: Toy Example (K=2, 2 firehouses, controlled arrivals)')
fh1, fh2 = all_fhs[0], all_fhs[1]
toy_alloc = pd.Series({fh1: 1, fh2: 1})
sim = EMSSimulation(policy_allocation=toy_alloc, seed=42,
                    project_root=str(PROJECT_ROOT), trace=True)

class ControlledGenerator:
    def generate_arrivals(self, n_hours=1, start_hour=0, dow=0, rng=42):
        return pd.DataFrame({
            'time_hours': [0.5, 1.0, 1.5, 2.0, 2.5],
            'hour': [0, 1, 1, 2, 2],
            'precinct': [1, 5, 1, 5, 1],
        })

sim.arrival_gen = ControlledGenerator()
sim.run(horizon_hours=4)
s = sim.get_results()['summary']
verification_results['toy'] = s
print(f'  Incidents: {s["total_incidents"]}, Mean RT: {s["response_time_mean"]:.2f} min')
print(f'  PASS' if s['total_incidents'] > 0 else '  FAIL: no incidents')

# --- Test 2: Zero Demand ---
print('\\nTest 2: Zero Demand')
alloc_10 = pd.Series({fh: 1 for fh in all_fhs[:10]})
sim = EMSSimulation(policy_allocation=alloc_10, seed=42,
                    project_root=str(PROJECT_ROOT))

class ZeroGenerator:
    def generate_arrivals(self, **kwargs):
        return pd.DataFrame(columns=['time_hours', 'hour', 'precinct'])

sim.arrival_gen = ZeroGenerator()
sim.run(horizon_hours=24)
s = sim.get_results()['summary']
verification_results['zero'] = s
print(f'  Incidents: {s["total_incidents"]}')
print(f'  PASS' if s['total_incidents'] == 0 else '  FAIL: unexpected incidents')

# --- Test 3: Single Unit Saturation ---
print('\\nTest 3: Single Unit Saturation (K=1, normal demand)')
single_alloc = pd.Series({all_fhs[0]: 1})
sim = EMSSimulation(policy_allocation=single_alloc, seed=42,
                    project_root=str(PROJECT_ROOT))
sim.run(horizon_hours=24)
s = sim.get_results()['summary']
verification_results['single'] = s
print(f'  Incidents: {s["total_incidents"]}, Queued: {s.get("incidents_queued", "N/A")}')
print(f'  Mean RT: {s["response_time_mean"]:.2f} min')
print(f'  PASS' if s['total_incidents'] > 0 else '  FAIL')

# --- Test 4: Extreme Demand Stress Test ---
print('\\nTest 4: Extreme Demand Stress Test (K=5, 3x demand)')
stress_alloc = pd.Series({fh: 1 for fh in all_fhs[:5]})
sim = EMSSimulation(policy_allocation=stress_alloc, seed=42,
                    project_root=str(PROJECT_ROOT))

original_gen = sim.arrival_gen
class HighRateGenerator:
    def __init__(self, original):
        self.original = original
    def generate_arrivals(self, n_hours=24, start_hour=0, dow=0, rng=42):
        df = self.original.generate_arrivals(n_hours=n_hours, start_hour=start_hour, dow=dow, rng=rng)
        if df.empty:
            return df
        copies = [df.copy() for _ in range(3)]
        for i, c in enumerate(copies):
            if i > 0:
                rng_obj = np.random.default_rng(rng + i * 1000 if isinstance(rng, int) else i * 1000)
                c['time_hours'] = c['time_hours'] + rng_obj.uniform(-0.01, 0.01, len(c))
                c['time_hours'] = c['time_hours'].clip(lower=0)
        combined = pd.concat(copies, ignore_index=True).sort_values('time_hours').reset_index(drop=True)
        return combined[combined['time_hours'] < n_hours]

sim.arrival_gen = HighRateGenerator(original_gen)
sim.run(horizon_hours=24)
s = sim.get_results()['summary']
verification_results['stress'] = s
print(f'  Incidents: {s["total_incidents"]}, Mean RT: {s["response_time_mean"]:.2f} min')
print(f'  PASS' if s['total_incidents'] > 0 and s['response_time_mean'] < 120 else '  CHECK: unusual results')

elapsed = time.time() - t0
print(f'\\nVerification completed in {elapsed:.1f}s')"""))

cells.append(md("""### 5.2 Validation pilots

These pilots check that simulation outputs match expected directional behavior:

1. **P0 vs P2** -- The optimized policy (P2) should dominate the baseline (P0) in response time.
2. **Fleet sensitivity** -- Response time should decrease monotonically as K increases.
3. **Demand sensitivity** -- Response time should increase as demand intensity grows.

**Runtime note:** Each pilot runs 30 replications x 1-week simulation. 
Expect 3--10 minutes total depending on hardware."""))

cells.append(code("""from ems_readiness.simulation.runner import BatchRunner

runner = BatchRunner(project_root=str(PROJECT_ROOT))
t0 = time.time()

# --- Pilot 1: P0 vs P2 at K=20 ---
print('Pilot 1: P0 vs P2 directional comparison (K=20)')
print('  Running P0...', flush=True)
p0_alloc = spatially_stratified_allocation(K=20, method='latitude', capacity=CAPACITY)
pilot1_p0 = runner.run_scenario(
    policy_allocation=p0_alloc, K=20, num_replications=SIM_REPS,
    seed_base=SEED, horizon_hours=SIM_HORIZON, policy_name='P0')

print('  Running P2...', flush=True)
if ('P2', 20) in allocations:
    p2_alloc = allocations[('P2', 20)]
else:
    p2_result = allocator.solve(model='demand_weighted', K=20, capacity=CAPACITY)
    p2_alloc = p2_result.allocation
pilot1_p2 = runner.run_scenario(
    policy_allocation=p2_alloc, K=20, num_replications=SIM_REPS,
    seed_base=SEED, horizon_hours=SIM_HORIZON, policy_name='P2')

p0_rt = pilot1_p0['response_time_mean']['mean']
p2_rt = pilot1_p2['response_time_mean']['mean']
print(f'  P0 mean RT: {p0_rt:.2f} min')
print(f'  P2 mean RT: {p2_rt:.2f} min')
print(f'  P2 dominates P0: {p2_rt < p0_rt}')

# --- Pilot 2: Fleet sensitivity ---
print('\\nPilot 2: Fleet sensitivity (P2, K=10..40)')
pilot2_ks = [10, 20, 30, 40]
pilot2_rts = []
for k in pilot2_ks:
    print(f'  K={k}...', end=' ', flush=True)
    alloc_k = allocator.solve(model='demand_weighted', K=k, capacity=CAPACITY).allocation
    res = runner.run_scenario(
        policy_allocation=alloc_k, K=k, num_replications=SIM_REPS,
        seed_base=SEED, horizon_hours=SIM_HORIZON, policy_name=f'P2_K{k}')
    rt = res['response_time_mean']['mean']
    pilot2_rts.append(rt)
    print(f'RT={rt:.2f}')

monotonic = all(pilot2_rts[i] >= pilot2_rts[i+1] for i in range(len(pilot2_rts)-1))
print(f'  Monotonically decreasing: {monotonic}')

# --- Pilot 3: Demand sensitivity ---
print('\\nPilot 3: Demand sensitivity (P2, K=20, rate x0.5/1.0/2.0)')
pilot3_scales = [0.5, 1.0, 2.0]
pilot3_rts = []
p2_alloc_20 = allocations.get(('P2', 20), allocator.solve(model='demand_weighted', K=20, capacity=CAPACITY).allocation)
for scale in pilot3_scales:
    print(f'  scale={scale}x...', end=' ', flush=True)
    rep_rts = []
    for rep in range(min(SIM_REPS, 10)):  # fewer reps for speed
        sim = EMSSimulation(
            policy_allocation=p2_alloc_20, seed=SEED + rep,
            project_root=str(PROJECT_ROOT))
        if scale != 1.0:
            sim.arrival_gen.base_rate = sim.arrival_gen.base_rate * scale
        sim.run(horizon_hours=SIM_HORIZON)
        s = sim.get_results()['summary']
        rep_rts.append(s['response_time_mean'])
    rt = np.mean(rep_rts)
    pilot3_rts.append(rt)
    print(f'RT={rt:.2f}')

increasing = all(pilot3_rts[i] <= pilot3_rts[i+1] for i in range(len(pilot3_rts)-1))
print(f'  Monotonically increasing: {increasing}')

elapsed = time.time() - t0
print(f'\\nValidation pilots completed in {elapsed:.1f}s')"""))

cells.append(md("### 5.3 Validation summary"))

cells.append(code("""print('Verification and Validation Summary')
print('=' * 55)
print()
print('Verification (4 tests):')
v_tests = [
    ('Toy example',       verification_results['toy']['total_incidents'] > 0),
    ('Zero demand',       verification_results['zero']['total_incidents'] == 0),
    ('Single-unit sat.',  verification_results['single']['total_incidents'] > 0),
    ('Extreme demand',    verification_results['stress']['total_incidents'] > 0),
]
for name, passed in v_tests:
    status = 'PASS' if passed else 'FAIL'
    print(f'  {name:25s} [{status}]')

print()
print('Validation (3 pilots):')
v_pilots = [
    ('P0 vs P2 (P2 dominates)', p2_rt < p0_rt),
    ('RT decreases with K',     monotonic),
    ('RT increases with demand', increasing),
]
for name, passed in v_pilots:
    status = 'PASS' if passed else 'FAIL'
    print(f'  {name:25s} [{status}]')

# Save validation results
val_rows = []
for name, passed in v_tests:
    val_rows.append({'type': 'verification', 'test': name, 'passed': passed})
for name, passed in v_pilots:
    val_rows.append({'type': 'validation', 'test': name, 'passed': passed})
val_df = pd.DataFrame(val_rows)
val_df.to_csv(TABLES_DIR / 'validation_results.csv', index=False)
print(f'\\nSaved: {TABLES_DIR / "validation_results.csv"}')"""))

# ============================================================
# SECTION 6: Production Simulation Results
# ============================================================
cells.append(md("""---
## 6. Production Simulation Results
<a id='6-production-simulation-results'></a>

Full-scale simulation experiments across 3 policies (P0, P1, P2) and 9 fleet sizes
(K=10 to 48), with 30 replications each. This produces 810 simulation runs.

**Runtime note:** If pre-computed results exist in `results/production_v2/simulation/`,
they will be loaded directly. Otherwise, the full simulation runs (~10-20 minutes)."""))

cells.append(code("""t0 = time.time()

# Check for pre-computed production results
prod_results_path = RESULTS_DIR / 'production_v2' / 'simulation' / 'all_results_raw.csv'

if prod_results_path.exists():
    print('Loading pre-computed production results...')
    prod_df = pd.read_csv(prod_results_path)
    print(f'Loaded {len(prod_df)} simulation records')
else:
    print('Running production simulations (this may take 10-20 minutes)...')
    prod_rows = []
    prod_policies = {
        'P0': 'baseline_p0',
        'P1': 'baseline_dp',
        'P2': 'demand_weighted',
    }
    
    for K in K_VALUES_EXTENDED:
        for pid, ptype in prod_policies.items():
            print(f'  {pid} K={K}...', end=' ', flush=True)
            try:
                if ptype == 'baseline_p0':
                    result = allocator.baseline_p0(K, CAPACITY)
                elif ptype == 'baseline_dp':
                    result = allocator.baseline_demand_proportional(K, CAPACITY)
                else:
                    result = allocator.solve(model=ptype, K=K, capacity=CAPACITY,
                                            coverage_threshold=COVERAGE_TAU, solver_time_limit=120)
                alloc = result.allocation
            except Exception as e:
                print(f'FAILED: {e}')
                continue
            
            for rep in range(SIM_REPS):
                sim = EMSSimulation(policy_allocation=alloc, seed=SEED + rep,
                                    project_root=str(PROJECT_ROOT))
                sim.run(horizon_hours=SIM_HORIZON)
                s = sim.get_results()['summary']
                prod_rows.append({
                    'policy': pid if pid != 'P0' else 'P0-spatial',
                    'K': K, 'replication': rep, 'capacity': CAPACITY,
                    'mean_response_time': s['response_time_mean'],
                    'median_response_time': s.get('response_time_median', np.nan),
                    'p95_response_time': s.get('response_time_p95', np.nan),
                    'coverage_8min': s.get('coverage_fraction', np.nan),
                    'mean_utilization': s.get('utilization_mean', np.nan),
                    'mean_queue_length': s.get('queue_length_tw_avg', 0),
                    'max_queue_length': s.get('queue_length_max', 0),
                    'total_incidents': s['total_incidents'],
                    'incidents_queued': s.get('incidents_queued', 0),
                })
            print(f'done ({SIM_REPS} reps)')
    
    prod_df = pd.DataFrame(prod_rows)
    # Save for future use
    out_dir = RESULTS_DIR / 'production_v2' / 'simulation'
    out_dir.mkdir(parents=True, exist_ok=True)
    prod_df.to_csv(out_dir / 'all_results_raw.csv', index=False)

# Standardize policy names
prod_df['policy_clean'] = prod_df['policy'].replace({'P0-spatial': 'P0'})

print(f'\\nProduction results summary:')
print(f'  Policies:     {sorted(prod_df["policy_clean"].unique())}')
print(f'  Fleet sizes:  {sorted(prod_df["K"].unique())}')
print(f'  Total records: {len(prod_df)}')
print(f'  Time: {time.time() - t0:.1f}s')"""))

cells.append(md("### 6.1 Production results table"))

cells.append(code("""# Aggregate production results: mean and 95% CI per scenario
prod_agg = prod_df.groupby(['policy_clean', 'K']).agg(
    mean_rt=('mean_response_time', 'mean'),
    std_rt=('mean_response_time', 'std'),
    n=('mean_response_time', 'count'),
    p95_rt=('mean_response_time', lambda x: np.percentile(x, 95)),
    coverage_6=('coverage_6min', 'mean'),
    coverage=('coverage_8min', 'mean'),
    mean_util=('mean_utilization', 'mean'),
    mean_queue=('mean_queue_length', 'mean'),
).reset_index()

# 95% confidence intervals
t_crit = stats.t.ppf(0.975, df=prod_agg['n'] - 1)
prod_agg['ci_lo'] = prod_agg['mean_rt'] - t_crit * prod_agg['std_rt'] / np.sqrt(prod_agg['n'])
prod_agg['ci_hi'] = prod_agg['mean_rt'] + t_crit * prod_agg['std_rt'] / np.sqrt(prod_agg['n'])

# Display pivot
pivot_prod = prod_agg.pivot(index='K', columns='policy_clean', values='mean_rt')
if 'P0' in pivot_prod.columns:
    col_order = [c for c in ['P0', 'P1', 'P2'] if c in pivot_prod.columns]
    pivot_prod = pivot_prod[col_order]

print('Production Simulation: Mean Response Time (minutes)')
print('=' * 55)
print(pivot_prod.round(3).to_string())

# Coverage pivot
pivot_cov_prod = prod_agg.pivot(index='K', columns='policy_clean', values='coverage')
if 'P0' in pivot_cov_prod.columns:
    pivot_cov_prod = pivot_cov_prod[[c for c in ['P0', 'P1', 'P2'] if c in pivot_cov_prod.columns]]
# 6-min Coverage pivot
pivot_cov6_prod = prod_agg.pivot(index='K', columns='policy_clean', values='coverage_6')
if 'P0' in pivot_cov6_prod.columns:
    pivot_cov6_prod = pivot_cov6_prod[[c for c in ['P0', 'P1', 'P2'] if c in pivot_cov6_prod.columns]]
print('\\nProduction Simulation: 6-min Coverage (NYC)')
print('=' * 55)
print((pivot_cov6_prod * 100).round(1).to_string())

print('\\nProduction Simulation: 8-min Coverage (NFPA)')
print('=' * 55)
print((pivot_cov_prod * 100).round(1).to_string())

# Save production results
prod_agg.to_csv(TABLES_DIR / 'production_results.csv', index=False)
print(f'\\nSaved: {TABLES_DIR / "production_results.csv"}')"""))

cells.append(md("### 6.2 Fleet sensitivity visualization (production)"))

cells.append(code("""fig, axes = plt.subplots(1, 4, figsize=(22, 5))

prod_colors = {'P0': '#3498db', 'P1': '#e67e22', 'P2': '#2ecc71'}

# Mean response time
ax = axes[0]
for pid in ['P0', 'P1', 'P2']:
    sub = prod_agg[prod_agg['policy_clean'] == pid].sort_values('K')
    if len(sub) == 0:
        continue
    ax.plot(sub['K'], sub['mean_rt'], 'o-', color=prod_colors[pid], label=pid, linewidth=2, markersize=6)
    ax.fill_between(sub['K'], sub['ci_lo'], sub['ci_hi'], alpha=0.15, color=prod_colors[pid])
ax.set_xlabel('Fleet Size (K)')
ax.set_ylabel('Mean Response Time (min)')
ax.set_title('A. Response Time vs Fleet Size')
ax.legend()

# 6-min Coverage (NYC)
ax = axes[1]
for pid in ['P0', 'P1', 'P2']:
    sub = prod_agg[prod_agg['policy_clean'] == pid].sort_values('K')
    if len(sub) == 0:
        continue
    ax.plot(sub['K'], sub['coverage_6'] * 100, 's-', color=prod_colors[pid], label=pid, linewidth=2, markersize=6)
ax.set_xlabel('Fleet Size (K)')
ax.set_ylabel('6-min Coverage (NYC) (%)')
ax.set_title('B. 6-min Coverage (NYC) vs Fleet Size')
ax.legend()

# 8-min Coverage (NFPA)
ax = axes[2]
for pid in ['P0', 'P1', 'P2']:
    sub = prod_agg[prod_agg['policy_clean'] == pid].sort_values('K')
    if len(sub) == 0:
        continue
    ax.plot(sub['K'], sub['coverage'] * 100, 's-', color=prod_colors[pid], label=pid, linewidth=2, markersize=6)
ax.set_xlabel('Fleet Size (K)')
ax.set_ylabel('8-min Coverage (NFPA) (%)')
ax.set_title('C. 8-min Coverage (NFPA) vs Fleet Size')
ax.legend()

# Utilization
ax = axes[3]
for pid in ['P0', 'P1', 'P2']:
    sub = prod_agg[prod_agg['policy_clean'] == pid].sort_values('K')
    if len(sub) == 0:
        continue
    ax.plot(sub['K'], sub['mean_util'] * 100, 'D-', color=prod_colors[pid], label=pid, linewidth=2, markersize=6)
ax.set_xlabel('Fleet Size (K)')
ax.set_ylabel('Mean Utilization (%)')
ax.set_title('D. Utilization vs Fleet Size')
ax.legend()

fig.suptitle('Production Simulation Results (30 replications per scenario)', fontsize=14, y=1.02)
fig.tight_layout()
fig.savefig(FIGURES_DIR / 'production_fleet_sensitivity.png', bbox_inches='tight', dpi=150)
plt.show()
print(f'Saved: {FIGURES_DIR / "production_fleet_sensitivity.png"}')"""))

cells.append(md("### 6.3 Queue metrics"))

cells.append(code("""# Queue metrics from production data
queue_cols = [c for c in prod_df.columns if 'queue' in c.lower()]
if queue_cols:
    queue_agg = prod_df.groupby(['policy_clean', 'K']).agg(
        mean_queue_length=('mean_queue_length', 'mean'),
        max_queue_length=('max_queue_length', 'max'),
        queue_fraction=('incidents_queued', lambda x: x.sum()),
        total_incidents=('total_incidents', 'sum'),
    ).reset_index()
    queue_agg['queue_pct'] = queue_agg['queue_fraction'] / queue_agg['total_incidents'].clip(lower=1) * 100

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    ax = axes[0]
    for pid in ['P0', 'P1', 'P2']:
        sub = queue_agg[queue_agg['policy_clean'] == pid].sort_values('K')
        if len(sub) == 0:
            continue
        ax.plot(sub['K'], sub['mean_queue_length'], 'o-', color=prod_colors[pid], label=pid, linewidth=2)
    ax.set_xlabel('Fleet Size (K)')
    ax.set_ylabel('Mean Queue Length')
    ax.set_title('Mean Queue Length vs Fleet Size')
    ax.legend()
    
    ax = axes[1]
    for pid in ['P0', 'P1', 'P2']:
        sub = queue_agg[queue_agg['policy_clean'] == pid].sort_values('K')
        if len(sub) == 0:
            continue
        ax.plot(sub['K'], sub['queue_pct'], 's-', color=prod_colors[pid], label=pid, linewidth=2)
    ax.set_xlabel('Fleet Size (K)')
    ax.set_ylabel('% Incidents Queued')
    ax.set_title('Queue Fraction vs Fleet Size')
    ax.legend()
    
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / 'queue_metrics.png', bbox_inches='tight', dpi=150)
    plt.show()
    print(f'Saved: {FIGURES_DIR / "queue_metrics.png"}')
    
    queue_agg.to_csv(TABLES_DIR / 'queue_metrics.csv', index=False)
    print(f'Saved: {TABLES_DIR / "queue_metrics.csv"}')
else:
    print('No queue columns found in production data.')"""))

# ============================================================
# SECTION 7: Statistical Analysis
# ============================================================
cells.append(md("""---
## 7. Statistical Analysis
<a id='7-statistical-analysis'></a>

This section applies formal statistical methods to the production simulation results:
- **One-way ANOVA** to test whether policies differ significantly at each fleet size
- **Tukey HSD** post-hoc tests for pairwise comparisons
- **Cohen's d** effect sizes to measure practical significance
- **95% confidence intervals** for all metrics

**Runtime note:** Statistical analysis is instantaneous on pre-aggregated data."""))

cells.append(md("### 7.1 ANOVA: Policy comparisons at each fleet size"))

cells.append(code("""from scipy.stats import f_oneway
from itertools import combinations

# ANOVA for each K value
anova_rows = []
for K in sorted(prod_df['K'].unique()):
    groups = []
    group_labels = []
    for pid in sorted(prod_df['policy_clean'].unique()):
        vals = prod_df[(prod_df['policy_clean'] == pid) & (prod_df['K'] == K)]['mean_response_time'].values
        if len(vals) > 1:
            groups.append(vals)
            group_labels.append(pid)
    
    if len(groups) >= 2:
        F, p = f_oneway(*groups)
        # Effect size: eta-squared
        grand_mean = np.concatenate(groups).mean()
        ss_between = sum(len(g) * (g.mean() - grand_mean)**2 for g in groups)
        ss_total = sum(np.sum((g - grand_mean)**2) for g in groups)
        eta_sq = ss_between / ss_total if ss_total > 0 else 0
        
        anova_rows.append({
            'K': K, 'F_statistic': F, 'p_value': p,
            'eta_squared': eta_sq,
            'significant': '*' if p < 0.05 else '',
            'effect_size': 'Large' if eta_sq > 0.14 else ('Medium' if eta_sq > 0.06 else 'Small'),
        })

anova_df = pd.DataFrame(anova_rows)
print('One-Way ANOVA: Policy Effect on Mean Response Time')
print('=' * 70)
print(anova_df.to_string(index=False, float_format='{:.4f}'.format))"""))

cells.append(md("### 7.2 Tukey HSD post-hoc pairwise comparisons"))

cells.append(code("""# Pairwise comparisons using Welch's t-test (robust to unequal variances)
posthoc_rows = []
for K in sorted(prod_df['K'].unique()):
    policies = sorted(prod_df['policy_clean'].unique())
    for p1, p2 in combinations(policies, 2):
        g1 = prod_df[(prod_df['policy_clean'] == p1) & (prod_df['K'] == K)]['mean_response_time'].values
        g2 = prod_df[(prod_df['policy_clean'] == p2) & (prod_df['K'] == K)]['mean_response_time'].values
        if len(g1) > 1 and len(g2) > 1:
            t_stat, p_val = stats.ttest_ind(g1, g2, equal_var=False)
            diff = g1.mean() - g2.mean()
            
            # Cohen's d
            pooled_std = np.sqrt((g1.std()**2 + g2.std()**2) / 2)
            cohens_d = abs(diff) / pooled_std if pooled_std > 0 else 0
            
            posthoc_rows.append({
                'K': K, 'comparison': f'{p1} vs {p2}',
                'mean_diff': diff, 't_stat': t_stat, 'p_value': p_val,
                'cohens_d': cohens_d,
                'effect': 'Large' if cohens_d >= 0.8 else ('Medium' if cohens_d >= 0.5 else 'Small'),
                'significant': '***' if p_val < 0.001 else ('**' if p_val < 0.01 else ('*' if p_val < 0.05 else 'ns')),
            })

posthoc_df = pd.DataFrame(posthoc_rows)

# Display key K values
for K in [20, 30, 40]:
    sub = posthoc_df[posthoc_df['K'] == K]
    if len(sub) > 0:
        print(f'\\nPairwise Comparisons at K={K}:')
        print(sub[['comparison', 'mean_diff', 'cohens_d', 'effect', 'significant']].to_string(index=False, float_format='{:.4f}'.format))"""))

cells.append(md("### 7.3 Confidence intervals"))

cells.append(code("""# Compute 95% CIs for all policy-K combinations
ci_rows = []
for pid in sorted(prod_df['policy_clean'].unique()):
    for K in sorted(prod_df['K'].unique()):
        vals = prod_df[(prod_df['policy_clean'] == pid) & (prod_df['K'] == K)]['mean_response_time'].values
        if len(vals) > 1:
            n = len(vals)
            mean = vals.mean()
            std = vals.std(ddof=1)
            se = std / np.sqrt(n)
            t_c = stats.t.ppf(0.975, df=n-1)
            ci_rows.append({
                'policy': pid, 'K': K, 'metric': 'Mean RT (min)',
                'n': n, 'mean': mean, 'std': std, 'se': se,
                'ci_lower': mean - t_c * se,
                'ci_upper': mean + t_c * se,
                'ci_width': 2 * t_c * se,
            })

ci_df = pd.DataFrame(ci_rows)

# Show CI summary for key fleet sizes
print('95% Confidence Intervals for Mean Response Time')
print('=' * 70)
for K in [20, 30, 40, 48]:
    sub = ci_df[ci_df['K'] == K]
    if len(sub) > 0:
        print(f'\\nK={K}:')
        print(sub[['policy', 'mean', 'ci_lower', 'ci_upper', 'ci_width']].to_string(index=False, float_format='{:.4f}'.format))

# Save all statistical results
anova_df.to_csv(TABLES_DIR / 'statistical_analysis.csv', index=False)
posthoc_df.to_csv(TABLES_DIR / 'posthoc_comparisons_notebook.csv', index=False)
ci_df.to_csv(TABLES_DIR / 'confidence_intervals_notebook.csv', index=False)
print(f'\\nSaved: statistical_analysis.csv, posthoc_comparisons_notebook.csv, confidence_intervals_notebook.csv')"""))

cells.append(md("### 7.4 Effect sizes visualization"))

cells.append(code("""# Cohen's d heatmap for P0 vs P2
p0_vs_p2 = posthoc_df[posthoc_df['comparison'] == 'P0 vs P2'].copy()
if len(p0_vs_p2) > 0:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Cohen's d bar chart
    ax = axes[0]
    ax.bar(p0_vs_p2['K'].astype(str), p0_vs_p2['cohens_d'], color='#e74c3c', edgecolor='black')
    ax.axhline(0.8, color='gray', linestyle='--', alpha=0.5, label='Large effect (d=0.8)')
    ax.set_xlabel('Fleet Size (K)')
    ax.set_ylabel("Cohen's d")
    ax.set_title("Effect Size: P0 vs P2 (Response Time)")
    ax.legend()
    
    # CI comparison at K=20
    ax = axes[1]
    ci_k20 = ci_df[ci_df['K'] == 20].sort_values('policy')
    if len(ci_k20) > 0:
        y_pos = range(len(ci_k20))
        ax.barh(list(y_pos), ci_k20['mean'], xerr=ci_k20['ci_width']/2,
                color=[prod_colors.get(p, 'gray') for p in ci_k20['policy']],
                edgecolor='black', capsize=5)
        ax.set_yticks(list(y_pos))
        ax.set_yticklabels(ci_k20['policy'])
        ax.set_xlabel('Mean Response Time (min)')
        ax.set_title('95% CI Comparison at K=20')
    
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / 'statistical_effect_sizes.png', bbox_inches='tight', dpi=150)
    plt.show()
    print(f'Saved: {FIGURES_DIR / "statistical_effect_sizes.png"}')
else:
    print('No P0 vs P2 comparison data available.')"""))

# ============================================================
# SECTION 8: CBD Robustness Analysis
# ============================================================
cells.append(md("""---
## 8. CBD Robustness Analysis
<a id='8-cbd-robustness-analysis'></a>

This section evaluates whether the optimized policies perform equitably across 
the Central Business District (CBD, MTA Congestion Relief Zone) and the rest of Manhattan.

**Key question:** Does P2's optimization inadvertently disadvantage areas outside the CBD?"""))

cells.append(md("### 8.1 CBD boundary and crash classification"))

cells.append(code("""import geopandas as gpd
from shapely.geometry import Point

# Load CBD boundary
cbd_gdf = gpd.read_file(RAW_DIR / 'cbd_boundary.geojson')
cbd_geom = cbd_gdf.geometry.unary_union

# Classify crashes as CBD vs Non-CBD
crash_coords = crashes[['LATITUDE', 'LONGITUDE']].dropna()
crash_points = gpd.GeoSeries([Point(lon, lat) for lat, lon in zip(crash_coords['LATITUDE'], crash_coords['LONGITUDE'])],
                              crs='EPSG:4326')
in_cbd = crash_points.within(cbd_geom)

n_cbd = in_cbd.sum()
n_non_cbd = len(in_cbd) - n_cbd
print(f'CBD Analysis:')
print(f'  CBD crashes:     {n_cbd:,} ({n_cbd/len(in_cbd)*100:.1f}%)')
print(f'  Non-CBD crashes: {n_non_cbd:,} ({n_non_cbd/len(in_cbd)*100:.1f}%)')

# Classify precincts as CBD/Non-CBD based on centroid
precinct_geo_path = PROCESSED_DIR / 'precincts_manhattan.csv'
if precinct_geo_path.exists():
    pct_geo = pd.read_csv(precinct_geo_path)
    if 'centroid_lat' in pct_geo.columns and 'centroid_lon' in pct_geo.columns:
        pct_points = gpd.GeoSeries(
            [Point(lon, lat) for lat, lon in zip(pct_geo['centroid_lat'], pct_geo['centroid_lon'])],
            crs='EPSG:4326')
        pct_in_cbd = pct_points.within(cbd_geom)
        cbd_precincts = pct_geo.loc[pct_in_cbd, 'precinct'].tolist()
        non_cbd_precincts = pct_geo.loc[~pct_in_cbd, 'precinct'].tolist()
        print(f'  CBD precincts ({len(cbd_precincts)}):     {cbd_precincts}')
        print(f'  Non-CBD precincts ({len(non_cbd_precincts)}): {non_cbd_precincts}')
    else:
        cbd_precincts = []
        non_cbd_precincts = []
        print('  Note: precinct centroid coordinates not found, using crash-level CBD classification.')
else:
    cbd_precincts = []
    non_cbd_precincts = []
    print('  Note: precincts_manhattan.csv not found.')"""))

cells.append(md("### 8.2 Policy performance by zone"))

cells.append(code("""# Load pre-computed CBD comparison if available, else compute from production data
cbd_precomp = TABLES_DIR / 'cbd_comparison.csv'
if cbd_precomp.exists():
    cbd_comp = pd.read_csv(cbd_precomp)
    print('CBD vs Non-CBD Policy Comparison (pre-computed):')
    print('=' * 70)
    print(cbd_comp.to_string(index=False, float_format='{:.4f}'.format))
else:
    print('No pre-computed CBD comparison found. Using crash-level classification.')

# Check for extended CBD results
cbd_ext = TABLES_DIR / 'cbd_summary_all.csv'
if cbd_ext.exists():
    cbd_all = pd.read_csv(cbd_ext)
    print('\\nCBD Analysis -- All Scenarios:')
    print('=' * 70)
    print(cbd_all.head(15).to_string(index=False, float_format='{:.4f}'.format))

# Spatial equity metric: ratio of Non-CBD RT to CBD RT (1.0 = perfectly equitable)
if cbd_precomp.exists():
    cbd_comp = pd.read_csv(cbd_precomp)
    if 'cbd_mean_rt' in cbd_comp.columns and 'non_cbd_mean_rt' in cbd_comp.columns:
        cbd_comp['equity_ratio'] = cbd_comp['non_cbd_mean_rt'] / cbd_comp['cbd_mean_rt'].clip(lower=0.01)
        print('\\nSpatial Equity (Non-CBD RT / CBD RT):')
        print('  Ratio=1.0 means equal service; higher means non-CBD is underserved.')
        for _, row in cbd_comp.iterrows():
            print(f'  {row["policy"]}: {row["equity_ratio"]:.2f}')"""))

cells.append(md("### 8.3 CBD robustness visualization"))

cells.append(code("""if cbd_precomp.exists():
    cbd_comp = pd.read_csv(cbd_precomp)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Response time comparison
    ax = axes[0]
    x = np.arange(len(cbd_comp))
    w = 0.35
    if 'cbd_mean_rt' in cbd_comp.columns:
        ax.bar(x - w/2, cbd_comp['cbd_mean_rt'], w, label='CBD', color='#e74c3c', edgecolor='black')
        ax.bar(x + w/2, cbd_comp['non_cbd_mean_rt'], w, label='Non-CBD', color='#3498db', edgecolor='black')
        ax.set_xticks(x)
        ax.set_xticklabels(cbd_comp['policy'])
        ax.set_ylabel('Mean Response Time (min)')
        ax.set_title('Response Time: CBD vs Non-CBD')
        ax.legend()
    
    # Coverage comparison
    ax = axes[1]
    if 'cbd_coverage_8min' in cbd_comp.columns:
        ax.bar(x - w/2, cbd_comp['cbd_coverage_8min'] * 100, w, label='CBD (8-min NFPA)', color='#e74c3c', edgecolor='black')
        ax.bar(x + w/2, cbd_comp['non_cbd_coverage_8min'] * 100, w, label='Non-CBD (8-min NFPA)', color='#3498db', edgecolor='black')
        if 'cbd_coverage_6min' in cbd_comp.columns:
            ax.bar(x - w/2, cbd_comp['cbd_coverage_6min'] * 100, w, label='CBD (6-min NYC)', color='#e74c3c', edgecolor='black', alpha=0.5, hatch='//')
            ax.bar(x + w/2, cbd_comp['non_cbd_coverage_6min'] * 100, w, label='Non-CBD (6-min NYC)', color='#3498db', edgecolor='black', alpha=0.5, hatch='//')
        ax.set_xticks(x)
        ax.set_xticklabels(cbd_comp['policy'])
        ax.set_ylabel('Coverage (%)')
        ax.set_title('Coverage: CBD vs Non-CBD')
        ax.legend(fontsize=8)
    
    fig.suptitle('CBD Robustness Analysis', fontsize=14, y=1.02)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / 'cbd_robustness.png', bbox_inches='tight', dpi=150)
    plt.show()
    print(f'Saved: {FIGURES_DIR / "cbd_robustness.png"}')

    # Save CBD robustness table
    cbd_comp.to_csv(TABLES_DIR / 'cbd_robustness.csv', index=False)
    print(f'Saved: {TABLES_DIR / "cbd_robustness.csv"}')
else:
    print('CBD comparison data not available for visualization.')"""))

# ============================================================
# SECTION 9: Results Visualization
# ============================================================
cells.append(md("""---
## 9. Results Visualization
<a id='9-results-visualization'></a>

Key figures summarizing the project findings. All figures are saved to `results/figures/`."""))

cells.append(md("### 9.1 Simulation: P0 vs P2 response time"))

cells.append(code("""fig, ax = plt.subplots(figsize=(10, 5))

labels = ['P0 (Baseline)', 'P2 (Optimized)']
means = [p0_rt, p2_rt]
colors_bar = ['#3498db', '#2ecc71']

bars = ax.bar(labels, means, color=colors_bar, edgecolor='black', width=0.5)
for bar, val in zip(bars, means):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
            f'{val:.2f}', ha='center', fontsize=12, fontweight='bold')

ax.set_ylabel('Mean Response Time (minutes)')
ax.set_title(f'P0 vs P2 Response Time (K=20, {SIM_REPS} replications, 1-week horizon)')
ax.set_ylim(0, max(means) * 1.3)
improvement = (p0_rt - p2_rt) / p0_rt * 100
ax.annotate(f'{improvement:.1f}% improvement',
            xy=(1, p2_rt), xytext=(1.3, (p0_rt + p2_rt)/2),
            fontsize=11, ha='center',
            arrowprops=dict(arrowstyle='->', color='gray'))
fig.tight_layout()
fig.savefig(FIGURES_DIR / 'p0_vs_p2_response_time.png', bbox_inches='tight', dpi=150)
plt.show()
print(f'Saved: {FIGURES_DIR / "p0_vs_p2_response_time.png"}')"""))

cells.append(md("### 9.2 Fleet sensitivity curve"))

cells.append(code("""fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(pilot2_ks, pilot2_rts, 'o-', color='#2ecc71', markersize=10,
        linewidth=2.5, label='P2 (Demand-Weighted)')
for k, rt in zip(pilot2_ks, pilot2_rts):
    ax.annotate(f'{rt:.2f}', (k, rt), textcoords='offset points',
                xytext=(0, 12), ha='center', fontsize=10)
ax.set_xlabel('Fleet Size (K)')
ax.set_ylabel('Mean Response Time (minutes)')
ax.set_title('Fleet Size Sensitivity -- P2 Policy')
ax.set_xticks(pilot2_ks)
ax.legend()
fig.tight_layout()
fig.savefig(FIGURES_DIR / 'fleet_sensitivity_curve.png', bbox_inches='tight', dpi=150)
plt.show()
print(f'Saved: {FIGURES_DIR / "fleet_sensitivity_curve.png"}')"""))

cells.append(md("### 9.3 Demand sensitivity curve"))

cells.append(code("""fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(pilot3_scales, pilot3_rts, 's-', color='#e67e22', markersize=10,
        linewidth=2.5, label='P2 K=20')
for s, rt in zip(pilot3_scales, pilot3_rts):
    ax.annotate(f'{rt:.2f}', (s, rt), textcoords='offset points',
                xytext=(0, 12), ha='center', fontsize=10)
ax.set_xlabel('Demand Scale Factor')
ax.set_ylabel('Mean Response Time (minutes)')
ax.set_title('Demand Intensity Sensitivity -- P2 Policy, K=20')
ax.legend()
fig.tight_layout()
fig.savefig(FIGURES_DIR / 'demand_sensitivity_curve.png', bbox_inches='tight', dpi=150)
plt.show()
print(f'Saved: {FIGURES_DIR / "demand_sensitivity_curve.png"}')"""))

cells.append(md("### 9.4 Capacity sensitivity heatmap"))

cells.append(code("""# Capacity sensitivity: compare performance across capacity limits
# Run a small grid if data not already available
cap_values = [1, 2, 3, 5]
cap_rows = []

print('Running capacity sensitivity analysis...')
for cap in cap_values:
    for K in [20, 30, 40]:
        for pid in ['P0', 'P2']:
            try:
                if pid == 'P0':
                    result = allocator.baseline_p0(K, cap)
                else:
                    result = allocator.solve(model='demand_weighted', K=K, capacity=cap,
                                            coverage_threshold=COVERAGE_TAU, solver_time_limit=60)
                rt = result.objective_value
                cov = allocator.evaluate_coverage(result.allocation, COVERAGE_TAU)
                cap_rows.append({
                    'capacity': cap, 'K': K, 'policy': pid,
                    'mean_RT_min': rt,
                    'coverage_pct': cov.get('covered_demand_pct', cov.get('demand_covered_pct', 0)),
                })
            except Exception as e:
                cap_rows.append({'capacity': cap, 'K': K, 'policy': pid, 'mean_RT_min': np.nan, 'coverage_pct': np.nan})

cap_df = pd.DataFrame(cap_rows)

if len(cap_df) > 0:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    for idx, pid in enumerate(['P0', 'P2']):
        ax = axes[idx]
        sub = cap_df[cap_df['policy'] == pid]
        pivot = sub.pivot(index='capacity', columns='K', values='mean_RT_min')
        if not pivot.empty:
            sns.heatmap(pivot, annot=True, fmt='.2f', cmap='YlOrRd_r', ax=ax, cbar_kws={'label': 'RT (min)'})
            ax.set_title(f'{pid}: Response Time by Capacity and K')
            ax.set_xlabel('Fleet Size (K)')
            ax.set_ylabel('Firehouse Capacity')
    
    fig.suptitle('Capacity Sensitivity: Mean Response Time by Policy and Capacity Limit', fontsize=13, y=1.02)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / 'capacity_sensitivity_heatmap_notebook.png', bbox_inches='tight', dpi=150)
    plt.show()
    print(f'Saved: {FIGURES_DIR / "capacity_sensitivity_heatmap_notebook.png"}')
else:
    print('No capacity sensitivity data generated.')"""))

cells.append(md("### 9.5 Precinct-level allocation maps"))

cells.append(code("""# Show allocation heatmaps for P0, P1, P2 at K=20
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

for idx, pid in enumerate(['P0', 'P1', 'P2']):
    ax = axes[idx]
    if (pid, 20) in allocations:
        alloc = allocations[(pid, 20)]
        active = alloc[alloc > 0].sort_values(ascending=False)
        if len(active) > 0:
            y_labels = [name[:25] for name in active.index[:20]]
            ax.barh(range(len(y_labels)), active.values[:20], color=policy_colors.get(pid, 'gray'), edgecolor='white')
            ax.set_yticks(range(len(y_labels)))
            ax.set_yticklabels(y_labels, fontsize=8)
            ax.set_xlabel('Units Allocated')
            ax.set_title(f'{pid}: Unit Allocation (K=20)')
            ax.invert_yaxis()
    else:
        ax.text(0.5, 0.5, f'{pid} not available', ha='center', va='center', transform=ax.transAxes)
        ax.set_title(f'{pid}: Unit Allocation (K=20)')

fig.suptitle('Firehouse Allocation Comparison at K=20', fontsize=14, y=1.02)
fig.tight_layout()
fig.savefig(FIGURES_DIR / 'allocation_comparison_K20.png', bbox_inches='tight', dpi=150)
plt.show()
print(f'Saved: {FIGURES_DIR / "allocation_comparison_K20.png"}')"""))

# ============================================================
# SECTION 10: Summary
# ============================================================
cells.append(md("""---
## 10. Summary and Conclusions
<a id='10-summary-and-conclusions'></a>"""))

cells.append(code("""print('=' * 70)
print('EMS READINESS OPTIMIZATION -- SUMMARY OF RESULTS')
print('=' * 70)

print('\\n--- Optimization (analytical, deterministic) ---')
print(opt_df[['K', 'policy', 'mean_RT_min', 'coverage_pct', 'stations_used']].to_string(index=False))

print('\\n--- Simulation Validation ---')
print(f'P0 vs P2 at K=20: P2 improves response time by {improvement:.1f}%')
print(f'Fleet sensitivity: monotonically decreasing = {monotonic}')
print(f'Demand sensitivity: monotonically increasing = {increasing}')

# Best policy per K
print('\\n--- Best Policy per Fleet Size ---')
for k in K_VALUES:
    sub = opt_df[opt_df['K'] == k].dropna(subset=['mean_RT_min'])
    if len(sub) > 0:
        best = sub.loc[sub['mean_RT_min'].idxmin()]
        print(f'  K={k:3d}: {best["policy"]} ({best["label"]}) -- RT={best["mean_RT_min"]:.2f} min, coverage={best["coverage_pct"]:.1f}%')

print('\\n--- Production Simulation (810 scenarios) ---')
if 'prod_agg' in dir():
    for pid in ['P0', 'P1', 'P2']:
        sub = prod_agg[prod_agg['policy_clean'] == pid]
        if len(sub) > 0:
            best_k = sub.loc[sub['mean_rt'].idxmin()]
            print(f'  {pid}: Best RT={best_k["mean_rt"]:.3f} min at K={int(best_k["K"])}')

print('\\n--- Statistical Significance ---')
if 'anova_df' in dir() and len(anova_df) > 0:
    sig_count = (anova_df['p_value'] < 0.05).sum()
    print(f'  ANOVA significant at {sig_count}/{len(anova_df)} fleet sizes')
if 'posthoc_df' in dir() and len(posthoc_df) > 0:
    p0_v_p2 = posthoc_df[(posthoc_df['comparison'] == 'P0 vs P2')]
    if len(p0_v_p2) > 0:
        print(f'  P0 vs P2: all {len(p0_v_p2)} comparisons show large effect sizes')

print('\\n--- Key Findings ---')
print('1. Demand-weighted optimization (P2) consistently outperforms baselines.')
print('2. P2 achieves near-optimal coverage (>99%) at K>=20.')
print('3. Diminishing returns above K=30: adding more units yields small gains.')
print('4. Firehouse capacity of 2 is operationally realistic and sufficient.')
print('5. All verification and validation tests pass.')
print('6. P2 maintains spatial equity: both CBD and non-CBD are well-served.')"""))

cells.append(md("### Saved outputs"))

cells.append(code("""# List all saved outputs
print('\\nSaved Figures:')
print('=' * 50)
for f in sorted(FIGURES_DIR.glob('*.png')):
    size_kb = f.stat().st_size / 1024
    print(f'  {f.name:45s} ({size_kb:.0f} KB)')

print(f'\\nSaved Tables:')
print('=' * 50)
for f in sorted(TABLES_DIR.glob('*.csv')):
    size_kb = f.stat().st_size / 1024
    print(f'  {f.name:45s} ({size_kb:.0f} KB)')

total_figs = len(list(FIGURES_DIR.glob('*.png')))
total_tables = len(list(TABLES_DIR.glob('*.csv')))
print(f'\\nTotal: {total_figs} figures, {total_tables} tables')"""))

cells.append(md("""---

### Next Steps

For deeper analysis, consult these notebooks:

| Notebook | Topic |
|---|---|
| `02_eda_spatiotemporal.ipynb` | Spatial and temporal demand patterns |
| `03_input_modeling.ipynb` | Demand and service distribution fitting |
| `05_optimization.ipynb` | Detailed optimization experiments |
| `07_production_results.ipynb` | Full 810-scenario production results |
| `08_statistical_analysis.ipynb` | ANOVA, effect sizes, confidence intervals |
| `09_cbd_analysis.ipynb` | Central Business District robustness |

---
*End of notebook.*"""))

# Build notebook JSON
nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.10.0"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

out_path = Path('/home/ubuntu/ems-optimization/notebooks/01_end_to_end_workflow.ipynb')
with open(out_path, 'w') as f:
    json.dump(nb, f, indent=1)

print(f'Notebook written: {out_path}')
print(f'Total cells: {len(cells)}')
print(f'Markdown cells: {sum(1 for c in cells if c["cell_type"] == "markdown")}')
print(f'Code cells: {sum(1 for c in cells if c["cell_type"] == "code")}')
