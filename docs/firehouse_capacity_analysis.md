# Firehouse Capacity Analysis – EMS Optimization Model

**Date:** March 15, 2026 
**Scope:** Capacity constraints in the MIP formulations allocating K EMS units across 48 Manhattan firehouses

---

## 1. Current Model Assumptions

### 1.1 Capacity Parameter in Code

The optimization configuration (`configs/optimization.yaml`) sets:

```yaml
firehouse_capacity: 5
```

Every MIP formulation in `models.py` uses `capacity=5` as the default upper bound:

| Model | Variable | Capacity Enforcement |
|-------|----------|---------------------|
| **Demand-Weighted (P2)** | `x_i ∈ {0, …, capacity}` (Integer) | Hard upper bound on `LpVariable` |
| **P-Median (P2b)** | `x_i ∈ {0, 1}` (Binary) | Implicit cap = 1 (facility open/close) |
| **Maximal Coverage (P2c)** | `x_i ∈ {0, …, capacity}` (Integer) | Hard upper bound on `LpVariable` |
| **CBD-Focused** | Same as above | Same |

Baseline policies (`policies.py`) also accept `capacity=5`:

| Policy | Capacity Enforcement |
|--------|---------------------|
| **P0 – Uniform** | Round-robin respects `capacity` ceiling |
| **P1 – Demand-Proportional** | Integer rounding capped at `capacity` |
| **P0-Spatial (stratified)** | Round-robin among selected firehouses, capped at `capacity` |

**Key finding:** The capacity parameter *exists and is enforced*, but the default value of **5** is generous. Several models exploit it.

### 1.2 How the Constraint Appears in the MIP

```python
# models.py – Demand-Weighted
x = pulp.LpVariable.dicts("x", firehouses,
 lowBound=0, upBound=capacity, cat="Integer")
```

The P-Median model uses **binary** `x_i` (open/close), so each opened firehouse effectively gets exactly 1 unit—capacity is not a binding concern there.

---

## 2. Current Allocation Patterns

### 2.1 K = 20 (Primary Scenario)

| Policy | Max Units at 1 FH | # Active FHs (of 48) | Distribution |
|--------|-------------------:|----------------------:|-------------|
| P0 (Uniform) | **1** | 20 | {0: 28, 1: 20} |
| P1 (Demand-Prop) | **2** | 18 | {0: 30, 1: 16, 2: 2} |
| P2 (Demand-Wt) | **1** | 20 | {0: 28, 1: 20} |
| P2b (P-Median) | **1** | 20 | {0: 28, 1: 20} |
| P2c (Max Coverage) | **5** | 7 | {0: 41, 1: 3, 2: 1, 5: 3} |

**At K=20, P2c is the only policy that hits the capacity ceiling**, concentrating 5 units at 3 firehouses (15 of 20 units at 3 locations). All other policies stay at ≤ 2 units per firehouse.

### 2.2 Across All K Values

| K | P0 max | P1 max | P2 max | P2b max | P2c max |
|--:|-------:|-------:|-------:|--------:|--------:|
| 20 | 1 | 2 | 1 | 1 | **5** |
| 30 | 1 | 3 | **5** | 1 | **5** |
| 40 | 1 | 4 | **5** | 1 | **5** |
| 48 | 1 | **5** | **5** | 1 | **5** |

- **P2c (Maximal Coverage)** always concentrates at the cap of 5, regardless of K.
- **P2 (Demand-Weighted)** starts concentrating once K > 20 (reaches cap at K=30+).
- **P1 (Demand-Proportional)** gradually concentrates as K grows.
- **P0 and P2b** never exceed 1 unit/firehouse (by design: uniform and binary p-median).

---

## 3. Realistic Capacity Recommendations

### 3.1 Research Findings

| Source | Key Finding |
|--------|-------------|
| **FDNY structure** | Each firehouse houses 1–3 fire companies (engine + ladder + battalion). Apparatus bays hold 1–3 vehicles typically. |
| **FDNY EMS** | Manhattan has only **6 dedicated EMS stations** (not firehouses). FDNY EMS is a *separate* system from fire suppression with its own stations. |
| **EMS-only stations** | Purpose-built EMS stations can house 2–20 ambulances (Boston example: 11-bay for 20 ambulances). These are *not* standard firehouses. |
| **Fire station design** | Typical fire stations have **2–4 apparatus bays**. EMS units sharing space must compete with engines, ladders, and special units. |
| **NYC reality** | FDNY firehouses already house engine + ladder companies. An additional EMS unit (ambulance + crew) requires a free bay, crew quarters, and supplies. |

### 3.2 Recommended Capacity Constraints

| Scenario | Recommended Cap | Rationale |
|----------|----------------:|-----------|
| **Conservative / Realistic** | **2** | Most Manhattan firehouses have 2–3 bays already occupied by engine + ladder companies. Fitting 1–2 EMS units is feasible with shared bays or apron staging. |
| **Moderate** | **3** | Allows for larger double-house stations (e.g., Battalion HQ stations) that may have extra bay space. |
| **Current (generous)** | 5 | Only achievable at purpose-built EMS stations, not typical firehouses. Unrealistic for most of the 48 Manhattan firehouses. |

