# EMS Optimization: EDA & Data Split Methodology Summary

## Part 1 — EDA of Crash Counts by Dimension

The project contains comprehensive EDA across all four dimensions. Here's what exists and where:

---

### 1.1 Hourly Patterns

| Source | What It Contains |
|--------|-----------------|
| `notebooks/02_eda_spatiotemporal.ipynb` (Cells 9–12) | Bar charts of hourly crash distribution (overall + CBD vs Non-CBD split); summary table of hourly counts and percentages |
| `notebooks/03_input_modeling.ipynb` (Cells 5, 7) | Hourly factor table display and visualization; bar chart of hourly rate factors with reference line at 1.0 |
| `docs/demand_model_spec.md` §3.1 | Full 24-row table of λ per hour, multiplicative factors, and annotations (peak at 4 PM = 1.52, trough at 5 AM = 0.45) |
| **Figures** | `results/figures/fig_hourly_demand.png` — hourly distribution (overall + CBD/non-CBD) |
| | `results/figures/fig_hourly_rates.png` — CBD vs Non-CBD hourly rate comparison |

**Key finding:** Peak 2–6 PM (factors >1.3), trough 3–6 AM (factors <0.5). CBD peaks at 2 PM; Non-CBD peaks at 4 PM.

---

### 1.2 Day-of-Week Patterns

| Source | What It Contains |
|--------|-----------------|
| `notebooks/02_eda_spatiotemporal.ipynb` (Cells 13–16) | Bar charts of DOW crash counts (overall + CBD/Non-CBD); weekday vs weekend comparison statistics |
| `notebooks/03_input_modeling.ipynb` (Cell 6) | Day-of-week factor table |
| `docs/demand_model_spec.md` §3.2 | 7-row factor table — Friday highest (1.15), Sunday lowest (0.81); "Friday has 41% more crashes than Sunday" |
| **Figures** | `results/figures/fig_daily_demand.png` — DOW distribution with CBD comparison |

**Key finding:** Weekdays > weekends. Friday peak (95.8/day), Sunday trough (67.9/day). CBD shows sharper weekday concentration.

---

### 1.3 Seasonal / Monthly Patterns

| Source | What It Contains |
|--------|-----------------|
| `notebooks/02_eda_spatiotemporal.ipynb` (Cells 17–19) | Monthly distribution bar chart across all years; yearly trend line; seasonal grouping summary |
| `scripts/analyze_seasonal_patterns.py` | Dedicated script computing monthly factors, statistical tests (chi-square, ANOVA, Kruskal-Wallis), decomposition, and heatmaps |
| `docs/demand_model_spec.md` §8 | Full 12-month factor table (October peak = 1.103, February trough = 0.822); statistical test results (all p < 0.001); amplitude analysis (28% peak-to-trough) |
| **Figures** | `results/figures/fig_temporal_trends.png` — monthly + yearly trend |
| | `results/figures/seasonal_patterns.png` — seasonal pattern visualization |
| | `results/figures/seasonal_decomposition.png` — time-series decomposition |
| | `results/figures/seasonal_heatmap.png` — month × year heatmap |

**Key finding:** Seasonal variation is statistically significant but **moderate** (CV = 9%, amplitude 28%) compared to hourly variation (amplitude ~110%). October is the peak; February is the trough. The NHPP model uses annual averages, justified because seasonal amplitude is far below the demand-multiplier robustness range tested (up to 2.0×).

---

### 1.4 Geographic / Spatial Patterns

| Source | What It Contains |
|--------|-----------------|
| `notebooks/02_eda_spatiotemporal.ipynb` (Cells 20–34) | Hexbin crash heatmap over Manhattan; choropleth by precinct crash count; firehouse overlay on density map; CBD vs Non-CBD pie/bar comparison (55.7% vs 44.3%); top-10 precincts table |
| `notebooks/03_input_modeling.ipynb` (Cells 9–12) | Precinct-level rate table; CBD vs Non-CBD rate comparison |
| `docs/demand_model_spec.md` §4–5 | Full precinct-level λ table (Precinct 19 highest at 9.9%); high-demand vs low-demand zone breakdown; CBD vs Non-CBD overall rates and temporal pattern differences |
| **Figures** | `results/figures/fig_crash_heatmap.png` — hexbin density map |
| | `results/figures/fig_precinct_demand.png` — precinct-level bar chart |
| | `results/figures/fig_precinct_density.png` — choropleth density |
| | `results/figures/fig_firehouses_map.png` — firehouses overlaid on crash density |

**Key finding:** Top 7 precincts (Midtown, Financial District, Lower East Side, Chelsea) account for 55.9% of demand. CBD captures 55.7% of all crashes. Precinct 19 (Midtown East) is the single highest-demand zone at 9.9%.

---

### EDA Coverage Summary Matrix

