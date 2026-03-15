# Data Source Manifest

This document provides an inventory of all data files used in the EMS Readiness Optimization project.

## Raw Data Files

### 1. FDNY Firehouse Listing

| Attribute | Value |
|-----------|-------|
| **Filename** | `FDNY_Firehouse_Listing_20260223.csv` |
| **Size** | 34 KB |
| **Records** | 219 firehouses |
| **Source** | NYC Open Data |
| **Download Date** | February 23, 2026 |
| **Data Dictionary** | `FDNY_Firehouse_Listing_Data_Dictionary.xlsx` |
| **Description** | Complete listing of FDNY firehouses across NYC, including location coordinates, facility names, and borough assignments |

**Key Fields**:
- FacilityName: Name of the firehouse
- FacilityAddress: Street address
- Borough: NYC borough (Manhattan, Brooklyn, Queens, Bronx, Staten Island)
- Latitude/Longitude: Geographic coordinates

### 2. Motor Vehicle Collisions - Crashes

| Attribute | Value |
|-----------|-------|
| **Filename** | `Motor_Vehicle_Collisions_-_Crashes_20260223.csv` |
| **Size** | 536 MB |
| **Records** | ~2.24 million crash records |
| **Source** | NYC Open Data (NYPD) |
| **Download Date** | February 23, 2026 |
| **Data Dictionary** | `Motor_Vehicle_Collisions_Data_Dictionary.xlsx` |
| **Description** | Comprehensive record of motor vehicle collisions in NYC reported by NYPD, including date, time, location, and injury information |

**Key Fields**:
- CRASH DATE / CRASH TIME: Temporal information
- BOROUGH: NYC borough
- LATITUDE / LONGITUDE: Crash coordinates
- NUMBER OF PERSONS INJURED/KILLED: Casualty counts
- CONTRIBUTING FACTOR: Crash cause
- VEHICLE TYPE: Types of vehicles involved

### 3. Police Precincts

| Attribute | Value |
|-----------|-------|
| **Filename** | `Police_Precincts_20260223.csv` |
| **Size** | 3.6 MB |
| **Records** | 78 precincts |
| **Source** | NYC Open Data |
| **Download Date** | February 23, 2026 |
| **Data Dictionary** | `Police_Precincts_Data_Dictionary.xlsx` |
| **Description** | Police precinct boundaries and information for NYC |

**Key Fields**:
- Precinct: Precinct number
- the_geom: Polygon geometry for precinct boundaries

### 4. Manhattan Boundary

| Attribute | Value |
|-----------|-------|
| **Filename** | `manhattan_boundary.geojson` |
| **Size** | 247 KB |
| **Source** | NYC Open Data / Derived |
| **Description** | GeoJSON polygon defining Manhattan borough boundary |

### 5. CBD Boundary (MTA Congestion Relief Zone)

| Attribute | Value |
|-----------|-------|
| **Filename** | `cbd_boundary.geojson` |
| **Size** | 101 KB |
| **Source** | MTA / NYC Open Data |
| **Description** | GeoJSON polygon defining the Central Business District (MTA Congestion Relief Zone) used for robustness analysis |

### 6. NYC Borough Boundaries

| Attribute | Value |
|-----------|-------|
| **Filename** | `nyc_borough_boundaries.geojson` |
| **Size** | 3.1 MB |
| **Source** | NYC Open Data |
| **Description** | GeoJSON polygons for all five NYC borough boundaries |

## Data Dictionary Files

| Filename | Description |
|----------|-------------|
| `FDNY_Firehouse_Listing_Data_Dictionary.xlsx` | Field definitions for firehouse listing |
| `Motor_Vehicle_Collisions_Data_Dictionary.xlsx` | Field definitions for crash data |
| `Police_Precincts_Data_Dictionary.xlsx` | Field definitions for precinct data |

## Data Lineage

```
Raw Data (data/raw/)
 ↓
Interim Data (data/interim/)
 - Manhattan-filtered crashes
 - Manhattan firehouses
 - Temporal aggregations
 ↓
Processed Data (data/processed/)
 - Demand matrices
 - Network graphs
 - Simulation inputs
```

## Processed Data Files

### crashes_manhattan.csv
| Attribute | Value |
|-----------|-------|
| **Location** | `data/processed/` |
| **Size** | 99 MB |
| **Records** | 416,434 |
| **Description** | Crash records filtered to Manhattan boundary with `in_cbd` flag |
| **Date Range** | July 2012 - February 2026 |

### firehouses_clean.csv
| Attribute | Value |
|-----------|-------|
| **Location** | `data/processed/` |
| **Records** | 219 (all NYC) |
| **Description** | All firehouses with `in_manhattan` and `in_cbd` flags |

### firehouses_manhattan.csv
| Attribute | Value |
|-----------|-------|
| **Location** | `data/processed/` |
| **Records** | 48 (27 in CBD) |
| **Description** | Manhattan firehouses only |

### precincts_manhattan.geojson
| Attribute | Value |
|-----------|-------|
| **Location** | `data/processed/` |
| **Records** | 30 precincts |
| **Description** | Police precincts intersecting Manhattan |

---

## Data Quality Audit Findings

**Audit Date:** March 12, 2026

### Crash Data Quality Issues
| Issue | Count | Percentage | Impact |
|-------|-------|------------|--------|
| Missing coordinates | ~448,804 | 20.0% | Cannot be geocoded; excluded from spatial analysis |
| Missing borough | ~134,641 | 6.0% | Borough field unreliable; use spatial filtering instead |
| Invalid coordinates | ~0.1% | <0.1% | Outside NYC bounds; excluded |

### Geographic Validation
| Boundary | Status | Notes |
|----------|--------|-------|
| Manhattan | ✓ Valid | 636.63 sq km; CRS EPSG:4326 |
| CBD | ✓ Valid | 259.58 sq km; 100% within Manhattan |
| Precincts | ✓ Valid | All 78 geometries valid |

### Firehouse Data
- All 219 firehouses have valid NYC coordinates
- 48 firehouses in Manhattan (27 in CBD)
- No missing data

### Borough Distribution (from raw crash data)
| Borough | Crashes | Percentage |
|---------|---------|------------|
| Brooklyn | ~627,000 | 28.0% |
| Queens | ~516,000 | 23.0% |
| Bronx | ~294,000 | 13.1% |
| Manhattan | ~278,000 | 12.4% |
| Staten Island | ~79,000 | 3.5% |
| Missing | ~450,000 | 20.0% |

*Note: Spatial filtering to Manhattan boundary yields 416,434 crashes with valid coordinates.*

---

## Update Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-03-12 | Initial data acquisition | All raw data files downloaded from NYC Open Data |
| 2026-03-12 | Data audit complete | Validated all datasets; created Manhattan-filtered processed files |
