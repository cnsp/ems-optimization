# Service & Travel Proxy Model Specification

## 1. Overview

This document describes the **service model** used in the EMS Readiness
Optimization simulation. The model has two components:

| Component | Purpose | Module |
|-----------|---------|--------|
| **Travel-time proxy** | Estimate response time from firehouse to incident | `service/travel_time.py` |
| **Service-time distribution** | Sample on-scene + return-to-available duration | `service/service_time.py` |

Both feed into the SimPy discrete-event simulation (Phase 3).

---

## 2. Travel-Time Proxy

### 2.1 Approach

We approximate travel time with:

$$
t_{\text{travel}} = \frac{d_{\text{haversine}}}{v_{\text{avg}}}
$$

where:

- $d_{\text{haversine}}$ is the great-circle (Haversine) distance between
 the firehouse and the incident/precinct centroid.
- $v_{\text{avg}}$ is a configurable average EMS speed (default: **20 mph**).

### 2.2 Justification

| Consideration | Detail |
|---------------|--------|
| **Why Haversine?** | Simple, reproducible, requires only lat/lon. Manhattan's grid layout means Haversine consistently underestimates road distance by a "detour factor" of ~1.3–1.4, but the relative ordering of firehouse–precinct pairs is preserved. |
| **Why not road-network routing?** | Per the project charter, full network routing is **out of scope**. A distance-based proxy is standard in EMS operations research (Goldberg 2004, Ingolfsson et al. 2008). |
| **Why 20 mph?** | NYC DOT reports average Manhattan traffic speeds of 12–25 mph. EMS vehicles with lights & sirens travel faster than ambient traffic. 20 mph is the midpoint used in prior NYC EMS studies. |

### 2.3 Time-of-Day Variation (Optional)

Speed multipliers can be applied by hour of day:

| Period | Hours | Speed Factor | Effective Speed |
|--------|-------|-------------|----------------|
| Overnight | 00–06 | 1.30 | 26.0 mph |
| AM Peak | 06–10 | 0.75 | 15.0 mph |
| Midday | 10–16 | 0.90 | 18.0 mph |
| PM Peak | 16–20 | 0.70 | 14.0 mph |
| Evening | 20–24 | 1.10 | 22.0 mph |

These factors are derived from NYC DOT speed monitoring data and can be
toggled on/off in `configs/service.yaml`.

### 2.4 Distance Matrix

A pre-computed distance matrix is stored at:

```
data/processed/distance_matrix_firehouse_precinct.csv
```

- **Rows**: 48 Manhattan firehouses (by facility name).
- **Columns**: 30 Manhattan precincts (by precinct number).
- **Values**: Haversine distance in miles.

---

## 3. Service-Time Distribution

### 3.1 Distribution Choice: LogNormal

We model on-scene service time with a **LogNormal** distribution.

**Why LogNormal over Exponential?**

| Criterion | LogNormal | Exponential |
|-----------|-----------|-------------|
| Positivity | ✅ Always > 0 | ✅ Always > 0 |
| Skewness | ✅ Right-skewed (matches EMS data) | ✅ Right-skewed |
| Mode ≠ 0 | ✅ Has a meaningful mode | ❌ Mode = 0 |
| Coefficient of variation | ✅ Flexible (CV < 1 possible) | ❌ Fixed at CV = 1 |
| Empirical fit | ✅ Better fit in EMS literature | ❌ Over-predicts short calls |

### 3.2 Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Mean | 25 minutes | Mid-range of 20–30 min typical in literature |
| Std Dev | 10 minutes | CV ≈ 0.4, consistent with EMS data |

These are converted internally to LogNormal (μ, σ) via moment-matching:

$$
\sigma^2 = \ln\!\left(1 + \frac{\text{Var}}{\text{Mean}^2}\right), \quad
\mu = \ln(\text{Mean}) - \frac{\sigma^2}{2}
$$

### 3.3 What Service Time Covers

The sampled service time represents the **on-scene + return-to-available**
duration. The full call timeline is:

1. **Dispatch delay** — fixed 1.5 min (configurable)
2. **Travel to scene** — from travel-time proxy
3. **On-scene service** — from service-time distribution ← *this component*
4. **Return to available** — included in service-time draw

---

## 4. Limitations & Assumptions

| # | Assumption | Risk | Mitigation |
|---|-----------|------|-----------|
| 1 | Haversine underestimates road distance | Response times may be optimistic | Sensitivity analysis with speed ± 25% |
| 2 | Average speed is constant within a TOD period | Ignores micro-level congestion | TOD factors capture macro patterns |
| 3 | Service time is i.i.d. across calls | Call severity varies | LogNormal captures heterogeneity in tail |
| 4 | No mutual-aid or cross-borough dispatch | Some calls may be served from outside Manhattan | Conservative (overstates Manhattan-only demand) |
| 5 | Precinct centroids represent demand locations | Demand is spread across precinct | Centroid is acceptable for strategic-level analysis |

---

## 5. Configuration

All parameters are centralized in:

- `configs/service.yaml` — speed, service-time distribution, dispatch delay
- `configs/demand.yaml` — base rate, lambda table paths, simulation defaults

---

## 6. References

1. Goldberg, J. B. (2004). *Operations Research Models for the Deployment
 of Emergency Services Vehicles*. EMS Management Journal.
2. Ingolfsson, A., Budge, S., & Erkut, E. (2008). Optimal ambulance
 location with random delays and travel times. *Health Care Management
 Science*, 11(3), 262–274.
3. NYC DOT. *NYC Mobility Report* — average traffic speeds in Manhattan.
4. Lewis, P. A. W., & Shedler, G. S. (1979). Simulation of
 nonhomogeneous Poisson processes by thinning.
 *Naval Research Logistics Quarterly*, 26(3), 403–413.
