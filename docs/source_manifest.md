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

## Update Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-03-12 | Initial data acquisition | All raw data files downloaded from NYC Open Data |