### 3.3 Recommendation

> **Use `firehouse_capacity: 2` as the default, with an optional override of 3 for identified large stations.**

This ensures:
1. No firehouse is unrealistically over-loaded.
2. The optimizer spreads units geographically (better spatial coverage).
3. Results align with FDNY operational reality where EMS ambulances share space with fire companies.

---

## 4. Impact Assessment

### 4.1 Would Capacity = 2 Change Optimal Solutions?

| Policy | K=20 Impact | K=30 Impact | K=40+ Impact |
|--------|-------------|-------------|--------------|
| **P0 (Uniform)** | None (already max=1) | None | None |
| **P1 (Demand-Prop)** | None (max=2) | **Yes** – forces spreading from 3 to 2 | **Yes** – significant redistribution |
| **P2 (Demand-Wt)** | None (max=1 at K=20) | **Yes** – forces more firehouses open | **Yes** |
| **P2b (P-Median)** | None (binary) | None | None |
| **P2c (Max Coverage)** | **YES – major change** – must use 10+ FHs instead of 7 | **Yes** | **Yes** |

**At K=20:** Only P2c would be materially affected. Its objective value will decrease (less coverage or same coverage with worse concentration).

**At K=30:** P1, P2, and P2c are all affected. With cap=2, P1-demand uses 21 firehouses (vs 30 at cap=1) and achieves the best mean RT of 2.39 min. P2-optimised uses 25 firehouses at cap=2 with mean RT of 2.44 min. The optimizer is forced to open more firehouses, improving spatial dispersion.

**At K=40+:** Similar effects are amplified — see capacity_sensitivity_analysis.md for the full spectrum.

### 4.2 Is This a Problem?

**No – it's a feature.** The current P2c solution (3 firehouses with 5 units each at K=20) is operationally unrealistic. Forcing dispersion through capacity constraints produces solutions that could actually be implemented.

---

## 5. Code Snippets for Updating Capacity Constraints

### 5.1 Update `configs/optimization.yaml`

```yaml
# Change from 5 to 2
firehouse_capacity: 2

# Or use per-firehouse capacities (future enhancement)
# firehouse_capacity_overrides:
# "Battalion 10/Engine 22/Ladder 13": 3 # large double-house
```

### 5.2 No Code Changes Needed in `models.py`

The capacity parameter is already properly implemented. Changing the YAML value from 5 to 2 propagates through `allocator.py` to all MIP formulations:

```python
# In models.py – already correct:
x = pulp.LpVariable.dicts("x", firehouses,
 lowBound=0, upBound=capacity, cat="Integer")
```

### 5.3 Optional: Per-Firehouse Capacity (Future Enhancement)

To allow different capacities per firehouse (e.g., large stations get cap=3):

```python
# In models.py – replace scalar capacity with dict
def build_demand_weighted(
 travel_time, demand, K,
 capacity=2, # default
 capacity_overrides: dict = None, # NEW
 solver_time_limit=300,
):
 firehouses = list(travel_time.index)
 precincts = [p for p in travel_time.columns if p in demand.index]
 
 # Per-firehouse capacity
 cap = {}
 for fh in firehouses:
 if capacity_overrides and fh in capacity_overrides:
 cap[fh] = capacity_overrides[fh]
 else:
 cap[fh] = capacity
 
 prob = pulp.LpProblem("DemandWeighted_EMS_Allocation", pulp.LpMinimize)
 
 # Use per-firehouse upper bound
 x = {fh: pulp.LpVariable(f"x_{fh}", lowBound=0, upBound=cap[fh], cat="Integer")
 for fh in firehouses}
 # ... rest unchanged ...
```

---

## 6. Summary & Next Steps

| Item | Status | Action |
|------|--------|--------|
| Capacity constraint exists in code | | No structural changes needed |
| Default capacity = 5 is too generous | Note: | **Change to 2** in `optimization.yaml` |
| P2c solutions are unrealistic at all K | Note: | Will auto-fix with cap=2 |
| P2 solutions unrealistic at K≥30 | Note: | Will auto-fix with cap=2 |
| P0, P2b unaffected | | No action needed |
| Per-firehouse capacity | Pending —  | Nice-to-have for future phases |

### Recommended Immediate Action

1. Set `firehouse_capacity: 2` in `configs/optimization.yaml`
2. Re-run all optimization experiments at K ∈ {20, 30, 40, 48}
3. Compare new results with current results to quantify the impact on objective values
4. Update the spatially-stratified P0 analysis with the same capacity constraint

---

## Appendix: Visualization

See `firehouse_capacity_analysis.png` for:
- Distribution of units per firehouse for each policy at K=20
- Maximum firehouse load trends across K values with realistic capacity thresholds
- Count of firehouses exceeding realistic capacity (>2 units)
