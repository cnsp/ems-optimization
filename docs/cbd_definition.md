# CBD Definition for EMS Optimization Study

**Last Updated:** March 12, 2026

---

## Overview

The Central Business District (CBD) for this study is defined based on the **MTA Congestion Relief Zone** boundary, which closely aligns with the economic core of Manhattan below 60th Street. This boundary was chosen because:

1. **Official designation** – The MTA congestion pricing zone is a legally defined area with a precise geographic boundary
2. **High activity density** – It encompasses the highest density of commercial, retail, and transit activity in Manhattan
3. **EMS relevance** – The CBD experiences significantly higher crash rates due to traffic density, pedestrian volume, and complex intersection geometry

## CBD Boundary

The geographic boundary is stored in `data/raw/cbd_boundary.geojson` as a MultiPolygon geometry in WGS84 (EPSG:4326).

**Approximate extent:**
- **North boundary:** ~60th Street
- **South boundary:** Battery Park / Financial District
- **East boundary:** East River waterfront
- **West boundary:** Hudson River waterfront (with exclusions for some waterfront areas)

## CBD Precincts

Police precincts were classified as CBD if ≥30% of their area overlaps the CBD boundary. This threshold ensures that precincts with meaningful CBD presence are included while excluding those with only marginal overlap.

| Precinct | CBD Overlap | Description |
|----------|------------|-------------|
| 1 | 100.0% | Financial District / Tribeca |
| 5 | 100.0% | Chinatown / Lower East Side (south) |
| 6 | 100.0% | West Village / Greenwich Village |
| 7 | 100.0% | Lower East Side |
| 9 | 100.0% | East Village |
| 10 | 100.0% | Chelsea (south) |
| 13 | 100.0% | Gramercy / Stuyvesant Town |
| 14 | 100.0% | Midtown South |
| 17 | 100.0% | Midtown East |
| 18 | 61.4% | Midtown North (partial) |

**Total CBD precincts:** 10 out of 25 Manhattan precincts (40%)

## Demand Characteristics

Based on analysis of 416,434 Manhattan crash records:

- **CBD crashes:** 231,786 (55.7% of all Manhattan crashes)
- **Non-CBD crashes:** 184,648 (44.3%)
- **CBD demand intensity:** ~1.26× higher per-precinct than non-CBD average

The CBD generates disproportionately high demand relative to its geographic area, making it a critical focus for EMS resource allocation.

## Methodology

The CBD precinct classification was performed using:
1. Loading the MTA Congestion Relief Zone boundary (`data/raw/cbd_boundary.geojson`)
2. Loading police precinct boundaries (`data/raw/Police_Precincts_20260223.csv`)
3. Computing the intersection area ratio for each Manhattan precinct
4. Classifying precincts with ≥30% overlap as CBD

This classification is used in:
- CBD robustness experiments (`scripts/run_cbd_experiment.py`)
- CBD analysis (`notebooks/09_cbd_analysis.ipynb`)
- Technical report CBD robustness section