| Dimension | Notebook 02 (EDA) | Notebook 03 (Modeling) | demand_model_spec.md | Figures |
|-----------|:--:|:--:|:--:|:--:|
| **Hourly** | ✅ Charts + table | ✅ Factor table + viz | ✅ Full 24-hr table | `fig_hourly_demand.png`, `fig_hourly_rates.png` |
| **Day-of-Week** | ✅ Charts + weekday/weekend | ✅ Factor table | ✅ 7-day table | `fig_daily_demand.png` |
| **Seasonal/Monthly** | ✅ Monthly + yearly trends | ❌ | ✅ 12-month table + tests | `fig_temporal_trends.png`, `seasonal_*.png` (×3) |
| **Geographic** | ✅ Heatmap + choropleth + precinct + CBD | ✅ Precinct rates + CBD | ✅ Precinct table + CBD split | `fig_crash_heatmap.png`, `fig_precinct_*.png`, `fig_firehouses_map.png` |

---

## Part 2 — Data Split Methodology for Predictive/Staging Optimization

### Short Answer

**There is no train/test split.** The project does not build a predictive ML model. Instead, it uses **all** historical data to calibrate a stochastic demand model (NHPP), which then drives a simulation-optimization pipeline.

---

### 2.1 How Historical Data Was Used

The methodology is a **simulation-based optimization** approach, not a supervised learning pipeline:

```
Historical Crash Data (416,434 records, 2012–2026)
        │
        ▼
   Demand Model Calibration (NHPP)
   ├── Hourly factors (24 values)
   ├── Day-of-week factors (7 values)
   └── Precinct proportions (22 values)
        │
        ▼
   Discrete-Event Simulation (DES)
   ├── Generates crash arrivals using NHPP thinning algorithm
   ├── Simulates dispatch, travel, and service
   └── Evaluates response times under each allocation policy
        │
        ▼
   Allocation Optimization (MIP)
   ├── P0: Uniform allocation (baseline)
   ├── P1: Demand-proportional allocation
   └── P2: Demand-weighted optimized allocation (MIP)
```

### 2.2 NHPP Demand Model Calibration

From `docs/demand_model_spec.md` and `scripts/demand_modeling.py`:

1. **All 416,434 Manhattan crash records** were used to compute empirical rates — no holdout
2. **Hourly factors** `f_hour(h)`: Computed as (observed crashes in hour h) / (expected under uniform), yielding 24 multiplicative factors
3. **DOW factors** `f_dow(d)`: Same approach, 7 factors
4. **Precinct proportions**: Fraction of total crashes per precinct → spatial probability distribution
5. **Base rate** λ_base = 3.482 crashes/hour (total crashes ÷ total hours)
6. **Combined intensity**: `λ(t) = λ_base × f_hour(h) × f_dow(d)` with spatial assignment via precinct probabilities

The homogeneous Poisson model was **rejected** via chi-square (stat = 723,713, p < 0.0001). The NHPP was validated through goodness-of-fit checks documented in `fig_demand_model_fit.png`.

### 2.3 How Staging Allocations Were Determined

From `docs/experimental_design.md`:

- **No data split for training/testing** — instead, robustness is established through **experimental design**:
  - **Experiment 1** (90 runs): Compare 3 policies at baseline (K=20, δ=1.0)
  - **Experiment 2** (540 runs): Fleet size sensitivity (K ∈ {15, 20, 25, 30, 35, 40})
  - **Experiment 3** (540 runs): Demand multiplier sensitivity (δ ∈ {0.5, 0.75, 1.0, 1.25, 1.5, 2.0})
  - **Experiment 4** (270 runs): Service time robustness (μ_s ∈ {20, 25, 30} min)
- **1,440 total simulation runs**, each 168 hours (1 week), 30 replications per scenario with **Common Random Numbers (CRN)** for variance reduction
- Statistical analysis via paired t-tests, ANOVA, and confidence intervals

### 2.4 Why No Train/Test Split Was Needed

| Traditional ML Approach | This Project's Approach |
|------------------------|------------------------|
| Split data into train/test | Use all data for rate estimation |
| Fit predictive model on train | Calibrate NHPP intensity function |
| Evaluate on test set | Evaluate via simulation experiments |
| Risk: overfitting | Risk mitigated by: simple parametric model (53 parameters), demand sensitivity experiments (δ up to 2.0×), seasonal robustness analysis |

The demand model has only **53 free parameters** (24 hourly + 7 DOW + 22 precinct proportions), estimated from 416K observations — effectively zero overfitting risk. Robustness is validated by showing policy rankings hold across demand multipliers from 0.5× to 2.0×, which far exceeds real-world seasonal variation (0.82–1.10).

---

### Key File Locations

| Purpose | File |
|---------|------|
| EDA notebook | `notebooks/02_eda_spatiotemporal.ipynb` |
| Input modeling notebook | `notebooks/03_input_modeling.ipynb` |
| Demand model specification | `docs/demand_model_spec.md` |
| Experimental design | `docs/experimental_design.md` |
| Seasonal analysis script | `scripts/analyze_seasonal_patterns.py` |
| Demand modeling script | `scripts/demand_modeling.py` |
| Processed hourly rates | `data/processed/demand_lambda_hourly.csv` |
| Processed DOW factors | `data/processed/demand_lambda_dow.csv` |
| Processed precinct rates | `data/processed/demand_lambda_precinct.csv` |
| Model summary | `data/processed/demand_model_summary.json` |
