# Conceptual Model — EMS Discrete-Event Simulation

> **Document version:** 1.0 
> **Date:** March 12, 2026 
> **Project:** EMS Readiness Optimization — Manhattan, NYC 
> **Phase:** 4 (Simulation Design) 
> **Status:** Approved for implementation

---

## Table of Contents

1. [System Description](#1-system-description) 
2. [Entities](#2-entities) 
3. [Resources](#3-resources) 
4. [Queues](#4-queues) 
5. [Events](#5-events) 
6. [State Variables](#6-state-variables) 
7. [Dispatch Logic](#7-dispatch-logic) 
8. [Performance Measures](#8-performance-measures) 
9. [Time Representation](#9-time-representation) 
10. [Random Phenomena](#10-random-phenomena) 
11. [Event Flow Diagram](#11-event-flow-diagram) 
12. [Assumptions and Limitations](#12-assumptions-and-limitations) 
13. [References](#13-references) 

---

## 1. System Description

### 1.1 Purpose

This simulation evaluates **strategic EMS unit staging policies** under
stochastic crash-driven demand in Manhattan, New York City. The central
research question is:

> *Given K ambulance units and 48 candidate firehouses, which allocation
> policy minimises average response time and maximises the fraction of
> incidents served within an 8-minute threshold?*

Five candidate policies are compared:

| Code | Policy | Source |
|------|--------|--------|
| P0 | Uniform allocation | Baseline heuristic |
| P1 | Demand-proportional allocation | Baseline heuristic |
| P2 | Demand-weighted optimisation | MIP (Phase 3) |
| P2-alt | P-median selection | MIP (Phase 3) |
| P2-cov | Maximal coverage | MIP (Phase 3) |

### 1.2 Study Type — Terminating Simulation

The simulation is classified as a **terminating** (finite-horizon) simulation
rather than a steady-state simulation.

| Criterion | Rationale |
|-----------|-----------|
| **Natural endpoint** | Each replication covers a fixed horizon (default 168 hours = 1 week). The system has a well-defined start (empty-and-idle) and end. |
| **Initial conditions** | At *t = 0* every EMS unit is available at its assigned firehouse and no incidents are in queue. This is a realistic depiction of a fresh deployment cycle. |
| **Cyclic non-stationarity** | Crash demand follows a Non-Homogeneous Poisson Process with pronounced hourly and day-of-week patterns (λ varies by factor ≈ 0.3–2.1× from base rate 3.48 /hr). Steady-state assumptions require stationarity, which does not hold here. |
| **Policy evaluation horizon** | Decision-makers evaluate staging plans on a weekly operational cycle, matching the 168-hour horizon. |
| **Replication strategy** | Statistical inference is drawn from *R* independent replications (default *R* = 30), each with a different random-number stream, following the method of independent replications for terminating simulations (Law 2015, Ch. 9). |

Because the simulation is terminating, there is **no warm-up period** to
discard. Performance measures are computed over the entire horizon of each
replication.

### 1.3 System Boundary

The system boundary encompasses:

- **Included:** Crash incident arrivals, EMS unit dispatch, travel to scene,
 on-scene service, return-to-available transition, queueing of unserved
 incidents.
- **Excluded:** Real-time unit relocation, congestion-dependent travel,
 full road-network routing, dispatch priority / preemption, hospital
 turnaround delays, non-crash EMS calls.

---

## 2. Entities

### 2.1 Incident (Temporary Entity)

An **Incident** represents a motor-vehicle crash event that requires exactly
one EMS unit for service. Incidents are created dynamically by the arrival
process and destroyed after service completion.

| Attribute | Type | Description |
|-----------|------|-------------|
| `incident_id` | int | Unique sequential identifier |
| `arrival_time` | float | Simulation clock time of occurrence (hours) |
| `precinct` | int | NYPD precinct where the crash occurs (spatial allocation) |
| `location_lat` | float | Latitude of incident (precinct centroid proxy) |
| `location_lon` | float | Longitude of incident (precinct centroid proxy) |
| `assigned_unit` | str / None | ID of the EMS unit assigned (None while queued) |
| `dispatch_time` | float | Clock time when a unit is dispatched |
| `service_start_time` | float | Clock time when unit arrives on scene |
| `service_end_time` | float | Clock time when unit completes service |
| `dispatch_delay` | float | `dispatch_time − arrival_time` (wait in queue + fixed processing) |
| `travel_time` | float | Travel time from unit's current location to incident (minutes) |
| `service_time` | float | On-scene service duration (minutes) |
| `response_time` | float | `dispatch_delay + travel_time` (total from crash to unit arrival on scene) |

### 2.2 Entity Lifecycle

```
Created ──► Queued (if no unit available) ──► Dispatched ──► In Service ──► Completed (destroyed)
```

---

## 3. Resources

### 3.1 EMS Unit (Permanent Entity)

EMS Units are the **servers** in this system. They are stationed at FDNY
firehouses according to the allocation policy under evaluation and remain
in the system for the entire simulation horizon.

| Attribute | Type | Description |
|-----------|------|-------------|
| `unit_id` | str | Unique identifier (e.g., `E026_1` for unit 1 at Engine 26) |
| `home_firehouse` | str | Assigned firehouse (FacilityName) |
| `home_lat` | float | Latitude of home firehouse |
| `home_lon` | float | Longitude of home firehouse |
| `current_lat` | float | Current latitude (home when idle, incident location when busy) |
| `current_lon` | float | Current longitude |
| `status` | enum | `AVAILABLE` · `DISPATCHED` · `ON_SCENE` · `RETURNING` |
| `busy_since` | float / None | Clock time when unit last became busy |
| `total_busy_time` | float | Cumulative busy time (for utilisation calculation) |
| `calls_served` | int | Count of incidents served |

### 3.2 Capacity

Total fleet size **K** is a scenario parameter (default values: 20, 30, 40, 48).
Units are distributed across 48 Manhattan firehouses subject to:

- Per-firehouse capacity cap: **C = 2** units maximum (default; sensitivity analysis tested C = 1–5).
- Allocation vector **x** = (x₁, x₂, …, x₄₈) where Σxᵢ = K and 0 ≤ xᵢ ≤ C.

The allocation vector is determined **before** the simulation begins and remains
**fixed** throughout the replication (static staging policy).

### 3.3 Firehouse Locations

48 Manhattan FDNY firehouses serve as candidate staging locations. Their
coordinates are loaded from `data/raw/FDNY_Firehouse_Listing_20260223.csv`.
A pre-computed distance matrix (`data/processed/distance_matrix_firehouse_precinct.csv`)
gives Haversine distances between each firehouse and each of the 30 Manhattan
precinct centroids.

---

## 4. Queues

### 4.1 Waiting Incidents Queue

| Property | Specification |
|----------|--------------|
| **Name** | `incident_queue` |
| **Discipline** | First-In, First-Out (FIFO) |
| **Capacity** | Unlimited (no balking or reneging) |
| **Trigger** | An arriving incident enters the queue when **all** EMS units across **all** firehouses are currently busy. |
| **Drain** | When a unit completes service and becomes available, the longest-waiting incident (queue head) is immediately dispatched. |
| **Tracked statistics** | Queue length over time, maximum queue length, time-weighted average queue length, individual waiting times. |

### 4.2 Queueing Dynamics

The system is analogous to a spatially distributed **M(t)/G/K** queue:

- **M(t):** Non-Homogeneous Poisson arrivals (time-varying rate).
- **G:** General (LogNormal) service-time distribution.
- **K:** Total EMS units across all firehouses.

Unlike a classical queue, travel time depends on the dispatched unit's
location relative to the incident, introducing a spatial component absent
from standard queueing models. This is a key motivation for using simulation
rather than analytical queueing formulae.

---

## 5. Events

The simulation is driven by five event types. Each is described with its
triggering condition, detailed logic, and state transitions.

### 5.1 Incident Arrival

| Property | Detail |
|----------|--------|
| **Trigger** | Generated by the NHPP thinning algorithm at rate λ(t). |
| **Frequency** | Base rate 3.48 /hr × hourly factor × day-of-week factor. |
| **Logic** | |

```
INCIDENT_ARRIVAL(t):
 1. Create new Incident entity with arrival_time = t
 2. Assign precinct via multinomial draw from precinct probabilities
 3. Set incident location to precinct centroid (lat, lon)
 4. IF any EMS unit has status == AVAILABLE:
 → trigger DISPATCH_DECISION(incident)
 ELSE:
 → enqueue incident in incident_queue (FIFO)
 5. Schedule next INCIDENT_ARRIVAL via thinning algorithm
```

### 5.2 Dispatch Decision

| Property | Detail |
|----------|--------|
| **Trigger** | (a) New incident arrives and ≥ 1 unit is available, OR (b) a unit completes service and the queue is non-empty. |
| **Logic** | |

```
DISPATCH_DECISION(incident):
 1. Compute travel time from each AVAILABLE unit to incident location:
 t_travel(u, inc) = haversine(u.current_lat, u.current_lon,
 inc.location_lat, inc.location_lon)
 / effective_speed(hour_of_day)
 2. Select unit u* = argmin { t_travel(u, inc) : u ∈ AVAILABLE }
 Tie-breaking: lowest unit_id (deterministic)
 3. Set u*.status = DISPATCHED
 4. Set incident.assigned_unit = u*.unit_id
 5. Set incident.dispatch_time = current_time
 6. Add fixed dispatch processing delay δ = 1.5 minutes
 7. Compute travel_time = t_travel(u*, inc)
 8. Schedule SERVICE_START at t + δ/60 + travel_time/60
 (all converted to hours for the simulation clock)
```

### 5.3 Service Start

| Property | Detail |
|----------|--------|
| **Trigger** | Scheduled by DISPATCH_DECISION after dispatch delay + travel time elapses. |
| **Logic** | |

```
SERVICE_START(incident, unit):
 1. Set unit.status = ON_SCENE
 2. Set unit.current_lat = incident.location_lat
 3. Set unit.current_lon = incident.location_lon
 4. Set incident.service_start_time = current_time
 5. Draw service_duration ~ LogNormal(μ=3.136, σ=0.385)
 [moment-matched: mean=25 min, std=10 min]
 6. Schedule SERVICE_COMPLETION at current_time + service_duration/60
```

### 5.4 Service Completion

| Property | Detail |
|----------|--------|
| **Trigger** | Scheduled by SERVICE_START after service duration elapses. |
| **Logic** | |

```
SERVICE_COMPLETION(incident, unit):
 1. Set incident.service_end_time = current_time
 2. Record incident performance metrics
 3. Set unit.status = AVAILABLE
 4. Set unit.current_lat = unit.home_lat (return to firehouse)
 5. Set unit.current_lon = unit.home_lon
 6. Update unit.total_busy_time += (current_time − unit.busy_since)
 7. Increment unit.calls_served
 8. IF incident_queue is NOT empty:
 → dequeue oldest incident
 → trigger DISPATCH_DECISION(dequeued_incident)
```

> **Note on return travel:** The unit is modelled as returning to its home
> firehouse **instantaneously** upon service completion. This is a
> simplifying assumption; the service-time distribution is calibrated to
> absorb the return component (see § 12, Assumption A-7).

### 5.5 End of Simulation

| Property | Detail |
|----------|--------|
| **Trigger** | Simulation clock reaches the horizon *T* (default 168 hours). |
| **Logic** | |

```
END_OF_SIMULATION(T):
 1. Stop generating new incident arrivals
 2. Allow in-progress services to complete (drain phase)
 3. For any incidents still in queue: mark as "unserved"
 4. Compute replication-level summary statistics:
 a. Average dispatch delay
 b. Average response time
 c. Fraction of incidents with response_time ≤ τ (8 min)
 d. Maximum and mean queue length
 e. Per-unit utilisation = total_busy_time / T
 f. Total incidents served / arrived / unserved
 5. Return replication results
```

---

## 6. State Variables

State variables define the complete system state at any point in simulated
time. They are updated exclusively by the event routines described in § 5.

### 6.1 Core State

| Variable | Type | Description |
|----------|------|-------------|
| `sim_clock` | float | Current simulation time (hours from *t = 0*) |
| `units` | list[EMS_Unit] | All EMS unit objects with current attributes |
| `available_units` | set[str] | Set of unit IDs with status `AVAILABLE` |
| `incident_queue` | deque[Incident] | FIFO queue of waiting incidents |
| `active_incidents` | dict[int, Incident] | Incidents currently being served |
| `completed_incidents` | list[Incident] | All completed incident records |

### 6.2 Statistical Accumulators

| Accumulator | Type | Updated By |
|-------------|------|------------|
| `total_dispatch_delay` | float | SERVICE_START |
| `total_response_time` | float | SERVICE_START |
| `total_service_time` | float | SERVICE_COMPLETION |
| `count_within_threshold` | int | SERVICE_START (if response_time ≤ τ) |
| `count_delayed` | int | DISPATCH_DECISION (if dispatch_delay > 0) |
| `max_queue_length` | int | INCIDENT_ARRIVAL / SERVICE_COMPLETION |
| `queue_length_area` | float | Time-weighted area under queue-length curve |
| `incidents_arrived` | int | INCIDENT_ARRIVAL |
| `incidents_served` | int | SERVICE_COMPLETION |

### 6.3 Configuration Parameters

| Parameter | Symbol | Default | Source |
|-----------|--------|---------|--------|
| Simulation horizon | *T* | 168 h (1 week) | `configs/demand.yaml` |
| Total EMS units | *K* | 40 | `configs/optimization.yaml` |
| Per-firehouse capacity | *C* | 5 | `configs/optimization.yaml` |
| Base arrival rate | λ₀ | 3.48 /hr | `configs/demand.yaml` |
| Average EMS speed | *v* | 20 mph | `configs/service.yaml` |
| Service time mean | μ_s | 25 min | `configs/service.yaml` |
| Service time std | σ_s | 10 min | `configs/service.yaml` |
| Dispatch processing delay | δ | 1.5 min | `configs/service.yaml` |
| Response-time threshold | τ | 8 min | `configs/optimization.yaml` |
| Replications | *R* | 30 | `configs/demand.yaml` |
| Random seed | — | 42 | `configs/demand.yaml` |

---

## 7. Dispatch Logic

### 7.1 Nearest-Available Dispatch

The dispatch policy is **nearest-available**: the available unit with the
shortest estimated travel time to the incident location is selected.

**Travel-time estimate:**

$$
t_{travel}(u, j) = \frac{d_{haversine}(u_{loc},\; j_{loc})}{v_{eff}(h)}
$$

where:

- $d_{haversine}$ is the great-circle distance in miles,
- $v_{eff}(h) = v_{base} \times f_{TOD}(h)$ is the effective speed at hour *h*,
- $f_{TOD}$ is the time-of-day speed multiplier from `configs/service.yaml`.

### 7.2 Tie-Breaking Rule

When multiple available units have identical minimum travel times (e.g., two
units co-located at the same firehouse), the unit with the **lowest unit ID**
(lexicographic order) is selected. This provides deterministic, reproducible
behaviour.

### 7.3 Queue Discipline

- **FIFO:** When a unit becomes available and the queue is non-empty, the
 incident that has been waiting the longest (head of the deque) is dispatched
 first.
- **No priority classes:** All incidents are treated equally regardless of
 severity. Priority dispatch is listed as out-of-scope.
- **No preemption:** Once a unit begins serving an incident, it cannot be
 recalled for a higher-priority call.

### 7.4 Dispatch upon Service Completion

When a unit completes service and returns to the available pool, the system
checks the queue before the unit becomes idle. If incidents are waiting,
dispatch occurs immediately—there is no idle gap between consecutive services
when the queue is non-empty.

---

## 8. Performance Measures

All measures are computed per replication and then summarised across *R*
replications using point estimates and 95% confidence intervals.

### 8.1 Primary Measures

| Measure | Formula | Units |
|---------|---------|-------|
| **Average dispatch delay** | $\bar{W}_q = \frac{1}{N}\sum_{i=1}^{N} (d_i.\text{dispatch\_time} - d_i.\text{arrival\_time})$ | minutes |
| **Average response time** | $\bar{R} = \frac{1}{N}\sum_{i=1}^{N} (d_i.\text{dispatch\_delay} + d_i.\text{travel\_time})$ | minutes |
| **Coverage (% within τ)** | $P(\text{resp} \leq \tau) = \frac{1}{N}\sum_{i=1}^{N} \mathbb{1}[R_i \leq \tau]$ | % |

### 8.2 Secondary Measures

| Measure | Formula | Units |
|---------|---------|-------|
| **Mean queue length** | $\bar{L}_q = \frac{1}{T}\int_0^T Q(t)\, dt$ (time-weighted) | incidents |
| **Maximum queue length** | $\max_{t \in [0,T]} Q(t)$ | incidents |
| **Unit utilisation** | $\rho_u = \frac{\text{busy\_time}_u}{T}$, system avg: $\bar{\rho} = \frac{1}{K}\sum \rho_u$ | fraction |
| **Number of delayed incidents** | $N_{delayed} = \sum \mathbb{1}[W_{q,i} > 0]$ | count |
| **Total incidents served** | $N_{served}$ | count |
| **Fraction unserved at horizon** | $N_{unserved} / N_{arrived}$ | fraction |

### 8.3 Statistical Output Analysis

For each performance measure *Y*, across *R* independent replications:

- Point estimate: $\bar{Y} = \frac{1}{R}\sum_{r=1}^{R} Y_r$
- Standard error: $SE = s_Y / \sqrt{R}$
- 95% confidence interval: $\bar{Y} \pm t_{R-1, 0.025} \cdot SE$
- Comparison across policies via paired-*t* or Welch's *t*-test on
 replication-level means using Common Random Numbers (CRN).

---

## 9. Time Representation

### 9.1 Simulation Clock

| Property | Specification |
|----------|--------------|
| **Time model** | Continuous (real-valued) |
| **Units** | Hours from simulation start (*t = 0*) |
| **Advancement** | Next-event time advance (SimPy process-based) |
| **Framework** | SimPy 4.x (Python process-interaction DES library) |

The simulation clock does **not** advance in fixed increments. Instead, it
jumps from one scheduled event to the next, making it efficient even for
long horizons with variable inter-event gaps.

### 9.2 Simulation Horizon

| Parameter | Default | Notes |
|-----------|---------|-------|
| Horizon *T* | 168 hours | 1 full week (Mon 00:00 – Sun 23:59) |
| Start hour | 0 (Monday midnight) | Configurable; aligns with DOW factor indexing |
| Configurable? | Yes | Via `configs/demand.yaml → simulation.default_duration_hours` |

The 168-hour (1-week) horizon captures the full weekly demand cycle, including
weekday/weekend variation and all hourly peaks.

### 9.3 Time Conversions

All internal calculations use **hours** as the canonical unit. When service
times and travel times are drawn in minutes, they are divided by 60 before
being added to the simulation clock.

---

## 10. Random Phenomena

### 10.1 Incident Arrivals — Non-Homogeneous Poisson Process (NHPP)

| Property | Specification |
|----------|--------------|
| **Distribution** | Non-Homogeneous Poisson Process |
| **Algorithm** | Lewis–Shedler thinning (acceptance–rejection) |
| **Base rate** | λ₀ = 3.48 crashes / hour (Manhattan-wide) |
| **Rate function** | λ(t) = λ₀ × f_hour(h(t)) × f_dow(d(t)) |
| **Hourly factors** | Loaded from `data/processed/demand_lambda_hourly.csv` |
| **DOW factors** | Loaded from `data/processed/demand_lambda_dow.csv` |
| **Spatial allocation** | Multinomial draw over 30 precincts, probabilities from `data/processed/demand_lambda_precinct.csv` |
| **Envelope rate** | λ_max = λ₀ × max(f_hour) × max(f_dow) |

**Thinning Algorithm Summary:**

```
1. Compute λ_max over the simulation horizon
2. Generate candidate arrival from Exponential(1/λ_max)
3. Advance clock to candidate time t_c
4. Compute acceptance probability p = λ(t_c) / λ_max
5. Draw U ~ Uniform(0,1)
6. IF U ≤ p: accept arrival; assign precinct; record event
 ELSE: reject (thin) the candidate
7. Repeat from step 2 until t_c > T
```

### 10.2 Service Times — LogNormal Distribution

| Property | Specification |
|----------|--------------|
| **Distribution** | LogNormal(μ, σ) |
| **Target moments** | Mean = 25 min, Std = 10 min |
| **LogNormal parameters** | μ = ln(25² / √(25² + 10²)) ≈ 3.136, σ = √(ln(1 + (10/25)²)) ≈ 0.385 |
| **Support** | (0, ∞) — strictly positive |
| **Justification** | Right-skewed, positive, matches empirical EMS service-time profiles (see `docs/service_model_spec.md`) |

### 10.3 Travel Times — Deterministic Given State

Travel times are **not** random draws. They are deterministic functions of:

- The dispatched unit's current location (lat, lon),
- The incident location (precinct centroid),
- The Haversine distance between them,
- The effective speed at the current hour of day.

Stochasticity in travel time arises **indirectly** through (a) random
incident locations (precinct assignment) and (b) which unit happens to be
available (depends on prior random service completions).

### 10.4 Random Number Streams and Reproducibility

| Stream | Purpose | Seed Strategy |
|--------|---------|---------------|
| Stream 1 | NHPP arrival generation (thinning) | Base seed + replication index |
| Stream 2 | Precinct assignment (multinomial) | Base seed + replication index + offset |
| Stream 3 | Service-time sampling (LogNormal) | Base seed + replication index + offset |

- **Base seed:** 42 (configurable in `configs/demand.yaml`).
- **Dedicated streams** ensure that changes to one random component (e.g.,
 service time distribution) do not alter the arrival sequence, enabling
 valid variance-reduction via **Common Random Numbers (CRN)**.
- NumPy `Generator` (PCG64) is used for all sampling.

---

## 11. Event Flow Diagram

### 11.1 High-Level Event Transition Diagram

```
 ┌─────────────────────────┐
 │ SIMULATION START │
 │ t = 0, all units idle │
 └────────────┬────────────┘
 │
 ▼
 ┌──────────────────────────────────┐
 │ INCIDENT ARRIVAL │
 │ (NHPP thinning at rate λ(t)) │
 └──────────┬───────────┬───────────┘
 │ │
 unit free?│ │ all units busy
 ▼ ▼
 ┌──────────────┐ ┌──────────────────┐
 │ DISPATCH │ │ ENQUEUE (FIFO) │
 │ DECISION │ │ incident_queue │
 └──────┬───────┘ └────────┬─────────┘
 │ │
 │ ◄─────────────┘ (dequeued when
 │ unit freed)
 ▼
 ┌──────────────────────┐
 │ SERVICE START │
 │ (after δ + travel) │
 └──────────┬───────────┘
 │
 ▼
 ┌──────────────────────┐
 │ SERVICE COMPLETION │
 │ unit → AVAILABLE │
 └──────┬──────┬────────┘
 │ │
 queue empty? │ │ queue non-empty
 ▼ ▼
 ┌──────────┐ ┌──────────────┐
 │ UNIT │ │ DISPATCH │
 │ IDLES │ │ next queued │
 │ at home │ │ incident │
 └──────────┘ └──────────────┘
 │
 ▼
 (back to SERVICE START)

 ─────────────────────────────────────
 When sim_clock ≥ T:
 ┌──────────────────────────────┐
 │ END OF SIMULATION │
 │ • Stop new arrivals │
 │ • Drain in-progress services │
 │ • Collect final statistics │
 └──────────────────────────────┘
```

### 11.2 Single-Incident Timeline

```
 arrival_time dispatch_time service_start service_end
 │ │ │ │
 ├──── dispatch_delay ──┤ │ │
 │ (queue wait + δ) │ │ │
 │ ├─── travel_time ────┤ │
 │ │ ├── service_time ────┤
 │ │ │ │
 ├────── response_time ─────────────────────┤ │
 │ │ │
 ├──────────────── total_time ───────────────────────────────────┤
```

### 11.3 Process-Interaction View (SimPy)

```
┌───────────────────────────────────────────────────────────┐
│ ArrivalProcess (SimPy generator) │
│ while sim_clock < T: │
│ yield env.timeout(inter_arrival) ← thinning │
│ if accepted: │
│ env.process(IncidentProcess(incident)) │
├───────────────────────────────────────────────────────────┤
│ IncidentProcess (SimPy generator, one per incident) │
│ request unit from resource pool │
│ yield request ← may wait in queue │
│ yield env.timeout(dispatch_delay + travel_time) │
│ yield env.timeout(service_time) │
│ release unit back to resource pool │
│ record all timestamps │
└───────────────────────────────────────────────────────────┘
```

---

## 12. Assumptions and Limitations

### 12.1 Key Assumptions

| ID | Assumption | Justification | Impact if Violated |
|----|-----------|---------------|--------------------|
| A-1 | Historical crash data (2013–2026) is representative of future demand patterns. | Long time-series provides stable hourly/DOW/precinct estimates. | Demand mis-specification; mitigated by sensitivity analysis on λ₀. |
| A-2 | Each incident requires exactly **one** EMS unit. | Simplifies dispatch; most crashes require a single ambulance. | Under-estimates resource demand for multi-unit incidents. |
| A-3 | Travel distance approximated by **Haversine** (great-circle). | Avoids road-network dependency; Haversine underestimates true road distance by ~20–30%. | Systematically underestimates travel time; mitigated by conservative speed (20 mph) and sensitivity analysis. |
| A-4 | Constant average EMS speed within each TOD band (20 mph base). | NYC DOT reports urban speeds 12–25 mph; 20 mph is a reasonable central estimate with lights/sirens. | Ignores route-specific congestion; partially mitigated by TOD factors. |
| A-5 | Service time i.i.d. LogNormal(mean=25, std=10 min) for all incidents. | Literature-supported; captures right-skew and positive support. | Severity-dependent service times are ignored; sensitivity analysis on μ_s and σ_s. |
| A-6 | Incident locations are **precinct centroids** (not exact crash coordinates). | 30-precinct spatial resolution balances fidelity and tractability. | Intra-precinct spatial variation is lost; acceptable for strategic firehouse-level decisions. |
| A-7 | Upon service completion, units **instantaneously** return to home firehouse. | Service-time distribution is calibrated to include return component. | Slight overestimate of availability during return; conservative from a policy-evaluation perspective. |
| A-8 | No dispatch priority or preemption. | Out-of-scope; focuses on spatial staging rather than triage. | Model does not differentiate critical vs. non-critical calls. |
| A-9 | Static allocation: unit positions fixed for the entire replication. | Evaluates strategic staging; dynamic relocation is a separate problem. | Cannot capture real-time repositioning benefits. |
| A-10 | Empty-and-idle initial conditions at *t = 0*. | Natural for a fresh deployment cycle start. | Brief transient at start; negligible over 168 h horizon. |
| A-11 | No balking, reneging, or abandonment from the queue. | All crashes require response regardless of wait. | Queue may over-accumulate under extreme load; realistic for emergency services. |
| A-12 | Firehouses have a maximum capacity of 5 units. | Physical space constraint from optimisation model. | May restrict optimal solutions; configurable parameter. |

### 12.2 Limitations and Exclusions

| Exclusion | Reason |
|-----------|--------|
| Real-time dynamic relocation | Out-of-scope; this study evaluates static staging policies only. |
| Congestion-dependent travel times | Would require a full traffic simulation model; beyond project scope. |
| Full road-network routing | Requires OSRM/GraphHopper integration; Haversine proxy is a defensible simplification for strategic analysis. |
| Dispatch priority / preemption | All incidents treated equally; priority modelling is a future extension. |
| Hospital turnaround delays | Would add complexity with limited impact on firehouse staging decisions. |
| Non-crash EMS demand | Study focuses on motor-vehicle collision response; other call types excluded. |
| Multiple-unit incidents | Assumed single-unit; major incidents are rare and would require a separate protocol model. |
| Shift changes / breaks | Units are available 24/7 for the simulation horizon; workforce scheduling is out-of-scope. |
| Equipment failures / breakdowns | All units assumed to be operational throughout the replication. |

### 12.3 Sensitivity Analysis Plan

To assess robustness of results to key assumptions, the following parameters
will be varied in sensitivity experiments:

| Parameter | Base Value | Sensitivity Range |
|-----------|-----------|-------------------|
| Base arrival rate λ₀ | 3.48 /hr | ±25% (2.61 – 4.35) |
| Average EMS speed *v* | 20 mph | 15 – 25 mph |
| Service time mean μ_s | 25 min | 20 – 35 min |
| Total units *K* | 40 | {20, 30, 40, 48} |
| Response-time threshold τ | 8 min | {6, 8, 10, 12} min |

---

## 13. References

1. **Law, A. M.** (2015). *Simulation Modeling and Analysis*, 5th ed. McGraw-Hill. 
 Chapters 9 (terminating simulation output analysis), 12 (random variate generation).

2. **Banks, J., Carson, J. S., Nelson, B. L., & Nicol, D. M.** (2014). 
 *Discrete-Event System Simulation*, 5th ed. Pearson.

3. **Lewis, P. A. W., & Shedler, G. S.** (1979). Simulation of nonhomogeneous 
 Poisson processes by thinning. *Naval Research Logistics Quarterly*, 26(3), 403–413.

4. **Daskin, M. S.** (1983). A maximum expected covering location model. 
 *Transportation Science*, 17(1), 48–70.

5. **Church, R. L., & ReVelle, C.** (1974). The maximal covering location problem. 
 *Papers of the Regional Science Association*, 32, 101–118.

6. **McLay, L. A., & Mayorga, M. E.** (2010). Evaluating emergency medical 
 service performance measures. *Health Care Management Science*, 13(2), 124–136.

7. **Budge, S., Ingolfsson, A., & Zerom, D.** (2010). Empirical analysis of 
 ambulance travel times. *Management Science*, 56(4), 716–723.

8. **SimPy Documentation** — https://simpy.readthedocs.io/en/latest/

---

*Document prepared as part of the EMS Readiness Optimization project, Phase 4.* 
*Cross-references: `docs/project_charter.md`, `docs/assumptions_log.md`,
`docs/service_model_spec.md`, `docs/optimization_formulation.md`.*
