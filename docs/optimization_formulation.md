# Optimization Formulation Specification

> **EMS Readiness Optimization – Phase 3**
>
> This document describes the mathematical formulations used to determine
> optimal EMS unit allocation across Manhattan FDNY firehouses.

---

## 1. Notation

| Symbol | Description |
|--------|-------------|
| $I$ | Set of firehouses (staging locations), $\lvert I \rvert = 48$ |
| $J$ | Set of demand precincts, $\lvert J \rvert = 25$ |
| $K$ | Total number of EMS units to allocate |
| $C$ | Maximum units per firehouse (capacity) |
| $d_j$ | Demand weight for precinct $j$ (arrival rate $\lambda_j$) |
| $t_{ij}$ | Travel time (minutes) from firehouse $i$ to precinct $j$ |
| $\tau$ | Coverage threshold (minutes) for the maximal-coverage model |
| $a_{ij}$ | Coverage indicator: $1$ if $t_{ij} \le \tau$, else $0$ |

---

## 2. Formulation A – Demand-Weighted Allocation

**Goal:** Minimise the total demand-weighted expected response time.

### Decision Variables

- $x_i \in \{0, 1, \dots, C\}$ — number of units at firehouse $i$
- $y_{ij} \in \{0, 1\}$ — 1 if precinct $j$ is served by firehouse $i$

### Objective

$$\min \sum_{j \in J} \sum_{i \in I} d_j \, t_{ij} \, y_{ij}$$

### Constraints

| # | Constraint | Meaning |
|---|-----------|---------|
| 1 | $\sum_{i \in I} x_i = K$ | Deploy exactly $K$ units |
| 2 | $0 \le x_i \le C,\; x_i \in \mathbb{Z}$ | Capacity and integrality |
| 3 | $\sum_{i \in I} y_{ij} = 1 \;\forall j$ | Each precinct served by exactly one firehouse |
| 4 | $y_{ij} \le x_i \;\forall i,j$ | Can only assign to an open firehouse |

### Interpretation

This is the primary model for **P2 (optimised fixed staging)**. It
simultaneously decides how many units to place at each firehouse *and*
which firehouse serves each precinct, minimising the demand-weighted
travel time.

---

## 3. Formulation B – P-Median Model

**Goal:** Select exactly $K$ firehouses and assign precincts to minimise
total demand-weighted distance.

### Decision Variables

- $x_i \in \{0, 1\}$ — 1 if firehouse $i$ is opened
- $y_{ij} \in \{0, 1\}$ — 1 if precinct $j$ is served by firehouse $i$

### Objective

$$\min \sum_{j \in J} \sum_{i \in I} d_j \, t_{ij} \, y_{ij}$$

### Constraints

| # | Constraint | Meaning |
|---|-----------|---------|
| 1 | $\sum_{i \in I} x_i = K$ | Open exactly $K$ firehouses |
| 2 | $\sum_{i \in I} y_{ij} = 1 \;\forall j$ | Each precinct served by exactly one firehouse |
| 3 | $y_{ij} \le x_i \;\forall i,j$ | Can only assign to an open firehouse |

### Interpretation

The p-median answers: *"If we can only staff K firehouses, which K
should we choose?"*  This is useful when fixed costs dominate and units
are scarce. Note that here $K$ refers to the number of **open
locations**, not the total unit count.

---

## 4. Formulation C – Maximal Coverage Model

**Goal:** Maximise the total demand that is covered within a travel-time
threshold $\tau$.

### Decision Variables

- $x_i \in \{0, 1, \dots, C\}$ — number of units at firehouse $i$
- $z_j \in \{0, 1\}$ — 1 if precinct $j$ is covered

### Objective

$$\max \sum_{j \in J} d_j \, z_j$$

### Constraints

| # | Constraint | Meaning |
|---|-----------|---------|
| 1 | $\sum_{i \in I} x_i = K$ | Deploy exactly $K$ units |
| 2 | $0 \le x_i \le C,\; x_i \in \mathbb{Z}$ | Capacity and integrality |
| 3 | $z_j \le \sum_{i \in I} x_i \, a_{ij} \;\forall j$ | Precinct covered only if a nearby firehouse has units |

### Interpretation

The maximal-coverage model focuses on a binary service-level target:
*"Can we reach precinct $j$ in $\le \tau$ minutes?"*  With $\tau = 8$
minutes (configurable), it maximises the proportion of demand that
meets this standard. This model is especially useful for equity
analysis and minimum service-level guarantees.

---

## 5. Baseline Policies (Non-Optimisation)

### P0 – Uniform Allocation

$$x_i = \lfloor K / |I| \rfloor$$

Remainder units distributed round-robin. Ignores demand patterns;
serves as a naïve lower bound.

### P1 – Demand-Proportional Allocation

$$x_i \propto \sum_{j : i = \text{nearest}(j)} d_j$$

Each firehouse receives units proportional to the demand of precincts
for which it is the closest firehouse. Rounded to integers respecting
capacity.

---

## 6. Solver Details

| Property | Value |
|----------|-------|
| Library | PuLP 3.x (Python) |
| Default solver | CBC (COIN-OR Branch-and-Cut) |
| Fallback solver | GLPK |
| Time limit | 300 seconds |
| Optimality gap | Default (solver-determined) |

CBC is bundled with PuLP and requires no external installation.
Problem sizes ($48 \times 25$ variables) are well within CBC's
capabilities; typical solve times are under 5 seconds.

---

## 7. Implementation Map

| Formulation | Source file | Function |
|-------------|-----------|----------|
| Demand-Weighted | `optimization/models.py` | `build_demand_weighted()` |
| P-Median | `optimization/models.py` | `build_p_median()` |
| Maximal Coverage | `optimization/models.py` | `build_maximal_coverage()` |
| Uniform baseline | `optimization/policies.py` | `uniform_allocation()` |
| Demand-proportional | `optimization/policies.py` | `demand_proportional_allocation()` |
| High-level runner | `optimization/allocator.py` | `EMSAllocator.solve()` |
| Configuration | `configs/optimization.yaml` | — |

---

## 8. Use Cases

| Policy | Model | When to use |
|--------|-------|-------------|
| P0 | Uniform | Naïve baseline / equity benchmark |
| P1 | Demand-proportional | Quick heuristic; no solver needed |
| P2 | Demand-weighted | **Primary recommendation** – optimal fixed staging |
| P2-alt | P-median | Selecting K locations from 48 candidates |
| P2-alt | Maximal coverage | Service-level / equity analysis |
| P3 | Time-varying | Future phase (hour-specific $\lambda$ tables) |

---

## References

1. Daskin, M.S. (2013). *Network and Discrete Location*. Wiley.
2. Church, R. & ReVelle, C. (1974). The Maximal Covering Location Problem.
   *Papers of the Regional Science Association*, 32, 101–118.
3. ReVelle, C. & Swain, R. (1970). Central facilities location.
   *Geographical Analysis*, 2(1), 30–42.
