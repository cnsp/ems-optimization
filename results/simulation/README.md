# simulation/ — ✅ CURRENT

Simulation verification, validation pilots, and production experiment results.
All files use cap=2 and spatially-stratified P0.

## Structure

### verification/
4 verification tests confirming simulator correctness:
- `01_toy_example.json` — Known analytical solution
- `02_zero_demand.json` — No arrivals → no incidents
- `03_single_unit.json` — Saturation test
- `04_extreme_demand.json` — Stress test

### validation_pilot/
3 validation pilots confirming expected behavior:
- `pilot1_*` — P0 vs P2 directional comparison (P2 dominates)
- `pilot2_*` — Response time decreases with fleet size
- `pilot3_*` — Response time increases with demand intensity

### production/
Full production experiments (30 replications each):
- `exp1_policy_comparison.csv`
- `exp2_fleet_sensitivity.csv`
- `exp3_demand_sensitivity.csv`
- `exp4_service_robustness.csv`
- `experiment_summary.csv` — Combined summary

### cbd_experiment/
CBD-focused simulation analysis.
