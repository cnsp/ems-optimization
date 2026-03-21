---
status: ✅ CURRENT
last_updated: "2026-03-20"
verified: "All metrics, code references, and nomenclature are current as of March 2026"
---
# Demand Model Specification

**EMS Optimization Project - Phase 2: Demand Modeling**

*Last Updated: March 12, 2026*

---

## Executive Summary

This document specifies the stochastic demand models fitted for crash arrivals in the EMS discrete-event simulation. Based on 416,434 Manhattan crash records (2012-2026), we developed:

1. **Baseline Homogeneous Poisson** - Constant rate model (rejected by chi-square test)
2. **Non-Homogeneous Poisson Process (NHPP)** - Recommended model with hourly and day-of-week variation
3. **Spatial Demand Model** - Precinct-level arrival rates

---

## 1. Data Summary

| Metric | Value |
|--------|-------|
| Total crashes | 416,434 |
| Date range | July 1, 2012 - February 20, 2026 |
| Duration | 4,983 days (119,592 hours) |
| Average daily rate | 83.6 crashes/day |
| Average hourly rate | 3.48 crashes/hour |

### Geographic Distribution
- **CBD crashes**: 231,786 (55.7%)
- **Non-CBD crashes**: 184,648 (44.3%)

---

## 2. Homogeneous Poisson Model

### Model Specification
$$N(t) \sim \text{Poisson}(\lambda t)$$

Where:
- λ = 3.482 crashes/hour (constant)

### Goodness-of-Fit Test

| Test | Statistic | p-value | Result |
|------|-----------|---------|--------|
| Chi-square | 723,713.09 | < 0.0001 | **REJECT** |
| Dispersion (Var/Mean) | 2.43 | - | Overdispersed |

**Conclusion**: The homogeneous Poisson assumption is **rejected**. The data shows significant time-varying patterns that require a non-homogeneous model.

### Limitations
- Ignores clear hourly and daily patterns
- Underestimates demand during peak hours
- Overestimates demand during off-peak hours
- Not suitable for realistic simulation

---

## 3. Non-Homogeneous Poisson Process (NHPP)

### Model Specification

The recommended model uses a time-varying arrival rate:

$$\lambda(t) = \lambda_{base} \times f_{hour}(h) \times f_{dow}(d)$$

Where:
- **λ_base** = 3.482 crashes/hour (overall mean rate)
- **f_hour(h)** = hourly factor for hour h ∈ {0, 1, ..., 23}
- **f_dow(d)** = day-of-week factor for day d ∈ {0=Mon, 1=Tue, ..., 6=Sun}

### 3.1 Hourly Factors

| Hour | λ (crashes/hr) | Factor | Description |
|------|----------------|--------|-------------|
| 0 | 3.46 | 0.88 | Midnight |
| 1 | 2.42 | 0.61 | |
| 2 | 2.08 | 0.53 | |
| 3 | 1.93 | 0.49 | |
| 4 | 1.94 | 0.49 | |
| 5 | 1.78 | **0.45** | **Minimum** |
| 6 | 2.17 | 0.55 | |
| 7 | 2.61 | 0.66 | Morning ramp-up |
| 8 | 4.24 | 1.08 | Morning commute |
| 9 | 4.81 | 1.22 | |
| 10 | 4.83 | 1.23 | |
| 11 | 5.03 | 1.28 | |
| 12 | 5.15 | 1.31 | Noon |
| 13 | 5.27 | 1.34 | |
| 14 | 5.76 | 1.47 | Afternoon |
| 15 | 5.20 | 1.32 | |
| 16 | 5.97 | **1.52** | **Peak** |
| 17 | 5.70 | 1.45 | Evening commute |
| 18 | 5.28 | 1.34 | |
| 19 | 4.60 | 1.17 | |
| 20 | 4.04 | 1.03 | |
| 21 | 3.60 | 0.91 | |
| 22 | 3.44 | 0.87 | |
| 23 | 3.10 | 0.79 | |

**Peak Period**: 2 PM - 6 PM (factors > 1.3)
**Low Period**: 3 AM - 6 AM (factors < 0.5)

### 3.2 Day-of-Week Factors

| Day | λ (crashes/day) | Factor |
|-----|-----------------|--------|
| Monday | 78.2 | 0.94 |
| Tuesday | 86.4 | 1.03 |
| Wednesday | 87.1 | 1.04 |
| Thursday | 90.3 | 1.08 |
| **Friday** | **95.8** | **1.15** |
| Saturday | 79.4 | 0.95 |
| **Sunday** | **67.9** | **0.81** |

