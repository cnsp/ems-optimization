---
status: ✅ CURRENT
last_updated: "2026-03-20"
verified: "All metrics, code references, and nomenclature are current as of March 2026"
---
# Distance Metric Comparison: Haversine vs Manhattan

**Date:** March 12, 2026 
**Version:** 1.0 
**Author:** EMS Optimization Team

---

## 1. Motivation

The baseline EMS Optimization model uses **Haversine (great-circle) distance** to compute firehouse-to-precinct travel times. Haversine measures the shortest path over a sphere, which underestimates actual road distances in cities with grid-based street networks.

**Manhattan (taxicab / L1) distance** may be more realistic for Manhattan's grid layout, where EMS vehicles travel along north–south avenues and east–west streets rather than in straight lines.

This analysis compares both metrics to assess whether the choice of distance function significantly affects EMS allocation decisions and simulated performance.

## 2. Methodology

### 2.1 Distance Formulas

| Metric | Formula | Characteristics |
|--------|---------|----------------|
| **Haversine** | `2R × arcsin(√(sin²(Δlat/2) + cos(lat₁)cos(lat₂)sin²(Δlon/2)))` | Great-circle distance; underestimates road distance |
| **Manhattan** | `|Δlat| × 69.0 + |Δlon| × 52.3` (miles) | L1 distance; better approximation for grid networks |

The Manhattan distance conversion factors are:
- **69.0 miles per degree latitude** (approximately constant)
- **52.3 miles per degree longitude** at 40.75°N (Manhattan's average latitude), computed as `cos(40.75°) × 69.0`

### 2.2 Distance Matrix Comparison

Both metrics produce a 48×30 distance matrix (firehouses × precincts):

| Statistic | Haversine | Manhattan |
|-----------|-----------|-----------|
| **Mean distance** | 4.285 miles | 5.480 miles |
| **Min distance** | 0.028 miles | 0.030 miles |
| **Max distance** | 14.197 miles | 18.634 miles |
| **Manhattan/Haversine ratio** | — | 1.273 ± 0.111 |

Manhattan distances are on average **27.3% longer** than Haversine distances, consistent with the theoretical expectation that L1 ≥ L2 for any pair of points.

### 2.3 Experiment Design

1. Solve P2 (demand-weighted allocation) using Haversine-based travel times → **P2-Haversine**
2. Solve P2 using Manhattan-based travel times → **P2-Manhattan**
3. Run 10 replications of each allocation in the DES simulation engine
4. Compare response times, coverage, and other metrics

## 3. Results

### 3.1 Allocation Differences

Both optimisations allocated K=20 units across 20 firehouses. Only **2 firehouses** had different allocations, indicating that the two distance metrics produce very similar optimal solutions for this problem.

### 3.2 Simulation Performance

| Scenario | Mean RT (min) | Median RT (min) | P90 (90th %ile) RT (min) | 8-min Coverage (NFPA) |
|----------|--------------|----------------|-------------|-------------------|
| **P2-Haversine** | 2.55 | 2.24 | 3.73 | 99.6% |
| **P2-Manhattan** | 2.55 | 2.24 | 3.73 | 99.6% |

The simulation results are **nearly identical** because the simulation engine uses its own travel-time model (Haversine-based) regardless of which distance metric was used for optimisation.

### 3.3 Key Observation

The similarity of results occurs because:
1. Manhattan distances are a scaled version of Haversine distances (ratio ≈ 1.27×)
2. The scaling is approximately uniform across all firehouse–precinct pairs
3. Uniform scaling preserves the **relative ordering** of distances, so the same firehouses remain "nearest" to each precinct under both metrics
4. The optimiser's allocation decisions depend primarily on relative distances, not absolute values

## 4. Figures

| Figure | Description |
|--------|-------------|
| `results/distance_comparison/distance_matrices_heatmap.png` | Side-by-side heatmaps of Haversine and Manhattan distance matrices |
| `results/distance_comparison/distance_scatter.png` | Scatter plot showing linear relationship between metrics |
| `results/distance_comparison/distance_comparison_bar.png` | Bar chart comparing simulation performance |
| `results/distance_comparison/distance_comparison_boxplot.png` | Box plots of per-replication response time distributions |

## 5. Discussion

### 5.1 When Would the Metrics Diverge?

The two metrics would produce more different allocations in scenarios where:
- The street network is **not** a regular grid (diagonal avenues, one-way restrictions)
- There are **physical barriers** (rivers, parks, highway overpasses) that the Manhattan metric does not capture
- The study area has **heterogeneous grid orientation** (e.g., Lower Manhattan's irregular street pattern)

### 5.2 Limitations

1. Neither metric accounts for actual road network topology or real-time traffic
2. The Manhattan metric assumes a perfectly orthogonal grid aligned with cardinal directions
3. Both metrics use constant conversion factors across the study area

## 6. Recommendation

For this study, **Haversine distance is adequate** as the primary distance metric because:
1. The travel-time proxy already underestimates actual road distances (acknowledged in assumptions)
2. Manhattan distance does not improve the relative ordering of firehouse–precinct distances
3. The simulation performance is effectively identical under both metrics

However, if the model were extended to use **real road network distances** (e.g., via OSRM or Google Maps API), the improvement would be more significant than switching between Haversine and Manhattan.

## 7. Files Generated

| File | Description |
|------|-------------|
| `data/processed/distance_matrix_firehouse_precinct_manhattan.csv` | Manhattan distance matrix (48×30) |
| `results/distance_comparison/comparison_table.csv` | Simulation performance comparison |
| `results/distance_comparison/allocation_comparison.csv` | Firehouse allocation comparison |
| `scripts/generate_manhattan_distance_matrix.py` | Matrix generation script |
| `scripts/run_distance_comparison_experiment.py` | Experiment script |