**Key Insight**: Friday has 41% more crashes than Sunday.

### 3.3 Combined Rate Calculation

**Example**: Friday at 5 PM

```
λ(Friday, 17:00) = 3.482 × 1.45 × 1.15 = 5.81 crashes/hour
```

**Example**: Sunday at 5 AM

```
λ(Sunday, 05:00) = 3.482 × 0.45 × 0.81 = 1.27 crashes/hour
```

---

## 4. Spatial Demand Model

### Precinct-Level Rates

| Precinct | Crashes | λ/hour | λ/day | % Total | Category |
|----------|---------|--------|-------|---------|----------|
| 19 (Midtown East) | 41,097 | 0.344 | 8.25 | 9.9% | **High** |
| 18 (Midtown North) | 35,577 | 0.297 | 7.14 | 8.5% | **High** |
| 14 (Midtown South) | 31,551 | 0.264 | 6.33 | 7.6% | **High** |
| 1 (Financial District) | 27,999 | 0.234 | 5.62 | 6.7% | **High** |
| 17 (Midtown East) | 27,628 | 0.231 | 5.54 | 6.6% | **High** |
| 13 (Lower East Side) | 25,101 | 0.210 | 5.04 | 6.0% | **High** |
| 10 (Chelsea) | 23,796 | 0.199 | 4.78 | 5.7% | **High** |
| ... | ... | ... | ... | ... | ... |
| 22 (Central Park) | 4,209 | 0.035 | 0.84 | 1.0% | Low |
| 50 (Marble Hill) | 765 | 0.006 | 0.15 | 0.2% | Low |
| 52 (Inwood) | 284 | 0.002 | 0.06 | 0.1% | Low |
| 114 (Randall's Island) | 80 | 0.001 | 0.02 | 0.0% | Low |

### High-Demand vs Low-Demand Zones

| Category | Precincts | Combined λ/day |
|----------|-----------|----------------|
| **High (≥75th percentile)** | 19, 18, 14, 1, 17, 13, 10 | 46.7 (55.9%) |
| **Low (≤25th percentile)** | 28, 30, 26, 22, 50, 52, 114 | 5.0 (6.0%) |

---

## 5. CBD vs Non-CBD Patterns

### Overall Rates

| Area | λ (crashes/hour) | λ (crashes/day) | % of Total |
|------|------------------|-----------------|------------|
| CBD | 1.94 | 46.5 | 55.7% |
| Non-CBD | 1.54 | 37.1 | 44.3% |

### Temporal Pattern Differences

| Characteristic | CBD | Non-CBD |
|----------------|-----|---------|
| Peak hour | 14:00 (2 PM) | 16:00 (4 PM) |
| Peak factor | 1.60 | 1.71 |
| Minimum hour | 4 AM | 3 AM |
| Peak day | Friday | Friday |
| Weekend dropoff | Sharper | Moderate |

**Insight**: CBD peaks earlier (business hours) while non-CBD peaks during evening commute.

---

## 6. Implementation for Simulation

### Arrival Generation Algorithm

```python
import numpy as np
import pandas as pd

# Load rate tables
hourly_factors = pd.read_csv('demand_lambda_hourly.csv').set_index('hour')['factor']
dow_factors = pd.read_csv('demand_lambda_dow.csv').set_index('dow')['factor']
precinct_probs = pd.read_csv('demand_lambda_precinct.csv').set_index('precinct')['pct_of_total'] / 100

BASE_RATE = 3.482 # crashes per hour

def get_arrival_rate(hour: int, dow: int, area: str = 'all') -> float:
 """
 Get arrival rate λ(t) for given time.
 
 Args:
 hour: Hour of day (0-23)
 dow: Day of week (0=Monday, 6=Sunday)
 area: 'all', 'cbd', or 'non_cbd'
 
 Returns:
 Arrival rate in crashes per hour
 """
 rate = BASE_RATE * hourly_factors[hour] * dow_factors[dow]
 
 if area == 'cbd':
 rate *= 0.557 # CBD proportion
 elif area == 'non_cbd':
 rate *= 0.443 # Non-CBD proportion
 
 return rate

def generate_next_arrival(current_time: float, dt: float = 1.0) -> float:
 """
 Generate next arrival time using thinning algorithm.
 
 Args:
 current_time: Current simulation time (hours from start)
 dt: Time step for rate evaluation
 
 Returns:
 Time until next arrival (hours)
 """
 # Get maximum rate in next period
 hour = int(current_time % 24)
 dow = int((current_time // 24) % 7)
 lambda_max = get_arrival_rate(hour, dow) * 1.1 # Safety margin
 
 t = 0
 while True:
 # Generate candidate arrival
 t += np.random.exponential(1 / lambda_max)
 
 # Accept/reject
 new_hour = int((current_time + t) % 24)
 new_dow = int(((current_time + t) // 24) % 7)
 lambda_t = get_arrival_rate(new_hour, new_dow)
 
 if np.random.random() < lambda_t / lambda_max:
 return t

def assign_precinct() -> int:
 """Randomly assign crash to precinct based on demand distribution."""
 return np.random.choice(precinct_probs.index, p=precinct_probs.values)
```

### Validation Checks

Before simulation, verify:
1. Generated hourly counts match expected patterns (within 10%)
2. Day-of-week distribution matches historical (within 5%)
3. Precinct assignments match spatial distribution

---

## 7. Model Limitations

1. **Stationarity assumption**: Factors assumed constant across years
2. **Independence**: Events assumed independent (no clustering)
3. **Weather effects**: Not modeled (could affect rates ±20%)
4. **Special events**: Holidays, major events not explicitly modeled
5. **Trend**: Long-term trend not captured (data spans 13+ years)

### Recommendations for Future Work

1. Include seasonal (monthly) factors
2. Add weather covariates
3. Model holiday effects
4. Consider Hawkes process for event clustering

---

## 8. Seasonal Patterns

### Monthly Variation Analysis

Analysis of 416,434 Manhattan crash records reveals moderate seasonal variation in demand:

| Month | Factor | Season |
|-------|--------|--------|
| January | 0.876 | Winter |
| February | 0.822 | Winter (trough) |
| March | 0.956 | Spring |
| April | 0.887 | Spring |
| May | 1.067 | Spring |
| June | 1.072 | Summer |
| July | 1.056 | Summer |
| August | 1.049 | Summer |
| September | 1.071 | Fall |
| October | 1.103 | Fall (peak) |
| November | 1.026 | Fall |
| December | 1.016 | Winter |

### Statistical Tests

| Test | Statistic | p-value | Result |
|------|-----------|---------|--------|
| Chi-square (uniformity) | — | < 0.001 | **Reject** |
| ANOVA (across months) | — | < 0.001 | **Significant** |
| Kruskal-Wallis | — | < 0.001 | **Significant** |

### Key Metrics
- **Coefficient of variation:** 9% (moderate)
- **Seasonal amplitude:** 28% (peak-to-trough range)
- **Peak month:** October (factor = 1.103)
- **Trough month:** February (factor = 0.822)

### Implications for Simulation

While seasonal variation is statistically significant, its magnitude is **moderate** relative to within-day patterns:
- **Hourly variation:** Factor range 0.5–1.6 (amplitude ~110%)
- **Day-of-week variation:** Factor range 0.85–1.15 (amplitude ~30%)
- **Monthly/seasonal variation:** Factor range 0.82–1.10 (amplitude ~28%)

The NHPP model uses an annual average rate, which is a **reasonable approximation** because:
1. Hourly patterns dominate (10× larger amplitude)
2. The maximum seasonal factor (1.103) is modest
3. Policy rankings are robust to demand multipliers up to 2.0× (Experiment 3), far exceeding seasonal variation

For **high-fidelity future models**, monthly factors could be incorporated as an additional modulation layer in the NHPP intensity function:
```
λ(t) = λ_base × f_hour(h) × f_dow(d) × f_month(m)
```

### Seasonal Visualizations

See `results/analysis/figures/seasonal_patterns.png`, `seasonal_decomposition.png`, and `seasonal_heatmap.png` for detailed seasonal analysis plots.

---

## 9. Output Files

| File | Location | Description |
|------|----------|-------------|
| `demand_lambda_hourly.csv` | `data/processed/` | 24 hourly rates with CBD/non-CBD factors |
| `demand_lambda_dow.csv` | `data/processed/` | 7 day-of-week factors |
| `demand_lambda_precinct.csv` | `data/processed/` | Precinct-level rates |
| `demand_model_summary.json` | `data/processed/` | Model summary statistics |
| `fig_demand_model_fit.png` | `results/figures/` | Diagnostic plots |
| `fig_hourly_rates.png` | `results/figures/` | CBD vs Non-CBD comparison |
| `fig_precinct_demand.png` | `results/figures/` | Precinct demand bar chart |

---

## References

1. Law, A.M. (2015). *Simulation Modeling and Analysis*, 5th ed. McGraw-Hill.
2. Ross, S.M. (2014). *Introduction to Probability Models*, 11th ed. Academic Press.
3. NYC Open Data - Motor Vehicle Collisions (NYPD)
